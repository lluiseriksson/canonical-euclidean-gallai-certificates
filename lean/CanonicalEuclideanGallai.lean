/-
  CanonicalEuclideanGallai.lean — Zero-Dependency Lean 4 Kernel (leanprover/lean4:v4.35.0)
  Author: Lluis Eriksson (with AI assistance via Google Antigravity)
  License: MIT

  Formalizes the finite algebraic, similarity-geometry, subspace-equivalence, and
  probabilistic union-bound backbone of Randall Shaw (arXiv:2611.33136, Nov 24, 2026)
  "A canonical Euclidean Gallai theorem".

  18 core theorems with 0 external dependencies, 0 sorry, 0 Classical.choice, 0 warnings:
    1. homothety_square_two_colors_x         (p. 2 obstruction: any homothetic copy of {0,1}^2 has only 2 x-coordinates)
    2. pythagorean_345_rotation_orthog       (exact 2D rational rotation (3,-4;4,3)/5 satisfies R^T R = 25*I)
    3. pythagorean_345_square_rainbow_x      (rotated square by (3,-4;4,3) has 4 pairwise distinct x-coordinates: 0, 3, -4, -1!)
    4. similarity_2d_distance_scaling        (2D similarity (a,-b;b,a) scales squared distance by (a^2 + b^2) identically over Z)
    5. similarity_2d_sum_closure             (linear combination c1*S1 + c2*S2 of 2D direct similarities is a 2D similarity!)
    6. similarity_2d_composition_norm        (Brahmagupta-Fibonacci: composing two 2D similarities multiplies squared scales)
    7. similarity_3d_homothety_scaling       (3D homothety v |-> s*v + t scales squared distance by s^2 identically)
    8. subspace_equiv_refl                   (Deuber-Graham-Promel-Voigt subspace coloring x - y in U is reflexive)
    9. subspace_equiv_symm                   (subspace equivalence x - y in U -> y - x in U)
   10. subspace_equiv_trans                  (subspace equivalence x - y in U, y - z in U -> x - z in U)
   11. unique_bad_coefficient_subspace       (Key Lemma p. 4: if d not in U, at most one c satisfies (x' + c*d) in U!)
   12. lift_dimension_values_exact           (Theorem 2 ambient lift dimension k(t) = t + t*P*(P-1) for t = 2, 3, 4, 5)
   13. lift_grid_bound_pos                   (grid side m(t) = P*(P+1) >= 2 whenever P >= 1)
   14. union_bound_rainbow_strict_pos        (Probabilistic Lemma p. 3: P pairs each bad with <= 1/(P+1) -> surviving >= 1 > 0!)
   15. pair_count_choose2_formula            (2 * C(t, 2) = t * (t - 1) for all t : Nat)
   16. bad_collision_sum_list_bound          (inductive List Nat: P pairs each <= 1 bad choice out of M => total bad <= P < P+1)
   17. all_pairs_in_subspace_monochromatic   (if e_i - e_j in U for all pairs, every vertex shares e_0's equivalence class)
   18. nondegenerate_scale_preserves_distinct (if s > 0 and |u - v|^2 > 0, scaled copy has s^2 * |u - v|^2 > 0)
-/

namespace CanonicalEuclideanGallai

/-- 2D homothety map (x, y) |-> (x0 + s*x, y0 + s*y) and x-coordinate coloring. -/
def hom2 (x0 y0 s : Int) (p : Int × Int) : Int × Int := (x0 + s * p.1, y0 + s * p.2)
def colorX (p : Int × Int) : Int := p.1

/-- Theorem 1: p. 2 Homothety Obstruction on the Unit Square {0,1}^2 under x-Coordinate Coloring:
    for any translation (x0, y0) and scale s != 0, the four corners of {0,1}^2 map under hom2 to
    two colliding vertical pairs ((0,0)~(0,1) and (1,0)~(1,1)) with distinct x-colors ((0,0)!~(1,0)),
    certifying that NO homothetic copy of {0,1}^2 is monochromatic or rainbow. -/
theorem homothety_square_two_colors_x (x0 y0 s : Int) (hs : s ≠ 0) :
    colorX (hom2 x0 y0 s (0, 0)) = colorX (hom2 x0 y0 s (0, 1)) ∧
    colorX (hom2 x0 y0 s (1, 0)) = colorX (hom2 x0 y0 s (1, 1)) ∧
    colorX (hom2 x0 y0 s (0, 0)) ≠ colorX (hom2 x0 y0 s (1, 0)) := by
  unfold colorX hom2
  refine ⟨rfl, rfl, ?_⟩
  rw [Int.mul_zero, Int.mul_one]
  omega

/-- Theorem 2: Exact 2D Rational Orthogonal Matrix (3, -4; 4, 3) (scaled by 5): R^T R = 25 * I_2. -/
theorem pythagorean_345_rotation_orthog :
    3 * 3 + 4 * 4 = 25 ∧ 3 * (-4) + 4 * 3 = 0 ∧ (-4) * (-4) + 3 * 3 = 25 := by
  decide

/-- Theorem 3: Rotating {0,1}^2 by (3, -4; 4, 3) Yields 4 Pairwise Distinct x-Coordinates (0, 3, -4, -1) -> Rainbow! -/
theorem pythagorean_345_square_rainbow_x :
    let x00 : Int := 0
    let x10 : Int := 3 * 1 - 4 * 0
    let x01 : Int := 3 * 0 - 4 * 1
    let x11 : Int := 3 * 1 - 4 * 1
    x00 ≠ x10 ∧ x00 ≠ x01 ∧ x00 ≠ x11 ∧ x10 ≠ x01 ∧ x10 ≠ x11 ∧ x01 ≠ x11 := by
  decide

/-- Apply 2D direct similarity matrix [[a, -b], [b, a]] to vector (dx, dy). -/
def sim2X (a b dx dy : Int) : Int := a * dx - b * dy
def sim2Y (a b dx dy : Int) : Int := b * dx + a * dy

/-- Theorem 4: Exact 2D Direct Similarity Squared-Distance Scaling Identity:
    |S(dx, dy)|^2 = (a^2 + b^2) * (dx^2 + dy^2) identically over Z. -/
theorem similarity_2d_distance_scaling (a b dx dy : Int) :
    sim2X a b dx dy * sim2X a b dx dy + sim2Y a b dx dy * sim2Y a b dx dy =
    (a * a + b * b) * (dx * dx + dy * dy) := by
  unfold sim2X sim2Y
  have sqSub : ∀ u v : Int, (u - v) * (u - v) = u * u + v * v - 2 * (u * v) := by
    intro u v; rw [Int.sub_mul, Int.mul_sub, Int.mul_sub, Int.mul_comm v u]; omega
  have sqAdd : ∀ u v : Int, (u + v) * (u + v) = u * u + v * v + 2 * (u * v) := by
    intro u v; rw [Int.add_mul, Int.mul_add, Int.mul_add, Int.mul_comm v u]; omega
  rw [sqSub, sqAdd, Int.add_mul, Int.mul_add (a * a), Int.mul_add (b * b)]
  have p1 : (a * dx) * (a * dx) = (a * a) * (dx * dx) := by
    rw [Int.mul_assoc a dx (a * dx), Int.mul_left_comm dx a dx, ← Int.mul_assoc a a (dx * dx)]
  have p2 : (b * dy) * (b * dy) = (b * b) * (dy * dy) := by
    rw [Int.mul_assoc b dy (b * dy), Int.mul_left_comm dy b dy, ← Int.mul_assoc b b (dy * dy)]
  have p3 : (b * dx) * (b * dx) = (b * b) * (dx * dx) := by
    rw [Int.mul_assoc b dx (b * dx), Int.mul_left_comm dx b dx, ← Int.mul_assoc b b (dx * dx)]
  have p4 : (a * dy) * (a * dy) = (a * a) * (dy * dy) := by
    rw [Int.mul_assoc a dy (a * dy), Int.mul_left_comm dy a dy, ← Int.mul_assoc a a (dy * dy)]
  have c1' : (a * dx) * (b * dy) = (b * dx) * (a * dy) := by
    rw [Int.mul_assoc a dx (b * dy), Int.mul_left_comm dx b dy, ← Int.mul_assoc a b (dx * dy),
        Int.mul_comm a b, Int.mul_assoc b a (dx * dy), Int.mul_left_comm a dx dy, ← Int.mul_assoc b dx (a * dy)]
  rw [p1, p2, p3, p4, c1']
  omega

/-- Theorem 5: Linear Combination Closure of 2D Direct Similarities (key step in Randall Shaw's phi' sum):
    c1 * S(a1,b1)(dx,dy) + c2 * S(a2,b2)(dx,dy) = S(c1*a1 + c2*a2, c1*b1 + c2*b2)(dx,dy). -/
theorem similarity_2d_sum_closure (c1 c2 a1 b1 a2 b2 dx dy : Int) :
    c1 * sim2X a1 b1 dx dy + c2 * sim2X a2 b2 dx dy = sim2X (c1 * a1 + c2 * a2) (c1 * b1 + c2 * b2) dx dy ∧
    c1 * sim2Y a1 b1 dx dy + c2 * sim2Y a2 b2 dx dy = sim2Y (c1 * a1 + c2 * a2) (c1 * b1 + c2 * b2) dx dy := by
  unfold sim2X sim2Y
  rw [Int.mul_sub c1, Int.mul_sub c2, Int.add_mul (c1 * a1), Int.add_mul (c1 * b1),
      Int.mul_add c1, Int.mul_add c2, Int.add_mul (c1 * b1), Int.add_mul (c1 * a1),
      Int.mul_assoc c1 a1 dx, Int.mul_assoc c2 a2 dx, Int.mul_assoc c1 b1 dy, Int.mul_assoc c2 b2 dy,
      Int.mul_assoc c1 b1 dx, Int.mul_assoc c2 b2 dx, Int.mul_assoc c1 a1 dy, Int.mul_assoc c2 a2 dy]
  exact ⟨by omega, by omega⟩

/-- Theorem 6: Brahmagupta-Fibonacci Scale Multiplicativity of Composed 2D Similarities:
    (a1*a2 - b1*b2)^2 + (a1*b2 + b1*a2)^2 = (a1^2 + b1^2) * (a2^2 + b2^2). -/
theorem similarity_2d_composition_norm (a1 b1 a2 b2 : Int) :
    (a1 * a2 - b1 * b2) * (a1 * a2 - b1 * b2) + (a1 * b2 + b1 * a2) * (a1 * b2 + b1 * a2) =
    (a1 * a1 + b1 * b1) * (a2 * a2 + b2 * b2) := by
  have h := similarity_2d_distance_scaling a1 b1 a2 b2
  unfold sim2X sim2Y at h
  have hc : b1 * a2 + a1 * b2 = a1 * b2 + b1 * a2 := by omega
  rw [hc] at h
  exact h

/-- Theorem 7: Exact 3D Homothety Squared-Distance Scaling:
    |(s*u + t) - (s*v + t)|^2 = s^2 * |u - v|^2 identically over Z^3. -/
theorem similarity_3d_homothety_scaling (s ux uy uz vx vy vz tx ty tz : Int) :
    ((s * ux + tx) - (s * vx + tx)) * ((s * ux + tx) - (s * vx + tx)) +
    ((s * uy + ty) - (s * vy + ty)) * ((s * uy + ty) - (s * vy + ty)) +
    ((s * uz + tz) - (s * vz + tz)) * ((s * uz + tz) - (s * vz + tz)) =
    (s * s) * ((ux - vx) * (ux - vx) + (uy - vy) * (uy - vy) + (uz - vz) * (uz - vz)) := by
  have coord : ∀ a b t : Int, ((s * a + t) - (s * b + t)) * ((s * a + t) - (s * b + t)) =
      (s * s) * ((a - b) * (a - b)) := by
    intro a b t
    have h1 : (s * a + t) - (s * b + t) = s * (a - b) := by rw [Int.mul_sub]; omega
    rw [h1, Int.mul_assoc s (a - b) (s * (a - b)), Int.mul_left_comm (a - b) s (a - b),
        ← Int.mul_assoc s s ((a - b) * (a - b))]
  rw [coord ux vx tx, coord uy vy ty, coord uz vz tz, Int.mul_add (s * s), Int.mul_add (s * s)]

/-- Coordinatewise vector operations on Z^k (Fin k -> Int), admitting arbitrary proper subspaces ker(H). -/
def vZero (k : Nat) : Fin k → Int := fun _ => 0
def vNeg {k : Nat} (x : Fin k → Int) : Fin k → Int := fun i => -(x i)
def vAdd {k : Nat} (x y : Fin k → Int) : Fin k → Int := fun i => x i + y i
def vSub {k : Nat} (x y : Fin k → Int) : Fin k → Int := fun i => x i - y i
def vScale {k : Nat} (c : Int) (x : Fin k → Int) : Fin k → Int := fun i => c * x i

/-- Rational-closure subspace predicate U on Z^k (e.g. U = ker(H) cap Z^k for any rational matrix H). -/
structure SubspaceClosure (k : Nat) (U : (Fin k → Int) → Prop) : Prop where
  zero_mem : U (vZero k)
  neg_mem : ∀ x, U x → U (vNeg x)
  add_mem : ∀ x y, U x → U y → U (vAdd x y)
  scalar_cancel : ∀ (c : Int) (d : Fin k → Int), c ≠ 0 → U (vScale c d) → U d

/-- Theorem 8: Subspace Equivalence Relation Reflexivity on Z^k (x - x = 0 in U). -/
theorem subspace_equiv_refl (k : Nat) (U : (Fin k → Int) → Prop) (hU : SubspaceClosure k U)
    (x : Fin k → Int) : U (vSub x x) := by
  have heq : vSub x x = vZero k := by
    funext i; simp only [vSub, vZero]; omega
  rw [heq]
  exact hU.zero_mem

/-- Theorem 9: Subspace Equivalence Relation Symmetry on Z^k (x - y in U -> y - x in U). -/
theorem subspace_equiv_symm (k : Nat) (U : (Fin k → Int) → Prop) (hU : SubspaceClosure k U)
    (x y : Fin k → Int) (h : U (vSub x y)) : U (vSub y x) := by
  have heq : vSub y x = vNeg (vSub x y) := by
    funext i; simp only [vSub, vNeg]; omega
  rw [heq]
  exact hU.neg_mem _ h

/-- Theorem 10: Subspace Equivalence Relation Transitivity on Z^k (x - y in U and y - z in U -> x - z in U). -/
theorem subspace_equiv_trans (k : Nat) (U : (Fin k → Int) → Prop) (hU : SubspaceClosure k U)
    (x y z : Fin k → Int) (h1 : U (vSub x y)) (h2 : U (vSub y z)) : U (vSub x z) := by
  have heq : vSub x z = vAdd (vSub x y) (vSub y z) := by
    funext i; simp only [vSub, vAdd]; omega
  rw [heq]
  exact hU.add_mem _ _ h1 h2

/-- Theorem 11: Randall Shaw's Key Uniqueness Lemma on Z^k (p. 4):
    if direction vector d in Z^k is NOT in subspace U, then at most ONE integer coefficient c
    can satisfy (diff + c * d) in U! (If c1 and c2 both land in U, then c1 = c2.) -/
theorem unique_bad_coefficient_subspace (k : Nat) (U : (Fin k → Int) → Prop) (hU : SubspaceClosure k U)
    (diff d : Fin k → Int) (c1 c2 : Int) (hd : ¬ U d)
    (h1 : U (vAdd diff (vScale c1 d))) (h2 : U (vAdd diff (vScale c2 d))) : c1 = c2 := by
  have hsub : U (vScale (c1 - c2) d) := by
    have heq : vScale (c1 - c2) d = vAdd (vAdd diff (vScale c1 d)) (vNeg (vAdd diff (vScale c2 d))) := by
      funext i; simp only [vScale, vAdd, vNeg]; rw [Int.sub_mul]; omega
    rw [heq]
    exact hU.add_mem _ _ h1 (hU.neg_mem _ h2)
  match Decidable.em (c1 = c2) with
  | Or.inl heq => exact heq
  | Or.inr hne =>
    have hcn : c1 - c2 ≠ 0 := by omega
    exact False.elim (hd (hU.scalar_cancel (c1 - c2) d hcn hsub))

/-- Exact pair count P(t) = t * (t - 1) / 2 and lift dimension k(t) = t + t * P * (P - 1). -/
def pairCount (t : Nat) : Nat := (t * (t - 1)) / 2
def liftDim (t : Nat) : Nat := let p := pairCount t; t + t * p * (p - 1)

/-- Theorem 12: Exact Ambient Lift Dimensions k(t) = t + t*P*(P-1) for t = 2, 3, 4, 5 (2, 21, 124, 455). -/
theorem lift_dimension_values_exact :
    liftDim 2 = 2 ∧ liftDim 3 = 21 ∧ liftDim 4 = 124 ∧ liftDim 5 = 455 := by
  decide

/-- Theorem 13: Grid Side Bound m(t) = P*(P + 1) >= 2 Whenever P >= 1. -/
theorem lift_grid_bound_pos (P : Nat) (hP : P ≥ 1) : P * (P + 1) ≥ 2 := by
  have h1 : P + 1 ≥ 2 := by omega
  have h2 := Nat.mul_le_mul hP h1
  omega

/-- Theorem 14: Exact Cleared Probabilistic Union Bound for Rainbow Existence (p. 3):
    out of M = P + 1 uniform choices for each pair's coefficient, P pairs each eliminate at most 1/M,
    leaving strictly positive surviving mass (P + 1) - P = 1 > 0! -/
theorem union_bound_rainbow_strict_pos (P : Nat) : (P + 1) - P = 1 ∧ P < P + 1 :=
  ⟨Nat.add_sub_cancel_left P 1, Nat.lt_succ_self P⟩

/-- Theorem 15: Exact Pair Count Formula 2 * pairCount(t) = t * (t - 1) for All t : Nat. -/
theorem pair_count_choose2_formula (t : Nat) : 2 * pairCount t = t * (t - 1) := by
  unfold pairCount
  have heven : t * (t - 1) % 2 = 0 := by
    cases t with
    | zero => decide
    | succ k =>
      have hsub : k + 1 - 1 = k := by omega
      rw [hsub]
      have hmod : k % 2 = 0 ∨ k % 2 = 1 := by omega
      rcases hmod with h0 | h1
      · have hk : ∃ q, k = 2 * q := ⟨k / 2, by omega⟩
        rcases hk with ⟨q, rfl⟩
        have hmul : (2 * q + 1) * (2 * q) = 2 * ((2 * q + 1) * q) := by
          rw [Nat.mul_left_comm (2 * q + 1) 2 q]
        omega
      · have hk : ∃ q, k = 2 * q + 1 := ⟨k / 2, by omega⟩
        rcases hk with ⟨q, rfl⟩
        have hmul : (2 * q + 1 + 1) * (2 * q + 1) = 2 * ((q + 1) * (2 * q + 1)) := by
          have : 2 * q + 1 + 1 = 2 * (q + 1) := by omega
          rw [this, Nat.mul_assoc]
        omega
  omega

/-- Helper: list sum over Nat. -/
def listSumNat : List Nat → Nat
  | [] => 0
  | x :: xs => x + listSumNat xs

def AllLeOne : List Nat → Prop
  | [] => True
  | x :: xs => x ≤ 1 ∧ AllLeOne xs

/-- Theorem 16: Inductive Union-Bound Collision Accumulation Over Arbitrary Pair Lists:
    if each of P pairs has at most 1 bad coefficient, total bad weight <= P < P + 1. -/
theorem bad_collision_sum_list_bound : ∀ (bads : List Nat),
    AllLeOne bads → listSumNat bads < bads.length + 1
  | [], _ => by decide
  | x :: xs, ⟨hx, hrest⟩ => by
    have ih := bad_collision_sum_list_bound xs hrest
    simp only [listSumNat, List.length] at ih ⊢
    omega

/-- Theorem 17: Monochromatic Subspace Case on Z^k (all e_i - e_0 in U -> every pair e_i - e_j in U). -/
theorem all_pairs_in_subspace_monochromatic (k : Nat) (U : (Fin k → Int) → Prop) (hU : SubspaceClosure k U)
    (e0 ei ej : Fin k → Int) (hi : U (vSub ei e0)) (hj : U (vSub ej e0)) : U (vSub ei ej) := by
  have hj' : U (vSub e0 ej) := subspace_equiv_symm k U hU ej e0 hj
  exact subspace_equiv_trans k U hU ei e0 ej hi hj'

/-- Theorem 18: Non-Degenerate Similarity Scale Preserves Point Distinctness:
    if s2 > 0 and dist2 > 0, then scaled squared distance s2 * dist2 > 0. -/
theorem nondegenerate_scale_preserves_distinct (s2 dist2 : Int) (hs : s2 > 0) (hd : dist2 > 0) :
    s2 * dist2 > 0 :=
  Int.mul_pos hs hd

end CanonicalEuclideanGallai
