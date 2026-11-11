import pytest

from engines.xlsx.compiler import compile_expr
from office_skill.plan import PlanError, validate_plan
from office_skill.profiles import load_profile


def test_compiler_emits_excel_and_rejects_xlookup():
    formula = compile_expr(
        "prev(ending)+openings*rev*(1+g)**year_index",
        col_index=1,
        row_cells={"ending": ["B6", "C6"], "openings": ["B7", "C7"]},
        assumptions={"rev": "'Assumptions'!$C$5", "g": "'Assumptions'!$C$6"},
        prev_base={"ending": "8"},
    )
    assert formula.startswith("=")
    assert "C6" in formula or "B6" in formula
    assert "^" in formula
    assert "XLOOKUP" not in formula
    with pytest.raises(PlanError):
        compile_expr(
            "XLOOKUP(1, A, B)",
            col_index=0,
            row_cells={},
            assumptions={},
            prev_base={},
        )


def test_plan_rejects_placeholder_and_unsourced_chart():
    profile = load_profile("consulting")
    bad = {
        "file_type": "pptx",
        "domain": "consulting",
        "language": "zh",
        "title": "Title",
        "slides": [
            {
                "primitive": "chart",
                "title": "Title",
                "categories": ["A"],
                "series": [{"name": "Value", "values": [1]}],
                "insight": "TODO fill this",
            }
        ],
    }
    with pytest.raises(PlanError):
        validate_plan(bad, profile)


def test_academic_requires_limitations():
    profile = load_profile("academic")
    plan = {
        "file_type": "pdf",
        "domain": "academic",
        "language": "en",
        "title": "Title",
        "sections": [{"heading": "Section 1", "blocks": [{"type": "paragraph", "text": "Text."}]}],
    }
    with pytest.raises(PlanError):
        validate_plan(plan, profile)
