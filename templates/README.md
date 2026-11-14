# Starter templates

- `brief.md`, `review.md`: copy into `projects/<name>/` and fill in.
- `scene-2d.json`: self-contained 1-second bouncing-ball proof; render directly.
- `scene-3d.json`: self-contained 1-second Blender proof; requires Blender.
- `edit.json`: decision-list example. Its paths intentionally refer to the two proof outputs below; render them first or replace the paths. Schema validation does not check media existence.

From the repository root after bootstrap:

```bash
.venv/bin/animation-studio render templates/scene-2d.json --output output/template-2d-proof --workspace .
.venv/bin/animation-studio render3d templates/scene-3d.json --output output/template-3d-proof
# After both exist, load edit.json and pass its object to assemble_video,
# or call animation_mcp.edit.edit_video(spec, Path('output/edit-proof'), Path('.')).
```

On Windows use `.venv\\Scripts\\animation-studio.exe`. Templates are also packaged as `animation_mcp.templates` resources; they are starting points, not finished films.
