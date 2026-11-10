"""Deterministic slide primitives.

The agent picks a primitive and fills its fields. Coordinates stay in this file.
"""

from __future__ import annotations

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

from office_skill.geometry import audit_slide, emu
from office_skill.plan import PlanError

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"a": A_NS}
THEME_FACES = {"", "+mj-lt", "+mn-lt", "+mj-ea", "+mn-ea", "+mj-cs", "+mn-cs"}
UNSAFE_FACES = {
    "Calibri",
    "Calibri Light",
    "Aptos",
    "Arial",
    "Times New Roman",
    "Cambria",
    "微软雅黑",
    "宋体",
    "等线",
    "黑体",
    "DengXian",
}

CHART_TYPES = {
    "column": XL_CHART_TYPE.COLUMN_CLUSTERED,
    "bar": XL_CHART_TYPE.BAR_CLUSTERED,
    "line": XL_CHART_TYPE.LINE,
}


def _rgb(value: str) -> RGBColor:
    return RGBColor.from_string(value.removeprefix("#"))


def _align(name: str):
    return {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[name]


class Deck:
    def __init__(self, plan: dict, profile: dict):
        self.plan = plan
        self.profile = profile
        self.lang = plan["language"]
        self.labels = profile["labels"][self.lang]
        self.fonts = profile["type"]["pptx"]
        self.scale = profile["type"]["scale"]
        self.pal = profile["palette"]
        self.tones = profile["tones"]
        page = profile["page"]["pptx"]
        self.W = float(page["width_in"])
        self.H = float(page["height_in"])
        self.m = float(page["margin_in"])
        self.prs = Presentation()
        self.prs.slide_width = Emu(emu(self.W))
        self.prs.slide_height = Emu(emu(self.H))
        self.sw = int(self.prs.slide_width)
        self.sh = int(self.prs.slide_height)
        self.latin = self.fonts["latin"]
        self.ea = self.fonts["ea"]
        self.mono = self.fonts.get("mono", self.latin)
        self.total = len(plan["slides"])

    @property
    def content_w(self) -> float:
        return self.W - 2 * self.m

    def sz(self, key: str, default: float) -> float:
        return float(self.scale.get(key, default))

    def blank(self):
        for layout in self.prs.slide_layouts:
            if layout.name.lower() == "blank":
                return self.prs.slides.add_slide(layout)
        return self.prs.slides.add_slide(self.prs.slide_layouts[6])

    def tone_of(self, spec: dict, fallback: str) -> str:
        return spec.get("tone") or self.tones.get(fallback, "light")

    def colors(self, tone: str) -> dict:
        if tone == "dark":
            return {
                "bg": self.pal["dark"],
                "ink": self.pal["on_dark"],
                "muted": self.pal["on_dark_muted"],
                "line": self.pal["on_dark_muted"],
                "accent": self.pal["mark"],
            }
        return {
            "bg": self.pal["paper"],
            "ink": self.pal["ink"],
            "muted": self.pal["muted"],
            "line": self.pal["line"],
            "accent": self.pal["accent"],
        }

    def paint(self, slide, color: str) -> None:
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = _rgb(color)

    def add_text(self, slide, left, top, width, height, paragraphs, *, anchor="top", name="text"):
        shape = slide.shapes.add_textbox(
            Emu(emu(left)), Emu(emu(top)), Emu(emu(width)), Emu(emu(height))
        )
        shape.name = name
        frame = shape.text_frame
        frame.word_wrap = True
        frame.auto_size = None
        frame.margin_left = Emu(emu(0.04))
        frame.margin_right = Emu(emu(0.04))
        frame.margin_top = Emu(emu(0.02))
        frame.margin_bottom = Emu(emu(0.02))
        frame._txBody.bodyPr.set("anchor", {"top": "t", "middle": "ctr", "bottom": "b"}[anchor])
        for index, spec in enumerate(paragraphs):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.alignment = _align(spec.get("align", "left"))
            paragraph.space_before = Pt(spec.get("before", 0))
            paragraph.space_after = Pt(spec.get("after", 0))
            paragraph.line_spacing = spec.get("leading", 1.05)
            run = paragraph.add_run()
            run.text = spec.get("text", "")
            self._style_run(run, spec)
        return shape

    def _style_run(self, run, spec: dict) -> None:
        latin = self.mono if spec.get("mono") else self.latin
        size = spec.get("size", 14)
        run.font.size = Pt(size)
        run.font.bold = bool(spec.get("bold", False))
        run.font.italic = bool(spec.get("italic", False))
        run.font.color.rgb = _rgb(spec.get("color", self.pal["ink"]))
        r_pr = run._r.get_or_add_rPr()
        lang = "zh-CN" if self.lang == "zh" else "en-US"
        r_pr.set("lang", lang)
        r_pr.set("altLang", "en-US" if lang == "zh-CN" else "zh-CN")
        _set_typeface(r_pr, "latin", latin)
        _set_typeface(r_pr, "ea", self.ea)
        _set_typeface(r_pr, "cs", latin)

    def rule(self, slide, left, top, width, color, pt=1.0, name="rule"):
        height = max(pt / 72.0, 0.01)
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Emu(emu(left)), Emu(emu(top)), Emu(emu(width)), Emu(emu(height))
        )
        shape.name = name
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(color)
        shape.line.fill.background()
        return shape

    def square(self, slide, left, top, size, color):
        shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Emu(emu(left)), Emu(emu(top)), Emu(emu(size)), Emu(emu(size))
        )
        shape.name = "mark"
        shape.fill.solid()
        shape.fill.fore_color.rgb = _rgb(color)
        shape.line.fill.background()
        return shape

    def footer(self, slide, spec: dict, index: int, cols: dict) -> None:
        parts = []
        if spec.get("illustrative"):
            parts.append(self.labels["illustrative"])
        source = str(spec.get("source", "")).strip()
        if source:
            parts.append(source)
        text = "  ·  ".join(parts)
        top = self.H - 0.34
        if text:
            self.add_text(
                slide,
                self.m,
                top,
                self.content_w - 1.35,
                0.26,
                [
                    {
                        "text": text,
                        "size": self.sz("source", 10),
                        "color": cols["muted"],
                        "leading": 1.0,
                    }
                ],
                anchor="middle",
                name="source",
            )
        self.add_text(
            slide,
            self.W - self.m - 1.15,
            top,
            1.15,
            0.26,
            [
                {
                    "text": f"{index}  /  {self.total}",
                    "size": self.sz("source", 10),
                    "color": cols["muted"],
                    "align": "right",
                    "leading": 1.0,
                }
            ],
            anchor="middle",
            name="page",
        )

    def title_block(self, slide, text: str, cols: dict):
        return self.add_text(
            slide,
            self.m,
            0.32,
            self.content_w,
            1.08,
            self._chunks(
                text,
                size=self.sz("action_title", 22),
                bold=True,
                color=cols["ink"],
                leading=1.08,
                after=0,
            ),
            name="title",
        )

    def _chunks(self, text: str, **style) -> list[dict]:
        parts = (text or "").split("\n")
        chunks = []
        for part in parts:
            item = dict(style)
            item["text"] = part
            chunks.append(item)
        return chunks or [dict(style, text="")]

    def finish(self, slide) -> None:
        issues = audit_slide(slide, self.sw, self.sh)
        if issues:
            raise PlanError("Layout overflow or out-of-bounds shape: " + "; ".join(issues))


