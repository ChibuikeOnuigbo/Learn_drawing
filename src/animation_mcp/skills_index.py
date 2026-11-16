"""Read packaged, allow-listed animation playbooks without relying on cwd."""
from __future__ import annotations

import importlib.resources
import json


def index() -> dict:
    resource = importlib.resources.files("animation_mcp.skills").joinpath("index.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def read_skill(name: str = "animation-director") -> dict:
    catalog = index()
    entry = next((item for item in catalog["skills"] if item["name"] == name), None)
    if entry is None:
        available = ", ".join(item["name"] for item in catalog["skills"])
        raise ValueError(f"Unknown skill {name!r}. Available: {available}")
    if entry["path"] != f"{name}/SKILL.md":
        raise ValueError("Skill index path does not match its allow-listed name")
    resource = importlib.resources.files("animation_mcp.skills").joinpath(entry["path"])
    return {"name": name, "description": entry["description"],
            "content": resource.read_text(encoding="utf-8"),
            "scope": "Repository guidance; available tools must still be checked."}
