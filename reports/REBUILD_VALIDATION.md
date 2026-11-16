# Rebuild validation report

Date: 2026-11-14. Branch: `arena/a166910d-learn-drawing`.

This report separates **measured technical checks** from **artistic review**. It does not claim reference-film parity or model-weight training.

## Automated tests

```text
PATH=.tools/bin:$PATH ANIMATION_ASR_CACHE=.work/whisper-cache .venv/bin/pytest -q
33 passed, 1 skipped, 1 warning
```

- The skip is CLIP retrieval because the pinned CLIP ONNX model was not fetched in this sandbox.
- The warning is a benign upstream `pydantic_settings` forward-reference warning.
- `python -m compileall -q src scripts tests` succeeded.
- Blender-dependent tests used the isolated Blender 4.5 / bpy launcher; `bpy` is not installed in the project venv.

## Reaction timing and audio

Generated speech was transcribed with pinned Whisper base.en; cue frames were rounded from ASR word times. Exports include audio and passed technical/timing checks.

| Clip | Trigger | Word time | Frame @30fps | Rounding error | Audio peak |
|---|---|---:|---:|---:|---:|
| brain | “all.” | 1.20 s | 36 | 0.000 s | 0.830 |
| disaster | “messed” | 4.84 s | 145 | −0.0067 s | 0.837 |
| victory | “worked.” | 2.54 s | 76 | −0.0067 s | 0.839 |
| victory | “comeback” | 4.92 s | 148 | +0.0133 s | 0.839 |

The brain insert uses the actual Squidward brain-erasing GIF and lands after the verbal setup. GIF frame durations are respected. The asset is third-party and is included only as a local semantic/timing test.

## 3D rig QA

Evaluated deformed-pose checks from Blender:

| Exercise | Bones | Weighted vertices | IK chains | Min foot vertex z | Max IK target error | Payload hold error | Geometry pass |
|---|---:|---:|---:|---:|---:|---:|---|
| simple wave | 15 | 5994 | 4 | ≈0.000000 | 0.000145 | — | true |
| medium walk | 15 | 5994 | 4 | ≈0.000000 | 0.021414 | — | true |
| hard reach/grasp | 15 | 5994 | 4 | −0.000027 | 0.000075 | 0.000000 | true |

The hard reach target was corrected after an initial audit measured a 0.297 IK target error; targets now stay inside the limb reach envelope and translate with the body. The payload rests on a pedestal before grasp and follows the evaluated hand afterward.

## Export checks

| Deliverable | Resolution | Frames | Duration | Technical pass |
|---|---:|---:|---:|---|
| 2D moonlight | 1280×720 | 240 | 10.0 s | true |
| brain reaction | 960×540 | 181 | 6.03 s | true |
| disaster reaction | 960×540 | 274 | 9.13 s | true |
| victory reaction | 960×540 | 245 | 8.17 s | true |
| 3D easy bounce | 800×450 | 96 | 4.0 s | true |
| 3D simple wave | 800×450 | 96 | 4.0 s | true |
| 3D medium walk | 800×450 | 120 | 5.0 s | true |
| 3D hard reach/grasp | 800×450 | 120 | 5.0 s | true |
| asset-based short | 1280×720 | 216 | 9.0 s | true |

## Reference corpus scan

- 55 supplied MP4 files, 7.534 total hours, 2.2 GB local mirror (gitignored).
- 2,805 timestamped visual samples.
- 27 files received every-adjacent-frame change measurements; 453,734 frames decoded in that pass.
- Longer files are explicitly sparse-sample only. Cut candidates are image-delta events, not semantic labels.
- Provenance: `references/DRIVE_SCAN.json`. Reviewed observations: `references/STUDY_REBUILD.md`.

## Artistic review

Contact sheets and representative frames were inspected. The 2D sequence is a layered vector cut-out rig with parallax and focal FX; the 3D exercises have modeled sets, art-directed lighting, camera moves and readable silhouettes. These are substantial improvements over the deleted primitive/flat-image examples, but they remain stylized toolkit exercises, not professional reference-film reconstruction. Humor, taste and full-motion polish still require human review.

## Cleanup and portability

- Removed `exmapels/`, `legacy/`, old `reports/`, old preview videos, weak example scenes and the unrelated sleeping-brain still.
- Replaced CairoSVG with `resvg-py`; bundled fonts and licenses.
- Gitignored local corpora/tooling/scratch: `google_drive/`, `.tools/`, `.work/`, `image-search/`.
- Added portable MCP template, absolute client config generator, headless Blender notes, resume support and configurable Blender timeout.
