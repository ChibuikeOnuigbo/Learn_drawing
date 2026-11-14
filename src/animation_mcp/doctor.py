"""Offline readiness checks. Never install software, fetch models or claim artistic QA."""
from __future__ import annotations

import importlib.metadata
import importlib.resources
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REQUIRED_DISTRIBUTIONS = (
    "mcp", "pydantic", "Pillow", "resvg-py", "numpy", "scikit-learn",
    "espeakng-loader", "faster-whisper",
)


def resolve_command(name: str) -> str | None:
    """Resolve a PATH command or an explicit executable path without running it."""
    value = os.environ.get("ANIMATION_BLENDER") if name == "blender" else None
    if value:
        path = Path(value).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
        return shutil.which(value)
    return shutil.which(name)


def _check(checks: list[dict], name: str, status: str, detail: str) -> None:
    checks.append({"name": name, "status": status, "detail": detail})


def _version(command: str, executable: str) -> str:
    flag = "--version" if command == "blender" else "-version"
    result = subprocess.run([executable, flag], capture_output=True, text=True,
                            timeout=30, check=True)
    return (result.stdout or result.stderr).splitlines()[0][:240]


def run_checks(smoke: bool = False, smoke_3d: bool = False, workspace: Path | None = None) -> dict:
    """Return required/optional readiness, optionally proving a tiny real render.

    Blender absence is optional unless --smoke-3d explicitly requests a 3D proof.
    Smoke outputs are temporary and removed; this is an environment test, not a deliverable.
    """
    checks: list[dict] = []
    supported = sys.version_info >= (3, 11)
    _check(checks, "python", "pass" if supported else "fail", sys.version.split()[0])
    for distribution in REQUIRED_DISTRIBUTIONS:
        try:
            version = importlib.metadata.version(distribution)
            _check(checks, f"package:{distribution}", "pass", version)
        except importlib.metadata.PackageNotFoundError:
            _check(checks, f"package:{distribution}", "fail", "not installed; run scripts/bootstrap.py")

    engines = {}
    for name in ("ffmpeg", "ffprobe", "blender"):
        executable = resolve_command(name)
        engines[name] = executable
        if not executable:
            required = name != "blender" or smoke_3d
            detail = ("not configured; 3D disabled (see docs/HEADLESS_BLENDER.md)" if name == "blender"
                      else "not found on PATH; install FFmpeg including ffprobe")
            if name == "blender" and os.environ.get("ANIMATION_BLENDER"):
                detail = "ANIMATION_BLENDER is not an executable or resolvable command"
                required = True
            _check(checks, f"engine:{name}", "fail" if required else "warn", detail)
            continue
        try:
            _check(checks, f"engine:{name}", "pass", f"{executable} — {_version(name, executable)}")
        except (OSError, subprocess.SubprocessError) as exc:
            required = name != "blender" or smoke_3d
            _check(checks, f"engine:{name}", "fail" if required else "warn", str(exc))

    root = Path(workspace) if workspace is not None else Path(os.environ.get("ANIMATION_WORKSPACE", Path.cwd()))
    root = root.resolve()
    try:
        if not root.is_dir():
            raise FileNotFoundError(f"Workspace does not exist: {root}")
        with tempfile.TemporaryFile(dir=root):
            pass
        _check(checks, "workspace", "pass", str(root))
    except OSError as exc:
        _check(checks, "workspace", "fail", str(exc))

    try:
        from .skills_index import index, read_skill
        catalog = index()
        for entry in catalog["skills"]:
            content = read_skill(entry["name"])["content"]
            if not content.startswith("---\n"):
                raise ValueError(f"Missing skill frontmatter: {entry['name']}")
        _check(checks, "skills", "pass", f"{len(catalog['skills'])} readable playbooks")
        from .scene import Scene
        from .blender_scene import Scene3D
        from .edit import Edit
        templates = importlib.resources.files("animation_mcp.templates")
        Scene.model_validate(json.loads(templates.joinpath("scene-2d.json").read_text(encoding="utf-8")))
        Scene3D.model_validate(json.loads(templates.joinpath("scene-3d.json").read_text(encoding="utf-8")))
        Edit.model_validate(json.loads(templates.joinpath("edit.json").read_text(encoding="utf-8")))
        _check(checks, "templates", "pass", "2D, 3D and edit templates validate")
    except Exception as exc:
        _check(checks, "agent-package", "fail", f"{type(exc).__name__}: {exc}")

    # Presence is useful routing information, not a checksum or quality claim.
    from .asr import asr_cache
    from .semantic import model_cache
    optional = {
        "whisper_files_present": (asr_cache() / "model.bin").is_file(),
        "clip_files_present": all((model_cache() / kind / "model.onnx").is_file() for kind in ("text", "vision")),
        "optional_model_integrity": "not checked by doctor; preparation tools verify SHA-256",
    }
    if smoke or smoke_3d:
        try:
            from .render import render
            with tempfile.TemporaryDirectory(prefix="animation-doctor-") as temporary:
                folder = Path(temporary)
                scene = folder / "scene.json"
                scene.write_text(json.dumps({"width": 64, "height": 64, "fps": 3, "frames": 3,
                    "layers": [{"id": "proof", "kind": "rect", "x": 16, "y": 32,
                                "width": 12, "height": 12, "fill": "#ff9900",
                                "tracks": [{"property": "x", "keys": [
                                    {"frame": 0, "value": 16}, {"frame": 2, "value": 48}]}]}]}))
                qa = render(scene, folder / "render", folder)
                if not (qa["technical_pass"] and qa["frames"] == 3 and qa["codec"] == "h264"):
                    raise RuntimeError(f"2D proof failed: {qa['errors']}")
            _check(checks, "smoke:2d", "pass", "3-frame SVG→H.264 render decoded and checked; temporary files removed")
        except Exception as exc:
            _check(checks, "smoke:2d", "fail", f"{type(exc).__name__}: {exc}")
    if smoke_3d:
        try:
            from .blender_scene import render_3d
            with tempfile.TemporaryDirectory(prefix="animation-doctor-3d-") as temporary:
                qa = render_3d({"width": 64, "height": 64, "fps": 2, "frames": 2, "samples": 1,
                                "objects": [{"name": "Proof", "kind": "sphere"}]}, Path(temporary) / "render")
                if not (qa["technical_pass"] and qa["frames"] == 2 and Path(qa["blend"]).is_file()):
                    raise RuntimeError(f"3D proof failed: {qa['errors']}")
            _check(checks, "smoke:3d", "pass", "2-frame Blender render and .blend verified; temporary files removed")
        except Exception as exc:
            _check(checks, "smoke:3d", "fail", f"{type(exc).__name__}: {exc}")

    failures = [c["name"] for c in checks if c["status"] == "fail"]
    return {"ok": not failures, "workspace": str(root), "engines": engines,
            "ready": {"2d": not failures, "3d": not failures and bool(engines["blender"])},
            "checks": checks, "failures": failures, "optional_models": optional,
            "scope": "Environment/template checks only; no downloads, model-weight changes or artistic evaluation."}


def format_report(report: dict) -> str:
    lines = ["Animation Studio self-check", "=" * 27]
    symbols = {"pass": "OK  ", "warn": "WARN", "fail": "FAIL"}
    lines.extend(f"[{symbols[c['status']]}] {c['name']}: {c['detail']}" for c in report["checks"])
    lines.append("")
    lines.append(f"Required checks: {'PASS' if report['ok'] else 'FAIL'}")
    lines.append("3D: " + ("configured (not render-proven)" if report["ready"]["3d"] else "unavailable or failed"))
    if any(c["name"] == "smoke:3d" and c["status"] == "pass" for c in report["checks"]):
        lines[-1] = "3D: tiny render proven"
    lines.append("Models: " + json.dumps(report["optional_models"]))
    lines.append(report["scope"])
    return "\n".join(lines)
