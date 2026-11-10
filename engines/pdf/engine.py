"""Typst PDF renderer.

The plan is content. This module owns the template, the type scale, and the
page geometry from the domain profile.
"""

from __future__ import annotations

import re
from pathlib import Path

import typst

from office_skill.plan import PlanError

_CITE = re.compile(r"\[@([A-Za-z0-9_-]+)\]")
_MATH_BANNED = ("#", "import", "include", "read(", "eval(")


def render(plan: dict, profile: dict, out_path) -> None:
    engine = plan.get("pdf_engine", "typst")
    if engine == "weasyprint":
        from engines.pdf.weasy import render_weasy

        render_weasy(plan, profile, out_path)
        return
    if engine != "typst":
        raise PlanError(f"Unknown pdf engine {engine!r}.")
    source = build_typst(plan, profile)
    target = Path(out_path)
    typst_path = target.with_suffix(".typ")
    typst_path.write_text(source, encoding="utf-8")
    try:
        typst.compile(str(typst_path), output=str(target))
    except typst.TypstError as exc:
        raise PlanError(f"Typst failed to compile {typst_path.name}: {exc}") from exc


def build_typst(plan: dict, profile: dict) -> str:
    pdf = profile["type"]["pdf"]
    page = profile["page"]["pdf"]
    margins = page["margins_mm"]
    palette = profile["palette"]
    language = plan["language"]
    body_font = pdf["latin"] if language == "en" else pdf["ea"]
    alt_font = pdf["ea"] if language == "en" else pdf["latin"]
    sans = pdf.get("sans", "Liberation Sans")
    ea_sans = pdf.get("ea_sans", "Noto Sans CJK SC")
    body_pt = pdf.get("body_pt", 11)
    heading_pt = pdf.get("heading_pt", 14)
    justify = "true" if pdf.get("justify", True) else "false"
    indent = float(pdf.get("first_line_indent_em", 0))
    numbering = '"1.1"' if pdf.get("number_headings", True) else "none"
    lang = "zh" if language == "zh" else "en"
    region = "CN" if language == "zh" else "US"
    refs = {item["id"]: item for item in plan.get("references") or []}
    parts = [
        f"""#set document(title: [{_inline(plan["title"], refs)}], author: ({_authors(plan)}))
#set page(
  paper: "{page["paper"]}",
  margin: (top: {margins["top"]}mm, bottom: {margins["bottom"]}mm, left: {margins["left"]}mm, right: {margins["right"]}mm),
  header: context {{
    if counter(page).get().first() > 1 {{
      text(size: 9pt, fill: rgb("#{palette["muted"]}"), font: ("{sans}", "{ea_sans}"))[
        {_inline(plan.get("running_head") or plan["title"], refs)}
        #h(1fr)
        {_inline(plan.get("classification", ""), refs)}
      ]
    }}
  }},
  footer: context {{
    align(center, text(size: 9pt, fill: rgb("#{palette["muted"]}"))[
      #counter(page).display("1")
    ])
  }},
)
#set text(font: ("{body_font}", "{alt_font}"), size: {body_pt}pt, lang: "{lang}", region: "{region}", fill: rgb("#{palette["ink"]}"))
#set par(justify: {justify}, leading: 0.78em, spacing: 0.72em, first-line-indent: {indent}em)
#set heading(numbering: {numbering})
#show heading.where(level: 1): it => {{
  set text(font: ("{ea_sans if language == "zh" else sans}", "{sans}"), size: {heading_pt}pt, fill: rgb("#{palette["ink"]}"))
  set par(first-line-indent: 0em)
  block(above: 1.35em, below: 0.55em, it)
}}
#show heading.where(level: 2): it => {{
  set text(font: ("{ea_sans if language == "zh" else sans}", "{sans}"), size: {heading_pt - 2}pt)
  set par(first-line-indent: 0em)
  block(above: 1.1em, below: 0.4em, it)
}}
"""
    ]
    parts.append(_front(plan, refs, palette, sans, ea_sans))
    parts.append(f"#set par(first-line-indent: {indent}em)")
    for section in plan["sections"]:
        level = int(section.get("level", 1))
        numbering_override = "none" if section.get("unnumbered") else numbering
        parts.append(
            f"#heading(level: {level}, numbering: {numbering_override})[{_inline(section['heading'], refs)}]"
        )
        for block in section.get("blocks") or []:
            parts.append(_block(block, refs, palette))
    if plan.get("references"):
        parts.append(
            "#heading(level: 1, numbering: none)[References]"
            if language == "en"
            else "#heading(level: 1, numbering: none)[参考文献]"
        )
        parts.append("#set par(first-line-indent: 0em, hanging-indent: 1.1em, spacing: 0.55em)")
        for ref in plan["references"]:
            parts.append(f"#block(below: 0.45em)[{_inline(ref['text'], {})}]")
    return "\n".join(parts) + "\n"


def _authors(plan: dict) -> str:
    authors = plan.get("authors") or []
    if not authors:
        return f'"{_escape(plan.get("author", ""))}"'
    rendered = []
    for author in authors:
        if isinstance(author, str):
            rendered.append(f'"{_escape(author)}"')
        else:
            rendered.append(f'"{_escape(author.get("name", ""))}"')
    return ", ".join(rendered)


