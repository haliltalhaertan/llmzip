# HARD AUDIT — NUMBERS (local exploratory pilot)

> [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
> Audit evidence, not a desired PASS/FAIL. All coordinator claims including STOP are untrusted hypotheses.
> Sources are READ ONLY. All recomputation uses the auditor's own code in this directory.
> NOT RUN means the check was not executed — never infer it.
> Workspace (audit, writable): `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r1/numbers`
> Published package (READ ONLY): `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/`
> Main repo: `/mnt/c/Users/MDP/dev/llmzip` — Research root: `/mnt/c/Users/MDP/dev/llmzip-work`

Status: STARTED 2026-09-17. This file is written incrementally; partial results preserved.

## Coverage ledger (filled at end)
- Examined: (pending)
- Sampled: (pending)
- NOT REVIEWED: (pending)

## Row format
`claim | recomputed | status (EXACT/CLOSE/MISMATCH/NOT RUN) | notes`

Tolerances: ladder 0.01 pp; T2 CI 0.3 pp. EXACT = bit/round identical; CLOSE = within tolerance.

---

## T0 — contracts and challenged claims (examined 2026-09-17)
- Metric contract (read, not executed): `det_top10(scores, archive_id, k)` sorts by (-score, sha256("top10-r1|<arch>|<row>"), row) — deterministic tie-break. Source: `top10_comparison_r1/audit/audit_baseline_lib.py:79-83` (TIE_SALT=top10-r1). Hit@10 = any gold in top10; FR@3 = |gold∩top3|/|gold|, ×100, micro-averaged over queries. Reused verbatim by ladder.py:134-142, decision_tests.py, t3 script.
- Coordinator BM25 contract: idf=log(1+(N-df+0.5)/(df+0.5)), tf term c*(k1+1)/(c+k1*(1-b+b*len/avg)); k1=0 variant scores idf-only (sum of idf for matched query terms). Tokenizers: coarse `[a-z0-9]+`; frozen `\b\w\w+\b` minus English stop list. Read from ladder.py:63-109, decision_tests.py:112-152.
- Coordinator code arms: C,QC = L2-normalized TruncatedSVD then archive-mean-centered; sym=sign(QC)@sign(C).T; qscale=(QC/sigma)@B.T with sigma=C.std(ddof=0), floor 1e-12; asym=QC@B.T (T3 only); float=normalize(QC)@normalize(C).T (centered+normalized). Read from ladder.py:111-154, t3:60-69.
- hr/standardized-float-correction-2026-09-16 (commit 7501991, `docs/v52/V52_STANDARDIZED_FLOAT_CORRECTION_2026-09-16.md`, read via `git show`): frozen G=+10.037943pp SIGN-beats-FLOAT stands arithmetically BUT is measured against FLOAT96_UNCENTERED; standardizing the same float reverses the comparison on Hit@10 (sym minus float_std: -2.22 LME, -8.20 PerLTQA, -1.83 RealTalk, -6.19 LoCoMo). float_std costs 768B vs 12B (ceiling, not byte-competitor); raw float still wins on PerLTQA en_v1/zh. Metric caveat: pilot Hit@k, not frozen frac@3.
- Challenge ledger (auditor position, evidence below): (a) sym does NOT divide by sigma — qscale does; sign is invariant to positive per-dim scaling, so the "qscale divides by sigma" overflow story cannot apply to sym — checked in T3; (b) rank-overflow correction as causal explanation — tested by k_eff rebuild; (c) rerank dissolving first-stage value — tested by T2 inversion counts; (d) BM25 needs raw text — BM25 runs on tokenized text by construction, tested by tokenizer variants; (e) RealTalk-only delta applied to all datasets — T2 shows per-dataset heterogeneity, reported separately; (f) best-of-4 BM25 on seen gold — selection bias noted, no held-out split exists (all NOT PREREGISTERED pilot); (g) STOP as project closure — coordinator DECISION_TESTS gates C1/C3 are local pilot gates, not a project-closure authorization (no ledger authorization found in examined scope).
- Pre-registration status: all coordinator JSONs carry [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED]; file mtimes not used as evidence. No prereg document found in examined scope.

## T2 — rerank dissolution (auditor recompute 2026-09-17, own code `audit_t2.py`, seed 777 + multiseed 11/22/33/44/55)
- Source: incoming CSV `.../LLMZIP_FIKIR1_2026-09-16/results/text_rerank_per_query.csv` (READ ONLY). Method: own CSV parse, own micro-mean levels, own cluster-bootstrap (per-cluster sums, resample clusters with replacement). Coordinator used seed 20260916/20000 reps; auditor used seed 777/20000 reps + 5×2000-rep multiseed distribution for the focal contrast.
- claim 164256 rows | recomputed 164256 | EXACT.
- LME qscale96+rerank vs BM25 -0.33pp | recomputed -0.3298, CI audit [-1.3830,+0.6277] vs coord [-1.3830,+0.6170] | CLOSE (est EXACT, CI within 0.02pp Monte-Carlo noise; excludes-zero=FALSE both).
- PerLTQA qscale96+rerank vs BM25 +0.33pp | recomputed +0.3283, CI audit [-0.0247,+0.6681] vs coord [-0.0172,+0.6706] | CLOSE (within 0.01pp; excludes-zero=FALSE both; C3 FAIL both since est<1.0).
- LoCoMo qscale96+rerank vs BM25 +1.07pp | recomputed +1.0652, CI audit [+0.4400,+1.7139] vs coord [+0.4389,+1.7162] | CLOSE (within 0.01pp; excludes-zero=TRUE both; C3 PASS both since est>=1.0 and sig).
- All 15 contrast point estimates: EXACT to 4dp (max |diff| 0.0000pp). All level means (BM25_full, qscale96, float_raw32, float_std32, reranked): EXACT (diff +0.000000).
- All 15 CIs: within 0.3pp tolerance (max endpoint diff ~0.02pp, Monte-Carlo noise across seeds). Multiseed focal distributions: LME est -0.330 all 5 seeds, CI lo in [-1.447,-1.277], hi in [+0.574,+0.617]; LoCoMo est +1.065 all seeds, lo in [+0.406,+0.459], hi in [+1.685,+1.736]; PerLTQA est +0.328 all seeds, lo in [-0.027,-0.011], hi in [+0.658,+0.670]. No seed flips any excludes-zero verdict. A single seed is not offered as refutation; the distribution is the evidence.
- Rank inversion LME float_raw32 44.16->57.76 | recomputed 44.159574->57.762411 | EXACT. LME float_std 55.74->58.05 | recomputed 55.744681->58.046099 | EXACT.
- Inversion counts: LME 4/10 | 4/10 EXACT; LoCoMo 3/10 | 3/10 EXACT; PerLTQA 6/10 | 6/10 EXACT.
- Interpretation (auditor, not a number): (a) holds only on LoCoMo for qscale96 (C3 PASS); LME/PerLTQA FAIL. (b) inversion present on all three benchmarks — first-stage order does not survive reranking. Heterogeneity across datasets means a RealTalk-only delta cannot be applied to all datasets.

## T1 — fair BM25 baseline (auditor recompute 2026-09-17, own code `audit_t1.py`)
- Method: own tokenizers (coarse `[a-z0-9]+`; frozen `\b\w\w+\b` minus same English stop list), own BM25 (textbook k1=1.2/b=0.75; idf-only k1=0/b=0 scores sum-of-idf), own det_top10 (same deterministic contract: -score, sha256("top10-r1|<arch>|<row>"), row). No coordinator code imported. All 10 RT archives rebuilt from raw `top10_comparison_r1/data/RT*.json`.
- claim frozen_idfonly Hit@10 65.67 | recomputed 65.673759, diff +0.000000 | EXACT. (FR@3 40.022965 diff -0.000000.)
- claim frozen_textbook 61.70 | recomputed 61.702128 diff +0.000000 | EXACT. (FR@3 36.048330.)
- claim coarse_idfonly 57.30 | recomputed 57.304965 diff +0.000000 | EXACT. (FR@3 34.050582.)
- claim coarse_textbook 55.32 | recomputed 55.319149 diff +0.000000 | EXACT. (FR@3 33.905360.)
- n=705 queries confirmed (85+70+73+71+70+74+70+70+63+59, all with gold rows present; no query dropped by the gold filter in this recompute).
- claim strongest-vs-24B/qscale gap -10.35pp | recomputed 55.31914894-65.67375887 = -10.354610 | EXACT.
- Strongest variant = frozen_idfonly (own recompute agrees). Selection-bias note: best-of-4 chosen on the same gold it is evaluated on; no held-out split exists anywhere in this pilot (all labels NOT PREREGISTERED). BM25 scoring needs tokenized text, not raw text — the frozen tokenizer itself is part of why frozen BM25 wins (+6.38pp over coarse textbook: 61.70 vs 55.32).
- Code arms (12B/sym 46.52 ... 48B/qscale 57.87) are ladder values; verified in the Ladder section below, not re-derived here.

## Ladder — RealTalk (auditor recompute 2026-09-17, own code `audit_ladder.py`)
- Method: frozen feature recipe reused read-only as the shared benchmark definition (import of `drive/v52_t4d_locomo_frozen_cross_benchmark.py` fit functions only; no coordinator script executed; outputs to own dir). SVD runs, sign coding, scoring, metrics are the auditor's own. Compared per-archive against `LADDER_CACHE.jsonl` (tolerance 0.01pp) and re-aggregated.
- Fidelity gate claim 858624/0 | recomputed sum over 10 cache rows: 0/858624 | EXACT (858624 = 8944 docs x 96; own k=96 rebuild on RT04/RT05: 0/40512 and 0/39360, max_abs n/a — bit-exact).
- RT05 (410 docs/70q) all 9 cells k96/k192/k384 x sym/qscale/float | EXACT (all d=+0.000000).
- RT04 (422 docs/71q) all 9 cells | EXACT (all d=+0.000000).
- Re-aggregation of all 10 cache rows (query-count-weighted micro-mean) reproduces every LADDER.json arm to 6dp (e.g. k96/sym 46.524823/22.867556, k384/qscale 57.872340/32.791941, n=705) | EXACT.
- Cross-check: LADDER.json BM25_coarse 55.319149 / BM25_frozen 61.702128 equal the T1 textbook variants | EXACT (same two numbers, consistent).
- Sampled scope: 2/10 archives rebuilt (RT04, RT05 — the two smallest); other 8 archives' cache rows verified only through the exact re-aggregation, NOT by fresh SVD. Full-table MATCH is therefore sampled, not exhaustive.
- Observation (not a mismatch): on RT04, centered+normalized float at k96 hits 66.20 vs sym 50.70 — consistent with hr/standardized-float-correction-2026-09-16 that the comparator's normalization decides the sign-vs-float headline.

## T3 — PerLTQA k<n (auditor recompute 2026-09-17, own code `audit_t3.py`)
- Method: document texts rebuilt from raw `bench3/PerLTQA/Dataset/en_v2` mem JSONs by reimplementing the deterministic itemization; frozen feature recipe re-run (word TF-IDF(1,2)+char_wb(3,5)+latent32 SVD seed 5101, concat, archive SVD seed 5204, L2 norm, mean-center); query texts re-derived via the deterministic qid scheme. Validation BEFORE scoring: all 8 archives' (qid->gold) mappings EXACT-match `cache_q_eval.pkl` (216/216, 323/323, 281/281, 205/205, 301/301, 299/299-ish per archive; total nq=2217 | EXACT). k_eff=min(k,n-1) enforced. SVD/scoring/metrics own. All 8/8 small archives rebuilt (exceeded the 2-archive minimum).
- gate diff claim 0 | recomputed sum of per-archive sign-bit diffs = 0 | EXACT. gate bits claim 276480 | recomputed 2880 docs x 96 = 276480 | EXACT.
- qscale FR@3 claims 56.38/57.71/54.11 | recomputed 56.378124/57.709750/54.111460 | EXACT (agree to 6dp; full-precision diff <1e-9).
- sym FR@3 claims 51.69/53.88/48.71 | recomputed 51.693995/53.884346/48.710983 | EXACT (same precision note).
- asym FR@3 claims 57.09/60.79/61.09 | recomputed 57.086611/60.790925/61.091881 | EXACT (same).
- Hit@10 arms (78.12/81.33/81.87, 77.94/82.18/84.71, 74.65/79.70/84.89) | all EXACT to 6dp (same note).
- const_dims@384=0 claim | recomputed sigma-floor count = 0 constant dims at k=96/192/384 for ALL 8 archives | EXACT.
- 192->384 FR@3 deltas: qscale -3.598290 / sym -5.173363 / asym +0.300956 | recomputed identical to 6dp | EXACT.
- Archive N values 293/343/359/371/376/377/380/381 | all EXACT (asserted against arch_cache before building).
- CAUSAL CHALLENGE OUTCOME (evidence, not a number): sym does NOT divide by sigma (pure sign-vs-sign arm; sign invariant to positive per-dim scaling), yet sym 192->384 falls -5.17pp — HARDER than qscale's -3.60pp. The rank-overflow/sigma-division mechanism therefore cannot be the complete causal explanation of the 192->384 decline: the decline persists at full strength on an arm immune to that mechanism. Coordinator's own prespecified S3-type reading (real capacity effect beyond the artifact) is supported for sym; asym (unstandardized, query NOT binarized) rises +0.30. The open question is why query binarization (sym) collapses while asym does not — same pattern as the hr correction's unresolved "binarising the QUERY costs 4.43pp on PerLTQA" note.

## INCONSISTENCIES AND CAVEATS (severity-ranked)
1. [MEDIUM, reproducibility — NOT a number mismatch] Committed T3 producer `coordinator/t3_perltqa_kltn.py` cannot have produced `T3_PERLTQA_KLTN.json`: (a) it calls `fit_archive(items)` with items=list of (id,text) tuples, but committed `bench3/runs/b3b_perltqa/step2_build.py:fit_archive(texts)` passes its argument straight into TfidfVectorizer — demonstrated with a benign sklearn fixture: tuples raise `AttributeError: 'tuple' object has no attribute 'lower'` (the script would print BLOCKER per archive and end with "NO RESULTS — nothing written"); even past that, it reads Z from `built[0]` which is a vectorizer, not a matrix. (b) Output schema differs on four points: script writes gate as per-archive dict vs JSON `{diff,bits}`; arms entries `{hit10,fr3,n_queries,k_eff}` vs JSON `{hit10,fr3,n}`; delta key `delta_192_384_fr3` (flat) vs JSON `delta_192_384.{sc}.{fr3,hit10}`; `const_dims_at_384` is written by no line of the script. The NUMBERS verify exactly via independent rebuild, so the artifact data stands; the committed producer does not match it. Recommendation: commit the actual producer or mark the script non-canonical.
2. [MEDIUM, interpretation — numbers verify] The "rank overflow explains the 192->384 decline" causal claim is incomplete (see T3 outcome above): sym falls -5.17pp with no sigma division. Quoting the artifact story as the full explanation inherits this error.
3. [LOW, method — disclosed] T1 strongest-BM25 is best-of-4 selected on the evaluated gold (no held-out split; whole pilot NOT PREREGISTERED). Gap magnitudes (-10.35 etc.) are in-sample comparisons, not generalization estimates.
4. [LOW, framing — corroborated] hr/standardized-float-correction-2026-09-16 (commit 7501991): any "SIGN beats FLOAT" headline must name its float reference. In THESE artifacts the float arms are centered+normalized (strong reference): e.g. RT04 k96/float Hit@10 66.20 beats sym 50.70. No headline in LADDER/DECISION_TESTS/T3 JSONs contradicts the correction; the correction's own numbers come from a different pilot dir and are NOT cross-checked here (NOT REVIEWED scope).
5. [GOVERNANCE, no numeric content] C1/C3 gates and any STOP recommendation are local pilot decision rules. No ledger authorization for project closure was found in examined scope; treating a pilot STOP as project closure would be misrepresentation.

## COVERAGE LEDGER
- Examined (read + independently recomputed): T0 contracts (det_top10, BM25, arm defs, hr correction doc); T1 all 4 BM25 variants from raw RT JSONs (n=705); T2 full CSV (164256 rows), all 15 _bm25 contrasts + CIs (own seed + 5-seed distribution), all level means, inversion counts; Ladder gates (sum), 2/10 archives fresh SVD (RT04, RT05, 18 cells), full 10-archive re-aggregation, BM25 cross-checks; T3 all 8/8 small archives fresh SVD (gates, gold validation, 9 arms, const dims, deltas).
- Sampled: ladder full-table MATCH rests on 2/10 fresh rebuilds + exact re-aggregation of the other 8 cache rows (not fresh SVD).
- NOT REVIEWED (NOT RUN): NOPROJ_WORD/NOPROJ_FULL ladder arms; T2 _rrf60 contrasts/CIs (levels only); k=768 (dropped by coordinator, justification on record in ladder.py:56-62); hr-correction pilot numbers (different artifact); any main-repo frozen estimands (frac@3 etc.); cost_audit/repr/rerank-ceiling artifacts; decision_r1/lit_r2/digest/math/ablation/ideas dirs; remote-tracking refs beyond branch listing; pre-registration search beyond examined scope.
- Source protection: all sources READ ONLY; coordinator/original scripts never executed (only read); all outputs in this audit dir; PYTHONDONTWRITEBYTECODE=1; each probe completed well under 180 s.
- Hash snapshots / mtimes: not used as evidence (per instructions, mtimes prove nothing; no hash snapshot taken — a snapshot detects change but prevents no writes; stated here instead of performed).

## TOTALS
- Rows checked: T2 42 (1 rowcount + 15 contrasts w/ CI + 21 levels + 2 named inversion pairs + 3 inversion counts) | T1 11 (4 Hit@10 + 4 FR@3 + gap + strongest-id + n) | Ladder 30 (1 gate + 18 fresh cells + 9 re-aggregated + 2 BM25 cross) | T3 18 (2 gate + 9 arms + 1 const + 1 n + 1 archive-N + 3 deltas + 1 gold-validation) = 101 rows.
- Statuses: EXACT 84 | CLOSE 17 (15 T2 CIs within 0.02pp Monte-Carlo noise of the 0.3pp tolerance; 2 T3 arm rows at full-precision <1e-9 dust — all agree to published 2dp/6dp) | MISMATCH 0 | NOT RUN 0 (in-scope numbers; out-of-scope items listed as NOT REVIEWED above, not counted).
- MATCH rate (EXACT+CLOSE within tolerance): 101/101 = 100.0%. No numeric claim checked was refuted.
- Bottom line: every number in scope reproduces — including gates 858624/0 and 276480/0, all four BM25 variants, the -10.35 gap, all T2 contrasts/CIs/inversions, and the full T3 table. The audit's positive findings are (a) the T3 producer-script/artifact mismatch and (b) the sym-decline evidence against the completeness of the rank-overflow causal story. All claims remain [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION].
