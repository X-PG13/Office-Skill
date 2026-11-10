"""Gate every committed sample. Previews go to a temp dir so CI does not dirty the tree."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.qa.gate import run_gate

EXTS = {".pptx", ".docx", ".xlsx", ".pdf"}


def main() -> int:
    out = ROOT / "examples" / "out"
    files = sorted(path for path in out.glob("*/*") if path.suffix.lower() in EXTS)
    if not files:
        print("no samples under examples/out", file=sys.stderr)
        return 1
    failed = 0
    with tempfile.TemporaryDirectory(prefix="example-gates-") as tmp:
        for path in files:
            result = run_gate(path, preview_dir=Path(tmp) / path.parent.name)
            state = "PASS" if result["passed"] else "FAIL"
            print(f"{state}  {path.relative_to(ROOT)}")
            if not result["passed"]:
                failed += 1
                for check in result["checks"]:
                    if not check["passed"]:
                        print(f"    {check['name']}: {check['detail']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
