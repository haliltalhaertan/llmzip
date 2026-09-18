# RESIDUE AUDIT (round 3) — root logs, self-audit, leftover diagnostics

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 1. VERDICT

No headline conclusion overturned. Best 48B code still loses to fair BM25; that gap is untouched.
Two shipped artifacts are still wrong (stale expected-hit column + false REPORT sentence), one
external arm (qsign_dstd) mis-reproduces by 0.85pp, and the primary PPLX-0.6B comparison has no
results at all (encoder stalled at RT01 partial). Full gap ledger: `GAP_LEDGER.csv` (same dir).

## 2. Findings

### F-B1 — HIGH — data expected-hit column + REPORT sentence

- File: `data/REPORT.md:55-57`, `data/per_query_{bm25,tfidf}.jsonl`
- Ran: recomputed means from shipped files vs `audit/lexical_audit.json`
- Result: `expected_hit_at_10` holds expected-Recall (0.4316), not expected-Hit (0.5418)

### F-B2 — HIGH — self-audit correction never shipped

- File: `audit/per_query_*_corrected.jsonl` vs `data/` (hashes unchanged)
- Ran: compared corrected means; checked for `AUDIT_REPORT.md`/`VERIFIED.json`
- Result: fix exists only in `audit/`; producer files + REPORT untouched; 2 promised files absent

### F-C1 — HIGH — incoming qsign_dstd does not reproduce

- File: `coordinator/verify_incoming.json` (partB max dev 0.85pp)
- Ran: tabulated ours-vs-theirs per bench; qscale exact, qsign_dstd off everywhere
- Result: RealTalk 49.50 vs claimed 50.35 (-0.85pp); LME +0.64pp; PerLTQA -0.27pp

### F-C2 — LOW — ideas v1 false REJECT corrected by v2

- File: `coordinator/ideas_audit.json` (REJECT) vs `ideas_audit_v2.json` (ACCEPT)
- Ran: read both JSONs + v2 header documenting 3 v1 bugs
- Result: all 3 failures were audit bugs (wrong anchor, histogram walk, schema); self-fixed

### F-C3 — LOW — semantic fidelity RED then GREEN; fix present

- File: `coordinator/semantic_RED.log` (4 fail) vs `semantic_GREEN.log` (4 pass)
- Ran: grepped live `semantic/pplx_scorer.py` for fp32 path + `load_checkpoint`
- Result: production file has the fix (torch fp32, lines 29/52/57); pre-fix kept aside

### F-A1 — MED — `baseline_audit_replay.log` is 0 bytes

- File: `coordinator/baseline_audit_replay.log` (empty)
- Ran: `ls -la`; searched for any other replay output
- Result: a replay step logged nothing; UNVERIFIED it ever ran

### F-A2 — HIGH — PPLX encoder stalled; primary comparison missing

- File: `semantic/progress.json`, `payloads/`, `checkpoints/`
- Ran: read progress + listed payload/checkpoint dirs
- Result: only RT01 partial (120/662 docs, est ~41h at first rate); no scored PPLX artifacts

### F-A3 — LOW — log hygiene notes

- File: `pq.log`, `data.log`, `model.log`, `weight_headers.txt`, `download.log`
- Ran: read all root logs/txts in full (all <9 KB)
- Result: pq.log repeats one result 3x; model.log empty; data.log spot-check is 1 query

### F-X1 — INFO — stale coordinator note on PQ expected-hit

- File: `COORDINATOR_NOTES.md:3` vs `pq/run_pq.py:145`
- Ran: read current `expected_hit_uniform`; recomputed 705-row means
- Result: note describes a count-based bug that was fixed pre-run; current code correct

## 3. Per-finding detail

### F-B1. Producer `expected_hit_at_10` is expected-Recall; REPORT sentence false

