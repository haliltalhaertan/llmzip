[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — all-N/K dominance for the corrected shared-gold sign model (model H)

No scientific priority, no universal security/losslessness claim, no new benchmark win.
Proofs, finite exhaustive witnesses, and conjectures are kept distinct below.
This toy does not model true benchmark dependence or centering; its sign-vs-cosine
direction may be very special.

## 1. Setup (model H, shared gold)

- Query `q = (1,1,1)`. One gold `R = (1, t·e1, t·e2)`, `N-1` nongolds
  `I_j = (-1, t·d_j1, t·d_j2)`, each nuisance sign iid ±1, `t > 0` fixed.
  The SAME drawn `R` is shared by all comparisons.
- `A = #{i : e_i = +1} ∈ {0,1,2}` (gold nuisance agreement with query);
  `B_j = #{i : d_ji = +1} ∈ {0,1,2}`; `D_j = B_j − A ∈ {−2,…,2}`.
- Sign distance from `q` = number of strictly negative entries
  (nonnegative-bit Hamming). Gold has `2−A` negatives (first entry `1 > 0`
  never counts); nongold has `3−B_j` (first entry `−1` always counts).
  Sign gap `G^sign_j = 1 + A − B_j = 1 − D_j`.
- Cosine: all docs share norm `√(1+2t²)`, so dot order = cosine order.
  `sum(R) = 1+2t(A−1)`, `sum(I_j) = −1+2t(B_j−1)`,
  gap `G^cos_j = 2 − 2t·D_j`.
- Outcome per nongold (gold view): `W` = gold strictly closer, `T` = tied,
  `L` = gold strictly farther.
- Tie law (uniform priorities, i.e. random permutation; `S` = #`L`, `Tc` = #`T`,
  integer `K ≥ 1`): `recall(S,Tc,K) = 0` if `S ≥ K`, else `min(1, (K−S)/(Tc+1))`.
  (Gold is uniform among its `Tc+1` tied slots.)

## 2. Theorem (one parametric result; scope = model H only)

For every `N ≥ 1`, every integer `K ≥ 1`, every `t > 0`, with expectations over
iid nuisance signs and uniform tie priorities:

(i) `0 < t < 1`: cosine weakly dominates sign, `E[recall_cos] ≥ E[recall_sign]`.
(ii) `t = 1`: identical outcomes on every realization ⇒ `E[recall_cos] = E[recall_sign]`.
(iii) `t > 1`: sign weakly dominates cosine, `E[recall_sign] ≥ E[recall_cos]`.
(iv) Exact classification (`D = D_j`):
  - Sign, all `t`: `W ⇔ D ≤ 0`, `T ⇔ D = 1`, `L ⇔ D = 2`.
  - Cosine: `W ⇔ 2−2tD > 0`, `T ⇔ = 0`, `L ⇔ < 0`. Hence
    `t < 1/2`: always `W`; `t = 1/2`: `W` except `T ⇔ D = 2`;
    `1/2 < t < 1`: `W ⇔ D ≤ 1` else `L`; `t = 1`: same table as sign;
    `t > 1`: `W ⇔ D ≤ 0` else `L` (never ties).
  - Corollary: per-realization cosine outcomes (hence expectations) are constant
    on each of `(0,1/2)`, `(1/2,1)`, `(1,∞)`, with jumps only at `t ∈ {1/2, 1}`.
    Cosine never ties for `t ∉ {1/2, 1}`.
(v) Strict vs degenerate: for `N ≥ 2` and `1 ≤ K < N`, the inequalities in
  (i) and (iii) are STRICT; for `K ≥ N` or `N = 1` both methods give recall `1`
  (for `K ≤ 0`, both give `0`). At `t = 1` equality holds for all `N, K`.

Proof. Fix the full nuisance realization `(A, all B_j)` and fix one draw of
tie priorities shared by both methods (coupling). Nongold `j` precedes gold iff
`o_j = L`, or `o_j = T` with better priority. From the tables: if `t < 1` each
`o^cos_j ≥ o^sign_j` (`W > T > L`), checked cell-by-cell — `D ≤ 0`: both `W`;
`D = 1`: cosine `W` vs sign `T`; `D = 2`: cosine `W` (`t<1/2`), `T` (`t=1/2`), `L` (`t>1/2`) vs sign `L`. Each precedence indicator
under cosine is thus `≤` that under sign, so total preceders under cosine `≤`
under sign, so gold top-`K` inclusion under cosine `≥` under sign — pointwise,
for every realization and every priority draw. Averaging gives (i); (iii) is
the mirror image (`D = 1`: sign `T` vs cosine `L`; `D ≤ 0`: both `W`;
`D = 2`: both `L`); (ii)/(iv) are read off the gap formulas. Strictness: with
`A = 1`, exactly `K` nongolds at `B = 2` (`D = 1`) and the rest at `B ≤ 1`
(`D ≤ 0`, `W` under both) — positive probability `2^{−2N}`-order event — the
`K` differing nongolds never precede under the better method but precede with
positive probability (`1/(K+1)` all-beat-gold) under the worse one; the rest
never precede under either. Hence strict expected gap when `1 ≤ K ≤ N−1`. ∎

## 3. Verification (own checker AND independent formulation + hand derivation)

`verify.py` (exact `Fraction` arithmetic throughout; exit `0`; ~50 PASS lines):

- (a) Own checker A: joint `(A, composition)` enumeration with the analytic tie law.
- (b) Differently formulated checker B: coordinator formula — condition on each of
  4 gold states, conditional multinomial, average. A and B agree on EVERY tested
  `(N,K,method,t)` (N6/N10/K3 knowns, full N2–N6 × K × 6 t-reps sweep).
- (c) Finite exhaustive witnesses: per-cell coupling table, all `(A,B) × 6` t-reps;
  same-priority permutation check, N=3, all 64 joint states × all 6 priority orders
  × K=1..3 × 6 t-reps; plus exact-equality pass at `t = 1`.
- (d) Hand derivation, N=2/K=1 (`recall = P(W)+P(T)/2`, `P(D≤0)=11/16`,
  `P(D=1)=1/4`, `P(D=2)=1/16`): sign `13/16`; cosine `t=1/4: 1`, `t=1/2: 31/32`,
  `t=3/4: 15/16`, `t=1: 13/16`, `t=10: 11/16`. All match both checkers.
- (e) FALSE-claim negative control: original unconditional-pairwise multinomial
  (marginals `P(W)=11/16, P(T)=1/4` treated as iid) gives N6K3 sign `33129/524288`,
  which mismatches the corrected `1763/2048` — the control is detected as false.
- (f) Corrected coordinator values confirmed by both checkers:
  N6K3 sign `1763/2048`, cosine(`t=1/2`) `4067/4096`, cosine(`t=10`) `1483/2048`;
  N10K3 sign `475849/655360`, cosine(`t=1/2`) `2535999/2621440`,
  cosine(`t=10`) `36089/65536`.
- (g) Sweep N2–N6, all K, t ∈ {1/4, 1/2, 3/4, 1, 3/2, 10}: ordering and
  strict/degenerate pattern hold everywhere (e.g. N3K1: sign `45/64`,
  `t025: 1`, `t05: 181/192`, `t075: 57/64`, `t1: 45/64`, `t>1: 35/64`).

Full numbers in `results.json` (`status: ALL-PASS`).

## 4. Failed attempts, limits, provenance

- Failed attempts (this session, both recovered): (1) `verify.py` first run →
  `SyntaxError`, header banner not commented (line 1); fixed by commenting it.
  (2) Exit-code probe using `${PIPESTATUS[0]}` → `/bin/sh: Bad substitution`
  (dash); reran portably, true exit `0`. No mathematical failure occurred.
- Prior sessions: two conditional-ranking attempts timed out on 180s model-stream
  idle; no partial proof is assumed or reused — the above is self-contained.
- Scope limits: result covers ONLY model H (uncentered binary nuisance, shared
  gold, uniform tie priorities). Not a benchmark explanation; centering,
  correlated/continuous nuisances, and other K-rules are outside scope.
- Commands/exit codes: `python3 verify.py` → exit `0` (FAILURES: none);
  results inspection → exit `0`. No network, installs, model APIs, or git writes.
- Inputs read (narrow): `sign_mechanism/{COORDINATOR_REVIEW.md,
  check_conditional_transport.py, conditional_transport_results.json}` (read-only).
  Original REPORT.md was not needed and not read. Outputs: `STATUS.md`,
  `REPORT.md`, `verify.py`, `results.json` in this workspace only.
