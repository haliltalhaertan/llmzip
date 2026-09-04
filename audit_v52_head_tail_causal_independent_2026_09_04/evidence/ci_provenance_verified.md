# CI provenance — independently verified via the GitHub Actions API

All values below were read by the auditor from the GitHub API, not from the repository's
own provenance manifest. Manifest values are quoted only for comparison.

## Complete workflow-run history on `research/v52-sign-mechanism-locomo-2026-09-04`

`total_count = 11`. Runs relevant to the Head/Tail stage:

| workflow | run id | run_number | run_attempt | conclusion | head_sha |
|---|---:|---:|---:|---|---|
| V52 LoCoMo head-tail two-subspace causal | 33884713242 | 1 | 1 | success | 5a0e80234de760e0e8f4457cbd654faf8e07f56e |
| V52 LongMemEval head-tail two-subspace causal | 33884860024 | 1 | 1 | success | c30c36d48b250c0c50a9a190db03f877c78e24c8 |

Each Head/Tail workflow has **exactly one run, run_number 1, run_attempt 1, conclusion
success**. There is no failed, cancelled, superseded or re-run Head/Tail execution anywhere
in the branch's run history. (Failures that do appear in the history — runs 33864225295,
33864665619, 33864691367, 33883822273 — all belong to the *earlier* spectral-band and
shard-recovery stages and are visible rather than scrubbed.)

## Artifacts

LoCoMo run 33884713242 — 1 artifact:

| id | name | digest | expires |
|---:|---|---|---|
| 9941357062 | v52-locomo-head-tail-causal-results | sha256:c8518840ee0afdd4547e65d35553b337df3053e2c68735e8a40d4b1171b89b2b | 2026-10-04 |

Manifest declares artifact_id `9941357062`, digest
`sha256:c8518840ee0afdd4547e65d35553b337df3053e2c68735e8a40d4b1171b89b2b` — **match**.

LongMemEval run 33884860024 — 6 artifacts: shards 0,1,2,3,4 (each present exactly once)
plus the final aggregate:

| id | name | digest |
|---:|---|---|
| 9941573793 | v52-longmemeval-head-tail-shard-0 | sha256:767a238d8e92ef4c6a25ebdaf6d8177681d5c20c04bb94c0e1f73aa6af4f1cb6 |
| 9941579714 | v52-longmemeval-head-tail-shard-1 | sha256:03d02bc542aab8bdef9df2e0698f06e7a0fa777eb4605d98046ed0fa6749f8c5 |
| 9941618395 | v52-longmemeval-head-tail-shard-2 | sha256:1752d0288e762c2ddff176c9d660673c133ccafafc5baa0ab37ff2fe08b34b69 |
| 9941604011 | v52-longmemeval-head-tail-shard-3 | sha256:e6ad851f9c7a1cbffdb7278bcce05236a8d2a125bccb382b02616fd5de367a5d |
| 9941587508 | v52-longmemeval-head-tail-shard-4 | sha256:b40fbeaedd7eb134fed21276399b3d882307760964ec201afa35524f9bc69e49 |
| 9941639442 | v52-longmemeval-head-tail-causal-final | sha256:073aa74930afb6fae32cecc269e76f7ca6aaeb3afee3d248a725a8d23d7f4961 |

Manifest declares artifact_id `9941639442`, digest
`sha256:073aa74930afb6fae32cecc269e76f7ca6aaeb3afee3d248a725a8d23d7f4961` — **match**.
Exactly five shard artifacts, indices 0–4, each produced once.

## The CI hash-gate

Both Head/Tail workflows refuse to execute unless the preregistration bytes are exactly the
declared blob. From `.github/workflows/v52-locomo-head-tail-causal.yml`:

    test "$(git hash-object research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md)" = "0d34207be55a75194b585789c7139cbc8aeb264d"
    test "$(git hash-object research/v52/locomo_spectral_band_haar_causal.py)"      = "7c4140252fb7f846d617189925cdf534515743f4"
    test "$(git hash-object research/v52/locomo_sign_mechanism_replication.py)"     = "6700454915176854a55b0b5cf6ffe922a22e35f2"
    test "$(git hash-object research/v52/locomo_head_tail_two_subspace_causal.py)"  = "cb16d4136c6280875b7c5875ffd89f9fc01cb810"

The LongMemEval workflow gates the prereg blob and both LongMemEval sources identically.
This is a structural (not timestamp-based) guarantee that the executed code saw exactly the
preregistration bytes that are on the branch.

## Ancestry (structural, not timestamp-based)

- `6fe2374` (introduces the preregistration blob) is an ancestor of BOTH CI head SHAs
  (`5a0e8023`, `c30c36d4`) and of every commit that introduced a runner or an output.
- Both CI head SHAs are ancestors of the audit target `7799502b`.
- The preregistration file appears in exactly ONE commit in history and has exactly ONE
  blob id — it was never amended.
- Each runner appears in exactly one commit and was never modified after the outputs were
  produced.

## Limitation

The Actions artifacts carry `retention-days: 30` and expire **2026-10-04**. After that date
the CI-artifact leg of this provenance is no longer independently re-obtainable. It is not
load-bearing for this audit: the primary LoCoMo result was re-derived from scratch by the
auditor from the public frozen inputs (see `locomo_end_to_end_rerun_diff.txt`).
