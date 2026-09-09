# LLMZIP — research takeover checkpoint, 2026-09-09

## Disposition

**Research takeover review completed; canonical continuation remains UNVERIFIED and execution remains BLOCKED.** This is an additive Head Researcher review and a narrow synthetic diagnostic, not a cold-start independent audit, package acceptance, scientific reseal, or run authorization.

The user's request is to take over `haliltalhaertan/llmzip`. The relevant work is compact, evidence-traceable long-term memory retrieval, not a claim that all prompt tokens or source archives can already be losslessly eliminated. The active continuation point is the membership execution-preparation review recorded on 8 September, not the older V3/V7 audit instructions still appearing in the entry documents.

No canonical state, ledger, accepted scientific document, candidate, closed core, ingestion implementation, gold mapping, seed panel, or prior audit was changed. No real corpus was fetched, read, hashed, fitted, ranked, scored, bootstrapped, or finalized. No production authorization, HMAC key, or experimental result was created.

## Source anchors inspected through the authenticated GitHub connector

| Object | Exact reference | Scope used here |
|---|---|---|
| Canonical `main` | `a8e6d5d31dd01f2ea953012c7899420de7356232` | README, entry point, current state, continuity protocol/verifier source, latest commit record L-081 |
| GitHub default branch | `claude/itq-frontier-audit-wfrz6a` at `76556234bdf6b49531382eccb9500a37e097cdeb` | Metadata only; not treated as the current research branch |
| Membership preparation v1 | `ed4e22c520b7dc0ae2f43f915e0c621070c72a87` | README, commit diff, complete `pipeline.py`, relevant core source ranges |
| Preparation audit | `5126766cac9201bbede178ccb558efa428f9488c` | `audit_v52_execution_prep_v1_review_2026_09_08/EXECUTION_PREP_V1_REVIEW.md` |
| Preparation parent | `07ec929243068914676a0f30efd10c9f294c7e71` | Identified from candidate and audit; prior repair not independently rerun |
| Pipeline Git blob | `6b41a4242ec7de5018537f4be5f4835d16ed03fd` | Source of the isolated canary expressions |
| Core Git blob | `b0f8183ec53d590abd765afe5a301ca906fb6a35` | Source of `check_identity` and `hamming_dist` |

The candidate and audit occupy separate branches; this review does not claim that either is merged into `main`. L-081 records **PASS WITH FINDINGS**, limited to prepared M-1/M-2/M-3 functions. It leaves seven findings, nine named test gaps, and all five integration obligations open. That recorded verdict is not a new verdict from this session.

The current state still says Task 4F1 scientific preregistration is sealed at Seal V3, its run is BLOCKED, and retrieval-quality outcome access is FORBIDDEN. The membership environment is distinct from the Task 4F1 environment; their candidate/version numbers must not be conflated.

## N1 — Aggregate-distance cancellation defeats a broader canary interpretation

### Observed locally

The existing `controls()` uses reversal plus alternating signs and compares the **sum** of bit disagreements for each archive/query pair. F3 already identified that only 48 of 96 original coordinates are negated. The audit also suggested negating every coordinate as a way to make coverage total.

There is an additional limitation: even **two coordinates which are both negated** can undergo opposite disagreement changes, leaving the summed Hamming distance unchanged. Thus coverage of every coordinate by one sign vector is not a sufficient certificate of coordinatewise invariance.

The local diagnostic builds a finite, column-centered synthetic 96-by-96 archive, one synthetic query, and the positive diagonal `D=I`. Original columns 0 and 2 are zero in the archive; the query has values +1 and -1 respectively. Both columns are negated by the existing fixed canary after reversal.

The isolated source control passes. Two bit-disagreement indicators change per archive row, but their sum does not. Replacing the signs with all -1 also passes. Negating either affected coordinate separately exposes the change.

This reproduces a **limitation of the control's assurance**, not an incorrect retrieval score. The current function correctly compares the distances for the one transformation it actually tests. This finding does not establish that the fixture occurs after fitting any real archive, that an accepted result is wrong, or that the research hypothesis is false.

### Exact arithmetic witness

Use `b(x)=1` for `x>=0` and zero otherwise. For two-dimensional rational vectors:

```
x = (0, 0)
y = (1, -1)

H(b(x), b(y))                         = 1
H(b(-x), b(-y))                       = 1
H(b((-x0, x1)), b((-y0, y1)))          = 2
H(b((x0, -x1)), b((y0, -y1)))          = 0
```

This is not floating-point roundoff. One change contributes +1 and the other -1. A common coordinate permutation cannot remove that cancellation.

For any finite real pair, a single-coordinate negation preserves that coordinate's disagreement when both entries are nonzero or both are zero. It toggles the disagreement when exactly one entry is zero. Consequently, invariance under **every** common coordinate-sign pattern is equivalent to equality of the two zero masks. Necessity follows by negating a single mismatched coordinate; sufficiency follows coordinate by coordinate. The script additionally checks this characterization over all 81 ordered pairs of two-dimensional vectors with entries in {-1,0,1}, including both coordinate permutations and all sign patterns. This is an elementary local derivation, not a literature novelty claim.

