# Basketball drawing redo

## Start here
- `basketball_bounce_browser.mp4`: redone animation, 6 seconds, 30 fps, H.264.
- `redo_comparison.jpg`: an AI visualization, the approximate 3D guide, and before/after drawings.
- `drawn_gym_from_memory.png`, `drawn_gym_lines.png`, `drawn_ball_from_memory.png`: predicted drawings.
- `court_visible_3d_trace.png` and `court_learned_strokes.png`: the visible 3D-projected court-stroke teacher and the trained model's strokes.
- `references/`: the six AI-generated visualizations. They are not consistent calibrated views.
- `gym_scene.obj`/`.mtl` and `basketball_3d.obj`/`.mtl`: the manually constructed 3D models; the ball is separate.

## What changed
The previous redo produced double, broken court-marking outlines. Here, a new supervised stroke network was trained on visible centerline segments projected from the 3D court geometry instead. A depth buffer is used while constructing the training targets to hide markings behind the back wall or bleachers. At inference, the model predicts the segment endpoints and widths, and the renderer paints those predictions; it does not read the geometry or guide. Other scene strokes, ball, and the overall 3D environment are carried forward from the prior version.

A new supervised color-correction network was trained on the difference between the old guide and a 3D guide with court markings removed, so the single-stroke network can draw the markings separately. It receives coordinates at inference, not either guide. The predicted color is passed through a coded bilateral smoothing filter. The court and room remain simplified, with some imperfections and gaps.

## Evidence and limitations
- Court network: 65,000 updates, 313 visible teacher segments. The best checkpoint was selected at update 36,500. The 3-pixel F1 against the same projected paths used for training is approximately 1.000. This is in-sample memorization, not evidence of general drawing ability or artistic quality.
- Color correction: 50,000 updates, selected checkpoint 41,000. On a held-out subset of positions from the same image, error on the 1,779 automatically selected changed-area pixels fell from 0.10969 to 0.02890; overall MAE **increased** from 0.02220 to 0.02423. The validation positions were used repeatedly for checkpoint selection, and this was not an independent new scene. Results are before coded smoothing.
- `court_training_results.json`, `color_detail_v4_results.json`, and training logs contain the details.

The generated visualizations were used as references, not pasted as final artwork. The 3D scene and stroke teachers are coded/manually constructed, and the scene-specific networks use supervised training, not reinforcement learning or a forgetting function. The animation is scripted gravity with a single learned ball image moved and rotated in 2D; it does not generate newly drawn ball poses. This does not establish general artist-like drawing or learned animation.

## Reproduce
Requires Python, NumPy, OpenCV and Pillow. To render from the saved checkpoints:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python draw_and_animate.py output_folder
```

The drawing worker reads five checkpoints after imports; a Python audit hook rejects other Python-level file reads. This is not an OS security sandbox, and native-library IO is not necessarily intercepted. A separate-folder run produced byte-identical images and OpenCV video. Convert the resulting MPEG-4 Part 2 video for browsers with `ffmpeg -i basketball_bounce.mp4 -c:v libx264 -crf 18 -pix_fmt yuv420p -movflags +faststart basketball_bounce_browser.mp4`.

To rerun this redo's training, use the supplied previous checkpoints and guides: run `train_court_strokes.py` and `train_color_detail_v4.py`, then `draw_and_animate.py`. Pin BLAS threads to 1. The earlier scene-training code and checkpoints are included for inspection; see `baseline_v2/` for older files.

No pre-existing Drive files were deleted or modified.
