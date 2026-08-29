# V52 TASK 4D — COLD-START INDEPENDENT ADVERSARIAL AUDIT

Date: 2026-08-29

Canonical full audit prompt in Drive:
https://docs.google.com/document/d/13DvnfWaAD3oDA1czHETAxPzfMLw1Eam2aokqa7LUUzA/edit?usp=drivesdk

## Mission

Perform a zero-trust independent audit of `V52 TASK 4D — LOCOMO FROZEN CROSS-BENCHMARK REPLICATION`. Do not trust the compute handoff or aggregates; reconstruct the load-bearing result from raw Drive artifacts, sealed source, preregistration, and hash chain.

Task 4D result folder:
https://drive.google.com/drive/folders/1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF

Preregistration commit: `68c4c10a6886e1076efcffd8981d53bf14fb9b6f`
Task 4D prereg prompt blob: `bd82b564b5ee065ee2e4dad799bf0bacf6bd2aa8`
Parent canonical commit: `8f52c8072f4f781ad2539c461fae154c4c52753b`

Expected chain:
- pre-run seal SHA256 `8b1e65a99316002e4c1bf08406513d431c4bc1a53fa07352325f6573050d041d`
- sealed script SHA256 `3f7f091fadc88dfcc1f68f38d6df10607d05d1e416d048fe776929a9a7b185a7`
- post-run manifest SHA256 `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c`

Reported claims to falsify:
- dataset SHA `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`
- 10 conversations / 1,540 Cat1–Cat4 questions
- audit evidence-valid denominator 1,535
- Native SIGN96 Fractional Evidence R@3 `23.654714666441%`
- Haar96 mean `13.770827054136%`
- `D_LoCoMo = -9.883887612305 pp`
- all five Haar seeds below native
- `[STRONG CROSS-BENCHMARK REPLICATION — NATIVE AXES MATTER ON LOCOMO]`
- signed-permutation exact PASS
- continuous invariance PASS, max error `1.6653345369377348e-15`
- W/T/L `361/992/182`
- top50-removed residual native advantage `+6.849675073999 pp`
- ITQ96 `14.220856478786%`, within Haar envelope
- maximum reported correction/protocol sensitivity `0.352051902899 pp`.

## Load-bearing audit requirements

1. Verify preregistration temporal integrity: decision bands, methods, seeds, top-k=3, tie rule, representation family and no-rescue rules were fixed before outcomes.
2. Recompute seal/script/manifest hashes and verify final script bytes match sealed bytes.
3. Verify dataset/correction identity, 156 corrections, explicit-empty semantics, BLIP captions, raw-vs-audit separation and retrievable-gold mapping.
4. Explicitly audit the `1540 cohort vs 1535 evidence-valid` distinction. Identify the five non-valid questions, prove exclusion is dictated by frozen V51 evidence semantics rather than outcome selection, quantify sensitivity, and state whether it changes the preregistered verdict. Do not silently call 1535 questions 1540.
5. Audit representation transfer: same source-block family, archive-only fitting, per-conversation LoCoMo archive fit, no QA/gold/category/answer metadata leakage.
6. Independently reconstruct native, each Haar seed, mean Haar, D_LoCoMo, ITQ, W/T/L, median gap, contributor-removal sensitivity, categories and all 10 conversations from raw trial/question rows.
7. Verify nuisance collapse within question first and Haar seeds are not independent units; equal question weighting only.
8. Recompute signed-permutation invariance exactly. Any distance/ranking/top3/metric mismatch is load-bearing.
9. Recompute continuous orthogonal invariance and inspect Haar generator, transform orientation, transpose use, centering, same-R docs/query, and QR sign convention.
10. Treat tie handling as high-risk because prior project history found corpus-order bias. Verify priorities are independent of corpus/gold/evidence order and paired methods use the same realizations.
11. Reproduce raw-vs-audit correction sensitivity and compute the change in the primary native-minus-Haar gap directly, not merely per-arm effects.
12. Verify Task 4D scientific intervention is semantically comparable to audited LongMemEval Task 4C3.
13. Verify effect concentration: W/T/L, top10/25/50 removal, all category gaps and all conversation gaps. Cat3's smaller effect must be reported rather than hidden.
14. Verify ITQ canonical archive-only orientation and only classify its relation to the five-Haar range; do not infer ITQ=random Haar.

