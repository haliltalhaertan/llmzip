# META AUDIT — Round 2: Audit the Auditors

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. VERDICT (3 lines)

Round 1's numbers reproduce: every numeric anchor I re-checked (T1 bit-identity, T2 164256 rows + funnel asymmetry, T3 schema/gate values, manifest gap 0/756, git refs) confirms the auditors' factual claims.
Round 1's false-positive rate is low (~1/25 in stated universal form, plus 3 language overreaches); the coordinator was right in every rejection/narrowing I tested.
No CRITICAL published-number error was found by round 1 or by me; the two strongest round-1 misses I confirm as real are T2's undisclosed top-50-vs-full-corpus funnel and the C1 gate implementation omitting CI + guardrail + both-benchmarks structure (outcome-robust FAILs, but the code cannot PASS as written).

## 2. Findings table

ID | severity | claim audited | what I did | result
---|---|---|---|---
M-01 | HIGH (auditor overreach, not published-number error) | Repro: "package alone reproduces nothing — all scripts hard-code absolute paths outside the package" | Compared package vs raw bytes; listed package inputs; grep'd hardcoded W paths | OVERREACH in universal form: T1 inputs ARE in-package byte-identical; T2/T3 inputs truly absent. Coordinator narrowing CORRECT
M-02 | MED | Repro/claims/integrity/numbers: sigma-division cannot explain sym decline | Read t3_perltqa_kltn.py:60-68, t3_ladder.py:186-188, DECISION_TESTS.md:168; verified sign scale-invariance logic | TRUE. All four workers agree; coordinator agrees. No FP
M-03 | MED | Repro: T2 top-50 funnel vs full-corpus BM25 undisclosed in DECISION_TESTS.md | Read CSV columns + actual_candidates distribution; grep DECISION_TESTS.md for candidat/depth/pool/recall (0 hits) | TRUE. New vs known-issues list. Coordinator accepts
M-04 | MED | Numbers: coordinator/t3_perltqa_kltn.py cannot have produced T3_PERLTQA_KLTN.json (interface + 4 schema points) | Read t3_perltqa_kltn.py:90-110,149-172; step2_build.py:25-66; t3_ladder.py:141-235; published JSON keys | TRUE technically; coordinator narrowing CORRECT that actual producer ablation_r2/perltqa/t3_ladder.py exists and is named in DECISION_TESTS.md:11
M-05 | MED | Integrity: manifest covers 0/756 decision files; 30/30 sample + 14/14 blob identity | Recomputed manifest counts; independent 15-file rehash (seed 999); checked mtimes | TRUE. Independent sample 15/15 match. Scope disclosure adequate
M-06 | MED | Integrity: LADDER_REALTALK.md stale (rank overflow live, zero retraction pointers, dims-as-bytes) | Grep retract/correct/superseded (0 hits except "wrong design"); read LADDER_REALTALK.md:1-55; checked REPORT.md:304 | TRUE
M-07 | MED | Integrity/coordinator: gates+results share commit 8bcdef5 → prespecification UNVERIFIABLE; mtimes prove nothing | Verified git log (REFEREE.md + decision_tests.py one commit each: 8bcdef5); checked mtimes | TRUE. Both worker and coordinator state this correctly
M-08 | MED | Repro: C1 implementation point-only (>=2.0) vs prespecified CI-excluding-0 | Read decision_tests.py:190-197; REFEREE.md:76-77,178 | TRUE. EXTENDED by me: also omits Hit@10 guardrail (REFEREE.md:76-77) and both-benchmarks structure (T1 loads RealTalk only) — round 1 noted only CI
M-09 | LOW-MED | Claims C1: ITQ -2.27 exact over 10 rotations; PerLTQA -0.13 null | Read au_c1_itq.py (stable sort, single ITQ init seed 20260916, 7 fresh RAND); checked code disclosure vs report "TO 0.00pp" + "pre-registered-fresh" | TRUE direction; OVERREACH on exactness language (alternate tie-break) and "pre-registered" (no prereg exists). Consolidated correction CORRECT
M-10 | LOW-MED | Claims C6/repro: frozen_idfonly 65.67 best-of-4 on seen gold; genuine BM25 61.70 still wins; ~4pp setting gap | Verified T1 JSON values; read au_c6_bm25.py (stable sort → 65.53 vs 65.67, 0.14 tie-break); verified per-arch scatter claim structure | TRUE substance; coordinator narrowing CORRECT that 3.97pp is observed setting difference, NOT estimated selection-bias magnitude
M-11 | LOW-MED | Integrity-worker OK on "BM25 needs raw text"; NOT DONE on universal -10.35; broad rerank/novelty acceptance | Read FINAL_STATE.md:117-118 + §reopen; DECISION_TESTS.md:116-117; CSV funnel; lit_r2 scope | Coordinator's four rejections all CORRECT; worker over-permissive on all four
M-12 | LOW | Claims C2: r=-0.80/-0.91 vs claimed -0.78; Spearman/LOO/drop-3; FR@3 weakening; small/large split residual | Recomputed Pearson qscale -0.8013/sym -0.9131; grep'd REPORT.md + math_r1 for -0.78 source (NO HIT) | TRUE computations; PROVENANCE GAP (new): -0.78 source not located in package REPORT/math — UNVERIFIED origin, auditor should have cited exact source
M-13 | LOW | Claims C5: ~10pp gap exact vs naive float (9.93/11.35/10.50), reversed vs float_std 48.51 | Verified LADDER.json arithmetic gaps; REPORT.md:25-29 prints 48.51 vs 46.68 | TRUE. Minor protocol-mixing (46.52 vs 46.68 vs 46.81 across LADDER/REPORT/own-rerun = 0.16-0.29pp tie-break noise); consolidated warning CORRECT
M-14 | LOW | Claims C3/C4: MED perfects balance no gain; qscale collapse +1.33/-3.60 with RealTalk control; asym-T3-only | Read au_c3_balance.py, au_c4_sigma.py (pure-JSON); verified T3 deltas from JSON | TRUE. Caveats self-disclosed (MED changes query threshold; asym-local). No FP
M-15 | LOW | Numbers: T1 4 variants EXACT, gap -10.3546, n=705; T2 contrasts/CIs/inversions; ladder 18 cells; T3 9 arms | Recomputed T1 bit-identity (max diff 1.4e-14); verified n=705 per-arch; T2 rows 164256; T3 JSON arms/deltas/gate | TRUE. Sample limits (ladder 2/10 fresh SVD; T2 CIs Monte-Carlo noise) disclosed. No FP
M-16 | INFO | Repro: 38/38 seal controls; T1 20/20; T3 2-arch direction; LoCoMo 1531/1535 disclosure | Checked iso_t1/iso_t3 outputs exist; verified T3 provenance sha/schema match to t3_ladder | TRUE as far as checked; seal area unrelated, not independently re-executed (stated)

