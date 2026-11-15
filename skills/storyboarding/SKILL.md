---
name: storyboarding
description: Turn a script or idea into beats, shot plans, animatics and exposure sheets with exact frame continuity.
---

# Storyboarding and animatics

Use before expensive animation. Load [composition](../composition/SKILL.md) for framing and [video-editing](../video-editing/SKILL.md) for the final cut.

## Beat → shot → drawing

1. Write the viewer takeaway in one sentence.
2. Split the story into beats: setup, change, payoff. Each beat needs a visible action, not only dialogue.
3. Assign shots with a purpose: establish geography, show action, reveal detail or capture reaction.
4. Thumbnail the strongest pose per shot. Check silhouette and screen direction before detail.
5. Build an animatic with held drawings and real/temporary sound. Judge readability and duration before inbetweens.

## Frame-accurate planning

Call `plan_shots` with beats containing `title`, optional `visual_brief`, `narration`, `acceptance`, and either `seconds` or `weight`.

- Without `duration_seconds`, every beat needs `seconds`; each rounds to the frame grid.
- With `duration_seconds`, hints become proportional and the total is exact via largest-remainder allocation.
- Intervals are `[start_frame,end_frame)`. Adjacent shots share no frame.
- `review_frames` gives first/middle/last frames to inspect.

This is not forced audio alignment. For narration-led work, replace estimated boundaries with reviewed word events and leave breathing room at sentence ends.

## Exposure sheets

Call `timing_sheet(frames, fps, keys=[{"frame":0,"label":"anticipation"}, ...], exposure_step=2)`.

- `exposure_step` 1/2/3/4 means ones/twos/threes/fours.
- The sheet returns drawing numbers, held frames, key labels and interval spans.
- It schedules drawings; it does not create poses or prove good spacing.

Block keys first, then decide where breakdowns and inbetweens belong. A hold can be intentional; an accidental frozen interval is a defect. Keep key labels tied to action (`contact`, `release`, `settle`) rather than vague numbers.

## Animatic proof

Use held image layers or simple vector poses in a 2D scene, or assemble still-derived clips with the edit tool. Keep captions short. If using temporary speech, label it synthetic/temporary and retime after final voiceover.

Inspect cut boundaries and the last readable frame of each shot. Ask: can a viewer understand the sequence without explanation? If not, fix staging/order before adding motion polish.

## Deliverables

Preserve `brief.md`, `shot-plan.json`, thumbnails/animatic, exposure sheet and review notes. Record changed durations and why. The scaffold command `animation-studio new <slug>` creates a starting structure, not a finished film.
