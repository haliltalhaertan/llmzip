# 01_metrics — HARD REVIEW ROUND 2 REPORT

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Neutral audit of metric implementations and joins. Prior round (`audit_hard_r1/numbers`, 101 rows, 100% match) is treated as fallible, not ground truth. This round does NOT redo those 101 checks; it recomputes load-bearing selected comparisons with exact source tie rules, adds harmless numeric fixtures for test/gate mismatch, and writes a coverage ledger. Datasets covered: RealTalk (primary) plus PerLTQA, LME, LoCoMo via the stored T2 rerank CSV.

## Outcome

Numbers recomputed here reproduce (41 EXACT, 3 CLOSE within Monte-Carlo noise, 62 ledger rows total). The findings are about **what the tests actually implement versus what the gates document**, one mislabeled published column, and comparator-definition ambiguity — not about arithmetic errors in the headline estimates. Two published artifacts make claims that are **no longer supported** as stated (F1, F2 below); three documented gates are **untestable** from the built artifacts (F3).

## Findings (severity-ranked)

### F1 [HIGH, test/gate mismatch] — T1 code does not implement documented C1

- Location: published `coordinator/decision_tests.py:168-175` (copied to `orig/decision_tests.py.txt:168-175`).
- Documented gate (`orig/DECISION_TESTS.json` "gates", `orig/DECISION_TESTS.md:6`, referee §5 C1): some arm ≤48 B beats fair BM25 by ≥ +2.0 pp **FR@3, CI excluding zero, on BOTH benchmarks**.
- Implemented: `C1_gate_plus2pp_fr3 = any(vs_strongest_fr3 >= 2.0)` — point estimate only, no CI, RealTalk only. `strongest_bm25` is selected on **Hit@10** (`max(...hit10)`, line ~160) while the gate is on FR@3 (same winner here, so unobserved risk, not an observed flip).
- Performed test: harmless fixture `scripts/p1_fixtures.py` F4 — synthetic 10-cluster paired diff with point +2.78 pp and CI [-8.06, +13.63]. Code-style check returns PASS; documented-style check returns FAIL (`out/p1_fixtures.json`).
- Observed: the shipped `verdict.C1_gate_plus2pp_fr3=false` happens to agree with the documented reading (all six code-vs-strongest gaps are negative), so no verdict flips on current data — but the variable must not be quoted as the gate outcome.
- Interpretation: any future or re-scored comparison near the +2.0 boundary needs the CI+both-benchmarks implementation; the current code cannot produce it.

### F2 [HIGH, data integrity] — published `expected_hit_at_10` (producer) is expected recall, not expected hit

- Location: published `data/run_lexical.py:55-76` (copied to `orig/run_lexical.py`); values shipped in `data/lexical_summary.json` and `data/per_query*.jsonl`.
- Contract: `orig/PROTOCOL.md:6` requires "exact expected Hit@10 under uniform ties as tie-sensitivity".
- Performed tests: (a) CE fixture from the audit's own `orig/test_expected_hit.py` rerun in own code (`scripts/p1_fixtures.py` F2 + brute-force permutation oracle): correct any-gold probability 0.7, brute 0.7, producer formula 0.4 = `(take·gb/B)/|gold|`. (b) Full-column quantification over published `audit/per_query_bm25_corrected.jsonl` (n=705): mean corrected 0.541844 == deterministic Hit@10; mean producer 0.431599 == Recall@10; 129/705 queries differ per-query (all multi-gold, max abs 0.95); 678/705 have no tie at the cut.
- Observed: `orig/lexical_summary.json` carries `expected_hit_at_10` bit-identical to `recall_at_10` on both arms (recomputed in `out/p2_realtalk_denominator.json`).
- Interpretation: the producer column cannot be cited as the PROTOCOL tie-sensitivity measure. Mitigations already in the pilot: the audit layer ships `expected_hit_at_10_corrected` alongside `expected_hit_at_10_producer`, and no gate (C1/C3/S3) consumes the producer column, so gate verdicts are unaffected. Tie-sensitivity at the mean level on this BM25 arm is nil (0.000000 gap), but that is arm-specific: continuous BM25 scores tie rarely (27/705 at cut), while discrete Hamming code arms tie pervasively and their expected-hit was never published (NOT RUN X05).

