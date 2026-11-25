"""Generate 3 publication-quality 300-DPI figures for Paper 26.
Author: Lluis Eriksson
"""
from __future__ import annotations

import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIG_DIR = ROOT / "paper" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 9.5,
    "axes.titlesize": 10.0,
    "axes.labelsize": 9.2,
    "legend.fontsize": 7.3,
    "xtick.labelsize": 8.4,
    "ytick.labelsize": 8.4,
    "axes.grid": True,
    "grid.alpha": 0.28,
    "grid.linestyle": "--",
})


def make_fig1() -> None:
    d2 = json.loads((RESULTS / "exp2_lift_scaling.json").read_text(encoding="utf-8"))
    d3 = json.loads((RESULTS / "exp3_exhaustive_rainbow_prob.json").read_text(encoding="utf-8"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.65), dpi=300)

    # Panel (a): Lift dimension k(t) and grid side m(t) scaling with configuration size t
    r2 = d2["rows"]
    ts = [r["t_points"] for r in r2]
    ks = [r["lift_dim_k"] for r in r2]
    ms = [r["grid_bound_m"] for r in r2]
    ax1.semilogy(ts, ks, "o-", color="#1b6ca8", lw=2.1, ms=5.6,
                 label=r"Ambient lift dimension $k(t) = t + t P(P-1)$")
    ax1.semilogy(ts, ms, "s--", color="#c1121f", lw=1.9, ms=5.4,
                 label=r"DGPV grid bound $m(t) = P(P+1)$")
    ax1.set_xticks(ts)
    ax1.set_xlabel(r"Configuration cardinality $t = |S|$")
    ax1.set_ylabel(r"Exact integer parameter (log scale)")
    ax1.set_title(r"(a) Theorem 2 Ambient Lift & Grid Growth")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.94)

    # Panel (b): Exhaustive rainbow probability on {0..3}^3 (64 choices) vs union bound 1/4
    r3 = d3["rows"]
    labels = ["Spread", "Tight", "Skewed", "Sparse"]
    probs = [r["prob_float"] for r in r3]
    x = np.arange(len(labels))
    bars = ax2.bar(x, probs, width=0.52, color="#2a9d8f", edgecolor="#222", lw=0.75,
                   label=r"Exact rainbow fraction on $\{0,1,2,3\}^3$")
    ax2.axhline(0.25, color="#c1121f", lw=1.6, ls="--", label=r"Theorem 2 union bound $\frac{1}{P+1} = \frac{1}{4}$")
    for xv, pv, r in zip(x, probs, r3):
        ax2.text(xv, pv + 0.02, r["exact_prob"], ha="center", va="bottom", fontsize=7.8, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=8.2)
    ax2.set_ylim(0, 1.32)
    ax2.set_xlabel(r"Rank-1 annihilator instance ($t=3, P=3, k=9$)")
    ax2.set_ylabel(r"Exact rainbow probability")
    ax2.set_title(r"(b) Exact Rainbow Probability vs. Union Bound ($1/4$)")
    ax2.legend(loc="upper right", frameon=True, framealpha=0.95)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig1_lift_and_rainbow_prob.png", dpi=300)
    plt.close(fig)


