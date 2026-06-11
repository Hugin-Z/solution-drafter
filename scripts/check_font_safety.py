# -*- coding: utf-8 -*-
"""
check_font_safety.py · 字体安全检查（docx 字体白名单 + fontTable 双层校验）

提供:
    - _CHINESE_CANONICAL / _FONT_ALLOWED_NORMALIZED / _FONT_BOILERPLATE_TOLERATED 三字体常量
    - _normalize_font_alias  字体别名归一化
    - _check_fonttable       fontTable.xml 级 warn 检查
    - check_font_safety      段落级 styles.xml + document.xml 白名单检查（主公共函数）

依赖:
    - stdlib only (re / zipfile / xml.etree.ElementTree / pathlib) / 无第三方依赖
"""

from __future__ import annotations

from pathlib import Path


# ── 字体常量 ─────
# 中文字体规范名 → 别名清单（归一化目标）
_CHINESE_CANONICAL: dict[str, list[str]] = {
    "宋体":     ["宋体", "SimSun", "宋体-简", "NSimSun", "STSong", "宋体-繁"],
    "黑体":     ["黑体", "SimHei", "STHeiti"],
    "仿宋":     ["仿宋", "FangSong", "仿宋_GB2312", "STFangsong"],
    "微软雅黑": ["微软雅黑", "Microsoft YaHei", "Microsoft YaHei UI"],
}
# 归一化后的合法字体集合（快速查找用）
_FONT_ALLOWED_NORMALIZED: frozenset[str] = frozenset(
    list(_CHINESE_CANONICAL.keys())
    + ["Times New Roman", "Arial", "Calibri", "Cambria", "Consolas"]
)
# python-docx 默认 boilerplate 自带的字体（知道存在，容忍不报 warn）
_FONT_BOILERPLATE_TOLERATED: frozenset[str] = frozenset({
    "Symbol",
    "Courier",
    "ＭＳ 明朝",    # ＭＳ 明朝（全角，MS Mincho，python-docx 默认）
    "ＭＳ ゴシック",  # ＭＳ ゴシック（全角，MS Gothic，python-docx 默认）
})


# ── 字体别名归一化（compliance_check.py line 333-338）─────
def _normalize_font_alias(font_name: str) -> str:
    """把字体别名归一化到 canonical name；未识别则原样返回。"""
    for canonical, aliases in _CHINESE_CANONICAL.items():
        if font_name in aliases:
            return canonical
    return font_name


# ── fontTable.xml 级 warn 检查 ─────
def _check_fonttable(docx_path) -> list[str]:
    """解析 word/fontTable.xml，返回非白名单且非 boilerplate 字体的 warn 列表。"""
    import zipfile as _zipfile
    import xml.etree.ElementTree as _ET

    NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

    try:
        with _zipfile.ZipFile(docx_path) as z:
            if "word/fontTable.xml" not in z.namelist():
                return []
            xml_bytes = z.read("word/fontTable.xml")
    except (_zipfile.BadZipFile, KeyError):
        return ["字体检查(fontTable)：docx 解压失败"]

    try:
        root = _ET.fromstring(xml_bytes.decode("utf-8"))
    except _ET.ParseError:
        return ["字体检查(fontTable)：xml 解析失败"]

    fonts = [f.get(f"{NS}name") for f in root.findall(f"{NS}font")]
    fonts = [f for f in fonts if f]

    suspicious = []
    for font in fonts:
        normalized = _normalize_font_alias(font)
        if normalized in _FONT_ALLOWED_NORMALIZED:
            continue
        if font in _FONT_BOILERPLATE_TOLERATED or normalized in _FONT_BOILERPLATE_TOLERATED:
            continue
        suspicious.append(font)

    if not suspicious:
        return []
    return [
        f"字体检查(fontTable warn)：docx 声明非白名单字体 {suspicious}，"
        f"非 python-docx 默认 boilerplate；若被实际引用可能导致 WPS fallback 渲染问题。"
        f"白名单 + boilerplate 容忍见 compliance_check.py _FONT_ALLOWED_NORMALIZED / _FONT_BOILERPLATE_TOLERATED。"
    ]


