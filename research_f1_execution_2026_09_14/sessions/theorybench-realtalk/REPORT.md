# REPORT — Model-H proxy transfer on REALTALK

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Outcome: NEGATIVE for the LOW48 proxy transfer (primary endpoint contrast
-0.00114, 95% cluster-bootstrap CI [-0.01933, +0.01849], includes zero and is
nonpositive). This falsifies the proxy/transfer, NOT the conditional Model-H
theorem. All results provisional until separate recompute + adversarial review.

## 1. Question, scope, and what was fixed before outcomes

Model H proves a sign-vs-cosine ordering for synthetic signal/nuisance vectors
only. Real coordinates carry no signal/nuisance labels, and theoretical t is
not identified on real data. The tested transfer hypothesis: query-magnitude
proxies (LOW48 = 48 lowest-|q| coords per query) behave like model-H nuisance
dimensions, so positive diagonal scaling of LOW48 should open a sign-minus-float
gap with t (primary: mean[delta(t=4) - delta(t=.25)] > 0, CI excluding zero).
Groups, t grid {0.25, 0.5, 1, 2, 4}, bootstrap (2000 reps, seed 20260913,
archive-cluster, question-weighted), and decision rules were sealed in
PRE_RUN.json BEFORE any intervention metric was computed. No tuning after
outcomes; no benchmark pooling; category strata secondary.

## 2. Inputs and provenance (read-only sources)

- Eval caches `rt_repr/RT01..RT10.pkl` were produced by
  `bench3_realtalk_adapter.py` via the frozen T4D `build_representation`
  (T4D sha256 `3f7f091f…9a7b185a`, matches the port report's pinned value).
  Evidence: cache keys are the adapter format
  (chat_no/file/conv_id/C/QC/qids/gold_rows/qa_diag/id_to_row/N); the scratch
  `RT05_rebuild331.pkl` has raw frozen-T4D keys (archive_fit_docs/…) and is NOT
  the eval input. Cache-vs-rebuild sign arrays are 100% identical
  (maxabs 1.4137e-13, reproducing the port report's 1.4137e-13).
- Text format follows the frozen producer: `"{speaker}: {clean_text}"` plus
  `" [IMAGE: …]"` iff caption; NO date component (code governs over prompt
  paraphrase). Questions transformed post-fit; events keys never read.
- No embedding regeneration, no network, no installs; interpreter
  `/home/mdp/muse-work/ml-python -B` (3.14.4 / numpy 2.5.3), threads=1 env,
  PYTHONDONTWRITEBYTECODE=1. Windows venv not executed.

## 3. Gate BEFORE intervention: PASS

Recomputed original native SIGN96 and centered-float96 fractional R@3 from
caches with exact frozen conventions (K=3, NT=20,
tie_seed=5_100_000+ci*100_000+t*100+99; Hamming lexsort((p,d)); cosine
lexsort((p,-s)); invalid FR=null excluded):

- Counts from code: 728 total / 705 measured / 23 excluded (exact IDs in
  `excluded_ids.json`, derived from source details.json by code).
- Per-QA max abs diff vs stored details.json: 0.0 native, 0.0 float.
- Means: 0.22477507598784194 / 0.17253405381064957, diff vs anchors 0.0/0.0.
- Tolerance 1e-12; no cross-stack relaxation needed (bit-identical here).

## 4. Intervention outcomes (exact tie-bucket expectation, n=705)

Primary outcome uses the exact expected fractional R@3 under uniform tie
priorities (per-gold `min(1,(K-S)/(T+1))`, shared-gold formula; ties by exact
`==` on int Hamming / float64 scores). The 20-seed MC is reported alongside
and differs slightly, as the plan anticipates
(exact sign mean 0.225535 vs MC 0.224775 at t=1).

| group  | d(t=.25) | d(t=.5) | d(t=1) | d(t=2) | d(t=4) |
|--------|----------|---------|--------|--------|--------|
| LOW48  | 0.051716 | 0.051905 | 0.053001 | 0.052080 | 0.050780 |
| HIGH48 | 0.050780 | 0.052080 | 0.053001 | 0.051905 | 0.051716 |
| FULL96 | 0.053001 | 0.053001 | 0.053001 | 0.053001 | 0.053001 |

(d = mean sign-minus-float gap; sign_exact is t-invariant by construction —
sign encodings are byte-identical for all positive t, verified 0 violations;
this tautology is NOT claimed as theory evidence.)

- PRIMARY (LOW48 endpoint contrast): effect -0.001137, CI [-0.01933, +0.01849].
  Nonpositive with CI covering zero → NEGATIVE per the fixed rule: the LOW48
  proxy does not transfer. HIGH48 comparison: +0.000755, CI [-0.01799,
  +0.01880], likewise inconclusive.
- Pointwise monotonicity violations (any decreasing adjacent delta as t
  grows): LOW48 41/705 (5.8%), HIGH48 40/705 (5.7%), FULL96 0/705. Model-H
  pointwise monotonicity cannot transfer unconditionally.
- LOW48@t and HIGH48@1/t curves agree to ~2e-4 (global-scale identity, up to
  floating-point tie flips); FULL96 is exactly flat (maxabs 0.0, both scores
  and ranks invariant).
- Per-category LOW48 contrasts (secondary, no selection): cat1 (n=288)
  +0.01559, cat2 (n=312) -0.00641, cat3 (n=105) -0.03000 — mixed signs,
  consistent with no systematic proxy effect.
- MC sensitivity at endpoints reproduces the exact pattern to ~1e-3
  (LOW48 MC delta: .050957/.052241/.050020 at t=.25/1/4).
- Bootstrap caveat: only 10 archive clusters — the interval is approximate;
  raw effects are reported and the effect is two orders below the CI half-width.

## 5. Checks (verification.py, 23/23 PASS)

Baseline per-QA reproduction (0.0/0.0); positive-scale sign invariance (0
violations); t=1 identity (0 violations); FULL96 cosine invariance (maxabs
0.0); MC t=1 reproduces stored details bit-exactly (0.0); group mapping
reproduced from caches for all 705 QAs; 3 representative QAs recomputed via an
independent pure-Python `sorted()` path incl. a discriminating case
(RT03_q003: native 1.0 vs float 0.0, both matched); bootstrap determinism
re-run; PRE_RUN predates outputs; PLAN/details/caches hashes stable.
`CHECKS: 23/23 pass; gate=728/705/23 outcomes=10575 rows`
(23rd check: exact exclusion-ID list persisted in `excluded_ids.json`).

## 6. Artifacts (isolated outputs only, this workspace)

PLAN.md (byte-exact, sha a0f9e8e6…), STATUS.md, producer_run_realtalk.py,
producer_adapter.py (byte-exact copies), gate_runner.py, gate.json,
gate_receipt.txt, PRE_RUN.json, transfer_runner.py, checkpoints/ (10 per-chat
pickles), per_query.jsonl (10575 rows), summary.json, verification.py,
verify_receipt.txt, run_receipt.txt, REPORT.md (this file).
Heavy caches remain outside Git. No push performed.

## 7. Limits

Single stack; exact-expectation estimand differs from 20-seed MC by ~9e-4 at
baseline; few (10) clusters; theory reading restricted to the two round-3
ranking files; sign invariance is a construction tautology, not validity
evidence; no unconditional-multinomial computation was used (gold is shared).
This is NOT preregistered and NOT yet independently audited.