def _set_typeface(r_pr, tag: str, name: str) -> None:
    element = r_pr.find(qn(f"a:{tag}"))
    if element is None:
        r_pr.append(parse_xml(f'<a:{tag} xmlns:a="{A_NS}" typeface="{name}"/>'))
    else:
        element.set("typeface", name)


def _style_cell(cell, text, deck: Deck, *, size, bold, color, align):
    frame = cell.text_frame
    frame.clear()
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = _align(align)
    paragraph.line_spacing = 1.0
    run = paragraph.add_run()
    run.text = "" if text is None else str(text)
    deck._style_run(run, {"size": size, "bold": bold, "color": color})
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE


def _set_cell_border(cell, color: str, edges: set[str], width_pt: float) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    width = int(width_pt * 12700)
    for edge in ("lnL", "lnR", "lnT", "lnB"):
        existing = tc_pr.find(qn(f"a:{edge}"))
        if existing is not None:
            tc_pr.remove(existing)
        if edge in edges:
            tc_pr.append(
                parse_xml(
                    f'<a:{edge} xmlns:a="{A_NS}" w="{width}" cap="flat" cmpd="sng" algn="ctr">'
                    f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
                    f'<a:prstDash val="solid"/></a:{edge}>'
                )
            )
        else:
            tc_pr.append(parse_xml(f'<a:{edge} xmlns:a="{A_NS}" w="0"><a:noFill/></a:{edge}>'))


