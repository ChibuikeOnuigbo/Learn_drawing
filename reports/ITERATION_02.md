# Iteration 2 — actual production evidence

## Delivered exports

Eight original example projects are in [exmapels](../exmapels/README.md), totaling about 76 seconds of exported video. They include a 20.2-second narration-led explainer, a 15.17-second reaction edit, an audio-transcribed version, an 11.71-second editable character study, and four short 3D exercises. [Measured results](../exmapels/results.json) preserve dimensions, frame counts, frame rates, audio presence and technical outcomes.

The 3D character has 15 bones, 5,994 weighted mesh vertices and four IK chains. Actual deformed foot vertices were checked against the floor. The walk/carry minima were approximately -0.000001 and -0.000078 world units. The carry's evaluated hand/prop offset error was zero at sampled frames. These are geometric checks, not proof of acting quality or physical contact realism. Rig reports and editable `.blend` sources are included.

Contact sheets were inspected for expressions, pose changes, caption readability, reaction selection and scene continuity. Walk samples were extended to quarter-second positions so a one-second sampling interval would not alias its gait cycle. Full uninterrupted playback and subjective humor/quality acceptance remain viewer review.

## Speech and synchronization

The test story actually speaks the disaster, “no brains” and victory phrases. Engine events place its reaction cues at the intended words, with frame-rounding error below half a frame. Original generated reaction illustrations are used; no downloaded franchise GIF is falsely claimed.

The uploaded-audio workflow uses local Whisper base.en. It recovered all three key phrases from the longer demo. Compared with the known synthesis events, its phrase onsets differed by -0.279s, -0.046s and -0.248s. The audio-only export is flagged for review. These are ASR estimates; sub-frame cue quantization does not imply sub-frame speech alignment. Short speech could lose the plural s in “brains”; the semantic selector accepts the singular variant while preserving this observed transcript limitation.

Whisper tiny was tested first and misrecognized the longer conclusion. It was replaced by base.en after that diagnosis. The downloaded models are pinned and checksum verified. The offline eSpeak voice is intentionally a test voice, not a claim of expressive narration quality.

## Models, training and package validation

A new six-intent classifier was trained on 110 original synthetic English examples. It classified 19/20 fixed holdout sentences correctly. The split shares vocabulary and author with training, so this is a limited sanity check. Negation/literal-topic guards are explicit editorial rules. No artistic accuracy percentage or calibrated humor score is claimed.

CLIP ViT-B/32 and Whisper base.en were reused unchanged from upstream. Six sampled frames from each of 55 supplied videos were embedded for reference retrieval. Similarity can misrank stylistic requests and is not a production-quality score. No general drawing/animation model, generative video model or RL policy was trained.

The wheel was built and imported outside the checkout. Bundled reaction assets, safe numeric classifier weights, the curve checkpoint, workflow resource and model manifests were checked there. A generated client configuration uses the actual interpreter and cache paths, avoiding reliance on a GUI host inheriting an activated shell.

Tests include actual speech audio, encoded reaction video, supplied-audio transcription and semantic cue selection, CLIP retrieval, a real Blender armature render, nested 2D transforms/visibility, explicit shot holds, and MCP tools/prompts/resources. The final test log/count is recorded in the completion report. CI skips optional model or Blender checks when their prerequisites are absent; it does not describe skips as passes.

The full local run with both pretrained model caches and Blender available completed **32 passed, zero skipped, zero failed**. One upstream Pydantic-settings warning remained; actual MCP initialization, tools, prompts and resources passed. The saved setup script was also exercised with these prerequisites.

## Data and remaining limitations

All 62 files currently exposed by the new Drive folder were downloaded and hashed: 55 videos plus seven other files. The channel inventory lists 184 intended videos, but Alan Becker exposes 10/67 and Remnant777 exposes none. No direct YouTube download was needed. The reference manifest and study catalog are versioned; third-party source footage stays outside Git.

The new 2D/3D work is authored/procedural. The rig targets a stylized humanoid, not arbitrary mesh auto-rigging. It does not implement expressive lip sync, advanced anime action, cloth simulation or the user's hardest reference quality. The current Blender build lacks OpenImageDenoise; the failed denoising test was corrected by disabling it in supported presets, and low-sample previews retain visible grain. No cloud environment publication was performed.
