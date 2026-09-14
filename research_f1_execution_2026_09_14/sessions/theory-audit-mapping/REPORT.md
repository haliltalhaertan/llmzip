[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT.md — theorem-to-intervention fidelity audit (Model H vs benchmark LOW48/HIGH48)

## 0. Plain-English summary (Özet)

We tested whether the benchmark intervention (scaling LOW48 coordinates of
BOTH documents and query) is the same mathematical parameter as Model H's
theorem (scaling document-only nuisance with a FIXED query). **It is not.**
The algebra differs (t² in the numerator instead of t, plus unequal document
norms), the query-variation the theorem holds fixed is varied by the
experiment, and "low query magnitude" was never shown to mean "nuisance".
So the benchmark outcomes — LME strongly opposite (-6.44pp), REALTALK
inconclusive (-0.09pp), PerLTQA weakly positive (+2.46pp), LoCoMo opposite but
conditional (-2.58pp) — **falsify only the unlicensed transfer mapping, never
the conditional synthetic theorem**. A second, independent finding: even the
correct joint-scaling math admits nonmonotone pairwise ranking (proved by an
exact rational counterexample in `verify.py`), so no uniform-monotonicity law
was ever licensed for this intervention — consistent with the hundreds of
per-QA monotonicity violations the coordinators already recorded. Nothing here
is a new compression method, and HIGH48 adds zero independent evidence (it is
an algebraic mirror of LOW48). All diagnosis below is post-hoc and
exploratory, not preregistered and not a held-out prediction.

## 1. Scope, budget, and what was NOT done

- Bounded ~20-minute first pass. Writes ONLY in
  `/home/mdp/muse-work/theory-audit-mapping` (`STATUS.md`, `verify.py`,
  `results.json`, this file). All prior sources READ ONLY (hashes §8).
- No Git push/main changes (no repo writes at all), no installs, no network,
  no paid APIs, no embeddings, no new training/routing, no new empirical
  arms, frozen Task4F1 untouched. Muse subscription only.
- `threads=1` (`OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1`), and
  `PYTHONDONTWRITEBYTECODE=1` with `/home/mdp/muse-work/ml-python -B`
  (Python 3.14.4, numpy 2.5.3 — versions re-observed at run time, §8).
- Coordinator corrections supersede unreviewed worker prose throughout; claim
  provenance (`source file + line`) is given inline. "Before" hashes were not
  taken prior to reading (procedure gap, disclosed); "after" hashes plus
  read-only tool discipline are the preservation evidence (§8).
- The background 1+1-dimension monotonicity sweep did not finish inside the
  pass budget: whether a single scaled coordinate already allows
  nonmonotonicity is reported UNRESOLVED (§5), not asserted either way.

## 2. The central identification failure (with exact algebra)

Model H (`all_n_ranking/REPORT.md:12-23`): query `q=(1,1,1)` is FIXED while
documents move with `t`: gold `R=(1,t·e1,t·e2)`, nongold `I_j=(-1,t·d_j1,…)`.
All documents share norm `√(1+2t²)`, so dot order = cosine order and the gap
is `G^cos_j = 2-2t·D_j` — linear in `t`.

Benchmark (`PLAN.md:21-23` + all four runners): for group G and
`t∈{0.25,0.5,1,2,4}`, BOTH document and query group coords are multiplied by
`t` (LME `run_lme.py:265-268`; REALTALK `transfer_runner.py:152-160`;
PerLTQA `runner.py:244-252`; LoCoMo `run_locomo.py:293-297`).

For arbitrary document `C_i=(c_i,g_i)`, query `q=(qc,qg)`, fixed group G,
joint scaling gives, with `z=t²`:

- dot: `C_i(t)·q(t) = qc·c_i + t²(qg·g_i) = a_i + z·b_i`
- doc norm²: `||c_i||² + t²||g_i||² = u_i + z·v_i`
- query norm: common positive factor across documents — removed for ranking.

Rank-equivalent score: **`s_i(z) = (a_i + z·b_i)/√(u_i + z·v_i)`**.
Checked in `verify.py` §H: `raw_cosine == s/||q(t)||` to <1e-12 on the
counterexample vectors (numpy as second route, Fractions as oracle).

Three differences from Model H, each load-bearing:

1. **Numerator is quadratic in t** (`z=t²` multiplies the group-dot), where
   Model H's gap is linear in `t`. Different parameter, different motion.
2. **Query is not fixed.** Model H's proof varies documents against a frozen
   `q`; the benchmark reweights the query itself, changing what "alignment"
   means per t. Query magnitude alone never established relevance/nuisance
   (§4, error E2).
3. **Document norms are unequal and t-dependent** (`u_i+z·v_i` differs per
   document), where Model H's proof uses one shared norm to equate dot order
   with cosine order (`COORDINATOR_REVIEW.md:5`: "Equal document norms justify
   dot/cosine ordering in this particular synthetic law").

Necessary vs merely-sufficient assumptions in H (read off the proof,
`REPORT.md:51-65`): the cell-by-cell coupling table (`D`, gap formulas) is
necessary — it IS the theorem. Fixed-`q`, equal norms, Rademacher signs, and
uniform tie priorities are the sufficient synthetic scaffolding that makes the
table hold; none was ever mapped to real centered, correlated, continuous
benchmark vectors. The real-data mappings (LOW48-by-|q| = nuisance; t=1 =
signal/nuisance balance point; uncentered binary law ≈ centered embeddings)
were never justified — PerLTQA coordinator states this explicitly
(`perltqa/COORDINATOR_REVIEW.md:7`: "Real intervention t=1 is unmodified
embeddings, NOT the synthetic law's identified signal/nuisance balance
point").

## 3. Pairwise crossing analysis under joint scaling

Crossing `s_1(z)=s_2(z)` requires care before squaring (sign/zero
discipline, implemented exactly in `verify.py:cmp_rank`):

- Opposite strict signs (or nonzero-vs-zero) decide WITHOUT squaring.
- Squaring `n_1²d_2 ? n_2²d_1` is valid only when both numerators are nonzero
  with a shared strict sign (order flips if that sign is negative).
- Squared equation is cubic in `z` (linear² × linear), so up to three
  crossings survive the sign filter: uniform monotonicity is NOT provable in
  general.

Minimal rational counterexample (shared query, fixed group, exact integers —
`verify.py` §§B–D, 87/87 PASS, numpy cross-confirmed):

- query complement `qc=(-1,-1)`, query group `qg=(-1,-1)` (fixed group =
  last two coords);
- `C1`: complement `(2,1)`, group `(-3,-1)` → `(a,b,u,v)=(-3,4,5,10)`;
- `C2`: complement `(1,1)`, group `(-3,1)` → `(a,b,u,v)=(-2,2,2,10)`;
- joint-scaling verdicts (C1−C2) at `z=t² ∈ {1/64,1/16,1/4,1,4,16,64}`:
  **`(+1,-1,-1,+1,+1,+1,+1)`** — C1 leads, loses, leads again.
  Nonmonotonicity with fixed group and shared query. Q.E.D.
- Zero-discipline spot included: at `z=1`, C2's numerator is exactly 0 while
  C1's is positive — decided without squaring (`verify.py` C.zero-verdict).
- Raw-vs-rank-score derivative: `raw_i(t)=s_i(t)/||q(t)||`; ranking uses only
  `s_i`, so slope stories told about raw cosine trajectories (which mix in the
  growing query norm) do not transfer to ranking claims. The identity — not a
  sign-flip exhibit — is machine-checked (§H).

Matched algebraic ablations on the SAME vectors (synthetic only, no new arms):

| arm (same C1,C2,q) | verdicts at t∈{1/8,…,8} | shape |
|---|---|---|
| joint (doc+query) | C1,C2,C2,C1,C1,C1,C1 | nonmonotone (two flips) |
| document-only | all C1 | monotone, no flip |
| query-only | C2,C2,C1,C1,C1,C1,C1 | monotone, one flip |

Document-only, query-only, and joint scaling are three different parameters
with three different qualitative behaviors on identical inputs. The benchmark
ran the first row; Model H proves something about a fourth (doc-only,
fixed-q, equal-norm, binary-sign) setup. No outcome of one binds the others.

## 4. Error taxonomy (one entry each, no 'proven cause' from correlation)

- **(a) Algebra error — ours (experimental identification).** Treating joint
  doc+query scaling as Model H's document-only `t`. Correct formula is
  `s_i(z)=(a_i+z b_i)/√(u_i+z v_i)`, `z=t²` (§2). Correction: re-derive every
  prediction from the joint law, not the H gap table.
- **(b) Wrong assumption — query fixed.** H holds `q=(1,1,1)` frozen; runners
  scale `q[cols]` too (four code cites, §2). Correction: any transfer must
  model query reweighting, not quote frozen-query theorems.
- **(c) Unidentifiable mapping — |q|-magnitude as nuisance label.** PLAN
  itself warns proxies "mean low/high query magnitude, NOT proven
  nuisance/signal dimensions" (`PLAN.md:21`); no gold-free evidence ever
  upgraded the proxy to a label, and relevance must not be defined from gold
  after outcomes. Correction: predeclare a positive identification test (e.g.
  gold-conditional predictiveness on frozen caches) before any causal reading.
- **(d) Metric mismatch — endpoint contrast ≠ monotone law.** The primary
  (`mean[delta(4)-delta(.25)]>0`) is an aggregate endpoint; Model H's
  pointwise monotonicity is strictly stronger. PerLTQA proves the gap: primary
  positive (+2.46pp) with a decrease-then-increase curve and 961/8265
  decreasing-adjacent QAs. Correction: report both; never claim the law from
  the endpoint.
- **(e) Numerical/provenance bugs — worker-level, coordinator-caught.**
  REALTALK headline used mean-of-bootstrap-replicates instead of the
  prespecified mean contrast (corrected -0.0936pp,
  `realtalk/COORDINATOR_REVIEW.md:7`); sign_mechanism Theorem 2(iii) transport
  used an unconditional multinomial ignoring the shared gold (exact values
  replaced: N=6 SIGN 1763/2048 etc.,
  `sign_mechanism/COORDINATOR_REVIEW.md:11-14`); all-N negative control passed
  a swapped win/loss probability (`all_n_ranking/COORDINATOR_REVIEW.md:9`).
  Corrections stand as written by coordinators; none touches the main H
  theorem.
- **(f) Inference overreach — ours + worker prose.** "Math theorem remains
  true" is scoped: the all-N H theorem holds (strictness wording corrected,
  `all_n_ranking/COORDINATOR_REVIEW.md:7`); the sign_mechanism top-3 numbers
  were FALSE and replaced; HIGH48 "corroboration" is a mirror (§6); "two
  checker paths" were single-author, not independent review (stated in both
  coordinator notes). Four primaries are unadjusted; LoCoMo is CONDITIONAL
  (float gate not met, `locomo/COORDINATOR_REVIEW.md:7`); the +12pp LoCoMo
  baseline is ungrounded (current exact-cache value +6.83pp, ibid.:9).
  Correction: cite each result with its qualifier, always.

## 5. What the observed outcomes actually license (post-hoc, exploratory)

- LME LOW48 `-6.44326pp, CI[-9.2734,-3.6871]`: opposite-direction, interval
  excludes zero — falsifies THIS proxy transfer, not H
  (`lme/COORDINATOR_REVIEW.md:9`). Float means rise 42.53%→48.97% across the
  sweep while sign is fixed: reweighted float retrieval, not a codec.
- REALTALK `-0.093606pp, CI[-1.9330,+1.8490]`: inconclusive for a population
  mean (interval covers substantial effects either way); only 10 clusters
  (`realtalk/COORDINATOR_REVIEW.md:9`). Pointwise monotonicity still
  contradicted on these arrays (41/705).
- PerLTQA `+2.46415pp, CI[1.5540,3.44284]`: prespecified aggregate direction
  only; sign arm invariant so this is float degradation, "not a newly improved
  compressed method" (`perltqa/COORDINATOR_REVIEW.md:9`); sections diverge
  (profile -18.62pp vs events +4.95/social +8.65); monotonic law fails.
- LoCoMo `-2.58291pp, CI[-3.77676,-1.31321]`: CONDITIONAL — protocol deviation
  (fresh float baseline substituted, gate not met). Exploratory only.
- UNRESOLVED in this pass: 1+1-dim (single scaled coordinate) monotonicity —
  background sweep unfinished; no claim made. Minimal discriminating test is
  ledger item R4.

## 6. HIGH48 has no independent evidential value (proof sketch, checked)

LOW48(t) scales low coords by `t` in both C and q. HIGH48(1/t) scales high
coords by `1/t`. Multiply the latter's vectors by global `t>0`: high coords
return to original, low coords become `t`-scaled — exactly LOW48(t). Positive
global scaling cancels in cosine (and preserves all signs), so per-QA
float-recall pairs must match exactly. REALTALK coordinator verified max
difference 0 (`realtalk/COORDINATOR_REVIEW.md:13`); PerLTQA notes CIs differ
only from separate bootstrap draws (`perltqa/COORDINATOR_REVIEW.md:11`).
`verify.py` §E checks the integer proportionality exactly. Corroboration
claims from HIGH48 must be withdrawn everywhere.

## 7. Ranked error ledger

| # | Claim | Evidence | Correction | Still valid | Minimal discriminating next test |
|---|---|---|---|---|---|
| R1 | Joint LOW48 scaling tests Model H's parameter | §2 algebra + 4 runner cites: numerator `a+z b` vs H's linear gap; query scaled | Different parameter; withdraw identification | H theorem (scoped); observed contrasts as proxy-only facts | Re-derive predicted sign from joint law on frozen caches (read-only), preregistered before looking |
| R2 | Low-|q| coords are nuisance | PLAN warning + no identification test; §4c | Proxy ≠ label; no relevance-from-gold | Endpoint numbers as directional observations | Gold-conditional predictiveness test of LOW48 membership on frozen per_query rows, fixed before running |
| R3 | Endpoint contrast confirms monotone law | PerLTQA +2.46pp with 961 violations + U-curve; LME 114/470, REALTALK 41/705, LoCoMo 151 violations | Report curve + violation fraction alongside primary | Primaries as stated | Preregister curve-shape + violation-rate criteria, not just endpoints |
| R4 | Uniform monotonicity holds for joint scaling | §3 counterexample (+,-,-,+,+,+,+) | No universal rule; crossings ≤3 in z, sign-filtered | Single-crossing cases exist | Settle 1+1-dim: exhaustive small-integer proof or counterexample (unfinished sweep) |
| R5 | HIGH48 corroborates LOW48 | §6 proportionality + REALTALK exact match | Mirror, not replication | Neither as independent evidence | Enforce identical bootstrap draws if both shown (must mirror) |
| R6 | Theorem "remains true" unconditionally | §4e–f: transport numbers were false; strictness wording fixed; single-author checkers | Scope per result; quote corrected values only | All-N H theorem with corrected wording | Genuinely independent re-derivation by a second author before any citation |
| R7 | LoCoMo result is fully gated | Float gate not met; +12pp baseline ungrounded | CONDITIONAL status stands | Exploratory contrast value | Independent float-baseline recompute + baseline-provenance audit |

## 8. Reproduction: exact commands, counts, hashes

Executed (each once, in order; outputs observed, not assumed):

1. `cd /home/mdp/muse-work/theory-audit-mapping && PYTHONDONTWRITEBYTECODE=1
   OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/mdp/muse-work/ml-python -B
   verify.py` → `87/87 checks passed`, exit 0, writes `results.json`
   (first run: SyntaxError from uncommented label banner — the same failure
   mode `all_n_ranking/REPORT.md:96-99` documents; fixed by commenting line 1.
   Second run: 86/87 — my hand-predicted query-only flip point was one grid
   step off; the exact Fraction computation corrected me, expectation updated,
   third run 87/87).
2. Counterexample pre-searches (throwaway, `/tmp`-equivalent inline probes,
   not deliverables): 2+2-dim random sweep found nonmonotone pairs (5 shown);
   1+1-dim sweep to 500k trials did not complete in budget — UNRESOLVED.
3. `sha256sum` of the 13 source files read (after-read hashes; before-hashes
   not taken — disclosed gap; no writes were ever made to source roots):

- `theory_benchmark_test_v1/PLAN.md` a0f9e8e6…821
- `round3/all_n_ranking/REPORT.md` 137c7aae…34aa; `COORDINATOR_REVIEW.md` 2e3d7242…3d838
- `sign_mechanism/REPORT.md` b5c2752f…5fa1; `COORDINATOR_REVIEW.md` 351a679b…89b39
- `lme/run_lme.py` 6785a748…f0b3b7; `realtalk/transfer_runner.py` 4fc0266c…406366
- `perltqa/runner.py` f53072af…32db4cc; `locomo/run_locomo.py` 0c924486…19e419
- `lme/COORDINATOR_REVIEW.md` 537960d5…02e44; `realtalk/…` 3aaabbc7…f17f9ee
- `perltqa/…` a80f3bcd…53c931a4; `locomo/…` dba3a6624…21a928959
  (full hex in tool log exec-15; `git status` N/A — not a git checkout at
  that mount.)

Counts: 13 source files read (4 coordinator reviews authoritative over worker
prose); 4 runner scaling kernels inspected; 87/87 verify.py checks pass
(~40 Model-H table/dominance cells + 9 counterexample/ablation + identity,
invariance, proportionality, and numpy cross-checks); 0 new empirical arms;
0 source bytes modified; 4 files written (STATUS.md, verify.py, results.json,
REPORT.md). No independent-review claim: `verify.py`'s Fractions-vs-numpy
agreement is one author's two routes, not two authors. All diagnosis post-hoc
and exploratory: partial and disclosed beats fabricated and flattering.
