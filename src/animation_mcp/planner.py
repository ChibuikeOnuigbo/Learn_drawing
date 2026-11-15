"""Concept → shot plan / seeded variation / image brief, grounded in local traces and assets.

Deterministic planning aid for the connected agent. It does not call a hosted
image model or claim to generate finished artwork; it emits prompts and editable
scene structure that the agent/user can review and render.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path

from .production import plan_shots, color_palette
from .procedural import KINDS
from .styles import catalog as style_catalog
from .tracing import get_frame

WEATHER_ASSETS = {
    "snow": ["snow", "fog", "tree_pine", "vignette"],
    "rain": ["rain", "fog", "tree_oak", "vignette"],
    "wind": ["wind", "leaves", "grass_clump", "tree_bare"],
    "storm": ["rain", "wind", "light_rays", "fog"],
    "clear": ["cloud", "tree_oak", "grass_clump", "bokeh"],
    "night": ["bokeh", "fog", "tree_bare", "vignette"],
    "fire": ["sparks", "dust", "light_rays", "rock"],
}


def _seed_rng(seed: int | str) -> random.Random:
    if isinstance(seed, str):
        seed = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16)
    return random.Random(seed)


def _infer_weather(concept: str, explicit: str | None) -> str:
    if explicit:
        if explicit not in WEATHER_ASSETS:
            raise ValueError(f"weather must be one of {', '.join(WEATHER_ASSETS)}")
        return explicit
    lowered = concept.lower()
    for key in WEATHER_ASSETS:
        if key in lowered:
            return key
    if any(w in lowered for w in ("snow", "winter", "blizzard")):
        return "snow"
    if any(w in lowered for w in ("rain", "drizzle", "wet")):
        return "rain"
    if any(w in lowered for w in ("wind", "gust", "breeze")):
        return "wind"
    return "clear"


def plan_scene(concept: str, *, style_id: str | None = None, seed: int | str = 0,
               duration_seconds: float = 8.0, fps: int = 24, weather: str | None = None,
               reference_video: str | None = None, reference_frame: int | None = None,
               workspace: Path | None = None) -> dict:
    if not concept.strip() or len(concept) > 4000:
        raise ValueError("Provide a concept up to 4000 characters")
    rng = _seed_rng(seed)
    weather = _infer_weather(concept, weather)
    styles = style_catalog(workspace)["styles"]
    style = None
    if style_id:
        style = next((s for s in styles if s["video_id"] == style_id), None)
        if style is None:
            raise ValueError(f"Unknown style_id {style_id!r}; build/review traces first")
    elif styles:
        reviewed = [s for s in styles if s["review_status"] == "reviewed"]
        style = rng.choice(reviewed or styles)
    trace_evidence = None
    if reference_video:
        frame = reference_frame if reference_frame is not None else 0
        data = get_frame(reference_video, frame, workspace)
        trace_evidence = {"video_id": reference_video, "frame": frame, "time": data["time"],
                          "point_count": len(data["points"]), "contour_points": len(data["contours"]),
                          "motion": data["motion"], "status": data["status"],
                          "use": "Read get_trace_frame/get_trace_track for geometry; adapt spacing/arcs, do not copy protected characters."}
    beats = [
        {"title": "Establish", "weight": 1.2,
         "visual_brief": f"Wide establishing view: {concept}. Read silhouette, depth layers and light direction.",
         "acceptance": "Focal subject readable at thumbnail size; background/midground/foreground separated."},
        {"title": "Develop", "weight": 2.0,
         "visual_brief": "Move closer or parallax-shift; reveal the action/concept beat with secondary motion.",
         "acceptance": "Motion has anticipation/overlap; no synchronized grass/cloth unless motivated."},
        {"title": "Accent", "weight": 1.0,
         "visual_brief": f"Weather/FX accent ({weather}) supports the focal beat without obscuring the face/silhouette.",
         "acceptance": "Overlay density protects focal region; depth bands differ in speed/scale."},
        {"title": "Settle", "weight": 1.0,
         "visual_brief": "Hold or ease out; let the pose and atmosphere land.",
         "acceptance": "Final frame is a clean hold; loop seam checked if looping."},
    ]
    shots = plan_shots(beats, fps=fps, duration_seconds=duration_seconds)
    base = rng.choice(["#243b55", "#3b2f4a", "#2f4a3b", "#4a3b2f", "#1f2d3d"])
    palette = color_palette(base, harmony=rng.choice(["complementary", "analogous", "triadic"]), dark=True)
    assets = WEATHER_ASSETS[weather]
    extra = rng.sample([k for k in KINDS if k not in assets], k=min(3, len(KINDS) - len(assets)))
    variations = []
    for i in range(3):
        r = _seed_rng(f"{seed}:{i}")
        variations.append({"id": i, "camera": r.choice(["slow push", "lateral parallax", "crane down", "locked-off"]),
                           "light": r.choice(["cool rim + warm key", "overcast soft", "low sun backlight", "moonlit blue"]),
                           "asset_seed": r.randint(0, 10_000), "weather_density": r.choice(["light", "medium", "heavy"])})
    prompt = (f"Original scene: {concept}. Weather/mood: {weather}. "
              f"{'Style reference tags: ' + ', '.join(style['tags']) + '. ' if style and style.get('tags') else ''}"
              f"Palette base {base}; clear focal silhouette; separate background, midground, subject and foreground overlays. "
              f"Coherent light direction; animation-ready layers; no lettering, watermarks or borrowed characters.")
    return {"concept": concept, "seed": seed, "fps": fps, "weather": weather,
            "style_reference": style and {"video_id": style["video_id"], "tags": style["tags"],
                                          "review_status": style["review_status"], "mechanics": style.get("transferable_mechanics", [])},
            "trace_evidence": trace_evidence, "shot_plan": shots, "palette": palette,
            "suggested_assets": assets + extra, "variations": variations,
            "image_generation_brief": {"prompt": prompt, "generated": False,
                                       "next": "Use the connected agent's image tool, save PNG layers in the workspace, then composite/animate. Label generated art."},
            "scope": "Deterministic plan/prompts; not a finished drawing, hosted image call or reference parity claim."}


def composite_scene(layers: list[dict], *, width: int = 1280, height: int = 720, fps: int = 24,
                    frames: int = 192, background: str = "#101827", title: str = "Composite") -> dict:
    """Build an editable 2D scene from depth-ordered image/overlay layers.

    Each layer: {id, asset, depth (0 far..1 near), x, y, scale, opacity, parallax, loop}.
    Parallax is a small depth-scaled horizontal drift; overlays can use %04d frame tokens.
    """
    from .scene import Scene
    if not layers or len(layers) > 40:
        raise ValueError("Supply 1–40 layers")
    ordered = sorted(layers, key=lambda l: float(l.get("depth", 0.5)))
    scene_layers = []
    for i, l in enumerate(ordered):
        depth = float(l.get("depth", 0.5))
        if not 0 <= depth <= 1:
            raise ValueError("depth must be 0–1")
        lid = l.get("id") or f"layer{i}"
        scale = float(l.get("scale", 1.0))
        x = float(l.get("x", width / 2)); y = float(l.get("y", height / 2))
        drift = float(l.get("parallax", 24.0)) * (depth - 0.5) * 2
        layer = {"id": lid, "kind": "image", "asset": l["asset"], "x": x, "y": y,
                 "width": float(l.get("width", width)), "height": float(l.get("height", height)),
                 "scale": scale, "opacity": float(l.get("opacity", 1.0)),
                 "tracks": [{"property": "x", "keys": [{"frame": 0, "value": x - drift},
                                                       {"frame": frames - 1, "value": x + drift, "easing": "smooth"}]}]}
        scene_layers.append(layer)
    scene = Scene.model_validate({"title": title, "width": width, "height": height, "fps": fps,
                                  "frames": frames, "background": background, "layers": scene_layers})
    return json.loads(scene.model_dump_json())
