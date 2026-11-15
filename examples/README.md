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

**Skill:** localized distortion, anchored secondary motion, stable material coordinates.

Restages the pinned-drape/wind-wave lesson from the research Drive with an original generated empty-window plate and one procedural fabric atlas per panel. A fixed 13×17 triangle mesh keeps the same topology every frame; outer stops and rail are pinned, inner gliders meet at center, the tieback releases, and the hem lags then settles. `mesh-qa.json` records fold/compression checks; `rig.json` records timing and pins. Render: `video.mp4`, 1280×720, 24 fps, 96 frames / 4.0 s.

**Measured:** technical pass; zero inverted triangles in sampled frames. **Review required:** fold spacing is still regular; this is a 2D warp, not cloth physics or recovered source fabric.

## 06 — Eye/face performance (`06-eye-face-performance/`)

**Skill:** traced apertures, original-pixel iris gaze, protected face, hair follow-through.

An original generated portrait is decomposed into traced eye apertures and a colour-masked iris layer. Gaze shifts the original iris over an inpainted sclera estimate; hair tips lag with protected roots; a local ellipse warp raises the mouth corners. `rig.json` stores the traced controls; `eye-qa.json` records scope. Render: `video.mp4`, 720×720, 24 fps, 144 frames / 6.0 s.

**Scope:** no full blink. A squint prototype duplicated brow pixels and was removed; hidden closed-lid skin is not claimed. The inpainted sclera under the iris is an estimate.

## 07 — Whole-character flashlight (`07-flashlight-whole-character/`)

**Skill:** two complete same-canvas layers, one pixelwise mask, body-first reveal timing.

Two original generated matched detectives are composited with a single feathered circle: outside the beam the base character stays visible at reduced gain; inside it the alternate character's hair, face, clothing and hands appear together. `rig.json` stores the cubic-Hermite path; `beam-qa.json` measures face alpha before/after the intended reveal. Render: `video.mp4`, 720×720, 24 fps, 252 frames / 10.5 s.

**Measured:** technical pass; max face alpha before 4.5 s = 0; first mean face alpha > 0.5 at 4.667 s; no face gate. **Review required:** generated plate alignment is approximate; inspect fingers, strawberry, neckline and shoulder at 100%.

## Regeneration

```bash
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_showcase.py --stage all
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_drive_recreations.py
# Select one recreation:
python scripts/build_drive_recreations.py --only curtain
python scripts/build_drive_recreations.py --only eye
python scripts/build_drive_recreations.py --only flashlight
```

Showcase stages: `author`, `2d`, `reactions`, `3d`, `edit`, `all`. Blender is required for 3D. The reaction stage re-renders from stored `voice.wav` and `narration.json`; re-transcribing requires the pinned Whisper model. `build_drive_recreations.py` requires FFmpeg/ffprobe and `pip install -e '.[research]'` (OpenCV). It uses the bundled generated plates; private Drive references are study-only and are not required. See `reports/DRIVE_RECREATION_VALIDATION.md` and `references/DRIVE_RESEARCH_DIGEST.md`.
