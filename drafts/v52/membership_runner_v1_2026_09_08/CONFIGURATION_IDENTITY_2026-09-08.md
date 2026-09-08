# Configuration identity — V52 membership-under-scaling follow-up experiment

**Accepted by the Head Researcher on 2026-09-08** for this follow-up study only. This acceptance is
**not** a seal and **not** authorization to run the experiment on real data.

The **Task 4F1 lock is unchanged**: `task4f1_execution_candidate_v7_2026_09_03/DEPENDENCY_LOCK.txt`
is neither edited nor inherited by this study.

---

## 1. Environment lock — accepted

```
V52 membership-under-scaling follow-up experiment — environment lock
Python==3.13.15
numpy==2.3.5
scipy==1.17.0
scikit-learn==1.8.0
pandas==2.2.3
OMP_NUM_THREADS=1  MKL_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1  NUMEXPR_NUM_THREADS=1
PYTHONHASHSEED=0
UTF-8 source/data decoding required
Thread policy: one process; one worker; no implicit BLAS parallelism
```

### Everything else the environment actually carries, recorded rather than left implicit

Measured from the interpreter itself; the machine-readable copy is
`evidence/configuration_environment_record.json`.

**Full dependency freeze (11 entries)** — the five locked packages plus their transitive closure:

```
cloudpickle==3.1.2      joblib==1.6.0            numpy==2.3.5
pandas==2.2.3           python-dateutil==2.9.0.post0
pytz==2026.3.post1      scikit-learn==1.8.0      scipy==1.17.0
six==1.17.0             threadpoolctl==3.6.0     tzdata==2026.3
```

| | value |
|---|---|
| interpreter | `work/locomo_reproduction_tmp_20260907/venv/Scripts/python.exe` |
| platform | `Windows-10-10.0.19045-SP0`, `AMD64`, 64-bit |
| Python build / compiler | `tags/v3.13.15:4061bc4, Aug 5 2026 13:05:39` — `MSC v.1944 64 bit (AMD64)` |
| BLAS | `scipy-openblas` 0.3.30 — `OpenBLAS 0.3.30 USE64BITINT DYNAMIC_ARCH NO_AFFINITY Haswell MAX_THREADS=24` |
| LAPACK | `scipy-openblas` 0.3.30 |

`threadpoolctl.threadpool_info()` returns an **empty list** in this venv. That is recorded as an
observation, not smoothed over: thread counts here are pinned by the four environment variables
above, not by runtime introspection, and the BLAS identity comes from NumPy's own build config.

**Unlisted-dependency policy.** If anything outside this lock and this freeze is ever required, it is
**not to be chosen silently** — it comes back as a lock amendment for approval.

## 2. Bootstrap seeds — accepted, and what is bound with them

| benchmark | scheme | seed | replicates |
|---|---|---|---|
| LoCoMo | question | `52001107` | 10000 |
| LoCoMo | cluster | `52001207` | 10000 |
| LongMemEval | question | `52002107` | 10000 |

**No seed exists for LongMemEval × cluster.** R2 line 141 defines no conversation-cluster bootstrap
for LongMemEval and the runner refuses that combination.

### The generator and the sampling rules, bound explicitly

- **Algorithm:** `numpy.random.Generator` over the **PCG64** bit generator, constructed as
  `numpy.random.default_rng(seed)`. One generator per `(benchmark, scheme)`, seeded once from the
  value above and never reseeded mid-run.
- **Question scheme:** per replicate, one call `rng.integers(0, n_questions, size=n_questions)`.
  That single index set is applied identically to **all six arms** and to **all ten rotation seeds**,
  so every pairing the design establishes survives inside the replicate (R1 §6). The seed panel is
  **fixed and never resampled**.
- **Cluster scheme (LoCoMo only):** per replicate, one call
  `rng.integers(0, n_clusters, size=n_clusters)` — conversations drawn **with replacement**; each
  drawn conversation contributes **all** of its questions; **multiplicity preserved**; the mean
  divides by the **total number of selected question slots**, not by distinct questions and not by
  clusters; the same selection applied to all six arms and the fixed seed panel (acceptance record §4).
- **Interval:** percentiles 2.5 and 97.5. **Replicates:** 10000.
- Both constants come from the closed v3 core (`BOOTSTRAP_REPLICATES`, `PERCENTILES`); the runner does
  not redefine them.

### How the values were fixed

By an announced arithmetic rule, before any real result exists and with no reference to any outcome:
`52000000 + 1000·benchmark + 100·scheme + 7`, with LoCoMo=1, LongMemEval=2, question=1, cluster=2, and
`7` tagging the fixed ten-seed rotation panel. Machine-checked against all three values. No value was
tried, compared or selected against a computed quantity.

**What acceptance does and does not settle.** These seeds are now part of *this* configuration
identity, which is what makes them preregistered rather than merely written to a file before a run.
`freeze_bootstrap_seed` still enforces write-once and no-reuse-across-schemes at execution time; it
was never the thing that made them preregistered.

## 3. Wording limits that apply to every later report

These are constraints on claims, not on code.

1. **The identical RNG draws across the two candidate environments show only that the tested draws
   matched.** They were measured for `default_rng(seed).integers(0, n, size=n)` at seeds 424242 /
   515151 / 606060 / 717171 and `n ∈ {1535, 470, 10}`. That is **not** evidence that the two
   environments would produce the same results or the same intervals in general, and it must never be
   reported as such. It says nothing at all about the representation pipeline.
2. **The LoCoMo cross-record agreement is not corpus-independent verification.** Two committed records
   agreeing catches a transcription or pipeline error; both descend from the same producer labelling.
   Independent verification against the raw source is a separate thing, and it was done separately —
   see `DATA_IDENTITY_REPORT_2026-09-08.md`. The two must not be merged into one claim.
3. **The LongMemEval sentinel cluster is a technical placeholder.** It is not real conversation
   membership and not a dependency component recomputed at this stage. The conversation-cluster
   bootstrap stays refused for LongMemEval.

## 4. What this document does not authorize

No sealing. No run or finalize on real data. No real ingestion path — `run_on_real_corpus` remains a
refusing stub. No independent runner review yet. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
