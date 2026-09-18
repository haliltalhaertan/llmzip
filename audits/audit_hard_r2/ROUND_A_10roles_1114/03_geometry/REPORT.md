# 03_geometry — geometry / sigma / sign-float audit (Round 2)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Outcome

Seven findings (2 framing corrections confirmed, 1 label error, 1 contract
inconsistency, 3 scope confirmations). No frozen number is changed by this
report. The load-bearing algebraic claims check out; the load-bearing
*labels* on the float reference do not; no causal mechanism for SIGN–float
gaps is established anywhere in scope.

All probes below were executed in this session (20/20 pass,
`outputs/probe_stdout.txt`, `evidence/probe_results.json`). Everything
marked NOT RUN was not run and is not claimed.

## Findings

### F1 (interpretation guardrail, CONFIRMED): sigma division cannot explain sym — theorem, not story
Severity: high if violated; status: holds.
Source: `math_r1/quant/quant_math.py:161-162` (`sigma_docs`, ddof=0,
floor 1e-12), `:170-171` (qscale), `:239-246` (C/QC centered);
`math_r1/quant/REPORT.md:24-30` (sign-invariance proof).
Performed test: T1/T2 in `scripts/probe_geometry.py` — elementwise
`sign(C/sigma)==sign(C)` and identical Hamming vectors, on fixture F1;
plus read-only scan of all 10 cached RealTalk C frames
(`scripts/sigma_scan.py`): min column std 0.0451, zero exact-zero columns.
Observed: T1/T2 pass; scan confirms the "sigma>0 everywhere" premise on
RealTalk (PerLTQA/LME not scanned — sampled, not verified there).
Interpretation: for strictly positive per-axis sigma, per-axis rescaling
preserves every code bit, so sym scores/ranks are *exactly* invariant. Any
claim that sigma scaling explains sym movement is algebraically impossible.
Limits: this cuts both ways — it also licenses nothing about *why* sym
beats/float loses anywhere. Per the brief, I do not replace it with a noise
story: the mechanism remains open (see F5).

### F2 (scorer identity, CONFIRMED): sym / asym / qscale / centered / standardized are five distinct scorers under the SAME ties
Severity: medium (conflation risk in prose).
Sources: `baseline/metrics_top10.py:34-64` (sym=-Hamming, cosine_raw,
fit_std/cosine_std, asym=D@q/sqrt96); `quant_math.py:170` (qscale);
`parallel_ideas_r1/b8/lib_b8.py:198-212` (float_raw/std).
Performed test: fixtures F1 (coherent: all six scorers agree top-3 —
agreement recorded, T3bF1/T5F1/T6F1/T6bF1), F1b/F1c (heterogeneous scales).
Observed: F1b witness docs (0,1): sym prefers doc0 (H=1 vs 2) while asym
prefers doc1 (−1.35 vs +1.45) — query magnitude matters to asym, invisible
to sym. F1b witness (0,1): sym vs qscale disagree. F1c witness (0,1):
centered cosine ranks u(0.8944) over v(0.4472) while standardized cosine
ranks v(0.9938) over u(0.1114) — sigma reweighting flips float order while
sym is untouched. F1c witness (2,4): qscale ranks w over s while asym ranks
s over w. All under one deterministic tie rule (score desc, hash, row) with
exact uniform-tie expectation cross-checked against 40k-draw Monte Carlo
(T7b: exact 1.0000 vs MC 1.0000).
Interpretation: qscale (D@(q/sigma), unnormalized) and asym (D@q/sqrt96) are
different query-weightings; both differ from sym; standardization moves float
without moving sym. Headline comparisons must name all three choices
(scorer × reference × ties).
Limits: synthetic d=2..4 fixtures; they prove distinctness, not benchmark
effect sizes.

### F3 (contract inconsistency, OPEN): two different "asym" definitions in the codebase
Severity: low–medium.
Sources: `baseline/metrics_top10.py:60-64` (`asym = D@q/sqrt(96)`,
unnormalized) vs `parallel_ideas_r1/b8/lib_b8.py:160-170`
(`cosine_from_code`, normalized by reconstruction norm) as wired in
`research_twelve_byte_pilot_2026_09_15/scripts/run_hit10.py:119`.
Performed test: source read only; not executed numerically (NOT RUN).
Interpretation: cross-report "asym" numbers are comparable only within the
same runner. Any audit joining them must re-derive, not copy.
Limits: did not quantify the numeric gap between the two defs.

