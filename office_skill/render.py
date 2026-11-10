"""Load one profile, validate the plan, dispatch one engine."""

from __future__ import annotations

import json
from pathlib import Path

from office_skill.plan import validate_plan
from office_skill.profiles import load_profile, resolve_domain


def load_plan(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_plan(plan: dict, out_path: Path) -> dict:
    profile = load_profile(plan["domain"])
    plan = dict(plan)
    plan["domain"] = resolve_domain(plan["domain"])
    validate_plan(plan, profile)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    file_type = plan["file_type"]
    if file_type == "pptx":
        from engines.pptx.engine import render
    elif file_type == "docx":
        from engines.docx.engine import render
    elif file_type == "xlsx":
        from engines.xlsx.engine import render
    elif file_type == "pdf":
        from engines.pdf.engine import render
    else:
        raise ValueError(file_type)
    render(plan, profile, out_path)
    return profile


def render_file(plan_path: Path, out_path: Path) -> dict:
    return render_plan(load_plan(plan_path), out_path)
