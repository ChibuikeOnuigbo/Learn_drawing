# Animation production workflow for connected agents

Call `capabilities`, `get_model_catalog` and `get_scene_schema` and inspect the actual available tools. The server supplies local production tools, pretrained/limited models and examples; the host agent still supplies creative reasoning. Never claim connecting the server upgrades the host model's weights.

1. Convert the brief into a concise storyboard: purpose, aspect ratio, voiceover, shot durations, character continuity and measurable acceptance conditions.
2. Search local reference indexes when available. Distinguish sampled-frame evidence from whole-video review. Learn composition and motion techniques; create original deliverables.
3. For narration-driven editing, use supplied speech plus reliable word timings. `prepare_voiceover_model` fetches verified Whisper base.en weights; `transcribe_voiceover` accepts an English audio file and returns a narration JSON. Review uncertain transcript words and estimated alignment. To make a demo, `synthesize_narration` returns actual audio and engine word events. It is a synthetic English test voice, not an expressive human narrator.
4. Call `select_reaction` and `plan_reaction_cues`. Check the full story and negation. Literal brain anatomy must not receive a stupidity gag. The small classifier can be wrong; prefer abstention when unsure. Theme preference does not justify a semantically wrong meme. Review the bundled original assets or supply licensed local images/GIFs/video through overrides.
5. Use `render_reaction_video` for reaction tests, `save_scene`/`render_scene` for editable 2D motion, `assemble_video` for local cuts/captions/audio, and `render_3d_scene` for object or rigged scenes. `render_3d_exercise` offers editable bounce, wave, walk and reach/grasp examples.
6. Start with a low-cost preview. Render actual video, inspect exact onset/offset frames, check the audio and review full playback when the host has that capability. A passed metadata check is not artistic acceptance.
7. Check perspective, silhouette, motion weight, character continuity, foot contact, prop attachment, typography, voiceover sync and export metadata. Fix concrete defects and rerender. Record failures as well as verified fixes using `record_lesson`.
8. Deliver the video, editable source, relevant provenance and a short honest QA report. Never fabricate watching, model training, confidence calibration, reference parity or a quality score.

The cloud task already has an isolated checkout. Use it; do not create a worktree unless requested. Processes do not persist across environment publication. Reconnect the stdio server in the MCP host for each new session.
