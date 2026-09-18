# 02_itq — HARD REVIEW ROUND 2 REPORT: ITQ vs rotation

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Neutral audit (neither STOP nor CONTINUE as goal). Same-CLI agents provide only
partial independence — disclosed. Prior agent reports treated as fallible, verified below.

## Outcome (one paragraph)

The two suspected flaws in the prior ITQ audit are real and self-documented in its own
code: it used a different tie-break from the coordinator and fit ITQ only once while
varying only the random controls. Re-running with the exact coordinator tie rule and
document/query pipeline, five ITQ initializations with paired same-seed random controls:
on the full RealTalk cohort (n=705) ITQ underperforms its paired random rotation on the
production qscale scorer at all five seeds, and the five ITQ runs sit entirely below the
five RAND runs; sym is null-scale and mixed. On a documented 5-archive PerLTQA subset
(n=1605) the paired contrasts are mixed-sign at ±2pp scale — a null, and NO full-cohort
PerLTQA claim is made. Quantization loss decreased in all 75 fits while RealTalk
retrieval moved against ITQ, quantifying the objective-vs-retrieval dissociation. The
codex Haar-objective package measures the same per-entry quantity on synthetic data with
historical (non-refit) finals and no retrieval — it cannot support any retrieval or
novelty claim, and none is made here (no primary literature reviewed).

## Exact protocol recovered (P1)

Source: `top10_comparison_r1/math_r1/quant/quant_math.py` (copied here as
`quant_math_ORIG.py`, sha256 `2f5514d2…`; published pilot copy byte-identical per
`diff -q`, no output = identical).

- Arms fit on DOCUMENTS ONLY, per archive; payload asserted `(N,12)` packed big-endian.
  `FULL`: bits `(C>=0)`. `ITQ_C`: 50 alternating-minimization iters
  (`quant_math_ORIG.py:140-158`), init `random_orthogonal(96, 20260916)`, seed fixed
  before running; query scored as `QC R`; sigma refit on rotated DOCUMENTS ONLY.
  `RAND_s`: same pipeline, fixed random-orthogonal R; `RAND_20260916` uses the same
  generator+seed as the ITQ init, so ITQ starts exactly there (`REPORT_ORIG.md:40-42`).
- Tie rule (load-bearing): descending score, then ascending
  `SHA256("top10-r1|"+archive_id+"|"+row)`, then row; exactly ten even at boundary ties;
  `audit_baseline_lib_ORIG.py:79-83` (`TIE_SALT="top10-r1"`), copied here as
  `audit_baseline_lib_ORIG.py` (sha256 `673cb430…`). Scorers: sym `-Hamming`,
  qscale `Dpm @ (Qc/sig).T` with `sig=max(std(ddof=0),1e-12)` on that arm's doc frame
  (`quant_math_ORIG.py:161-171,588-594`). Bootstrap for published contrasts: paired
  archive-clustered, 20000 reps, seed 20260916 (not re-run; see limits).
- Codex branch `codex/v52-itq-haar-objective-2026-09-12` (`b06bc04…`): objective
  `mean((abs(Y@R)-1)^2)` per entry (`replay_objectives.py:55-57`); PLAN states
  `fit_itq:false`, `historical_final_objectives: read from pinned RESULTS, not refitted`,
  `no held-out or retrieval measurement`. Scope: 12 synthetic panels × 20 init + 20 null
  seeds; replay criterion is exact equality of the 480 stored initial/null values only.

## Prior-audit flaws confirmed (exact citations)

1. Changed ties: `audit_hard_r1/claims/au_c1_itq.py:11-15` states its top-10 is
   "stable descending argsort (ties → lower doc index)" and "This DIFFERS from the
   coordinator's archive-seeded det_top10", with FULL/sym calibration off by 0.3–0.5pp.
   Severity: HIGH for absolute levels; its ITQ-vs-RAND contrast was internally
   self-consistent but is not an exact-protocol replication.
2. Single ITQ fit: `au_c1_itq.py:fit_itq(C)` called once per archive at default seed
   20260916 while 7 fresh seeds varied only RAND (`HARD_AUDIT_CLAIMS.md:29-32`). So
   "ITQ beats 0/10 rotations" varies the control distribution but not the ITQ init
   distribution. Severity: HIGH for the init-sensitivity question — fixed by this audit.

## Tests performed and observed results

