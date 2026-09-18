[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DO NOT REPEAT — experiments already run (one-line result + proof file)

Rule: if it is on this list, re-running it is rediscovery. Re-derive from the
listed file instead. Statuses: VERIFIED = re-derived this session from raw
per-query rows; CLAIM = producer report inspected, not re-derived.

## Full 9440-query coverage (PerLTQA 8265 + LME 470 + REALTALK 705)

- Top10 sign96/float_raw/float_std/asym (Hit/Recall/nDCG/expected-Hit) — VERIFIED.
  Proof: `top10_comparison_r1/baseline/per_query_top10.jsonl` (+ REPORT.md).
- FR@3 sym/sign8/asym/float/float_std + nDCG@3 — CLAIM.
  Proof: `parallel_ideas_r1/asymmetric/per_query.jsonl`, REPORT.md.
- FR@3 sym/asym/B8/sign88/float/float_std — CLAIM.
  Proof: `parallel_ideas_r1/b8/per_query.jsonl`, REPORT.md.
- FR@3 base/sign_only8/mag8/float + tie-oracle/random-seed diagnostics — CLAIM.
  Proof: `residual8_pilot_r1/coordinator/VERIFIED_RESULTS.json`, FINDINGS.md.
- Hit@k/FR@k k=1,3,5,10,20 (6 arms) + full k-curves — CLAIM.
  Proof: `parallel_ideas_r1/hit10/HIT10.json`, KSWEEP.json.
- qscale (+qscale_dot) Hit@1/3/10: LME 88.51 / PerLTQA 80.00 / RT 49.65 — CLAIM,
  coordinator-reproduced EXACTLY. Proof: `hit10/QSCALE.json`,
  `top10_comparison_r1/coordinator/verify_incoming.json`.
- qsign_dstd Hit@10 — ran but NOT reproduced (dev LME +0.64 / PerLTQA -0.27 /
  RT -0.85pp). Do not re-run blindly; resolve the scorer mismatch first.
  Proof: verify_incoming.json + `incoming_20260916/files/LLMZIP_HATA_YERI_OZET_2026-09-16.json`.

## Historical replay gates (all PASS, do not re-run)

- SIGN/FLOAT exact FR@3 gate, tol 1e-12, maxdev 0.0 on all 3 benches — VERIFIED
  this session (fr3 vs ctrl columns). Proof: baseline per_query_top10.jsonl.
- Same gate PASS in asymmetric / B8 / residual8 pipelines — CLAIM.
  Proof: their REPORT.md / VERIFIED_RESULTS.json (historical_gate_maxdiff 0.0).
- 12/12 old-arm cells + qscale reproduced EXACTLY (0.000000pp) — CLAIM.
  Proof: `top10_comparison_r1/coordinator/verify_incoming.py` + .json.
- B8 S1 nDCG bug found and repaired; FR validity stands (replay maxerr 0.0);
  only sym nDCG column changed (450/35/31 rows) — CLAIM.
  Proof: `parallel_ideas_r1/retrieval_review/REPORT.md`, per_query_ndcg_corrected.jsonl.
- 510/510 payload/encoder integrity (signs, thresholds, std, 9440 unique keys) — CLAIM.
  Proof: `retrieval_review/integrity_checks.json`, cost_integrity.json.

## Lexical BM25/TFIDF controls (REALTALK 705, per-archive docs-only fit)

- BM25 Hit .5418 / TFIDF .5291 (recall .4316/.4191, nDCG .3428/.3166) + all 10
  per-archive splits — VERIFIED. Proof: `top10_comparison_r1/audit/per_query_{bm25,tfidf}_corrected.jsonl`.
- Producer expected_hit column actually equaled recall (mislabeled); corrected
  expected-Hit == hit mean — VERIFIED + audit-confirmed (0 mismatches).
  Proof: same files + `audit/lexical_audit.json`.
- 46 partial-valid queries carry unresolved evidence tokens and were retained —
  CLAIM. Proof: lexical_audit.json (partial_qids list).

## PQ12B (REALTALK 705, faiss M12/nbits8, seed 20260915)

- Hit .3305 / Rec .2439 / nDCG .1734, per-archive 0.60 (RT03) down to 0.04
  (RT06/RT08) — VERIFIED. Proof: `top10_comparison_r1/pq/per_query.jsonl`, SUMMARY.json.
- LUT-vs-brute maxdiff 1.8e-15; 8944 train rows, 728 queries excluded — CLAIM
  (in-file verification block). Do not retrain the same config.

## B8 / SIGN88 / residual-8bit verdicts (all CLAIM, keep as-is)

- B8 vs asym: PerLTQA +0.00058 (null), LME -0.024, RT -0.022; symmetric-beating
  gain is query-precision effect, not allocation. Proof: b8/REPORT.md.
- SIGN88 ablation inside B8 runs (11B payload). Proof: same.
- MAG8 vs SIGN_ONLY8: PerLTQA +0.05pp (null); ~90% of MAG8-base lift is the
  zero-extra-payload ablation; tie-oracle ceiling +1.68pp can't reach FLOAT gap
  (+6.27pp). Proof: residual8 VERIFIED_RESULTS.json + FINDINGS.md + ORACLE_CLOSEOUT.md.
- Threshold sweeps: any move off zero-threshold hurts (PerLTQA zero-sym Hit@10
  .76 vs q0.1 .31). Proof: hit10/THRESHOLD_*.json.
- LME-240 LADDER stages (raw Z -> SVD -> norm -> center -> sign). Proof: hit10/LADDER.json.
- LoCoMo transfer of frozen arms (10 arch): CLAIM with caveats, NOT unseen.
  Proof: hit10/LOCOMO.json + HIZ_GENELLEME_OZET json (n=1535 vs 1531 unresolved).
- Faiss binary-index equivalence + CODESIZE incompressibility + AUDIT_CORRECTNESS
  tiebreak-convention delta (+0.41pp faiss vs frozen over 311 convention queries).
  Proof: hit10/FAISS.json, CODESIZE.json, AUDIT_CORRECTNESS.json.
- Raw-text rebuilds: 78 arch / 8313 queries, 0 sign-bit changes, 249390 scalar
  checks match; centering net effects (-0.21/+0.33/+0.14pp); label fix
  (old "uncentered" float was centered-unstandardized). Proof: HATA_YERI report +
  DIAGNOSIS_SUMMARY.json (producer package).
- KV/inverse fixture probes (ridge vs q4; Newton-GMRES 0/12; ledger L14).
  Proof: kv_repair/REPORT.md, inverse_repair/REPORT.md (corrected versions).

## Design-only (no numbers; read before proposing "new" ideas)

- `next_route_round1/revised/PLAN_V2.md` (contender execution BLOCKED; kill/promote
  rule withdrawn) and `LITERATURE_CORRECTION.md` (paper-method claims withdrawn;
  paper_s2.py is formula-only, 24B conceptual payload, not a 12B challenger).
