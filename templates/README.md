# Starter templates

- `brief.md`, `review.md`: copy into `projects/<name>/` and fill in.
- `scene-2d.json`: self-contained 1-second bouncing-ball proof; render directly.
- `scene-3d.json`: self-contained 1-second Blender proof; requires Blender.
- `edit.json`: decision-list example. Its paths intentionally refer to the two proof outputs below; render them first or replace the paths. Schema validation does not check media existence.
- `scene-vertical.json`: portrait-safe 540×960 bounce/title proof; render directly.
- `shot-plan.json`: example half-open shot intervals and review frames; replace with your beats.
- `exposure-sheet.json`: example twos exposure/dope sheet; schedules drawings, not poses.
- `palette.json`: example role palette with measured contrast; adjust roles before adding detail.

One-command scaffold (does not overwrite an existing project):

```bash
.venv/bin/animation-studio new my-film --brief "A 7-second proof about weight" --engine 2d
.venv/bin/animation-studio new my-solid --engine 3d --width 640 --height 360
```

MCP hosts can call `create_project`. Planning helpers `plan_shots`, `color_palette` and `timing_sheet` generate the same structures as the planning templates.

From the repository root after bootstrap:

```bash
.venv/bin/animation-studio render templates/scene-2d.json --output output/template-2d-proof --workspace .
.venv/bin/animation-studio render templates/scene-vertical.json --output output/template-vertical-proof --workspace .
.venv/bin/animation-studio render3d templates/scene-3d.json --output output/template-3d-proof
# After both exist, load edit.json and pass its object to assemble_video,
# or call animation_mcp.edit.edit_video(spec, Path('output/edit-proof'), Path('.')).
```

On Windows use `.venv\\Scripts\\animation-studio.exe`. Templates are also packaged as `animation_mcp.templates` resources; they are starting points, not finished films.
