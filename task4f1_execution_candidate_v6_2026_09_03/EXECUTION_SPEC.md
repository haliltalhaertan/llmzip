# V52 Task 4F1 — Byte-Bound Execution Specification

Date: 2026-09-01  
Status: `PREPARED — NOT INDEPENDENTLY AUDITED — DO NOT RUN`

## Scope

This specification binds implementation details required to make the independently sealed Task 4F0 restricted-cohort protocol executable. It does not alter the 1,712-question cohort, excluded archives, representation family, arms, seeds, top-k, metrics, dependency lock, tie-priority formula, or stop rule.

No BEAM Native/Haar/ITQ retrieval-quality result may be computed until this exact implementation is independently audited, a separate Task 4F1 preregistration is accepted, and a byte-bound Head Researcher run authorization is issued.

## Exact input bindings

- llmzip parent commit: `d3c7aa09c9553cd5ac100e668923abab602e4257`
- BEAM commit: `3e12035532eb85768f1a7cd779832b650c4b2ef9`
- sealed restricted cohort SHA256: `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`
- final restricted seal SHA256: `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c`
- restricted protocol SHA256: `f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1`
- dependency lock SHA256: `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`
- accepted BEAM pinned-tree manifest SHA256: `650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`

The materialized BEAM corpus is not required to contain `.git`. For every used `chat.json` and `probing_questions.json`, the runner reconstructs the Git blob SHA1 directly from the raw file bytes (`SHA1("blob " + decimal_length + NUL + payload)`) and requires both blob ID and size to equal the accepted pinned-tree manifest. Manifest commit identity alone is insufficient.

## Archive and question identity

Canonical archive order is lexical `(tier, conversation_id)` order. Canonical memory order is the recursive order of the pinned `chat.json`: batch list, then turn list, then message list. Every eligible archive must have unique raw message IDs.

The textual memory key used by the sealed tie formula is exactly:

`tier + "::" + conversation_id + "::" + decimal_raw_message_id`

The fitted memory text is exactly UTF-8 `role + ": " + content`. Key fields, question metadata, gold IDs, answers, rubrics, difficulty, ability and evaluator fields are excluded from fitting.

Questions are resolved from the frozen `audit_question_id = tier::conversation_id::ability::one_based_index`. Only the `question` string is transformed after archive fitting. Gold IDs are used only after ranking to score the frozen metrics.

## Representation and caching

Each archive representation is fitted once from its complete ordered archive text and reused for every eligible question in that same archive. This is an exact cache of a query-independent archive-only fit, not a cross-question or query-adaptive fit.

The implementation uses the sealed word/character TF-IDF, latent SVD32 (`5101`), mixed SVD96 (`5204`), L2 normalization and archive-mean centering recipe. All calculations entering invariance checks and rotations use float64 after mixed-SVD output.

No query, answer, source ID, cohort category or retrieval result may alter a vectorizer, SVD, mean, dimension, threshold, rotation or ranking rule.

The outcome-free preflight also fits raw archive `100K::12` and transforms only the fixed canary string `Which project phase mentioned module 7 and a deadline?`. Its acceptance criteria are defined in exactly one place, the **Canary specification** section below, which is the sole normative source for this check. No probing-question file or gold label enters this canary.

## Arms

`NATIVE_SIGN96`: threshold centered archive/query coordinates at `>= 0`.

`SIGNED_PERM_CONTROL96`: for each seed `43001, 43002, 43003, 43004, 43005`, NumPy `default_rng(seed)` generates `permutation(96)` followed by 96 equiprobable signs from `[-1.0, +1.0]`. The same permutation/signs are applied to archive and query. Every Hamming vector and complete ranking must equal Native exactly or the archive aborts.

`HAAR96_SIGN`: for each seed `43001, 43002, 43003, 43004, 43005`, draw an IID standard-normal 96×96 matrix with NumPy `default_rng(seed)`, compute reduced QR, and multiply each Q column by `sign(diag(R))`, replacing exact zero signs by `+1`. Apply the same rotation to archive and query, verify continuous dot products and norms within `1e-12`, then threshold at `>= 0`.

`ITQ96_CENTERED`: descriptive only. For each seed `101, 202, 303, 404, 505`, use the canonical audited archive-only ITQ Procrustes update for exactly 100 iterations. Initialize from the SVD orthogonal factor of a seeded IID standard-normal 96×96 matrix. At each iteration set `B = +1` where `C96 @ R >= 0`, otherwise `-1`; then update from the SVD of `B.T @ C96` using the audited orientation. The query never enters ITQ fitting.

## Tie and trial interpretation

The sealed tie priority has no trial input. It is implemented literally as the unsigned big-endian integer represented by the first 16 bytes of:

`SHA256(b"V52_T4F0_TIE_PRIORITY_V1" + b"\0" + archive_id_utf8 + b"\0" + memory_key_utf8)`.

Ranking is ascending integer Hamming distance, then ascending 128-bit priority, then ascending canonical archive index.

Consequently, `trial=0..19` are deterministic replication identities under the same frozen priority. They must produce identical top-three sets for a fixed question/method/seed. The code computes the ranking once and emits the 20 required identical trial rows. It does not introduce an unsealed trial-dependent priority or pretend the repeated rows are independent evidence.

## Metrics and aggregation

For each eligible question, use the sealed Fractional Source Evidence Recall@3, ANY@3 and ALL@3 definitions. Questions with more than three gold units retain structural ALL@3 zero.

