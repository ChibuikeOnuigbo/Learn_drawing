# Author, render, inspect, revise

Start with `capabilities`, then ask the agent to write a shot plan with exact frame intervals. Use `save_scene`, `preview_frame`, `render_scene` and `inspect_video`. Inspect the resulting PNGs and video before accepting artistic quality. Record concrete defects using `record_lesson` and revise the scene under a new filename.

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

Layers are ordered from back to front. Shapes are centered on `x,y`; paths use local point coordinates. Rotation uses degrees around the layer origin. Image paths and audio paths are relative to `ANIMATION_WORKSPACE`. Image transforms allow parallax using separate background/midground/foreground PNGs.

Visibility is `[start,end)`. Keyframe easing on a key describes motion **into that key**. Values hold before the first and after the last key. A key at `scene.frames` supplies the endpoint of a transition; the last rendered frame is `scene.frames - 1`.

Animate `x`, `y`, `scale`, `scale_x`, `scale_y`, `rotation`, `opacity` or `reveal`. Independent X/Y scale supports eye blinks and squash/stretch. A `group` layer can parent other layers: declare it first and set each child's `parent` to its ID. Transforms and visibility inherit through groups. See `exmapels/2d-character/scene.json` for a complete editable character.

`reveal` trims a point path by its actual length. Paths stay open and unfilled until fully revealed; this is a stroke animation, not a fill morph. Curves can be sampled using `curve_points`. Colors use `#rrggbb` or `none`. Text is escaped, single-line vector text; use separate layers for lines.

Set `audio` to a local voiceover path to mux narration. The renderer rejects narration longer than the scene and pads shorter tracks with silence; it does not align speech or generate captions automatically.

## Edit clips and add captions

Call `assemble_video` with:

```json
{
  "edit": {
    "width": 1080, "height": 1920, "fps": 30,
    "clips": [
      {"path": "output/shot-a/video.mp4", "start": 0, "duration": 3},
      {"path": "output/shot-b/video.mp4", "start": 1, "duration": 2}
    ],
    "captions": [{"text": "One idea at a time.", "start": 0.5, "end": 2.8}],
    "audio": "assets/narration.wav"
  }
}
```

Clips use aspect-fit padding rather than cropping important content. Durations round to the output frame grid. Source clip audio is discarded; provide a separate narration/music mix if needed. Caption intervals are half-open, positioned near the lower center. Automatic typography only wraps on whitespace; shorten long unbroken words and use short cues. Cuts are supported; cross-dissolves, music ducking, beat detection and forced alignment remain future work.

Set a clip's `hold_last` to `true` to freeze its final frame when the narration slot exceeds the source duration. The default rejects an overlong source interval. Use clean visual masters when adding new captions; the example explainer avoids duplicating the character study's burned captions.

`caption_position` sets the caption block's lower edge as a fraction of frame height (default `0.8`). The landscape explainer uses `0.94` so captions leave the character's feet visible. Check the intended platform's safe area before reusing that position in vertical Shorts.

## 3D

Use `examples/orbital-3d.json` for primitive scenes or `exmapels/3d/*/scene3d.json` for rigged examples. Call `get_scene_schema` with `kind: "3d"` for the full schema. Supported primitives are sphere, cube, cylinder, cone and torus. The studio adds three area lights, a world and materials. Object poses specify frame, location, rotation **in radians**, and scale. Camera keys specify location and look target.

`rigs` can add a weighted humanoid with `idle`, `wave`, `walk` or `pickup` actions. `target_keys` can animate `hand.R`, `hand.L`, `foot.R` and `foot.L` IK controls. A key location is relative to the rig's configured origin; constraints are solved in world space. The presets are editable starting points, not arbitrary mesh auto-rigging or learned acting. Output includes `.blend`, video and evaluated rig QA. The current cloud Blender build lacks OpenImageDenoise, so supported presets use `denoise: false`.

## Narration and reactions

Call `synthesize_narration` to generate a test voice and engine word events. For supplied audio, prepare the pinned speech model, call `transcribe_voiceover`, and review uncertain words. Pass the returned `narration_json` to `plan_reaction_cues` or `render_reaction_video`.

The selector uses six narrow learned intents plus editorial abstention/negation rules. Three original reaction asset families are bundled. Optional `asset_overrides` maps intents such as `brain_wipe` to local image, GIF or video paths. Animated assets use a bounded six-second decoded loop. The tool does not download memes from external services.

Cue frames round supplied word times to the frame grid. Engine timestamps and ASR estimates have different accuracy: ASR onset offsets reached 0.279 seconds in the measured story. Inspect the exported audio/video before treating synchronization or humor as accepted.

## Reproducible practice

1. Select one 3–10 second skill: perspective, reveal, easing, parallax, pose continuity or narration timing.
2. Author an original scene and explicit acceptance conditions.
3. Render a small preview and extract boundary frames.
4. Check drawing, timing, legibility and full motion separately; metadata alone cannot prove artistic quality.
5. Fix concrete defects, rerender affected work, save a lesson linked to evidence.

Use the existing checkout in each isolated cloud task. Do not create Git worktrees unless requested. Live server/render processes do not survive environment publication; start the MCP server again through the host configuration.
