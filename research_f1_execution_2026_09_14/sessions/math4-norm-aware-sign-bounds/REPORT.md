# REPORT.md — Normalization-aware sign-code uncertainty and ranking certificate

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 0. Result in one paragraph

Sign bits alone cannot guarantee cosine ordering, and the exact reason is
quantified: for a fixed full-precision unit query `q` and a sign pattern `s`,
the sharp range of compatible cosines is `‖P_K q‖`-type on each side
(Theorem 1), with sup/inf possibly unattained because negative signs demand
strictly negative coordinates. One extra scalar per document — the codebook
angle `ρ = x·c(s)` stored at stated bit precision with conservative rounding —
tightens the deterministic bound to the elementary spherical cap
`[cos(β+α), cos(|β−α|)]` (Theorem 2, which is Cauchy–Schwarz/angle-addition,
**not** a new inequality). With 8-bit `ρ`, an explicit 6-document case turns a
fully vacuous sign-only bound into a certified top-3 decision, and an explicit
failure case stays vacuous. When the query is also sign-coded, a single joint
triangle-inequality chain (no independent-extrema fiction) gives the valid
two-sided certificate. `verify.py`: **272/272 checks pass** via two
independent routes (exact `Fractions` algebra vs float trig/numpy/Gram).

## 1. Scope, budget, sources — read-only discipline

- ~20-minute first pass; writes ONLY in
  `/home/mdp/muse-work/math4-norm-aware-sign-bounds`
  (`STATUS.md`, `verify.py`, `results.json`, this file). No benchmark sweeps,
  no trained arms, no Task4F1 measurement, no installs/network/model APIs,
  no Git push/main edits.
- Mandatory context (read-only): `theory_benchmark_test_v1/audit_mapping/`
  `{COORDINATOR_REVIEW.md, REPORT.md}`,
  `theory_benchmark_test_v1/audit_real_geometry/`
  `{COORDINATOR_REVIEW.md, COORDINATOR_LME_WITNESS.json}`,
  `math_discovery_2026_09_13/round3/joint_gold_bounds/COORDINATOR_REVIEW.md`.
- Governing corrections (applied, not re-argued): LME15745da0 t4 gold dot
  `1.02997959496 <` rival `1.04672119662` yet gold cosine `.54573812 >`
  `.53902568` — numerator alone does NOT explain the flip, norms are
  essential; t-vs-t² alone does not explain opposite Model-H dominance;
  query magnitude is NOT a proved nuisance label; +12pp LoCoMo retracted
  (same-cache MC diff +6.82838pp only); no literature novelty claim.

## 2. Definitions (exact; everything else refers to these)

- Dimension `d ≥ 1`. Document `v ∈ ℝ^d ∖ {0}`, unit `x = v/‖v‖ ∈ S^{d−1}`.
  Cosine is scale-invariant, so raw magnitudes never enter: **no
  equal-magnitude assumption is used anywhere** (only directions matter).
- Zero convention `sign(0) = +1`: pattern `s ∈ {±1\}^d`,
  `P = {i : s_i = +1}`, `N = {i : s_i = −1}`.
  Feasible set `F(s) = {x ∈ S^{d−1} : x_P ≥ 0, x_N < 0}` (strict on `N`).
  Closure `F̄(s) = {x ∈ S^{d−1} : s_i x_i ≥ 0 ∀i}`, compact.
  `F(s)` is dense in `F̄(s)` (Lemma, §4); if `N = ∅`, `F(s) = F̄(s)`.
- Fixed full-precision unit query `q`. Score `t(x) = q·x` (exact cosine).
- Hamming/agreement score `A = #{i : sign(x_i) = sign(q_i)}` under the same
  zero convention. Code vectors `ĉ(x) = s(x)/√d`, `q̂ = s(q)/√d` satisfy the
  **exact** identity `q̂·ĉ = (2A−d)/d` (checked `F.hamming-identity`).
