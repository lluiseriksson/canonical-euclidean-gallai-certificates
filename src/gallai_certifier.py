"""Pure-stdlib zero-float verifier for CANONICAL-GALLAI-CERT-1.0 certificates.
Supports four exact-Q verification modes aligned with Randall Shaw (arXiv:2611.33136, Nov 24, 2026)
"A canonical Euclidean Gallai theorem":
  1. rational_similarity_copy_exact       (Thm 2: exact scaled+rotated copy & monochromatic/rainbow certification)
  2. homothety_obstruction_vs_rotation_exact (p. 2 obstruction: homothety trapped in [2, t-1] colors vs rotation rainbow)
  3. subspace_coloring_dichotomy_exact    (Thm 3 & Key Lemma p. 4: ker(H) coloring, uniqueness lemma & rainbow witness)
  4. lift_union_bound_and_2d_sum_exact    (Thm 2 lift k(t), grid m(t), union bound 1/(P+1) > 0, & 2D similarity sum)

Author: Lluis Eriksson
"""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, List, Tuple

from src.gallai_exact import (
    MatQ,
    VecQ,
    dist_sq_q,
    dot_q,
    grid_bound,
    is_scaled_orthogonal_exact,
    lift_dim,
    mat_vec_mul,
    pair_count,
    vec_add,
    vec_scale,
    vec_sub,
)

SCHEMA_VERSION = "CANONICAL-GALLAI-CERT-1.0"
_CANON_INT_RE = re.compile(r"\A(?:0|-?[1-9][0-9]*)\Z")
_CANON_FRAC_RE = re.compile(r"\A-?[1-9][0-9]*/[1-9][0-9]*\Z")


class CanonicalGallaiCertificateError(ValueError):
    """Raised whenever any CANONICAL-GALLAI-CERT-1.0 verification check fails."""


def _assert_strict_json_types(obj: Any, path: str = "root") -> None:
    t = type(obj)
    if t is int or t is str or obj is None:
        return
    if t is dict:
        for k, v in obj.items():
            if type(k) is not str:
                raise CanonicalGallaiCertificateError(f"Non-str dict key at {path}: {type(k).__name__}")
            _assert_strict_json_types(v, f"{path}.{k}")
        return
    if t is list:
        for i, v in enumerate(obj):
            _assert_strict_json_types(v, f"{path}[{i}]")
        return
    raise CanonicalGallaiCertificateError(f"Forbidden type {t.__name__} at {path}")


def _parse_int(val: Any, name: str) -> int:
    if type(val) is not int:
        raise CanonicalGallaiCertificateError(f"{name} must be strict int, got {type(val).__name__}")
    return val


def _parse_rat(val: Any, name: str) -> Fraction:
    if type(val) is int:
        return Fraction(val, 1)
    if type(val) is str:
        if _CANON_INT_RE.match(val):
            return Fraction(int(val), 1)
        if _CANON_FRAC_RE.match(val):
            num_s, den_s = val.split("/")
            num, den = int(num_s), int(den_s)
            if den < 2:
                raise CanonicalGallaiCertificateError(f"{name} denominator must be >= 2: {val!r}")
            q = Fraction(num, den)
            if q.numerator != num or q.denominator != den:
                raise CanonicalGallaiCertificateError(f"{name} unreduced fraction: {val!r}")
            return q
        raise CanonicalGallaiCertificateError(f"{name} non-canonical rational string: {val!r}")
    raise CanonicalGallaiCertificateError(f"{name} invalid type {type(val).__name__}")


def _parse_vec(raw: Any, dim: int, name: str) -> VecQ:
    if type(raw) is not list or len(raw) != dim:
        raise CanonicalGallaiCertificateError(f"{name} must be vector of length {dim}")
    return [_parse_rat(x, f"{name}[{i}]") for i, x in enumerate(raw)]


def _parse_mat(raw: Any, rows: int, cols: int, name: str) -> MatQ:
    if type(raw) is not list or len(raw) != rows:
        raise CanonicalGallaiCertificateError(f"{name} must have {rows} rows")
    return [_parse_vec(raw[i], cols, f"{name}[{i}]") for i in range(rows)]


