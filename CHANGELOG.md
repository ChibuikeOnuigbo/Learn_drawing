# Changelog

## 0.7.0 — deeper Drive studies: solved cloth, real blink, measured alignment, aura + licensed strokes

### Verified
- Curtain rebuilt as a 2D position-based distance-constraint solve at 17 Hz, exported both as a 60 fps cubic-interpolated comparison (240f) and a true 17 fps file (68f); zero inverted render triangles, solver strain/projection/fallback reported in `mesh-qa.json`.
- Eye study now ships a procedural blink from traced apertures; `max_pixel_diff_outside_eye_boxes = 0`; upper lid travels farther than lower; lid skin labelled as an estimate.
- Flashlight plates rigidly aligned from 8 hand-picked landmarks; `alignment-qa.json` reports RMSE before/after (improved) and per-landmark residuals.
- New examples 08 (aura/rain/breath, 192f) and 09 (CC0 OpenSketch stroke trace, 144f) rendered and frame-inspected; technical QA pass.
- New `tests/test_cloth_eye.py`; example regression extended to all five studies.

### Added
- `animation_mcp.cloth`: coloured Gauss-Seidel PBD distance constraints, rail/tieback pins, centre-seam collision, monotonic projection, slack-driven fold shading.
- `animation_mcp.eye_rig`: hand-traced aperture rasterisation, per-column lid closure, lashes on moving lids, smooth skin-estimate underlay, outside-box identity.
- `scripts/build_drive_recreations.py --only aura|strokes`; examples 08–09 with provenance and QA.
- `assets/open-sketch/`: one CC0 OpenSketch SVG + licence note (Gryaditskaya et al.).

### Changed
- Curtain `control_rate_hz` label now matches the actual 17 Hz solve; first-pass renders preserved under `previous-0.6/` instead of overwritten.
- Docs, provenance and validation report updated to describe solved cloth, blink scope, alignment measurement and the new studies.

### Limits
- Cloth is 2D PBD, not 3D XPBD; horizontal gathering follows hung span and fold risk falls back to a reported analytic blend. Blink lid skin is estimated, not recovered. Alignment is rigid landmark RMSE, not a structural-deviation certificate. Aura rain is evaluated continuously (not 8 Hz sampled) and the clip is not a seamless loop. OpenSketch example is product linework, not character animation.

## 0.6.0 — Drive-informed recreations replace generic starters

### Verified
- Decoded and reviewed the user's Drive curtain, eye/distortion and flashlight evidence (see `references/DRIVE_RESEARCH_DIGEST.md`); reference media stays local/ignored.
- Three new examples rendered and frame-inspected: curtain mesh (96f), eye/face performance (144f), whole-character flashlight (252f). All technical QA pass.
- Curtain mesh: zero inverted triangles in sampled frames. Flashlight: max face alpha before 4.5 s = 0, first mean face reveal > 0.5 at 4.667 s, one mask with no face gate.
- New `tests/test_deformation.py`; example regression replaced with Drive-recreation QA assertions.

### Added
- `animation_mcp.deformation`: fixed-topology piecewise-affine mesh warp with premultiplied alpha and fold/compression rejection; cubic Hermite keys with zero velocity at repeated pauses; single-mask whole-image flashlight composite.
- `scripts/build_drive_recreations.py` and examples 05–07 with original generated plates, editable rig/path JSON, provenance and QA.
- `references/DRIVE_RESEARCH_DIGEST.md`, `reports/DRIVE_RECREATION_VALIDATION.md`.

### Removed
- Generic 0.5.0 starter demos 05–09 (kinetic type, walk cycle, particle burst, vertical Short, narrated explainer) and `scripts/build_skill_examples.py`. They did not address the user's actual Drive references.

### Changed
- README, examples/scripts docs and affected skills now route to the recreation studies. Research extra includes OpenCV for the recreation builder.

### Limits
- Recreations are technique restagings with original model-assisted art, not pixel recovery of Drive videos. Curtain is a 2D warp, not cloth physics. Eye study ships no full blink after a squint prototype duplicated brow pixels. Flashlight plates are approximately matched generated characters, not authentic source frames.

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
