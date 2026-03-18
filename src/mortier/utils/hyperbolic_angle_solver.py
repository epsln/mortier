from dataclasses import dataclass
from collections import defaultdict
from typing import Sequence
from mortier.tesselation.tesselation_combinatorics import TilingCombinatorics
from scipy.optimize import minimize
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import lsqr

import numpy as np

@dataclass
class HyperbolicAngles:
    """
    Result of the angle solver.

    Attributes
    ----------
    angles : dict[int, float]
        Interior angle (radians) for each polygon type p.
    residual : float
        Maximum absolute constraint violation (radians).
        Should be < 1e-10 for a valid solution.
    success : bool
        Whether all constraints are satisfied within tolerance.
    message : str
        Human-readable status.
    """
    angles:   dict[int, float]
    residual: float
    success:  bool
    message:  str

    def __str__(self) -> str:
        lines = [
            f"Hyperbolic angle solution  "
            f"(max_residual={self.residual:.2e},  success={self.success})"
        ]
        for p, alpha in sorted(self.angles.items()):
            eucl  = _euclidean_angle(p)
            ratio = alpha / eucl
            lines.append(
                f"  {p}-gon : α = {math.degrees(alpha):.6f}°  "
                f"(Euclidean = {math.degrees(eucl):.4f}°,  ratio = {ratio:.6f})"
            )
        lines.append(f"  {self.message}")
        return "\n".join(lines)

def solve_hyperbolic_angles(
    polygon_types:         Sequence[int],
    vertex_orbit_configs:  Sequence[Sequence[int]],
    *,
    regularity_weight:     float = 0.1,
    n_restarts:            int   = 20,
    tol:                   float = 1e-10,
) -> HyperbolicAngles:
    """
    Solve for hyperbolic interior angles satisfying all vertex orbit constraints.

    Parameters
    ----------
    polygon_types : list of int
        Distinct polygon types in the tiling, e.g. [3, 4, 6].

    vertex_orbit_configs : list of sequences of int
        One entry per vertex orbit. Each entry is the cyclic sequence of
        polygon types around that vertex, e.g. (3, 4, 6, 4).
        Only the *multiset* of types matters for the angle sum.

    regularity_weight : float
        Weight of the regularization term (only active when m > k, i.e.
        when the system is underdetermined). Pushes angles toward the
        midpoint of their admissible range.

    n_restarts : int
        Number of random restarts for the optimizer.

    tol : float
        A solution is declared successful if max|Σα − 2π| < tol.

    Returns
    -------
    HyperbolicAngles
    """
    polygon_types        = list(polygon_types)
    vertex_orbit_configs = [tuple(c) for c in vertex_orbit_configs]

    _validate_inputs(polygon_types, vertex_orbit_configs)

    m   = len(polygon_types)
    k   = len(vertex_orbit_configs)
    idx = {p: i for i, p in enumerate(polygon_types)}  # p → column index

    # ------------------------------------------------------------------
    # Bounds: 0 < α_p < euclidean_angle(p)
    # We use 1% of the Euclidean value as lower bound to avoid degenerate
    # polygons while keeping the full range numerically accessible.
    # ------------------------------------------------------------------
    lo  = np.array([_euclidean_angle(p) * 0.01         for p in polygon_types])
    hi  = np.array([_euclidean_angle(p) * (1.0 - 1e-8) for p in polygon_types])
    mid = 0.5 * (lo + hi)

    # ------------------------------------------------------------------
    # Constraint matrix A  (k × m):
    #   A[i, j] = number of times polygon type j appears at vertex orbit i
    # The system to satisfy is:  A @ α = 2π · ones(k)
    # ------------------------------------------------------------------
    A      = np.zeros((k, m), dtype=float)
    target = np.full(k, 2.0 * math.pi)

    for i, config in enumerate(vertex_orbit_configs):
        for p in config:
            A[i, idx[p]] += 1.0

    # ------------------------------------------------------------------
    # Regularization: only active when system is underdetermined (m > k).
    # When k >= m the system is exactly/over-determined; regularization
    # would bias the solution away from the true answer.
    # ------------------------------------------------------------------
    reg_w = regularity_weight if m > k else 0.0

    def objective(x: np.ndarray) -> float:
        res     = A @ x - target
        penalty = float(np.dot(res, res))
        if reg_w > 0.0:
            penalty += reg_w * float(np.sum(((x - mid) / (hi - lo)) ** 2))
        return penalty

    def gradient(x: np.ndarray) -> np.ndarray:
        res  = A @ x - target
        grad = 2.0 * (A.T @ res)
        if reg_w > 0.0:
            grad = grad + 2.0 * reg_w * (x - mid) / (hi - lo) ** 2
        return grad

    bounds = list(zip(lo.tolist(), hi.tolist()))

    # ------------------------------------------------------------------
    # Multi-start L-BFGS-B
    # ------------------------------------------------------------------
    best_result: OptimizeResult | None = None
    best_obj = math.inf
    rng = np.random.default_rng(seed=42)

    for restart in range(n_restarts):
        x0 = mid.copy() if restart == 0 else rng.uniform(lo, hi)

        res = minimize(
            objective,
            x0,
            jac     = gradient,
            method  = "L-BFGS-B",
            bounds  = bounds,
            options = {"ftol": 1e-15, "gtol": 1e-12, "maxiter": 5000},
        )

        if res.fun < best_obj:
            best_obj    = res.fun
            best_result = res

        if best_obj < (tol ** 2) * k:
            break   # early exit: constraints already satisfied

    assert best_result is not None
    x_opt = best_result.x

    # ------------------------------------------------------------------
    # Evaluate solution quality
    # ------------------------------------------------------------------
    violations = np.abs(A @ x_opt - target)
    max_viol   = float(violations.max())
    success    = max_viol < tol

    angles = {p: float(x_opt[i]) for i, p in enumerate(polygon_types)}

    if success:
        msg = (
            f"All {k} vertex-orbit constraints satisfied "
            f"(max |error| = {max_viol:.2e} rad)."
        )
    else:
        msg = (
            f"WARNING: max constraint violation = {max_viol:.4f} rad "
            f"({math.degrees(max_viol):.4f}°). "
            "The tiling may not be realizable in hyperbolic space with "
            "uniform (same-size) polygons. Consider allowing per-instance angles."
        )
        #warnings.warn(msg)

    return HyperbolicAngles(angles=angles, residual=max_viol, success=success, message=msg)


