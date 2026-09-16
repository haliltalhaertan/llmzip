# Top10 comparison r1 — DATA worker report (REALTALK export + lexical controls)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope of THIS report: REALTALK canonical export (10 archives, 705 valid queries)
plus BM25/TFIDF lexical controls on the same 705. Semantic PPLX arms are NOT RUN
here (other worker). No input files changed, no git writes, no paid APIs, no web,
no model downloads, no old TFIDF/SVD refit.

## 1. Canonical export (done first, ~1 s; EXPORT_DONE.json written before lexical)

- Source binding: each archive uses its cache `file` field to the raw chat file
  under `bench3/REALTALK/data` (lexical filename order RT01..RT10 =
  Chat_10, Chat_1..Chat_9).
- Doc text = frozen `message_text`: `{speaker}: {clean_text}` plus
  ` [IMAGE: {blip_caption}]` when a caption is present. No date, no
  `events_session_*` keys read. Verbatim copy of
  `drive/v52_t4d_locomo_frozen_cross_benchmark.py` lines 107–114 is inlined in
  `export_realtalk.py` (the frozen module itself is never executed).
- Verification (all asserted inside the exporter, then independently re-checked
  by `test_top10_data.py`: 40108 checks GREEN):
  - EVERY dia_id: rebuilt raw order map equals cached `id_to_row` exactly
    (bijection + order) for all 10 archives (8944 messages total).
  - EVERY question: cached `questions[i]` equals raw `qa[i].question` exactly;
    every category equals raw `qa[i].category`.
  - EVERY cached gold: recomputed from raw `evidence` via the verbatim old
    `norm_evidence` (regex `D\d+:\d+`, dedupe, keep only ids in `id_to_row`)
    equals `gold_rows` exactly — 728/728 stable, zero mismatches.
  - Row IDs preserved (doc `row` = cache row index = retrieval row numbering).
  - No answers/gold in doc texts (texts derive from dialogue messages only).
- Coverage: 728 total QA, 705 valid exported, 23 empty-gold excluded with the
  ORIGINAL reason only. `exclusions.json` qid set is byte-identical to the
  frozen `theory_benchmark_test_v1/realtalk/excluded_ids.json` list
  (RT06×2, RT08×2, RT09×8, RT10×11). No new exclusions. Unresolved-annotation
  detail: none beyond these 23 — every listed evidence dia_id in the 705 valid
  queries resolved (recompute equality proves it).
- Per-archive sizes (docs N / valid queries): RT01 662/85, RT02 476/70,
  RT03 453/73, RT04 422/71, RT05 410/70, RT06 1548/74, RT07 1511/70,
  RT08 1162/70, RT09 1044/63, RT10 1256/59.

## 2. Lexical controls (SAME 705, per-archive DOCUMENTS-ONLY fit)

- Tokenizer (both arms): lowercased Unicode word regex `\w+`.
- BM25: k1=1.5, b=0.75, idf=log((N−df+0.5)/(df+0.5)+1), tf component
  f·(k1+1)/(f+k1·(1−b+b·|d|/avgdl)). Per-archive N/avgdl/idf from docs only.
- TFIDF: raw-count tf, smooth idf=log((1+N)/(1+df))+1 from docs only, query
  weighted with the same idf, cosine; zero-norm rows score 0.
- Zero-vector handling (declared before run): empty token sequence → zero
  vector; any nonfinite score → −inf (worst). None observed (asserted finite
  for all 705×2 runs).
- Tie rule (protocol, gold-unaware): descending score, ascending
  SHA256(`top10-r1|`+archive_id+`|`+row), ascending row. Exactly 10 IDs per
  query, no duplicates (asserted). Expected-Hit@10 under uniform within-bucket
  tiebreak is also stored per query as tie-sensitivity evidence.
- Overall (n=705): BM25 Hit@10 0.5418, Recall@10 0.4316, nDCG@10 0.3428;
  TFIDF Hit@10 0.5291, Recall@10 0.4191, nDCG@10 0.3166. Expected-Hit@10
  equals Recall@10 to all digits (no boundary ties: float scores).
- Per archive (Hit@10 / Recall@10 / nDCG@10):
  - BM25: RT01 .5176/.4701/.3630, RT02 .5429/.4029/.2957, RT03 .6849/.5861/.4670,
    RT04 .5775/.4359/.3591, RT05 .6429/.4898/.4058, RT06 .4324/.3293/.2531,
    RT07 .6857/.5369/.4302, RT08 .2714/.2274/.1539, RT09 .6032/.4176/.3474,
    RT10 .4576/.4054/.3493.
  - TFIDF: RT01 .5529/.4980/.3717, RT02 .4857/.3505/.2408, RT03 .6438/.5402/.4171,
    RT04 .5493/.4331/.3038, RT05 .5714/.4665/.3660, RT06 .4865/.3500/.2298,
    RT07 .6571/.5107/.4136, RT08 .2571/.1910/.1117, RT09 .6032/.4174/.3634,
    RT10 .4746/.4138/.3471.

## 3. Files in this directory (consumer: start at EXPORT_DONE.json + manifest.json)

- `RT01.json` … `RT10.json`: `{archive_id, source_file,
  docs:[{row,id,text}], queries:[{qid,text,gold:[row…],category}]}` (valid only).
- `exclusions.json`: 23 original empty-gold qids + reasons.
- `manifest.json`: counts + sha256/bytes of the 10 caches, 10 raw chats, exports.
- `EXPORT_DONE.json`: completion signal (written BEFORE lexical ran).
- `per_query_bm25.jsonl`, `per_query_tfidf.jsonl` (705 rows each),
  `per_query.jsonl` (combined 1410 rows): `{arm,archive_id,qid,category,N,gold,
  gold_size,top10,top10_scores,hit_at_10,recall_at_10,ndcg_at_10,
  expected_hit_at_10}`.
- `lexical_summary.json`: formulas, tie rule, means, timings.
- Code (repro): `export_realtalk.py`, `run_lexical.py`,
  durable checks `test_top10_data.py`, logs `tdd_export.log`, `tdd_lexical.log`.
- Repro: `$HOME/muse-work/ml-python export_realtalk.py`
  (≈1 s), `$HOME/muse-work/ml-python test_top10_data.py export` (GREEN, 40108),
  `$HOME/muse-work/ml-python run_lexical.py` (≈49 s),
  `$HOME/muse-work/ml-python test_top10_data.py lexical` (GREEN, 8464).
  Independent audit: RT01_q000 BM25 top10 re-derived by a second code path —
  exact match, scores non-increasing.

## 4. TDD log + blockers

- RED1: `export-exists-RT01` (no exports) → wrote `export_realtalk.py` → GREEN.
- RED2: `lex-exists-bm25` (no per-query files) → wrote `run_lexical.py` → GREEN.
- Blockers: none — no missing inputs, nothing invented. Prior
  `parallel_ideas_r1/asymmetric/run.py` used read-only as specified (cache
  paths, `norm_evidence`, cosine/std definitions mirrored, main never invoked).
- NOT RUN / NOT MEASURED here: all PPLX semantic arms, PCA96/PQ12B payload
  arms, PerLTQA/LME secondary baselines (other workers). No claim beyond the
  REALTALK-705 lexical controls above; no extrapolation to larger corpora.
