"""Prepare layered cutout assets for the talking-scene and PNGTuber examples.

Inputs (AI-generated plates + user-supplied avatar):
  examples/assets/sky-day-clean.jpg        - clean sky gradient plate
  examples/assets/ground-grass-stones.jpg  - grass/stone ground strip on white
  examples/assets/clouds-cluster-a.jpg     - cumulus cluster on magenta
  examples/assets/clouds-cluster-b.jpg     - wispy cloud pair on magenta
  /tmp/arena-coding-uploads/image-2.png    - user hand-drawn PNGTuber avatar on green screen

Outputs (RGBA cutouts, committed):
  examples/assets/ground-cutout.png
  examples/assets/clouds-a.png
  examples/assets/clouds-b.png
  examples/assets/avatar-cutout.png
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "examples/assets"


def key_background(img: Image.Image, target: np.ndarray, tol: float, soft: float,
                   despill: str | None = None) -> Image.Image:
    """Remove pixels near `target` RGB, feathering alpha by distance in tol..soft band.

    despill removes background colour contamination from semi-transparent edges:
    'green' clamps a dominant green channel down; 'magenta' lifts green toward
    min(red, blue) so pink fringes become neutral.
    """
    rgba = np.asarray(img.convert("RGBA"), dtype=np.float32)
    rgb = rgba[..., :3]
    dist = np.linalg.norm(rgb - target[None, None, :], axis=2)
    alpha = np.clip((dist - tol) / max(1.0, soft - tol), 0, 1)
    if despill == "green":
        cap = np.maximum(rgb[..., 0], rgb[..., 2])
        rgb[..., 1] = np.minimum(rgb[..., 1], cap + 6)
    elif despill == "magenta":
        floor = np.minimum(rgb[..., 0], rgb[..., 2])
        rgb[..., 1] = np.maximum(rgb[..., 1], floor - 6)
    rgba[..., :3] = rgb
    rgba[..., 3] = alpha * 255
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def cut_top_white(img: Image.Image) -> Image.Image:
    """Flood the white background from the top edge only, so white flowers inside stay solid."""
    rgba = np.asarray(img.convert("RGBA"), dtype=np.uint8).copy()
    h, w = rgba.shape[:2]
    rgb = rgba[..., :3].astype(np.int16)
    white = (rgb.min(axis=2) > 232) & (np.ptp(rgb, axis=2) < 18)
    # BFS from top-row white pixels across connected white pixels.
    from collections import deque
    visited = np.zeros((h, w), dtype=bool)
    queue: deque[tuple[int, int]] = deque()
    for x in range(w):
        if white[0, x]:
            queue.append((0, x))
            visited[0, x] = True
    while queue:
        y, x = queue.popleft()
        for ny, nx in ((y-1, x), (y+1, x), (y, x-1), (y, x+1)):
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not visited[ny, nx]:
                visited[ny, nx] = True
                queue.append((ny, nx))
    rgba[..., 3] = np.where(visited, 0, 255)
    im = Image.fromarray(rgba, "RGBA")
    # Feather the silhouette edge slightly.
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(a)
    return im


def main() -> None:
    ground = Image.open(ASSETS / "ground-grass-stones.jpg")
    cut_top_white(ground).save(ASSETS / "ground-cutout.png")
    print("ground-cutout.png", (ASSETS / "ground-cutout.png").stat().st_size)

    magenta = np.array([255.0, 0.0, 255.0])
    for name in ("clouds-cluster-a", "clouds-cluster-b"):
        img = Image.open(ASSETS / f"{name}.jpg")
        keyed = key_background(img, magenta, tol=85, soft=150, despill="magenta")
        out = ASSETS / (name.replace("cluster-", "") + ".png")
        keyed.save(out)
        print(out.name, out.stat().st_size)

    uploads = Path("/tmp/arena-coding-uploads/image-2.png")
    if uploads.exists():
        img = Image.open(uploads)
        arr = np.asarray(img.convert("RGB"), dtype=np.float32)
        corners = np.concatenate([arr[:8, :8].reshape(-1, 3), arr[:8, -8:].reshape(-1, 3)])
        green = np.median(corners, axis=0)
        print("avatar key colour:", green)
        keyed = key_background(img, green, tol=85, soft=145, despill="green")
        # Trim to content bounds so the scene layer box matches the character.
        bbox = keyed.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if bbox:
            keyed = keyed.crop(bbox)
        keyed.save(ASSETS / "avatar-cutout.png")
        print("avatar-cutout.png", keyed.size, (ASSETS / "avatar-cutout.png").stat().st_size)

    # State variants (AI edits) arrive on white at arbitrary size; key, trim and
    # normalize onto the main cutout's box so mouth/blink swaps never jump.
    base = Image.open(ASSETS / "avatar-cutout.png")
    for name in ("avatar-eyes-closed", "avatar-mouth-closed"):
        path = ASSETS / f"{name}.png"
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        keyed = cut_top_white(img)
        bbox = keyed.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        if bbox:
            keyed = keyed.crop(bbox)
        keyed = keyed.resize(base.size, Image.LANCZOS)
        keyed.save(path)
        print(name, keyed.size, path.stat().st_size)


if __name__ == "__main__":
    main()
