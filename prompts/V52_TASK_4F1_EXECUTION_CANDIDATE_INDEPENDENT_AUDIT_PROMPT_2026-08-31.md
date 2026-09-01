# V52 Task 4F1 — Execution Candidate Cold-Start Independent Audit

Date: 2026-08-31  
Role: cold-start independent implementation auditor

## Mission

Independently audit the guarded, outcome-capable Task 4F1 implementation candidate without running BEAM retrieval quality and without opening or calculating Native/Haar/ITQ evidence-recall outcomes.

Your task is to decide whether these exact implementation bytes faithfully execute the already sealed 1,712-question Task 4F0 restricted-cohort protocol and are safe to place before a later, separate Head Researcher preregistration decision.

This audit does not authorize Task 4F1 preregistration or execution. Do not create a valid run-authorization file.

## Canonical locations

Repository: `haliltalhaertan/llmzip`  
Expected repository HEAD: `d3c7aa09c9553cd5ac100e668923abab602e4257`  
Expected branch: `codex/research-lead-takeover-2026-08-31`

Execution candidate namespace:

`../task4f1_execution_candidate_2026_08_31/`

Preparation evidence namespace:

`../task4f1_execution_candidate_preflight_2026_08_31/`

Sealed Task 4F0 namespace:

`../audit_v52_t4f0_restricted_refreeze_2026_08_31/`

Accepted Task 4F0 audit namespace:

`../audit_v52_t4f0_restricted_refreeze_independent_audit_2026_08_31/`

Pinned BEAM materialization:

`../../BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9/`

Accepted pinned-tree manifest:

`../audit_v52_t4f0_codex_2026_08_31/pinned_tree_manifest.json`

Write all audit outputs only to a new namespace:

`../audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31/`

Do not modify the candidate namespace, the sealed Task 4F0 namespace, original 4C3/4D/4F0 artifacts, or existing audit outputs.

## Exact byte anchors

