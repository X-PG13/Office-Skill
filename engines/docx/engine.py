"""DOCX renderer.

Legal memos get real heading styles, a TOC field, and numbered paragraphs.
公文 follows the public GB/T 9704 measurements with open-license font fallbacks.
"""

from __future__ import annotations

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor, Twips

from office_skill.plan import PlanError


def render(plan: dict, profile: dict, out_path) -> None:
    document = Document()
    _set_core(document, plan, profile)
    if plan.get("doc_kind") == "gongwen" or plan.get("gongwen"):
        _render_gongwen(document, plan, profile)
    else:
        _render_prose(document, plan, profile)
    _ask_word_to_update_fields(document)
    document.save(str(out_path))


def _set_core(document: Document, plan: dict, profile: dict) -> None:
    props = document.core_properties
    props.title = plan["title"]
    props.author = plan.get("author", "")
    props.subject = profile["id"]
    props.category = plan.get("doc_kind", plan["file_type"])


def _font(
    run, latin: str, ea: str, size_pt: float, *, bold=False, italic=False, color="111111"
) -> None:
    run.font.name = latin
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.insert(0, r_fonts)
    r_fonts.set(qn("w:ascii"), latin)
    r_fonts.set(qn("w:hAnsi"), latin)
    r_fonts.set(qn("w:cs"), latin)
    r_fonts.set(qn("w:eastAsia"), ea)
    lang = r_pr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        r_pr.append(lang)
    lang.set(qn("w:val"), "en-US")
    lang.set(qn("w:eastAsia"), "zh-CN")


def _mark(paragraph, latin: str, ea: str, size_pt: float, *, bold=False) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    r_pr = p_pr.find(qn("w:rPr"))
    if r_pr is None:
        r_pr = OxmlElement("w:rPr")
        p_pr.append(r_pr)
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), latin)
    r_fonts.set(qn("w:hAnsi"), latin)
    r_fonts.set(qn("w:eastAsia"), ea)
    r_fonts.set(qn("w:cs"), latin)
    size = str(int(round(size_pt * 2)))
    for tag in ("w:sz", "w:szCs"):
        node = r_pr.find(qn(tag))
        if node is None:
            node = OxmlElement(tag)
            r_pr.append(node)
        node.set(qn("w:val"), size)
    if bold:
        if r_pr.find(qn("w:b")) is None:
            r_pr.append(OxmlElement("w:b"))


def _doc_defaults(document: Document, latin: str, ea: str, size_pt: float) -> None:
    styles = document.styles.element
    defaults = styles.find(qn("w:docDefaults"))
    if defaults is None:
        defaults = OxmlElement("w:docDefaults")
        styles.insert(0, defaults)
    r_default = defaults.find(qn("w:rPrDefault"))
    if r_default is None:
        r_default = OxmlElement("w:rPrDefault")
        defaults.append(r_default)
    r_pr = r_default.find(qn("w:rPr"))
    if r_pr is None:
        r_pr = OxmlElement("w:rPr")
        r_default.append(r_pr)
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), latin)
    r_fonts.set(qn("w:hAnsi"), latin)
    r_fonts.set(qn("w:eastAsia"), ea)
    r_fonts.set(qn("w:cs"), latin)
    existing = r_pr.find(qn("w:rFonts"))
    if existing is not None:
        r_pr.remove(existing)
    r_pr.append(r_fonts)
    half = str(int(round(size_pt * 2)))
    for tag in ("w:sz", "w:szCs"):
        node = r_pr.find(qn(tag))
        if node is None:
            node = OxmlElement(tag)
            r_pr.append(node)
        node.set(qn("w:val"), half)
    lang = r_pr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        r_pr.append(lang)
    lang.set(qn("w:val"), "en-US")
    lang.set(qn("w:eastAsia"), "zh-CN")


def _style_font(style, latin: str, ea: str, size_pt: float, *, bold=None, color="111111") -> None:
    style.font.name = latin
    style.font.size = Pt(size_pt)
    style.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        style.font.bold = bold
    r_pr = style.element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), latin)
    r_fonts.set(qn("w:hAnsi"), latin)
    r_fonts.set(qn("w:eastAsia"), ea)
    r_fonts.set(qn("w:cs"), latin)


