# Provenance — curtain mesh recreation

- `assets/room-window-empty.png`: original AI-generated empty-window plate created for this repository. Not a Drive frame.
- Curtain fabric: deterministic procedural atlas in `scripts/build_drive_recreations.py` with baked irregular fold shading; no external texture and no temporal photo blending.
- Motion: 2D position-based distance-constraint solve (`animation_mcp.cloth`) at 17 Hz control rate, cubic-interpolated to a 60 fps comparison export (`video.mp4`, 240 frames) plus a true 17 fps export (`video-17fps.mp4`, 68 frames).
- Technique reference: user's Drive curtain research (see `references/DRIVE_RESEARCH_DIGEST.md`). Reference videos are not bundled or required.
- Scope: not a 3D cloth simulation. Horizontal gathering follows the hung span (out-of-plane buckling is represented by shading, not solved depth). A monotonic-column projection and a reported fallback blend to an analytic safe pose keep the render mesh fold-free; `mesh-qa.json` records fallback count, solver strain and projection magnitude.
- `previous-0.6/`: preserved first-pass 24 fps analytic-warp render and QA, kept rather than overwritten.
