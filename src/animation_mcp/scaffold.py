"""Create a small, editable project folder without overwriting user work."""
from __future__ import annotations

import importlib.resources
import json
import math
from pathlib import Path
import re

from .production import plan_shots
from .scene import Scene
from .blender_scene import Scene3D


def _retime(frames: list[int], base_last: int, last: int) -> list[int]:
    """Map ordered key/pose frames onto a new grid without duplicate indices.

    When the target grid has room, preserve relative spacing with a minimum
    one-frame gap. When it does not, keep an evenly spaced subset including the
    endpoints rather than emitting an invalid scene.
    """
    if not frames:
        return []
    if len(frames) == 1:
        return [0]
    base_last = max(1, base_last)
    if last >= len(frames) - 1:
        gaps = [b - a for a, b in zip(frames, frames[1:])]
        total = sum(gaps) or 1
        raw = [last * g / total for g in gaps]
        alloc = [max(1, math.floor(x)) for x in raw]
        while sum(alloc) > last:
            i = max((i for i, n in enumerate(alloc) if n > 1), key=lambda i: alloc[i] - raw[i])
            alloc[i] -= 1
        while sum(alloc) < last:
            i = max(range(len(raw)), key=lambda i: (raw[i] - alloc[i], -i))
            alloc[i] += 1
        out = [0]
        for gap in alloc:
            out.append(out[-1] + gap)
        return out
    keep = sorted({round(i * (len(frames) - 1) / last) for i in range(last + 1)})
    return [frames[i] for i in keep]


def _apply_retime(items: list, base_last: int, last: int, get_frame, set_frame) -> list:
    """Return a retimed subset of key/pose items, preserving order and endpoints."""
    if not items:
        return []
    original = [get_frame(item) for item in items]
    mapped = _retime(original, base_last, last)
    if len(mapped) == len(items):
        for item, frame in zip(items, mapped):
            set_frame(item, frame)
        return items
    # Too few target frames for every key: keep the items whose original frames
    # were selected by _retime, then place them on a strictly increasing grid.
    selected = []
    used = set()
    for frame in mapped:
        i = min(range(len(items)), key=lambda j: abs(original[j] - frame) if j not in used else math.inf)
        used.add(i)
        selected.append(items[i])
    selected.sort(key=get_frame)
    for i, item in enumerate(selected):
        set_frame(item, round(i * last / max(1, len(selected) - 1)))
    return selected


