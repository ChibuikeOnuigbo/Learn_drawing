import json
from pathlib import Path

import av
import numpy as np
import pytest
from PIL import Image

from animation_mcp.tracing import trace_video, get_frame, get_track, read_catalog, identify_insert, library_root
from animation_mcp.procedural import generate, KINDS
from animation_mcp.planner import plan_scene, composite_scene
from animation_mcp.scene import Scene


def _synthetic_video(path: Path, frames: int = 36, fps: int = 12) -> None:
    container = av.open(str(path), mode="w")
    stream = container.add_stream("libx264", rate=fps)
    stream.width = 160; stream.height = 96; stream.pix_fmt = "yuv420p"
    for i in range(frames):
        im = np.full((96, 160, 3), 24, np.uint8)
        if i < 24:
            x = 10 + i * 4
            im[30:60, x:x + 24] = (220, 180, 60)
        else:
            im[:, :] = (40, 60, 90)
            im[20:70, 60:100] = (200, 200, 210)
        frame = av.VideoFrame.from_ndarray(im, format="rgb24")
        for packet in stream.encode(frame):
            container.mux(packet)
    for packet in stream.encode():
        container.mux(packet)
    container.close()


def test_every_frame_indexed_tracks_and_exclusion(tmp_path):
    video = tmp_path / "synthetic.mp4"
    _synthetic_video(video)
    annotations = tmp_path / "annotations.json"
    annotations.write_text(json.dumps({"ranges": [
        {"start_frame": 24, "end_frame": 30, "kind": "meme", "label": "test insert",
         "origin": {"source_url": "https://example.com/source", "title": "Example source"},
         "evidence": "synthetic test annotation"}]}))
    out = tmp_path / "data/traces/synthetic"
    manifest = trace_video(video, out, video_id="synthetic", analysis_width=160, max_tracks=32,
                           chunk_size=16, annotations=annotations)
    assert manifest["coverage"]["decoded_frames"] == 36
    assert manifest["coverage"]["excluded_frames"] == 6
    assert manifest["coverage"]["every_frame_indexed"]
    for frame in range(36):
        record = get_frame("synthetic", frame, tmp_path)
        assert record["frame"] == frame
        if 24 <= frame < 30:
            assert record["status"] == 1 and record["points"] == [] and record["origin"]["source_url"] == "https://example.com/source"
        else:
            assert record["status"] in (0, 2)
    first = get_frame("synthetic", 2, tmp_path)
    assert first["track_ids"]
    track = get_track("synthetic", first["track_ids"][0], 0, 20, tmp_path)
    assert len(track["samples"]) >= 5
    assert identify_insert("synthetic", 25, tmp_path)["status"] == "excluded"
    catalog = read_catalog(tmp_path)
    assert "synthetic" in catalog["videos"]


def test_missing_trace_and_bad_ids_fail(tmp_path):
    with pytest.raises(FileNotFoundError):
        get_frame("missing", 0, tmp_path)
    with pytest.raises(ValueError):
        get_frame("../escape", 0, tmp_path)


def test_procedural_assets_deterministic_and_looping(tmp_path):
    a = generate("tree_oak", tmp_path / "a", seed=7, width=128, height=128)
    b = generate("tree_oak", tmp_path / "b", seed=7, width=128, height=128)
    assert (tmp_path / "a/tree_oak.png").read_bytes() == (tmp_path / "b/tree_oak.png").read_bytes()
    assert a["license"].startswith("Original procedural")
    loop = generate("snow", tmp_path / "snow", seed=3, width=96, height=96, frames=12)
    assert loop["loop_seamless"] and len(loop["files"]) == 12
    assert loop["mean_first_last_pixel_delta"] is not None
    for kind in ("rain", "wind", "fog", "vignette", "depth_blur"):
        m = generate(kind, tmp_path / kind, seed=1, width=64, height=64, frames=4 if KINDS[kind] == "loop" else 1)
        assert m["files"]


def test_planner_seed_and_composite_schema(tmp_path):
    a = plan_scene("A lone tree in falling snow at night", seed=42, duration_seconds=4, fps=12, workspace=tmp_path)
    b = plan_scene("A lone tree in falling snow at night", seed=42, duration_seconds=4, fps=12, workspace=tmp_path)
    assert a == b
    assert a["weather"] == "snow" and a["shot_plan"]["frames"] == 48
    assert a["image_generation_brief"]["generated"] is False
    assert "snow" in a["suggested_assets"]
    layers = [{"id": "bg", "asset": "bg.png", "depth": 0.0},
              {"id": "subject", "asset": "subject.png", "depth": 0.5},
              {"id": "snow", "asset": "snow-%04d.png", "depth": 1.0, "opacity": 0.8}]
    scene = composite_scene(layers, width=320, height=180, fps=12, frames=24)
    Scene.model_validate(scene)
    assert [l["id"] for l in scene["layers"]] == ["bg", "subject", "snow"]
