---
name: motion-graphics
description: Design kinetic typography, explainers, diagrams and UI-style motion with readable hierarchy and disciplined easing.
---

# Motion graphics and kinetic typography

Use for titles, educational explainers, infographics, diagrams and interface-style animation. Load [storyboarding](../storyboarding/SKILL.md), [composition](../composition/SKILL.md) and [2d-animation](../2d-animation/SKILL.md).

## Hierarchy before movement

Identify primary message, supporting label and decorative motion. Animate them in that order of importance. A viewer should understand the frame even if motion stops.

For typography: short phrases, one idea per cue, generous line spacing, consistent alignment and readable holds. The native text layer is single-line and center-anchored; use separate layers for lines. For wrapped timed captions, use the edit tool.

## Motion grammar

- Enter with purpose: reveal, slide, scale or draw-on. Avoid combining every effect at once.
- Use easing that matches meaning: crisp UI response, weighted impact, calm editorial drift.
- Stagger related elements by a small consistent offset; do not make the viewer wait through arbitrary delays.
- Keep secondary motion subordinate to the message.
- Hold the completed state long enough to read. A useful starting point is at least 1–2 seconds for a short phrase, adjusted for length and audience.

Native tracks: x/y/scale/scale_x/scale_y/rotation/opacity/reveal. There is no blur, mask-path, text-per-glyph or automatic layout engine in the schema. Author separate layers when you need those behaviors.

## Diagrams and explainers

Use stroke reveal for construction lines and open paths. Keep arrows/labels attached to the same parent group as the object they describe. Reveal cause before effect. If a diagram changes state, preserve landmarks so the viewer can track what changed.

For narrated explainers, plan shots from real speech events where possible. `plan_shots` can allocate a proportional skeleton, but it is not alignment. Use a clean visual master and add captions once in the edit.

## Proof route

Start from `templates/scene-2d.json`. Preview first/middle/last and each text onset. Render a small proof, inspect legibility at target display size, then finalize.

Accept only after checking reading order, hold duration, safe areas, contrast and export timing. Motion energy is not a substitute for clarity.