def _cell_margins(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    for tag, val in (("marL", 50000), ("marR", 50000), ("marT", 28000), ("marB", 28000)):
        existing = tc_pr.find(qn(f"a:{tag}"))
        if existing is not None:
            tc_pr.remove(existing)
        tc_pr.append(parse_xml(f'<a:{tag} xmlns:a="{A_NS}" val="{val}"/>'))


def render(plan: dict, profile: dict, out_path) -> None:
    deck = Deck(plan, profile)
    builders = {
        "cover": _cover,
        "section": _section,
        "action": _action,
        "chart": _chart,
        "table": _table,
        "matrix": _matrix,
        "timeline": _timeline,
        "comparison": _comparison,
        "steps": _steps,
        "close": _close,
    }
    for index, spec in enumerate(plan["slides"], start=1):
        slide = deck.blank()
        builders[spec["primitive"]](deck, slide, spec, index)
        deck.finish(slide)
    _finalize_fonts(deck)
    _strip_effects(deck.prs)
    props = deck.prs.core_properties
    props.title = plan["title"]
    props.author = plan.get("author", "")
    props.subject = profile["id"]
    props.category = plan["file_type"]
    deck.prs.save(str(out_path))


def _cover(deck: Deck, slide, spec: dict, index: int) -> None:
    tone = deck.tone_of(spec, "cover")
    cols = deck.colors(tone)
    deck.paint(slide, cols["bg"])
    deck.square(slide, deck.m, 0.50, 0.11, cols["accent"])
    if spec.get("kicker"):
        deck.add_text(
            slide,
            deck.m + 0.24,
            0.44,
            deck.content_w - 0.24,
            0.32,
            [{"text": spec["kicker"], "size": deck.sz("kicker", 13), "color": cols["muted"]}],
            anchor="middle",
            name="kicker",
        )
    deck.add_text(
        slide,
        deck.m,
        2.05,
        deck.content_w * 0.92,
        2.05,
        deck._chunks(
            spec["title"],
            size=deck.sz("cover_title", 34),
            bold=True,
            color=cols["ink"],
            leading=1.02,
        ),
        name="cover-title",
    )
    if spec.get("subtitle"):
        deck.add_text(
            slide,
            deck.m,
            4.30,
            deck.content_w * 0.86,
            1.15,
            deck._chunks(
                spec["subtitle"], size=deck.sz("cover_sub", 16), color=cols["muted"], leading=1.15
            ),
            name="subtitle",
        )
    meta = spec.get("meta", "")
    if isinstance(meta, list):
        meta = "   ·   ".join(str(item) for item in meta)
    if meta:
        deck.add_text(
            slide,
            deck.m,
            6.72,
            deck.content_w - 1.4,
            0.32,
            [{"text": meta, "size": deck.sz("source", 12), "color": cols["muted"]}],
            name="meta",
        )
    deck.add_text(
        slide,
        deck.W - deck.m - 1.15,
        6.72,
        1.15,
        0.32,
        [
            {
                "text": f"{index}  /  {deck.total}",
                "size": deck.sz("source", 12),
                "color": cols["muted"],
                "align": "right",
            }
        ],
        name="page",
    )


def _section(deck: Deck, slide, spec: dict, index: int) -> None:
    tone = deck.tone_of(spec, "section")
    cols = deck.colors(tone)
    deck.paint(slide, cols["bg"])
    deck.square(slide, deck.m, 2.55, 0.12, cols["accent"])
    kicker = spec.get("kicker", "")
    if kicker:
        deck.add_text(
            slide,
            deck.m + 0.26,
            2.48,
            deck.content_w,
            0.32,
            [{"text": kicker, "size": deck.sz("kicker", 14), "color": cols["accent"]}],
            anchor="middle",
            name="kicker",
        )
    deck.add_text(
        slide,
        deck.m,
        3.05,
        deck.content_w * 0.88,
        1.8,
        deck._chunks(
            spec["title"],
            size=deck.sz("section_title", 32),
            bold=True,
            color=cols["ink"],
            leading=1.05,
        ),
        name="title",
    )
    if spec.get("subtitle"):
        deck.add_text(
            slide,
            deck.m,
            5.05,
            deck.content_w * 0.75,
            0.8,
            deck._chunks(
                spec["subtitle"], size=deck.sz("body", 16), color=cols["muted"], leading=1.15
            ),
            name="subtitle",
        )
    deck.footer(slide, spec, index, cols)


def _action(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    paragraphs = []
    if spec.get("pull"):
        paragraphs.extend(
            deck._chunks(
                spec["pull"],
                size=deck.sz("pull", 18),
                color=cols["ink"],
                leading=1.15,
                after=14,
            )
        )
    for text in spec.get("paragraphs") or []:
        paragraphs.extend(
            deck._chunks(text, size=deck.sz("body", 15), color=cols["ink"], leading=1.18, after=10)
        )
    deck.add_text(
        slide,
        deck.m,
        1.55,
        deck.content_w,
        5.25,
        paragraphs,
        name="body",
    )
    deck.footer(slide, spec, index, cols)


def _chart(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    top = 1.52
    if spec.get("unit"):
        deck.add_text(
            slide,
            deck.m,
            top,
            deck.content_w * 0.60,
            0.28,
            [{"text": spec["unit"], "size": deck.sz("caption", 12), "color": cols["muted"]}],
            name="unit",
        )
        top += 0.30
    chart_w = deck.content_w * 0.60
    chart_h = 6.85 - top
    _draw_chart(deck, slide, spec, deck.m, top, chart_w, chart_h, cols)
    insight = []
    if spec.get("insight_lead"):
        insight.extend(
            deck._chunks(
                spec["insight_lead"],
                size=deck.sz("insight", 14),
                bold=True,
                color=cols["ink"],
                leading=1.12,
                after=8,
            )
        )
    if spec.get("insight"):
        insight.extend(
            deck._chunks(
                spec["insight"],
                size=deck.sz("insight", 13),
                color=cols["ink"],
                leading=1.18,
                after=8,
            )
        )
    deck.add_text(
        slide,
        deck.m + chart_w + 0.28,
        top,
        deck.content_w - chart_w - 0.28,
        chart_h,
        insight,
        name="insight",
    )
    deck.footer(slide, spec, index, cols)


def _draw_chart(deck: Deck, slide, spec: dict, left, top, width, height, cols: dict) -> None:
    chart_type = spec.get("chart_type", "column")
    if chart_type not in CHART_TYPES:
        raise PlanError(f"Unsupported chart_type {chart_type!r}.")
    categories = list(spec["categories"])
    series_specs = [dict(item) for item in spec["series"]]
    emphasis = spec.get("emphasis_index")
    if chart_type == "bar":
        # A bar chart draws the first category at the bottom. Reverse the
        # rows so the plan's first category sits at the top, and leave the
        # value axis reading left to right.
        categories = list(reversed(categories))
        series_specs = [{**item, "values": list(reversed(item["values"]))} for item in series_specs]
        if emphasis is not None:
            emphasis = len(spec["categories"]) - 1 - int(emphasis)
    data = CategoryChartData()
    data.categories = categories
    for series in series_specs:
        data.add_series(series["name"], series["values"])
    shape = slide.shapes.add_chart(
        CHART_TYPES[chart_type],
        Emu(emu(left)),
        Emu(emu(top)),
        Emu(emu(width)),
        Emu(emu(height)),
        data,
    )
    shape.name = "chart"
    chart = shape.chart
    chart.has_title = False
    plot = chart.plots[0]
    plot.vary_by_categories = False
    plot.has_data_labels = False
    plot.gap_width = 70
    colors = spec.get("colors") or deck.pal["series"]
    for series_index, series in enumerate(chart.series):
        color = colors[series_index % len(colors)]
        if chart_type == "line":
            series.format.line.color.rgb = _rgb(color)
            series.format.line.width = Pt(1.75)
        else:
            series.format.fill.solid()
            series.format.fill.fore_color.rgb = _rgb(color)
            series.format.line.fill.background()
    if emphasis is not None and chart_type != "line":
        point = chart.series[0].points[int(emphasis)]
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = _rgb(deck.pal["accent"])
        point.format.line.fill.background()
    value_axis = chart.value_axis
    value_axis.has_major_gridlines = True
    value_axis.has_minor_gridlines = False
    value_axis.minimum_scale = spec.get("axis_min", 0)
    value_axis.major_gridlines.format.line.color.rgb = _rgb(deck.pal["line"])
    value_axis.major_gridlines.format.line.width = Pt(0.75)
    value_axis.format.line.fill.background()
    value_axis.tick_labels.font.size = Pt(10)
    value_axis.tick_labels.font.name = deck.latin
    value_axis.tick_labels.font.color.rgb = _rgb(cols["muted"])
    if spec.get("number_format"):
        value_axis.tick_labels.number_format = spec["number_format"]
        value_axis.tick_labels.number_format_is_linked = False
    category_axis = chart.category_axis
    category_axis.has_major_gridlines = False
    category_axis.format.line.color.rgb = _rgb(cols["ink"])
    category_axis.tick_labels.font.size = Pt(11)
    category_axis.tick_labels.font.name = deck.latin
    category_axis.tick_labels.font.color.rgb = _rgb(cols["ink"])
    if len(spec["series"]) > 1:
        chart.has_legend = True
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.size = Pt(10)
        chart.legend.font.name = deck.latin
    else:
        chart.has_legend = False
    chart.font.size = Pt(10)
    chart.font.name = deck.latin


def _table(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    columns = spec["columns"]
    rows = spec["rows"]
    aligns = spec.get("aligns") or ["left"] * len(columns)
    n_rows = 1 + len(rows)
    top = 1.58
    available = 5.15
    row_h = min(0.48, available / n_rows)
    shape = slide.shapes.add_table(
        n_rows,
        len(columns),
        Emu(emu(deck.m)),
        Emu(emu(top)),
        Emu(emu(deck.content_w)),
        Emu(emu(row_h * n_rows)),
    )
    shape.name = "table"
    table = shape.table
    weights = spec.get("widths") or [1] * len(columns)
    total = sum(weights)
    for col_index, weight in enumerate(weights):
        table.columns[col_index].width = Emu(emu(deck.content_w * weight / total))
    for col_index, header in enumerate(columns):
        cell = table.cell(0, col_index)
        _cell_margins(cell)
        cell.fill.background()
        _style_cell(
            cell,
            header,
            deck,
            size=deck.sz("table", 12),
            bold=True,
            color=cols["ink"],
            align=aligns[col_index],
        )
        _set_cell_border(cell, cols["ink"], {"lnB"}, 1.25)
    for row_index, row in enumerate(rows, start=1):
        table.rows[row_index].height = Emu(emu(row_h))
        for col_index, value in enumerate(row):
            cell = table.cell(row_index, col_index)
            _cell_margins(cell)
            cell.fill.background()
            _style_cell(
                cell,
                value,
                deck,
                size=deck.sz("table", 12),
                bold=False,
                color=cols["ink"],
                align=aligns[col_index],
            )
            _set_cell_border(cell, deck.pal["line"], {"lnB"}, 0.75)
    table.rows[0].height = Emu(emu(row_h))
    if spec.get("note"):
        deck.add_text(
            slide,
            deck.m,
            top + row_h * n_rows + 0.12,
            deck.content_w,
            0.7,
            deck._chunks(
                spec["note"], size=deck.sz("caption", 12), color=cols["muted"], leading=1.15
            ),
            name="note",
        )
    deck.footer(slide, spec, index, cols)


def _matrix(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    deck.add_text(
        slide,
        deck.m,
        1.48,
        deck.content_w,
        0.30,
        [{"text": spec.get("y_axis", ""), "size": deck.sz("caption", 12), "color": cols["muted"]}],
        name="y-axis",
    )
    inner_top = 1.84
    inner_h = 4.55
    gutter = 0.16
    qw = (deck.content_w - gutter) / 2
    qh = (inner_h - gutter) / 2
    spots = {
        "tl": (deck.m, inner_top),
        "tr": (deck.m + qw + gutter, inner_top),
        "bl": (deck.m, inner_top + qh + gutter),
        "br": (deck.m + qw + gutter, inner_top + qh + gutter),
    }
    deck.rule(
        slide,
        deck.m,
        inner_top + qh + gutter / 2,
        deck.content_w,
        deck.pal["line"],
        1.0,
        name="axis-x",
    )
    _replace_vertical(
        deck, slide, deck.m + qw + (gutter - 0.012) / 2, inner_top, inner_h, deck.pal["line"]
    )
    for item in spec["quadrants"]:
        pos = item["pos"]
        left, top = spots[pos]
        paragraphs = deck._chunks(
            item["title"],
            size=deck.sz("insight", 15),
            bold=True,
            color=cols["ink"],
            leading=1.05,
            after=4,
        )
        paragraphs.extend(
            deck._chunks(
                item.get("body", ""), size=deck.sz("caption", 13), color=cols["ink"], leading=1.15
            )
        )
        deck.add_text(
            slide,
            left + 0.16,
            top + 0.08,
            qw - 0.32,
            qh - 0.16,
            paragraphs,
            anchor="middle",
            name=f"quad-{pos}",
        )
    deck.add_text(
        slide,
        deck.m,
        inner_top + inner_h + 0.06,
        deck.content_w,
        0.28,
        [{"text": spec.get("x_axis", ""), "size": deck.sz("caption", 12), "color": cols["muted"]}],
        name="x-axis",
    )
    deck.footer(slide, spec, index, cols)


def _replace_vertical(deck: Deck, slide, left, top, height, color) -> None:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Emu(emu(left)), Emu(emu(top)), Emu(emu(0.012)), Emu(emu(height))
    )
    shape.name = "axis-y-line"
    shape.fill.solid()
    shape.fill.fore_color.rgb = _rgb(color)
    shape.line.fill.background()


def _timeline(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    items = spec["items"]
    n = len(items)
    item_w = deck.content_w / n
    line_y = 3.05
    deck.rule(
        slide,
        deck.m + item_w * 0.18,
        line_y,
        deck.content_w - item_w * 0.36,
        cols["ink"],
        1.25,
        name="time-line",
    )
    for item_index, item in enumerate(items):
        left = deck.m + item_index * item_w
        center = left + item_w / 2
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Emu(emu(center - 0.07)),
            Emu(emu(line_y - 0.06)),
            Emu(emu(0.14)),
            Emu(emu(0.14)),
        )
        dot.name = f"dot-{item_index}"
        dot.fill.solid()
        dot.fill.fore_color.rgb = _rgb(cols["bg"])
        dot.line.color.rgb = _rgb(cols["ink"])
        dot.line.width = Pt(1.25)
        deck.add_text(
            slide,
            left + 0.08,
            2.35,
            item_w - 0.16,
            0.42,
            [
                {
                    "text": item["label"],
                    "size": deck.sz("caption", 13),
                    "bold": True,
                    "color": cols["accent"],
                    "align": "center",
                }
            ],
            name=f"when-{item_index}",
        )
        deck.add_text(
            slide,
            left + 0.08,
            3.35,
            item_w - 0.16,
            2.7,
            deck._chunks(
                item["title"],
                size=14,
                bold=True,
                color=cols["ink"],
                leading=1.05,
                after=6,
                align="center",
            )
            + deck._chunks(
                item.get("detail", ""), size=12, color=cols["ink"], leading=1.15, align="center"
            ),
            name=f"event-{item_index}",
        )
    deck.footer(slide, spec, index, cols)


def _comparison(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    columns = spec["columns"]
    n = len(columns)
    gutter = 0.28
    col_w = (deck.content_w - gutter * (n - 1)) / n
    for col_index, column in enumerate(columns):
        left = deck.m + col_index * (col_w + gutter)
        if column.get("recommended"):
            deck.rule(slide, left, 1.50, col_w, cols["accent"], 2.25, name=f"rec-{col_index}")
            label = deck.labels["recommend"]
        else:
            label = ""
        deck.add_text(
            slide,
            left,
            1.58,
            col_w,
            0.28,
            [{"text": label, "size": 12, "bold": True, "color": cols["accent"]}],
            name=f"rec-label-{col_index}",
        )
        title_top = 1.92
        paragraphs = deck._chunks(
            column["title"], size=16, bold=True, color=cols["ink"], leading=1.05, after=10
        )
        for point in column.get("points") or []:
            paragraphs.extend(
                deck._chunks(point, size=13, color=cols["ink"], leading=1.15, after=8)
            )
        deck.add_text(slide, left, title_top, col_w, 4.7, paragraphs, name=f"col-{col_index}")
    deck.footer(slide, spec, index, cols)


def _steps(deck: Deck, slide, spec: dict, index: int) -> None:
    cols = deck.colors(deck.tone_of(spec, "content"))
    deck.paint(slide, cols["bg"])
    deck.title_block(slide, spec["title"], cols)
    steps = spec["steps"]
    n = len(steps)
    gutter = 0.24
    col_w = (deck.content_w - gutter * (n - 1)) / n
    deck.rule(
        slide, deck.m + 0.2, 2.18, deck.content_w - 0.4, deck.pal["line"], 1.0, name="step-line"
    )
    for step_index, step in enumerate(steps):
        left = deck.m + step_index * (col_w + gutter)
        deck.add_text(
            slide,
            left,
            1.78,
            0.7,
            0.42,
            [
                {
                    "text": f"{step_index + 1:02d}",
                    "size": 18,
                    "bold": True,
                    "color": cols["accent"],
                    "mono": True,
                }
            ],
            name=f"num-{step_index}",
        )
        paragraphs = deck._chunks(
            step["title"], size=15, bold=True, color=cols["ink"], leading=1.05, after=6
        )
        paragraphs.extend(
            deck._chunks(step.get("detail", ""), size=13, color=cols["ink"], leading=1.15)
        )
        deck.add_text(slide, left, 2.45, col_w, 3.8, paragraphs, name=f"step-{step_index}")
    deck.footer(slide, spec, index, cols)


def _close(deck: Deck, slide, spec: dict, index: int) -> None:
    tone = deck.tone_of(spec, "close")
    cols = deck.colors(tone)
    deck.paint(slide, cols["bg"])
    deck.square(slide, deck.m, 0.48, 0.11, cols["accent"])
    if spec.get("kicker"):
        deck.add_text(
            slide,
            deck.m + 0.24,
            0.42,
            deck.content_w,
            0.32,
            [{"text": spec["kicker"], "size": 13, "color": cols["accent"]}],
            anchor="middle",
            name="kicker",
        )
    deck.add_text(
        slide,
        deck.m,
        1.15,
        deck.content_w * 0.92,
        1.55,
        deck._chunks(
            spec["title"],
            size=deck.sz("close_title", 28),
            bold=True,
            color=cols["ink"],
            leading=1.05,
        ),
        name="title",
    )
    decisions = spec.get("decisions") or []
    n = max(len(decisions), 1)
    gutter = 0.36
    col_w = (deck.content_w - gutter * (n - 1)) / n
    for dec_index, decision in enumerate(decisions):
        left = deck.m + dec_index * (col_w + gutter)
        paragraphs = deck._chunks(
            decision.get("label", ""),
            size=13,
            bold=True,
            color=cols["accent"],
            leading=1.0,
            after=8,
        )
        paragraphs.extend(
            deck._chunks(
                decision.get("text", ""), size=15, color=cols["ink"], leading=1.18, after=8
            )
        )
        deck.add_text(slide, left, 3.05, col_w, 3.3, paragraphs, name=f"decision-{dec_index}")
    deck.footer(slide, spec, index, cols)


def _finalize_fonts(deck: Deck) -> None:
    allowed_keep = {deck.latin, deck.mono}
    for part in deck.prs.part.package.iter_parts():
        element = getattr(part, "_element", None)
        if element is None:
            continue
        content_type = getattr(part, "content_type", "")
        if "theme" in content_type:
            _patch_theme(element, deck.latin, deck.ea)
            continue
        for r_pr in element.xpath(".//a:rPr | .//a:defRPr | .//a:endParaRPr"):
            _normalize_rpr(r_pr, deck.latin, deck.ea, allowed_keep)


def _patch_theme(element, latin: str, ea: str) -> None:
    for tag, name in (("latin", latin), ("ea", ea), ("cs", latin)):
        for node in element.xpath(f".//a:{tag}"):
            node.set("typeface", name)
    for node in element.xpath(".//a:font"):
        script = node.get("script")
        if script in {"Hans", "Hant", "Jpan", "Hang", "Zhhh"}:
            node.set("typeface", ea)


def _normalize_rpr(r_pr, latin: str, ea: str, keep: set[str]) -> None:
    latin_el = r_pr.find(qn("a:latin"))
    current = latin_el.get("typeface") if latin_el is not None else ""
    if current not in keep or current in THEME_FACES or current in UNSAFE_FACES:
        chosen = latin
    else:
        chosen = current
    _set_typeface(r_pr, "latin", chosen)
    _set_typeface(r_pr, "ea", ea)
    _set_typeface(r_pr, "cs", chosen)


def _strip_effects(prs: Presentation) -> None:
    for part in prs.part.package.iter_parts():
        element = getattr(part, "_element", None)
        if element is None:
            continue
        for node in element.xpath(".//a:effectLst | .//a:scene3d | .//a:sp3d"):
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
