# Cloud, sky and scenery motion — research notes and applied recipe

Date: 2026-11-16. This report records what was actually read from the linked research
Drive, what was applied in the new talking-scene example, and what remains unverified.
It is a technique log, not a claim of artistic mastery.

## Sources actually read (research Drive `1prGI_23hOqgjXHfZd_nc0BEf3DGfIVoI`)

1. `ANIME_AURA_MOTION_RESEARCH_PLAYBOOK.md` (14,791 bytes, read in full) — layered
   2D/2.5D compositing recipe: silhouette-derived aura, rain depth bands, scrolling
   fog/smoke, cloth displacement, breathing. The cloud/sky-relevant rules:
   - **Multiple independent depth bands**, never one uniform layer. Foreground moves
     faster than background; each band gets its own speed, opacity and phase.
   - **Independent phases and gentle envelopes** — synchronized pulsing reads as
     artificial. Ease densities and speeds in/out rather than popping layers on.
   - **Wrap-around must be tested**: keep moving elements off-screen at wrap, fade
     entry/exit if needed, and decode consecutive frames to confirm no jump.
   - Procedural scrolling noise is a controllable graphic effect, not a simulation.
2. `SCENE_DRAWING_LEARNING_LOG_Composition_Motion.md` (25,489 bytes, read) —
   composition/motion principles: three landscape depths moving at different rates,
   a consistent hero silhouette, timing vs spacing, pose-to-pose workflow with
   anticipation/follow-through. The explorer example applies three-depth parallax;
   the new talking scene applies the same rule to sky/crowd layers.
3. Playbook reference links consulted as *technique sources only* (not re-fetched
   in full): yelzkizi anime-fx layering, Boris FX rain-design depth notes, Adobe
   12-principles material, 2.5D explanations (pixeldust). The learning log also
   indexes background-focused tutorial leads (Drawing 2D Backgrounds for Animation,
   From Animatic to Backgrounds, Aaron Blaise) which remain **listings, not watched**.

## Applied recipe — `exmapels/talking-scene`

The scene is assembled from AI-generated raster plates plus the hand-drawn PNGTuber
cutout (user's own avatar, green-screen keyed). Scenery motion follows the playbook:

| Layer | Motion | Rule applied |
|---|---|---|
| sky plate | slow scale push 1.06 → 1.10 | subtle camera move, no sliding edges |
| wispy far clouds ×2 | −34 px / −26 px over 19 s, opacity 0.8–0.9 | far band slowest |
| cumulus near clouds ×2 | −88 px / −118 px over 19 s | near band ~3× far rate, offset phases |
| grass/stone ground | −46 px over 19 s | mid band, between the cloud rates |
| avatar | talk bounce ±3 px bob | hold-eased mouth swaps driven by eSpeak word timings |
| avatar blink | eyes-closed plate, 5-frame spikes ≈ 3.1 s cycle | independent phase from speech |

All cloud layers drift in the same direction (wind) at different rates — depth reads
from *speed difference*, exactly as the rain/fog bands do in the playbook. Motion is
linear (constant wind) while character motion uses smooth easing; this contrast keeps
the background from feeling like a tweened UI.

## Asset pipeline

`scripts/prepare_talking_assets.py` keys the plates:
- magenta-key + despill for the cloud clusters (flood-white would eat cloud whites),
- top-edge flood key for the ground strip (keeps white flowers inside the meadow),
- green-screen key for the avatar, trimmed and re-registered to one shared 628×697
  box so mouth/blink state swaps never shift the character.

State plates (`avatar-mouth-closed`, `avatar-eyes-closed`) are AI edits of the same
cutout, re-normalized to the identical box. They are generated variants of the
user-supplied drawing, not new characters.

## Interactive PNGTuber tester — `exmapels/pngtuber-demo/index.html`

Self-contained page matching the requested PNGTuber usage: expression mood states
(happy/exited/calm/surprised/sad affect bounce amplitude and speed), blink-interval
slider, voice-energy meter, Auto Talk Demo (scripted envelope) and Manual/Mic Test
(WebAudio RMS with a sensitivity gate). It is a demo harness for the cutout, not a
character animation model.

## Honest limits

- Cloud shapes are generated plates; the drift recipe is applied technique, not a
  fluid simulation and not a reconstruction of any specific creator's sky.
- Remnant777 is referenced only from the user's description and repository notes.
  No Remnant777 video was available locally to study; nothing here is traced from
  that channel.
- The tutorial library (`07_Video_Tutorial_Library.md`) is a discovery index. The
  background-technique videos it lists were not watched in this pass.
- "More training" in this pass = re-ran the two bounded supervised experiments
  (`training/`): reaction intent classifier (95% on a 20-sentence shared-author
  holdout — vocabulary and author are shared, so this is not generalization) and
  the Bezier stroke MLP (≈2.29 px error at 256 px vs 0.0 for exact geometry; exact
  interpolation remains the production path). No claim that either trains drawing
  ability; they are the repository's existing narrow experiments, not new learning
  from the reference videos. Reference videos were **indexed frame-by-frame** (see
  `references/frame_index/`), which is data preparation, not training.
