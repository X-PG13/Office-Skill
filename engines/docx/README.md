# DOCX engine

python-docx. Two paths.

**Prose** (legal, academic, memos). Real styles: Normal, Heading 1–3, Caption. A TOC field when `include_toc` is true. Legal numbering is a numbering part, not typed digits. Header and footer are fields and text, with East Asian fonts set.

**公文** (`doc_kind: gongwen`). GB/T 9704 margins, 16 pt body, 28 pt exact line spacing, red issuing authority, red separator, 版记. Read `profiles/government.md` before writing the plan. The red is `palette.header_red` and is not used anywhere else.

```bash
python -m office_skill render plan.json -o note.docx
```

Captions are numbered 表 1 / Table 1 in document order. Do not draw a table with tab characters.