@dataclass
class NonUniformAngles:
    """
    Per-face interior angles for a non-uniform hyperbolic realization.

    Attributes
    ----------
    angles : dict[int, float]
        Maps face index → interior angle (radians).

    residual : float
        Max |Σ_v α_i − 2π| over interior vertices (radians).

    success : bool
        True if residual < tol.

    per_type_stats : dict[int, dict]
        Per polygon type: 'mean', 'std', 'min', 'max' (degrees).

    message : str
    """
    angles:         dict[int, float]
    residual:       float
    success:        bool
    per_type_stats: dict[int, dict]
    message:        str

    def poincare_circumradius(self, face_idx: int, p: int) -> float:
        """Poincaré disk circumradius for a specific face instance."""
        return poincare_circumradius(p, self.angles[face_idx])

    def __str__(self) -> str:
        lines = [
            f"Non-uniform hyperbolic angles  "
            f"(residual={self.residual:.2e}, success={self.success})",
            f"  {len(self.angles)} face angles solved",
        ]
        for p, s in sorted(self.per_type_stats.items()):
            eucl = math.degrees(_euclidean_angle(p))
            lines.append(
                f"  {p}-gon: mean={s['mean']:.3f}°  std={s['std']:.4f}°  "
                f"range=[{s['min']:.3f}°, {s['max']:.3f}°]  "
                f"(Euclidean={eucl:.3f}°)"
            )
        lines.append(f"  {self.message}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve_nonuniform_angles(
    tc:             TilingCombinatorics,
    target_ratio:   float = 0.85,
    regularization: float = 0.01,
    tol:            float = 2e-3,
) -> NonUniformAngles:
    """
    Solve for per-face hyperbolic interior angles.

    Works for any tiling, including Euclidean ones (vertex angle sums = 360°)
    that cannot be realized uniformly.

    Parameters
    ----------
    tc : TilingCombinatorics
        Must have _face_vertex_keys attached via attach_face_vertex_keys().

    target_ratio : float in (0, 1)
        Target angle as a fraction of each polygon's Euclidean value.
        0.85 gives a moderately hyperbolic tiling.
        Lower values (e.g. 0.7) give more curvature — tiles shrink faster
        toward the disk boundary.

    regularization : float
        Weight of the smoothness term. Small values (0.01–0.1) prioritize
        constraint satisfaction; larger values (1–10) keep polygons more
        uniform at the cost of larger angle-sum errors.

    tol : float
        Success threshold for max constraint violation (radians).
        1e-3 (~0.06°) is appropriate for finite patches where boundary
        faces are geometrically constrained. Use 1e-6 for large tilings.

    Returns
    -------
    NonUniformAngles
    """
    if not hasattr(tc, "_face_vertex_keys"):
        raise AttributeError(
            "tc._face_vertex_keys not found. "
            "Call attach_face_vertex_keys(tc, faces) first."
        )

    two_pi   = 2.0 * np.pi
    n_faces  = len(tc.face_polygon_type)
    p_of     = tc.face_polygon_type   # face_idx → number of sides

    # ------------------------------------------------------------------
    # 1. Identify interior vertices
    #    Use ALL vertices whose Euclidean angle sum equals the global
    #    maximum — these are the genuine interior vertices of the tiling.
    # ------------------------------------------------------------------
    eucl_sum_of = {
        vk: sum(euclidean_angle(p) for p in cfg)
        for vk, cfg in tc.vertex_configurations.items()
    }
    max_sum = max(eucl_sum_of.values())

    interior_verts = [
        vk for vk, s in eucl_sum_of.items()
        if abs(s - max_sum) < 1e-6
    ]

    if not interior_verts:
        raise ValueError(
            "No interior vertices found. "
            "Check that the tiling patch is large enough."
        )

    n_int = len(interior_verts)

    # ------------------------------------------------------------------
    # 2. Build vertex → face lookup
    # ------------------------------------------------------------------
    vk_to_faces: dict[tuple, list[int]] = defaultdict(list)
    for fi, vk_list in tc._face_vertex_keys.items():
        for vk in vk_list:
            vk_to_faces[vk].append(fi)

    # ------------------------------------------------------------------
    # 3. Classify faces
    #
    # A face is "strictly interior" if ALL its vertices are interior.
    # Strictly interior faces must be bounded strictly below the Euclidean
    # value to guarantee hyperbolicity.
    # Boundary faces may reach (but not exceed) the Euclidean value —
    # they need this freedom to satisfy angle sums at boundary vertices
    # that have few surrounding faces.
    # ------------------------------------------------------------------
    interior_vk_set = set(interior_verts)

    strictly_interior: set[int] = set()
    for fi in range(n_faces):
        if all(vk in interior_vk_set for vk in tc._face_vertex_keys[fi]):
            strictly_interior.add(fi)

    # ------------------------------------------------------------------
    # 4. Bounds and targets
    # ------------------------------------------------------------------
    lo  = np.array([euclidean_angle(p_of[i]) * 0.01 for i in range(n_faces)])

    # In solve_nonuniform_angles, replace the hi definition:
    MIN_RADIUS = 0.01  # minimum acceptable Poincaré disk circumradius

    def max_alpha_for_min_radius(p: int, r_min: float) -> float:
        """Upper bound on alpha such that poincare_circumradius(p, alpha) >= r_min."""
        # r = tanh(R/2),  R = acosh(cos(π/p) / sin(α/2))
        # r >= r_min  ↔  R >= 2*arctanh(r_min)  ↔  cosh(R) <= cos(π/p)/sin(α/2)
        # ↔  sin(α/2) <= cos(π/p) / cosh(2*arctanh(r_min))
        # ↔  α <= 2*arcsin(cos(π/p) / cosh(2*arctanh(r_min)))
        R_min = 2 * np.atanh(r_min)
        sin_half_alpha_max = np.cos(np.pi / p) / np.cosh(R_min)
        if sin_half_alpha_max >= 1.0:
            return euclidean_angle(p) * (1.0 - 1e-8)  # no constraint from radius
        return 2 * np.asin(sin_half_alpha_max)

    hi = np.array([
        min(
            euclidean_angle(p_of[i]) * (1.0 - 1e-8),
            max_alpha_for_min_radius(p_of[i], MIN_RADIUS)
        )
        for i in range(n_faces)
    ])
    tgt = np.array([euclidean_angle(p_of[i]) * target_ratio for i in range(n_faces)])

    # Normalisation weights (per polygon type, so regularization is scale-invariant)
    W = 1.0 / np.array([euclidean_angle(p_of[i]) for i in range(n_faces)])

    # ------------------------------------------------------------------
    # 5. Build sparse constraint matrix  A  (n_int × n_faces)
    #    A[i, j] = 1  iff face j surrounds interior vertex i
    # ------------------------------------------------------------------
    A_sparse = lil_matrix((n_int, n_faces), dtype=float)
    for i, vk in enumerate(interior_verts):
        for fi in vk_to_faces.get(vk, []):
            A_sparse[i, fi] = 1.0
    A = A_sparse.tocsr()

    rhs = np.full(n_int, two_pi)

    # ------------------------------------------------------------------
    # 7. Objective and gradient
    #
    # f(x) = ||A·x − 2π||²  +  λ · ||W·(x − tgt)||²
    # ------------------------------------------------------------------
    lam = regularization
    # After building vk_to_faces and interior_vk_set, identify constrained faces
    constrained_faces = set()
    for vk in interior_verts:
        for fi in vk_to_faces.get(vk, []):
            constrained_faces.add(fi)

    unconstrained_faces = set(range(n_faces)) - constrained_faces
    print(f"Unconstrained faces: {len(unconstrained_faces)}")

    # Fix their angles to target directly — exclude from optimization
    # Reduce problem to constrained faces only
    constrained_list = sorted(constrained_faces)
    face_to_idx = {fi: i for i, fi in enumerate(constrained_list)}
    n_constrained = len(constrained_list)

    # Rebuild bounds and targets for constrained faces only
    lo_c  = lo[constrained_list]
    hi_c  = hi[constrained_list]
    tgt_c = tgt[constrained_list]
    W_c   = W[constrained_list]

    # Rebuild constraint matrix for constrained faces only
    # But first subtract contribution of unconstrained faces (fixed at tgt)
    # from the RHS
    A_full = A  # original matrix over all faces
    A_c    = A_full[:, constrained_list]  # columns for constrained faces only

    # Contribution of unconstrained faces to each vertex sum
    unconstrained_list = sorted(unconstrained_faces)
    A_u    = A_full[:, unconstrained_list]
    tgt_u  = tgt[unconstrained_list]
    rhs_c  = rhs - A_u @ tgt_u  # adjusted RHS

    # Solve over constrained faces only
    def objective_c(x):
        r = A_c @ x - rhs_c
        return float(r @ r + lam * np.sum((W_c * (x - tgt_c)) ** 2))

    def gradient_c(x):
        r = A_c @ x - rhs_c
        return np.asarray(2.0 * (A_c.T @ r) + 2.0 * lam * (W_c ** 2) * (x - tgt_c)).ravel()

    x0_c, *_ = lsqr(A_c, rhs_c, damp=np.sqrt(regularization))
    x0_c = np.clip(x0_c, lo_c * 1.01, hi_c * 0.99)
    result = minimize(
        objective_c, x0_c, jac=gradient_c, method="L-BFGS-B",
        bounds=list(zip(lo_c.tolist(), hi_c.tolist())),
        options={"ftol": 1e-15, "gtol": 1e-13, "maxiter": 50_000},
    )

    # Reassemble full angle array
    x_opt = tgt.copy()                          # unconstrained faces get target
    for i, fi in enumerate(constrained_list):
        x_opt[fi] = result.x[i]                # constrained faces get solved value

    # ------------------------------------------------------------------
    # 9. Evaluate quality
    # ------------------------------------------------------------------
    violations = np.abs(A @ x_opt - rhs)
    max_viol   = float(violations.max())
    success    = max_viol < tol

    angles = {i: float(x_opt[i]) for i in range(n_faces)}

    if success:
        msg = (
            f"All {n_int} interior vertex constraints satisfied "
            f"(max |error| = {max_viol:.2e} rad)."
        )
    else:
        msg = (
            f"Max constraint violation = {max_viol:.6f} rad "
            f"({np.degrees(max_viol):.4f}°) over {n_int} interior vertices. "
            f"Try lowering target_ratio or decreasing regularization."
        )
        #warnings.warn(msg)

    # ------------------------------------------------------------------
    # 10. Per-type statistics
    # ------------------------------------------------------------------
    type_angles: dict[int, list[float]] = defaultdict(list)
    for fi, alpha in angles.items():
        type_angles[p_of[fi]].append(np.degrees(alpha))

    per_type_stats = {}
    for p, alphas in sorted(type_angles.items()):
        arr = np.array(alphas)
        per_type_stats[p] = {
            "mean": float(arr.mean()),
            "std":  float(arr.std()),
            "min":  float(arr.min()),
            "max":  float(arr.max()),
        }

    return NonUniformAngles(
        angles         = angles,
        residual       = max_viol,
        success        = success,
        per_type_stats = per_type_stats,
        message        = msg,
    )

