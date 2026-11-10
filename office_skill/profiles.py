"""Load one domain profile. The router never loads every palette at once."""

from __future__ import annotations

import json
from pathlib import Path

from office_skill.paths import repo_root

ALIASES = {
    "marketing": "brand",
    "tech": "product",
    "technology": "product",
    "gongwen": "government",
    "official": "government",
    "公文": "government",
    "strategy": "consulting",
    "ib": "finance",
    "law": "legal",
}


class ProfileError(ValueError):
    pass


def list_domains() -> list[str]:
    root = repo_root() / "profiles"
    return sorted(path.stem for path in root.glob("*.json"))


def resolve_domain(domain: str) -> str:
    key = domain.strip()
    lowered = key.lower()
    return ALIASES.get(key, ALIASES.get(lowered, lowered))


def profile_paths(domain: str) -> tuple[Path, Path]:
    canonical = resolve_domain(domain)
    root = repo_root() / "profiles"
    return root / f"{canonical}.json", root / f"{canonical}.md"


def load_profile(domain: str) -> dict:
    path, _md = profile_paths(domain)
    if not path.is_file():
        known = ", ".join(list_domains()) or "(none)"
        raise ProfileError(f"Unknown domain {domain!r}. Known profiles: {known}.")
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_profile(data)
    if data["id"] != path.stem:
        raise ProfileError(f"{path.name} id is {data['id']!r}, expected {path.stem!r}.")
    return data


def validate_profile(data: dict) -> None:
    for key in ("id", "palette", "page", "type", "labels", "tones", "model"):
        if key not in data:
            raise ProfileError(f"Profile {data.get('id', '?')} is missing {key}.")
    palette = data["palette"]
    for key in (
        "ink",
        "paper",
        "muted",
        "line",
        "accent",
        "series",
        "dark",
        "on_dark",
        "on_dark_muted",
        "mark",
    ):
        if key not in palette:
            raise ProfileError(f"Palette missing {key}.")
    if not palette["series"]:
        raise ProfileError("Palette series is empty.")
    for fmt, fields in {
        "pptx": ("width_in", "height_in", "margin_in"),
        "docx": ("paper", "margins_mm"),
        "pdf": ("paper", "margins_mm"),
        "xlsx": ("paper",),
    }.items():
        block = data["page"].get(fmt)
        if not isinstance(block, dict):
            raise ProfileError(f"page.{fmt} missing.")
        for field in fields:
            if field not in block:
                raise ProfileError(f"page.{fmt}.{field} missing.")
    for fmt in ("pptx", "docx", "xlsx", "pdf"):
        block = data["type"].get(fmt)
        if not isinstance(block, dict) or "latin" not in block or "ea" not in block:
            raise ProfileError(f"type.{fmt} needs latin and ea.")
    if "body" not in data["type"].get("scale", {}):
        raise ProfileError("type.scale.body missing.")
    for lang in ("zh", "en"):
        labels = data["labels"].get(lang)
        if not isinstance(labels, dict) or "illustrative" not in labels:
            raise ProfileError(f"labels.{lang}.illustrative missing.")
    for tone in ("cover", "section", "close", "content"):
        if data["tones"].get(tone) not in {"light", "dark"}:
            raise ProfileError(f"tones.{tone} must be light or dark.")
    for key in ("input_font", "formula_font", "cross_font", "input_fill"):
        if key not in data["model"]:
            raise ProfileError(f"model.{key} missing.")
