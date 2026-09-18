# Sharp full-distance-profile-only bounds after coordinate deletion

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Second-pass extension of first-pass T3/T4 (ranking_bounds REPORT.md), read under
its COORDINATOR_REVIEW.md. Worker reports treated as fallible; coordinator notes
governed disagreements. All results below are synthetic exact mathematics (no
benchmark data touched, no fits); finite enumerations are falsification/tightness
evidence, NEVER universal proofs (proofs stand on their own).

## 0. Setup (quantifiers, dimensions, assumptions)

- Dimensions: full width b (frozen programme value 96; theorems parametric; finite
  checks at b <= 4). FIXED retained subset S, |S| = s, removed r = b - s.
  n documents; K = 3 throughout (theorems state general K; checks run K = 3, plus a
  K = 1 spot scope). Duplicate documents ALLOWED (needed for Theorem R; mirrors the
  near-duplicate clusters of MATH-1).
- Query encoding/scoring: query Q in {0,1}^b arbitrary; full distances
  d_i = Hamming(D_i, Q); retained distances e_i = Hamming on S; rank by e_i,
  smaller is better. WLOG Q = 0 (global XOR with Q preserves all Hamming
  distances and fixes S as a set).
- Tie law (DEFINITION, reused MATH-1 identity): uniform random permutation over
  each tied block (frozen continuous priorities); per-gold expected fractional
  inclusion f(S,T) = 0 if S >= K, 1 if S + T <= K, (K-S)/T otherwise, with
  S = #{i != g : e_i < e_g}, T = 1 + #{i != g : e_i = e_g}.
- Distribution assumptions: NONE (worst case over codebooks compatible with the
  observed full profile; the only randomness is the tie-break).
- Cost ledger: no Pass-1 compute is repeated; this pass enumerates 4,432
  (full-profile, retained-profile) pairs for realizability, 6,492 per-gold
  (K=3) corner-vs-brute-force cells, 380 (K=1) spot cells, 36 monotonicity cells,
  plus 3 exact witness codebooks; all arithmetic exact integers/Fractions.

## 1. Counterexample-first search (done before proving)

Before proving realizability we searched for the most plausible obstructions:
(a) shared-Q coupling across docs; (b) shared-S coupling across docs;
(c) distinctness (no-duplicate) constraints. (a) and (b) dissolve: after XOR-ing
Q to 0 and permuting S to the front, each document is an INDEPENDENT choice of
e_i ones on S and f_i = d_i - e_i ones on R. (c) is real but out of scope:
with duplicates FORBIDDEN, joint realizability can fail (pigeonhole: e.g. more
docs pinned to one retained vector than its multiplicity allows); the frozen
protocol allows duplicates, so we keep them allowed and prove realizability
there. Edge cases s = 0 / r = 0 checked explicitly (Section 4).

## 2. PROVEN LEMMAS

> **Lemma I (intervals are necessary).** For every doc, e_i in
> [L_i, U_i] := [max(0, d_i - r), min(s, d_i)]. *Proof.* e_i <= s, e_i <= d_i,
> d_i - e_i = f_i <= r. Direct.

> **Theorem R (joint realizability; the ONE substantive extension).**
> Fix b, s, r = b - s, n, and ANY full profile d in {0..b}^n. Then EVERY choice
> e with e_i in [L_i, U_i] for all i is jointly realized by one common binary
> query and one fixed subset S (duplicates allowed).
> *Proof.* Set Q = 0, S = {0..s-1}. For each i independently, put e_i ones on S
> and f_i = d_i - e_i ones on R (possible iff 0 <= e_i <= s, 0 <= f_i <= r,
> exactly the interval condition). Full weight is e_i + f_i = d_i. Docs are
> independent, so all combinations co-occur. Q.E.D.
> Degeneracies: s = 0 forces e = (0..0) (only if all d_i <= r = b, always true);
> r = 0 forces e = d; b = 0 forces the unique empty codebook. All machine-checked.

> **Lemma M (coordinate-wise monotonicity, with the required care).**
> Fix all retained distances except doc j != g. As e_j rises (competitor moves
> ahead -> tied -> behind), f_g weakly INCREASES; each single step is checked:
> behind->tied lowers (K-S)/(T)->(K-S)/(T+1); tied->ahead (S,T)->(S+1,T-1)
> lowers since ((K-S)-T)/(T(T-1)) < 0 in the middle regime; behind->ahead
> (S,T)->(S+1,T) lowers. As e_g rises (gold sinks past a competitor
> behind->tied->ahead), f_g weakly DECREASES by the symmetric steps. The subtle
> point flagged in the task is real: a tied->ahead move changes S AND T at once,
> so monotonicity is not "f decreases in S and decreases in T" separately (in
> fact f INCREASES when T shrinks with S fixed); the proof goes through ordered
> single-doc transitions, each verified with exact rational deltas (36 cells).

