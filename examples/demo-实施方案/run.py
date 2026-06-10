# -*- coding: utf-8 -*-
"""
demo-实施方案 · 端到端 demo (implementation-plan doc_type / 默认空领域)
intake.json → outline_filled.json → draft.md → final.docx + check_font_safety

标准 L2 文档类型 demo / run.py 主流程与其它 demo 一致，仅 doc_type 配置不同。
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


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
from llm_stub_local import generate_section_content

DOC_TYPE_DIR = "实施方案"


def safe_filename(value: object, default: str = "draft") -> str:
    text = str(value or default)
    cleaned = "".join("_" if ch in '<>:"/\\|?*' or ord(ch) < 32 else ch for ch in text)
    return cleaned.strip(" .") or default


def main() -> int:
    print("=" * 60)
    print(f"solution-drafter · demo-{DOC_TYPE_DIR} · M7 阶段 1 端到端")
    print("=" * 60)

    outline_yaml = REPO_ROOT / "templates" / DOC_TYPE_DIR / "outline.yaml"
    template_docx = REPO_ROOT / "templates" / DOC_TYPE_DIR / "template.docx"
    intake_json = DEMO_DIR / "input" / "intake.json"

    output_dir = DEMO_DIR / "output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outline_cfg = yaml.safe_load(outline_yaml.read_text(encoding="utf-8"))
    # M7-j S2 产物:fixture assets.json (示例素材 / 真实 agent 用其手段获取)
    _assets = build_demo_assets(outline_cfg)
    (output_dir / 'assets.json').write_text(json.dumps(_assets, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n[1/7] outline.yaml: doc_type={outline_cfg['doc_type']} / sections={len(outline_cfg['outline'])}")

    intake_data = json.loads(intake_json.read_text(encoding="utf-8"))
    print(f"[2/7] intake.json: {len(intake_data)} 字段 / project={intake_data.get('project_name')}")

    system_prompt = (REPO_ROOT / outline_cfg["generation"]["system_prompt"]).read_text(encoding="utf-8")
    stage_prompt = (REPO_ROOT / outline_cfg["generation"]["stages"]["s4_generate"]).read_text(encoding="utf-8")
    domain_plugin = (REPO_ROOT / outline_cfg["generation"]["domain_plugin"]).read_text(encoding="utf-8")
    print(f"[3/7] system={len(system_prompt)} / s4={len(stage_prompt)} / domain={len(domain_plugin)} chars")

    outline_filled = {
        "doc_type": outline_cfg["doc_type"], "doc_type_zh": outline_cfg["doc_type_zh"],
        "intake": intake_data,
        "sections": [
            {"id": s["id"], "title": s["title"], "intake_fields": s["intake_fields"],
             "filled_values": {f: intake_data.get(f) for f in s["intake_fields"]}}
            for s in outline_cfg["outline"]
        ],
    }
    (output_dir / "outline_filled.json").write_text(
        json.dumps(outline_filled, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[4/7] outline_filled.json 落盘")

    # ── 逐 section 生成 → 逐段 append+save 落盘 (M7-l 缺口1+4: 不攒齐再写 / 中途断保住已写) ─
    print(f"[5/7] 逐 section 生成 + 逐段落盘 (append+save 每段 / 不攒齐):")
    body_font = outline_cfg["output"].get("font_policy", "宋体")  # M7-g C-full font_policy 驱动
    doc_title = f"# {intake_data.get('project_name', '【待补充】')} {outline_cfg['doc_type_zh']}\n"
    safe_name = safe_filename(intake_data.get("project_name"))
    final_docx = output_dir / f"{safe_name}_{outline_cfg['doc_type_zh']}.docx"
    draft_md = output_dir / "draft.md"

    create_section_doc(final_docx, body_font=body_font)
    document = Document(str(final_docx))
    stats = append_markdown(document, doc_title, body_font=body_font)  # M7-l: 一级标题先落盘
    document.save(str(final_docx))
    draft_md.write_text(doc_title + "\n", encoding="utf-8")

    for sec in outline_cfg["outline"]:
        section_prompt = (REPO_ROOT / sec["prompt_path"]).read_text(encoding="utf-8")
        md = generate_section_content(
            section_id=sec["id"], section_title=sec["title"], section_prompt=section_prompt,
            intake_data=intake_data, intake_fields=sec["intake_fields"],
            system_prompt=system_prompt, stage_prompt=stage_prompt, domain_plugin=domain_plugin,
            section_assets=_assets["sections"][sec["id"]],   # M7-k 高-2: S2 素材消费
        )
        s = append_markdown(document, md, body_font=body_font)   # M7-l 缺口1+4: 逐 section 追加
        document.save(str(final_docx))                            # 每 section 落盘 (中途断保住已写)
        with draft_md.open("a", encoding="utf-8") as f:
            f.write("\n" + md + "\n")                             # draft.md 同步逐段追加
        for k in stats:
            stats[k] += s.get(k, 0)
        print(f"  [{sec['id']}] {sec['title']}: {len(md)} chars / 已落盘")

    cleaned = clean_docx_whitespace(document)
    document.save(str(final_docx))
    draft_text = draft_md.read_text(encoding="utf-8")
    h2 = draft_text.count(chr(10) + "## ")
    print(f"[6/7] draft.md 逐段落盘 / 二级标题数: {h2}")
    issues = check_font_safety(final_docx, declared_font=body_font)
    print(f"[7/7] final.docx: {final_docx.stat().st_size} bytes / stats={stats} / cleaned={cleaned}")
    print(f"      check_font_safety: {issues}")

    print("\n" + "=" * 60)
    if issues:
        print(f"DEMO FAIL / check_font_safety {len(issues)} 处问题")
        return 1
    print(f"DEMO PASS / M7 实施方案 6 section + docx + font 全合规")
    print(f"  final.docx: {final_docx}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