def _front(plan: dict, refs: dict, palette: dict, sans: str, ea_sans: str) -> str:
    lines = ["#set par(first-line-indent: 0em)"]
    if plan.get("classification"):
        lines.append(
            f'#text(size: 9pt, fill: rgb("#{palette["muted"]}"), font: ("{sans}", "{ea_sans}"))[{_inline(plan["classification"], refs)}]'
        )
    lines.append(f'#text(size: 20pt, weight: "bold")[{_inline(plan["title"], refs)}]')
    if plan.get("subtitle"):
        lines.append(
            f'#text(size: 12pt, fill: rgb("#{palette["muted"]}"))[{_inline(plan["subtitle"], refs)}]'
        )
    byline = []
    for author in plan.get("authors") or []:
        if isinstance(author, str):
            byline.append(author)
        else:
            name = author.get("name", "")
            aff = author.get("affiliation", "")
            byline.append(f"{name}, {aff}" if aff else name)
    meta = []
    if byline:
        meta.append("; ".join(byline))
    if plan.get("date"):
        meta.append(plan["date"])
    if meta:
        lines.append(f"#text(size: 10.5pt)[{_inline('  ·  '.join(meta), refs)}]")
    if plan.get("abstract"):
        label = "Abstract" if plan["language"] == "en" else "摘要"
        lines.append(
            f'#v(0.9em)\n#text(weight: "bold")[{label}] #h(0.6em) {_inline(plan["abstract"], refs)}'
        )
    if plan.get("keywords"):
        label = "Keywords" if plan["language"] == "en" else "关键词"
        words = (
            "; ".join(plan["keywords"]) if plan["language"] == "en" else "；".join(plan["keywords"])
        )
        lines.append(
            f'#text(size: 10.5pt, fill: rgb("#{palette["muted"]}"))[{label}  {_inline(words, refs)}]'
        )
    lines.append("#v(0.2em)")
    return "\n\n".join(lines)


def _block(block: dict, refs: dict, palette: dict) -> str:
    kind = block["type"]
    if kind == "paragraph":
        return _inline(block.get("text", ""), refs)
    if kind == "list":
        items = "\n".join(f"+ {_inline(item, refs)}" for item in block.get("items") or [])
        return '#set enum(numbering: "1.", indent: 0.5em, body-indent: 0.4em)\n' + items
    if kind == "quote":
        body = _inline(block.get("text", ""), refs)
        cite = _inline(block.get("cite", ""), refs)
        return f"#block(inset: (left: 10pt, y: 2pt))[{body}]" + (
            f'\n#text(size: 9.5pt, fill: rgb("#{palette["muted"]}"))[{cite}]' if cite else ""
        )
    if kind == "math":
        expr = block.get("tex", "")
        for banned in _MATH_BANNED:
            if banned in expr:
                raise PlanError("Math blocks cannot import, read, or embed Typst scripts.")
        return f"$ {expr} $"
    if kind == "table":
        return _table(block, refs, palette)
    if kind == "page_break":
        return "#pagebreak()"
    raise PlanError(f"Unknown PDF block {kind!r}.")


def _table(block: dict, refs: dict, palette: dict) -> str:
    columns = block["columns"]
    spec = ", ".join(["1fr"] * len(columns))
    aligns = block.get("aligns") or (["left"] + ["right"] * (len(columns) - 1))
    align_src = ", ".join(aligns)
    cells = ["[* " + _inline(col, refs) + " *]" for col in columns]
    cells.append("table.hline(stroke: 0.8pt)")
    for row_index, row in enumerate(block["rows"]):
        for value in row:
            cells.append("[" + _inline(str(value), refs) + "]")
        if row_index != len(block["rows"]) - 1:
            cells.append(f'table.hline(stroke: 0.3pt + rgb("#{palette["line"]}"))')
    caption = _inline(block.get("caption", ""), refs)
    body = ",\n  ".join(cells)
    return f"""#figure(
  caption: [{caption}],
  table(
    columns: ({spec}),
    stroke: none,
    inset: (x: 7pt, y: 5pt),
    align: ({align_src}),
    {body},
  ),
)"""


def _inline(text: str, refs: dict) -> str:
    if text is None:
        return ""

    def replace(match: re.Match) -> str:
        key = match.group(1)
        if key not in refs:
            raise PlanError(f"Unknown citation @{key}.")
        return "(" + refs[key]["label"] + ")"

    replaced = _CITE.sub(replace, str(text))
    return _escape(replaced).replace("\n", " \\ ")


def _escape(text: str) -> str:
    mapping = {
        "\\": "\\\\",
        "[": "\\[",
        "]": "\\]",
        "#": "\\#",
        "$": "\\$",
        "<": "\\<",
        ">": "\\>",
        "*": "\\*",
        "_": "\\_",
        "`": "\\`",
        "@": "\\@",
    }
    return "".join(mapping.get(ch, ch) for ch in text)
