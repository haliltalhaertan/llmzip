# V52 — HEAD/TAIL BOUNDARY LOCALIZATION: ZERO-TRUST COLD-START INDEPENDENT AUDIT

You are a **cold-start, session-independent auditor**. You did not produce this result, did not write
its preregistration, and must not treat any prior chat, commit message, checkpoint prose, provenance
manifest, or this handoff as evidence. They are **claims to be tested**.

Türkçe cevap verebilirsiniz; kararı İngilizce yazın, kısa Türkçe özet ekleyebilirsiniz.

---

## 1. Status and why this audit gates everything

The boundary-localization experiment is **already preregistered, sealed, triggered, executed,
persisted, backed up and checkpointed**. Do **not** re-run it, do not tune it, do not extend it.

Its status is `[PREREGISTERED RESULT — AUDIT PENDING]`, and a standing stop rule is in force: **no
finer boundary scan, adaptive localization, knee search, or new mechanism experiment may begin
before this audit closes.** Your verdict releases or holds the entire research line.

---

## 2. Exact audit target — bind to digests, not to branch names

```
repo    https://github.com/haliltalhaertan/llmzip
branch  research/v52-sign-mechanism-locomo-2026-09-04
commit  1a33ef0d1a2715257920201f7a3db8ab4677a007
```

**The repository default branch does NOT point at `main`.** Fetch by name or address commits
directly. Audit the commit above; if the branch has moved, audit this commit and say that it moved.

Verify each identity yourself before use. Do not proceed on any item that fails.

| Artifact | Declared git blob |
|---|---|
| Preregistration `research/v52/V52_CAUSAL_HEAD_TAIL_BOUNDARY_LOCALIZATION_PREREG_2026-09-04.md` | `b8acebedd49497a62ec637beabbcef6720460d15` |
| Pre-run seal `research/v52/V52_BOUNDARY_LOCALIZATION_PRERUN_SEAL_2026-09-04.json` | `cd3ad221ed66816a7b36c1edc746016ca73f9188` |
| Binding post-audit addendum `research/v52/V52_HEAD_TAIL_POST_AUDIT_INTERPRETATION_ADDENDUM_2026-09-04.md` | `456b3b51f49a0238cd936bc3f639988fb0d673af` |
| LoCoMo runner `research/v52/locomo_boundary_localization.py` | `0e66431449ad48b5f24049e0c05d65c917d8b893` |
| LongMemEval runner `research/v52/longmemeval_boundary_localization_shard.py` | `26c1fe89ca025747b47f3fa6daf80326a8864747` |
| LoCoMo workflow `.github/workflows/v52-locomo-boundary-localization.yml` | `1de6c8abad80976c51843592801b53b18a998541` |
| LongMemEval workflow `.github/workflows/v52-longmemeval-boundary-localization.yml` | `128987f7402a71160981f8f0cd28677e6c931710` |
| LoCoMo summary | `89c30a2a58fd638809477ded0d41b996f051c0f1` |
| LongMemEval summary | `2d6e3a4b5f5bfdfd2b3b93bbc068a4fcc685b954` |
| Checkpoint | `b5a8ed6542c78cde14f608b9b23b51eb6e34b917` |
| Provenance manifest | `2751b51aea4ce43fbe08ac3ddfbafdc534d56dd0` |

Content digests (SHA-256 of the file bytes):

```
locomo_boundary_per_question.csv.gz        87e7ae969403b0bb06efcd726d317fb08427cce7c29f221dd0e520ff8722fd1b
longmemeval_boundary_per_question.csv.gz   e73576039cb1c9b76ceb4b440148b90f3caa044ca082585d1a0f4d23ac08eaba
both *_boundary_random_partitions.json     232ffa300d832188ad0fc1fdb5fcd38d6ae7745922d5e8350080d845ed5bb791
```

The two random-partition files hashing **identically** is expected under the paired design, but
**verify that it is intentional and not a copy of the wrong file**: the partitions depend only on the
seeds and the 96 coordinate indices, so both datasets should legitimately produce the same file. Say
which of those two explanations the bytes support.

