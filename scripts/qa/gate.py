"""Run the machine gate and, unless skipped, rasterize every page."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from scripts.qa import checks, soffice


def run_gate(
    path: Path,
    *,
    plan_path: Path | None = None,
    preview_dir: Path | None = None,
    typst_source: Path | None = None,
    skip_render: bool = False,
) -> dict:
    path = Path(path)
    plan = None
    if plan_path is not None:
        plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    elif path.with_suffix(".plan.json").is_file():
        plan = json.loads(path.with_suffix(".plan.json").read_text(encoding="utf-8"))
    sibling = path.parent / "plan.json"
    if plan is None and sibling.is_file():
        plan = json.loads(sibling.read_text(encoding="utf-8"))
    profile = checks.profile_for(plan, path)
    results = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        results.append({"name": name, "passed": ok, "detail": detail})

    suffix = path.suffix.lower()
    if suffix in {".pptx", ".docx", ".xlsx"}:
        problem = checks.check_ooxml(path)
        add("ooxml", problem is None, problem or "")
    elif suffix == ".pdf":
        pdf_issues = checks.check_pdf(path)
        add("pdf_open", not pdf_issues, "; ".join(pdf_issues))
    else:
        add("filetype", False, f"unsupported {suffix}")

    text = ""
    try:
        text = checks.extract_text(path)
        problems = checks.placeholder_issues(text)
        add("placeholders", not problems, "; ".join(problems))
    except Exception as exc:  # surface a broken file as a failed check, not a crash
        add("placeholders", False, f"could not read text: {exc}")

    if suffix == ".pptx" and profile is not None:
        issues = checks.check_pptx(path, profile)
        add("pptx_layout_and_fonts", not issues, "; ".join(issues[:12]))
    if suffix == ".docx" and profile is not None:
        issues = checks.check_docx(path, profile, plan)
        add("docx_styles_and_fonts", not issues, "; ".join(issues[:12]))
    if suffix == ".xlsx":
        issues = checks.check_xlsx_structure(path)
        add("xlsx_formulas", not issues, "; ".join(issues[:12]))

    if typst_source is None and path.with_suffix(".typ").is_file():
        typst_source = path.with_suffix(".typ")
    if typst_source is not None:
        problem = checks.compile_typst(Path(typst_source))
        add("typst_compile", problem is None, problem or "")

    preview_pages = 0
    if not skip_render and all(item["passed"] for item in results):
        try:
            with tempfile.TemporaryDirectory(prefix="office-skill-preview-") as tmp:
                tmp_path = Path(tmp)
                if suffix == ".pdf":
                    pdf = path
                elif suffix == ".xlsx":
                    pdf = soffice.convert(path, tmp_path / "pdf", "pdf")
                    recalc = soffice.convert(path, tmp_path / "xlsx", "xlsx")
                    recalc_issues = checks.check_xlsx_recalc(recalc, path)
                    add("xlsx_recalc", not recalc_issues, "; ".join(recalc_issues[:12]))
                else:
                    pdf = soffice.convert(path, tmp_path / "pdf", "pdf")
                if preview_dir is not None and (
                    suffix != ".xlsx" or all(item["passed"] for item in results)
                ):
                    pages = soffice.rasterize(pdf, Path(preview_dir))
                    preview_pages = len(pages)
                    add("render", preview_pages > 0, f"{preview_pages} page(s)")
                elif suffix != ".xlsx":
                    # Still require a successful PDF conversion when the caller
                    # did not ask for previews.
                    add("render", pdf.is_file() and pdf.stat().st_size > 0, pdf.name)
        except Exception as exc:
            add("render", False, str(exc))

    passed = all(item["passed"] for item in results) and bool(results)
    return {
        "file": str(path),
        "passed": passed,
        "checks": results,
        "preview_pages": preview_pages,
        "preview_dir": str(preview_dir) if preview_dir else None,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="office-skill-gate")
    parser.add_argument("file")
    parser.add_argument("--plan")
    parser.add_argument("--preview-dir")
    parser.add_argument("--result")
    parser.add_argument("--typst")
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args(argv)
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


if __name__ == "__main__":
    raise SystemExit(main())
