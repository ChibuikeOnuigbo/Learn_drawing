# Provenance — aura / rain / breath

- `assets/hooded-figure-chroma.png`: original AI-generated hooded figure on a chroma-green plate, created for this repository. Not a Drive frame and not an existing franchise character.
- Background, rain, aura and breath: deterministic procedural graphics in `scripts/build_drive_recreations.py` (`build_aura`). No external texture or stock footage.
- Technique reference: user's Drive `ANIME_AURA_MOTION_RESEARCH_PLAYBOOK.md` (file `14IjIsllAStFJ6SUhTlHdfm28gNL5OXah`): silhouette-derived aura behind subject, depth-banded rain, face protection, breath puff timing, premultiplied compositing.
- Differences from the playbook restaging: rain paths are evaluated continuously at 24 fps here rather than sampled at 8 Hz and interpolated; this is labelled in `aura-qa.json`. The clip is an 8-second weather ramp, **not** a seamless loop.
- Scope: graphic effects, not fluid simulation; breath/cloth are small masked 2D warps with the face protected. The keyed silhouette is an estimate from chroma keying + despill, not a hand-painted matte.
