"""Strict, editable scene format. All frame intervals are half-open."""
from __future__ import annotations

import math
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Keyframe(Strict):
    frame: int = Field(ge=0)
    value: float
    easing: Literal["linear", "ease_in", "ease_out", "smooth", "hold"] = "smooth"


class Track(Strict):
    property: Literal["x", "y", "scale", "scale_x", "scale_y", "rotation", "opacity", "reveal"]
    keys: list[Keyframe] = Field(min_length=1, max_length=200)

    @model_validator(mode="after")
    def ordered(self):
        frames = [k.frame for k in self.keys]
        if frames != sorted(set(frames)):
            raise ValueError("Keyframe indices must be strictly increasing")
        if self.property in {"opacity", "reveal"} and any(not 0 <= k.value <= 1 for k in self.keys):
            raise ValueError("Opacity and reveal must be between zero and one")
        if self.property in {"scale","scale_x","scale_y"} and any(not 0 < k.value <= 50 for k in self.keys):
            raise ValueError("Scale must be greater than zero and at most 50")
        return self


def sample(track: Track, frame: int) -> float:
    keys = track.keys
    if frame <= keys[0].frame:
        return keys[0].value
    for a, b in zip(keys, keys[1:]):
        if frame < b.frame:
            t = (frame - a.frame) / (b.frame - a.frame)
            t = {"linear": lambda: t, "hold": lambda: 0,
                 "ease_in": lambda: t*t, "ease_out": lambda: 1-(1-t)**3,
                 "smooth": lambda: t*t*(3-2*t)}[b.easing]()
            return a.value + (b.value-a.value)*t
    return keys[-1].value


class Layer(Strict):
    id: str = Field(pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
    kind: Literal["ellipse", "rect", "path", "text", "image", "group"]
    parent: str | None = None
    start: int = Field(default=0, ge=0)
    end: int | None = Field(default=None, ge=1)
    x: float = 0
    y: float = 0
    width: float = Field(default=100, gt=0, le=20000)
    height: float = Field(default=100, gt=0, le=20000)
    fill: str = "#ffffff"
    stroke: str = "none"
    stroke_width: float = Field(default=2, ge=0, le=200)
    # Point-based paths support deterministic stroke-length reveals.
    points: list[tuple[float, float]] = Field(default_factory=list, max_length=5000)
    closed: bool = False
    text: str = Field(default="", max_length=2000)
    font_size: float = Field(default=36, gt=0, le=500)
    asset: str | None = None
    scale: float = Field(default=1, gt=0, le=50)
    scale_x: float = Field(default=1, gt=0, le=50)
    scale_y: float = Field(default=1, gt=0, le=50)
    rotation: float = 0
    opacity: float = Field(default=1, ge=0, le=1)
    reveal: float = Field(default=1, ge=0, le=1)
    tracks: list[Track] = Field(default_factory=list, max_length=8)

    @field_validator("fill", "stroke")
    @classmethod
    def color(cls, value):
        if value != "none" and not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError("Use #rrggbb or none")
        return value

    @model_validator(mode="after")
    def complete(self):
        if self.end is not None and self.end <= self.start:
            raise ValueError("Layer end must be after start")
        if self.kind == "path" and len(self.points) < 2:
            raise ValueError("A path requires at least two points")
        if self.kind == "image" and not self.asset:
            raise ValueError("An image requires an asset")
        props = [t.property for t in self.tracks]
        if len(set(props)) != len(props):
            raise ValueError("Duplicate property tracks")
        return self


class Scene(Strict):
    version: Literal[1] = 1
    title: str = Field(default="Untitled", max_length=200)
    width: int = Field(default=1280, ge=64, le=3840)
    height: int = Field(default=720, ge=64, le=3840)
    fps: int = Field(default=30, ge=1, le=60)
    frames: int = Field(default=150, ge=1, le=18000)
    background: str = "#111827"
    layers: list[Layer] = Field(max_length=500)
    audio: str | None = None

    @field_validator("background")
    @classmethod
    def color(cls, value):
        return Layer.color(value)

    @model_validator(mode="after")
    def timeline(self):
        if self.width % 2 or self.height % 2:
            raise ValueError("H.264 output requires even dimensions")
        ids = [x.id for x in self.layers]
        if len(ids) != len(set(ids)):
            raise ValueError("Layer IDs must be unique")
        parents={}
        for layer in self.layers:
            if layer.parent is not None and (layer.parent not in parents or parents[layer.parent]!='group'):
                raise ValueError('A parent must be a group declared before its children')
            parents[layer.id]=layer.kind
            if layer.start >= self.frames or (layer.end is not None and layer.end > self.frames):
                raise ValueError(f"{layer.id}: layer interval outside scene")
            if any(k.frame > self.frames for t in layer.tracks for k in t.keys):
                raise ValueError(f"{layer.id}: key outside scene")
        return self


def reveal_points(points, amount):
    """Trim by actual polyline arc length, including an interpolated tip."""
    if amount <= 0:
        return []
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    remaining = sum(lengths)*min(amount, 1)
    result = [points[0]]
    for a, b, length in zip(points, points[1:], lengths):
        if length <= remaining:
            result.append(b)
            remaining -= length
        else:
            t = remaining/length
            result.append((a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t))
            break
    return result
