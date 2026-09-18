# Quantization pilot (math_r1/quant): ITQ / random rotation / median thresholds

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Question

Keep the production 96-dim representation EXACTLY as is; fix only the sign
quantization. Payload stays 96 bits / 12 B per document in every arm (asserted
per archive: packed shape `(N, 12)`).

## Fidelity gate — PASS (before any new arm; see `FIDELITY_GATE.json`)

- RealTalk G1: 0 / 858,624 differing `>=0` doc bits, 0 differing QC signs
  (qid-matched; cache carries 23 pre-excluded extra rows), max abs C diff 0.0.
- RealTalk G2 (rebuilt FULL): qscale Hit@10 **49.6454**, FR@3 **22.41**;
  sym det-Hit@10 **46.5248**, sym expected-Hit@10 **46.6809** — all four match.
- PerLTQA G1: 0 / 1,179,648 differing bits across all 30 archives, max abs 0.0.
- PerLTQA G2 (cached-code replay): qscale Hit@10 **80.0000**, FR@3 **53.24**;
  sym det **75.6806**, sym expected **75.7612** — all four match.
- Internal check: the arms-stage FULL reproduces every gate G2 number to <1e-9
  on both benchmarks (guards against scoring-orientation bugs; it caught one:
  run 1 transposed the sym score matrix and was discarded, gate untouched).

## Sign-invariance proof (verified numerically, RT01)

`sigma_docs` > 0 on all 96 columns. Rescaling changed **0** doc bits and **0**
query bits: for `sigma_j > 0`, `sign(C_ij/sigma_j) == sign(C_ij)` elementwise,
so per-axis scaling CANNOT change a single code bit. Only a ROTATION (families
C/D) or a shifted threshold (family E) changes the bits. Hence naive rescaling
was never tested — there was nothing to test.

## Arms (fit on DOCUMENTS ONLY, per archive; both scorers; never averaged)

