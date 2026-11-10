"""Optional HTML-to-PDF path for letters and one-page templates.

WeasyPrint is not installed by default. `build_html` is safe to call without it.
"""

from __future__ import annotations

import html


def build_html(plan: dict, profile: dict) -> str:
    pdf = profile["page"]["pdf"]
    margins = pdf["margins_mm"]
    fonts = profile["type"]["pdf"]
    palette = profile["palette"]
    lang = "zh-CN" if plan.get("language") == "zh" else "en"
    font = fonts["ea"] if plan.get("language") == "zh" else fonts["latin"]
    parts = [
        "<!DOCTYPE html>",
        f'<html lang="{lang}">',
        '<head><meta charset="utf-8"/>',
        "<style>",
        f"@page {{ size: {pdf['paper']}; margin: {margins['top']}mm {margins['right']}mm {margins['bottom']}mm {margins['left']}mm; }}",
        "body { margin: 0; }",
        (
            f"body {{ font-family: '{font}', '{fonts['latin']}', serif; "
            f"color: #{palette['ink']}; font-size: 11.5pt; line-height: 1.45; }}"
        ),
        "h1 { font-size: 18pt; font-weight: 600; margin: 0 0 0.4em; }",
        f"p.meta {{ color: #{palette['muted']}; font-size: 10pt; }}",
        "p { margin: 0 0 0.7em; }",
        "</style></head><body>",
        f"<h1>{html.escape(plan.get('title', ''))}</h1>",
    ]
    if plan.get("classification"):
        parts.append(f'<p class="meta">{html.escape(plan["classification"])}</p>')
    for section in plan.get("sections") or []:
        parts.append(f"<h2>{html.escape(section.get('heading', ''))}</h2>")
        for block in section.get("blocks") or []:
            if block.get("type") == "paragraph":
                parts.append(f"<p>{html.escape(block.get('text', ''))}</p>")
    parts.append("</body></html>")
    return "\n".join(parts)


def render_weasy(plan: dict, profile: dict, out_path) -> None:
    try:
        from weasyprint import HTML
    except ImportError as exc:
        raise RuntimeError(
            "WeasyPrint is optional. Install the system libraries and pip install 'office-skill[weasy]'."
        ) from exc
    HTML(string=build_html(plan, profile)).write_pdf(str(out_path))