def hyperbolic_polygon_circumradius(p: int, alpha: float) -> float:
    """
    Circumradius in the hyperbolic metric of a regular hyperbolic p-gon
    with interior angle alpha (radians).

    Standard formula derived from the hyperbolic law of cosines:

        cosh(R) = cos(π/p) / sin(α/2)

    Parameters
    ----------
    p     : number of sides (≥ 3)
    alpha : interior angle in radians, must satisfy 0 < alpha < (p-2)π/p

    Returns
    -------
    R : circumradius in the hyperbolic metric

    Raises
    ------
    ValueError if alpha is outside the admissible range.
    """
    eucl = euclidean_angle(p)
    # Clamp to valid range with a small margin
    alpha = min(alpha, eucl * (1.0 - 1e-9))
    if alpha <= 0:
        raise ValueError(f"Interior angle must be positive, got {math.degrees(alpha):.6f}°")
    ratio = np.cos(np.pi / p) / np.sin(alpha / 2.0)
    if ratio < 1.0:
        raise ValueError(
            f"cosh(R) = {ratio:.6f} < 1 — angle too large for a hyperbolic {p}-gon."
        )
    return np.acosh(ratio)


def poincare_circumradius(p: int, alpha: float) -> float:
    """
    Circumradius in Poincaré disk coordinates (Euclidean distance from the
    disk origin to a vertex when the polygon is centered at the origin).

        r_disk = tanh(R / 2)

    where R is the hyperbolic circumradius.
    """
    R = hyperbolic_polygon_circumradius(p, alpha)
    return np.tanh(R / 2.0)

