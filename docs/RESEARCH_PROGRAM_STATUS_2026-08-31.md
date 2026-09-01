# Research Program Status — 2026-08-31

Decision authority: Head Researcher

This document is the current operational research ledger. It distinguishes accepted scientific evidence, feasibility evidence, blocked branches and required next gates.

## Executive state

- `[FROZEN — TASK 4C3 LONGMEMEVAL NUMERICAL CHECKPOINT]`
- `[FROZEN — TASK 4D LOCOMO NUMERICAL CHECKPOINT]`
- `[CROSS-BENCHMARK REPLICATION ESTABLISHED — LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — GENERALIZATION BEYOND LONGMEMEVAL + LOCOMO]`
- `[NOT ESTABLISHED — CAUSAL MEDIATOR]`
- `[TASK 4E0 BLOCKED — LONGMEMEVAL-V2 PUBLIC DATA/METHOD INCOMPATIBILITY]`
- `[TASK 4F0 AUDIT ACCEPTED WITH CONDITIONS — RESTRICTED BEAM COHORT IS REFREEZEABLE]`
- `[TASK 4F1 BLOCKED — DO NOT PREREGISTER OR RUN]`
- `[TASK 4F0 RESTRICTED-COHORT PROTOCOL SEALED — 22/22 INDEPENDENT GATES PASS]`
- `[TASK 4F1 EXECUTION IMPLEMENTATION PREPARED — INDEPENDENT CODE AUDIT PENDING]`
- `[TASK 4F1 V2 INDEPENDENT AUDIT BLOCKED — B1/B2/B3 FINALIZATION INTEGRITY DEFECTS]`
- `[TASK 4F1 V3 CANDIDATE PREPARED — FRESH OUTCOME-FREE INDEPENDENT AUDIT PENDING]`

## Accepted scientific evidence

Task 4C3 established a fixed-benchmark native-axis effect on the frozen 470-question LongMemEval cohort: Native SIGN96 `54.197517730496%`, mean Full-Haar96 `38.271666666667%`, `D96 = -15.925851063830 pp`.

Task 4D independently replicated the direction on the frozen 1,535-question evidence-valid LoCoMo cohort: Native SIGN96 `23.654714666441%`, mean Full-Haar96 `13.770827054136%`, `D_LoCoMo = -9.883887612305 pp`.

These are benchmark-level paired results. They do not establish a universal theorem, population-level generalization, a causal mediator, or production superiority.

## Task 4F0 decision

The independent BEAM audit is accepted as a feasibility and governance result with verdict:

`[PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE]`

Verified audit facts:

- upstream BEAM commit `3e12035532eb85768f1a7cd779832b650c4b2ef9`;
- 100 conversations, 2,000 probing questions and 327,116 raw message units;
- 1,743 exact-source questions, 200 abstentions, 55 ambiguous/missing, one coarse and one malformed record;
- 1,720 divergent duplicate message keys in `1M::5`, `1M::26`, `1M::33`, and `1M::34`;
- outcome-independent restricted primary cohort: 1,712 questions;
- representation transfer: pass on clean archives;
- scale feasibility: pass at 100K, 500K, restricted-clean 1M and 10M;
- Native-vs-Haar retrieval-quality outcome inspected: no.

The full-cohort BEAM estimand is rejected. The restricted cohort is eligible for a new pre-outcome refreeze, not for immediate scientific execution.

## Mandatory gate to Task 4F1

Task 4F1 remains closed until a new 4F0 restricted-cohort refreeze locks all of the following before any outcome access:

