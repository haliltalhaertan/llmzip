# Runner + ingestion v4 — evidence normalisation and the last two error paths

Status: **`[FIXES PREPARED — NOT INDEPENDENTLY REVIEWED; NO AUTHORIZATION TO RUN ON REAL DATA]`**

Answers the three items left open by the v3 closure check at
`audit/v52-runner-ingest-v3-closure-2026-09-08` @ `dc4c47dafc6f4dfe40e8bfacebca910f6b8f75da`
(report sha256 `079dc9726529595d4a17472afa7837f2b472b7643f89bf25003f9cef46404f7b`).

**Nothing else was touched.** No M-1/M-2/M-3. **No scan of the real corpus** was made to find out
whether the malformed evidence shapes occur there — the fix does not need it and reading it is not
authorized. The closed core, all v1/v2/v3 packages, every audit namespace and both accepted manifests
are byte-unchanged.

---

## The table

| item | fix | independent test | status |
|---|---|---|---|
| **evidence normalisation** — `_normalise_evidence` silently discarded what it could not turn into an id | the bound contract is transcribed with its source and its three cases separated. **Valid empty:** `None`, `[]`, `()` — nothing was dropped. **Valid non-empty:** a string (including the producer's whole-string fallback, kept because it *is* the contract), or a list/tuple of such strings or dicts carrying `dia_id`/`id`. **Malformed item inside a valid list → `E-COH-011`.** **Unsupported structure → `E-COH-012`.** Nothing is guessed, coerced to a string or dropped. No question excluded, no gold repaired, no cohort changed | seven malformed shapes — dict without either key, empty id, null id, non-string item, and malformed **first / middle / last** — each shown silently discarded by v3 and refused by v4, with no content in the refusal. Three unsupported structures likewise | **CLOSED** |
| **three counts kept distinct** | `raw_evidence_items`, `declared_reference_ids`, `resolved_reference_ids` and `unresolved_reference_ids` are four published fields. v3 published two and let a third be inferred, which is how a dropped raw item looked like an item that never existed. De-duplication of **valid** repeats is unchanged — `dict.fromkeys`, as before | `["D1:0","D1:0"]` gives raw 2, declared 1, resolved 1 — the difference is now visible rather than invisible | **CLOSED** |
| **"one valid + one malformed"** could be reported as successful and lossless | it now stops | v3 reports `declared = resolved = 1, unresolved = 0, empty_gold = 0, partial_loss = 0` on a source where one of two entries vanished — every published number saying nothing was lost. v4 refuses and writes nothing | **CLOSED** |
| **`validate_identifier`'s `kind`** was a caller string, echoed | `kind` is a member of `IdentifierKind`, a closed enumeration. An unrecognised kind is refused by code without being echoed | v3 echoes a 70-character canary; v4 does not, and still refuses genuine identifier faults by code with `kind=question_id, position=3` | **CLOSED** |
| **`int(mapping["n_questions"])`** raised an uncaught `ValueError` carrying the value out | the manifest field types the source contract requires are validated explicitly — no silent conversion, and no new value accepted by coercion | v3 raises `ValueError` with the canary in it; v4 refuses with `E-SRC-012`, no content and no `ValueError`. Also checked for `expected_question_to_cluster`, `expected_cluster_ids`, a float `n_questions` and a bool `n_questions` | **CLOSED** |
| **claims and label** | the stale `v2` headers are corrected to `v4`. No fourth universal sentence is written | the three earlier sentences survive **only as quoted, falsified text** inside an inventory of what was checked — asserted nowhere. What is untested is named | **CLOSED** |

**70 checks, ALL PASS**, of which **13 are negative controls** on v3. Evidence:
`evidence/v4_delta_tests.txt`. The v3 suite (60) and the core suite (99) still pass.

## The claim, fourth time — an inventory instead

v1: *"never printed, logged, put in an exception message, or written to disk."* v2: *"no value is
interpolated into any message in this module."* v3: *"every message here is built by `errors.message`"*
and *"A string cannot enter a message without first raising `UnsafeErrorField`."* Three universal
sentences, three independent falsifications, all mine.

v4 writes no fourth. It states **which interfaces were checked** — the message builders used by each
path, where `safe_report` is used to describe rather than name, and the specific error paths the tests
exercise with the surface captured for each — and then names what is **untested and therefore
unclaimed**: what a caller does with what it is handed, and any message written in future without this
interface.

## What was deliberately not done

No scan of the real corpus for the malformed shapes. The fix is unconditional — it refuses them
wherever they appear — so whether they occur is not needed to make it correct, and it would be a corpus
read.

M-1, M-2, M-3 remain unwritten and unauthorized. No pilot. No real corpus access, fitting, retrieval,
ranking or real-data bootstrap. No sealing, no HMAC. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
