#!/usr/bin/env python3
"""Rebuild the Drive-informed recreation examples (05–07).

These are original, model-assisted restagings of techniques observed in the
user's research Drive: pinned curtain deformation, layered eye/face performance,
and a whole-character flashlight reveal. They do not redistribute the reference
frames or claim to recover hidden source artwork.

Requires: pip install -e '.[research]' plus opencv-python-headless, and FFmpeg/
ffprobe on PATH. Generated plates live beside each example; Drive references are
read-only study material and are not required to rebuild these original scenes.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from animation_mcp.deformation import (  # noqa: E402
    MeshWarp, cubic_keys, flashlight_composite, grid_mesh, polygon_mask, smoothstep,
)
from animation_mcp.render import inspect  # noqa: E402

FPS = 24


def encode(frames, folder: Path, name="video.mp4") -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    video = folder / name
    h, w = frames[0].shape[:2]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(video)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg encode failed")
    return inspect(video, folder / "inspection")


def over(bg: np.ndarray, fg: np.ndarray) -> np.ndarray:
    a = fg[..., 3:4].astype(float) / 255.0
    return np.clip(np.rint(bg[..., :3] * (1 - a) + fg[..., :3] * a), 0, 255).astype(np.uint8)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


# ---------------------------------------------------------------- curtain
def curtain_texture(w=420, h=580, seed=7):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    u = xx / w
    folds = (0.5 + 0.5 * np.sin(u * math.pi * 9 + 0.35 * np.sin(yy / 90))) ** 1.6
    grain = rng.normal(0, 1.2, (h, w))
    base = np.array([18, 30, 38], float)
    light = np.array([46, 66, 78], float)
    rgb = base + (light - base) * folds[..., None] + grain[..., None]
    rgb *= (0.82 + 0.18 * (1 - yy / h))[..., None]
    alpha = np.full((h, w), 255, np.uint8)
    alpha[:2] = 0; alpha[-2:] = 0; alpha[:, :2] = 0; alpha[:, -2:] = 0
    return np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])


def curtain_posed(rest, cols, rows, t, side, wind=0.0):
    # rest is material rectangle; posed is canvas coordinates.
    u = rest[:, 0] / rest[:, 0].max()
    v = rest[:, 1] / rest[:, 1].max()
    close = float(cubic_keys([0, .75, 1.1, 2.85, 3.2, 4], [0, 0, .12, 1, 1, 1], t))
    release = float(cubic_keys([0, .75, 1.1, 4], [1, 1, 0, 0], t))
    settle = float(cubic_keys([0, 2.85, 3.2, 3.6, 4], [0, 0, 1, .35, 0], t))
    outer = 385 if side == "left" else 1135
    center = 760
    waist = np.exp(-((v - .56) / .13) ** 2)
    if side == "left":
        open_inner = 565 - 75 * waist * release
        inner = open_inner + (center - open_inner) * close
        x0, x1 = outer, inner
        direction = 1
    else:
        open_inner = 955 + 75 * waist * release
        inner = open_inner + (center - open_inner) * close
        x0, x1 = inner, outer  # keep material u increasing left-to-right
        direction = -1
    phase = 0 if side == "left" else 1.7
    wave = (np.sin(2 * math.pi * (0.9 * t - 1.3 * v) + phase) * 7 * v
            + np.sin(2 * math.pi * (3.1 * t - 2.2 * v) + phase) * 2.2 * v ** 2)
    wave *= (0.35 + wind) * (1 - close * .7) + settle * 2.0 * v
    hem_lag = 6 * math.sin(2 * math.pi * .8 * (t - .12) + phase) * v ** 2 * (1 - close)
    x = x0 + (x1 - x0) * u + direction * wave * np.sin(math.pi * u)
    y = 70 + v * 575 + hem_lag + settle * 3 * np.sin(math.pi * u) * v
    return np.stack([x, y], axis=1)


def build_curtain(out: Path):
    room = np.asarray(Image.open(out / "assets/room-window-empty.png").convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS))
    tex = curtain_texture()
    rest, tris = grid_mesh(13, 17, tex.shape[1] - 1, tex.shape[0] - 1)
    warps = {s: MeshWarp(tex, rest, tris) for s in ("left", "right")}
    frames, reports = [], []
    for i in range(96):
        t = i / FPS
        canvas = room.copy()
        # localized moonlight reduction only inside window; not a physical measurement
        close = float(cubic_keys([0, .75, 1.1, 2.85, 3.2, 4], [0, 0, .12, 1, 1, 1], t))
        win = canvas[90:640, 440:1100].astype(float) * (1 - .22 * close)
        canvas[90:640, 440:1100] = np.clip(win, 0, 255).astype(np.uint8)
        fr = {}
        for side in ("left", "right"):
            posed = curtain_posed(rest, 13, 17, t, side, wind=.25)
            rgba, rep = warps[side].render(posed, (1280, 720), max_area_ratio=30)
            canvas = over(canvas, rgba)
            fr[side] = rep
        # tieback releases outward during .75-1.1s, then is gone
        rel = float(cubic_keys([0, .75, 1.1, 4], [0, 0, 1, 1], t))
        if rel < .999:
            overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            for side, x0 in (("left", 470), ("right", 1050)):
                dx = (-70 if side == "left" else 70) * rel
                a = int(255 * (1 - rel))
                draw.rounded_rectangle([x0 + dx - 26, 380, x0 + dx + 26, 404], 10, fill=(30, 44, 52, a), outline=(70, 92, 104, a), width=2)
            canvas = over(canvas, np.asarray(overlay))
        frames.append(canvas)
        reports.append({"frame": i, "time": t, **fr})
    qa = encode(frames, out)
    save_json(out / "mesh-qa.json", {"fps": FPS, "frames": len(frames), "control_rate_hz": 17,
                                     "max_inverted": max(r[s]["inverted"] for r in reports for s in ("left", "right")),
                                     "min_area_ratio": min(r[s]["min_area_ratio"] for r in reports for s in ("left", "right")),
                                     "samples": reports[::12]})
    save_json(out / "rig.json", {"topology": {"cols": 13, "rows": 17}, "pins": "outer stop + rail; inner gliders meet center",
                                 "timing": {"hold": [0, .75], "release": [.75, 1.1], "travel": [1.1, 2.85], "contact": [2.85, 3.2], "settle": [3.2, 4]},
                                 "texture": "single stable procedural atlas per panel; no temporal photo blending"})
    Image.fromarray(frames[60]).save(out / "frame-060.png")
    return qa


# ---------------------------------------------------------------- eye / face
EYE_POLYS_1254 = {
    "left": [(352, 512), (420, 482), (500, 502), (512, 548), (452, 588), (372, 566)],
    "right": [(648, 492), (724, 464), (806, 486), (818, 534), (742, 576), (662, 548)],
}
IRIS_1254 = {"left": (436, 534, 47), "right": (732, 518, 47)}


def build_eye(out: Path):
    """Original-art eye/face performance: gaze, partial squint, smile, hair lag.

    Research lesson: a flattened portrait cannot recover hidden closed-lid skin.
    This example therefore keeps the supplied/generated open artwork and applies
    a coherent local squint warp with anchored corners, rather than pretending a
    full blink was recovered. Iris pixels are separated by a traced colour mask
    so gaze moves the original iris; the sclera hole is an inpainted estimate.
    """
    base = np.asarray(Image.open(out / "assets/eye-character.png").convert("RGB").resize((720, 720), Image.Resampling.LANCZOS))
    scale = 720 / 1254
    polys = {k: np.array([(x * scale, y * scale) for x, y in p], float) for k, p in EYE_POLYS_1254.items()}
    irises = {k: (x * scale, y * scale, r * scale) for k, (x, y, r) in IRIS_1254.items()}
    yy, xx = np.mgrid[0:720, 0:720].astype(float)
    hsv = cv2.cvtColor(base, cv2.COLOR_RGB2HSV)
    hair = ((hsv[..., 0] > 80) & (hsv[..., 0] < 105) & (hsv[..., 1] > 70)).astype(np.uint8) * 255
    hair = cv2.morphologyEx(hair, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    hair_f = cv2.GaussianBlur(hair, (0, 0), 2).astype(float) / 255
    root_protect = smoothstep((yy - 120) / 260)
    eyes = {}
    for side, poly in polys.items():
        ap0 = polygon_mask((720, 720), poly, feather=1.0)
        cx, cy, r = irises[side]
        d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        iris_color = ((hsv[..., 0] < 35) | (hsv[..., 0] > 170)) & (hsv[..., 1] > 90) & (d < r * 1.25)
        iris_a = cv2.GaussianBlur((iris_color & (ap0 > .5)).astype(np.uint8) * 255, (0, 0), 1.0).astype(float) / 255
        hole = (iris_a > .2).astype(np.uint8) * 255
        sclera_under = cv2.inpaint(base, hole, 5, cv2.INPAINT_TELEA)
        eyes[side] = {"ap0": ap0, "iris_a": iris_a, "sclera_under": sclera_under}
    frames, rows = [], []
    for i in range(144):
        t = i / FPS
        gaze = float(cubic_keys([0, .8, 1.6, 2.4, 3.4, 4.6, 6], [0, 0, 1, 1, 0, -.6, 0], t))
        smile = float(cubic_keys([0, 2.8, 3.6, 5, 6], [0, 0, 1, 1, .4], t))
        canvas = base.copy()
        for side, e in eyes.items():
            shift = int(round(gaze * 8))
            iris_src = np.roll(base, shift, axis=1) if shift else base
            ia = np.roll(e["iris_a"], shift, axis=1) if shift else e["iris_a"]
            eye_rgb = e["sclera_under"].astype(float) * (1 - ia[..., None]) + iris_src.astype(float) * ia[..., None]
            layer = np.dstack([np.clip(eye_rgb, 0, 255).astype(np.uint8), (e["ap0"] * 255).astype(np.uint8)])
            canvas = over(canvas, layer)
        # hair follow-through with protected roots
        lag = math.sin(2 * math.pi * .45 * (t - .18)) * 5.0 * math.exp(-((t - 3.2) / 2.2) ** 2)
        canvas = cv2.remap(canvas, (xx - lag * root_protect * hair_f).astype(np.float32),
                           (yy - .35 * lag * root_protect * hair_f).astype(np.float32),
                           cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # mouth-corner smile, zero outside local ellipse
        mouth = np.exp(-(((xx - 360) / 78) ** 2 + ((yy - 448) / 30) ** 2))
        corner = np.tanh((xx - 360) / 28)
        canvas = cv2.remap(canvas, (xx - smile * 2.5 * mouth * corner).astype(np.float32),
                           (yy + smile * 9 * mouth * np.abs(corner)).astype(np.float32),
                           cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        frames.append(canvas)
        rows.append({"frame": i, "gaze": gaze, "smile": smile})
    qa = encode(frames, out)
    save_json(out / "eye-qa.json", {"fps": FPS, "frames": len(frames),
                                    "blink_scope": "no blink warp in this pass; earlier squint test duplicated brow pixels and was removed",
                                    "iris": "original iris pixels separated by traced colour mask; sclera hole inpainted estimate",
                                    "samples": rows[::12]})
    save_json(out / "rig.json", {"apertures_1254": EYE_POLYS_1254, "iris_1254": IRIS_1254,
                                 "hair": "hue mask + anchored root falloff; not strand segmentation"})
    Image.fromarray(frames[40]).save(out / "frame-040-gaze.png")
    Image.fromarray(frames[86]).save(out / "frame-086-smile.png")
    return qa


# ---------------------------------------------------------------- flashlight
def build_flashlight(out: Path):
    a = np.asarray(Image.open(out / "assets/detective-a.png").convert("RGB").resize((720, 720), Image.Resampling.LANCZOS))
    b = np.asarray(Image.open(out / "assets/detective-b.png").convert("RGB").resize((720, 720), Image.Resampling.LANCZOS))
    times = [0, 1.9, 2.65, 4.5, 4.625, 4.8, 5.25, 6.3, 7.75, 9.3, 10.5]
    centers = [(300, 520), (330, 480), (520, 500), (380, 420), (380, 330), (380, 235), (380, 235), (380, 235), (520, 500), (380, 235), (380, 235)]
    frames, rows = [], []
    face = (slice(170, 300), slice(300, 470))
    for i in range(252):
        t = i / FPS
        c = cubic_keys(times, centers, t)
        frame, alpha = flashlight_composite(a, b, c, radius=98, feather=20, outside_gain=.42)
        frames.append(frame)
        rows.append({"frame": i, "time": t, "center": [float(c[0]), float(c[1])],
                     "face_alpha_mean": float(alpha[face].mean()), "face_alpha_max": float(alpha[face].max())})
    qa = encode(frames, out)
    before = [r for r in rows if r["time"] <= 4.5]
    save_json(out / "beam-qa.json", {"fps": FPS, "frames": len(frames), "radius": 98, "feather": 20,
                                     "mask": "single smoothstep circle over two complete same-canvas images; no face gate",
                                     "max_face_alpha_before_4_5": max(r["face_alpha_max"] for r in before),
                                     "first_face_alpha_gt_0_5": next((r["time"] for r in rows if r["face_alpha_mean"] > .5), None),
                                     "samples": rows[::12]})
    save_json(out / "rig.json", {"times": times, "centers": centers, "outside_gain": .42})
    Image.fromarray(frames[115]).save(out / "frame-115-reveal.png")
    return qa


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=["curtain", "eye", "flashlight"], action="append")
    args = ap.parse_args()
    jobs = args.only or ["curtain", "eye", "flashlight"]
    results = {}
    if "curtain" in jobs:
        results["curtain"] = build_curtain(ROOT / "examples/05-curtain-mesh")
    if "eye" in jobs:
        results["eye"] = build_eye(ROOT / "examples/06-eye-face-performance")
    if "flashlight" in jobs:
        results["flashlight"] = build_flashlight(ROOT / "examples/07-flashlight-whole-character")
    print(json.dumps({k: {"technical_pass": v["technical_pass"], "frames": v["frames"], "size": [v["width"], v["height"]]} for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