Trigger commit: `2edeef4a99cba20c94f3ec1c42c3da229f9d2452`.

---

## 3. The preregistered rule you must apply mechanically

For each dataset `D` and boundary `b`:

```
rho_b(D) = ( R_native(D) - R_b(D) ) / ( R_native(D) - R_fullhaar(D) )
```

Sufficiency: `rho_b <= 0.25`, where `rho_b` is the mean over the ten rotation seeds.

```
S_D       = { b in {16,24,32,48,64} : rho_b(D) <= 0.25 }
S_common  = S_LoCoMo  ∩  S_LongMemEval
```

**The set is the primary object.** No visual knee or elbow selection, no interpolated optimum, no
post-hoc finer search is authorized — check that none was performed.

Frozen boundaries `{16, 24, 32, 48, 64}`, where `b` = size of the leading (Head) block.
Rotation seeds `58001..58010`. Fresh matched-random-partition seeds `68001..68010`.
The spectral `B32` arm and the `RANDOM32` arm are designed to share the **same numerical Q32/Q64
matrices**; only coordinate membership differs.

---

## 4. Gates — establish each independently, from bytes or from execution

**A. Preregistration precedes outcome access.** Establish structurally, not from author-controlled
timestamps: which commit first introduced the preregistration blob, the runners, the workflows, the
seal and the trigger; which commits first introduced each outputs directory; and whether each result
file names the preregistration blob it followed. State explicitly whether any result could have
existed before the preregistration bytes did.

**B. Frozen boundaries are exactly `{16,24,32,48,64}`** in the executed code, and nothing else was
computed and discarded.

**C. Seeds are exactly** rotation `58001..58010` and partition `68001..68010`.

**D. No unreported boundaries, runs, retries or tuning.** Inspect the workflow history and the
runners for any additional arm, any re-dispatch, any conditional branch that could have been taken.

**E. Exact frozen source identities** for both datasets — dataset digests, byte counts, adapter
digests, cohort sizes (1535 / 470), audit-layer manifest.

**F. Native reproduction** against the frozen values.

**G. The spectral transformation construction for every boundary** — block-diagonal orthogonal, head
block first from one RNG stream, applied to archive and query alike after centering and before sign
quantization, orthogonal to tolerance.

**H. Matched Q32/Q64 equality** between the spectral `B32` arm and the `RANDOM32` arm. The summaries
declare `matched_q32_q64_max_abs_error = 0.0`; re-derive it.

**I. Random partition cardinality, disjointness, exhaustiveness and ordering** for all ten partition
seeds on both datasets.

**J. Per-question completeness and duplication.** Declared: LoCoMo `92100/92100` rows, LongMemEval
`28200/28200` rows over `470/470` unique primary questions across ten deterministic shards. Check row
counts, uniqueness, and that no question appears in two shards or none.

**K. Reconstruct every seed-level `R@3` and `rho` directly from the persisted per-question
outputs** — not from the summary JSONs, and not from the per-seed CSVs. This stage persisted
per-question records precisely so that this is possible without re-running the representation
pipeline. If you cannot do it, mark the gate `NOT ESTABLISHED` rather than passing it on inspection.

**L. Reconstruct `S_LoCoMo`, `S_LongMemEval`, `S_common`** from your own reconstruction.

**M. Confirm the mechanical verdict follows** from the preregistered rules, with no threshold, seed
or estimand altered after outcome access.

**N. LongMemEval deterministic sharding semantics.** Establish whether the shard partition is
disjoint and exhaustive, whether per-question tie-break randomness depends on shard membership or on
a shard-invariant global index, and whether the aggregate is order-independent. Note that the summary
claims `DETERMINISTIC_SHARDED_SEMANTICS_INVARIANT` rather than bit-exactness — judge whether the
wording matches what is demonstrable.

**O. Uncertainty and dispersion disclosures.** Per-arm `sample_sd`, `se`, `rho_min`, `rho_max` and
`sign_inverting_rotation_seeds` are declared. Verify them, and verify that the individually
threshold-exceeding seeds are disclosed rather than hidden — the checkpoint should name at minimum
LongMemEval `B32` seed `58004` and `B48` seed `58009`.

