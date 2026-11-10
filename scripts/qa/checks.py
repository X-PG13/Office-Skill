"""Checks that do not require a screenshot."""

from __future__ import annotations

import zipfile
from pathlib import Path

from defusedxml import ElementTree as SafeTree
from lxml import etree

from office_skill.geometry import audit_slide
from office_skill.patterns import GENERIC_TITLES, text_problems
from office_skill.profiles import load_profile

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ANS = {"a": A_NS}
WNS = {"w": W_NS}
EXCEL_ERRORS = ("#REF!", "#NAME?", "#VALUE!", "#DIV/0!", "#NUM!", "#NULL!", "#N/A", "#GETTING_DATA")


def _color_rgb(color) -> str | None:
    if color is None or getattr(color, "type", None) == "theme":
        return None
    try:
        value = color.rgb
    except (AttributeError, ValueError, TypeError):
        return None
    if not value or not isinstance(value, str):
        return None
    return value[-6:].upper()


BANNED_FUNCS = ("XLOOKUP", "XMATCH", "FILTER(", "UNIQUE(", "SORT(", "SEQUENCE(")


def check_ooxml(path: Path) -> str | None:
    try:
        with zipfile.ZipFile(path) as package:
            names = package.namelist()
            if "[Content_Types].xml" not in names or "_rels/.rels" not in names:
                return "package is missing content types or the root relationships"
            for name in names:
                if name.endswith(".xml"):
                    SafeTree.fromstring(package.read(name))
    except (zipfile.BadZipFile, etree.XMLSyntaxError, OSError) as exc:
        return f"OOXML package is not valid: {exc}"
    return None


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        return _pptx_text(path)
    if suffix == ".docx":
        return _docx_text(path)
    if suffix == ".xlsx":
        return _xlsx_text(path)
    if suffix == ".pdf":
        return _pdf_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def placeholder_issues(text: str) -> list[str]:
    return text_problems(text)


def check_pptx(path: Path, profile: dict) -> list[str]:
    from pptx import Presentation
    from pptx.oxml.ns import qn

    prs = Presentation(str(path))
    issues: list[str] = []
    allowed_latin = {
        profile["type"]["pptx"]["latin"],
        profile["type"]["pptx"].get("mono", profile["type"]["pptx"]["latin"]),
    }
    allowed_ea = {profile["type"]["pptx"]["ea"]}
    for index, slide in enumerate(prs.slides, start=1):
        issues.extend(
            f"slide {index}: {item}"
            for item in audit_slide(slide, int(prs.slide_width), int(prs.slide_height))
        )
        issues.extend(_run_fonts(slide._element, allowed_latin, allowed_ea, f"slide {index}", qn))
        for shape in slide.shapes:
            if getattr(shape, "has_chart", False):
                issues.extend(
                    _run_fonts(
                        shape.chart.part._element,
                        allowed_latin,
                        allowed_ea,
                        f"slide {index} chart",
                        qn,
                    )
                )
                issues.extend(
                    _def_fonts(shape.chart.part._element, allowed_ea, f"slide {index} chart", qn)
                )
            name = getattr(shape, "name", "")
            if name in {"title", "cover-title"} and getattr(shape, "has_text_frame", False):
                title = " ".join(shape.text_frame.text.split())
                if title.casefold() in GENERIC_TITLES:
                    issues.append(f"slide {index} title is generic: {title}")
    return issues


def _run_fonts(element, allowed_latin: set[str], allowed_ea: set[str], label: str, qn) -> list[str]:
    issues = []
    for run in element.xpath(".//a:r"):
        texts = run.xpath("./a:t/text()")
        if not any(piece.strip() for piece in texts):
            continue
        r_pr = run.find(qn("a:rPr"))
        if r_pr is None:
            issues.append(f"{label}: a text run has no rPr")
            continue
        latin = r_pr.find(qn("a:latin"))
        ea = r_pr.find(qn("a:ea"))
        latin_face = latin.get("typeface") if latin is not None else ""
        ea_face = ea.get("typeface") if ea is not None else ""
        if latin_face not in allowed_latin:
            issues.append(f"{label}: latin face {latin_face!r} is not {sorted(allowed_latin)}")
        if ea_face not in allowed_ea:
            issues.append(f"{label}: East Asian face {ea_face!r} is not {sorted(allowed_ea)}")
    return issues


def _def_fonts(element, allowed_ea: set[str], label: str, qn) -> list[str]:
    issues = []
    nodes = element.xpath(".//a:defRPr")
    if not nodes:
        issues.append(f"{label}: chart text style has no defRPr, so CJK axis labels can fall back")
        return issues
    for node in nodes:
        ea = node.find(qn("a:ea"))
        face = ea.get("typeface") if ea is not None else ""
        if face not in allowed_ea:
            issues.append(f"{label}: chart defRPr East Asian face is {face!r}")
    return issues


