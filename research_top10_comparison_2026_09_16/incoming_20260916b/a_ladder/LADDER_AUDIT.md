[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LADDER AUDIT — LLMZIP_GERCEK_12_24_48_BAYT (96/192/384-bit) package

Auditor: llmzip programme worker (Muse Code). Budget ~25 min. Method: read their
code + stored artifacts, re-derive independently with own scripts in this directory
(`q4_repro.py`, `q4_result.json`). Their self-audit (`SELF_AUDIT.json`) is by the
same author as the experiment code — treated as THEIR-CLAIM, never as verification.

Package audited:
- report: `incoming_20260916b/LLMZIP_GERCEK_12_24_48_BAYT_RAPORU_2026-09-16.md`
- summary: `incoming_20260916b/LLMZIP_GERCEK_12_24_48_BAYT_OZET_2026-09-16.json`
- evidence: `incoming_20260916b/extracted/LLMZIP_GERCEK_12_24_48_BAYT_2026-09-16/LLMZIP_BYTE_LADDER_2026-09-16/`
  (510 shards; each: `quality.jsonl.gz` per-query rows incl. stored top-10 ids,
  `packed_inputs.npz` packed codes + float queries + scales + tie_rank, `DONE.json` gates)

Claim tags used below: THEIR-CLAIM / VERIFIED-BY-ME (how stated) / CONTRADICTS-OURS / NO-ARTIFACT.

## HEADLINE ANSWERS (for the coordinator, in question order)

- **Q1 BITS OR FLOATS? VERIFIED-BY-ME: the headline ladder arms are REAL PACKED BITS.**
  `scripts/run_quality.py:75-79` builds `m['codes']` via `np.packbits` in `make_width`
  (`core.py:71`), asserts `m['codes'].nbytes == n*(bits//8)` for every shard/width, asserts
  `unpackbits == (C>=0)`, and scores qscale/hamming/asym through `native()` → compiled C
  (`packed.c`: `weighted`/`hamming`) reading ONLY the packed byte planes. I confirmed on
  disk: every `packed_inputs.npz` has `P96:(12,n) P192:(24,n) P384:(48,n)` uint8 =
  exactly 12/24/48 bytes/doc at all 7 shards sampled (000/100/200/300/400/500/509);
  `costs.code_bytes/docs` = 12.00/24.00/48.00 on all 3 benchmarks; shard-level DONE gates
  record `packed_code_bytes_checked` and `packed_dot_max_error ~1e-13`.
  The `float_raw`/`float_std` arms are scored from float coordinate matrix `C`
  (`run_quality.py:82`) — 384/768/1536 B/doc at float32 (their in-memory math is float64)
  — and are correctly labelled `float_*`, NOT presented as byte-ladder rungs. **No "48 byte"
  headline number is a float arm. The retracted-confusion failure mode is NOT present here.**
  Caveat the coordinator must keep: "12/24/48 bytes" = DOCUMENT code payload only. The query
  vector (`Q{bits}` float64), per-dim scales, and the shared encoder are floats; total
  `service_serialized_bytes` is ~9.9/10.1/10.5 GB (LME, 470 archives), ~148/157/176 MB
  (PerLTQA), ~51/56/65 MB (LoCoMo). Quoting "48 bytes/doc" without "plus the encoder" is
  misleading about system cost, though the per-doc payload claim itself is true.
- **Q2 SOLVER SWITCH: real confound, but they disclose it and keep the control.**
  VERIFIED-BY-ME from code: ladder rungs use exact Gram eigendecomposition
  (`gram_system`, `core.py:63-66`); `original_*96` arms rebuild the production randomized
  SVD96 from raw text and gate `rebuild_doc_bit_diff == 0` (`run_quality.py:53-59`).
  Solver effect (exact96 − original96, paired cluster bootstrap, their CIs) is small/negative:
  FR@3 LME −1.81 [−3.80,+0.09]; PerLTQA −0.25 [−0.93,+0.45]; LoCoMo −0.73 [−1.78,+0.32];
  Hit@10 LoCoMo −1.83 [−2.94,−0.73] SIG. Dimension effects must be read exact96→192→384
  (table below), never original96→exact384. Their report states this separation explicitly —
  THEIR-CLAIM that matches the code.
- **Q3 DOES THE LADDER RISE? Only on LoCoMo. VERIFIED-BY-ME from per-query artifacts**
  (re-aggregated all 510 shard files; worst deviation from their table 2.2e-14):
  PerLTQA qscale FR@3 52.98 → 54.82 → **51.87** (48 worse than 24 AND worse than 12;
  192→384 Δ −2.95 CI [−3.87,−2.01] SIG); Hit@10 79.89 → 80.71 → 79.41 (192→384 SIG negative).
  LME FR@3 52.47 → 61.48 → 61.75 (192→384 Δ +0.27 CI [−1.94,+2.45], flat) while Hit@10
  88.72 → 89.15 → **86.60** (192→384 Δ −2.55 CI [−4.47,−0.64] SIG negative — 48 is the WORST
  of the three on Hit@10). LoCoMo rises on both metrics (FR@3 35.11 → 41.21 → 44.15;
  Hit@10 55.39 → 62.12 → 63.16), but LoCoMo gold is disputed per our digest (n=1531 vs 1535).
  Their abstract's "PerLTQA gets worse at 48" is CONFIRMED by the artifacts — it is even
  stronger than stated (48 < 12 on FR@3). "More bits is better" is CONTRADICTED on 2 of 3 benches.
- **Q4 REPRODUCE ONE CELL: exact match.** VERIFIED-BY-ME with fully independent code
  (pure numpy, no shared source with their C scorer or aggregator): re-scored packed bits for
  5 shard×arm cells incl. a 409-query PerLTQA shard — **0 top-10 position diffs, 0.0 metric
  diffs**; dataset-level re-aggregation of all 66 cells matches their tables to ≤2.2e-14.
  Their pipeline computes what ours computes (same tie-break `SHA256(top10-r1|archive|row)`,
  same Hit/FR definitions). Detail in §5.
- **Q5 REALTALK HOLE: they kept the promise.** VERIFIED-BY-ME: plan selection = 470 LME +
  30 PerLTQA + 10 LoCoMo inputs, 0 RealTalk input files, 0 RealTalk rows in QUALITY_LEVELS/
  SUMMARY scope, and the report mentions RealTalk only as missing ("sonuç uydurulmadı").
  No RealTalk 24/48 number exists anywhere in the package. This is positive evidence for
  their refusal-to-estimate discipline.
- **Q6 ANCHORS: original96 reproduces our frozen anchors.** VERIFIED-BY-ME:
  PerLTQA original_qscale Hit@10 80.0000 (dev +0.0000), original_hamming 75.6806 (−0.0000);
  PerLTQA original_qscale FR@3 53.2375 vs frozen 53.24 (dev −0.0025 = rounding of 2dp anchor);
  LME original_qscale FR@3 54.2730 vs 54.27 (dev +0.0030 = rounding). They measured our system.
  (RealTalk anchors N/A — no RealTalk in package, see Q5.)

## 1. VERDICT TABLE — qscale ladder (headline arms; all PACKED, bytes/doc VERIFIED-BY-ME)

`theirs` = QUALITY_LEVELS.csv/SUMMARY.json. `mine` = my mean over stored per-query rows
(all 510 shards) except Q4 rows where scoring itself was redone. Dev in percentage points.
CIs = THEIR-CLAIM (paired archive-cluster bootstrap, 20000 reps, seed 20260916; LME has
470 single-query clusters so its intervals ≈ query bootstrap).

| bench (n) | arm | B/doc | theirs FR@3 | mine FR@3 | dev | theirs Hit@10 | mine Hit@10 | dev | verdict |
|---|---|---|---|---|---|---|---|---|---|
| LME (470) | original_qscale96 (randomized control) | 12 | 54.2730 | 54.2730 | +7e-15 | 88.5106 | 88.5106 | +1e-14 | VERIFIED |
| LME | exact qscale96 = 12 B rung | 12 | 52.4681 | 52.4681 | −7e-15 | 88.7234 | 88.7234 | +0 | VERIFIED |
| LME | exact qscale192 = 24 B rung | 24 | 61.4752 | 61.4752 | +7e-15 | 89.1489 | 89.1489 | +0 | VERIFIED |
| LME | exact qscale384 = 48 B rung | 48 | 61.7482 | 61.7482 | −7e-15 | 86.5957 | 86.5957 | +1e-14 | VERIFIED |
| PerLTQA (8265) | original_qscale96 | 12 | 53.2375 | 53.2375 | +7e-15 | 80.0000 | 80.0000 | +0 | VERIFIED |
| PerLTQA | exact qscale96 | 12 | 52.9829 | 52.9829 | −1e-14 | 79.8911 | 79.8911 | +0 | VERIFIED |
| PerLTQA | exact qscale192 | 24 | 54.8192 | 54.8192 | +0 | 80.7139 | 80.7139 | +0 | VERIFIED |
| PerLTQA | exact qscale384 | 48 | 51.8664 | 51.8664 | +0 | 79.4071 | 79.4071 | +0 | VERIFIED |
| LoCoMo (1531) | original_qscale96 | 12 | 35.8437 | 35.8437 | +7e-15 | 57.2175 | 57.2175 | −7e-15 | VERIFIED* |
| LoCoMo | exact qscale96 | 12 | 35.1109 | 35.1109 | +7e-15 | 55.3886 | 55.3886 | +0 | VERIFIED* |
| LoCoMo | exact qscale192 | 24 | 41.2129 | 41.2129 | +0 | 62.1163 | 62.1163 | +0 | VERIFIED* |
| LoCoMo | exact qscale384 | 48 | 44.1464 | 44.1464 | +7e-15 | 63.1613 | 63.1613 | +7e-15 | VERIFIED* |

\* VERIFIED = arithmetic reproduction only. LoCoMo gold authority is disputed in our digest
(n=1531 vs 1535, 156 unapplied corrections) — applicability flag, not an arithmetic one.

## 2. VERDICT TABLE — other packed arms (hamming, asym; all PACKED, 12/24/48 B/doc VERIFIED-BY-ME)

Same method (re-aggregation; worst dev over ALL 66 cells 2.2e-14). Values: theirs (= mine).

| bench | arm | 12 B FR@3 / Hit@10 | 24 B FR@3 / Hit@10 | 48 B FR@3 / Hit@10 | verdict |
|---|---|---|---|---|---|
| LME | hamming (sym) | 50.7872 / 83.8298 | 59.2730 / 85.1064 | 59.3050 / 83.4043 | VERIFIED |
| LME | asym | 49.5071 / 85.1064 | 58.7908 / 87.6596 | 61.5851 / 89.3617 | VERIFIED |
| LME | original_hamming96 | 54.6028 / 86.3830 | — | — | VERIFIED |
| LME | original_asym96 | 50.6489 / 85.7447 | — | — | VERIFIED |
| PerLTQA | hamming | 49.0055 / 75.0272 | 50.6783 / 75.4749 | 47.7394 / 74.2650 | VERIFIED |
| PerLTQA | asym | 53.7143 / 80.0847 | 57.2986 / 83.0490 | 58.0250 / 83.6419 | VERIFIED |
| PerLTQA | original_hamming96 | 49.0919 / 75.6806 | — | — | VERIFIED |
| PerLTQA | original_asym96 | 53.5251 / 80.1936 | — | — | VERIFIED |
| LoCoMo | hamming | 30.0187 / 51.7309 | 39.1725 / 59.3730 | 42.4760 / 59.8302 | VERIFIED* |
| LoCoMo | asym | 34.7547 / 55.2580 | 40.7383 / 63.6839 | 44.8636 / 65.4474 | VERIFIED* |
| LoCoMo | original_hamming96 | 31.4030 / 52.5147 | — | — | VERIFIED* |
| LoCoMo | original_asym96 | 34.2683 / 56.8256 | — | — | VERIFIED* |

Note: asym (unweighted dot of ±1 codes against float query, sd=ones) is ALSO packed-bits
scoring (`native(m,v,'asym')` → `LIB.weighted` on `m['codes']`, `core.py:78-83`). Hamming is
`-popcount(doc xor querybits)` on packed planes (`packed.c:34-37`). Neither touches floats.

## 3. FLOAT ARMS (NOT byte-ladder rungs — scored from float coordinates; VERIFIED-BY-ME from code)

`run_quality.py:82`: `fs=unit(q/sd)@unit(C/sd).T`, `raw=unit(q)@unit(C).T` — dense float matrix
multiply, no packing. Bytes/doc if stored: k×4 (float32) = 384/768/1536; their in-memory math
is float64 (×8). Re-aggregation dev +0 over all float cells (same 2.2e-14 bound).

| bench | arm | 96-dim FR@3 | 192-dim FR@3 | 384-dim FR@3 | verdict |
|---|---|---|---|---|---|
| LME | float_std | 54.8511 | 59.8865 | 63.6064 | VERIFIED (float, not 12/24/48 B) |
| LME | float_raw | 44.7979 | 51.6879 | 56.2092 | VERIFIED (float) |
| PerLTQA | float_std | 56.2410 | 57.7773 | 54.4946 | VERIFIED (float) |
| PerLTQA | float_raw | 55.0343 | 58.5458 | 60.4272 | VERIFIED (float) |
| LoCoMo | float_std | 38.8545 | 43.9038 | 44.7540 | VERIFIED (float) |

Quantization gap at 384 dims (float_std384 − qscale384, FR@3, THEIR-CLAIM CIs): LME +1.86
CI [+0.23,+3.50] SIG; PerLTQA +2.62 CI [+2.06,+3.19] SIG; LoCoMo +0.61 CI [−0.16,+1.52] ns.
So even TRUE 384-bit codes do not "close the gap" to the 384-dim float representation on
LME/PerLTQA — consistent with, not contradicting, our retraction. No CONTRADICTS-OURS found
in this package.

## 4. SOLVER-VS-DIMENSION SEPARATION (never merged — read dimension effects within exact family)

Solver effect = exact96 − original_randomized96 (same 96 bits, different eigendecomposition).
Dimension effect = exact192−exact96, exact384−exact192 (same solver). Deltas in pp with
THEIR-CLAIM 95% paired cluster-bootstrap CIs (verified present in `paired_comparisons`;
method read at `scripts/audit_and_summarize.py:114-125`: resample archives, pooled-query
ratio, 20000 draws, seed 20260916 — sound design; I did not re-run the bootstrap).

| bench | effect | FR@3 Δ [95% CI] | Hit@10 Δ [95% CI] |
|---|---|---|---|
| LME | SOLVER exact96−orig96 | −1.81 [−3.80,+0.09] ns | +0.21 [−1.28,+1.70] ns |
| LME | DIM 96→192 | +9.01 [+6.12,+11.91] SIG | +0.43 [−1.91,+2.77] ns |
| LME | DIM 192→384 | +0.27 [−1.94,+2.45] ns | −2.55 [−4.47,−0.64] SIG (negative) |
| PerLTQA | SOLVER exact96−orig96 | −0.25 [−0.93,+0.45] ns | −0.11 [−0.69,+0.45] ns |
| PerLTQA | DIM 96→192 | +1.84 [+1.00,+2.70] SIG | +0.82 [−0.00,+1.62] borderline |
| PerLTQA | DIM 192→384 | −2.95 [−3.87,−2.01] SIG (negative) | −1.31 [−2.05,−0.62] SIG (negative) |
| LoCoMo | SOLVER exact96−orig96 | −0.73 [−1.78,+0.32] ns | −1.83 [−2.94,−0.73] SIG (negative) |
| LoCoMo | DIM 96→192 | +6.10 [+4.46,+7.83] SIG | +6.73 [+4.84,+8.48] SIG |
| LoCoMo | DIM 192→384 | +2.93 [+1.23,+4.51] SIG | +1.05 [−0.67,+2.80] ns |

Reading: the solver switch costs nothing-to-a-little (worst SIG −1.83 Hit@10 on LoCoMo).
The 192→384 step is flat-to-harmful on LME/PerLTQA and the only clearly positive step on
LoCoMo. Any "48 B beats production 12 B by +7.5 (LME)/−1.4 (PerLTQA)/+8.3 (LoCoMo) FR@3"
comparison mixes solver+dims; the table above is the unmixed version. Their report's §2/§3
presents exactly this separation — THEIR-CLAIM confirmed by code and numbers.

Rank-cap honesty (VERIFIED-BY-ME, SUMMARY.json `rank_caps`): PerLTQA 8 archives (2217 queries)
have effective rank 293–381 < 384; LoCoMo 1 archive (81 queries) rank 369. Missing dims are
constant-filled and the full 48 bytes charged (`Cpad` zeros, `mean` zeros, `sd` ones,
`core.py:69-71`; `constant_bit_columns` recorded per shard). So "48 bytes" is storage-true
but not "384 independent directions" — they disclose this; do not quote 384-dim
representational claims for those archives.

## 5. Q4 DETAIL — independent re-derivation (the only check that is mine, not theirs)

Script: `q4_repro.py` (this directory); output: `q4_result.json`.
- SHARD-LEVEL (pure-numpy re-scoring from `P{bits}`/`Q{bits}`/`SD{bits}` + `tie_rank`,
  own full-sort top-k with tie_rank tie-break, own Hit/FR; zero shared code with their C
  scorer or their aggregator):
  shard 500 (LoCoMo, 419 docs, 150 q) qscale96: 0 top-10 diffs, 0.0 metric diff;
  hamming96: 0 / 0.0; qscale384: 0 / 0.0. Shard 000 (LME, 1 q) qscale96: 0 / 0.0.
  Shard 470 (PerLTQA, 459 docs, 409 q) qscale96: 0 / 0.0.
- DATASET-LEVEL (mean of stored per-query rows vs QUALITY_LEVELS.csv, all 510 shards):
  all 66 cells agree to ≤2.2e-14 (worst cell PerLTQA original_asym96 FR@3 +2.1e-14).
- Definitions match ours: Hit@k = any-gold-in-top-k on exactly-k ids; FR@k = retrieved-gold
  fraction; deterministic tie-break `SHA256(top10-r1|archive|row)` (`core.py:21-22,24-30`).
- Their SELF_AUDIT.json claims (739,152 metric comparisons, 0 top-10 diffs vs unpack+dot
  re-scoring, 246,384 scalar expected-metric checks vs old records, 235,680 exact0 checks)
  are same-author re-runs: THEIR-CLAIM, consistent with everything I checked, but NOT
  independent verification. My Q4 above is the independent leg, and it passes exactly.

## 6. Q5/Q6 DETAIL

- Q5 (RealTalk hole): VERIFIED-BY-ME — `PLAN_BEFORE_RUN.json` selection = 470 LME + 30 PerLTQA
  + 10 LoCoMo files, 0 RealTalk inputs on disk; QUALITY_LEVELS.csv datasets = {LME, PerLTQA,
  LoCoMo}; SUMMARY.json scope keys identical; summary JSON contains 0 "RealTalk" mentions;
  report mentions RealTalk only to refuse estimation ("sonuç uydurulmadı", "ölçümü
  tamamlanmadı"). Promise kept — positive trust evidence.
- Q6 (anchors): VERIFIED-BY-ME — PerLTQA original_qscale96 Hit@10 80.0000 (dev +0.0000 pp),
  original_hamming96 75.6806 (−0.0000); PerLTQA original_qscale96 FR@3 53.2375 vs frozen 53.24
  (dev −0.0025 = 2-decimal rounding of the anchor, not a mismatch); LME original_qscale96 FR@3
  54.2730 vs 54.27 (+0.0030, same rounding note). BM25/float_std/sign96 RealTalk anchors N/A
  (no RealTalk in package). Verdict: they measured our system; no CONTRADICTS-OURS.
- Extra THEIR-CLAIM CIs worth knowing (paired, same bootstrap): qscale−BM25 FR@3 —
  PerLTQA 96/192/384 all SIG negative (−7.16/−5.32/−8.28); LME 96 SIG negative (−4.67),
  192/384 SIG positive (+4.33/+4.61); LoCoMo 384 +1.28 [−0.21,+2.56] ns. BM25 still rules
  PerLTQA at every width. These CIs are THEIR-CLAIM (method read, not re-run).

## 7. WHAT THE COORDINATOR MUST NOT QUOTE

1. **"48 bytes beats 24 bytes" as a general claim — CONTRADICTED on 2/3 benches.**
   PerLTQA 192→384 FR@3 −2.95 SIG (and 384 < 96!); LME 192→384 Hit@10 −2.55 SIG with 48 the
   worst of the three. Only LoCoMo rises monotonically, and its gold is disputed.
2. **"384 dims closes the gap, so 48 bytes is enough" — still retracted, this package agrees.**
   float_std384 beats qscale384 SIG on LME (+1.86) and PerLTQA (+2.62). The gap persists.
3. **Any RealTalk 24/48 number — NO-ARTIFACT by design.** Zero such numbers exist; anyone
   quoting one is not quoting this package.
4. **"12/24/48 bytes total cost" — the payload is 12/24/48 B/doc VERIFIED, but the system is
   not 48 bytes.** Service-serialized bytes run ~10 GB (LME) / ~150–176 MB (PerLTQA) /
   ~51–65 MB (LoCoMo), dominated by the shared TF-IDF/LSA encoder. Quote payload and system
   cost together or not at all.
5. **LoCoMo ladder values as confirmed findings** — arithmetic VERIFIED, but our digest flags
   LoCoMo gold as contradictory (n=1531 vs 1535). Treat as exploratory/transfer-only.
6. **Their CIs and self-audit as independent confirmation** — method sound and read by me,
   but same-author. The independent legs of this audit are Q4 (exact match) and Q6 (anchors
   reproduce). Do not upgrade THEIR-CLAIM CIs to coordinator-verified without re-running
   the bootstrap from per-query rows.
7. **Nothing in this package contradicts our frozen anchors or our digest's central
   diagnosis** (representation bottleneck, BM25 > codes on PerLTQA/RealTalk-style lexical
   ground). If a downstream summary claims this ladder refutes either, that claim has no
   artifact behind it.
8. **NO-ARTIFACT check:** every headline number I was asked about had an artifact. No
   invented numbers were needed; no plausible-value filling was performed.

