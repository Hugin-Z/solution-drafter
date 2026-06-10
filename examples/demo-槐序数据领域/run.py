# -*- coding: utf-8 -*-
"""
demo-槐序数据领域 · 领域插件端到端 demo (proposal-document doc_type + 槐序数据 L3 领域插件 / 全虚构示例)
intake.json → outline_filled.json → draft.md → final.docx + check_font_safety

演示 L3 领域插件如何接入：
- run.py override domain_plugin（不改 outline.yaml）/ 拼接 prompts/domain/槐序数据/ 的 4 个文件。
- 对照 demo-解决方案建议书（默认空领域 / §01 公司实力输出整段【待补充】），
  本 demo 切到槐序数据领域后，§01 公司实力由 company-profile.md 的 own_* 4 字段真实填充。

注：槐序数据为虚构公司，所有领域内容均为示例（见 prompts/domain/槐序数据/）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


# ── 路径 ──────────────────────────────────────────────────────────────
DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(DEMO_DIR))

try:
    import yaml
except ImportError:
    print("[错误] 缺少 PyYAML, 请 python -m pip install PyYAML", file=sys.stderr)
    sys.exit(1)

try:
    from docx import Document
except ImportError:
    print("[错误] 缺少 python-docx, 请 python -m pip install python-docx", file=sys.stderr)
    sys.exit(1)

import sys as _sys
_sys.path.insert(0, str(REPO_ROOT / 'examples'))
from _demo_assets import build_demo_assets
from docx_builder import create_section_doc, clean_docx_whitespace
from append_chapter import append_markdown
from check_font_safety import check_font_safety
from llm_stub_local import generate_section_content   # 本目录 local stub (demo fixture)


# ── 领域插件 4 文件按序拼接 (run.py override / 不改 outline.yaml) ──────
DOMAIN_DIR = REPO_ROOT / "prompts" / "domain" / "槐序数据"
DOMAIN_FILES = [
    "company-profile.md",   # own_* 4 段 (公司主体字段)
    "glossary.md",
    "client-logic.md",
    "compliance.md",
]


def safe_filename(value: object, default: str = "draft") -> str:
    """清洗 Windows 文件名非法字符，避免项目名直接作为 docx 文件名时报错."""
    text = str(value or default)
    cleaned = "".join("_" if ch in '<>:"/\\|?*' or ord(ch) < 32 else ch for ch in text)
    return cleaned.strip(" .") or default


def load_domain() -> str:
    """拼接 4 个领域文件 / 段落分隔 / 缺失文件返回占位 (容错)."""
    parts: list[str] = []
    for fname in DOMAIN_FILES:
        p = DOMAIN_DIR / fname
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
        else:
            parts.append(f"<!-- {fname} 不存在 -->\n")
    return "\n\n".join(parts)


def main() -> int:
    print("=" * 60)
    print("solution-drafter · demo-槐序数据领域 · 领域插件端到端")
    print("=" * 60)

    # ── 路径 (proposal-document doc_type / L2 配置) ─────
    outline_yaml = REPO_ROOT / "templates" / "解决方案建议书" / "outline.yaml"
    intake_json = DEMO_DIR / "input" / "intake.json"

    output_dir = DEMO_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    outline_filled_json = output_dir / "outline_filled.json"
    draft_md = output_dir / "draft.md"

    # ── 1. 加载 outline.yaml ─────────────────────────────────
    print(f"\n[1/8] 加载 outline.yaml: {outline_yaml.relative_to(REPO_ROOT)}")
    outline_cfg = yaml.safe_load(outline_yaml.read_text(encoding="utf-8"))
    print(f"  doc_type: {outline_cfg['doc_type']}")
    print(f"  sections: {len(outline_cfg['outline'])}")

    # ── 2. 加载 intake.json ─────────────────────────────────
    print(f"\n[2/8] 加载 intake.json: {intake_json.relative_to(REPO_ROOT)}")
    intake_data = json.loads(intake_json.read_text(encoding="utf-8"))
    print(f"  字段数: {len(intake_data)}")
    print(f"  project_name: {intake_data.get('project_name', '<missing>')}")
    print(f"  client_name: {intake_data.get('client_name', '<missing>')}")

    # ── 3. 加载 system + s4 prompts ─────────────────────────
    print(f"\n[3/8] 加载 system + s4-generate")
    system_prompt = (REPO_ROOT / outline_cfg["generation"]["system_prompt"]).read_text(encoding="utf-8")
    stage_prompt = (REPO_ROOT / outline_cfg["generation"]["stages"]["s4_generate"]).read_text(encoding="utf-8")
    print(f"  system_prompt: {len(system_prompt)} chars")
    print(f"  s4_generate: {len(stage_prompt)} chars")

    # ── 3b. override domain_plugin → 拼接 4 文件 (不改 outline.yaml) ─
    print(f"\n[3b/8] override domain_plugin: 槐序数据 (拼接 4 文件)")
    print(f"  outline.yaml 字段: {outline_cfg['generation']['domain_plugin']} (默认空领域 / 本 demo override 不读)")
    domain_plugin = load_domain()
    print(f"  override 字面: {len(domain_plugin)} chars / 拼接 {len(DOMAIN_FILES)} 文件")
    for anchor in ("own_company_brief", "own_qualifications", "own_certifications", "own_team_size"):
        print(f"  含 ## {anchor}: {('## ' + anchor) in domain_plugin}")

    # ── 4. 模板填充 (S3) ─────────────────────────────────────
    print(f"\n[4/8] 模板填充 → outline_filled.json")
    outline_filled = {
        "doc_type": outline_cfg["doc_type"],
        "doc_type_zh": outline_cfg["doc_type_zh"],
        "domain": "huaixu-data",
        "intake": intake_data,
        "sections": [
            {
                "id": s["id"],
                "title": s["title"],
                "intake_fields": s["intake_fields"],
                "filled_values": {f: intake_data.get(f) for f in s["intake_fields"]},
            }
            for s in outline_cfg["outline"]
        ],
    }
    outline_filled_json.write_text(
        json.dumps(outline_filled, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  落盘: {outline_filled_json.relative_to(REPO_ROOT)} ({outline_filled_json.stat().st_size} bytes)")
    # S2 产物: fixture assets.json (示例素材 / 真实 agent 用其手段获取)
    _assets = build_demo_assets(outline_cfg)
    (output_dir / 'assets.json').write_text(json.dumps(_assets, ensure_ascii=False, indent=2), encoding='utf-8')

    # ── 5-7. 逐 section 生成 → 逐段 append+save 落盘 (不攒齐再写 / 中途断保住已写) ─
    body_font = outline_cfg["output"].get("font_policy", "宋体")  # font_policy 驱动正文字体
    doc_title = f"# {intake_data.get('project_name', '【待补充】')} {outline_cfg['doc_type_zh']}\n"
    safe_name = safe_filename(intake_data.get("project_name"))
    final_docx = output_dir / f"{safe_name}_{outline_cfg['doc_type_zh']}.docx"
    print(f"\n[5/8] 逐 section 生成 + 逐段落盘 (含 槐序数据 domain_plugin / append+save 每段)")

    create_section_doc(final_docx, body_font=body_font)
    document = Document(str(final_docx))
    stats = append_markdown(document, doc_title, body_font=body_font)  # 一级标题先落盘
    document.save(str(final_docx))
    draft_md.write_text(doc_title + "\n", encoding="utf-8")

    for sec in outline_cfg["outline"]:
        section_prompt_path = REPO_ROOT / sec["prompt_path"]
        section_prompt = section_prompt_path.read_text(encoding="utf-8")
        md = generate_section_content(
            section_id=sec["id"],
            section_title=sec["title"],
            section_prompt=section_prompt,
            intake_data=intake_data,
            intake_fields=sec["intake_fields"],
            system_prompt=system_prompt,
            stage_prompt=stage_prompt,
            domain_plugin=domain_plugin,   # 领域插件注入 (§01 own_* 填充)
            section_assets=_assets["sections"][sec["id"]],   # S2 素材消费
        )
        s = append_markdown(document, md, body_font=body_font)   # 逐 section 追加
        document.save(str(final_docx))                            # 每 section 落盘 (中途断保住已写)
        with draft_md.open("a", encoding="utf-8") as f:
            f.write("\n" + md + "\n")                             # draft.md 同步逐段追加
        for k in stats:
            stats[k] += s.get(k, 0)
        print(f"  [{sec['id']}] {sec['title']}: {len(md)} chars / 已 append+save 落盘")

    # ── 6-7. 末尾统一清空格 + final save ─────────────────────
    cleaned = clean_docx_whitespace(document)
    document.save(str(final_docx))
    draft_text = draft_md.read_text(encoding="utf-8")
    print(f"\n[6/8] draft.md 逐段落盘 ({draft_md.stat().st_size} bytes / 二级标题数: {draft_text.count(chr(10) + '## ')})")
    print(f"[7/8] final.docx: {final_docx.relative_to(REPO_ROOT)} ({final_docx.stat().st_size} bytes) / stats: {stats} / cleaned: {cleaned} run")

    # ── 8. check_font_safety ────────────────────────────────
    print(f"\n[8/8] check_font_safety on final.docx")
    issues = check_font_safety(final_docx, declared_font=body_font)
    print(f"  issues: {issues}")

    print("\n" + "=" * 60)
    if issues:
        print(f"DEMO FAIL / check_font_safety 报告 {len(issues)} 处问题")
        return 1
    print("DEMO PASS / 槐序数据 领域插件切换 + 6 section + docx + font 全合规")
    print(f"  final.docx: {final_docx}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