### F4 (label error, CONFIRMED): the pilot "float (uncentered ref)" arm is centered-unstandardized; hr correction repeats the misnomer
Severity: medium (framing; numbers unaffected).
Sources: `research_twelve_byte_pilot_2026_09_15/scripts/run_hit10.py:122`
(float arm = `B.float_raw_scores(C, q)` on cached C);
`parallel_ideas_r1/b8/lib_b8.py:198-203` (plain cosine of inputs);
T9 probe (`bench3/runs/b3a_realtalk/rt_repr/RT01.pkl` C column-mean max
4.95e-16 — the cache IS centered, C=Y−mu per `quant_math.py:239-246`);
`HANDOFF_2026-09-15.md:48` (labels it "uncentered ref");
`_wt_top10/.../incoming_20260916b` HATA_YERI report `:154` (restored code
uses C/qC cosine; true pre-centering values measured separately as
82.77/80.48/36.45 vs labeled 82.55/80.81/36.60);
`hr/standardized-float-correction-2026-09-16` = commit `75019912`
(`FLOAT96_UNCENTERED` language).
Performed test: source read + T9 cache check + sigma/scorer reads (F1–F3
algebra corroborates that centering, unlike sigma, *does* move bits: T4
shows 6/24 bits flip under centering on F1).
Observed: the weak reference in the +10pp headline is centered,
unstandardized cosine — not pre-centering cosine.
Interpretation: the hr correction's *direction* (standardizing reverses the
comparison; float_std is a 64×-cost ceiling, not a budget competitor; raw
wins on PerLTQA en_v1/zh) stands and is consistent with my F1c flip
mechanism. But its `FLOAT96_UNCENTERED` label inherits HANDOFF's naming bug
and should read "centered, unstandardized float". The ~0.2–0.3pp true
uncentered deltas do not rescue the old headline either way.
Limits: true-uncentered values quoted from the HATA_YERI report, not
recomputed (NOT RUN); matched-protocol gapfill numbers in commit `9993f95`
(sym≈float_std, ns, under shared frozen ties) reviewed, not recomputed.

### F5 (theory scope, CONFIRMED): Model-H theorem intact; every benchmark transfer step broken or unidentified; E1 mechanism unresolved
Severity: high for any causal claim; status: no causal claim licensed.
Sources: `theory_benchmark_test_v1/PLAN.md`, `realtalk/REPORT.md`,
`lme/REPORT.md`, `audit_mapping/REPORT.md:0-3`, `audit_real_geometry/REPORT.md:0-2`,
`origin/research/e1-*` bridge/V2/checkpoint reports.
Performed test: source read (no new benchmark runs).
Observed: LOW48-as-nuisance proxy falsified/unsupported — LME −6.44pp
(CI excl. 0, wrong sign), RealTalk −0.09pp (inconclusive),
PerLTQA +2.46pp, LoCoMo −2.58pp conditional on substituted baseline;
HIGH48 is an algebraic mirror (reciprocal identity maxdiff 0.0), not
independent evidence; joint-scaling math differs from Model H (t² numerator,
query varied, unequal doc norms); exact rational counterexample to
uniform monotonicity exists in `audit_mapping/verify.py`. E1 checkpoint
(§8) states the load-bearing V2 metrics (PHI_GAP/EFFDIM_GAP/duplicate-code/
query-magnitude/strictly-closer-rival gaps) were NEVER run — caches missing,
refit forbidden. P64 (BOT−TOP polarity) is a weak query-level correlate
(rho ≈ +0.08–0.11) and a regime marker at aggregate level, explicitly not a
predictor or cause; archive-only geometry is refuted as sufficient (22/30
character flips hold archive fixed).
Interpretation: distinguish (a) conditional synthetic theorems — intact,
(b) proxy/transfer hypotheses — tested and failed/inconclusive,
(c) numerical corroboration — existing arms only, (d) mechanism — open.
The older representation/E1 theory explains no benchmark gap today.
Limits: relied on coordinator/worker recomputations (e.g. −6.44326pp);
verified identities/inequalities quoted, not re-executed, except T10.

