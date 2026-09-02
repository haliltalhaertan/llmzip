# V52 Task 4F1 — Co-Chair Review of L-008 and Scientific Route

Date: 2026-09-02  
Role: Research Co-Chair / independent approval-veto reviewer  
Reviewed canonical state: `main@a5ee73fa2df29683a8a68fcb2f17461a607cc011`  
Outcome boundary: outcome-free; no run, finalize, HMAC key, valid authorization, real ranking, metric, or arm result was accessed or produced

## Decision summary

1. **L-008: REQUEST CHANGES; not co-signed as a final package seal.** The independent
   V4 audit evidence is accepted as authentic and internally hash-consistent, and its nine
   implementation gates are accepted. The broader L-008 conclusion that the complete V4
   execution package is ready to remain sealed is not co-signed because the byte-bound
   execution specification contains a load-bearing internal contradiction that the audit
   did not report.
2. **Seal mechanism: detached attestation is the correct mechanism, but V5 is required for
   the content defect.** An audited candidate must not be edited in place merely to change
   its historical submission status. The final authoritative seal should remain a separate,
   immutable attestation that binds the candidate, audit, and acceptance hashes. V5 is
   required here to repair contradictory and stale candidate payload text, not to mutate an
   already audited seal after the fact.
3. **Task 4F1 route: option B.** Before preregistration, write and freeze the outcome-free
   scientific justification for the restricted cohort and the exact tier-stratified
   estimands. A passing implementation audit alone is not a reason to run.
4. **Tier analysis: yes, as the primary scientific interest, with a strict interpretation
   boundary.** The primary object should be a scale-stratified fixed-benchmark heterogeneity
   profile. It must not be described as a causal effect of context length or as a monotonic
   degradation law because the tiers are not paired/randomized and their question/gold
   composition differs.
5. **Single writer: Continuity Lead remains the sole writer.** The co-chair writes only
   review/approval artifacts on a separate branch. The Continuity Lead alone updates
   `ops/CURRENT_STATE.json` and `docs/CONTINUITY_LEDGER.md`, recording the exact review
   commit and file SHA256. A load-bearing transition closes only after an explicit co-chair
   approval; a request-changes verdict keeps the transition blocked.

Task 4F1 remains **BLOCKED** for preregistration and execution.

## Evidence independently checked

- Accepted audit branch commit:
  `641568d8b78af97eb69c9dc4e0434e7b6564a26c`; parent:
  `8700098d4b89a45229abf5634086bffe3a6df9a7`.
- Diff versus the parent: 31 additions, zero deletions, all confined to
  `audit_v52_t4f1_execution_candidate_v4_independent_audit_2026_09_01/`.
- Audit manifest SHA256:
  `8dcb2fb8b23980fd3fe0e65a25834e1af259bdef855ed577ae40ab4a43ee4387`.
  Independent local verification: 30/30 declared files match hash and byte size; zero
  missing, zero mismatch, zero undeclared recursive payload.
- V4 runner SHA256:
  `f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8`.
- V4 payload inventory SHA256:
  `fe1de9c7160191f7a001ecadb928057411cc7b560a3f8f8a9130c6d3ceb1ba5e`.
- V4 candidate seal SHA256:
  `1bf740f573fc74c6e8aa6e23a3f07a5bcc97a10d1fa7e6e7358560e1598f06e9`.
- V4 preflight manifest SHA256:
  `4f78b5c8b184ad0ecfbbf444ffddbbcd076c6b78fa65c4b0d76696259f1c930f`.
- L-008 acceptance record SHA256:
  `f04eecd5f1b9e81aa2bb90830d3c678deb9dcf80adc335130e54314ac5f6c547`.
- Audit command log: 16 launches; zero launch containing `--mode run`; zero containing
  `--mode finalize`; zero carrying `V52_T4F1_AUTH_HMAC_KEY_HEX`; three guard self-test
  commands rejected before launch.
- The committed outcome-boundary record reports zero real ranking and no retrieval-quality
  result computed, read, or reported.
- `tools/verify_continuity_state.py` passes on `main@a5ee73f` using the bundled local
  interpreter.

These checks resolve the role-concentration concern for the evidence review: the V4
implementer did not author the audit package, and this co-chair independently re-fetched
and verified the audit commit instead of accepting the implementer's relayed verdict.

## Blocking finding CC-01 — contradictory V4 canary specification

The byte-bound `task4f1_execution_candidate_v4_2026_09_01/EXECUTION_SPEC.md` states in its
Representation and caching section that the archive/query **raw array SHA256** values must
exactly reproduce the two V3 digests:

- `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`
- `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`

The same bound file later says that V4 replaces those machine-dependent float digests with
the sign-code digests:

- `7365b6c4ba7753ee5431f89816c3151a2618f475415024d8932c839609ded5b5`
- `5e40a5d1f0d33bf16c4005ed8aa172464dd1fb205da983f5373c9940f4ccad2b`

