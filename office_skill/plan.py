"""Validate the structured plan an agent writes before any shape is drawn."""

from __future__ import annotations

from office_skill.patterns import text_problems
from office_skill.profiles import load_profile

FILE_TYPES = {"pptx", "docx", "xlsx", "pdf"}
LANGUAGES = {"zh", "en"}

PPTX_PRIMITIVES = {
    "cover",
    "section",
    "action",
    "chart",
    "table",
    "matrix",
    "timeline",
    "comparison",
    "steps",
    "close",
}

DOCX_BLOCKS = {
    "heading",
    "paragraph",
    "definition",
    "quote",
    "table",
    "signature",
    "page_break",
}


class PlanError(ValueError):
    pass


def _walk_strings(value, path: str = "$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PlanError(message)


def validate_plan(plan: dict, profile: dict | None = None) -> dict:
    if not isinstance(plan, dict):
        raise PlanError("Plan must be a JSON object.")
    file_type = plan.get("file_type")
    _require(file_type in FILE_TYPES, f"file_type must be one of {sorted(FILE_TYPES)}.")
    _require(isinstance(plan.get("domain"), str) and plan["domain"], "domain is required.")
    _require(plan.get("language") in LANGUAGES, "language must be zh or en.")
    _require(isinstance(plan.get("title"), str) and plan["title"].strip(), "title is required.")
    if profile is None:
        profile = load_profile(plan["domain"])
    # Aliases are resolved by the caller before this point. The profile id is canonical.
    for path, text in _walk_strings(plan):
        problems = text_problems(text)
        if problems:
            raise PlanError(f"{path} contains {', '.join(problems)}.")
    if file_type == "pptx":
        _validate_pptx(plan)
    elif file_type == "docx":
        _validate_docx(plan)
    elif file_type == "xlsx":
        _validate_xlsx(plan)
    else:
        _validate_pdf(plan, profile)
    return plan


def _validate_pptx(plan: dict) -> None:
    slides = plan.get("slides")
    _require(isinstance(slides, list) and slides, "pptx plan needs slides.")
    _require(len(slides) <= 24, "A v1 deck is at most 24 slides.")
    for index, slide in enumerate(slides, start=1):
        kind = slide.get("primitive")
        _require(kind in PPTX_PRIMITIVES, f"Slide {index} has unknown primitive {kind!r}.")
        _require(isinstance(slide.get("title", ""), str), f"Slide {index} title must be a string.")
        if kind not in {"cover"}:
            _require(slide.get("title", "").strip(), f"Slide {index} needs a title.")
        if kind == "chart":
            categories = slide.get("categories")
            series = slide.get("series")
            _require(
                isinstance(categories, list) and categories, f"Slide {index} needs categories."
            )
            _require(isinstance(series, list) and series, f"Slide {index} needs series.")
            for item in series:
                values = item.get("values")
                _require(
                    isinstance(values, list) and len(values) == len(categories),
                    f"Slide {index} series length must match categories.",
                )
                _require(
                    all(isinstance(v, (int, float)) for v in values),
                    "Chart values must be numbers.",
                )
            _require(
                bool(slide.get("illustrative")) or bool(str(slide.get("source", "")).strip()),
                f"Slide {index} chart needs illustrative: true or a source.",
            )
        if kind == "matrix":
            _require(
                len(slide.get("quadrants", [])) == 4, f"Slide {index} matrix needs 4 quadrants."
            )
        if kind == "comparison":
            columns = slide.get("columns") or []
            _require(2 <= len(columns) <= 3, f"Slide {index} comparison needs 2 or 3 columns.")
        if kind == "timeline":
            _require(
                3 <= len(slide.get("items") or []) <= 6, f"Slide {index} timeline needs 3–6 items."
            )
        if kind == "steps":
            _require(
                3 <= len(slide.get("steps") or []) <= 4, f"Slide {index} steps needs 3 or 4 steps."
            )
        if kind == "table":
            rows = slide.get("rows") or []
            columns = slide.get("columns") or []
            _require(columns and rows, f"Slide {index} table is empty.")
            _require(len(rows) <= 8, f"Slide {index} table has too many rows for one slide.")
            for row in rows:
                _require(len(row) == len(columns), f"Slide {index} has a ragged table row.")
        if plan.get("domain") == "consulting" and kind not in {"cover", "section", "close"}:
            _require(
                bool(slide.get("illustrative")) or bool(str(slide.get("source", "")).strip()),
                f"Consulting slide {index} needs a source line or illustrative: true.",
            )


def _validate_docx(plan: dict) -> None:
    blocks = plan.get("blocks")
    _require(isinstance(blocks, list) and blocks, "docx plan needs blocks.")
    for index, block in enumerate(blocks, start=1):
        kind = block.get("type")
        _require(kind in DOCX_BLOCKS, f"Block {index} has unknown type {kind!r}.")
        if kind == "heading":
            _require(block.get("level") in {1, 2, 3}, f"Heading {index} level must be 1, 2, or 3.")
            _require(str(block.get("text", "")).strip(), f"Heading {index} is empty.")
        if kind == "table":
            _require(block.get("columns") and block.get("rows"), f"Table block {index} is empty.")
    if plan.get("doc_kind") == "gongwen" or plan.get("gongwen"):
        gongwen = plan.get("gongwen") or {}
        for key in ("org", "doc_number", "signoff", "date", "recipients"):
            _require(str(gongwen.get(key, "")).strip(), f"gongwen.{key} is required.")


def _validate_xlsx(plan: dict) -> None:
    assumptions = plan.get("assumptions")
    rows = plan.get("rows")
    years = plan.get("years")
    _require(
        isinstance(years, list) and 2 <= len(years) <= 8, "xlsx years must be a list of 2–8 labels."
    )
    _require(isinstance(assumptions, list) and assumptions, "xlsx plan needs assumptions.")
    _require(isinstance(rows, list) and rows, "xlsx plan needs rows.")
    _require(
        plan.get("illustrative") is True or plan.get("data_status") == "sourced",
        "Set illustrative: true, or data_status 'sourced' when every figure comes from the named sources.",
    )
    ids = set()
    for item in assumptions:
        _require(item.get("id") and item["id"] not in ids, "Assumption ids must be unique.")
        ids.add(item["id"])
        _require(
            isinstance(item.get("value"), (int, float)),
            f"Assumption {item.get('id')} needs a number.",
        )
        _require(
            str(item.get("source", "")).strip(), f"Assumption {item.get('id')} needs a source."
        )
        _require(str(item.get("label", "")).strip(), f"Assumption {item.get('id')} needs a label.")
    row_ids = set()
    for row in rows:
        _require(
            row.get("id") and row["id"] not in row_ids and row["id"] not in ids, "Row id collides."
        )
        row_ids.add(row["id"])
        if "values" in row:
            _require(len(row["values"]) == len(years), f"Row {row['id']} values must match years.")
        else:
            _require(str(row.get("expr", "")).strip(), f"Row {row['id']} needs expr or values.")
    for chart in plan.get("charts") or []:
        _require(
            chart.get("row") in row_ids or set(chart.get("rows") or []) <= row_ids,
            "Chart row is unknown.",
        )


def _validate_pdf(plan: dict, profile: dict) -> None:
    sections = plan.get("sections")
    _require(isinstance(sections, list) and sections, "pdf plan needs sections.")
    if plan.get("pdf_engine", "typst") not in {"typst", "weasyprint"}:
        raise PlanError("pdf_engine must be typst or weasyprint.")
    if profile["id"] == "academic":
        headings = " ".join(str(section.get("heading", "")) for section in sections).lower()
        _require(
            any(
                token in headings for token in ("limitation", "does not", "局限", "不足", "不说明")
            ),
            "An academic piece needs a limitations section.",
        )
        for ref in plan.get("references") or []:
            _require(
                "doi" not in ref,
                "Do not attach a DOI field unless you have verified it; omit the key.",
            )
            _require(
                str(ref.get("text", "")).strip() and str(ref.get("id", "")).strip(),
                "Broken reference.",
            )
