# Changelog

## 0.5.0 — deeper creative playbooks, planning tools and rendered starters

### Verified
- Full suite: 50 passed, 1 skipped (CLIP weights not fetched), with verified Whisper cache and real Blender rig regression.
- `animation-studio doctor --smoke-3d`: 16 readable playbooks, expanded template checks, real 2D and 3D smoke proofs.
- Five new examples rendered and frame-inspected: kinetic typography, 2D walk cycle, particle burst, vertical Short and narrated explainer. Scaffolded 2D/3D projects and the portrait template also rendered successfully.

### Added
- Seven portable skills: storyboarding/animatics, color & lighting, motion graphics/kinetic typography, physics & secondary motion, sound design, reference analysis and platform delivery. The catalog now contains 16 playbooks.
- Deterministic MCP/Python pre-production helpers: `plan_shots` (exact half-open frame grid), `color_palette` (role colors + measured contrast), `timing_sheet` (exposure/dope schedule).
- No-overwrite project scaffolder: CLI `animation-studio new <slug>` and MCP `create_project`, with brief, shot plan, starter scene, asset provenance and review form.
- Starter/planning templates: `scene-vertical.json`, `shot-plan.json`, `exposure-sheet.json`, `palette.json`.
- `scripts/build_skill_examples.py` and examples 05–09 with editable source, real exports and measured QA.
- `tests/test_expansion.py` plus MCP assertions for the new planning/scaffold tools.

### Changed
- Director skill, AGENTS, README, connect/usage/architecture docs, skill/template indexes and doctor now route to the expanded library and planning tools.
- Scaffolder restages portrait/landscape starters without distorting shape aspect ratios and retimes keys onto the requested frame grid without duplicate indices.
- Narrated explainer captions are non-overlapping and cuts follow sentence-level engine word events; redundant shot notes that collided with captions were removed.

### Limits
- Planning helpers are deterministic schedules/color math, not forced alignment, generative art or artistic acceptance.
- The particle burst is authored keyframes, not a physics simulator. The explainer voice is offline synthetic demo speech, not a human narrator.

## 0.4.0 — agent-ready repository structure

### Verified
- Full suite: 40 passed, 1 skipped (CLIP weights not fetched), with verified Whisper cache and real Blender rig regression.
- Cross-platform bootstrap exercised with real 2D/3D smoke proofs; wheel contains all nine skills/templates and reads correctly from a separate installed venv.
- Starter 2D/3D/edit templates rendered/assembled successfully; see `reports/AGENT_KIT_VALIDATION.md`.

### Added
- Root `AGENTS.md` entry point; thin Claude/Copilot pointers rather than competing rulebooks.
- Nine portable `skills/*/SKILL.md` playbooks: director, drawing, composition, 2D, 3D, rigging, editing, reactions and QA; machine-readable router.
- Packaged MCP skill resources (`studio://workflow`, `studio://skills`, `studio://skills/{name}`), `get_skill` and `check_environment` tools.
- Cross-platform `scripts/bootstrap.py`, compatibility shell wrappers, and CLI `doctor` with optional real 2D/3D smoke renders and JSON reporting.
- Validated starter 2D/3D/edit templates plus brief/review forms; `projects/` source convention and connection/architecture guides.
- Agent-kit regressions for catalog/frontmatter, links, templates, missing engines, invalid Blender override, CLI smoke and MCP resource access.

### Changed
- README is now a mode-aware quickstart with the skill map and actual evidence links.
- Historical reference notes moved to `references/archive/`; download manifests to `references/manifests/`. Optional research scripts live under `scripts/research/`.
- Optional caches default to `.work/models/` in generated client config; research extra now declares PyAV directly instead of the retired OpenCV sampler dependency.
- CI runs the real doctor smoke check before pytest and includes the working branch pattern.
- Linux/CI lock regenerated from the core+test environment; sandbox-only imageio-ffmpeg and stale optional dependencies excluded.

### Removed
- Duplicate `src/animation_mcp/WORKFLOW.md`; the director skill is the single canonical contract for repository and MCP readers.
- Seven superseded generators/samplers targeting deleted `exmapels/` paths, the empty root `migration/` folder, and a duplicate stroke checkpoint. Git history preserves prior work.

## 0.3.0 — reference-informed rebuild

### Changed
- Replaced CairoSVG/cairocffi with `resvg-py` and bundled Inter/Space Grotesk fonts; 2D rendering no longer needs system Cairo.
- Reaction `brain_wipe` now uses the verified Squidward brain-erasing GIF, cropped only to remove blank source canvas. Cue lands after the verbal setup “No brain(s) at all”.
- 3D presets are art-directed editable exercises (bounce, wave, walk, reach/grasp) with modeled sets, materials, lighting, camera moves and rig QA. Difficulty labels are not claims of reference-film parity.
- Blender subprocess timeout is configurable (`ANIMATION_BLENDER_TIMEOUT`, default 3600s); worker can resume interrupted frame sequences (`ANIMATION_RESUME=1`).
- MCP config template uses portable relative workspace; `scripts/configure_client.py` emits absolute client config.

### Added
- `scripts/analyze_drive.py`: PyAV/libdav1d dense reference scanner (2,805 samples across 55 supplied files; adjacent-frame change measurements for short files).
- `references/DRIVE_SCAN.json`, `references/STUDY_REBUILD.md`: honest provenance and reviewed observations.
- `examples/`: 2D moonlight rig, semantic reaction tests, four editable 3D exercises, asset-based multi-shot edit.
- `character.py`, `cinematic.py`, `blender_launcher.py`: nested vector character, authored Blender sets, trusted isolated-Blender launcher.
- Regression tests for frame-token image sequences and layered character poses.

### Removed
- Weak/typo legacy surfaces: `exmapels/`, `legacy/`, old `reports/`, old preview videos, old example scenes, unrelated sleeping-brain still.
- `yt-dlp` optional dependency; the rebuild does not download YouTube videos.
- `bpy` from the project venv (kept isolated due NumPy conflict).

### Verified
- Full pytest: 33 passed, 1 skipped (CLIP model not fetched), 1 benign pydantic warning.
- Reaction exports: technical/timing pass, audio present, cue rounding ≤ half frame.
- Simple/medium/hard rig QA: 15 bones, 5,994 weighted vertices, 4 IK chains, foot floor contact and IK target error within thresholds; hard payload hold error 0.
- All example exports pass technical checks; see `reports/REBUILD_VALIDATION.md`.
