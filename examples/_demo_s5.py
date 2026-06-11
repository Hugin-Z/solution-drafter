# -*- coding: utf-8 -*-
"""
_demo_s5.py · demo 共享 S5 评审修订步骤 (让 S5 从空壳变真闭环)

S5 = draft.md → 走 s5-review.md 自检清单 → final.md → 逐段渲染 final.docx。

诚实边界 (R10 不夸大):
- demo 的 S5 是"机械自检 + 透传"版:按 s5-review.md 清单做可机械化的检查
  (二级标题数 = section 数 / 无内部术语外泄 / 无总结性 footer),自检通过后 final.md = draft.md 字面透传。
- 真实 S5 的"用户多轮对话评审 + 改写 markdown 字面"仍靠人 (见 SKILL.md / README S5 表述)。
  本函数不替代人工评审,只让"S5 阶段被真正走一遍 + final.md/final.docx 真产出 + s5-review.md 被消费"。
"""

from __future__ import annotations


# s5-review.md 清单里可机械化的项 (其余可读性/事实核验靠人)
_INTERNAL_TERMS = ("__PENDING_USER__", "intake_fields", "production_mode", "part_attribution")


def s5_review_and_render(
    draft_text: str,
    section_markdowns: list,
    doc_title: str,
    outline_cfg: dict,
    s5_review_md: str,
    final_md_path,
    final_docx_path,
):
    """demo S5: 机械自检 draft → final.md → 逐段渲染 final.docx (逐段落盘)。

    入参:
    - draft_text: S4 产出的 draft.md 全文
    - section_markdowns: S4 各 section markdown 列表 (供逐段渲染)
    - doc_title: 一级标题行 (# <项目名> <类型>\\n)
    - outline_cfg: outline.yaml dict (取 font_policy + section 数)
    - s5_review_md: s5-review.md 字面 (被消费 / 证 S5 stage prompt 进流程)
    - final_md_path / final_docx_path: 落盘路径

    返回 (self_check_issues: list[str], font_issues: list[str], stats: dict)。
    """
    # 延迟 import (调用时 scripts 已在 sys.path)
    from docx import Document
    from docx_builder import create_section_doc, clean_docx_whitespace
    from append_chapter import append_markdown
    from check_font_safety import check_font_safety

    assert s5_review_md, "s5-review.md 为空 / S5 stage prompt 未加载"
    n_sections = len(outline_cfg["outline"])
    body_font = outline_cfg["output"].get("font_policy", "宋体")

    # ── 机械自检 (s5-review.md 清单可机械化项) ──
    self_check: list[str] = []
    if draft_text.count("\n## ") != n_sections:
        self_check.append(
            f"二级标题数 {draft_text.count(chr(10) + '## ')} != 本 doc_type section 数 {n_sections}"
        )
    for term in _INTERNAL_TERMS:
        if term in draft_text:
            self_check.append(f"内部术语外泄: {term}")
    if draft_text.rstrip().endswith(("---", "End", "结束")):
        self_check.append("疑似总结性 footer")

    # ── final.md (demo: 自检透传 / 真实 S5 用户改写字面) ──
    final_md = draft_text
    final_md_path.write_text(final_md, encoding="utf-8")

    # ── 逐段渲染 final.docx (逐段落盘 / docx 三步) ──
    create_section_doc(final_docx_path, body_font=body_font)
    document = Document(str(final_docx_path))
    stats = append_markdown(document, doc_title, body_font=body_font)  # 一级标题先落盘
    document.save(str(final_docx_path))
    for md in section_markdowns:
        s = append_markdown(document, md, body_font=body_font)   # 逐 section 追加
        document.save(str(final_docx_path))                      # 每段落盘
        for k in stats:
            stats[k] += s.get(k, 0)
    clean_docx_whitespace(document)
    document.save(str(final_docx_path))

    font_issues = check_font_safety(final_docx_path, declared_font=body_font)
    return self_check, font_issues, stats
