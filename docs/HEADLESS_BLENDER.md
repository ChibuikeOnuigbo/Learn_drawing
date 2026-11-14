# Headless Blender / bpy notes

Prefer a normal Blender 4.5+ executable on `PATH`, or set `ANIMATION_BLENDER` to its absolute path. The server runs the trusted `blender_launcher.py` against validated scene JSON; clients cannot supply arbitrary executable Blender code.

## Isolated sandbox fallback

In a headless Linux sandbox without system Blender/package-manager access, a separate `bpy` environment can work:

1. Keep the project venv on NumPy 2.x. **Do not install `bpy` into it.**
2. Create `.tools/blender-env` with `bpy==4.5.0`, `numpy<2` and the worker's Pydantic dependency.
3. Collect the real X/GL shared libraries required by that wheel into `.tools/lib`. In the verified rebuild, the `eXtern-OS/eXternOS-Base` repository's `squashfs-root/usr/lib/x86_64-linux-gnu/` supplied Xrender, Xfixes, Xi, SM, ICE, GL, GLdispatch, GLX, X11, Xau, Xdmcp, X11-xcb and xkbcommon. Preserve SONAME symlinks. These are sandbox workarounds, not project dependencies; verify their origin and suitability for your environment.
4. Add an executable wrapper at `.tools/bin/blender` and either put that directory on `PATH` or set `ANIMATION_BLENDER` to the wrapper.

The studio invokes this fixed shape:

```text
blender --background --threads 2 --python <launcher.py> -- <worker.py> <scene.json> <output>
```

A wrapper for that shape must drop Blender-only flags before `--python`, then exec the isolated Python with the launcher and everything after it. Example:

```bash
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
export LD_LIBRARY_PATH="$root/.tools/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export OPENBLAS_NUM_THREADS=1
if [[ "${1:-}" == "--version" ]]; then
  exec "$root/.tools/blender-env/bin/python" -c 'import bpy; print("Blender", bpy.app.version_string)'
fi
while (($#)); do
  case "$1" in
    --python) shift; exec "$root/.tools/blender-env/bin/python" "$@" ;;
    *) shift ;;
  esac
done
echo 'Expected --python <launcher> -- <worker> <scene> <output>' >&2
exit 2
```

This wrapper is intentionally narrow; it is not a general replacement for the Blender CLI. `.tools/` is ignored and may disappear after a sandbox reset. Rebuild it rather than assuming an old process or wrapper survived.

## Verify and run

```bash
.venv/bin/animation-studio doctor --smoke-3d
.venv/bin/animation-studio render3d templates/scene-3d.json --output output/template-3d-proof
```

`ANIMATION_BLENDER_TIMEOUT` (seconds, default 3600) controls the subprocess limit. `ANIMATION_RESUME=1` lets the worker skip existing frame PNGs when resuming an **unchanged** example build; changed scenes/settings need a fresh output directory.

The fallback was exercised with real 2D/3D doctor proofs and the humanoid rig regression. A configured executable alone is not a render proof, and neither proof is artistic acceptance.
