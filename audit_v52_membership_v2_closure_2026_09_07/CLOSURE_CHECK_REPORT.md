# Closure check — V52 Membership Under Scaling, candidate v2

Cold-start independent closure checker. No prior context; findings rest on repository bytes and on
execution performed here.

**Verdict: `CLOSURE PASS WITH FINDINGS`.**

Both blockers (F-1, F-2) are genuinely closed. The corrections introduce one REAL new finding and
three cosmetic ones. Nothing found here re-opens a blocker, and nothing found here authorizes the
experiment.

---

## 0. Scope, limits and environment

Checked: the corrections listed in the commission and the core behaviours they could affect. **Not**
re-run: the full implementation review, earlier stages, the design, any literature scan.

Observed absolutely: synthetic data only; no corpus or model access of any kind; no real
retrieval/fitting/ranking; no real-data bootstrap; no pilot; no sealing; no HMAC; no `run` /
`finalize`; no Task 4F1 action. No corpus-bound runner was written or reviewed — it does not exist,
and **closing the core does not authorize the experiment**.

| item | value |
|---|---|
| Python | 3.14.3 (CPython, win32) |
| NumPy | 2.5.2 |
| checker branch | `audit/v52-membership-v2-closure-2026-09-07`, based on `main` @ `3279b28c991095f9339fd22d1d99782a4582b613` |
| candidate v2 | `impl/v52-membership-under-scaling-v2-2026-09-07` @ `8179ce31afc8ec9a2469c801a0a5e022b4494518` |
| candidate v1 | `impl/v52-membership-under-scaling-2026-09-07` @ `a6d70ff63ce44ea0f066a075853c9e93dec53122` |
| review | `audit/v52-membership-impl-review-2026-09-07` @ `68819424765ed3da89377c89980d7e42546bfe02` |

**Hash discipline.** Every sha256 in this report is of the **raw Git blob**
(`git show <commit>:<path> | sha256sum`), never of a Windows checkout. A checked-out file differs
from its blob by line endings; no such artefact is reported as a mismatch.

Blob hashes verified against the commission:

