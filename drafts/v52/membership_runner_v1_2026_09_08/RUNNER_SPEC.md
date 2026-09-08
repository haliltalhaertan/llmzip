# Corpus-bound runner v1 — specification

Status: **`[IMPLEMENTATION PREPARATION — NOT AUTHORIZED TO RUN ON REAL DATA; NOT INDEPENDENTLY REVIEWED]`**

Prepared by the Continuity Lead, who therefore **may not** call it reviewed. No corpus is read,
downloaded or approximated anywhere in this namespace. The audited v3 core is imported and **left
byte-unchanged**; see `GOVERNING_AND_LINEAGE.md`.

---

## 1. What this runner is

The computation core was closed against the design text. It assumes its inputs are already
trustworthy. This runner is the layer between a data source and that core, and it exists to make the
assumption true before the core sees anything:

| stage | function | what it guarantees |
|---|---|---|
| identity | `validate_identifier`, `validate_identifier_columns` | no missing-value indicator, no unsupported type, no silent transformation |
| source | `load_expected_mapping`, `verify_source_identity` | the cohort **is** the bound source, on six checks |
| N-2 | `freeze_bootstrap_seed`, `read_bootstrap_seed` | the bootstrap seed is fixed to a record **before** any result exists |
| N-4 | `fit_archive_transform`, `apply_archive_transform`, `assert_query_transform_is_inherited` | centering and `D` are learned from the archive only and applied unchanged to the query |
| N-3 | `compute_results` | the LongMemEval inheritance tag is emitted; its cluster bootstrap is refused |
| output | `write_results` | closed schema, refusal to overwrite |
| gate | `run_on_real_corpus` | refuses through the core's own authorization check, with nothing behind it |

## 2. Input schema

**Per-question record** — a mapping with exactly these fields:

| field | type | constraint |
|---|---|---|
| `question_id` | `str` | passes §3 |
| `rotation_seed` | `int` | one of `60001 … 60010` |
| `arm` | `str` | one of the six arms `NATIVE, SCALED_NATIVE, B32_FRESH, SCALED_B32, RANDOM32_FRESH, SCALED_RANDOM32` |
| `fractional_R3` | real, not `bool` | finite, in `[0, 1]` |

Every `(question, seed, arm)` triple must be present **exactly once** — the core enforces this and
the integration tests exercise it through the runner.

**Identifier columns** — `question_ids` and `cluster_ids`, aligned positionally, same length,
non-empty.

**Expected-mapping manifest** — a JSON object with exactly these fields:
`source_id`, `source_sha256`, `benchmark`, `expected_cluster_ids`,
`expected_question_to_cluster`, `n_questions`. It is loaded only against a caller-supplied sha256.

## 3. Identifier contract — what is rejected, by name

Identifiers are **strings only**. This is deliberately narrower than the core.

| rejected | why |
|---|---|
| any non-`str` type — `int`, `np.int64`, `float`, `bool`, `bytes`, `None`, tuple | **NEW-5.** The core keys integer labels by `int()`, so two distinct objects equal under `int()` merge into one cluster. Accepting no integer at all makes that unreachable rather than merely tested. A source with integer ids must render them as strings **in the adapter**, where the choice is visible |
| a designated missing-value indicator: `""`, `"nan"`, `"none"`, `"null"`, `"na"`, `"n/a"`, `"nil"`, `"-"`, `"--"`, `"?"`, compared on a case-folded stripped **copy** | **NEW-4.** A label column read from CSV or JSON commonly renders a missing value as exactly one of these, and the core accepts them as ordinary distinct labels |
| a whitespace-only string | same class |
| a string with leading or trailing whitespace | stripping it would silently **merge** `" c1"` with `"c1"`. The instruction is that valid identifiers are never silently altered or merged, so it is rejected instead |
| a duplicate question id | the cohort must be a set |

A valid identifier is returned **byte-identical**: never stripped, re-cased, coerced or normalised.
An id that merely *contains* a rejected token as a substring (`"nancy-01"`) is valid and untouched.

## 4. Source-identity contract — and why a count check is not accepted

`verify_source_identity` checks **six** things against the bound manifest:

1. identifier type and missing-value validation (§3);
2. duplicate question ids;
3. question ids missing against the bound source;
4. question ids not in the bound source;
5. **the per-question conversation mapping** — every question routed to its expected conversation;
6. **conversation id set equality** — not the count, the set.

`n_clusters == 10` alone is rejected as evidence. Three corruptions demonstrated in the test suite
leave the total unchanged:

- two questions **swapped** between conversations — ten conversations, wrong grouping;
- a whole conversation **relabelled** — ten conversations, different set;
- one conversation's ids all rendered as `""` — still ten distinct labels.

