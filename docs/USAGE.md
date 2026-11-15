# Author, render, inspect, revise

Read [AGENTS.md](../AGENTS.md) and the [task playbooks](../skills/README.md) first. Run `animation-studio doctor --smoke` or MCP `check_environment` before claiming readiness. Validated starter scenes and brief/review forms are in [templates](../templates/README.md).

Start with `capabilities`, then ask the agent to write a shot plan with exact frame intervals. Use `save_scene`, `preview_frame`, `render_scene` and `inspect_video`. Inspect the resulting PNGs and video before accepting artistic quality. Record concrete defects using `record_lesson` and revise the scene under a new filename.

## Pre-production and scaffolding

```bash
animation-studio new my-film --brief "A 7-second proof about weight" --engine 2d
animation-studio new my-solid --engine 3d --width 640 --height 360
```

MCP: `create_project(name, brief, fps, width, height, engine)`. Both refuse an existing project and create `brief.md`, `shot-plan.json`, a starter scene, `assets/PROVENANCE.md` and `review.md`. The starter is a proof to edit, not a finished film.

- `plan_shots(beats, fps, duration_seconds=None)`: contiguous `[start,end)` shot intervals. Without a total, every beat needs `seconds`; with a total, `seconds`/`weight` hints are allocated proportionally. This is not forced audio alignment.
- `color_palette(base, harmony, dark)`: role colors plus measured luminance contrast. Harmonies: complementary, analogous, triadic, split_complementary. Contrast warnings are legibility checks, not artistic approval.
- `timing_sheet(frames, fps, keys, exposure_step)`: drawing numbers, held frames, key labels and interval spans. It schedules exposure; it does not draw poses or accept spacing.

Planning templates live in `templates/shot-plan.json`, `templates/exposure-sheet.json` and `templates/palette.json`; `templates/scene-vertical.json` is a portrait-safe starter.

## Minimal 2D scene

```json
{
  "width": 1280, "height": 720, "fps": 30, "frames": 90,
  "background": "#102030",
  "layers": [{
    "id": "ball", "kind": "ellipse", "x": 300, "y": 360,
    "width": 120, "height": 120, "fill": "#ff9900",
    "tracks": [{"property": "x", "keys": [
      {"frame": 0, "value": 300},
      {"frame": 60, "value": 900, "easing": "ease_out"}
    ]}]
  }]
}
```

Layers are ordered back to front. Shapes are centered on `x,y`; paths use local point coordinates. Rotation is degrees around the layer origin. MCP image/audio paths are relative to `ANIMATION_WORKSPACE`. The CLI uses `--workspace` (default: current directory); pass the scene's asset directory explicitly when needed. Image transforms allow parallax using separate background/midground/foreground plates. An image asset containing `%04d` is expanded with the current frame number, which supports pre-rasterized rig sequences.

Visibility is `[start,end)`. Keyframe easing on a key describes motion **into that key**. Values hold before the first and after the last key. A key at `scene.frames` supplies the endpoint of a transition; the last rendered frame is `scene.frames - 1`.

Animate `x`, `y`, `scale`, `scale_x`, `scale_y`, `rotation`, `opacity` or `reveal`. Independent X/Y scale supports blinks and squash/stretch. A `group` layer can parent other layers: declare it first and set each child's `parent` to its ID. Transforms and visibility inherit through groups. See `examples/01-2d-moonlight/scene.json` and `character.svg` for a complete nested cut-out rig.

`reveal` trims a point path by actual length. Paths stay open and unfilled until fully revealed; this is stroke animation, not a fill morph. Curves can be sampled with `curve_points`. Colors use `#rrggbb` or `none`. Text is escaped single-line vector text; use separate layers for lines.

Set `audio` to a local voiceover/music path to mux it. The renderer rejects narration longer than the scene and pads shorter tracks with silence; it does not align speech or generate captions automatically.

## Edit clips and add captions

Call `assemble_video` with the edit object directly:

```json
{
  "width": 1080, "height": 1920, "fps": 30,
  "clips": [
    {"path": "output/shot-a/video.mp4", "start": 0, "duration": 3},
    {"path": "output/shot-b/video.mp4", "start": 1, "duration": 2}
  ],
  "captions": [{"text": "One idea at a time.", "start": 0.5, "end": 2.8}],
  "audio": "assets/narration.wav"
}
```

Clips use aspect-fit padding rather than cropping important content. Durations round to the output frame grid. Source clip audio is discarded; provide a separate narration/music mix if needed. Caption intervals are half-open, positioned near the lower center. Automatic typography wraps on whitespace; shorten long unbroken words and use short cues. Cuts are supported; cross-dissolves, music ducking, beat detection and forced alignment remain future work.

Set a clip's `hold_last` to `true` to freeze its final frame when the slot exceeds the source duration. The default rejects an overlong source interval. `caption_position` sets the caption block's lower edge as a fraction of frame height (default `0.8`). Check the intended platform's safe area before reusing a position in vertical Shorts.

