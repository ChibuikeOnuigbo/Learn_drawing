# Expansion validation — 0.5.0

Scope: deeper skill library, deterministic pre-production tools, no-overwrite scaffolder, expanded templates and five new rendered examples. This report records a specific local run; it is not automatic artistic acceptance.

## Commands

```bash
PATH="$PWD/.tools/bin:$PATH" ANIMATION_ASR_CACHE="$PWD/.work/whisper-cache" OPENBLAS_NUM_THREADS=1 .venv/bin/pytest -q
PATH="$PWD/.tools/bin:$PATH" .venv/bin/animation-studio doctor --smoke-3d --json
PATH="$PWD/.tools/bin:$PATH" .venv/bin/python scripts/build_skill_examples.py
```

## Results

- Pytest: **50 passed, 1 skipped**. The skip is optional CLIP retrieval because weights were not fetched. Whisper cache was re-fetched from the documented GitHub mirror and SHA-256 verified before the run.
- Doctor: `ok=true`, `ready.2d=true`, `ready.3d=true`, no failures. Checks include **16 readable playbooks**, expanded template validation, a real 3-frame 2D smoke proof and a real 2-frame Blender smoke proof.
- MCP surface: **28 tools**, 3 `studio://` resources and the `produce_video` prompt. New tools exercised through a real stdio client: `plan_shots`, `color_palette`, `timing_sheet`, `create_project`.
- Scaffold proofs: 2D and 3D projects created at 320×180 / 6 fps and rendered successfully (42 frames each). Portrait template rendered successfully (48 frames, 540×960).
- `scripts/bootstrap.py --smoke-3d`: PASS after reinstalling the editable package as 0.5.0.
- Wheel: `animation_agent_studio-0.5.0-py3-none-any.whl` built (~7.0 MB). A separate no-dependency venv installed it and read all 16 packaged skills plus the expanded template set through `importlib.resources`.

## New rendered examples

| Example | Dimensions | FPS | Frames | Duration | Technical QA |
|---|---:|---:|---:|---:|---|
| `05-kinetic-typography` | 960×540 | 24 | 96 | 4.000 s | pass |
| `06-2d-walk-cycle` | 640×360 | 24 | 48 | 2.000 s | pass; stance-foot y error 0.0 px |
| `07-particle-burst` | 960×540 | 24 | 72 | 3.000 s | pass |
| `08-vertical-short` | 540×960 | 24 | 120 | 5.000 s | pass |
| `09-narrated-explainer` | 1280×720 | 24 | 219 | 9.125 s | pass; AAC audio present; non-overlapping captions |

## Frame-based review performed

- Kinetic typography: contact sheet plus raw/encoded frames 70 and 75. Type is legible; a striped appearance in the downscaled JPEG contact sheet was not present in the raw or encoded frame.
- Walk cycle: contact sheet plus frames 6 and 18. Stance feet remain on the authored ground line; swing lift and arm counter-swing are visible. Geometric contact is not gait approval.
- Particle burst: contact sheet plus frame 24. Anticipation, shockwave and staggered sparks are visible. This is authored keyframes, not a particle simulation.
- Vertical Short: contact sheet plus frames 5 and 80. Headline, subtitle, lower caption and CTA remain inside the authored safe staging; phone-size/platform-overlay review remains a delivery step.
- Narrated explainer: contact sheet plus frame 109. An earlier redundant shot note collided with the caption block; it was removed, cuts were aligned to sentence-level engine word events, and caption cues were made non-overlapping before the final render.

## Limits

- `plan_shots` allocates a frame grid; it is not forced audio alignment.
- `color_palette` reports deterministic HLS roles and luminance contrast; it does not score mood, harmony or accessibility for all viewers.
- `timing_sheet` schedules exposure; it does not create drawings or accept spacing.
- The explainer uses offline synthetic eSpeak NG demo speech. Replace with supplied final voiceover for production.
- Technical pass and sampled frame review are separate from full-motion listening/artistic acceptance.
