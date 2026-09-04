# V52 Head/Tail Spectral Boundary Localization — Cross-Dataset Checkpoint

Date: 2026-09-04
Status: `[PREREGISTERED RESULT — AUDIT PENDING]`
Research branch: `research/v52-sign-mechanism-locomo-2026-09-04`

Preregistration Git blob: `b8acebedd49497a62ec637beabbcef6720460d15`
Post-audit narrowing Git blob: `456b3b51f49a0238cd936bc3f639988fb0d673af`
Pre-run seal Git blob: `cd3ad221ed66816a7b36c1edc746016ca73f9188`
Trigger commit: `2edeef4a99cba20c94f3ec1c42c3da229f9d2452`

This checkpoint applies the preregistered boundary-set decision rules mechanically. It does not choose a visual knee or optimize a boundary after outcome access.

## 1. Mechanical verdict

LoCoMo:
- `S_LoCoMo = {32}`
- P1 (`rho_32 <= 0.25`): `PASS`
- P2 (`Delta32 >= 0.25`): `[SPECTRAL POSITION CONFIRMED UNDER NEW PANEL]`

LongMemEval:
- `S_LongMemEval = {32,48}`
- P1: `PASS`
- P2: `[SPECTRAL POSITION CONFIRMED UNDER NEW PANEL]`

Common set:

`S_common = {32}`

Therefore the preregistered L1 rule fires:

**`[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]`**

The preregistered heterogeneity rule also fires because the dataset-level sufficiency sets differ:

**`[BOUNDARY-SET HETEROGENEITY PRESENT]`**

These labels must be reported together.

The result means that among the five preregistered contiguous splits `{16,24,32,48,64}`, the only split jointly sufficient across both frozen datasets is 32/64. It does **not** establish that coordinate 32 is globally optimal, mathematically unique, necessary, or universally causal. LongMemEval also admits 48/48 under the frozen mean-rho criterion.

## 2. Primary summaries

### LoCoMo

| Arm | Mean R@3 | mean rho | conditional SE(rho) | per-seed rho range | sufficient? |
|---|---:|---:|---:|---:|---|
| 16/80 | 0.155199 | 0.823 | 0.012 | 0.749–0.869 | no |
| 24/72 | 0.184483 | 0.527 | 0.020 | 0.417–0.641 | no |
| **32/64** | **0.228403** | **0.082** | **0.018** | **0.009–0.207** | **yes** |
| 48/48 | 0.206556 | 0.303 | 0.015 | 0.214–0.381 | no |
| 64/32 | 0.184078 | 0.531 | 0.023 | 0.453–0.662 | no |
| matched random 32/64 | 0.143917 | 0.937 | 0.014 | 0.870–0.986 | null |

- Native R@3: `0.23654714666441054`
- Frozen Full-Haar R@3: `0.13770827054136`
- `Delta32 = rho_random32 - rho_32 ≈ 0.855`
- no new-panel seed inverted the sign of `L_b`
- previous audited Head/Tail panel's LoCoMo seed `56001` sign inversion remains a binding historical disclosure and is not erased by this new panel.

### LongMemEval

| Arm | Mean R@3 | mean rho | conditional SE(rho) | per-seed rho range | sufficient? |
|---|---:|---:|---:|---:|---|
| 16/80 | 0.413798 | 0.805 | 0.020 | 0.693–0.922 | no |
| 24/72 | 0.450162 | 0.577 | 0.021 | 0.477–0.677 | no |
| **32/64** | **0.516194** | **0.162** | **0.020** | **0.066–0.267** | **yes** |
| **48/48** | **0.511099** | **0.194** | **0.016** | **0.132–0.302** | **yes** |
| 64/32 | 0.484640 | 0.360 | 0.030 | 0.193–0.476 | no |
| matched random 32/64 | 0.384163 | 0.991 | 0.023 | 0.880–1.092 | null |

- Native R@3: `0.5419751773049645`; frozen reference `0.5419751773049646`; reproduction error `1.11e-16`
- Frozen Full-Haar R@3: `0.38271666666667`
- `Delta32 ≈ 0.829`
- no new-panel seed inverted the sign of `L_b`
- individual seed 58004 for B32 has `rho≈0.267`; individual seed 58009 for B48 has `rho≈0.302`. The preregistered sufficiency object is based on the ten-seed mean, so these do not alter `S_LongMemEval`, but they are retained as dispersion evidence.

