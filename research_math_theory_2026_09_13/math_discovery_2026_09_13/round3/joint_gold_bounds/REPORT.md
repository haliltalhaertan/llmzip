# Exact joint multi-gold bounds: corner theorem (third pass)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

No scientific priority, no universal security/losslessness claim, no benchmark
win, no benchmark run. All arithmetic exact (`Fraction`s). Proofs below are
proofs; finite enumerations are tightness/falsification evidence only, never
universal proofs. Conjectures are labeled as such.

## 0. Setup (quantifiers, premises, tie law)

Fix integers `b, s, r = b - s, n`, full profile `d ∈ {0..b}^n`, retained set `S`
fixed with `|S| = s`, designated gold set `G`, `|G| = m ≥ 1`, `1 ≤ K ≤ n`.
Premise (taken valid from round 2, re-checked constructively in
`check_independent.py` §B): binary codebook, duplicates allowed, and every
product choice `e_i ∈ [L_i, U_i] := [max(0,d_i-r), min(s,d_i)]` is jointly
realizable by one common query and one fixed `S`. Metric for a retained vector
`e`: `R(e) = E_π[C(e,π)] / m`, where `π` ranges uniformly over all `n!`
priority permutations, ranking is lexicographic by `(e_i, rank_π(i))`
(smaller first), and `C(e,π)` = number of golds among the first `K`.

## 1. THEOREM (joint corner; the one rigorous result of this pass)

> For every `d, G, K` as above, over all jointly realizable `e`:
> MAX of `R` is attained at the corner `e^max` (every gold at `L`, every
> nongold at `U`); MIN at the reverse corner `e^min`. Both corners are
> feasible, hence the bounds are sharp.

> *Proof.* Fix `π`. Others' relative order is then fixed; moving one doc only
> reinserts it. Write others sorted as `a_1, a_2, …` and let `pos` be the
> moved doc's 1-indexed slot.
>
> Claim A (gold improvement): fix `e_{-g}`, gold `g`, and `π`. If `e'_g ≤ e_g`
> (`pos' ≤ pos`), then `C(e',π) ≥ C(e,π)`. Indeed: if `pos > K` and `pos' > K`,
> the top-`K` sets coincide. If `pos' ≤ K < pos`, top-`K` gains `g` and loses
> `a_K`: gold count changes by `+1` if `a_K` is nongold, `0` if `a_K` is gold
> ("at worst displaces a gold"). If `pos ≤ K`, then `pos' ≤ K` and both
> top-`K` sets equal `{a_1..a_{K-1}, g}` as sets — identical count.
>
> Claim B (nongold worsening): fix `e_{-i}`, nongold `i`, and `π`. If
> `e'_i ≥ e_i` (`pos' ≥ pos`), then `C(e',π) ≥ C(e,π)`. Indeed: if both slots
> are `≤ K`, both top-`K` sets equal `{a_1..a_{K-1}, i}`; if `pos ≤ K < pos'`,
> top-`K` loses nongold `i` and gains `a_K`, weakly increasing gold count; if
> both `> K`, sets coincide.
>
> Path argument: from any feasible `e`, move each gold down to `L_g` and each
> nongold up to `U_i` one doc at a time; each step weakly raises `C(·,π)` for
> EVERY `π` simultaneously. Hence `C(e^max,π) ≥ C(e,π)` for all `π`, and
> averaging over `π` gives `R(e^max) ≥ R(e)` for all feasible `e`. The MIN
> direction is symmetric (reverse every move). ∎

Degeneracies (all inside the proof, machine-checked): `K = n` ⇒ top-`K` is
everything, `C ≡ m`, all corners tie. `s = 0` ⇒ single feasible point
`e = 0` (corners coincide). `r = 0` ⇒ `e = d` pinned (corners coincide).
`m = n` (all gold) ⇒ `C ≡ K`; claims hold vacuously. `K ≥ m` needs no special
casing — the proof never displaces more than one doc per move. Simultaneous
ties are handled because `π` is fixed before the move (distinct priorities;
no tied comparison ever occurs under fixed `π`).

## 2. Exact evaluation (no search needed) and recall change

