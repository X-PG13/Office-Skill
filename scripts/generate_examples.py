"""Render the sample plans, run the gate, and write preview PNGs."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from office_skill.deliver import write_delivery_note
from office_skill.profiles import load_profile
from office_skill.render import render_plan
from scripts.qa.gate import run_gate

SAMPLES = [
    "consulting_pptx",
    "product_pptx",
    "legal_docx",
    "government_docx",
    "finance_xlsx",
    "education_xlsx",
    "academic_pdf",
    "education_pdf",
]


def main() -> int:
    failed = 0
    for name in SAMPLES:
        module = importlib.import_module(f"examples.src.{name}")
        slug = name.replace("_", "-")
        folder = ROOT / "examples" / "out" / slug
        plan_dir = ROOT / "examples" / "plans"
        folder.mkdir(parents=True, exist_ok=True)
        plan_dir.mkdir(parents=True, exist_ok=True)
        plan = module.PLAN
        plan_path = plan_dir / f"{slug}.json"
        plan_path.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (folder / "plan.json").write_text(plan_path.read_text(encoding="utf-8"), encoding="utf-8")
        target = folder / module.FILENAME
        print(f"render {slug}")
        profile = render_plan(plan, target)
        note_profile = profile or load_profile(plan["domain"])
        preview = folder / "preview"
        result = run_gate(target, plan_path=folder / "plan.json", preview_dir=preview)
        (folder / "gate.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        write_delivery_note(plan, note_profile, target, result)
        state = "PASS" if result["passed"] else "FAIL"
        print(f"  {state}  pages={result.get('preview_pages')}")
        if not result["passed"]:
            failed += 1
            for check in result["checks"]:
                if not check["passed"]:
                    print(f"    {check['name']}: {check['detail'][:500]}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