The displayed standard errors are conditional on the inherited frozen Full-Haar denominator. This experiment does not identify uncertainty in that denominator.

## 3. All ten per-seed rho values

Seed order in every vector is:
`[58001,58002,58003,58004,58005,58006,58007,58008,58009,58010]`.

### LoCoMo

- 16/80: `[0.822863,0.864752,0.748501,0.868507,0.833294,0.777122,0.845445,0.830583,0.832379,0.806935]`
- 24/72: `[0.468720,0.525483,0.488306,0.640821,0.556861,0.530897,0.603350,0.528179,0.507988,0.416979]`
- 32/64: `[0.081606,0.089542,0.021330,0.142179,0.009019,0.073834,0.049200,0.207165,0.058024,0.092060]`
- 48/48: `[0.293031,0.338253,0.325792,0.380858,0.326385,0.248183,0.213671,0.303156,0.284119,0.320925]`
- 64/32: `[0.489123,0.517933,0.533815,0.658512,0.504551,0.661956,0.452594,0.487534,0.524247,0.478242]`
- random 32/64: `[0.986498,0.891118,0.937158,0.932855,0.936387,0.983548,0.972422,0.977939,0.883979,0.869914]`

Authoritative exact-float table:
`research/v52/locomo_boundary_outputs/locomo_boundary_seed_results.csv`
Git blob: `f9e572328df0da3df7bf7068d7f6fe0c579957a3`

### LongMemEval

- 16/80: `[0.922137,0.794729,0.762565,0.780813,0.813099,0.826815,0.753815,0.693039,0.873897,0.827494]`
- 24/72: `[0.567824,0.605109,0.487699,0.476944,0.677330,0.559096,0.654229,0.531530,0.618046,0.587207]`
- 32/64: `[0.130080,0.128632,0.236524,0.266505,0.155552,0.174401,0.160718,0.209682,0.065841,0.090891]`
- 48/48: `[0.154662,0.180658,0.186135,0.141079,0.174022,0.132440,0.199217,0.247557,0.302087,0.220860]`
- 64/32: `[0.475987,0.284341,0.355860,0.461926,0.423650,0.415645,0.239508,0.346152,0.404033,0.193038]`
- random 32/64: `[1.051682,0.904357,1.004266,1.056915,0.984939,0.879953,1.091706,0.906706,0.992621,1.036051]`

Authoritative exact-float table:
`research/v52/longmemeval_boundary_outputs/longmemeval_boundary_seed_results.csv`
Git blob: `481287b2509bd38e0c70aafc0a25fb241e05d06d`

## 4. Fresh matched random-partition control

Rotation seeds:
`58001..58010`

Partition seeds:
`68001..68010`

For each paired seed, the spectral-32 and random-32 arms used exactly the same numeric `Q32` and `Q64`; only the coordinate membership/order differed. The runtime equality check gave max absolute Q difference `0.0` on both datasets.

The exact ten `S32` / `T64` arrays are persisted verbatim in:

- `research/v52/locomo_boundary_outputs/locomo_boundary_random_partitions.json`
- `research/v52/longmemeval_boundary_outputs/longmemeval_boundary_random_partitions.json`

Both files have SHA-256:
`232ffa300d832188ad0fc1fdb5fcd38d6ae7745922d5e8350080d845ed5bb791`

Because the exact partition file is hash-bound and common to both result packages, it is part of this checkpoint package by reference rather than retyped into this Markdown. Cardinality, uniqueness, disjointness, exhaustiveness, and 0..95 range checks passed before interpretation.

Fresh position-dependence contrasts:

- LoCoMo: `Delta32 ≈ 0.855` -> `[SPECTRAL POSITION CONFIRMED UNDER NEW PANEL]`
- LongMemEval: `Delta32 ≈ 0.829` -> `[SPECTRAL POSITION CONFIRMED UNDER NEW PANEL]`

Thus the auditor-supplied LoCoMo null result is independently replicated by a new seed panel, and the corresponding position-dependence control is now also observed on LongMemEval. The LongMemEval result is researcher-produced in this stage and is audit-pending.

## 5. Integrity and auditability controls

