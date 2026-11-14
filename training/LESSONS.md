# Verified production lessons

## Speech and reaction timing

Use actual word events when synthesizing test speech. Word-count estimates drift because sentence lengths differ. Place the visual on the semantic punchline, and preserve evidence of the selected word, timestamp and output frame.

Whisper base.en recovered the required reaction phrases in the generated tests, but word starts are estimates and can differ from synthesis events. Short speech sometimes loses the plural s in “brains”; semantic matching accepts the singular variant and keeps a real audio-timing regression. The brain-erase cue is anchored to the final word of “No brain(s) at all” so the verbal setup lands before the visual gag. Low confidence and ASR-based sync remain flagged for review.

A literal medical/scientific brain reference should abstain rather than use a stupidity gag. The classifier's raw fixed holdout score is 19/20; explicit negation handling is an editorial guard, not learned language understanding. The bundled library is small, not a universal best-meme oracle. The old sleeping-brain still was semantically wrong for “no brains at all”; it was replaced with the verified Squidward eraser GIF. GIF disposal and frame durations must be respected; the source's blank upper canvas was cropped without changing timing.

## Rendering portability

CairoSVG/cairocffi required system Cairo and failed in the headless sandbox. Replacing them with `resvg-py` plus bundled Inter/Space Grotesk fonts removed that dependency; the 2D pipeline tests pass without Cairo. Do not reintroduce cairocffi for SVG rasterization.

`bpy` conflicts with the project's NumPy 2.x requirement. Keep Blender/bpy in an isolated environment or use a real Blender executable. The project venv should not contain bpy. The trusted launcher runs the validated worker without accepting arbitrary client code.

## Video decoding and reference study

Pip OpenCV could not decode the supplied AV1 references. PyAV/libdav1d succeeded; `scripts/research/analyze_drive.py` uses it. The dense scan produced 2,805 timestamped samples across 55 files. Short files also received every-adjacent-frame change measurements; longer files are explicitly sparse-sample only. Cut candidates are not semantic shot labels. No file was obtained from YouTube directly in this rebuild.

CLIP searches sampled frames and can misrank stylistic queries. It does not recover animation rigs, brush paths or a creator's production process. The video files were not used to fine-tune CLIP or a generative drawing model. The bundled CLIP index remains 330 samples; the denser scan is study provenance, not a claimed rebuilt embedding index.

## 2D and editing

Nested groups keep eyes, hair, hands and other parts attached during pose changes. Independent X/Y scaling enables blinks without shrinking the entire eye uniformly. Parent visibility must propagate to children; the renderer has an image-level regression for this. Frame-token image assets (`%04d`) support pre-rasterized rig sequences and have a regression test.

Equal-quarter acting beats did not align with narration sentences. Character exercises should retime beats to speech events. A clean visual master prevents duplicated burned captions. Explicit final-frame holds let a shot remain readable through a longer narration segment without silently truncating audio.

## 3D rigging

The humanoid uses 15 actual bones, 5,994 weighted mesh vertices and four IK chains. Foot orientation needs its own control so shin rotations do not point the feet into the floor. Measured floor minima, IK target error and attachment errors are in each rig report. The simple wave measured max IK target error ≈0.000145 and minimum foot vertex z ≈0.0. The prop follows the evaluated hand after grasp; this is baked procedural animation, not a learned manipulation policy or physics simulation.

Art direction matters: a primitive on a gray void is not a finished scene. Modeled sets, beveled materials, area lights, camera coverage and color contrast make the rig readable. Blender 4.5 Cycles CPU denoising succeeded in the isolated environment; earlier missing-denoiser failures were environment-specific. Still inspect low-sample renders for grain and do not claim a denoiser ran unless the log/output supports it.

## Learning scope

Repeated renders and these notes improve reproducible workflows, not neural weights. The small supervised narration-intent classifier is the only project-trained model in this iteration. General drawing-policy training, advanced character animation and reinforcement learning remain separate research work requiring appropriate data, models and evaluation.