1. exact prompt bytes and a reproducible prompt SHA256;
2. `estimand_primary_cohort.csv` SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`;
3. exclusion of the four defective 1M archives and the exact 1,712-row denominator;
4. formulas for Fractional Source Evidence R@3, ANY@3 and ALL@3, with ALL@3 structural zeros retained for the 587 questions having more than three gold units;
5. memory-unit key/text, dependency versions, single-thread environment and random states;
6. exact frozen adapter/compute script bytes and hashes;
7. pre-run leakage, non-vacuity, representation-repeatability and resource gates;
8. a stop rule forbidding post-outcome cohort repair, rescue seeds, extra rotations, threshold tuning or metric substitution.

The initial restricted-refreeze audit attempt blocked on the unavailable dependency lock. After the exact isolated environment was installed, the superseding independent audit passed 22/22 byte, cohort, raw-corpus, determinism, leakage and invariance gates and returned `PASS WITH CONDITIONS — CANDIDATE MAY BE SEALED BY HEAD RESEARCHER`. The Head Researcher accepted that sign-off and sealed the 1,712-question restricted-cohort protocol. The remaining blocker is a separately byte-bound outcome-bearing 4F1 implementation and an independent audit of that implementation. This is an execution-governance gate, not a scientific outcome.

Only after the future 4F1 implementation is byte-bound and independently accepted may the Head Researcher decide whether to preregister Task 4F1.

## Task 4F1 implementation preparation

A separate guarded execution candidate now exists at `task4f1_execution_candidate_2026_08_31/`. It binds the outcome-capable runner SHA256 `28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428` and candidate seal SHA256 `a1277e4665936ea691505a2d386c1d6a4824c2ebc5e5e56d6a94aba1f58876cd` while retaining blocked authorization.

The outcome-free preparation preflight passed exact environment, 1,712-question/96-archive cohort structure, 192 pinned corpus blob checks, synthetic method/invariance checks, a raw `100K::12` representation digest canary and a negative run-authorization probe. No retrieval-quality result was computed. This is implementer evidence, not independent sign-off.

The next gate is a cold-start independent audit of these exact execution bytes. Even a passing code audit will only permit sealing the implementation; a separate Task 4F1 preregistration and Head Researcher run authorization will still be required.

## 2026-09-01 — Task 4F1 audit/remediation chain

The V1 execution-code audit supplied useful technical checks but disclosed Incident A1: an auditor-side negative-test error triggered outcome-capable execution before containment. No metric value was reported, but that audit cannot serve as the clean outcome-free seal sign-off.

The subsequent clean V2 audit was `BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`. Its synthetic-only tests reproduced three load-bearing defects: derived finalization CSV overwrite when no manifest exists; acceptance of stored metrics not recomputed from frozen gold; and acceptance of Native/signed-control top-three divergence when metrics remain equal.

V3 preserves V2 and its audit unchanged, adds exclusive no-replace derived-output commits, exact frozen-gold metric recomputation, and exact Native/signed-control ID-plus-distance validation. V3 passed outcome-free implementer preflight and synthetic B1–B3 regressions only. It remains unsealed, unpreregistered and unauthorized until a new cold-start audit of its exact bytes returns an uncontaminated PASS.

## Operational governance defect

Remote `main` was verified at `d3c7aa09c9553cd5ac100e668923abab602e4257`, but GitHub's remote `HEAD` currently points to `claude/itq-frontier-audit-wfrz6a` at `78b4fdfa7234fb545dbf9eb51ebce90a794a0d6b`. This conflicts with `CHAIN_OF_CUSTODY.md`, which defines `main` as canonical.

Before opening or merging further research work:

1. restore the GitHub default branch to `main`;
2. require PR bases to be explicit;
3. verify remote `main` commit immediately before branch creation and merge;
4. never infer canonical state from remote `HEAD` until the setting is repaired.

## Priority queue

1. P0 — repair GitHub default branch to `main`.
2. P0 — review and merge the accepted 4F0 audit/governance package without modifying frozen artifacts.
3. P0 — preserve the sealed 4F0 restricted-cohort payload and audit chain; do not run Task 4F1.
4. P0 — independently audit the byte-bound 4F1 execution candidate without running retrieval quality.
5. P1 — seal or reject that implementation and close or retain each execution gate explicitly.
6. P1 — only then make a Head Researcher decision on Task 4F1 preregistration.
7. P1 — recover `V52_T4C2_same_input_proof.csv` only from its canonical byte source and accept it only if SHA256 equals `16a6c4a66be6f5cb4ac81157588c9e735cb1b31d122e83c68f14fbf77dd57e57`.
8. P1 — independently materialize and hash the four currently external Task 4C3/dataset pins when resources permit.
9. P2 — defer mediator studies, alternate representations and production claims to separately justified branches.