### F6 (old mathematics, CONFIRMED with standing blocker): norm_math D1–D7 defects real; rank_cert repair still REQUEST_CHANGES at package level
Severity: high for certification use; low for retrieval claims.
Sources: `findings/representation-geometry-2026-09-13` = `75b7e057`:
`repairs/norm_math/proofs_exact.py`, `WITNESSES.json`,
`CORRECTIONS_NORM_MATH_TR.md`, `AUDIT/poc_bulgu1.py`;
`representation_geometry_fix/COORDINATOR_VERDICT_V3.md`.
Performed test: T10a/b/c re-verify D1 (m=0 face witness: unit, in-F,
score 0, both axes outside F), D3 (rho support [1/sqrt(d),1]; rho=−0.3
impossible), D4 ([0.5,1] closed, q·e1=1/2) in exact Fractions — all pass.
BULGU-1 PoC read, not executed (needs worker modules — NOT RUN).
Observed: original axis-attainment rule wrong at m=0, d=2 table flags 4/8
wrong (values right), rho support unstated, interval open at 0.5, D5 claims
retracted, 1e-12 "certified" language not a certificate. v3 candidate passes
the frozen adversarial bar + independent 684-case oracle per coordinator
verdict, but the published package disposition stays REQUEST_CHANGES and
only BULGU-1/5 are addressed (BULGU-2/3/4/6/7/8, F-01..F-07 open).
Interpretation: use norm_math corrections; do not use `certify_v2.py` for
anything; v3 is a review candidate, not an accepted repair.
Limits: same-family independence only throughout (stated in the branch
README itself); no different-family review exists.

### F7 (minor contract note): sigma zero-floor conventions differ between runners
Severity: low (latent).
Sources: `quant_math.py:162` (floor 1e-12) vs `metrics_top10.py:47-51`
(zero→1.0). T8 pins both behaviors; sigma scan finds no exact-zero column
in RealTalk caches, so currently harmless there.
Limits: PerLTQA/LME not scanned.

## What was NOT run (not passes)

BULGU-1 PoC execution; E1 V2 joint-geometry metrics (caches unavailable);
matched-protocol gapfill recomputation (`9993f95`); PerLTQA/LME sigma scans;
any embedding/model/benchmark run; any full-cohort statistic; literature
verification (no primary sources supplied locally — novelty claims NOT
VERIFIED by this role).

## Whole-project scope outside 03_geometry

This role covers geometry/sigma/sign-float algebra, the standardized-float
framing, Model-H/E1 transfer status, and the round4 norm/rank-cert
mathematics. Everything else — metric tie-contract joins and bootstrap
units (01), ITQ-vs-random with matched ties (02), comparator/cascade and
rerank ceilings (04), F1 execution/contracts (05), dense/MRL/residual lines
(06), KV/inverse-memory (07), storage/rank-membership certificates and cost
accounting (08), clean-room portability (09), whole-project coverage and
STOP authority (10) — is outside my scope and I make no claim about it.
Same-CLI agents give only partial independence; prior reports were treated
as fallible and every load-bearing algebraic point above was re-derived.

## Totals (mechanically counted)

- `COVERAGE.csv`: 30 rows = 20 REVIEWED + 2 SAMPLED + 2 VERIFIED-PROBE + 6 NOT RUN.
- Executed checks: 20/20 probe checks PASS (`evidence/probe_results.json`) + 10-archive sigma scan (`evidence/sigma_scan.json`).
- Total items checked (ledger rows + executed checks): 30 + 21 = 51; the 6 NOT RUN rows are blockers/gaps, not passes.

## Provenance

Read-only sources listed in COVERAGE.csv; branch files via `git show`
against `REFS_BEFORE.txt` refs (`75b7e057`, `75019912`, `9993f95`
observed post-start as the checked-out HEAD content). Originals copied to
`scripts/*_COPY.py` before execution; all outputs under this directory.
Env: `/home/mdp/muse-work/ml-python` (Python 3.14.4, numpy 2.5.3),
`PYTHONDONTWRITEBYTECODE=1`, single-thread BLAS. `compute.sh` could not be
used (its lock file is on a read-only path — `flock: cannot open lock
file`); probes are kilobyte-scale numpy fixtures plus two small cache
reads, run directly, each well under 180 s.
