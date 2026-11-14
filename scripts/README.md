# Supported scripts

Run from the repository root with the bootstrap interpreter (`.venv/bin/python`, or `.venv\\Scripts\\python.exe` on Windows).

| Script | Purpose |
|---|---|
| `bootstrap.py` | Cross-platform venv/install/self-check; `--smoke-3d` also proves Blender |
| `bootstrap.sh` | POSIX wrapper; `setup.sh` remains a compatibility alias |
| `configure_client.py` | Emit an absolute-path stdio MCP client entry for this interpreter |
| `build_showcase.py` | Regenerate verified examples by stage; `--stage 3d --level hard` selects one |
| `prepare_models.py` | Explicitly download/verify optional CLIP + Whisper; large network operation |

Showcase stages: `author`, `2d`, `reactions`, `3d`, `edit`, `all`. Run `author` before `2d` when rig frames are absent. `edit` requires the source renders. Long Blender jobs should use the host's background-process mechanism.

## Optional research utilities

`research/analyze_drive.py` scans authorized local videos with PyAV; install `.[research]`. `research/migrate_drive.py` restores manifest files with checksum verification using gdown; it does not use cookies or execute downloaded code. These are not bootstrap steps.

The seven old generators targeting deleted `exmapels/` paths and the failing OpenCV reference sampler were removed. Git history preserves them; `build_showcase.py` and the current examples replace their production role.
