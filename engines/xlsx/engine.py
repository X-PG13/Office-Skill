"""Workbook renderer.

Inputs are blue on yellow. Formulas are black. Cross-sheet links are green.
The only hardcoded numbers are the named assumptions.
"""

from __future__ import annotations

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.marker import Marker
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.comments import Comment
from openpyxl.drawing.line import LineProperties
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from engines.xlsx.compiler import compile_expr
from office_skill.plan import PlanError

BANNERS = {
    "en": "Illustrative model. Hardcoded figures are scenario assumptions, not reported results.",
    "zh": "示意模型。手工输入的数字都是情景假设，不是已披露的经营实绩。",
}
SOURCED = {
    "en": "Figures are taken from the sources named beside each assumption.",
    "zh": "数字来自假设表中写明的资料，不是模型反推出来的。",
}
LEGEND = {
    "en": [
        ("Input", "Blue type, yellow fill. The only cells you type into."),
        ("Formula", "Black type. Leave the formula in place."),
        ("Cross-sheet", "Green type. This cell reads another sheet."),
    ],
    "zh": [
        ("输入", "蓝字、黄底。只有这些格子可以手改。"),
        ("公式", "黑字。不要把公式贴成死数。"),
        ("跨表", "绿字。这个格子读的是另一张表。"),
    ],
}


def render(plan: dict, profile: dict, out_path) -> None:
    language = plan["language"]
    model = profile["model"]
    font_name = (
        profile["type"]["xlsx"]["latin"] if language == "en" else profile["type"]["xlsx"]["ea"]
    )
    styles = _styles(font_name, model)
    wb = Workbook()
    names = plan.get("sheet_names") or _default_names(language)
    cover = wb.active
    cover.title = names["cover"]
    assumptions = wb.create_sheet(names["assumptions"])
    forecast = wb.create_sheet(names["forecast"])
    dashboard = wb.create_sheet(names["dashboard"])
    assumption_cells = _write_assumptions(assumptions, plan, styles, names["assumptions"])
    row_cells = _write_forecast(forecast, plan, styles, assumption_cells, names["forecast"])
    _write_dashboard(dashboard, plan, styles, assumption_cells, row_cells, names, profile)
    _write_cover(cover, plan, styles, names, profile)
    wb.calculation.calcMode = "auto"
    wb.calculation.fullCalcOnLoad = True
    wb.properties.title = plan["title"]
    wb.properties.creator = plan.get("author", "")
    wb.properties.subject = profile["id"]
    _page_setup(cover, assumptions, forecast, dashboard, plan["title"], language, font_name)
    wb.save(str(out_path))


def _default_names(language: str) -> dict:
    if language == "zh":
        return {"cover": "封面", "assumptions": "假设", "forecast": "测算", "dashboard": "结果"}
    return {
        "cover": "Cover",
        "assumptions": "Assumptions",
        "forecast": "Forecast",
        "dashboard": "Dashboard",
    }


def _styles(font_name: str, model: dict) -> dict:
    base = Font(name=font_name, size=10, color="000000")
    return {
        "base": base,
        "title": Font(name=font_name, size=16, bold=True, color="000000"),
        "header": Font(name=font_name, size=10, bold=True, color="000000"),
        "input": Font(name=font_name, size=10, color=model["input_font"]),
        "formula": Font(name=font_name, size=10, color=model["formula_font"]),
        "cross": Font(name=font_name, size=10, color=model["cross_font"]),
        "muted": Font(name=font_name, size=9, italic=True, color="595959"),
        "fill": PatternFill("solid", fgColor=model["input_fill"]),
        "thin": Border(bottom=Side(style="thin", color="222222")),
        "wrap": Alignment(vertical="center", wrap_text=True),
        "right": Alignment(vertical="center", horizontal="right"),
        "left": Alignment(vertical="center", horizontal="left", wrap_text=True),
    }


def _quote(sheet: str) -> str:
    return "'" + sheet.replace("'", "''") + "'"


