# V52 TASK 4C3 — INDEPENDENT ADVERSARIAL AUDIT

## ROLE
You are an independent zero-trust auditor. Audit the completed V52 Task 4C3 Coordinate-Axis / Orthogonal-Rotation Causal Probe. Do not optimize, rescue, tune, add seeds, add methods, run LoCoMo, or invent a new mechanism experiment.

## CANONICAL SOURCES
GitHub: https://github.com/haliltalhaertan/llmzip
Task 4C3 Drive result folder: https://drive.google.com/drive/folders/1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv

Before interpreting any result, verify every frozen artifact byte-for-byte against the post-run manifest and verify the binding chain: canonical Git commit -> adapters/dataset identifiers -> pre-run seal -> sealed compute script -> post-run manifest. Treat any mismatch as a chain-of-custody defect until independently resolved from the canonical byte source. Never reformat or regenerate frozen artifacts.

## FROZEN IDENTIFIERS
Canonical Git commit: `7959c1df46b09f48bdbd1d1922bf62715e119839`
Dataset SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` (277383467 bytes)
Adapter v1: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
Adapter v2: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
4C3 pre-run seal SHA256: `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97`
4C3 sealed script SHA256: `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
Post-run manifest records identical pre/final script SHA and `script_hash_match=true`.

## PRE-REGISTERED QUESTION
Does sign/Hamming retrieval materially depend on preserving native coordinate axes, such that orthogonal coordinate mixing degrades retrieval even though centered continuous geometry is exactly preserved?

Frozen methods: NATIVE_SIGN96; signed-permutation Hamming-invariance control; data-independent block-Haar rotations at block sizes `{2,4,8,16,32,96}` with seeds `{43001,43002,43003,43004,43005}`; frozen ITQ96 centered reference; centered FLOAT96 invariance reference. No post-result expansion is allowed.

## COMPUTE CLAIMS TO REPRODUCE — DO NOT ASSUME TRUE
- Full cohort: 470/470; chain/sanity: PASS 29/29.
- Native Fractional Evidence R@3: `54.197517730496%`.
- Full-Haar96 mean Fractional Evidence R@3: `38.271666666667%`.
- `D96 = S_haar96 - S_native = -15.925851 pp`.
- Full-Haar96 seed values: 43001 `36.1395390070922%`; 43002 `39.1393617021277%`; 43003 `37.9320921985816%`; 43004 `38.0195035460993%`; 43005 `40.1278368794326%`. All five are below native.
- Preregistered verdict: `[STRONG AXIS-STRUCTURE EFFECT — FULL ORTHOGONAL MIXING HURTS SIGN RETRIEVAL]`.
- Signed-permutation control: exact PASS.
- Continuous-invariance max absolute score error: `1.1102230246251565e-15`, below frozen `1e-12` gate.
- Block means: b2 `50.3931%`, b4 `47.2620%`, b8 `43.6954%`, b16 `40.6348%`, b32 `39.4257%`, b96 `38.2717%`; reported `rho(log2 b,gap)=-1.0`.
- Native variance-CV mean `0.993725`; Haar96 `0.149863`. Native effective-coordinate count `48.324473`; Haar96 `93.885425`.
- Heterogeneity alignment: `[HETEROGENEITY-ALIGNMENT NOT CONSISTENT]`.
- ITQ96 Fractional R@3 `37.614113%`; full-Haar envelope `36.1395%..40.1278%`; `[ITQ WITHIN FULL-HAAR ENVELOPE]`.
- Native-rank Spearman: Haar96 mean `~0.177045`; ITQ `~0.172479`.
- Native unique-code fraction `0.995505`; Haar96 `0.992231`. Native top-3 boundary tie rate `0.234043`; Haar96 `0.340426`.

## ROBUSTNESS PROFILE TO REPRODUCE
Independent Head Researcher inspection of the question-level table gives native-vs-mean-Haar96 W/T/L `245/138/87`, median native advantage `+4.75 pp`, mean native advantage `+15.925851 pp`; after removing the top 50 positive contributors, the remaining mean advantage is still about `+8.56 pp`. Treat as fixed-benchmark composition sensitivity only. Reproduce or correct exactly.

