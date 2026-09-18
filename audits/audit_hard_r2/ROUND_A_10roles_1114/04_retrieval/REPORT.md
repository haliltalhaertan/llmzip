# 04_retrieval — comparator fairness and cascade claims

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Independent hard review round 2 (retrieval role). Neutral: prior agent reports and
coordinator summaries were treated as fallible claims, every load-bearing number below
was recomputed with own code from stored artifacts. Read-only sources; no checkouts,
commits, or source repairs. All probes ran single-thread BLAS with
`PYTHONDONTWRITEBYTECODE=1`; each completed in one bounded run (see blockers note in
[evidence.json](/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/04_retrieval/evidence.json)).

## Outcome (one paragraph)

The headline comparator reversal is arithmetically solid and the cascade's flagship
result stands, but the pilot's gate reporting has three material blemishes: (1) the
executed C1 gate uses an in-sample best-of-four BM25 (65.67) while the governing
referee contract names textbook BM25 (61.70) as primary — outcome-robust (C1 FAILs
both ways: best code trails by 3.26pp FR@3 vs textbook, 7.23pp vs max) but unminuted;
(2) the "C3 fails 1-of-3 on disputed gold only" summary is wrong — PerLTQA
`float_raw32_bm25` passes (+1.13pp SIG) on undisputed data, and the omitted-by-design
`_rrf60` diagnostic adds three more SIG passes on PerLTQA, so passing arms exist on
2 of 3 datasets (flagship qscale passes only on disputed LoCoMo); (3) the "328 both
miss / 170 unreachable" decomposition is unverifiable from any stored per-query rows
(it needs unstored sym rankings). Candidate recall and oracle ceilings verify exactly
(350/183/172; 49/67 complementarity). STOP of the code-vs-BM25 first-stage programme
remains the contract-correct readout (C1 fails under every comparator; referee STOP
triggers on C1 alone), but it is a **local** verdict: it does not dispose the dense/
F1/residual lines, any text-free deployment (Q9, unanswered), or the RRF-fusion
first stage, which beats BM25 alone on pool quality.

## Severity-ranked findings