def _apply_numbering(paragraph, level: int) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    existing = p_pr.find(qn("w:numPr"))
    if existing is not None:
        p_pr.remove(existing)
    num_pr = OxmlElement("w:numPr")
    ilvl = OxmlElement("w:ilvl")
    ilvl.set(qn("w:val"), str(level))
    num_id = OxmlElement("w:numId")
    num_id.set(qn("w:val"), "1")
    num_pr.append(ilvl)
    num_pr.append(num_id)
    p_pr.append(num_pr)


def _install_numbering(document: Document, latin: str, ea: str) -> None:
    numbering = document.part.numbering_part._element
    for child in list(numbering):
        numbering.remove(child)
    xml = f"""
    <w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:abstractNum w:abstractNumId="1">
        <w:multiLevelType w:val="multilevel"/>
        <w:lvl w:ilvl="0">
          <w:start w:val="1"/>
          <w:numFmt w:val="decimal"/>
          <w:lvlText w:val="%1."/>
          <w:lvlJc w:val="left"/>
          <w:pPr><w:ind w:left="420" w:hanging="420"/></w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="{latin}" w:hAnsi="{latin}" w:eastAsia="{ea}" w:cs="{latin}"/>
          </w:rPr>
        </w:lvl>
        <w:lvl w:ilvl="1">
          <w:start w:val="1"/>
          <w:numFmt w:val="lowerLetter"/>
          <w:lvlText w:val="(%2)"/>
          <w:lvlJc w:val="left"/>
          <w:pPr><w:ind w:left="840" w:hanging="420"/></w:pPr>
          <w:rPr>
            <w:rFonts w:ascii="{latin}" w:hAnsi="{latin}" w:eastAsia="{ea}" w:cs="{latin}"/>
          </w:rPr>
        </w:lvl>
      </w:abstractNum>
      <w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>
    </w:numbering>
    """
    parsed = parse_xml(xml)
    for child in list(parsed):
        numbering.append(child)


def _paragraph_border(paragraph, *, color="222222", edge="left", size="8") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    node = OxmlElement(f"w:{edge}")
    node.set(qn("w:val"), "single")
    node.set(qn("w:sz"), size)
    node.set(qn("w:space"), "8")
    node.set(qn("w:color"), color)
    borders.append(node)


def _add_field(
    paragraph, instruction: str, latin: str, ea: str, size: float, cached: str = ""
) -> None:
    begin = paragraph.add_run()
    _font(begin, latin, ea, size)
    fld = OxmlElement("w:fldChar")
    fld.set(qn("w:fldCharType"), "begin")
    begin._r.append(fld)
    instr = paragraph.add_run()
    _font(instr, latin, ea, size)
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = instruction
    instr._r.append(instr_text)
    separate = paragraph.add_run()
    _font(separate, latin, ea, size)
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    separate._r.append(sep)
    if cached:
        shown = paragraph.add_run(cached)
        _font(shown, latin, ea, size)
    end = paragraph.add_run()
    _font(end, latin, ea, size)
    end_el = OxmlElement("w:fldChar")
    end_el.set(qn("w:fldCharType"), "end")
    end._r.append(end_el)


def _ask_word_to_update_fields(document: Document) -> None:
    settings = document.settings.element
    node = OxmlElement("w:updateFields")
    node.set(qn("w:val"), "true")
    settings.append(node)


def _page_setup(section, margins: dict, header_mm: float, footer_mm: float) -> None:
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.top_margin = Mm(margins["top"])
    section.bottom_margin = Mm(margins["bottom"])
    section.left_margin = Mm(margins["left"])
    section.right_margin = Mm(margins["right"])
    section.header_distance = Mm(header_mm)
    section.footer_distance = Mm(footer_mm)


