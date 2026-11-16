"""Fixed-topology mesh warps, premultiplied alpha and whole-image reveal math.

This module is deliberately small and deterministic. It does not infer hidden
artwork, segment hair, or claim physical cloth. Callers supply traced controls
and stable source layers; the helpers validate geometry and resample once.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np
from PIL import Image
from scipy.interpolate import CubicHermiteSpline
from scipy.ndimage import map_coordinates


def premultiply(rgba: np.ndarray) -> np.ndarray:
    a = rgba[..., 3:4].astype(np.float64) / 255.0
    out = rgba.astype(np.float64).copy()
    out[..., :3] *= a
    return out


def unpremultiply(arr: np.ndarray) -> np.ndarray:
    a = arr[..., 3:4] / 255.0
    out = arr.copy()
    np.divide(arr[..., :3], a, out=out[..., :3], where=a > 1e-8)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def signed_areas(vertices: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    a, b, c = vertices[triangles[:, 0]], vertices[triangles[:, 1]], vertices[triangles[:, 2]]
    return 0.5 * ((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0]))


def grid_mesh(cols: int, rows: int, width: float, height: float) -> tuple[np.ndarray, np.ndarray]:
    if cols < 2 or rows < 2:
        raise ValueError("Mesh needs at least 2x2 vertices")
    xs = np.linspace(0, width, cols)
    ys = np.linspace(0, height, rows)
    v = np.stack(np.meshgrid(xs, ys, indexing="xy"), axis=-1).reshape(-1, 2)
    tris = []
    for r in range(rows - 1):
        for c in range(cols - 1):
            i = r * cols + c
            tris += [[i, i + 1, i + cols], [i + 1, i + cols + 1, i + cols]]
    return v, np.asarray(tris, dtype=np.int32)


def fold_report(rest: np.ndarray, posed: np.ndarray, triangles: np.ndarray) -> dict:
    a0 = signed_areas(rest, triangles)
    a1 = signed_areas(posed, triangles)
    if np.any(np.abs(a0) < 1e-9):
        raise ValueError("Degenerate rest triangle")
    ratio = a1 / a0
    return {
        "triangles": int(len(triangles)),
        "inverted": int(np.sum(ratio <= 0)),
        "min_area_ratio": float(np.min(ratio)),
        "max_area_ratio": float(np.max(ratio)),
        "max_vertex_displacement": float(np.max(np.linalg.norm(posed - rest, axis=1))),
    }


def cubic_keys(times: Sequence[float], values: Sequence, t: float) -> np.ndarray:
    """Cubic Hermite through keys; repeated pause values get zero velocity."""
    ts = np.asarray(times, dtype=float)
    vs = np.asarray(values, dtype=float)
    if ts.ndim != 1 or len(ts) < 2 or np.any(np.diff(ts) <= 0):
        raise ValueError("Keys need strictly increasing times")
    if vs.shape[0] != len(ts):
        raise ValueError("Key/value count mismatch")
    flat = vs.reshape(len(ts), -1)
    d = np.zeros_like(flat)
    for i in range(len(ts)):
        if i == 0:
            slope = (flat[1] - flat[0]) / (ts[1] - ts[0])
            d[i] = 0 if np.allclose(slope, 0) else slope
        elif i == len(ts) - 1:
            slope = (flat[-1] - flat[-2]) / (ts[-1] - ts[-2])
            d[i] = 0 if np.allclose(slope, 0) else slope
        else:
            s0 = (flat[i] - flat[i - 1]) / (ts[i] - ts[i - 1])
            s1 = (flat[i + 1] - flat[i]) / (ts[i + 1] - ts[i])
            d[i] = 0 if np.allclose(s0, 0) or np.allclose(s1, 0) else 0.5 * (s0 + s1)
    tc = float(np.clip(t, ts[0], ts[-1]))
    out = np.stack([CubicHermiteSpline(ts, flat[:, k], d[:, k])(tc) for k in range(flat.shape[1])], axis=-1)
    return out.reshape(vs.shape[1:]) if vs.ndim > 1 else float(out.reshape(-1)[0])


@dataclass
class MeshWarp:
    """Inverse piecewise-affine warp with cached rest topology.

    ``source`` is RGBA uint8. ``rest`` and ``triangles`` define material
    coordinates. ``posed`` moves those same vertices; no retriangulation occurs.
    """
    source: np.ndarray
    rest: np.ndarray
    triangles: np.ndarray

    def __post_init__(self):
        self.source = np.asarray(self.source, dtype=np.uint8)
        if self.source.ndim != 3 or self.source.shape[2] != 4:
            raise ValueError("Source must be RGBA")
        self.rest = np.asarray(self.rest, dtype=np.float64)
        self.triangles = np.asarray(self.triangles, dtype=np.int32)
        if self.rest.ndim != 2 or self.rest.shape[1] != 2:
            raise ValueError("Rest vertices must be Nx2")
        if np.any(self.triangles < 0) or np.any(self.triangles >= len(self.rest)):
            raise ValueError("Triangle index outside mesh")
        self._pm = premultiply(self.source)
        self._areas0 = signed_areas(self.rest, self.triangles)
        if np.any(np.abs(self._areas0) < 1e-9):
            raise ValueError("Degenerate rest mesh")

    def render(self, posed: np.ndarray, size: tuple[int, int], *, max_area_ratio: float = 4.0) -> tuple[np.ndarray, dict]:
        posed = np.asarray(posed, dtype=np.float64)
        if posed.shape != self.rest.shape:
            raise ValueError("Posed mesh must keep rest vertex count/order")
        report = fold_report(self.rest, posed, self.triangles)
        if report["inverted"] or report["min_area_ratio"] < 1.0 / max_area_ratio or report["max_area_ratio"] > max_area_ratio:
            raise ValueError(f"Mesh fold/compression outside budget: {report}")
        w, h = size
        out = np.zeros((h, w, 4), dtype=np.float64)
        covered = np.zeros((h, w), dtype=bool)
        for tri in self.triangles:
            dst = posed[tri]
            src = self.rest[tri]
            x0 = max(0, int(math.floor(dst[:, 0].min())))
            x1 = min(w - 1, int(math.ceil(dst[:, 0].max())))
            y0 = max(0, int(math.floor(dst[:, 1].min())))
            y1 = min(h - 1, int(math.ceil(dst[:, 1].max())))
            if x1 < x0 or y1 < y0:
                continue
            yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1]
            p = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(np.float64)
            a, b, c = dst
            v0, v1 = b - a, c - a
            den = v0[0] * v1[1] - v0[1] * v1[0]
            if abs(den) < 1e-12:
                continue
            q = p - a
            u = (q[:, 0] * v1[1] - q[:, 1] * v1[0]) / den
            v = (q[:, 0] * v0[1] - q[:, 1] * v0[0]) / -den
            inside = (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6)
            if not np.any(inside):
                continue
            uvw = np.stack([1 - u - v, u, v], axis=1)[inside]
            src_pts = uvw @ src
            coords = np.stack([src_pts[:, 1], src_pts[:, 0]])
            sampled = np.stack([map_coordinates(self._pm[..., k], coords, order=1, mode="constant", cval=0.0) for k in range(4)], axis=1)
            px = p[inside].astype(int)
            # Deterministic last-triangle wins on shared edges; interiors do not overlap.
            out[px[:, 1], px[:, 0]] = sampled
            covered[px[:, 1], px[:, 0]] = True
        out[~covered] = 0
        return unpremultiply(out), report


def smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def flashlight_composite(base: np.ndarray, alternate: np.ndarray, center: Sequence[float], radius: float,
                         feather: float = 20.0, outside_gain: float = 0.42) -> tuple[np.ndarray, np.ndarray]:
    """One pixelwise mask over two complete same-canvas images.

    Returns uint8 RGB and float alpha. There is no face gate or body exception.
    """
    base = np.asarray(base, dtype=np.float64)
    alternate = np.asarray(alternate, dtype=np.float64)
    if base.shape != alternate.shape or base.ndim != 3 or base.shape[2] < 3:
        raise ValueError("Layers must be same-canvas RGB/RGBA")
    if radius <= 0 or feather < 0:
        raise ValueError("Invalid beam geometry")
    h, w = base.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2)
    alpha = smoothstep((radius + feather / 2 - d) / max(feather, 1e-9))
    a = alpha[..., None]
    out = (1 - a) * (outside_gain * base[..., :3]) + a * np.clip(1.03 * alternate[..., :3] + 2, 0, 255)
    return np.clip(np.rint(out), 0, 255).astype(np.uint8), alpha


def polygon_mask(size: tuple[int, int], polygon: Sequence[Sequence[float]], feather: float = 0.0) -> np.ndarray:
    from PIL import ImageDraw, ImageFilter
    w, h = size
    im = Image.new("L", (w, h), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in polygon], fill=255)
    if feather > 0:
        im = im.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(im, dtype=np.float64) / 255.0
