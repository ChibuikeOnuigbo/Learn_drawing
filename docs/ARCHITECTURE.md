# Repository architecture

## Instruction layer

`AGENTS.md` is the short repository entry point. `skills/animation-director/SKILL.md` is the single detailed operating contract; `skills/index.json` routes to 16 task playbooks. Client-specific files point back instead of duplicating rules.

Setuptools maps root `skills/` and `templates/` into the installed package as `animation_mcp.skills` and `animation_mcp.templates`. `skills_index.py` reads only catalog-listed resources. MCP exposes the same contract through `studio://workflow`, `studio://skills`, `studio://skills/{name}` and `get_skill`.

The former `src/animation_mcp/WORKFLOW.md` duplicate was removed. Update the director skill once; repository and MCP readers then receive the same guidance.

## Production layer

```text
brief/shot plan
  ├─ production.py (shot grid, palette/contrast, exposure sheet)
  ├─ deformation.py (fixed-topology mesh warp, fold checks, whole-image reveal)
  ├─ cloth.py (2D PBD distance-constraint curtain panel)
  ├─ eye_rig.py (traced-aperture blink with outside-box identity)
  ├─ scaffold.py (no-overwrite project starter from packaged templates)
  ├─ scene.py → render.py (resvg SVG/raster → FFmpeg → inspect)
  ├─ blender_scene.py → trusted launcher → blender_worker / rig_worker / cinematic
  ├─ edit.py (local clips → captions + final audio → inspect)
  ├─ speech/asr → reactions.py (reviewed intent + word cues → composite)
  ├─ tracing.py (per-frame PyAV decode → LK tracks/contours → chunked NPZ + catalog)
  ├─ styles.py / planner.py (measured+reviewed style catalog, seeded scene plan)
  └─ procedural.py (deterministic assets/overlay loops) → composite_scene → render
                         ↓
                 video + editable source + measured QA
```

- `server.py`: stdio MCP surface, workspace confinement and packaged guidance.
- `cli.py`: local render/render3d/inspect plus `new` and `doctor` subcommands.
- `production.py`, `scaffold.py`: deterministic pre-production helpers and project scaffolding; planning output is not artistic acceptance.
- `deformation.py`: traced-control mesh warps and one-mask character reveals used by `scripts/build_drive_recreations.py`; geometry checks are not artistic approval.
- `cloth.py`: position-based distance constraints with pins/seam collision and reported strain/projection; 2D gathering approximation, not 3D cloth.
- `eye_rig.py`: per-column lid closure over a traced aperture; lid skin is a labelled estimate and pixels outside the eye neighbourhood stay bit-identical.
- `doctor.py`: offline package/engine/template checks and optional tiny real renders; no downloads.
- `scene.py`, `blender_scene.py`, `edit.py`: strict current schemas and budget guards.
- `character.py`, `cinematic.py`, `presets.py`: original example art/staging, not general generators.
- `blender_launcher.py`: trusted repository worker entry; scene JSON is not executable code.
- `semantic.py`, `asr.py`: pinned pretrained retrieval/ASR with explicit preparation and checksums.
- `reactions.py`: transparent phrase-rule intent selection plus editorial/timing guards.
- `tracing.py`: every-frame index, sparse forward/backward optical-flow tracks, simplified contours, shot-cut candidates, confirmed insert exclusions and local template-hash origin matching. Unknown origins stay unknown.
- `styles.py`, `planner.py`, `procedural.py`: style catalog, seeded concept planning/image briefs, code-generated assets and depth-layer compositing. These are planning/geometry aids, not generative art models.

## Evidence and source layer

`examples/` contains actual source, exports and inspection evidence. `references/` separates the current measured scan from historical archives/manifests. `reports/` contains validation evidence and production lessons; no project-trained weights are bundled. `reports/REBUILD_VALIDATION.md` records a specific historical run, not automatic approval of future work.

`projects/` is for new editable user work; `output/` is ignored regenerable material. Local corpora, models, Blender fallback tools and scratch boards stay in ignored directories. The repository does not require the 2.2 GB Drive mirror to run its core tools.

## Maintenance rules

1. Change schemas and tests together; update the affected skill and usage example.
2. Keep one canonical operating contract; do not revive per-client copies.
3. Add a skill to both its directory and `index.json`; package/link tests must pass.
4. Keep historical claims scoped to their evidence and date.
5. Run bootstrap/doctor, pytest and a relevant proof before reporting readiness.