Producer formula bug (project's own self-audit caught it; `audit/README_COUNTEREXAMPLE.txt:4-11`,
`audit/test_expected_hit.py:74-80`): multi-gold boundary-tie case returns fractional recall, not
any-gold probability. Observed means (`audit/lexical_audit.json:214-239`, recomputed this session):

- BM25: Hit 0.541844 / corrected-exp 0.541844 / producer-exp 0.431599 (= Recall 0.431599)
- TFIDF: Hit 0.529078 / corrected-exp 0.529078 / producer-exp 0.419062 (= Recall 0.419062)

`data/REPORT.md:55-57` still ships the sentence "Expected-Hit@10 equals Recall@10 to all digits
(no boundary ties: float scores)". Both halves are wrong as written: the column equals Recall
because of the bug, and "no boundary ties" is false — audit counted tie-at-cut on 27 BM25 + 28
TFIDF queries (`lexical_audit.json` arms summary; rechecked: `tie_at_cut=27`, `gold_in_bucket>0=0`
for BM25 this session). Primary Hit/Recall/nDCG verified exact (`top_mismatch=0`,
`actual_mismatch=0`), so headlines are unaffected; only the auxiliary column + sentence are wrong.

Command (read-only):

    python3 -c "import json; ..."  # means over data/per_query_bm25.jsonl (=0.431599)
      # vs audit/per_query_bm25_corrected.jsonl corrected (=0.541844)

### F-B2. Correction exists but was quietly dropped (no write-back)

`audit/audit_lexical.py:190-220` writes corrected JSONLs + `lexical_audit.json` and asserts
`hashes_unchanged` — by design it never edits `data/`. Verified `source_hashes_before.json ==
source_hashes_after.json` (19 files, equal=True this session), so `data/per_query_*.jsonl` still
carry the buggy column and `data/REPORT.md` still carries the false sentence. Additionally the
tasking memo `audit.txt:1-3` promises `AUDIT_REPORT.md` + `VERIFIED.json`; neither exists in
`audit/` (dir listing: 12 files, neither present), and `audit_baseline.py` (subtasks 2-3:
baseline/PQ full rescore, semantic review) has no output artifacts anywhere in `audit/`. The
baseline worker's own `baseline/audit_top10.py` + `audit_top10.log` partially cover subtask 2,
but the audit-owned deliverables were never produced. So: correction done, disclosure partial
(`lexical_audit.json` + `partial_qids` list of 46 unresolved-gold queries = 6.52%, consistent
with the known gold-incompleteness item), propagation zero.

### F-C1. `verify_incoming.py` partB: qscale exact, qsign_dstd off by up to 0.85pp

`coordinator/verify_incoming.json:10-46` (recomputed table this session):

- PerLTQA qscale 80.0000 vs 80.0000 (+0.00); qsign_dstd 79.4676 vs 79.7338 (-0.27pp, n=8265)
- LME qscale 88.5106 vs 88.5106 (+0.00); qsign_dstd 88.2979 vs 87.6596 (+0.64pp, n=470)
- RealTalk qscale 49.6454 vs 49.6454 (+0.00); qsign_dstd 49.5035 vs 50.3546 (-0.85pp, n=705)

PartA (12 cells, old arms) max dev 0.0pp, so the harness is sound; only the incoming package's new
`qsign_dstd` arm (`(C/sigma) @ b_q`) mis-reproduces, on all 3 benches, both directions. Likely a
spec ambiguity (sigma ddof/floor, bit convention, or tie rule) in the external package, not in the
project's code — but root cause NOT isolated (would need the incoming package, out of tree).
No published project conclusion rests on qsign_dstd (decision gates use qscale/sym/BM25), so impact
is contained to trusting that external number. `verify_incoming.py:31-42` documents the formula used.

### F-C2. `audit_ideas.py` v1 REJECT was the audit's bug; v2 ACCEPT stands

