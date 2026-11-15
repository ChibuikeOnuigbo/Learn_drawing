# Drive recreation validation

Scope: replace the generic 0.5.0 starter demos with three studies driven by the user's research Drive. This report records measured export/geometry checks and sampled-frame review. It is not human playback approval or a claim of source recovery.

## What was studied

Read-only Drive research (folder `1prGI_23hOqgjXHfZd_nc0BEf3DGfIVoI`) including:

- `LEARNED_CURTAIN_ANIMATION_AND_DISTORTIONS.md`, `CURTAIN_ONLY_MASTER_AGENT_PROMPT.md`, `V9_REBUILD_AND_MODEL_NOTES.md`; decoded `REFERENCE_01_PINNED_DRAPE_720p.mp4`, `REFERENCE_02_WIND_WAVE_720p.mp4`, `RECOVERED_V7_13s_60fps_720p.mp4`.
- `EYE_ANIMATION_RESEARCH.md`, `EYE_SOURCE_RESEARCH_BUNDLE.zip` (deformation lab notes/tests), `MOTION__DISTORTION_AND_MOTION_WORK.md`, `PROJECT_HISTORY.md`, `LEARNED_GTA_LOADING_MEME.md`.
- `START_HERE_LEARNINGS.md` / `DEATH_NOTE_LEARNINGS_EVIDENCE.zip`, decoded `03_LIGHT_L_TWO_FULL_IMAGES_V7.mp4`, full Light/L plates, flashlight reference contact sheet.
- `ANIME_AURA_MOTION_RESEARCH_PLAYBOOK.md`, `Composition_Motion_Research_Report.md`, `Motion_RL_Followup_README.md`, `11_User_Preferences_and_Workflow.md`.

The decisive lessons were: do not crossfade photographs and call it cloth; do not substitute only a face under a body reveal; anchor roots/seams; keep material coordinates stable; label invented underlays; verify frames rather than trusting a metric or a model confidence.

## What changed in the repository

- Removed generic examples 05–09 and `scripts/build_skill_examples.py`.
- Added `animation_mcp.deformation`: fixed-topology piecewise-affine mesh warp with premultiplied alpha and fold/compression checks; cubic Hermite keys with zero velocity at repeated pauses; one-mask whole-image flashlight composite.
- Added `scripts/build_drive_recreations.py` and examples 05–07 with bundled **original generated plates**, editable rig/path JSON, QA and H.264 exports.
- Drive references remain local study material under `google_drive/` (gitignored). They are not redistributed in the examples.

## Measured results

| Example | Size | FPS | Frames | Technical QA | Geometry / timing QA |
|---|---:|---:|---:|---|---|
| `05-curtain-mesh` | 1280×720 | 24 | 96 | pass | 0 inverted triangles across sampled frames; min area ratio > 0; single stable procedural texture per panel |
| `06-eye-face-performance` | 720×720 | 24 | 144 | pass | original-iris gaze separation; no blink warp claimed after a squint prototype duplicated brow pixels and was removed |
| `07-flashlight-whole-character` | 720×720 | 24 | 252 | pass | max face alpha before 4.5 s = 0; first mean face alpha > 0.5 at 4.667 s; one circle mask, no face gate |

## Frame review performed

- Curtain: contact sheet + frame 60. Open tied panels release and close; folds remain attached to the rail/hem. The fabric is a stylized procedural atlas, not recovered source cloth; fold spacing is still regular.
- Eye/face: contact sheet + gaze/smile frames. An earlier procedural sclera/iris replacement looked pasted-on; it was replaced with original iris pixels over an inpainted sclera estimate. A later local squint warp duplicated brow pixels and was removed rather than shipped.
- Flashlight: contact sheet + frame 115. The beam reveals the alternate character's face, hair and clothing together; outside the beam the base character remains visible. The matched plates are generated alternatives, not authentic source frames, and hand/strawberry alignment still needs close review.

## Limits

- These are technique restagings with original model-assisted art, not pixel reconstructions of the Drive videos.
- The curtain is a 2D fixed-topology warp, not XPBD cloth, collision solving or calibrated material length.
- The eye study does not recover hidden closed-lid skin and does not ship a full blink.
- The flashlight plates are approximately matched generated characters; no measured ≤15% structural-deviation claim is made.
- No reference audio was copied. Exports are silent study renders.
