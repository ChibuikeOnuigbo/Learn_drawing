"""Download the Drive reference videos and bisect EVERY frame into compact index data.

Per video this writes (tracked by git):
  references/frame_index/<stem>/summary.json      - metadata, sha256, cuts, totals
  references/frame_index/<stem>/index.jsonl.gz    - one record per decoded frame
  references/frame_index/<stem>/contact-sheet.jpg - 12 evenly sampled frames

Raw videos live in data/videos/ (gitignored). The pipeline is resumable: a video
whose summary.json already reports `frames_indexed` is skipped.

Per-frame record: f (frame index), t (seconds), ph (64-bit dHash hex),
lm/ls (luma mean/std 0..1), m (mean abs diff vs previous frame, 0..1),
s (shot id), c (1 when this frame starts a new shot).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import av
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "migration/reference_drive_manifest.json"
VIDEO_DIR = ROOT / "data/videos"
OUT_DIR = ROOT / "references/frame_index"
SCAN_W = 320

CUT_THRESHOLD = 0.28  # mean abs diff on 0..1 scale


def dhash(gray: np.ndarray) -> int:
    """64-bit difference hash on a 9x8 grayscale crop."""
    small = np.asarray(Image.fromarray(gray).resize((9, 8), Image.BILINEAR), dtype=np.int16)
    bits = (small[:, 1:] > small[:, :-1]).flatten()
    value = 0
    for b in bits:
        value = (value << 1) | int(b)
    return value


def scan_video(video: Path, out: Path, meta: dict) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    records = []
    thumbs = []
    shot = 0
    prev = None
    with av.open(str(video)) as c:
        stream = c.streams.video[0]
        rate = stream.average_rate or stream.guessed_rate
        fps = float(rate) if rate else 24.0
        for n, frame in enumerate(c.decode(stream)):
            img = frame.to_image().convert("RGB")
            w, h = img.size
            nh = max(1, round(SCAN_W * h / w))
            small = np.asarray(img.resize((SCAN_W, nh), Image.BILINEAR), dtype=np.float32) / 255.0
            gray = (small @ np.array([0.299, 0.587, 0.114], dtype=np.float32)).astype(np.uint8)
            lm = float(gray.mean()) / 255.0
            ls = float(gray.std()) / 255.0
            motion = 0.0
            if prev is not None:
                motion = float(np.abs(small - prev).mean())
            prev = small
            cut = motion > CUT_THRESHOLD and n > 0
            if cut:
                shot += 1
            if n % max(1, (stream.frames or 300) // 12) == 0 and len(thumbs) < 12:
                thumbs.append((n, img.copy()))
            records.append({
                "f": n, "t": round(n / fps, 4), "ph": f"{dhash(gray):016x}",
                "lm": round(lm, 4), "ls": round(ls, 4), "m": round(motion, 4),
                "s": shot, "c": int(cut),
            })
        duration = float(stream.duration * stream.time_base) if stream.duration and stream.time_base else len(records) / fps
        width, height = stream.codec_context.width, stream.codec_context.height

    with gzip.open(out / "index.jsonl.gz", "wt", compresslevel=6) as fh:
        for r in records:
            fh.write(json.dumps(r, separators=(",", ":")) + "\n")

    if thumbs:
        sheet = Image.new("RGB", (4 * 240, ((len(thumbs) + 3) // 4) * 150), "#101820")
        draw = ImageDraw.Draw(sheet)
        for i, (n, im) in enumerate(thumbs):
            im.thumbnail((240, 135))
            x, y = i % 4 * 240, i // 4 * 150
            sheet.paste(im, (x, y))
            draw.text((x + 6, y + 136), f"f{n}", fill="white")
        sheet.save(out / "contact-sheet.jpg", quality=88)

    cuts = [r["f"] for r in records if r["c"]]
    summary = {
        "video": video.name,
        "drive_id": meta.get("id"),
        "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
        "bytes": video.stat().st_size,
        "width": width, "height": height, "fps": fps,
        "duration_seconds": round(duration, 3),
        "frames_indexed": len(records),
        "every_frame_indexed": True,
        "shots": shot + 1,
        "cut_frames": cuts[:500],
        "cut_count": len(cuts),
        "scope": "every decoded frame indexed: perceptual hash, luma stats, motion delta, shot id; sampled contact sheet",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    return summary


def main() -> int:
    entries = [f for f in json.loads(MANIFEST.read_text())["files"] if f["name"].endswith(".mp4")]
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    catalog = {"updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "videos": []}
    failures = []
    for i, entry in enumerate(entries):
        stem = Path(entry["path"]).stem
        out = OUT_DIR / stem
        summary_path = out / "summary.json"
        if summary_path.exists():
            done = json.loads(summary_path.read_text())
            if done.get("frames_indexed"):
                catalog["videos"].append(done)
                print(f"[{i+1}/{len(entries)}] skip (done): {entry['name']}", flush=True)
                continue
        video = VIDEO_DIR / entry["path"]
        local = ROOT / "google_drive" / entry["name"]
        if not video.exists() and local.exists():
            video = local
        if not video.exists() or video.stat().st_size == 0:
            failures.append({"name": entry["name"], "id": entry["id"], "error": "missing locally; connector download required"})
            print(f"  missing: {entry['name']}", flush=True)
            continue
        try:
            summary = scan_video(video, out, entry)
        except Exception as exc:
            failures.append({"name": entry["name"], "id": entry["id"], "error": f"scan: {exc}"[:300]})
            print(f"  scan failed: {exc}", flush=True)
            continue
        catalog["videos"].append(summary)
        print(f"[{i+1}/{len(entries)}] indexed {summary['frames_indexed']} frames, "
              f"{summary['shots']} shots: {entry['name']}", flush=True)

    catalog["totals"] = {
        "videos_indexed": len(catalog["videos"]),
        "frames_indexed": sum(v["frames_indexed"] for v in catalog["videos"]),
        "shots": sum(v["shots"] for v in catalog["videos"]),
        "failures": len(failures),
    }
    catalog["failures"] = failures
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "CATALOG.json").write_text(json.dumps(catalog, indent=1) + "\n")
    print("COMPLETE", json.dumps(catalog["totals"]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