def _verify_mode1_similarity_copy(cert: Dict[str, Any]) -> Dict[str, Any]:
    req = {
        "schema", "mode", "name", "dim_d", "source_points", "target_points",
        "sim_matrix", "translation", "claimed_scale_sq",
        "color_functional_w", "claimed_coloring_type",
    }
    if set(cert.keys()) != req:
        raise CanonicalGallaiCertificateError(f"Mode 1 key mismatch: {sorted(set(cert.keys()) ^ req)}")
    d = _parse_int(cert["dim_d"], "dim_d")
    if d not in (2, 3):
        raise CanonicalGallaiCertificateError(f"dim_d must be 2 or 3, got {d}")
    s_raw, t_raw = cert["source_points"], cert["target_points"]
    if type(s_raw) is not list or type(t_raw) is not list or not (2 <= len(s_raw) <= 12) or len(s_raw) != len(t_raw):
        raise CanonicalGallaiCertificateError("source_points and target_points must have equal length in [2, 12]")
    t = len(s_raw)
    S = [_parse_vec(p, d, f"source_points[{i}]") for i, p in enumerate(s_raw)]
    T = [_parse_vec(p, d, f"target_points[{i}]") for i, p in enumerate(t_raw)]
    if len({tuple(p) for p in S}) != t:
        raise CanonicalGallaiCertificateError("source_points must be pairwise distinct")

    M = _parse_mat(cert["sim_matrix"], d, d, "sim_matrix")
    v = _parse_vec(cert["translation"], d, "translation")
    ok_orth, s2 = is_scaled_orthogonal_exact(M)
    if not ok_orth:
        raise CanonicalGallaiCertificateError("sim_matrix is not a non-degenerate scaled orthogonal matrix (M^T M = s^2 I)")
    if _parse_rat(cert["claimed_scale_sq"], "claimed_scale_sq") != s2:
        raise CanonicalGallaiCertificateError(f"claimed_scale_sq mismatch: exact={s2}")

    for i in range(t):
        if vec_add(mat_vec_mul(M, S[i]), v) != T[i]:
            raise CanonicalGallaiCertificateError(f"Affine similarity mismatch at point {i}")
    for i in range(t):
        for j in range(i + 1, t):
            if dist_sq_q(T[i], T[j]) != s2 * dist_sq_q(S[i], S[j]):
                raise CanonicalGallaiCertificateError(f"Distance scaling mismatch on pair ({i},{j})")

    w = _parse_vec(cert["color_functional_w"], d, "color_functional_w")
    if all(x == 0 for x in w):
        raise CanonicalGallaiCertificateError("color_functional_w must be nonzero")
    colors = [dot_q(w, p) for p in T]
    n_distinct = len(set(colors))
    if n_distinct == 1:
        actual = "monochromatic"
    elif n_distinct == t:
        actual = "rainbow"
    else:
        raise CanonicalGallaiCertificateError(f"Target copy is neither monochromatic nor rainbow ({n_distinct}/{t} colors)")
    if cert["claimed_coloring_type"] != actual:
        raise CanonicalGallaiCertificateError(f"claimed_coloring_type={cert['claimed_coloring_type']!r} != {actual!r}")

    return {
        "verified": True,
        "mode": cert["mode"],
        "dim_d": d,
        "num_points": t,
        "scale_sq": str(s2),
        "coloring_type": actual,
    }