Actively test at least these bugs: different query/archive rotations; double rotation; transpose mismatch; nonorthogonal QR; centering leakage; QA/gold fitting leakage; corpus-order tie leakage; different tie priorities across arms; seed/trial overweighting; conversation weighting; post-hoc exclusion of five evidence-invalid questions; asymmetric corrections; BLIP mismatch; method-specific gold denominator; raw/audit mixing; top-k mismatch; Hamming direction error; threshold mismatch; post-outcome seed choice; family mismatch vs 4C3; cross-conversation cache contamination; duplicate/dropped qids; restart-duplicated rows; script bytes changed post-seal; stale manifest; denominator inconsistency changing verdict.

## Verdict standard

Return `PASS`, `PASS WITH CONDITIONS`, or `FAIL`.

A strong or partial Task 4D result must not be frozen without this audit.

## Required handoff

Report:

`VERDICT: ...`
`AUDIT LEVEL: ...`
`CHAIN OF CUSTODY: ...`
`PREREGISTRATION TEMPORAL INTEGRITY: ...`
`DATASET / CORRECTION IDENTITY: ...`
`COHORT 1540 IDENTITY: ...`
`EVIDENCE-VALID PRIMARY DENOMINATOR: ...`
`1540-vs-1535 ISSUE CLASSIFICATION: ...`
`SIGNED-PERMUTATION CONTROL: ...`
`CONTINUOUS ORTHOGONAL INVARIANCE: ...; MAX ERROR=...`
`REPRESENTATION TRANSFER / LEAKAGE: ...`
`NATIVE FRACTIONAL R@3: ...%`
`HAAR96 MEAN FRACTIONAL R@3: ...%`
`D_LOCOMO: ... pp`
`HAAR SEED VALUES: ...`
`ALL FIVE HAAR SEEDS BELOW NATIVE: YES/NO`
`PRE-REGISTERED VERDICT REPRODUCED: YES/NO`
`NATIVE-vs-HAAR W/T/L: ...`
`MEDIAN PAIRED GAP: ... pp`
`TOP50-REMOVED RESIDUAL NATIVE ADVANTAGE: ... pp`
`CATEGORY GAPS: ...`
`10 CONVERSATION GAPS: ...`
`ITQ96 FRACTIONAL R@3: ...%`
`ITQ VS HAAR ENVELOPE: ...`
`RAW-vs-AUDIT CHANGE IN D_LOCOMO: ... pp`
`MAX QUANTIFIED DEFECT EFFECT ON D_LOCOMO: ... pp`
`SCIENTIFIC DEFECT FOUND: YES/NO; ...`
`TASK 4D NUMERICAL CHECKPOINT MAY FREEZE: YES/NO`
`CROSS-BENCHMARK NATIVE-AXIS EFFECT ESTABLISHED ON FROZEN LOCOMO: YES/NO`
`CROSS-BENCHMARK GENERALIZATION BEYOND LONGMEMEVAL+LOCOMO ESTABLISHED: NO`
`CAUSAL MEDIATOR ESTABLISHED: NO`
`NEXT STEP RECOMMENDATION: ...`

## Interpretation ceiling

Even after a passing audit, the strongest licensed statement is only that the same native-basis versus data-independent full-orthogonal-mixing intervention yields a material loss in zero-threshold sign/Hamming evidence retrieval on both frozen LongMemEval and frozen LoCoMo while centered continuous geometry is preserved to numerical precision.

Do not claim universal native-axis superiority, population generalization, a proven variance/collision/tie mechanism, ITQ=random Haar, or production speed/RAM superiority.

## Stop rule

Do not launch Task 4E, LongMemEval-V2, million-memory scaling, mechanism rescue, or publication drafting from the audit chat. Finish the audit and hand off to the Head Researcher.