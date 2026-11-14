# Animation Agent Studio

A working local MCP toolkit for agents to author editable drawings, animate layered scenes, assemble videos, render simple 3D scenes and inspect real output. Includes the user's recovered basketball neural checkpoints and source projects.

This is an initial production foundation. It does **not** make every agent an expert animator, supply a universal drawing model, or establish parity with the user's advanced YouTube references.

## Start

Python 3.11+, FFmpeg/ffprobe and system Cairo are required. Blender 4.3+ enables 3D. Tested here with Python 3.12 and Blender 4.3.2 on CPU.

```bash
cd /workspace/Learn_drawing
bash scripts/setup.sh
source .venv/bin/activate
animation-studio render examples/explorer.json --output output/explorer
animation-studio render examples/ai-scenery.json --output output/ai-scenery
animation-studio render3d examples/orbital-3d.json --output output/orbital3d
```

Activate the environment before launching an MCP host, or replace `animation-mcp` in [.mcp.json](.mcp.json) with the absolute path to `.venv/bin/animation-mcp`. Set `ANIMATION_WORKSPACE` to this checkout on your machine. Hosts differ in how they load MCP configuration; adding this file alone does not connect an agent automatically.

For the current cloud instance, the tested interpreter is `/workspace/drawing-venv/bin/python` and the server executable is `/workspace/drawing-venv/bin/animation-mcp`.

## MCP tools

| Tool | Actual behavior |
|---|---|
| `capabilities` | Check engines and get the full 2D JSON schema |
| `save_scene` | Validate and save a versioned, editable scene |
| `preview_frame` | Write PNG and SVG for an exact frame |
| `render_scene` | Render H.264, optionally mux local narration, inspect output |
| `render_3d_scene` | CPU Blender primitive scenes, keyframes, lights, editable `.blend` |
| `assemble_video` | Trim/concatenate local clips, fit portrait/landscape, add timed captions and a narration track |
| `inspect_video` | Decode frames, measure metadata, extract boundary stills/contact sheet |
| `plan_narration` | Estimate sentence timings by word count; **not** forced alignment |
| `curve_points` | Exact Bezier points or the explicitly selected synthetic neural baseline |
| `concept_brief` | Prepare a prompt for the calling agent's image tool; does **not** generate an image |
| `record_lesson` | Append evidence-linked project memory; does **not** change neural weights |

The toolkit uses local stdio and workspace-contained paths. It does not accept arbitrary Blender scripts, shell commands or remote SVGs. Use a trusted local MCP client; this is not a hardened multi-tenant render service. Render calls block until complete and have preview budgets.

The calling agent does the creative planning and authors the scene. It may use its own image-generation tool to supply local PNG layers. No hosted AI provider or credentials are bundled. No Giphy/Tenor integration, automatic character rigging, mouth animation, generative video or advanced anime action system is implemented yet.

The second example demonstrates an AI background generated during this session, combined with an editable vector character and diagrams. It is a layered composition prototype, not learned character animation. `requirements.lock` captures the clean environment's tested Python dependencies.

Watch the actual exports: [AI scenery](docs/previews/ai-scenery.mp4), [vector explorer](docs/previews/explorer.mp4), [Blender scene](docs/previews/orbital3d.mp4), [reproduced basketball](docs/previews/basketball-reproduced.mp4).

## Existing model and training

- [legacy/basketball_quality_v4](legacy/basketball_quality_v4): original supplied scripts, small numeric neural checkpoints, AI reference images, guides and logs. Reproduced a 180-frame basketball scene using `draw_and_animate.py` from five checkpoints.
- [legacy/basketball_4k_upgrade](legacy/basketball_4k_upgrade): original upscaling sources, assets and FSRCNN model/license. Its upscaling scripts require **OpenCV contrib** (`cv2.dnn_superres`); the default research extra installs headless core OpenCV and does not enable them. Existing 4K media is preserved in Drive. This optional pipeline was not rerun.
- [training/train_stroke_policy.py](training/train_stroke_policy.py): newly trained, bounded supervised curve experiment with disjoint train/validation/test control polygons. [Results](reports/stroke-training.json) include the exact mathematical baseline. The small neural model is not a general artist and is not used by default.
- [training/ROADMAP.md](training/ROADMAP.md): staged goals and the requirements for real drawing-policy training and later RL.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python legacy/basketball_quality_v4/draw_and_animate.py "$PWD/output/basketball"
OPENBLAS_NUM_THREADS=1 python training/train_stroke_policy.py --output output/stroke-training --epochs 160
python -m pytest -q
```

## Drive migration

All **13 files** were downloaded and hashed; the study ZIP contains **185 videos** and passed CRC verification. [migration/drive_manifest.json](migration/drive_manifest.json) records exact file IDs, sizes and SHA-256 checksums. Downloaded originals are in `/workspace/drawing-data/drive`; extracted archives are beside them outside Git.

User project source, checkpoints, small source art, notes and reproducible examples are stored here. Third-party study videos, thumbnails/contact sheets and serialized classifier binaries remain outside Git; this repository includes provenance and restoration instructions rather than publicly republishing those files. Cookies were not needed or read, and are excluded from Git.

```bash
python scripts/migrate_drive.py --output /workspace/drawing-data/drive --extract
```

Direct YouTube requests were rejected by the environment proxy. The reference catalog records those links as unreviewed. Reviewing samples from the Drive study archive is not the same as watching every reference or obtaining training rights.

See [docs/USAGE.md](docs/USAGE.md) for the scene/edit formats, [reports/VALIDATION.md](reports/VALIDATION.md) for evidence and limits, and [references/REFERENCE_CATALOG.json](references/REFERENCE_CATALOG.json) for the user's ranked targets.

## Attribution

The recovered project materials came from the user's supplied Drive folder. FSRCNN's supplied license is retained in its directory. External tools retain their own licenses. The uploaded agent prompt is preserved as **reference text**, not installed as repository policy. Third-party study material is not a grant to redistribute or train. No new license is asserted over recovered or third-party material.