- implementation `v52_t4f1_beam_retrieval.py`: 52,673 bytes; SHA256 `28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428`
- candidate payload inventory `PAYLOAD_HASHES.json`: SHA256 `278dbf80d6388a7dcd2605791283442615d5a951b2ef1e1ce1b6c92b4dd392b7`
- candidate seal `CANDIDATE_EXECUTION_SEAL.json`: SHA256 `a1277e4665936ea691505a2d386c1d6a4824c2ebc5e5e56d6a94aba1f58876cd`
- preparation preflight `IMPLEMENTATION_PREFLIGHT.json`: SHA256 `138f291ee53a70c0c4f37d4797e683acd1db77d5f362db676b5517e0d8f91f49`
- sealed Task 4F0 final seal: SHA256 `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`
- sealed cohort: SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`
- restricted protocol: SHA256 `f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1`
- dependency lock: SHA256 `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`
- accepted pinned-tree manifest: SHA256 `650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`
- pinned BEAM commit: `3e12035532eb85768f1a7cd779832b650c4b2ef9`

Any mismatch is blocking. Record a dirty worktree but do not repair it.

## Hard no-outcome boundary

Forbidden during this audit:

- executing runner mode `run` or `finalize` with a valid authorization;
- constructing a valid `V52_T4F1_RUN_AUTHORIZATION_V1` file;
- computing or inspecting any BEAM Native/Haar/ITQ retrieval-quality metric;
- ranking real BEAM probing questions against their archives;
- opening answers, ideal answers, rubrics or evaluator output for analysis;
- using gold/source IDs as fitting, rotation, threshold, tie, seed or cohort-selection inputs;
- changing candidate bytes after seeing any outcome-like value.

Allowed:

- candidate package preflight;
- runner `preflight` mode;
- AST/static analysis;
- synthetic fixtures with invented texts, IDs, questions and gold sets;
- raw archive-only representation canaries with a fixed synthetic query and no real gold;
- negative authorization tests that must fail before any archive result is written;
- independent aggregation tests on wholly synthetic result tables.

If a check risks producing a real retrieval-quality value, stop and redesign the check.

## Required audit gates

### 1. Namespace and byte closure

Independently re-hash every candidate file. Verify `PAYLOAD_HASHES.json`, candidate seal bindings, file counts, sizes, no unbound payload and exact upstream anchors. Confirm that `RUN_AUTHORIZATION_TEMPLATE.json` cannot satisfy the runner’s authorization schema.

### 2. Environment enforcement

Use the exact isolated environment: Python 3.12.13, NumPy 2.3.2, SciPy 1.16.1, scikit-learn 1.7.1, psutil 7.0.0, `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1`, `PYTHONHASHSEED=0`, one process and one worker.

Run negative tests for at least one wrong dependency/thread value. It must block before representation or outcome work.

### 3. Corpus byte identity

Do not trust the materialized directory name. Independently reconstruct Git blob SHA1 from raw bytes for every used `chat.json` and `probing_questions.json`, compare size/blob to the accepted pinned-tree manifest and confirm 192/192 matches across the 96 eligible archives.

### 4. Cohort and source-ID join

Independently verify 2,000 rows, exactly 1,712 eligible, 96 archives, excluded archives exactly `1M::5`, `1M::26`, `1M::33`, `1M::34`, all eligible categories exact/non-abstention, positive gold cardinality and unique archive message IDs. Verify every eligible frozen gold ID joins exactly once to its archive raw ID. Do not rank questions.

### 5. Static and runtime leakage audit

Trace every caller into `fit_archive_representation`, both SVD fits, archive mean, signed permutation, Haar generation and ITQ fitting. Prove that only ordered `role + ': ' + content` archive texts enter representation fitting and only centered archive C96 enters ITQ fitting.

Instrument or monkeypatch fit functions in a copy/import-only audit harness to log runtime payload types/shapes. Use synthetic questions and labels. Confirm question text enters only post-fit transform; gold IDs enter only `metrics_at_3` after ranking. Search for answer/rubric/difficulty/ability/source-order/evaluator leakage and cross-archive cache contamination.

### 6. Representation equivalence

Independently reproduce the raw `100K::12` fixed-canary gate without opening probing questions or gold labels:

- 392 units;
- archive shape 392×96 and rank 96;
- query shape 1×96;
- archive SHA256 `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`;
- query SHA256 `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`;
- finite values and repeat-identical bytes.

Confirm archive caching is mathematically identical to refitting the same query-independent archive model and cannot mix different archives.

### 7. Binary arms and invariance

On synthetic/pre-outcome inputs:

- Native uses centered coordinates and threshold `>=0`;
- signed permutations use seeds 43001..43005 with the exact declared NumPy operation order;
- for every signed seed, all Hamming distances, tie sets, full rankings and top-three sets equal Native exactly;
- Haar uses the declared Gaussian→QR→diagonal-sign correction and seeds 43001..43005;
- each Haar matrix is orthogonal and archive/query dot products and norms are preserved within `1e-12`;
- transforms are common to archive/query and neither double-applied nor transposed inconsistently.

### 8. ITQ implementation

Verify the candidate’s ITQ against the canonical audited Task 4C2 `fit_itq` implementation: NumPy `default_rng`, SVD initialization, exactly 100 iterations, threshold orientation, covariance orientation and Procrustes update. Confirm seeds 101/202/303/404/505, archive-only fit, common archive/query rotation and descriptive-only status. Test byte/numeric equivalence on synthetic centered matrices.

### 9. Tie and nuisance semantics

Verify exact priority bytes:

`uint128_be(SHA256(prefix + NUL + archive_id + NUL + canonical_memory_key)[:16])`.

Audit 128-bit ordering, high/low splitting, lexsort key precedence and canonical-index tertiary tie break. Confirm memory-key serialization is exactly `tier::conversation_id::decimal_raw_message_id` and independent of answer/gold/source order.

The sealed priority contains no trial index. Confirm the implementation therefore emits trials 0..19 as identical deterministic replication rows and never treats them as independent evidence. Decide explicitly whether this literal interpretation is faithful and scientifically non-misleading. Any hidden trial-dependent priority is blocking.

### 10. Metrics and structural zero

Using synthetic IDs only, independently test Fractional Source Evidence Recall@3, ANY@3 and ALL@3, including zero hits, partial multi-gold, complete gold and more-than-three-gold structural zero. Verify retrieved items are raw message IDs, top-k is exactly three and duplicates cannot inflate hits.

### 11. Checkpoint/resume safety

With synthetic or authorization-free harnesses, verify atomic temporary-file replacement, paired CSV/meta requirements, hash/size/count validation, refusal to overwrite, resume skipping only validated checkpoints and no finalization of fewer than 96 archives. Check path construction and archive-selection validation.

### 12. Authorization guard

Run negative tests for missing authorization, the supplied template, wrong script hash, wrong seal hash, wrong cohort hash, wrong output namespace, wrong required archive count and forbidden outcome-access status. Every case must block before output-directory creation or real archive ranking.

Inspect whether a user could bypass authorization through `finalize`, resume, archive selection, symlinks, stale checkpoints, direct imports or malformed JSON. Separate normal CLI protection from adversarial Python source modification; the latter is prevented by byte bindings, not claimed as an OS sandbox.

### 13. Row schema and aggregation

Using wholly synthetic result rows, verify:

- 320 rows per eligible question: Native 20; signed-permutation 5×20; Haar 5×20; ITQ 5×20;
- complete and unique `(question, method, seed, trial)` cells;
- trial collapse inside question×method×seed;
- seed collapse inside question×method;
- exactly 1,712 equal-weight question units per arm at final aggregation;
- no seed/trial/archive-size weighting;
- signed-permutation aggregate equals Native if the hard control passes;
- finalization prints no metric values and sets `interpretation_authorized=false`.

Actively test malformed/missing/duplicate rows and ensure they block rather than silently aggregate.

### 14. Active bug hunt

Do not merely confirm declarations. Search for at least these failure modes:

- wrong BEAM question indexing;
- raw ID string/integer mismatch;
- incorrect recursive message order;
- wrong memory-key serialization;
- lexsort priority reversal;
- sign threshold inconsistency at exact zero;
- signed-permutation operation-order mismatch;
- wrong Haar QR orientation/sign correction;
- ITQ transpose/orientation error;
- query entering archive or ITQ fit;
- archive model reused across different conversations;
- gold/source IDs entering priority or fitting;
- wrong ALL@3 for more than three gold units;
- duplicated trial/seed rows or incorrect 320-row count;
- partial/stale checkpoint acceptance;
- authorization bypass;
- output overwrite;
- console leakage of partial metric values;
- candidate payload manifest or seal staleness.

## Required outputs

Write at least:

- `INDEPENDENT_EXECUTION_AUDIT_REPORT.md`
- `GATE_TABLE.csv`
- `INDEPENDENT_EXECUTION_AUDIT_HASHES.json`
- `COMMAND_LOG.txt`
- `STATIC_RUNTIME_LEAKAGE_AUDIT.json`
- `AUTHORIZATION_NEGATIVE_TESTS.json`
- `SYNTHETIC_METHOD_EQUIVALENCE.json`
- `SYNTHETIC_AGGREGATION_TESTS.json`
- any audit scripts required to reproduce those results

Hash every audit output except the self-referential manifest itself. Record all superseded attempts rather than silently discarding them.

## Verdict

Return exactly one:

`PASS WITH CONDITIONS — EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT AUTHORIZED`

or

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

PASS requires every load-bearing gate above to pass. A PASS still does not authorize preregistration, execution or outcome access; it only permits the Head Researcher to seal the execution implementation and proceed to a separate Task 4F1 preregistration decision.

End with a concise account of what was tested, what could not be tested without outcomes, exact hashes, discovered defects and remaining conditions. Do not modify the candidate seal.
