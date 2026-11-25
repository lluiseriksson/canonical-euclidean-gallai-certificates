"""Gate-2 verification, exhaustive 4^3 rainbow probability cross-checks, and 54-attack live red-team suite for Paper 26.
Author: Lluis Eriksson
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
from decimal import Decimal
from fractions import Fraction
from itertools import product

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.gallai_certifier import (
    CanonicalGallaiCertificateError,
    verify_canonical_gallai_certificate_exact,
)
from src.gallai_exact import (
    dist_sq_q,
    is_scaled_orthogonal_exact,
    mat_vec_mul,
)

CERTS_DIR = ROOT / "results" / "certificates"


def test_exhaustive_rainbow_union_bound_and_3d_orthogonality_cross_checks() -> None:
    """Independently cross-check exact rainbow probability over {0..3}^3 (64 tuples) and 3D cube pairwise distances."""
    c3 = json.loads((CERTS_DIR / "subspace_rainbow_t3_k9.cert.json").read_text(encoding="utf-8"))
    H_row = [Fraction(x) for x in c3["annihilator_H"][0]]
    rainbow_cnt = 0
    for c0, c1, c2 in product(range(4), repeat=3):
        vals = [c0 * H_row[i] + c1 * H_row[3 + i] + c2 * H_row[6 + i] for i in range(3)]
        if len(set(vals)) == 3:
            rainbow_cnt += 1
    # Exact probability MUST satisfy rainbow_cnt / 64 >= 1 / (P + 1) = 1/4 (at least 16/64!)
    assert Fraction(rainbow_cnt, 64) >= Fraction(1, 4)

    # Cross-check 3D cube 8-vertex exact isometry: 12 edges of d^2=1, 12 face diagonals of d^2=2, 4 space diagonals of d^2=3
    c1d = json.loads((CERTS_DIR / "sim3d_cube8_236_rainbow.cert.json").read_text(encoding="utf-8"))
    T = [[Fraction(x) for x in p] for p in c1d["target_points"]]
    M = [[Fraction(x) for x in row] for row in c1d["sim_matrix"]]
    ok, s2 = is_scaled_orthogonal_exact(M)
    assert ok and s2 == Fraction(1, 1)
    dists = sorted(dist_sq_q(T[i], T[j]) for i in range(8) for j in range(i + 1, 8))
    assert dists.count(Fraction(1)) == 12
    assert dists.count(Fraction(2)) == 12
    assert dists.count(Fraction(3)) == 4
    assert len({p[0] for p in T}) == 8  # All 8 x-coordinates pairwise distinct (rainbow!)


def test_all_16_certificates_verify_cleanly() -> None:
    files = sorted(CERTS_DIR.glob("*.cert.json"))
    assert len(files) == 16
    for f in files:
        res = verify_canonical_gallai_certificate_exact(json.loads(f.read_text(encoding="utf-8")))
        assert res["verified"] is True


def test_57_live_adversarial_red_team_attacks_rejected() -> None:
    c1 = json.loads((CERTS_DIR / "sim2d_square_345_rainbow.cert.json").read_text(encoding="utf-8"))
    c2 = json.loads((CERTS_DIR / "obstruct_square4_xcoord.cert.json").read_text(encoding="utf-8"))
    c3m = json.loads((CERTS_DIR / "subspace_mono_t4_k4.cert.json").read_text(encoding="utf-8"))
    c3r = json.loads((CERTS_DIR / "subspace_rainbow_t3_k9.cert.json").read_text(encoding="utf-8"))
    c4 = json.loads((CERTS_DIR / "lift_union_2dsum_t4.cert.json").read_text(encoding="utf-8"))

    attacks = []

    def add(name, base, fn):
        cand = copy.deepcopy(base)
        fn(cand)
        attacks.append((name, cand))

    # Group A: Schema, Types & Canonical Rationals (16 attacks)
    attacks.append(("01_root_not_dict", ["bad"]))
    add("02_wrong_schema", c1, lambda x: x.__setitem__("schema", "CANONICAL-GALLAI-CERT-9.9"))
    add("03_unknown_mode", c1, lambda x: x.__setitem__("mode", "bogus"))
    add("04_extra_key", c1, lambda x: x.__setitem__("evil", 1))
    add("05_missing_key", c1, lambda x: x.pop("sim_matrix"))
    add("06_float_injection", c1, lambda x: x["translation"].__setitem__(0, 2.0))
    add("07_bool_injection", c1, lambda x: x.__setitem__("dim_d", True))
    add("08_decimal_injection", c1, lambda x: x.__setitem__("claimed_scale_sq", Decimal("1")))
    add("09_complex_injection", c1, lambda x: x["translation"].__setitem__(0, 1 + 0j))
    add("10_tuple_injection", c1, lambda x: x.__setitem__("translation", tuple(x["translation"])))
    add("11_non_str_key", c1, lambda x: x.__setitem__(99, "bad"))
    add("12_unreduced_frac", c1, lambda x: x["sim_matrix"][0].__setitem__(0, "6/10"))
    add("13_denom_one_frac", c1, lambda x: x.__setitem__("claimed_scale_sq", "1/1"))
    add("14_neg_zero", c1, lambda x: x["source_points"][0].__setitem__(0, "-0"))
    add("15_non_str_name", c1, lambda x: x.__setitem__("name", 123))
    add("16_empty_name", c1, lambda x: x.__setitem__("name", "   "))

    # Group B: Mode 1 Rational Similarity Copy Forgeries (11 attacks)
    add("17_dim_d_4", c1, lambda x: x.__setitem__("dim_d", 4))
    add("18_duplicate_source_pt", c1, lambda x: x["source_points"].__setitem__(1, x["source_points"][0]))
    add("19_shear_matrix_not_orthog", c1, lambda x: x.__setitem__("sim_matrix", [["1", "1"], ["0", "1"]]))
    add("20_zero_matrix_degenerate", c1, lambda x: x.__setitem__("sim_matrix", [["0", "0"], ["0", "0"]]))
    add("21_wrong_claimed_scale_sq", c1, lambda x: x.__setitem__("claimed_scale_sq", "2"))
    add("22_perturbed_target_point", c1, lambda x: x["target_points"][0].__setitem__(0, "99"))
    add("23_zero_color_functional", c1, lambda x: x.__setitem__("color_functional_w", ["0", "0"]))
    add("24_wrong_coloring_type_mono", c1, lambda x: x.__setitem__("claimed_coloring_type", "monochromatic"))
    add("25_unrotated_square_2colors_rejected", c1, lambda x: (
        x.__setitem__("sim_matrix", [["1", "0"], ["0", "1"]]),
        x.__setitem__("translation", ["0", "0"]),
        x.__setitem__("target_points", x["source_points"]),
    ))
    add("26_mismatched_source_target_len", c1, lambda x: x["target_points"].pop())
    add("27_anisotropic_stretch_rejected", c1, lambda x: x.__setitem__("sim_matrix", [["2", "0"], ["0", "1"]]))

    # Group C: Mode 2 Homothety Obstruction vs Rotation Forgeries (8 attacks)
    add("28_no_obstruction_already_rainbow", c2, lambda x: x.__setitem__("color_functional_w", ["1", "2"]))
    add("29_wrong_homothety_colors", c2, lambda x: x.__setitem__("claimed_homothety_colors", 3))
    add("30_non_unit_rotation_matrix", c2, lambda x: x.__setitem__("rotation_matrix", [["3", "-4"], ["4", "3"]]))
    add("31_identity_rotation_fails_rainbow", c2, lambda x: x.__setitem__("rotation_matrix", [["1", "0"], ["0", "1"]]))
    add("32_wrong_rotated_colors", c2, lambda x: x.__setitem__("claimed_rotated_colors", 3))
    add("33_zero_w_mode2", c2, lambda x: x.__setitem__("color_functional_w", ["0", "0"]))
    add("34_duplicate_pts_mode2", c2, lambda x: x["source_points"].__setitem__(1, x["source_points"][0]))
    add("35_too_few_pts_mode2", c2, lambda x: x.__setitem__("source_points", [["0", "0"], ["1", "0"]]))

    # Group D: Mode 3 Subspace Coloring & Key Uniqueness Forgeries (10 attacks)
    add("36_mono_broken_by_H", c3m, lambda x: x.__setitem__("annihilator_H", [["1", "2", "1", "1"]]))
    add("37_mono_wrong_prob", c3m, lambda x: x.__setitem__("claimed_surviving_prob_lb", "1/2"))
    add("38_invalid_case_type", c3r, lambda x: x.__setitem__("case_type", "mixed"))
    add("39_coeff_out_of_range", c3r, lambda x: x["coefficients_c"].__setitem__(0, 4))
    add("40_coeff_negative", c3r, lambda x: x["coefficients_c"].__setitem__(0, -1))
    add("41_all_zero_coeffs_collision", c3r, lambda x: x.__setitem__("coefficients_c", [0, 0, 0]))
    add("42_pair_basis_in_U_violated", c3r, lambda x: x["annihilator_H"][0].__setitem__(1, x["annihilator_H"][0][0]))
    add("43_wrong_union_bound_prob_mode3", c3r, lambda x: x.__setitem__("claimed_surviving_prob_lb", "1/3"))
    add("44_t_points_below_2", c3r, lambda x: x.__setitem__("t_points", 1))
    add("45_wrong_pb_length", c3r, lambda x: x["pair_basis_vectors"].pop())

    # Group E: Mode 4 Lift Dimension & 2D Similarity Sum Forgeries (9 attacks)
    add("46_wrong_pair_count_P", c4, lambda x: x.__setitem__("claimed_pair_count_P", 5))
    add("47_wrong_lift_dim_k", c4, lambda x: x.__setitem__("claimed_lift_dim_k", 120))
    add("48_wrong_grid_bound_m", c4, lambda x: x.__setitem__("claimed_grid_bound_m", 40))
    add("49_wrong_union_bound_lb", c4, lambda x: x.__setitem__("claimed_union_bound_lb", "1/6"))
    add("50_degenerate_zero_component_sim", c4, lambda x: x["sim2d_params_ab"].__setitem__(0, ["0", "0"]))
    add("51_sum_collapses_to_zero", c4, lambda x: x.__setitem__("sim2d_weights_c", [0] * 6))
    add("52_forged_sum_scale_sq", c4, lambda x: x.__setitem__("claimed_sum_scale_sq", "1"))
    add("53_t_above_12_mode4", c4, lambda x: x.__setitem__("t_points", 13))
    add("54_weight_above_P_mode4", c4, lambda x: x["sim2d_weights_c"].__setitem__(0, 7))
    # Group F: Mode 2 SO(2) Rotation & Mode 3 Monochromatic Auxiliary Field Forgeries (3 attacks -> 57 total!)
    add("55_mono_garbage_pair_basis", c3m, lambda x: x.__setitem__("pair_basis_vectors", ["garbage"]))
    add("56_mono_garbage_coeffs", c3m, lambda x: x.__setitem__("coefficients_c", [1]))
    add("57_mode2_reflection_det_neg1", c2, lambda x: x.__setitem__("rotation_matrix", [["3/5", "4/5"], ["4/5", "-3/5"]]))

    assert len(attacks) == 57
    for name, cand in attacks:
        with pytest.raises(CanonicalGallaiCertificateError):
            verify_canonical_gallai_certificate_exact(cand)
