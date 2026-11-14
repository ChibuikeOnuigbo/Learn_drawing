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
from .speech import synthesize
from .reactions import classify,plan_cues,compose_reactions
from .presets import scene_preset

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
                        "primitive 3D scenes", "Bezier stroke sampling", "offline speech with word events",
                        "learned reaction intent", "timed local meme compositing", "weighted humanoid rig and IK"],
            "limits":["agent authors scene; no universal text-to-art model bundled",
                      "rigging is a procedural humanoid preset, not universal auto-rigging",
                      "no automatic lip sync or hosted AI image provider bundled",
                      "stdio transport; local trusted client"],
            "scene_schema": Scene.model_json_schema()}


@mcp.tool()
def get_scene_schema(kind: str = '2d') -> dict:
    """Get the exact editable schema for 2d, 3d (including rigs) or edit."""
    from .blender_scene import Scene3D
    from .edit import Edit
    schemas={'2d':Scene,'3d':Scene3D,'edit':Edit}
    if kind not in schemas:raise ValueError('Use 2d, 3d or edit')
    return schemas[kind].model_json_schema()


@mcp.tool()
def get_model_catalog() -> dict:
    """List bundled/trusted downloadable models, scope and preparation tools."""
    from .semantic import model_cache
    from .asr import asr_cache
    return dict(models=[
        dict(name='reaction-intent',source='trained in this project',bundled=True,
             scope='6 English editorial intents; small synthetic corpus, not a general reasoning model'),
        dict(name='curve-interpolation',source='trained in this project',bundled=True,
             scope='predicts points along provided Bezier controls; exact geometry is better'),
        dict(name='CLIP ViT-B/32',source='pretrained upstream; reused unchanged',bundled=False,
             files_present=(model_cache()/'text/model.onnx').exists() and (model_cache()/'vision/model.onnx').exists(),
             prepare_tool='prepare_reference_models',scope='text-to-sampled-frame retrieval; 330 samples from 55 supplied videos'),
        dict(name='Whisper base.en',source='pretrained upstream; reused unchanged',bundled=False,
             files_present=(asr_cache()/'model.bin').exists(),prepare_tool='prepare_voiceover_model',
             scope='English ASR with estimated word times; review low confidence and sync')],
        integrity='Preparation tools verify pinned SHA-256 checksums. files_present alone does not claim verification.',
        host_agent='Connecting these tools does not change the host agent model weights')


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
def synthesize_narration(text: str, speed: int = 155, voice: str = 'en-us') -> dict:
    """Generate real offline demo speech and word onset events. English synthetic voice."""
    result=synthesize(text,new_folder('speech'),speed,voice)
    result['narration_json']=str(Path(result['audio']).with_name('narration.json'))
    return result


@mcp.tool()
def select_reaction(text: str) -> dict:
    """Classify a phrase's meme intent. May abstain; synthetic training has limited coverage."""
    from .reactions import ASSETS,PACKAGE
    result=classify(text)
    if result['intent'] in ASSETS:
        name,style,meaning=ASSETS[result['intent']]
        result.update(asset=str(PACKAGE/'assets/reactions'/name),style=style,meaning=meaning,
                      provenance='original generated illustration; not a retrieved franchise GIF')
    return result


@mcp.tool()
def plan_reaction_cues(narration_json: str, theme: str = 'anime') -> dict:
    """Anchor reactions to timed spoken words, with intent, abstention and frame evidence."""
    narration=json.loads(confined(ROOT,narration_json,True).read_text())
    return plan_cues(narration,theme=theme)


@mcp.tool()
def render_reaction_video(narration_json: str, theme: str = 'anime', asset_overrides: dict | None = None,
                          width: int = 960, height: int = 540, heading: str = 'The story takes a turn') -> dict:
    """Render narration, chosen reactions, captions and generated sound accents.

    Optional intent→local path overrides accept images/GIFs/video. Supply licensed
    assets in the workspace. This tool does not search Giphy or Tenor.
    """
    return compose_reactions(confined(ROOT,narration_json,True),new_folder('reactions'),ROOT,
                             theme,asset_overrides,width,height,heading=heading)


@mcp.tool()
def render_3d_exercise(level: str = 'simple', width: int = 640, height: int = 360, samples: int = 12) -> dict:
    """Render editable easy bounce, simple rigged wave, medium IK walk or hard reach/grasp demo.

    Difficulty labels describe this toolkit's exercises, not parity with the
    user's advanced reference films. Rig reports inspect actual deformed poses.
    """
    return render_3d(scene_preset(level,width,height,samples),new_folder('exercise-'+level))


@mcp.tool()
def prepare_reference_models() -> dict:
    """Download/verify pinned MIT CLIP models (~606MB) for offline semantic reference search."""
    from .semantic import prepare_models
    return prepare_models()


@mcp.tool()
def prepare_voiceover_model() -> dict:
    """Download and SHA-256 verify pinned Whisper base.en (~145MB), without credentials."""
    from .asr import prepare_speech_model
    return prepare_speech_model()


@mcp.tool()
def transcribe_voiceover(audio_path: str) -> dict:
    """Transcribe a supplied English audio file with local Whisper and estimated word times.

    The returned narration_json can be passed to plan_reaction_cues and
    render_reaction_video. Review uncertain words before publishing.
    """
    from .asr import transcribe
    return transcribe(confined(ROOT,audio_path,True),new_folder('transcript'))


@mcp.tool()
def search_reference_library(query: str, limit: int = 5) -> dict:
    """Find supplied reference frames by text using pretrained CLIP; not a quality score."""
    from .semantic import search_references
    return search_references(query,limit)


@mcp.resource('studio://workflow')
def workflow() -> str:
    """Production workflow available to any connected MCP client."""
    return Path(__file__).with_name('WORKFLOW.md').read_text()


@mcp.prompt()
def produce_video(brief: str) -> str:
    """Guide a connected agent through actual production and evidence-based review."""
    return workflow()+'\n\nUSER PRODUCTION BRIEF:\n'+brief


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
        path=Path(__file__).with_name('models')/'stroke_policy.npz'
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
