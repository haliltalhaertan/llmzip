[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LADDER_INDEP — width ladder under fixed-encoder (INDEP) conditions, RealTalk

## 1. VERDICT (3 lines)

No published number is contradicted: all TRANS anchors reproduced (k=96: 0
differing bits on all 10 archives; k=192/384 within 0.005pp of LADDER.json).
The ladder still rises under INDEP — qscale 20.00 -> 27.09 -> 39.86 — so most
of the width gain is NOT corpus-adaptive; the STOP verdict (fair BM25 61.70 >
best 48B code 57.87) still stands.

## 2. Findings table

| ID | Sev | Check | Result |
|----|-----|-------|--------|
| L1 | LOW | k=96 identity gate | PASS: 0 diff bits, 10/10 archives |
| L2 | LOW | k=192/384 anchor match | PASS: all within 0.005pp |
| L3 | HIGH | INDEP ladder shape | Rises at every step, both metrics |
| L4 | MED | Rank-limit exposure | No failure; RT05/RT04 flagged |
| L5 | LOW | Coverage | 10/10 archives, all 3 widths |

L1/L2 are LOW, not CRITICAL, because they confirm rather than overturn a
published number. L3 is HIGH (new result, qualifies the width story) but not
CRITICAL (no published number or conclusion is wrong).

## 3. Detail

### 3.1 Reference and rebuild (Task A/B)

- Reference (read-only, never modified):
  `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/ROUND_B_8roles_1318/code/t_inductive_all10.py`
  (copy sha256 `c352c724...9984aaa3`, both files).
- Verbatim copy: `t_inductive_all10_REF_COPY.py` (this dir, same sha256).
- Adapted runner: `t_ladder_k.py` (this dir). Only changes vs reference:
  second-stage `TruncatedSVD(n_components=K)` from argv instead of hardcoded
  96; OUT path `INDUCTIVE_K{K}.json` in this dir; K recorded per archive;
  per-fit try/except so a rank-limit failure is recorded, not fatal. Seeds
  (5101/5204), vectorizer params, `det_top10` tie-break, scoring, and
  bootstrap seed (20260917, 4000 resamples) are byte-identical.
- Interpreter: `~/muse-work/ml-python` (wrapper adding sklearn/scipy to
  PYTHONPATH; sklearn 1.9.1, numpy 2.5.3, scipy 1.18.1).
- Commands (each full 10-archive sweep, TRANS+INDEP per archive):
  `~/muse-work/ml-python t_ladder_k.py 96` / `... 192` / `... 384`.

### 3.2 Production-identity gates (Task B) — all PASS

k=96 pooled over 705 queries: TRANS sym 46.52 (anchor 46.5248, diff -0.0048),
qscale 49.65 (anchor 49.6454, diff +0.0046); sign-bit gate 0 differing bits on
all 10 archives (totals 39360-148608 bits). This also reproduces the known
control: INDEP sym 18.16, qscale 20.00, exactly the established numbers.
k=192 TRANS sym 51.77 (anchor 51.7730, diff -0.0030), qscale 55.32 (anchor
55.3191, diff +0.0009). k=384 TRANS sym 54.18 (anchor 54.1844, diff -0.0044),
qscale 57.87 (anchor 57.8723, diff -0.0023). All diffs are 2-decimal rounding.
Per-archive gate lines and Z shapes are in `INDUCTIVE_K{K}.json` (this dir).

### 3.3 The 3x2 table (Task C/D) — 10/10 archives, pooled Hit@10, n=705

sym, TRANS:

| k | Hit@10 |
|---|--------|
| 96 | 46.52 [39.38, 52.94] |
| 192 | 51.77 [47.62, 55.90] |
| 384 | 54.18 [48.46, 59.40] |

sym, INDEP (fit on other 9 archives):

| k | Hit@10 |
|---|--------|
| 96 | 18.16 [13.55, 23.34] |
| 192 | 25.11 [19.60, 30.90] |
| 384 | 35.04 [27.63, 42.67] |

qscale, TRANS:

| k | Hit@10 |
|---|--------|
| 96 | 49.65 [41.95, 57.30] |
| 192 | 55.32 [49.92, 61.29] |
| 384 | 57.87 [52.26, 63.04] |

qscale, INDEP:

| k | Hit@10 |
|---|--------|
| 96 | 20.00 [15.27, 25.35] |
| 192 | 27.09 [21.26, 32.54] |
| 384 | 39.86 [33.36, 46.77] |

Brackets are archive-clustered bootstrap CI95 (resample 10 archive means,
4000 resamples, seed 20260918). Per-archive rows are in the JSONs.

Per-step deltas (pooled pp, same bootstrap on paired archive-mean diffs):

- TRANS qscale: 96->192 +5.67 [+2.73, +8.98]; 192->384 +2.55 [-1.00, +6.51].
- INDEP qscale: 96->192 +7.09 [+4.26, +9.92]; 192->384 +12.77 [+8.85, +17.94].
- TRANS sym: 96->192 +5.25 [+1.66, +9.40]; 192->384 +2.41 [-0.88, +5.73].
- INDEP sym: 96->192 +6.95 [+4.07, +10.34]; 192->384 +9.93 [+7.28, +12.82].

THE DECISIVE QUESTION — does the ladder still rise under INDEP, and by how
much? Yes, at every step, both metrics, with CIs excluding zero. Total INDEP
gain 96->384: qscale +19.86pp, sym +16.88pp — LARGER than the published TRANS
gains (+8.22 qscale, +7.66 sym). The width gain is therefore not mostly
corpus-adaptive; a large share persists with a fixed other-archive projector.
Corollary: the optimism gap (TRANS-INDEP) SHRINKS with width — qscale
29.65 -> 28.23 -> 18.01pp; sym 28.37 -> 26.67 -> 19.15pp (gap CIs in JSON
`_SUMMARY`, seed 20260917). Note the second TRANS step is not significant at
95% (both CIs cross zero) while both INDEP steps are.

### 3.4 Rank limit (Task E)

No archive has n_docs < k: doc counts are RT01 662, RT02 476, RT03 453,
RT04 422, RT05 410, RT06 1548, RT07 1511, RT08 1162, RT09 1044, RT10 1256 —
all > 384, zero fit failures at any k. Feature rank never binds either
(Z cols 23422-33257 TRANS, 120606-124301 INDEP). FLAGGED as approaching the
sample-rank cap at k=384: RT05 (410 docs, k uses 93.7% of hard rank cap) and
RT04 (422 docs, 91.0%). Their k=384 TRANS numbers are fine here
(RT05 qscale 64.29, RT04 60.56) but any wider k would hit the wall there first.

## 4. What could NOT be checked and why

- PerLTQA/LoCoMo/LME ladders under INDEP: out of scope for this run (RealTalk
  only); needs the same sweep per dataset.
- Float (unquantized) arm under INDEP: not run; would separate quantizer loss
  from projector loss at width.
- BM25 under INDEP shift: BM25 needs no fitting, so no INDEP arm exists; the
  STOP comparison (frozen BM25 61.70 vs 48B TRANS 57.87) is unaffected by L3.
- Seed robustness: single seed pair (5101/5204), same as production; the known
  1-init-vs-10-seeds caveat still applies.
- No held-out split within archive: pre-existing limitation, unchanged; INDEP
  here is cross-archive, which is strictly harsher.
- Sampling: none — full census (10/10 archives, 705/705 queries, all 3 widths).

## Artifacts (this dir only)

`t_inductive_all10_REF_COPY.py`, `t_ladder_k.py`, `INDUCTIVE_K96.json`,
`INDUCTIVE_K192.json`, `INDUCTIVE_K384.json`, `LADDER_INDEP.md` (this report).
No source tree was modified (read-only honored; only this dir written).
