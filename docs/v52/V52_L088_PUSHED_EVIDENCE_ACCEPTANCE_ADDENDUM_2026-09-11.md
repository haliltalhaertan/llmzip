# V52 — L-088 Draft Addendum: pushed evidence acceptance status

**Date:** 2026-09-11
**Prepared by:** ChatGPT continuity/research session.
**Applies to draft:** `docs/v52/V52_L088_MUSE_PQ_AUDIT_DISPOSITION_2026-09-11.md`
on branch `hr/l088-muse-pq-disposition-2026-09-11`.
**Status:** ADDITIVE DRAFT ADDENDUM. Not a canonical ledger entry. Does not modify
`ops/CURRENT_STATE.json`, does not authorize a baseline run, and does not touch Task 4F1.

## Why this addendum exists

The original L-088 draft correctly treated the operator-local Muse/storage/PQ measurements
as `RELAYED / NOT LOAD-BEARING UNTIL THEIR BYTES ARE PUSHED AND VERIFIED`.
That condition has now partly changed: the cost/PQ measurement package has been pushed as a
hash-bound, additive evidence branch. This addendum updates only that evidence status; it does
not rewrite the original hash-bound draft.

## Evidence branch verified here

Branch:
`evidence/twelve-byte-cost-2026-09-11`

Commit:
`f11498319829b10dbd32f4b55e306072be933df9`

Canonical parent / merge base:
`489e5f94c344c9cee02aa357ff3d59c2029f5846` (L-087).

Scope check:
- one additive evidence commit;
- no canonical `main` mutation;
- no sealed Task 4F1 path touched;
- evidence namespace only.

The pushed `HASHES.txt` binds:

- `EVIDENCE.json`
  `4925ba839f79143847c86f94b7d66a81d0b08dc89a2ccbc27e6fcb0f67c8b9f2`
- `measure_twelve_byte_cost.py`
  `0eb472ebd14585f677c340fb54a4b5ae6eeb980373e75507678ea0b378ed8028`
- `README.md`
  `c93a5637b811a12c17e54987d66c10c2c53d1b4ed1af20d60b7511703fd8c0af`

The measurement script pins and checks the archive-cardinality source Git blob
`b4336dd47fcf14e4b39f65bed3377d56ea9e77c7`; the pushed evidence records
`blob_matches: true`.

## What is independently verified by this session

1. The evidence branch/ref, commit identity, additive scope and hash manifest are present on
   GitHub and internally consistent at the repository-object level.
2. The exact archive-cardinality source blob named by the script exists at the pinned ref.
3. Official Faiss v1.15.0 source independently confirms the structural RaBitQ code-size rule:
   one-bit storage is `ceil(d/8) + 8` bytes per vector, with the extra eight bytes carried
   as two float32 per-vector quantities used by the distance computation.
4. Official Faiss v1.15.0 clustering source independently confirms
   `min_points_per_centroid = 39` is a warning/reliability threshold, while the hard
   training refusal is `n < k`.
5. The original preregistration is archive-local by construction, so archive-local shared-state
   amortization uses each archive's stored-vector count `N_archive`, not the panel's question count.

## Pushed measurements now available as evidence

The pushed `EVIDENCE.json` reports, among other quantities:

- `RaBitQ(32, 1 bit)` = 12 marginal bytes/vector;
- `RaBitQ(96, 1 bit)` = 20 marginal bytes/vector;
- `RaBitQ(96, 2 bit)` = 44 marginal bytes/vector;
- serialized linear storage decompositions:
  - `SIGN96`: shared ≈ 33 B, marginal 12 B/vector;
  - `TOP32_RABITQ32`: shared ≈ 202 B, marginal 12 B/vector;
  - `RABITQ96`: shared ≈ 458 B, marginal 20 B/vector;
  - `PQ96_m12x8`: shared ≈ 98,390 B, marginal 12 B/vector;
  - `OPQ_PQ96_m12x8`: shared ≈ 135,325 B, marginal 12 B/vector;
- the listed 12-byte PQ layouts have Faiss default recommendation thresholds
  9,984 / 2,496 / 624 / 156 points for m12x8 / m16x6 / m24x4 / m48x2;
- the archive-cardinality record contains 470 archives, min 396, max 616,
  mean 492.77872340425535;
- for OPQ+PQ shared state 135,325 B, the pushed mean archive-local effective cost is
  `287.6889713064122 B/vector`; this is `mean_i(12 + 135325/N_i)`, not
  `12 + 135325/mean(N_i)`.

These are no longer chat-only relayed numbers: their script, output, environment record and
source pin are pushed and hash-bound at `f1149831`.

## Remaining verification boundary

This session **did not dynamically rerun** `measure_twelve_byte_cost.py` under
`faiss-cpu==1.15.0` and `numpy==2.4.6`.

Reason: the available execution container has no Faiss installed and failed to resolve/download
the pinned wheel from `files.pythonhosted.org`. An attempted independent GitHub-Actions replay
could not be created because workflow-file writes were blocked by the tool safety layer.
Therefore this addendum does **not** claim independent numerical runtime reproduction of the
serialized-byte table.

Correct status distinction:

- `CHAT-RELAYED`: **closed** for the pushed cost/PQ package;
- `PUSHED + HASH-BOUND + SOURCE/STRUCTURE VERIFIED`: **yes**;
- `INDEPENDENT DYNAMIC RUNTIME REPLAY`: **pending**.

The Muse report/ANSWER_KEY/raw JSONL are not part of this evidence branch and remain separately
unverified by this session unless/pending their own pushed evidence package.

## Consequence for canonical L-088

A canonical L-088 may now cite `f11498319829b10dbd32f4b55e306072be933df9`
as the operator measurement evidence package without calling those measurements chat-relayed.
It must still state that independent runtime replay of the exact serialized-byte measurements
was not completed by this session.

This is sufficient for a **source/package disposition** (`PASS WITH FINDINGS`), not for a claim
that a third environment reproduced every number and not for baseline execution readiness.

## Outcome boundary

Unchanged: Task 4F1 is `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
No real retrieval result was computed or accessed by this addendum.
