# Drive recreation validation

Scope: replace the generic 0.5.0 starter demos with studies driven by the user's research Drive, then deepen them (0.7.0). This report records measured export/geometry checks and sampled-frame review. It is not human playback approval or a claim of source recovery.

## What was studied

Read-only Drive research (folder `1prGI_23hOqgjXHfZd_nc0BEf3DGfIVoI`) including:

- `LEARNED_CURTAIN_ANIMATION_AND_DISTORTIONS.md`, `CURTAIN_ONLY_MASTER_AGENT_PROMPT.md`, `V9_REBUILD_AND_MODEL_NOTES.md`; decoded `REFERENCE_01_PINNED_DRAPE_720p.mp4`, `REFERENCE_02_WIND_WAVE_720p.mp4`, `RECOVERED_V7_13s_60fps_720p.mp4`.
- `EYE_ANIMATION_RESEARCH.md`, `EYE_SOURCE_RESEARCH_BUNDLE.zip` (deformation lab notes/tests, `code/blink.py`), `MOTION__DISTORTION_AND_MOTION_WORK.md`, `PROJECT_HISTORY.md`, `LEARNED_GTA_LOADING_MEME.md`.
- `START_HERE_LEARNINGS.md` / `DEATH_NOTE_LEARNINGS_EVIDENCE.zip`, decoded `03_LIGHT_L_TWO_FULL_IMAGES_V7.mp4`, full Light/L plates.
- `ANIME_AURA_MOTION_RESEARCH_PLAYBOOK.md` (full text read), `Composition_Motion_Research_Report.md`, `Motion_RL_Followup_README.md`, `11_User_Preferences_and_Workflow.md`.
- `OpenSketch_Human_Design_Strokes_CC0.zip` (357 SVGs, inspected) and `OpenSketch_Stroke_Experiment_Research.zip` (prior MLP code + held-out evaluation; the blend lost to a linear baseline on unseen houses).

Decisive lessons: do not crossfade photographs and call it cloth; do not substitute only a face under a body reveal; anchor roots/seams; keep material coordinates stable; label invented underlays; verify frames rather than trusting a metric or a model confidence; compare learned models to simple baselines.

## Measured results (0.7.0)

| Example | Size | FPS | Frames | Technical QA | Geometry / timing QA |
|---|---:|---:|---:|---|---|
| `05-curtain-mesh` comparison | 1280×720 | 60 | 240 | pass | 0 inverted render triangles; min area ratio 0.030; 17 Hz PBD control |
| `05-curtain-mesh` true control | 1280×720 | 17 | 68 | pass | same controls, no interpolation |
| `06-eye-face-performance` | 720×720 | 24 | 144 | pass | blink outside-box pixel diff = 0; aperture monotonic; upper lid travel > lower |
| `07-flashlight-whole-character` | 720×720 | 24 | 252 | pass | face alpha 0 before 4.5 s; first mean >0.5 at 4.667 s; alignment RMSE 7.74→6.07 px |
| `08-aura-rain-breath` | 576×864 | 24 | 192 | pass | 3 rain bands; face protected from warp/aura; not a seamless loop |
| `09-opensketch-stroke-trace` | 690×690 | 24 | 144 | pass | 82 CC0 human strokes replayed; derived variant labelled |

Curtain solver diagnostics (`mesh-qa.json`): max edge strain 0.876, max monotonic projection 25.8 px, 18 control samples used a reported fallback blend to an analytic safe pose when the 2D solve risked a fold. These are disclosed, not hidden; the render mesh itself has zero inversions.

Full local suite: **58 passed, 3 skipped** (Blender/CLIP-dependent skips). `doctor --smoke` 2D ready.

## Frame review performed

- Curtain: contact sheets for both 60 fps and 17 fps exports + frame 180. Panels release from tiebacks, travel centreward, meet at the seam and settle; fold shading is irregular and baked into a stable atlas (no temporal photo blending).
- Eye/face: contact sheet + gaze/smile/blink proof frames. The procedural blink closes cleanly without double lids or white streaks; lid skin is a smooth estimate. Earlier generated-underlay and squint prototypes were abandoned (see PROVENANCE).
- Flashlight: contact sheet + frame 115. The beam reveals the alternate character's face/hair/clothing together; outside the beam the base remains. Landmark alignment reduces rigid offset but hair/strawberry/hands still differ by design.
- Aura: contact sheet + frame 96. Red silhouette aura sits behind the figure; rain bands differ in speed/length; breath puff drifts and fades; face is protected from the warp.
- Strokes: traced and variant proof frames. The house linework is the actual CC0 human drawing; the red twist is labelled "not original".

## Limits

- These are technique restagings with original model-assisted art (plus one CC0 human sketch), not pixel reconstructions of the Drive videos.
- Curtain: 2D PBD, not 3D XPBD/cloth. Horizontal gathering follows the hung span; out-of-plane buckling is shading. A reported fallback blend guards fold risk. Solver strain is non-trivial and disclosed.
- Eye: lid skin is estimated from surrounding face colour, not recovered hidden artwork; no generated closed-lid plate is used.
- Flashlight: rigid landmark RMSE is not a structural-deviation certificate; generated plates remain approximate.
- Aura: procedural graphics, not fluid sim; rain evaluated continuously (playbook used 8 Hz samples); 8-second ramp is not a seamless loop.
- Strokes: product-design linework, not character/face animation; SVG path order is stored geometry, not recorded stylus timing. No stroke-MLP weights are used.
- No reference audio was copied. Exports are silent study renders.
