# Reference evidence

## Current

- [DRIVE_SCAN.json](DRIVE_SCAN.json): measured scan of 55 supplied Drive videos, 2,805 timestamped visual samples, checksums and explicit decode scope.
- [STUDY_REBUILD.md](STUDY_REBUILD.md): reviewed contact-board observations and the mechanics applied to original examples. This is not a claim of uninterrupted viewing or model training.
- [manifests/](manifests/): historical Drive download/checksum manifests used by the optional restoration utility. They describe files observed at collection time, not guaranteed current availability.

The 2.2 GB local mirror and generated study boards are intentionally outside Git (`google_drive/`, `.work/`). Their absence does not invalidate the committed scan record, but search/review requiring actual media needs the files restored with permission.

## Archive

[archive/](archive/) preserves earlier channel inventories, sparse-sample catalogs, upload reports, drawing experiments and the old user-authored standards. They are provenance, **not active agent instructions**. The current contract is `skills/animation-director/SKILL.md`.

Old counts and paths can differ from the current scan. Prefer the current manifest and code; do not infer that a historical “downloaded” status means a file exists in this checkout. Third-party study access is not permission to redistribute or train on the work.

## Reproduce a scan

Install the research extra and use `scripts/research/analyze_drive.py` with a local, authorized media folder. It uses PyAV/libdav1d; the retired OpenCV sampler failed on the supplied AV1 files. See [scripts/README.md](../scripts/README.md).
