# V52 Task 4C3 — Cold-Start Independent Adversarial Audit

Date: 2026-08-28  
Audit branch: `audit/v52-t4c3-independent-2026-08-28`  
Pinned compute commit: `7959c1df46b09f48bdbd1d1922bf62715e119839`

## Top-level verdict

**PASS WITH CONDITIONS**

**AUDIT LEVEL:** full raw-table + source

No chain-of-custody, implementation, aggregation, or intervention defect was found that can materially explain the reported `D96` result. The main fixed-benchmark axis-structure result reproduces independently from the raw trial table and is supported by the source-level intervention logic.

The remaining conditions are provenance/governance conditions, not observed scientific discrepancies:

1. The 277,383,467-byte LongMemEval cleaned-S dataset was not independently downloaded and re-hashed in this audit environment. Its expected SHA256 is pinned and the Task 4C3 sealed runtime gate reports it matched.
2. The adapter v1/v2 source files were independently inspected at the pinned Git commit, but their SHA256 values were not independently recomputed from separately downloaded GitHub raw bytes in this audit environment. The sealed Task 4C3 runtime gate would abort on adapter mismatch, and the frozen parent native/ITQ metrics reproduce exactly.
3. `CHAIN_OF_CUSTODY.md` / `tools/verify_frozen_artifacts.py` on `main` contain stale Task 4C2-era status/comments and do not yet provide explicit Task 4C3 verifier coverage. This is a governance/documentation defect, not a scientific-run defect.
4. The heterogeneity-quintile temporal freeze is reconstructible exactly from the sealed deterministic rule and raw native heterogeneity table, but the work-only temporal flag itself is not among the canonical output artifacts. This weakens independent proof of timing, not the `D96` intervention.

## Chain of custody

Canonical Drive bytes were fetched for the Task 4C3 pre-run seal, sealed script, post-run manifest, and the complete output archive.

