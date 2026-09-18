# 06_dense_residual — dense-MRL, residual and alternate-representation audit (Round 2)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independent hard review, not a repair task. Neutral: neither STOP nor CONTINUE is the target.
Prior agent/coordinator reports are treated as fallible claims, re-checked from files.
All probes ran on copies in this directory; no source ref, branch, or worktree was modified.
No credentials, external API charges, model downloads, or exploit workflows were used.

Environment: `/usr/bin/python3` single-thread BLAS (`OMP/MKL/OPENBLAS_NUM_THREADS=1`,
`PYTHONDONTWRITEBYTECODE=1`). Blocker: `audit_hard_r2/compute.sh` could not run —
its `flock` lock file is on a read-only filesystem (`touch .../compute.lock` →
`Read-only file system`). The two probes below are tiny (≤6×96 synthetic arrays;
read-only reaggregation of stored JSONL) and were run bounded directly instead.
No huge recomputation was attempted; each probe ran in seconds (limit ≤180 s).

Coverage: **26 items checked — 14 REVIEWED, 8 SAMPLED, 4 NOT RUN** (mechanically counted
from `COVERAGE.csv`, header excluded). NOT RUN items are listed as such, never as passes.

## 1. Inventory — complete raw outcomes per line (before any experiment)

| line | raw outcome location | headline numbers (as reported; verification in §3) |
|---|---|---|
| dense-MRL parity | branch `findings/dense-mrl-parity-2026-09-14` (commit `36c7bf0`), `research_dense_mrl_parity_2026_09_14/{README,measurement/*.json,OLCUM_RAPORU_TR.md,audit/}` | 3 arms on LongMemEval corpus, parity pipeline. Same-axis-fraction (1/8): lexical 35.66% (2.85× null) vs best dense (arctic-m-v1.5) 20.65% (1.65×). 48-bit question: best dense f48=10.61% vs lowest threshold 17.83% (margin 7.2 pp). MRL ordering real (pB +0.3292 vs −0.0169 control; f48 enrichment 1.70× vs 0.97×) but spectrum flatter (0.329 vs 0.861). Audit FAIL-FIXABLE → 4 repairs; "alignment" metric withdrawn. Proxy only, not retrieval. |
| sign96-nanobeir | `refs/remotes/origin/bench/sign96-nanobeir-sweep-2026-09-14` (commit `ead53ec`), `reports/SIGN96_NANOBEIR_RUN_34866074513.md` | 13 NanoBEIR tasks, 649 q, 56 723 docs. SIGN96−FLOAT96 macro Recall@3 **+2.472 pp** (W8/T0/L5), nDCG@10 +1.770 pp. Outliers: SciFact +18.1, Quora +9.03, HotpotQA +7.2; reversals ArguAna −5.7, NQ −3.0. Licensed as regime-dependent, not universal. |
| micro-residual | `refs/remotes/origin/bench/sign96-micro-residual-2026-09-14` (commit `95ec9a1`), `reports/SIGN96_MICRO_RESIDUAL_NANOBEIR_RUN_34886350705.md` + frozen `benchmarks/sign96_micro_residual_2026_09_14/PROTOCOL.md` | Frozen primary SIGN96_R8 (96+8b): Recall@3 +0.113 pp vs SIGN96, nDCG@10 +0.478 pp (10/13 tasks). Boundary-tie rate 39.7%→14.5%; exact-code collision only 2.233%→2.216%. R16 worsens Recall@3 (−0.144 pp) despite 9.4% ties. SciFact has zero collision yet +18.1 pp SIGN gain (R8 reduces it 1.0 pp) — collision-only explanation falsified in-report. |
| heavy wave | `refs/remotes/origin/bench/sign96-heavy-retrieval-2026-09-14` (commit `94c5e7a`), `reports/SIGN96_HEAVY_WAVE_STATUS_2026-09-14.md` | BRIGHT (861 q): Recall@3 −0.205 pp (4/0/4). BIRCO (410 q): −0.818 pp (1/1/3, WTB +2.6 exception). Full BEIR scientific: SciFact +1.924 (vs Nano +18.1, direction kept, magnitude collapses), ArguAna −2.405, SCIDOCS −0.103, NFCorpus +0.079. FiQA/TREC-COVID: infra failures, explicitly unlicensed. |
| residual8_pilot_r1 | `llmzip-work/residual8_pilot_r1/` (`PROTOCOL.md`, `PROSPECTIVE_SNAPSHOT.json`, `perltqa/` 8265-row `per_query.jsonl` + 30 ckpts + `state_*.npz`, `coordinator/FINDINGS.md`, `ORACLE_COORDINATOR_REVIEW.md`) | PerLTQA gate PASS (maxd 0.0). MAG8−BASE +0.481 pp (95% CI excl. 0); MAG8−SIGN_ONLY8 +0.049 pp (CI incl. 0; ~90% of lift is sign reweight). Tie headroom only +1.68 pp vs FLOAT gap +6.27 pp. LME −0.057 pp, RealTalk +0.072 pp (both CI span 0). Oracle v1 REJECTED; repair pending. |
| asymmetric (parallel_ideas TASK A) | `llmzip-work/parallel_ideas_r1/asymmetric/` (`REPORT.md`, 470+8265+705 ckpts) | asym=float-query cosine vs ±1 doc signs. PerLTQA asym−base +4.63 pp; LME −3.56 pp; RealTalk −2.49 pp (sign flips by benchmark). float_std best everywhere. Gates PASS; 18/18 green + red mutations. |
| B8 (parallel_ideas TASK B) | `llmzip-work/parallel_ideas_r1/b8/` (`PROTOCOL.md`, `lib_b8.py`, 9440-row `per_query.jsonl`, `REPORT.md`) | Fixed 96-bit (88 signs + 8 mag flags), 12 B payload. B8−asym: PerLTQA +0.00058 (CI spans 0), LME −0.02436, RealTalk −0.02214. B8−sym gain fully explained by float-query scoring (ASYM−SYM +0.046), not reallocation. |
| next_route_round1 | `llmzip-work/next_route_round1/` (`COORDINATOR_DECISION.md`, fair-contest/literature-fidelity/storage-accounting) | No new retrieval outcomes. Direction retained; DESIGN REJECTED AS EXECUTION-READY. Blocks: reversed promotion inequality, unjustified 2 pp margin, hash-split ≠ unseen data, multi-challenger inference, rounded-mean replay ≠ 1e-12 gate, PQ mislabelling, "ceilings" language, interpreter-scoped lib claims. Xiao paper: local test is NOT faithful 2-bit reproduction (median-per-axis vs mean-abs; equal-Hamming vs weighted product); Corollary 3 scope withdrawn. |
| published STOP | `_wt_top10/research_top10_comparison_2026_09_16/` (`REPORT.md`, `FINAL_STATE.md`, `DECISION_TESTS.md`) | Gates C1 (≤48 B beats fair BM25 ≥2 pp both benches) FAIL (−7.80 pp); C3 (code+rerank ≥1 pp) FAIL; S3 did not fire (asym rises). Verdict STOP scoped to the TF-IDF/SVD 12-byte-vs-BM25/rerank programme. Five retractions preserved. |

