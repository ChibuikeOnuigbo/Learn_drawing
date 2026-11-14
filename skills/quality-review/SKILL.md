---
name: quality-review
description: Review animation using exact frames, measured export/rig checks and separate artistic judgments; report only verified evidence.
---

# Quality review and delivery

Use for every deliverable. A render existing is not the same as a render being correct, and technical pass is not artistic approval.

## Evidence ladder

Use these labels precisely:

1. **Authored:** source JSON/SVG/edit plan exists and validates.
2. **Rendered:** an actual output file was produced.
3. **Technically verified:** metadata/frames/audio/rig checks were run against expectations.
4. **Visually reviewed:** actual frames or playback were inspected; state which.
5. **Artistically accepted:** the user/reviewer approved the creative result. Do not infer this from a metric.

Never claim full playback, listening, model training, reference parity or a calibrated quality score without the corresponding evidence.

## Technical checks

For video confirm codec, dimensions, fps, decoded frame count, duration and expected audio presence. Compare against the scene/edit plan, not just “a file plays.” Render tools return QA; `inspect_video` extracts exact frames and a contact sheet.

Important: standalone `inspect_video` has no expected scene argument. Its `technical_pass` means no supplied expectation failed; it does not independently know your intended duration/fps/audio. Compare its returned values with the brief yourself.

For 3D rigs also read `rig-qa.json`: armature modifier, weighted vertices, IK chains, foot penetration, target error and payload attachment. Current preset gates are foot Z ≥ −0.025, hold error < 0.001 and IK error < 0.03. Do not relax gates to manufacture a pass.

For reactions check cue-frame rounding, transcript flags, asset identity/provenance and hold duration. Rounding accuracy does not validate semantic choice or ASR truth.

## Visual/temporal checklist

Inspect first/middle/last frames, every cut, cue onset/offset, extreme pose and contact frame. Include adjacent frames at visibility boundaries.

- Drawing: recognizable construction, consistent proportions, clean silhouette, connected joints.
- Composition: focal hierarchy, no accidental tangents/cropping, readable text and safe areas.
- Motion: arcs, spacing, anticipation, follow-through, deliberate holds, no unintended pops.
- Continuity: screen direction, eyeline, costume/prop placement and palette across shots.
- 3D: floor contact, reachable IK, prop attachment, camera framing, light direction and grain.
- Sound: complete narration, intelligibility, mix balance and sync when listening is available.
- Rights: third-party assets identified; publication permission not assumed.

A contact sheet cannot prove smooth motion or audio quality. If playback/listening tools are unavailable, mark those reviews pending and give the user the file plus exact review points.

## Defect loop

Record one concrete defect at a time:

```text
Observation: left foot slides during frames 34–42.
Evidence: output/proof/inspection/sample-0007.png and rig-qa trace.
Cause hypothesis: foot target does not compensate for root travel.
Change: adjust local foot track; keep other motion unchanged.
Verification: rerender the same interval; compare contact and IK error.
```

Fix the source, rerender affected work and repeat inspection. Do not edit only the QA report. Use `record_lesson` for durable evidence-linked lessons; it appends project memory and does not train weights.

## Delivery packet

Use `templates/review.md`. Provide:

- Final video and poster/contact sheet when useful.
- Editable scene/SVG/edit JSON and `.blend` for 3D.
- Asset/provenance notes, especially third-party test media.
- Measured QA plus a short visual-review note and remaining limitations.
- Exact regeneration command and required engines/models.

Keep bulky regenerable frames out of Git. Preserve the source and small evidence needed to understand the result. Historical test results in `reports/REBUILD_VALIDATION.md` describe that run; they are not automatic validation of a new project.
