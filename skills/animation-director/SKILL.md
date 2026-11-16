---
name: animation-director
description: Turn an animation idea into an executable production plan; route drawing, composition, 2D, 3D, rigging, editing, reactions and review work.
---

# Animation director — the operating contract

Use this skill first. The repository gives an agent reusable methods, exact scene formats, local tools and verified examples. It does not change model weights or make an unavailable engine available.

## 1. Establish what is actually available

Read the root `AGENTS.md`, then `skills/index.json`. Load only the playbooks needed for the request. In an MCP host, call `capabilities`, `get_model_catalog`, and `get_scene_schema` for the intended format. Without MCP, inspect the source and run `python scripts/bootstrap.py` if installation is authorized.

Choose one working mode and state it:

- **Guidance:** critique supplied drawings, write a shot plan, or author editable scene JSON. No render is claimed.
- **Local production:** use the CLI or Python API to create, render and inspect actual files.
- **Connected production:** use the studio's MCP tools, keeping all asset paths inside `ANIMATION_WORKSPACE`.

A linked chat may need permission to browse the repository. A URL alone does not install FFmpeg, Blender, Python packages or MCP access. If files cannot be read, ask for `AGENTS.md` and the relevant skill rather than inventing their contents.

## 2. Write a small, concrete brief

Use `templates/brief.md`. Record the viewer's takeaway, audience, duration, aspect ratio, style, supplied assets, dialogue, deadline/compute limits and acceptance conditions. Ask only about decisions that materially change the work; otherwise label sensible defaults.

Default to a short proof shot before a long film. For example: 3 seconds, 320×180, 24 fps; prove the pose, action and camera before increasing resolution. Keep the user's chosen duration and style even when the preview is smaller.

## 3. Route the work

| Need | Read | Main tools |
|---|---|---|
| Recognizable drawing, construction, layered artwork | [drawing](../drawing/SKILL.md) | `concept_brief`, `curve_points`, `save_scene`, `preview_frame` |
| Focal point, staging, camera, continuity | [composition](../composition/SKILL.md) | `preview_frame`, `render_3d_scene`, `inspect_video` |
| Vector animation, cut-out character, animatic, explainer | [2d-animation](../2d-animation/SKILL.md) | `save_scene`, `preview_frame`, `render_scene` |
| Modeled primitive scene or staged Blender exercise | [3d-animation](../3d-animation/SKILL.md) | `get_scene_schema`, `render_3d_scene`, `render_3d_exercise` |
| Humanoid motion, hand/foot controls, prop contact | [character-rigging](../character-rigging/SKILL.md) | `render_3d_exercise`, `render_3d_scene` |
| Assemble shots, captions, narration or music | [video-editing](../video-editing/SKILL.md) | `assemble_video`, `synthesize_narration`, `transcribe_voiceover` |
| A reaction gag at a spoken beat | [reaction-timing](../reaction-timing/SKILL.md) | `select_reaction`, `plan_reaction_cues`, `render_reaction_video` |
| Decide whether the output is acceptable | [quality-review](../quality-review/SKILL.md) | `inspect_video`, returned QA, `record_lesson` |
| Beats, animatic, shot grid, exposure sheet | [storyboarding](../storyboarding/SKILL.md) | `plan_shots`, `timing_sheet`, `create_project` |
| Palette, value script, light direction, contrast | [color-lighting](../color-lighting/SKILL.md) | `color_palette`, `preview_frame`, `inspect_video` |
| Kinetic type, explainer, diagram, UI-style motion | [motion-graphics](../motion-graphics/SKILL.md) | `save_scene`, `preview_frame`, `render_scene`, `assemble_video` |
| Weight, arcs, overlap, follow-through, burst | [physics-secondary-motion](../physics-secondary-motion/SKILL.md) | `timing_sheet`, `save_scene`, `render_scene`, `render_3d_exercise` |
| Narration, music/SFX spotting, sync, mix handoff | [sound-design](../sound-design/SKILL.md) | `synthesize_narration`, `transcribe_voiceover`, `assemble_video` |
| Study a supplied reference without copying | [reference-analysis](../reference-analysis/SKILL.md) | `inspect_video`, `search_reference_library`, `record_lesson` |
| Landscape/portrait/square delivery and safe areas | [platform-delivery](../platform-delivery/SKILL.md) | `assemble_video`, `inspect_video`, `create_project` |