def _verify_mode2_homothety_vs_rotation(cert: Dict[str, Any]) -> Dict[str, Any]:
    req = {
        "schema", "mode", "name", "source_points", "color_functional_w",
        "rotation_matrix", "claimed_homothety_colors", "claimed_rotated_colors",
    }
    if set(cert.keys()) != req:
        raise CanonicalGallaiCertificateError(f"Mode 2 key mismatch: {sorted(set(cert.keys()) ^ req)}")
    s_raw = cert["source_points"]
    if type(s_raw) is not list or not (3 <= len(s_raw) <= 12):
        raise CanonicalGallaiCertificateError("source_points must have length in [3, 12]")
    t = len(s_raw)
    S = [_parse_vec(p, 2, f"source_points[{i}]") for i, p in enumerate(s_raw)]
    if len({tuple(p) for p in S}) != t:
        raise CanonicalGallaiCertificateError("source_points must be pairwise distinct")
    w = _parse_vec(cert["color_functional_w"], 2, "color_functional_w")
    if all(x == 0 for x in w):
        raise CanonicalGallaiCertificateError("color_functional_w must be nonzero")

    # Under ANY non-degenerate homothety x |-> s*x + v (s != 0), w.(s*x + v) = s*(w.x) + w.v,
    # so the number of distinct colors equals len({w.a : a in S}) identically!
    hom_colors = len({dot_q(w, p) for p in S})
    if not (2 <= hom_colors <= t - 1):
        raise CanonicalGallaiCertificateError(f"No homothety obstruction: homothety has {hom_colors} colors (need in [2, {t-1}])")
    if _parse_int(cert["claimed_homothety_colors"], "claimed_homothety_colors") != hom_colors:
        raise CanonicalGallaiCertificateError("claimed_homothety_colors mismatch")

    R = _parse_mat(cert["rotation_matrix"], 2, 2, "rotation_matrix")
    ok_orth, s2 = is_scaled_orthogonal_exact(R)
    det_R = R[0][0] * R[1][1] - R[0][1] * R[1][0]
    if not ok_orth or s2 != Fraction(1, 1) or det_R != Fraction(1, 1):
        raise CanonicalGallaiCertificateError("rotation_matrix must be exact unit proper rotation (R^T R = I_2, det R = +1)")
    rot_pts = [mat_vec_mul(R, p) for p in S]
    rot_colors = len({dot_q(w, p) for p in rot_pts})
    if rot_colors != t:
        raise CanonicalGallaiCertificateError(f"Rotated copy is not rainbow: got {rot_colors}/{t} colors")
    if _parse_int(cert["claimed_rotated_colors"], "claimed_rotated_colors") != rot_colors:
        raise CanonicalGallaiCertificateError("claimed_rotated_colors mismatch")

    return {
        "verified": True,
        "mode": cert["mode"],
        "num_points": t,
        "homothety_colors": hom_colors,
        "rotated_colors": rot_colors,
    }


