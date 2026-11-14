# Development and learning goals

The user's minimum target is narration-led YouTube explainers with useful drawing, tweening, composition and editing. Their preference for short composed character shots is recorded from their description of Remnant777, not inferred from watching the channel.

| Stage | Acceptance evidence | Current state |
|---|---|---|
| Drawing and local rendering | Editable original art, stroke reveals, exact frames, reproducible video | Implemented and tested |
| Layered scenery and motion | Distinct depth-layer movements; consistent hero silhouette | Basic original explorer demo |
| Narration and editing | Local voiceover, cuts, captions, correct export | Actual generated speech, supplied-audio ASR path, reaction and caption tests |
| 3D foundation | Editable scene, moving objects, real render | Primitive scenes plus weighted humanoid, IK, walk and reach/grasp exercises |
| Full 20–60 second explainer | Storyboard, 3+ shots, actual voiceover, visual review | Basic 20.2-second six-shot example with test voice; sampled review complete, full artistic acceptance pending |
| Advanced 2D character animation | Pose sheets, deforming rigs, expression and action continuity | Original hierarchical vector character study; complex action and advanced deformation remain open |
| Advanced 3D shorts | Character mesh/rig, blocking, acting, lighting, sound, render review | Stylized rig/preset exercises; advanced acting, arbitrary asset pipelines and film quality remain open |
| General learned drawing policy | New subjects from text, editable action sequences, unseen-subject test suite | No such model established |

## What is actually trained

The supplied basketball models encode one scene's color and stroke information; moving a learned ball image with physics does not establish learned animation. The supplied video-order classifier recognizes relative frame order, not how to draw. Their original reports and limitations are retained.

The new supervised MLP experiment learns positions along procedurally generated Bezier curves, given their control points and progress. Train/validation/test use entire independent curves. This is deliberately narrow and cheap; exact interpolation has zero error and remains the production default. No third-party video was used in this new training.

Iteration 2 also trains a six-intent reaction classifier on 110 original synthetic sentences, with a fixed 20-sentence holdout. CLIP and Whisper base.en are pretrained upstream models reused unchanged. Reference indexing and speech transcription do not constitute training a general animator. See `reports/ITERATION_02.md` and the rendered exercises in `exmapels/`.

## Meaningful next model experiment

Define an action vocabulary: editable stroke geometry, width, color, layer, transform and stop. Collect original or licensed drawings with their real stroke/layer histories and aligned descriptions. Split by subject and creator, not neighboring frames. Select a trainable vision-language/action backbone based on the data and available hardware. Keep a fixed hidden test suite of unfamiliar subjects and scene layouts.

First establish supervised stroke-policy performance against exact geometry, retrieval, a code-authoring agent and the existing scene-specific model. Evaluate recognizable shapes, perspective, semantic brief match, stroke economy and temporal consistency. Preserve human review; pixel similarity alone rewards copying.

Only then consider reinforcement learning with bounded rollouts and explicit rewards. Renderer validity, timing and editability can be checked automatically; artistic quality needs meaningful preference labels. Track reward exploitation, failed rollouts, held-out subjects, compute and model checkpoints. Repeating tutorial downloads or appending prompt lessons is not weight training or RL.

No general model architecture, authorized drawing-action corpus or GPU training run has been established in this task. CPU rendering and bounded supervised experiments are available now. Do not report later stages as solved because the foundation runs.
