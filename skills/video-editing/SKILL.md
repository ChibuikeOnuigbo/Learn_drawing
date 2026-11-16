---
name: video-editing
description: Assemble local animation shots into a timed video with captions, narration and music using an editable decision list.
---

# Video editing and sound

Use after shot assets exist, or to edit supplied local footage. Read [composition](../composition/SKILL.md) for coverage/continuity and [reaction-timing](../reaction-timing/SKILL.md) for semantic gag inserts.

## Build an edit decision list

For each shot record source path, source in-point, output duration, story purpose, caption and sound. Keep source media unchanged. Work on a copy of the decision JSON and preserve a known-good version.

The supported `Edit` schema is:

```json
{
  "width":1280,"height":720,"fps":24,
  "clips":[
    {"path":"shots/establish.mp4","start":0,"duration":3},
    {"path":"shots/action.mp4","start":1,"duration":4}
  ],
  "captions":[{"text":"One clear idea at a time.","start":0.5,"end":2.8}],
  "audio":"audio/final-mix.wav","caption_position":0.85
}
```

Call `assemble_video(edit=<object>)`. For Python, `edit_video(spec, output_folder, workspace_root)` validates the same schema. There is no dedicated edit-file MCP argument; load the JSON and pass its object.

## Exact timing and media behavior

- Clip `start` is the **source in-point in seconds**, not the output placement. Output placement is the cumulative sum of prior clip durations.
- Each duration rounds to the output frame grid and must occupy at least one frame.
- Caption intervals are seconds, half-open, and must fit the assembled duration.
- `hold_last=true` explicitly freezes the source's final frame for a longer slot. Without it, an overlong source interval is rejected.
- Sources are aspect-fit padded, not center-cropped. This protects framing but can introduce bars.
- **Source clip audio is discarded.** Supply one final narration/music/effects mix as `edit.audio`.
- Captions are wrapped on whitespace, limited to four lines and drawn near the lower center. Shorten long unbroken words and split dense dialogue.
- `caption_position` is the caption block's lower edge as a fraction of frame height. Check platform overlays; a landscape position may not suit Shorts.

The tool supports cuts, not cross-dissolves, speed ramps, transitions, beat detection or automatic ducking. Do not invent those fields. Prepare those effects in source shots or an authorized external editor.

## Narration-led workflow

1. Finalize the script before locking picture.
2. Use supplied voiceover when available. `prepare_voiceover_model` then `transcribe_voiceover` gives English Whisper text and estimated word times.
3. For an offline test, `synthesize_narration` creates real synthetic English speech and engine word events. It is not an expressive human performance.
4. Review transcript errors and critical cue times. `plan_narration` only estimates shot lengths from word counts; it is not audio alignment.
5. Build shot durations around actual audio. Leave breathing room at sentence boundaries and payoff beats.
6. Prepare one final audio mix. The 2D renderer rejects overlong audio; the edit workflow should likewise be checked for a complete ending rather than assumed safe.
7. Assemble, inspect caption onsets/offsets and listen to the export if audio playback is available.

Do not duplicate burned-in shot captions with edit captions. Use a clean visual master when adding typography in the edit.

## Local starting points

- `examples/04-asset-based-short/edit.json`: real multi-shot 2D/3D assembly with music.
- `docs/USAGE.md`: schema details and a portrait example.
- `scripts/build_showcase.py --stage edit`: regenerate the example after its source renders exist.

Paths are workspace-relative. Keep the decision JSON in the project source tree and media in a stable asset/shot directory, not only in a temporary MCP output folder.

## Editorial review

Check every cut for screen direction, eyeline, action continuity and readable hold duration. Inspect frames just before/after cuts and caption boundaries. Verify the intended audio stream exists, the ending is not truncated and captions stay inside safe areas.

Metadata/audio presence cannot prove mix balance, intelligibility or comedic timing. If the host cannot listen, state that listening review remains pending. Deliver the video, edit JSON, source-shot list and audio provenance together.