The latter is what the V4 runner implements and what the independent audit validated. The
two statements cannot both be normative: V3 was superseded precisely because the former
raw-float digests change across conformant BLAS dispatches. Because `EXECUTION_SPEC.md` is
listed in `PAYLOAD_HASHES.json`, this is a sealed package-semantics defect rather than an
unbound README typo. It also creates a real cold-start handoff hazard.

The V4 audit prompt concentrated Gate 2 on runner/AST change isolation and did not require
a semantic contradiction scan across all bound prose. Accordingly, the nine reported gate
results may remain valid while the complete execution package is not ready for co-signing.

## Required V5 scope

Create a new V5 namespace; preserve V1–V4 and all audits unchanged.

Minimum required corrections:

1. Remove the obsolete raw-float digest requirement from `EXECUTION_SPEC.md` and leave one
   unambiguous V5 canary definition based on sign codes plus the frozen margin.
2. Correct the V3 docstring in `candidate_package_preflight.py`.
3. Replace the inert V3 authorization template label/note with a V5 fail-closed template
   matching the V5 authorization schema. It must remain incapable of authorizing a run.
4. Redesign status terminology so `CANDIDATE_EXECUTION_SEAL.json` explicitly records the
   immutable **status at audit submission**, while a detached final-seal/acceptance file is
   explicitly authoritative for post-audit state. Do not edit the candidate seal after its
   audit.
5. Prove the execution runner is byte-identical to the accepted V4 runner unless a separately
   justified preregistration requirement changes executable behavior. Any executable change
   expands the independent audit accordingly.
6. Add a mandatory cross-payload semantic-consistency gate to the V5 audit prompt, including
   canary digests, schema names, authorization status, cohort anchors, and precedence rules.

A delta-scoped audit may reuse V4 computational evidence only if its protocol first proves
that the runner and all execution-affecting bytes are identical and that every V5 change is
declarative. Otherwise V5 receives the full cold-start audit.

## Scientific decision for Task 4F1

The restricted cohort still has scientific value because it preserves 1,712 questions over
96 uniquely keyed archives without selecting duplicate occurrences using outcomes. Its most
distinctive contribution is the broad nominal scale range rather than a third undifferentiated
replication of the existing LongMemEval and LoCoMo direction.

The frozen structural profile is materially unbalanced:

| Tier | Eligible questions | Eligible archives | Mean raw message units/archive | Mean gold units/question | Structural ALL@3 zeros |
| --- | ---: | ---: | ---: | ---: | ---: |
| 100K | 355 | 20 | 286.6 | 3.08 | 96 |
| 500K | 629 | 35 | 1,087.4 | 4.26 | 168 |
| 1M | 553 | 31 | 2,105.7 | 8.59 | 253 |
| 10M | 175 | 10 | 20,869.6 | 7.47 | 70 |

Therefore the preregistration should freeze this hierarchy before any outcome access:

- **Primary scientific family:** four tier-specific question-weighted contrasts,
  `Native SIGN96 - mean(Haar96 seeds)`, for Fractional Evidence Recall@3.
- **Supportive metrics:** the same tier-specific contrast for ANY@3; ALL@3 reported with
  its existing structural-zero rule but not used as the main scale claim because gold
  cardinality changes strongly across tiers.
- **Negative control:** Signed-permutation must remain exactly equal to Native at ordered
  top-3 IDs and distances; failure invalidates interpretation.
- **Descriptive comparator:** ITQ96 remains descriptive only.
- **Across-tier summary:** pre-specify a heterogeneity/profile summary. Any ordered trend is
  an association across fixed benchmark strata, not a causal context-length effect. Report
  ability-stratified and gold-cardinality-stratified sensitivity so composition cannot be
  mistaken for scale.
- **Denominators:** freeze the four denominators above and retain the pooled 1,712-question
  estimand as a secondary replication summary.
- **Inference boundary:** this is a fixed-benchmark estimand. Do not claim population-level
  inference from trial rows or seeds; trials are deterministic replication identities.

The exact formulas, multiplicity/decision rule, any uncertainty calculation, and the
post-processing implementation must be byte-bound and independently audited before a run
authorization is even constructible.

## Governance and next action

The Continuity Lead remains sole writer of `ops/CURRENT_STATE.json` and
`docs/CONTINUITY_LEDGER.md`. This review branch is an external co-chair decision record and
must not itself advance canonical state.

Next single action for the Continuity Lead: record this co-chair `REQUEST CHANGES` decision
and its exact commit/file hash in the ledger, then prepare the minimal V5 remediation and
V5 independent-audit prompt. Do not preregister or run Task 4F1.

Two repository-owner operations remain separate P0 items: set GitHub's default branch from
`claude/itq-frontier-audit-wfrz6a` to `main`, and publish any missing state tag using an
identity with tag-push permission. Neither changes the scientific verdict above.
