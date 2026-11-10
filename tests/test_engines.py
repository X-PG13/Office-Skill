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
    title = "一份具体的判断" if language == "zh" else "A specific claim about the work"
    return {
        "file_type": "pptx",
        "domain": domain,
        "language": language,
        "title": title,
        "slides": [{"primitive": "cover", "kicker": "Note", "title": title, "meta": "2026"}],
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
        "title": "关于违约金的法律意见书",
        "header_left": "事项",
        "header_right": "示例",
        "blocks": [
            {"type": "heading", "level": 1, "text": "范围"},
            {"type": "paragraph", "text": "只审阅了复印件。", "numbered": True},
            {"type": "definition", "term": "「合同」", "text": "指双方所称的买卖合同。"},
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
        "title": "临湾市教育局关于调整作息的通知",
        "gongwen": {
            "org": "临湾市教育局",
            "doc_number": "临教基〔2026〕1号",
            "recipients": "各学校：",
            "signoff": "临湾市教育局",
            "date": "2026年11月10日",
            "copy_to": "市财政局。",
            "print_org": "临湾市教育局办公室",
            "print_date": "2026年11月10日印发",
        },
        "blocks": [
            {"type": "paragraph", "level": 0, "text": "自下周一起执行。"},
            {"type": "paragraph", "level": 1, "text": "一、时间"},
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
        "title": "Tiny case",
        "illustrative": True,
        "years": ["Y0", "Y1"],
        "assumptions": [
            {
                "id": "g",
                "label": "Growth",
                "value": 0.1,
                "format": "0%",
                "unit": "rate",
                "note": "case",
                "source": "scenario",
            }
        ],
        "rows": [
            {"id": "base", "label": "Base", "values": [10, 10], "format": "0"},
            {"id": "rev", "label": "Revenue", "expr": "base*(1+g)**year_index", "format": "0.00"},
        ],
        "highlights": [{"label": "Y1", "row": "rev", "year_index": 1, "format": "0.00"}],
        "paragraphs": ["Illustrative."],
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
        "title": "A short note",
        "classification": "Discussion note",
        "authors": [{"name": "Ke Lin", "affiliation": "Independent"}],
        "sections": [
            {
                "heading": "Claim",
                "blocks": [{"type": "paragraph", "text": "The title should state the comparison."}],
            },
            {
                "heading": "What this note does not show",
                "blocks": [{"type": "paragraph", "text": "No experiment was run."}],
            },
        ],
        "references": [
            {
                "id": "cleveland1984",
                "label": "Cleveland and McGill, 1984",
                "text": "Cleveland, W. S., and McGill, R. (1984). Graphical Perception.",
            }
        ],
    }
    target = tmp_path / "note.pdf"
    render_plan(plan, target)
    assert check_pdf(target) == []
    assert "comparison" in (PdfReader(str(target)).pages[0].extract_text() or "")
    assert target.with_suffix(".typ").is_file()


def test_weasy_html_has_no_script_and_uses_the_ink():
    from engines.pdf.weasy import build_html

    profile = load_profile("legal")
    html = build_html(
        {
            "language": "en",
            "title": "A letter",
            "sections": [
                {
                    "heading": "Matter",
                    "blocks": [{"type": "paragraph", "text": "We read the copies."}],
                }
            ],
        },
        profile,
    )
    assert "<script" not in html.lower()
    assert profile["palette"]["ink"] in html


def test_bulk_dataframe_write(tmp_path: Path):
    from openpyxl import Workbook

    frame = pd.DataFrame({"Zone": ["Hub"], "Cost": [6.4]})
    wb = Workbook()
    write_dataframe(wb.active, frame)
    path = tmp_path / "t.xlsx"
    wb.save(path)
    again = load_workbook(path)
    assert again.active["A1"].value == "Zone"
    assert again.active["A2"].value == "Hub"
