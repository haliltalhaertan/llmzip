# COVERAGE AUDIT (round 2) — the dark corners round 1 never entered

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Read-only on all source trees; writes only in this directory. No invented numbers;
UNVERIFIED is stated where it applies. Sampling is declared.

## 1. VERDICT (3 lines)

No dropped contradiction found: nothing in the never-audited directories beats fair
BM25 or otherwise overturns the STOP direction. Three verified passes (PQ 33.05,
first-stage pools, ceiling decomposition) all reproduce exactly. Three new
labeling/storage inconsistencies found (HIGH: none change any conclusion; §§F1–F3).

## 2. FINDINGS

### F1 — HIGH (labeling): REPORT §1 mixes expected-Hit into a det-metric table
Claim: REPORT §1 table, sign96 46.68. Check: recomputed both variants from stored
rows. Result: FAIL on labeling (numbers exact, label wrong) — det-Hit is 46.52
(328/705); 46.68 is expected-Hit under uniform ties (329.1/705, impossible for any
det rule). Rest of table is det. 0.16 pp; conclusions unaffected.

### F2 — MED (storage): firststage REPORT quotes the disclaimed pickle number
Claim: ideas_r1/firststage/REPORT.md storage table (BM25 index 1,450,229 B).
Check: compared against cost_audit.json + REPORT §4. Result: CONTRADICTION —
1,450,229 is the pickle artifact REPORT §4 says must not be quoted; honest varint
is 670,511. Same directory's numbers verify; its storage table does not.

### F3 — MED (labeling): three live definitions of "plain BM25", 54.18 vs 55.32
Claim: REPORT §1 BM25 54.18 vs DECISION_TESTS "what we always quoted" 55.32.
Check: traced each number to its producer. Result: CONFIRMED GAP — 54.18 is the
lexical worker (k1=1.5, `\w+` tokenizer); 55.32 is T1 coarse-textbook (k1=1.2).
1.14 pp apart, no cross-pointer. Neither touches the STOP margin (both lose to
code by less than fair BM25 beats it — and fair BM25 beats code regardless).

### F4 — LOW (control quality): PQ 33.05 verifies but is a weak control
Claim: pq/SUMMARY.json Hit@10 0.3305 as equal-budget control. Check: independent
recompute from 705 stored rows + config review. Result: PASS arithmetically
(0/705 flag mismatches, all 10 archives exact), WEAK as control — single
seed/config, faiss undertraining warning (8944 < 9984 points), 98 KB codebook
uncharged in the headline, ~59 ms/query scoring. Per-archive collapse (RT06 5.4%,
RT08 4.3%) fits the size-damage story but is not mentioned in REPORT §1.

### V1 — PASS: PQ 33.05 reproduces to 0.000000
705/705 rows; independent set-intersection vs stored flags agree fully.

### V2 — PASS: first-stage pools + complementarity reproduce exactly
M=100 CODE 75.6028 / BM25 78.1560 / RRF 81.2766; complementarity 49/67/484/105;
contrasts +5.67 CI [+3.23,+8.20], RRF−BM25 +3.12 all match stored aggregates.

### V3 — PASS: ceiling table + 350/183/172 + 328/158/170 reproduce exactly
Ceilings 76.52/92.62/61.30; CODE hit@10 350, reachable 183, unreachable 172;
sym+qscale both-miss 328 with 158 in-top-100 / 170 outside, from independent join
of math_r1/repr FULL arms × firststage pools.

### D — NO CONTRADICTION in older dirs (checked, not sampled away)
Baseline 12/12 arm means reproduce exactly; float_std beats sign on all three
benches (supports, not contradicts, the hr correction). Semantic dir holds
embeddings only, zero retrieval numbers — abandonment account accurate. LME
partial rows carry timings/shapes/g1 only, no arm means — nothing hidden, verdict
honestly PENDING. All previously-positive repr arms (IDF_p2 rare +4.78 SIG,
SHIFT_m1 +1.58 SIG, WORD_ONLY +1.37 SIG) are disclosed in REPORT with caveats.

## 3. DETAIL (paths, lines, commands)

F1: [REPORT.md](/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/REPORT.md:26)
says sign96 46.68. Stored truth
[top10_comparison_r1/math_r1/quant/RESULTS.json](NEVER-AUDITED-PATH: math_r1/quant/RESULTS.json,
benchmarks.RealTalk.summary): FULL/sym hit10_pct 46.52482269503546,
exp_hit10_pct 46.68085106382979. The worker diagnosed this itself in
[top10_comparison_r1/ideas_r1/ablation/REPORT.md](NEVER-AUDITED-PATH) G2 note
(46.6809×705 = 329.1, impossible for a det rule). Command: `v1_pq.py`-style JSON
read of RESULTS.json summary (this dir). Round 1 reproduced the det variant
(46.524823) and never checked which variant REPORT §1 printed.

F2: [firststage/REPORT.md](NEVER-AUDITED-PATH: ideas_r1/firststage/REPORT.md:16-18)
table: BM25 "1,450,229 index + 998,654 raw text = 2,448,883".
[cost_audit.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/cost_audit.json:1-8):
bm25_pickle_B 1450229, bm25_compact_B 670511, raw_text_B 998654.
REPORT §4 (lines 216-219) uses 670,511 and disclaims the pickle number. Arithmetic
confirming the honest total ran here: 670511+998654 = 1669165 = FINAL_STATE §cost.
The firststage table was never audited (round-1 repro praised the pickle warning
without noticing the firststage doc still uses the pickle value as primary).

