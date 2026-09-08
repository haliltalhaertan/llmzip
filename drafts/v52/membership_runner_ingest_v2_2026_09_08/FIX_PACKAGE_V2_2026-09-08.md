# Runner + ingestion v2 — findings-limited fix package

Status: **`[FIXES PREPARED — NOT INDEPENDENTLY REVIEWED; NO AUTHORIZATION TO RUN ON REAL DATA]`**

Answers findings **D-1 … D-8** and the directly connected source-trust items of the independent review
at `audit/v52-runner-ingest-review-2026-09-08` @ `8c8ba7aefe2622efb4fbf65230f04dbfbec25449`
(report sha256 `456645a61c7e44148ee454287e7db0e66adfa128539b17679ce1c94897764676`, verdict **FAIL**).

**Nothing else was touched.** No M-1/M-2/M-3 preparation. The closed core is byte-unchanged and its
findings are not reopened. The accepted scientific design, cohort, manifests, seeds and environment
lock are unchanged. v1 of both modules stays byte-unchanged in its own namespace, and so does every
audit namespace.

---

## The table

| finding | fix | independent test | status |
|---|---|---|---|
| **D-1** partially unresolvable evidence silently truncated the gold rows | evidence ids are counted three ways — **declared / resolved / unresolved** — per question and in total. An *unexpected* partial resolution now **stops** the ingestion with a named `DesignViolation`. Proceeding requires `allow_partial_evidence=True` **and** a `partial_evidence_citation`, which travels into the result. All three counts plus `questions_with_partial_evidence_loss` are published **unconditionally** in the written manifest. Gold/adapter semantics unchanged; nothing excluded, repaired or re-derived | v1 negative control accepts the loss and reports `questions_with_empty_gold=0` with no evidence accounting at all; v2 refuses it, refuses an uncited waiver, and with a cited waiver reports `declared=2, resolved=1, unresolved=1` — and a clean source reports zero | **CLOSED** |
| **D-2** the replicate count was not checked against the frozen seed record | `compute_results` refuses when `replicates` contradicts the record, and `freeze_bootstrap_seed` refuses a count that is not the accepted one | v1 negative control runs 7 replicates and persists a record saying 10000; v2 refuses that call and runs on 10000 | **CLOSED** |
| **D-3** the accepted seed *values* governed nothing | seeds and replicate counts resolve from `authoritative/accepted_configuration.py`. `freeze_bootstrap_seed` refuses a non-accepted seed; `read_bootstrap_seed` refuses a record that drifts from it | v1 accepts seed 999 and reads it back; v2 refuses 999, refuses the transposed `52001170`, accepts `52001107`, and catches a hand-edited record | **CLOSED** |
| **source trust** the expected manifest hash was an arbitrary caller argument | the argument is **gone**. `load_accepted_mapping(benchmark, raw=…|path=…)` takes the expected hash from the authoritative module. A mapping that did not come through it is refused downstream by a stamp check | v1 loads any file against any caller hash; v2 refuses non-accepted bytes, refuses both-arguments, and refuses the superseded v1 manifest **as superseded** with the reason | **CLOSED** |
| **D-4** the accepted manifests could not be loaded from a default Windows checkout | manifests resolve from **Git's original bytes** (`git cat-file blob`), or from a file produced by the documented **byte-preserving materialisation** (`open(..., "wb")`, re-read and re-hashed). The hash check is **not** relaxed and line endings are **never** normalised; a CRLF-translated file is refused **with that diagnosis** | v1 refuses its own accepted manifest from a CRLF checkout; v2 also refuses it — but says *why*, and states that it refuses rather than normalising. The blob path and the materialised file both load. No `.gitattributes`, no global Git change | **CLOSED** |
| **D-5** exception messages carried source-derived text verbatim, unbounded, un-policed | `_describe` is **deleted**. Every message in both modules is built from counts, positions, field names and `safe_report` — type, shape, 12-hex digest. The content policy no longer echoes dict keys | seven v1 paths leak sub-120-character canaries through stdout/stderr/exception text; the same inputs leak **none** in v2. The happy path and the written manifest carry none, while the in-memory structures still hold the text — which is what ingestion is for | **CLOSED** |
| **D-6** the N-4 inheritance assertion was bypassable and a self-report | `apply_archive_transform` now returns `(transformed, stamp)` and **stamps the parameter bytes it actually consumed**. The assertion checks that stamp; the caller has nothing left to report | v1 passes on `mu.copy()`/`D.copy()` and passes when the archive `mu` is reported after a query-derived transform; v2 catches a query-derived transform and a 1-ULP `D` perturbation, and refuses a non-stamp argument | **CLOSED** |
| **D-7** ragged LongMemEval haystacks truncated silently | the three parallel arrays are length-checked **before** `zip`, and an empty haystack is refused | v1 truncates to **zero** units silently; v2 refuses with the three lengths | **CLOSED** |
| **D-8** a raw `KeyError` instead of a named refusal | required fields are checked and refused by name, with no content in the message | v1 raises `KeyError: 'question_id'`; v2 raises a named `DesignViolation` | **CLOSED** |

