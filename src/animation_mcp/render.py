"""SVG drawing, frame-accurate rasterization, H.264 output and measured QA."""
from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache

# The cloud user's home cache may be read-only. Configure a writable font cache
# before Cairo/fontconfig initializes, without replacing an explicit user choice.
if "XDG_CACHE_HOME" not in os.environ:
    cache = Path(tempfile.gettempdir()) / f"animation-studio-{getattr(os, 'getuid', lambda: 0)()}"
    cache.mkdir(mode=0o700, exist_ok=True)
    os.environ["XDG_CACHE_HOME"] = str(cache)

import resvg_py
import numpy as np
from PIL import Image, ImageDraw

from .scene import Scene, sample, reveal_points


def confined(root: Path, name: str, must_exist=False) -> Path:
    root = root.resolve()
    path = (root/name).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path must stay inside the studio workspace")
    if must_exist and not path.is_file():
        raise FileNotFoundError(path)
    return path


def load_scene(path: Path) -> Scene:
    return Scene.model_validate_json(path.read_text())


@lru_cache(maxsize=16)
def image_data(path: str, mtime_ns: int, size: int) -> str:
    # Cache decoded/encoded assets across frames; invalidate when a source changes.
    with Image.open(path) as im:
        if im.width*im.height > 40_000_000:
            raise ValueError("Asset exceeds 40 megapixels")
        buf = io.BytesIO()
        im.convert("RGBA").save(buf, format="PNG")
    return "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode()


def svg_frame(scene: Scene, frame: int, asset_root: Path) -> bytes:
    if not 0 <= frame < scene.frames:
        raise ValueError("Frame outside timeline")
    root = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width=str(scene.width),
                      height=str(scene.height), viewBox=f"0 0 {scene.width} {scene.height}")
    ET.SubElement(root, "rect", width="100%", height="100%", fill=scene.background)
    containers={}
    for layer in scene.layers:
        active=layer.start <= frame < (layer.end if layer.end is not None else scene.frames)
        state = {p: getattr(layer, p) for p in ["x", "y", "scale", "scale_x", "scale_y", "rotation", "opacity", "reveal"]}
        state.update({t.property: sample(t, frame) for t in layer.tracks})
        container=containers[layer.parent] if layer.parent else root
        g = ET.SubElement(container, "g", id=layer.id, opacity=str(state["opacity"]),
                          transform=f"translate({state['x']} {state['y']}) rotate({state['rotation']}) scale({state['scale']*state['scale_x']} {state['scale']*state['scale_y']})")
        containers[layer.id]=g
        if not active:
            g.set('display','none');continue
        attrs = dict(fill=layer.fill, stroke=layer.stroke,
                     **{"stroke-width": str(layer.stroke_width), "stroke-linecap": "round", "stroke-linejoin": "round"})
        if layer.kind == "rect":
            ET.SubElement(g, "rect", x=str(-layer.width/2), y=str(-layer.height/2),
                          width=str(layer.width), height=str(layer.height), **attrs)
        elif layer.kind == "ellipse":
            ET.SubElement(g, "ellipse", rx=str(layer.width/2), ry=str(layer.height/2), **attrs)
        elif layer.kind == "text":
            e = ET.SubElement(g, "text", **attrs, **{"font-size": str(layer.font_size),
                              "font-family": "Inter", "text-anchor": "middle"})
            e.text = layer.text
        elif layer.kind == "path":
            points = list(layer.points)
            if layer.closed:
                points.append(points[0])
            points = reveal_points(points, state["reveal"])
            if len(points) >= 2:
                tag = "polygon" if layer.closed and state["reveal"] >= 1 else "polyline"
                if tag == "polyline":
                    attrs["fill"] = "none"
                ET.SubElement(g, tag, points=" ".join(f"{x},{y}" for x,y in points), **attrs)
        elif layer.kind == "image":
            asset_name = layer.asset % frame if "%04d" in layer.asset else layer.asset
            path = confined(asset_root, asset_name, must_exist=True)
            stat = path.stat()
            ET.SubElement(g, "image", x=str(-layer.width/2), y=str(-layer.height/2),
                          width=str(layer.width), height=str(layer.height),
                          href=image_data(str(path),stat.st_mtime_ns,stat.st_size))
    return ET.tostring(root, encoding="utf-8")


def draw_frame(scene: Scene, frame: int, asset_root: Path) -> Image.Image:
    fonts = Path(__file__).parent / "assets" / "fonts"
    png = resvg_py.svg_to_bytes(svg_string=svg_frame(scene, frame, asset_root).decode(),
                                font_files=[str(p) for p in fonts.glob("*.ttf")],
                                sans_serif_family="Inter")
    return Image.open(io.BytesIO(png)).convert("RGB")