def _write_assumptions(ws, plan: dict, styles: dict, sheet_name: str) -> dict[str, str]:
    ws["A1"] = plan["title"]
    ws["A1"].font = styles["title"]
    ws["A2"] = BANNERS[plan["language"]] if plan.get("illustrative") else SOURCED[plan["language"]]
    ws["A2"].font = styles["muted"]
    headers = ["Id", "Assumption", "Value", "Unit", "Note", "Source"]
    if plan["language"] == "zh":
        headers = ["编号", "假设", "取值", "单位", "说明", "来源"]
    for col, header in enumerate(headers, start=1):
        cell = ws.cell(5, col, header)
        cell.font = styles["header"]
        cell.border = styles["thin"]
        cell.alignment = styles["left"]
    addresses: dict[str, str] = {}
    for offset, item in enumerate(plan["assumptions"]):
        row = 6 + offset
        ws.cell(row, 1, item["id"]).font = styles["base"]
        ws.cell(row, 2, item["label"]).font = styles["base"]
        value = ws.cell(row, 3, item["value"])
        value.font = styles["input"]
        value.fill = styles["fill"]
        value.number_format = item.get("format", "0.00")
        value.alignment = styles["right"]
        note = " ".join(part for part in (item.get("note", ""), item.get("source", "")) if part)
        value.comment = Comment(note[:800], "Office-Skill")
        ws.cell(row, 4, item.get("unit", "")).font = styles["base"]
        note_cell = ws.cell(row, 5, item.get("note", ""))
        note_cell.font = styles["base"]
        note_cell.alignment = styles["left"]
        ws.cell(row, 6, item["source"]).font = styles["base"]
        for col in range(1, 7):
            ws.cell(row, col).alignment = styles["right"] if col == 3 else styles["left"]
        addresses[item["id"]] = f"{_quote(sheet_name)}!$C${row}"
    ws.freeze_panes = "A6"
    ws.auto_filter.ref = f"A5:F{5 + len(plan['assumptions'])}"
    widths = [22, 36, 16, 16, 55, 36]
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width
    ws.row_dimensions[1].height = 24
    ws.sheet_properties.tabColor = "C4A46A"
    return addresses


def _write_forecast(
    ws, plan: dict, styles: dict, assumptions: dict[str, str], sheet_name: str
) -> dict[str, list[str]]:
    years = plan["years"]
    ws["A1"] = plan["title"]
    ws["A1"].font = styles["title"]
    ws["A2"] = BANNERS[plan["language"]] if plan.get("illustrative") else SOURCED[plan["language"]]
    ws["A2"].font = styles["muted"]
    header_row = 5
    label = "Line" if plan["language"] == "en" else "项目"
    ws.cell(header_row, 1, label).font = styles["header"]
    ws.cell(header_row, 1).border = styles["thin"]
    for index, year in enumerate(years):
        cell = ws.cell(header_row, 2 + index, str(year))
        cell.font = styles["header"]
        cell.border = styles["thin"]
        cell.alignment = Alignment(horizontal="right", vertical="center")
        cell.number_format = "@"
    first = 6
    row_cells: dict[str, list[str]] = {}
    for offset, row in enumerate(plan["rows"]):
        excel_row = first + offset
        row_cells[row["id"]] = [
            f"{get_column_letter(2 + year)}{excel_row}" for year in range(len(years))
        ]
    prev_base_map: dict[str, str] = {}
    for row in plan["rows"]:
        if "prev_base" not in row:
            continue
        base = row["prev_base"]
        if isinstance(base, str):
            if base not in assumptions:
                raise PlanError(f"prev_base {base!r} is not an assumption.")
            prev_base_map[row["id"]] = assumptions[base]
        else:
            prev_base_map[row["id"]] = _literal(base)
    for offset, row in enumerate(plan["rows"]):
        excel_row = first + offset
        label_cell = ws.cell(excel_row, 1, row["label"])
        label_cell.font = styles["base"]
        label_cell.alignment = styles["left"]
        if row.get("expr"):
            label_cell.comment = Comment(row["expr"], "Office-Skill")
        for year_index in range(len(years)):
            cell = ws.cell(excel_row, 2 + year_index)
            cell.alignment = styles["right"]
            cell.number_format = row.get("format", "#,##0.00")
            if "values" in row:
                cell.value = row["values"][year_index]
                cell.font = styles["input"]
                cell.fill = styles["fill"]
            else:
                cell.value = compile_expr(
                    row["expr"],
                    col_index=year_index,
                    row_cells=row_cells,
                    assumptions=assumptions,
                    prev_base=prev_base_map,
                )
                cell.font = styles["formula"]
    ws.freeze_panes = "B6"
    ws.column_dimensions["A"].width = 38
    for index in range(len(years)):
        ws.column_dimensions[get_column_letter(2 + index)].width = 16
    ws.row_dimensions[1].height = 24
    ws.sheet_properties.tabColor = "1A1F1C"
    _ = sheet_name
    return row_cells


