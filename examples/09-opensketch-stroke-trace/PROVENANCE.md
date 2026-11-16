# Provenance — OpenSketch stroke trace

- Source drawing: `assets/open-sketch/Professional1_house_view1_concept.svg` (bundled in the repository root `assets/open-sketch/`), one human-drawn product-design sketch from **OpenSketch**, Gryaditskaya et al. (2019), **CC0 1.0**. Project: <https://repo-sam.inria.fr/d3/OpenSketch/>. Drive copy: file `1NfMF6iJJwi7gLMRxFo3i1fWl78Abot5H`.
- The trace phase replays the SVG path geometry in file order. SVG path order is **not** a recording of actual stylus timing, pressure or eraser events; it is a replay of stored geometry.
- The red phase is a **derived geometric twist variant** authored for this example, explicitly labelled "not original" on every frame. It is not a model prediction and not the human drawing.
- Scope: human product-design linework, not character/face animation. The prior Drive stroke-MLP experiment (file `13640cJ04nqh90qFIJQjnzsct3bIn-fpx`) lost to a linear baseline on unseen houses; no model weights from it are used or bundled here.
