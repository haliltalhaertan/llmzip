# V52 static-storage V7 — semantic anchor and guarded-plan integration

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION.**

Parent implementation: `695e3c78aee16a719bcfdd622a6527d448f71a47` (`static_storage_integration_v6_2026_09_12`).
Canonical context observed during preparation: `main@5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`.

V7 is additive. It does not rewrite V6, the earlier anchor guard, the reviewed contract, `main`, ledger, or state.

## Why V7 exists

Independent/adversarial work after V6 showed that three dilution paths still existed:

1. the archive-anchor parser let the caller choose the semantic value column, so a different numeric column could masquerade as `N_archive`;
2. the expected anchor digest was caller-supplied, so a fake table plus its own digest could be accepted;
3. `population.count` could remain internally consistent with the plan while disagreeing with the true archive size, letting effective bytes/vector be diluted.

A fourth binding weakness remained: the V6 public interface accepted caller-supplied guarded-plan/contract digest strings rather than mechanically creating and carrying the reviewed parent `Plan` object itself.

## V7 design

`storage_semantic_gate_v7.py` exposes one LongMemEval entry point:
`preflight_longmemeval_v7(...)`.

The caller may supply only the externally frozen plan digest and companion-file digests. The caller cannot supply:

- anchor digest;
- anchor id/value column names;
- anchor source semantics;
- parent-guard source;
- V6 source;
- guarded-plan digest;
- guarded-contract digest.

Those are pinned by V7.

Pinned LongMemEval anchor:

- exact content SHA256: `d4c9ce62b0f1b66611611bb014a887d2e7e5fcfaee0af94f53ffb70dc84d7d32`;
- id column: `question_id`;
- value column: `N_archive`;
- exact row count: 470;
- source identity: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00:docs/v52/task4c2/V52_T4C2_feature_geometry.csv`.

The anchor digest and columns exist in code, not in the literal plan and not as function arguments.

## Mechanical parent-guard binding

V7 authenticates the reviewed `measurement_plan_guard.py` source by its frozen SHA256, executes those authenticated source bytes, then invokes its `load_plan()` itself.

The `Plan` object returned by that exact pinned guard is used for semantic anchor checks. V7 then derives the digest values passed internally to pinned V6 from that object. There is no public `guarded_plan_sha256` / `guarded_contract_sha256` knob.

The reviewed measurement contract is also pinned to SHA256
`e395451d026f176b875856244abe73b54a7d54cdf2649eec272f14cfc609c510`.

## Denominator semantics

The plan archive roster and order must exactly equal the pinned 470-row LongMemEval anchor, and every declared `N_i` must equal its pinned `N_archive`.

An authoritative denominator probe is **only**:

`N == anchored N_i AND q == 1`.

This matters because the frozen panel may also contain `(N_i,q=8)` for sentinel archives. That q=8 probe is a batch diagnostic and is never eligible as the amortization denominator.

For every physical copy, V7 selects exactly one BEFORE population bound to the archive's authoritative `(N_i,q=1)` probe and requires:

`population.count == anchored N_i`.

Therefore neither an inflated plan `N_i` nor an inflated `population.count` can create a smaller effective B/vector denominator.

Diagnostic staircase populations and q=8 populations remain in the frozen plan but cannot contribute the authoritative sharing denominator.

## LongMemEval-only scope

V7 deliberately supports LongMemEval only. It does **not** infer a LoCoMo anchor format from unrelated evidence. LoCoMo remains blocked until a separate source-specific anchor profile/parser is prepared and independently reviewed.

## Test status

Local sandbox test run on the exact candidate source:

- 8 tests discovered;
- 6 passed;
- 2 skipped because this sandbox has no repository checkout and DNS could not clone GitHub.

The six executed tests cover:
- q=8 at `N_i` is not authoritative;
- inflated `population.count` is rejected;
- wrong declared `N_i` is rejected;
- missing authoritative q=1 is rejected;
- a subset archive roster is rejected;
- the public entry point exposes no anchor-column/digest or guarded-digest knobs.

The two skipped tests are intentionally repo-dependent:
- loading the real canonical 470-row anchor and pinned dependency modules;
- mutating the real anchor bytes and proving fixed-digest rejection.

They must be run by the independent reviewer from a real repository checkout. This receipt does not promote those two checks to PASS.

## Still open

V7 does not create a literal actual plan and does not measure bytes.

The following remain open:
- independent V7 audit;
- repo-checkout execution of the two canonical dependency tests;
- unresolved fitted/projector artifacts from the source inventory;
- persistent ID/offset representation where unresolved;
- actual physical-copy/share populations;
- final serialization identity;
- real adapter/runner implementation;
- external freeze record;
- a separately reviewed LoCoMo anchor profile.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
