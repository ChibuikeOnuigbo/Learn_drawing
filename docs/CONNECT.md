# Connect an agent to the studio

There are three different levels of access. Be explicit about which one you have.

## 1. Link-only chat: methods and source guidance

Give a browsing-capable chat this repository:

<https://github.com/ChibuikeOnuigbo/Learn_drawing>

Copy this prompt:

> Read `AGENTS.md` in this repository first, then `skills/animation-director/SKILL.md`. Use `skills/index.json` to load the drawing, composition, 2D, 3D, rigging, editing, reaction, QA, storyboarding, color/lighting, motion-graphics, physics/secondary-motion, sound, reference-analysis and platform-delivery playbooks relevant to my request. Check which tools you actually have. Help me design and author editable animation source; do not claim rendering or playback unless you actually performed it. My project is: …

A chat that cannot browse should ask you to paste/upload those files. A GitHub URL does not automatically grant repository access, install plugins or change model weights. If the default branch has not yet received this structure, use the active working branch or the merged commit containing `AGENTS.md`.

This mode can produce briefs, critiques, drawings through the host's own tools, SVG/JSON scenes and edit plans. It cannot use local engines unless the host also provides execution/MCP access.

## 2. Repository-aware coding agent

The root `AGENTS.md` is the canonical entry point. `CLAUDE.md` imports it; `.github/copilot-instructions.md` points to it. Other agents should be instructed to read it explicitly.

After cloning/opening the checkout, with installation authorized:

```bash
python3 scripts/bootstrap.py
# POSIX alternative: bash scripts/bootstrap.sh
# Include a real tiny Blender proof when Blender is installed:
python3 scripts/bootstrap.py --smoke-3d
```

Windows: use `py -3 scripts/bootstrap.py` and `.venv\\Scripts\\` executables. Bootstrap creates/reuses `.venv`, installs the toolkit and runs a real 2D encode/decode self-check. It does not download models, corpora or Blender. FFmpeg **and ffprobe** must be installed separately; Blender 4.5+ enables 3D.

The default bootstrap resolves `.[test]`. For the tested Linux/CI dependency set use `--locked`; the lock is not a cross-OS guarantee. Re-run after engine installation:

```bash
.venv/bin/animation-studio doctor --smoke
.venv/bin/animation-studio doctor --smoke-3d --json
```

Exit code is nonzero when required checks fail. Missing Blender alone is a warning unless a 3D proof was requested. Model file presence is reported separately from checksum verification.

## 3. MCP host: actual local production tools

Generate a concrete configuration using the bootstrap interpreter:

```bash
.venv/bin/python scripts/configure_client.py --output output/mcp-client.json
```

The generated `mcpServers` entry uses an absolute interpreter path, absolute workspace and local model-cache paths. Import that entry into the client's MCP configuration format. `.mcp.json` is a portable template for hosts that support it; its `python` command requires the correct environment to be active. Client configuration schemas differ—do not assume every chat accepts the same file.

Equivalent server command:

```bash
ANIMATION_WORKSPACE=/absolute/project/workspace .venv/bin/python -m animation_mcp.server
```

The server uses stdio. Do not wrap it in a web server or pollute protocol stdout with logs. Restart/reconnect after a sandbox reset; background processes and ignored tool directories may not survive.

First calls/resources:

1. `capabilities`
2. `check_environment` (or `check_environment(smoke=true)` for a tiny real proof)
3. `studio://workflow` / `get_skill("animation-director")`
4. `studio://skills` / `studio://skills/{name}`
5. `get_scene_schema(kind="2d"|"3d"|"edit")`
6. `get_model_catalog`
7. `produce_video` prompt with the user's brief

The 16 playbooks and starter/planning templates are packaged with the server, not read from an uncertain client cwd. `studio://workflow` returns the same director skill stored in the repository. Pre-production tools include `plan_shots`, `color_palette`, `timing_sheet` and `create_project`.

## Engines, caches and boundaries

| Variable | Meaning |
|---|---|
| `ANIMATION_WORKSPACE` | Asset/project root; MCP paths must stay inside it |
| `ANIMATION_BLENDER` | Executable/command or wrapper override |
| `ANIMATION_BLENDER_TIMEOUT` | Subprocess seconds; default 3600 |
| `ANIMATION_RESUME` | `1` reuses unchanged example frame sequences |
| `ANIMATION_ASR_CACHE` | Whisper cache; preparation verifies checksums |
| `ANIMATION_MODEL_CACHE` | CLIP cache; preparation verifies checksums |

Generated client configs point optional caches at `.work/models/`. Bootstrap does not fetch them. Use `prepare_voiceover_model` / `prepare_reference_models` explicitly when needed and permitted.

For headless Blender, see [HEADLESS_BLENDER.md](HEADLESS_BLENDER.md). Keep bpy out of the project venv. For schemas and examples see [USAGE.md](USAGE.md) and [../examples/README.md](../examples/README.md).

Connecting provides methods and tools; it does not supply a universal text-to-video model, arbitrary auto-rigging or automatic artistic approval.