- Ties: ranking certificates (§6) assume ADVERSARIAL tie-breaking
  (a rival that can tie can rank above), so guarantees are sound, not lucky.
- Status words: THEOREM (proved), WITNESS (finite exact instance),
  CONJECTURE (unproved), ILLUSTRATION (real data, explanatory only).

## 3. THEOREM 1 — sharp sign-only cosine extrema (open-boundary correct)

Let `K(s) = {y : s_i y_i ≥ 0}` (closed convex cone), `P_K` its projection
(coordinate-wise positive part twisted by `s`).

- Non-degenerate case `P_K q ≠ 0`:
  `sup_{F(s)} q·x = ‖P_K q‖ = ‖(q_i · 1[s_i q_i > 0])‖₂`.
- Degenerate case `P_K q = 0` (query points entirely out of the orthant):
  `sup_{F(s)} q·x = max_i s_i q_i ≤ 0` (extreme-ray value, proof below).
- `inf` mirrors with `q → −q`: `inf = −‖P_K(−q)‖` if nonzero, else
  `min_i s_i q_i`.
- In all cases the value over `F(s)` equals the max/min over compact `F̄(s)`.

Attainment over the OPEN set (checked exactly per instance in `verify.py`):

- Norm case sup: attained iff `q_i < 0 ∀i ∈ N`
  (else the closure maximizer `P_K q/‖P_K q‖` has a zero `N`-coordinate).
  Norm case inf: attained iff `q_i > 0 ∀i ∈ N`.
- Axis case: attained iff some optimizing axis `s_j e_j` has `N ⊆ {j}`.

*Proof.* For `x ∈ F̄(s)`, disagree terms satisfy `q_i x_i ≤ 0`, so
`q·x ≤ Σ_{agree} q_i x_i ≤ ‖P_K q‖` by Cauchy–Schwarz; equality at
`P_K q/‖P_K q‖ ∈ F̄(s)` (Moreau: the polar residual is orthogonal to it).
If `P_K q = 0` then `−q ∈ K(s)`; writing `w̃_j = −q_j s_j ≥ 0`,
`z_j = x_j s_j ≥ 0`, `min Σ w̃_j z_j` over `z ≥ 0, ‖z‖ = 1` is `min_j w̃_j`
(take `z = e_j`; any `z` gives `≥ min w̃ · Σz ≥ min w̃`), attained at an
axis. Density lemma: `y ∈ F̄(s) ∖ F(s)` is approached by
`normalize(y − ε Σ_{j∈N, y_j=0} e_j)`, `ε ↓ 0`, which keeps `P`-signs and
makes all `N`-coords negative. ∎

Small exact table (`q = (3/5, 4/5)`, `verify.py` §B–C):

| `s`      | feasible cosine range        | ends attained? |
|----------|------------------------------|----------------|
| `(+,+)`  | `(3/5, 1]`                   | sup yes (`x=q`), inf no |
| `(+,-)`  | `[-4/5, 3/5)`                | inf yes (`(0,-1)`), sup no |
| `(-,+)`  | `[-3/5, 4/5)`                | neither |
| `(-,-)`  | `[-1, -3/5)`                 | sup yes, inf no |

## 4. WITNESS — sign-only information is insufficient (three saved instances)

With `q = (3/5,4/5)` (unit, rational):

1. **Same-pattern vacuity.** Any two documents sharing a pattern have
   IDENTICAL feasible intervals — signs alone order nothing (§E: six docs,
   one pattern, one shared `(0.5, 1]` interval).
2. **Rank flip against agreement count.** `x_A = (1,0)` (pattern `(+,+)`,
   2 agreements) scores exactly `3/5`; `x_E = (−0.01,1)/√1.0001`
   (pattern `(−,+)`, 1 agreement, verified in `F(s)`) scores `0.793960303…`.
   Fewer agreements, strictly higher cosine (`C.flip`, `G.F2`, reason
   RANK_FLIP). Hamming order does not imply cosine order.