`coordinator/ideas_audit.json:23-31` verdict REJECT on 2 failures + 2 warnings. `audit_ideas_v2.py:4-11`
honestly records all three as v1 defects: (1) anchored FULL/sym to 46.6809 (EXPECTED-hit) while the
worker reported realized 46.5248 — worker correct, anchor wrong (same expected/realized mix-up as the
known REPORT-sec1 item); (2) monotonicity walker treated `gold_size_dist` histogram as an M-curve;
(3) assumed flat rows, firststage schema is nested. `ideas_audit_v2.json` verdict ACCEPT, failed=[].
Recomputed-pool check (`mine vs theirs` max dev <1e-9) and RRF rebuild (0/705 mismatches) support v2.
No contradiction with published claims remains here; finding recorded so nobody re-opens v1's REJECT.

### F-C3. Semantic fidelity: RED (4 fail) -> GREEN (4 pass); fix is live

`coordinator/semantic_RED.log`: `test_pool_is_official_fp32_reduction` FAIL (float64-vs-fp32 mean,
0.333 vs 0.0 on the 1e8-magnitude fixture), `test_int8_matches_official_torch_fp32_boundaries` FAIL
(166/756 boundary mismatches, +/-1 LSB), 2x `load_checkpoint` ERROR (attribute missing — partial
checkpoint would finalize zero rows as complete, exactly the `COORDINATOR_NOTES.md:4` hazard).
`coordinator/semantic_GREEN.log`: 4/4 OK. Live `semantic/pplx_scorer.py:27-70` now uses
`torch.as_tensor(..., dtype=torch.float32)` pooling/int8 and defines `load_checkpoint`; pre-fix
copies preserved at `coordinator/semantic_before_fidelity_fix/`. Fix verified present, not just
logged. (Whether the 1-LSB int8 change moves any retrieval metric is UNVERIFIED — no scored
artifacts exist to compare; see F-A2.)

### F-A1. `coordinator/baseline_audit_replay.log` is empty (0 bytes)

