"""Pure-stdlib zero-float exact-Q Euclidean similarity and subspace-coloring engine.
Aligned with Randall Shaw (arXiv:2611.33136, Nov 24, 2026)
"A canonical Euclidean Gallai theorem".

Author: Lluis Eriksson
"""
from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple

VecQ = List[Fraction]
MatQ = List[List[Fraction]]


def dot_q(u: Sequence[Fraction], v: Sequence[Fraction]) -> Fraction:
    return sum((a * b for a, b in zip(u, v)), Fraction(0, 1))


def vec_sub(u: Sequence[Fraction], v: Sequence[Fraction]) -> VecQ:
    return [a - b for a, b in zip(u, v)]


def vec_add(u: Sequence[Fraction], v: Sequence[Fraction]) -> VecQ:
    return [a + b for a, b in zip(u, v)]


def vec_scale(c: Fraction, u: Sequence[Fraction]) -> VecQ:
    return [c * a for a in u]


def dist_sq_q(u: Sequence[Fraction], v: Sequence[Fraction]) -> Fraction:
    return sum(((a - b) * (a - b) for a, b in zip(u, v)), Fraction(0, 1))


def mat_vec_mul(M: MatQ, v: Sequence[Fraction]) -> VecQ:
    return [dot_q(row, v) for row in M]


def mat_transpose(M: MatQ) -> MatQ:
    r, c = len(M), len(M[0])
    return [[M[i][j] for i in range(r)] for j in range(c)]


def mat_mul(A: MatQ, B: MatQ) -> MatQ:
    m, k, n = len(A), len(A[0]), len(B[0])
    return [
        [sum((A[i][t] * B[t][j] for t in range(k)), Fraction(0, 1)) for j in range(n)]
        for i in range(m)
    ]


def is_scaled_orthogonal_exact(M: MatQ) -> Tuple[bool, Fraction]:
    """Check if M^T M == s^2 * I_d with s^2 > 0 over Q."""
    d = len(M)
    if d == 0 or any(len(row) != d for row in M):
        return False, Fraction(0, 1)
    gram = mat_mul(mat_transpose(M), M)
    s2 = gram[0][0]
    if s2 <= 0:
        return False, Fraction(0, 1)
    for i in range(d):
        for j in range(d):
            expected = s2 if i == j else Fraction(0, 1)
            if gram[i][j] != expected:
                return False, Fraction(0, 1)
    return True, s2


def pair_count(t: int) -> int:
    return (t * (t - 1)) // 2


def lift_dim(t: int) -> int:
    p = pair_count(t)
    return t + t * p * (p - 1)


def grid_bound(t: int) -> int:
    p = pair_count(t)
    return p * (p + 1)


def fmt_rat(q: Fraction) -> str:
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"
