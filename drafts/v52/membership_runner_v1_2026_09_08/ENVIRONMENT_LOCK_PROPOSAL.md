# Environment lock — the binding one does not exist; this is a PROPOSAL for approval

**Nothing here is a final lock.** No package was installed, no interpreter was changed, and no
existing lock file was edited.

## 1. Which lock is binding for this experiment? — none

I searched the four normative documents of this experiment for any environment, interpreter or
dependency requirement. **There is none.** Not a Python version, not a NumPy version, not a
determinism or thread policy.

| document | commit | sha256 | environment clause |
|---|---|---|---|
| `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` | `9b4af5949c4dc0e5054f8f522f1952ec47513f8f` | `a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71` | **none** |
| `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R2_2026-09-07.md` | `16019724564b5ac8db4a4d2d8bb08f98feb45c09` | `39cbfcea3a93307d582f9765529d6d99c09d0204706befa6470b8b932f451669` | **none** |
| `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R1_2026-09-07.md` | `2eadc41b7133aa5c78e767ce8f1766beb48b4404` | `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391` | **none** |
| `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_PREREG_DRAFT_2026-09-07.md` | `56c294162412482ca85e77ea991a20eb22f65dac` | `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399` | **none** |

The acceptance record's §7 authorizes "preparation of runners in a separate implementation namespace,
and unit and negative tests **on synthetic data only**" and lists what the implementation must do —
coverage, refusal of bad records, explicit units and weights, no silent overwrite, synthetic
demonstration of pairing and multiplicity, real-data execution off by default. It says nothing about
an execution environment. **So the environment for this experiment is not yet bound.**

## 2. The Task 4F1 V7 lock was NOT applied

`task4f1_execution_candidate_v7_2026_09_03/DEPENDENCY_LOCK.txt` reads:

```
Python==3.12.13
numpy==2.3.2
scipy==1.16.1
scikit-learn==1.7.1
psutil==7.0.0
OMP_NUM_THREADS=1  MKL_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1  NUMEXPR_NUM_THREADS=1
PYTHONHASHSEED=0
UTF-8 source/data decoding required
Thread policy: one process; one worker; no implicit BLAS parallelism
```

That lock belongs to **Task 4F1**, a different, sealed and blocked task. It is **not** carried over to
this follow-up experiment automatically, and it was not treated as binding here. It is quoted only as
the nearest existing precedent, which is what a proposal should be measured against.

## 3. What was actually used, and how it is labelled

`evidence/environment_record.json`, measured not assumed:

| package | Task 4F1 V7 lock | environment used here |
|---|---|---|
| Python | 3.12.13 | **3.12.14** ← differs |
| numpy | 2.3.2 | 2.3.2 |
| scipy | 1.16.1 | 1.16.1 |
| scikit-learn | 1.7.1 | 1.7.1 |
| psutil | 7.0.0 | 7.0.0 |

Interpreter: `work/llmzip/remediation_v52_t4f0_env_2026_08_31/Scripts/python.exe`, on
Windows-10-10.0.19045. Run with `PYTHONHASHSEED=0` and all four thread variables at 1.

Both suites were run there and both pass. **Those results are labelled
`DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS`.** They are evidence that the code behaves as described in a
development environment. They are **not** evidence of lock conformance, not a seal, and not
authorization to run on real data. Full environment verification stays **OPEN**.

## 4. Proposal — requires Head Researcher approval; not adopted here

I am not selecting the final lock. Two options, and the trade-off between them:

**Option A — adopt the Task 4F1 V7 stack verbatim, including Python 3.12.13.**
Maximum comparability with the sealed lineage. Costs a fresh interpreter build or download, since
3.12.13 is not present on this machine; the existing environment cannot simply be renamed into
compliance.

**Option B — bind Python `3.12.14` with the same four packages and the same thread and hash policy.**
Uses the environment that exists, so no installation is needed. The divergence from the 4F1 lineage is
one CPython patch release, with the numerical stack identical. If comparability with the sealed
lineage matters for this experiment, that is a scientific judgement, not an implementation one, and it
is yours.

Either way the lock should state, as the V7 lock does: exact package versions, the four thread
variables, `PYTHONHASHSEED=0`, UTF-8 decoding, and the one-process/one-worker policy.

**Until a lock is approved, no run on real data may be presented as environment-conformant.**