| file | expected | observed | |
|---|---|---|---|
| v2 `membership_scaling_core.py` | `60141d05f228…0db0a1e1` | `60141d05f2285d268a88d98344770c8cb5d166168a6fa29371a1ea330db0a1e1` | MATCH |
| v2 `test_membership_scaling_core.py` | `a0e9cc271916…9ce3ec12` | `a0e9cc27191e3c7a9683cbd94007c17c9c6666eb8bea1a78f40e7ec09ce3ec12` | MATCH |
| v1 `membership_scaling_core.py` | `707e166c80d9…0731a00` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` | MATCH |

**Method.** Every check I rely on is paired with a negative control that I show failing. Where a
control of mine came out degenerate, I say so rather than claiming the check passed.

---

## 1. Findings table

Status of each finding raised by the review at `68819424`.

| id | severity (review) | closure status | basis |
|---|---|---|---|
| **F-1** | BLOCKER | **CLOSED** | `_cv` is `values.std(ddof=0) / mean`; AST shows the only numeric constants in the body are `0.0`/`0` and the only division is `values.std(ddof=0) / mean` — no epsilon. Zero mean returns `NaN` explicitly and is tested on an all-zero archive. On the review's own 20-dead-coordinate fixture the core now reports `cv = 0.512989` (the review's "true CV") and publishes the v1 quantity `0.406116` under the honest name `sd_sigma_after`. Both CVs recomputed independently here and matched to `< 1e-15`. |
| **F-2** | BLOCKER | **CLOSED** (two narrow residuals, see NEW-4/NEW-5) | `build_clusters` validates before grouping and proves the partition. 33 break attempts run here: `None`, python and numpy `NaN`, python and numpy floats, `bool`, `np.bool_`, tuple, list, bytes, `Decimal`, 0-d and 1-element `ndarray`, and mixed kinds are all rejected with named `DesignViolation`s; numpy int8/32/64/uint8 scalars, `np.str_`, an `np.int64` label vector, a generator, `2**200` ints, `np.int64` max, one cluster, and one cluster per question are all accepted correctly. 300 random label vectors: every question in exactly one cluster, 0 violations. "Cluster not drawn in a replicate" is reported as `mean_clusters_not_drawn_per_replicate` (0.870 on the fixture) and is structurally distinct from `questions_lost_to_invalid_labels`, which is provably 0. |
| **F-3** | REAL | **CLOSED** | duplicate question ids raise `DesignViolation: duplicate question ids in the cohort: ['q0']`, not `IndexError`. Reproduced. |
| **F-4** | REAL | **PARTIALLY CLOSED** | The dishonest half is fully withdrawn: the forbidden-token loop is **gone** from the v2 suite (the only remaining `needle` is `expect_violation`'s error-message matcher, a different thing), and both the README and the module docstring state that a word scan is not assurance and that the AST enumeration "is still not a proof". That much is honest and verified. But the *replacement* guarantee is narrower than the candidate states — see **NEW-1**. |
| **F-5** | REAL | **CLOSED** | The fixture is three clusters of unequal size and value (2×3.0, 3×1.0, 5×0.0). On it slot- / distinct- / cluster-weighting give three different answers, and the suite asserts the core matches the slot value and differs from the other two. The README's cluster-multiplicity claim now matches what is tested — verified line by line against test L249-264. |
| **F-6** | REAL | **CLOSED** (as far as a core can) | The gate reads the module global at call time; flipping and restoring it is tested. Still declarative because no runner calls it — the candidate states this rather than implying otherwise. |
| **F-7 / F-8** | COSMETIC | **CLOSED** | `_check_index` rejects empty, non-integer dtype, negative and out-of-range selections with `DesignViolation`. Reproduced for `[-1]`, `[0.7]`, `[99]`, `[]`. |
| **F-9** | COSMETIC | **CLOSED** | a boolean score is rejected before `float()` coercion. |
| **F-10** | COSMETIC | **CLOSED** | `MIN_ARCHIVE_ROWS = 2`; n=0 and n=1 archives rejected. |
| **F-11** | COSMETIC | **CLOSED for the three cited instances**; a new one introduced | The no-op `replace`, the dead conditional and `spans_zero in (True, False)` are gone; `spans_zero` is now asserted `is True` on a zero-centred fixture and `is False` on a distant one, and mutation M9 is killed by exactly that check. But see **NEW-2**. |
| **F-12** | COSMETIC | **NOT ACTED ON, disclosed** | Deliberate and correctly reasoned: binding §6 fixes an absolute `1e-12`; the measured headroom is recorded in `LINEARITY_HEADROOM_NOTE`; a relative tolerance would need a new decision. Accepted as recorded. |
| N-2, N-3, N-4 | — | carried forward | correctly identified as runner obligations, not core defects. |
| N-5 | — | **preserved** | sigma exactly `eps` still takes the divide branch (`d = 1e12`). Verified. |

---

## 2. New defects introduced or left by the corrections

### NEW-1 — REAL — the conformance guarantee covers three of the seven published quantities

`aggregate` publishes seven keys. The conformance test recomputes **three** of them
(`G_bar_pp`, `G_bar_scaled_pp`, `Delta_bar_pp`) against the independent reference. The other four are
covered only by the closed-schema equality, which constrains the **set of key names** and says
nothing about the **values behind them**. `reference_quantities` returns `G, GS, D` and nothing
per-seed; no check whose name contains `CONFORMANCE` mentions `per_seed`.

The consequence is not theoretical. The acceptance binding forbids "any ratio of `Δ` to `G` —
including `ρ`, under any name". I substituted such a ratio into an existing, permitted key and the
entire 88-check suite passed:

| mutant | what it does | result |
|---|---|---|
| **R1** | `per_seed_Delta_pp` becomes `per_seed_d / per_seed_g` — a genuine Δ/G ratio published under the permitted name | **SURVIVED** (exit 0, 0 failing checks) |
| **R2** | `per_seed_G_scaled_pp` becomes `per_seed_gs / per_seed_g` | **SURVIVED** |
| **R3** | `per_seed_G_pp` multiplied by an arbitrary 1.5 — not even a ratio, simply wrong | **SURVIVED** |
| **R6** | the same Δ/G ratio written with `np.divide`, invisible to the `ast.Div` count | **SURVIVED** |
| **R4 — negative control** | `Delta_bar_pp` itself becomes `D_/G`, i.e. a scalar the conformance test *does* reach | **KILLED** — `FAIL CONFORMANCE: Delta_bar matches an independent reference` |
| **negative control** | unmutated copy | passes, exit 0 |

R4 killing while R1–R3 survive is the point: the conformance test works, and it simply does not
reach three quarters of the record. The supporting AST division check does not close the gap either —
it is a **count band** (`0 < n <= 12`) currently sitting at 2, so ten further `Div` nodes pass, and
`np.divide` is not a `Div` node at all. The candidate does disclaim the AST check as "not a proof",
so that part is disclosed rather than dishonest.

What must change in the claim: "a quantity added under **any** name fails a test instead of slipping
past a scan" is true for a **new** name and false for a **forbidden quantity substituted into an
existing** one. Extend `reference_quantities` to return the per-seed vectors and compare all seven
keys, or state the narrower guarantee.

### NEW-2 — COSMETIC — a vacuous check reintroduced, inside the F-1 block that closes F-1

`test_membership_scaling_core.py` L132-133:

```
check("F-1: cv_sigma_before is a CV too", abs(diag["cv_sigma_before"] - float(...)) > 0
      or True)
```

The trailing `or True` makes the condition unconditionally true. Proven, not asserted: with
`cv_sigma_before` hard-coded to `123456.0` in the core, that check still prints
`ok    F-1: cv_sigma_before is a CV too`. This is the exact defect class F-11 raised. (The suite as a
whole still catches that particular break through a different check, so it is not a coverage hole —
but the check labelled as testing `cv_sigma_before` tests nothing.) An AST sweep of the suite finds
this as the only `check(...)` whose condition is a `BoolOp` ending in literal `True`; the two other
literal-`True` calls (L101, L150) are the legitimate "the preceding call did not raise" pattern.

### NEW-3 — COSMETIC — a raw exception where v2 fixed exactly this elsewhere

`build_clusters([], 0)` raises `ValueError: need at least one array to concatenate` from
`np.concatenate` at the partition proof, not a `DesignViolation`. Same class as F-8, which v2 fixed
for index selections. Guard `n_questions == 0` explicitly.

### NEW-4 — observation — "missing" is rejected only in its typed forms

`None` and `NaN` are rejected, but the empty string `""`, a whitespace-only string, and the literal
strings `"nan"` and `"None"` are all accepted as ordinary distinct cluster labels. A label column
sourced from CSV or JSON commonly renders a missing value as exactly one of these. Not a defect
against the finding's wording, and coercing them would be worse; worth a named rejection or an
explicit note.

### NEW-5 — observation — integer labels are keyed by `int()`

Two labels that are distinct objects but equal under `int()` are merged into one cluster. Realistic
instance: members of two different `IntEnum` classes sharing a value — `A.X` and `B.Y`, both 1, give
`n_clusters = 1`. Treating integer-equal labels as one cluster is defensible; it is recorded because
F-2's wording is that different labels must never be silently merged by coercion.

---

## 3. Adopted tests, and whether they test what they claim

Attribution is genuine and specific: the suite docstring names the branch, the full commit sha
`68819424765ed3da89377c89980d7e42546bfe02`, and the two source files, and states that the audit
namespace is not modified. Fourteen `[adopted]` markers sit on the individual cases.

They test what they claim against v2 — verified by running each and by the mutation kills that land
on them (M5 on the flag boundary, M6 on the eps fallback, M9 on `spans_zero`, M10 on the CV, M13 on
duplicates, M14 on label validation, M15 on the negative index). The vacuous
`spans_zero in (True, False)` is replaced by a genuinely meaningful pair of assertions.

Reproduction, independent of the preparer:

- candidate suite: **88 checks, ALL PASS**, exit 0. Output is byte-identical to the shipped
  `evidence/synthetic_test_output.txt` after normalising the one line printing a random temp path.
- mutation probes: **16 applied, 15 killed, 1 survived** — reproducing the shipped counts exactly.

The README's cluster-multiplicity claim (F-5 row) matches the fixture at test L249-264. The kill
count is correctly scoped in both the README and the script output as evidence about those 16
variants only.

---

## 4. The claimed survivor, M16

**The claim is upheld.** M16 removes the partition-coverage proof
(`covered != n_questions` and the `array_equal` check). The guard is genuinely unreachable through
the public API:

- *Structural*: an AST sweep of `build_clusters` finds **exactly one** `members[k].append(i)` site,
  inside the single `for i, lab in enumerate(labels)` loop. Each index is therefore appended exactly
  once, so `covered == len(labels)`, and `len(labels) == n_questions` is already enforced by the
  length check that precedes grouping. The condition cannot be false.
- *Empirical*: five pathological-but-valid label vectors (repeated, all-identical, all-distinct,
  numpy scalars, `2**300` ints) never reach it.
- *Adversarial*: a hand-written `numbers.Integral` subclass whose `__int__` collapses every label to
  one key still yields `covered = 10` of 10 — the coverage invariant survives even deliberate key
  collapse, which is the strongest evidence that the guard is defence in depth rather than a live
  check.

It is not covering a hole. Reporting it as a survivor, rather than deleting the guard or reaching it
by monkeypatching internals, is the right disposal.

---

## 5. Housekeeping

| check | result |
|---|---|
| v2 namespace separate and versioned | `drafts/v52/membership_impl_v2_2026_09_07/` — distinct path, distinct README, supersession stated with the v1 blob hash. |
| v1 byte-unchanged at the v2 tip | all four v1 files identical at `a6d70ff6` and `8179ce31`: `README_IMPL.md` `37e86ed5…`, core `707e166c…`, `synthetic_test_output.txt` `eedf5b66…`, tests `97e6e720…`. |
| earlier audit namespace byte-unchanged | `audit/v52-membership-impl-review-2026-09-07` still resolves to `68819424765ed3da89377c89980d7e42546bfe02`; the v2 commit adds only 7 files and touches nothing under `audit_v52_membership_impl_review_2026_09_07/`. |
| v2 commit touches only the 7 claimed files | confirmed: README_IMPL_V2.md, 3 evidence files, core, tests, scripts/mutation_probes_v2.py — 1416 insertions, 0 deletions, 0 modifications. |
| no seal / `.github` / Task 4F1 / `research/` / finalize / HMAC path | none touched. |
| each change maps to a finding id | the README carries a finding→change table covering F-1…F-12 and N-2/N-3/N-4; every substantive code change I found is attributable to a row in it. |
| **disclosed process incident (the tracked `.pyc`)** | **claim verified.** `task4f1_execution_candidate_2026_08_31/__pycache__/v52_t4f1_beam_retrieval.cpython-312.pyc` is present at both commits with the identical blob `b9b8a3e435b2b167c3d8364193ad0c48f0306e71`. The worktree deletion was never committed. |

One recorded observation, not a defect: the candidate branch is based on `16019724`, which predates
`9b4af59`. The governing binding document
`docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` therefore does **not exist**
on the candidate branch (empty-blob sha `e3b0c442…`); it exists on `main` @ `3279b28c`
(`a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71`), which is what I read it from.
Nothing on the candidate branch contradicts it. Separately, `main` @ `3279b28c` already carries a
ledger entry recording the v2 correction; the closure judgement in this report is mine and is not
that record's.

---

## 6. Regression

No correction broke a behaviour it should not have. Verified independently here: `G_bar` and
`Delta_bar` match a from-scratch reference to `< 1e-12`; the output schema is exactly
`AGGREGATE_KEYS`; both bootstraps are deterministic in the seed; the N-5 razor edge (sigma exactly
`eps` takes the divide branch, `d = 1e12`) is preserved; duplicate ids, overwrite refusal and the
default-closed real-data gate all still fire.

---

## 7. Verdict

**`CLOSURE PASS WITH FINDINGS`.**

- **F-1: CLOSED.** **F-2: CLOSED.**
- F-3, F-5, F-6, F-7/F-8, F-9, F-10 CLOSED; F-11 CLOSED for its three instances; F-12 correctly not
  acted on and disclosed.
- **F-4: PARTIALLY CLOSED** — the false claim is withdrawn, the replacement one is overstated.
- New: **NEW-1 (REAL)**, NEW-2/NEW-3 (COSMETIC), NEW-4/NEW-5 (observations).

NEW-1 is an assurance gap, not a defect in the shipped bytes: the core as committed contains no
ratio, and I verified its arithmetic against an independent reference. It is graded REAL for the
same reason the review graded F-4 REAL rather than BLOCKER.

**Single next concrete step.** Extend `reference_quantities` to return the per-seed vectors and add
conformance checks for `per_seed_G_pp`, `per_seed_G_scaled_pp` and `per_seed_Delta_pp`, so that all
seven published keys are recomputed rather than three; then correct the "any name" sentence in the
README and the module docstring to the guarantee that is actually held. Re-run mutants R1–R3 and R6
as the acceptance criterion.

**What this verdict does not do.** It does not authorize the experiment. No corpus-bound runner
exists; none was written or reviewed here; closing the core is not authorization to run it. Task 4F1
remains untouched.

---

*Checker: cold-start independent closure checker, commissioned 2026-09-07. Branch*
`audit/v52-membership-v2-closure-2026-09-07`. *Python 3.14.3, NumPy 2.5.2.*