**P. Historical disclosure.** The earlier Head/Tail LoCoMo panel contained seed `56001` where the
loss changed sign (`rho_2 ≈ -0.067`). Verify that this remains disclosed and was not quietly dropped
when the new panel showed no inversions.

**Q. Interpretation ceiling.** Verify the reported claim does not exceed: sufficiency is not
necessity; a tested grid is not a global optimum; two datasets under one shared pipeline are not
independent methodological replication; and nothing here transfers to Task 4F1. The mandatory paired
labels are `[PC32-LOCALIZED SUFFICIENCY LEAD — ON TESTED GRID]` **and**
`[BOUNDARY-SET HETEROGENEITY PRESENT]`; check both are reported together wherever the result appears.

**R. Task 4F1 boundary.** Verify that no Task 4F1 execution, outcome, authorization or HMAC material
was touched anywhere in this stage.

**S. Strongest argument against — required, not optional.** Construct the best case that the
localization result is an artifact: of the ten-seed mean as an estimator, of the coarse grid, of the
inherited Full-Haar denominator whose own sampling uncertainty this package does not quantify, of the
shared pipeline, or of the interpretation. Then say whether that case defeats the result, weakens it,
or fails.

---

## 5. Absolute prohibitions

- Never invoke a Task 4F1 execution candidate with `--mode run` or `--mode finalize`; never call
  `run_archives`, `evaluate_archive` or `finalize_results`; never set `V52_T4F1_AUTH_HMAC_KEY_HEX`
  or construct an authorization; never access any Task 4F1 (BEAM) retrieval outcome. Task 4F1 is
  `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`. LoCoMo and LongMemEval are a
  different track and **are** in scope.
- Do not modify the research branch, any frozen checkpoint, seal, manifest, output or the
  preregistration. You audit; you do not edit. Corrections are additive addenda authored by others.
- Do not run a finer boundary scan, a knee search, or any new mechanism experiment. Re-executing the
  **existing** frozen runners for verification is in scope; new arms are not.
- Do not build a generalized prose scanner.

---

## 6. Verdict

Return exactly one, and state whether each finding is **established** or merely **not falsified**:

- `AUDIT PASS — BOUNDARY LOCALIZATION INDEPENDENTLY SUPPORTED`
- `AUDIT PASS WITH CAVEATS` — state the exact narrowed claim you would accept
- `AUDIT BLOCKED` — name each defect with file and line, or the reproduction command
- `AUDIT INCONCLUSIVE` — say exactly what you could not obtain

## 7. Output — push it

```
branch  audit/v52-boundary-localization-independent-2026-09-04
files   audit_v52_boundary_localization_independent_2026_09_04/AUDIT_REPORT.md
        audit_v52_boundary_localization_independent_2026_09_04/GATE_TABLE.md   (A-S, PASS / FAIL / NOT ESTABLISHED, evidence path each)
        audit_v52_boundary_localization_independent_2026_09_04/AUDIT_HASHES.json
        evidence/ and scripts/ for everything you computed or re-executed
        a .sha256 sidecar for the report
```

State the digests **you measured yourself**, and include an explicit outcome-boundary declaration.

---

## 8. Known-open items you should be aware of, and must not treat as settled

- An earlier stage, the matched random-partition null control at commit
  `410bcf59e29c64096bfb988d6d95e89658f50f6e`, carries its own audit dispatch record but **no auditor
  branch exists for it**. Its LongMemEval position result was never independently audited. The
  boundary-localization stage repeats matched random partitions on both datasets with fresh seeds; you
  may state whether that supersedes the older stage, but you are not required to audit it.
- The only previously audited random-partition control is the LoCoMo one supplied by the Head/Tail
  auditor itself.
- The Full-Haar denominator is inherited and its sampling uncertainty is not quantified anywhere in
  this package.

An honest `AUDIT BLOCKED` is worth more to this program than a `PASS` that was easier to write.
