# Reference study and rebuild notes

Date: 2026-11-14. This file replaces the earlier sparse-sample observations. It separates **measured file facts**, **reviewed visual observations**, and **implemented changes**. It does not claim model-weight training or full viewing of every tutorial.

## 1. What was actually scanned

The user's already-downloaded Google Drive corpus was used; no YouTube video was downloaded by this rebuild.

- 55 MP4 files, 2.2 GB local mirror, 7.534 total hours.
- 2,805 timestamped visual samples (at least 48 per video, plus opening samples).
- 27 files had every adjacent frame decoded at 96×54 for change measurements; 453,734 frames decoded in that pass. The remaining longer files are explicitly labelled sparse-sample only.
- Most reference files are AV1. OpenCV's bundled FFmpeg failed to decode them; PyAV/libdav1d succeeded. `scripts/research/analyze_drive.py` is the reproducible scanner (moved under `research/` in 0.4.0).
- Machine-readable provenance: `references/DRIVE_SCAN.json` (name, Drive ID where known, SHA-256, duration, fps, frame count, sample count, decode scope). Review boards are generated under `.work/reference-study/` and are intentionally not committed.

Cut candidates are mean-absolute-delta > 24 at 96×54. They are **not** semantic shot labels, and a flash or fast motion can trigger them. Long tutorials with sparse samples have `cut_candidates: null`, not zero.

## 2. Reviewed visual observations

These notes come from inspecting generated contact boards, not uninterrupted playback. Timestamps are sample times visible on the boards.

### `04_extremely-hard-2.5d-3d-animation_6xSD11AtCqU.mp4` (55.08 s, full adjacent decode)
- Observed: black/neon-green title build, silhouetted winged figure at ~17.8 s, orange impact burst at ~29.25 s, objective/UI card at ~36.17 s, cyan energy close-ups at ~43 s.
- Useful mechanics: extreme value contrast, readable silhouette before detail, color-scripted accent (green world / orange danger), insert cards as punctuation, close-up impact framing.
- Implemented analogy: the hard 3D exercise uses a mint-lit corridor, amber iris/core, moving camera and an independently animated drone. It does **not** copy the reference characters or frames.

### `14_very-extremely-hard-3d-blender_hCnsaahr2cc.mp4` (704.88 s, sparse samples)
- Observed: Roblox-style Squid Game parody; guards at ~80.75 s, pink-frontman close-up at ~168.88 s, ball-pit set at ~345.08 s, lightning effect at ~624.12 s.
- Useful mechanics: modeled environments with repeated architectural rhythm, costume continuity, coverage (wide → medium → close-up), title cards between beats, practical light sources.
- Implemented analogy: editable `.blend` projects now contain actual sets, beveled materials, area lights, camera keys and weighted rigs instead of a lone primitive on a gray void.

### `08_uDqjIdI4bF4_12_Principles_of_Animation.mp4` (1442.61 s, sparse samples)
- Observed: spacing charts, anticipation comparisons, pose-to-pose vocabulary, drag/overlap diagrams, timing examples on ones/twos.
- Useful mechanics: weight, anticipation, slow-in/slow-out, secondary action, readable holds.
- Implemented analogy: easy bounce uses squash/stretch and impact spacing; walk uses planted stance/swing phasing; reach uses anticipation → contact → lift → settle.

### `09_almost-hard-music-video-sketches_9w0_e9X4FDw.mp4` (99.9 s, full adjacent decode)
- Observed: limited-palette animatic, emotional close-ups (~13.5 s eye burst, ~26 s crying), silhouette moon sequence (~32–36 s), door reveal (~48.9 s).
- Useful mechanics: silhouette storytelling, held emotional poses, palette shifts to mark memory/mood, cuts timed to musical beats.
- Implemented analogy: the 2D moonlight sequence uses a fixed character rig, layered parallax, a focal orb and particle release rather than translating a flat image.

### `10_complex-anime-edit-composition_s-n7xL8JxZE.mp4` (102.05 s, full adjacent decode)
- Observed: cockpit POV (~13.8 s), explosion (~26.6 s), train/city parallax, phone-shard particle montage (~71–84 s), end title.
- Useful mechanics: 2D/3D composite layering, match cuts, particle reveals, rapid montage with a clear focal object.
- Implemented analogy: `04-asset-based-short` assembles independently rendered 2D and 3D shots with captions and music; the 2D scene has separate background/character/FX/foreground planes.

### `11_medium-memes-script-visuals_rv0CZ919PFw.mp4` (627.88 s, sparse samples)
- Observed: reaction inserts and manga panels aligned to spoken beats; facepalm at ~307.4 s, Squidward insert at ~372.8 s, manga reaction panels at ~529.78 s.
- Useful mechanics: the insert must match the *intent* of the line, not just be a random meme; anime/manga styling is used when the story is anime-themed.
- Implemented analogy: semantic reaction tests use generated speech + Whisper word times. “This is absolutely messed up” selects the anime disaster illustration; “No brains at all” selects the actual Squidward brain-erasing GIF after the verbal setup.

### Original NothingxArt / basketball work
- The supplied study annotations describe 186 IbisPaint-style painting timelapses, dominated by city/landscape/sunset palettes and seasonal cat-character scenes. They are useful for layer/value scaffolding, not proof of a learned drawing policy.
- `Basketball_Redo.mp4` and comparison boards show cleaner visibility-aware strokes than the earlier attempt, but still flat/low-detail. The rebuild keeps the lesson (construct layers, verify output) and deletes the weak legacy pixel-reproduction artifacts.

## 3. What changed in the MCP

- **Portable rendering:** CairoSVG/cairocffi replaced by `resvg-py`; bundled Inter/Space Grotesk fonts with licenses. 2D tests pass without system Cairo.
- **Real reaction timing:** local Whisper base.en transcribes generated test speech; cue frames are rounded from word timestamps. The brain gag is the verified 38-frame eraser GIF, cropped only to remove blank canvas, not the old unrelated sleeping-brain still.
- **Editable 2D character:** nested SVG pivot groups, connected limbs, face layers, blink/expression states, parallax background and independent FX. Source SVG + scene JSON are included; frame PNGs are regenerable intermediates.
- **Editable 3D exercises:** easy/simple/medium/hard presets save `.blend`, weighted 15-bone humanoid, 4 IK chains, art-directed sets, camera moves and rig QA. Difficulty labels describe the exercises, not equivalence to the reference films.
- **Honest QA:** technical pass checks codec/frame count/fps/dimensions/audio presence and rig geometry/IK/attachment. Artistic fit remains a separate review note.
- **Cleanup:** removed `exmapels/`, `legacy/`, old `reports/`, old preview videos and weak example scenes. Drive mirror, tools and scratch boards are gitignored.

## 4. Limits that remain

- No universal text-to-art or text-to-3D model is bundled. The host agent authors scenes/assets; the MCP validates, renders, edits and inspects.
- Rigging is a procedural stylized humanoid preset, not universal auto-rigging or learned acting.
- ASR word boundaries are estimates; low-confidence cues are flagged for review.
- The Squidward GIF is a third-party local test asset. No republication license is asserted; replace with licensed/original art before public monetized use.
- CLIP retrieval currently uses the bundled 330-sample index. The denser 2,805-sample scan is provenance for study; rebuilding the CLIP index requires preparing the pinned vision model and is not claimed here.