3. **Exact cross-pattern tie.** `x ≈ (0.9914, 0.1309)` in `F((+,+))` and
   `x ≈ (−0.1513, 0.9885)` in `F((−,+))` both score `0.7 ± 1e−9`
   (`C.tie-A`, `C.tie-E`): equal relevance, different Hamming scores.
4. **Adjacent-pattern strict separation (saved non-flip).** Every `(+,+)`
   doc strictly beats every `(+,-)` doc (`sup = inf = 3/5`, both
   unattained) — insufficiency is generic, not universal.

## 5. THEOREM 2 — one scalar tightens the bound (known inequality, new assembly)

Per-document centroid `c(s) = ŝ/√d`, `ŝ_i = s_i`. Scalar payload
`ρ = x·c(s)` (equivalently angle `α = arccos ρ`, or residual
`‖x − c‖² = 2 − 2ρ` — same information). Let `u = q·c`, `β = arccos u`.
Then, with exact clamping,

`q·x ∈ [uρ − √((1−u²)(1−ρ²)), uρ + √((1−u²)(1−ρ²))] = [cos(β+α), cos(|β−α|)]`.

*Proof.* Decompose along `c`: `q·x = uρ + q_⊥·x_⊥`,
`|q_⊥·x_⊥| ≤ ‖q_⊥‖‖x_⊥‖` (Cauchy–Schwarz in `c^⊥`). Angle form is
cosine-addition. ∎ — This recovers the standard spherical-cap bound; **no
new inequality is claimed**. The content is the certificate assembly below.

Payload discipline (NOT a free codec): `ρ ∈ [−1,1]` stored in `k = 8` bits
uniformly (`m = round((ρ+1)·255/2)`); decode interval widens by half-LSB
`1/255` plus `1e−12` fp slack; `[L,U]` takes min/max over the interval
INCLUDING interior stationary points `ρ* = ∓u` of the endpoint maps
(closed-form vertex, `cert_interval`). Total per-doc cost is `d` sign bits
`+ k` stated bits; no byte-storage or benchmark-codec claim is made.

## 6. Pairwise / top-K margin certificate

Per-doc intervals `[L_i, U_i]` (independent across docs — each doc ranges
over its own feasible set; the shared query is fixed). Pair `i ≻ j` is
CERTIFIED iff `L_i > U_j`. Worst-case rank
`rank(i) = 1 + #{j ≠ i : U_j ≥ L_i}` (adversarial ties); `i` is certified
top-`K` iff `rank(i) ≤ K`. Certificates compose across docs without any
joint-attainability assumption (only per-doc validity is needed).

Certified top-3 instance (`d = 4`, `q = c = (½,½,½,½)`, all `s = (+,+,+,+)`,
8-bit `ρ`; `verify.py` §E). True scores
`[1.00000, 0.99751, 0.99015, 0.50000, 0.70711, 0.86603]`; certified
`L_{1..3} = [0.9961, 0.9961, 0.9882]`, `U_{4..6} = [0.5020, 0.7137, 0.8706]`:
every `L_i > ` every `U_j`, worst-ranks `[3,3,3,6,5,4]` — docs 1–3 certified
top-3 while sign-only gives all six the identical `(0.5,1]` (vacuous).

Failure instance (saved): `u = −1/(5√2)`, `ρ = 1/√2` gives
`[−0.8, 0.6]`, width `1.4`; quantized cert `[-0.8010, 0.6014]` — the scalar
adds nothing there. Practical bounds are often loose; that quantified
negative stands.

## 7. Query also sign-coded (frozen native protocol)

Only `q̂`, doc codes `c_j`, doc payload `ρ_j` (or `α_j`), and query-time
`θ_q = ∠(q,q̂)` (computable at query time — `q` is known then) are assumed.
Per doc, one joint triangle chain on the sphere (shared `θ_q` is fine —
validity is per-doc, then §6 composes):

