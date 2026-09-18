[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DECISION AUDIT — the "STOP" verdict (round 2; round-1 gaps only)

## 1. VERDICT (3 lines)

STOP-the-spend is justified as engineering judgment (magnitudes, ceilings,
0-for-history base rates), but STOP-by-prespecified-gates is UNPROVEN:
the gates were co-committed with their results, half-implemented, and
deviated from their own referee text — while the missing cells I computed
all corroborate the verdict's direction.
Keep STOP; strike the word "prespecified"; minute the deviations below.

## 2. Findings (5 fields each; list, not table: 5 columns won't fit 100 cols)

### F1 — HIGH — C1's second benchmark was never tested
Claim: C1 fails on "both benchmarks" (DECISION_TESTS.md:102).
Did: read coordinator/decision_tests.py t1() (lines 103-192); grepped
coordinator/*.py,*.json for any PerLTQA fair/frozen BM25.
Result: t1() builds RealTalk BM25 only. No PerLTQA (or LoCoMo) fair-BM25
exists anywhere in the repo. The AND-gate's RealTalk half fails (reproduced),
which logically suffices for failure — but "tested on both" is untrue.

### F2 — HIGH — C1's required CIs were never computed, and are irreproducible
Claim: gate needs "CI excluding 0" (decision_tests.py:23; REFEREE §5).
Did: read t1() verdict (lines 188-191, point estimates only, no boot() call);
checked LADDER_CACHE.jsonl (per-archive means only, 10 lines — no per-query
code rows stored); ran own archive-level bootstrap (AUDIT_T1_ARCHIVE_CI.json).
Result: query-level paired CI for C1 cannot be built from stored artifacts.
Supplementary archive-level check (n=10, crude) corroborates direction vs the
referee-primary textbook BM25: Hit@10 gap -3.83 [-5.67,-2.06], FR@3 gap
-3.26 [-5.79,-0.93], both exclude 0. Hole is real; verdict direction holds.

### F3 — HIGH — executed comparator deviates from referee spec, doubling gap
Claim: headline gap -7.80 pp Hit@10 (DECISION_TESTS.md:32; FINAL_STATE:26).
Did: read REFEREE §2/§5 ("textbook k1=1.2/b=0.75 as primary") vs
decision_tests.py:179 (strongest = max Hit@10 = frozen_idfonly);
decomposed the +10.35 from DECISION_TESTS.json T1 numbers.
Result: +10.35 = +6.38 tokenizer (legit, prespecified) + up to +3.97 from
post hoc best-of-4 selection of a degenerate k1=0/b=0 sum-of-IDF variant on
the eval gold (no held-out anywhere). Vs spec-primary textbook the gaps are
-3.83 Hit@10 / -3.26 FR@3 — still losses (F2: SIG at archive level), but less
than half the headline. Partly noted by round-1 claims audit (S3); the
decomposition and archive-level CIs are new.

### F4 — HIGH — T2 silently drops the second stored rerank path; it passes
Claim: "code's net contribution -0.33/+0.33/+1.07" (REPORT §5; DECISION_TESTS.md:46).
Did: recomputed every *_rrf60 vs BM25_full contrast with the same bootstrap
(AUDIT_RRF60.json); read decision_tests.py:80 (endswith('_bm25') filter).
Result: 15 stored RRF-path contrasts never mentioned in prose. On PerLTQA
(n=8265, best-powered benchmark) asym96_rrf60 = +1.48 [+0.45,+2.47] SIG —
passes the +1.0 gate on undisputed gold. LME/LoCoMo RRF arms all fail (several
SIG-negative), so no both-benchmarks rescue — but the "net contribution"
headline cherry-picks one of two rerank operators, and the referee-mandated
same-rerank-budget control (BM25+rerank) is missing from the CSV entirely,
making C3-as-written untestable. Round-1 explicitly excluded _rrf60: new.

### F5 — CRITICAL — "gates fixed before running" is false as stated
Claim: "Gates fixed BEFORE running" (decision_tests.py:3);
"written before any of this ran" (DECISION_TESTS.md:5).
Did: git log/show/ls-tree (commands in §3): 8bcdef5 commits REFEREE.md +
decision_tests.py + DECISION_TESTS.json + CASE_FOR/AGAINST atomically, 15 min
after ladder commit 74e21e1, 3 min before final e672192; parent tree contains
none of the 7 gate files; `git log --follow` = exactly one commit each.
Result: git cannot separate pre-fixation from joint authorship (round-1
integrity: NOT PROVEN). Stronger, new: REFEREE text itself quotes result
numbers (55.32→61.70, 48B 57.87, rerank nets) — it was written AFTER seeing
ladder/rerank data, so "before any of this ran" is self-refuting. Also
dropped without mention: referee conjuncts C2 (Hit@10 guardrail) and C4
(same arm both benchmarks). (C2 would also fail: -3.83 < -1.0 guardrail —
direction-robust, procedure-defective.)

### F6 — MED — S3 generalizes 8/30 archives to the whole benchmark
Claim: S3 "does not fire" for PerLTQA-corrected (DECISION_TESTS.md:104).
Did: read t3_perltqa_kltn.py (scope line 150: 8 archives, 2217/8265 queries);
__main__ of decision_tests.py never runs T3 (lines 194-220).
Result: full k<n-capped PerLTQA ladder never built; asym +0.30 on the small-
archive subset is generalized to the benchmark. T3's retraction (rank overflow
dead, sigma-noise conjecture live) is fairly reported; the gate verdict
overreaches its scope. (Producer-script/artifact mismatch already in round-1.)

### F7 — MED — storage/latency asymmetry is real but corpus-dependent, partly mismeasured
Claim: BM25 costs 76x/112x storage, ~100x latency (REPORT §5; FINAL_STATE:86-88).
Did: verified RealTalk from cost_audit.json (115008 / 670511 / 998654 B);
LME from memory_accounting.json + timing_summary.json (external package).
Result: RealTalk honest ratios 5.83x index-only, 14.5x with text — verified.
LME text 76x honest (237865248/3140232); but 112x is a Python-object size —
the same class FINAL_STATE:85 disowns for pickle (fair postings-payload ratio
81.5x; stats-json 20x). Latency 14.9→17.6 vs 0.14 rests on n=6 queries; the
clean first-stage pair runs the other way (code scoring 0.05-0.06 ms vs BM25
0.12 ms); qscale96 14.89 ms vs float_std32 0.059 ms (250x intra-family)
unresolved. Range is 6x-90x by corpus, not a general "100x". Cost/latency was
explicitly out of round-1 scope: new.

### F8 — LOW — labels and loose ends (checked, mostly fine)
164,256-row claim verified exactly (164257 lines incl. header). LoCoMo's only
qscale C3 pass sits on disputed gold (already disclosed in prose). LME "470
clusters" = 470 singletons (archive==qid), so "archive-clustered" is vacuous
there. decision_tests.log matches DECISION_TESTS.json to the printed digit.

## 3. Detail: paths, lines, commands

- Gates in prose: decision_r1/cost/REFEREE.md §2 (textbook-primary, 3-benchmark
  rescore), §4 (same-rerank-budget; strong−weak ≥1.0 AND code+rerank−BM25 ≥1.0),
  §5 (C1 both +2.0; C2 Hit@10 lowerCI>−1.0; C3 +1.0 no benchmark qualifier;
  C4 same arm; S1/S2/S3; N1/N2; Q9). Gate in code: coordinator/decision_tests.py
  :22-26 (C1/C3/S3 only), :45-54 boot(), :80 _bm25 filter, :154-155 4 variants,
  :179 max-Hit@10 pick, :188-191 CI-less verdict, :194-220 __main__ (no T3).
  T3 scope: coordinator/t3_perltqa_kltn.py :60-69 scorers, :115 k_eff, :149-151
  8-archive scope. Readouts: DECISION_TESTS.md :5,:19-37,:46,:54-69,:98-107;
  FINAL_STATE.md :77-88,:104-121; REPORT.md §4 :210-219, §5 :244-258.
- Git (env: GIT_DIR=.../.git/worktrees/_wt_top10, GIT_COMMON_DIR=.../.git):
  `git log --pretty='%H %ad %s'` → 74e21e1 21:19:29 → 8bcdef5 21:34:17 →
  e672192 21:37:27; `git show --stat 8bcdef5` (10 files, +1874, REFEREE+tests+
  JSONs+verdict one commit); `git ls-tree -r 8bcdef5~1 | grep -i referee|
  decision_tests` (empty) vs at 8bcdef5 (7 files); `git log --follow` for both
  gate files = single commit 8bcdef5.
- Recompute: `wc -l .../text_rerank_per_query.csv` → 164257 (=164256+1 header;
  164,256 claimed ✓). Probes: decision/audit_probes.py → AUDIT_RRF60.json,
  AUDIT_T1_ARCHIVE_CI.json (same boot(): paired archive-clustered, 20000 reps,
  seed 20260916). Ratios: python3 -c from cost_audit.json (670511/115008=5.83;
  (670511+998654)/115008=14.51) and memory_accounting.json LME block above.
- No source tree written: all probes read inputs, wrote only this directory.

## 4. Steelman: the strongest honest case STOP is premature (ranked, costed)

Gap to close: 7.80 Hit@10 / 7.23 FR@3 vs executed idfonly; 3.83 / 3.26 vs
spec-primary textbook. Ceilings that cap the dream: word-only full float 56.03
trails textbook by 5.67 and idfonly by 9.64 (LADDER.json) — a lossy code under
its ceiling cannot win outright; largest observed single effects: scorer swap
+6.98 FR@3 (T3 asym−qscale @384, PerLTQA subset), RRF pool +5.67 @100 (REPORT
§4, coarse era), IDF^p rare-band +4.78 FR@3 SIG (subgroup, hurts PerLTQA SIG).

1. Fusion-vs-FAIR recall test (cheapest, ~minutes CPU: fair-BM25 pools are a
   T1-type 14 s rescore; code top-50s stored in incoming rankings/): RRF was
   measured @100 vs coarse only. The 49 CODE-only queries (REPORT §4) may
   survive against fair BM25. Win shape is NARROW (complementarity), not C1.
2. Missing C1 half: PerLTQA fair BM25 (~2 min CPU, 30 small archives). Won't
   rescue (never-won-both predicts wider lead); needed for gate validity.
3. RealTalk asym-48B ladder (moderate, ~1-3 CPU-hr at ladder.log pace):
   T3's "wrong readout" never tested where the verdict bites. Could plausibly
   halve the 3.8 textbook gap; nothing in evidence closes 7.8 vs idfonly.
4. Q9 owner answer (zero compute): FINAL_STATE concedes a text-free deployment
   reopens the 12 B question. Only non-empirical decider. Unanswered.
5. Word-only 48B asym + truncated-float ceilings (moderate 1-4 CPU-hr refit):
   ceiling math (56.03 < 61.70) makes outright win implausible; needs a
   denoising surprise. Poor base rate; CASE_FOR #1 agrees.
6. Held-out re-evaluation of best-of-4 (moderate: T1 code per-query rows are
   not stored, so pairing needs a ladder rerun): shrinks idfonly→textbook
   gap on paper only; changes no retrieval number.

## 5. Could NOT check (and why)

- Full PerLTQA k<n ladder (needs 8-30 SVD refits; ladder.log pace ≈ hours) —
  S3's full-scope claim stays untested.
- qscale96 14.89 ms timing composition (needs the external timing harness;
  n=6 either way — too thin to adjudicate the 250x intra-family anomaly).
- Held-out generalization of best-of-4 (no query splits exist anywhere).
- LoCoMo adjudicated gold; literature novelty; sibling branches (out of role).

## 6. Answer to E

STOP-the-spend: JUSTIFIED (direction corroborated in every cell I could fill:
archive-level CIs exclude 0 against textbook too; RRF paths fail 2/3 or need
disputed gold; ceilings sit below both comparators; never-won-both unbroken).
STOP-by-prespecified-gates: UNPROVABLE (F5 alone voids "prespecified"; F1/F2/F4
void "as written"). Publishable form: "exploratory decision rule applied to
reproduced numbers — gates post hoc, deviations minuted (textbook→best-of-4,
C2/C4 dropped, RRF path omitted, PerLTQA fair-BM25 missing)". Optional cheap
close-out before external citation: steelman items 1+2 (~minutes CPU).
