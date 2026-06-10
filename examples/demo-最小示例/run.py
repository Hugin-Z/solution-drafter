# -*- coding: utf-8 -*-
"""
demo-最小示例/run.py - M1 端到端 docx 生成 demo

调用链:
    docx_builder.create_section_doc  -> 产出空 docx (内部 save / 返回 Path)
    docx.Document                     -> 读回 doc 对象
    append_chapter.append_markdown    -> 追加 markdown 内容 (mutate doc)
    doc.save                          -> 显式 save
    check_font_safety.check_font_safety -> 字体合规校验

走模块 API / 不走 subprocess (CLI 路径依赖 brief_schema / M1 不迁移)。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from docx import Document

from docx_builder import create_section_doc
from append_chapter import append_markdown
from check_font_safety import check_font_safety


def main() -> None:
    here = Path(__file__).parent
    input_md = here / "input.md"
    output_docx = here / "output.docx"

    create_section_doc(output_docx)

    doc = Document(str(output_docx))
    stats = append_markdown(doc, input_md.read_text(encoding="utf-8"))
    doc.save(str(output_docx))

    issues = check_font_safety(output_docx)

    print(f"[demo] output: {output_docx}")
    print(f"[demo] append_markdown stats: {stats}")
    print(f"[demo] check_font_safety issues: {issues}")


if __name__ == "__main__":
    main()