`ls -la` confirms 0 bytes, dated Sep 15 16:36 (mid-run). No sibling replay output found
(`audit/` has no baseline-rescore artifacts; baseline's own `audit_top10.log` exists but is the
worker's self-check, not the coordinator replay). Either the replay never ran or its output was
lost. UNVERIFIED which. Risk is bounded: `baseline.log:5` gates claim 9440/9440 FR3 replay PASS
with max diff 0.0, and round-2's production-identity gate (0/858624 bits) independently re-anchors
RealTalk k=96 — but the coordinator-level replay evidence for PerLTQA/LME is missing.

### F-A2. Semantic/PPLX primary comparison never completed (stalled encoder)

`semantic/progress.json`: RT01 docs 120/662, first-batch 124s/8 texts (0.064 texts/s, est total
~150108s ≈ 41.7h), peak RSS 2.48 GB. `progress_fast.json`: RT01 495 docs at 1.82 texts/s (still
~1.5h for 9649 texts, and no later progress file exists). `payloads/` holds only `RT01_docs.npz`;
`checkpoints/` holds only RT01 batches; `tokenizer_stats.json` has lengths for all 10 archives
(no truncation: max 463 tokens < 1024) but zero embeddings. `model.log` (2 lines) shows the
semantic worker logged under `semantic/`, not root. `ladder.log` RT06 line (2277s) vs `ladder2.log`
(79s/archive + "FIDELITY GATE: 0 differing of 858624 bits") shows the transposed-pipeline path got
fast — but that gate covers the SVD/sign pipeline, not PPLX. Bottom line: PROTOCOL.md:8's PRIMARY
deliverable (PPLX-0.6B INT8/BIN/asym arms on 705 queries) has no per-query artifacts; any verdict
about neural-vs-BM25 at 12B rests on SVD-sign codes only. This is a scope gap, not a wrong number.

### F-A3. Root-log hygiene (all read in full; files <9 KB each)

- `pq.log` (60 lines): the same Hit 0.3305/Recall 0.2439/nDCG 0.1734 result is pasted 3x with
  escalating "verification observed" repetition — no contradiction found, but triplicated text
  inflates apparent independent confirmation. `download.log`: 14/14 files + DOWNLOAD_COMPLETE;
  `MODEL_DOWNLOAD.json` SHAs match (spot: README sha a93b39... in both). `weight_headers.txt` is
  raw HTTP 302/200 headers (CDN redirect + Xet hash) — benign, confirms pin
  2c4d510dd4a732063c31a0f70193e35067b51fd8, size 2384233112.
- `data.log:11`: "Independent audit re-derived RT01_q000's BM25 top10" — exactly one query by a
  second code path. True but thin; the full 705x2 second-path check only arrived later via the
  audit worker (`top_mismatch=0`). `audit.log` (4 lines) is just a session shutdown notice —
  the audit worker logged to `audit/*.json`, not root. `model.txt`/`baseline.txt`/`data.txt`/
  `pq.txt` are tasking memos, not execution records — no hidden retries/parameter changes found
  in any of them. No failed runs with kept partials found in root logs (pq REPORT:76-83 does
  disclose one fixed-then-rerun expected-Hit version — handled in F-X1).

### F-X1. COORDINATOR_NOTES pq note is stale (fix already landed)

`COORDINATOR_NOTES.md:3` says `pq/run_pq.py expected_hit_uniform()` "returns EXPECTED NUMBER of
golds, possibly >1". Current `run_pq.py:145-172` implements the hypergeometric tail
1-C(B-G,s)/C(B,s) (bounded in [0,1]); `pq/REPORT.md:74-77` documents the fix ("initial
count-based version could return values >1 and was fixed"); recheck of all 705 rows: expected ==
hit on every row (float scores, no cutoff ties), none >1. The note predates the fix. No action
needed — recorded to stop future re-flagging. Baseline's `exp_hit10` likewise verified sane
(sign96 gaps +0.08/+0.16/-0.31pp vs Hit; float arms diff 0.0000 — Hamming-only ties, as
`baseline/REPORT.md:117` claims).

## 4. What you could NOT check and why

- `_wt_top10/` worktree: never listed (time + brief centers top10_comparison_r1). UNVERIFIED it
  matches the main tree.
- Rounds 1-2 corpora (`audit_hard_r1/`, `audit_hard_r2/`): read-only + summarized by brief;
  not re-read except the cited `t_inductive_all10.py` path (existence not re-confirmed).
- `diag_mask.py` / `diag_speed.py`: read (perf-only scripts, print timings, save no artifacts).
  NOT executed (each loads the 2.4 GB model; <15 min probe budget; outputs could not contradict
  any published retrieval number by construction).
- Full-text diff of `data/RT*.json` vs raw chats: relied on audit's `alignment_errors=0` over
  8944 bindings; independent re-read of ~1 MB text skipped as duplicative.
- Per-archive baseline checkpoints (`ckpt_top10_*.jsonl`, ~1000 files): checked via gates +
  summary only; single-file corruption would surface in means but was not byte-scanned.
- Upstream caches (`bench3/.../*.pkl`, raw chats): treated as ground truth per PROTOCOL; a cache
  bug would move all arms together and no probe here could separate it.
- Semantic metric impact of the fp32 fidelity fix: no scored artifacts exist — UNVERIFIABLE until
  the encoder finishes.
- Sampling statement: root logs + `audit/` + named coordinator diagnostics read in full (small
  files); `lexical_audit.json` partial list sampled (first 10 of 46 shown, full `partial_qids`
  used for count); per-query JSONLs checked by streaming means over ALL rows (no sampling);
  everything else is as listed in `GAP_LEDGER.csv`. No sample is presented as whole-area clean.

*Methods: read-only probes (`python3` stdlib + numpy for means), `grep`/`sed` for wording,
`ls` for completeness. No source tree modified. Coordinator + report paths cited as
`/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/<path>:<line>`.*
