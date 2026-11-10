"""Headless LibreOffice conversion with an isolated profile.

A shared soffice process hangs in some sandboxes. Each call gets its own
user profile and the headless VCL plugin.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


def convert(source: Path, outdir: Path, target_ext: str, timeout: int = 180) -> Path:
    source = Path(source)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="office-skill-lo-"))
    env = os.environ.copy()
    env["SAL_USE_VCLPLUGIN"] = "svp"
    env.setdefault("LANG", "C.UTF-8")
    cmd = [
        "soffice",
        f"-env:UserInstallation=file://{profile}",
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--nologo",
        "--convert-to",
        target_ext,
        "--outdir",
        str(outdir),
        str(source),
    ]
    completed = subprocess.run(
        cmd, env=env, capture_output=True, text=True, timeout=timeout, check=False
    )
    produced = outdir / f"{source.stem}.{target_ext.split(':')[0]}"
    if completed.returncode != 0 or not produced.is_file():
        detail = (completed.stdout + "\n" + completed.stderr).strip()
        raise RuntimeError(f"LibreOffice failed to convert {source.name} to {target_ext}: {detail}")
    return produced


def rasterize(pdf: Path, outdir: Path, dpi: int = 110) -> list[Path]:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = outdir / "page"
    cmd = ["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(prefix)]
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "pdftoppm failed")
    pages = sorted(outdir.glob("page*.png"))
    if not pages:
        raise RuntimeError(f"pdftoppm wrote no pages for {pdf}")
    return pages
