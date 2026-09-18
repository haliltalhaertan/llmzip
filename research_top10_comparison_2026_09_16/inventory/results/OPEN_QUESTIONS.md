[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# OPEN QUESTIONS — genuinely unmeasured (strict: CLAIM-exists = "needs replay", not "missing")

1. PPLX semantic arms on REALTALK (INT8 cosine / BIN Hamming / INT8-asym /
   PCA96_SIGN / protocol primary comparison). Reason: never executed — encoder
   is still on RT01 docs (~495/662 texts in `semantic/progress_fast.json`, old
   run 120/662; no PPLX scores exist anywhere). All other REALTALK numbers exist.
2. qsign_dstd reconciled replay. Reason: exists as CLAIM (HATA_YERI_OZET), but
   coordinator independent replay deviated (LME +0.6383 / PerLTQA -0.2662 /
   RealTalk -0.8511pp) — needs scorer-mismatch resolution, not a fresh benchmark.
   Status: exists-as-CLAIM-needs-replay.
3. LoCoMo authoritative numbers. Reason: two inconsistent CLAIMs exist
   (HIZ: n=1531 weighted Hit@10 57.22; LOCOMO.json: n=1535/5-skipped, sym 43.84)
   with different gold/pipelines, plus 156 audited gold corrections never applied
   (open Head-Researcher obligation per LOCOMO.json). Needs one pinned gold +
   replay, not a new method.
4. Any PPLX / large-model encoding on PerLTQA or LME. Reason: nothing exists;
   PROTOCOL's PPLX scope is REALTALK-only and 8B-FP32 was declared infeasible
   (WSL 15GiB). Missing, blocked by hardware, not by oversight.
5. RealTalk raw-text rebuild (gold/content re-verification from source chats).
   Reason: HATA report explicitly did NOT rebuild RealTalk from raw text
   (reused cached rows/SHAs); lexical audit flags 46 partial-valid queries with
   unresolved evidence tokens. Missing.
6. LME cache_repr builder provenance. Reason: retrieval_review could not locate
   the LME embedding-builder script within budget; LME construction is
   taken-as-given. Missing (audit gap, not a number).
7. End-to-end deployability receipts for qscale (CPU/RSS/queue latency, cold
   query/return-path load, full totals incl. encoder/means/buffers). Reason:
   only micro-timing exists (HIZ latencies_us, CLAIM); HATA report states CPU/RSS
   NOT measured. Missing.
8. Confirmatory inference on any contrast. Reason: every CI in the programme is
   labeled exploratory (few clusters: RT 10, LoCoMo 10; all cohorts already
   influenced decisions per PLAN_V2). A preregistered protocol on untouched
   data does not exist anywhere. Missing by design status, not executable now.
9. Coordinator_retrieval FLOAT columns independent re-derivation. Reason: exists
   as equality cross-check (maxerr 0.0, CLAIM in retrieval_review C5/I7), but
   never re-derived from a second independent pipeline — shared-input caveat
   stands. Needs-replay, not missing.
10. Incoming-package raw per-query CSVs integration (`results/readout_per_query.csv`,
    `raw_stage_per_query.csv`, rank-inversion examples). Reason: files are cited
    in HATA_YERI_RAPORU §10 but were not in the inspected JSON scope; contents
    not inventoried here. Uninspected (possible gap in this ledger, flagged
    honestly) — check before claiming full incoming coverage.
