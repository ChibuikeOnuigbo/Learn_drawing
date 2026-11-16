---
name: sound-design
description: Plan narration, music, effects and sync; prepare a final mix and report measured audio facts without claiming unperformed listening.
---

# Sound design and sync

Use with [video-editing](../video-editing/SKILL.md) and [reaction-timing](../reaction-timing/SKILL.md). Sound should clarify action and emotion, not fill every silence.

## Spotting sheet

List each cue: time/frame, type (dialogue/music/SFX/ambience), story purpose, source/license and duration. Mark silence intentionally. Align impacts to visible contact and reaction gags to reviewed semantic anchors.

## Narration

Use supplied final voiceover when available. For English tests, `synthesize_narration` creates real synthetic speech and engine word events; it is not an expressive human narrator. For supplied audio, prepare Whisper and `transcribe_voiceover`, then review uncertain words/critical timings.

`plan_shots` and `plan_narration` are planning estimates, not forced alignment. Lock picture to reviewed audio events and leave breaths/punchlines room.

## Music and effects

The toolkit can mux one final audio track and includes deterministic demo soundtracks in example builders. It does not bundle a general music generator, stem mixer, ducking engine or loudness-normalization tool. Prepare the final mix in an authorized audio workflow, then supply it as `scene.audio` or `edit.audio`.

Check rights for every music/SFX asset. Original procedural demo audio is labeled as such; do not describe it as a composed commercial score.

## Sync and export checks

- Confirm expected audio stream presence and duration with ffprobe/returned QA.
- Compare cue frame/time against visible action or word event.
- Ensure the ending is not truncated; overlong audio is rejected by the render/edit paths.
- Source clip audio is dropped by the edit tool; provide the final mix explicitly.
- If listening is available, review intelligibility, clipping, balance and distracting noise. If not, mark listening pending.

Peak/RMS measurements can be computed from samples, but they are not perceptual loudness or mix approval. Do not invent LUFS compliance unless measured with an appropriate meter.

## Deliverables

Provide cue/spotting sheet, final mix provenance, narration JSON when used and sync evidence. Separate technical stream checks from listening review.
