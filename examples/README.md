# Skill-test examples

These are authored, reproducible tests of the rebuilt MCP surface. They are original exercises informed by the supplied reference study, not copies of the reference films. Technical QA and artistic review are reported separately; see `reports/REBUILD_VALIDATION.md` for the measured summary.

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

## Regeneration

```bash
PATH="/path/to/ffmpeg/bin:$PATH" python scripts/build_showcase.py --stage all
```

Stages: `author`, `2d`, `reactions`, `3d`, `edit`, `all`. Blender is required for 3D. The reaction stage re-renders from the stored `voice.wav` and `narration.json`; re-transcribing requires the pinned Whisper model. Generated frame sequences and intermediate encode files are gitignored; source projects, cue plans, QA and final videos are retained where size permits.
