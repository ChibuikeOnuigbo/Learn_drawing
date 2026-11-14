#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Each cloud task is isolated. Use this checkout; do not create a worktree.
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps -e .
command -v ffmpeg >/dev/null
command -v ffprobe >/dev/null
if ! command -v blender >/dev/null; then
  echo 'Install Blender 4.3+ separately to enable 3D tools.' >&2
fi
.venv/bin/python -m pytest -q
