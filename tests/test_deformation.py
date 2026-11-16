"""Geometry and compositing regressions for the Drive recreation helpers."""
import numpy as np
import pytest

from animation_mcp.deformation import (
    MeshWarp, cubic_keys, flashlight_composite, fold_report, grid_mesh, premultiply, unpremultiply,
)


def test_cubic_keys_pause_has_zero_velocity_and_clamps():
    assert cubic_keys([0, 1, 2], [0, 0, 1], 0.5) == 0
    assert cubic_keys([0, 1, 2], [0, 0, 1], -1) == 0
    assert cubic_keys([0, 1, 2], [0, 0, 1], 3) == 1
    v = cubic_keys([0, 1, 2], [(0, 0), (1, 1), (1, 1)], 1.5)
    assert v.shape == (2,) and np.allclose(v, [1, 1], atol=1e-9)
    with pytest.raises(ValueError):
        cubic_keys([0, 0], [1, 2], 0)


def test_mesh_warp_identity_and_fold_rejection():
    src = np.zeros((20, 20, 4), np.uint8); src[..., :3] = 200; src[..., 3] = 255
    rest, tris = grid_mesh(3, 3, 19, 19)
    w = MeshWarp(src, rest, tris)
    out, rep = w.render(rest, (20, 20))
    assert rep["inverted"] == 0 and out[10, 10, 3] == 255
    posed = rest.copy(); posed[:, 0] = 19 - posed[:, 0]  # mirror folds every triangle
    with pytest.raises(ValueError):
        w.render(posed, (20, 20))


def test_premultiply_roundtrip_protects_transparent_rgb():
    a = np.array([[[10, 20, 30, 0], [200, 100, 50, 128]]], np.uint8)
    back = unpremultiply(premultiply(a))
    assert back[0, 0, 3] == 0 and back[0, 1, 3] == 128
    assert np.max(np.abs(back[0, 1, :3].astype(int) - a[0, 1, :3].astype(int))) <= 1


def test_flashlight_is_one_mask_over_complete_layers():
    base = np.zeros((40, 40, 3), np.uint8); base[:] = (100, 0, 0)
    alt = np.zeros_like(base); alt[:] = (0, 100, 0)
    out, alpha = flashlight_composite(base, alt, (20, 20), radius=5, feather=2, outside_gain=.5)
    assert alpha.shape == (40, 40)
    assert out[20, 20, 1] > out[20, 20, 0]      # alternate inside
    assert out[0, 0, 0] == 50 and out[0, 0, 1] == 0  # dimmed base outside
    # same alpha governs every channel/region; no face exception exists
    assert np.allclose(out[20, 20], np.clip(1.03 * alt[20, 20] + 2, 0, 255).astype(np.uint8), atol=1)
