"""Pandas bulk write for a rectangular block. Models themselves stay on formulas."""

from __future__ import annotations

import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter


def write_dataframe(
    worksheet, frame: pd.DataFrame, start_cell: str = "A1", font_name: str = "Liberation Sans"
) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("write_dataframe expects a pandas DataFrame.")
    from openpyxl.utils.cell import coordinate_to_tuple

    row, col = coordinate_to_tuple(start_cell)
    font = Font(name=font_name, size=10)
    header_font = Font(name=font_name, size=10, bold=True)
    for offset, name in enumerate(frame.columns):
        cell = worksheet.cell(row, col + offset, str(name))
        cell.font = header_font
        cell.alignment = Alignment(vertical="center")
    for r_index, record in enumerate(frame.itertuples(index=False), start=1):
        for c_index, value in enumerate(record):
            cell = worksheet.cell(
                row + r_index, col + c_index, value if not _is_na(value) else None
            )
            cell.font = font
            cell.alignment = Alignment(vertical="center")
    for offset, name in enumerate(frame.columns):
        letter = get_column_letter(col + offset)
        worksheet.column_dimensions[letter].width = max(12, min(36, len(str(name)) + 2))


def _is_na(value) -> bool:
    try:
        return bool(pd.isna(value))
    except TypeError:
        return False
