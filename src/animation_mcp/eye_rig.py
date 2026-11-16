"""Eyelid rig from a single portrait: traced aperture, per-column blink, lashes.

The blink only composites inside a traced eye neighbourhood. Pixels outside that
neighbourhood are bit-identical to the input, which the builder asserts. Lid skin
is a smooth low-frequency estimate sampled from surrounding skin (not recovered
hidden artwork and not a Telea inpaint of the white sclera, which bled). The
aperture is hand-traced on the source plate; colour alone confused brown iris
with brown skin. Upper lid travels farther than lower; lashes ride the lids.
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class EyeRegion:
    box: tuple[int, int, int, int]
    top: np.ndarray
    bottom: np.ndarray
    valid: np.ndarray
    source: np.ndarray
    upper_skin: np.ndarray                  # per-column RGB
    lower_skin: np.ndarray
    band: np.ndarray                        # float neighbourhood mask 0..1
    lash_colour: tuple[int, int, int]


def _sample_skin(crop: np.ndarray, skin: np.ndarray, x: int, y0: int, y1: int) -> np.ndarray:
    hh = crop.shape[0]
    y0, y1 = max(0, y0), min(hh, y1)
    sel = skin[y0:y1, x]
    px = crop[y0:y1, x][sel]
    if len(px) < 3:
        ya, yb = max(0, y0 - 12), min(hh, y1 + 12)
        px = crop[ya:yb, x][skin[ya:yb, x]]
    return np.median(px, axis=0) if len(px) else np.array([150.0, 95.0, 55.0])


def trace_aperture(rgb: np.ndarray, box: tuple[int, int, int, int],
                   polygon: list[tuple[float, float]]) -> EyeRegion:
    x0, y0, x1, y1 = box
    crop = rgb[y0:y1, x0:x1]
    hh, ww = crop.shape[:2]
    poly = np.asarray([(x - x0, y - y0) for x, y in polygon], np.int32)
    mask = np.zeros((hh, ww), np.uint8)
    cv2.fillPoly(mask, [poly], 255)
    valid = mask.max(axis=0) > 0
    top = np.zeros(ww, float); bottom = np.zeros(ww, float)
    for x in range(ww):
        ys = np.flatnonzero(mask[:, x])
        if len(ys):
            top[x], bottom[x] = ys.min(), ys.max()
    xs = np.flatnonzero(valid)
    hsv = cv2.cvtColor(crop, cv2.COLOR_RGB2HSV)
    h, s, v = (hsv[..., k].astype(int) for k in range(3))
    skin = (h > 5) & (h < 30) & (s > 70) & (s < 210) & (v > 70) & (v < 230)
    upper = np.zeros((ww, 3)); lower = np.zeros((ww, 3))
    for x in range(ww):
        xx = int(min(xs, key=lambda q: abs(q - x)))
        upper[x] = _sample_skin(crop, skin, xx, int(top[xx]) - 28, int(top[xx]) - 14)
        lower[x] = _sample_skin(crop, skin, xx, int(bottom[xx]) + 14, int(bottom[xx]) + 30)
    upper = cv2.GaussianBlur(upper[None, :, :], (1, 11), 0)[0]
    lower = cv2.GaussianBlur(lower[None, :, :], (1, 11), 0)[0]
    hull = np.asarray([(x, top[x]) for x in xs] + [(x, bottom[x]) for x in xs[::-1]], np.int32)
    m = np.zeros((hh, ww), np.uint8)
    cv2.fillPoly(m, [hull], 255)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (23, 23)))
    band = cv2.GaussianBlur(m.astype(float) / 255.0, (0, 0), 2)
    samples = np.asarray([crop[max(0, int(top[x]) - 3), x] for x in xs])
    dark = samples[samples.mean(axis=1) < 90]
    lash = tuple(int(v) for v in np.median(dark, axis=0)) if len(dark) else (15, 10, 8)
    return EyeRegion(box, top, bottom, valid, crop.copy(), upper, lower, band, lash)


def blink_crop(region: EyeRegion, closure: float, *, upper_fraction: float = 0.72,
               lash_width: int = 6, source: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    b = float(np.clip(closure, 0.0, 1.0))
    crop = (source if source is not None else region.source).astype(float)
    hh, ww = crop.shape[:2]
    top, bot, valid = region.top, region.bottom, region.valid
    xs = np.flatnonzero(valid)
    yy, xx = np.mgrid[0:hh, 0:ww]
    col = xx
    meet = top + upper_fraction * (bot - top)
    nt = top + (meet - top) * b
    nb = bot - (bot - meet) * b
    sp = np.maximum(nb - nt, 1e-6)
    sy = top[col] + (yy - nt[col]) * (np.maximum(bot - top, 1e-6)[col] / sp[col])
    inside = valid[col] & (yy >= nt[col]) & (yy <= nb[col]) & (sp[col] > 0.75)
    warped = cv2.remap(crop, xx.astype(np.float32), np.clip(sy, 0, hh - 1).astype(np.float32),
                       cv2.INTER_LINEAR)
    frac = np.clip((yy - nt[col]) / np.maximum(nb[col] - nt[col], 1), 0, 1)
    lid = region.upper_skin[col] * (1 - frac[..., None]) + region.lower_skin[col] * frac[..., None]
    lid *= 1 - 0.08 * np.clip(1 - (yy - nt[col]) / 18, 0, 1)[..., None]
    recon = lid.copy()
    edge = np.clip(np.minimum(yy - nt[col], nb[col] - yy) / 1.2, 0, 1) * inside
    recon = recon * (1 - edge[..., None]) + warped * edge[..., None]
    for curve, width, gain in ((nt, lash_width, 1.0), (nb, 2, 0.5)):
        pts = np.asarray([(x, curve[x]) for x in xs], np.int32)
        layer = np.zeros((hh, ww), np.uint8)
        cv2.polylines(layer, [pts], False, 255, max(1, int(width)), cv2.LINE_AA)
        a = (layer.astype(float) / 255.0) * gain
        recon = recon * (1 - a[..., None]) + np.asarray(region.lash_colour, float) * a[..., None]
    out = crop * (1 - region.band[..., None]) + recon * region.band[..., None]
    out = np.clip(np.rint(out), 0, 255).astype(np.uint8)
    area = float(np.sum(np.maximum(nb - nt, 0) * valid))
    open_area = float(np.sum(np.maximum(bot - top, 0) * valid))
    return out, {"closure": b, "aperture_area_px": area,
                 "aperture_ratio": area / max(open_area, 1e-9),
                 "upper_lid_travel_px": float(np.max(np.abs(nt - top))),
                 "lower_lid_travel_px": float(np.max(np.abs(nb - bot)))}


def apply_eye(rgb: np.ndarray, region: EyeRegion, closure: float, *, source: np.ndarray | None = None, **kw) -> tuple[np.ndarray, dict]:
    x0, y0, x1, y1 = region.box
    crop, info = blink_crop(region, closure, source=source, **kw)
    out = rgb.copy()
    out[y0:y1, x0:x1] = crop
    return out, info
