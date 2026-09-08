# Runner + ingestion v3 — the three remaining items

Status: **`[FIXES PREPARED — NOT INDEPENDENTLY REVIEWED; NO AUTHORIZATION TO RUN ON REAL DATA]`**

Answers the three items left open by the delta-closure check at
`audit/v52-runner-ingest-v2-closure-2026-09-08` @ `823a361d1a72735783259e5a6fa1914c25870abf`
(report sha256 `43969c4e1614a98b707dbc730a31b10bf83bac19ebaf87e069c25e141371b0df`,
verdict `CLOSURE PASS WITH FINDINGS`).

**Nothing else was touched.** No M-1/M-2/M-3. The closed core, both v1 modules, the v2 package, every
audit namespace and both accepted manifests are byte-unchanged. The accepted design, cohort, seeds and
environment lock are unchanged.

---

## The table

| item | fix | independent test | status |
|---|---|---|---|
| **D-5** nine residual paths still interpolated raw values (F12–F20) | the **error interface was replaced**, not patched nine times. `errors.py` builds every message from a **fixed code** out of a closed enumeration, that code's **fixed sentence**, and fields restricted to numbers, booleans, `None` and **enum members already validated against a closed set**. A string cannot enter a message — `UnsafeErrorField` fires first. `require_benchmark` / `require_scheme` canonicalise **before** any value could be formatted, so an unrecognised name is never echoed. Refusals are raised `from None`, so no library context travels out. **F12's ordering defect is fixed at the root:** the `_accepted_manifest_sha256` stamp check now runs **first**, before anything from the mapping is read, compared or formatted | each of F12–F20 driven with sub-120-character canaries; the surface captured is stdout **+** stderr **+** the message **+** the whole `__cause__`/`__context__` chain. v2 leaks on every one; v3 on none. The four paths that live in `authoritative/` are controlled **in a subprocess** against v2's own package, because in-process v3's package shadows it and the control would prove nothing | **CLOSED** |
| **D-1** the waiver was an unauthorized exception and was not recorded | `allow_partial_evidence` and `partial_evidence_citation` are **removed**. A non-empty string was never an authorization, nothing checked that it named a real decision, and it reached no artefact. An unexpected partial resolution **stops** with `E-COH-002` and safe numeric diagnostics. **No gold repaired, no question excluded, no cohort changed.** `PARTIAL_EVIDENCE_POLICY` records that no accepted exception exists, and that if the bound semantics ever require one it is **brought for decision, not produced in code** | v2 proceeds on any non-empty string and the citation reaches no manifest; v3 refuses, with `affected_questions=1, declared_ids=2, unresolved_ids=1`. A **fully** unresolvable question is distinguished — it is not a partial loss, it proceeds and is counted. A fully resolved source proceeds with zero unresolved | **CLOSED** |
| **LongMemEval** `evidence_ids_declared` was defined as the resolved count | the accounting is **one field whose shape is named by its gold model**, not shared keys. LoCoMo keeps `declared/resolved/unresolved_reference_ids`. LongMemEval reports `declared_reference_ids: null` with status `NOT_APPLICABLE`, plus `gold_units_resolved` under its own name and `completeness_guarded_by` naming the checks that stand in for a declared-vs-resolved comparison. **And the real silent loss is closed:** a non-boolean `has_answer` is now **refused** (`E-COH-009`) instead of coerced to `False` as the bound adapter does | v2 silently drops a `has_answer: 1` and reports `declared == resolved == 0`, calling the accounting complete; v3 refuses it. The two shapes are asserted to be genuinely different, and every guard token is asserted to have a real check behind it | **CLOSED** |

**60 checks, ALL PASS**, of which **12 are negative controls** on v2 — four of them in a subprocess.
Evidence: `evidence/v3_delta_tests.txt`. The v2 suite (82) and the core suite (99) still pass:
`evidence/v2_regression.txt`, `evidence/core_regression.txt`.

## Why the gold model matters, and where it came from

The two benchmarks were never the same. From the **bound** adapter,
`adapters/longmemeval_v52_adapter_v2.py` lines 37–38 and 45: a turn's `has_answer` marks gold, a
non-boolean value is recorded as `INVALID_HAS_ANSWER_TYPE`, and it is then coerced to `False`.

So LongMemEval has **no declared-reference model**: gold is a per-turn marker, not a pointer that can
dangle. There is no declared count to report, and v2 inventing one by copying the resolved count was
worse than reporting nothing — the shared field names promised an accounting that did not exist. The
analogue of an unresolvable reference here is a marker in a type the adapter ignores, and that is what
v3 refuses.

## The claim, third time

v1 said content is *"never printed, logged, put in an exception message, or written to disk"* — false.
v2 said *"no value is interpolated into any message"* — false. **v3 does not make a third absolute
claim.** It states a mechanism and a tested surface: every exception these modules raise, stdout,
stderr, the exception chain, and every file they write. Against that surface the tests find nothing.

**Not claimed:** that no content can escape under any condition. A caller that prints what it is handed
defeats all of it, and no module can prevent that.

## Optional residuals, not added

N-3 (`transform_stamp` is public and forgeable), N-4 (one unguarded `KeyError`) and N-5 (the stamp is a
public constant) were **not** folded in. Reported as required: none of them causes wrong data to be
**accepted** on a real call path. Each requires a caller to construct and pass a value it did not
obtain from the function that produces it — a caller doing that is not a wrong-data path, it is a
caller overriding its own check. The one arguable case, `mapping["benchmark"]` raising `KeyError`, is
now unreachable from `compute_results`: the stamp check refuses a hand-built mapping before that line.

## Out of scope

M-1, M-2, M-3 remain unwritten and unauthorized. No pilot. No real corpus access, fitting, retrieval,
ranking or real-data bootstrap. No sealing, no HMAC. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