Independent SHA256:
- `V52_T4C3_PRE_RUN_SEAL.json` = `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97`
- `v52_t4c3_coordinate_axis_probe.py` = `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
- `V52_T4C3_POST_RUN_MANIFEST.json` = `7bfeae589ffdf86012c04eec02017918cae92c3fa20a699c8d342f4baa39c00c`

The post-run manifest binds the pre-run seal and reports:
- pre-run seal SHA256: exact match
- pre-run script SHA256: exact match
- final script SHA256: exact match

All 26 manifest-declared compact/raw Task 4C3 outputs contained in `V52_T4C3_ALL_OUTPUTS.zip` were independently re-hashed: **26/26 match, 0 mismatches**.

The pinned Git commit exists and contains the preregistered Task 4C3 prompt. Adapter v1 and v2 source are present at the pinned commit and were source-inspected.

## Source-level intervention audit

The sealed script uses the same per-question centered representation for the native and rotation interventions:
`C96 = Y96 - mu96` and `qC96 = QY96 - mu96`, with `mu96` fit from archive documents only.

The representation fitting API accepts archive `memory_text` only. Query transformation occurs only after archive fitting. Gold labels, answer fields, question type, and evidence annotations do not enter the archive fit or rotation construction.

For block-Haar:
- the permutation is generated only from the frozen rotation seed;
- the same permutation/transform is applied to archive and query;
- blocks are exactly `{2,4,8,16,32,96}`;
- QR uses IID standard normal matrices with deterministic diagonal-sign correction;
- thresholding is at zero;
- the assembled transform is orthogonal.

An independent numerical check of the script's `happly`/assembled-matrix indexing for every 6 block sizes × 5 seeds found maximum application mismatch `2.22e-15` and maximum orthogonality error `1.22e-15`. No double-permutation or inverse/permutation basis-indexing bug was found.

For signed permutation, Hamming distances are mathematically invariant under a common coordinate permutation and sign flip. Independent random-vector checking gave maximum Hamming-distance difference 0, and the frozen output control passed all 2,350 question×seed rows.

Hamming ranking is ascending distance with the independent frozen priority as tie-breaker. Code packing is used for collision diagnostics, not for retrieval ranking.

The ITQ reference uses the frozen adapter implementation; its Procrustes update orientation is consistent with the intended `V @ R` encoding.

## Raw-table reproduction

`V52_T4C3_trial_results.csv` has **385,400 rows**, 470 unique primary questions, and exactly 820 rows per question:
- native: 20 nuisance trials
- signed permutation: 5 seeds × 20 trials
- block-Haar: 6 block sizes × 5 seeds × 20 trials
- ITQ: 5 seeds × 20 trials

There are no duplicate `(question, method, block, seed, trial)` cells. Frozen trials are exactly `0..19`. Rotation seeds are exactly `43001..43005`; ITQ seeds are exactly `101,202,303,404,505`.

Fractional recall, ANY and ALL semantics were independently cross-checked against each question's gold cardinality; all rows are consistent.

Independent nuisance/seed collapse reproduces:

| Method | ANY R@3 | ALL R@3 | Fractional R@3 |
|---|---:|---:|---:|
| NATIVE_SIGN96 | 71.308511% | 38.457447% | **54.197518%** |
| SIGNED_PERM_CONTROL96 | 71.308511% | 38.457447% | **54.197518%** |
| ITQ96_CENTERED | 54.276596% | 22.672340% | **37.614113%** |
| HAAR b=96 mean | 54.793617% | 23.748936% | **38.271667%** |

Therefore:

`D96 = S_haar96 - S_native = 38.2716667% - 54.1975177% = -15.9258511 pp`.

Full-Haar seed-specific Fractional R@3 values:
- 43001: 36.1395390% (`-18.057979 pp`)
- 43002: 39.1393617% (`-15.058156 pp`)
- 43003: 37.9320922% (`-16.265426 pp`)
- 43004: 38.0195035% (`-16.178014 pp`)
- 43005: 40.1278369% (`-14.069681 pp`)

All five seeds are below native. The preregistered decision rule is therefore reproduced:

**[STRONG AXIS-STRUCTURE EFFECT — FULL ORTHOGONAL MIXING HURTS SIGN RETRIEVAL]**

## Continuous invariance and positive control

All 14,100 continuous-invariance rows pass. Maximum recorded deviation over orthogonality/norm/dot-product/cosine checks is `1.1102230246251565e-15`, far below the frozen `1e-12` gate.

Signed-permutation retrieval metrics are exactly equal to native, and its diagnostic rows preserve the expected Hamming behavior. These controls strongly disfavor a generic ranking-direction, threshold-sign, tie-priority, or transform-application bug as an explanation for `D96`.

## Block-mixing gradient

Independent recomputation gives:

| b | Fractional R@3 | gap vs native |
|---:|---:|---:|
| 2 | 50.393085% | -3.804433 pp |
| 4 | 47.261950% | -6.935567 pp |
| 8 | 43.695390% | -10.502128 pp |
| 16 | 40.634752% | -13.562766 pp |
| 32 | 39.425709% | -14.771809 pp |
| 96 | 38.271667% | -15.925851 pp |

The degradation is strictly monotone over the six preregistered block sizes. `rho(log2 b, gap) = -1.0` is descriptive only and is not treated as population inference.

Question-level W/T/L in the frozen table's orientation `(block better / tie / block worse)`:
- b2: 96 / 219 / 155
- b4: 99 / 188 / 183
- b8: 95 / 158 / 217
- b16: 82 / 150 / 238
- b32: 100 / 120 / 250
- b96: 87 / 138 / 245

Mean native-rank Spearman falls from `0.6023` at b2 to `0.1770` at b96; mean top-3 overlap falls from `0.6581` to `0.4286`.

## Concentration / composition sensitivity

For native minus mean full-Haar96 at the question level:
- native better / tie / native worse = **245 / 138 / 87**
- median paired advantage = **+4.75 pp**
- mean advantage = **+15.925851 pp**

After removing the largest positive contributors, the remaining mean native advantage is:
- top 10 removed: **+14.098152 pp**
- top 25 removed: **+11.661011 pp**
- top 50 removed: **+8.560675 pp**

Thus the benchmark effect is not essentially explained by a tiny handful of questions. It remains composition-sensitive fixed-benchmark evidence; it is not a population estimate.

## Heterogeneity mechanism audit

Rotation strongly flattens coordinate variance heterogeneity:
- mean native variance-CV: `0.993725`
- mean full-Haar96 variance-CV: `0.149863`
- native effective-coordinate count: `48.3245`
- full-Haar96 effective-coordinate count: `93.8854`

The sealed quintile rule (stable sort by native variance-CV then question id; 94 questions per quintile) was independently reconstructed from `V52_T4C3_native_heterogeneity.csv`; all 470 assignments match the frozen quintile file.

However the preregistered alignment condition fails. Highest-heterogeneity Q5 has a larger native-minus-Haar loss than Q1 for only 3 of 5 seeds, not all 5. Therefore:

**[HETEROGENEITY-ALIGNMENT NOT CONSISTENT]**

Rotation flattens variance heterogeneity, but this experiment does **not** establish variance heterogeneity as the causal mediator of the retrieval loss.

## ITQ vs Haar

ITQ Fractional R@3 = `37.614113%`.

Full-Haar96 seed envelope = `36.139539%` to `40.127837%`.

Therefore:

**[ITQ WITHIN FULL-HAAR ENVELOPE]**

Mean native-rank Spearman:
- ITQ: `0.172479`
- full-Haar96: `0.177045`

This licenses only the statement that the observed ITQ quality lies inside the five-seed preregistered full-Haar envelope and similarly reorders native sign/Hamming neighborhoods. It does not establish that ITQ is mathematically or causally equivalent to random rotation.

## Collision / tie / rank diagnostics

Native mean diagnostics:
- unique-code fraction `0.995505`
- duplicate-code fraction `0.004495`
- largest collision bucket `2.243`
- exact query-code match rate `0`
- candidates at minimum Hamming distance `1.153`
- top-3 boundary tie rate `0.234`

Full-Haar96 mean diagnostics:
- unique-code fraction `0.992231`
- duplicate-code fraction `0.007769`
- largest collision bucket `2.687`
- exact query-code match rate `0`
- candidates at minimum Hamming distance `1.255`
- top-3 boundary tie rate `0.340`

These are consequences/diagnostics of the changed binary geometry; this audit does not promote collisions or ties to causal mediators.

## Defects and conditions

### Observed governance defect
`CHAIN_OF_CUSTODY.md` and `tools/verify_frozen_artifacts.py` contain stale Task 4C2-era statements that adapters are not yet in Git and do not explicitly enumerate Task 4C3. GitHub inspection at the pinned commit confirms both adapters are present.

**Maximum plausible effect on D96: 0.000 pp.** This documentation/verifier-coverage defect does not touch the frozen Task 4C3 raw outputs or the within-representation native-vs-Haar intervention.

### Provenance conditions
The dataset and adapter expected hashes are strongly bound by the sealed runtime input gate, but this audit environment did not independently re-download/re-hash the full dataset or independently compute SHA256 from separately downloaded GitHub adapter bytes. These are verification gaps, not observed mismatches.

### Heterogeneity temporal-freeze condition
The deterministic frozen quintile assignment was independently reconstructed exactly, but the work-only temporal flag is not part of the canonical output bundle. This affects how strongly one can attest the timing of that mechanism diagnostic; it cannot explain `D96`, which does not depend on quintile assignment.

## Required Head Researcher handoff

VERDICT: PASS WITH CONDITIONS  
AUDIT LEVEL: full raw-table + source  
CHAIN OF CUSTODY: PASS WITH CONDITIONS — 26/26 manifest outputs hash-match; seal/script binding passes; bounded independent dataset/adapter rehash conditions remain  
470/470 COHORT: PASS  
SEALED SCRIPT HASH: PASS  
SIGNED-PERMUTATION CONTROL: PASS  
CONTINUOUS ORTHOGONAL INVARIANCE: PASS  
NATIVE FRACTIONAL R@3: 54.197517730496%  
HAAR96 FRACTIONAL R@3: 38.271666666667%  
D96: -15.925851063830 pp  
ALL FIVE HAAR96 SEEDS BELOW NATIVE: YES  
AXIS-STRUCTURE VERDICT REPRODUCED: YES  
BLOCK GRADIENT REPRODUCED: YES  
HETEROGENEITY ALIGNMENT: [HETEROGENEITY-ALIGNMENT NOT CONSISTENT]  
ITQ VS HAAR ENVELOPE: [ITQ WITHIN FULL-HAAR ENVELOPE]  
NATIVE-vs-HAAR ROBUSTNESS/CONCENTRATION: 245/138/87 native-better/tie/native-worse; median +4.75 pp; after removing top 50 positive contributors, remaining mean native advantage +8.560675 pp  
MAX QUANTIFIED DEFECT EFFECT: 0.000 pp on D96 for observed governance/temporal-attestation defects; no scientific defect found  
TASK 4C3 NUMERICAL CHECKPOINT MAY FREEZE: YES — record the provenance conditions and repair stale verifier/governance metadata  
AXIS-STRUCTURE EFFECT ESTABLISHED ON THIS FROZEN BENCHMARK: YES  
VARIANCE-HETEROGENEITY CAUSAL MECHANISM ESTABLISHED: NO  
CROSS-BENCHMARK GENERALIZATION ESTABLISHED: NO  
NEXT STEP RECOMMENDATION: Stop per Task 4C3 stop rule. Record this audit, repair/extend chain-of-custody verifier metadata, independently re-hash adapter raw bytes and the dataset when practical, then freeze the accepted numerical checkpoint. Do not launch Task 4C4/LoCoMo/rescue experiments from this audit.

## Strongest scientifically defensible sentence

On the frozen 470-question LongMemEval benchmark and the sealed centered 96D representation, preregistered data-independent full orthogonal mixing preserved centered continuous geometry to at most `1.11e-15` while reducing mean Fractional Evidence Recall@3 from `54.1975%` to `38.2717%` (`D96 = -15.9259 pp`), with all five Haar seeds below native; therefore preserving the native coordinate axes materially matters for zero-threshold sign/Hamming retrieval on this frozen benchmark.

## Stronger statements that remain unsupported

- Coordinate variance heterogeneity is the causal mediator of the loss.
- ITQ is equivalent to, or "just", a random orthogonal rotation.
- Collision or tie-rate changes are established causal mediators.
- Native SIGN is universally superior to rotated/learned binary representations.
- The result is a population-level statistically significant superiority claim.
- The effect generalizes to LoCoMo, other benchmarks, bit widths, thresholds, or representation families.
- Task 4C2 SIGN-vs-centered-FLOAT and Task 4C3 native-SIGN-vs-Haar have the same concentration/robustness profile.

## Stop rule

Audit complete. No Task 4C4, LoCoMo, larger-scale benchmark run, or rescue experiment was launched.