F3: producers: [data/lexical_summary.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data/lexical_summary.json)
(bm25 k1 1.5, Hit@10 0.5418 = 54.18) vs
[DECISION_TESTS.md](/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/DECISION_TESTS.md:21)
(coarse-textbook 55.32). [firststage/RESULTS.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/RESULTS.json)
gates.G5_bm25_hit10 = 54.184397163120565 pins 54.18 to the lexical worker.
V2 recompute confirms 54.1844 at M=10 from stored pools. No doc links the two.

V1: script `v1_pq.py` (this dir) over
[pq/per_query.jsonl](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/pq/per_query.jsonl)
(705 rows) vs [pq/SUMMARY.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/pq/SUMMARY.json):
indep 0.3304964539007092 = stored = SUMMARY, 0 mismatches, per-archive diffs all
+0.000000. Caveats from [pq/REPORT.md](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/pq/REPORT.md:46-48)
(faiss warning) and SUMMARY.json timing (41.56 s / 705 ≈ 59 ms/query).

V2: script `v2_firststage.py` (this dir) over
[ideas_r1/firststage/per_query.jsonl](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl):
M=100 pools 75.6028/78.1560/81.2766; code_only 49, bm25_only 67, both 484,
neither 105 — all equal stored [RESULTS.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/firststage/RESULTS.json)
pool/contrast/complementarity sections to 4dp.

V3: script `v3_ceiling.py` + `v3b_bothmiss.py` (this dir):
[rerank_ceiling.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/rerank_ceiling.json)
fr3_now/ceil100: PerLTQA 53.24/76.52, LME 54.27/92.62, RealTalk 22.41/61.30 —
equal REPORT §5 (LME gain +38.35, rounds to the printed +38.4).
350/183/172 derived from V2 CODE pools (350 hit@10, 533 hit@100).
328/158/170 from independent join of
[math_r1/repr/per_query.jsonl](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/math_r1/repr/per_query.jsonl)
(FULL sym/qscale hit10, 705 qids) with firststage CODE top-100 pools — equal
[digest_r1/brain/check_bothmiss.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/brain/check_bothmiss.json)
exactly. (Note: REPORT's "both scorers" = qscale+sym, not CODE+BM25, whose
both-miss is 270 — ambiguous phrasing, numbers right.)

D: script `v4_baseline_spot.py` (this dir) over
[baseline/per_query_top10.jsonl](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/baseline/per_query_top10.jsonl)
(9440 rows): all 12 (bench, arm) means equal
[baseline/REPORT.md](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/baseline/REPORT.md:86-110)
to 4dp; float_std > sign on PerLTQA (+8.28), LME (+1.92), RealTalk (+1.99).
Semantic: [progress.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/semantic/progress.json)
(120/9649 texts, est 150108 s total) + payloads (embeddings only) — matches
REPORT §6 "no retrieval numbers". LME: REPORT tables PENDING (lines 50-60),
PARTIAL rows lack arm-hit keys (checked first-row key list), 322/322 G1 rows
with differing_bits 0. Repr positives: REPORT §§3.2–3.3 carry their own caveats
(post-hoc subgroup, cross-bench reversal); [rare_band_decisive.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/coordinator/rare_band_decisive.json)
rare/fr3 +4.78 CI [+0.69,+8.43] matches REPORT; LOO instability (+12.76/−8.43
range quoted) lives in [check_decisive.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/brain/check_decisive.json)
— disclosed, not dropped.

Task B roll-call (cited in FINAL_STATE/REPORT, producer never audited in round 1):
PQ 33.05 (now V1 PASS) · RRF pools 75.60/78.16/81.28 (now V2 PASS) · ceiling
76.52/92.62/61.30 + 350/183/172 + 328/170 (now V3 PASS) · baseline float arms
(now spot PASS) · cost 115008/670511/1669165 (arithmetic confirmed here; per-row
recompute NOT RUN) · band table 70.67/85.04 (read in why_bm25_wins.json, NOT
recomputed) · channel ablation NO_LSA 52.06 etc (STILL never recomputed) · repr
IDF_p2/SHIFT_m1 arms (STILL never recomputed) · LME partial (no results exist).

## 4. NOT CHECKED (and why)

- faiss PQ training rerun (needs faiss + hours; would test robustness, not the
  printed number, which is arithmetic over stored rows).
- ideas_r1/ablation + math_r1/repr arm recomputes incl. bootstrap CIs (needs
  sklearn reruns over cached features; time-box forced triage toward STOP-critical
  claims; listed above as still-never-audited).
- T2 164,256-row rerank CSV re-derivation (external drop; round 1 also NOT RUN;
  V3 checks the ceiling JSON, not the incoming CSV).
- cost_audit per-archive byte recompute; MODEL weights sha (2.4 GB, NOT RUN by
  any round); lit_r2 content vs novelty wrappers (no search protocol exists to
  audit against); ~130 remote refs (no fetch, read-only rule).
- Full-file coverage: working tree ≈1309 non-cache files; this audit executed
  code against ~10 of them and read ~30. See coverage_map.csv (this dir).

## 5. FRACTION GENUINELY AUDITED (honest)

- By files: round 1 ≈ 40 + this audit ≈ 15 substantive files of ≈1309 ≈ 4–5%.
  Expected answer: low. The baseline/ checkpoint mass (~1000 files) is data, not
  claims, and is correctly unaudited.
- By STOP-critical claims (gate inputs C1/C3/S3 + fair-BM25 + ladder + T3): 100%
  after round 1; this audit adds nothing there and finds nothing against them.
- By numbers printed in FINAL_STATE/REPORT: roughly two-thirds independently
  recomputed after round 1 + this work; the remainder is enumerated in the Task B
  roll-call above. The genuinely-new-mechanism items (F1–F6 in claims audit) rest
  on math_r1/quant, which round 1 covered, except their repr-side echoes, which
  nobody has recomputed.
