#!/usr/bin/env python3
"""Cross-platform bootstrap: venv + toolkit + real 2D self-check; no model downloads."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locked", action="store_true", help="Use the Linux/CI requirements.lock instead of resolving extras")
    parser.add_argument("--smoke-3d", action="store_true", help="Also require Blender and prove a tiny 3D render")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        print("Python 3.11+ is required; run this script with a newer interpreter.", file=sys.stderr)
        return 1
    venv = ROOT / ".venv"
    python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    # Reuse only a compatible existing venv; never delete user files.
    subprocess.run([str(python), "-c", "import sys; assert sys.version_info >= (3,11)"], check=True)
    subprocess.run([str(python), "-m", "pip", "install", "--upgrade", "pip"], check=True)
    if args.locked:
        subprocess.run([str(python), "-m", "pip", "install", "-r", "requirements.lock"], cwd=ROOT, check=True)
        subprocess.run([str(python), "-m", "pip", "install", "--no-deps", "-e", "."], cwd=ROOT, check=True)
    else:
        subprocess.run([str(python), "-m", "pip", "install", "-e", ".[test]"], cwd=ROOT, check=True)
    command = [str(python), "-m", "animation_mcp.cli", "doctor", "--smoke"]
    if args.smoke_3d:
        command.append("--smoke-3d")
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        print("Bootstrap incomplete. Fix the failed checks and re-run; no models were downloaded.", file=sys.stderr)
        return result.returncode
    print(f"\nReady. Interpreter: {python}")
    print("Connect: " + str(python) + " scripts/configure_client.py --output output/mcp-client.json")
    print("Read AGENTS.md and docs/CONNECT.md. FFmpeg/ffprobe are required; Blender enables 3D.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