For any `e`, group docs by retained value into buckets `(g_j, t_j)` with `S_j`
docs strictly ahead. Expected gold count (exact):
`Σ_{full} g_j + (K − S_j)·g_j/t_j` over the one partial bucket; divide by `m`.
Cost `O(n log n)`. Applied to `e^max / e^min` this yields the sharp joint
bounds directly. Baseline `R_orig` = same formula on the full profile `d`;
sharp recall-change interval = `[R(e^min) − R_orig, R(e^max) − R_orig]`.
Witness reproduction `d = (2,2,0,0)`, `b = 4, s = 2, K = 3`, `G = {0,1}`:
joint MAX corner `(0,0,0,0)` → `3/4`; joint MIN corner `(2,2,0,0)` → `1/2`;
baseline `1/2`; change `∈ [0, 1/4]`; average of per-gold maxima `= 1`
(each gold alone attains `1` at `(0,2,0,0)`-type corners) — strict gap `1/4`
to the joint `3/4`, as in round 2. This confirms the target is NOT the
average of incompatible per-gold maxima.

## 3. Weighted extension: corner theorem FAILS (smallest counterexample)

With nonnegative gold weights `w_g ≥ 0` and objective = expected gold weight
in top-`K`, Claim A breaks: improving a light gold can displace a heavy gold
(§1 crossing case: net change `w_g − w_{a_K}` can be negative). Smallest
counterexample (`n = 2, m = 2, K = 1`, weights `1, 2`, both intervals `[0,1]`
via `d = (1,1)`, `b = 2, s = 1`): all-golds-at-`L` corner `(0,0)` gives `3/2`,
but deviating the LIGHT gold downward to `(1,0)` gives `2 > 3/2`. Verified
exact in both scripts. Hence nonnegative weights do NOT preserve the corner
theorem in general. Preserved fragments: equal weights (reduces to §1), and
`K = n` (trivially, everything is taken). Failure persists even at `K ≥ m`:
e.g. `K = 2` with golds `(w=1, w=100)` + pinned nongold at `0` gives corner
`202/3 < 100` at the deviation — so `K ≥ m` does not rescue it.

## 4. Per-question recall vs benchmark aggregation (no empirical run)

The theorem bounds per-question fractional recall (one gold set, one
codebook). Macro recall = mean of per-question recalls; micro recall =
gold-count-weighted mean. Since each question's codebook varies independently
(product across questions), the corpus-level sharp bounds are the same
(mean / weighted-mean) aggregation of the per-question corner values — valid
and sharp with no extra gap. Aggregation choice only changes question
weighting, not the corner construction. No data touched.

## 5. Verification (two formulations + negative control)

- `python3 verify.py results.json` → exit 0. Bucket formulation; 4400
  dominance cells (`rmin ≤ v ≤ rmax` over every feasible `e`): sweep A
  (`b=2,s=1,n=3`, all profiles × all nonempty gold sets × all `K`), sweep B
  (`b=3,s=2,n=3`, all profiles × gold sets, `K∈{1,3}`), sweep C (8 targeted
  `n=4` cases incl. witness, `s=0`, `r=0`, `K=n`, `m=n`). Zero violations.
- `python3 check_independent.py` → exit 0. Differently formulated: expectation
  by raw `n!` permutation enumeration (no bucket formula), 2478 cells, plus 19
  explicit binary codebook builds re-measuring Hamming distances. Agrees with
  primary (witness joint `3/4` both ways).
- Negative control: the deliberately false universal "avg of per-gold maxima
  is jointly attainable" is asserted-then-rejected on the witness
  (`1 ≠ 3/4`, verdict REJECTED in `results.json`); both scripts abort if it
  ever held.
- Failed attempts / corrections this pass: none structural — the coordinator's
  suggested coupling went through on first formalization; one draft edge
  (`s=0` baseline) was folded into sweep C rather than kept separate. No
  DP/flow machinery was needed (consistent with the coordinator's warning that
  hardness was never established). Scope limits: exhaustive checks cover
  `n ≤ 4`, `b ≤ 4`; universality rests on the §1 proof, not the sweeps.
- Commands/exit codes: `python3 verify.py results.json` → 0;
  `python3 check_independent.py` → 0;
  results inspection via `python3 -c` → 0. No network, no installs, no
  external model APIs, no git writes (working tree only: STATUS.md, REPORT.md,
  verify.py, results.json, check_independent.py).