**S1 — C3 summary understates passes (reporting, medium).**
`DECISION_TESTS.json` stored contrasts (verified bit-identical by own bootstrap
re-run, probe_p2) show `float_raw32_bm25` on PerLTQA at +1.13pp FR@3, CI
[+0.85,+1.44], SIG, `passes_C3_gate=true` — an undisputed-benchmark pass the
`FINAL_STATE.md`/`DECISION_TESTS.md` "1 of 3, on disputed-gold LoCoMo" sentence
omits. Correct statement: at least one passing `_bm25` arm on 2 of 3 datasets;
flagship qscale passes only on LoCoMo. Gate C3 as literally written ("best
code+rerank ≥ +1.0pp") therefore passes on PerLTQA. STOP still holds via C1, but
the dissolution narrative ("reranker erases everything everywhere") overreaches:
on PerLTQA the code+rerank combination significantly beats BM25 alone.

**S2 — `_rrf60` diagnostic excluded from gate evaluation (method, medium).**
The incoming package preselected two rerank operators (`RAPOR.md` p.21:
BM25-rerank primary + RRF60 fusion diagnostic over the same 50 candidates, no new
candidates; `PLAN_BEFORE_RUN.json` pre-registered). The pilot gated only `_bm25`.
Own CIs (same 20000-rep archive-clustered contract, `rrf60_ci.json`): PerLTQA
`asym_rrf60` +1.48 SIG, `float_raw32_rrf60` +2.80 SIG, `float_std32_rrf60` +2.57 SIG
all pass C3; LME best (`hamming_rrf60` +2.23) misses SIG by 0.08pp on the lower
bound; LoCoMo `_rrf60` all fail (two SIG-negative). Two consequences: (a) the
inversion phenomenon is operator-dependent — `_bm25` inversions 4/3/6 of 10 vs
`_rrf60` inversions 2/2/1 (own recomputation) — so "first-stage quality is
irrelevant post-rerank" is true of BM25-rerank and largely false of RRF fusion;
(b) the production arm qscale fails under both operators on undisputed data
(+0.33ns / +0.83ns on PerLTQA; −0.33ns / +0.78ns on LME), which is the finding
that actually matters and survives.

**S3 — C1 executed against in-sample max, referee names textbook (method, low-medium, outcome-robust).**
Referee `decision_r1/cost/REFEREE.md` §5: comparator is "fair (textbook k1=1.2/b=0.75)
BM25". Executed `decision_tests.py` T1 picks max Hit@10 over four
tokenizer×scorer variants on the same 705 evaluation queries (no held-out split)
and gates on `frozen_idfonly` (65.67/40.02). Selection premium over textbook:
+3.97pp on both metrics. "Strongest honest BM25" therefore means "strongest
in-sample lexical baseline in our scorer family" (prior round's wording, endorsed);
the `k1=0/b=0` variant is the degenerate IDF-sum limit, not BM25 as the field uses
the term — quote 61.70 as "BM25", 65.67 as "strongest lexical". C1 FAILs either way
(best code −3.26 FR@3 vs textbook, −7.23 vs max; T1 verdicts are point gaps with no
bootstrap despite the referee's CI requirement — moot at these margins, but a
contract gap). T1 BM25 numbers were not re-rescored here; prior round `au_c6_bm25.py`
reproduced three variants to 0.00pp and the fourth within 0.14pp with independent
code — cited as explicit verification.

**S4 — 328/170 decomposition not reproducible from stored rows (evidence, low).**
REPORT §5 "350 hit, 183 reachable, 172 unreachable" verifies exactly from
`ideas_r1/firststage/per_query.jsonl.gz` (qid buckets persisted in
`realtalk_reachability_qids.json`), as do 49 CODE-only / 67 BM25-only @100 and all
36 pool/ceiling cells (max diff 1.4e-14) plus `rerank_ceiling.json` cross-checks.
But "328 queries both our scorers miss, 170 outside top-100" refers to the
sym+qscale oracle pair (REPORT §7: oracle saturates at ~55%; (705−328)/705=53.5%),
and no sym per-query rankings are stored anywhere — qscale+BM25 both-miss@10 is 270,
not 328, under every @k/FR@3 reading tried. The 51.8% unreachable fraction inherits
this gap. Direction (large unreachable mass) is corroborated by the verified 172 and
by PerLTQA/LME ceilings, but 328/170 must be cited as unstored-computation, not as
replicated fact.

**S5 — BM25 is three different implementations (interpretation, low).**
T1-fair (frozen tokenizer + stopwords, textbook/idf-only, tie-hash ranking),
firststage (k1=1.5/b=0.75, `\w+` lower, doc-order scoring; RealTalk Hit@10 54.18),
T2/incoming (unicode word/number tokens, no stemming/stopwords, query terms once).
Within-artifact contrasts are valid; cross-artifact BM25 numbers (e.g. 61.70 vs
54.18 on the same 705 queries) must never be mixed. T1 docstring claims "1–2 grams"
while `decision_tests.py:toks/score` implements unigrams — doc/code mismatch, shared
code path so metric-neutral. Storage quoting is inconsistent across artifacts:
pilot REPORT §4 prints the honest varint index (670,511 B, 5.83×) and bans the
pickle number, but `ideas_r1/firststage/REPORT.md`'s cost table quotes the pickle
1,450,229 B as "BM25 index". The text-dependency conclusion itself verifies
(LME raw UTF-8 237.87 MB = 76× codes+sigma; IDF objects 351 MB = 112×).

## Verified (own recomputation, tolerances stated)

- T1 denominator 705 (8944 docs, 10 archives) recomputed from `top10_comparison_r1/data/RT*.json`; qid set identical across T1 filter, firststage rows, band file.
- T1 gap arithmetic exact; ladder arms copied exactly into T1; C1 FAIL vs textbook (−3.26 FR@3) and vs max (−7.23).
- T2: 164,256 rows = 16 methods × 10,266 qids; denominators 470/8265/1531 match distinct qids (lists+hashes in `t2_query_identities.json`); all 48 level means exact (≤2.2e-14); all 15 `_bm25` CIs bit-identical; inversions 4/3/6 exact; candidate depth M=50 for every code arm, full-archive for `BM25_full`.
- Ceilings/recall as above; no RealTalk measured rerank exists in T2 (incoming RAPOR: only numeric caches in permitted backups — a stated absence, not a hidden one).
- RRF k=60 preselected (`firststage.py:10,60,284`; RAPOR + PLAN_BEFORE_RUN); not post-hoc; no cross-dataset winner-shopping in the source package.
- No RealTalk offsets transferred: asym−qscale FR@3 = −3.62 LME / −1.58 LoCoMo / +0.29 PerLTQA from stored levels.

## STOP scope: local only

Justified locally: stop optimizing the TF-IDF/SVD sign-code family as a
BM25-beating first stage (C1 fails vs textbook and vs max; flagship qscale+rerank
fails C3 on all undisputed data under both operators; ceilings show the bottleneck
is representation, and standardized float beats sign — prior round). Not justified
more broadly: (a) gates C1–C4/N1–N2 were written for the code-vs-BM25 race only;
(b) RRF fusion (code+BM25, preselected k=60) beats BM25 alone on RealTalk pool
quality with SIG CIs and deserves its own gate if any work continues — the pilot
measured it but never gated it; (c) dense-MRL/residual/F1/KV lines, LoCoMo gold
adjudication, and owner question Q9 (text-free deployment, which changes the
comparator and revives the 12-byte question) are outside this evidence entirely;
(d) every RealTalk interval is wide (10 clusters) and everything there is
exploratory by the pilot's own admission. Same-CLI partial independence noted:
this audit shares the CLI lineage with prior rounds; mitigation was own-code
recomputation and the two new quantifications (`_rrf60` CIs, RRF-vs-BM25 inversion
split), not re-reading of prior conclusions.

## Limits and NOT RUN

- No T1 BM25 rescore re-execution (prior-round verified; §S3). No rerank
  re-retrieval (no text for RealTalk; T2 trusted at CSV-arithmetic level after
  exact level/CI reproduction — ranking internals above the CSV not re-derived).
- No M-sensitivity for T2 (fixed M=50); T2 effect sizes are M-conditional.
- LoCoMo gold dispute not adjudicated; LoCoMo passes quarantined throughout.
- Cost/latency not re-measured. PerLTQA T3, ITQ, geometry, F1/dense/KV/storage/
  portability/governance out of role scope (see evidence.json).
- `compute.sh` root lock was unwritable from this role directory (read-only
  outside assigned dir); probes ran as bounded single-thread direct executions,
  each completing well within the 180s cap — serialization across the ten agents
  was therefore not enforced for these runs; all probes were CSV/JSON-level
  (light) except the numpy bootstraps, which are still small.

## Files in this directory

- `REPORT.md` (this file), `STATUS.md`, `COVERAGE.csv`, `evidence.json`
- `DECISION_TESTS.orig.json`, `rerank_ceiling.orig.json`, `firststage_RESULTS.orig.json` (read-only copies)
- Scripts + outputs: `probe_p1_t2.py/.out.txt`, `probe_p2_rrf60ci.py/.out.txt`, `rrf60_ci.json`, `probe_p3a_inspect.py`, `probe_p3b_ceiling.py/.out.txt`, `t2_query_identities.json`, `realtalk_reachability_qids.json`
- Mechanically counted checks: 22 evidence rows in evidence.json, 25 COVERAGE.csv rows (22 REVIEWED, 1 SAMPLED-EXTERNAL T1-rescore, 1 SAMPLED-STORED fusion-pool, 1 NOT RUN sym-pair 328).
