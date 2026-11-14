---
name: drawing
description: Construct recognizable original drawings, character sheets and animation-ready layered SVG/raster assets.
---

# Drawing for animation

Use for character design, illustration, pose construction, stroke animation and preparing art that can actually be animated. Load [composition](../composition/SKILL.md) for staging and [2d-animation](../2d-animation/SKILL.md) for motion.

## Inputs to establish

Subject, viewpoint, style, proportions, emotion/action, palette, output size and whether the result must be layered. Preserve supplied reference images and rights information. If no style is specified, start with a clear silhouette and a small value palette rather than decorative detail.

## Construction workflow

1. **Gesture before contour.** Find the action line, tilt of shoulders/pelvis and weight-bearing foot. A pose should communicate its action in silhouette.
2. **Build simple volumes.** Use spheres, boxes and cylinders for skull, ribcage, pelvis and limbs. Keep a consistent horizon and cross-contours; limbs taper toward joints.
3. **Check proportions deliberately.** Establish a head-height or stylized proportion guide. Compare left/right landmarks and joint spacing. Exaggeration is a design choice, not accidental inconsistency.
4. **Group values.** Thumbnail in 3–4 values: background, shadow family, light family, focal accent. Squint at the preview; detail must not destroy the big shape.
5. **Add anatomy and features.** Place eye line, brow, nose and mouth on the head's form. Hands start as palm masses plus finger gesture groups. Avoid tracing every muscle when a simple shape reads better.
6. **Refine edges and line weight.** Use heavier edges at contact/occlusion, lighter edges for internal form. Keep facial features readable at the final display size.
7. **Make a continuity sheet.** Front/side/three-quarter views, expression extremes, palette swatches, prop scale and distinctive costume landmarks. Reuse the same source assets across shots.

These are drawing methods, not a claim that the toolkit contains a general learned drawing model.

## Choose an editable representation

- **Native scene shapes:** `ellipse`, `rect`, `path`, `text` and `group`. Best for diagrams, motion graphics and simple characters.
- **SVG cut-out asset:** author pivot groups for torso, head, upper arms, forearms, hands, thighs, shins and feet. Keep joints overlapped enough to avoid gaps. See `examples/01-2d-moonlight/character.svg` and `src/animation_mcp/character.py`.
- **Separate raster plates:** background, midground, character and foreground. Supply PNG/JPEG/SVG files with appropriate rights. Transparent character plates are useful for parallax.
- **Pose sequence:** rasterize genuinely different drawings to `pose-%04d.png`, starting at 0000. A scene image layer can use that exact token. Moving one flat drawing is not the same as drawing new poses.

The scene path format is a polyline, not arbitrary SVG path commands. `curve_points` samples a cubic Bezier from four normalized control points; scale those points into the layer's local coordinates. Analytic geometry is preferred over the narrow learned curve baseline.

## Minimal native drawing

```json
{
  "version": 1, "width": 320, "height": 180, "fps": 24, "frames": 24,
  "background": "#102030",
  "layers": [
    {"id":"head","kind":"ellipse","x":160,"y":70,"width":64,"height":72,
     "fill":"#e8b47a","stroke":"#172536","stroke_width":3},
    {"id":"eye","kind":"ellipse","x":174,"y":65,"width":7,"height":10,
     "fill":"#172536"}
  ]
}
```

Shapes are centered on `x,y`. Path points are local to the layer transform. A parent group must be declared before its children. For a cut-out eye, parent it to the head rather than animating it independently in world space.

## Tool route

1. `concept_brief` prepares a prompt for the host's own image tool; it does not generate an image.
2. Save original/supplied art inside the workspace and record provenance.
3. `save_scene` validates the layer structure.
4. `preview_frame` produces a PNG and an editable SVG at an exact frame.
5. Inspect the actual preview. Fix construction before animating a flawed design.

Without MCP, edit `templates/scene-2d.json`, then use `animation-studio render <scene.json> --output output/drawing-proof --workspace <asset-directory>`.

## Animation-ready checks

- Joints remain connected through the full intended pose range.
- Eyes, hair, clothing and props have explicit parents/attachment points.
- Separate movable parts from baked scenery; do not promise independent motion from a flattened image.
- Keep stroke widths, facial proportions and palette consistent across poses.
- Check silhouette, tangent edges, accidental overlaps and readability at final size.
- For stroke reveal, use an open unfilled path. The renderer trims by arc length; it does not morph one filled subject into another.

## Common failures

A detailed but stiff drawing needs gesture/weight work, not more texture. A face that drifts between poses needs landmarks and head construction. Gaps at elbows need overlapping cut-out parts. A “3D-looking” flat plate still lacks parallax and occlusion; construct depth layers or use Blender.

Accept only after viewing the exported drawing. Record specific observations, not an invented art score.
