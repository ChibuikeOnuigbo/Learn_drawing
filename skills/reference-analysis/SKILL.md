---
name: reference-analysis
description: Study supplied animation references systematically, extract transferable mechanics and preserve provenance without copying or overstating review.
---

# Reference analysis

Use when the user supplies a film, clip, board or link and wants to learn from it. Load [composition](../composition/SKILL.md), [storyboarding](../storyboarding/SKILL.md) and the relevant engine skill.

## Establish access and scope

Record what you can actually inspect: full video, sparse frames, contact board, transcript, metadata or only a description. Do not call sampled-frame review “watched the whole film.” If media is absent, ask for an authorized local copy or work from the supplied evidence.

The committed Drive scan is current measured provenance; archived catalogs are historical. Local corpora are ignored and may be absent after a sandbox reset.

## Observation pass

For each selected interval note:

- Shot purpose, framing, camera move and cut reason.
- Silhouette, value grouping, focal accent and depth layers.
- Timing: keys, holds, spacing, anticipation, impact, settle.
- Continuity: screen direction, eyeline, prop attachment, costume landmarks.
- Sound: cue placement, pause, punchline relationship.
- What is observed vs inferred.

Use exact timestamps/frame indices when available. `inspect_video` can extract frames from local media. For broader local corpora, the optional PyAV scanner samples timestamps and measures adjacent-frame change on short files; cut candidates are not semantic shot labels.

## Extract mechanics, not assets

Translate observations into transferable rules: “increase value contrast at the reveal,” “delay sleeve overlap three frames,” “hold the reaction after the verbal setup.” Apply them to original artwork. Do not trace/reuse protected characters, frames, music or rigs without permission.

CLIP retrieval finds sampled frames by text; it does not recover production files, brush histories or a creator’s process. Similarity is not a quality score.

For per-frame geometry use `trace_video_file` / `scripts/build_trace_library.py`, then `get_trace_frame` and `get_trace_track`. Tracks are sparse optical-flow features, contours are raster approximations, and IDs reset at cuts. Exclude confirmed meme/insert ranges with `exclude_trace_inserts` only after source review; `identify_video_insert` returns unknown rather than guessing. Record reviewed style tags/mechanics in the style catalog with evidence frames.

## Comparative proof

Author an original shot using the extracted mechanic. Render a proof and compare specific evidence: silhouette readability, contact spacing, cue offset, focal hierarchy. Record what improved and what remains different. Avoid vague “reference parity” claims.

## Deliverables

Provide an observation log with scope/timestamps, extracted mechanics, original proof and provenance/rights notes. Keep third-party media out of Git unless redistribution is clearly authorized.

## Worked Drive digest

`references/DRIVE_RESEARCH_DIGEST.md` maps the user's curtain, eye/distortion and flashlight research to exact Drive IDs and the mechanics used in examples 05–07. Rebuild those proofs with `scripts/build_drive_recreations.py`; inspect `mesh-qa.json`, `eye-qa.json` and `beam-qa.json` before claiming a fix. The recurring failures to avoid are photo crossfades sold as cloth, face-only body reveals, unanchored warps and invented detail sold as recovered source.