def make_fig2() -> None:
    d4 = json.loads((RESULTS / "exp4_homothety_vs_rotation.json").read_text(encoding="utf-8"))
    rows = d4["rows"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.65), dpi=300)

    # Panel (a): Visual p. 2 obstruction: unit square {0,1}^2 (2 x-colors) vs (3,-4;4,3)/5 rotated square (4 rainbow x-colors)
    sq = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], dtype=float)
    R = np.array([[0.6, -0.8], [0.8, 0.6]])
    sq_rot = (R @ sq.T).T + np.array([2.2, 0.0])
    # Draw vertical x-color stripes for original square
    for xv in [0.0, 1.0]:
        ax1.axvline(xv, color="#c1121f", lw=1.0, ls=":", alpha=0.65)
    for xv in sorted({p[0] for p in sq_rot[:-1]}):
        ax1.axvline(xv, color="#2a9d8f", lw=1.0, ls="--", alpha=0.65)
    ax1.plot(sq[:, 0], sq[:, 1], "o-", color="#c1121f", lw=2.0, ms=6.2, label=r"Homothety $\{0,1\}^2$: 2 $x$-colors")
    ax1.plot(sq_rot[:, 0], sq_rot[:, 1], "s-", color="#2a9d8f", lw=2.0, ms=6.0,
             label=r"Rotated $\frac{1}{5}(3,-4;4,3)$: 4 rainbow $x$-colors")
    ax1.set_xlim(-0.35, 3.25)
    ax1.set_ylim(-0.25, 1.85)
    ax1.set_xlabel(r"$x$-coordinate (color class)")
    ax1.set_ylabel(r"$y$-coordinate")
    ax1.set_title(r"(a) Rotation Rescues Homothety Obstruction (p. 2)")
    ax1.legend(loc="upper left", frameon=True, framealpha=0.94, fontsize=7.0)

    # Panel (b): Homothety vs Rotated Rainbow Color Counts across 4 2D shapes
    shapes = [r["shape"] for r in rows]
    hc = [r["homothety_colors"] for r in rows]
    rc = [r["rotated_colors"] for r in rows]
    x = np.arange(len(shapes))
    w = 0.34
    ax2.bar(x - w / 2, hc, width=w, color="#c1121f", edgecolor="#222", lw=0.7, label="Unrotated homothety colors")
    ax2.bar(x + w / 2, rc, width=w, color="#2a9d8f", edgecolor="#222", lw=0.7, label="Rational rotation rainbow colors")
    for xv, hv, rv in zip(x, hc, rc):
        ax2.text(xv - w / 2, hv + 0.2, str(hv), ha="center", va="bottom", fontsize=7.8, fontweight="bold")
        ax2.text(xv + w / 2, rv + 0.2, str(rv), ha="center", va="bottom", fontsize=7.8, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(shapes, fontsize=7.6)
    ax2.set_ylim(0, 10.8)
    ax2.set_ylabel("Distinct color count")
    ax2.set_title("(b) Trapped Homotheties vs. Rotated Rainbows")
    ax2.legend(loc="upper left", frameon=True, framealpha=0.94, fontsize=7.2)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig2_homothety_vs_rotation.png", dpi=300)
    plt.close(fig)


def make_fig3() -> None:
    d1 = json.loads((RESULTS / "exp1_certified_atlas.json").read_text(encoding="utf-8"))
    rows = d1["rows"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.95), dpi=300, gridspec_kw={"width_ratios": [1.62, 1.0]})

    mode_colors = {
        "rational_similarity_copy_exact": "#1b6ca8",
        "homothety_obstruction_vs_rotation_exact": "#2a9d8f",
        "subspace_coloring_dichotomy_exact": "#e07a5f",
        "lift_union_bound_and_2d_sum_exact": "#c1121f",
    }
    labels = [r["file"].replace(".cert.json", "") for r in rows]
    ms = [r["verify_ms"] for r in rows]
    cols = [mode_colors[r["mode"]] for r in rows]
    y = np.arange(len(rows))
    ax1.barh(y, ms, color=cols, edgecolor="#222", lw=0.6, height=0.68)
    ax1.set_xscale("log")
    ax1.set_yticks(y)
    ax1.set_yticklabels(labels, fontsize=6.1)
    ax1.invert_yaxis()
    ax1.set_xlabel(r"Exact-$\mathbb{Q}$ verification latency (ms, log scale)")
    ax1.set_title(r"(a) Zero-Float Replay Latency Across 16 Certificates")

    counts = [
        sum(1 for r in rows if r["mode"] == "rational_similarity_copy_exact"),
        sum(1 for r in rows if r["mode"] == "homothety_obstruction_vs_rotation_exact"),
        sum(1 for r in rows if r["mode"] == "subspace_coloring_dichotomy_exact"),
        sum(1 for r in rows if r["mode"] == "lift_union_bound_and_2d_sum_exact"),
    ]
    m_labels = ["Mode 1\nSimilarity\nCopy", "Mode 2\nHomothety\nvs. Rot.", "Mode 3\nSubspace\nDichot.", "Mode 4\nLift &\n2D Sum"]
    bars = ax2.bar(range(4), counts, color=["#1b6ca8", "#2a9d8f", "#e07a5f", "#c1121f"], edgecolor="#222", lw=0.7)
    for b, c in zip(bars, counts):
        ax2.text(b.get_x() + b.get_width() / 2.0, c + 0.15, str(c), ha="center", va="bottom", fontweight="bold", fontsize=8.5)
    ax2.set_xticks(range(4))
    ax2.set_xticklabels(m_labels, fontsize=7.6)
    ax2.set_ylabel("Certified instances")
    ax2.set_ylim(0, 5.4)
    ax2.set_title("(b) Coverage Across All 4 Modes")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig3_atlas_summary.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    make_fig1()
    make_fig2()
    make_fig3()
    print("[PASS] Generated all 3 publication figures in paper/figures/.")
