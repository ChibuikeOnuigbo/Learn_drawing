# 4K, cleaner basketball scene

`basketball_4k.mp4` is 3840 × 2160, 16:9, 30 fps, 180 frames, H.264. All frames were decoded successfully after export. `first_frame_4k.png` is a 4K still. `cleanup_comparison.jpg` shows a same-size side-by-side of the prior scene and the new denoised/upscaled scene.

## What changed
- Used OpenCV's non-local-means color denoising on the previous 960 × 540 drawing.
- Upscaled that static drawing 4× with the pretrained FSRCNN ×4 neural super-resolution model by Saafke via OpenCV's dnn_superres. The upscaler was not trained in this session. Source: https://github.com/Saafke/FSRCNN_Tensorflow (Apache 2.0; license included). It is applied in overlapped tiles to reduce boundary artifacts.
- Upscaled the RGB of the separately predicted basketball with the same model; transparency was resized with Lanczos interpolation. Composited the ball at 4K for each frame.
- Increased ball radius from 0.12 to 0.15 scene units (25% larger in diameter) relative to the immediately preceding scale-only test. The larger size is a creative choice, not a regulation-sized basketball. The initial ball height remains 2 scene units.

## Important limits
The 4K file contains 3840 × 2160 pixels, but it is **upscaled**, not a natively drawn 4K scene. The old scene was generated from low-resolution color predictions and automatically traced strokes on a simplified, manually constructed 3D guide. Denoising and super-resolution cannot guarantee recovery of details missing from that source. The ball is a single previously predicted image moved and rotated by scripted gravity; the shadow is coded. This is not newly trained artist-like drawing or learned motion, and no new supervised or reinforcement learning was performed for this upgrade. The smoothing can remove texture or fine detail.

A larger EDSR super-resolution model was attempted but the process was killed in this environment even for a small tile; the delivered result uses FSRCNN, not EDSR or Real-ESRGAN.

## Reproduce
The upgrade package includes the two earlier drawing PNGs in `basketball_quality_v4/`, as well as the FSRCNN weights, scripts, output and license in `basketball_4k_upgrade/`. Install NumPy, Pillow and `opencv-contrib-python-headless` 4.11.x (the contrib package is required for `dnn_superres`), and FFmpeg with libx264:

```
python basketball_4k_upgrade/upscale_background.py
FFMPEG_PATH=/path/to/ffmpeg python basketball_4k_upgrade/render_4k.py
```

The scripts use a lightweight CPU-friendly video encoder setting. Visual output and video bytes can vary with library versions. The full earlier scene training project remains separately in the Google Drive folder.