Two method families must not be conflated: micro-residual selects axes by `Var(|C|)` with
`>=` median bits and unweighted residual-Hamming tie-break; residual8_pilot selects axes by
top-8 `Var(C)` with strict `>` median bits and weighted signed-product tie-break. Different
residuals, different tie-breakers, both lexicographic (tie-only).

## 2. Findings (severity, location, test, result, interpretation, limits)

### F1 [medium] Packed-byte budgets are correct as *active-code minima* — but are not system costs
- Location: micro `PROTOCOL.md` budget table; micro report Boundaries; `residual8_pilot_r1/PROTOCOL.md:Payload`;
  `parallel_ideas_r1/b8/REPORT.md:Costs`; `asymmetric/REPORT.md:Cost`.
- Test performed: arithmetic probe on copies (`scripts/t_probe_synth.py`, `outputs/t_probe_synth.log` T1):
  `(bits+7)//8` gives 96→12, 100→13, 104→13, 112→14 B; plus `packbits/big-endian` roundtrips
  (`lib_residual8.encode_archive` → `[N,13]`; `lib_b8.encode_docs` → `[N,12]`) on 5×96 synthetic docs.
- Observed: PASS. All four reports explicitly disclaim whole-system cost
  ("active-code sizes only"; "TF-IDF/SVD pipeline and text/IDs outside payload";
  residual8 discloses 72 B content shared + `.npz` container overhead 184 644 vs 161 904 B;
  B8 discloses 80 B/archive shared).
