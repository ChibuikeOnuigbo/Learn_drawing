"""Pre-production helpers, scaffolder and expanded skill/example regressions."""
import importlib.resources
import json
from pathlib import Path
import sys

import pytest
from pydantic import ValidationError

from animation_mcp.production import plan_shots, color_palette, timing_sheet, contrast_ratio
from animation_mcp.scaffold import scaffold_project
from animation_mcp.scene import Scene
from animation_mcp.blender_scene import Scene3D
from animation_mcp.edit import Edit
from animation_mcp.skills_index import index, read_skill

ROOT = Path(__file__).resolve().parents[1]


def test_shot_plan_is_contiguous_exact_and_half_open():
    plan = plan_shots([
        {"title": "A", "weight": 1}, {"title": "B", "weight": 2}, {"title": "C", "weight": 1},
    ], fps=24, duration_seconds=3)
    assert plan["frames"] == 72 and plan["duration_seconds"] == 3
    assert [s["frames"] for s in plan["shots"]] == [18, 36, 18]
    assert plan["shots"][0]["start_frame"] == 0
    for a, b in zip(plan["shots"], plan["shots"][1:]):
        assert a["end_frame"] == b["start_frame"]
    assert plan["shots"][-1]["end_frame"] == 72
    assert all(s["review_frames"][-1] == s["end_frame"] - 1 for s in plan["shots"])


def test_shot_plan_rounds_explicit_durations_and_warns():
    plan = plan_shots([{"title": "A", "seconds": 0.51}], fps=24)
    assert plan["frames"] == 12 and plan["warnings"]
    assert not plan_shots([{"title": "A", "seconds": 0.5}], fps=24)["warnings"]
    with pytest.raises(ValueError):
        plan_shots([{"title": "A", "weight": 1}], fps=24)
    with pytest.raises(ValueError):
        plan_shots([{"title": "A", "seconds": 1, "weight": 1}], fps=24)
    with pytest.raises(ValueError):
        plan_shots([{"title": "A"}, {"title": "B"}], fps=24, duration_seconds=0.01)


def test_minimum_one_frame_allocation_still_sums_exactly():
    plan = plan_shots([{"title": str(i), "weight": w} for i, w in enumerate([1000, 1, 1])],
                      fps=24, duration_seconds=0.125)  # 3 frames
    assert plan["frames"] == 3
    assert [s["frames"] for s in plan["shots"]] == [1, 1, 1]


def test_palette_contrast_math_and_harmonies():
    assert contrast_ratio("#000000", "#ffffff") == pytest.approx(21)
    for harmony in ("complementary", "analogous", "triadic", "split_complementary"):
        for dark in (True, False):
            p = color_palette("#4f8cff", harmony, dark)
            assert set(p["roles"]) == {"background", "surface", "primary", "secondary", "accent", "text", "muted"}
            assert p["contrast_ratios"]["text/background"] >= 4.5
            assert all(v.startswith("#") and len(v) == 7 for v in p["roles"].values())
    with pytest.raises(ValueError):
        color_palette("blue")
    with pytest.raises(ValueError):
        color_palette("#ffffff", "rainbow")


def test_exposure_sheet_holds_drawings_and_labels_keys():
    sheet = timing_sheet(12, 24, [{"frame": 0, "label": "contact"}, {"frame": 6, "label": "passing"}], 2)
    assert sheet["drawing_count"] == 6
    assert [r["drawing"] for r in sheet["rows"]] == [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6]
    assert sheet["rows"][0]["key"] == "contact" and sheet["rows"][6]["key"] == "passing"
    assert sheet["intervals"][0]["span_frames"] == 6
    with pytest.raises(ValueError):
        timing_sheet(12, keys=[{"frame": 12, "label": "outside"}])
    with pytest.raises(ValueError):
        timing_sheet(12, keys=[{"frame": 4, "label": "b"}, {"frame": 2, "label": "a"}])
    with pytest.raises(ValueError):
        timing_sheet(12, exposure_step=5)


def test_scaffold_2d_landscape_and_portrait_validate_and_do_not_overwrite(tmp_path):
    for name, width, height in [("land", 1280, 720), ("port", 540, 960)]:
        result = scaffold_project(tmp_path, name, "A test brief", fps=24, width=width, height=height)
        project = Path(result["project"])
        scene = Scene.model_validate_json((project / "scenes/scene-2d.json").read_text())
        assert (scene.width, scene.height, scene.frames) == (width, height, 168)
        assert "A test brief" in (project / "brief.md").read_text()
        assert (project / "assets/PROVENANCE.md").is_file()
        assert json.loads((project / "shot-plan.json").read_text())["frames"] == 168
        with pytest.raises(FileExistsError):
            scaffold_project(tmp_path, name)
    with pytest.raises(ValueError):
        scaffold_project(tmp_path, "../escape")
    with pytest.raises(ValueError):
        scaffold_project(tmp_path, "bad", engine="magic")


