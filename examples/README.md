# Skill-test examples

These are authored, reproducible tests of the rebuilt MCP surface. Examples 01–04 are original engine exercises; examples 05–07 are Drive-informed technique restagings with original generated plates, not copies of the reference films. Technical QA and artistic review are reported separately; see `reports/REBUILD_VALIDATION.md` for the measured summary.

## 01 — 2D moonlight (`01-2d-moonlight/`)

**Skill:** asset-based 2D character animation, layered parallax, facial expression, focal FX.

- Painted observatory background (`observatory.jpg`, original AI-generated plate).
- Nested SVG cut-out rig (`character.svg`): body/head pivots, connected arms/legs, eye/blink layers, expression states.
- Independent orb halo/core, 26 particle sparks, foreground parallax silhouette, original synthesized music.
- `scene.json` is the editable timeline; `rig-frames/` is a regenerable raster intermediate (gitignored). Run `scripts/build_showcase.py --stage author` to rebuild it.
- Render: `render/video.mp4`, 1280×720, 24 fps, 240 frames / 10.0 s. `qa.json` reports technical pass.

**Artistic note:** substantially more constructed than a flat image translation, but still a stylized vector cartoon, not reference-film anime parity.

## 02 — Semantic reaction timing (`02-semantic-reactions/`)

**Skill:** generated test speech → local Whisper word times → intent classification → correct meme at the correct second.

| Clip | Trigger word | ASR word time | Cue frame @30fps | Asset |
|---|---:|---:|---:|---|
| `brain/` | “all.” | 1.20 s | 36 | Squidward brain-erase GIF (actual eraser gag) |
| `disaster/` | “messed” | 4.84 s | 145 | original anime disaster illustration |
| `victory/` | “worked.” | 2.54 s | 76 | original anime victory illustration |
| `victory/` | “comeback” | 4.92 s | 148 | original anime victory illustration |

Each folder contains `voice.wav`, `narration.json`, `cue-plan.json`, `video.mp4`, and `inspection/qa.json`. The brain cue is placed after the short verbal setup so the punchline lands. GIF frame durations are respected; the bundled copy is cropped only to remove blank source canvas.

**Measured:** cue rounding error ≤ half a frame; audio present; H.264/AAC export. **Review required:** ASR word boundaries are estimates; humor/taste is not scored by the classifier. The Squidward GIF is third-party; replace with licensed/original art before public publication.

## 03 — 3D exercises (`03-3d-easy|simple|medium|hard/`)

**Skill:** editable Blender projects, weight/spacing, humanoid IK, staged cinematography.

| Level | Exercise | Frames | Editable source | QA focus |
|---|---|---:|---|---|
| easy | squash/stretch bounce on inlaid dais | 96 | `scene.blend`, `scene3d.json` | impact spacing, export |
| simple | rigged wave on stage | 96 | `scene.blend`, `scene3d.json` | armature, IK reach, foot contact |
| medium | walk through light portals | 120 | `scene.blend`, `scene3d.json` | stance/swing feet, camera track |
| hard | reach/grasp in corridor with iris door + drone | 120 | `scene.blend`, `scene3d.json` | payload attachment, IK error, staged camera |

Renders are 800×450, 24 fps, Cycles CPU with denoising. `rig-qa.json` records evaluated deformed poses, minimum foot vertex height, max IK target error and payload hold error. Difficulty labels describe these exercises, **not** equivalence to the user's advanced reference films.

## 04 — Asset-based short (`04-asset-based-short/`)

**Skill:** multi-shot local assembly, captions, music, cross-engine asset reuse.

Assembles the 2D moonlight render and hard/simple 3D renders into a 9-second 1280×720 edit with timed captions and an original synthesized music bed. `edit.json` is the editable decision list; `qa.json` reports export checks. Source clip audio is intentionally dropped and replaced by the music track.

## 05 — Curtain mesh recreation (`05-curtain-mesh/`)

**Skill:** constraint-solved secondary motion, anchored deformation, stable material coordinates.

