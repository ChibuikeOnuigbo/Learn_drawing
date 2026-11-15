# Provenance — eye/face performance

- `assets/eye-character.png`: original AI-generated anime portrait created for this repository. Not an existing franchise character and not a Drive frame.
- Iris/sclera separation, apertures and hair mask: authored in `scripts/build_drive_recreations.py` from that plate.
- Blink: `animation_mcp.eye_rig` traces the aperture by hand-authored polygon, moves upper/lower lids per column (upper travels farther), draws lashes on the moving lid, and fills revealed lid skin with a smooth estimate sampled from surrounding face skin. This is **not** recovered hidden artwork and **not** a generated closed-lid plate. Pixels outside the traced eye neighbourhoods are asserted bit-identical (`max_pixel_diff_outside_eye_boxes: 0`).
- Technique reference: user's Drive eye/distortion research (see `references/DRIVE_RESEARCH_DIGEST.md`).
- Earlier abandoned approaches (not shipped): a generated closed-eye underlay left double lids/white streaks after registration; a local squint inverse-warp duplicated eyebrow pixels. Both were removed.
- `previous-0.6/`: preserved gaze/smile/hair-only pass without blink, kept rather than overwritten.