## ZERO-TRUST AUDIT REQUIREMENTS
1. Verify seal, script, manifest, output hashes, adapters, cohort, parent Task 4C2 bindings, and dataset hash if practical. If the 277 MB dataset is not independently hashed, state that limitation.
2. Inspect sealed source to ensure results could not affect seeds, block sizes, quintiles, thresholds, metrics, tie priority, or any frozen choice.
3. Confirm native variance-CV quintiles were frozen before retrieval outcomes were joined; exactly 94 questions per quintile; no outcome leakage.
4. Prove/check signed-permutation is a common permutation plus common coordinate sign flips and independently verify exact Hamming distance/ranking/top-3/metric invariance. Any mismatch is blocking.
5. Verify every block-Haar transform is data-independent and determined only by frozen seed/permutation/block size/IID-normal QR plus deterministic diagonal sign correction. No archive/query/gold-dependent orientation.
6. Verify orthogonality, norm preservation, centered dot/cosine preservation, and maximum continuous-score difference `<=1e-12` for every question/block/seed. A substantive failure is blocking.
7. Verify archive and query receive the same transform; audit row/column orientation, permutation reconstruction, dtype, zero threshold, Hamming direction, complement/sign logic.
8. Independently aggregate raw trials to reproduce Native, ITQ and every block/seed ANY/ALL/Fractional R@3. Collapse nuisance/seeds within question correctly; they are not independent statistical units.
9. Recompute D96 and apply the preregistered decision band exactly; confirm all 5 full-Haar seeds are below native before accepting STRONG.
10. Recompute the block gradient, seed gaps, W/T/L, median paired gaps, native-rank Spearman, top-3 overlap; test whether any coding artifact mechanically forces monotonicity.
11. Recompute heterogeneity diagnostics and quintile alignment. The frozen result is NOT CONSISTENT; do not rescue with alternative metrics/bins.
12. Recompute ITQ-vs-Haar envelope. Do not infer ITQ is equivalent to random Haar merely because it lies inside the range.
13. Audit collision/tie diagnostics but do not infer causality. Test tie-priority asymmetry, corpus/gold-order leakage, boolean packing, exact-code handling and score direction.
14. Reproduce robustness profile `245/138/87`, median `+4.75 pp`, top-50 residual `~+8.56 pp` or provide corrected values.
15. Reproduce frozen strata (question type, one/multi-gold, archive quartiles, reuse tertiles) and report whether native-minus-Haar96 is positive in every frozen stratum. No post-hoc strata.
16. Actively search for one defect capable of explaining a substantial fraction of D96: wrong/double permutation, different tie priorities, altered centered representation, query-dependent rotation, incorrect QR sign correction, non-orthogonal transform, outcome leakage, overweighted seeds/nuisance, duplication, cohort mismatch, denominator/gold mapping error, or archive/query transform mismatch.

## INTERPRETATION DISCIPLINE
If the audit passes, the strongest licensed statement is:

> On the frozen LongMemEval representation and protocol, data-independent orthogonal coordinate mixing preserves centered continuous geometry to numerical precision but materially degrades zero-threshold sign/Hamming evidence retrieval relative to the native axes.

Do not claim coordinate heterogeneity is the unique cause: the preregistered heterogeneity-alignment test failed. Do not claim collision/ties cause the loss. Do not claim ITQ is equivalent to Haar. Do not claim cross-benchmark or population generalization. No population CI/p-values.

## REQUIRED VERDICT
Return exactly one top-level verdict: `PASS`, `PASS WITH CONDITIONS`, or `FAIL`.

Then answer exactly:
- TASK 4C3 NUMERICAL CHECKPOINT MAY FREEZE: YES/NO
- STRONG AXIS-STRUCTURE EFFECT IS ESTABLISHED AS A FIXED-BENCHMARK CAUSAL INTERVENTION: YES/NO/NOT ESTABLISHED
- CONTINUOUS-GEOMETRY INVARIANCE: VERIFIED/FAILED/NOT FULLY VERIFIED
- SIGNED-PERMUTATION POSITIVE CONTROL: VERIFIED/FAILED/NOT FULLY VERIFIED
- BLOCK-SIZE GRADIENT: VERIFIED/FAILED/NOT FULLY VERIFIED
- HETEROGENEITY-ALIGNMENT CLAIM: NOT CONSISTENT / CONSISTENT / NOT VERIFIED
- ITQ-vs-HAAR ENVELOPE: BELOW/WITHIN/ABOVE/NOT VERIFIED
- MECHANISM 'NATIVE AXES MATTER FOR SIGN/HAMMING ON THIS FROZEN REPRESENTATION': SUPPORTED/NOT SUPPORTED/NOT ESTABLISHED
- STRONGER COORDINATE-HETEROGENEITY CAUSAL MECHANISM: SUPPORTED/NOT SUPPORTED/NOT ESTABLISHED
- NEXT STEP MAY PROCEED BEYOND 4C3: YES/NO

If PASS/PASS WITH CONDITIONS, identify the strongest remaining falsification risk and specify exactly one next theorem/experiment target. Do not run it.

## STOP RULE
Stop after the audit. Do not launch LoCoMo, rescue experiments, new rotations, thresholds, widths, or any other scientific experiment.