def _verify_mode3_subspace_dichotomy(cert: Dict[str, Any]) -> Dict[str, Any]:
    req = {
        "schema", "mode", "name", "t_points", "ambient_k", "annihilator_H",
        "case_type", "pair_basis_vectors", "coefficients_c", "claimed_surviving_prob_lb",
    }
    if set(cert.keys()) != req:
        raise CanonicalGallaiCertificateError(f"Mode 3 key mismatch: {sorted(set(cert.keys()) ^ req)}")
    t = _parse_int(cert["t_points"], "t_points")
    if not (2 <= t <= 5):
        raise CanonicalGallaiCertificateError(f"t_points must be in [2, 5], got {t}")
    k = _parse_int(cert["ambient_k"], "ambient_k")
    if not (t <= k <= 64):
        raise CanonicalGallaiCertificateError(f"ambient_k must be in [{t}, 64], got {k}")
    H_raw = cert["annihilator_H"]
    if type(H_raw) is not list or not (1 <= len(H_raw) <= k):
        raise CanonicalGallaiCertificateError("annihilator_H must be non-empty matrix with <= k rows")
    r_rows = len(H_raw)
    H = _parse_mat(H_raw, r_rows, k, "annihilator_H")

    def in_U(vec: VecQ) -> bool:
        return all(x == 0 for x in mat_vec_mul(H, vec))

    P = pair_count(t)
    case = cert["case_type"]
    if case not in ("monochromatic", "rainbow"):
        raise CanonicalGallaiCertificateError(f"Invalid case_type: {case!r}")

    if case == "monochromatic":
        if cert["pair_basis_vectors"] != [] or cert["coefficients_c"] != []:
            raise CanonicalGallaiCertificateError("Monochromatic case requires empty pair_basis_vectors and coefficients_c")
        # Check all e_i - e_j in ker(H) for 0 <= i < j < t
        for i in range(t):
            for j in range(i + 1, t):
                diff = [Fraction(0, 1)] * k
                diff[i] = Fraction(1, 1)
                diff[j] = Fraction(-1, 1)
                if not in_U(diff):
                    raise CanonicalGallaiCertificateError(f"e_{i} - e_{j} not in U; not monochromatic")
        if _parse_rat(cert["claimed_surviving_prob_lb"], "claimed_surviving_prob_lb") != Fraction(1, 1):
            raise CanonicalGallaiCertificateError("Monochromatic case must claim probability 1")
        return {
            "verified": True,
            "mode": cert["mode"],
            "t_points": t,
            "ambient_k": k,
            "case": "monochromatic",
            "distinct_colors": 1,
        }

    # Rainbow case: verify Randall Shaw's pair-indexed construction & Key Uniqueness Lemma (p. 4)!
    pairs = [(i, j) for i in range(t) for j in range(i + 1, t)]
    pb_raw = cert["pair_basis_vectors"]
    c_raw = cert["coefficients_c"]
    if type(pb_raw) is not list or len(pb_raw) != P or type(c_raw) is not list or len(c_raw) != P:
        raise CanonicalGallaiCertificateError(f"pair_basis_vectors and coefficients_c must have length P={P}")
    cs = [_parse_int(x, f"coefficients_c[{q}]") for q, x in enumerate(c_raw)]
    if any(not (0 <= c <= P) for c in cs):
        raise CanonicalGallaiCertificateError(f"Each coefficient c_q must lie in [0, {P}]")

    # pair_basis_vectors[q][i] is vector e_{p,q,i} in Q^k for q in 0..P-1, i in 0..t-1
    v_qi: List[List[VecQ]] = []
    for q, (a, b) in enumerate(pairs):
        if type(pb_raw[q]) is not list or len(pb_raw[q]) != t:
            raise CanonicalGallaiCertificateError(f"pair_basis_vectors[{q}] must have {t} vectors")
        vecs = [_parse_vec(pb_raw[q][i], k, f"pb[{q}][{i}]") for i in range(t)]
        # Must satisfy e_{p,q,a} - e_{p,q,b} NOT in U!
        if in_U(vec_sub(vecs[a], vecs[b])):
            raise CanonicalGallaiCertificateError(f"Pair q={q} ({a},{b}) violates e_{{p,q,a}} - e_{{p,q,b}} not in U")
        v_qi.append(vecs)

    # Compute x_i = sum_q c_q * v_{q,i}
    xs: List[VecQ] = [[Fraction(0, 1)] * k for _ in range(t)]
    for q in range(P):
        cq = Fraction(cs[q], 1)
        for i in range(t):
            xs[i] = vec_add(xs[i], vec_scale(cq, v_qi[q][i]))

    # Check rainbow: for EVERY pair (a, b), x_a - x_b NOT in U, AND verify Key Uniqueness Lemma explicitly!
    for q, (a, b) in enumerate(pairs):
        if in_U(vec_sub(xs[a], xs[b])):
            raise CanonicalGallaiCertificateError(f"Rainbow collision on pair ({a}, {b}): x_a - x_b in U")
        # Hold all other c_{q'} fixed and sweep c_q in 0..P: at most 1 bad value allowed!
        base_diff = [Fraction(0, 1)] * k
        for q2 in range(P):
            if q2 != q:
                base_diff = vec_add(base_diff, vec_scale(Fraction(cs[q2], 1), vec_sub(v_qi[q2][a], v_qi[q2][b])))
        dir_vec = vec_sub(v_qi[q][a], v_qi[q][b])
        bad_cnt = sum(1 for cand_c in range(P + 1) if in_U(vec_add(base_diff, vec_scale(Fraction(cand_c, 1), dir_vec))))
        if bad_cnt > 1:
            raise CanonicalGallaiCertificateError(f"Impossible: Key Uniqueness Lemma violated on pair {q} (bad={bad_cnt})")

    expected_lb = Fraction(1, P + 1)
    if _parse_rat(cert["claimed_surviving_prob_lb"], "claimed_surviving_prob_lb") != expected_lb:
        raise CanonicalGallaiCertificateError(f"claimed_surviving_prob_lb != 1/(P+1) = {expected_lb}")

    return {
        "verified": True,
        "mode": cert["mode"],
        "t_points": t,
        "ambient_k": k,
        "case": "rainbow",
        "distinct_colors": t,
        "union_bound_lb": str(expected_lb),
    }


