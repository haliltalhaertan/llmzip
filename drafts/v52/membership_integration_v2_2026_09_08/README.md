# Membership integration v2 — synthetic candidate, not execution ready

Base: 56e67018b61c32fd0392f0d8f4234e731faf8ce9. User authorized continuation and
subagent-assisted implementation. All changes are new files in this namespace.
Main/state/ledger remain owned by Continuity Lead. No old payload is changed.

## Scope delivered

The v1 representation and scoring arithmetic is ported, not re-designed. Current
six arms, ten paired rotation/partition seeds, twenty nuisance priorities and
zero convention remain unchanged. Source contracts from 56e6701 are loaded from
verified Git bytes. LoCoMo corrected gold is applied without cohort reselection;
LongMemEval all-source lexical ordinals and source-order modulo-ten shard plan
are connected to scoring. The plan is emitted; distributed shard scheduling is
NOT implemented.

`finish_synthetic.compute_synthetic` connects generated ingestion-shaped objects
to representation, scoring, the unchanged core's paired matrices, aggregate and
bootstrap functions, then an explicitly synthetic create-only bundle writer.
It uses the accepted 10000 replicates and seeds 52001107/52001207/52002107, and
never computes a LongMemEval cluster bootstrap. It is NOT the accepted production
runner's manifest/seed-file/provenance finalizer. It does not authenticate inputs.
No real source reader, correction-file loader, corpus acquisition, pilot, seal,
HMAC or production authorization path is added. Real entry functions refuse.

## Audit 5126766 findings — implementation changes, closure pending reviewer

- F1/F2/F7: validate nonempty cohort, schema, question coverage and duplicate
  membership before fitting; wrap closed-core record validation with code-only
  errors. Tests cover IDs in missing/extra/unscored cases. Contracts separately
  raise code-only ContractError; not every exception is PipelineError.
- F3: 96 predetermined single-coordinate sign flips combined with reversal, for
  scaled/unscaled input. One all-negative mask could conceal cancellation across
  zero coordinates; tests include that case. Both mixed-zero directions are
  covered at every coordinate; all-zero coordinates pass. The gate can reject
  real zero-containing inputs; no zero convention or rescue canary is changed.
- F4: compare actual blocks extracted from assembled rotations, not (a,b,a,b).
- F5: remove dead E-M-005; collapsed-vocabulary failure intentionally uses E-M-006.
- F6: execute fixed-commit, SHA256-verified raw Git source for core/contracts,
  ignoring CRLF-converted working copies. Git and dependencies are trusted.
  No global/repository line-ending setting is changed. Missing blobs fail closed.

This is implementation-team evidence, including subagents, NOT independent audit.
Exception tests cover named surfaces; arbitrary callers, traceback-local inspection,
native libraries and hostile Python objects are not certified confidential.

## Two source-policy decisions and remaining obligations

Decision authority: chat approval recorded in 56e6701's DECISION_AND_SCOPE.md.
`source_adapter` explicitly translates historical normalized correction objects:
has_correct_evidence=False must OMIT correct_evidence, while True preserves even
an empty normalized list. New contracts must not receive historical dictionaries
untranslated. `evidence_declared` counts unique normalized references, not raw items.
Regex extraction and malformed-raw-input handling still belong upstream.

OPEN before production:
1. Native reference: historical runner checks aggregate frozen scalar, while v1/v2
   preparation requires per-question anchors. No per-question artifact has been
   bound. Choose/record compatible granularity before enabling a real connector.
   Synthetic test anchors are generated fixtures, never historical reproduction.
2. Bind the ten correction-file sizes/hashes from pinned producer code. Original
   audit manifest covers twenty files, so ten-only verification cannot claim its
   full verification. No correction bytes were opened here. Source acquisition,
   original field presence, strict normalization and duplicate-policy checks remain.
3. Actual source-ID plan must be derived from hash-verified corpus under separate
   access permission; synthetic_counts is a test convenience, not a production gate.
4. Production mapping/seed-record/provenance finalizer and distributed scheduling
   remain absent. Synthetic writer receipts are not seals. Partial failed output
   directories are retained and cannot be reused.
5. Independent whole-candidate review, broader accepted-environment regression,
   pre-run binding and distinct real-ingestion/run permission remain mandatory.

## Replay

    <Python3.13.15> -B drafts/v52/membership_integration_v2_2026_09_08/replay.py <new-evidence-dir>

Checks all eleven recorded package versions. Suites run sequentially in separate
processes with four thread environment variables=1 and PYTHONHASHSEED=0. A thread
configuration is not measurement of executed native thread counts. Core suite
does not reopen scientific results. Only synthetic fixtures are fitted/scored.

Governance inherited: acceptance9b4af594 > R2 16019724 > R1 2eadc41b > draft56c29416;
source-policy additive approval56e6701. No new ratio, outcome band or verdict.
