# Development and learning goals

The target is useful, reproducible animation assistance across drawing, composition, 2D, 3D and editing—not a claim of universal generated artistry.

| Area | Current evidence | Remaining work |
|---|---|---|
| Agent onboarding | Canonical director contract, task skills, packaged MCP resources, bootstrap/doctor | Keep docs aligned with schemas as tools evolve |
| Drawing / 2D | Editable vector/cut-out moonlight example, stroke reveal, parallax, frame-token regressions | Richer pose/deformation tools and original inbetween workflows |
| Composition / edit | Staged shots, camera keys, captions, music and multi-engine assembly | Dissolves, ducking, richer compositing and platform-specific review |
| Narration / reactions | Synthetic speech, pinned Whisper path, narrow intent classifier, timed cue examples | Broader authorized assets/languages and better editorial evaluation |
| 3D / rigging | Editable primitive/preset scenes, weighted humanoid, IK/contact/payload QA | Arbitrary mesh pipelines, facial rigs, cloth/fluids and advanced acting |
| General learned drawing | No general policy established | Requires authorized stroke/action data, disjoint-subject evaluation and a suitable model |

## What is actually trained here

`train_stroke_policy.py` learns points along supplied procedural Bezier controls. Whole control polygons are disjoint between splits; exact analytic interpolation remains the better production default. The packaged numeric checkpoint is `src/animation_mcp/models/stroke_policy.npz`; the former duplicate under `training/checkpoints/` was removed.

`train_reactions.py` trains a small English editorial-intent classifier on original synthetic sentences with a fixed hand-authored holdout. It exports safe JSON/NumPy data, not pickle. Its score is not calibrated general reasoning. New experiment reports go to `output/research/`, not the historical validation report.

CLIP and Whisper are pretrained upstream models reused unchanged. Scanning references, writing lessons and connecting MCP do not train the host agent.

## Next meaningful experiment

Define an editable action vocabulary and collect original/authorized drawing histories with aligned descriptions. Split by subject and creator, not adjacent frames. Compare against exact geometry, retrieval and code-authoring baselines on unfamiliar subjects. Measure recognizability, perspective, brief match, stroke economy and temporal consistency with human review. Only consider RL after a supervised baseline and meaningful reward/evaluation design exist.

No general drawing architecture, authorized action corpus or GPU training run is established by this repository. Historical basketball/NothingxArt notes are archived context, not current capability claims.
