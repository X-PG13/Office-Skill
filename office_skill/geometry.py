"""Shared fit and bounds checks for slides and tables.

The renderer and the QA gate call the same estimator, so a file cannot pass
the gate by using a looser definition of "fits" than the one that built it.
"""

from __future__ import annotations

EMU_PER_INCH = 914400


def emu(inches: float) -> int:
    return int(round(inches * EMU_PER_INCH))


def inches_of(value: int | float) -> float:
    return float(value) / EMU_PER_INCH


def _char_em(ch: str) -> float:
    code = ord(ch)
    if ch == "\n":
        return 0.0
    if code > 0x2E80 or ch in "—–·":
        return 1.02
    if ch == " ":
        return 0.33
    if ch.isdigit():
        return 0.52
    return 0.50


def estimate_lines(text: str, width_in: float, font_pt: float) -> int:
    """How many wrapped lines `text` needs. Newlines are hard breaks."""
    if not text:
        return 0
    if width_in <= 0.05 or font_pt <= 0:
        return 99
    capacity = width_in / (font_pt / 72.0)
    lines = 1
    used = 0.0
    for ch in text:
        if ch == "\n":
            lines += 1
            used = 0.0
            continue
        width = _char_em(ch)
        if used > 0 and used + width > capacity + 1e-6:
            lines += 1
            used = width
        else:
            used += width
    return lines


def _length_inches(value) -> float:
    if value is None:
        return 0.0
    if hasattr(value, "inches"):
        return float(value.inches)
    return float(value)


def _line_height_in(paragraph, font_pt: float) -> float:
    spacing = paragraph.line_spacing
    if spacing is None:
        return font_pt * 1.05 / 72.0
    if isinstance(spacing, (int, float)) and not hasattr(spacing, "inches"):
        return font_pt * float(spacing) / 72.0
    return _length_inches(spacing)


def _run_size_pt(paragraph, default: float) -> float:
    for run in paragraph.runs:
        if run.font.size is not None:
            return float(run.font.size.pt)
    return default


def text_frame_overflow(shape, default_pt: float = 14.0) -> str | None:
    frame = shape.text_frame
    width_in = (
        inches_of(shape.width)
        - _length_inches(frame.margin_left)
        - _length_inches(frame.margin_right)
    )
    height_in = (
        inches_of(shape.height)
        - _length_inches(frame.margin_top)
        - _length_inches(frame.margin_bottom)
    )
    needed = 0.0
    snippets: list[str] = []
    for paragraph in frame.paragraphs:
        text = "".join(run.text or "" for run in paragraph.runs)
        if text == "" and not snippets:
            continue
        if not text.strip() and needed == 0:
            continue
        size = _run_size_pt(paragraph, default_pt)
        lines = estimate_lines(text, width_in, size) if text else 0
        if lines:
            needed += lines * _line_height_in(paragraph, size)
            snippets.append(text.replace("\n", " ")[:42])
        needed += _length_inches(paragraph.space_before)
        needed += _length_inches(paragraph.space_after)
    if needed <= 0:
        return None
    slack = 0.045
    if needed > height_in + slack:
        name = getattr(shape, "name", "shape")
        preview = " / ".join(snippets)[:80]
        return f"{name}: text needs {needed:.2f}in but the box is {height_in:.2f}in ({preview})"
    return None


def table_overflow(shape) -> list[str]:
    issues: list[str] = []
    table = shape.table
    for row_index, row in enumerate(table.rows):
        row_height = row.height
        if not row_height:
            continue
        for col_index, cell in enumerate(row.cells):
            text = cell.text or ""
            if not text.strip():
                continue
            frame = cell.text_frame
            col_width = table.columns[col_index].width
            width_in = (
                inches_of(col_width)
                - _length_inches(frame.margin_left)
                - _length_inches(frame.margin_right)
            )
            height_in = (
                inches_of(row_height)
                - _length_inches(frame.margin_top)
                - _length_inches(frame.margin_bottom)
            )
            needed = 0.0
            for paragraph in frame.paragraphs:
                ptext = "".join(run.text or "" for run in paragraph.runs) or text
                size = _run_size_pt(paragraph, 12.0)
                lines = estimate_lines(ptext, max(width_in, 0.2), size)
                needed += lines * _line_height_in(paragraph, size)
            if needed > height_in + 0.04:
                issues.append(
                    f"table r{row_index}c{col_index}: needs {needed:.2f}in "
                    f"in {height_in:.2f}in ({text[:40]})"
                )
    return issues


def shape_out_of_bounds(
    shape, slide_width: int, slide_height: int, tolerance_in: float = 0.02
) -> str | None:
    tol = emu(tolerance_in)
    left = int(shape.left)
    top = int(shape.top)
    right = left + int(shape.width)
    bottom = top + int(shape.height)
    if left < -tol or top < -tol or right > slide_width + tol or bottom > slide_height + tol:
        name = getattr(shape, "name", "shape")
        return (
            f"{name} sits outside the slide "
            f"(L{inches_of(left):.2f} T{inches_of(top):.2f} "
            f"R{inches_of(right):.2f} B{inches_of(bottom):.2f})"
        )
    return None


def audit_slide(slide, slide_width: int, slide_height: int) -> list[str]:
    issues: list[str] = []
    for shape in slide.shapes:
        bounds = shape_out_of_bounds(shape, slide_width, slide_height)
        if bounds:
            issues.append(bounds)
        if getattr(shape, "has_text_frame", False):
            overflow = text_frame_overflow(shape)
            if overflow:
                issues.append(overflow)
        if getattr(shape, "has_table", False):
            issues.extend(table_overflow(shape))
    return issues
