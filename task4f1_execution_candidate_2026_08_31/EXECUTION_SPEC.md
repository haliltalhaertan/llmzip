# V52 Task 4F1 — Byte-Bound Execution Specification

Date: 2026-08-31  
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

The outcome-free preflight also fits raw archive `100K::12` and transforms only the fixed canary string `Which project phase mentioned module 7 and a deadline?`. Its archive/query array SHA256 values must exactly reproduce the independently audited digests `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025` and `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`. No probing-question file or gold label enters this canary.

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

`run` and `finalize` require a separate JSON authorization with schema `V52_T4F1_RUN_AUTHORIZATION_V1`. It must bind:

- the exact implementation SHA256;
- the independently accepted execution-candidate seal SHA256;
- the exact cohort SHA256;
- the exact output namespace basename;
- 96 required archives;
- explicit `AUTHORIZED_FOR_TASK_4F1_EXECUTION` and outcome-access fields.

This candidate package contains no such authorization. A template cannot authorize execution.

## Checkpoint and stop behavior

Archive outputs are written atomically as one CSV plus one hash-binding metadata JSON. Existing or mismatched archive checkpoints are never overwritten. Resume skips only checkpoints whose sizes, counts and hashes validate. Console progress contains counts and hashes, not metric values.

Finalization refuses to run until all 96 archive checkpoints are present and valid. After outcome access, no method, seed, threshold, representation, priority, denominator, metric or cohort repair is allowed.