### Head Researcher disposition

Do not close F3 with the assertion that an all-negative sign vector alone is a complete detector. First specify whether the required assurance is just equality for the fixed canary or invariance under arbitrary signed permutations. For the former, describe the exact limited scope. For the latter, require a coordinate-resolved check or independently checked single-coordinate controls, with cancellation fixtures among the negative tests.

Do not change zero handling, drop coordinates, choose canaries after real-data inspection, or silently strengthen the production abort policy. Those would require a separately reviewed design decision. The old candidate and audit remain intact; N1 is an additive qualification.

## Bounded preparation dispositions

These are repair priorities and acceptance criteria, **not permission to access a corpus or accept an execution package**.

| Finding | Disposition before a new integration candidate can be accepted |
|---|---|
| F1 — identifiers in exceptions | Treat corpus-derived IDs like text on public exception surfaces. Validate coverage before computation, refuse with fixed code-only errors, and verify `str`, `repr`, traceback, cause/context, stdout and stderr. Do not change the closed core to conceal a wrapper defect. |
| F2 — successful empty cohort | Reject an empty cohort before fitting. Require nonempty archive/record counts and exact expected coverage at both connector and eventual finalizer boundaries. |
| F3 — canary coverage | Retain the existing finding and add N1's cancellation qualification. A single all-negative aggregate check is not sufficient closure. |
| F4 — `assert_matched_blocks(a,b,a,b)` | Remove false assurance or compare independently extracted/constructed blocks from the actual rotations. A deliberately wrong embedding must make the check fail. |
| F5 — unreachable E-M-005 | Restore a reachable fixed diagnostic without reintroducing input-bearing exception context, or explicitly document the intentionally coarser error. |
| F6 — checkout byte changes | Prefer documented repository-local byte-preserving checkout settings for replay; do not mass-normalize immutable files or weaken hash comparisons. |
| F7 — missing ingestion schema gates | Validate builtin container/value types, mandatory keys, ID coverage, and archive indices before use; malformed fixtures must fail closed without caller IDs. |

Carry forward all nine audit test gaps: nuisance-priority reuse; malformed M-3 fixtures; E-M-026/027/028; empty cohort; exception suppression; E-M-022; tie-heavy parity; canary coverage including cancellation; and the distinction between top-k selection sets and ranked order. Passing a count of test methods is not equivalent to closing those obligations.

## Scientific integration obligations remain open

1. **Native anchor:** bind the exact frozen artifact, its hash, granularity, and compatibility with the declared per-question tolerance. Do not generate a replacement from forbidden outcomes.
2. **LoCoMo gold:** reconcile the historical corrected-evidence producer with raw-evidence ingestion through pinned source/provenance records first. Do not choose raw or corrected labels silently. The source divergence alone does not prove that any selected question's gold changes.
3. **LongMemEval order and shards:** bind an explicit historical archive-ordinal convention and ten-shard rule. The current `enumerate(cohort_ids)` choice is load-bearing through nuisance-priority seeds. Do not invent lexicographic ordering or a new shard formula as a supposedly harmless repair.
4. **Finalizer:** connect only to the accepted aggregation/output design, with full provenance, overwrite protection, and empty-record refusal. No finalizer or real driver was enabled here.
5. **Readiness:** require all mandatory negative controls, full accepted-environment regression, independent acceptance and the applicable pre-run seal/authorization process. A preparation PASS is not execution readiness.

The research question remains why native-coordinate sign/Hamming retrieval behaves differently under mixing and scaling, and whether that mechanism transfers. A robust measurement pipeline is a prerequisite to interpreting that experiment, not its scientific answer.

## What was and was not executed

**Executed now:** nine local synthetic diagnostic test methods, zero failures and zero errors. The source expressions for the canary and its two numerical helpers were isolated in a standalone script; the package itself was not imported. A separate exact `Fraction` oracle reproduced the cancellation. See `EVIDENCE.json` and `TEST_LOG.txt`.

**Environment:** Python 3.13.5, NumPy 2.3.5. This is NOT the accepted membership replay interpreter (3.13.15), and not a Task 4F1 replay. The rational witness does not depend on NumPy or floating point.

**Not completed:** a full clone, recursive anchor verification, `tools/verify_continuity_state.py`, the seal verifier, the original package replay, or an independent audit. The authenticated GitHub connector could read the repository, but the execution container's `git ls-remote` failed with `Could not resolve host: github.com`. Therefore this session does not certify continuity or any complete file inventory, and no canonical state/ledger update or merge is justified by it.

## Next single action

**Restore and verify the exact canonical snapshot and its continuity anchors in the accepted execution environment; then record the Head Researcher disposition of L-081, including N1, before issuing a tightly scoped synthetic-only repair candidate.** Any source/anchor disagreement must remain blocked rather than being repaired by assumption. Scientific gold and ordering decisions stay explicit and separate from mechanical code repairs.

The present branch is an additive, reviewable takeover checkpoint, not a replacement for `ops/CURRENT_STATE.json`.