## 3D

Call `get_scene_schema` with `kind: "3d"` for the full schema. Basic mode supports sphere, cube, cylinder, cone and torus primitives with frame/location/rotation(radians)/scale poses and camera look-target keys. `art_direction` presets (`easy`, `simple`, `medium`, `hard`) add authored sets, materials, lighting and rigged characters; `render_3d_exercise` exposes them directly.

`rigs` add a weighted humanoid with `idle`, `wave`, `walk`, `pickup` or `reach` actions. `target_keys` animate `hand.R`, `hand.L`, `foot.R`, `foot.L` IK controls relative to the rig origin. Presets are editable starting points, not arbitrary mesh auto-rigging or authored acting. Output includes `.blend`, video and evaluated rig QA (foot height, IK target error, payload attachment). Difficulty labels describe these exercises, not parity with professional reference films.

Blender must be on PATH or selected with `ANIMATION_BLENDER`. In headless sandboxes without system Blender, an isolated `bpy` 4.5 environment can be used through `src/animation_mcp/blender_launcher.py`; keep it separate from the project venv because `bpy` requires NumPy 1.x while the project uses NumPy 2.x. The launcher accepts only the trusted worker and validated scene JSON.

## Narration and reactions

Call `synthesize_narration` to generate a test voice and engine word events. For supplied audio, prepare the pinned speech model, call `transcribe_voiceover`, and review uncertain words. Pass the returned `narration_json` to `plan_reaction_cues` or `render_reaction_video`.

The selector uses six transparent phrase-rule intents plus editorial abstention/negation rules; no fitted intent weights are bundled. Bundled assets include original anime-style disaster/victory illustrations and a third-party Squidward brain-erase GIF for the `brain_wipe` intent. Optional `asset_overrides` maps intents to local image/GIF/video paths. GIF frame durations are respected; video assets use a bounded six-second decoded loop. The tool does not download memes from external services.

Cue frames round supplied word times to the frame grid. Engine timestamps and ASR estimates have different accuracy; inspect exported audio/video before treating synchronization or humor as accepted. The brain-erase cue is deliberately placed after the short verbal setup (“No brains at all”) so the visual punchline lands rather than covering the words.

## Reproducible practice

1. Select one 3–10 second skill: perspective, reveal, easing, parallax, pose continuity or narration timing.
2. Author an original scene and explicit acceptance conditions.
3. Render a small preview and extract boundary frames.
4. Check drawing, timing, legibility and full motion separately; metadata alone cannot prove artistic quality.
5. Fix concrete defects, rerender affected work, save a lesson linked to evidence.

Use the existing checkout in each isolated cloud task. Do not create Git worktrees unless requested. Live server/render processes do not survive environment publication; start the MCP server again through the host configuration.

## Per-frame trace library, styles, planner and procedural assets

Restore authorized Drive videos locally first; the tools never download from YouTube.

```bash
pip install -e '.[research]'
python scripts/build_trace_library.py google_drive/clip.mp4 --output data/traces
python scripts/build_asset_kit.py
```

MCP surface:

- `trace_video_file`, `list_trace_library`, `get_trace_frame`, `get_trace_track`, `identify_video_insert`, `exclude_trace_inserts`.
- `search_art_styles`, `plan_new_scene`, `generate_procedural_asset`, `list_procedural_assets`, `build_composite_scene`.
- Resources: `studio://traces`, `studio://traces/{video_id}`, `studio://styles`, `studio://assets`.

Every decoded frame gets an index record. Sparse tracks/contours are normalized image evidence, not recovered brush strokes or rigs. Confirmed meme/insert ranges are excluded and carry `source_url` evidence; low-motion static shots are only review candidates. The local hash catalog identifies known templates (e.g. the bundled Squidward GIF), not exact episodes/uploads. Unknown origins require review and must not be invented.

`plan_new_scene` consumes reviewed style/trace evidence and emits a shot grid, seeded variations, asset suggestions and an image prompt for the connected agent's own image tool. It does not call a hosted generator. `build_composite_scene` creates editable depth-ordered parallax layers; overlay sequences use `%04d` frame tokens.

## Drive-informed recreation studies

Examples 05–07 restage techniques from the user's research Drive using original generated plates:

```bash
pip install -e '.[research]'
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_drive_recreations.py
python scripts/build_drive_recreations.py --only curtain --only eye --only flashlight --only aura --only strokes
```

Read `references/DRIVE_RESEARCH_DIGEST.md` for the source IDs/lessons and `reports/DRIVE_RECREATION_VALIDATION.md` for measured checks. The builder does not need the private Drive videos at render time; they were study-only. Inspect `mesh-qa.json`, `eye-qa.json` and `beam-qa.json` plus actual frames before accepting a result.
