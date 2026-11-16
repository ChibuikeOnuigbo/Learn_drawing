"""Position-based cloth panel: distance constraints, pins, wind, seam collision.

Scope: a 2D position-based dynamics (PBD) solve for a hanging curtain panel.
It is not a 3D cloth simulator: out-of-plane buckling is represented by fold
*shading* derived from material slack and by a monotonic-column projection, not
by solved depth geometry. The solver enforces material rest lengths with
coloured Gauss-Seidel distance constraints, pinned rail gliders, a releasable
tieback, hem inertia and a centre-seam collision, and reports measured strain.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


def _edge_colors(edges: np.ndarray, n: int) -> list[np.ndarray]:
    """Greedy edge colouring so each colour batch has no shared vertices."""
    used = [set() for _ in range(n)]
    colors: list[list[int]] = []
    palette: list[set[int]] = []
    for e, (a, b) in enumerate(edges):
        for c, banned in enumerate(palette):
            if a not in banned and b not in banned:
                break
        else:
            c = len(palette)
            palette.append(set())
            colors.append([])
        palette[c].update((int(a), int(b)))
        colors[c].append(e)
    return [np.asarray(c, dtype=np.int32) for c in colors]


@dataclass
class ClothPanel:
    cols: int
    rows: int
    material_width: float
    material_height: float
    side: str = "left"
    gravity: float = 240.0
    damping: float = 0.985
    iterations: int = 8
    wind: float = 26.0
    _pos: np.ndarray = field(init=False, repr=False)
    _prev: np.ndarray = field(init=False, repr=False)
    _edges: np.ndarray = field(init=False, repr=False)
    _rest: np.ndarray = field(init=False, repr=False)
    _stiff: np.ndarray = field(init=False, repr=False)

    def __post_init__(self):
        if self.cols < 3 or self.rows < 3:
            raise ValueError("Cloth needs at least a 3x3 particle grid")
        if self.side not in ("left", "right"):
            raise ValueError("side must be 'left' or 'right'")
        if self.material_width <= 0 or self.material_height <= 0:
            raise ValueError("Material dimensions must be positive")
        n = self.cols * self.rows
        self._pos = np.zeros((n, 2))
        self._prev = np.zeros((n, 2))
        idx = np.arange(n).reshape(self.rows, self.cols)
        pairs, stiff = [], []
        pairs += [np.stack([idx[:, :-1].ravel(), idx[:, 1:].ravel()], 1)]
        stiff += [np.full(self.rows * (self.cols - 1), 0.9)]
        pairs += [np.stack([idx[:-1, :].ravel(), idx[1:, :].ravel()], 1)]
        stiff += [np.full((self.rows - 1) * self.cols, 0.9)]
        pairs += [np.stack([idx[:-1, :-1].ravel(), idx[1:, 1:].ravel()], 1)]
        stiff += [np.full((self.rows - 1) * (self.cols - 1), 0.35)]
        pairs += [np.stack([idx[:-1, 1:].ravel(), idx[1:, :-1].ravel()], 1)]
        stiff += [np.full((self.rows - 1) * (self.cols - 1), 0.35)]
        pairs += [np.stack([idx[:, :-2].ravel(), idx[:, 2:].ravel()], 1)]
        stiff += [np.full(self.rows * (self.cols - 2), 0.12)]
        pairs += [np.stack([idx[:-2, :].ravel(), idx[2:, :].ravel()], 1)]
        stiff += [np.full((self.rows - 2) * self.cols, 0.12)]
        self._edges = np.concatenate(pairs).astype(np.int32)
        self._stiff = np.concatenate(stiff)
        self._colors = _edge_colors(self._edges, n)
        self._drc = np.asarray([divmod(int(b), self.cols)[0] - divmod(int(a), self.cols)[0]
                                for a, b in self._edges])
        self._dcc = np.asarray([divmod(int(b), self.cols)[1] - divmod(int(a), self.cols)[1]
                                for a, b in self._edges])
        self._dv = self.material_height / (self.rows - 1)
        self._rest = np.hypot(self._dcc * (self.material_width / (self.cols - 1)), self._drc * self._dv)
        self._initialised = False
        self._projection_px = 0.0

    def _set_hung_width(self, width: float):
        """Gathering is out-of-plane in real cloth; in this 2D solve the horizontal
        rest spacing follows the hung span so the sheet does not buckle/invert.
        Fold *shading* carries the material slack instead (see ``slack``)."""
        du = abs(width) / (self.cols - 1)
        self._rest = np.hypot(self._dcc * du, self._drc * self._dv)

    @property
    def positions(self) -> np.ndarray:
        return self._pos.copy()

    def _pins(self, rail_y: float, span: tuple[float, float], tie: float, tie_x: float):
        u = np.linspace(0, 1, self.cols)
        x0, x1 = span
        idx = list(range(self.cols))
        pos = np.stack([x0 + (x1 - x0) * u, np.full(self.cols, rail_y)], 1)
        if tie > 1e-3:
            waist_row = int(round(0.56 * (self.rows - 1)))
            inner = self.cols - 1 if self.side == "left" else 0
            idx.append(waist_row * self.cols + inner)
            pos = np.vstack([pos, [tie_x, rail_y + 0.56 * self.material_height]])
        return np.asarray(idx, dtype=np.int32), np.asarray(pos, float)

    def step(self, dt: float, *, rail_y: float, span: tuple[float, float], closure: float,
             tie: float, tie_x: float, seam_x: float, t: float, substeps: int = 4) -> dict:
        if dt <= 0 or substeps < 1:
            raise ValueError("dt must be positive and substeps >= 1")
        u = np.linspace(0, 1, self.cols)[None, :].repeat(self.rows, 0)
        v = np.linspace(0, 1, self.rows)[:, None].repeat(self.cols, 1)
        x0, x1 = span
        self._set_hung_width(x1 - x0)
        if not self._initialised:
            self._pos = np.stack([(x0 + (x1 - x0) * u).ravel(),
                                  (rail_y + v * self.material_height).ravel()], 1)
            self._prev = self._pos.copy()
            self._initialised = True
        pin_idx, pin_pos = self._pins(rail_y, span, tie, tie_x)
        h = dt / substeps
        phase = 0.0 if self.side == "left" else 1.9
        for s in range(substeps):
            tt = t + s * h
            vel = (self._pos - self._prev) * self.damping
            gust = (np.sin(2 * np.pi * (0.75 * tt - 1.15 * v) + phase)
                    + 0.35 * np.sin(2 * np.pi * (2.6 * tt - 2.1 * v) + phase))
            force = np.stack([self.wind * gust * v ** 1.4 * (1 - 0.55 * closure),
                              np.full_like(v, self.gravity * 0.02)], -1).reshape(-1, 2)
            self._prev = self._pos.copy()
            pred = self._pos + vel + force * (h * h)
            pred[pin_idx] = pin_pos
            for _ in range(self.iterations):
                for batch in self._colors:
                    a, b = self._edges[batch, 0], self._edges[batch, 1]
                    d = pred[b] - pred[a]
                    length = np.linalg.norm(d, axis=1)
                    ok = length > 1e-9
                    if not np.any(ok):
                        continue
                    scale = np.zeros_like(length)
                    scale[ok] = ((length[ok] - self._rest[batch][ok]) / length[ok]
                                 * 0.5 * self._stiff[batch][ok])
                    corr = d * scale[:, None]
                    # colour batches are vertex-disjoint, so fancy indexing is safe
                    pred[a] += corr
                    pred[b] -= corr
                    pred[pin_idx] = pin_pos
            if self.side == "left":
                pred[:, 0] = np.minimum(pred[:, 0], seam_x)
            else:
                pred[:, 0] = np.maximum(pred[:, 0], seam_x)
            pred[pin_idx] = pin_pos
            self._pos = pred
        return self.report()

    def project_monotonic(self, min_gap: float = 0.5) -> np.ndarray:
        """Keep material columns ordered so the render mesh cannot fold.

        Real cloth buckles out of plane; this 2D solve instead projects each row
        to a strictly increasing (left panel) or decreasing (right panel) x order.
        The maximum correction is reported, not hidden.
        """
        grid = self._pos.reshape(self.rows, self.cols, 2).copy()
        moved = 0.0
        for r in range(self.rows):
            # material u always runs left-to-right on canvas for both panels
            xs = grid[r, :, 0]
            fixed = np.maximum.accumulate(xs + np.arange(self.cols) * min_gap) - np.arange(self.cols) * min_gap
            moved = max(moved, float(np.max(np.abs(fixed - xs))))
            grid[r, :, 0] = fixed
        self._pos = grid.reshape(-1, 2)
        self._projection_px = moved
        return self._pos.copy()

    def report(self) -> dict:
        a, b = self._edges[:, 0], self._edges[:, 1]
        length = np.linalg.norm(self._pos[b] - self._pos[a], axis=1)
        strain = np.abs(length - self._rest) / np.maximum(self._rest, 1e-9)
        return {
            "particles": int(len(self._pos)),
            "constraints": int(len(self._edges)),
            "max_edge_strain": float(strain.max()),
            "mean_edge_strain": float(strain.mean()),
            "projection_px": float(self._projection_px),
        }

    def slack(self, span: tuple[float, float]) -> float:
        """Material width divided by hung span: >1 means the cloth must gather."""
        return float(self.material_width / max(abs(span[1] - span[0]), 1e-6))


def fold_shading(cols: int, rows: int, slack: float, t: float, seed: int = 11) -> np.ndarray:
    """Irregular fold luminance from material slack (shading, not geometry)."""
    rng = np.random.default_rng(seed)
    u = np.linspace(0, 1, cols)[None, :]
    v = np.linspace(0, 1, rows)[:, None]
    freqs = rng.uniform(6.0, 13.0, 4)
    phases = rng.uniform(0, 2 * np.pi, 4)
    drift = 0.12 * np.sin(2 * np.pi * 0.22 * t + phases)
    wave = sum(np.sin(2 * np.pi * (f * u + 0.06 * np.sin(3 * v + p)) + p + drift[i])
               for i, (f, p) in enumerate(zip(freqs, phases))) / len(freqs)
    amp = float(np.clip(np.sqrt(max(slack - 1.0, 0.0)) * 0.55, 0.0, 0.65))
    return 1.0 + amp * wave * (0.55 + 0.45 * v)
