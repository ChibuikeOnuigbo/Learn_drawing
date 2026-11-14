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

Animate `x`, `y`, `scale`, `rotation`, `opacity` or `reveal`. `reveal` trims a point path by its actual length. Paths stay open and unfilled until fully revealed; this is a stroke animation, not a fill morph. Curves can be sampled using `curve_points`. Colors use `#rrggbb` or `none`. Text is escaped, single-line vector text; use separate layers for lines.

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

## 3D

Use `examples/orbital-3d.json` as a template for `render_3d_scene`. Supported mesh primitives: sphere, cube, cylinder, cone, torus. The studio adds three area lights, a world, materials and a fixed target camera. Poses specify frame, location, rotation **in radians**, and scale. Output includes an editable `.blend` and video. This is a constrained scene renderer, not arbitrary mesh creation, skeletal animation or a complete 3D character workflow.

## Reproducible practice

1. Select one 3–10 second skill: perspective, reveal, easing, parallax, pose continuity or narration timing.
2. Author an original scene and explicit acceptance conditions.
3. Render a small preview and extract boundary frames.
4. Check drawing, timing, legibility and full motion separately; metadata alone cannot prove artistic quality.
5. Fix concrete defects, rerender affected work, save a lesson linked to evidence.

Use the existing checkout in each isolated cloud task. Do not create Git worktrees unless requested. Live server/render processes do not survive environment publication; start the MCP server again through the host configuration.
