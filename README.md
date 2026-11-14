# Animation Agent Studio

A local MCP production toolkit for narration-led videos, editable 2D characters, reaction edits and procedural rigged 3D animation. Includes rendered examples and the user's recovered basketball project.

**Start with the videos in [exmapels](exmapels/README.md)** — that folder uses the spelling requested by the user. It includes a 20.2-second narrated explainer, two reaction-video workflows, a 2D character study, and four 3D exercises. Sources and QA accompany the exports.

## Install and connect

Tested on Linux, Python 3.12, FFmpeg, Cairo and Blender 4.3.2 with CPU rendering. Blender enables the optional 3D tools.

```bash
cd /workspace/Learn_drawing
bash scripts/setup.sh
.venv/bin/python scripts/prepare_models.py
```

Setup writes `output/mcp-client.json` with the current interpreter, workspace and model-cache paths. Copy that server entry into an MCP-capable client's configuration and reconnect it. The tracked [.mcp.json](.mcp.json) is configured for this cloud checkout. On another machine, run `scripts/configure_client.py` there to generate the correct paths. Hosts differ in how they register MCP servers; the repository file alone does not connect every agent automatically.

Ask the connected agent to read `studio://workflow` or invoke the `produce_video` prompt. Start with `capabilities`, `get_model_catalog` and `get_scene_schema`. The host agent supplies creative reasoning; connecting the server does not alter its weights.

## Available workflows

| Goal | Tools |
|---|---|
| Create test speech | `synthesize_narration`: offline eSpeak audio and engine word events |
| Use an uploaded English voiceover | `prepare_voiceover_model`, then `transcribe_voiceover`: local Whisper base.en and estimated word times |
| Choose and time reactions | `select_reaction`, `plan_reaction_cues`, `render_reaction_video` |
| Use your own memes | Pass local image/GIF/video paths as `asset_overrides`; original bundled reaction art works without accounts |
| Search supplied references | `prepare_reference_models`, then `search_reference_library`: local pretrained CLIP retrieval |
| Draw and animate 2D | `save_scene`, `preview_frame`, `render_scene`: SVG paths, nested groups, keyframes, blinks, stroke reveals and image layers |
| Rig and animate 3D | `render_3d_scene`, `render_3d_exercise`: weighted humanoid mesh, armature, IK, custom target keys, camera motion and editable `.blend` |
| Edit a YouTube video | `assemble_video`: timed cuts, aspect fitting, explicit final-frame holds, captions and narration |
| Inspect and retain lessons | `inspect_video`, `record_lesson` |

`concept_brief` prepares a prompt for the host's image generator. This MCP does not bundle a hosted image-generation service. Giphy/Tenor search and account access are not implemented; local licensed reaction assets are supported.

## Models and actual training

| Model | Origin and scope |
|---|---|
| Reaction intent classifier | Trained here on 110 original synthetic English examples; 19/20 on a fixed sentence holdout. Six editorial intents, not a general humor or language model. Probabilities are uncalibrated. |
| Curve interpolator | Earlier bounded supervised experiment; predicts points from supplied Bezier controls. Exact mathematics remains better and is the production default. |
| CLIP ViT-B/32 | Pretrained upstream, reused unchanged. Searches 330 sampled frames from 55 supplied videos. Similarity is not an artistic score. |
| Whisper base.en | Pretrained upstream, reused unchanged. Transcribes English speech; word timing and uncertain words need review. |
| Basketball checkpoints | Recovered scene-specific reconstruction models, preserved with original source in `legacy/`; not a general artist or learned animation system. |

Small models, reference embeddings and original reaction art are bundled in the Python wheel. Large upstream models remain outside Git. Preparation tools fetch pinned revisions and verify SHA-256 checksums, about 750 MB total. Model cards declare MIT licenses; manifests record the origins. No API key or paid training service was used.

Actual new training was supervised reaction classification. Reference indexing is not fine-tuning, and no general visual model or reinforcement-learning policy was trained in this iteration. See [training/LESSONS.md](training/LESSONS.md), [training/ROADMAP.md](training/ROADMAP.md) and [the evaluation report](reports/ITERATION_02.md).

## Reproduce the examples

```bash
.venv/bin/python scripts/render_reaction_example.py
.venv/bin/python scripts/render_character_example.py
.venv/bin/python scripts/render_exercise_suite.py
.venv/bin/python scripts/render_explainer_example.py
```

The explainer uses the character's clean visual master to avoid duplicated burned captions. The 3D suite limits concurrency to two CPU workers. The default exercises use short, modest-resolution previews. Difficulty labels describe these exercises, not parity with the user's advanced reference films.

Run the full local model checks with:

```bash
ANIMATION_MODEL_CACHE=/workspace/drawing-models/clip \
ANIMATION_ASR_CACHE=/workspace/drawing-models/whisper-base.en \
.venv/bin/python -m pytest -q
```

Tests that need unfetched pretrained models or an absent Blender executable skip explicitly. CI does not claim to validate models it has not downloaded. See [docs/USAGE.md](docs/USAGE.md) for schema conventions and limits.

## Supplied Drive material

The first Drive folder's 13 files remain recorded in [its manifest](migration/drive_manifest.json). The new folder currently exposed **62 files, including 55 videos**, all downloaded and hashed. Six frames per video were decoded and indexed. [The new manifest](migration/reference_drive_manifest.json) records the files actually available. The channel catalog lists 184 intended videos; it is not evidence that all were uploaded. Alan Becker's progress file reports 10/67, and no files were visible in Remnant777's folder at inspection.

```bash
.venv/bin/python scripts/migrate_drive.py \
  --manifest migration/reference_drive_manifest.json \
  --output /workspace/drawing-data/new-drive
```

Original third-party videos and study boards remain outside Git. Source metadata, observations, checksums and restoration instructions are versioned. The uploaded master prompt is retained as reference text rather than activated as repository instructions. Cookies were not needed or read. [Study notes](references/STUDY_02.md) distinguish observed frames, an ASR-assisted audio excerpt, and unreviewed content.

## Current limits

The examples demonstrate working tools and bounded exercises. They do not establish general drawing intelligence, arbitrary mesh auto-rigging, expressive lip sync, feature-film character acting or the user's advanced reference quality. ASR estimates are not frame-accurate ground truth; the measured demo onset error reached about 0.28 seconds. The synthetic voice is a test voice. Full playback, humor and artistic acceptance remain viewer review; contact-sheet and metadata checks are reported separately.

The server is a trusted local stdio tool, not a hardened public render service. Render budgets are bounded. External dependencies retain their licenses; the original FSRCNN license and user project provenance are preserved. No new license is asserted over recovered or third-party materials.