> **Theorem P (sharp per-gold bounds, K = 3 explicit, general K proved).**
> Over all codebooks compatible with the full profile d, per-gold expected
> inclusion attains:
> MIN at e_g = U_g with all competitors at L (gold highest, rivals lowest);
> MAX at e_g = L_g with all competitors at U.
> *Proof.* Feasible set is a product (Theorem R); objective is coordinate-wise
> monotone (Lemma M); hence extrema sit at opposite corners. Concretely, with
> [L_i, U_i] per doc: fmin_g = f(#{i!=g: L_i < U_g}, 1 + #{i!=g: L_i = U_g}),
> fmax_g = f(#{i!=g: U_i < L_g}, 1 + #{i!=g: U_i = L_g}). Both attained by the
> exhibited corners. For m = 1 gold these are the exact robust bounds.

## 3. Exact finite witnesses (checked, not just claimed)

- Strict LO improvement (K=3): b=4, s=2, r=2, d=(4,0,4,4,4), gold 0. Old T4 lower
  indicator 0 (H = 5 > 3); every compatible codebook is the single pinned
  e=(2,0,2,2,2) with S'=1, T'=4, f = 1/2. Gain 0 -> 1/2.
- Strict HI improvement (K=3): b=4, s=2, r=2, d=(4,0,0,2,2), gold 0. Old T4 upper
  indicator 1 (L = 2 < 3); max corner gives S'=2, T'=3, f = 1/3. Gain 1 -> 1/3.
- Sweep-first-found genuine-deletion witnesses: b=2, s=1, r=1, d=(0,0,0,0):
  old 0/1 vs new 3/4 (four-way retained tie at K=3).
- Dominance verified on all 6,492 K=3 cells: new-min >= old indicator,
  new-max <= old indicator.

## 4. Multi-gold: per-gold average is NOT jointly sharp (Theorem J)

Per-gold maxima conflict through SHARED golds: g's max corner wants rival gold h
at U_h, while h's max corner wants h at L_h. Witness (K=3): b=4, s=2, r=2,
d=(2,2,0,0), golds {0,1}. Each gold's max corner attains f = 1 (gold at 0, other
gold at 2, pinned comps tied at 0: S'=0, T'=3), so avg-of-max = 1; but exact
enumeration over all 3^2 x 1 x 1 = 9 compatible codebooks gives best jointly
attained mean 3/4 (at e = (0,0)), a strict gap of 1/4. Single-gold case has no
conflict (m = 1 bounds are jointly sharp). Computable envelope: with
U = uniform golds-at-L corner value, 0 <= avgmax - jointmax <= Gamma :=
avgmax - U (here Gamma = 1/4, tight). NO complexity-hardness claim is made; the
joint optimum over the product is exactly computable by enumeration on small
cases and a polynomial DP/flow formulation is left OPEN (conjecture, not theorem).

## 5. What a real-data read-only evaluation would measure (NOT run this pass)

On frozen 96-bit sign archives, per question: full top-3 profile d; intervals at
r in {16, 32, 48}; per-gold corners (Theorem P) vs old T3/T4 indicators; share
of golds with strict improvement; and, for the ACTUAL subsets used
(SPREAD/BOT/RAND), where measured subset-code recall falls inside the new
[robust-min, robust-max] envelope. Prediction (conjecture): new lower bounds
stay far below measured means on thin-margin questions, localizing the room a
spike-aware premise must fill. One read-only session; no frozen artifact touched.

## 6. Failed conjectures / corrected derivations (preserved)

1. "Shared Q/S coupling blocks some interval combinations" -- REFUTED by Theorem R
   (independence after canonicalization); the only real blocker is a
   no-duplicates rule, which the protocol does not impose.
2. "f monotone in S and T separately" -- FALSE as stated (shrinking T with S
   fixed INCREASES f); salvaged as Lemma M via ordered transitions.
3. "Avg-of-per-gold-max is jointly attainable" -- REFUTED (Theorem J witness);
   the DELIBERATELY FALSE variant in verify.py asserts it and both checkers
   reject it (fail-closed demo). This also corrects any reading of first-pass T4
   as an "upper envelope": averaging sharp per-gold bounds is a valid but
   UNSHARP multi-gold envelope (gap <= Gamma).
4. First-pass caveats inherited unchanged: T6 is K=1 only (not top-3 evidence);
   data-dependent-selector quantifiers unproven; no literature-novelty claim
   (no priority review, no web access); learned-routing arms stay closed.

## 7. Reproduction

```
$ cd /home/mdp/muse-work/math2-sharp-bounds
$ python3 verify.py results.json        # exit 0
realizability_pairs=4432
K3_checks=6492 ... mono_cells=36 joint={... avg=1, best=3/4, gamma=1/4}
edge={...} broken_rejected=True
DONE ALL SHARP-BOUND CHECKS PASSED (K=3 full + K=1 spot)
$ python3 check_independent.py          # exit 0
independent: realizability=4432 goldcells=380 joint=(avg=1,best=3/4) ...
INDEPENDENT ALL CHECKS PASSED
```

Coverage counted in Section 0; skipped assumptions: none within scope (no
distributional claims; duplicates allowed throughout; K=3 primary + K=1 spot).
Artifacts: REPORT.md (this file), verify.py, results.json, STATUS.md,
check_independent.py. Source archive and original reports untouched (read-only).