Most requests use several skills. A narrated character explainer normally needs director → drawing/composition → 2D or 3D → editing → quality review.

## 4. Build in evidence-producing stages

1. **Beat sheet:** setup, change, payoff. Give each beat one visible action and a purpose.
2. **Shot plan:** exact start/end frames, framing, assets, sound, transitions and acceptance condition. Frame intervals are half-open: `[start, end)`. At 24 fps, frames 0–23 occupy one second.
3. **Design:** thumbnail the poses and value hierarchy; make a character/prop continuity sheet when needed.
4. **Blocking:** key storytelling poses first. Preview exact frames before adding secondary motion.
5. **Animation:** spacing, arcs, anticipation, follow-through and readable holds. Change one motion variable at a time when diagnosing a defect.
6. **Sound/edit:** use real audio durations and word events where timing matters. Word-count shot estimates are not forced alignment.
7. **Render/inspect:** small proof first, then final export. Inspect boundary frames and actual playback if the host supports it.
8. **Revise/deliver:** fix observed defects, rerender affected shots, and deliver video plus editable source, asset provenance and an honest review report.

Use `templates/review.md`. For a new folder, `animation-studio new <slug>` or MCP `create_project` lays out brief, shot plan, starter scene, asset provenance and review without overwriting. `plan_shots`, `color_palette` and `timing_sheet` produce deterministic planning structures; they do not align audio, judge harmony or create inbetweens.

Do not stop at a promising script when an authorized renderer can produce the actual result. Do not claim a render exists when only JSON was authored.

## 5. Keep projects reproducible

Suggested layout for new work:

```text
projects/<project-name>/
  brief.md
  shot-plan.json          # or shot-plan.md; exact half-open intervals
  assets/                 # supplied or original licensed sources + PROVENANCE.md
  scenes/                 # editable 2D/3D JSON and SVG
  edits/                  # edit decision JSON
  review.md
output/<project-name>/    # regenerable renders, frames, audio and QA
```

`output/` is ignored by Git. Preserve important source under `projects/`; do not hide the only editable copy in a temporary folder. Use versioned scene filenames instead of overwriting a known-good source. The MCP `save_scene` deliberately refuses an existing path.

Use relative asset paths. For CLI rendering, pass the directory containing the assets as `--workspace`. For MCP, paths are relative to `ANIMATION_WORKSPACE`, not automatically to the scene file's folder.

## 6. Respect engine boundaries

The bundled renderer supports editable vector/cut-out 2D, constrained primitive/preset 3D, a procedural humanoid, cuts/captions/audio mux and narrow reaction timing. It is not a universal text-to-video, arbitrary-mesh auto-rigger, full compositor or automatic lip-sync system.

For sculpted characters, cloth, fluid simulation, complex compositing or hand-drawn inbetweens, use the same brief/design/review method with the host's authorized tools or an external artist/application. The saved `.blend` is an editable handoff. Do not invent unsupported MCP parameters or pass arbitrary executable code through the scene server.

## 7. Learn from references without copying or overstating

`references/README.md` distinguishes current evidence from historical notes. The Drive scan contains 2,805 timestamped samples across 55 supplied videos; sampled-frame review is not watching every tutorial. CLIP retrieves sampled frames, not rigs, brush histories or a creator's process.

Extract transferable mechanics—silhouette, value grouping, spacing, coverage, prop contact—and apply them to original artwork. Confirm rights before publishing third-party assets. The bundled Squidward GIF is a local test asset, not a cleared publication asset.

## 8. Report truthfully

Separate **implemented**, **rendered**, **technically verified**, **visually reviewed** and **artistically accepted**. No invented quality score, reference parity or full-playback claim. Record a concrete lesson only when linked to an artifact; `record_lesson` updates project memory, not neural weights.
