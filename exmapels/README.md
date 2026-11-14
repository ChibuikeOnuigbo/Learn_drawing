# Rendered production exercises

Every linked MP4 was actually rendered. [results.json](results.json) records measured export properties. Each project contains source JSON or reproducible scripts, audio where applicable, and an inspection contact sheet/QA report. Full playback and artistic acceptance remain viewer review.

| Example | Video | What it demonstrates |
|---|---|---|
| Narration-led YouTube explainer | [Watch](youtube-explainer/video.mp4) | 20.2 seconds, six timed shots, actual speech, captions and clean source assembly |
| Anime reaction story | [Watch](reaction-story/video.mp4) | 15.17 seconds; disaster, brain gag and victory reactions placed on engine-timed spoken cues |
| Same story from audio alone | [Watch](reaction-from-audio/video.mp4) | Whisper transcript → intent selection → reactions; ASR timing is approximate and flagged for review |
| Original 2D character | [Watch](2d-character/video.mp4) | 11.71 seconds; nested vector rig, blinks, expressions, preparation, wave, facepalm and settle |
| Easy 3D | [Watch](3d/easy/video.mp4) | 3-second gravity bounce with squash/stretch |
| Simple 3D | [Watch](3d/simple/video.mp4) | 3-second wave using a real weighted humanoid skeleton and IK |
| Medium 3D | [Watch](3d/medium/video.mp4) | 4-second planted-foot walk, root travel and moving camera |
| Hard 3D exercise | [Watch](3d/hard/video.mp4) | 4-second squat, reach, grasp and carry; hand-driven prop motion and camera change |

These difficulty labels are relative to the toolkit's exercises. The user's advanced film references require much more modeling, animation and production work.

## Inspect the work

- Open each `inspection/contact-sheet.jpg` and `inspection/qa.json`.
- Reaction projects include `cue-plan.json`; speech sources contain actual WAV audio and word-event JSON.
- `reaction-story/asr-base/narration.json` preserves the recognized words. [The synchronization report](../reports/voiceover-sync.json) compares ASR estimates with known synthesis events.
- The 2D source is `2d-character/scene.json`. `scene-clean.json` and `clean/video.mp4` retain a caption-free master for editing.
- Each 3D folder includes `scene3d.json`, an editable `scene.blend`, and `rig-qa.json` where applicable. Rig reports evaluate real deformed mesh vertices, foot height and payload attachment.
- The explainer's `edit.json` records source in/out times, final-frame holds and captions. Its narration and frames are not inferred from a successful encoder exit alone.

## Reproduce

From the repository root, after setup:

```bash
.venv/bin/python scripts/render_reaction_example.py
.venv/bin/python scripts/render_character_example.py
.venv/bin/python scripts/render_exercise_suite.py
.venv/bin/python scripts/render_explainer_example.py
```

For the audio-only variant, call `transcribe_voiceover` on `reaction-story/speech/narration.wav`, then pass its returned narration JSON to `render_reaction_video`. Prepare the pinned Whisper model first. The generated speech is an offline test voice; it can be replaced with a supplied voiceover.

Intermediate raw frames and log files are excluded from Git. The source JSON and generator scripts reproduce them. Absolute paths in measured reports describe this cloud run; rerendering regenerates them for another checkout.

## Asset provenance

The character drawings, robot geometry, animation, story and sound accents are original code-authored work. Reaction illustrations were generated in this session from original anime/cartoon prompts and are bundled with the toolkit. The brain gag is an original sponge-like space creature with a sleepy brain inside a helmet; it is not a downloaded SpongeBob clip. No third-party reference footage was inserted into these public exports.
