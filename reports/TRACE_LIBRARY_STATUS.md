# Per-frame trace library status

## Built in this pass

| Video | Decoded/indexed frames | Excluded | Insert candidates | Notes |
|---|---:|---:|---:|---|
| `17_tutorial-short_vNxqa8ltH20` | 751 | 0 | 1 | Vertical anime drawing tutorial; every frame indexed. |
| `09_almost-hard-music-video-sketches_9w0_e9X4FDw` | 999 | 0 | 13 | 2D narrative sketches; style reviewed. |
| `04_extremely-hard-2.5d-3d-animation_6xSD11AtCqU` | 1,322 | 0 | 2 | Neon 2.5D/3D sci-fi; style reviewed. |
| `10_complex-anime-edit-composition_s-n7xL8JxZE` | 2,041 | 0 | 26 | Mixed 2D/3D anime edit; style reviewed. |
| `26_5lMNtULECHE_GvsK_Part_3_preview` | 887 | 0 | 2 | 2D kaiju fight preview; style reviewed. |
| `11_medium-memes-script-visuals_rv0CZ919PFw` | 37,673 | 608 | 242 | Mixed commentary; four visible sponsor/brand ranges excluded with source URLs. Remaining meme origins unconfirmed. |

Total: **43,673 frames decoded and indexed**, **608 excluded insert frames**, **43,065 traced frames**. Storage: chunked NPZ + manifests under gitignored `data/traces/` (~156 MB). Every decoded frame has a record; sparse tracks/contours are image evidence, not recovered vector strokes or rigs.

## Meme/insert handling

- Low-motion shots are flagged as **candidates**, not automatically called memes.
- Confirmed exclusions require review and `source_url` evidence. Applied sponsor/brand inserts: Zocdoc (frames 8702–8831 and 11848–12003), Google search screen (8972–9198), BetterHelp (9974–10072).
- The local perceptual-hash catalog currently identifies the bundled Squidward brain-erase template only; it did not match the reviewed candidates. Unknown origins remain unknown and require authorized source review.

## Still pending

- 49 indexed Drive videos remain pending local media restoration/processing (`references/TRACE_LIBRARY_PLAN.json`).
- Remnant777: 89 videos listed in the channel inventory, but the Drive folder lists **0 accessible files**; no Remnant compositing study is claimed (`reports/REMNANT777_COMPOSITING.md`).
- Style tags are reviewed for the six built videos only; other videos remain measured-only once traced.

## Reproduce/continue

```bash
python scripts/build_trace_library.py google_drive/<video>.mp4 --output data/traces
python scripts/build_asset_kit.py
```

MCP: `list_trace_library`, `get_trace_frame`, `get_trace_track`, `identify_video_insert`, `exclude_trace_inserts`, `search_art_styles`, `plan_new_scene`, `generate_procedural_asset`, `build_composite_scene`; resources `studio://traces`, `studio://styles`, `studio://assets`.
