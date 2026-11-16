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
    MeshWarp, cubic_keys, flashlight_composite, fold_report, grid_mesh, polygon_mask, smoothstep,
)
from animation_mcp.cloth import ClothPanel, fold_shading  # noqa: E402
from animation_mcp.eye_rig import apply_eye, trace_aperture  # noqa: E402
from animation_mcp.render import inspect  # noqa: E402

FPS = 24


def encode(frames, folder: Path, name="video.mp4", fps: int = FPS, inspection_name="inspection") -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    video = folder / name
    h, w = frames[0].shape[:2]
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-an", "-c:v", "libx264",
           "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(video)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg encode failed")
    return inspect(video, folder / inspection_name)


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


CONTROL_HZ = 17
DURATION = 4.0


def _curtain_controls():
    """Simulate both panels at 17 Hz; return control vertex arrays + solver QA."""
    rest, tris = grid_mesh(13, 17, 419, 579)
    n_controls = int(round(DURATION * CONTROL_HZ)) + 1
    panels = {s: ClothPanel(13, 17, 375, 565, s, iterations=20, wind=18, gravity=120)
              for s in ("left", "right")}
    controls = {s: [] for s in panels}
    solver_reports, fallbacks = [], 0
    for i in range(n_controls):
        t = i / CONTROL_HZ
        cl = float(np.clip((t - .9) / 2.0, 0, 1)); cl = cl * cl * (3 - 2 * cl)
        row = {"control": i, "time": t}
        for side, p in panels.items():
            if side == "left":
                outer, open_inner = 385, 565
                inner = open_inner + (760 - open_inner) * cl
                span, tie_x, seam = (outer, inner), 490, 760
            else:
                outer, open_inner = 1135, 955
                inner = open_inner + (760 - open_inner) * cl
                span, tie_x, seam = (inner, outer), 1030, 760
            rep = p.step(1 / CONTROL_HZ, rail_y=70, span=span, closure=cl,
                         tie=max(0.0, 1 - t / .9), tie_x=tie_x, seam_x=seam,
                         t=t, substeps=8)
            pos = p.project_monotonic(1.0).reshape(17, 13, 2)
            for c in range(13):
                pos[:, c, 1] = np.maximum.accumulate(pos[:, c, 1] + np.arange(17) * .5) - np.arange(17) * .5
            pos = pos.reshape(-1, 2)
            fr = fold_report(rest, pos, tris)
            if fr["inverted"] or fr["min_area_ratio"] < .05:
                safe = curtain_posed(rest, 13, 17, t, side, wind=.25)
                lo, hi = 0., 1.
                for _ in range(14):
                    mid = (lo + hi) / 2
                    rr = fold_report(rest, pos * (1 - mid) + safe * mid, tris)
                    if rr["inverted"] == 0 and rr["min_area_ratio"] > .05:
                        hi = mid
                    else:
                        lo = mid
                pos = pos * (1 - hi) + safe * hi
                fallbacks += 1
            controls[side].append(pos)
            row[side] = {**rep, "fallback_blend": float(hi) if fr["inverted"] or fr["min_area_ratio"] < .05 else 0.0}
        solver_reports.append(row)
    return rest, tris, {s: np.asarray(v) for s, v in controls.items()}, solver_reports, fallbacks