### P2 — Baseline gates (exact tie rule, copied `det_top10/hrn/expected_hit`)

- Tie-equivalence: cached `fast_topk` vs copied `audit.det_top10` on 18 random-score
  samples per bench (k=3,10): 36/36 identical (`probe_rt.log`, `probe_pq.log`).
- FULL replay from read-only caches vs stored `RESULTS_ORIG.json` per-archive rows
  (hit10/fr3/exp_hit10 × sym/qscale): RealTalk 10 archives → 60/60 exact;
  PerLTQA subset 5 archives → 30/30 exact; max abs diff **0.000e+00** in both
  (`summary_rt.json`, `summary_pqsub5.json`). Cohort means reproduce to all 14 decimals,
  e.g. RT FULL/qscale 49.645390070921984 = published. G1 bit-identity (0/858624 RT,
  0/1179648 PQ) was not rebuilt from text; cache==rebuilt is established empirically by
  the 90/90 exact gate matches (rebuild path uses identical C up to the proven G1).
- Explicit verification (not new): single-fit contrasts reproduce published rounded
  values — ITQ16−FULL qscale −16.8794 (publ −16.88); ITQ16−RAND16/17/18 qscale
  −2.4113/−2.5532/−1.8440 (publ −2.41/−2.55/−1.84). (`evidence_itq.json`,
  `benchmarks.rt.verify_vs_published`.)

### P3 — Five ITQ inits + paired same-seed RANDs, identical ties/pipeline

Design: seeds `[20260916, 20260917, 20260918, 7, 42]`; `RAND_s` reuses the exact init
rotation of `ITQ_s`, so each paired contrast isolates the optimizer. 75 ITQ fits total
(50 RT + 25 PQ-subset); all decreased quantization loss (asserted per fit, 75/75);
orthogonality error <1e-10 every fit; payload `(N,12)` asserted every frame.
Rows: `per_archive_rows_rt.csv` (220 data rows), `per_archive_rows_pqsub5.csv`
(110 data rows) — 330 mechanically counted rows (`wc -l` = 332 with headers).

RealTalk, FULL cohort (10 archives, n=705) — qscale Hit@10, ITQ_s − RAND_s:

| seed | ITQ | RAND | diff (pp) | per-archive −/0/+ |
|---|---|---|---|---|
| 20260916 | 32.77 | 35.18 | −2.41 | 7/1/2 |
| 20260917 | 34.18 | 35.32 | −1.13 | 6/2/2 |
| 20260918 | 34.47 | 34.61 | −0.14 | 5/1/4 |
| 7 | 32.91 | 34.33 | −1.42 | 6/2/2 |
| 42 | 33.90 | 36.17 | −2.27 | 7/1/2 |

ITQ range [32.77, 34.47] lies entirely below RAND range [34.33, 36.17]. RT sym paired
diffs: +0.14/0.00/+0.43/0.00/−1.13pp — null-scale, mixed sign (5/0/5, 6/0/4, 5/1/4,
4/2/4, 5/2/3). FR@3/Hit@3/exp rows persisted per archive; same pattern (see CSVs).

PerLTQA SUBSET (first 5 archives alphabetically — Cai Xiuying, Cao Lili, Feng Wei,
Han Gang, He Feng; n=1605; deterministic, documented): qscale paired diffs
+0.81/−0.81/−0.62/−1.25/−0.81pp; sym +1.25/+0.75/−2.18/−1.31/+0.06pp. Mixed signs at
small magnitude on 5 clusters: NULL on this subset. **NO FULL-COHORT PerLTQA claim** —
the remaining 25 archives were not run (budget), and subset statistics do not
generalize to the cohort.

### Quantization objective vs gold retrieval (dissociation, quantified)

- Production objective `||B−CR||_F²` decreased in 75/75 fits; mean relative reduction
  1.83% (RT, min 1.60%) / 2.32% (PQ-subset, min 2.23%) — small but uniformly negative
  direction, matching the published "decreased on all 40 archives".
- Identity check: `loss_final/haar_final` is an integer (N·96) to ≤1.5e-11 on all 75
  rows, i.e. the codex Haar objective is the same per-entry quantity
  `(sign(x)−x)² = (|x|−1)²` up to normalization — on DIFFERENT (synthetic) data.
- Interpretation: on RealTalk, minimizing the quantization objective moved bits to a
  worse retrieval frame at 5/5 inits on the production scorer. The optimizer did what
  was asked; what was asked is not retrieval.
