# Acceptance record — bound seeds and bound cohort/mapping manifests

**Separate acceptance record.** No `PROPOSED_*` file is modified in place. What binds them is this
document plus the ledger entry that records it; the files themselves stay byte-unchanged, and their
own sidecars still say `PROPOSED` because that is what they said when they were written.

This acceptance is **identity and mapping scope only**. It is not a statement about the correctness of
the experiment, not a seal, and not authorization to execute on real data.

---

## 1. Seed binding — the clarification

The earlier phrasing, "seeds bound with their sampling rules, not just their values", was ambiguous. It
should not be read as *the rules are bound and the values are not*. **Both are bound.** Precisely:

| what | where it is bound | commit | path | sha256 |
|---|---|---|---|---|
| the three seed **values**, and the rules | `CONFIGURATION_IDENTITY_2026-09-08.md` §2 | `e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf` | `drafts/v52/membership_runner_v1_2026_09_08/CONFIGURATION_IDENTITY_2026-09-08.md` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` |
| the same values as a machine-readable file | `PROPOSED_bootstrap_seeds.json` | `6911a03af68cb48a5090690b05acec59a67ce211` | `drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_bootstrap_seeds.json` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` |

So the values were **already** in a hash-bound file at acceptance time: the configuration identity
document carries them in its text and it is itself hash-recorded in ledger entry **L-074**. Nothing
needed to be re-chosen and nothing was.

The JSON file still carries `binding_status: "PROPOSED"` in its own text. That word describes its state
when it was written; this record and L-074 are what make its values accepted. It is **not** edited, so
its hash keeps resolving.

**The accepted values, restated for the record — no new value is chosen:**

| benchmark | scheme | seed | replicates |
|---|---|---|---|
| LoCoMo | question | `52001107` | 10000 |
| LoCoMo | cluster | `52001207` | 10000 |
| LongMemEval | question | `52002107` | 10000 |

No seed exists for LongMemEval × cluster; R2 line 141 defines no such scheme.

**Bound with them, and equally binding:** `numpy.random.Generator` over **PCG64** via
`default_rng(seed)`; one generator per `(benchmark, scheme)`, seeded once and never reseeded mid-run;
question scheme — one `rng.integers(0, n, size=n)` per replicate applied identically to all six arms
and all ten rotation seeds, the seed panel fixed and never resampled (R1 §6); cluster scheme, LoCoMo
only — one `rng.integers(0, n_clusters, size=n_clusters)` per replicate, conversations drawn with
replacement, each contributing **all** of its questions, multiplicity preserved, the mean divided by
the **total number of selected question slots** (acceptance record §4); percentiles 2.5 and 97.5.

## 2. Manifest acceptance — the fixed cohort/mapping contract

Both hashes were **recomputed from raw Git objects** at acceptance time
(`git cat-file blob <commit>:<path> | sha256sum`), not copied forward from an earlier note.

| benchmark | file | commit | sha256 (re-verified from the raw blob) |
|---|---|---|---|
| LoCoMo | `drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json` | `6911a03af68cb48a5090690b05acec59a67ce211` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` |
| LongMemEval | `drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` | `e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` |

These two are now **the fixed cohort and mapping contract** of this study: LoCoMo, 1535 questions in 10
conversations; LongMemEval, a 470-question cohort in one sentinel cluster.

### LongMemEval v1 → v2 precedence, stated plainly

- **v2 (`d5b8ed69…`) is the accepted manifest. It supersedes v1 for every purpose.**
- **v1 (`bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886`) is superseded and must not
  be loaded by the ingestion or the runner.** It is kept byte-unchanged only so its hash keeps
  resolving in L-072 and L-073.
- The **only** difference is `source_id` and `source_sha256`: v1 carried the placeholder
  `UNRESOLVED-see-BINDING_PROPOSAL-section-1`; v2 carries the raw-file identity
  `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`, verified in the narrow
  data-identity task. **The 470 question ids and the sentinel cluster are identical in both.**

### The scope of this acceptance

It fixes **which questions exist, which conversation each belongs to, and which source file is
authoritative**. It says nothing about whether the design is right, whether the estimand answers the
question, or whether any result is valid — and it does not permit a run.

### What the sentinel cluster still is

A **technical placeholder** for LongMemEval: not real conversation membership, and not a dependency
component recomputed at this stage. The conversation-cluster bootstrap stays refused for LongMemEval.

## 3. Environment — a correction, made additively

`CONFIGURATION_IDENTITY_2026-09-08.md` and L-074 state that `threadpoolctl.threadpool_info()` returns
an **empty list** in this venv. **That statement is wrong as written, and the cause was my probe, not
the environment**: I called it in a process that had not imported NumPy, so no BLAS library was loaded
and there was no pool to report.

With NumPy imported first it reports **one** pool — `libscipy_openblas`, OpenBLAS 0.3.30, `pthreads`,
Haswell — at **`num_threads: 1`**. The control (no NumPy import) still returns `[]`, which is what
identifies the cause. Both are recorded in `evidence/thread_policy_observation.json`.

The earlier documents are **not edited**; this is the correction, and the distinction it was meant to
protect stands and is sharpened:

| statement | status |
|---|---|
| single-threaded execution is **requested** by the four environment variables | true, and that is all the variables establish |
| the loaded BLAS pool is **configured** at `num_threads = 1` | **observed** via threadpoolctl after NumPy import |
| single-threaded execution was **measured at runtime** | **not established.** Neither of the above counts executed threads, and Python-level thread counting cannot see native OpenBLAS workers |

None of these three may be reported as either of the others.
