# LoCoMo computational reproduction: PASS

The one authorized invocation of the unchanged sealed coordinate-scale runner completed with exit 0 in 59.309 seconds. Every persisted question-level score reproduced exactly as a parsed float: **92,100 rows, 1,535 questions, ten original seeds (59001–59010), six original arms, maximum numerical difference 0.0**. Key sets and nonnumeric metadata also matched. No second benchmark invocation occurred.

This is a computational reproduction of the same implementation and frozen benchmark, not an independent methodological replication, a population inference, or complete preregistration-compliance certification.

## Gates and evidence

| Gate | Result | Evidence |
|---|---|---|
| Explicit limited scope before computation | PASS | Parent published authorization receipt commit `540580cfd87f70443123a3349979ab863e2fccc6` |
| Preflight publication before invocation | PASS | Parent published audit gate commit `d1d169f9104ff4dad7415ed68df02bc954730286` before its GO message; invocation receipt binds this commit |
| Trigger-to-seal and all ten seal-bound blobs | PASS | `preflight.json`; trigger `680b10b8a3ef3dd55a5a05fe47f6fb5fa6d931d0` |
| Transitive LoCoMo source identity | PASS | Raw Git source bytes extracted separately; common blob `6700454915176854a55b0b5cf6ffe922a22e35f2` and runner/base verified against trigger and audit HEAD |
| Numerical environment | PASS at required version granularity | Python 3.13.15; NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0; `environment.txt`, `numerical_configuration.txt` |
| Frozen corpus and audit corrections | PASS before and after invocation | Dataset 2,805,274 bytes; all 20 audit files; `preflight.json`, independently rehashed `actual_source_identity.json` |
| Dataset parser identity | PASS | 10 archives, 1,540 category-selected questions, 156 correction records; parser assertions are in sealed common code |
| Sealed synthetic pure-function controls | PASS | `pure_function_tests.txt`, including deliberately failing negative controls |
| Single real invocation | PASS | `run_receipt.json`; one exclusive latch; exit 0; 2026-09-07 11:47:59–11:49:00 UTC |
| Original runner native, scaling, rotation and row controls | PASS | Unchanged runner finished successfully; reproduced summary records zero native-anchor error, exact scaled-native identity, norm error 5.329070518200751e-15, dot error 1.2789769243681803e-13 |
| Question-score and metadata comparison | PASS | `comparison.json`; all 92,100 keyed rows; no changed numeric cells |
| Comparison verifier negative controls | PASS | Numeric perturbation, duplicate key, missing row, changed seed, NaN, metadata drift all rejected |

The numerical environment was Windows 10 x86-64 with explicit OMP/OpenBLAS/MKL/NumExpr thread limits of 1, as requested by the parent at the invocation gate. The original workflow used Ubuntu. Package versions were reproduced, but original OS/compiler/BLAS identity was not asserted. Backend configuration is retained without installing additional optional packages.

The preflight hash bound into the invocation is `134acfc12fbebabf8044a1742a064aca710680b6051d41e6674f7d9613a6557f`. The corpus SHA-256 is `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`; the sorted audit manifest SHA-256 is `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06`.

## Exact scope of agreement

| Arm | Original and reproduced mean fractional R@3 |
|---|---:|
| NATIVE | 0.23654714666441054 |
| SCALED_NATIVE | 0.23654714666441054 |
| FULLHAAR_FRESH | 0.13913106338041972 |
| SCALED_FULLHAAR | 0.20986555436330145 |
| BLOCK32_FRESH | 0.23121552178841082 |
| SCALED_BLOCK32 | 0.23468983738864888 |

All primary summary fields agree, including fraction estimates, seed arrays, dispersions, and the runner's descriptive bands. The only 21 parsed summary differences are the maximum dot-invariance diagnostic (difference 1.4210854715202004e-14) and 20 per-archive CV diagnostics (differences at most 4.440892098500626e-16). They remain below the runner's 1e-12 numerical tolerance. These are disclosed numerical differences, not byte-exact summary reproduction.

Compressed bytes differ. Decompressed CSV bytes also differ: the original has 92,101 LF line endings, while this Windows output has 92,101 CRLF line endings. **Replacing CRLF with LF solely in comparison memory makes the full CSV bytes identical**, including header, row ordering, metadata, and number spellings. Original output bytes were never rewritten. Gzip headers also carry different modification timestamps (1788764836 versus 1788781739). `comparison.json` preserves both compressed and decompressed hashes, header bytes, and line-ending counts.

Original gzip SHA-256: `b7abd942c13cf9ce1b1c4a13e3ff39fb26a26e8b2f2749dd92d76f0b2a474602`.
Reproduced gzip SHA-256: `efed0c46cd0f34e45daa5fcdf5d08fc51a61ffaafd6ca1d522c6c4c98fc7834f`.
Reproduced summary SHA-256: `74f533780d1174b31fe40fa45f77e98ca293e3a441c344cef9bc50bdfa40e19d`.

## Scientific and compliance limits

The saved CSV contains question scores and tie-scheme metadata, not selected document IDs. Matching scores cannot certify identical top-three document selections. No such identity claim is made.

The sealed scale runner does not implement the preregistration's bootstrap requirements. The present user explicitly barred new bootstrap work, so this reproduction does not repair or reassess that gap and does not inherit results from a separate post-outcome package.

The preregistration also lists signed-permutation Hamming invariance. The sealed base runner implements that control in its own `run` function (`locomo_spectral_band_haar_causal.py`, lines 158–167), and retained upstream `locomo_causal_summary.json` reports it passed. The scale runner calls base helpers, not `base.run`, so this invocation does not re-execute that upstream control. Retained upstream evidence is distinct from a control verified during this reproduction. Full preregistration compliance therefore remains qualified even though numerical reproduction passes.

No seeds, scale rule, threshold, method, original runner, seal, research output, or workflow was modified. No LongMemEval run, Task4F1/BEAM/HMAC operation, new bootstrap, or GitHub Actions invocation occurred. Only the two small derived reproduction outputs were copied into this audit namespace. Raw source bytes and the virtual environment remain outside this Git checkout; they are not publication artifacts.

## Recheck without rerunning the benchmark

From the audit checkout, invoke the pinned venv Python with:

```text
-B audit_v52_locomo_reproduction_2026_09_07/compare.py research/v52/locomo_scale_outputs/locomo_scale_per_question.csv.gz audit_v52_locomo_reproduction_2026_09_07/reproduced_outputs/locomo_scale_per_question.csv.gz
```

`compare.py` was extended after the first comparison only to report newline/header diagnostics; the saved benchmark outputs stayed unchanged. `comparison_stdout_stderr.txt` is the initial comparison transcript; `comparison.json` is the final richer comparison receipt. The exclusive invocation latch remains present. `artifact_manifest.json` binds the report, scripts, logs, receipts and derived output bytes; it excludes only itself to avoid a recursive hash definition.