Finalization requires exactly 96 archive checkpoints and 1,712 questions. Before aggregation it validates the exact CSV schema, unique question×method×seed×trial cells, frozen question metadata, method/seed sets, 20-trial coverage, three unique retrieved IDs, sorted valid Hamming distances, metric ranges, structural ALL@3 zeros and exact Native/signed-control equality. Nuisance rows collapse inside question×method×seed; seeds then collapse inside question×method; questions receive equal weight. Seeds and trials are never treated as independent statistical units.

The implementation does not encode a scientific verdict band. A later Task 4F1 preregistration must define the decision variable and interpretation before run authorization.

## Run guard

`run` and `finalize` require a separate JSON authorization with schema `V52_T4F1_RUN_AUTHORIZATION_V4`. It must bind:

- the exact implementation SHA256;
- the independently accepted execution-candidate seal SHA256;
- the exact cohort SHA256;
- the exact output namespace basename;
- 96 required archives;
- the accepted preregistration-seal SHA256;
- a unique 256-bit authorization nonce and authorization ID;
- explicit `AUTHORIZED_FOR_TASK_4F1_EXECUTION` and outcome-access fields.

The exact canonical authorization payload must carry a valid HMAC-SHA256. The 32-byte HMAC key is supplied only through `V52_T4F1_AUTH_HMAC_KEY_HEX`; its SHA256 commitment must already be fixed in the independently accepted execution seal. A missing, malformed, arbitrary or mismatched key fails before output-directory creation. The key itself must never be stored in the repository, candidate, preregistration, audit output, command log or result namespace.

During candidate audit the seal commitment is literally `PENDING_HEAD_RESEARCHER_PREREGISTRATION`; therefore no authorization can pass. The final commitment may be inserted only by the Head Researcher during the separate preregistration/sealing decision, after which all affected seal and authorization hashes must be recorded. This candidate package contains no valid authorization. A template cannot authorize execution.

## Checkpoint and stop behavior

Archive outputs are written atomically as one CSV plus one hash-binding metadata JSON. Every metadata file binds `script_sha256`, `cohort_sha256`, `execution_candidate_seal_sha256` and `run_authorization_sha256`. Existing, provenance-mismatched or internally inconsistent checkpoints are never overwritten. Resume and finalization skip or accept only checkpoints whose provenance, sizes, counts and hashes validate. Console progress contains counts, not metric values.

Before aggregation, finalization independently canonicalizes the retrieved IDs and the frozen cohort gold IDs, recomputes Fractional Source Evidence Recall@3, ANY@3 and ALL@3, and rejects any stored-metric mismatch. It also requires the ordered top-three IDs and their Hamming distances for every signed-permutation seed/trial cell to equal the corresponding Native cell exactly. Trial replication identity covers both IDs and distances.

The three derived CSV destinations, their temporary paths, the post-run manifest and its temporary path must all be absent before finalization begins. Derived outputs are committed with exclusive no-replace semantics; an existing or crash-left partial output blocks forensic review rather than being silently replaced.

The candidate package preflight walks the namespace recursively. Any nested or top-level file absent from `PAYLOAD_HASHES.json`, including generated `__pycache__` bytecode, blocks sealing.

Finalization refuses to run until all 96 archive checkpoints are present and valid. After outcome access, no method, seed, threshold, representation, priority, denominator, metric or cohort repair is allowed.

## Canary specification (NORMATIVE — sole source)

This section is the single normative source for the real-archive representation canary.
No other bound payload may state canary acceptance criteria; any restatement elsewhere is a
derived mirror, must be typed as such in `NORMATIVE_SOURCE_MAP.json`, and must equal these
values exactly.

The canary on `100K::12` asserts:

1. `archive_units == 392`;
2. `centered96` shape `[392, 96]` and query shape `[1, 96]`;
3. `sha256(packbits(centered96 >= 0))` equals
   `7365b6c4ba7753ee5431f89816c3151a2618f475415024d8932c839609ded5b5`;
4. `sha256(packbits(query >= 0))` equals
   `5e40a5d1f0d33bf16c4005ed8aa172464dd1fb205da983f5373c9940f4ccad2b`;
5. `min(|centered96|) > 1e-9` and `min(|query|) > 1e-9`.

Sign codes, not raw float bytes, are the bound quantity. The V3 raw-array digests are
**superseded and deprecated**: they varied across conformant BLAS kernel dispatches, which is
why the V3 candidate was blocked. They are enumerated as deprecated literals in
`NORMATIVE_SOURCE_MAP.json` and must not appear as a requirement in any bound payload.

Condition 5 is the guard that makes 3 and 4 safe: it fails closed if the representation ever
drifts close enough to zero that a sign code could flip between conformant environments.

## Package versioning versus schema versioning

This is the V5 **package**. It is not a schema version bump. The retrieval runner is
byte-identical to the audited V4 runner, so every schema literal the runner verifies stays at
its V4 value: `V52_T4F1_RUN_AUTHORIZATION_V4`, `V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4`,
`V52_T4F1_ARCHIVE_RESULT_META_V4`, `V52_T4F1_POST_RUN_MANIFEST_V4` and
`V52_T4F1_IMPLEMENTATION_PREFLIGHT_V4`.

Relabelling those literals to "V5" would either change the runner, breaking the byte-identity
constraint that permits a delta-scoped audit, or make this payload fail closed against the
runner it ships with. A successor must not "correct" them.

## Status and attestation precedence

`CANDIDATE_EXECUTION_SEAL.json` records `status_at_audit_submission`, an immutable historical
fact fixed when the package is handed to an auditor. It is never edited afterwards to reflect
acceptance.

Post-audit acceptance state is carried solely by a detached, hash-bound attestation under
`docs/v52/task4f1/`. Where the two appear to disagree, the detached attestation is
authoritative for current state and the seal is authoritative for what was submitted.
