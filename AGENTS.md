# Agent entry point

This repository is an animation production kit: reusable creative methods, strict editable scene formats, local render/edit tools, MCP access and verified examples.

## Start here, in order

1. Read [skills/animation-director/SKILL.md](skills/animation-director/SKILL.md) — the single operating contract.
2. Use [skills/index.json](skills/index.json) to load only the relevant drawing, composition, 2D, 3D, rigging, editing, reaction, QA, storyboarding, color/lighting, motion-graphics, physics/secondary-motion, sound, reference-analysis and platform-delivery playbooks.
3. Check the actual environment: `python -m animation_mcp.cli doctor` after installation, or MCP `capabilities` / `check_environment`.
4. Inspect the closest [example](examples/README.md) and current schema before authoring. Use [templates](templates/README.md) for new work.

If you are connected over MCP, `studio://workflow` returns the operating contract, `studio://skills` lists the library, and `get_skill` reads a playbook. If you only have a repository link, read these files directly. A link does not grant tools or change model weights.

## Non-negotiable rules

- Produce actual artifacts when authorized and equipped; otherwise state the guidance/source-only mode.
- Brief → design/block → preview → animate → render → inspect → revise → deliver.
- Keep editable source, asset provenance and QA with the video. New source belongs in `projects/`; regenerable output belongs in `output/`.
- Use current schemas and relative workspace paths. Never invent unsupported tool arguments or send arbitrary executable code through MCP.
- Separate technical checks from visual review and artistic acceptance. Never fabricate playback, listening, training or reference parity.
- Preserve user assets and known-good sources. Do not commit caches, credentials, local corpora or bulky intermediates.
- Third-party reaction GIFs are local tests, not cleared publication assets.

## Repository map

| Path | Purpose |
|---|---|
| `skills/` | Canonical task playbooks and router |
| `templates/` | Validated starter scenes and brief/review forms |
| `src/animation_mcp/` | Server, schemas, engines and packaged resources |
| `examples/` | Real rendered skill tests with source and QA |
| `scripts/` | Bootstrap, client config, showcase; research utilities below |
| `docs/` | Connection, usage, architecture and headless setup |
| `references/` | Current scan evidence; historical material under `archive/` |
| `training/` | Narrow reproducible experiments and evidence-linked lessons |
| `tests/`, `reports/` | Regressions and measured validation |

 Historical notes do not override the operating contract or current code. When docs and schema disagree, inspect the schema/code, fix the documentation, and report the discrepancy.
