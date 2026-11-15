---
name: physics-secondary-motion
description: Author believable weight, arcs, overlap, follow-through and particle-like effects within the toolkit’s explicit keyframe limits.
---

# Physics and secondary motion

Use for bounces, throws, impacts, hair/cloth overlap, trails and particle bursts. This is authored motion, not a physics simulation engine.

## Primary action first

Block the main mass and contact points. Decide weight, force direction and energy loss. A heavy object accelerates and settles differently from a light one; spacing communicates this more than labels.

For a bounce: anticipate/release, accelerate toward contact, squash at impact, rebound with less energy, settle. Preserve approximate volume unless stylization intentionally breaks it. Keep the shadow/contact relationship coherent.

## Arcs and spacing

Sample positions along an arc rather than moving diagonally through space. Wider spacing reads faster; clustered spacing reads slower. Use `timing_sheet` to plan keys and exposure, then author actual poses/keys.

The 2D easing set is linear/ease_in/ease_out/smooth/hold. It does not provide arbitrary bezier easing or simulated collisions. Approximate a curve with explicit keys and inspect the result.

## Overlap and follow-through

Animate the root/body first. Delay loose parts by a few frames, then let them overshoot and settle. Keep attachment points fixed. Secondary action should support the story beat, not compete with it.

For cut-out characters, parent hair/sleeves/props to the correct body group. For the 3D humanoid, use supported IK actions and inspect contact/attachment; there is no cloth or soft-body solver in the MCP schema.

## Particle-like bursts

The toolkit can animate many explicit ellipse/path/image layers. A burst recipe:

1. Define emitter origin, trigger frame and lifetime.
2. Give each particle a direction, speed, size, spin and fade.
3. Add drag/gravity-like curvature with sampled keys if appropriate.
4. Stagger birth/death so the effect does not pop as one rigid group.
5. Keep particle count bounded; preview before scaling up.

See `examples/07-particle-burst/` for a deterministic authored burst. It is keyframed geometry, not a particle simulator, fire/fluid solve or learned VFX model.

## Validation

Inspect contact frames, extreme poses, trail continuity and fade endpoints. Check that objects do not slide through floors, detach from parents or vanish mid-action. Technical frame count cannot prove believable weight; review motion and state any playback limitation.
