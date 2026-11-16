"""STDIO MCP tools for local agents. Logs must never pollute protocol stdout."""
from __future__ import annotations
import json
import os
from pathlib import Path
import uuid

from mcp.server.fastmcp import FastMCP
from .scene import Scene
from .render import confined, render, inspect, draw_frame, svg_frame, load_scene
from .blender_scene import render_3d
from .edit import edit_video
from .speech import synthesize
from .reactions import classify,plan_cues,compose_reactions
from .presets import scene_preset
from .doctor import resolve_command, run_checks
from .skills_index import index as skill_index, read_skill

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
    return {"workspace": str(ROOT), "ffmpeg":bool(resolve_command("ffmpeg")),
            "ffprobe":bool(resolve_command("ffprobe")),
            "blender":bool(resolve_command("blender")),
            "agent_entry":"studio://workflow", "skill_catalog":"studio://skills",
            "skills":[entry["name"] for entry in skill_index()["skills"]],
            "features":["editable SVG", "2D keyframes", "stroke reveal", "layered image parallax",
                        "nested vector character rig", "voiceover mux", "clip assembly", "timed captions", "frame inspection",
                        "primitive and art-directed 3D scenes", "Bezier stroke sampling", "offline speech with word events",
                        "transparent reaction-intent rules", "timed local meme/GIF compositing", "weighted humanoid rig and IK",
                        "frame-accurate shot planning", "role-based palette/contrast", "exposure/dope sheets", "project scaffolding",
                        "per-frame point/contour trace library", "insert/meme exclusion with origin evidence", "art-style catalog",
                        "seeded scene planner/randomizer", "procedural assets and overlay loops", "depth-layer compositing"],
            "limits":["agent authors scene; no universal text-to-art model bundled",
                      "rigging is a procedural humanoid preset, not universal auto-rigging",
                      "no automatic lip sync or hosted AI image provider bundled",
                      "trace features are sparse image evidence, not recovered brush strokes/rigs",
                      "meme origin matches identify local templates; unknown origins require review",
                      "trace/asset libraries are local data, not bundled third-party media",
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
        dict(name='CLIP ViT-B/32',source='pretrained upstream; reused unchanged',bundled=False,
             files_present=(model_cache()/'text/model.onnx').exists() and (model_cache()/'vision/model.onnx').exists(),
             prepare_tool='prepare_reference_models',scope='text-to-sampled-frame retrieval; 330 samples from 55 supplied videos; separate trace library records per-frame geometry'),
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
    """Render constrained 3D animation in CPU Blender; save editable .blend.

    Basic mode accepts primitives. art_direction presets (easy/simple/medium/hard)
    add authored sets, materials, lighting and rigged characters.
    """
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
    """Select a reaction intent with transparent phrase rules; may abstain."""
    from .reactions import ASSETS,PACKAGE
    result=classify(text)
    if result['intent'] in ASSETS:
        name,style,meaning=ASSETS[result['intent']]
        result.update(asset=str(PACKAGE/'assets/reactions'/name),style=style,meaning=meaning,
                      provenance=('third-party reaction GIF; review rights before publication' if name.endswith('.gif')
                                  else 'original generated illustration; not a retrieved franchise GIF'))
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


@mcp.tool()
def trace_video_file(video_path: str, video_id: str | None = None, annotations_path: str | None = None,
                     analysis_width: int = 480, max_tracks: int = 192) -> dict:
    """Decode every frame of a local authorized video into persistent point tracks/contours.

    Confirmed meme/insert annotation ranges are excluded and carry origin evidence.
    Static low-motion shots are flagged for review, not silently called memes.
    Long job; for batches use scripts/build_trace_library.py. Output: data/traces.
    """
    from .tracing import trace_video, library_root
    path = confined(ROOT, video_path, True)
    annotations = confined(ROOT, annotations_path, True) if annotations_path else None
    vid = video_id or path.stem
    return trace_video(path, library_root(ROOT)/vid, video_id=vid, annotations=annotations,
                       analysis_width=analysis_width, max_tracks=max_tracks)


@mcp.tool()
def list_trace_library() -> dict:
    """List locally built per-frame traces, coverage, measured style stats and pending reviews."""
    from .tracing import read_catalog
    return read_catalog(ROOT)


@mcp.tool()
def get_trace_frame(video_id: str, frame: int) -> dict:
    """Read one indexed frame: normalized points, track ids, confidence, contours, motion, insert origin."""
    from .tracing import get_frame
    return get_frame(video_id, frame, ROOT)


@mcp.tool()
def get_trace_track(video_id: str, track_id: int, start_frame: int = 0, end_frame: int | None = None) -> dict:
    """Read a sparse feature trajectory across a frame range (max 20000 frames)."""
    from .tracing import get_track
    return get_track(video_id, track_id, start_frame, end_frame, ROOT)


@mcp.tool()
def identify_video_insert(video_id: str, frame: int) -> dict:
    """Check a frame against excluded annotations and the local known-template hash catalog.

    Unknown origins are returned as unknown with a review path; the tool does not invent sources.
    """
    from .tracing import identify_insert
    return identify_insert(video_id, frame, ROOT)


@mcp.tool()
def exclude_trace_inserts(video_id: str, ranges: list[dict]) -> dict:
    """Apply reviewed meme/insert exclusions to an existing trace and clear their geometry.

    ranges: {start_frame, end_frame, kind, label, origin:{source_url,...}, evidence}.
    A claimed origin requires source_url. Use only after visual/source review.
    """
    from .tracing import apply_exclusions
    return apply_exclusions(video_id, ranges, ROOT)


@mcp.tool()
def search_art_styles(query: str = '', limit: int = 10) -> dict:
    """Search the art-style catalog built from trace statistics plus reviewed tags/notes."""
    from .styles import search
    return search(query, ROOT, limit)


@mcp.tool()
def plan_new_scene(concept: str, style_id: str | None = None, seed: int | str = 0,
                   duration_seconds: float = 8.0, fps: int = 24, weather: str | None = None,
                   reference_video: str | None = None, reference_frame: int | None = None) -> dict:
    """Plan an original scene from a concept using local style/trace evidence, seeded variations,
    procedural asset suggestions and an image-generation brief for the connected agent's image tool.
    Does not call a hosted image model or produce finished artwork."""
    from .planner import plan_scene
    return plan_scene(concept, style_id=style_id, seed=seed, duration_seconds=duration_seconds, fps=fps,
                      weather=weather, reference_video=reference_video, reference_frame=reference_frame, workspace=ROOT)


@mcp.tool()
def generate_procedural_asset(kind: str, seed: int = 0, width: int = 512, height: int = 512,
                              frames: int = 48, variant: int = 0, blur: float = 0.0) -> dict:
    """Generate a deterministic code-based asset/overlay loop (trees, snow, rain, wind, fog, sparks,
    bokeh, vignette, depth blur, etc.). Returns manifest and PNG paths under data/assets."""
    from .procedural import generate, KINDS
    if kind not in KINDS:
        raise ValueError(f"Unknown kind; available: {', '.join(sorted(KINDS))}")
    folder = ROOT/'data/assets'/f'{kind}-s{seed}-v{variant}-{width}x{height}'
    result = generate(kind, folder, seed=seed, width=width, height=height, frames=frames, variant=variant, blur=blur)
    result['directory'] = str(folder)
    return result


@mcp.tool()
def list_procedural_assets() -> dict:
    """List built-in procedural kinds and locally generated asset manifests."""
    from .procedural import KINDS
    built = []
    root = ROOT/'data/assets'
    if root.exists():
        for manifest in sorted(root.glob('*/manifest.json')):
            built.append(json.loads(manifest.read_text()) | {'directory': str(manifest.parent)})
    return {'kinds': KINDS, 'generated': built, 'scope': 'Original procedural code output; regenerate with generate_procedural_asset.'}


@mcp.tool()
def build_composite_scene(layers: list[dict], width: int = 1280, height: int = 720, fps: int = 24,
                          frames: int = 192, background: str = '#101827', title: str = 'Composite',
                          save_path: str | None = None) -> dict:
    """Create an editable depth-layered 2D composite scene with parallax from local image/overlay assets.

    layers: {id, asset, depth 0..1, x, y, width, height, scale, opacity, parallax}.
    Overlay sequences may use %04d frame tokens. Returns scene JSON; optionally saves it.
    """
    from .planner import composite_scene
    scene = composite_scene(layers, width=width, height=height, fps=fps, frames=frames, background=background, title=title)
    if save_path:
        target = confined(ROOT, save_path)
        if target.exists():
            raise ValueError('File already exists; use a new versioned path')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(scene, indent=2))
        return {'scene': scene, 'path': str(target)}
    return {'scene': scene}


@mcp.tool()
def plan_shots(beats: list[dict], fps: int = 24, duration_seconds: float | None = None) -> dict:
    """Allocate contiguous half-open shot intervals on an exact frame grid.

    Each beat: title, optional visual_brief/narration/acceptance, and seconds OR
    weight. Without duration_seconds every beat needs seconds. With a total,
    hints become proportional. This is planning, not forced audio alignment.
    """
    from .production import plan_shots as plan
    return plan(beats, fps, duration_seconds)


@mcp.tool()
def color_palette(base: str, harmony: str = 'complementary', dark: bool = True) -> dict:
    """Derive role-based colors and measured contrast from a #rrggbb base.

    Harmonies: complementary, analogous, triadic, split_complementary.
    Deterministic color math; not an artistic quality score.
    """
    from .production import color_palette as palette
    return palette(base, harmony, dark)


@mcp.tool()
def timing_sheet(frames: int, fps: int = 24, keys: list[dict] | None = None,
                 exposure_step: int = 2) -> dict:
    """Build an exposure/dope sheet with drawing numbers, key labels and intervals.

    keys are ordered {frame,label}; exposure_step 1/2/3/4 = ones/twos/threes/fours.
    Schedules drawings only; it does not draw inbetweens or accept spacing.
    """
    from .production import timing_sheet as sheet
    return sheet(frames, fps, keys, exposure_step)


@mcp.tool()
def create_project(name: str, brief: str = '', fps: int = 24, width: int = 1280,
                   height: int = 720, engine: str = '2d') -> dict:
    """Scaffold projects/<slug>/ with brief, shot plan, starter scene and review.

    Refuses existing projects. Creates editable source only, not a finished film.
    """
    from .scaffold import scaffold_project
    return scaffold_project(ROOT, name, brief, fps, width, height, engine)


@mcp.tool()
def get_skill(name: str = 'animation-director') -> dict:
    """Read a packaged production playbook by name; start with animation-director.

    Available names are listed by capabilities and studio://skills. Guidance does
    not install engines or change the host agent's weights.
    """
    return read_skill(name)


@mcp.tool()
def check_environment(smoke: bool = False, smoke_3d: bool = False) -> dict:
    """Check actual engines/packages/templates; optionally render tiny temporary proofs.

    No downloads or installation. Blender is optional unless smoke_3d is requested.
    This is environment readiness, not artistic QA.
    """
    return run_checks(smoke=smoke, smoke_3d=smoke_3d, workspace=ROOT)


@mcp.resource('studio://workflow')
def workflow() -> str:
    """Canonical production operating contract, identical to the director skill."""
    return read_skill('animation-director')['content']


@mcp.resource('studio://skills')
def skills() -> str:
    """Machine-readable routing catalog for the packaged skill library."""
    return json.dumps(skill_index(), indent=2)


@mcp.resource('studio://skills/{name}')
def skill_resource(name: str) -> str:
    """Read one allow-listed skill; unknown names cannot access arbitrary files."""
    return read_skill(name)['content']


@mcp.resource('studio://traces')
def trace_resource() -> str:
    """Local per-frame trace catalog and coverage."""
    from .tracing import read_catalog
    return json.dumps(read_catalog(ROOT), indent=2)


@mcp.resource('studio://traces/{video_id}')
def trace_video_resource(video_id: str) -> str:
    """One trace manifest (source, coverage, shots, cuts, style stats, insert candidates)."""
    from .tracing import _load_manifest
    _, manifest = _load_manifest(video_id, ROOT)
    return json.dumps(manifest, indent=2)


@mcp.resource('studio://styles')
def styles_resource() -> str:
    """Art-style catalog: measured stats plus reviewed tags/mechanics."""
    from .styles import catalog
    return json.dumps(catalog(ROOT), indent=2)


@mcp.resource('studio://assets')
def assets_resource() -> str:
    """Procedural asset kinds and locally generated manifests."""
    return json.dumps(list_procedural_assets(), indent=2)


@mcp.prompt()
def produce_video(brief: str) -> str:
    """Guide a connected agent through actual production and evidence-based review."""
    return workflow()+'\n\nUSER PRODUCTION BRIEF:\n'+brief


@mcp.tool()
def curve_points(controls: list[list[float]], samples: int = 64) -> dict:
    """Sample an exact cubic Bezier stroke from four normalized 0–1 control points."""
    import numpy as np
    c=np.asarray(controls,dtype=float)
    if c.shape != (4,2) or not np.isfinite(c).all() or (c<0).any() or (c>1).any():
        raise ValueError('Supply four finite 2D control points in [0,1]')
    if not 2<=samples<=1000:
        raise ValueError('Use 2–1000 samples')
    t=np.linspace(0,1,samples)
    basis=np.stack([(1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3],axis=1)
    points=basis@c
    return {'points':points.tolist(),'method':'exact geometry',
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
    folder = ROOT/"reports"
    folder.mkdir(exist_ok=True)
    folder = folder
    folder.mkdir(exist_ok=True)
    entry = {"task":task,"observation":observation,"artifact":str(artifact),"verified_by_caller":verified}
    with (folder/"lessons.jsonl").open("a") as f:
        f.write(json.dumps(entry)+"\n")
    return {"saved":True,"model_weights_changed":False}


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
