# Study of the supplied reference videos

The new Drive folder was inspected on 2026-11-14. It exposed 62 files, including 55 MP4 videos. All exposed files were downloaded from Drive, sized and SHA-256 hashed. Six frames per video were decoded with system FFmpeg: 330 samples. The original videos and study boards are retained outside Git in `/workspace/drawing-data/new-drive`. The catalog and numeric CLIP index are versioned.

The direct-reference contact sheets were visually inspected. These are sparse samples, not uninterrupted viewing, exact cut analysis, rig extraction or recovered drawing strokes. The index can locate sampled imagery; it cannot establish the complete production process or artistic quality.

| Supplied reference | Observed samples | Applied technique or remaining work |
|---|---|---|
| `X2Cv8DbygpA` | Around 120s a small desert action silhouette; 240s a bright energy mark; 408s rough/clean-up comparison panels | Pose-first construction and staged accents matter. Comparable action/effects quality remains open. |
| `Y2vDwR9rW-0` | Around 200s muted map graphics; 400s graphic pathogen shapes and a paper label; 680s hands around an object | Cohesive palettes, layered scenes and narrative visual changes. |
| `3q1KnXSD7Qg` | White-field title at the start; anime character collages around 313s, 625s and 1063s | Asset selection and composition are central even when little full-character animation is visible. |
| `6xSD11AtCqU` | Green branching intro; dense green environment around 13.8s; cel-shaded form around 27.6s; angled luminous type around 46.9s | Advanced lighting/compositing remains beyond the exercise suite. Samples do not establish the source engine. |
| `HDsziw2LuQA` | Tiny spotlighted character at 1.5s; large chibi close-up around 107.7s; expressive phone pose around 215.4s | Large readable faces, silhouette, facial changes and uncluttered staging informed the original vector character exercise. |
| `AhICirv_6lw` | Colorful character/scene changes around 91.9s, 183.7s and 312.3s | Character acting and varied shot composition require more than translating a flat sprite. |
| `92ibAh-rSLk` | Simple figures in a room, a vehicle sequence, a graphic diagram and grouped characters | Hierarchical editable parts and clear explanatory staging. |
| `3I0E21EOZu4` | Anime cutout at 1.5s; live-action reaction imagery around 309s/618s; manga panels around 1050s | Narration/visual association and local media composition. Exact audio sync was not inferred from stills. |
| `9w0_e9X4FDw` | Clean outlined wedding pose, face/hand close-up and later back-facing character | Consistent linework and identity across changing poses. The new exercise is simpler. |
| `s-n7xL8JxZE` | Room/close-up changes in the opening; transformed scene elements around 25.5s; hands at 51s; angled panels around 86.8s | Camera/layer transforms and composition. Production methods are inferred possibilities, not recovered project facts. |
| `rv0CZ919PFw` | Batman reaction imagery in the opening; a small text card around 157s; manga panels around 314s; live reaction/caption around 534s | Match a reaction to the spoken claim and topic, not just an isolated keyword. See audio excerpt below. |
| `BAYQ2W_v08s` | Low-poly character at a desk; particle/diagram panel around 122s; an insurance form around 244s; black-hole imagery around 415s | The user's “very simple” label still includes 3D assets and graphic explanation. Difficulty labels do not determine implementation cost. |
| `hCnsaahr2cc` | Brick-like 3D characters, a crowd shot, a bed scene and a large face close-up | Rigging, acting, framing and lighting need independent validation. The robot suite demonstrates foundations rather than parity. |
| `2Wv3p9WCs6M` | Limited black/gray/red palette, staged city/figures, strong light shapes and a later tiled-room composition | Large value groups and selective accents can carry explanation without constant visual noise. |
| `vNxqa8ltH20` | Character-led tutorial opening followed by a painting interface and close cropped forms | Separate the reference image, editable drawing actions and final output. |
| `OSULm_VDO04` | Stick figure at a table, money/card-like graphics and later quantity labels | Keep visual quantities and narration beats readable; use a timeline contract. |

## Audio-assisted check of the meme/editing reference

An 18-second opening excerpt of `rv0CZ919PFw` was transcribed privately using local Whisper base.en. It discusses fictional romantic partners and gives character examples. Three words were low-confidence, so the transcript is not treated as exact quotation. The opening's Batman image is therefore a contextual reaction to a spoken opinion, not evidence of a literal Batman story. This informed the semantic-intent plus story-theme approach. The excerpt was not used to train the new classifier or inserted into the public demos.

## Channel archive availability

The Zimaut progress file reports 28/28 catalog entries plus the copied direct reference. Those 29 videos were visible. Alan Becker's progress file reports 10/67, matching the visible files. No files were exposed in Remnant777's folder. Its desired style is still recorded from the user's description, not from an invented video review. The 184-entry channel CSV is an intended inventory, not a completed-download count.

## What was trained and what was reused

CLIP was reused as a pinned pretrained model to embed the samples; its weights were not updated. The new supervised reaction classifier uses original synthetic text labels. The supplied videos were not claimed as a stroke-action dataset, a general drawing curriculum that changed neural weights, or an RL training run. Broader animation skill still requires authored production, review, and more suitable learning data.
