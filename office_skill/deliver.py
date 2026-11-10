"""Short note shipped beside the file. Not a substitute for reading the pages."""

from __future__ import annotations

from pathlib import Path


def write_delivery_note(
    plan: dict, profile: dict, out_path: Path, gate: dict | None = None
) -> Path:
    language = plan.get("language", "en")
    target = Path(out_path).with_suffix(".delivery.md")
    illustrative = _illustrative(plan)
    fonts = profile["type"][plan["file_type"]]
    if language == "zh":
        lines = [
            "# 交付说明",
            "",
            f"- 文件：`{Path(out_path).name}`",
            f"- 体裁：{plan['file_type']}",
            f"- 剖面：{profile['id']}（{profile.get('name', '')}）",
            f"- 语言：{language}",
            f"- 拉丁字体：{fonts.get('latin', '')}；东亚字体：{fonts.get('ea', '')}",
            "",
            "## 数据",
            "",
            illustrative or "计划未把整份文件标为示意。请仍核对每个数字是否能回到资料。",
            "",
            "## 限制",
            "",
            "- 打开文件的电脑若没有上述字体，换行会变化。QA 机安装的是 Noto CJK 与 Liberation。",
            "- 本文件是草稿，不是法律意见、投资建议或已经套红的公文。",
            "- v1 只生成新文件，不会安全地改一份已有的复杂 Office 文件。",
        ]
        if (
            plan["file_type"] == "docx"
            and plan.get("include_toc", True)
            and plan.get("doc_kind") != "gongwen"
        ):
            lines.append("- 目录是 Word 域。Word 打开时会更新页码；未更新时也能看到标题列表。")
        if profile["id"] == "government":
            lines.append(
                "- 公文用字以 Noto Serif CJK SC / Noto Sans CJK SC 替代小标宋、仿宋和黑体。"
            )
    else:
        lines = [
            "# Delivery note",
            "",
            f"- File: `{Path(out_path).name}`",
            f"- Type: {plan['file_type']}",
            f"- Profile: {profile['id']} ({profile.get('name', '')})",
            f"- Language: {language}",
            f"- Latin face: {fonts.get('latin', '')}; East Asian face: {fonts.get('ea', '')}",
            "",
            "## Data",
            "",
            illustrative
            or "The plan did not mark the whole file illustrative. Check each figure against a source.",
            "",
            "## Limits",
            "",
            "- Line breaks move if the reader's machine lacks these faces. QA uses Noto CJK and Liberation.",
            "- This is a draft. It is not legal advice, an investment recommendation, or an issued official document.",
            "- v1 creates a new file. It does not safely edit an arbitrary existing Office file.",
        ]
        if (
            plan["file_type"] == "docx"
            and plan.get("include_toc", True)
            and not plan.get("gongwen")
        ):
            lines.append(
                "- The table of contents is a Word field. Word refreshes page numbers on open."
            )
    if gate is not None:
        state = "passed" if gate.get("passed") else "failed"
        lines.extend(["", "## Gate", "", f"- Machine gate: {state}."])
        if not gate.get("passed"):
            failed = [item["name"] for item in gate.get("checks", []) if not item.get("passed")]
            lines.append("- Failed checks: " + ", ".join(failed))
    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")
    return target


def _illustrative(plan: dict) -> str:
    language = plan.get("language", "en")
    if plan.get("illustrative"):
        return (
            "整份计划标为示意。图表和假设里的数字不是已披露实绩。"
            if language == "zh"
            else "The plan is marked illustrative. Chart and assumption figures are not reported results."
        )
    bits = []
    for index, slide in enumerate(plan.get("slides") or [], start=1):
        if slide.get("illustrative"):
            bits.append(str(index))
    if bits:
        label = "、".join(bits) if language == "zh" else ", ".join(bits)
        return (
            f"以下幻灯片标为示意：{label}。"
            if language == "zh"
            else f"Slides marked illustrative: {label}."
        )
    return ""