### F3 [MEDIUM, scope] — documented C1 / C2 / C3 are untestable from built artifacts

- C1 "both benchmarks": T1 builds fair BM25 on RealTalk only; no PerLTQA-corrected fair-BM25 run exists (T3 has codes but no BM25 arm — checked `coordinator/T3_PERLTQA_KLTN.json` arms qscale/sym/asym only).
- C2 Hit@10 guardrail CI: `decision_tests.py` computes CIs only for FR@3 contrasts; no Hit@10 CI exists anywhere in `DECISION_TESTS.json`.
- C3 on PerLTQA-corrected: T2 PerLTQA is the full uncorrected 8265-query set; T3 (corrected 2217) has no rerank/BM25 arms.
- Interpretation: STOP/CONTINUE readouts against C1–C4 as literally documented require new runs (PerLTQA-corrected fair BM25; Hit@10 CIs), not re-reads. The published FAILs rest on RealTalk-T1 points and uncorrected-T2 CIs.

### F4 [MEDIUM] — four BM25 numbers circulate under one name

- `out/p2_realtalk_denominator.json` comparator table: PROTOCOL BM25 (k1=1.5, Unicode-word) 54.18; decision coarse-textbook (k1=1.2, `[a-z0-9]+`) 55.32; frozen-textbook 61.70; frozen-idfonly 65.67. Each reproduces within its contract; cross-quoting without the contract label is unsupported.
- The "-10.35 pp correction" headline is Hit@10-specific: the same pair on the gate metric FR@3 is +6.12 pp (`metric_divergence`). REPORT §1's "BM25 beats uncompressed by 5.67 pp" uses yet another (PROTOCOL 54.18) baseline. Rank agreement (frozen_idfonly top on both metrics) held here, but T1's select-on-Hit@10/test-on-FR@3 pattern is a standing hazard.

### F5 [MEDIUM] — bootstrap cluster unit is inconsistent; 10-cluster CIs are coarse by construction

- `out/p3_t2_second_dataset.json`: LME 470 clusters of size 1 (archive==query → clustering is a no-op, i.i.d.-equivalent); LoCoMo 10 archives (sizes 81–197); PerLTQA 30 archives (202–409). Same "archive-clustered" label, different effective units — CI widths are not comparable across datasets.
- Own re-seed check (2000 reps, seed 777 vs published 20000/20260916): levels and point estimates EXACT (0.0 diff, all 3 datasets, rowcount 164256); CIs within 0.02 pp; all sig/C3 verdicts agree. Explicit verification, not a refutation: verdicts are seed-stable, but with 10 clusters the percentile bootstrap has only 10 effective units — the pilot's own `firststage.py` labels these "wide CIs, exploratory", and PROTOCOL likewise says "10 clusters limited, exploratory, no unseen certification".
- `_rrf60` T2 levels exist but have no CIs in `DECISION_TESTS.json` (NOT RUN X01); the REPORT §4 RRF CI [+3.23,+8.20] comes from the firststage pool-Hit@100 estimand, a different metric from the FR@3 gate.

### F6 [MEDIUM] — multiplicity: 13 SIG / 23 ns labels, no correction anywhere

- Mechanically counted in REPORT.md (6 explicit CI brackets); 15 T2 contrasts + 6 T1 arms in `DECISION_TESTS.json`; band-level SIGs (e.g. IDF_p2 rare-band +4.78 [+0.69,+8.43]) are post-hoc subgroup contrasts. REPORT carries the three required caveats for IDF^p; the structural point stands: only C1/C3/S3 were prespecified, everything else is exploratory whether or not it prints SIG.

### F7 [LOW] — tie determinism caveat already disclosed; denominator inheritance