`q·x_j ∈ [cos(min(π, θ_q + γ_j + α_j)), cos(max(0, γ_j − θ_q − α_j))]`,
`γ_j = ∠(q̂, c_j)` from codes only.

Explicit instance (`F.joint-valid`): `q = (1,2,2)/3`, `x = (2,2,−1)/3`,
`t = 4/9 ≈ 0.4444 ∈ [−0.209877, 0.777778]`
(`θ_q = α = 15.79°`, `γ = 70.53°`). Independent per-doc extrema are never
combined as if jointly attainable — the single chain above is the bound.

Encoding/query split: `s, ρ` need only the doc vector at ingest (no gold
labels); `u = q·c`, `β`, `θ_q` need only the query at query time; `γ`
needs only the two codes. Doc vector norms are irrelevant throughout
(scale invariance); "magnitude concentration" across coordinates matters
only through direction — already captured by `ρ`.

## 8. Audit trail: independent routes, seeded falses, counterexamples

- Route 1: exact `Fractions` (squared-norm identities, strict `<0`
  membership, attainment predicates) — no trig.
- Route 2: numpy circle/sphere grids (fences + reachability), trig
  angle-addition, Gram-determinant quadratic — agrees with route 1 to
  `<1e-12` on endpoints (`D.agree.*`); 24 d2 cells × fences/reach/exactness
  + 24 d3 cells + constructive `x(ε)` approach wherever sup is unattained.
- Seeded broken variants, each caught FOR the named reason (`G.*`):
  F1 closed-set fallacy → OPEN_BOUNDARY (`y* = (1,0)` attains closure sup
  `3/5` but `x_2 = 0` violates `s_2 = −1`); F2 Hamming-orders-cosine →
  RANK_FLIP (`0.793960 > 0.6`); F3 exact-8-bit-payload → ROUNDING.
  Negative control (`exec-7`): naive closed membership says feasible
  (`True`), exact says infeasible (`False`) — the checker discriminates, so
  green cannot come from the same mistake.
- Saved counterexamples/limitations: §4 witnesses, §6 failure instance,
  degenerate `P_K q = 0` axis case, adversarial-tie rank convention.
  No source file was modified (read-only discipline); no silent rewrites.

## 9. Real-data ILLUSTRATION (not validation, no new measurement)

Read-only transcription of the coordinator-saved witness
(`COORDINATOR_LME_WITNESS.json`, t4 row; `H.numerator-insufficient`):
gold dot `1.02997959496 <` rival `1.04672119662` while gold cosine
`.54573812 >` rival `.53902568`. This is exactly the normalization effect
Theorem 1 is built around: dot/unnormalized-score order need not survive
normalization, and sign/Hamming information (which sees neither dot
magnitudes nor norms) cannot adjudicate such flips. One illustration only;
no population claim.

## 10. Reproduction: exact commands and observed results

1. `cd /home/mdp/muse-work/math4-norm-aware-sign-bounds && PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/mdp/muse-work/ml-python -B verify.py` → `272/272 checks passed`, exit 0, writes `results.json` (observed `exec-6`; earlier `exec-5` run caught 3 worker-side errors — two checker sign/bracket bugs and one wrong flip direction — all fixed and re-greened honestly, §8).
2. Negative control (`exec-7`, `/tmp`-equivalent inline probe, not a
   deliverable): naive-vs-exact membership `True` vs `False`; broken
   Hamming claim evaluates `False`. Pass, exit 0.
3. `results.json` key numbers: sup/inf `(+,+)=(1.0, 0.6)`,
   `(+,-)=(0.6, −0.8)`; flip `0.7939603029772521` vs `0.6`; LME t4 row as §9.

Conjecture (explicitly UNPROVED): an 8-bit `ρ` payload certifies a
nontrivial top-K margin on a non-negligible share of real queries. Offered
as conjecture only — no benchmark coverage was measured.