def scaffold_project(root: Path, name: str, brief: str = "", fps: int = 24,
                     width: int = 1280, height: int = 720, engine: str = "2d") -> dict:
    """Create projects/<slug>/ with brief, shot plan, starter scene and review.

    Refuses an existing project directory. The starter scene is a proof, not a
    finished film; paths in the returned commands are relative to root.
    """
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        raise ValueError("Project name must be a lowercase slug: letters, digits and hyphens")
    if engine not in ("2d", "3d"):
        raise ValueError("engine must be 2d or 3d")
    if not 1 <= fps <= 60 or not 64 <= width <= 3840 or not 64 <= height <= 3840 or width % 2 or height % 2:
        raise ValueError("Use fps 1–60 and even dimensions within the scene limits")
    if engine == "3d" and (width > 1920 or height > 1920):
        raise ValueError("3D starter dimensions must be at most 1920 per side")
    if len(brief) > 5000:
        raise ValueError("Brief must be at most 5000 characters")
    root = Path(root).resolve()
    project = (root / "projects" / name).resolve()
    if not project.is_relative_to(root):
        raise ValueError("Project path must stay inside the workspace")
    if project.exists():
        raise FileExistsError(f"Project already exists: {project}")
    plan = plan_shots([
        {"title": "Establish", "visual_brief": "Show subject, place and focal point.", "seconds": 2},
        {"title": "Change", "visual_brief": "Perform the main action or reveal the idea.", "seconds": 3},
        {"title": "Resolve", "visual_brief": "Hold the result long enough to read.", "seconds": 2},
    ], fps=fps)
    templates = importlib.resources.files("animation_mcp.templates")
    brief_text = templates.joinpath("brief.md").read_text(encoding="utf-8")
    review_text = templates.joinpath("review.md").read_text(encoding="utf-8")
    brief_text = brief_text.replace("- Project / version:", f"- Project / version: {name} / 001")
    brief_text = brief_text.replace("- Duration / aspect ratio / fps:",
                                    f"- Duration / aspect ratio / fps: {plan['duration_seconds']:g}s proof / {width}×{height} / {fps} fps")
    if brief:
        brief_text += "\n## User brief\n\n" + brief.strip() + "\n"
    scene_rel = f"projects/{name}/scenes/{'scene-3d.json' if engine == '3d' else 'scene-2d.json'}"
    if engine == "2d":
        template_name = "scene-vertical.json" if height > width else "scene-2d.json"
        scene = Scene.model_validate(json.loads(templates.joinpath(template_name).read_text(encoding="utf-8")))
        base_frames, base_width, base_height = scene.frames, scene.width, scene.height
        scene.title = name + " — proof 001"
        scene.width, scene.height, scene.fps = width, height, fps
        scene.frames = plan["frames"]
        if width * height * scene.frames > 2_000_000_000:
            raise ValueError("Starter exceeds the 2D preview pixel-frame budget; reduce dimensions or fps")
        # Restage positions to the canvas while preserving shape aspect ratios.
        sx, sy = width / base_width, height / base_height
        shape_scale = min(sx, sy)
        last = max(1, scene.frames - 1)
        base_last = max(1, base_frames - 1)
        for layer in scene.layers:
            layer.x *= sx; layer.y *= sy
            layer.width *= shape_scale; layer.height *= shape_scale
            layer.font_size *= shape_scale; layer.stroke_width *= shape_scale
            layer.points = [(x * shape_scale, y * shape_scale) for x, y in layer.points]
            if layer.start:
                layer.start = round(layer.start / base_last * last)
            if layer.end is not None:
                layer.end = max(layer.start + 1, min(scene.frames, round(layer.end / base_frames * scene.frames)))
            for track in layer.tracks:
                track.keys = _apply_retime(track.keys, base_last, last,
                                           lambda k: k.frame, lambda k, f: setattr(k, "frame", f))
                for key in track.keys:
                    if track.property == "x": key.value *= sx
                    elif track.property == "y": key.value *= sy
        scene_json = scene.model_dump_json(indent=2)
        render_cmd = f"animation-studio render {scene_rel} --output output/{name}/proof --workspace ."
    else:
        raw = json.loads(templates.joinpath("scene-3d.json").read_text(encoding="utf-8"))
        base_last = max(1, raw.get("frames", 24) - 1)
        raw.update(width=width, height=height, fps=fps, frames=plan["frames"])
        if width * height * raw["frames"] * raw.get("samples", 16) > 1_500_000_000:
            raise ValueError("Starter exceeds the 3D preview budget; reduce dimensions, fps or samples")
        last = plan["frames"] - 1
        for obj in raw["objects"]:
            obj["poses"] = _apply_retime(obj.get("poses", []), base_last, last,
                                         lambda p: p["frame"], lambda p, f: p.__setitem__("frame", f))
        raw["camera_poses"] = _apply_retime(raw.get("camera_poses", []), base_last, last,
                                            lambda p: p["frame"], lambda p, f: p.__setitem__("frame", f))
        scene = Scene3D.model_validate(raw)
        scene_json = scene.model_dump_json(indent=2)
        render_cmd = f"animation-studio render3d {scene_rel} --output output/{name}/proof"
    files = {
        "brief.md": brief_text,
        "shot-plan.json": json.dumps(plan, indent=2) + "\n",
        "review.md": review_text,
        "assets/PROVENANCE.md": "# Asset provenance\n\nRecord each supplied/generated asset, source, license and publication restrictions.\n",
        f"scenes/{'scene-3d.json' if engine == '3d' else 'scene-2d.json'}": scene_json + "\n",
    }
    # Create only after all validation/content preparation succeeds. No overwrite.
    project.mkdir(parents=True)
    try:
        for rel, content in files.items():
            path = project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    except BaseException:
        # Remove only the directory this call just created; never touch pre-existing work.
        import shutil
        shutil.rmtree(project)
        raise
    return {"project": str(project), "engine": engine, "files": sorted(files),
            "shot_plan": plan, "render_command": render_cmd,
            "next": "Edit the brief/scene, preview storytelling frames, then render and review. This scaffold is not a finished animation."}