def euclidean_angle(p: int) -> float:
    """Interior angle of a regular Euclidean p-gon: (p−2)π/p."""
    return (p - 2) * np.pi / p

def check_realizability(
    polygon_types:        Sequence[int],
    vertex_orbit_configs: Sequence[Sequence[int]],
) -> str:
    """
    Check whether the angle-sum constraints are potentially satisfiable.

    For each vertex orbit independently, computes the range of achievable
    angle sums [Σ lo_p, Σ hi_p]. If 2π falls outside this range for any
    orbit, no hyperbolic realization with uniform polygons can exist.

    Individual feasibility is necessary but not sufficient — shared polygon
    types couple the constraints and may prevent a joint solution even when
    all orbits are individually feasible.

    Returns a human-readable report string.
    """
    lo_a   = {p: _euclidean_angle(p) * 0.01         for p in polygon_types}
    hi_a   = {p: _euclidean_angle(p) * (1.0 - 1e-8) for p in polygon_types}
    two_pi = 2.0 * math.pi

    lines    = ["Realizability check:"]
    feasible = True

    for i, config in enumerate(vertex_orbit_configs):
        lo_sum = sum(lo_a[p] for p in config)
        hi_sum = sum(hi_a[p] for p in config)
        ok     = lo_sum < two_pi < hi_sum
        status = "✓ feasible" if ok else "✗ INFEASIBLE"
        lines.append(
            f"  Orbit {i} ({'.'.join(str(p) for p in config)}): "
            f"angle-sum range = [{math.degrees(lo_sum):.1f}°, "
            f"{math.degrees(hi_sum):.1f}°]  (need 360°)  {status}"
        )
        if not ok:
            feasible = False

    lines.append("")
    if feasible:
        lines.append(
            "All orbits individually feasible. "
            "Shared polygon types couple the constraints — run the solver to confirm."
        )
    else:
        lines.append(
            "At least one orbit is individually infeasible — "
            "no hyperbolic realization exists with uniform polygons."
        )
    return "\n".join(lines)

def solve_angles(tc: TilingCombinatorics) -> HyperbolicAngles | None:
    """
    Extract solver inputs from TilingCombinatorics and call the solver.
    Returns None if there are no interior orbits or the tiling is
    provably not realizable in hyperbolic space.
    """
    if not tc.interior_orbit_ids:
        return None

    # Polygon types present in the tiling
    polygon_types = sorted(set(tc.face_polygon_type.values()))

    # One config per interior orbit (using representative vertex)
    interior_configs = [
        tc.vertex_configurations[tc.vertex_orbits[oid][0]]
        for oid in tc.interior_orbit_ids
    ]

    # Quick feasibility check — if any orbit is provably infeasible, bail early
    report = check_realizability(polygon_types, interior_configs)
    if "INFEASIBLE" in report:
        return None

    return solve_hyperbolic_angles(polygon_types, interior_configs)