def _header_footer(section, plan: dict, latin: str, ea: str, *, gongwen: bool) -> None:
    header = section.header
    header.is_linked_to_previous = False
    paragraph = header.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if not gongwen:
        width = section.page_width - section.left_margin - section.right_margin
        paragraph.paragraph_format.tab_stops.add_tab_stop(width, WD_TAB_ALIGNMENT.RIGHT)
        left = plan.get("header_left", "")
        right = plan.get("header_right", "")
        if left:
            run = paragraph.add_run(left)
            _font(run, latin, ea, 9, color="444444")
        if right:
            run = paragraph.add_run("\t" + right)
            _font(run, latin, ea, 9, color="444444")
        _mark(paragraph, latin, ea, 9)
    footer = section.footer
    footer.is_linked_to_previous = False
    foot = footer.paragraphs[0]
    foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if gongwen:
        run = foot.add_run("— ")
        _font(run, latin, ea, 14)
        _add_field(foot, " PAGE ", latin, ea, 14, cached="1")
        run = foot.add_run(" —")
        _font(run, latin, ea, 14)
        _mark(foot, latin, ea, 14)
    else:
        _add_field(foot, " PAGE ", latin, ea, 9, cached="1")
        _mark(foot, latin, ea, 9)


def _configure_styles(document: Document, latin: str, ea: str, body_pt: float) -> None:
    _doc_defaults(document, latin, ea, body_pt)
    normal = document.styles["Normal"]
    _style_font(normal, latin, ea, body_pt, bold=False)
    normal.paragraph_format.space_after = Pt(8)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.15
    for level, size, before in ((1, 16, 16), (2, 13, 12), (3, 12, 10)):
        style = document.styles[f"Heading {level}"]
        _style_font(style, latin, ea, size, bold=True)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.15
    caption = document.styles["Caption"]
    _style_font(caption, latin, ea, 10.5, bold=False, color="333333")
    caption.paragraph_format.space_before = Pt(10)
    caption.paragraph_format.space_after = Pt(4)


def _render_prose(document: Document, plan: dict, profile: dict) -> None:
    fonts = profile["type"]["docx"]
    latin, ea = fonts["latin"], fonts["ea"]
    body_pt = float(fonts.get("body_pt", 12))
    _configure_styles(document, latin, ea, body_pt)
    if plan.get("numbering", "legal") == "legal":
        _install_numbering(document, latin, ea)
    section = document.sections[0]
    margins = profile["page"]["docx"]["margins_mm"]
    _page_setup(section, margins, 12, 12)
    _header_footer(section, plan, latin, ea, gongwen=False)
    _add_title_block(document, plan, latin, ea)
    if plan.get("include_toc", True):
        label = "目录" if plan["language"] == "zh" else "Contents"
        paragraph = document.add_paragraph()
        run = paragraph.add_run(label)
        _font(run, latin, ea, 16, bold=True)
        _mark(paragraph, latin, ea, 16, bold=True)
        paragraph.paragraph_format.space_before = Pt(6)
        paragraph.paragraph_format.space_after = Pt(6)
        headings = [block["text"] for block in plan["blocks"] if block.get("type") == "heading"]
        toc = document.add_paragraph()
        cached = "  ·  ".join(headings)
        _add_field(toc, ' TOC \\o "1-2" \\h \\z \\u ', latin, ea, 11, cached=cached)
        _mark(toc, latin, ea, 11)
        toc.paragraph_format.space_after = Pt(12)
    table_no = 0
    for block in plan["blocks"]:
        kind = block["type"]
        if kind == "heading":
            paragraph = document.add_heading(block["text"], level=int(block["level"]))
            for run in paragraph.runs:
                _font(run, latin, ea, {1: 16, 2: 13, 3: 12}[int(block["level"])], bold=True)
            _mark(paragraph, latin, ea, {1: 16, 2: 13, 3: 12}[int(block["level"])], bold=True)
        elif kind == "paragraph":
            paragraph = document.add_paragraph()
            run = paragraph.add_run(block.get("text", ""))
            _font(run, latin, ea, body_pt)
            _mark(paragraph, latin, ea, body_pt)
            paragraph.paragraph_format.space_after = Pt(8)
            paragraph.paragraph_format.line_spacing = 1.15
            if block.get("numbered"):
                _apply_numbering(paragraph, int(block.get("level", 0)))
        elif kind == "definition":
            paragraph = document.add_paragraph()
            term = paragraph.add_run(block["term"])
            _font(term, latin, ea, body_pt, bold=True)
            body = paragraph.add_run(block.get("text", ""))
            _font(body, latin, ea, body_pt)
            _mark(paragraph, latin, ea, body_pt)
            paragraph.paragraph_format.space_after = Pt(8)
            paragraph.paragraph_format.line_spacing = 1.15
        elif kind == "quote":
            paragraph = document.add_paragraph()
            run = paragraph.add_run(block.get("text", ""))
            _font(run, latin, ea, body_pt - 0.5)
            _mark(paragraph, latin, ea, body_pt)
            paragraph.paragraph_format.left_indent = Cm(0.75)
            paragraph.paragraph_format.right_indent = Cm(0.4)
            paragraph.paragraph_format.space_before = Pt(6)
            paragraph.paragraph_format.space_after = Pt(2)
            _paragraph_border(paragraph)
            if block.get("cite"):
                cite = document.add_paragraph()
                run = cite.add_run(block["cite"])
                _font(run, latin, ea, 10.5, color="444444")
                _mark(cite, latin, ea, 10.5)
                cite.paragraph_format.left_indent = Cm(0.75)
                cite.paragraph_format.space_after = Pt(8)
        elif kind == "table":
            table_no += 1
            caption = document.add_paragraph(style="Caption")
            prefix = "表" if plan["language"] == "zh" else "Table"
            run = caption.add_run(f"{prefix} {table_no}  {block.get('caption', '')}")
            _font(run, latin, ea, 10.5, color="333333")
            _mark(caption, latin, ea, 10.5)
            _write_table(document, block, latin, ea)
        elif kind == "signature":
            for line_index, line in enumerate(block.get("lines") or []):
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                run = paragraph.add_run(line)
                _font(run, latin, ea, body_pt)
                _mark(paragraph, latin, ea, body_pt)
                paragraph.paragraph_format.space_before = Pt(16 if line_index == 0 else 0)
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.right_indent = Cm(1.2)
        elif kind == "page_break":
            document.add_page_break()
        else:
            raise PlanError(f"Unhandled block {kind}")