def _literal(value) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PlanError("prev_base must be a number or an assumption id.")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _write_dashboard(ws, plan, styles, assumptions, row_cells, names, profile) -> None:
    language = plan["language"]
    ws["A1"] = plan["title"]
    ws["A1"].font = styles["title"]
    ws["A2"] = BANNERS[language] if plan.get("illustrative") else SOURCED[language]
    ws["A2"].font = styles["muted"]
    ws["A4"] = "Result" if language == "en" else "结果"
    ws["B4"] = "Value" if language == "en" else "数值"
    ws["A4"].font = styles["header"]
    ws["B4"].font = styles["header"]
    ws["A4"].border = styles["thin"]
    ws["B4"].border = styles["thin"]
    row = 5
    forecast = names["forecast"]
    for item in plan.get("highlights") or []:
        ws.cell(row, 1, item["label"]).font = styles["base"]
        addr = row_cells[item["row"]][int(item["year_index"])]
        cell = ws.cell(row, 2, f"={_quote(forecast)}!{addr}")
        cell.font = styles["cross"]
        cell.number_format = item.get("format", "#,##0.00")
        cell.alignment = styles["right"]
        row += 1
    returns = plan.get("returns")
    if returns:
        cash = row_cells[returns["cashflow_row"]]
        rate = assumptions[returns["discount_rate"]]
        start, end = cash[0], cash[-1]
        rest_start = cash[1]
        npv_label = "NPV" if language == "en" else "净现值"
        irr_label = "IRR" if language == "en" else "内部收益率"
        ws.cell(row, 1, npv_label).font = styles["base"]
        npv = ws.cell(
            row, 2, f"=NPV({rate},{_quote(forecast)}!{rest_start}:{end})+{_quote(forecast)}!{start}"
        )
        npv.font = styles["cross"]
        npv.number_format = plan.get("currency_format", "$#,##0;($#,##0)")
        row += 1
        ws.cell(row, 1, irr_label).font = styles["base"]
        irr = ws.cell(row, 2, f"=IRR({_quote(forecast)}!{start}:{end})")
        irr.font = styles["cross"]
        irr.number_format = "0.0%"
        row += 1
    note = plan.get("returns_note")
    if note:
        row += 1
        ws.cell(row, 1, note).font = styles["muted"]
        row += 1
    _draw_charts(ws, plan, names["forecast"], row_cells, row + 1, profile)
    ws.column_dimensions["A"].width = 42
    ws.column_dimensions["B"].width = 20
    ws.row_dimensions[1].height = 24
    ws.sheet_properties.tabColor = profile["palette"]["accent"]
    ws.freeze_panes = "A5"


def _draw_charts(ws, plan, forecast_name, row_cells, anchor_row, profile) -> None:
    years = plan["years"]
    header_row = 5
    # Forecast years sit on row 5, columns B onward. The chart reads that sheet.
    for index, chart_spec in enumerate(plan.get("charts") or []):
        chart_type = chart_spec.get("type", "col")
        chart = LineChart() if chart_type == "line" else BarChart()
        if chart_type != "line":
            chart.type = "col"
            chart.grouping = "clustered"
        chart.title = chart_spec.get("title")
        chart.style = 10
        chart.y_axis.numFmt = chart_spec.get("format", "#,##0")
        if chart_type != "line":
            chart.y_axis.scaling.min = 0
        chart.legend = None
        ids = chart_spec.get("rows") or [chart_spec["row"]]
        # Build a compact plot range by referencing each row. openpyxl wants a
        # rectangular reference, so multiple rows must be contiguous. We plot
        # one row per chart in v1; extra ids are rejected.
        if len(ids) != 1:
            raise PlanError(
                "Each chart plots one forecast row. Add another chart for the next row."
            )
        excel_row = int(row_cells[ids[0]][0][1:])
        # row_cells addresses are like B12; the row number may be 6 or 16.
        excel_row = int("".join(ch for ch in row_cells[ids[0]][0] if ch.isdigit()))
        data = Reference(
            ws.parent[forecast_name],
            min_col=2,
            max_col=1 + len(years),
            min_row=excel_row,
            max_row=excel_row,
        )
        cats = Reference(
            ws.parent[forecast_name],
            min_col=2,
            max_col=1 + len(years),
            min_row=header_row,
            max_row=header_row,
        )
        chart.add_data(data, from_rows=True, titles_from_data=False)
        chart.set_categories(cats)
        chart.shape = 4
        chart.legend = None
        series = chart.series[0]
        color = profile["palette"]["series"][0]
        if chart_type == "line":
            series.graphicalProperties.line.solidFill = color
            series.graphicalProperties.line.width = 18000
            series.marker = Marker(symbol="circle", size=6)
            series.marker.graphicalProperties.solidFill = color
            series.marker.graphicalProperties.line.solidFill = color
            series.smooth = False
        else:
            series.graphicalProperties.solidFill = color
        chart.graphicalProperties = GraphicalProperties(ln=LineProperties(noFill=True))
        chart.width = 18
        chart.height = 7
        ws.add_chart(chart, f"A{anchor_row + index * 15}")
    _ = header_row