Restages the pinned-drape/wind-wave lesson with an original generated empty-window plate and one procedural fabric atlas per panel (baked irregular fold shading). Motion comes from a 2D position-based distance-constraint solve (`animation_mcp.cloth`) at **17 Hz**, cubic-interpolated to a **60 fps** comparison (`video.mp4`, 240 frames) plus a **true 17 fps** export (`video-17fps.mp4`, 68 frames). Rail gliders and outer stops are pinned, the tieback releases, panels collide at the centre seam, and the hem lags then settles. `mesh-qa.json` records fold checks, solver strain, projection magnitude and fallback count; `rig.json` records timing/pins.

**Measured:** technical pass on both exports; zero inverted render triangles. **Scope:** not 3D cloth. Horizontal gathering follows the hung span (out-of-plane buckling is shading, not solved depth); a reported fallback blend to an analytic safe pose guards fold risk. `previous-0.6/` preserves the first analytic-warp pass.

## 06 — Eye/face performance (`06-eye-face-performance/`)

**Skill:** traced apertures, original-pixel iris gaze, procedural blink, protected face, hair follow-through.

An original generated portrait is decomposed into traced eye apertures and a colour-masked iris layer. Gaze shifts the original iris over an inpainted sclera estimate; hair tips lag with protected roots; a local ellipse warp raises the mouth corners. A **procedural blink** (`animation_mcp.eye_rig`) closes traced apertures per column — upper lid travels farther, lashes ride the lid, and revealed lid skin is a smooth estimate sampled from the surrounding face. Pixels outside the eye neighbourhoods are asserted bit-identical. Render: `video.mp4`, 720×720, 24 fps, 144 frames / 6.0 s.

**Measured:** `max_pixel_diff_outside_eye_boxes = 0`; aperture area decreases monotonically with closure. **Scope:** lid skin is an estimate, not recovered hidden artwork; no generated closed-lid plate. Earlier generated-underlay and squint prototypes were abandoned and are documented in PROVENANCE. `previous-0.6/` preserves the no-blink pass.

## 07 — Whole-character flashlight (`07-flashlight-whole-character/`)

**Skill:** two complete same-canvas layers, one pixelwise mask, body-first reveal timing, measured plate alignment.

Two original generated matched detectives are composited with a single feathered circle: outside the beam the base stays visible at reduced gain; inside it the alternate's hair, face, clothing and hands appear together. B is first rigidly aligned to A via a similarity transform from 8 hand-picked landmarks; `alignment-qa.json` reports per-landmark residuals and RMSE before/after. `beam-qa.json` measures face alpha before/after the intended reveal. Render: `video.mp4`, 720×720, 24 fps, 252 frames / 10.5 s.

**Measured:** technical pass; max face alpha before 4.5 s = 0; first mean face alpha > 0.5 at 4.667 s; no face gate; alignment RMSE reduced vs. unaligned. **Review required:** landmark alignment is not a structural certificate — hair silhouette, strawberry and hands still differ by design; inspect at 100%. `previous-0.6/` preserves the unaligned pass.

## 08 — Aura / rain / breath (`08-aura-rain-breath/`)

**Skill:** silhouette-derived effects behind subject, depth-banded rain, face protection, breath timing.

An original generated hooded figure on chroma green is keyed/despilled and placed over a procedural dark alley. A red aura is derived from the dilated silhouette at three blur scales and screened **behind** the subject; three rain depth bands fall at different speeds/lengths with reduced coverage over the protected face; a periodic breath puff originates near the mouth, drifts and fades; tiny masked warps suggest breathing/cloth sway. Render: `video.mp4`, 576×864, 24 fps, 192 frames / 8.0 s.

**Scope:** graphic effects, not fluid simulation. Rain paths are evaluated continuously at 24 fps here (the Drive playbook sampled at 8 Hz); this difference is labelled in `aura-qa.json`. The clip is a weather ramp, **not** a seamless loop.

## 09 — OpenSketch stroke trace (`09-opensketch-stroke-trace/`)

**Skill:** licensed human-stroke tracing, geometry replay, labelled derived variant.

Replays one **CC0** OpenSketch human-drawn product-design sketch (Gryaditskaya et al.) stroke-by-stroke in SVG path order, then shows a red geometric twist variant explicitly labelled "not original". Render: `video.mp4`, 690×690, 24 fps, 144 frames / 6.0 s. Source SVG bundled under `assets/open-sketch/` with licence note.