def test_scaffold_3d_respects_schema_and_budget(tmp_path):
    result = scaffold_project(tmp_path, "solid", fps=24, width=320, height=180, engine="3d")
    scene = Scene3D.model_validate_json((Path(result["project"]) / "scenes/scene-3d.json").read_text())
    assert scene.frames == 168
    assert scene.objects[1].poses[-1].frame == 167
    with pytest.raises(ValueError):
        scaffold_project(tmp_path, "too-big", fps=60, width=1920, height=1920, engine="3d")


def test_cli_new_is_machine_readable(tmp_path, monkeypatch, capsys):
    from animation_mcp.cli import main
    monkeypatch.setattr(sys, "argv", ["animation-studio", "new", "cli-proof", "--workspace", str(tmp_path),
                                      "--width", "320", "--height", "180"])
    assert main() == 0
    result = json.loads(capsys.readouterr().out)
    assert Path(result["project"]).is_dir()
    assert "render_command" in result


def test_expanded_catalog_and_new_templates():
    catalog = index()
    names = {s["name"] for s in catalog["skills"]}
    assert len(names) == 16
    assert {"storyboarding", "color-lighting", "motion-graphics", "physics-secondary-motion",
            "sound-design", "reference-analysis", "platform-delivery"} <= names
    for name in names:
        assert read_skill(name)["content"].startswith("---\n")
    templates = importlib.resources.files("animation_mcp.templates")
    Scene.model_validate(json.loads(templates.joinpath("scene-vertical.json").read_text()))
    shot = json.loads(templates.joinpath("shot-plan.json").read_text())
    assert shot["shots"][-1]["end_frame"] == shot["frames"]
    sheet = json.loads(templates.joinpath("exposure-sheet.json").read_text())
    assert len(sheet["rows"]) == sheet["frames"]
    palette = json.loads(templates.joinpath("palette.json").read_text())
    assert palette["roles"]["text"] != palette["roles"]["background"]


def test_drive_recreation_examples_have_passing_qa_and_honest_scope():
    curtain = ROOT / "examples/05-curtain-mesh"
    qa = json.loads((curtain / "inspection/qa.json").read_text())
    mesh = json.loads((curtain / "mesh-qa.json").read_text())
    assert qa["technical_pass"] and (qa["frames"], qa["width"], qa["height"], qa["fps"]) == (240, 1280, 720, 60)
    assert mesh["max_inverted"] == 0 and mesh["min_area_ratio"] > 0
    assert mesh["control_rate_hz"] == 17 and mesh["true_control_frames"] == 68
    qa17 = json.loads((curtain / "inspection-17fps/qa.json").read_text())
    assert qa17["technical_pass"] and (qa17["frames"], qa17["fps"]) == (68, 17)
    eye = ROOT / "examples/06-eye-face-performance"
    qa = json.loads((eye / "inspection/qa.json").read_text())
    eye_qa = json.loads((eye / "eye-qa.json").read_text())
    assert qa["technical_pass"] and (qa["frames"], qa["width"], qa["height"]) == (144, 720, 720)
    assert eye_qa["max_pixel_diff_outside_eye_boxes"] == 0
    assert "procedural lid blink" in eye_qa["blink_scope"]
    flash = ROOT / "examples/07-flashlight-whole-character"
    qa = json.loads((flash / "inspection/qa.json").read_text())
    beam = json.loads((flash / "beam-qa.json").read_text())
    align = json.loads((flash / "alignment-qa.json").read_text())
    assert qa["technical_pass"] and (qa["frames"], qa["width"], qa["height"]) == (252, 720, 720)
    assert beam["max_face_alpha_before_4_5"] == 0
    assert beam["first_face_alpha_gt_0_5"] >= 4.5
    assert "no face gate" in beam["mask"]
    assert align["rmse_px_after"] < align["rmse_px_before"]
    aura = ROOT / "examples/08-aura-rain-breath"
    qa = json.loads((aura / "inspection/qa.json").read_text())
    aura_qa = json.loads((aura / "aura-qa.json").read_text())
    assert qa["technical_pass"] and (qa["frames"], qa["width"], qa["height"]) == (192, 576, 864)
    assert aura_qa["face_protected"] and aura_qa["rain_bands"] == 3
    strokes = ROOT / "examples/09-opensketch-stroke-trace"
    qa = json.loads((strokes / "inspection/qa.json").read_text())
    stroke_qa = json.loads((strokes / "stroke-qa.json").read_text())
    assert qa["technical_pass"] and (qa["frames"], qa["width"], qa["height"]) == (144, 690, 690)
    assert stroke_qa["strokes"] > 0 and "CC0" in stroke_qa["source"]
