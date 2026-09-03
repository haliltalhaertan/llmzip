# V52 Task 4F1 — Byte-Bound Execution Specification

Date: 2026-09-01  
Status: `PREPARED — NOT INDEPENDENTLY AUDITED — DO NOT RUN`

## Scope

This specification binds implementation details required to make the independently sealed Task 4F0 restricted-cohort protocol executable. It does not alter the 1,712-question cohort, excluded archives, representation family, arms, seeds, top-k, metrics, dependency lock, tie-priority formula, or stop rule.

No BEAM Native/Haar/ITQ retrieval-quality result may be computed until this exact implementation is independently audited, a separate Task 4F1 preregistration is accepted, and a byte-bound Head Researcher run authorization is issued.

## Exact input bindings

- llmzip parent commit: (see the runner's module constants)
- BEAM commit: (see the runner's module constants)
- sealed restricted cohort SHA256: (see the runner's module constants)
- final restricted seal SHA256: (see the runner's module constants)
- restricted protocol SHA256: (see the runner's module constants)
- dependency lock SHA256: (see the runner's module constants)
- accepted BEAM pinned-tree manifest SHA256: (see the runner's module constants)

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

## Canary specification

The real-archive representation canary on `100K::12` asserts, and the runner is the sole
normative source for every value below:

1. `archive_units` equals the count enforced by the runner;
2. `centered96` and query shapes as enforced by the runner;
3. the archive sign-code digest equals `EXPECTED_REAL_CANARY_ARCHIVE_SIGN_SHA256`;
4. the query sign-code digest equals `EXPECTED_REAL_CANARY_QUERY_SIGN_SHA256`;
5. both minimum absolute values exceed `CANARY_SIGN_MARGIN`.

Sign codes, not raw float bytes, are the bound quantity: the V3 raw-array digests varied across
conformant BLAS kernel dispatches, which is why that candidate was blocked. Condition 5 is the
guard that makes 3 and 4 safe — it fails closed if the representation ever drifts close enough to
zero for a sign code to flip between conformant environments.

## This document is not normative

**No value in this file is a requirement.** Every threshold, digest, seed, count, tolerance and
identifier that governs execution lives in exactly one place: the module constants of
`v52_t4f1_beam_retrieval.py`. This document refers to them **by constant name only** and
deliberately contains no value-shaped literal of its own.

That is the whole of the package's consistency claim, and it is stated at exactly the strength it
can be checked at. Two earlier packages claimed instead that every value had one authoritative
source and that all restatements agreed. Both claims were defeated by independent audit, because
reconciling restatements across arbitrary prose in arbitrary encodings is not something a package
checker can establish. This package makes no such claim. It removes the restatements instead, so
there is nothing left to reconcile.

The checker enforces a prohibition rather than an agreement: the narrative payloads
(`EXECUTION_SPEC.md`, `README.md`, `RUN_AUTHORIZATION_TEMPLATE.json`, `DEPENDENCY_LOCK.txt`) must
contain **no** sha256- or sha1-shaped literal at all. Value-shaped literals are permitted only in
the runner, which is their single source; in `PAYLOAD_HASHES.json`, which computes them from the
package; in `CANDIDATE_EXECUTION_SEAL.json`, which binds those two; and in the package checker,
which pins the accepted runner identity.

## Package versioning versus schema versioning

This is the V7 **package**. It is not a schema version bump. The retrieval runner is byte-identical
to the audited V4 runner, so every schema literal the runner verifies stays at its V4 value.
Relabelling them would either change the runner, breaking the byte-identity that permits a
delta-scoped audit, or make this payload fail closed against the runner it ships with. A successor
must not "correct" them.

## Status and attestation

`CANDIDATE_EXECUTION_SEAL.json` records `status_at_audit_submission`, an immutable historical fact
fixed when the package is handed to an auditor. It is never edited afterwards.

The candidate makes **no claim at all** about post-audit acceptance state. Acceptance lives in
`ops/CURRENT_STATE.json` and `docs/CONTINUITY_LEDGER.md` on the canonical branch, outside this
package and outside anything the package can redirect.
