"""STDIO MCP tools for local agents. Logs must never pollute protocol stdout."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

from mcp.server.fastmcp import FastMCP
from .scene import Scene
from .render import confined, render, inspect, draw_frame, svg_frame, load_scene
from .blender_scene import render_3d
from .edit import edit_video

ROOT = Path(os.environ.get("ANIMATION_WORKSPACE", os.getcwd())).resolve()
ROOT.mkdir(parents=True,exist_ok=True)
mcp = FastMCP("Animation Agent Studio")


def new_folder(prefix):
    folder = ROOT/"output"/(prefix+"-"+uuid.uuid4().hex[:10])
    folder.mkdir(parents=True)
    return folder


@mcp.tool()
def capabilities() -> dict:
    """Check installed render engines and the supported scene format."""
    return {"workspace": str(ROOT), "ffmpeg":bool(shutil.which("ffmpeg")),
            "ffprobe":bool(shutil.which("ffprobe")),"blender":bool(shutil.which("blender")),
            "features":["editable SVG", "2D keyframes", "stroke reveal", "layered image parallax",
                        "voiceover mux", "clip assembly", "timed captions", "frame inspection",
                        "primitive 3D scenes", "Bezier stroke sampling"],
            "limits":["agent authors scene; no universal text-to-art model bundled",
                      "no character rigging, automatic lip sync or AI image provider bundled",
                      "stdio transport; local trusted client"],
            "scene_schema": Scene.model_json_schema()}


@mcp.tool()
def save_scene(scene: dict, path: str) -> dict:
    """Validate and save editable 2D JSON. Paths are relative to ANIMATION_WORKSPACE."""
    target = confined(ROOT,path)
    if target.exists():
        raise ValueError("File already exists; use a new versioned path")
    parsed = Scene.model_validate(scene)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(parsed.model_dump_json(indent=2))
    return {"path":str(target), "frames":parsed.frames,"duration":parsed.frames/parsed.fps}


@mcp.tool()
def preview_frame(scene_path: str, frame: int) -> dict:
    """Create PNG and editable SVG for a precise frame before a full render."""
    scene = load_scene(confined(ROOT,scene_path,True))
    folder = new_folder("preview")
    draw_frame(scene,frame,ROOT).save(folder/"frame.png")
    (folder/"drawing.svg").write_bytes(svg_frame(scene,frame,ROOT))
    return {"png":str(folder/"frame.png"),"svg":str(folder/"drawing.svg")}


@mcp.tool()
def render_scene(scene_path: str) -> dict:
    """Render H.264 video with optional local voiceover, source SVG and measured QA."""
    return render(confined(ROOT,scene_path,True),new_folder("render"),ROOT)


@mcp.tool()
def inspect_video(video_path: str, frames: list[int] | None = None) -> dict:
    """Decode video and extract exact frames/contact sheet. Does not score artistic merit."""
    return inspect(confined(ROOT,video_path,True),new_folder("inspection"),frames=frames)


@mcp.tool()
def render_3d_scene(scene: dict) -> dict:
    """Render constrained sphere/cube/cone/cylinder/torus animation in CPU Blender; save .blend."""
    return render_3d(scene,new_folder("blender"))


@mcp.tool()
def assemble_video(edit: dict) -> dict:
    """Assemble local clips with aspect-fit padding, timed captions and optional narration.

    Source audio is dropped. Supply edit.audio for a narration/music track.
    Clip durations are rounded to the output frame grid.
    """
    return edit_video(edit,new_folder("edit"),ROOT)


@mcp.tool()
def curve_points(controls: list[list[float]], samples: int = 64, learned: bool = False) -> dict:
    """Create a cubic Bezier stroke from 4 control points. Optional narrow learned baseline.

    Controls use normalized 0–1 coordinates. Analytic geometry is exact and preferred.
    """
    import numpy as np
    c=np.asarray(controls,dtype=float)
    if c.shape != (4,2) or not np.isfinite(c).all() or (c<0).any() or (c>1).any():
        raise ValueError('Supply four finite 2D control points in [0,1]')
    if not 2<=samples<=1000:
        raise ValueError('Use 2–1000 samples')
    t=np.linspace(0,1,samples)
    if learned:
        path=confined(ROOT,'training/checkpoints/stroke_policy.npz',True)
        h=np.concatenate([np.broadcast_to(c.reshape(1,8),(samples,8)),t[:,None]],axis=1)*2-1
        with np.load(path,allow_pickle=False) as z:
            for i in range(3):
                h=h@z[f'coef_{i}']+z[f'intercept_{i}']
                if i<2:h=np.tanh(h)
        points=h
    else:
        basis=np.stack([(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3],axis=1)
        points=basis@c
    return {'points':points.tolist(),'method':'learned synthetic-curve baseline' if learned else 'exact geometry',
            'scope':'Interpolates supplied controls; does not invent subjects or artwork'}


@mcp.tool()
def plan_narration(text: str, duration_seconds: float, fps: int = 30) -> dict:
    """Draft sentence-aligned shot timings. Estimates only, NOT forced audio alignment."""
    import re
    if not 0 < duration_seconds <= 600 or not 1 <= fps <= 60:
        raise ValueError("Duration must be 0–600 seconds and fps 1–60")
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+",text.strip()) if s.strip()]
    if not sentences or len(text) > 50000:
        raise ValueError("Provide nonempty narration up to 50,000 characters")
    total = round(duration_seconds*fps)
    if total < len(sentences):
        raise ValueError("Timeline too short for sentence count")
    weights = [len(s.split()) for s in sentences]
    remaining = total-len(sentences)
    extras = [remaining*w/sum(weights) for w in weights]
    lengths = [1+int(x) for x in extras]
    for i in sorted(range(len(lengths)),key=lambda i:extras[i]-int(extras[i]),reverse=True)[:total-sum(lengths)]:
        lengths[i] += 1
    shots=[]
    start=0
    for sentence,length in zip(sentences,lengths):
        shots.append({"text":sentence,"start":start,"end":start+length,
                      "visual_brief":"Agent: supply a concrete visual metaphor and assets"})
        start += length
    return {"alignment":"estimated by word counts; confirm against real voiceover", "fps":fps,"shots":shots}


@mcp.tool()
def concept_brief(subject: str, style: str = "layered editorial illustration") -> dict:
    """Prepare a visual-generation brief for an agent's own image tool; no API call occurs."""
    return {"prompt":f"Original {subject}. {style}. Clear silhouette, coherent lighting, readable composition. "
                      "Separate background, midground and subject for animation. No lettering or borrowed characters.",
            "next":"Use your available image-generation tool, save a PNG inside the workspace, then animate it as image layers.",
            "generated":False}


@mcp.tool()
def record_lesson(task: str, observation: str, artifact_path: str, verified: bool = False) -> dict:
    """Append evidence-linked practice memory. Does not update model weights."""
    artifact = confined(ROOT,artifact_path,True)
    folder = ROOT/"training"
    folder.mkdir(exist_ok=True)
    entry = {"task":task,"observation":observation,"artifact":str(artifact),"verified_by_caller":verified}
    with (folder/"lessons.jsonl").open("a") as f:
        f.write(json.dumps(entry)+"\n")
    return {"saved":True,"model_weights_changed":False}


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