So the honest statement is **"the grouping can be corrupted silently"**, not "a visible eleventh
cluster will appear". Several missing ids collapse into one pseudo-conversation, a missing id equal
to an existing one is absorbed, and an `int()`-merged pair *reduces* the count. Each of these changes
which questions resample together, which is the only thing the cluster bootstrap depends on.

### The expected mapping is MISSING and is not invented here

**No document bound to this experiment supplies it.** The four normative documents
(`ACCEPTANCE_BINDING`, `R2`, `R1`, `PREREG_DRAFT`) contain no conversation-id inventory and no
question→conversation map; the acceptance record's §4 says only "draw `n_clusters` conversations".
This runner therefore treats it as a **required external input**, hash-bound at load time. It was not
fabricated and it was **not produced by reading a raw corpus in this task**.

A candidate artifact exists in the repository — `audit_v52_t4f0_codex_2026_08_31/conversation_inventory.csv` —
but it belongs to a different task's audit namespace and **nothing binds it to this experiment**. Its
contents were **not read** here. Binding it, or producing a mapping manifest another way, is a Head
Researcher decision and is listed in §7 as a remaining requirement.

Until then the contract is demonstrated against the **known** mapping of the synthetic adapter, where
ground truth exists by construction.

## 5. The three carried obligations

**N-2 — the bootstrap seed.** `freeze_bootstrap_seed` writes `{seed, benchmark, scheme, replicates,
frozen_before_any_result}` to a **new** file through the core's refusal-to-overwrite path, and returns
the record. `read_bootstrap_seed` is the only way a run obtains a seed: it refuses when no record
exists, and refuses a record written for a different `(benchmark, scheme)`. A seed therefore cannot be
chosen after seeing a result, and a second seed cannot be tried into the same record. The seed's own
sha256 travels into the output.

**N-3 — LongMemEval.** `LONGMEMEVAL_INHERITANCE_TAG` is emitted in every LongMemEval output and states
the structure (single connected component over all 470 questions), the provenance (**inherited from
Task 3A.1, provenance-verified, not recomputed here**), the consequence (a conversation-cluster
bootstrap is **ill-posed**, not merely wide) and the authority (R2 line 141). Requesting
`scheme="cluster"` for LongMemEval raises a named `DesignViolation`. LoCoMo outputs carry `None`, so
the tag can never be read as applying to both.

**N-4 — the query transform.** `fit_archive_transform` sees the archive only and returns
`(mu, D, diagnostics)`. `assert_query_transform_is_inherited` compares the objects used on the query
against those two **bitwise**. Bitwise is correct *here* and tolerance is correct in the core: this
asserts that the same numbers were reused, not that two summation orders agree; a tolerance would
admit a query mean that merely *resembles* the archive mean, which is the failure N-4 names. The
synthetic query is drawn from a deliberately different distribution, so the test would fail if the
transform were refitted.

## 6. What this suite claims, and what it does not

**No claim is made that any wrong ingestion is necessarily caught.** What is demonstrated, and only
this: the declared input schema; the named rejection of each identifier shape in §3; the six-axis
identity contract including a corruption that leaves the cluster count unchanged; N-2, N-3, N-4; and
that the output schema, the refusal to overwrite and the real-data gate all survive integration.

Evidence: `evidence/runner_synthetic_tests.txt` (**85 checks, ALL PASS**) and
`evidence/core_regression_v3.txt` (**99 checks, ALL PASS**), both labelled
**DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS** — see `ENVIRONMENT_LOCK_PROPOSAL.md`. They are **not**
evidence of lock conformance, not a seal, and not authorization to run.

## 7. Remaining requirements before this can touch real data

1. **A bound expected-mapping manifest** per benchmark — §4. Missing. Head Researcher decision.
2. **A binding environment lock for this experiment** — `ENVIRONMENT_LOCK_PROPOSAL.md`. Missing; the
   Task 4F1 V7 lock is **not** automatically applicable and was not applied.
3. **The registered bootstrap seed values** — the mechanism exists and is tested; the *values* are a
   preregistration decision and are not chosen here.
4. **A real ingestion path** — `run_on_real_corpus` is a refusing stub with nothing behind it. Writing
   one is not authorized at this stage.
5. **An independent review of this runner** — not commissioned; see `SCOPE_NOTE_FOR_INDEPENDENT_REVIEW.md`.
6. **A rerun of both suites under the bound lock**, once one exists.

Not authorized and not done here: reading or downloading any corpus; real fitting, retrieval or
ranking; any bootstrap on real data; a pilot; a model download; sealing; HMAC material; `run` or
`finalize`. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
