"""Command line: render a plan, or gate a file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from office_skill.deliver import write_delivery_note
from office_skill.render import render_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="office-skill")
    sub = parser.add_subparsers(dest="cmd", required=True)

    render = sub.add_parser("render", help="render a plan JSON to a file")
    render.add_argument("plan")
    render.add_argument("-o", "--output", required=True)
    render.add_argument("--no-note", action="store_true")

    gate = sub.add_parser("gate", help="run machine checks and rasterize pages")
    gate.add_argument("file")
    gate.add_argument("--plan")
    gate.add_argument("--preview-dir")
    gate.add_argument("--result")
    gate.add_argument("--typst")
    gate.add_argument("--skip-render", action="store_true")

    args = parser.parse_args(argv)
    if args.cmd == "render":
        profile_and_plan = _render(Path(args.plan), Path(args.output), note=not args.no_note)
        print(profile_and_plan)
        return 0
    from scripts.qa.gate import run_gate

    result = run_gate(
        Path(args.file),
        plan_path=Path(args.plan) if args.plan else None,
        preview_dir=Path(args.preview_dir) if args.preview_dir else None,
        typst_source=Path(args.typst) if args.typst else None,
        skip_render=args.skip_render,
    )
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.result:
        Path(args.result).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0 if result["passed"] else 1


def _render(plan_path: Path, out_path: Path, *, note: bool) -> str:
    from office_skill.render import load_plan

    plan = load_plan(plan_path)
    profile = render_file(plan_path, out_path)
    if note:
        write_delivery_note(
            plan if plan.get("domain") == profile["id"] else {**plan, "domain": profile["id"]},
            profile,
            out_path,
        )
    return str(out_path)
