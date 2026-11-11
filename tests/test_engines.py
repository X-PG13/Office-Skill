from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook
from pypdf import PdfReader

from engines.xlsx.bulk import write_dataframe
from office_skill.profiles import list_domains, load_profile
from office_skill.render import render_plan
from scripts.qa.checks import (
    check_docx,
    check_pdf,
    check_pptx,
    check_xlsx_recalc,
    check_xlsx_structure,
)
from scripts.qa.soffice import convert


def _cover(domain: str) -> dict:
    language = "zh" if domain in {"government", "education"} else "en"
    return {
        "file_type": "pptx",
        "domain": domain,
        "language": language,
        "title": "Title",
        "slides": [{"primitive": "cover", "kicker": "Note", "title": "Title", "meta": "1"}],
    }


@pytest.mark.parametrize("domain", list_domains())
def test_every_domain_renders_a_cover(domain, tmp_path: Path):
    target = tmp_path / "deck.pptx"
    render_plan(_cover(domain), target)
    issues = check_pptx(target, load_profile(domain))
    assert issues == []


def test_legal_docx_has_toc_numbering_and_east_asian_font(tmp_path: Path):
    plan = {
        "file_type": "docx",
        "domain": "legal",
        "language": "zh",
        "title": "Title",
        "header_left": "Left",
        "header_right": "Right",
        "blocks": [
            {"type": "heading", "level": 1, "text": "Section 1"},
            {"type": "paragraph", "text": "Section 1", "numbered": True},
            {"type": "definition", "term": "Term", "text": "Section 2"},
        ],
    }
    target = tmp_path / "note.docx"
    render_plan(plan, target)
    assert check_docx(target, load_profile("legal"), plan) == []
    from docx import Document

    xml = Document(str(target)).element.xml
    assert "TOC" in xml
    assert "w:numPr" in xml


def test_gongwen_uses_red_only_as_a_header_signal(tmp_path: Path):
    plan = {
        "file_type": "docx",
        "domain": "government",
        "language": "zh",
        "doc_kind": "gongwen",
        "title": "Title",
        "gongwen": {
            "org": "Org",
            "doc_number": "No. 1",
            "recipients": "To",
            "signoff": "Org",
            "date": "Date",
            "copy_to": "Copy",
            "print_org": "Org",
            "print_date": "Date",
        },
        "blocks": [
            {"type": "paragraph", "level": 0, "text": "Section 1"},
            {"type": "paragraph", "level": 1, "text": "Section 2"},
        ],
    }
    target = tmp_path / "notice.docx"
    render_plan(plan, target)
    assert check_docx(target, load_profile("government"), plan) == []


def test_xlsx_formulas_colors_and_recalc(tmp_path: Path):
    plan = {
        "file_type": "xlsx",
        "domain": "finance",
        "language": "en",
        "title": "Title",
        "illustrative": True,
        "years": ["A", "B"],
        "assumptions": [
            {
                "id": "g",
                "label": "Input",
                "value": 0.1,
                "format": "0%",
                "unit": "rate",
                "note": "note",
                "source": "source",
            }
        ],
        "rows": [
            {"id": "base", "label": "Row", "values": [1, 1], "format": "0"},
            {"id": "rev", "label": "Row 2", "expr": "base*(1+g)**year_index", "format": "0.00"},
        ],
        "highlights": [{"label": "B", "row": "rev", "year_index": 1, "format": "0.00"}],
        "paragraphs": ["Section 1"],
    }
    target = tmp_path / "m.xlsx"
    render_plan(plan, target)
    assert check_xlsx_structure(target) == []
    wb = load_workbook(target)
    formulas = [
        cell.value
        for ws in wb.worksheets
        for row in ws.iter_rows()
        for cell in row
        if isinstance(cell.value, str) and cell.value.startswith("=")
    ]
    assert formulas
    assert all("XLOOKUP" not in item.upper() for item in formulas)
    recalc = convert(target, tmp_path / "out", "xlsx")
    assert check_xlsx_recalc(recalc, target) == []


def test_academic_pdf_compiles(tmp_path: Path):
    plan = {
        "file_type": "pdf",
        "domain": "academic",
        "language": "en",
        "title": "Title",
        "classification": "Note",
        "authors": [{"name": "Author", "affiliation": "Org"}],
        "sections": [
            {
                "heading": "Section 1",
                "blocks": [{"type": "paragraph", "text": "Section 1"}],
            },
            {
                "heading": "Limitations",
                "blocks": [{"type": "paragraph", "text": "Section 2"}],
            },
        ],
        "references": [
            {
                "id": "ref1",
                "label": "Ref 1",
                "text": "Author. Title.",
            }
        ],
    }
    target = tmp_path / "note.pdf"
    render_plan(plan, target)
    assert check_pdf(target) == []
    assert "Section" in (PdfReader(str(target)).pages[0].extract_text() or "")
    assert target.with_suffix(".typ").is_file()


def test_weasy_html_has_no_script_and_uses_the_ink():
    from engines.pdf.weasy import build_html

    profile = load_profile("legal")
    html = build_html(
        {
            "language": "en",
            "title": "Title",
            "sections": [
                {
                    "heading": "Section 1",
                    "blocks": [{"type": "paragraph", "text": "Section 1"}],
                }
            ],
        },
        profile,
    )
    assert "<script" not in html.lower()
    assert profile["palette"]["ink"] in html


def test_bulk_dataframe_write(tmp_path: Path):
    from openpyxl import Workbook

    frame = pd.DataFrame({"Column": ["A"], "Value": [1]})
    wb = Workbook()
    write_dataframe(wb.active, frame)
    path = tmp_path / "t.xlsx"
    wb.save(path)
    again = load_workbook(path)
    assert again.active["A1"].value == "Column"
    assert again.active["A2"].value == "A"