def _add_title_block(document: Document, plan: dict, latin: str, ea: str) -> None:
    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run(plan["title"])
    _font(run, latin, ea, 18, bold=True)
    _mark(title, latin, ea, 18, bold=True)
    title.paragraph_format.space_after = Pt(4)
    if plan.get("subtitle"):
        subtitle = document.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = subtitle.add_run(plan["subtitle"])
        _font(run, latin, ea, 12, color="333333")
        _mark(subtitle, latin, ea, 12)
        subtitle.paragraph_format.space_after = Pt(2)
    meta = plan.get("meta") or []
    if isinstance(meta, str):
        meta = [meta]
    if meta:
        line = document.add_paragraph()
        line.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = line.add_run("  ·  ".join(meta))
        _font(run, latin, ea, 10.5, color="444444")
        _mark(line, latin, ea, 10.5)
        line.paragraph_format.space_after = Pt(8)


def _write_table(document: Document, block: dict, latin: str, ea: str) -> None:
    columns = block["columns"]
    rows = block["rows"]
    table = document.add_table(rows=1 + len(rows), cols=len(columns))
    table.alignment = 1  # center; WD_TABLE_ALIGNMENT.CENTER == 1
    table.autofit = False
    _set_table_width(table, columns)
    _set_table_borders(table)
    for index, header in enumerate(columns):
        _cell(table.rows[0].cells[index], header, latin, ea, 10.5, bold=True)
    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row):
            _cell(table.rows[row_index].cells[col_index], value, latin, ea, 10.5, bold=False)


def _cell(cell, text, latin, ea, size, *, bold) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run("" if text is None else str(text))
    _font(run, latin, ea, size, bold=bold)
    _mark(paragraph, latin, ea, size, bold=bold)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0


def _set_table_width(table, columns) -> None:
    total = 8800
    each = total // len(columns)
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), "8800")
    tbl_w.set(qn("w:type"), "dxa")
    for cell_width, cell in zip([each] * len(columns), table.rows[0].cells, strict=True):
        _ = cell_width
    for column in table.columns:
        column.width = Twips(each)


def _set_table_borders(table, color="222222") -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{edge}")
        if edge in {"top", "bottom", "insideH"}:
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), "8" if edge != "top" else "12")
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), color)
        else:
            node.set(qn("w:val"), "nil")
        borders.append(node)
    tbl_pr.append(borders)