False-positive rate: of ~25 specific falsifiable round-1 findings, 1 fails in stated universal form (M-01), 3 have language overreach requiring narrowing (M-09 exactness/prereg, M-10 bias-magnitude wording, M-13 protocol mixing). All others hold. FP rate ≈ 4% strict (1/25), ≈ 16% including overreaches (4/25). No auditor fabricated a number, path, or result.

## 3. Per-finding detail (paths, lines, commands)

### M-01 — Package portability overreach (coordinator right)

- Repro claim: HARD_AUDIT_REPRO.md:109-112 "package alone reproduces nothing — all scripts hard-code absolute machine paths outside the package."
- Coordinator counter: REPRO_COORDINATOR_REVIEW.md:10-11 "Package contains data/RT01.json and audit/audit_baseline_lib.py ... conflates hard-coded destinations with absent equivalents. T1 can plausibly be made portable by path repair."
- My checks (read-only):
  - `python3 -c` byte compare: `data/RT01.json` package vs `top10_comparison_r1/data/RT01.json` → **byte-identical** (len 136405). `audit/audit_baseline_lib.py` package vs raw → **identical**.
  - Hardcoded paths confirmed: `coordinator/decision_tests.py:34-42` (W=/mnt/c/...; RERANK_CSV, PERLTQA_CACHE, STEP2 outside package), `coordinator/ladder.py:40-45` (FROZEN/LIB/RT/CACHE outside), `ablation_r2/perltqa/t3_ladder.py:235` writes absolute raw-dir path. So path repair IS required.
  - Absent inputs confirmed: `bench3/`, `drive/`, `model/` do not exist in package; `find incoming_20260916b -name *.csv` → (none). So T2 CSV + T3 caches truly missing.