- Interpretation: no whole-system 12/13-byte claim was found in these lines. Any citation must carry
  the shared-state + pipeline + index/text qualifier.
- Limits: shared-state accounting is content-bytes (`nbytes`), not serialized deployment bytes;
  per-archive vs per-system amortization is not modelled. Micro `run_micro_residual.py` packing path
  not re-executed (NOT RUN id 12).

### F2 [high] Tie-only constraint holds in code — residual cannot overturn a strict base-Hamming lead
- Location: `copies/lib_residual8.py:13-15,152-193` (`STRIDE_MAG8=65`, `STRIDE_SIGN8=17`, `STRIDE_RAND8=9`);
  micro `PROTOCOL.md:Ranking rule`.
- Test: stride-bound check + brute-force non-inversion on 6-doc synthetic
  (`outputs/t_probe_synth.log` T2/T2b). Residual ranges are [−32,+32]/[−8,+8]/[0,8]; strides exceed
  each range width, so `-H*stride+resid` is a faithful lexicographic encoding.
- Observed: PASS — for every pair with `H[i]<H[j]`, `score[i]>score[j]` under both MAG8 and SIGN_ONLY8.
- Interpretation: both residual lines test *Hamming-tie resolution only*, by construction. Their
  deltas (+0.11 pp micro; +0.48 pp residual8, of which +0.43 pp is sign reweight) are correctly read as
  tie-recovery effects, and the coordinator's tie-headroom bound (+1.68 pp < FLOAT gap +6.27 pp) is the
  right ceiling for this design class. A residual allowed to reorder distinct Hamming distances would be
  a different (untested here) method.
- Limits: synthetic fixture only; full-corpus replay not rerun (coordinator already replayed all 8265
  packed payloads with maxdiff 0.0 — cited, not repeated).

### F3 [high] Query-scoring asymmetry: residual8 uses a quantized 8-axis query channel; asym/B8 use full float queries
- Location: `copies/lib_residual8.py:109-124,152-168` vs `copies/lib_b8.py:160-195`
  (`asym_sign96_scores`, `b8_scores` → `cosine_from_code(R, q)` with float `q`).
- Test: signature/source inspection + fixture (`outputs/t_probe_synth.log` T3). Residual8 `mag8_scores`
  accepts only `(packed, encoded_query, axis_map)` — no doc floats; query enters via packed 96 signs +
  8-axis `(s8, m01)`. Asym/B8 take the full 96D float query vector.
- Observed: quantizing the fixture query flips asym scores
  (`[-0.2722, 0.2722]` → `[0.3333, -0.3333]`) while Hamming is unchanged (`[1, 2]`) — asym/B8 consume
  float query precision; symmetric Hamming does not.
- Interpretation: asym/B8 are **not code-only on the query side**. Doc storage stays packed (12 B),
  but scoring needs the float query + decode path (B8/asym reports disclose query workspace; asym
  reports `768 B float query + transient N×8 score`). Deployment comparisons against code-only query
  paths must price this. Residual8's query channel is narrower (8 axes) but still float-derived at
  encode time — allowed by its protocol ("query float state is allowed and reported"), correctly
  distinguished from doc-float leakage (none: scorer signature excludes `C`).
- Limits: no latency/energy measurement was made; "FLOAT oracle access" here means query-time float
  use, not qrel/gold leakage (none found — see F5).

### F4 [medium] Seed selection is clean at the global level; per-query-max reporting would inflate by ~1.6 pp
- Location: `copies/constants.json` (20 seeds `62001..62020`, bootstrap 63001×2000);
  `residual8_pilot_r1/perltqa/per_query.jsonl:random8[20]`; micro report "20 deterministic SHA-256
  nuisance priorities".
