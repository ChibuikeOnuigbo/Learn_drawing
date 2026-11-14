# Validation — 2026-11-14

Historical v0.1 report. See [ITERATION_02.md](ITERATION_02.md) for the later speech, reaction, character and rigging work.

## Current environment

Clean virtual-environment setup and the pinned Python dependencies were installed successfully. **17 tests passed**, including a real stdio MCP client calling the server to save and render a scene. One dependency emits an incomplete forward-annotation warning; initialization and tool calls still pass. FFmpeg, ffprobe and Blender are system dependencies; the tests do not install them.

Tests exercise half-open layer timing, actual changing pixels, eased endpoints, arc-length stroke reveal, invalid scenes, workspace/symlink confinement, cached image invalidation, H.264 encode/decode, optional audio, refusal to truncate narration, timed caption overlays, clip assembly/portrait fitting, and inference from the saved neural curve checkpoint.

## Render evidence

| Artifact | Verified technical output | Visual review |
|---|---|---|
| Recovered basketball | 960×540, 180 frames, 30 fps, 6 seconds | Inspected 6-frame timeline: gym perspective and bouncing ball are visible. Court/ball image pixels match supplied originals exactly. Ball is a 2D sprite, not learned character motion. |
| Original explorer | 1280×720, 180 frames, 30 fps, 6 seconds, H.264 | Inspected boundary/contact-sheet frames: clear hero silhouette, layered mountains, staged orbit and signal reveals. Basic vector prototype, not advanced character animation. |
| AI scenery composition | 1280×720, 180 frames, 30 fps, 6 seconds, H.264 | Inspected contact sheets: generated painted observatory, original vector character and scientific overlays. Revised overlay contrast and helmet reflection tracking. Raster background remains one plate; it is not a reconstructed 3D environment. |
| Blender orbital scene | 640×360, 48 frames, 24 fps, 2 seconds, H.264; editable `.blend` | Inspected five sample frames. Ring orientation changes around a cyan core with three-point lighting. Rerendered at 48 samples rather than 12 to reduce noise. Still a small prototype, not a production character render. |

Generated videos are in `docs/previews/`; JSON sources are in `examples/`. Per-render metadata and contact sheets are in this directory. `.blend` and intermediate frames are in local ignored `output/` directories and can be regenerated from JSON. Supplied original video files are restored from the Drive manifest.

The inspection code decodes video and extracts exact frame indices, including timeline boundaries. Contact sheets were visually inspected; no uninterrupted real-time playback review or blind artistic evaluation was completed. Metadata tests and stills are not a guarantee of smooth or high-quality full motion. No fabricated artistic scores or reference-match percentages are reported.

## Training evidence

The 160-epoch supervised curve run used 600 train, 120 validation and 120 held-out test curves with disjoint control polygons. Its test mean absolute error is **0.0089497 normalized units**, about **2.29 pixels at 256 scale**, versus **0.19309** for holding the starting point. Exact mathematical Bezier interpolation has **zero error** and is the production default. These are coordinate errors, not artistic scores. The experiment is not RL, text-to-drawing training or evidence of anatomy/composition knowledge.

The recovered basketball model was run without reading source images in its inference worker. Its Python audit hook is not an OS sandbox. Both output gym and ball PNGs match the supplied project images exactly at the pixel level. This demonstrates reconstruction of the known scene, not generalization to new scenes.

## Migration evidence

- All 13 Drive files downloaded and SHA-256 verified.
- Four ZIP archives checked; the study archive contains 185 videos and passed CRC verification.
- Project source, reference notes, numeric checkpoints, small project art and original demos prepared for GitHub.
- Third-party study videos/boards and classifier binaries retained outside Git; IDs, checksums and restoration instructions are versioned.
- Cookie uploads were not opened, required or committed. The uploaded master prompt was preserved as reference text, not activated as agent policy.
- Direct YouTube requests failed with proxy `403 Forbidden`; the user's ranked examples remain unreviewed. Existing Drive sample sheets were inspected with that narrower scope recorded.

## Outstanding work

The user's advanced reference quality has not been reached. A full narration-driven multi-shot explainer still needs a real brief/voiceover and production review. General character drawing, rigs, lip sync, advanced 2D/3D animation, Giphy/Tenor sourcing and a general learned drawing policy remain future work. The optional legacy FSRCNN upscaling scripts need OpenCV contrib and were not rerun. No GPU or general model training was performed. No new cloud environment draft was published in this task.