- Verdict: **OVERREACH in universal form**. Correct statement: "No script runs unmodified from the package (absolute W paths + overwrite risks); T1 inputs are vendored byte-identical so a 2-line W redirect suffices; T2/T3 inputs are absent so only T1 is path-repairable." Coordinator narrowing CORRECT. Severity HIGH only as auditor-accuracy issue; it does not change any STOP number.

### M-02 — sym/sigma (all workers correct)

- Code: `_wt_top10/.../coordinator/t3_perltqa_kltn.py:64-68` sym=QB@B.T (no sigma), qscale=(QC/sigma)@B.T floor 1e-12, asym=QC@B.T. `_wt_top10/.../ablation_r2/perltqa/t3_ladder.py:186-188` same (Dpm@QB.T / Dpm@(QC/sigma).T / Dpm@QC.T).
- Data: T3_PERLTQA_KLTN.json delta_192_384 fr3 sym -5.17336, qscale -3.59829, asym +0.30096 (verified by JSON read). sym falls hardest with no division.
- All four workers state this; both coordinator reviews + consolidation agree. TRUE, no FP. Sign scale-invariance argument is sound (positive per-dim scaling cannot flip signs).

### M-03 — T2 funnel (repro true; missed by other workers; new)

- CSV: `incoming_20260916b/.../text_rerank_per_query.csv` columns include `actual_candidates`. distributions: BM25_full actual_candidates = full corpus (nuniq 159, max 689, samples 514/486/...); qscale96_bm25/hamming96_bm25/float_raw32_bm25 = 50 (nuniq 1). Command: per-method `set(int(actual_candidates))` comparison.
- DECISION_TESTS.md grep `candidat|depth|top-50|pool|recall` → 0 hits. decision_tests.py t2() (lines 57-99) never references candidate depth; it contrasts reranked-top-50 arms against full-corpus BM25_full without disclosure.
- Numbers T2 recompute is arithmetically correct but inherits the undisclosed asymmetry; integrity worker §6.3 acceptance ("No overclaim found") is over-permissive — coordinator + consolidation correctly flag recall@50 gating (REPORT oracle 172/705 unreachable outside top-100 corroborates). TRUE finding.

### M-04 — T3 producer mismatch (numbers technically true; coordinator narrowing correct)

- Interface: `bench3/runs/b3b_perltqa/step2_build.py:25` build_items(char)→list of (id,text) tuples; `:54` fit_archive(texts) passes argument to TfidfVectorizer. `coordinator/t3_perltqa_kltn.py:104-110` calls fit_fn(items) with tuples (would raise AttributeError 'tuple' has no 'lower' per sklearn contract) and reads built[0] (a vectorizer, since fit_archive returns 6-tuple wv,cv,svd,s96,mu,C) as Z. Numbers auditor's sklearn-fixture demonstration is consistent with this read.
- Schema: published T3 JSON has gate {diff,bits}, arms {hit10,fr3,n}, delta_192_384.{sc}.{fr3,hit10}, const_dims_at_384. t3_perltqa writer (lines 127-128,149-172) emits per-archive gate dict, arms {hit10,fr3,n_queries,k_eff}, flat delta_192_384_fr3. t3_ladder writer (lines 141,217-235) emits exactly the published schema. DECISION_TESTS.md:11 names `ablation_r2/perltqa/t3_ladder.py → T3_PERLTQA_KLTN.json`.
- Verdict: numbers' "cannot have produced" TRUE for that script; "commit the actual producer" recommendation OVERLOOKS that the actual producer is already present and cited. Coordinator (NUMBERS review:6) + repro §4 provenance note handle this correctly. Do NOT upgrade to fabrication (numbers report itself says "artifact data stands").