- Test: independent reaggregation (`scripts/t_reaggregate.py`, `outputs/t_reaggregate.log`).
  PerLTQA means reproduce worker/coordinator to 15 decimals
  (BASE 0.488944796163641, MAG8−BASE +0.481294 pp, MAG8−SIGN8 +0.048917 pp);
  RANDOM8 seed-mean 0.48884477, best *global* seed idx0 (=62001) 0.48986852 — matches the worker's
  "best seed (62001)". Per-query-max mean is 0.50571091, i.e. **+1.5842 pp above best-global**.
- Observed: the PerLTQA worker used the correct global-seed figure. The coordinator's correction stands:
  preservation workers' "best seed" means of per-query maxima (LME 0.56500 / RT 0.23904) are
  gold-dependent oracle selections, not deployable baselines; correct best-global seeds are LME 62020
  (0.54741135) / RT 62004 (0.22932568) per `FINDINGS.md`.
- Interpretation: no cherry-picked seed was deployed in the primary contrasts. Any future citation of a
  "best seed" number must use the global-seed value; per-query-max values are diagnostic oracle bounds.
- Limits: RNG substream construction differs between producers (frozen plan fixed labels, not stream
  mapping) — panels are independent diagnostics, not paired draws (per coordinator; not re-tested here).

### F5 [low] No qrel/gold or query-fit leakage found in the residual fit paths
- Location: `copies/lib_residual8.py:78-97` (`select_axes(C)`, median over `|C|` docs-only);
  `copies/lib_b8.py:87-109` (`fit_archive(C)`); micro `PROTOCOL.md:Residual construction` + `Outcome-blind boundary`.
- Test: signature inspection (`outputs/t_probe_synth.log` T5/T5b) — neither `select_axes` nor
  `fit_archive` accepts query/gold; thresholds are corpus-median statistics; `encode_query` consumes
  stored thresholds. Micro protocol freezes rankings + SHA-256 *before* qrels load; residual8 gates
  require 1e-12 baseline replay before candidate outcomes (reported PASS, maxd 0.0).
- Observed: PASS on inspected code paths. Document-fit axis/threshold selection is disclosed as
  document-fitted (not "unsupervised-novel"), queries never fit.
- Interpretation: the residual gains cannot be attributed to test-label fitting on the inspected paths.
  Adaptive reuse across pilots (same PerLTQA/LME/RealTalk cohorts re-examined) remains — correctly
  labelled exploratory, never confirmatory.
- Limits: corpus-side provenance (cache hashes) and Actions-side freeze hashes were read from reports,
  not re-hashed here; micro ranking code not re-executed (NOT RUN id 12).

### F6 [medium] Dense-MRL verdict is a *proxy* verdict (variance share), not a retrieval verdict — and it is scored correctly as such
- Location: branch README + `measurement/measure_mrl_parity.py:1-60` + `MRL_PARITY_*.json` aggregates.
- Test: read parity code head (verbatim `loglog_fit`/`archive_texts_only`, row-L2→center→`var(ddof=0)`,
  `p=-slope`); synthetic `p` convention check + 1/8 null arithmetic (`outputs/t_probe_synth.log` T6:
  96/768 = 12.50%, matches reported nulls 12.49–12.51%); JSON aggregate cross-read
  (arctic-m f96 20.65%, mxbai f128 12.60%, control f48 12.10%).
- Observed: the closing numbers are internally consistent; the report's own boundary ("variance share is
  not retrieval … the hybrid was not proven useless for retrieval") is honoured in text.
- Interpretation: "the front closes" means *the pre-declared proxy criterion was not met* — correctly
  scoped. The MRL-positive control (nominal ordering present, enrichment 1.70× vs 0.97×) prevents the
  misreading "MRL failed"; the spectrum-flatness reading (0.329 vs 0.861) is the licensed one.
- Limits: embeddings not recomputed (no downloads; declared re-fit; NOT RUN id 05); per-archive rows and
  the Turkish report `OLCUM_RAPORU_TR.md` §6b/§9/§11 plus full `MUSE_DENETIM_V55.md` not reopened beyond the
  README table (SAMPLED ids 02–04). Same-model-family partial independence stands as stated.

