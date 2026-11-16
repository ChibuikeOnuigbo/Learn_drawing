# Agent-kit structure validation

Date: 2026-11-14. Scope: repository onboarding, packaged guidance, setup/self-check and starter templates. This does not re-score the artistic quality of the historical examples.

## Measured checks

| Check | Result |
|---|---|
| Full pytest with local FFmpeg/ffprobe, Blender wrapper and verified Whisper cache | **40 passed, 1 skipped**, 1 benign upstream pydantic-settings warning |
| Skip | CLIP retrieval; pinned ONNX weights not fetched |
| `scripts/bootstrap.py --smoke-3d` | PASS; real 3-frame 2D and 2-frame 3D proofs, temporary outputs removed |
| Skill catalog | 9 readable playbooks; frontmatter/index/directory consistency tested |
| MCP guidance | `studio://workflow`, `studio://skills`, `studio://skills/{name}`, `get_skill`; unknown/path-like names rejected in regression |
| Wheel | Built successfully; contains all 9 SKILL.md files, index and 3 JSON templates |
| Installed-wheel resource read | PASS from a separate venv outside the source package path |
| Starter 2D template | 24 frames, 24 fps, technical_pass=true |
| Starter 3D template | 24 frames, 24 fps, technical_pass=true, editable `.blend` produced |
| Starter edit template | 48 frames, technical_pass=true after both proof renders |
| Compileall | PASS for src, scripts, tests and training |
| Active Markdown links | Resolved by regression; historical archives excluded |
| Whisper cache restoration | All four file sizes and SHA-256 digests match the pinned manifest |

Test command:

```bash
PATH="$PWD/.tools/bin:$PATH" ANIMATION_ASR_CACHE="$PWD/.work/whisper-cache" OPENBLAS_NUM_THREADS=1 .venv/bin/pytest -q
```

The Blender wrapper and FFmpeg binaries are ignored sandbox tooling, not committed dependencies. A normal installation should use system FFmpeg/ffprobe and Blender. The lock is a tested Linux/CI core+test set; cross-platform bootstrap resolves the declared extras instead.

## Issues caught and corrected during validation

- Doctor initially used `--version` for FFmpeg/ffprobe; corrected to `-version` and proved by a real encode/decode smoke test.
- The rebuilt sandbox wrapper initially forwarded Blender-only flags to Python; corrected to the documented launcher argument shape and proved by the rig regression/3D smoke.
- Starter edit paths initially differed from the proof commands; aligned and assembled successfully.
- Blender capability/test discovery now honors the same validated `ANIMATION_BLENDER` resolution as rendering.

## Remaining boundaries

- No universal text-to-video/art model or arbitrary auto-rigging is claimed.
- Doctor checks environment/templates, not creative quality; model presence is not checksum verification.
- Historical example QA remains in `REBUILD_VALIDATION.md`; new projects need their own inspection.
- The third-party reaction GIF still requires replacement/clearance before public publication.