### M-05 — Manifest + blobs + gap (integrity true)

- Manifest: FILE_MANIFEST.json n=756; path-substring counts decision_r1=0, DECISION=0, T3_=0, FINAL_STATE=0 (command: json path scan). Mtime manifest 16:36:35 predates DECISION_TESTS.md 21:33:59 and FINAL_STATE.md 21:37:19 (ls --time-style=full-iso). Gap claim TRUE.
- Hashes: verify_manifest.py (seed 20260917, gunzip-then-sha256, 30-sample) and verify_blobs.py (seed 777, 10+4 worktree-vs-`git show findings/...` blobs) read correctly; note verify_blobs.py:22 has dead placeholder line but rel/disk recomputed correctly on lines 24-25, harmless. My independent rehash (different seed 999, 15 files) → 15/15 match. Git refs main=59b891e, branch=e672192, merge-base=5ec3db6, c31719b/a68fcdc/8bcdef5 resolve + ancestor YES — all re-verified via rev-parse/cat-file/merge-base/log. TRUE.

### M-06 — Stale LADDER_REALTALK.md + REPORT §8 (integrity true)

- LADDER_REALTALK.md:1-55 presents rank overflow as live cause ("why PerLTQA's decline was an artifact", "That is the entire pattern", "k<n per archive"). Grep retract/correct/superseded/wrong → only "wrong design" (line 51). Zero pointers to T3 retraction. Tabulates 384 dims as "48 bytes/doc" without sign-bits caveat. TRUE.
- REPORT.md:304 lists older retraction set only; REPORT last touched by a68fcdc before T3 (git log path-scoped, per integrity §1). TRUE. Not silent editing (retractions preserved in FINAL_STATE + DECISION_TESTS + commit messages) — worker's "un-annotated superseded docs, moderate" is the right severity.

### M-07 — Chronology NOT PROVEN (both sides correct)

- `git log --oneline findings/... -- decision_r1/cost/REFEREE.md` and `-- coordinator/decision_tests.py` → exactly one commit each (8bcdef5), verified pattern via log reads. Mtimes REFEREE 21:26 < decision_tests.py 21:30 < JSONs 21:31-33 < commit 21:34:17 consistent but same-commit entry cannot separate pre-fixation from joint authorship. Worker (NOT PROVEN) + coordinator (unverifiable) agree. TRUE.

### M-08 — C1 gate implementation gap (repro true; extended by me)

- Gate text: REFEREE.md:76-77 + :178 require FR@3 ≥+2.0pp, 95% CI excluding zero, BOTH benchmarks, plus Hit@10 lower-CI > -1.0 guardrail.
- Code: decision_tests.py:190-197 tests only `vs_strongest_bm25_fr3_pp >= 2.0` point estimate; no bootstrap, no CI, no guardrail (grep guardrail/lower → 0 hits in file), and t1() loads RealTalk RT*.json only (lines 105-160) so both-benchmarks clause is structurally untestable.
- Round 1 (repro §7.7 + consolidation §7) noted CI omission; **missed guardrail + single-benchmark structure**. Moot for outcome (behind by 7.80pp FR@3 at 48B, FAIL under any version) but the function cannot certify PASS as written. Fix: separate gate/results commits + bootstrap + guardrail + PerLTQA fair-BM25 arm.

### M-09 — ITQ seed/tie-break language (claims direction true; language overreach)