### F7 [info] Residual dose-response is non-monotonic and benchmark-fragile — the reports already say so
- Evidence: micro R16 lowers Recall@3 (−0.144 pp) while cutting ties to 9.4%; residual8
  MAG8−SIGN_ONLY8 spans zero (+0.049 pp); B8≡asym on PerLTQA but loses on LME/RealTalk; asym itself flips
  sign across benchmarks (+4.6 / −3.6 / −2.5 pp); Nano→full SciFact shrinks +18.1→+1.9 pp.
- Interpretation: these are tie-resolution micro-effects with no demonstrated general law. The micro
  report's "naive global-median residual is not a universal cure" and residual8's "not justified over
  SIGN_ONLY8" dispositions are the correct, non-overclaimed readings. Verified reaggregation
  (`outputs/t_reaggregate.log`: B8−asym +0.000583/−0.024362/−0.022140, matching REPORTs) supports them.

## 3. Explicit verification (repeated results, labelled as such)

- **V1 — residual8 PerLTQA means**: recomputed from stored `per_query.jsonl` (8265 rows) with independent
  summation: BASE 0.488944796163641 / SIGN8 0.493268569120851 / MAG8 0.493757734339849 /
  FLOAT 0.551692074528852 — digit-identical to worker/coordinator values. (`outputs/t_reaggregate.log`)
- **V2 — B8 means**: recomputed from stored `per_query.jsonl` (9440 rows): PerLTQA sym .488945 / asym
  .535251 / b8 .535834; LME sym .542134 / asym .506489 / b8 .482128; RealTalk sym .225535 / asym .200596 /
  b8 .178456 — all match REPORTs to 6 decimals. (`outputs/t_reaggregate.log`)
- **V3 — seed mapping**: best-global RANDOM8 index 0 ⇔ seed 62001 (via `constants.json` order), value
  0.489868517012778 — matches worker "best seed (62001)". Per-query-max inflation +1.5842 pp demonstrated.
- No other existing result was repeated. Gate replays (1e-12), packed-payload reload rescores, and
  bootstrap CIs were cited from reports, not recomputed.

## 4. Byte-budget, oracle-access, seed, tie, leakage checklist (per line)

| check | micro-residual (NanoBEIR) | residual8_pilot | asymmetric | B8 | dense-MRL |
|---|---|---|---|---|---|
| packed active bytes | 12 / 13 / 13 / 14 for 96/100/104/112 b — verified arithmetic (T1) | 13 B `[N,13]` + 72 B shared content — roundtrip verified (T1b) | 12 B doc payload; float query disclosed | 12 B `[N,12]` + 80 B shared — verified (T1c) | n/a (variance proxy, no code) |
| code-only query? | yes both sides (signs + residual bits from corpus thresholds) | query quantized to 8 axes (float-derived, protocol-allowed) | **no** — full float q | **no** — full float q | n/a |
| doc FLOAT at score? | no (lexicographic Hamming) | no (signature excludes C; T3) | no (sign reconstruction) | no (reconstruction from packed) | n/a |
| seed handling | 20 SHA-256 nuisance priorities (tie-break) | 20 fixed seeds; mean + global-best reported; per-query-max corrected | cluster bootstrap seed 20260915 (descriptive) | same bootstrap | isotropic null seed 20260914 |
| tie rule | lexicographic (−H96, resid-H, SHA-256); exact expectation | lexicographic via stride; exact fractional expectation (T2) | exact FR/nDCG expectation | exact FR/nDCG expectation | n/a |
| gold leakage | qrels after frozen rankings (protocol; not re-run) | gates + no-query-fit (T5); oracle bounds diagnostic only | gates PASS (cited) | gates PASS (cited) | no retrieval computed (sealed T4F1) |

Convention difference preserved: micro magnitude bit is `|C| >= median`; residual8 is strict `|C| > thr`.
Both are disclosed; they are not the same residual.

## 5. Limits of this audit