**Scope:** product-design linework, not character/face animation; path order is stored geometry, not recorded stylus timing. No model weights from the prior Drive stroke-MLP experiment are used (that experiment lost to a linear baseline on unseen houses).

## Regeneration

```bash
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_showcase.py --stage all
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_drive_recreations.py
# Select one recreation:
python scripts/build_drive_recreations.py --only curtain
python scripts/build_drive_recreations.py --only eye
python scripts/build_drive_recreations.py --only flashlight
python scripts/build_drive_recreations.py --only aura
python scripts/build_drive_recreations.py --only strokes
```

Showcase stages: `author`, `2d`, `reactions`, `3d`, `edit`, `all`. Blender is required for 3D. The reaction stage re-renders from stored `voice.wav` and `narration.json`; re-transcribing requires the pinned Whisper model. `build_drive_recreations.py` requires FFmpeg/ffprobe and `pip install -e '.[research]'` (OpenCV). It uses the bundled generated plates and the CC0 OpenSketch SVG; private Drive references are study-only and are not required. See `reports/DRIVE_RECREATION_VALIDATION.md` and `references/DRIVE_RESEARCH_DIGEST.md`.

## 10 — Procedural asset kit (`10-procedural-assets/`)

**Skill:** deterministic code-generated assets, seamless overlay loops, depth-layer compositing.

Original procedural PNGs/SVG-style raster assets: oak/pine/bare trees, palm, bush, grass, rock, cloud; snow/rain/wind/fog/dust/leaves/sparks/bokeh loops; light rays, vignette and depth-blur overlays. `contact-sheet.jpg` previews the kit; `scene.json` is an editable 9-layer winter composite with parallax; `render/video.mp4` is a 144-frame / 6 s demo. Bulky generated sequences live in gitignored `data/assets/kit` and regenerate with `scripts/build_asset_kit.py`.

**Measured:** technical QA pass; overlay loops wrap modulo the canvas. **Scope:** stylized code output, not photogrammetry or a Remnant777 study. Inspect suitability per shot.

## 11 — Narrated talking scene (`11-talking-scene/`)

**Skill:** AI-plate scenery, depth-layered cloud drift, PNGTuber cutout lip-sync, timed captions.

A 19 s / 1280×720 / 24 fps narration scene in the style of Remnant777-approach talk videos: generated sky, cumulus/wispy cloud and grass-stone plates keyed and de-fringed by `scripts/prepare_talking_assets.py`, then composited with independent cloud speeds (far bands −26…−34 px, near bands −88…−118 px over the clip), 46 px grass parallax and a 1.06→1.10 sky push. The user's green-screen sticker avatar is keyed into three pixel-aligned plates (mouth open / closed / eyes closed) and swaps states from real eSpeak word timings (`speech/narration.json`), with independent blink spikes and a smooth talk bob. Five captions are timed to the narration words. `scene.json` is the editable timeline; regenerate with `scripts/render_talking_scene.py`. `render/inspection/` holds boundary-frame samples, `qa.json` and a contact sheet.

**Measured:** technical pass, 457 frames, audio muxed, mouth state matches word boundaries in sampled frames. **Scope:** layered 2.5D compositing per the research playbook — cloud motion is scrolling layers, not a fluid simulation. Full playback acceptance remains viewer review.

## 12 — PNGTuber interactive demo (`12-pngtuber-demo/`)

**Skill:** cutout-avatar state machine, mic-reactive mouth swap.

Self-contained `index.html` (states embedded, no server needed) that demonstrates PNGTuber behavior for the same cutout: expression moods (happy/excited/calm/surprised/sad affect bounce, speed and tilt), blink-interval slider, voice-energy meter, Auto Talk Demo (scripted envelope) and Manual/Mic Test (WebAudio RMS gate with adjustable sensitivity). `states.json` holds the three state PNGs as data URIs.

**Measured:** states load inline; UI covers voice energy, blink, talk and mic controls. **Scope:** an interactive demo harness for the cutout, not a tracking rig or a trained model.
