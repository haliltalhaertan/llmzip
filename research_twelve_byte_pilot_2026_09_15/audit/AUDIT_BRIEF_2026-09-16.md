# Adversarial audit brief — the scaled-query result

**Your job is to BREAK these claims, not to confirm them.** Confirming a wrong
claim is the failure mode that matters here. The author of this brief has been
wrong repeatedly in this session — eleven claims withdrawn, most of them found
by an auditor or an outside reviewer rather than by the author — so treat
every number below as a hypothesis, not a finding.

`[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]`

---

## 0. Rules

- **Re-derive everything with your own code**, prefixed `audit2_`. Do not
  import `run_qscale.py`, `run_qscale_fast.py`, `run_ladder.py` or
  `audit_qscale_ci.py`. Read them to find bugs, not to reuse them.
- **Do not modify** any existing `run_*.py`, `audit_*.py` or `*.json`.
- **Do not touch** the frozen venv at `llmzip-work/venv` (numpy 2.3.5). Use it
  read-only to run things; install nothing.
- **Do not push to git**, do not touch `main`, do not run or read any BEAM /
  Task 4F1 surface.
- Everything is under `C:\Users\MDP\dev\llmzip-work\parallel_ideas_r1\hit10`.
  Frozen scorer: `../b8/lib_b8.py`.
- Report what you find, including "this claim survives" where it does. A clean
  bill of health on a claim you genuinely attacked is a useful result.

## 1. What was done

Documents are stored as the production 12-byte code: `sign(C)` packed, where
`C` is the centered 96-dim representation. **That storage is unchanged in every
arm below.** Only the query side and the scorer move.

```
sym        production: query binarised too, ranked by Hamming
asym       float query, cosine against the +-1 reconstruction
qscale     float query divided ELEMENTWISE by the per-coordinate std,
           then dotted with the +-1 reconstruction
```

`std` is `lib_b8.fit_archive(C)["std"]`, the same array the existing
`float_std` arm already uses: 96 float32 per archive.

## 2. Claims to attack

**C1 — qscale beats sym on all three benchmarks, cluster-bootstrapped.**

| benchmark | sym | qscale | delta | cluster CI95 |
|---|---|---|---|---|
| PerLTQA (8,265 q / 30 arch) | 75.76 | 80.00 | **+4.24** | [+3.40, +5.03] |
| LongMemEval (470 / 470) | 86.08 | 88.51 | **+2.43** | [+0.65, +4.27] |
| RealTalk (705 / 10) | 46.68 | 49.65 | **+2.96** | [+0.79, +4.98] |

**C2 — qscale MATCHES the 768 B/doc standardized float on two of three, and
loses on the third.** `qscale - float_std`: LME +0.21 [-1.70, +2.13] ns;
RealTalk +1.13 [-2.08, +4.21] ns; PerLTQA -3.96 [-4.74, -3.19] significant.
(An earlier draft claimed qscale *beat* float_std on two benchmarks. That was
a query-level bootstrap artifact and is already withdrawn. Check the
withdrawal is complete and that no other query-level interval survives.)

**C3 — rerank recovers the gain cheaply.** Score all N with the production
popcount kernel, keep the top 50, apply qscale to those only:

| | sym µs | rerank50 µs | ratio | rerank50 hit@10 | % of gain recovered |
|---|---|---|---|---|---|
| PerLTQA | 7.62 | 15.03 | 1.97x | 79.82 | 96 % |
| LME | 10.91 | 21.52 | 1.97x | 88.30 | 91 % |
| RealTalk | 12.06 | 22.25 | 1.85x | 49.65 | 100 % |

**C4 — lookup tables lose in numpy.** 12x256 byte tables (`lut8`) and 24x16
nibble tables (`lut4`) are arithmetically exact on every archive but 4-6x
slower than sym.

**C5 — dense qscale is FASTER than sym** (0.50-0.65x) but needs the 768 B/doc
+-1 matrix, which is why rerank exists at all.

**C6 — the pipeline ladder puts the real loss at the SVD step, and hit@10
hides it.** Rebuilt from raw text on 240 LME archives, seeds 5101 / 5204:

```
                  hit@1   hit@3   hit@10
S1_Z (raw TF-IDF) 52.08   72.92   85.42
S2_svd (96 dims)  34.17   60.42   83.33     step: -17.92  -12.50  -2.08
S3_norm           34.17   60.42   83.33     step:  +0.00   +0.00  +0.00
S4_center         33.75   60.42   82.92
S6_sign           42.29   70.62   87.29     S4->S6: +8.54 +10.21  +4.38
```