def _render_curtain_frame(rest, tris, warps, controls, room, t):
    canvas = room.copy()
    cl = float(np.clip((t - .9) / 2.0, 0, 1)); cl = cl * cl * (3 - 2 * cl)
    win = canvas[90:640, 440:1100].astype(float) * (1 - .22 * cl)
    canvas[90:640, 440:1100] = np.clip(win, 0, 255).astype(np.uint8)
    times = np.arange(len(controls["left"])) / CONTROL_HZ
    fr = {}
    for side in ("left", "right"):
        posed = cubic_keys(times, controls[side], t)
        check = fold_report(rest, posed, tris)
        if check["inverted"] or check["min_area_ratio"] < .03:
            safe = curtain_posed(rest, 13, 17, t, side, wind=.25)
            lo, hi = 0., 1.
            for _ in range(14):
                mid = (lo + hi) / 2
                rr = fold_report(rest, posed * (1 - mid) + safe * mid, tris)
                if rr["inverted"] == 0 and rr["min_area_ratio"] > .03:
                    hi = mid
                else:
                    lo = mid
            posed = posed * (1 - hi) + safe * hi
        rgba, rep = warps[side].render(posed, (1280, 720), max_area_ratio=50)
        canvas = over(canvas, rgba)
        fr[side] = rep
    rel = float(cubic_keys([0, .75, 1.1, 4], [0, 0, 1, 1], t))
    if rel < .999:
        overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for side, x0 in (("left", 470), ("right", 1050)):
            dx = (-70 if side == "left" else 70) * rel
            a = int(255 * (1 - rel))
            draw.rounded_rectangle([x0 + dx - 26, 380, x0 + dx + 26, 404], 10,
                                   fill=(30, 44, 52, a), outline=(70, 92, 104, a), width=2)
        canvas = over(canvas, np.asarray(overlay))
    return canvas, fr


def build_curtain(out: Path):
    room = np.asarray(Image.open(out / "assets/room-window-empty.png").convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS))
    tex = curtain_texture()
    # bake irregular fold shading into the stable atlas (no temporal photo blending)
    shade = fold_shading(13, 17, slack=375 / 180, t=0.0, seed=11)
    shade_img = np.asarray(Image.fromarray(np.clip((shade - .5) * 128 + 128, 0, 255).astype(np.uint8)).resize((tex.shape[1], tex.shape[0]), Image.Resampling.BILINEAR), float) / 255.0
    tex[..., :3] = np.clip(tex[..., :3].astype(float) * (0.6 + 0.8 * shade_img[..., None]), 0, 255).astype(np.uint8)
    rest, tris, controls, solver_reports, fallbacks = _curtain_controls()
    warps = {s: MeshWarp(tex, rest, tris) for s in ("left", "right")}

    # 60 fps cubic-interpolated comparison
    frames60, reports60 = [], []
    for i in range(int(DURATION * 60)):
        t = i / 60
        canvas, fr = _render_curtain_frame(rest, tris, warps, controls, room, t)
        frames60.append(canvas); reports60.append({"frame": i, "time": t, **fr})
    qa60 = encode(frames60, out, "video.mp4", fps=60)

    # true 17 fps control-rate export
    frames17, reports17 = [], []
    for i in range(int(DURATION * CONTROL_HZ)):
        t = i / CONTROL_HZ
        canvas, fr = _render_curtain_frame(rest, tris, warps, controls, room, t)
        frames17.append(canvas); reports17.append({"frame": i, "time": t, **fr})
    qa17 = encode(frames17, out, "video-17fps.mp4", fps=CONTROL_HZ, inspection_name="inspection-17fps")

    all_reports = reports60 + reports17
    save_json(out / "mesh-qa.json", {
        "control_rate_hz": CONTROL_HZ, "comparison_fps": 60, "comparison_frames": len(frames60),
        "true_control_fps": CONTROL_HZ, "true_control_frames": len(frames17),
        "max_inverted": max(r[s]["inverted"] for r in all_reports for s in ("left", "right")),
        "min_area_ratio": min(r[s]["min_area_ratio"] for r in all_reports for s in ("left", "right")),
        "solver_fallback_controls": fallbacks,
        "max_solver_edge_strain": max(r[s]["max_edge_strain"] for r in solver_reports for s in ("left", "right")),
        "max_projection_px": max(r[s]["projection_px"] for r in solver_reports for s in ("left", "right")),
        "scope": "2D PBD distance constraints + monotonic projection; horizontal gathering follows hung span (out-of-plane buckling is shading, not solved depth); fallback blend to analytic safe pose on fold risk is reported per control",
        "samples": reports60[::30], "solver_samples": solver_reports[::8]})
    save_json(out / "rig.json", {
        "topology": {"cols": 13, "rows": 17}, "solver": "position-based distance constraints, coloured Gauss-Seidel",
        "pins": "rail gliders + releasable tieback; centre-seam collision",
        "timing": {"hold": [0, .75], "release": [.75, 1.1], "travel": [1.1, 2.85], "contact": [2.85, 3.2], "settle": [3.2, 4]},
        "texture": "single stable procedural atlas per panel with baked irregular fold shading; no temporal photo blending"})
    Image.fromarray(frames60[180]).save(out / "frame-180.png")
    return qa60


