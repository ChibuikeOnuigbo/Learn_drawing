# Research Drive digest (read-only)

Source folder: <https://drive.google.com/drive/folders/1prGI_23hOqgjXHfZd_nc0BEf3DGfIVoI>

This digest records what informed the 0.6.0 recreation pass. It is not a copy of the private Drive library and does not assert redistribution rights. File IDs are kept so the user can reopen the exact source.

## Curtains / room

| File | ID | Lesson used |
|---|---|---|
| `LEARNED_CURTAIN_ANIMATION_AND_DISTORTIONS.md` | `10vJ-apeXuDECsRr8L08zyt41i0Zj1eoS` | V7 ghosting came from mixing appearances/leftover fabric, not FPS. Use one stable texture, anchored rail/outer stops, localized deformation, separate tieback release. |
| `CURTAIN_ONLY_MASTER_AGENT_PROMPT.md` | `1P4uTslAq7PLePn0vQS8DlI-OdQxYLJxz` | 17 Hz control geometry interpolated to output; no temporal alpha fade; inspect seams at 200%. |
| `V9_REBUILD_AND_MODEL_NOTES.md` | `1O_gL1KsDUJFb8ZqnoKjm8kJ_0Hw4pMHf` | Even later AI-upscaled versions remained approximate 2D warps; upscaling does not fix correspondence. |
| `REFERENCE_01_PINNED_DRAPE_720p.mp4` | `1r1qJomKtnFWvoNMS1DOENVU1KHy8g1Mf` | Decoded 240 frames @60 fps; centerward closure after a held open state. |
| `REFERENCE_02_WIND_WAVE_720p.mp4` | `1lz0t3X6yXBjIQJqchr1saRCff30vGiui` | Decoded 240 frames @60 fps; similar trajectory with stronger wave. |
| `RECOVERED_V7_13s_60fps_720p.mp4` | `1OJSIO1CKpTrVVMRmFagRDa5rYG6yeT_h` | Decoded 780 frames; rejected ghosting/appearance-mixing evidence. |

Implemented analogy: `examples/05-curtain-mesh/` uses a generated empty-window plate and one procedural fabric atlas per panel, fixed 13×17 topology, fold checks, tieback release and damped settle. It does not reuse the room/curtain pixels.

## Eyes, hair, distortion

| File | ID | Lesson used |
|---|---|---|
| `EYE_ANIMATION_RESEARCH.md` | `1WIbQPTvgQkhR9mPwlanNkLEfC6tBwCl-` | Keep iris/pupil coherent under a traced aperture; protect corners/lashes; flattened art cannot recover closed-lid skin. |
| `EYE_SOURCE_RESEARCH_BUNDLE.zip` | `1HEJwU9w5mCcowCPCBdfnUGHPhHCGSzNI` | Deformation lab: fixed topology, inverse mapping, fold rejection, partial squint only; numerical validity ≠ visual quality. |
| `MOTION__DISTORTION_AND_MOTION_WORK.md` | `1gnoaDdFdul9APEggTBlheOY39l2muuwX` | Move a body, not a patch; anchor joints; small coherent local fields; secondary motion lags then settles. |
| `LEARNED_GTA_LOADING_MEME.md` | `1O8Y6fZSdgknLZnJJgSyZbpeBzNhffTXL` | Diagnostic masks before rendering; pinned borders; heavy liquify and painted eyelids were rejected. |
| `PROJECT_HISTORY.md` | `13PUvQULNTjapkWMyJPjtepRrgSs_MdUc` | Preserve identity; do not sell generated alternatives as source; keep editable layers. |

Implemented analogy: `examples/06-eye-face-performance/` traces apertures/iris on an original generated portrait, moves original iris pixels for gaze, adds anchored hair lag and a local smile warp. A full blink was deliberately not shipped.

## Flashlight / whole-character reveal

| File | ID | Lesson used |
|---|---|---|
| `START_HERE_LEARNINGS.md` | `1yQua2ypn1i6Jqw-pM5lWLHqVABv7Ix_0` | Two complete same-canvas images; one pixelwise mask; body-first path; no face gate; generated assets must be labelled. |
| `DEATH_NOTE_LEARNINGS_EVIDENCE.zip` | `1Bv1WaitHGKSWf7ASaH8JNVSPwPE6xpD1` | V7 equation/timing and failed pose-flip/hand-edit evidence. |
| `03_LIGHT_L_TWO_FULL_IMAGES_V7.mp4` | `1yWlKSaa7C_os4S6lbZwGo5WkMhybh01i` | Decoded 252 frames @24 fps; body→hand→face→pause→return structure. |
| `01_LIGHT_FULL_IMAGE.png` | `13Kbr7HTJ5_SNL42_6OXC2IwSLawOaUp1` | Base complete layer study. |
| `02_L_FULL_IMAGE_AI.png` | `1GzJUr0TszFTyt78_oi4IJuSvhPQId5Ew` | Alternate complete layer study; generated hand/pose compromises. |

Implemented analogy: `examples/07-flashlight-whole-character/` uses two original generated matched detectives and the same smoothstep circle over every pixel. QA measures face alpha before/after the intended reveal.

## General guardrails

| File | ID | Lesson used |
|---|---|---|
| `11_User_Preferences_and_Workflow.md` | `1JhzNIU5Fb4Y3mFxbTZYt6k5KVWkaBLl1` | Evidence first; label original/alternative/generated/reconstructed; do not claim hidden pixels recovered; preserve sources. |
| `ANIME_AURA_MOTION_RESEARCH_PLAYBOOK.md` | `14IjIsllAStFJ6SUhTlHdfm28gNL5OXah` | Silhouette-derived effects behind subject; independent phases; protect face; premultiplied alpha; review whole contour. |
| `Composition_Motion_Research_Report.md` | `1uHuRtkkZ3sJF2TX4aVXydTvWzV3YCtK9` | Tiny RL/PCA experiments are not drawing models; do not overclaim learned capability. |
| `Motion_RL_Followup_README.md` | `1JwhWzt7vvFmzz9p-_at-dUjHnyTUCZbZ` | A learned scalar policy lost to a hold baseline; metrics must be compared to simple baselines. |

## Not used as training data

The downloaded videos/images were inspected and decoded for technique study. No model weights were trained on them. Generated plates in the examples are new model-assisted art, labelled in each example's `PROVENANCE.md`.