Only `S4 -> S6` is significant at hit@10, paired bootstrap [+0.62, +8.33].

## 3. Weaknesses the author already knows about — start here, then go further

- **W1. `M = 50` was chosen by looking at these very results.** No held-out
  selection. Quantify the optimism: pick M on a split and evaluate on the
  rest. The curve looked flat from 20 to 200, which may or may not save it.
- **W2. Leakage.** Verify `lib_b8.fit_archive` builds `std` from documents
  only. If any query vector or gold label touches it, C1 collapses. Check the
  PerLTQA and RealTalk loaders too, not just the function.
- **W3. Every timing is numpy, single-thread, one machine.** C4's verdict is
  therefore numpy-specific — faiss FastScan uses exactly the LUT approach and
  wins with it in SIMD. Do not let C4 be read as "LUTs are bad".
- **W4. rerank quality is NOT monotone in M** (RealTalk: 49.65 at M=50 and
  M=100, 49.50 at M=200; LME: 88.30 at 50, 88.09 at 100, 88.51 at 200). Is
  that noise or instability? If it is instability, C3 is fragile.
- **W5. The ladder's hit@1 and hit@3 intervals are analytic worst-case bounds,
  not bootstrap** — per-query values were only saved for hit@10. Redo them
  properly. Also: 240 of 470 archives, sampled with seed 20260916.
- **W6. Everything here is hit@k.** The frozen tasks measure expected
  fractional R@3. Nothing in this brief is a frozen-estimand result, and the
  gain may not transfer to FR@3. Check whether it does.
- **W7. The author already shipped one query-level bootstrap where a cluster
  bootstrap was required, was corrected, and then did it again in
  `run_qscale.py`.** Assume there are more. Audit every interval in every
  `*.json` in this directory for the same defect.
- **W8. `qscale` and `qscale_dot` ranked identically** in the quality run. The
  claimed reason is that all +-1 rows share a norm so the cosine denominators
  cannot change the order. Verify that, and verify it is not masking a bug
  where one of the two is silently unused.
- **W9. rerank expands candidates to include all ties at the M-th distance**,
  so the effective M is variable and larger than nominal. Does that inflate C3
  relative to a strict top-M?
- **W10. The cost accounting.** The `std` array is 96 float32 per archive,
  reported as 3.6-7.8 % of the document bits. Is the comparison honest? Does
  anything else have to be stored for qscale or rerank that has not been
  counted?

## 4. Ablations the author did NOT run, which could deflate C1

- **Is the gain really about scale, or just about the query being float?**
  `asym` is the float-query-without-scaling arm and it does NOT beat sym
  (LME -0.33 ns, RealTalk -3.13 ns under cluster bootstrap, PerLTQA +4.43).
  So scaling is claimed to be the active ingredient. Test it directly: sweep
  `q / std**alpha` for alpha in 0, 0.5, 1, 2 and see whether the gain is a
  smooth function of alpha or an artifact at alpha = 1.
- **Scale the DOCUMENT side instead.** Threshold `C / std` at zero — identical
  to thresholding `C` at zero, since std > 0, so the code cannot change. Make
  sure the author has not implicitly claimed otherwise anywhere.
- **Does a cheaper statistic work as well?** Try per-coordinate MAD, IQR, or
  simply the rank-transform of the query. If a 1-byte-per-coordinate quantised
  scale does as well, the memory argument changes.
- **Per-archive vs global std.** The std is fitted per archive. Does a single
  global std array do the same job? If yes, the per-archive state disappears.

## 5. What would actually falsify the headline

C1 is the load-bearing claim. It falls if any of these hold:

1. `std` is contaminated by query or gold information.
2. The cluster bootstrap is still wrong — e.g. PerLTQA's 30 "archives" are not
   independent, or the right cluster is something coarser.
3. The gain does not survive on the frozen FR@3 metric.
4. The gain is an artifact of the tie convention in `hit_at_k` rather than a
   real ranking improvement. Note `qscale` produces float scores with almost no
   ties while `sym` produces heavily tied integer Hamming distances — **this is
   the most dangerous confound in the whole brief.** A metric that splits ties
   uniformly at random penalises the tied arm. Quantify how much of the +4.24 /
   +2.43 / +2.96 is simply "fewer ties" by, for example, giving sym a random
   tie-break jitter and re-measuring, or by comparing on a metric that is
   tie-insensitive.

Item 4 is the one the author considers most likely to be fatal and has not
tested.

## 6. Deliverable

For each of C1-C6 and W1-W10: **CONFIRMED / OVERSTATED / WRONG**, with your own
number and the code that produced it. Then anything you found that is not on
this list. Do not soften a negative verdict.
