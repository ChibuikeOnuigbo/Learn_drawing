"""Art-style catalog backed by measured trace statistics and reviewed evidence."""
from __future__ import annotations

import json
import os
from pathlib import Path

from .tracing import library_root, read_catalog

PACKAGE = Path(__file__).resolve().parent


def _reviewed() -> dict:
    path = PACKAGE / "models/style-catalog.json"
    if not path.exists():
        return {"schema": 1, "styles": []}
    return json.loads(path.read_text())


def catalog(workspace: Path | None = None) -> dict:
    traces = read_catalog(workspace)
    reviewed = {s["video_id"]: s for s in _reviewed().get("styles", [])}
    entries = []
    for vid, info in traces.get("videos", {}).items():
        r = reviewed.get(vid, {})
        entries.append({"video_id": vid, "source": info["source"], "coverage": info["coverage"],
                        "measured": info["style"], "tags": r.get("tags", []),
                        "reviewed_notes": r.get("notes"), "evidence_frames": r.get("evidence_frames", []),
                        "review_status": "reviewed" if r else "measured-only; tags/notes pending visual review",
                        "transferable_mechanics": r.get("mechanics", [])})
    return {"schema": 1, "root": traces.get("root"), "styles": entries,
            "scope": "Palette/edge/motion statistics are measured; artistic labels require review of actual frames."}


def search(query: str = "", workspace: Path | None = None, limit: int = 10) -> dict:
    q = query.lower().strip()
    entries = catalog(workspace)["styles"]
    scored = []
    for e in entries:
        text = " ".join([e["video_id"], *e["tags"], e.get("reviewed_notes") or "",
                         *e.get("transferable_mechanics", [])]).lower()
        score = sum(1 for word in q.split() if word in text) if q else 0
        if not q or score:
            scored.append((score, e))
    scored.sort(key=lambda x: (-x[0], x[1]["video_id"]))
    return {"query": query, "results": [e for _, e in scored[:limit]],
            "scope": "Keyword match over reviewed tags/notes and video ids; not CLIP or a quality ranking."}