def _render_gongwen(document: Document, plan: dict, profile: dict) -> None:
    fonts = profile["type"]["docx"]
    latin = fonts["latin"]
    serif = fonts["ea"]
    sans = fonts.get("ea_sans", serif)
    red = profile["palette"].get("header_red", "FF0000")
    _doc_defaults(document, latin, serif, 16)
    normal = document.styles["Normal"]
    _style_font(normal, latin, serif, 16, bold=False)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    normal.paragraph_format.line_spacing = Pt(28)
    section = document.sections[0]
    margins = profile["page"]["docx"]["margins_mm"]
    _page_setup(section, margins, 15, 12)
    _header_footer(section, plan, latin, serif, gongwen=True)
    meta = plan["gongwen"]
    _gongwen_line(
        document, meta["org"], latin, serif, 26, align="center", color=red, bold=False, exact=36
    )
    _gongwen_line(document, "", latin, serif, 16, exact=28)
    number = _gongwen_line(document, meta["doc_number"], latin, serif, 16, align="center", exact=28)
    _paragraph_border(number, color=red, edge="bottom", size="18")
    _gongwen_line(document, "", latin, serif, 16, exact=16)
    _gongwen_line(document, plan["title"], latin, serif, 22, align="center", bold=True, exact=32)
    _gongwen_line(document, "", latin, serif, 16, exact=28)
    _gongwen_line(document, meta["recipients"], latin, serif, 16, exact=28)
    for block in plan["blocks"]:
        if block["type"] == "paragraph":
            level = int(block.get("level", 0))
            ea = sans if level == 1 else serif
            bold = level == 1
            paragraph = _gongwen_line(
                document,
                block.get("text", ""),
                latin,
                ea,
                16,
                bold=bold,
                exact=28,
                indent=level == 0,
            )
            if level == 0:
                paragraph.paragraph_format.first_line_indent = Pt(32)
        elif block["type"] == "page_break":
            document.add_page_break()
        else:
            raise PlanError("公文 body blocks are paragraphs (the header is the gongwen object).")
    _gongwen_line(document, "", latin, serif, 16, exact=28)
    sign = _gongwen_line(document, meta["signoff"], latin, serif, 16, align="right", exact=28)
    sign.paragraph_format.right_indent = Cm(2.26)
    dated = _gongwen_line(document, meta["date"], latin, serif, 16, align="right", exact=28)
    dated.paragraph_format.right_indent = Cm(2.26)
    _gongwen_line(document, "", latin, serif, 16, exact=28)
    _banji(document, meta, latin, serif)


def _gongwen_line(
    document,
    text,
    latin,
    ea,
    size,
    *,
    align="left",
    color="000000",
    bold=False,
    exact=28,
    indent=False,
):
    paragraph = document.add_paragraph()
    paragraph.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    paragraph.paragraph_format.line_spacing = Pt(exact)
    if text:
        run = paragraph.add_run(text)
        _font(run, latin, ea, size, bold=bold, color=color)
    _mark(paragraph, latin, ea, size, bold=bold)
    _ = indent
    return paragraph


def _banji(document: Document, meta: dict, latin: str, ea: str) -> None:
    table = document.add_table(rows=2, cols=2)
    table.autofit = False
    _set_table_width(table, ["a", "b"])
    copy = meta.get("copy_to", "")
    printed = meta.get("print_org", meta["signoff"])
    printed_on = meta.get("print_date", meta["date"] + "印发")
    table.rows[0].cells[0].merge(table.rows[0].cells[1])
    _cell(table.rows[0].cells[0], f"抄送：{copy}" if copy else "抄送：", latin, ea, 14, bold=False)
    _cell(table.rows[1].cells[0], printed, latin, ea, 14, bold=False)
    cell = table.rows[1].cells[1]
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run(printed_on)
    _font(run, latin, ea, 14)
    _mark(paragraph, latin, ea, 14)
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{edge}")
        if edge in {"top", "bottom", "insideH"}:
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), "12")
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), "000000")
        else:
            node.set(qn("w:val"), "nil")
        borders.append(node)
    tbl_pr.append(borders)
