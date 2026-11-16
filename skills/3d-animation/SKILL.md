---
name: 3d-animation
description: Build and render editable Blender scenes with primitives, authored presets, materials, lighting, cameras and measured QA.
---

# 3D animation

Use for object animation, stylized staged shots and the bundled humanoid exercises. Check `capabilities` before planning a render. Blender is optional for installation but required for actual 3D output.

## Supported scene boundary

The strict JSON schema supports:

- Objects: sphere, cube, cylinder, cone, torus.
- Object poses: frame, location, rotation in **radians**, positive scale.
- Camera: initial location/target and keyed location/look-target.
- Humanoid rigs: idle, wave, walk, pickup, reach; see [character-rigging](../character-rigging/SKILL.md).
- Art direction: `basic`, `easy`, `simple`, `medium`, `hard`.
- Cycles CPU samples and optional denoising.

It does **not** accept arbitrary mesh imports, sculpting commands, materials graphs, physics settings or executable Blender code. Do not invent fields for them. The saved `.blend` can be opened in Blender for an authorized human/agent workflow beyond this schema; keep that work separate from validated MCP renders.

## Production workflow

1. **Block the set and scale.** Z is up. Decide floor height, character height, prop size and travel distance before posing.
2. **Choose the camera.** Establish geography, then frame the action. The bundled camera lens is 48 mm; move position/target rather than adding an unsupported lens parameter.
3. **Key major poses.** Start, anticipation, contact/extreme and settle. Object keys are strictly ordered. Check interpolation and silhouette before adding detail.
4. **Light for separation.** Presets include authored materials and lights. Basic scenes get a simple default stage; inspect subject/background contrast rather than assuming a primitive is finished art.
5. **Render a proof.** Use small dimensions, few frames and low samples. There is no 3D still-preview tool; render a short actual sequence.
6. **Inspect and refine.** Check clipping, floor contact, prop attachment, camera crop, light direction, grain and motion continuity.
7. **Final export.** Increase resolution/samples only after the proof works. Preserve `scene3d.json`, `scene.blend`, video and QA.

## Minimal editable scene

`templates/scene-3d.json` is a short moving-object proof. The schema shape is:

```json
{
  "width":320,"height":180,"fps":24,"frames":24,"samples":4,
  "art_direction":"basic","camera":[4,-6,3],"target":[0,0,0.6],
  "objects":[{
    "name":"Hero","kind":"sphere","color":[0.1,0.6,0.7],
    "location":[0,0,0.6],"scale":[0.5,0.5,0.5],
    "poses":[
      {"frame":0,"location":[-0.7,0,0.6],"rotation":[0,0,0],"scale":[0.5,0.5,0.5]},
      {"frame":23,"location":[0.7,0,0.6],"rotation":[0,1.57,0],"scale":[0.5,0.5,0.5]}
    ]
  }]
}
```

RGB components are in `[0,1]`. Names are unique. Camera location and target must differ. `frames` is at most 600; dimensions at most 1920 per side. The render budget is `width × height × frames × samples ≤ 1.5 billion`.

## Choose a preset honestly

| Preset | Actual exercise | Useful starting point for |
|---|---|---|
| easy | Squash/stretch bounce on a dais | Weight, impact spacing |
| simple | Weighted humanoid wave | Arm motion, planted feet |
| medium | Humanoid walk through portals | Stance/swing and camera tracking |
| hard | Reach/grasp in a corridor | Hand target, payload attachment, staged camera |

`render_3d_exercise(level=...)` renders these directly. To customize, load the matching `examples/03-3d-*/scene3d.json`, edit supported fields and call `render_3d_scene`. Difficulty labels describe these exercises, not professional-film parity.

## Local execution

```bash
animation-studio doctor --smoke
animation-studio render3d templates/scene-3d.json --output output/3d-proof
```

`ANIMATION_BLENDER` may name an executable on PATH or an absolute executable/wrapper path. `ANIMATION_BLENDER_TIMEOUT` defaults to 3600 seconds. Use a long-running process mechanism for renders rather than a short shell timeout.

`ANIMATION_RESUME=1` allows the example worker to reuse existing frame PNGs. Only use it when the scene/settings are unchanged; otherwise start a fresh output directory. Resume is a render optimization, not QA evidence.

In a headless sandbox, keep `bpy` separate from the project venv because their NumPy requirements conflict. See `docs/HEADLESS_BLENDER.md`; prefer a normal Blender installation.

## Review and failure recovery

- Missing Blender: deliver the validated scene and installation instructions, not a claimed video.
- Schema error: call `get_scene_schema(kind="3d")`; remove invented fields and fix units/order.
- Budget error: reduce proof resolution, duration or samples; do not bypass the guard.
- Timeout: inspect the render log and existing frames, then resume only an unchanged job.
- Rig failure: read `rig-qa.json`; unreachable targets or floor penetration require pose changes, not a relaxed threshold.
- Grainy proof: inspect lighting and sample count. Denoising is not a substitute for a readable scene.

`technical_pass` includes export checks and, for bundled rigs, geometry checks. It does not establish attractive lighting, convincing acting or similarity to a reference film.
