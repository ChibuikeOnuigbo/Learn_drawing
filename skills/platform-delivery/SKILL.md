---
name: platform-delivery
description: Adapt animation deliverables for landscape, portrait, square and review contexts with safe areas, captions and honest export checks.
---

# Platform delivery

Use near delivery, but plan aspect ratio early. Load [composition](../composition/SKILL.md), [video-editing](../video-editing/SKILL.md) and [quality-review](../quality-review/SKILL.md).

## Choose the master deliberately

Common starting canvases: landscape 1920×1080 or 1280×720; portrait 1080×1920; square 1080×1080. Confirm the target platform’s current requirements before final export; this repository does not maintain live platform policy.

The edit tool aspect-fits and pads rather than cropping. That protects content but can create bars. For portrait-first work, author a portrait scene or re-stage shots; do not assume a landscape master will fill a Short well.

## Safe areas and captions

Keep faces, hands, essential text and call-to-action elements away from edges and platform overlays. `caption_position` controls the caption block’s lower edge as a fraction of height; inspect the actual frame. Use short cues, high contrast and readable hold duration.

Do not burn captions twice. Use a clean visual master when adding edit captions. Check legibility at phone size, not only on a desktop monitor.

## Export packet

Deliver final video, editable source, poster/contact sheet, cue/shot plan, asset provenance and QA. For 3D include `.blend`; for 2D include scene JSON/SVG/pose sources; for edits include decision JSON and audio provenance.

Verify codec, dimensions, fps, decoded frame count, duration and expected audio. The bundled encoder uses H.264/yuv420p and AAC when audio is supplied. It does not provide platform-specific loudness normalization, HDR metadata or adaptive streaming packages.

## Versioning and review

Use versioned filenames and preserve a known-good source. Record what changed between exports. Technical pass is not platform approval or artistic acceptance. If playback/listening was unavailable, state exactly what remains pending.

See `examples/08-vertical-short/` for a portrait-safe staging proof and `examples/09-narrated-explainer/` for a multi-shot narrated layout.
