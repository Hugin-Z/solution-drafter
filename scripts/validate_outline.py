# -*- coding: utf-8 -*-
"""
validate_outline.py · outline.yaml schema 校验 (M2 / 阶段 0 加载守门)

输入: outline.yaml 路径 (默认 templates/<doc_type>/outline.yaml)
输出: exit 0 (合规) / exit 非 0 (硬失败 + stderr 报告)

校验项:
- 必填顶层字段 (doc_type / version / intake_schema / outline / generation / output)
- intake_schema.required / optional 非空 list[str]
- outline 至少 1 个 section / id 唯一 / section 唯一
- 每个 section 含 id / section / title / prompt_path / intake_fields / asset_needs 六字段
- asset_needs 为非空 list[str] (M7-k 中-2 升必填 / S2 素材链 / 与 test_m7j + SKILL 三方对齐)
- prompt_path 文件存在 (相对仓库根)
- generation.system_prompt / stages.s1_extract / s2_acquire / s4_generate / s5_review 文件存在
- generation.domain_plugin 文件存在
- output.template_docx 父目录存在 (template.docx 本身可能 M2 内才生成)

R10: 硬失败 / 不造默认值兜底 / 不做语义推断
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("[错误] 缺少 PyYAML 依赖, 请先 python -m pip install PyYAML", file=sys.stderr)
    sys.exit(1)


REQUIRED_TOP_FIELDS = ["doc_type", "version", "intake_schema", "outline", "generation", "output"]
REQUIRED_SECTION_FIELDS = ["id", "section", "title", "prompt_path", "intake_fields", "asset_needs"]
# M7-k 中-2: s2_acquire 加入必填 stage (M7-j 把 S2 升硬阶段但漏接守门 / 现与 SKILL + test 对齐)
REQUIRED_GENERATION_STAGES = ["s1_extract", "s2_acquire", "s4_generate", "s5_review"]


def validate(yaml_path: Path, repo_root: Path) -> list[str]:
    """返回 issues list / 空 list 表示合规."""
    issues: list[str] = []

    if not yaml_path.exists():
        return [f"outline.yaml 不存在: {yaml_path}"]

    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"outline.yaml YAML 解析失败: {exc!r}"]

    if not isinstance(data, dict):
        return [f"outline.yaml 顶层应为 dict, 实测 {type(data).__name__}"]

    # 顶层必填
    for f in REQUIRED_TOP_FIELDS:
        if f not in data:
            issues.append(f"顶层缺字段: {f}")
    if issues:
        return issues

    # intake_schema
    intake = data["intake_schema"]
    if not isinstance(intake, dict):
        issues.append("intake_schema 应为 dict")
    else:
        if not isinstance(intake.get("required"), list) or not intake["required"]:
            issues.append("intake_schema.required 应为非空 list")
        if "optional" in intake and not isinstance(intake["optional"], list):
            issues.append("intake_schema.optional 应为 list")
        for f in intake.get("required", []) + intake.get("optional", []):
            if not isinstance(f, str) or not f:
                issues.append(f"intake_schema 字段应为非空 str, 实测 {f!r}")

    # outline
    outline = data["outline"]
    if not isinstance(outline, list) or not outline:
        issues.append("outline 应为非空 list")
        return issues

    seen_ids: set[str] = set()
    seen_sections: set[str] = set()
    for idx, sec in enumerate(outline):
        if not isinstance(sec, dict):
            issues.append(f"outline[{idx}] 应为 dict")
            continue
        for f in REQUIRED_SECTION_FIELDS:
            if f not in sec:
                issues.append(f"outline[{idx}] 缺字段: {f}")
        if "id" in sec:
            if sec["id"] in seen_ids:
                issues.append(f"outline id 重复: {sec['id']}")
            seen_ids.add(sec["id"])
        if "section" in sec:
            if sec["section"] in seen_sections:
                issues.append(f"outline section 重复: {sec['section']}")
            seen_sections.add(sec["section"])
        if "prompt_path" in sec:
            p = repo_root / sec["prompt_path"]
            if not p.exists():
                issues.append(f"outline[{idx}] prompt_path 不存在: {sec['prompt_path']}")
        if "intake_fields" in sec:
            if not isinstance(sec["intake_fields"], list):
                issues.append(f"outline[{idx}] intake_fields 应为 list")
            else:
                known = set((intake.get("required") or []) + (intake.get("optional") or []))
                for f in sec["intake_fields"]:
                    if f not in known:
                        issues.append(
                            f"outline[{idx}] intake_fields 含未定义字段: {f} "
                            f"(known: {sorted(known)})"
                        )
        # M7-k 中-2: asset_needs 升必填 (S2 素材链 / 手段无关列素材类型 / 每 section 必有非空 list[str])
        # 缺失由 REQUIRED_SECTION_FIELDS 捕获; 此处校验类型 + 非空 + 元素非空 str。
        if "asset_needs" in sec:
            if not isinstance(sec["asset_needs"], list) or not sec["asset_needs"]:
                issues.append(f"outline[{idx}] asset_needs 应为非空 list")
            else:
                for a in sec["asset_needs"]:
                    if not isinstance(a, str) or not a:
                        issues.append(f"outline[{idx}] asset_needs 元素应为非空 str, 实测 {a!r}")

    # generation
    gen = data["generation"]
    if not isinstance(gen, dict):
        issues.append("generation 应为 dict")
    else:
        sp = gen.get("system_prompt")
        if not sp or not (repo_root / sp).exists():
            issues.append(f"generation.system_prompt 文件不存在: {sp}")
        stages = gen.get("stages")
        if not isinstance(stages, dict):
            issues.append("generation.stages 应为 dict")
        else:
            for st in REQUIRED_GENERATION_STAGES:
                if st not in stages:
                    issues.append(f"generation.stages 缺: {st}")
                else:
                    if not (repo_root / stages[st]).exists():
                        issues.append(f"generation.stages.{st} 文件不存在: {stages[st]}")
        dp = gen.get("domain_plugin")
        if not dp or not (repo_root / dp).exists():
            issues.append(f"generation.domain_plugin 文件不存在: {dp}")

    # output
    out = data["output"]
    if not isinstance(out, dict):
        issues.append("output 应为 dict")
    else:
        tpl = out.get("template_docx")
        if not tpl:
            issues.append("output.template_docx 缺")
        else:
            tpl_parent = (repo_root / tpl).parent
            if not tpl_parent.exists():
                issues.append(f"output.template_docx 父目录不存在: {tpl_parent}")
        if not out.get("filename_pattern"):
            issues.append("output.filename_pattern 缺")
        if not out.get("font_policy"):
            issues.append("output.font_policy 缺")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="outline.yaml schema 校验")
    parser.add_argument("yaml_path", help="outline.yaml 路径")
    parser.add_argument("--repo-root", default=".", help="仓库根 (用于解析相对路径 / 默认 cwd)")
    args = parser.parse_args()

    yaml_path = Path(args.yaml_path).resolve()
    repo_root = Path(args.repo_root).resolve()

    issues = validate(yaml_path, repo_root)
    if issues:
        print(f"[validate_outline] FAIL / {len(issues)} 处问题:", file=sys.stderr)
        for i, msg in enumerate(issues, 1):
            print(f"  {i}. {msg}", file=sys.stderr)
        return 1

    print(f"[validate_outline] PASS / {yaml_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
