"""Generate all 16 canonical CANONICAL-GALLAI-CERT-1.0 certificates and 4 experiment JSONs for Paper 26.
Author: Lluis Eriksson
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from fractions import Fraction
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gallai_certifier import verify_canonical_gallai_certificate_exact
from src.gallai_exact import (
    fmt_rat,
    grid_bound,
    lift_dim,
    mat_vec_mul,
    pair_count,
    vec_add,
)

RESULTS = ROOT / "results"
CERTS = RESULTS / "certificates"
RESULTS.mkdir(parents=True, exist_ok=True)
CERTS.mkdir(parents=True, exist_ok=True)


def _fmt_vec(v: List[Fraction]) -> List[str]:
    return [fmt_rat(x) for x in v]


def _fmt_mat(M: List[List[Fraction]]) -> List[List[str]]:
    return [_fmt_vec(r) for r in M]


def _emit_cert(filename: str, cert: Dict) -> Dict:
    t0 = time.perf_counter()
    summary = verify_canonical_gallai_certificate_exact(cert)
    ms = (time.perf_counter() - t0) * 1000.0
    (CERTS / filename).write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    return {"file": filename, "mode": cert["mode"], "verify_ms": round(ms, 4), "summary": summary}


def main() -> None:
    atlas_rows = []

    # =========================================================================
    # MODE 1: 4 Exact Rational Similarity Copy Certificates (2D & 3D, Mono & Rainbow)
    # =========================================================================
    # 1a: Unit square {0,1}^2 rotated by Pythagorean (3,-4; 4,3) -> rainbow under x-coord!
    sq = [[Fraction(0), Fraction(0)], [Fraction(1), Fraction(0)], [Fraction(0), Fraction(1)], [Fraction(1), Fraction(1)]]
    M1a = [[Fraction(3, 5), Fraction(-4, 5)], [Fraction(4, 5), Fraction(3, 5)]]
    v1a = [Fraction(2, 1), Fraction(-1, 1)]
    T1a = [vec_add(mat_vec_mul(M1a, p), v1a) for p in sq]
    atlas_rows.append(_emit_cert("sim2d_square_345_rainbow.cert.json", {
        "schema": "CANONICAL-GALLAI-CERT-1.0",
        "mode": "rational_similarity_copy_exact",
        "name": "mode1_square_345_rainbow",
        "dim_d": 2,
        "source_points": [_fmt_vec(p) for p in sq],
        "target_points": [_fmt_vec(p) for p in T1a],
        "sim_matrix": _fmt_mat(M1a),
        "translation": _fmt_vec(v1a),
        "claimed_scale_sq": "1",
        "color_functional_w": ["1", "0"],
        "claimed_coloring_type": "rainbow",
    }))

    # 1b: Collinear 4-point arithmetic progression rotated onto x = const -> monochromatic!
    ap4 = [[Fraction(k), Fraction(0)] for k in range(4)]
    M1b = [[Fraction(0), Fraction(-2)], [Fraction(2), Fraction(0)]]
    v1b = [Fraction(5), Fraction(1)]
    T1b = [vec_add(mat_vec_mul(M1b, p), v1b) for p in ap4]
    atlas_rows.append(_emit_cert("sim2d_ap4_rotated_mono.cert.json", {
        "schema": "CANONICAL-GALLAI-CERT-1.0",
        "mode": "rational_similarity_copy_exact",
        "name": "mode1_ap4_rotated_mono",
        "dim_d": 2,
        "source_points": [_fmt_vec(p) for p in ap4],
        "target_points": [_fmt_vec(p) for p in T1b],
        "sim_matrix": _fmt_mat(M1b),
        "translation": _fmt_vec(v1b),
        "claimed_scale_sq": "4",
        "color_functional_w": ["1", "0"],
        "claimed_coloring_type": "monochromatic",
    }))

    # 1c: 2D 5-point house pentagon scaled & rotated by (5,-12; 12,5)/13 -> rainbow under x-coord!
    pent = [[Fraction(0), Fraction(0)], [Fraction(2), Fraction(0)], [Fraction(2), Fraction(2)],
            [Fraction(1), Fraction(3)], [Fraction(0), Fraction(2)]]
    M1c = [[Fraction(5, 13), Fraction(-12, 13)], [Fraction(12, 13), Fraction(5, 13)]]
    v1c = [Fraction(1, 2), Fraction(1, 3)]
    T1c = [vec_add(mat_vec_mul(M1c, p), v1c) for p in pent]
    atlas_rows.append(_emit_cert("sim2d_pentagon_51213_rainbow.cert.json", {
        "schema": "CANONICAL-GALLAI-CERT-1.0",
        "mode": "rational_similarity_copy_exact",
        "name": "mode1_pentagon_51213_rainbow",
        "dim_d": 2,
        "source_points": [_fmt_vec(p) for p in pent],
        "target_points": [_fmt_vec(p) for p in T1c],
        "sim_matrix": _fmt_mat(M1c),
        "translation": _fmt_vec(v1c),
        "claimed_scale_sq": "1",
        "color_functional_w": ["1", "0"],
        "claimed_coloring_type": "rainbow",
    }))

    # 1d: 3D unit cube {0,1}^3 (8 points) rotated by exact rational 3D orthogonal matrix (Pythagorean quaternion (1,2,2,0) -> /9)!
    # Quaternion q = (1, 2, 2, 0), |q|^2 = 9: R = (1/9) * [[1, 4, -8], [4, 7, 4], [8, -4, 1]]? Let's use exact Euler/Rodrigues:
    # q = (1, 1, 2, 3), |q|^2 = 15: let's check simple exact rational 3D orthogonal matrix (1/7)*[[2,3,6],[3,-6,2],[6,2,-3]]:
    # Check rows: 4+9+36=49; 9+36+4=49; 36+4+9=49; dots: 6-18+12=0; 12+6-18=0; 18-12-6=0! EXACT 3D ORTHOGONAL!!
    cube = [[Fraction(a), Fraction(b), Fraction(c)] for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    M1d = [
        [Fraction(2, 7), Fraction(3, 7), Fraction(6, 7)],
        [Fraction(3, 7), Fraction(-6, 7), Fraction(2, 7)],
        [Fraction(6, 7), Fraction(2, 7), Fraction(-3, 7)],
    ]
    # Note: 2*a + 3*b + 6*c for a,b,c in {0,1} yields {0, 2, 3, 5, 6, 8, 9, 11} — ALL 8 PAIRWISE DISTINCT -> RAINBOW!
    v1d = [Fraction(0), Fraction(0), Fraction(0)]
    T1d = [vec_add(mat_vec_mul(M1d, p), v1d) for p in cube]
    atlas_rows.append(_emit_cert("sim3d_cube8_236_rainbow.cert.json", {
        "schema": "CANONICAL-GALLAI-CERT-1.0",
        "mode": "rational_similarity_copy_exact",
        "name": "mode1_cube8_236_rainbow",
        "dim_d": 3,
        "source_points": [_fmt_vec(p) for p in cube],
        "target_points": [_fmt_vec(p) for p in T1d],
        "sim_matrix": _fmt_mat(M1d),
        "translation": _fmt_vec(v1d),
        "claimed_scale_sq": "1",
        "color_functional_w": ["1", "0", "0"],
        "claimed_coloring_type": "rainbow",
    }))

    # =========================================================================
    # MODE 2: 4 Exact Homothety-Obstruction vs. Rotation-Rainbow Rescue Certificates (p. 2)
    # =========================================================================
    rot345 = [[Fraction(3, 5), Fraction(-4, 5)], [Fraction(4, 5), Fraction(3, 5)]]
    rot51213 = [[Fraction(5, 13), Fraction(-12, 13)], [Fraction(12, 13), Fraction(5, 13)]]
    rot81517 = [[Fraction(8, 17), Fraction(-15, 17)], [Fraction(15, 17), Fraction(8, 17)]]
    m2_cases = [
        ("obstruct_square4_xcoord.cert.json", "mode2_square4_xcoord", sq, [Fraction(1), Fraction(0)], rot345, 2, 4),
        (
            "obstruct_grid6_rect_xcoord.cert.json", "mode2_grid6_rect",
            [[Fraction(x), Fraction(y)] for x in (0, 1, 2) for y in (0, 1)],
            [Fraction(1), Fraction(0)], rot345, 3, 6,
        ),
        (
            "obstruct_diamond4_diag.cert.json", "mode2_diamond4_diag",
            [[Fraction(1), Fraction(0)], [Fraction(-1), Fraction(0)], [Fraction(0), Fraction(1)], [Fraction(0), Fraction(-1)]],
            [Fraction(1), Fraction(1)], rot51213, 2, 4,
        ),
        (
            "obstruct_grid3x3_9pts.cert.json", "mode2_grid3x3_9pts",
            [[Fraction(x), Fraction(y)] for x in (0, 1, 2) for y in (0, 1, 2)],
            [Fraction(1), Fraction(0)], rot81517, 3, 9,
        ),
    ]
    for fname, cname, pts, w, R, hc, rc in m2_cases:
        atlas_rows.append(_emit_cert(fname, {
            "schema": "CANONICAL-GALLAI-CERT-1.0",
            "mode": "homothety_obstruction_vs_rotation_exact",
            "name": cname,
            "source_points": [_fmt_vec(p) for p in pts],
            "color_functional_w": _fmt_vec(w),
            "rotation_matrix": _fmt_mat(R),
            "claimed_homothety_colors": hc,
            "claimed_rotated_colors": rc,
        }))

    # =========================================================================
    # MODE 3: 4 Subspace-Coloring Dichotomy & Key Uniqueness Lemma Certificates (Thm 3 + p. 4)
    # =========================================================================
    # 3a: Monochromatic case t=4, k=4: H = [[1,1,1,1]] -> H(e_i - e_j) = 0 for all i, j!
    atlas_rows.append(_emit_cert("subspace_mono_t4_k4.cert.json", {
        "schema": "CANONICAL-GALLAI-CERT-1.0",
        "mode": "subspace_coloring_dichotomy_exact",
        "name": "mode3_subspace_mono_t4",
        "t_points": 4,
        "ambient_k": 4,
        "annihilator_H": [["1", "1", "1", "1"]],
        "case_type": "monochromatic",
        "pair_basis_vectors": [],
        "coefficients_c": [],
        "claimed_surviving_prob_lb": "1",
    }))

    # Helper to construct clean disjoint-block pair-indexed basis vectors e_{p,q,i} in Q^{P*t}
    def build_rainbow_subspace_cert(fname: str, cname: str, t: int, H_row: List[int], cs: List[int]) -> Dict:
        P = pair_count(t)
        k = P * t
        pb = []
        for q in range(P):
            vecs = []
            for i in range(t):
                v = ["0"] * k
                v[q * t + i] = "1"
                vecs.append(v)
            pb.append(vecs)
        return _emit_cert(fname, {
            "schema": "CANONICAL-GALLAI-CERT-1.0",
            "mode": "subspace_coloring_dichotomy_exact",
            "name": cname,
            "t_points": t,
            "ambient_k": k,
            "annihilator_H": [[str(x) for x in H_row]],
            "case_type": "rainbow",
            "pair_basis_vectors": pb,
            "coefficients_c": cs,
            "claimed_surviving_prob_lb": fmt_rat(Fraction(1, P + 1)),
        })

    # 3b: Rainbow t=3 (P=3, k=9), non-trivial rank-1 annihilator H = [1,2,4, 2,5,3, 3,1,6]
    # Check each pair (a,b) in block q has H[q*3+a] != H[q*3+b] and choose valid c_q in 0..3:
    H3 = [1, 2, 4, 2, 5, 3, 3, 1, 6]
    # Try exact search for rainbow c in {0..3}^3 (guaranteed by union bound >= 1/4!)
    def find_rainbow_c(t: int, H_row: List[int]) -> List[int]:
        P = pair_count(t)
        pairs = [(i, j) for i in range(t) for j in range(i + 1, t)]
        from itertools import product
        for cs in product(range(P + 1), repeat=P):
            vals = [sum(cs[q] * H_row[q * t + i] for q in range(P)) for i in range(t)]
            if len(set(vals)) == t:
                return list(cs)
        raise RuntimeError("Impossible by Theorem 2 union bound!")

    atlas_rows.append(build_rainbow_subspace_cert("subspace_rainbow_t3_k9.cert.json", "mode3_rainbow_t3", 3, H3, find_rainbow_c(3, H3)))

    # 3c: Rainbow t=4 (P=6, k=24), non-trivial rank-1 annihilator H
    H4 = [1, 2, 4, 7,  2, 5, 1, 6,  3, 1, 5, 2,  4, 2, 7, 1,  1, 6, 3, 5,  5, 2, 1, 4]
    # Pick deterministic non-colliding c in {0..6}^6 cleanly
    def find_rainbow_c_fast(t: int, H_row: List[int]) -> List[int]:
        P = pair_count(t)
        # Greedy/deterministic search in {0..P}^P
        cs = [1] * P
        for step in range(500):
            vals = [sum(cs[q] * H_row[q * t + i] for q in range(P)) for i in range(t)]
            if len(set(vals)) == t:
                return cs
            q_mod = step % P
            cs[q_mod] = (cs[q_mod] + 1) % (P + 1)
        raise RuntimeError("Could not find rainbow c")

    atlas_rows.append(build_rainbow_subspace_cert("subspace_rainbow_t4_k24.cert.json", "mode3_rainbow_t4", 4, H4, find_rainbow_c_fast(4, H4)))

    # 3d: Rainbow t=5 (P=10, k=50), non-trivial rank-1 annihilator H
    H5 = [(3 * q + 2 * i + ((q * i) % 5) + 1) for q in range(10) for i in range(5)]
    atlas_rows.append(build_rainbow_subspace_cert("subspace_rainbow_t5_k50.cert.json", "mode3_rainbow_t5", 5, H5, find_rainbow_c_fast(5, H5)))

    # =========================================================================
    # MODE 4: 4 Lift Dimension, Union Bound & 2D Similarity-Sum Closure Certificates
    # =========================================================================
    m4_ts = [3, 4, 5, 6]
    for t in m4_ts:
        P = pair_count(t)
        cs = [(q % P) + 1 for q in range(P)]
        ab = [[Fraction(3 + (q % 3), 5), Fraction(4 - (q % 3), 5)] for q in range(P)]
        sa = sum((cs[q] * ab[q][0] for q in range(P)), Fraction(0, 1))
        sb = sum((cs[q] * ab[q][1] for q in range(P)), Fraction(0, 1))
        atlas_rows.append(_emit_cert(f"lift_union_2dsum_t{t}.cert.json", {
            "schema": "CANONICAL-GALLAI-CERT-1.0",
            "mode": "lift_union_bound_and_2d_sum_exact",
            "name": f"mode4_lift_t{t}",
            "t_points": t,
            "claimed_pair_count_P": P,
            "claimed_lift_dim_k": lift_dim(t),
            "claimed_grid_bound_m": grid_bound(t),
            "claimed_union_bound_lb": fmt_rat(Fraction(1, P + 1)),
            "sim2d_weights_c": cs,
            "sim2d_params_ab": [[fmt_rat(a), fmt_rat(b)] for a, b in ab],
            "claimed_sum_scale_sq": fmt_rat(sa * sa + sb * sb),
        }))

    (RESULTS / "exp1_certified_atlas.json").write_text(
        json.dumps({"experiment": "exp1_certified_atlas", "count": len(atlas_rows), "rows": atlas_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    # =========================================================================
    # EXP 2: Lift Dimension k(t), Grid Bound m(t), and Rainbow Survival LB 1/(P+1) across t = 2..10
    # =========================================================================
    exp2_rows = []
    for t in range(2, 11):
        P = pair_count(t)
        exp2_rows.append({
            "t_points": t,
            "pair_count_P": P,
            "lift_dim_k": lift_dim(t),
            "grid_bound_m": grid_bound(t),
            "union_bound_lb_exact": fmt_rat(Fraction(1, P + 1)),
            "union_bound_lb": round(1.0 / (P + 1), 6),
        })
    (RESULTS / "exp2_lift_scaling.json").write_text(
        json.dumps({"experiment": "exp2_lift_scaling", "rows": exp2_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    # =========================================================================
    # EXP 3: Exhaustive Exact Rainbow Fraction on {0..P}^P for t=3 (4^3 = 64 choices) vs Union Bound 1/4!
    # =========================================================================
    from itertools import product
    exp3_rows = []
    test_H3s = [
        ("H3_spread", [1, 2, 4, 2, 5, 3, 3, 1, 6]),
        ("H3_tight", [1, 2, 3, 1, 2, 3, 1, 2, 3]),
        ("H3_skewed", [1, 3, 2, 4, 1, 5, 2, 6, 1]),
        ("H3_sparse", [0, 1, 2, 1, 0, 3, 2, 3, 0]),
    ]
    for label, H_row in test_H3s:
        total = 4 ** 3
        rainbow_cnt = 0
        for c0, c1, c2 in product(range(4), repeat=3):
            v0 = c0 * H_row[0] + c1 * H_row[3] + c2 * H_row[6]
            v1 = c0 * H_row[1] + c1 * H_row[4] + c2 * H_row[7]
            v2 = c0 * H_row[2] + c1 * H_row[5] + c2 * H_row[8]
            if len({v0, v1, v2}) == 3:
                rainbow_cnt += 1
        frac = Fraction(rainbow_cnt, total)
        exp3_rows.append({
            "instance": label,
            "rainbow_count": rainbow_cnt,
            "total_choices": total,
            "exact_prob": fmt_rat(frac),
            "prob_float": round(float(frac), 6),
            "union_bound_lb": 0.25,
        })
    (RESULTS / "exp3_exhaustive_rainbow_prob.json").write_text(
        json.dumps({"experiment": "exp3_exhaustive_rainbow_prob", "rows": exp3_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    # =========================================================================
    # EXP 4: Homothety Color Count vs Rotated Rainbow Color Count across 4 2D Shapes
    # =========================================================================
    exp4_rows = [
        {"shape": "Unit Square (4)", "t_points": 4, "homothety_colors": 2, "rotated_colors": 4},
        {"shape": "2x3 Grid (6)", "t_points": 6, "homothety_colors": 3, "rotated_colors": 6},
        {"shape": "Diamond (4)", "t_points": 4, "homothety_colors": 2, "rotated_colors": 4},
        {"shape": "3x3 Grid (9)", "t_points": 9, "homothety_colors": 3, "rotated_colors": 9},
    ]
    (RESULTS / "exp4_homothety_vs_rotation.json").write_text(
        json.dumps({"experiment": "exp4_homothety_vs_rotation", "rows": exp4_rows}, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"[PASS] Generated & verified {len(atlas_rows)}/16 exact-Q certificates and 4 experiment JSONs.")
    for r in atlas_rows:
        print(f"  {r['file']:44s} {r['verify_ms']:6.3f} ms  {r['summary']}")


if __name__ == "__main__":
    main()
