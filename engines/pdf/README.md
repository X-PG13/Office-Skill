# PDF engine

Default: Typst, via the pinned `typst` package. The plan's sections become a single `.typ` file next to the PDF, then the compiler runs. Domain tokens set the paper, margins, type size, fonts, and whether headings are numbered.

```bash
python -m office_skill render plan.json -o note.pdf
```

A failed compile is a failed render. Math is Typst math inside `$ ... $` and cannot import or read files. Prose is escaped.

WeasyPrint (`pdf_engine: weasyprint`) builds a plain HTML document for a letter or a one-pager. It is an optional extra (`office-skill[weasy]`) and needs Pango and Cairo.

Do not use ReportLab for these documents. Do not flatten the PDF from a screenshot.
