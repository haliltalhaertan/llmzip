# V52 TASK 4C2 — INDEPENDENT ADVERSARIAL AUDIT V2
## CENTERING / SIGN-GEOMETRY DIAGNOSTIC
## ZERO-TRUST AUDIT — ADAPTER GAP CLOSED

ROLE
You are the Independent Adversarial Auditor. Your job is not to help the result pass. Your job is to try to break it.

Repository entry point:
https://github.com/haliltalhaertan/llmzip

Use the `main` branch as the canonical accepted research surface. Do not treat auditor working branches as canonical evidence unless explicitly needed for historical comparison.

Current canonical commit at the time this prompt was issued:
`5ea42b31161094b651037e71edbf6ede21756ed9`

The two previously-missing LongMemEval adapters are now committed byte-exact under `adapters/` and must be audited directly.

---

# MANDATORY FIRST STEP — CHAIN OF CUSTODY

Before interpreting any result, verify every committed frozen artifact byte-for-byte against the corresponding manifest SHA256. Treat any mismatch as a packaging / chain-of-custody defect until the canonical Drive copy is independently checked.

Run:

```bash
python3 tools/verify_frozen_artifacts.py --list
```

Read:

- `CHAIN_OF_CUSTODY.md`
- `DATASETS_AND_LARGE_ARTIFACTS.md`
- `docs/v52/task4c2/V52_T4C2_PRE_RUN_SEAL.json`
- `docs/v52/task4c2/V52_T4C2_POST_RUN_MANIFEST.json`
- `docs/v52/task4c2/v52_t4c2_centering_geometry.py`

Verify the binding chain:

1. post-run manifest -> exact pre-run seal SHA256,
2. pre-run seal -> exact sealed compute-script SHA256,
3. adapter v1 -> pinned SHA256,
4. adapter v2 -> pinned SHA256.

Pinned adapter hashes:

`adapters/longmemeval_v52_adapter.py`
SHA256:
`0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`