- Code: au_c1_itq.py:9-12 DISCLOSES stable-sort tie-break differing from det_top10; :41-52 single ITQ init (seed 20260916) vs FRESH_SEEDS 7 RAND (:29). Report p.50 "7 pre-registered-fresh seeds" — no prereg exists anywhere in pilot (every doc NOT PREREGISTERED); "pre-registered" is UNSUPPORTED (consolidation §28 correct).
- Impact: qscale continuous → tie-break negligible, -2.27 TO 0.00pp plausible; sym Hamming-ties → 0.3-0.5pp offset self-reported. "ITQ rank 8/8 / 0/10" = one ITQ solution vs RAND distribution, not multi-init robustness. Consolidated "one ITQ solution versus fresh random-control distribution" is the correct framing. Direction (RealTalk qscale harm broad-based; PerLTQA qscale null, sym flips) stands.

### M-10 — Best-of-4 selection (substance true; magnitude wording narrowed)

- Values: DECISION_TESTS.json T1 frozen_idfonly 65.67375887/40.02296521 vs coarse_textbook 55.31914894/33.90536033 → gap -10.35460993 (recomputed). Claims rerun 65.53 vs 65.67 (0.14 tie-break from stable sort, disclosed). Genuine frozen_textbook 61.70212766 beats 12B qscale 49.6454 (-12.05) and 48B 57.8723 (-3.83); C1 FR@3 48B 32.7919 vs genuine 36.0483 → -3.26 FAIL under either baseline. TRUE.
- "Selection inflates headlines ~4pp" (65.67-61.70=3.97): observed setting difference, NOT a statistical bias estimate with uncertainty (no held-out, no selection-adjusted CI). Coordinator correction CORRECT. Direction conservative for C1 challenge (stronger opponent) but number not reusable as "the" BM25 without caveat — worker caveat stands.

### M-11 — Integrity-worker's four over-permissive OKs (coordinator right on all)

- BM25 raw text: FINAL_STATE.md:117 "needs an inverted index and raw text at query time." Standard BM25 scoring needs postings/statistics; raw text serves display/rerank. Cost table honestly separates index (670,511 B) vs index+text (1,669,165 B) but headline sentence overcharges. Worker §6.4 OK too permissive; INTEGRITY review §BM25 correct.
- Universal -10.35: DECISION_TESTS.md:116-117 "Every comparison table in this programme's history needs the −10.35 pp correction" — RealTalk-only delta (T1) prescribed programme-wide with no per-benchmark measurement. Worker §6.5 "NOT DONE ... OK" overlooks the sentence; INTEGRITY review correct. (Already-known issue; not claimed as new.)
- Rerank: see M-03. Worker §6.3 acceptance too permissive; coordinator correct.
- Novelty: FINAL_STATE "genuinely ours"/"appears unstudied" vs lit_r2 maps (existence-only, no protocol/queries/corpus). Absence≠novelty. Worker acceptance too permissive; coordinator + consolidation correct. No numeric anchor affected.

### M-12 — Correlation provenance gap (new, LOW)

- My recompute from RESULTS.json by_archive + RT*.json doc counts: Pearson qscale -0.8013, sym -0.9131; Spearman/LOO/drop-3/FR@3-weakening/small-large residuals as reported. Computations TRUE.
- Provenance: grep -rn "0.78|Spearman|Pearson" REPORT.md + math_r1 → no hit for claimed -0.78 source. Auditor compares -0.80 vs "claimed -0.78" without citing exact doc+line of the claim. UNVERIFIED origin. Require exact citation before quoting either value; 0.02 delta is aggregation-detail scale but should be minuted, not rounded away.

### M-13 — Float gaps + protocol mixing (substance true; mixing caution correct)