# ---------------------------------------------------------------- eye / face
EYE_POLYS_1254 = {
    "left": [(352, 512), (420, 482), (500, 502), (512, 548), (452, 588), (372, 566)],
    "right": [(648, 492), (724, 464), (806, 486), (818, 534), (742, 576), (662, 548)],
}
IRIS_1254 = {"left": (436, 534, 47), "right": (732, 518, 47)}
# Tighter hand-traced apertures for the lid rig (source 1254 coords)
BLINK_POLYS_1254 = {
    "left": [(388, 548), (403, 525), (430, 512), (460, 512), (488, 522), (508, 542), (514, 558), (502, 580), (475, 598), (443, 604), (413, 594), (396, 574)],
    "right": [(652, 548), (670, 518), (700, 497), (732, 490), (762, 494), (790, 508), (808, 532), (802, 556), (778, 574), (746, 582), (712, 578), (682, 566)],
}
BLINK_BOXES_1254 = {"left": (370, 488, 532, 620), "right": (632, 468, 828, 608)}
BLINK_CENTERS = [1.35, 4.25]
BLINK_DURATION = 0.28


def blink_closure(t: float) -> float:
    for c in BLINK_CENTERS:
        u = abs(t - c) / (BLINK_DURATION / 2)
        if u < 1:
            return float(1 - u * u)
    return 0.0


