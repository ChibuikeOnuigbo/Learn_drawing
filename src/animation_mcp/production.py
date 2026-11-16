"""Deterministic pre-production helpers: shot timing, palette and exposure sheets.

These are planning aids, not generative video/art models or automatic acceptance.
"""
from __future__ import annotations

import colorsys
import math
import re
from typing import Literal

from pydantic import Field, model_validator

from .scene import Strict


class Beat(Strict):
    title: str = Field(min_length=1, max_length=120)
    visual_brief: str = Field(default="", max_length=1000)
    narration: str = Field(default="", max_length=2000)
    seconds: float | None = Field(default=None, gt=0, le=600)
    weight: float | None = Field(default=None, gt=0, le=1000)
    acceptance: str = Field(default="", max_length=500)

    @model_validator(mode="after")
    def one_timing_hint(self):
        if self.seconds is not None and self.weight is not None:
            raise ValueError("Use seconds or weight, not both")
        return self


def _allocate(total: int, weights: list[float]) -> list[int]:
    """Largest-remainder allocation with at least one frame per beat."""
    if total < len(weights):
        raise ValueError("Timeline too short: every beat needs at least one frame")
    weight_sum = sum(weights)
    raw = [total * w / weight_sum for w in weights]
    counts = [max(1, math.floor(x)) for x in raw]
    # If minimums overshoot, remove frames from the largest allocations first.
    while sum(counts) > total:
        i = max((i for i, n in enumerate(counts) if n > 1), key=lambda i: counts[i] - raw[i])
        counts[i] -= 1
    while sum(counts) < total:
        i = max(range(len(raw)), key=lambda i: (raw[i] - counts[i], -i))
        counts[i] += 1
    return counts


