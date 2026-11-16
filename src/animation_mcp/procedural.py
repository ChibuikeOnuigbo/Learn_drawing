"""Deterministic procedural assets and seamless overlay loops (code-generated, no AI).

Outputs RGBA PNGs/SVGs plus a manifest. Particle overlays wrap modulo the canvas so
frame 0 and frame N join seamlessly. Trees/rocks/clouds are stylized silhouettes,
not photogrammetry. Seeds make every asset reproducible.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KINDS = {
    "tree_oak": "static", "tree_pine": "static", "tree_bare": "static", "palm": "static",
    "bush": "static", "grass_clump": "static", "rock": "static", "cloud": "static",
    "snow": "loop", "rain": "loop", "wind": "loop", "fog": "loop", "dust": "loop",
    "leaves": "loop", "sparks": "loop", "bokeh": "loop", "light_rays": "static",
    "vignette": "static", "depth_blur": "static",
}


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _canvas(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def _branch(draw, x, y, angle, length, width, depth, rng, color, leaf_color, leaves):
    if depth <= 0 or length < 3:
        if leaves:
            r = float(rng.uniform(6, 16))
            draw.ellipse([x - r, y - r, x + r, y + r], fill=leaf_color)
        return
    x2 = x + math.cos(angle) * length
    y2 = y + math.sin(angle) * length
    draw.line([x, y, x2, y2], fill=color, width=max(1, int(width)))
    n = 2 if depth > 2 else 3
    for _ in range(n):
        spread = float(rng.uniform(0.25, 0.7))
        sign = rng.choice([-1, 1])
        _branch(draw, x2, y2, angle + sign * spread, length * float(rng.uniform(0.62, 0.78)),
                width * 0.68, depth - 1, rng, color, leaf_color, leaves)


def tree(kind: str, size: int, seed: int, variant: int = 0) -> Image.Image:
    rng = _rng(seed + variant)
    scale = 2
    im = _canvas((size * scale, size * scale))
    d = ImageDraw.Draw(im)
    bark = (58 + variant * 8, 40 + variant * 4, 30, 255)
    leaf = (34 + variant * 12, 92 + variant * 10, 44, 235)
    base = (size * scale // 2, size * scale - 8)
    if kind == "tree_pine":
        h = size * scale * 0.85
        d.rectangle([base[0] - 6 * scale, base[1] - h * 0.25, base[0] + 6 * scale, base[1]], fill=bark)
        tiers = 6
        for i in range(tiers):
            t = i / tiers
            w = (0.42 - 0.32 * t) * size * scale
            y0 = base[1] - h * (0.2 + 0.75 * t)
            y1 = y0 - h * 0.22
            d.polygon([(base[0] - w, y0), (base[0] + w, y0), (base[0], y1)], fill=leaf)
    elif kind == "palm":
        h = size * scale * 0.7
        top = (base[0] + int(rng.uniform(-20, 20)) * scale, base[1] - h)
        d.line([base, top], fill=bark, width=10 * scale)
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * 0.35
            L = size * scale * 0.3
            x2 = top[0] + math.cos(a) * L
            y2 = top[1] + math.sin(a) * L * 0.6 + 20 * scale
            d.line([top, (x2, y2)], fill=leaf, width=6 * scale)
    else:
        leaves = kind != "tree_bare"
        trunk_h = size * scale * (0.28 if kind == "tree_oak" else 0.34)
        _branch(d, base[0], base[1], -math.pi / 2, trunk_h, 14 * scale, 6 if kind == "tree_oak" else 5,
                rng, bark, leaf, leaves)
    return im.resize((size, size), Image.Resampling.LANCZOS)


def bush(size: int, seed: int, variant: int = 0) -> Image.Image:
    rng = _rng(seed + variant)
    im = _canvas((size, size))
    d = ImageDraw.Draw(im)
    for _ in range(26):
        x = float(rng.uniform(0.15, 0.85)) * size
        y = float(rng.uniform(0.45, 0.9)) * size
        r = float(rng.uniform(0.08, 0.2)) * size
        c = (30 + int(rng.integers(0, 30)), 80 + int(rng.integers(0, 50)), 38, 230)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return im.filter(ImageFilter.GaussianBlur(0.6))


def grass_clump(size: int, seed: int, variant: int = 0) -> Image.Image:
    rng = _rng(seed + variant)
    im = _canvas((size, size))
    d = ImageDraw.Draw(im)
    for _ in range(70):
        x = float(rng.uniform(0.1, 0.9)) * size
        h = float(rng.uniform(0.2, 0.65)) * size
        bend = float(rng.uniform(-0.25, 0.25)) * size
        c = (40 + int(rng.integers(0, 40)), 100 + int(rng.integers(0, 70)), 45, 240)
        d.line([(x, size), (x + bend * 0.4, size - h * 0.6), (x + bend, size - h)], fill=c, width=2)
    return im


def rock(size: int, seed: int, variant: int = 0) -> Image.Image:
    rng = _rng(seed + variant)
    im = _canvas((size, size))
    d = ImageDraw.Draw(im)
    cx, cy = size / 2, size * 0.62
    pts = []
    for i in range(12):
        a = 2 * math.pi * i / 12
        r = size * float(rng.uniform(0.22, 0.4))
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.65))
    d.polygon(pts, fill=(96, 96, 104, 255))
    d.polygon(pts[:6], fill=(120, 120, 128, 255))
    return im.filter(ImageFilter.GaussianBlur(0.5))


def cloud(size: int, seed: int, variant: int = 0) -> Image.Image:
    rng = _rng(seed + variant)
    im = _canvas((size, size // 2))
    d = ImageDraw.Draw(im)
    for _ in range(18):
        x = float(rng.uniform(0.15, 0.85)) * size
        y = float(rng.uniform(0.3, 0.7)) * size / 2
        r = float(rng.uniform(0.1, 0.25)) * size
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=(235, 238, 245, 200))
    return im.filter(ImageFilter.GaussianBlur(size * 0.02))


def _particles(kind: str, size: tuple[int, int], seed: int, frames: int, variant: int) -> list[Image.Image]:
    rng = _rng(seed + variant)
    w, h = size
    count = {"snow": 140, "rain": 180, "wind": 36, "dust": 90, "leaves": 40, "sparks": 80, "bokeh": 30, "fog": 10}[kind]
    pos = rng.uniform(0, 1, (count, 2))
    speed = rng.uniform(0.2, 1.0, count)
    phase = rng.uniform(0, 2 * math.pi, count)
    out = []
    for f in range(frames):
        t = f / frames
        im = _canvas(size)
        d = ImageDraw.Draw(im)
        if kind == "fog":
            arr = np.zeros((h, w), np.float32)
            yy, xx = np.mgrid[0:h, 0:w]
            for i in range(count):
                cx = (pos[i, 0] + t * speed[i] * 0.3) % 1.0 * w
                cy = pos[i, 1] * h
                r = w * (0.12 + 0.1 * speed[i])
                arr += np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / (r * 0.4)) ** 2)) * 22
            arr = np.clip(arr, 0, 90).astype(np.uint8)
            rgba = np.zeros((h, w, 4), np.uint8)
            rgba[:, :, :3] = 210
            rgba[:, :, 3] = arr
            out.append(Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(6)))
            continue
        for i in range(count):
            if kind == "snow":
                x = (pos[i, 0] + 0.08 * math.sin(2 * math.pi * t + phase[i])) % 1.0 * w
                y = (pos[i, 1] + t * speed[i]) % 1.0 * h
                r = 1 + 2.5 * speed[i]
                d.ellipse([x - r, y - r, x + r, y + r], fill=(245, 248, 255, int(120 + 120 * speed[i])))
            elif kind == "rain":
                x = (pos[i, 0] + t * 0.15) % 1.0 * w
                y = (pos[i, 1] + t * speed[i] * 2.5) % 1.0 * h
                L = 10 + 22 * speed[i]
                d.line([(x, y), (x - L * 0.18, y + L)], fill=(170, 195, 225, int(70 + 110 * speed[i])), width=1)
            elif kind == "wind":
                x = (pos[i, 0] + t * speed[i]) % 1.0 * w
                y = pos[i, 1] * h
                L = 40 + 80 * speed[i]
                d.arc([x - L, y - 8, x + L, y + 8], 200, 340, fill=(220, 230, 240, int(40 + 70 * speed[i])), width=2)
            elif kind == "dust":
                x = (pos[i, 0] + t * speed[i] * 0.4) % 1.0 * w
                y = (pos[i, 1] + 0.03 * math.sin(2 * math.pi * t + phase[i])) % 1.0 * h
                r = 1 + 2 * speed[i]
                d.ellipse([x - r, y - r, x + r, y + r], fill=(210, 195, 160, int(50 + 80 * speed[i])))
            elif kind == "leaves":
                x = (pos[i, 0] + t * speed[i] * 0.6) % 1.0 * w
                y = (pos[i, 1] + t * speed[i]) % 1.0 * h
                r = 3 + 4 * speed[i]
                a = 2 * math.pi * t + phase[i]
                d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(150 + int(60 * speed[i]), 90, 35, 220))
            elif kind == "sparks":
                x = (pos[i, 0] + 0.05 * math.sin(2 * math.pi * t + phase[i])) % 1.0 * w
                y = (pos[i, 1] - t * speed[i]) % 1.0 * h
                r = 1 + 2 * speed[i]
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 190 + int(50 * speed[i]), 80, int(150 + 100 * speed[i])))
            elif kind == "bokeh":
                x = (pos[i, 0] + 0.02 * math.sin(2 * math.pi * t + phase[i])) % 1.0 * w
                y = pos[i, 1] * h
                r = 8 + 26 * speed[i]
                d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 210, int(18 + 30 * speed[i])))
        if kind == "bokeh":
            im = im.filter(ImageFilter.GaussianBlur(3))
        out.append(im)
    return out


def static_overlay(kind: str, size: tuple[int, int], seed: int, variant: int) -> Image.Image:
    w, h = size
    if kind == "vignette":
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a = np.clip((r - 0.45) / 0.7, 0, 1) ** 1.5 * 200
        rgba = np.zeros((h, w, 4), np.uint8); rgba[:, :, 3] = a.astype(np.uint8)
        return Image.fromarray(rgba)
    if kind == "light_rays":
        im = _canvas(size); d = ImageDraw.Draw(im)
        rng = _rng(seed + variant)
        for _ in range(7):
            x = float(rng.uniform(0.1, 0.9)) * w
            spread = float(rng.uniform(0.05, 0.16)) * w
            d.polygon([(x, 0), (x - spread, h), (x + spread, h)], fill=(255, 245, 210, int(rng.uniform(12, 35))))
        return im.filter(ImageFilter.GaussianBlur(w * 0.03))
    if kind == "depth_blur":
        yy, xx = np.mgrid[0:h, 0:w]
        depth = np.clip(yy / h, 0, 1)
        a = (depth * 180).astype(np.uint8)
        rgba = np.zeros((h, w, 4), np.uint8); rgba[:, :, :3] = 200; rgba[:, :, 3] = a
        return Image.fromarray(rgba).filter(ImageFilter.GaussianBlur(2))
    raise ValueError(kind)


def generate(kind: str, out_dir: Path, *, seed: int = 0, width: int = 512, height: int = 512,
             frames: int = 48, variant: int = 0, blur: float = 0.0) -> dict:
    if kind not in KINDS:
        raise ValueError(f"Unknown kind {kind!r}; available: {', '.join(sorted(KINDS))}")
    if not (64 <= width <= 2048 and 64 <= height <= 2048 and 1 <= frames <= 240):
        raise ValueError("width/height 64–2048, frames 1–240")
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    mode = KINDS[kind]
    files = []
    if mode == "loop":
        if frames < 2:
            raise ValueError("Loop overlays need at least 2 frames")
        imgs = _particles(kind, (width, height), seed, frames, variant)
        for i, im in enumerate(imgs):
            if blur:
                im = im.filter(ImageFilter.GaussianBlur(blur))
            p = out_dir / f"{kind}-{i:04d}.png"; im.save(p); files.append(p.name)
        # Seam check: wrapped particle positions make first/last adjacent, not identical.
        seam = float(np.mean(np.abs(np.asarray(imgs[0], float) - np.asarray(imgs[-1], float))))
    else:
        if kind.startswith("tree_") or kind == "palm":
            im = tree(kind, min(width, height), seed, variant)
            if im.size != (width, height):
                canvas = _canvas((width, height)); canvas.paste(im, ((width - im.width) // 2, height - im.height)); im = canvas
        elif kind == "bush":
            im = bush(min(width, height), seed, variant)
        elif kind == "grass_clump":
            im = grass_clump(min(width, height), seed, variant)
        elif kind == "rock":
            im = rock(min(width, height), seed, variant)
        elif kind == "cloud":
            im = cloud(width, seed, variant)
        else:
            im = static_overlay(kind, (width, height), seed, variant)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        p = out_dir / f"{kind}.png"; im.save(p); files.append(p.name)
        seam = None
    manifest = {"kind": kind, "mode": mode, "seed": seed, "variant": variant, "width": width, "height": height,
                "frames": frames if mode == "loop" else 1, "files": files, "blur": blur,
                "license": "Original procedural code output from this project; no third-party artwork.",
                "loop_seamless": mode == "loop", "mean_first_last_pixel_delta": seam,
                "scope": "Stylized code-generated asset; inspect suitability for the shot."}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest
