# Package ready for independent runner review — the reviewer is NOT commissioned

Status: **`[INGESTION CODE PREPARED — NO AUTHORIZATION TO EXECUTE ON REAL DATA; NOT INDEPENDENTLY REVIEWED]`**

Prepared by the Continuity Lead, who therefore may not call it reviewed. **Do not start the review
until the Head Researcher says so.** This page exists so that when they do, the reviewer inherits a
package rather than a search.

---

## 1. What is in the package, and where

| layer | branch / namespace | status |
|---|---|---|
| computation core | `impl/…-v3-2026-09-07` @ `dcb568d0` — `drafts/v52/membership_impl_v3_2026_09_07/` | **CLOSED** at `aa0ee8a9` (CLOSURE PASS). Byte-unchanged, `bc2282d3…` |
| runner + manifests + config identity | `impl/…-runner-v1-2026-09-08` @ `e61c414e` — `drafts/v52/membership_runner_v1_2026_09_08/` | prepared, **not reviewed** |
| **corpus ingestion (new)** | this branch — `drafts/v52/membership_ingest_v1_2026_09_08/` | prepared, **not reviewed**, **never executed on a real corpus** |

Every earlier namespace — v1, v2, v3 candidates and all audit namespaces — is untouched.

## 2. What the ingestion does, and where it stops

`corpus_ingest.py` goes from bytes on disk to the structures the pipeline needs and stops:

1. **source byte identity first** — streamed sha256 and byte size against bound values, **before any
   parse**, so a wrong, truncated or altered file is refused before its content is read;
2. **bound manifest** loaded through the runner's hash-checked loader;
3. **every bound question id resolved individually**, refusing missing, extra, misrouted, duplicated
   and position-mismatched ids rather than repairing them;
4. **archive units and query texts assembled in memory** with their gold row indices.

It does **not** fit a representation, retrieve, rank, evaluate, bootstrap or seal. It imports none of
that machinery — the test suite asserts the absence of `TfidfVectorizer`, `TruncatedSVD`, `sklearn`,
`haar_q` and `hamming_dist` from the module source.

### The cohort is bound, never recomputed

The ingestion takes the bound 1535 (LoCoMo) and 470 (LongMemEval) ids and resolves each one. It never
derives a cohort. The producer's three-step selection rule is documented in
`LOCOMO_SELECTION_RULE_NOTE_2026-09-08.md` and deliberately **not** reimplemented — a second selection
rule could drift from the bound cohort, most plausibly by omitting the audit-corrections step, which is
exactly the step an earlier reconstruction did miss.

### Content never leaves memory

Text is held in memory and handed to the caller. It is never printed, logged, placed in an exception
message, or written. `write_ingest_manifest` is the only writer: closed schema, then a conservative
content policy that refuses any string over 120 characters and any unexpected type, then the core's
refuse-to-overwrite path.

### The gate stays shut

`core.require_real_data_authorization()` is the first statement of every corpus-touching entry point
and refuses by default. Importing the module opens nothing: no module-level file access, no path
resolved at import time, and no corpus path stored anywhere in the module — so **test discovery cannot
trigger corpus access**. The test suite asserts each of these.

## 3. Evidence in this package

All produced in the **accepted environment** (Python 3.13.15 / numpy 2.3.5 / scipy 1.17.0 /
scikit-learn 1.8.0 / pandas 2.2.3, four thread variables at 1, `PYTHONHASHSEED=0`), and all labelled
**DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS** — not a seal, not run authorization.

| file | what it shows |
|---|---|
| `evidence/ingest_synthetic_tests.txt` | **55 checks, ALL PASS** — the ingestion end to end on fake files only |
| `evidence/runner_regression.txt` | **85 checks, ALL PASS** — the runner suite still passes |
| `evidence/core_regression.txt` | **99 checks, ALL PASS** — the closed core suite still passes |
| `evidence/selection_rule_result.json` | the committed producer rule reproduces the bound 1535 exactly |
| `evidence/thread_policy_observation.json` | requested vs observed vs measured thread policy, kept apart |

## 4. Scope for the review, when it is authorized

**In scope:** everything in §2 — identity-before-parse ordering; that no cohort can be derived; the
individual resolution of every bound id and each refusal; the content policy and whether any path can
leak text into a file, a log or an exception message; the gate, including whether any import or test
path reaches a corpus; the ingest manifest's schema and refusal to overwrite; and claim accuracy in
this namespace's documents. The reviewer should write their own corruptions rather than replay the ones
in the suite.

**Out of scope:** the computation core (F-1…F-12, NEW-1/2/3 are independently closed — do not
re-audit); the research, design, preregistration and statistics; the *choice* of environment lock,
seeds and manifests, which are Head Researcher decisions now accepted; and O-1, W-1, W-2, recorded
backlog.

**Ground rules:** hash **raw Git blobs**, never a checkout — there is no `.gitattributes` and a Windows
checkout hashes differently; `git diff main <branch>` will show document deletions that are an artefact
of the branch point, not a change; **no corpus may be opened** during the review, and no fitting,
retrieval, ranking or bootstrap run; nothing under any `task4f1*` namespace, sealed payload or earlier
audit namespace may be modified; no recursive delete anywhere in the checkout; the reviewer reports and
does not repair; and an optional improvement presented as a blocker is itself a reporting error.

## 5. What is still required before a real run — none of it granted here

1. **Authorization to execute the ingestion on a real corpus.** It has never been run on one.
2. **The independent runner review**, not commissioned.
3. **The next stage** — representation fitting, retrieval, ranking — which is not written and not
   authorized.
4. **A pre-run seal**, not made.

No sealing, no HMAC, no `run`, no `finalize`. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
