[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DATA AUDIT — dataset and ground-truth integrity (round 2)

Role: dataset/ground-truth integrity. Round-1 work (numbers/integrity/claims/repro)
is not repeated; already-known issues are not re-reported as new.
All source trees were read-only. All scripts/outputs below are in this directory
(`audit_hard_r2/data/`). No citation, number, path or result is invented:
everything traces to a listed file, line and command.

## 1. VERDICT (3 lines)

No dataset defect overturns the STOP verdict — every arm comparison runs on
identical question sets and golds within its pipeline, and the LoCoMo 1531/1535
gap is resolved to 4 identified partially-golded items worth at most 0.26 pp.
But the RealTalk gold is 6.5% incomplete (46/705 queries carry silently dropped
evidence, contradicting the data report), and the publication's headline table
still quotes the handicapped BM25 (54.18) while the fair number (65.67) lives
only in the decision appendix — the "give your tokenizer to the rival" rule is
satisfied in the verdict, not in the numbers most readers see.

## 2. Findings

Check method lives in section 3 per finding; this table is the index.
(4-column shape is a terminal-width constraint; the required "what you did"
content is in section 3, not dropped.)

| ID | Sevr | Claim audited | Result |
| --- | --- | --- | --- |
| F1 | HIGH | RT gold complete | 46/705 partial, report says none |
| F2 | MED | LoCoMo 1531 v 1535 | Resolved: 4 items named, <=0.26pp |
| F3 | MED | Fair BM25 in final nrs | Headline uses 54.18, not 65.67 |
| F4 | LOW | T1 "1-2 grams" | Code is unigrams-only; no effect |
| F5 | LOW | Dup docs inflate/deflate | RT 6 twin-q; LME 0; PQ sample 0 |
| F6 | LOW | D30:05 id format | Exact-match drops valid evidence |
| OK1 | — | Pool identity in-pipeline | Same q/gold/N across arms |
| OK2 | — | Cross-pipeline qsets | RT/LME/HIZ identical qids |
| OK3 | — | Empty/OOR docs | Zero everywhere checked |

## 3. Per-finding detail

### F1 (HIGH): 46 RealTalk queries have incomplete gold; data report claims zero

- Audited claim: `top10_comparison_r1/data/REPORT.md:31-36` — "Unresolved-annotation
  detail: none beyond these 23 — every listed evidence dia_id in the 705 valid
  queries resolved (recompute equality proves it)."
- What I did: independent recompute from raw chats with the project's own
  normalizer (`export_realtalk.py:48-66`, regex `D\d+:\d+`, keep only ids in
  `id_to_row`), over all 10 caches
  (`bench3/runs/b3a_realtalk/rt_repr/RT*.pkl`) + raw chats
  (`bench3/REALTALK/data/Chat_*.json`). Script: `inventory_gold.py` in this dir.
- Result: **46/705 (6.5%) valid queries have ≥1 raw evidence token that resolves
  to no document; 72 tokens dropped silently.** Examples: `RT01_q071` (`D18:8`
  unresolved, gold keeps 3/4: rows 512,568,570), `RT02_q020` (4 of 6 tokens
  unresolved, gold keeps rows 35,132). Full list in `audit_inventory_gold.json`
  (`RT_partial_examples` + counts `RT_partial_valid_with_unresolved: 46`).
- Cross-check: the project's own `top10_comparison_r1/audit/lexical_audit.json`
  agrees exactly (`n_partial_valid_with_unresolved: 46`, same example qids), so
  two independent code paths confirm it and the REPORT.md sentence is wrong.
  The "recompute equality" cited as proof is circular: it proves cached gold ==
  lossy recompute, not that all raw evidence resolved.
- Impact: both arms are scored on the same partial golds, so arm *comparisons*
  stand; absolute Hit@10 levels and any per-query "why BM25 wins" analysis on
  those 46 queries rest on incomplete truth (not CRITICAL by the stated bar).
- Exact refs: `data/REPORT.md:31-36`; `data/export_realtalk.py:48-66,131-137`
  (silent `if t in expect_map` drop at line 133-134);
  `audit/lexical_audit.json` (`n_partial_valid_with_unresolved`).

### F2 (MED): LoCoMo 1531 vs 1535 RESOLVED to 4 named items, effect ≤0.26 pp

- Audited claim: the known-unresolved gap (HIZ n=1531 vs `LOCOMO.json` n=1535).
- What I did: enumerated all three cohorts from raw artifacts. Script:
  `locomo_resolve.py` → `audit_locomo_resolve.json`.
- Result — three nested cohorts, all consistent:
  - Raw `drive/locomo10.json` (sha256 pinned in HIZ provenance): 1986 questions.
  - `regen/locomo/locomo_*.pkl`: 1540 (1986 minus 446 adversarial-cat-5).
    Per-arch kept: 150/81/152/199/178/123/150/191/156/155.
  - HIZ `locomo_adapter_before_scores.json`: 1531 kept
    (150/81/152/**197**/177/123/**149**/191/156/155), drops 4 no-evidence +
    5 invalid/unknown-evidence.
  - `parallel_ideas_r1/hit10/LOCOMO.json`: 1535 + 5 skipped
    (`run_locomo.py` skips no-retrievable-gold: the same 4 empty-evidence +
    1 unresolved `D30:05`). Regen kept: 150/81/152/**199**/178/123/**150**/
    191/156/155 = 1535.
  - The differing 4 (HIZ drops, LOCOMO.json keeps with partial gold):
    `L03_q0058`→`locomo_3_qa58` (gold 6 rows, `D10:19` dropped),
    `L03_q0088`→`locomo_3_qa88` (gold rows 17,19, `D` dropped),
    `L04_q0018`→`locomo_4_qa18` (gold 6 rows, `D:11:26` dropped),
    `L06_q0038`→`locomo_6_qa38` (gold rows 401,407, `D4:36` dropped).
    (`L09_q0069`/`D30:05` is dropped by *both* — agreement, see F6.)
- Impact: 4/1535 = **0.26 pp maximum swing** on any LoCoMo Hit@10, far inside
  HIZ's own ±~2 pp bootstrap CIs — flips no significance. But the two LoCoMo
  series stay non-comparable for the deeper reason both sides already state:
  `LOCOMO.json` uses raw evidence while 156 audited corrections
  (`run_locomo.py:189`, `correct_evidence`) sit unapplied in both pipelines
  (`AUDIT_LOCOMO_ANCHOR.json: verdict`). Do not mix the series.
- Exact refs: HIZ adapter file `results/locomo_adapter_before_scores.json`
  (`total_questions: 1986`, `kept_questions: 1531`); `LOCOMO.json`
  (`n_queries: 1535`, `queries_skipped_no_retrievable_gold: 5`);
  `regen/locomo/counts_report.json` (docs 419..689, total 5882).

### F3 (MED): "give your tokenizer to the rival" holds in the verdict, not the headline

- Audited claim: `FINAL_STATE.md:55-56` fair-baseline methodology.
- What I did: compared the code's frozen word channel
  (`drive/v52_t4d_locomo_frozen_cross_benchmark.py:203-208`: sklearn
  `TfidfVectorizer(lowercase, ngram 1-2, stop_words=english, sublinear_tf)` +
  char_wb 3-5 + LSA32) against every BM25 in the programme; reproduced T1 and
  probed bigrams. Scripts: `bm25_bigram_probe.py` →
  `audit_bm25_bigram_probe.json`.
- Result:
  - The STOP verdict itself uses the fair number (65.67) — rule satisfied there
    (`FINAL_STATE.md:24-27`, `DECISION_TESTS.md:15-37`).
  - But the main publication table (`REPORT.md:21-27`) quotes **BM25 54.18** =
    the handicapped `data/run_lexical.py` arm (`\w+`, no stopwords, k1=1.5),
    and every fusion/RRF claim (`ideas_r1/firststage/firststage.py:8,60-61,77`,
    gates pinned at 54.18/78.16) competes against the same coarse rival. A
    reader of REPORT §1 never meets 65.67.
  - T1's "frozen" rival (65.67) still withholds word bigrams and char-grams
    from BM25 — but my probe shows bigrams do not help BM25 on RealTalk
    (frozen+bigram IDF-only: 65.39 vs 65.67 unigram, n=705), and IDF-only
    (k1→0) is if anything a *stronger* rival TF handling than the code's
    sublinear TF. So the residual unfairness is documented but outcome-irrelevant
    here. My frozen-unigram IDF-only rerun reproduces 65.6738 exactly.
  - Minor: T1 textbook arms use k1=1.2 while data/firststage use k1=1.5 —
    cosmetic, does not change ordering.
- Exact refs: `coordinator/decision_tests.py:6` (docstring), `:112-155` (T1);
  `data/run_lexical.py:24,34,89-110`; `REPORT.md:23`; `LADDER_REALTALK.md:57-61`
  (does disclose 55.32→61.70 and the −3.83 pp fair loss — the one place that
  quotes both).

### F4 (LOW): T1 docstring overclaims "1-2 grams"; implementation is unigrams-only

- `coordinator/decision_tests.py:6` says "frozen tokenization (…, 1-2 grams)";
  `toks()` at lines 122-125 emits unigrams only — no bigram construction
  anywhere in the file (grep `gram|bigram` hits only the docstring and
  unrelated `pairs` variables). Per F3's probe the missing bigrams cost BM25
  nothing here (−0.28 pp), so this is a documentation defect, not a number
  defect.

### F5 (LOW): duplicate documents exist but barely touch the scores

- RealTalk exports: 59 extra exact-dup copies / 8944 docs (0.66%), spread over
  all 10 archives (`audit_inventory_gold.json: RT_dup_detail`). Only **6/705
  queries** have a non-gold doc with byte-identical text to a gold doc
  (20 twin pairs) — the only shape that can turn a true hit into a scored
  miss. Ceiling impact 6/705 = 0.85 pp on absolute levels, both arms exposed.
- LME (full 470 archives, turn-level, `role: content` formatting assumption —
  builder itself is unlocated, OPEN_QUESTIONS #6): 862 extra copies / 231606
  (0.37%), 0 empty, 11 near-empty, **0 queries** with a non-gold twin of gold.
- PerLTQA: 0 dups in a 3-archive sample (Cai Xiuying 459, Kong Tingting 293,
  Liang Xin 546 docs) — structured slots, expected; SAMPLE ONLY.
- No empty (0-length) documents anywhere checked; no out-of-range gold index in
  any dataset (RealTalk 0/705, PerLTQA 0/8265, LME 0/470).

### F6 (LOW): `D30:05` zero-padding shows exact-match evidence resolution is fragile

- `regen/locomo/locomo_9.pkl` evidence `D30:05` matches no `id_to_row` key, while
  `D30:5` exists — dropped by both pipelines (5th invalid). One question
  affected. Same fragility class as F1's 72 dropped tokens. Fix is
  normalizing numeric parts before lookup; not applied by anyone.

### OK1: same pool/questions across arms within every pipeline (verified, not sampled)

- Script `pool_identity.py` → `audit_pool_identity.json` (plus corrections
  below). RealTalk: data bm25↔tfidf (1410 rows), audit corrected files,
  pq codes, baseline ckpts — **0 gold/N mismatches on all 705**.
  PerLTQA: ablation (66120 rows) vs baseline (8265): identical 8265-qset both
  ways, **0 gold mismatches**; internal ablation gold identical across 4 arms ×
  2 scorers (2000-q sample, 0 mismatches). HIZ `quality_per_query.csv`
  (65826 rows): identical qset across all 6 arms within each of the 4 datasets.
- Correction to my own table: the `perltqa_abl_vs_bl_N_mismatch: 8265` cell in
  `audit_pool_identity.json` is a script artifact — ablation `per_query.jsonl`
  carries **no N field** (keys: qid/char/section/arm/scorer/top10/gold/…), so it
  compared None≠N. N identity for PerLTQA is instead established archive-wise:
  baseline N == raw `cache_arch_eval.pkl` N on all 30 archives (0 mismatches).
  LME ablation `ARCHIVE_CACHE.jsonl` (322 completed rows) vs baseline: 322/322
  overlap, 0 gold and 0 N mismatches.

### OK2: cross-pipeline question sets agree (RealTalk 705, LME 470)

- HIZ vs working-tree qid sets are **exactly equal** for RealTalk (705) and LME
  (470), same namespaces; PerLTQA namespaces match (`PQ000_DLG_q000`…).
  Gold *sizes* agree too: HIZ `gold_count` vs ours, 0/705 RealTalk and 0/470 LME
  mismatches.

### OK3: hit definition is one contract everywhere

- `hit10 = any gold row in exactly-10 ids; recall = |∩|/|gold|; binary nDCG` —
  identical in `data/run_lexical.py:79-86`, `baseline/metrics_top10.py:84-96`,
  `audit/audit_baseline_lib.py:86-95`, T1 (`decision_tests.py:170-173`),
  firststage. Deterministic tie-break `top10-r1|archive|row` likewise shared.
  No arm gets a looser "hit".

## 4. Dataset inventory (task A summary)

- RealTalk: 10 archives (docs 662/476/453/422/410/1548/1511/1162/1044/1256,
  total 8944; valid questions 85/70/73/71/70/74/70/70/63/59 = 705; 728 total QA,
  23 empty-gold excluded, list byte-identical to frozen exclusion list).
  Gold = raw `evidence` dia_ids → row indices via `norm_evidence`, silent drop
  of unresolvable (see F1). Multi-gold common (386/705 have >1 gold, max 22).
- PerLTQA: 30 archives (N 293–546, total 12288 docs; 8265 questions).
  1 archive excluded pre-eval (Chen Zhi, N=35, 40 QAs — SVD96 needs n>96).
  Gold = Reference-Memory → item index; 2322/8265 multi-gold (dialogue turns up
  to 20); 0 empty, 0 OOR, 0 dup-gold-entries. ≤11 partial-gold keymiss queries
  (0.13%; exact disposition needs builder tracing — limitation).
- LME: 470 single-question archives (N 396–616, median 490, total 231606
  turn-docs; doc unit verified N==turns on all 470). Gold 1–6 rows
  (174/228/38/14/10/6); 0 empty/OOR. Builder script unlocated (known gap #6).
- LoCoMo: 10 archives (docs 369–689, total 5882). Cohorts: raw 1986 → regen
  1540 → HIZ 1531 / LOCOMO.json 1535 (see F2). Doc text = frozen
  `message_text`, text-only adaptation (not official answer-F1), transfer not
  blind, 23% excluded mostly adversarial-cat-5 — HIZ's own report states all
  of this; I verified the counts, not the encoder.

## 5. What I could NOT check and why

- PerLTQA full-corpus dup/empty docs: doc texts require rebuilding all 30
  archives via sklearn (`step2_build.build_items` + vectorizers); I checked
  texts on 3/30 archives (0 dups) and gold/cache integrity on 30/30.
  Cost to close: one `ml-python` run of `build_items` over
  `bench3/PerLTQA/Dataset/en_v2` (no model, seconds).
- PerLTQA 11 keymiss queries' exact gold disposition: needs tracing
  `step2_build.py:108-140` → `step2_exclude.py` → `step2_eval.py` per qid;
  bounded at 0.13% either way.
- LME doc formatting byte-exactness: builder unlocated, so dup counts assume
  `role: content` turn formatting; N==turns verified exactly on 470/470, and
  caches (what scoring actually uses) are fully covered.
- LoCoMo 156 audited corrections: inspected only as metadata
  (`AUDIT_LOCOMO_ANCHOR.json`, `run_locomo.py:189` convention); re-scoring with
  corrected gold needs a rerun nobody has done — both pipelines agree it is
  open, so no new claim is made here.
- BM25 on PerLTQA/LME/LoCoMo with the frozen tokenizer: the +10.35 correction
  is RealTalk-only (already-known issue); I did not rerun T1-style BM25 on the
  other three benchmarks (compute: moderate; needs per-archive BM25 × 4
  variants on 12288+231606+5882 docs).
- No sampling is hidden above: every "SAMPLE" is labeled (PerLTQA dups 3/30,
  PerLTQA internal-gold 2000/8265, LME first probe 20/470 before the full run).
  All pool-identity and OOR/empty checks are exhaustive.

## 6. Commands run (all read-only on sources; writes only to this dir)

- `python3 inventory_gold.py` → `audit_inventory_gold.json`
- `python3 pool_identity.py` → `audit_pool_identity.json` (with the N-field
  artifact documented in OK1)
- `python3 locomo_resolve.py` → `audit_locomo_resolve.json`
- `python3 bm25_bigram_probe.py` → `audit_bm25_bigram_probe.json`
- Read-only probes (no output files): pickle/JSON structure reads of
  `bench3/runs/b3a_realtalk/rt_repr/`, `bench3/runs/b3b_perltqa/cache_*`,
  `regen/lme/{cache_repr,items}/`, `regen/locomo/`, HIZ CSVs, `LOCOMO.json`,
  plus `grep` over `coordinator/`, `data/`, `ideas_r1/firststage/`,
  `_wt_top10/.../REPORT.md|DECISION_TESTS.md|LADDER_REALTALK.md|FINAL_STATE.md`.
- Prior files in this dir (`audit_step1.py`, `audit_step2.py`,
  `audit_rt_gold.json`, `audit_perltqa_gold.json`) predate this session's work;
  I re-derived their claims independently above and do not rely on them.
