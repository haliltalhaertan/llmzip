# Membership M-1/M-2/M-3 preparation v1

Status: IMPLEMENTATION PREPARATION / NOT SEALED / REAL EXECUTION BLOCKED.
User authorized coding, synthetic checks and a separate-branch push on 2026-09-08.
This authorization is not a corpus-access, pilot, outcome, seal or execution authorization.
Base: 07ec929243068914676a0f30efd10c9f294c7e71. No predecessor bytes changed.
Canonical main/state/ledger remain the Continuity Lead's responsibility.

## Delivered and not delivered

- M-1: archive-only word/char TF-IDF, LSA, sparse concatenation, SVD96, normalization,
  centering; queries use the same fitted objects. Scale uses the unchanged closed core.
- M-2: six specified arms, ten paired seeds, shared rotation blocks, twenty common nuisance
  priority vectors, top-3 and fractional recall. No copied historical arms or old seed panel.
- M-3: an in-memory adapter for the existing LoCoMo and LongMemEval ingestion result schemas;
  records plus per-archive diagnostics. Both schemas tested with fake objects.
- Mandatory native anchor argument, native/scaled-native sign and distance checks, rotation
  norm/dot tests, signed-permutation canary, finite checks, complete record validation.
- No source ingestion call, download, cohort construction, on-disk record writer, production
  sharding, bootstrap invocation, seal or real driver. `run_on_real_corpus` always refuses.

This is NOT a declaration that M-3 or the whole execution package is ready for sealing.
Pure Python in-memory APIs can calculate what a caller gives them; the refusing real entry
point is not a universal security boundary. Code does not certify arbitrary callers or native
library logging. Preparation tests reject common data-file extensions and network connections
through a Python audit hook, with a narrow installed-package direct_url.json exception.

## Remaining integration obligations — do not silently decide

1. Native-anchor provenance and granularity must be bound without opening outcomes in this
   preparation. Current function requires per-question anchors; the governing control's exact
   frozen anchor artifact and compatibility must be checked before a production connector is
   accepted. Synthetic anchors are test fixtures only, never replacements.
2. Historical LoCoMo producer applies audit corrections, while accepted v5 ingestion reads raw
   evidence. This source-level difference is not evidence that any particular selected gold is
   wrong (no corpus was accessed). Gold semantics must be reconciled by the authority before a
   real connector is enabled; this package does not load corrections or change accepted gold.
3. LongMemEval archive ordinal currently follows supplied cohort order in the in-memory adapter.
   Production nuisance-priority ordering and deterministic ten-shard assignment must be bound to
   the historical convention, not inferred from this preparation. No sharding policy is invented.
4. Existing runner's accepted bootstrap/output path must eventually consume these records with
   complete provenance and overwrite protection. This package does not implement that finalizer.
5. Full mandatory negative-control coverage, real-ingestion-to-computation integration review,
   full accepted-lock regression, independent acceptance, and pre-run seal remain open.

Signed permutations of real coordinates with exact zeros can break the >=0 sign convention.
The canary deliberately aborts if that happens; it does not change zero handling or choose a
replacement canary after observing data. This behavior requires explicit independent review.

## Evidence

Seven unittest methods include both benchmark schema connectors, independent full-sort top-k
oracles, byte-pinned historical arithmetic comparisons, fit/query reuse, negative diagonal,
nonfinite and signed-control failures, bad gold, wrong/missing anchor and real-gate refusals.
Many assertions run within these methods; seven is the method count, not an inflated case count.
All inputs are generated strings/arrays. No real files or historical outcomes are read.

Development failures: first guard rejected NumPy installed-package origin metadata; added a
narrow metadata exception. A test demanded bit equality between SVD fit_transform and transform;
corrected to absolute 1e-12 numerical comparison. The actual native sign/distance gates retain
bit equality. Final replay evidence is under evidence/; initial failed attempts are disclosed
here, not misrepresented as passing runs. Tests are implementation-team checks, not audit.

Replay from repository root in accepted Python 3.13.15 environment:

    python -B drafts/v52/membership_execution_prep_v1_2026_09_08/replay.py <new-output-directory>

No dependency installed or changed. Expected NumPy2.3.5/SciPy1.17.0/sklearn1.8.0/pandas2.2.3
is the separately accepted membership environment, NOT the Task4F1 environment.

## Provenance and normative precedence

Core: dcb568d0a6c33154c1568500325ad457b4d6f455, membership_impl_v3_2026_09_07,
SHA256 bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72.
Runtime verifies core bytes and loads it by explicit path, not an ambiguous module name.
Arithmetic source: 692f599eedeb7e7a649443f24ff507e8c4d1c17d,
research/v52/locomo_sign_mechanism_replication.py,
SHA256 a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b.
Tests extract ONLY the three selected arithmetic functions from its hash-verified AST;
historical producer imports/acquisition/results never execute.

Governing order: acceptance 9b4af594 > R2 16019724 > R1 2eadc41b (except superseded
categorical rules) > draft 56c29416. Exact documents/hashes are registered in the unchanged
membership_impl_v3_2026_09_07/GOVERNING_DOCUMENTS.md. No ratio or verdict bands introduced.

Predecessor audit: audit/v52-codex-v5-repair-review-2026-09-08 at 2cf602090a6c4c42dba44f66d95d8dfed0e0f2e8,
CODEX_V5_REVIEW.md SHA256 fd10e53324787965e11155cb6cd31952496199f0e8250fe9416c996abf227cea.
PASS WITH FINDINGS only for v5 repair; F1-F4 remain documented, not reopened or declared fixed.
