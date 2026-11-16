# Provenance — whole-character flashlight

- `assets/detective-a.png`, `assets/detective-b.png`: original AI-generated matched character plates created for this repository. Detective B was generated as an edit of Detective A to preserve pose/canvas. They are not Death Note frames and do not depict Light/L.
- `assets/detective-b-aligned.png`: B warped by a similarity transform estimated from 8 hand-picked corresponding landmarks (LMEDS). `alignment-qa.json` records the transform, per-landmark residuals and RMSE before/after. This measures rigid landmark alignment only; it is **not** a structural-deviation certificate. Hair silhouette, strawberry and hands still differ by design.
- Technique reference: user's Drive flashlight research (see `references/DRIVE_RESEARCH_DIGEST.md`).
- Mask: one smoothstep circle over two complete same-canvas images; no face-only gate.
- Limits: approximate generated alignment; inspect fingers, strawberry, neckline and shoulder at 100%. Silent study render; no reference audio copied.
- `previous-0.6/`: preserved unaligned first pass, kept rather than overwritten.
