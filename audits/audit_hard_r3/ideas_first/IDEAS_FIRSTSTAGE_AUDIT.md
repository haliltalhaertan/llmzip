# IDEAS_FIRSTSTAGE_AUDIT — ideas_r1/firststage + ablation (dark-corner audit, round 3)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## (1) VERDICT

All quality and cost headline numbers in both lines reproduce exactly from the raw per-query rows
(firststage max diff 1.4e-14 pp; ablation max diff 7.1e-15); pools are built with no gold knowledge.
One real defect: firststage REPORT.md's latency table disagrees with its own RESULTS.json by 28-40%
with no generating code or provenance. No decision document quotes the fusion recommendation.

## (2) Findings table

| ID | Severity | Claim / file audited | What you actually ran | Result |
|----|----------|----------------------|----------------------|--------|
| F1 | HIGH | firststage REPORT.md latency table (lines 108-112) vs RESULTS.json timings | Compared every REPORT timing number to RESULTS.json values verbatim | MISMATCH on all 5 numbers (28-40%): REPORT CODE 0.99/1.90 vs RESULTS 1.37/2.59 ms; BM25 1.22/2.30 vs 1.70/3.20; RRF-marg 0.96/1.78 vs 1.33/2.45; UNION 0.08/0.11 vs 0.103/0.155; build 0.04 s vs 0.095 s |
| F2 | LOW | firststage REPORT.md BM25 index size 1,450,229 B (the round-2-flagged pickle number) | Independently rebuilt the BM25 index from data/*.json docs with stdlib pickle (same schema) + cross-read coordinator/cost_audit.py + cost_audit.json | Bit-exact match all 10 archives and totals (1,450,229 + 998,654 text). REPORT discloses the serialization explicitly; coordinator ACCEPTs with compact-varint alternative (670,511 B). Ratios ~13x/~21x are serialization-dependent (5.8x/14.5x under compact) — conclusion direction unchanged |
| F3 | LOW | firststage RESULTS.json + REPORT.md quality tables (pool Hit/recall/ceiling 6 M x 4 arms, own metrics, 2x2, gold dist) | Recomputed every aggregate from per_query.jsonl (705 rows); 23 REPORT spot-checks vs RESULTS.json | All match (pool max diff 1.4e-14; own 7.1e-15; 2x2 exact; gold dist exact incl. 319 single-gold, max 22). One bootstrap contrast (RRF-BM25 Hit@100) re-ran bit-exact incl. CI bounds |
| F4 | LOW | ablation RESULTS.json + REPORT.md (8 arm x scorer cells, contrasts, cost table) | Recomputed all 8 summary cells + by_archive n-sums from per_query.jsonl (5640 rows); 12 REPORT spot-checks; cost widths/build times vs RESULTS.json | All match (max diff 7.1e-15). Z widths FULL 23,422-33,257, NO_LSA -32 cols, NO_CHAR 7.7-9.9k, builds 9.4/11.0/3.5 s, 12 B/arm all as reported. LSA_ONLY blocked as documented |
| F5 | LOW | Pool construction gold-knowledge (highest-value check): firststage.py lines 294-301, 311-326; det_top10 tie rule | Code inspection + empirical: reconstructed all 4230 UNION pools from stored top-500 halves; recomputed all pool/own metrics from ids+gold; checked neither-counts, pool-size bounds, list integrity | CLEAN: 0 UNION reconstruction mismatches; 0 metric mismatches; pools miss gold on 270 (M=10) down to 10 (M=500) queries so gold cannot be in-pool by construction; union poolsize always <= M; all 2115 ranking lists valid permutations; tie rule (audit_baseline_lib.py:79-83, salt "top10-r1") takes only (scores, archive_id) — gold-unaware |
| F6 | LOW | G6 FAIL disclosure (BM25 top10 704/705 vs audit/per_query_bm25_corrected.jsonl; RT01_q016 tie story) | Rescored RT01_q016 both summation orders from production pkl + data docs; re-ran set-order scoring under PYTHONHASHSEED=0/1/42 | Corroborated: fwd/rev orders differ by 1 ulp (8.9e-16) and flip the 10th slot (596 vs 249, neither gold); set-order tail is [249,605] under seeds 0/1 vs [605,249] under seed 42 — exactly as REPORT claims; gate stays FAIL in RESULTS.json, not redefined |
| F7 | LOW | Whether firststage conclusions (RRF fusion 81.28/66.15 recommendation) are quoted anywhere downstream | Scoped grep of decision_r1/ + coordinator/ for headline numbers, "fusion", "RRF", "firststage" | NOT quoted in any decision_r1 STOP/GO document (those discuss only the unrelated LME rerank-§E experiment). Only consumers: coordinator/ideas_audit_v2.json (ACCEPT, values match exactly) and rerank_ceiling.json (CODE/BM25 ceilings consistent). No decision rests on the fusion claim |
| F8 | LOW | RRF fusion integrity (k=60, full-ranking fusion, no gold) | Full independent rescore of all 705 queries from production pkls + data docs (CODE qscale, BM25 index traversal, RRF fuse, det tie rule), top-10 vs stored lists | 705/705 match on CODE, BM25, and RRF top-10 (0 mismatches). Fusion claim rests on verified rankings |

## (3) Per-finding detail

Paths (all under /mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/ideas_r1/):
firststage/REPORT.md, firststage/RESULTS.json, firststage/per_query.jsonl (705 lines, 8,924,289 B),
firststage/firststage.py (644 lines), ablation/REPORT.md, ablation/RESULTS.json,
ablation/per_query.jsonl (5640 lines, 1,861,690 B), ablation/ablation.py (507 lines),
ablation/FIDELITY_GATE.json. Corroborating in-repo files: coordinator/ideas_audit_v2.json
(verdict ACCEPT, 20/20 pass), coordinator/cost_audit.py + cost_audit.json (ACCEPT; compact 670,511 B),
coordinator/rerank_ceiling.json, audit/audit_baseline_lib.py:79-83 (det_top10), :86-95 (hrn),
audit/per_query_bm25_corrected.jsonl. All probes used python3 + numpy + stdlib only
(no sklearn needed); worker scripts were never executed (they write into their own
read-only directories). Scratch probes in /tmp (not deliverables): fs_recompute.py,
fs_report_check.py, ab_recompute.py, fs_poolcheck.py, fs_bytes.py, fs_g6.py, fs_seed.py,
fs_boot.py, fs_rrf.py.

F1 (HIGH — REPORT timings vs RESULTS.json). REPORT.md lines 108-112:
"CODE score+full-rank mean 0.99 ms / p95 1.90 ms; BM25 ... mean 1.22 ms / p95 2.30 ms;
RRF fusion+rank marginal mean 0.96 ms / p95 1.78 ms ... UNION ... mean 0.08 ms / p95 0.11 ms ...
Index build one-off 0.04 s." RESULTS.json timings (observed output of `python3 /tmp/fs_recompute.py`):
CODE 1.3748/2.5883, BM25 1.6966/3.1978, RRF 1.3317/2.4550, UNION 0.1034/0.1550 ms,
build 0.095328799 s. Every number disagrees (28-40%; build 2.4x). firststage.py writes
per_query.jsonl (line 407) and RESULTS.json (line 609) but contains no REPORT-writing code
(grep "REPORT|report" hits only docstring/gate comments), so REPORT.md is hand-authored and its
timings have no provenance — they come from a different run/machine. Impact is bounded:
machine ordering is preserved (CODE < BM25 in both), and the "~3.2 ms honest end-to-end RRF"
claim equals the REPORT-number sum (0.99+1.22+0.96=3.17) — recomputed from RESULTS.json
timings it would be ~4.4 ms. No quality or storage conclusion depends on timings.
Not CRITICAL: no quality/storage number or conclusion is wrong.

F2 (LOW — pickle bytes). `python3 /tmp/fs_bytes.py` rebuilt {N, postings, idf, doc_lens, avglen}
per archive from data/RT*.json with pickle.HIGHEST_PROTOCOL. Observed: all 10 per-archive
index bytes (140402, 143725, 136323, 133730, 140177, 151742, 160580, 134946, 148980, 159624)
and text bytes match RESULTS.json exactly; totals 1,450,229 / 998,654 exact. REPORT.md lines
100-107 states the serialization explicitly ("ACTUAL serialized inverted index per archive
(pickle.dumps with HIGHEST_PROTOCOL of ...)") and separates index from raw text, and lines
32-35 frame fusion's incremental cost as the index only (~1.45 MB) given a reranker keeps text
anyway. The round-2 concern (pickle inflates vs a fair encoding) is therefore disclosed, not
hidden; the coordinator's independent cost_audit.py reproduces the same pickle total and adds
the compact-varint fair number (670,511 B, ratio 5.83x index-only / 14.51x with text, vs REPORT's
~13x/~21x). The qualitative conclusion (BM25 costs far more than 115,008 B) holds under both.

F3 (LOW — firststage aggregates). `python3 /tmp/fs_recompute.py` observed:
rows=705, unique qids=705; pool max|mine-stored|=1.421e-14 over 72 cells; own max diff 7.1e-15;
all six 2x2 rows exact (e.g. M=100: 484/49/67/105, oracle 85.1064); gold-size dist exact
(1:319, 2:178, 3:92, 4:49, 5:24, 6:15, 7:7, 8:4, 9:7, 10:4, 14:1, 17:1, 19:2, 21:1, 22:1).
`python3 /tmp/fs_report_check.py`: 23/23 REPORT spot-checks OK to rounding (direct-answer table,
all six contrasts incl. CIs and W/L, own FR@3 line 74-75, 172/705 CODE-miss and 105 oracle-miss
counts). `python3 /tmp/fs_boot.py`: RRF-BM25 pool-Hit@100 point 3.1206 CI [1.2295,4.9159]
bit-exact vs stored. Coordinator ideas_audit_v2.json independently reports recomputed pool
metrics match to 0.00e+00 and RRF(k=60) top10 rebuild 0/705 mismatches — consistent with mine.

F4 (LOW — ablation aggregates). `python3 /tmp/ab_recompute.py` observed: 5640 rows
(705 x 4 live arms x 2 scorers, balanced); summary max diff 7.105e-15, 0/8 bad cells;
12/12 REPORT table values OK (FULL/sym 46.5248/exp 46.6809, FULL/qscale 49.6454/22.4099,
NO_LSA/qscale 52.0567/25.8543/33.9007, NO_CHAR and WORD_ONLY cells); NO_LSA-FULL/qscale
contrasts match REPORT (+2.41 [-0.28,+5.15] Hit@10; +3.44 [-0.56,+7.56] FR@3;
+4.40 [-1.22,+9.96] Hit@3); 20/20 sampled hit10-from-ids OK (SAMPLE); by_archive n-sums = 705
every cell; per-archive n (85/70/73/71/70/74/70/70/63/59) consistent with firststage's 705.
Cost section: FULL Z widths 28003/33257/32151/29399/32230/25379/28084/23422/27682/28171
(range 23,422-33,257 as REPORT claims); NO_LSA exactly -32 cols each; NO_CHAR 7669-9910;
build totals 9.368 s / 11.022 s / 3.541 s (REPORT 9.4/11.0/3.5 s); payload 12 B every arm;
LSA_ONLY blocked with the min(Z.shape)>96 assertion message as documented.

F5 (LOW — pool gold-knowledge, the highest-value check). Code: UNION pools
(firststage.py:295-301) are top-(M/2)+top-(M/2) dedupe of the two full rankings; CODE/BM25/RRF
pools (:311-317) are ranking prefixes; oracle-union (RESULTS complementarity) is a post-hoc
max() labelled "gold-using upper bound, NOT a deployable method" (:491-495, REPORT lines 83-90
call it "NOT deployable" in the table header). No gold variable enters pool construction.
`python3 /tmp/fs_poolcheck.py` observed: 0/4230 UNION-pool reconstruction mismatches;
0 pool/own metric recompute mismatches; neither-in-pool counts 270/209/150/105/49/10 at
M=10/20/50/100/200/500 (a gold-stuffed pool would show 0); all union poolsizes <= M;
0 ranking-list violations over 2115 lists; (N,len) pairs show correct K=min(500,N) truncation
for the four small archives (410/422/453/476). det_top10 uses only scores + archive hash.
Conclusion: downstream rerank-ceiling claims are not invalidated by pool construction.

F6 (LOW — G6 disclosure). `python3 /tmp/fs_g6.py` observed on RT01_q016
(gold [6,22,28,52,87,93,105,135,145]): fwd/rev summation orders differ by max 8.9e-16 (1 ulp);
fwd top-10 tail [605,596], rev tail [249,605]; rank-9/10 scores 5.501322839570598/…597;
no tied row is gold. Reference file tail [605,249]; worker tail [605,596].
`PYTHONHASHSEED=0/1/42 python3 /tmp/fs_seed.py` observed set-order tails [249,605]/[249,605]/
[605,249] — exactly the REPORT's "seeds 0/1 pick {249,605}, seed 42 picks {605,249}" claim.
The gate is recorded FAIL in RESULTS.json with cause and 58-aggregate sensitivity (max 0.0000 pp),
not redefined. Minor precision note: I observe a 1-ulp cluster (2 exact-tied + 1 ulp-adjacent)
rather than a literal 3-way exact tie under every order — the REPORT's substantive point
(cut decided by float noise, zero metric impact) is unaffected.

F7 (LOW — downstream quotation). decision_r1 grep for 81.28/66.15/fusion: no hits tying to
ideas_r1 (only an unrelated "confusion" line in kill/CASE_AGAINST.md:100). RRF/firststage hits
in decision_r1/cost/REFEREE.md, keep/CASE_FOR.md, kill/CASE_AGAINST.md all concern the separate
LME text-rerank experiment (§4/§E/§5), never the RRF-fusion numbers. ideas_audit_v2.json quotes
the pool/ceiling numbers exactly (verified equal to RESULTS.json) with verdict ACCEPT;
rerank_ceiling.json REALTALK/RT_BM25 ceilings equal firststage CODE/BM25 values
(75.6028/78.1560 Hit@100; 61.3026/62.2551 ceil). UNVERIFIED whether any external (out-of-tree)
document cites the fusion recommendation — out of scope for this repo audit.

F8 (LOW — RRF fusion integrity). `python3 /tmp/fs_rrf.py` (independent rescore from
bench3/.../rt_repr/RT*.pkl production C/QC plus data docs; qscale + BM25 index traversal +
RRF k=60 + det tie rule) observed: checked=705, code_top10_mism=0, bm25_top10_mism=0,
rrf_top10_mism=0. (Zero BM25 mismatches here is consistent with G6: this compares against the
worker's sorted-order lists, while G6 compares against the hash-order reference file.)

Context (already known, NOT new): the CODE leg of these pools uses the transductive pipeline
fitted on the test archive (round-2 decisive finding: inductive collapse 46.52->18.16 sym /
49.65->20.00 qscale on RealTalk k=96 — the same regime as this 12-byte arm). The firststage
REPORT does not mention this; absolute CODE/RRF pool levels therefore carry the known inflation.
BM25 and the pool-construction integrity result are unaffected. Future honest-regime reruns of
this line would need inductive refits (reference: audit_hard_r2/ROUND_B_8roles_1318/code/
t_inductive_all10.py); not re-measured here.

## (4) What you could NOT check and why

1. Six of seven bootstrap contrast CIs (only RRF-BM25 pool-Hit@100 re-ran bit-exact): same
   deterministic code path (fresh default_rng(20260916) per contrast), so risk is low, but each
   CI was not individually re-executed. Need: rerun boot_contrast per pair from per-query rows
   (numpy only, minutes).
2. Ablation arm quality beyond row-level replay (whether NO_LSA truly beats FULL): rebuilding
   arms needs sklearn/scipy (~/muse-work/ml-python) AND ablation.py writes into its own
   read-only directory, so a rerun would violate the read-only rule; copying the script to /tmp
   with redirected outputs was out of the time budget. Need: a redirected rebuild + rescore.
3. RRF/UNION correctness below top-10 (only top-10 compared in F8; pools verified from stored
   top-500 lists, which themselves were not re-derived beyond top-10). Full top-500 RRF
   comparison data exists in /tmp/fs_rrf.py's method — need one longer run storing full lists.
4. Whether a real (non-oracle) reranker can approach the ceilings: ceilings are oracle bounds by
   construction (REPORT states this); no reranker artifact exists in these directories.
5. Other datasets/widths: both lines are RealTalk-only, k=96 12-byte by design; nothing to check.
6. External citations of the fusion recommendation outside this repo tree: out of scope.
7. F1 root cause (which run/machine produced REPORT's timings): no provenance recorded; the
   worker log (ideas_r1/firststage.log) quotes quality numbers but no timings. UNVERIFIED.
