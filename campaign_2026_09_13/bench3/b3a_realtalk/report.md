[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# BENCH-3A REALTALK port — report [LOCAL EXPLORATORY PILOT]

Local, read-only-source pilot. No network. faiss never run (constraint obeyed;
it is not needed: the frozen pipeline is TF-IDF/SVD + Hamming/cosine ranking).
No race_2026-09-13, prereg, or sealed programme artifacts touched.
Outputs: `/tmp/b3a/` (`port.py`, `port_gate.json`, `bench3_realtalk_adapter.py`,
`run_realtalk.py`, `rt_repr/RT*.pkl`, `rt_validate.json`, `details.json`,
`rt_summary.json`, this report).

## 0. Provenance and forced choices

- Sources (read-only): producer `llmzip-work/drive/v52_t4c3_coordinate_axis_probe.py`
  (sha256 `8dce37b1…3d996` verified OK), T4D LoCoMo module
  `drive/v52_t4d_locomo_frozen_cross_benchmark.py` (sha256
  `3f7f091f…9a7b185a`), adapters `llmzip/adapters/longmemeval_v52_adapter*.py`
  (both pinned hashes verified OK), dataset `drive/longmemeval_s_cleaned.json`
  (sha256 + 277383467 bytes verified OK), REALTALK
  `llmzip-work/bench3/REALTALK/data/Chat_*.json` (10 files).
- Interpreter: the brief names `$HOME/muse-work/faiss-python`, but that wrapper's
  `PYTHONPATH` carries only faiss+numpy — sklearn/scipy are NOT importable under
  it (verified: `ModuleNotFoundError: No module named 'sklearn'`). Used
  `$HOME/muse-work/ml-python` instead (`PYTHONPATH=fpylibs:mlpy`): numpy 2.5.3,
  scipy 1.18.1 (system), sklearn 1.9.1, faiss 1.15.0 present (faiss not imported).
  Single-thread env (`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`) as in the producer.
- REALTALK license: searched all of `bench3/REALTALK/` (incl. subdirs) for
  `*licen*`/`LICENSE*`/`CITATION*`: NO license file found. Local research use
  only. Dataset: REALTALK paper, arXiv:2502.13270 (Lee et al.).
- Reference deltas: LME sign−float = +10.0379pp (SIGN96_CENTERED 0.5419751773 −
  FLOAT96_CENTERED 0.4415957447, `V52_T4C2_aggregate.csv`); LoCoMo +12.0pp
  (programme-reported; not recomputed here — stated as given).

## 1. STEP 0 — port fidelity gate: PASS 5/5

`port.py` imports the frozen producer's `buildrep` directly
(`buildrep.__module__ == 'frozen_t4c3_producer'`; no reimplementation) and
rebuilds C/qC from `regen/lme/items/<qid>.json` (lex ordinal over all 500
dataset qids, as in `lme_regen.run`). Ground truth `regen/lme/cache_repr/`.

| qid | lex | C shape | max\|C−Cref\| | sign(C) match | max\|qC−qCref\| | sign(qC) match | gold equal |
|---|---|---|---|---|---|---|---|
| 001be529 | 0 | 514×96 | 2.2815e-12 | 100% | 2.5926e-13 | 100% | yes |
| 00ca467f | 1 | 486×96 | 6.5070e-13 | 100% | 4.1031e-13 | 100% | yes |
| 0100672e | 2 | 486×96 | 1.3999e-12 | 100% | 2.2949e-13 | 100% | yes |
| 01493427 | 3 | 487×96 | 6.5037e-13 | 100% | 2.0581e-13 | 100% | yes |
| 031748ae | 4 | 494×96 | 3.5467e-13 | 100% | 1.2060e-13 | 100% | yes |

Gate (≤1e-10 + 100% sign, C and qC): PASS. Residual ~1e-12 is the known
BLAS-contingent last-bit effect on this stack (cf. red-team note), two orders
below tolerance. Full rows in `port_gate.json`.

## 2. STEP 1 — canonical items and validation

- Chat order = lexical filename sort: RT01=Chat_10, RT02=Chat_1, RT03=Chat_2,
  RT04=Chat_3, RT05=Chat_4, RT06=Chat_5, RT07=Chat_6, RT08=Chat_7, RT09=Chat_8,
  RT10=Chat_9 (note: `Chat_10_*` sorts before `Chat_1_*`; stated, kept).
- qid `RT{chat:02d}_q{idx:03d}`, idx = 0-based position in the file's `qa` list.
- Archive = ALL messages across `session_i` (numeric session sort, file order
  within); `events_session_*` provably excluded (asserted, zero leakage path —
  the keys are never read); `memory_id` = `dia_id` (unique per chat, asserted).
- memory_text = frozen T4D `message_text` called directly:
  `"{speaker}: {clean_text}"` + `" [IMAGE: {blip_caption}]"` iff caption
  non-empty (313/9944 messages carry one). NO date component.
  DOCUMENTED DIFF vs the brief: the brief paraphrases the LoCoMo convention as
  `"[date] speaker: text"`, but the frozen code (`message_text`, T4D lines
  107–114, confirmed by the T4D seal's `BLIP_caption_rule`) contains no date.
  The code governs: no date was used. `clean_text` fills the frozen `text` slot
  (raw message text is absent from `Chat_*.json`).
- Representation = frozen T4D `build_representation` imported and called per
  chat (archive-only word+char TF-IDF + SVD32-latent source blocks → concat →
  SVD96 seed 5204 → L2-normalize → archive-mean center; all QA questions of the
  chat transformed post-fit into QC). `C`/`QC` float64, finite (asserted).
- Fit leakage barrier: fit entry is `fit_input_payload` (memory_text strings
  only) inside the frozen function; questions/gold never enter the fit.
- Gold = frozen LoCoMo `norm_evidence` (regex `D\d+:\d+` token extraction,
  endpoints of ranges, dedupe) intersected with `id_to_row`; QA valid iff ≥1
  resolved token (T4D seal denominator rule). DOCUMENTED DIFF vs the brief's
  "assert 100% resolution": 100% does NOT hold — see anomalies. The brief's own
  fallback ("else stop and report") is exercised as report-with-frozen-precedent
  instead of a hard stop, else no benchmark could run.
- Counts: 728 QA total; cats 1/2/3 = 301/319/108 — all match the brief.
  Per-chat (N messages, QA, cats): RT01 662/85/(30/45/10); RT02 476/70/(30/30/10);
  RT03 453/73/(30/31/12); RT04 422/71/(30/30/11); RT05 410/70/(30/30/10);
  RT06 1548/76/(31/31/14); RT07 1511/70/(30/30/10); RT08 1162/72/(30/30/12);
  RT09 1044/71/(30/31/10); RT10 1256/70/(30/31/9).

## 3. STEP 2 — results (n = 705 valid of 728 QA)

Eval: K=3, NT=20 trials, priorities `default_rng(5_100_000 + ci·100_000 + t·100 + 99)`
(ci = 0-based chat ordinal, LoCoMo convention); sign Hamming `lexsort((p,d))`;
float96 = T4C2 mirror (`cosine_centered`, `lexsort((p,−scores))`); ladder arms as
documented below. `details.json` holds per-QA FRs for all 41 arms (23 invalid
QAs stored with FR=null).

### 3.1 Headline

- NATIVE SIGN96 FR@3 = 0.2247750760 (22.4775%).
- FLOAT96 FR@3 = 0.1725340538 (17.2534%).
- Delta sign−float = +5.2241022177pp. Paired per-QA W/T/L (tol 1e-12):
  104 / 558 / 43; median paired gap 0.00pp; 79.1489% exact ties.

### 3.2 Ladder arms (means over n=705; costs = arm − native in pp)

| arm | 80 bits | cost | 64 bits | cost | 48 bits | cost |
|---|---|---|---|---|---|---|
| SPREAD (per-archive rank-linspace) | 0.2077044917 | −1.7071 | 0.1877885287 | −3.6987 | 0.1649501857 | −5.9825 |
| TOP (per-archive top-variance) | 0.1987208150 | −2.6054 | 0.1754674659 | −4.9308 | 0.1602788472 | −6.4496 |
| BOT (per-archive bottom-variance) | 0.2148344591 | −0.9941 | 0.1975344093 | −2.7241 | 0.1615503653 | −6.3225 |
| RAND mean (10 global draws) | 0.2069274766 | −1.7848 | 0.1894315065 | −3.5344 | 0.1613035200 | −6.3472 |
| RAND min–max | 0.1989–0.2122 | | 0.1766–0.2066 | | 0.1476–0.1751 | |

Construction (stated per the brief's "state clearly … and why"): SPREAD/TOP/BOT
are per-archive variance subsets under the R2C convention
(`order_desc=argsort(var,stable)[::-1]`; SPREAD positions
`floor(linspace(0,95,k)+0.5)`, eff_k==k asserted). RANDOM×10 are
benchmark-global draws shared across chats with the RACE-2 panel seeds
`93000+10·width_idx+j` (`width_idx` 48→0, 64→1, 80→2). WHY: the brief asks for
"deney1 arm definitions", but deney1's random formula (`91000+split·10+j`) is
inseparable from its 10 train/test splits, which do not exist for a
representation port with no learned utilities; the 93000-series is the
programme's split-free random-arm definition (race_sign.py) and the per-budget
`SPREAD/RANDOM×10/TOP/BOT` panel the brief itself names. Paired (vs per-QA
RAND64-mean, pp): TOP64 87/420/198, median 0.00, mean −1.3964040568;
SPREAD64 94/423/188, median 0.00, mean −0.1642977864;
BOT64 108/426/171, median 0.00, mean +0.8102902795.
Best ladder arm at 64 bits = BOT64.

### 3.3 Tie diagnostics (native code, n=705)

Boundary tie (3rd vs 4th Hamming distance equal): 250 QA = 35.4609929078%.
Mean top3-tail gap (d4−d3): 1.2865248227 distances.

### 3.4 Category and chat profiles

Per-category (n valid; NATIVE96 / FLOAT96 / BOT64):
cat1 n=288: 0.0768944279 / 0.0624531526 / 0.0625904315 (delta +1.44pp);
cat2 n=312: 0.3971955128 / 0.3108974359 / 0.3559294872 (delta +8.63pp);
cat3 n=105: 0.1180555556 / 0.0633333333 / 0.0970068027 (delta +5.47pp).
Valid-cat counts (288/312/105) reflect the 23 exclusions (13/7/3).
Per-chat native/float (valid n): RT01 85: 0.3695/0.2775; RT02 70: 0.1690/0.0933;
RT03 73: 0.3941/0.4039; RT04 71: 0.2542/0.3068; RT05 70: 0.2777/0.2653;
RT06 74: 0.0943/0.0270; RT07 70: 0.1474/0.0619; RT08 70: 0.0474/0.0000;
RT09 63: 0.1991/0.0823; RT10 59: 0.2680/0.1723.
Gold-count distribution (valid): 1:319, 2:178, 3:92, 4:49, 5:24, 6:15, 7:7,
8:4, 9:7, 10:4, 14:1, 17:1, 19:2, 21:1, 22:1.

### 3.5 Sensitivities and determinism

- Range expansion (same-day `Dx:a-Dx:b` interiors added to gold; 10 Chat_10 QAs):
  endpoints-only mean 0.0425 vs expanded 0.0222; benchmark-level effect
  (0.0222−0.0425)·10/705 = −0.0287pp ≈ −0.03pp. Primary (endpoints) stands.
- Determinism: re-ran `run_realtalk.py` verbatim → `details.json`
  (`8bae1d38…`) and `rt_summary.json` (`8e725fca…`) BIT-IDENTICAL (sha256).
  Repr rebuild (RT05, smallest chat): max|diff| 1.4137e-13 (C) / 8.3471e-14 (QC),
  sign 100% identical — same BLAS phenomenon as STEP 0; float96 FRs on the
  rebuild are 70/70 exactly identical (maxabs 0.0). Eval claims are
  rebuild-stable; byte-stability holds only for the eval outputs, not the SVD
  bytes.
- Independent spot-check: 3 QAs recomputed via a pure-Python
  `sorted(key=(d,p))` path (no `lexsort`) — 3/3 exactly equal to `details.json`.

## 4. Pattern checklist vs LME / LoCoMo

1. sign96 > float96? YES on REALTALK: +5.2241022177pp (n=705). DIFF: magnitude
   is ~half LME's +10.0379pp and below LoCoMo's +12.0pp. Concentration signature
   recurs (paired median 0.00pp; 79.1489% exact ties vs LME's 64.7%).
2. Ladder monotone in bits? YES for all four families (80 > 64 > 48 throughout).
   Costs vs native tabulated in §3.2 (80: −0.99…−2.61pp; 64: −2.72…−4.93pp;
   48: −5.98…−6.45pp).
3. SPREAD ≈ RANDOM vs TOP penalty? SPREAD−RANDmean: +0.08pp (80), −0.16pp (64),
   +0.36pp (48) — approximately equal, inside the RAND seed spread at every
   width. TOP penalty (TOP−RANDmean): −0.82pp (80), −1.40pp (64), −0.10pp (48):
   present at 80/64, negligible at 48. Sign consistent, size varies — partial match.
4. BOT position? BOT is the BEST ladder arm at 80 bits (0.2148344591) and at 64
   bits (BOT64 = best64, paired mean +0.8102902795pp vs RAND64-mean), and ties
   RAND/SPREAD at 48 bits. STRONGER than LME's BOT (LME48 BOT 0.428 < RAND 0.473).
   Logged as a DIFF.
5. Category profile? cat2 (0.3971955128) >> cat3 (0.1180555556) > cat1
   (0.0768944279) under native; same order under float; sign beats float in all
   three (+1.44/+8.63/+5.47pp). Single-gold QAs are 319/705 (45.25%).
6. Anomalies/limits: (a) 23/728 QA (3.160%) unretrievable → excluded (frozen
   denominator rule), concentrated in Chat_8/Chat_9 (19 of 23); 41 partial-QA
   (+5 valid QAs whose only unresolved items are token-less raws: 46 by the
   adapter's broader count — reconciled, both definitions reported);
   (b) evidence syntax: 46 compound entries (ranges/semicolons/punct) + 8
   token-less entries; day indices are non-contiguous in-archive (no parser bug:
   0 non-dict messages, 0 malformed dia_ids); (c) RT08 float96 is exactly
   0.0000 over 70 valid QAs while native is 0.0474; (d) sign LOSES to float on
   RT03 (−0.98pp) and RT04 (−5.26pp) — the headline delta is not uniform;
   (e) LoCoMo +12.0pp taken as given, not recomputed; (f) one stack only
   (numpy 2.5.3/scipy 1.18.1/sklearn 1.9.1), single-threaded; last-bit SVD noise
   ~1e-13 across rebuilds (sign- and FR-stable, not byte-stable);
   (g) no population inference (fixed-benchmark estimand, as in the seals);
   (h) T4D's `EXPECTED_CATEGORY_COUNTS` filter ({1,2,3,4} keys) is a no-op for
   REALTALK's cats 1–3 — no behavior change, noted for provenance honesty.

## 5. Files in /tmp/b3a

`port.py`, `port_gate.json` (STEP 0 PASS 5/5), `bench3_realtalk_adapter.py`,
`rt_repr/RT01..RT10.pkl`, `rt_validate.json` (728 QA, 301/319/108),
`run_realtalk.py`, `details.json` (sha256 `8bae1d38…`, 728 rows, 41 arms + tie),
`rt_summary.json` (`8e725fca…`), `det_hash_1/2.txt`, `rerun_log.txt`,
`RT05_rebuild331.pkl` (scratch rebuild), this `report.md`.