def probe(video: Path) -> dict:
    proc = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format",
                           "-of", "json", str(video)], capture_output=True, text=True, check=True, timeout=120)
    return json.loads(proc.stdout)


def inspect(video: Path, folder: Path, expected: Scene | None = None, frames=None) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    info = probe(video)
    stream = next(s for s in info["streams"] if s["codec_type"] == "video")
    count = int(stream["nb_read_frames"])
    n, d = map(int, stream["avg_frame_rate"].split("/"))
    fps = n/d
    indices = {0, count//4, count//2, 3*count//4, count-1}
    if frames:
        indices.update(frames)
    if expected:
        for layer in expected.layers:
            for boundary in [layer.start, layer.end, *[k.frame for t in layer.tracks for k in t.keys]]:
                if boundary is not None:
                    indices.update([boundary-1, boundary, boundary+1])
    indices = sorted(x for x in indices if 0 <= x < count)
    # One sequential decode preserves exact frame indices (no approximate timestamp seeking).
    expression = "+".join(f"eq(n,{i})" for i in indices)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"select='{expression}'",
                    "-fps_mode", "vfr", str(folder/"sample-%04d.png")], check=True, timeout=180)
    files = [folder/f"sample-{i+1:04d}.png" for i in range(len(indices))]
    sheet = Image.new("RGB", (4*320, ((len(files)+3)//4)*204), "#111827")
    draw = ImageDraw.Draw(sheet)
    metrics = []
    for i, (path, frame) in enumerate(zip(files, indices)):
        im = Image.open(path).convert("RGB")
        arr = np.asarray(im, dtype=float)
        metrics.append({"frame": frame, "stddev": float(arr.std()),
                        "luma_mean": float(arr.mean())})
        im.thumbnail((320,180))
        x,y = i%4*320, i//4*204
        sheet.paste(im, (x,y))
        draw.text((x+8,y+182), f"{frame:04d} / {frame/fps:.3f}s", fill="white")
    sheet.save(folder/"contact-sheet.jpg", quality=92)
    errors = []
    if expected:
        if count != expected.frames:
            errors.append(f"Expected {expected.frames} frames, got {count}")
        if abs(fps-expected.fps) > .001:
            errors.append("Incorrect frame rate")
        if (stream["width"],stream["height"]) != (expected.width,expected.height):
            errors.append("Incorrect output dimensions")
        if bool(expected.audio) != any(s["codec_type"] == "audio" for s in info["streams"]):
            errors.append("Audio stream expectation failed")
    result = {"video": str(video), "frames": count, "fps": fps, "duration": count/fps,
              "width": stream["width"], "height": stream["height"], "codec": stream["codec_name"],
              "technical_pass": not errors, "errors": errors, "samples": metrics,
              "contact_sheet": str(folder/"contact-sheet.jpg"),
              "visual_review": "pending: inspect actual frames and motion; statistics are not artistic scores"}
    (folder/"qa.json").write_text(json.dumps(result,indent=2)+"\n")
    return result


def render(scene_path: Path, folder: Path, asset_root: Path, max_pixel_frames=2_000_000_000) -> dict:
    scene = load_scene(scene_path)
    if scene.width*scene.height*scene.frames > max_pixel_frames:
        raise ValueError("Render exceeds pixel-frame budget; render a shorter or smaller preview first")
    folder.mkdir(parents=True, exist_ok=True)
    video = folder/"video.mp4"
    audio = None
    if scene.audio:
        audio = confined(asset_root, scene.audio, must_exist=True)
        duration = float(probe(audio)["format"]["duration"])
        if duration > scene.frames/scene.fps + 1/scene.fps:
            raise ValueError("Voiceover exceeds timeline; extend the scene to avoid truncating narration")
    cmd = ["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",
           f"{scene.width}x{scene.height}","-r",str(scene.fps),"-i","pipe:0"]
    if audio:
        cmd += ["-i",str(audio),"-af","apad","-c:a","aac","-b:a","192k"]
    cmd += ["-c:v","libx264","-threads","2","-crf","18","-pix_fmt","yuv420p",
            "-t",str(scene.frames/scene.fps),"-movflags","+faststart",str(video)]
    log = folder/"ffmpeg.log"
    with log.open("w") as err:
        proc = subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
        try:
            for frame in range(scene.frames):
                im = draw_frame(scene,frame,asset_root)
                proc.stdin.write(im.tobytes())
            proc.stdin.close()
            status = proc.wait(timeout=120)
            if status:
                raise RuntimeError(f"FFmpeg failed: {log.read_text()[-2000:]}")
        except BaseException:
            proc.kill()
            proc.wait()
            raise
    (folder/"scene.json").write_text(scene.model_dump_json(indent=2))
    (folder/"drawing.svg").write_bytes(svg_frame(scene,min(scene.frames-1,scene.frames//2),asset_root))
    return inspect(video,folder/"inspection",scene)
