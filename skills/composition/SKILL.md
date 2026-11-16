---
name: composition
description: Stage readable shots with focal hierarchy, depth, camera continuity, color and framing for 2D and 3D animation.
---

# Composition and cinematography

Use before drawing detail or keyframing a camera. A composition must tell the viewer where to look and what changed.

## Start with the shot's job

Write one sentence: “The viewer notices ___ and understands ___.” Identify the focal subject, emotional distance and information that must remain visible. Choose framing accordingly: wide for geography, medium for action, close-up for reaction/detail.

Thumbnail at least two arrangements when the shot matters. Compare them small and in grayscale before committing. Thirds and golden ratios are optional guides; focal hierarchy, balance and story clarity are the goal.

## Build a value and depth hierarchy

1. Assign the strongest appropriate contrast to the focal area.
2. Group background shapes into a quieter value family.
3. Separate foreground, midground and background with scale, overlap, edge sharpness and motion speed.
4. Use leading lines, light, gaze and motion toward the story point. Avoid tangencies that merge head/prop silhouettes.
5. Reserve the strongest accent color for a meaningful object or beat. A consistent palette is more useful than many unrelated saturated colors.

For 2D, implement depth with separate image/vector layers and modest transform differences. For 3D, use actual geometry, occlusion, camera position and lighting. A scale animation alone is not evidence of a modeled environment.

## Camera plan

For every shot record: framing, camera position/target, subject screen direction, entrance/exit side, focal action and cut reason.

- Establish geography before rapid coverage changes.
- Maintain the action axis unless a deliberate neutral shot or visible move establishes a new side.
- Match eyeline and prop position across cuts.
- Move the camera for a reason: reveal, follow or emphasize. Avoid drifting just to appear cinematic.
- Hold long enough for the viewer to read a new image or caption.
- Keep critical faces, hands, text and captions away from edges and platform overlays.

The bundled 3D camera uses a 48 mm lens. The scene schema exposes location and look-target keys, not arbitrary lens/rack-focus controls. Use framing distance for emphasis, or continue in the saved `.blend` with an authorized external workflow.

## Map the plan to actual controls

**2D:** layer order is back-to-front; `x/y` are frame coordinates; rotation is degrees; scale is positive. Use separate background/character/foreground groups. Keep text as short single-line layers.

**3D:** Z is up, object rotations are radians, and camera keys contain `location` and `target`. Basic primitives plus preset sets are supported. Check the camera is not inside geometry and location never equals target.

Example camera keys for a short push-in:

```json
"camera_poses": [
  {"frame":0,"location":[4,-7,3],"target":[0,0,1]},
  {"frame":47,"location":[3.2,-6,2.6],"target":[0,0,1.1]}
]
```

Do not add a `lens` field to the JSON; strict validation will reject it.

## Color and light script

Make a small sequence of palette/value thumbnails across the film. Use changes to mark story turns, not every shot. In a 3D preset, inspect the authored key/fill/rim lighting and material contrast. Low-sample Cycles renders can be grainy even when metadata passes; denoising helps but does not repair bad staging.

## Proof and review

Use `preview_frame` for 2D. For 3D, render a short low-resolution proof with `render_3d_scene`; there is no separate still-preview MCP tool. Inspect first, middle and last frames plus cut boundaries.

Check:

- The focal point survives thumbnail-size viewing.
- The subject's silhouette is readable against the background.
- Screen direction, eyeline, prop placement and character design remain continuous.
- Camera movement does not crop the action or reveal unfinished set edges.
- Captions do not cover faces/hands and remain inside the intended safe area.
- The final frame resolves the shot rather than stopping mid-gesture.

A contact sheet can reveal composition and continuity problems, but it cannot prove temporal smoothness. Review playback when available; otherwise label that limitation.


## Local compositing path

Use `build_composite_scene` for depth-ordered background/midground/subject/foreground/overlay layers with parallax. Generate weather/blur/vignette assets with `generate_procedural_asset`. A Remnant777-specific study requires accessible source videos; see `reports/REMNANT777_COMPOSITING.md`. Do not label a generic composite as his technique.
