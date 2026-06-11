# -*- coding: utf-8 -*-
"""
demo-需求方案 · 端到端 demo (requirement-proposal doc_type / 默认空领域)
intake.json → outline_filled.json → draft.md → final.docx + check_font_safety

调用链:
1. 加载 outline.yaml + intake.json
2. 逐 section 调 stub 生成 markdown
3. 逐 section append_markdown + save 落盘 (长文档不断流 / 中途断保住已写)
4. check_font_safety(final.docx) → 应返回 []

stub 是 demo fixture；真实使用时 agent 自读 section prompt 生成内容（见 SKILL.md）。
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


# ── 路径 (DEMO_DIR / REPO_ROOT / scripts / 模块解析) ──────────────────
DEMO_DIR = Path(__file__).resolve().parent
REPO_ROOT = DEMO_DIR.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# ── 依赖 (前置 verify: PyYAML / docx_builder / append_chapter / check_font_safety / llm_stub) ──
try:
    import yaml
except ImportError:
    print("[错误] 缺少 PyYAML 依赖, 请 python -m pip install PyYAML", file=sys.stderr)
    sys.exit(1)

try:
    from docx import Document
except ImportError:
    print("[错误] 缺少 python-docx 依赖, 请 python -m pip install python-docx", file=sys.stderr)
    sys.exit(1)

import sys as _sys
_sys.path.insert(0, str(REPO_ROOT / 'examples'))
from _demo_assets import build_demo_assets
from _demo_s5 import s5_review_and_render
from docx_builder import create_section_doc, clean_docx_whitespace
from append_chapter import append_markdown
from check_font_safety import check_font_safety
from llm_stub import generate_section_content


def safe_filename(value: object, default: str = "draft") -> str:
    """清洗 Windows 文件名非法字符，避免项目名直接作为 docx 文件名时报错."""
    text = str(value or default)
    cleaned = "".join("_" if ch in '<>:"/\\|?*' or ord(ch) < 32 else ch for ch in text)
    return cleaned.strip(" .") or default


def main() -> int:
    print("=" * 60)
    print("solution-drafter · demo-需求方案 · 端到端")
    print("=" * 60)

    # ── 路径 ────────────────────────────────────────────────
    outline_yaml = REPO_ROOT / "templates" / "需求方案" / "outline.yaml"
    template_docx = REPO_ROOT / "templates" / "需求方案" / "template.docx"
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

    # ── 3. 加载 system + stages + domain prompts ─────────────
    print(f"\n[3/8] 加载 system + s4-generate + domain plugin")
    system_prompt = (REPO_ROOT / outline_cfg["generation"]["system_prompt"]).read_text(encoding="utf-8")
    stage_prompt = (REPO_ROOT / outline_cfg["generation"]["stages"]["s4_generate"]).read_text(encoding="utf-8")
    domain_plugin = (REPO_ROOT / outline_cfg["generation"]["domain_plugin"]).read_text(encoding="utf-8")
    print(f"  system_prompt: {len(system_prompt)} chars")
    print(f"  s4_generate: {len(stage_prompt)} chars")
    print(f"  domain_plugin: {len(domain_plugin)} chars")

    # ── 4. 模板填充 / outline_filled.json (S3) ───────────────
    print(f"\n[4/8] 模板填充 → outline_filled.json")
    outline_filled = {
        "doc_type": outline_cfg["doc_type"],
        "doc_type_zh": outline_cfg["doc_type_zh"],
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
    # S2 产物:fixture assets.json (示例素材 / 真实 agent 用其手段获取)
    _assets = build_demo_assets(outline_cfg)
    (output_dir / 'assets.json').write_text(json.dumps(_assets, ensure_ascii=False, indent=2), encoding='utf-8')

    # ── 5. S4 内容生成: 逐 section 生成 → 逐段 append 到 draft.md (crash-safe / 不攒齐) ─
    # font_policy 驱动正文字体 (create_section_doc 重建容器 / Normal 样式 = font_policy)。
    body_font = outline_cfg["output"].get("font_policy", "宋体")
    doc_title = f"# {intake_data.get('project_name', '【待补充】')} 需求方案\n"
    print(f"\n[5/8] S4 逐 section 生成 → draft.md 逐段落盘 (body_font={body_font})")
    draft_md.write_text(doc_title + "\n", encoding="utf-8")
    section_markdowns: list[str] = []
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
            domain_plugin=domain_plugin,
            section_assets=_assets["sections"][sec["id"]],   # S2 素材消费
        )
        section_markdowns.append(md)
        with draft_md.open("a", encoding="utf-8") as f:
            f.write("\n" + md + "\n")                             # draft.md 逐段追加 (中途断保住已写)
        print(f"  [{sec['id']}] {sec['title']}: {len(md)} chars / draft 已落盘")
    draft_text = draft_md.read_text(encoding="utf-8")
    print(f"[6/8] S4 draft.md 完成 ({draft_md.stat().st_size} bytes / 二级标题数: {draft_text.count(chr(10) + '## ')})")

    # ── 7. S5 评审修订: s5-review 自检 → final.md + 逐段渲染 final.docx ─
    s5_review_md = (REPO_ROOT / outline_cfg["generation"]["stages"]["s5_review"]).read_text(encoding="utf-8")
    safe_name = safe_filename(intake_data.get("project_name"))
    final_md = output_dir / "final.md"
    final_docx = output_dir / outline_cfg["output"]["filename_pattern"].format(project_name=safe_name)  # 套用 filename_pattern
    sc_issues, issues, stats = s5_review_and_render(
        draft_text=draft_text, section_markdowns=section_markdowns, doc_title=doc_title,
        outline_cfg=outline_cfg, s5_review_md=s5_review_md,
        final_md_path=final_md, final_docx_path=final_docx,
    )
    print(f"[7/8] S5: final.md + final.docx 落盘 / s5-review 自检 {len(sc_issues)} 项 / stats {stats}")
    if sc_issues:
        print(f"  S5 自检问题: {sc_issues}")

    # ── 8. check_font_safety on final.docx (含 font_policy 契约校验) ──
    print(f"\n[8/8] check_font_safety on final.docx (declared_font={body_font})")
    print(f"  issues: {issues}")

    # ── 终态 ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if issues:
        print(f"DEMO FAIL / check_font_safety 报告 {len(issues)} 处问题")
        return 1
    print("DEMO PASS / 端到端 6 section 生成 + docx + font 全合规")
    print(f"  final.docx: {final_docx}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
