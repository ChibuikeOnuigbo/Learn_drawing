"""Frame-by-frame video tracing: persistent point tracks, contours and insert provenance.

This is deterministic computer vision, not model training. Every decoded frame
receives an index record. Confirmed meme/insert ranges are excluded from geometry
and carry origin evidence; unconfirmed static inserts are flagged for review.
Optical-flow tracks are sparse image features, not recovered brush strokes or rigs.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Callable

import numpy as np

try:
    import av
    import cv2
except ImportError:  # optional research extra; catalog/frame reads still work without decoders
    av = None
    cv2 = None
from PIL import Image, ImageDraw, ImageFont

PACKAGE = Path(__file__).resolve().parent
STATUS_TRACED = 0
STATUS_EXCLUDED = 1
STATUS_INSERT_CANDIDATE = 2
FONT = PACKAGE / "assets/fonts/inter-400.ttf"


def library_root(workspace: Path | None = None) -> Path:
    if os.environ.get("ANIMATION_TRACE_LIBRARY"):
        return Path(os.environ["ANIMATION_TRACE_LIBRARY"]).resolve()
    base = Path(workspace) if workspace else Path(os.environ.get("ANIMATION_WORKSPACE", os.getcwd()))
    return (base / "data/traces").resolve()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def phash(gray: np.ndarray) -> int:
    small = cv2.resize(gray, (32, 32), interpolation=cv2.INTER_AREA).astype(np.float32)
    dct = cv2.dct(small)[:8, :8]
    values = dct.ravel()[1:]
    bits = values > np.median(values)
    result = 0
    for bit in bits:
        result = (result << 1) | int(bit)
    return result


def hamming(a: int, b: int) -> int:
    return int(a ^ b).bit_count()


def default_meme_catalog() -> list[dict]:
    path = PACKAGE / "models/meme-origins.json"
    if not path.exists():
        return []
    return json.loads(path.read_text()).get("entries", [])


def _load_annotations(path: Path | None) -> list[dict]:
    if not path:
        return []
    data = json.loads(path.read_text())
    ranges = data.get("ranges", data if isinstance(data, list) else [])
    for r in ranges:
        if not (0 <= int(r["start_frame"]) < int(r["end_frame"])):
            raise ValueError("Annotation ranges must be half-open with start < end")
        if r.get("origin") and not r["origin"].get("source_url"):
            raise ValueError("A claimed origin needs source_url evidence")
    return ranges


def _annotation_for(frame: int, ranges: list[dict]) -> dict | None:
    for r in ranges:
        if r["start_frame"] <= frame < r["end_frame"]:
            return r
    return None


def _catalog_match(h: int, catalog: list[dict], threshold: int) -> dict | None:
    best = None
    for entry in catalog:
        for known in entry.get("phashes", []):
            d = hamming(h, int(known))
            if d <= threshold and (best is None or d < best[0]):
                best = (d, entry)
    if best is None:
        return None
    d, entry = best
    return {"catalog_id": entry["id"], "label": entry["label"], "source_url": entry["source_url"],
            "origin_status": entry.get("origin_status", "template-match"),
            "hamming_distance": d, "evidence": entry.get("evidence", "perceptual hash match against local catalog")}


def _seed(gray: np.ndarray, existing: np.ndarray | None, count: int, min_distance: int) -> np.ndarray:
    if count <= 0:
        return np.empty((0, 1, 2), np.float32)
    mask = np.full(gray.shape, 255, np.uint8)
    if existing is not None and len(existing):
        for x, y in existing.reshape(-1, 2):
            cv2.circle(mask, (int(round(x)), int(round(y))), min_distance, 0, -1)
    pts = cv2.goodFeaturesToTrack(gray, count, 0.01, min_distance, mask=mask, blockSize=7)
    return pts if pts is not None else np.empty((0, 1, 2), np.float32)


def _contours(gray: np.ndarray, max_contours: int, max_points: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    med = float(np.median(gray))
    lo = int(max(10, 0.66 * med))
    hi = int(min(255, max(lo + 20, 1.33 * med)))
    edges = cv2.Canny(gray, lo, hi)
    found, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    scored = []
    for c in found:
        if len(c) < 3:
            continue
        length = cv2.arcLength(c, True)
        if length < 12:
            continue
        scored.append((length, c))
    scored.sort(key=lambda item: item[0], reverse=True)
    points, offsets, closed = [], [0], []
    for _, c in scored[:max_contours]:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, max(0.75, 0.002 * peri), True).reshape(-1, 2)
        if len(approx) > max_points:
            idx = np.linspace(0, len(approx) - 1, max_points).round().astype(int)
            approx = approx[idx]
        if len(approx) < 3:
            continue
        points.append(approx.astype(np.float32))
        offsets.append(offsets[-1] + len(approx))
        closed.append(1)
    if not points:
        return np.empty((0, 2), np.float32), np.asarray([0], np.int32), np.empty((0,), np.uint8)
    return np.concatenate(points), np.asarray(offsets, np.int32), np.asarray(closed, np.uint8)


def _flush(chunk_dir: Path, chunk_index: int, rows: list[dict]) -> dict:
    arrays = {
        "frame_index": np.asarray([r["frame"] for r in rows], np.int32),
        "time": np.asarray([r["time"] for r in rows], np.float64),
        "shot_id": np.asarray([r["shot"] for r in rows], np.int32),
        "status": np.asarray([r["status"] for r in rows], np.uint8),
        "phash": np.asarray([r["phash"] for r in rows], np.uint64),
        "point_count": np.asarray([len(r["points"]) for r in rows], np.uint16),
        "contour_count": np.asarray([len(r["contour_closed"]) for r in rows], np.uint16),
        "motion": np.asarray([r["motion"] for r in rows], np.float32),
        "luma": np.asarray([r["luma"] for r in rows], np.float32),
        "edge_density": np.asarray([r["edge_density"] for r in rows], np.float32),
        "saturation": np.asarray([r["saturation"] for r in rows], np.float32),
    }
    point_offsets, contour_offsets, contour_meta_offsets = [0], [0], [0]
    all_points, all_ids, all_conf, all_vel, all_contours, all_closed = [], [], [], [], [], []
    origins = []
    for r in rows:
        all_points.append(r["points"]); all_ids.append(r["ids"]); all_conf.append(r["confidence"]); all_vel.append(r["velocity"])
        point_offsets.append(point_offsets[-1] + len(r["points"]))
        all_contours.append(r["contours"]); all_closed.append(r["contour_closed"])
        contour_offsets.append(contour_offsets[-1] + len(r["contours"]))
        contour_meta_offsets.append(contour_meta_offsets[-1] + len(r["contour_closed"]))
        origins.append(json.dumps(r.get("origin"), separators=(",", ":")) if r.get("origin") else "")
    arrays.update({
        "points": np.concatenate(all_points) if all_points else np.empty((0, 2), np.float32),
        "track_ids": np.concatenate(all_ids) if all_ids else np.empty((0,), np.int32),
        "confidence": np.concatenate(all_conf) if all_conf else np.empty((0,), np.float32),
        "velocity": np.concatenate(all_vel) if all_vel else np.empty((0, 2), np.float32),
        "point_offsets": np.asarray(point_offsets, np.int32),
        "contours": np.concatenate(all_contours) if all_contours else np.empty((0, 2), np.float32),
        "contour_closed": np.concatenate(all_closed) if all_closed else np.empty((0,), np.uint8),
        "contour_offsets": np.asarray(contour_offsets, np.int32),
        "contour_meta_offsets": np.asarray(contour_meta_offsets, np.int32),
        "origin_json": np.asarray(origins, dtype=str),
    })
    path = chunk_dir / f"frames-{chunk_index:05d}.npz"
    np.savez_compressed(path, **arrays)
    return {"file": path.name, "start_frame": int(arrays["frame_index"][0]),
            "end_frame": int(arrays["frame_index"][-1]) + 1, "frames": len(rows), "bytes": path.stat().st_size}


def trace_video(path: Path, out_dir: Path, *, video_id: str | None = None, drive_id: str | None = None,
                youtube_url: str | None = None, analysis_width: int = 480, max_tracks: int = 192,
                max_contours: int = 48, max_contour_points: int = 128, chunk_size: int = 256,
                cut_threshold: float = 30.0, fb_tolerance: float = 1.5,
                annotations: Path | None = None, meme_catalog: list[dict] | None = None,
                hash_threshold: int = 10, progress: Callable[[int, int], None] | None = None) -> dict:
    if av is None or cv2 is None:
        raise RuntimeError("Tracing requires the research extra: pip install -e '.[research]' (PyAV + OpenCV)")
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    if not (160 <= analysis_width <= 960 and 16 <= max_tracks <= 512 and chunk_size >= 16):
        raise ValueError("analysis_width 160–960, max_tracks 16–512, chunk_size >=16")
    out_dir = Path(out_dir).resolve()
    if out_dir.exists() and (out_dir / "manifest.json").exists():
        raise FileExistsError(f"Trace already exists at {out_dir}; use a new versioned directory")
    out_dir.mkdir(parents=True, exist_ok=True)
    chunk_dir = out_dir / "chunks"; chunk_dir.mkdir()
    review_dir = out_dir / "review"; review_dir.mkdir()
    ranges = _load_annotations(annotations)
    catalog = default_meme_catalog() if meme_catalog is None else meme_catalog
    vid = video_id or path.stem
    container = av.open(str(path))
    stream = container.streams.video[0]
    stream.thread_type = "AUTO"
    stream.codec_context.thread_count = 2
    fps = float(stream.average_rate or stream.guessed_rate or 24)
    width, height = stream.codec_context.width, stream.codec_context.height
    duration = float(stream.duration * stream.time_base) if stream.duration else None
    expected = stream.frames or (round(duration * fps) if duration else 0)
    aw = analysis_width
    ah = max(2, round(height * aw / width / 2) * 2)
    prev_gray = None
    prev_pts = None
    prev_ids: list[int] = []
    next_id = 0
    shot = 0
    cuts = []
    rows = []
    chunks = []
    decoded = 0
    excluded = 0
    review_tiles = []
    histogram = np.zeros((8, 8, 8), np.float64)
    sums = {"luma": 0.0, "edge_density": 0.0, "saturation": 0.0}
    recent_delta: list[float] = []
    shot_motion: dict[int, list[float]] = {}
    font = ImageFont.truetype(str(FONT), 13) if FONT.exists() else ImageFont.load_default()
    try:
        for frame in container.decode(stream):
            idx = decoded
            rgb = frame.to_ndarray(format="rgb24")
            small = cv2.resize(rgb, (aw, ah), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
            time = float(frame.pts * stream.time_base) if frame.pts is not None else idx / fps
            h = phash(gray)
            delta = float(np.mean(cv2.absdiff(gray, prev_gray))) if prev_gray is not None else 0.0
            recent_delta.append(delta)
            if len(recent_delta) > 120:
                recent_delta.pop(0)
            adaptive = max(cut_threshold, 5.0 * float(np.median(recent_delta)))
            is_cut = prev_gray is not None and delta > adaptive
            if is_cut:
                cuts.append({"frame": idx, "time": time, "mean_absolute_delta": delta, "threshold": adaptive})
                shot += 1
                prev_pts = None
                prev_ids = []
            annotation = _annotation_for(idx, ranges)
            match = _catalog_match(h, catalog, hash_threshold) if annotation is None else None
            origin = None
            status = STATUS_TRACED
            if annotation is not None:
                status = STATUS_EXCLUDED
                origin = {"kind": annotation.get("kind", "insert"), "label": annotation.get("label", "annotated insert"),
                          "origin_status": "confirmed-by-annotation" if annotation.get("origin") else "excluded-without-origin",
                          **(annotation.get("origin") or {}), "evidence": annotation.get("evidence", "caller-supplied frame range")}
            elif match is not None and match.get("origin_status") in {"confirmed", "catalog-confirmed"}:
                status = STATUS_EXCLUDED
                origin = {"kind": "meme", **match}
            if status == STATUS_EXCLUDED:
                points = np.empty((0, 2), np.float32); ids = np.empty((0,), np.int32)
                conf = np.empty((0,), np.float32); vel = np.empty((0, 2), np.float32)
                contours = np.empty((0, 2), np.float32); closed = np.empty((0,), np.uint8)
                motion = np.zeros(3, np.float32)
                prev_pts = None; prev_ids = []
                excluded += 1
            else:
                if prev_gray is None or prev_pts is None or len(prev_pts) == 0:
                    curr = _seed(gray, None, max_tracks, 6)
                    curr_ids = list(range(next_id, next_id + len(curr))); next_id += len(curr)
                    conf = np.ones(len(curr), np.float32)
                    vel = np.zeros((len(curr), 2), np.float32)
                else:
                    nxt, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, prev_pts, None, winSize=(15, 15), maxLevel=3,
                                                            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))
                    back, st2, _ = cv2.calcOpticalFlowPyrLK(gray, prev_gray, nxt, None, winSize=(15, 15), maxLevel=3,
                                                           criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03))
                    fb = np.linalg.norm(back - prev_pts, axis=2).ravel()
                    ok = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < fb_tolerance)
                    xy = nxt.reshape(-1, 2)
                    ok &= (xy[:, 0] >= 1) & (xy[:, 0] < aw - 1) & (xy[:, 1] >= 1) & (xy[:, 1] < ah - 1)
                    curr = nxt[ok]
                    curr_ids = [i for i, keep in zip(prev_ids, ok) if keep]
                    conf = np.exp(-fb[ok] / max(fb_tolerance, 1e-6)).astype(np.float32)
                    vel = (curr.reshape(-1, 2) - prev_pts.reshape(-1, 2)[ok]).astype(np.float32)
                    missing = max_tracks - len(curr)
                    if missing > 0:
                        fresh = _seed(gray, curr, missing, 6)
                        if len(fresh):
                            new_ids = list(range(next_id, next_id + len(fresh))); next_id += len(fresh)
                            curr = np.concatenate([curr, fresh]) if len(curr) else fresh
                            curr_ids += new_ids
                            conf = np.concatenate([conf, np.ones(len(fresh), np.float32)])
                            vel = np.concatenate([vel, np.zeros((len(fresh), 2), np.float32)])
                points = curr.reshape(-1, 2).astype(np.float32)
                ids = np.asarray(curr_ids, np.int32)
                contours, contour_offsets, closed = _contours(gray, max_contours, max_contour_points)
                # Store contour offsets per frame by splitting concatenated points.
                motion = np.asarray([float(vel[:, 0].mean()) if len(vel) else 0.0,
                                     float(vel[:, 1].mean()) if len(vel) else 0.0,
                                     float(np.linalg.norm(vel, axis=1).mean()) if len(vel) else 0.0], np.float32)
                prev_pts = curr if len(curr) else None
                prev_ids = curr_ids
            hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV)
            luma = float(gray.mean())
            edge_density = float((cv2.Canny(gray, 60, 160) > 0).mean())
            saturation = float(hsv[:, :, 1].mean()) / 255.0
            quant = (small >> 5).astype(np.int32)
            np.add.at(histogram, (quant[:, :, 0], quant[:, :, 1], quant[:, :, 2]), 1)
            shot_motion.setdefault(shot, []).append(float(motion[2]))
            sums["luma"] += luma; sums["edge_density"] += edge_density; sums["saturation"] += saturation
            row = {"frame": idx, "time": time, "shot": shot, "status": status, "phash": h,
                   "points": points / np.asarray([aw, ah], np.float32), "ids": ids, "confidence": conf,
                   "velocity": vel / np.asarray([aw, ah], np.float32), "contours": contours / np.asarray([aw, ah], np.float32),
                   "contour_closed": closed, "motion": motion, "luma": luma, "edge_density": edge_density,
                   "saturation": saturation, "origin": origin}
            rows.append(row)
            if len(rows) >= chunk_size:
                chunks.append(_flush(chunk_dir, len(chunks), rows)); rows = []
            if idx % max(1, expected // 24 if expected else 30) == 0 or status == STATUS_EXCLUDED:
                if len(review_tiles) < 48:
                    im = Image.fromarray(small).convert("RGB")
                    tile = Image.new("RGB", (256, 170), "#101827")
                    im.thumbnail((256, 144))
                    tile.paste(im, ((256 - im.width) // 2, 0))
                    label = f"f{idx} {time:.2f}s shot{shot}" + (" EXCLUDED" if status == STATUS_EXCLUDED else "")
                    ImageDraw.Draw(tile).text((6, 148), label[:36], font=font, fill="#dbeafe")
                    review_tiles.append(tile)
            prev_gray = gray
            decoded += 1
            if progress and decoded % 300 == 0:
                progress(decoded, expected)
        if rows:
            chunks.append(_flush(chunk_dir, len(chunks), rows))
    finally:
        container.close()
    if expected and decoded != expected:
        raise RuntimeError(f"Decoded {decoded} frames but stream reported {expected}; trace is incomplete")
    # Static-shot insert candidates are review flags, not automatic exclusions.
    candidates = []
    for sid, values in shot_motion.items():
        if len(values) >= max(8, round(fps * 0.4)) and float(np.median(values)) < 0.12:
            candidates.append({"shot_id": sid, "frames": len(values), "median_motion": float(np.median(values)),
                               "reason": "low-motion shot; possible inserted still/meme; review before excluding"})
    if candidates:
        _mark_candidates(chunk_dir, chunks, candidates)
    palette = []
    flat = histogram.ravel()
    for idx in np.argsort(flat)[::-1][:8]:
        if flat[idx] <= 0:
            continue
        r, g, b = np.unravel_index(idx, histogram.shape)
        palette.append({"rgb": [int(r * 32 + 16), int(g * 32 + 16), int(b * 32 + 16)],
                        "share": float(flat[idx] / flat.sum())})
    sheet = Image.new("RGB", (6 * 256, math.ceil(len(review_tiles) / 6) * 170 + 40), "#101827")
    draw = ImageDraw.Draw(sheet)
    draw.text((10, 10), f"{vid} — {decoded} frames decoded; {excluded} excluded", font=font, fill="white")
    for i, tile in enumerate(review_tiles):
        sheet.paste(tile, ((i % 6) * 256, 40 + (i // 6) * 170))
    sheet.save(review_dir / "contact-sheet.jpg", quality=88)
    motions = np.asarray([m for vals in shot_motion.values() for m in vals], np.float32)
    style = {"palette": palette, "mean_luma": sums["luma"] / max(1, decoded),
             "mean_edge_density": sums["edge_density"] / max(1, decoded),
             "mean_saturation": sums["saturation"] / max(1, decoded),
             "motion_median": float(np.median(motions)) if len(motions) else 0.0,
             "motion_p90": float(np.percentile(motions, 90)) if len(motions) else 0.0,
             "shot_count": shot + 1, "mean_shot_frames": decoded / max(1, shot + 1),
             "scope": "Measured image statistics; style tags require human/agent review of actual frames."}
    manifest = {"schema": 1, "video_id": vid, "source": {"file": path.name, "sha256": sha256(path), "bytes": path.stat().st_size,
                                                         "drive_id": drive_id, "youtube_url": youtube_url,
                                                         "width": width, "height": height, "fps": fps, "duration": duration,
                                                         "codec": stream.codec_context.name},
                "analysis": {"width": aw, "height": ah, "max_tracks": max_tracks, "max_contours": max_contours,
                             "max_contour_points": max_contour_points, "chunk_size": chunk_size,
                             "cut_threshold": cut_threshold, "fb_tolerance": fb_tolerance,
                             "coordinates": "normalized to analysis frame; multiply by source width/height for pixels"},
                "coverage": {"expected_frames": expected, "decoded_frames": decoded, "traced_frames": decoded - excluded,
                             "excluded_frames": excluded, "every_frame_indexed": True,
                             "scope": "Every decoded frame has a record; sparse tracks/contours are image evidence, not recovered vector artwork."},
                "shots": [{"shot_id": sid, "frames": len(vals)} for sid, vals in shot_motion.items()],
                "cuts": cuts, "insert_candidates": candidates, "chunks": chunks, "style": style,
                "annotations_file": str(annotations) if annotations else None,
                "review": {"contact_sheet": "review/contact-sheet.jpg", "status": "pending visual review"}}
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    _update_catalog(out_dir.parent, manifest)
    return manifest


def _iter_rows(chunk_dir: Path, chunks: list[dict]):
    for chunk in chunks:
        with np.load(chunk_dir / chunk["file"], allow_pickle=False) as z:
            for i in range(len(z["frame_index"])):
                yield {k: z[k][i] for k in ("frame_index", "luma", "edge_density", "saturation")}


def _mark_candidates(chunk_dir: Path, chunks: list[dict], candidates: list[dict]) -> None:
    shots = {c["shot_id"] for c in candidates}
    for chunk in chunks:
        path = chunk_dir / chunk["file"]
        with np.load(path, allow_pickle=False) as z:
            data = {k: z[k] for k in z.files}
        mask = np.isin(data["shot_id"], list(shots)) & (data["status"] == STATUS_TRACED)
        if mask.any():
            data["status"][mask] = STATUS_INSERT_CANDIDATE
            np.savez_compressed(path, **data)


def _update_catalog(library: Path, manifest: dict) -> None:
    library.mkdir(parents=True, exist_ok=True)
    path = library / "catalog.json"
    catalog = json.loads(path.read_text()) if path.exists() else {"schema": 1, "videos": {}}
    catalog["videos"][manifest["video_id"]] = {
        "manifest": str(Path(manifest["video_id"]) / "manifest.json"),
        "source": manifest["source"], "coverage": manifest["coverage"],
        "style": manifest["style"], "insert_candidates": len(manifest["insert_candidates"]),
    }
    path.write_text(json.dumps(catalog, indent=2) + "\n")


def read_catalog(workspace: Path | None = None) -> dict:
    root = library_root(workspace)
    path = root / "catalog.json"
    if not path.exists():
        return {"schema": 1, "root": str(root), "videos": {}, "note": "No traces built yet. Run scripts/build_trace_library.py on authorized local videos."}
    data = json.loads(path.read_text())
    data["root"] = str(root)
    return data


def _load_manifest(video_id: str, workspace: Path | None = None) -> tuple[Path, dict]:
    if "/" in video_id or ".." in video_id:
        raise ValueError("Invalid video id")
    root = library_root(workspace)
    path = root / video_id / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"No trace for {video_id!r}; build it first")
    return path.parent, json.loads(path.read_text())


def get_frame(video_id: str, frame: int, workspace: Path | None = None) -> dict:
    root, manifest = _load_manifest(video_id, workspace)
    if not 0 <= frame < manifest["coverage"]["decoded_frames"]:
        raise ValueError("Frame outside trace")
    chunk = next(c for c in manifest["chunks"] if c["start_frame"] <= frame < c["end_frame"])
    with np.load(root / "chunks" / chunk["file"], allow_pickle=False) as z:
        i = frame - int(chunk["start_frame"])
        po = z["point_offsets"]; co = z["contour_offsets"]; cm = z["contour_meta_offsets"]
        start = int(co[i]); end = int(co[i + 1])
        cstart = int(cm[i]); cend = int(cm[i + 1])
        origin = z["origin_json"][i]
        result = {"video_id": video_id, "frame": frame, "time": float(z["time"][i]), "shot_id": int(z["shot_id"][i]),
                  "status": int(z["status"][i]), "phash": int(z["phash"][i]),
                  "points": z["points"][po[i]:po[i + 1]].tolist(), "track_ids": z["track_ids"][po[i]:po[i + 1]].tolist(),
                  "confidence": z["confidence"][po[i]:po[i + 1]].tolist(),
                  "velocity": z["velocity"][po[i]:po[i + 1]].tolist(),
                  "contours": z["contours"][start:end].tolist(), "contour_closed": z["contour_closed"][cstart:cend].tolist(),
                  "motion": z["motion"][i].tolist(), "origin": json.loads(origin) if origin else None,
                  "coordinate_space": manifest["analysis"]["coordinates"]}
    return result


def get_track(video_id: str, track_id: int, start_frame: int = 0, end_frame: int | None = None,
              workspace: Path | None = None) -> dict:
    root, manifest = _load_manifest(video_id, workspace)
    end = manifest["coverage"]["decoded_frames"] if end_frame is None else end_frame
    if not 0 <= start_frame < end <= manifest["coverage"]["decoded_frames"]:
        raise ValueError("Invalid frame range")
    if end - start_frame > 20000:
        raise ValueError("Track query limited to 20000 frames")
    samples = []
    for chunk in manifest["chunks"]:
        if chunk["end_frame"] <= start_frame or chunk["start_frame"] >= end:
            continue
        with np.load(root / "chunks" / chunk["file"], allow_pickle=False) as z:
            for i in range(len(z["frame_index"])):
                frame = int(z["frame_index"][i])
                if not start_frame <= frame < end or z["status"][i] == STATUS_EXCLUDED:
                    continue
                po = z["point_offsets"]
                ids = z["track_ids"][po[i]:po[i + 1]]
                hit = np.flatnonzero(ids == track_id)
                if len(hit):
                    j = int(hit[0])
                    samples.append({"frame": frame, "time": float(z["time"][i]),
                                    "point": z["points"][po[i] + j].tolist(),
                                    "confidence": float(z["confidence"][po[i] + j])})
    return {"video_id": video_id, "track_id": track_id, "samples": samples,
            "scope": "Sparse optical-flow feature identity within a shot; IDs reset at cuts and are not semantic parts."}


def identify_insert(video_id: str, frame: int, workspace: Path | None = None, extra_catalog: list[dict] | None = None) -> dict:
    record = get_frame(video_id, frame, workspace)
    if record["origin"]:
        return {"video_id": video_id, "frame": frame, "status": "excluded", "origin": record["origin"]}
    catalog = default_meme_catalog() + (extra_catalog or [])
    match = _catalog_match(record["phash"], catalog, 10)
    if match:
        return {"video_id": video_id, "frame": frame, "status": "candidate-match", "origin": match,
                "review": "Confirm visually before treating as the exact source episode/upload."}
    return {"video_id": video_id, "frame": frame, "status": "unknown", "origin": None,
            "phash": record["phash"], "next": "Review the frame; use an authorized reverse-image/source search, then add an evidenced annotation or catalog entry. Do not invent an origin."}


def apply_exclusions(video_id: str, ranges: list[dict], workspace: Path | None = None) -> dict:
    """Mark reviewed frame ranges as excluded inserts/memes and clear their geometry.

    Use after visual review or a confirmed source match. Ranges are half-open and
    a claimed origin requires source_url evidence. This does not re-decode video.
    """
    root, manifest = _load_manifest(video_id, workspace)
    for r in ranges:
        if not (0 <= int(r["start_frame"]) < int(r["end_frame"]) <= manifest["coverage"]["decoded_frames"]):
            raise ValueError("Exclusion range outside trace")
        if r.get("origin") and not r["origin"].get("source_url"):
            raise ValueError("A claimed origin needs source_url evidence")
    total = manifest["coverage"]["decoded_frames"]
    excluded_mask = np.zeros(total, bool)
    origin_by_frame: dict[int, dict] = {}
    for r in ranges:
        for f in range(int(r["start_frame"]), int(r["end_frame"])):
            excluded_mask[f] = True
            origin_by_frame[f] = {"kind": r.get("kind", "insert"), "label": r.get("label", "reviewed insert"),
                                  "origin_status": "confirmed-by-review" if r.get("origin") else "excluded-without-origin",
                                  **(r.get("origin") or {}), "evidence": r.get("evidence", "caller-supplied reviewed frame range")}
    for chunk in manifest["chunks"]:
        path = root / "chunks" / chunk["file"]
        with np.load(path, allow_pickle=False) as z:
            data = {k: z[k] for k in z.files}
        n = len(data["frame_index"])
        po, co, cm = data["point_offsets"], data["contour_offsets"], data["contour_meta_offsets"]
        points, ids, conf, vel, contours, closed = [], [], [], [], [], []
        new_po, new_co, new_cm = [0], [0], [0]
        origins = []
        for i in range(n):
            frame = int(data["frame_index"][i])
            if excluded_mask[frame]:
                data["status"][i] = STATUS_EXCLUDED
                data["point_count"][i] = 0
                data["contour_count"][i] = 0
                data["motion"][i] = 0
                origins.append(json.dumps(origin_by_frame[frame], separators=(",", ":")))
            else:
                points.append(data["points"][po[i]:po[i+1]])
                ids.append(data["track_ids"][po[i]:po[i+1]])
                conf.append(data["confidence"][po[i]:po[i+1]])
                vel.append(data["velocity"][po[i]:po[i+1]])
                contours.append(data["contours"][co[i]:co[i+1]])
                closed.append(data["contour_closed"][cm[i]:cm[i+1]])
                origins.append(str(data["origin_json"][i]))
            new_po.append(new_po[-1] + (0 if excluded_mask[frame] else int(po[i+1]-po[i])))
            new_co.append(new_co[-1] + (0 if excluded_mask[frame] else int(co[i+1]-co[i])))
            new_cm.append(new_cm[-1] + (0 if excluded_mask[frame] else int(cm[i+1]-cm[i])))
        data.update({
            "points": np.concatenate(points) if points else np.empty((0,2),np.float32),
            "track_ids": np.concatenate(ids) if ids else np.empty((0,),np.int32),
            "confidence": np.concatenate(conf) if conf else np.empty((0,),np.float32),
            "velocity": np.concatenate(vel) if vel else np.empty((0,2),np.float32),
            "contours": np.concatenate(contours) if contours else np.empty((0,2),np.float32),
            "contour_closed": np.concatenate(closed) if closed else np.empty((0,),np.uint8),
            "point_offsets": np.asarray(new_po,np.int32), "contour_offsets": np.asarray(new_co,np.int32),
            "contour_meta_offsets": np.asarray(new_cm,np.int32), "origin_json": np.asarray(origins,dtype=str),
        })
        np.savez_compressed(path, **data)
    excluded = int(excluded_mask.sum())
    manifest["coverage"]["excluded_frames"] = excluded
    manifest["coverage"]["traced_frames"] = total - excluded
    manifest.setdefault("reviewed_exclusions", []).extend(ranges)
    manifest["review"]["status"] = "exclusions applied; remaining candidates still require review"
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    _update_catalog(root.parent, manifest)
    return manifest["coverage"]