- No embedding, ranking, or bootstrap recomputation beyond the two reaggregations and synthetic probes.
  Dense-MRL per-archive rows, Actions artifacts/digests, micro ranking source, oracle_repair, hit10/inverse/kv
  contents, and next_route storage/literature evidence files were not re-executed (see COVERAGE.csv NOT RUN).
- Same-CLI partial independence only (per task brief).
- `compute.sh` serialization unavailable (read-only lock); substitutes were bounded single-thread runs.
- Time-boxed (~40 min); partials preserved with exact blockers above.

## 6. Can the TF-IDF/SVD STOP dispose these lines? (logic)

No — with one scoped exception. The published STOP (gates C1/C3/S3) adjudicates a specific programme:
*TF-IDF/SVD 12→48 B codes vs fairly-built BM25 and vs code+rerank pipelines*. Its deficit scale is
7–16 pp. The lines audited here are logically separate from that adjudication:

1. **Dense-MRL is a different representation family** (dense embeddings, variance-share proxy, no BM25
   comparator, no retrieval measured). STOP neither supports nor weakens it; its own proxy verdict stands
   independently and explicitly disclaims retrieval scope.
2. **Residual/asym/B8 lines do not contest the STOP gates.** Their observed deltas (+0.11 pp micro R8;
   +0.48 pp residual8 MAG8−BASE with ~90% from sign reweight and MAG8−SIGN8 ≈ 0; B8≡asym; asym sign-flipping
   across benchmarks) are one to two orders of magnitude below the STOP deficit and were never framed as
   beating fair BM25 or dissolving rerank. They are *tie-resolution micro-measurements*, correctly
   disposed as "small positive / neutral / benchmark-fragile" by their own reports — a reading this audit
   endorses.
3. **The scoped exception**: STOP *does* dispose any continuation claim of the form "8 extra bits (or B8
   reallocation, or float-query scoring) rescue the 12-byte programme against fair BM25 / change the rerank
   conclusion." Nothing in these lines meets C1/C3 scale, and the heavy wave (BRIGHT≈0, BIRCO<0, full-BEIR
   shrinkage) directly warns against generalizing NanoBEIR tie gains. Such a rescue claim would need a new
   prospective, fair-baseline, full-corpus test — not a re-reading of these pilots.
4. **No changed tie-rule approximation was used as replication**: all lines use exact fractional-tie
   expectation (verified in copied libs); legacy finite-trial means are never substituted.

## 7. Whole-project scope statement (what remains outside *this* role)

This role covered only dense-MRL, sign96-micro-residual/nanobeir/heavy, residual8_pilot_r1,
parallel_ideas asymmetric/B8 (sampled), next_route_round1 (sampled), and the STOP-gate scope logic.
Outside this role (other roles' territory, not re-audited here): metric/tie-contract joins and F1
execution (roles 01/05), ITQ-vs-rotation with paired seeds (02), geometry/sigma/E1 theory (03),
comparator/cascade fairness incl. `_rrf60` and candidate recall (04), KV/inverse-memory continuation (07),
static-storage/rank/membership cost-certificate math (08), clean-room portability T1–T3 (09), and
whole-project coverage/governance adjudication incl. `audit4-postcheck-2026-09-17` and literature
primary-source checks (10). Within-scope NOT RUN items: dense embedding rerun, micro ranking rerun,
Actions-artifact checks, oracle_repair rerun, hit10/inverse/kv contents (see COVERAGE.csv ids
05/08/12/23).

## 8. Artifacts

- `STATUS.md` (phased checkpoints), `COVERAGE.csv` (26 rows: 14 REVIEWED / 8 SAMPLED / 4 NOT RUN),
  `evidence/evidence.json`, `scripts/t_probe_synth.py` + `scripts/t_reaggregate.py`,
  `outputs/t_probe_synth.log` + `outputs/t_reaggregate.log`, `copies/{lib_residual8.py,lib_b8.py,
  residual8_PROTOCOL.md,b8_PROTOCOL.md,constants.json}` (originals copied before execution).
- Severity summary: F2/F3 high (scope-critical, both correctly handled in source); F1/F4/F6 medium;
  F5 low; F7 info. No STOP/CONTINUE recommendation is made beyond §6 logic.

