"""Locate the skill repository, whether or not the package is installed editable."""

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "SKILL.md").is_file() and (candidate / "profiles").is_dir():
            return candidate
    raise FileNotFoundError("Office-Skill repo root not found (expected SKILL.md and profiles/)")
