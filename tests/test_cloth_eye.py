"""Constraint solver and eyelid rig regressions."""
import numpy as np
import pytest

from animation_mcp.cloth import ClothPanel, fold_shading
from animation_mcp.eye_rig import apply_eye, blink_crop, trace_aperture


def test_cloth_pins_hold_and_strain_stays_bounded():
    p = ClothPanel(7, 9, 200, 300, "left", iterations=16, wind=12, gravity=100)
    for i in range(34):
        t = i / 17
        rep = p.step(1 / 17, rail_y=50, span=(100, 300), closure=0, tie=0, tie_x=150,
                     seam_x=400, t=t, substeps=6)
    pos = p.positions.reshape(9, 7, 2)
    # rail row pinned exactly
    assert np.allclose(pos[0, :, 1], 50, atol=1e-6)
    assert np.allclose(pos[0, :, 0], np.linspace(100, 300, 7), atol=1e-6)
    assert rep["max_edge_strain"] < 0.5
    assert np.isfinite(pos).all()


def test_cloth_seam_collision_and_monotonic_projection():
    p = ClothPanel(7, 9, 200, 300, "left", iterations=16, wind=30)
    for i in range(20):
        p.step(1 / 17, rail_y=50, span=(100, 240), closure=1, tie=0, tie_x=150,
               seam_x=250, t=i / 17, substeps=6)
    # free (non-rail) particles respect the seam before render projection
    free = p.positions.reshape(9, 7, 2)[1:]
    assert np.all(free[:, :, 0] <= 250 + 1e-6)
    pos = p.project_monotonic(1.0).reshape(9, 7, 2)
    assert np.all(np.diff(pos[:, :, 0], axis=1) >= 1.0 - 1e-6)


def test_cloth_rejects_bad_inputs():
    with pytest.raises(ValueError):
        ClothPanel(2, 9, 100, 100)
    with pytest.raises(ValueError):
        ClothPanel(5, 5, -1, 100)
    p = ClothPanel(5, 5, 100, 100)
    with pytest.raises(ValueError):
        p.step(0, rail_y=0, span=(0, 100), closure=0, tie=0, tie_x=0, seam_x=200, t=0)


def test_fold_shading_is_bounded_and_slack_driven():
    flat = fold_shading(9, 9, slack=1.0, t=0)
    assert np.allclose(flat, 1.0)
    gathered = fold_shading(9, 9, slack=2.5, t=0)
    assert gathered.min() > 0.2 and gathered.max() < 1.8
    assert gathered.std() > 0.05


def _portrait():
    rng = np.random.default_rng(0)
    im = np.full((200, 200, 3), 150, np.uint8)
    im[..., 1] = 95; im[..., 2] = 55
    # dark eye aperture
    im[80:110, 60:130] = (20, 15, 10)
    im[85:105, 70:120] = (230, 230, 225)
    return im


def test_blink_closure_zero_preserves_source_and_outside_identity():
    im = _portrait()
    poly = [(60, 95), (75, 82), (110, 82), (130, 95), (115, 108), (75, 108)]
    reg = trace_aperture(im, (50, 70, 140, 120), poly)
    out0, info0 = apply_eye(im, reg, 0.0)
    assert info0["aperture_ratio"] == pytest.approx(1.0)
    # outside the box is bit-identical
    mask = np.ones((200, 200), bool); mask[70:120, 50:140] = False
    assert np.array_equal(out0[mask], im[mask])
    out1, info1 = apply_eye(im, reg, 1.0)
    assert info1["aperture_ratio"] == pytest.approx(0.0, abs=1e-9)
    assert info1["upper_lid_travel_px"] > info1["lower_lid_travel_px"]
    assert np.array_equal(out1[mask], im[mask])


def test_blink_aperture_monotonic_with_closure():
    im = _portrait()
    poly = [(60, 95), (75, 82), (110, 82), (130, 95), (115, 108), (75, 108)]
    reg = trace_aperture(im, (50, 70, 140, 120), poly)
    areas = [blink_crop(reg, c)[1]["aperture_area_px"] for c in np.linspace(0, 1, 6)]
    assert all(a >= b - 1e-6 for a, b in zip(areas, areas[1:]))