- LADDER.json: k96 sym 46.52482270, float 36.59574468 → +9.92908; k192 +11.34752; k384 +10.49645 (recomputed). Claims "9.93/11.35/10.50" TRUE.
- Three sym numbers: LADDER 46.5248 (det_top10 protocol) vs REPORT §1 sign96 46.68 vs claims rerun 46.81 (stable sort) = 0.16-0.29pp spread. Claims compares REPORT's 48.51 (REPORT protocol) against own 46.81 (-1.70) as confirming REPORT/hr -1.83 (48.51-46.68). Approximately right but cross-protocol; consolidation "do not mix as exact matched-protocol differences" CORRECT. Claim 5 ZAYIF verdict (exact vs naive float; reversed vs standardized float) stands.

### M-14 — MED + sigma-collapse controls (true, self-caveated)

- au_c3_balance.py: pooled 8944×96 balance FULL [0.309,0.658] vs MED [0.500,0.500]; retrieval MED-FULL negative (RealTalk sym -1.13/qscale -0.43; PerLTQA sym -0.81/qscale -0.53, published deltas, calibration <0.3pp). Code comment + report BOTH disclose MED re-thresholds queries at doc median (not pure balance knob) and lit-contrast unverified. Consolidated "not pure causal intervention" agrees with worker's own caveat — not a refutation.
- au_c4_sigma.py pure-JSON: T3 qscale 96→192 +1.33 then 192→384 -3.60 (Hit@10 -2.48); RealTalk qscale monotone +5.67/+2.55; asym≥qscale at every T3 k (+0.71/+3.08/+6.98); cross-benchmark asym-qscale +0.29 PerLTQA / -3.62 LME / -1.58 LoCoMo. All consistent with published JSONs. TRUE.

### M-15 — Numbers 101/101 (true within stated sampled scope)

- T1 bit-identity: audit_t1_out.json vs DECISION_TESTS.json diffs 0.0 / ±7.1e-15 / 1.4e-14 (float dust) across 4 variants; n=705 per-arch 85+70+73+71+70+74+70+70+63+59 re-verified from raw RT JSONs with gold-in-row filter (matches coordinator t1() filter). TRUE.
- T2: CSV rows 164256 re-verified; auditor seed 777 + 5×2000 multiseed vs coordinator 20000/seed-20260916 is adequate uncertainty (CIs within 0.02 vs 0.3 tolerance). Levels/inversions re-verified structurally. TRUE.
- Ladder: gate 858624 = 8944×96 re-verified arithmetically; RT04/RT05 18 cells + 10-archive re-aggregation to 6dp as reported (outputs audit_ladder_out.json present). Scope honestly labeled sampled (2/10 fresh SVD). TRUE.
- T3: gate 276480 = 2880×96; arms/deltas/const/N/gold-validation as in JSON (3 output files cover 8 archives: Kong_Zhu, Xu_Xu_Xiao, Cao_Xia_Madan). Full-precision <1e-9 dust noted. TRUE within scope. No MISMATCH found.

### M-16 — Repro mechanics (true as far as checked)

- T1 20/20 + RT01 own 61.1765 match: consistent with M-15 bit-identity; iso_t1/iso_t3 dirs + outputs present. TRUE.
- T3 2-arch direction + 0/61056 gate + provenance (sha 339fd9e6…, schema matches t3_ladder not t3_perltqa): schema verified by me (M-04); sha not re-hashed (stated). Accept as reported.
- 38/38 seal: unrelated area (main-repo tools/test_verify_preregistration_seal.py, 0 pytest, direct-exec negative controls), not re-executed here. Recorded, not relied upon.

## 4. What I could NOT check and why

