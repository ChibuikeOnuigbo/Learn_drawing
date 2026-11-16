# NothingxArt: drawing-process study and training experiment

Artist/channel: [NothingxArt](https://www.youtube.com/@Nothingxart/shorts). Study prepared for improving the basketball drawing workflow. The artist owns their work; the right to watch or download is not automatically permission to train on or redistribute it. Confirm appropriate permission or other applicable rights before using these clips for a public/commercial drawing model.

## What was collected and checked

- The Shorts listing contained **185 items**. All 185 videos were downloaded and stored in the user's Drive as a single private study archive, plus their public thumbnails. At collection time all 185 local videos existed and 185 files passed ZIP CRC checks.
- OpenCV successfully decoded **six sampled frames per video**, at approximately 8%, 24%, 40%, 56%, 72% and 88% of its duration. These are samples, not a frame-by-frame or audio analysis. Twenty sampled timelines were assembled for visual review; five timelines were inspected in more detail. Captions or actions between samples can be missed.
- The spreadsheet gives a **thumbnail-derived working title and proposed study target for every item**, a link to the original, times of sampled video frames, and OpenCV screen-change measurements. Those proposed lessons have NOT each been validated by watching the whole Short. Whole-screen changes are not brush strokes. The existing thumbnail-only catalog must not be mistaken for video narration.
- Sometimes a thumbnail title and an intermediate video stage appear different. For example, the thumbnail-derived title for `ajqhisQoP7g` mentions a tree, while sampled frames show a colorful ring/celestial motif during editing. Treat the per-item names as provisional and verify against the complete video.

## Grounded observations from sampled videos

Times below are sampled timestamps, not guaranteed start or end times of a stroke. They are observations of edits and visible stages, not recovered artist brush paths.

1. [Night Sky / meteor shower](https://www.youtube.com/shorts/uFTaTY1eT8c): around 2.27 seconds a dark horizontal landscape is present; later samples show tool/interface activity and, by around 25.13 seconds, multiple bright diagonal streaks across the sky. **Exercise:** establish a broad dark value field and distant silhouette first, then place a small number of directional bright accents. Do not assert the exact brush or stroke order from sparse samples.
2. [Last Sunset](https://www.youtube.com/shorts/ajqhisQoP7g): the 7.63–22.93 second samples show a ring motif being adjusted and becoming more colorful; the later sampled frame shifts to a softer pink glow. **Exercise:** separate the large warm/cool color regions from the small high-contrast focal form and compare readability at thumbnail size. Changes may include zooms, effects and edits.
3. [Morning landscape](https://www.youtube.com/shorts/W52Klsq-JuE): sampled stages progress from a broad blue field around 1.50 seconds to pale terrain and darker tree-like silhouettes, then a warm horizon by around 16.77 seconds. **Exercise:** block large sky and ground masses, reserve crisp silhouette details for focal areas, and check the warm horizon against cool surroundings. Sparse samples do not prove every mark was made in that order.
4. [Tree and night sky](https://www.youtube.com/shorts/3v3_3WAbnks): the early sample contains dark sky and a tree silhouette; by later sampled frames, small pink/purple light details are visible in the sky. **Exercise:** preserve a clear silhouette before adding selective color texture; avoid evenly distributing noisy detail.
5. [Pink city/eclipse](https://www.youtube.com/shorts/IHttW8k_Bog): early samples show simplified dark building forms against magenta; later samples show a luminous circular focal area. **Exercise:** compare the readability of big structural masses and the focal light separately, before adding small window highlights.

## Training performed: temporal-order recognition, not drawing

An OpenCV feature extractor and two small logistic-regression classifiers were trained to answer a limited question: **which of two sampled video frames came later?** Three frame pairs per video were used in both presentation orders. The split was by entire video: 138 training videos and 47 held-out videos, without overlap. On 282 ordered pair examples from held-out videos:

- Full-screen model: **86.5%** accuracy.
- Fixed-center-crop model: **86.5%** accuracy; that crop is not a validated canvas mask.
- A brightness-only model: **59.6%**; balanced chance baseline: **50%**.
- One fixed split only. Similar templates, editing UI, captions, zooms, fades, presentation cuts, or final-screen layout may provide shortcuts; the evaluation does not remove these confounds. The two orders of each frame pair are correlated, so 282 examples do not imply 282 independent clips.

This is **not** a GAN, reinforcement learning, a drawing model, stroke recovery, or evidence the system can produce better artwork. A classifier can learn video editing conventions without learning how to draw. There was no artist-like drawing test and no new basketball render in this experiment. The classifier files are saved only as research artifacts. `video_order_evaluation.json` records the split and additional pair-type results; `video_stage_experiment.py` reproduces it when the videos and dependencies are present.

## How this can actually improve the basketball project

1. Produce 4–10 visual references and a coherent environment guide, as requested; those are references, not the system's drawing.
2. Secure suitable training rights and collect real **time-ordered, human-made strokes**, preferably actual stroke coordinates/layers with linked final images. Screen recordings alone require careful canvas stabilization, UI removal and hand-verified intermediate stages; edits are not necessarily strokes.
3. Label coarse-to-fine stage transitions and deliberately exclude repeated near-identical scenes across train/test. Test on entirely unseen scenes and creators; use a fixed held-out set, not the training reference.
4. Train an actual drawing policy that emits editable strokes and color/paint actions on a canvas. If a GAN is tested, treat it as an optional realism critic—not proof of stroke knowledge or an automatic quality upgrade. Measure generalization and inspect action sequences rather than only judging pixels.
5. Compare generated drawings blind against human drawings and unseen reference layouts: perspective, scale, clean silhouette, value grouping, deliberate texture, focal light, and unwanted noise. For motion, compare new frames for consistency and ball scale separately. Only proceed to a full basketball remake after these checks show improvement.

## Files

- `results/NothingxArt_Video_Study_Catalog.xlsx`: all 185 provisional titles, links, sampled times and video measurements.
- `results/video_frame_measurements.json`: per-item timestamps, brightness, edge density and adjacent-sample change.
- `boards/video_first20_samples.jpg` and `boards/video_sample_timelines.jpg`: sampled-frame review sheets.
- `results/video_order_evaluation.json` and `results/video_order_*model.joblib`: limited frame-order experiment.
- The Drive archive of videos is for private study; it is not a rights grant. Cookies and credential logs are not included.
