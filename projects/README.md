# Your animation projects

Create `projects/<name>/` for brief, shot plan, original/supplied assets, editable scenes, edit decisions and review notes. Keep regenerable renders in `output/<name>/`.

Do not store the only editable source in a temporary render folder. Record asset provenance and use versioned scene filenames. Large local media and outputs are ignored by the repository's existing rules; deliberately add only source/evidence you intend to share and have rights to publish.

Start from `templates/brief.md` and the relevant `skills/*/SKILL.md`, or scaffold a starting structure without overwriting:

```bash
.venv/bin/animation-studio new <slug> --brief "Viewer takeaway and constraints" --engine 2d
```

This creates `brief.md`, `shot-plan.json`, `scenes/`, `assets/PROVENANCE.md` and `review.md`. The included scene is a proof, not a finished film; edit it, preview storytelling frames, then render into `output/<slug>/`.