- `firststage.py:411-460` (G6): reference BM25 sums over `set(q_tok)` (PYTHONHASHSEED-dependent); 1-ulp noise flips a true 3-way tie cut (RT01_q016, 704/705 match, zero metric impact); primary uses sorted-term order. The sha256 tie-break is deterministic conditional on scores; scores themselves need a deterministic summation convention — disclosed, no action beyond citing it with the contract.
- Denominator: raw `top10_comparison_r1/data/RT*.json` holds 705 queries total (already valid-only); per-archive 85/70/73/71/70/74/70/70/63/59 all mappable (D03–D12 EXACT). The 728→705 exclusion step is consistent (`exclusions.json`) but cannot be re-derived from the export — any "from raw" rerun silently inherits the 23 exclusions. 54.75% of valid queries are multi-gold, which is why Hit@10/Recall@10/FR@3 joins diverge (stored Recall@10 43.16 vs Hit@10 54.18).
- Seed/reps drift PROTOCOL (2000/s20260915) vs decision (20000/s20260916) is documented in each file; my re-seed run shows verdict stability.

## Claims no longer supported (as stated)

1. Any citation of `data/lexical_summary.json` or `data/per_query*.jsonl` `expected_hit_at_10` (producer) as "exact expected Hit@10 under uniform ties" — it is expected recall (F2). Use `audit/per_query_bm25_corrected.jsonl:expected_hit_at_10_corrected`.
2. `DECISION_TESTS.json:T1_fair_baseline:verdict:C1_gate_plus2pp_fr3` as the documented-C1 outcome — it is a point-only single-benchmark proxy (F1).
3. Unqualified "tokenizer choice is worth +10.35 pp" / "honest BM25 is 65.67" without metric + selection caveats: +10.35 is Hit@10-only (+6.12 on FR@3), best-of-4 in-sample, selected on Hit@10 (F4).
4. "Archive-clustered bootstrap" as a uniform precision claim across LME/LoCoMo/PerLTQA (F5).

## Totals (mechanically counted from COVERAGE.csv)

62 rows: EXACT 41 | CLOSE 3 (T2 CIs within 0.02 pp under changed seed/reps; verdicts agree) | MISMATCH 1 (D21 producer column) | REVIEWED 10 (contracts/methods read, not recomputed) | NOT RUN 7 (X01–X08). No not-run check is presented as a pass. No numeric estimate checked here was refuted; mismatches are test-vs-gate and label-vs-formula.

## Limits and blockers

- `compute.sh` could not be used: its `flock` lock file path is on a read-only filesystem (`touch .../compute.lock: Read-only file system`). All probes here are light (CSVs ≤18 MB, fixtures, aggregations; each well under 180 s) and ran directly with the mandated single-thread env (`PYTHONDONTWRITEBYTECODE=1`, `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `~/muse-work/ml-python`); recorded in `out/evidence_metrics.json`.
- No model downloads, no external APIs, no SVD recomputation, no source writes (originals copied to `orig/`; outputs to `scripts/` + `out/`).
- Whole-project scope outside this role: ITQ/rotation protocols, geometry/sign-float theory, comparator fairness beyond BM25 definitions, F1 execution, dense-MRL/residual lines, KV/inverse work, storage/rank contracts, portability clean-room, and governance/whole-project coverage (roles 02–10). Within metrics, NOT RUN items X01–X08 (notably code-arm tie-sensitivity and PerLTQA-corrected fair BM25) remain for follow-up.

## Files

- `REPORT.md` (this file), `COVERAGE.csv` (62 rows), `STATUS.md`
- `orig/`: PROTOCOL.md, DECISION_TESTS.md, REPORT.md, COORDINATOR_NOTES.md, lexical_summary.json, exclusions.json, DECISION_TESTS.json, audit_baseline_lib.py, test_expected_hit.py, run_lexical.py, decision_tests.py.txt
- `scripts/`: p1_fixtures.py, p2_realtalk.py, p3_t2.py
- `out/`: p1_fixtures.json, p2_realtalk_denominator.json, p3_t2_second_dataset.json, evidence_metrics.json