def _write_cover(ws, plan, styles, names, profile) -> None:
    language = plan["language"]
    ws["A1"] = plan["title"]
    ws["A1"].font = styles["title"]
    ws.merge_cells("A1:B1")
    subtitle = plan.get("subtitle", "")
    if subtitle:
        ws["A2"] = subtitle
        ws["A2"].font = styles["base"]
    banner_row = 4
    ws.cell(
        banner_row, 1, BANNERS[language] if plan.get("illustrative") else SOURCED[language]
    ).font = styles["header"]
    ws.merge_cells(start_row=banner_row, start_column=1, end_row=banner_row, end_column=4)
    row = 6
    for paragraph in plan.get("paragraphs") or []:
        cell = ws.cell(row, 1, paragraph)
        cell.font = styles["base"]
        cell.alignment = styles["left"]
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
        ws.row_dimensions[row].height = 32
        row += 1
    row += 1
    ws.cell(row, 1, "How to read the color" if language == "en" else "颜色怎么读").font = styles[
        "header"
    ]
    row += 1
    samples = [
        (styles["input"], styles["fill"], LEGEND[language][0]),
        (styles["formula"], None, LEGEND[language][1]),
        (styles["cross"], None, LEGEND[language][2]),
    ]
    for font, fill, (name, text) in samples:
        swatch = ws.cell(row, 1, name)
        swatch.font = font
        if fill is not None:
            swatch.fill = fill
        ws.cell(row, 2, text).font = styles["base"]
        row += 1
    row += 1
    sheets = " · ".join(names[key] for key in ("assumptions", "forecast", "dashboard"))
    label = "Sheets" if language == "en" else "工作表"
    ws.cell(row, 1, f"{label}: {sheets}").font = styles["muted"]
    row += 2
    caveat = plan.get("caveat")
    if caveat:
        ws.cell(row, 1, caveat).font = styles["muted"]
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=4)
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 78
    ws.column_dimensions["C"].width = 18
    ws.column_dimensions["D"].width = 18
    ws.row_dimensions[1].height = 26
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.tabColor = profile["palette"]["ink"]
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.page_setup.paperSize = ws.PAPERSIZE_A3
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:2"
    ws.page_setup.horizontalCentered = True
    ws.oddFooter.left.text = BANNERS[language] if plan.get("illustrative") else ""
    ws.oddFooter.right.text = "Page &P"


def _header_run(text: str, font_name: str, size: int = 9) -> str:
    safe = text.replace("&", " ")
    return f'&"{font_name}"&{size}&K595959 {safe}'


def _page_setup(*sheets_and_meta) -> None:
    *sheets, title, language, font_name = sheets_and_meta
    banner = BANNERS[language] if language in BANNERS else ""
    for ws in sheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.paperSize = ws.PAPERSIZE_A3
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 1
        ws.page_setup.fitToPage = True
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.horizontalCentered = True
        ws.page_margins.left = 0.5
        ws.page_margins.right = 0.5
        ws.page_margins.top = 0.6
        ws.page_margins.bottom = 0.6
        ws.oddHeader.left.text = _header_run(title, font_name)
        ws.oddFooter.right.text = f'&"{font_name}"&9&K595959 Page &P'
        ws.oddFooter.left.text = _header_run(banner, font_name)
        ws.sheet_view.zoomScale = 110
        ws.sheet_view.view = "pageBreakPreview"
        ws.sheet_view.view = "normal"
        ws.print_options.horizontalCentered = True