- Full fresh SVD for ladder 8/10 archives; full T3 8-archive × multi-seed; T2 _rrf60 contrasts; NOPROJ arms; k=768 grid: each exceeds the bounded-probe budget / requires hours or live jobs; auditors' NOT RUN labels accepted, my verdicts inherit their sampled scope. I state samples as samples.
- F1/KV/inverse, dense-MRL, E1/geometry/residual bodies; ~130 remote refs; v52-era bulk; cost/latency; lit_r2 maps beyond existence; MODEL_DOWNLOAD weights hash (2.4 GB excluded by design); LoCoMo gold adjudication (1531 vs 1535, 156 corrections): named-only or live-job scope, untouched per read-only + no-fetch rules.
- No internet: no external literature verification (novelty stays UNVERIFIED either way, as workers state).
- No clean-room clone/package-only execution: by source-protection rule (would overwrite published JSONs / duplicate GBs); path audit + byte-identity + blob-identity substituted and stated.
- Round-1 worker intermediate stdout logs (numbers.txt, claims.log etc.) not re-executed; I read code + outputs + sources instead. A re-run would test determinism, not correctness, for deterministic arms.
- Mtime/hash snapshots detect change, prevent nothing; I used them only as chronology consistency, never as pre-registration proof.

## 5. Coordinator-verdict scorecard (was the coordinator defending itself?)

- Numbers producer narrowing: CORRECT (not self-defense; actual producer cited).
- Integrity 4 corrections (raw-text, universal correction, rerank, novelty) + selection caveat: ALL CORRECT; worker over-permissive on each.
- Repro 4 narrowings (portability, universal-failure wording, k=768 timing, 3.97-as-bias): ALL CORRECT; worker's universal/estimate language exceeded its executed evidence.
- Consolidated claims-worker limits (tie-break, single-ITQ, "pre-registered", protocol mixing, Pearson/balance residuals, MED confound, trailing-noise-as-hypothesis, raw-text-as-owner-Q9): ALL CORRECT and consistent with workers' own buried caveats. Consolidation did not suppress any true positive; it preserved scope labels (sampled, NOT whole-project certificate) and correctly refused project-wide STOP.
- No coordinator rejection was self-defense; each added precision without reversing a true direction. The one place the coordinator could have gone further: stating M-08's guardrail + single-benchmark gaps and M-01's T1-repairability explicitly (done here).

## 6. Commands run (read-only; python3; no source writes)

- JSON reads: DECISION_TESTS.json T1 variants/keys; T3 gate/const/delta/arms; LADDER arms/gaps; FILE_MANIFEST counts (756; 0 decision/T3/FINAL_STATE); RESULTS.json seeds/keys.
- Byte-identity: package data/RT01.json vs raw; package audit_baseline_lib.py vs raw (both identical).
- Git: rev-parse main/findings, merge-base, cat-file -t c31719b/a68fcdc/8bcdef5, ancestor check, log stack.
- Manifest: independent 15-file rehash (seed 999) 15/15; mtime ls manifest vs DECISION_TESTS/FINAL_STATE.
- T2: DictReader rows 164256, columns, per-method actual_candidates sets (BM25_full 159 uniq/full-corpus vs *_bm25 1 uniq/50); grep DECISION_TESTS.md candidat/depth/pool/recall (0).
- T1 cohort: per-archive gold-in-row counts 85+70+73+71+70+74+70+70+63+59=705; repr+exclusions (23 excluded) same 705.
- T3: step2_build build_items/fit_archive signatures; t3_perltqa vs t3_ladder writer schema diff; DECISION_TESTS.md:11 producer line.
- Gates: decision_tests.py:190-197 C1 point check; REFEREE.md gate/guardrail lines; FINAL_STATE.md:117 raw-text + reopen; LADDER_REALTALK.md:1-55 + retract-grep; REPORT.md:25-29 float table + :304 stale list.
- Tie-break: det_top10 vs fast_topk (verified-equivalent assert in-file) vs claims stable-sort (au_c1/c5/c6); T1 bit-identity diffs ≤1.4e-14; gap -10.35460993.
- Correlation: Pearson recompute -0.8013/-0.9131; REPORT/math grep for -0.78 (no hit).
- Outputs inventory: numbers *.json (t1/t2/ladder/3×t3), repro iso_t1/iso_t3 listings.

All writes went to /mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/meta/ only. Sources read-only; no commit/push/clone/fetch; snapshot re-check expected to pass.