`adapters/longmemeval_v52_adapter_v2.py`
SHA256:
`643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

If either adapter differs by even one byte, stop and report a BLOCKING CHAIN-OF-CUSTODY FAILURE.

Do not reformat, regenerate, normalize, or reconstruct any frozen artifact.

---

# AUDIT TARGET

Task 4C2 was a pre-registered blocking mechanism test intended to determine whether the surprising Task 4C1 SIGN96 lead was merely caused by centering.

The frozen methods are:

A. `FLOAT96_UNCENTERED_GLOBAL`
- exact frozen Task 4C1 continuous Mixed96 representation,
- global cosine/dot ranking,
- no centering.

B. `FLOAT96_CENTERED_GLOBAL`
- same exact 96D archive representation `Y96`,
- archive mean `mu96 = mean(Y96)`,
- document input `C96 = Y96 - mu96`,
- query input `qC96 = QY96 - mu96`,
- global cosine ranking,
- no refit, whitening, alternate metric, shortlist or reranker.

C. `SIMPLE_SIGN96_GLOBAL`
- threshold the exact same centered `C96/qC96` at zero,
- 96-bit code,
- global Hamming top-3,
- frozen independent tie priority.

D. `MIXED_SVD_ITQ96_GLOBAL`
- apply the audited ITQ rotation to the exact same centered `C96/qC96`,
- threshold at zero,
- 96-bit Hamming top-3,
- same frozen tie priority semantics.

No other method belongs in this audit.

---

# FROZEN PRIMARY RESULTS TO REPRODUCE

On the canonical 470-question LongMemEval non-abstention cohort:

- `FLOAT96_UNCENTERED_GLOBAL`
  - Fractional Evidence R@3 = about `44.010638%`

- `FLOAT96_CENTERED_GLOBAL`
  - Fractional Evidence R@3 = about `44.159574%`

- `SIMPLE_SIGN96_GLOBAL`
  - Fractional Evidence R@3 = about `54.197518%`

- `MIXED_SVD_ITQ96_GLOBAL`
  - Fractional Evidence R@3 = about `37.614113%`

Frozen descriptive gaps:

- centered FLOAT - uncentered FLOAT = about `+0.148936 pp`
- SIGN96 - centered FLOAT = about `+10.037943 pp`
- SIGN96 - ITQ96 = about `+16.583404 pp`
- ITQ96 - centered FLOAT = about `-6.545461 pp`

Pre-registered Task 4C2 verdict band:

Let `S = SIGN96 fractional R@3`, `Fc = centered FLOAT96 fractional R@3`, `G = S - Fc`.

- `|G| <= 1.0 pp` -> `[CENTERING EXPLAINS SIGN96 ADVANTAGE]`
- `1.0 < G < 5.0 pp` -> `[MIXED — CENTERING EXPLAINS PART, SIGN/HAMMING RETAINS RESIDUAL]`
- `G >= 5.0 pp` -> `[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`
- `G < -1.0 pp` -> `[FALSIFIED — CENTERED FLOAT DOMINATES SIGN]`

The compute-side reported verdict is:

`[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`

This is NOT frozen as an audited checkpoint yet. Your audit determines whether it survives.

---

# PRIMARY AUDIT QUESTIONS

## 1. Chain of custody

Try to falsify the run provenance.

Verify:

- canonical dataset identity and pinned SHA references,
- exact 470-question primary cohort,
- exact pre-run seal bytes,
- exact sealed compute script,
- post-run manifest consistency,
- no post-seal script mutation,
- exact adapter v1 and v2 bytes,
- no accidental execution of a different adapter or similarly named file.

Report every hash independently.

## 2. Adapter audit — previously NOT VERIFIABLE, now mandatory

Audit `adapters/longmemeval_v52_adapter.py` and `adapters/longmemeval_v52_adapter_v2.py` from source.

You must now independently determine whether the previously open conditions can be CLOSED.

Check at minimum:

- archive construction,
- canonical/patched memory IDs,
- session-position semantics,
- primary non-`_abs` cohort construction,
- residual-positive abstention exclusion,
- gold mapping,
- fit-input payload construction,
- whether query text is excluded from archive fitting,
- whether answer/gold/has_answer/question_type/answer_session_ids are excluded from representation fitting,
- whether fitting is archive-local/per-question only,
- whether any cross-question fit exists,
- tie-priority construction,
- deterministic ranking semantics,
- ITQ implementation.

For ITQ specifically inspect `fit_itq` mathematically and at source level:

- initialization is orthogonal,
- Procrustes update is correctly oriented,
- use of `R` versus `R.T` is internally consistent,
- document and query transforms use the same orientation,
- threshold semantics are exactly zero,
- no hidden label/query dependence enters the rotation fit,
- n_iter and seeds match the frozen protocol.

Do not merely trust the previous Task 4B adapter audit. Re-audit now because exact source bytes are available in the canonical repository.

## 3. Same-input ablation integrity

The central claim of Task 4C2 requires a clean same-input comparison.

Prove from source and outputs that:

- centered FLOAT96,
- SIGN96,
- ITQ96 before ITQ rotation

all receive the exact same centered 96D document/query inputs.

Verify:

`C96 = Y96 - mu96`

`qC96 = QY96 - mu96`

and that `mu96` is computed from archive documents only.

Check for:

- extra normalization in only one method,
- double centering,
- query-dependent centering,
- alternate representation matrices,
- hidden block weighting,
- different SVD fits,
- dtype/cast effects large enough to alter the intended ablation.

Use the committed same-input diagnostics where available. If the per-question `V52_T4C2_same_input_proof.csv` remains outside Git, retrieve it from the Drive pointer in `DATASETS_AND_LARGE_ARTIFACTS.md` if your environment allows; otherwise mark only that specific per-row raw proof as externally pending, but still inspect the source-level equality directly.

Any substantive input mismatch -> `[BUG — NOT A CLEAN GEOMETRY ABLATION]`.

## 4. Independent numerical reproduction

Recompute the aggregate metrics independently from the most granular available result tables.

Primary metric:

- Fractional Evidence Recall@3.

Secondary:

- ANY Evidence Recall@3,
- ALL Evidence Recall@3.

Confirm aggregation hierarchy and ensure repeated seed/nuisance rows do not overweight methods/questions.

The question, not the seed/nuisance trial, is the substantive benchmark unit.

Confirm Task 4C1 reproduction gate before interpreting Task 4C2.

Report differences from frozen numbers in percentage points to at least 6 decimals.

If raw trial tables are needed, use the exact Drive pointers and SHA256s in `DATASETS_AND_LARGE_ARTIFACTS.md`.

## 5. Fixed-benchmark inference discipline

LongMemEval primary questions are linked through reused sessions; all 470 primary questions previously formed one connected component.

Therefore:

- do NOT report population p-values,
- do NOT report population confidence intervals as if questions were independent draws,
- do NOT call question bootstrap inferential evidence,
- do NOT make equivalence/superiority population claims.

The principal object is the exact paired fixed-benchmark estimand.

Question resampling, if inspected at all, must be labeled composition sensitivity only.

## 6. SIGN vs centered FLOAT robustness

Verify question-level W/T/L for SIGN96 vs centered FLOAT96.

Reported approximate pattern:

- wins: 122
- ties: 304
- losses: 44

Recompute it.

Inspect whether the +10.04 pp aggregate lead is dominated by a tiny number of questions.

Report:

- W/T/L,
- largest per-question contributors,
- result after removing the largest contributors as a descriptive robustness check only,
- all frozen strata outcomes.

Frozen strata only:

- 6 question types,
- one-gold vs multi-gold,
- 4 archive-size quartiles,
- 3 session-reuse tertiles.

Do not invent new subgroup splits.

## 7. Binary geometry diagnostics

Audit the already-generated diagnostics; do not create a rescue experiment.

SIGN96:

- bit occupancy distribution,
- constant-bit count,
- mean absolute deviation from 0.5,
- unique-code fraction,
- duplicate fraction,
- largest collision bucket,
- exact query-code matches,
- minimum-distance tie size,
- top-3 boundary tie rate.

ITQ96:

- same diagnostics per seed,
- confirm approximately balanced occupancy and zero dead bits if supported by the files,
- confirm whether collision/tie rates are materially higher than SIGN96.

Check the reported qualitative facts rather than assuming them:

- SIGN96 unique-code fraction about 99.55%,
- ITQ96 unique-code fraction about 89.4%,
- SIGN96 top-3 boundary tie rate about 0.234,
- ITQ96 roughly 0.37-0.42 depending on seed.

These are DESCRIPTIVE. Do not infer causality.

## 8. Neighborhood reordering

Audit `V52_T4C2_rank_geometry.csv` and any supporting payloads.

The reported SIGN-vs-ITQ Hamming ranking Spearman correlation is only about `0.17`.

Verify:

- the exact correlation definition,
- what items/questions are being correlated,
- whether ties were handled consistently,
- whether averaging is question-weighted,
- per-seed spread.

Determine whether the statement

> "ITQ rotation massively reorders the retrieval neighborhood relative to native sign/Hamming geometry"

is supported descriptively.

Do NOT promote the stronger causal statement

> "ITQ destroys useful coordinates"

unless the delivered evidence actually establishes causality. That causal mechanism is reserved for a later preregistered task.

## 9. Centering falsification

Directly audit the key mechanism question:

`Fc - F0` should be only about `+0.148936 pp`.

If this reproduces, then the previous hypothesis that centering explains SIGN96's roughly +10 pp advantage is falsified on this benchmark.

State this carefully:

Allowed:
- "centering explains essentially none of the observed fixed-benchmark SIGN96 lead under this frozen control."

Not allowed:
- "centering can never explain binary retrieval advantages."

## 10. Leakage / contamination / accidental supervision

Perform an independent static source audit across:

- adapter v1,
- adapter v2,
- Task 4C2 sealed script.

Search for any path by which these can reach representation fitting, rotation fitting, threshold choice, ranking, or tie priority:

- `answer`,
- `has_answer`,
- `answer_session_ids`,
- `question_type`,
- gold turn IDs,
- evidence annotations,
- QA labels,
- question text during archive fit.

A label may exist as metadata for scoring; that is not leakage by itself. The audit question is whether it affects learned/fitted retrieval representations, method choice, or ranking before evaluation.

## 11. Prior Task 4C1 conditions

Revisit the Task 4C1 audit's two important unresolved mechanism conditions:

A. centering confound,
B. absent adapter / ITQ orientation verification.

Task 4C2 was designed to resolve A.
The newly committed byte-exact adapters are intended to resolve B.

For each, explicitly say one of:

- CLOSED,
- PARTIALLY CLOSED,
- STILL OPEN,
- NEW BUG FOUND.

---

# WHAT YOU MUST TRY TO BREAK

At minimum test these adversarial hypotheses:

1. The Git pre-run seal does not hash to the post-run manifest claim.
2. The sealed script differs from the seal's script SHA.
3. Either adapter differs from its pinned SHA.
4. v2 imports or executes a different v1 than the committed byte-exact file.
5. archive fitting sees the query.
6. archive fitting sees gold/answer labels.
7. ITQ fitting sees query/gold labels.
8. ITQ rotation orientation is transposed or inconsistent between docs and query.
9. SIGN and ITQ do not actually start from the same centered C96.
10. centered FLOAT receives a different normalization/representation than SIGN.
11. aggregation weights ITQ's five seeds differently from SIGN/FLOAT in a way that biases the comparison.
12. repeated nuisance rows are treated as independent evidence.
13. abstention questions leak into the 470 primary recall cohort.
14. residual-positive `_abs` questions are incorrectly included.
15. tie-breaking favors SIGN96.
16. SIGN's lead is a collision artifact caused by invalid duplicate memory IDs.
17. SIGN's lead is concentrated in one question type or tiny set of questions.
18. reported rank-correlation ~0.17 is an averaging/tie-handling artifact.
19. centering effect is miscomputed because FLOAT uncentered and centered use different base representations.
20. post-result rescue/tuning occurred despite preregistration.
21. Task 4C1 reproduction gate actually fails.
22. cost/touch language is presented as whole-system runtime/memory despite only being analytical retrieval-code touch.

Add additional break hypotheses if source inspection suggests them.

---

# DO NOT RUN NEW SCIENTIFIC EXPERIMENTS

This is an audit, not Task 4C3.

Do NOT run:

- uncentered SIGN96,
- new thresholds,
- sign64/sign48/sign32/sign24,
- random rotations as a new benchmark arm,
- whitening,
- alternate centering,
- Euclidean reranking,
- cosine variants,
- new SVD dimensions,
- block weighting,
- alternative encoders,
- LoCoMo replication,
- new shortlist/reranker methods.

Diagnostic recomputation from frozen outputs is allowed.
Synthetic unit tests solely to verify implementation algebra/orientation are allowed only if clearly labeled AUDIT DIAGNOSTIC and never used as retrieval evidence.

---

# PRIOR-ART / CLAIM DISCIPLINE

Do not allow the project to claim the following as novel:

- sign/zero-threshold binary retrieval,
- Hamming retrieval,
- ITQ,
- learned hashing,
- binary LLM embeddings,
- binary agent memory,
- binary retrieval on LoCoMo/LongMemEval,
- two-stage binary candidate + richer reranking,
- coordinate-preserving binary quantization generally,
- the broad fact that rotations can help or hurt depending on embedding geometry.

The current Task 4C2 object is an empirical mechanism observation under this exact frozen conversational-memory evidence-retrieval protocol, not a claim that sign hashing itself is novel.

---

# REQUIRED AUDIT OUTPUT

Produce a single audit report with these sections:

1. `VERDICT`
2. `AUDIT LEVEL`
3. `CHAIN OF CUSTODY`
4. `ADAPTER V1/V2 AUDIT`
5. `LEAKAGE AUDIT`
6. `ITQ ORIENTATION / IMPLEMENTATION AUDIT`
7. `SAME-INPUT PROOF`
8. `NUMERICAL REPRODUCTION`
9. `CENTERING FALSIFICATION`
10. `SIGN VS CENTERED FLOAT ROBUSTNESS`
11. `BIT BALANCE / COLLISION / TIE DIAGNOSTICS`
12. `NEIGHBORHOOD REORDERING`
13. `BREAK HYPOTHESES`
14. `BUGS`
15. `OVERCLAIMS`
16. `OPEN CONDITIONS`
17. `TASK 4C1 CONDITION RETIREMENT`
18. `FREEZE RECOMMENDATION`
19. `NEXT-STEP CONSTRAINTS`

Use exact labels where possible:

- `[VALID]`
- `[BUG]`
- `[FIXABLE]`
- `[FALSE]`
- `[OPEN]`
- `[GAP]`
- `[AUDITED]`
- `[FROZEN]`

Final audit verdict must be exactly one of:

- `PASS`
- `PASS WITH CONDITIONS`
- `FAIL`
- `BLOCKED — INSUFFICIENT EVIDENCE`

Then answer explicitly:

- `TASK 4C2 NUMERICAL CHECKPOINT MAY FREEZE: YES/NO`
- `CENTERING CONDITION FROM TASK 4C1: CLOSED/PARTIALLY CLOSED/STILL OPEN`
- `ADAPTER / ITQ ORIENTATION CONDITION FROM TASK 4C1: CLOSED/PARTIALLY CLOSED/STILL OPEN`
- `SIGN96 PHENOMENON IS REAL ON THE FIXED BENCHMARK: YES/NO/NOT ESTABLISHED`
- `MECHANISM IS CAUSALLY EXPLAINED: YES/NO`
- `TASK 4C3 MAY PROCEED: YES/NO`

Do not say Task 4C3 may proceed merely because the numbers are interesting. It may proceed only if the load-bearing Task 4C2 result and adapter/implementation chain survive this audit.

---

# CURRENT HEAD-RESEARCHER STATUS BEFORE THIS AUDIT

`[TASK 4C2 COMPUTE COMPLETE]`

`[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`

`[PENDING INDEPENDENT AUDIT — NOT FROZEN]`

The strongest currently allowed interpretation before audit is:

> Under the frozen LongMemEval evidence-retrieval protocol, SIGN96 substantially outperforms both centered FLOAT96 and archive-trained ITQ96. Centering alone changes the continuous baseline very little. ITQ rotation is associated with a major reordering of Hamming neighborhoods and a large retrieval loss relative to native sign geometry. The causal mechanism remains open.

Try to falsify that statement.
