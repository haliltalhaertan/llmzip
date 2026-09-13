# OFFICIAL RUN — twelve-byte race (post-seal execution record)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

[LOCAL] [NOT PUSHED] Executed 2026-09-13 ~13:12–13:14 (TRT), WSL.
Interpreter: `~/muse-work/faiss-python` (= /usr/bin/python3 + PYTHONPATH=fpylibs);
env: python 3.14.4, numpy 2.5.3, faiss 1.15.0, OpenBLAS 0.3.34, threads=1.

## Seal binding

- Seal: `PRE_RUN_SEAL_local.json` (frozen 13:10). Executed runner files hash-verified EQUAL to the
  sealed hashes: `race_sign.py 6dbb6240…` , `race_faiss.py 67a4b5e4…` (both match to the digit).
- **Process note (honest):** build/smoke-phase runs preceded the seal (13:06–13:09, runner
  development). The seal was written 13:10; the official run re-executed the frozen files and
  reproduced the numbers below. No runner edit occurred between build and official runs (hash
  equality is the proof). This is a LOCAL exploratory process, disclosed as such.

## Executions

- RB2 (sign runner): exit 0; outputs → `official_run/sign/` (details, smoke_log, manifest, console).
- RB3 (faiss runner): exit 0; outputs → `official_run/faiss/` (details, smoke_log, environment,
  hash_manifest, console).

## Official vs build comparison (numeric)

- **RB2: all numeric content BIT-IDENTICAL.** Single difference across the whole JSON tree:
  `/meta/elapsed_s` (92.3 s build vs 86.5 s official). Anchors diff 0.0 both runs.
- **RB3: identical except —**
  1. timing fields (`timing_s`, `smokes/S1/eval_s`);
  2. ONE last-ulp float drift: `arms_summary/A4_random_axes94203/LoCoMo_FR` =
     0.08591252091337810 (build) vs 0.08591252091337809 (official) — Δ ≈ 1.1e-17 (blameless;
     last-digit float op-order; disclosed per programme convention "sayısal kimlik ~1e-14'e kadar");
  3. `byte_worksheet` exists ONLY in the build copy: it was a session-side ANNOTATION appended
     after the run (grep-verified: the string does not occur in the runner source). Content is
     preserved here by reference (build copy in `rb3/`). The runner itself does not emit it.
- Byte asserts re-verified in both official runs: RQ96=20B, RQ32=12B, PQ=12B, EXT2=44B;
  anchors ≤1e-12 both benchmarks; PQ masks 0; determinism smokes PASS.

## Canonical outputs

- CANONICAL = `official_run/{sign,faiss}/` (this directory).
- Build copies retained at `rb2/`, `rb3/` for byte-level provenance (incl. the annotation).

## Preliminary race disposition (for the analysis phase; formal wording there)

Under the sealed literals (RB1): no kill; LME gap vs best competitor ≈ +1.67pp ("moderate"
zone), LoCoMo ≈ +0.11pp ("parity") — both below the +2.0pp promote line. Bootstrap/CI analysis
(analysis phase) will finalize the 16-cell disposition.
