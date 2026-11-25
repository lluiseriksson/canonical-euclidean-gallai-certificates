# Machine-Checked Exact-Rational Similarity, Subspace-Equivalence, and Rainbow Union-Bound Certificates for the Canonical Euclidean Gallai Theorem

**Author:** Lluis Eriksson (with transparent AI assistance via Google Antigravity)  
**License:** MIT (code, Lean 4 proofs, certificates) / CC-BY-4.0 (manuscript)

Zero-dependency Lean 4 formalization and pure-stdlib exact-$\mathbb{Q}$ certificate verifier (`CANONICAL-GALLAI-CERT-1.0`) for the algebraic, geometric, and probabilistic union-bound core of Randall Shaw (*A canonical Euclidean Gallai theorem*, `arXiv:2611.33136`, November 24, 2026).

## Verification Summary
- **Lean 4 Kernel (`lean/CanonicalEuclideanGallai.lean`, Lean 4.35.0):** 18/18 theorems, 0 warnings, 0 `sorry`, 0 `Classical.choice`, 3 zero-axiom theorems (`pythagorean_345_rotation_orthog`, `pythagorean_345_square_rainbow_x`, `lift_dimension_values_exact`) + 2 `[propext]` + 13 `[propext, Quot.sound]`, formalizing the homothety obstruction, 2D similarity scaling/sum-closure/composition, 3D homothety scaling, subspace equivalence, Randall Shaw's Key Uniqueness Lemma, lift dimensions, and inductive union-bound survival.
- **Exact-$\mathbb{Q}$ Certificate Atlas (`results/certificates/*.cert.json`):** 16 canonical certificates across 4 modes (2D/3D rational similarity copies including an 8-vertex 3D cube rainbow copy; homothety-obstruction vs. rotation-rainbow rescues; $\ker(H)$ subspace dichotomies with exhaustive Key Uniqueness Lemma sweeps up to $t=5, k=50$; lift dimensions & 2D similarity-sum closure), replayed with zero floats in `0.060`–`22.181 ms`.
- **Cross-Checks & Red-Team Suite (`tests/test_suite.py`):** Exhaustive $4^3 = 64$-tuple rainbow probability cross-check, 3D cube pairwise distance spectrum cross-check, 16/16 certificate replays, and **57/57** live adversarial attacks rejected.

## One-Command Reproducibility
```bash
python scripts/verify_all.py
```
To regenerate all certificates, experiment JSONs, and 300-DPI figures from scratch:
```bash
python scripts/run_all_experiments.py
python scripts/make_figures.py
python scripts/verify_all.py
```