LoCoMo:
- evidence-valid questions: `1535`
- Native reproduction error: `0.0`
- signed-permutation exact Hamming: `PASS`
- continuous norm max abs error: `5.55e-16`
- continuous dot max abs error: `2.00e-15`
- matched Q32/Q64 max abs error: `0.0`
- per-question records: `92100/92100`
- per-question gzip SHA-256: `87e7ae969403b0bb06efcd726d317fb08427cce7c29f221dd0e520ff8722fd1b`

LongMemEval:
- primary questions: `470/470 unique`
- deterministic shard count: `10/10`
- Native reproduction error: `1.11e-16`
- signed-permutation exact Hamming: `PASS`
- continuous norm max abs error: `6.66e-16`
- continuous dot max abs error: `9.99e-16`
- matched Q32/Q64 max abs error: `0.0`
- per-question records: `28200/28200`
- per-question gzip SHA-256: `e73576039cb1c9b76ceb4b440148b90f3caa044ca082585d1a0f4d23ac08eaba`

LongMemEval is described as deterministic sharding with shard-invariant per-question semantics and deterministic sorted aggregation. No generic bitwise-exactness claim is made.

## 6. Immutable execution provenance

LoCoMo:
- Actions run: `33916946302`
- immutable artifact id: `9953521863`
- artifact digest: `sha256:da4e7a47d8b5491e956914a2216d187ea9ded49972eaa97a5d8e00b126e7cced`
- Drive artifact file id: `1suAZoTuYsaah_oWf1fB9vPxQ2KPg92tr`
- summary Git blob: `89c30a2a58fd638809477ded0d41b996f051c0f1`

LongMemEval:
- Actions run: `33916946226`
- deterministic shards: `10`
- immutable aggregate artifact id: `9953631412`
- artifact digest: `sha256:810aff5d4cb5e5c6b2851873555967b9fbbf4867e810bdf3eaf04cad455c66d1`
- Drive artifact file id: `1qLSdVsbUb8Eo5D8YgmGdkk3gx0w_vufQ`
- summary Git blob: `2d6e3a4b5f5bfdfd2b3b93bbc068a4fcc685b954`

Pre-run package:
- preregistration Git blob: `b8acebedd49497a62ec637beabbcef6720460d15`
- audit-narrowing addendum Git blob: `456b3b51f49a0238cd936bc3f639988fb0d673af`
- pre-run seal Git blob: `cd3ad221ed66816a7b36c1edc746016ca73f9188`
- LoCoMo runner Git blob: `0e66431449ad48b5f24049e0c05d65c917d8b893`
- LongMemEval runner Git blob: `26c1fe89ca025747b47f3fa6daf80326a8864747`
- LoCoMo workflow Git blob: `1de6c8abad80976c51843592801b53b18a998541`
- LongMemEval workflow Git blob: `128987f7402a71160981f8f0cd28677e6c931710`

The preregistration and pre-run seal were copied to Google Drive before the trigger commit. Task 4F1 execution state and outcomes were not touched.

## 7. Strongest defensible interpretation

Under one shared SIGN96/SVD/Hamming retrieval pipeline, on two frozen memory-retrieval datasets, the preservation of retrieval advantage is strongly sensitive to where the contiguous spectral boundary is placed.

On the preregistered coarse grid, 32/64 is the only boundary sufficient on both datasets. This sharpens the prior Head/Tail mechanism lead from a generic two-subspace statement to a **PC32-localized sufficiency lead on the tested grid**.

However:

- LongMemEval also admits 48/48, so dataset-level boundary heterogeneity is real;
- the grid is coarse and does not identify whether the true transition is at 29, 31, 33, 40, or another untested coordinate;
- sufficiency does not prove necessity;
- the two datasets share the same representation/estimation pipeline and are not independent methodological replications;
- the frozen Full-Haar denominator's own uncertainty is not quantified here;
- no universal, production, neural-axis, or Task 4F1 claim is licensed.

## 8. Audit state and stop rule

This localization result is **audit-pending**.

It is load-bearing because it changes the mechanism claim from `Head32/Tail64 is sufficient` to the narrower tested-grid claim that `32/64 is the only jointly sufficient preregistered boundary` while also exposing LongMemEval's 48/48 heterogeneity.

No finer boundary scan, adaptive localization, knee search, or new mechanism experiment should begin until an independent audit adjudicates this checkpoint and its per-question reconstruction package.