# ── 字体安全检查主函数 ─────
def check_font_safety(docx_path: Path, declared_font: str | None = None) -> list[str]:
    """
    字体安全检查(回归检查项)。

    扫 docx 的 word/styles.xml + word/document.xml,确保:
    - Normal 样式必须有 <w:rFonts> 且 w:eastAsia 在中文白名单
      (宋体 / 仿宋 / 仿宋_GB2312 / 黑体 / 微软雅黑)
    - 所有 run 级 <w:rFonts> 的 w:eastAsia 在上述白名单
    - 所有 run 级 <w:rFonts> 的 w:ascii 在 ("Times New Roman",)

    declared_font (font_policy 校验):若给定,额外断言
    Normal 样式实际 eastAsia == declared_font (= outline.yaml 的 output.font_policy)。
    防"声明仿宋 / 实际宋体"契约不一致回归 (Codex 三审 高1)。None 时跳过该校验
    (向后兼容 / 现有调用不传则仅白名单校验)。

    返回 issues 列表,空表示通过。

    根因背景:若 Normal 样式未设字体,Word/WPS 会 fallback 到 docDefaults 的
    minorEastAsia 主题字体,在主题文件 themeFontLang 为日语或 CJK 解析失败时
    渲染为 MS 明朝(日文字体),导致 WPS 提示"字体缺失"。
    """
    import re as _re
    import zipfile as _zipfile

    issues: list[str] = []
    ALLOWED_CJK = {a for aliases in _CHINESE_CANONICAL.values() for a in aliases}
    # Consolas: inline code (`API` / `SDK` 等术语) 等宽字体 / append_chapter 设此 ascii 字体
    ALLOWED_ASCII = {"Times New Roman", "Consolas"}

    try:
        with _zipfile.ZipFile(docx_path) as z:
            styles_xml = z.read("word/styles.xml").decode("utf-8")
            document_xml = z.read("word/document.xml").decode("utf-8")
    except (KeyError, _zipfile.BadZipFile) as exc:
        issues.append(f"字体检查:docx 解压失败 {exc}")
        return issues

    # 检查 Normal 样式
    m = _re.search(
        r'<w:style[^>]*w:styleId="Normal"[^>]*>(.*?)</w:style>',
        styles_xml, _re.DOTALL)
    if not m:
        issues.append("字体检查:styles.xml 中未找到 Normal 样式")
    else:
        normal_body = m.group(1)
        r = _re.search(r'<w:rFonts\s[^/]*/?>', normal_body)
        if not r:
            issues.append(
                "字体检查:Normal 样式无 <w:rFonts> 标签,run 会 fallback 到 "
                "docDefaults minorEastAsia 主题字体,WPS 可能渲染为日文 MS 明朝"
            )
        else:
            ea_m = _re.search(r'w:eastAsia="([^"]+)"', r.group(0))
            if not ea_m:
                issues.append("字体检查:Normal 样式 <w:rFonts> 缺 w:eastAsia 属性")
            elif ea_m.group(1) not in ALLOWED_CJK:
                issues.append(
                    f"字体检查:Normal 样式 eastAsia={ea_m.group(1)!r} "
                    f"不在白名单 {sorted(ALLOWED_CJK)}"
                )
            elif declared_font is not None and ea_m.group(1) != declared_font:
                issues.append(
                    f"字体契约不一致(font_policy):Normal 样式实际 eastAsia="
                    f"{ea_m.group(1)!r} 与声明 font_policy={declared_font!r} 不符"
                )

    # 抽样检查 run 级 rFonts 异常字体
    # document.xml 含所有正文 run(段落 + 表格 cell + 图注),findall 遍历全部。
    run_rfonts = _re.findall(r'<w:rFonts\s[^/]*/?>', document_xml)
    bad_ea: dict = {}
    bad_ascii: dict = {}
    # run 级 font_policy 契约校验。declared_font 给定时,所有正文 run 的
    # eastAsia 必须 ∈ {declared_font, 黑体}(标题黑体放行 / inline code 的 eastAsia 已=body_font)。
    # 任何 run 回落非声明字体(如 body_font=仿宋 时末段/表格/图注漏传成宋体)当场命中。
    policy_bad_ea: dict = {}
    for tag in run_rfonts:
        ea_m = _re.search(r'w:eastAsia="([^"]+)"', tag)
        if ea_m and ea_m.group(1) not in ALLOWED_CJK:
            bad_ea[ea_m.group(1)] = bad_ea.get(ea_m.group(1), 0) + 1
        if (declared_font is not None and ea_m
                and ea_m.group(1) not in (declared_font, "黑体")):
            policy_bad_ea[ea_m.group(1)] = policy_bad_ea.get(ea_m.group(1), 0) + 1
        asc_m = _re.search(r'w:ascii="([^"]+)"', tag)
        if asc_m and asc_m.group(1) not in ALLOWED_ASCII:
            bad_ascii[asc_m.group(1)] = bad_ascii.get(asc_m.group(1), 0) + 1

    for font, cnt in policy_bad_ea.items():
        issues.append(
            f"字体契约不一致(font_policy / run 级):正文 run eastAsia={font!r} × {cnt} 处 "
            f"与声明 font_policy={declared_font!r} 不符(标题黑体除外 / 疑 body_font 漏传回落)"
        )

    for font, cnt in bad_ea.items():
        issues.append(
            f"字体检查:检测到非白名单 eastAsia 字体 {font!r} × {cnt} 处 "
            f"(白名单 {sorted(ALLOWED_CJK)})"
        )
    for font, cnt in bad_ascii.items():
        issues.append(
            f"字体检查:检测到非白名单 ascii 字体 {font!r} × {cnt} 处 "
            f"(白名单 {sorted(ALLOWED_ASCII)})"
        )

    # ── fontTable.xml 级检查（warn 级）
    issues.extend(_check_fonttable(docx_path))

    return issues