def _verify_mode4_lift_and_2d_sum(cert: Dict[str, Any]) -> Dict[str, Any]:
    req = {
        "schema", "mode", "name", "t_points", "claimed_pair_count_P",
        "claimed_lift_dim_k", "claimed_grid_bound_m", "claimed_union_bound_lb",
        "sim2d_weights_c", "sim2d_params_ab", "claimed_sum_scale_sq",
    }
    if set(cert.keys()) != req:
        raise CanonicalGallaiCertificateError(f"Mode 4 key mismatch: {sorted(set(cert.keys()) ^ req)}")
    t = _parse_int(cert["t_points"], "t_points")
    if not (2 <= t <= 12):
        raise CanonicalGallaiCertificateError(f"t_points must be in [2, 12], got {t}")
    P = pair_count(t)
    k = lift_dim(t)
    m = grid_bound(t)
    lb = Fraction(1, P + 1)
    if _parse_int(cert["claimed_pair_count_P"], "claimed_pair_count_P") != P:
        raise CanonicalGallaiCertificateError("claimed_pair_count_P mismatch")
    if _parse_int(cert["claimed_lift_dim_k"], "claimed_lift_dim_k") != k:
        raise CanonicalGallaiCertificateError("claimed_lift_dim_k mismatch")
    if _parse_int(cert["claimed_grid_bound_m"], "claimed_grid_bound_m") != m:
        raise CanonicalGallaiCertificateError("claimed_grid_bound_m mismatch")
    if _parse_rat(cert["claimed_union_bound_lb"], "claimed_union_bound_lb") != lb:
        raise CanonicalGallaiCertificateError("claimed_union_bound_lb mismatch")

    c_raw = cert["sim2d_weights_c"]
    ab_raw = cert["sim2d_params_ab"]
    if type(c_raw) is not list or type(ab_raw) is not list or len(c_raw) != P or len(ab_raw) != P:
        raise CanonicalGallaiCertificateError(f"sim2d_weights_c and sim2d_params_ab must have length P={P}")
    cs = [_parse_int(x, f"c[{q}]") for q, x in enumerate(c_raw)]
    if any(not (0 <= c <= P) for c in cs):
        raise CanonicalGallaiCertificateError(f"Each weight c_q must lie in [0, {P}]")
    sum_a = Fraction(0, 1)
    sum_b = Fraction(0, 1)
    for q in range(P):
        if type(ab_raw[q]) is not list or len(ab_raw[q]) != 2:
            raise CanonicalGallaiCertificateError(f"sim2d_params_ab[{q}] must be [a_q, b_q]")
        aq = _parse_rat(ab_raw[q][0], f"a[{q}]")
        bq = _parse_rat(ab_raw[q][1], f"b[{q}]")
        if aq * aq + bq * bq == 0:
            raise CanonicalGallaiCertificateError(f"Component similarity {q} is degenerate (0, 0)")
        sum_a += cs[q] * aq
        sum_b += cs[q] * bq
    scale_sq = sum_a * sum_a + sum_b * sum_b
    if scale_sq <= 0:
        raise CanonicalGallaiCertificateError("Linear combination of 2D similarities collapsed to 0 (degenerate!)")
    if _parse_rat(cert["claimed_sum_scale_sq"], "claimed_sum_scale_sq") != scale_sq:
        raise CanonicalGallaiCertificateError(f"claimed_sum_scale_sq mismatch: exact={scale_sq}")

    return {
        "verified": True,
        "mode": cert["mode"],
        "t_points": t,
        "P": P,
        "lift_dim_k": k,
        "grid_bound_m": m,
        "sum_scale_sq": str(scale_sq),
    }


def verify_canonical_gallai_certificate_exact(cert: Dict[str, Any]) -> Dict[str, Any]:
    if type(cert) is not dict:
        raise CanonicalGallaiCertificateError("Certificate root must be a dict")
    _assert_strict_json_types(cert)
    if cert.get("schema") != SCHEMA_VERSION:
        raise CanonicalGallaiCertificateError(f"Invalid schema: {cert.get('schema')!r}")
    name = cert.get("name")
    if type(name) is not str or not name.strip():
        raise CanonicalGallaiCertificateError(f"Certificate name must be non-empty str, got {name!r}")
    mode = cert.get("mode")
    if mode == "rational_similarity_copy_exact":
        return _verify_mode1_similarity_copy(cert)
    if mode == "homothety_obstruction_vs_rotation_exact":
        return _verify_mode2_homothety_vs_rotation(cert)
    if mode == "subspace_coloring_dichotomy_exact":
        return _verify_mode3_subspace_dichotomy(cert)
    if mode == "lift_union_bound_and_2d_sum_exact":
        return _verify_mode4_lift_and_2d_sum(cert)
    raise CanonicalGallaiCertificateError(f"Unknown mode: {mode!r}")