- Novelty: NO claim. No primary literature was supplied locally or reviewed; the
  published REPORT's literature contrast was already marked not-independently-verified
  by the prior audit, and this round does not change that status.

## Interpretation

- The published RealTalk finding (ITQ ≤ random rotation on qscale; rotation harms;
  axis-aligned frame load-bearing) survives exact-protocol re-testing with varied ITQ
  inits: 5/5 paired qscale diffs negative, full-cohort, identical ties. The prior
  audit's headline survives its own methodological flaws on this bench/scorer.
- The PerLTQA half remains what the prior audit called it: a null at seed-noise scale
  — here confirmed as mixed-sign on a 5-archive subset, with no full-cohort rerun.
  "ITQ<random" must not be quoted for PerLTQA beyond the published −0.13-style null.
- The codex Haar package is a synthetic-objective replay with historical finals; it is
  consistent with "ITQ reduces training quantization error" and says nothing about
  retrieval. Citing it for/against any retrieval arm is a category error.

## Limits (what this audit does NOT establish)

- No bootstrap CIs recomputed (published 20000-rep CIs not re-verified); reported
  diffs are raw cohort means + per-archive sign counts, no significance claim.
- Convergence beyond 50 iters NOT RUN; larger relative loss reductions might change
  retrieval — unknown, not tested (changing iters would break protocol identity).
- MED arm, PerLTQA full 30-archive cohort, text-rebuild G1, and any literature review:
  NOT RUN / NOT REVIEWED (see COVERAGE.csv). No significance or generality beyond the
  stated cohorts.
- Environment: `/usr/bin/python3` 3.14.4 / numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1
  via `~/muse-work/ml-python` PYTHONPATH wrapper; single-thread BLAS flags set.
  `timeout(1)` is denied by the sandbox (RC=126), so the compute gate was adapted to
  `flock`-only serialization in `compute_local.sh` (same 180s budget; probes took
  9.7s RT + 6.4s PQ + analysis seconds; walls printed in `probe_*.log`). Cross-agent
  serialization is therefore best-effort only — disclosed.
- Originals were copied before execution (`*_ORIG.*` + sha256 above); all outputs are
  in this directory; no refs checked out, fetched, committed, or pushed; only `git show`
  reads against the main repo object store.

## Whole-project scope statement (required)

IN SCOPE (this role): sign-quantization ITQ-vs-random-rotation protocol, gates, and
the codex Haar-objective package's relationship to retrieval — RealTalk full cohort +
5-archive PerLTQA subset + synthetic-objective branch read.
OUTSIDE THIS ROLE'S SCOPE (remain for other roles / unreviewed): metric/join contracts
(01), geometry and sigma/sign-float theory (03), comparator fairness and cascades incl.
BM25/TF-IDF tokenization, candidate depth, RRF, rerank ceilings (04), F1 execution and
frozen contracts (05), dense/MRL/residual/alternate representations (06), KV/inverse
memory (07), static-storage/rank/membership cost and certificate contracts (08),
portability/clean-room (09), whole-project coverage/governance/STOP authority (10);
E1/residual theory lines, LoCoMo gold dispute, lit_r2 mappings, and any model/encoder
pre-training claims. Nothing in this report disposes those lines.

## Deliverables in this directory

`REPORT.md` (this file), `COVERAGE.csv`, `STATUS.md`, `evidence_itq.json`,
`summary_rt.json`, `summary_pqsub5.json`, `per_archive_rows_rt.csv` (220 rows),
`per_archive_rows_pqsub5.csv` (110 rows), `itq_probe.py`, `analyze.py`,
`compute_local.sh`, `probe_rt.log`, `probe_pq.log`, `analyze.log`,
`quant_math_ORIG.py`, `audit_baseline_lib_ORIG.py`, `RESULTS_ORIG.json`,
`FIDELITY_GATE_ORIG.json`, `REPORT_ORIG.md`, `exclusions_ORIG.json`.
Total items checked (mechanically summed from COVERAGE.csv): **637 reviewed** =
330 persisted per-archive rows + 90 exact gate comparisons + 36 tie-equivalence
samples + 75 verified ITQ fits + 75 objective-identity checks + 20 paired cohort
contrasts + 4 published-contrast verifications + 7 protocol-recovery items
(+2 sampled gate-contract items; 25 NOT RUN = 25 unrun PerLTQA archives).
