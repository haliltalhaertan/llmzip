# Scope note for a future independent review of the runner

**Not a commission.** The independent runner review is **not** to be started yet. This note exists so
that when it is authorized, its scope is set by the Head Researcher rather than improvised by whoever
happens to run it.

## Subject

| item | value |
|---|---|
| branch | `impl/v52-membership-runner-v1-2026-09-08` |
| namespace | `drafts/v52/membership_runner_v1_2026_09_08/` |
| commit / hashes | see the ledger entry that records this delivery, and `GOVERNING_AND_LINEAGE.md` |

## In scope

1. **Identifier validation** (`RUNNER_SPEC.md` §3) — that each rejected shape is rejected by name;
   that a valid identifier is returned byte-identical; that no path strips, re-cases or coerces one.
2. **The source-identity contract** (§4) — all six checks; specifically whether a corruption exists
   that changes which questions resample together yet passes. The reviewer should write their own
   corruptions rather than replay the ones in the suite.
3. **N-2** — that a seed cannot be obtained without a frozen record, cannot be overwritten, and cannot
   be reused across a different `(benchmark, scheme)`.
4. **N-3** — that the LongMemEval tag is emitted and its cluster bootstrap unreachable; that a LoCoMo
   output never carries the tag.
5. **N-4** — that nothing is estimated from the query; whether the bitwise assertion can be bypassed by
   passing an equal-valued but separately computed object.
6. **Output schema, refusal to overwrite, and the real-data gate**, as they behave *through the
   integration* rather than in the core.
7. **Claim accuracy** — that `RUNNER_SPEC.md` and the docstrings state only what the code does. Quote
   any overstatement byte-verbatim.

## Explicitly OUT of scope

- The computation core. F-1 … F-12, NEW-1, NEW-2 and NEW-3 are **independently closed**. Do not
  re-audit them, and do not re-audit the research, the design, the preregistration, the statistics or
  the LoCoMo / LongMemEval evidence.
- The **choice** of environment lock and the **choice** of bootstrap seed values. Both are Head
  Researcher decisions, not implementation defects. Report them as open if you wish; do not resolve
  them.
- O-1, W-1, W-2 — recorded backlog, deliberately not addressed in this delivery.

## Things a reviewer should know before starting

- **Hash raw Git blobs**, never files as checked out. No `.gitattributes` exists; a Windows checkout
  hashes differently. Two earlier auditors raised false alarms from exactly this.
- `git diff main <this branch>` will show **document deletions**. That is an artefact of the branch
  point, not a change: this branch descends from a commit predating those documents. Check what the
  commit itself touches.
- The suites here ran on **Python 3.12.14**, not on a lock bound to this experiment — because no such
  lock exists. Their results are labelled `DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS` and must not be
  read as lock conformance.
- **No corpus** may be read, downloaded or approximated during the review. No real fitting, retrieval,
  ranking or real-data bootstrap. No sealing, no HMAC, no `run`, no `finalize`. Nothing under any
  `task4f1*` namespace, sealed payload, manifest or earlier audit namespace may be modified, and no
  recursive delete may be run anywhere in the checkout.
- The reviewer reports; the reviewer does not repair.
- Distinguish sharply between a real defect, an optional improvement, and a wording problem. An
  optional improvement presented as a blocker is itself a reporting error.
