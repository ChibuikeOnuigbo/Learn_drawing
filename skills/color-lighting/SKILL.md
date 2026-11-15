---
name: color-lighting
description: Design role-based palettes, value scripts and lighting direction; measure contrast without treating it as artistic approval.
---

# Color and lighting

Use with [composition](../composition/SKILL.md) and [drawing](../drawing/SKILL.md). Color should guide attention and story mood, not decorate every surface equally.

## Palette workflow

1. Define mood, focal subject and platform viewing conditions.
2. Choose a base color and call `color_palette(base="#rrggbb", harmony=..., dark=true|false)`.
3. Assign returned roles: background, surface, primary, secondary, accent, text, muted.
4. Thumbnail in 3–4 values first. Keep the strongest appropriate contrast at the focal area.
5. Reserve the accent for a meaningful object/beat. Avoid giving every prop the same saturation.
6. Inspect actual rendered frames under the intended background, not only swatches.

Supported harmonies: complementary, analogous, triadic, split_complementary. The tool uses deterministic HLS math and reports WCAG-style luminance contrast ratios. It warns when text pairs fall below 4.5 or essential graphics below 3. These are legibility checks, not proof of harmony, mood or accessibility for all viewers.

## Value and color script

Make a small sequence of thumbnails across the film. Mark where palette/value changes signal a story turn. A quiet scene can use a narrow value range; a reveal may widen it. Do not change palette every shot without narrative reason.

Check colorblind readability by relying on value/shape/position differences, not hue alone. If essential information is only “red vs green,” add labels, icons or contrast.

## Lighting for 2D plates

Establish one light direction. Keep cast shadows and occlusion consistent with it. Separate light/shadow families before texture. Rim light can detach a silhouette, but should not appear on every edge regardless of geometry.

## Lighting for Blender presets

The bundled presets include authored key/fill/rim and materials. The strict scene schema does not expose arbitrary light graphs. Inspect subject/background separation, shadow direction, clipping and grain. Low samples plus denoising can still look waxy or noisy; fix framing/light intent before raising samples.

For custom lighting beyond the schema, continue in the saved `.blend` through an authorized external workflow. Do not invent `lights` or material-node fields in MCP JSON.

## Acceptance

Check focal hierarchy at thumbnail size, text contrast, consistent light direction, palette continuity and platform compression. Record measured ratios separately from subjective mood/style review.