def plan_shots(beats: list[dict], fps: int = 24, duration_seconds: float | None = None) -> dict:
    """Create contiguous half-open shot intervals on an exact frame grid.

    Without duration_seconds, every beat must supply seconds and each is rounded.
    With duration_seconds, seconds/weights become proportional hints and the total
    is exact. Word-count or proportional timing is not forced audio alignment.
    """
    if not 1 <= fps <= 60:
        raise ValueError("fps must be 1–60")
    if not beats or len(beats) > 100:
        raise ValueError("Supply 1–100 beats")
    parsed = [Beat.model_validate(b) for b in beats]
    warnings = []
    if duration_seconds is None:
        if any(b.seconds is None for b in parsed):
            raise ValueError("Without duration_seconds, every beat needs seconds")
        counts = [max(1, round(b.seconds * fps)) for b in parsed]
        if any(abs(n / fps - b.seconds) > 1e-9 for b, n in zip(parsed, counts)):
            warnings.append("Durations were rounded to the frame grid")
        total = sum(counts)
        alignment = "explicit beat durations rounded to frames; not audio alignment"
    else:
        if not 0 < duration_seconds <= 600:
            raise ValueError("duration_seconds must be greater than 0 and at most 600")
        total = round(duration_seconds * fps)
        weights = [b.seconds if b.seconds is not None else (b.weight if b.weight is not None else 1.0) for b in parsed]
        counts = _allocate(total, weights)
        if abs(total / fps - duration_seconds) > 1e-9:
            warnings.append("Total duration was rounded to the frame grid")
        alignment = "proportional allocation; confirm against real voiceover/events"
    shots = []
    cursor = 0
    for i, (beat, frames) in enumerate(zip(parsed, counts), 1):
        end = cursor + frames
        shots.append({
            "id": f"shot-{i:02d}", "title": beat.title, "visual_brief": beat.visual_brief,
            "narration": beat.narration, "acceptance": beat.acceptance,
            "start_frame": cursor, "end_frame": end, "frames": frames,
            "start_seconds": cursor / fps, "end_seconds": end / fps,
            "review_frames": sorted({cursor, cursor + frames // 2, end - 1}),
        })
        cursor = end
    return {"fps": fps, "frames": total, "duration_seconds": total / fps,
            "interval_convention": "[start_frame,end_frame)", "alignment": alignment,
            "shots": shots, "warnings": warnings,
            "next": "Author/preview each shot; replace estimated timing with reviewed audio events when needed."}


Harmony = Literal["complementary", "analogous", "triadic", "split_complementary"]


def _hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in rgb)


def _luminance(hex_color: str) -> float:
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def color_palette(base: str, harmony: Harmony = "complementary", dark: bool = True) -> dict:
    """Derive a small role-based palette and measure text/graphics contrast.

    This is deterministic color math, not a learned style model. Contrast ratios
    are WCAG-style luminance ratios; they do not guarantee artistic harmony.
    """
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", base):
        raise ValueError("base must be #rrggbb")
    rgb = tuple(int(base[i:i + 2], 16) / 255 for i in (1, 3, 5))
    offsets = {"complementary": [0, 0.5], "analogous": [0, 1 / 12, -1 / 12],
               "triadic": [0, 1 / 3, -1 / 3], "split_complementary": [0, 5 / 12, 7 / 12]}
    if harmony not in offsets:
        raise ValueError("harmony must be complementary, analogous, triadic or split_complementary")
    h, l, s = colorsys.rgb_to_hls(*rgb)
    s = max(0.35, min(0.85, s))
    offsets = offsets[harmony]
    hues = [(h + o) % 1 for o in offsets]
    def tone(hue, lightness, sat=s):
        return _hex(colorsys.hls_to_rgb(hue, lightness, sat))
    if dark:
        roles = {"background": tone(h, 0.07, 0.30), "surface": tone(h, 0.13, 0.32),
                 "primary": tone(hues[0], 0.58), "secondary": tone(hues[1 % len(hues)], 0.52),
                 "accent": tone(hues[-1], 0.68), "text": tone(h, 0.96, 0.18), "muted": tone(h, 0.70, 0.18)}
    else:
        roles = {"background": tone(h, 0.97, 0.18), "surface": tone(h, 0.92, 0.22),
                 "primary": tone(hues[0], 0.38), "secondary": tone(hues[1 % len(hues)], 0.42),
                 "accent": tone(hues[-1], 0.45), "text": tone(h, 0.10, 0.30), "muted": tone(h, 0.35, 0.20)}
    pairs = {"text/background": ("text", "background"), "text/surface": ("text", "surface"),
             "muted/background": ("muted", "background"), "primary/background": ("primary", "background"),
             "accent/background": ("accent", "background")}
    ratios = {name: round(contrast_ratio(roles[a], roles[b]), 3) for name, (a, b) in pairs.items()}
    warnings = []
    for name in ("text/background", "text/surface", "muted/background"):
        if ratios[name] < 4.5:
            warnings.append(f"{name} contrast {ratios[name]} < 4.5; adjust before using for small text")
    for name in ("primary/background", "accent/background"):
        if ratios[name] < 3:
            warnings.append(f"{name} contrast {ratios[name]} < 3; adjust before using for essential graphics")
    return {"base": base.lower(), "harmony": harmony, "mode": "dark" if dark else "light",
            "roles": roles, "contrast_ratios": ratios, "warnings": warnings,
            "usage": "Assign roles before adding detail; keep the strongest contrast at the focal point.",
            "scope": "Deterministic HLS harmony + luminance contrast; not an artistic quality score."}


class SheetKey(Strict):
    frame: int = Field(ge=0)
    label: str = Field(min_length=1, max_length=120)


def timing_sheet(frames: int, fps: int = 24, keys: list[dict] | None = None,
                 exposure_step: int = 2) -> dict:
    """Build an exposure/dope sheet with held drawing numbers and key labels.

    exposure_step=1 is on ones, 2 on twos, 3 on threes. This schedules drawings;
    it does not create inbetweens or judge spacing.
    """
    if not 1 <= frames <= 18000 or not 1 <= fps <= 60:
        raise ValueError("frames must be 1–18000 and fps 1–60")
    if exposure_step not in (1, 2, 3, 4):
        raise ValueError("exposure_step must be 1, 2, 3 or 4")
    parsed = [SheetKey.model_validate(k) for k in (keys or [])]
    indices = [k.frame for k in parsed]
    if indices != sorted(set(indices)) or any(i >= frames for i in indices):
        raise ValueError("Sheet keys must be unique, ordered and inside the rendered timeline")
    by_frame = {k.frame: k.label for k in parsed}
    rows = [{"frame": f, "seconds": round(f / fps, 6), "drawing": f // exposure_step + 1,
             "new_drawing": f % exposure_step == 0, "key": by_frame.get(f)} for f in range(frames)]
    intervals = []
    bounds = [k.frame for k in parsed]
    for a, b in zip(bounds, bounds[1:]):
        intervals.append({"from_key": by_frame[a], "to_key": by_frame[b], "start_frame": a,
                          "end_frame": b, "span_frames": b - a,
                          "inbetween_drawings": max(0, math.ceil((b - a) / exposure_step) - 1)})
    return {"fps": fps, "frames": frames, "exposure_step": exposure_step,
            "exposure_name": {1: "ones", 2: "twos", 3: "threes", 4: "fours"}[exposure_step],
            "drawing_count": (frames - 1) // exposure_step + 1, "keys": [k.model_dump() for k in parsed],
            "intervals": intervals, "rows": rows,
            "scope": "Exposure schedule only; author drawings/poses and inspect actual spacing."}