- `FULL`: production `bits = (C >= 0)`.
- `ITQ_C`: 50 alternating-minimization iterations from a random-orthogonal init
  (seed 20260916, fixed before running): `B <- sign(CR)`, `R <- U V^T` from SVD
  of `C^T B`. Quantization loss `||B-CR||_F^2` decreased on all 40 archives, so
  the optimizer did what was asked. Query scored as `QC R` (sym bits and
  `qscale = D' @ (QC R/sigma')`, sigma' refit on rotated DOCUMENTS ONLY).
- `RAND_{20260916,20260917,20260918}`: same pipeline, fixed random-orthogonal R.
  `RAND_20260916` uses the same generator+seed as the ITQ init, so ITQ starts
  exactly there by construction.
- `MED`: bit = 1 iff `C_ij >= median_j(documents)`; query sym-bits use the same
  thresholds; qscale query side stays continuous `QC/sigma` (documented choice —
  qscale has no query bits to threshold).

## Results (paired archive-clustered bootstrap, 20000 reps, seed 20260916)

n: RealTalk 705 (10 clusters), PerLTQA 8265 (30 clusters). Diffs in pp vs FULL.

### Family C — ITQ: FAIL on both benchmarks

| bench | scorer | FULL | ITQ | ITQ−FULL |
|---|---|---|---|---|
| RT | qscale Hit@10 | 49.65 | 32.77 | **−16.88 [−24.21,−9.42]** |
| RT | qscale FR@3 | 22.41 | 15.43 | **−6.98 [−9.17,−4.72]** |
| RT | sym Hit@10 (det / exp) | 46.52 / 46.68 | 32.34 / 32.33 | **−14.18 [−22.35,−6.05]** |
| PQ | qscale Hit@10 | 80.00 | 78.91 | −1.09 [−2.27,+0.05] (ns) |
| PQ | qscale FR@3 | 53.24 | 50.63 | **−2.61 [−4.10,−1.10]** |
| PQ | sym Hit@10 | 75.68 | 76.14 | +0.46 [−1.30,+2.08] (ns) |
| PQ | sym FR@3 | 49.09 | 47.32 | **−1.77 [−3.33,−0.20]** |

### Family D — random rotation: harmful on both (the "any rotation" effect is real)

- RT qscale Hit@10: −14.47 / −14.33 / −15.04 (all CIs exclude 0); sym Hit@10 ≈
  −14; FR@3 ≈ −6 to −8. All three seeds agree.
- PQ qscale Hit@10: −1.23 / −0.52 / −1.14; FR@3: −2.60 / −2.61 / −1.51 (all
  significant); sym Hit@10 ≈ 0 (ns), sym FR@3 ≈ −2 to −3 (significant).
- Reading: the axis-aligned SVD frame carries retrieval signal (qscale's sigma
  weighting is meaningless after mixing axes). Rotation destroys it.

### ITQ MINUS random — the contrast that says whether optimization did anything

- RT qscale: ITQ is **worse** than every random rotation: −2.41 [−4.74,−0.14],
  −2.55 [−4.73,−0.54], −1.84 [−3.70,−0.28]. The optimization bought
  significantly *negative* value. RT sym: ≈0 (ns).
- PQ qscale Hit@10: +0.15 / −0.57 / +0.05 (all ns). PQ sym FR@3: ITQ beats
  RAND_16 (+1.42 [+0.46,+2.36]) and RAND_17 (+1.04 [+0.05,+2.03]) but not
  RAND_18 (+0.36, ns); PQ qscale FR@3 ITQ loses to RAND_18 (−1.09 [−2.01,−0.16]).
- Verdict: the optimization did nothing useful anywhere, and on RealTalk it did
  significant harm *beyond* random rotation. Minimizing quantization loss moved
  bits to a worse retrieval frame — quantization fidelity ≠ retrieval quality.

### Family E — median thresholds: neutral (RT) / tiny significant hurt (PQ)

- RT: qscale −0.43 [−1.96,+1.12] (ns); sym −1.13 [−3.06,+0.73] (ns).
- PQ: qscale −0.53 [−0.92,−0.16]; sym −0.81 [−1.38,−0.25] — both significant but
  ≤0.9pp. Consistent with the known negative result on quantile thresholds:
  centered data ⇒ median ≈ 0 ⇒ near-zero effect, slightly negative.
- Bit balance (fraction of 1s, mean/min/max across the 96 bits, averaged over
  archives): FULL 0.492 / RT-min 0.309, PQ-min 0.220, max 0.66 (both benches);
  ITQ/RAND tighten to mean ≈0.500, min ≈0.44/0.41; MED hits 0.500/0.500/0.502
  by construction. Better-balanced bits did not help retrieval either.

## Cross-benchmark reversal: NONE this round (stated explicitly)

Rotations hurt on BOTH benchmarks (RT ≈ −15pp, PQ ≈ −1 to −2.5pp — same sign,
very different magnitude); MED is neutral-to-tiny-hurt on both. No arm helps on
one benchmark and hurts on the other. The magnitude gap is itself informative:
RealTalk's 96-dim frame is far more rotation-fragile than PerLTQA's.

## Rare-term stratification (best arm vs FULL; coordinator IDF recipe, docs-only)

Best arm by qscale Hit@10: RT → MED; PQ → RAND_20260917.

- RT/qscale: rare (n=341) FULL 70.67 → MED 71.26; common (n=224) 20.98 → 19.64;
  mid (n=116) 49.14 → 46.55; no_shared (n=24) 20.83 → 25.00. The 14pp rare-term
  gap vs BM25 persists untouched.
- PQ/qscale: rare (n=4879) FULL 93.11 → RAND_17 92.11; common (n=1037)
  41.37 → 39.63; mid (n=2155) 74.06 → 75.13.
- As predicted: no rotation/threshold fixes the rare-term gap, because it cannot
  add information the 96 dims already lost. Nothing surprising to flag — the
  prediction held. (RT FULL bands reproduce the diagnosis values exactly:
  24/224/116/341.)

## Cost accounting (a rotation is not free)

- Rotation state R (96×96): 36,864 B (float32) / 73,728 B (float64) per archive.
  RealTalk total 368,640 / 737,280 B vs payload 107,328 B (8,944 docs counted,
  matches 8944×12) → the shared state is **3.4× (f32) / 6.9× (f64) LARGER than
  the payload it damages**. PerLTQA total 1,105,920 / 2,211,840 B vs payload
  147,456 B (12,288 docs) → **7.5× / 15× larger**.
- Median thresholds (96 floats): 384 / 768 B per archive; RT total 3,840 / 7,680
  B (3.6% of payload); PQ total 11,520 / 23,040 B (7.8%).
- Fit time: ITQ mean 1.36 s/archive (RT) / 1.23 s (PQ); random-gen ms; median µs.
  Query overhead: QC@R mean 7.0 µs/query (RT) / 4.2 µs (PQ); MED 0.

## Verdicts

- Family C (ITQ): REJECT both benchmarks — significantly harmful on RT, never
  better than random anywhere.
- Family D (random): control behaved as a control should — uniform harm,
  consistent across all three seeds; required and reported, never cherry-picked.
- Family E (median): REJECT as improvement (neutral/tiny-hurt); confirms the
  quantile-threshold negative result extends to the median.
- Net: sign quantization is not the lever. The axis-aligned production frame is
  load-bearing; the representation bottleneck diagnosis stands.
