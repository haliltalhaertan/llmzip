# Project Status — 2026-08-28

## Accepted state

V52 Task 4C3 has completed independent cold-start adversarial audit with verdict `PASS WITH CONDITIONS` and has been accepted into canonical `main`.

Frozen status:

- `[AUDITED — TASK 4C2 PASS WITH CONDITIONS]`
- `[FROZEN — TASK 4C2 NUMERICAL CHECKPOINT]`
- `[AUDITED — TASK 4C3 PASS WITH CONDITIONS]`
- `[FROZEN — TASK 4C3 NUMERICAL CHECKPOINT]`
- `[ESTABLISHED ON FROZEN LONGMEMEVAL — NATIVE AXIS-STRUCTURE EFFECT]`
- `[NOT ESTABLISHED — VARIANCE-HETEROGENEITY CAUSAL MEDIATOR]`
- `[NOT ESTABLISHED — CROSS-BENCHMARK GENERALIZATION]`

## Task 4C3 accepted result

On the frozen 470-question LongMemEval cohort:

- Native SIGN96 Fractional Evidence Recall@3: `54.197517730496%`
- Full-Haar96 mean: `38.271666666667%`
- `D96 = -15.925851063830 pp`
- all five preregistered Haar96 seeds below native
- signed-permutation control exact PASS
- continuous centered geometry preserved to maximum deviation `1.1102230246251565e-15`

The block-mixing gradient is strictly monotone over preregistered block sizes 2, 4, 8, 16, 32, 96. Native-vs-Haar96 is broad at question level: `245/138/87` native-better/tie/native-worse; top-50 positive-contributor removal still leaves `+8.560675 pp` mean native advantage.

## Mechanism boundary

Orthogonal mixing strongly flattens coordinate variance heterogeneity, but the preregistered heterogeneity-alignment test failed:

`[HETEROGENEITY-ALIGNMENT NOT CONSISTENT]`

Therefore the accepted result establishes that native axes matter for zero-threshold sign/Hamming retrieval on this frozen representation, but does not establish variance heterogeneity as the mediator.

ITQ96 falls inside the five-seed full-Haar96 quality envelope:

`[ITQ WITHIN FULL-HAAR ENVELOPE]`

This does not imply mathematical equivalence between ITQ and random Haar rotation.

## Provenance / governance

The independent audit found no scientific defect capable of explaining D96. Observed governance/temporal-attestation defect effect was quantified as `0.000 pp`.

The stale adapter-gap language in `CHAIN_OF_CUSTODY.md`, `DATASETS_AND_LARGE_ARTIFACTS.md`, and `tools/verify_frozen_artifacts.py` has been repaired. Exact-byte v1/v2 adapters are present in Git. The verifier now explicitly records the accepted Task 4C3 frozen chain anchors.

Remaining bounded audit conditions are documented in `audit_v52_t4c3/AUDIT_REPORT.md` and `docs/v52/task4c3/TASK4C3_ACCEPTED_CHECKPOINT_2026-08-28.md`.

## Stop rule

No Task 4C4, LoCoMo, larger-scale benchmark, alternate bit-width/threshold/rotation, or rescue experiment is authorized from this audit. Any new research branch requires a separate Head Researcher decision and new preregistration.
