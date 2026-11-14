"""Local CLI sharing the MCP engines; doctor reports real readiness."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(prog="animation-studio")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("render", "render3d", "inspect"):
        command = commands.add_parser(name)
        command.add_argument("source", type=Path)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--workspace", type=Path, default=Path.cwd())
    doctor = commands.add_parser("doctor", help="Check engines/packages/templates; optionally render tiny proofs")
    doctor.add_argument("--smoke", action="store_true", help="Render and decode a temporary 3-frame 2D proof")
    doctor.add_argument("--smoke-3d", action="store_true", help="Require Blender and render a temporary 2-frame proof")
    doctor.add_argument("--json", action="store_true", help="Emit machine-readable report")
    doctor.add_argument("--workspace", type=Path, default=None)
    args = parser.parse_args()
    if args.command == "doctor":
        from .doctor import run_checks, format_report
        report = run_checks(args.smoke, args.smoke_3d, args.workspace)
        print(json.dumps(report, indent=2) if args.json else format_report(report))
        return 0 if report["ok"] else 1
    if args.command == "render":
        from .render import render
        result = render(args.source, args.output, args.workspace)
    elif args.command == "render3d":
        from .blender_scene import render_3d
        result = render_3d(json.loads(args.source.read_text()), args.output)
    else:
        from .render import inspect
        result = inspect(args.source, args.output)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
