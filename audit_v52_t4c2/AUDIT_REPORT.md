# V52 Task 4C2 — Independent Adversarial Audit (V2 prompt, adapter gap closed)

**Verdict:** `PASS WITH CONDITIONS`
**Audit level:** `FULL RAW-TABLE NUMERICAL REPRODUCTION + FULL SOURCE AUDIT`
**Audited commit:** `eb283f5` (canonical `main`)
**Date:** 2026-08-27

Both Task 4C1 mechanism conditions are now **CLOSED**. No bug was found. Every frozen number reproduces to 6 decimals. The conditions attached to this PASS are documentational and interpretive, not mechanism-blocking.

## Head Researcher accepted conclusions

- Chain of custody: PASS; 26 matched, 0 mismatched.
- Adapter v1/v2 hashes: exact.
- ITQ Procrustes orientation: correct.
- Archive-only / label-free fit barrier: clean.
- Same-input centered ablation: PASS.
- Numerical reproduction: exact to 6 decimals.
- `G = SIGN96_CENTERED - FLOAT96_CENTERED = +10.037943 pp`, confirming the preregistered LEAD band.
- Centering condition from Task 4C1: CLOSED.
- Adapter / ITQ orientation condition from Task 4C1: CLOSED.
- SIGN96 phenomenon: real as a fixed-benchmark descriptive fact on the frozen representation/protocol.
- Causal mechanism: NOT established.

## Required robustness caveat

The SIGN-vs-centered-FLOAT lead is concentrated. W/T/L = 122 / 304 / 44, median paired gap 0.0 pp; 64.7% of questions tie. Removing the 50 largest positive contributors leaves about +1.28 pp of the original +10.04 pp lead. This contrasts with the broad SIGN-vs-ITQ effect. This is descriptive composition sensitivity only, not population inference.

## Conditions retained in the accepted checkpoint

1. The auditor did not independently recompute the 277 MB dataset SHA from the dataset bytes.
2. `V52_T4C2_same_input_proof.csv` should be committed byte-exact when convenient; its conclusion is already independently verified by source-level assertions and committed sanity artifacts.
3. The concentration caveat above must accompany further communication of the SIGN-vs-centered-FLOAT result.
4. No causal mechanism claim is licensed by Task 4C2.

## Frozen Head Researcher decision

`[AUDITED — TASK 4C2 PASS WITH CONDITIONS]`

`[FROZEN — TASK 4C2 NUMERICAL CHECKPOINT]`

`[CLOSED — TASK 4C1 CENTERING CONDITION]`

`[CLOSED — TASK 4C1 ADAPTER / ITQ ORIENTATION CONDITION]`

`[REAL FIXED-BENCHMARK PHENOMENON — SIGN96]`

`[OPEN — CAUSAL MECHANISM]`

`[TASK 4C3 — CLEARED TO RUN]`

Canonical full auditor report originated on commit `78b4fdf` of branch `claude/itq-frontier-audit-wfrz6a`; this accepted main-branch copy records the Head Researcher’s governance decision and preserves the load-bearing findings and caveats.