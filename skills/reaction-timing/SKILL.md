---
name: reaction-timing
description: Place semantically appropriate reaction images/GIFs at reviewed spoken beats with honest timing and rights checks.
---

# Reaction timing

Use for narration-led commentary and meme inserts. The goal is the right reaction to the story, not merely any popular GIF near a keyword.

## Editorial workflow

1. Read the whole sentence and surrounding story. Identify intent, negation, sarcasm and whether a gag is appropriate at all.
2. Obtain real narration and word events. Supplied English audio: prepare Whisper, transcribe, review uncertain words. Demo audio: `synthesize_narration` returns engine events.
3. Call `select_reaction` for candidate intent, then `plan_reaction_cues` on the narration JSON.
4. Review every decision, including abstentions. Selection uses explicit English phrase rules; a rule match is not a calibrated probability or proof that the insert is funny.
5. Choose the semantic anchor. For a verbal setup/punchline, let the setup land before the visual gag. The brain-erase example anchors after “all.”
6. Check asset style, intensity, duration, transparency/disposal and rights. Override with licensed/original local art when needed.
7. Render, inspect cue onset/hold/offset and listen when possible.

## Supported intents and assets

The library covers disaster, confusion, disappointment, brain_wipe and victory, plus abstention (`none`). Several intents share artwork; style/theme preference never justifies a semantically wrong insert.

- Disaster/victory: original generated anime-style illustrations.
- Brain wipe: third-party Squidward eraser GIF, cropped only to remove blank canvas. Local test use has no asserted republication license; replace before public/monetized publication.
- `asset_overrides` maps intent to a local image/GIF/video path inside the workspace.

GIF frame durations are respected. Video inserts use a bounded six-second decoded loop. The server does not search Giphy/Tenor or download memes for you.

## Timing contract

Narration JSON contains text, duration and ordered words with character spans and start/end times. ASR boundaries are estimates; synthesis events are a different timing source. Cue frames round word times to the output frame grid.

Check:

`abs(frame_start / fps - word_time) ≤ 0.5 / fps`

This measures rounding, not whether the chosen word is the right punchline. `timing_pass` and audio presence do not prove humor or accurate ASR alignment.

The brain cue uses the final word of the short setup and holds long enough for the eraser action. Do not cover the setup with the gag or revert to the unrelated sleeping-brain still.

## Semantic guards

A literal medical/scientific brain discussion must not receive a stupidity gag. Explicit negation such as “not a dumb plan” must not be treated as the affirmative insult. The implementation has narrow editorial guards; the agent must still review context, including cases the guards do not cover.

Prefer abstention to a forced meme. Do not lower the threshold merely to fill screen time. Record why a cue was rejected as well as why one was accepted.

## Tools and evidence

`prepare_voiceover_model` → `transcribe_voiceover` → `plan_reaction_cues` → `render_reaction_video`.

For already reviewed narration, start at `plan_reaction_cues`. Working evidence lives in `examples/02-semantic-reactions/{brain,disaster,victory}/`: `voice.wav`, `narration.json`, `cue-plan.json`, video and QA.

The showcase reaction stage re-renders from stored narration. It does not re-run ASR. To verify recognition again, fetch the pinned model and transcribe the stored voice separately.

## Acceptance and handoff

Deliver the cue plan with selected phrase, word time, frame, intent, asset provenance and review flags. Separate technical timing from editorial acceptance. Replace the third-party test GIF for publication and state any unperformed listening review.