def check_docx(path: Path, profile: dict, plan: dict | None) -> list[str]:
    from docx import Document
    from docx.oxml.ns import qn

    document = Document(str(path))
    issues: list[str] = []
    allowed_ea = {profile["type"]["docx"]["ea"]}
    if profile["type"]["docx"].get("ea_sans"):
        allowed_ea.add(profile["type"]["docx"]["ea_sans"])
    xml = document.element
    for run in xml.xpath(".//w:r"):
        texts = run.xpath("./w:t/text()")
        if not any(piece.strip() for piece in texts):
            continue
        r_pr = run.find(qn("w:rPr"))
        fonts = None if r_pr is None else r_pr.find(qn("w:rFonts"))
        face = fonts.get(qn("w:eastAsia")) if fonts is not None else ""
        if face not in allowed_ea:
            issues.append(f"run East Asian face {face!r} not in {sorted(allowed_ea)}")
            break
    if (
        plan
        and plan.get("include_toc", True)
        and not plan.get("gongwen")
        and plan.get("doc_kind") != "gongwen"
    ):
        blob = document.element.xml
        if "TOC" not in blob:
            issues.append("TOC field is missing")
    if plan and (plan.get("gongwen") or plan.get("doc_kind") == "gongwen"):
        if profile["palette"].get("header_red", "FF0000") not in document.element.xml:
            issues.append("公文 red is missing from the document")
    headings = [style.name for style in document.styles if style.name.startswith("Heading")]
    if (
        plan
        and not plan.get("gongwen")
        and plan.get("doc_kind") != "gongwen"
        and "Heading 1" not in headings
    ):
        issues.append("Heading 1 style is missing")
    return issues


def check_xlsx_structure(path: Path) -> list[str]:
    from openpyxl import load_workbook

    wb = load_workbook(path)
    issues = []
    formulas = []
    has_blue = False
    has_yellow = False
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                value = cell.value
                if isinstance(value, str) and value.startswith("="):
                    formulas.append(value.upper())
                    for banned in BANNED_FUNCS:
                        if banned in value.upper():
                            issues.append(f"{ws.title}!{cell.coordinate} uses {banned}")
                font_color = _color_rgb(cell.font.color if cell.font is not None else None)
                if font_color == "0000FF":
                    has_blue = True
                fill = _color_rgb(cell.fill.fgColor if cell.fill is not None else None)
                if fill == "FFFF99":
                    has_yellow = True
    if not formulas:
        issues.append("workbook has no formulas")
    if not has_blue or not has_yellow:
        issues.append("workbook is missing blue inputs or yellow assumption fill")
    return issues


def check_xlsx_recalc(recalc_path: Path, original_path: Path) -> list[str]:
    from openpyxl import load_workbook

    original = load_workbook(original_path)
    cached = load_workbook(recalc_path, data_only=True)
    issues = []
    for ws in original.worksheets:
        other = cached[ws.title]
        for row in ws.iter_rows():
            for cell in row:
                if not (isinstance(cell.value, str) and cell.value.startswith("=")):
                    continue
                value = other[cell.coordinate].value
                if value is None:
                    issues.append(f"{ws.title}!{cell.coordinate} has no cached value after recalc")
                elif isinstance(value, str) and any(
                    value.upper().startswith(err) for err in EXCEL_ERRORS
                ):
                    issues.append(f"{ws.title}!{cell.coordinate} -> {value}")
    return issues[:40]


def check_pdf(path: Path) -> list[str]:
    from pypdf import PdfReader

    raw = path.read_bytes()[:5]
    if raw != b"%PDF-":
        return ["file does not start with %PDF"]
    reader = PdfReader(str(path))
    if len(reader.pages) < 1:
        return ["PDF has no pages"]
    return []


def compile_typst(source: Path) -> str | None:
    import tempfile

    import typst

    try:
        with tempfile.TemporaryDirectory(prefix="office-skill-typst-") as tmp:
            typst.compile(str(source), output=str(Path(tmp) / "compiled.pdf"))
    except typst.TypstError as exc:
        return str(exc)
    return None


def profile_for(plan: dict | None, path: Path) -> dict | None:
    if plan and plan.get("domain"):
        return load_profile(plan["domain"])
    return None


def _pptx_text(path: Path) -> str:
    from pptx import Presentation

    prs = Presentation(str(path))
    chunks: list[str] = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False):
                chunks.append(shape.text_frame.text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        chunks.append(cell.text)
    return "\n".join(chunks)


def _docx_text(path: Path) -> str:
    from docx import Document

    document = Document(str(path))
    chunks = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                chunks.append(cell.text)
    return "\n".join(chunks)


def _xlsx_text(path: Path) -> str:
    from openpyxl import load_workbook

    wb = load_workbook(path, data_only=False)
    chunks = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            for value in row:
                if value is not None:
                    chunks.append(str(value))
    return "\n".join(chunks)


def _pdf_text(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)