def build_eye(out: Path):
    """Original-art eye/face performance: gaze, blink, smile, hair lag.

    The blink uses a traced aperture and procedural lid skin sampled from the
    surrounding face (a labelled estimate, not recovered hidden artwork). Pixels
    outside the traced eye neighbourhoods are asserted bit-identical to the input.
    Iris pixels are separated by a traced colour mask so gaze moves the original
    iris; the sclera hole is an inpainted estimate.
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
    blink_regions = {}
    for side in ("left", "right"):
        box = tuple(int(round(v * scale)) for v in BLINK_BOXES_1254[side])
        poly = [(x * scale, y * scale) for x, y in BLINK_POLYS_1254[side]]
        blink_regions[side] = trace_aperture(base, box, poly)
    frames, rows = [], []
    max_outside_diff = 0
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
        # blink composites only inside traced eye neighbourhoods
        closure = blink_closure(t)
        pre_blink = canvas.copy()
        blink_info = {}
        for side, reg in blink_regions.items():
            x0, y0, x1, y1 = reg.box
            canvas, bi = apply_eye(canvas, reg, closure, source=pre_blink[y0:y1, x0:x1])
            blink_info[side] = bi
        outside = np.ones((720, 720), bool)
        for reg in blink_regions.values():
            x0, y0, x1, y1 = reg.box
            outside[y0:y1, x0:x1] = False
        max_outside_diff = max(max_outside_diff, int(np.abs(canvas[outside].astype(int) - pre_blink[outside].astype(int)).max()))
        frames.append(canvas)
        rows.append({"frame": i, "time": t, "gaze": gaze, "smile": smile, "blink_closure": closure, **{f"blink_{k}": v for k, v in blink_info.items()}})
    assert max_outside_diff == 0, f"blink leaked outside eye boxes: {max_outside_diff}"
    qa = encode(frames, out)
    save_json(out / "eye-qa.json", {"fps": FPS, "frames": len(frames),
                                    "blink_scope": "procedural lid blink from traced aperture; lid skin is a smooth estimate sampled from surrounding face, not recovered hidden artwork; no generated closed-lid plate",
                                    "blink_centers_s": BLINK_CENTERS, "blink_duration_s": BLINK_DURATION,
                                    "max_pixel_diff_outside_eye_boxes": max_outside_diff,
                                    "iris": "original iris pixels separated by traced colour mask; sclera hole inpainted estimate",
                                    "samples": rows[::12]})
    save_json(out / "rig.json", {"apertures_1254": EYE_POLYS_1254, "iris_1254": IRIS_1254,
                                 "blink_apertures_1254": BLINK_POLYS_1254, "blink_boxes_1254": BLINK_BOXES_1254,
                                 "blink_centers_s": BLINK_CENTERS, "blink_duration_s": BLINK_DURATION,
                                 "hair": "hue mask + anchored root falloff; not strand segmentation"})
    Image.fromarray(frames[40]).save(out / "frame-040-gaze.png")
    Image.fromarray(frames[86]).save(out / "frame-086-smile.png")
    Image.fromarray(frames[32]).save(out / "frame-032-blink.png")
    return qa


# ---------------------------------------------------------------- flashlight
# Hand-picked corresponding landmarks on the two generated plates (720 canvas).
# These measure rigid alignment only; they do not certify structural identity.
FLASH_LANDMARKS_A = np.array([[150, 390], [520, 400], [390, 310], [600, 520],
                              [370, 195], [440, 210], [370, 350], [360, 60]], float)
FLASH_LANDMARKS_B = np.array([[140, 395], [530, 400], [385, 312], [600, 520],
                              [365, 200], [445, 215], [370, 360], [360, 55]], float)


def build_flashlight(out: Path):
    a = np.asarray(Image.open(out / "assets/detective-a.png").convert("RGB").resize((720, 720), Image.Resampling.LANCZOS))
    b0 = np.asarray(Image.open(out / "assets/detective-b.png").convert("RGB").resize((720, 720), Image.Resampling.LANCZOS))
    M, inliers = cv2.estimateAffinePartial2D(FLASH_LANDMARKS_B, FLASH_LANDMARKS_A, method=cv2.LMEDS)
    if M is None:
        M = np.array([[1., 0, 0], [0, 1., 0]])
    b = cv2.warpAffine(b0, M, (720, 720), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    pred = (M[:, :2] @ FLASH_LANDMARKS_B.T).T + M[:, 2]
    resid = np.linalg.norm(pred - FLASH_LANDMARKS_A, axis=1)
    before = np.linalg.norm(FLASH_LANDMARKS_B - FLASH_LANDMARKS_A, axis=1)
    Image.fromarray(b).save(out / "assets/detective-b-aligned.png")
    save_json(out / "alignment-qa.json", {
        "method": "similarity (rotation+scale+translation) from 8 hand-picked landmarks, LMEDS",
        "landmarks_a": FLASH_LANDMARKS_A.tolist(), "landmarks_b": FLASH_LANDMARKS_B.tolist(),
        "transform": M.tolist(), "inliers": int(inliers.sum()) if inliers is not None else None,
        "residual_px_before": before.tolist(), "residual_px_after": resid.tolist(),
        "rmse_px_before": float(np.sqrt(np.mean(before ** 2))), "rmse_px_after": float(np.sqrt(np.mean(resid ** 2))),
        "max_residual_px_after": float(resid.max()),
        "scope": "rigid landmark alignment of two generated alternatives; not a structural-deviation certificate. Hair silhouette, strawberry and hands still differ by design."})
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


# ---------------------------------------------------------------- aura / rain / breath
def build_aura(out: Path):
    """Silhouette-derived aura, depth-banded rain, breath puff, gentle cloth motion.

    Follows the Drive aura playbook: effects behind the subject, independent
    phases, face protected, premultiplied compositing. The figure is a generated
    chroma-key plate; the background is procedural. Not a fluid simulation.
    """
    src = Image.open(out / "assets/hooded-figure-chroma.png").convert("RGB")
    W, H = 576, 864
    src = src.resize((W, H), Image.Resampling.LANCZOS)
    arr = np.asarray(src).astype(float)
    green = arr[..., 1] - np.maximum(arr[..., 0], arr[..., 2])
    alpha = np.clip(1 - smoothstep((green - 20) / 60), 0, 1)
    # despill: pull green toward max(r,b) at edges
    spill = np.clip(green / 80, 0, 1) * (alpha < .95)
    arr[..., 1] = arr[..., 1] * (1 - spill) + np.maximum(arr[..., 0], arr[..., 2]) * spill
    fg = np.dstack([np.clip(arr, 0, 255), alpha * 255]).astype(np.uint8)
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    rng = np.random.default_rng(42)
    # static dark alley gradient background
    bg = np.zeros((H, W, 3), float)
    bg[..., 0] = 12 + 8 * (yy / H); bg[..., 1] = 14 + 10 * (yy / H); bg[..., 2] = 22 + 14 * (yy / H)
    bg += rng.normal(0, 1.5, (H, W, 1))
    bg = np.clip(bg, 0, 255)
    # rain drops: three depth bands, evaluated continuously per output frame
    # (the Drive playbook used 8 Hz path samples; this restaging evaluates paths
    # directly at 24 fps and labels that difference in aura-qa.json)
    drops = []
    for band, (n, speed, length, width, bright) in enumerate([
            (60, 260, 14, 1, 70), (35, 420, 22, 1, 110), (14, 640, 34, 2, 160)]):
        for _ in range(n):
            drops.append({"x": rng.uniform(0, W), "y0": rng.uniform(-H, H), "speed": speed * rng.uniform(.8, 1.2),
                          "len": length * rng.uniform(.7, 1.3), "w": width, "b": bright * rng.uniform(.7, 1.0),
                          "slant": rng.uniform(-.12, -.05), "band": band})
    face_protect = np.exp(-(((xx - W * .48) / 70) ** 2 + ((yy - H * .22) / 55) ** 2))
    frames, rows = [], []
    n_frames = 192
    for i in range(n_frames):
        t = i / FPS
        canvas = bg.copy()
        # breath-driven torso scale (tiny) and cloth sway, face protected
        breath = math.sin(2 * math.pi * t / 3.8)
        sway = math.sin(2 * math.pi * t / 5.1 + .7)
        dx = 1.2 * sway * smoothstep((yy - H * .3) / (H * .5)) * (1 - face_protect)
        dy = -1.5 * breath * smoothstep((yy - H * .25) / (H * .5)) * (1 - face_protect)
        warped_fg = cv2.remap(fg.astype(np.uint8), (xx - dx).astype(np.float32), (yy - dy).astype(np.float32),
                              cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        wa = warped_fg[..., 3:4].astype(float) / 255
        # aura behind subject: dilated alpha blurred, red emission, screen composite
        mask = (warped_fg[..., 3] > 128).astype(np.uint8) * 255
        dil = cv2.dilate(mask, np.ones((9, 9), np.uint8))
        aura = np.zeros((H, W), float)
        for sigma, weight in [(4, .30), (14, .22), (40, .35)]:
            blur = cv2.GaussianBlur(dil, (0, 0), sigma).astype(float) / 255
            aura += weight * np.clip(blur - wa[..., 0], 0, 1)
        pulse = .8 + .2 * math.sin(2 * math.pi * t / 2.3)
        aura *= pulse * (1 - face_protect * .7)
        emission = np.zeros((H, W, 3), float); emission[..., 0] = aura * 200; emission[..., 1] = aura * 30; emission[..., 2] = aura * 25
        canvas = 255 * (1 - (1 - canvas / 255) * (1 - emission / 255))
        # rear rain (band 0) behind figure
        for d in drops:
            if d["band"] != 0:
                continue
            y = (d["y0"] + d["speed"] * t) % (H + d["len"]) - d["len"]
            x = d["x"] + d["slant"] * (y - d["y0"])
            cv2.line(canvas, (int(x), int(y)), (int(x + d["slant"] * d["len"]), int(y + d["len"])),
                     (d["b"], d["b"], d["b"] + 10), d["w"], cv2.LINE_AA)
        canvas = np.clip(canvas * (1 - wa) + warped_fg[..., :3].astype(float) * wa, 0, 255)
        # front rain (bands 1,2), reduced over face
        for d in drops:
            if d["band"] == 0:
                continue
            y = (d["y0"] + d["speed"] * t) % (H + d["len"]) - d["len"]
            x = d["x"] + d["slant"] * (y - d["y0"])
            fade = 1 - .6 * face_protect[int(np.clip(y, 0, H - 1)), int(np.clip(x, 0, W - 1))]
            b = int(d["b"] * fade)
            cv2.line(canvas, (int(x), int(y)), (int(x + d["slant"] * d["len"]), int(y + d["len"])),
                     (b, b, b + 8), d["w"], cv2.LINE_AA)
        # breath puff: periodic, originates near mouth, drifts/fades
        phase = (t % 3.8) / 3.8
        if .1 < phase < .7:
            age = (phase - .1) / .6
            cx, cy = W * .47 + age * 26, H * .235 - age * 18
            r = 6 + age * 22
            op = .35 * math.sin(math.pi * age)
            puff = np.exp(-(((xx - cx) / r) ** 2 + ((yy - cy) / (r * .7)) ** 2)) * op
            canvas = canvas * (1 - puff[..., None]) + np.array([200, 210, 220]) * puff[..., None]
        frames.append(np.clip(canvas, 0, 255).astype(np.uint8))
        rows.append({"frame": i, "time": t, "breath": breath, "aura_pulse": pulse})
    qa = encode(frames, out)
    save_json(out / "aura-qa.json", {"fps": FPS, "frames": len(frames),
                                     "rain_bands": 3, "rain_path_evaluation": "continuous per-frame (not low-rate sampled)", "output_fps": FPS,
                                     "face_protected": True, "loop_seamless": False,
                                     "scope": "procedural graphic effects, not fluid sim; generated chroma figure; aura from keyed silhouette; breath/cloth are small masked warps",
                                     "samples": rows[::24]})
    save_json(out / "rig.json", {"figure": "generated chroma-key plate, green-screen keyed + despill",
                                 "aura": "dilated alpha, 3 Gaussian scales, screen behind subject",
                                 "rain": {"bands": [{"n": 60, "speed": 260}, {"n": 35, "speed": 420}, {"n": 14, "speed": 640}]},
                                 "breath_period_s": 3.8, "cloth_sway_period_s": 5.1})
    Image.fromarray(frames[96]).save(out / "frame-096.png")
    return qa


# ---------------------------------------------------------------- OpenSketch stroke trace
def _parse_svg_paths(path: Path):
    import re
    import xml.etree.ElementTree as ET
    root = ET.parse(path).getroot()
    vb = root.attrib.get("viewBox", "0 0 691 691").replace(",", " ").split()
    side = float(max(float(vb[2]), float(vb[3])))
    num = r"[-+]?(?:\d*\.?\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?"
    strokes = []
    for e in root.iter():
        if not e.tag.endswith("path"):
            continue
        d = e.attrib.get("d", "")
        tokens = re.findall(r"[A-Za-z]|" + num, d)
        if not tokens or any(t.isalpha() and t not in ("M", "L") for t in tokens):
            continue
        pts, j = [], 0
        try:
            while j < len(tokens):
                if tokens[j] in ("M", "L"):
                    j += 1
                pts.append((float(tokens[j]), float(tokens[j + 1]))); j += 2
        except (ValueError, IndexError):
            continue
        p = np.asarray(pts, float)
        steps = np.linalg.norm(np.diff(p, axis=0), axis=1)
        if steps.sum() < 10:
            continue
        strokes.append(p / side)
    return strokes


def build_strokes(out: Path):
    """Trace a CC0 OpenSketch human stroke drawing, then show a distorted variant.

    Source: Gryaditskaya et al., OpenSketch (CC0). This traces actual human-drawn
    product-design strokes in path order; it is not a character/face animation.
    The variant applies a smooth global warp to the traced geometry, labelled as
    a derived reconstruction, not the original drawing.
    """
    src_svg = ROOT / "assets/open-sketch/Professional1_house_view1_concept.svg"
    strokes = _parse_svg_paths(src_svg)
    W = H = 690
    total_pts = sum(len(s) for s in strokes)
    n_frames = 144
    trace_frames = 96
    frames, rows = [], []
    for i in range(n_frames):
        t = i / FPS
        im = Image.new("RGB", (W, H), (248, 246, 240))
        draw = ImageDraw.Draw(im)
        if i < trace_frames:
            frac = i / (trace_frames - 1)
            budget = int(frac * total_pts)
            drawn = 0
            for s in strokes:
                if drawn >= budget:
                    break
                take = min(len(s), budget - drawn)
                if take >= 2:
                    pts = [tuple(p * (W - 60) + 30) for p in s[:take]]
                    draw.line(pts, fill=(30, 30, 35), width=2)
                drawn += len(s)
            label = f"tracing human strokes {min(budget, total_pts)}/{total_pts}"
        else:
            u = (i - trace_frames) / (n_frames - trace_frames - 1)
            warp = smoothstep(np.array(u))
            for s in strokes:
                p = s.copy()
                cx, cy = .5, .5
                dx, dy = p[:, 0] - cx, p[:, 1] - cy
                r = np.sqrt(dx ** 2 + dy ** 2)
                twist = warp * .35 * np.exp(-r * 3)
                ang = np.arctan2(dy, dx) + twist
                p = np.stack([cx + r * np.cos(ang), cy + r * np.sin(ang)], 1)
                pts = [tuple(q * (W - 60) + 30) for q in p]
                if len(pts) >= 2:
                    draw.line(pts, fill=(140, 40, 30), width=2)
            label = f"derived twist variant {warp:.2f} (not original)"
        draw.text((20, 20), label, fill=(60, 60, 60))
        draw.text((20, H - 30), "OpenSketch / Gryaditskaya et al. / CC0", fill=(120, 120, 120))
        frames.append(np.asarray(im))
        rows.append({"frame": i, "time": t, "phase": "trace" if i < trace_frames else "variant"})
    qa = encode(frames, out)
    save_json(out / "stroke-qa.json", {"fps": FPS, "frames": len(frames), "strokes": len(strokes),
                                       "total_points": total_pts, "trace_frames": trace_frames,
                                       "source": "OpenSketch Professional1_house_view1_concept.svg (CC0)",
                                       "scope": "human product-design strokes, not character/face animation; variant is a derived geometric warp"})
    save_json(out / "rig.json", {"source_svg": str(src_svg.relative_to(ROOT)), "stroke_count": len(strokes),
                                 "variant": "smooth radial twist, labelled derived"})
    Image.fromarray(frames[95]).save(out / "frame-095-traced.png")
    Image.fromarray(frames[143]).save(out / "frame-143-variant.png")
    return qa


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", choices=["curtain", "eye", "flashlight", "aura", "strokes"], action="append")
    args = ap.parse_args()
    jobs = args.only or ["curtain", "eye", "flashlight", "aura", "strokes"]
    results = {}
    if "curtain" in jobs:
        results["curtain"] = build_curtain(ROOT / "examples/05-curtain-mesh")
    if "eye" in jobs:
        results["eye"] = build_eye(ROOT / "examples/06-eye-face-performance")
    if "flashlight" in jobs:
        results["flashlight"] = build_flashlight(ROOT / "examples/07-flashlight-whole-character")
    if "aura" in jobs:
        results["aura"] = build_aura(ROOT / "examples/08-aura-rain-breath")
    if "strokes" in jobs:
        results["strokes"] = build_strokes(ROOT / "examples/09-opensketch-stroke-trace")
    print(json.dumps({k: {"technical_pass": v["technical_pass"], "frames": v["frames"], "size": [v["width"], v["height"]]} for k, v in results.items()}, indent=2))


if __name__ == "__main__":
    main()