**82 checks, ALL PASS**, of which **19 are negative controls** reproducing the old behaviour on the v1
modules. Evidence: `evidence/v2_delta_tests.txt`. The three earlier suites still pass unchanged —
`evidence/core_regression.txt` (99), `evidence/runner_v1_regression.txt` (85),
`evidence/ingest_v1_regression.txt` (55).

## Claim corrections — the wording the review falsified

- The v1 sentence *"It is never printed, logged, put in an exception message, or written to disk"* is
  **removed**. What replaces it describes behaviour and names its limit: no value is interpolated into
  any message **in these modules**, and a caller that prints what it is handed defeats that — no module
  can prevent it.
- The v1 claim that **extra** ids are *refused* is corrected. They are **not** refused, and refusing
  them would be the bug: the bound cohort is a strict subset of the source by design. They are counted
  and reported.
- *"IDENTICAL objects, bitwise"* is gone. The check is on the **bytes of the parameters actually
  consumed**, recorded by the code that consumed them.
- *"Never returns free text"* is gone from `_normalise_evidence`'s docstring context; the function's
  behaviour is unchanged.
- **The 120-character limit is nowhere presented as a guarantee.** It survives as one blunt structural
  check on data about to be written, explicitly labelled as not a guarantee — every leak the review
  demonstrated used a fragment under it.

## Governance question (a) — answered in code, not only in prose

The review found the PROPOSED-vs-accepted relation coherent but ambiguous: five `binding/` files carry
the identical `"PROPOSED - NOT BOUND"` string, the v1 sidecar never mentions supersession, and no file
in the runner namespace pointed at the acceptance record.

This package adds **one authoritative directory**, `authoritative/`, and everything downstream resolves
from it. `accepted_configuration.py` names the acceptance record by commit, path and hash, states in
`PROPOSED_VS_ACCEPTED` how to read the word "PROPOSED" in the older files, lists the **accepted**
manifests, and lists the **superseded** one separately with the reason it was superseded — so a refusal
says "this is superseded, and here is what replaced it", not merely "hash mismatch".

The historical files are **not modified**. Their hashes keep resolving in L-072 and L-073.

## Governance question (b) — the two gaps

The review found v2 precedence really enforced in the ingestion, with two gaps. The runner's loader
gap is **closed**: there is no caller-supplied hash any more. The second — `binding/validate_proposed_manifests.py`
still loading v1 — is a **v1-namespace script**, and v1 is deliberately byte-unchanged; the active
validator for this package is this namespace's own suite, which checks the accepted sources.

## Out of scope, deliberately

M-1, M-2 and M-3 remain unwritten and unauthorized. No pilot. No real corpus access, fitting,
retrieval, ranking or real-data bootstrap. No sealing, no HMAC. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
