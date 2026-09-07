# Delta closure check of candidate v3 — NEW-1, NEW-2, NEW-3

**VERDICT: `CLOSURE PASS`**

All three acceptance criteria are met. I found no defect that blocks closure. Three items below are
recorded as **wording/claim problems** or **observations**, all marked OUT OF SCOPE FOR CLOSURE; none
of them is a blocker and none of them is presented as one.

Independent auditor, cold start, fresh clone. I did not read the preparer's checkouts. Every identity
claim below was verified by hashing **raw Git blobs** (`git cat-file blob <commit>:<path> | sha256sum`),
never files as checked out — this repository ships no `.gitattributes` and a Windows checkout would
hash differently.

---

## 1. Subject and scope

| item | value |
|---|---|
| candidate branch | `impl/v52-membership-under-scaling-v3-2026-09-07` |
| candidate commit | `dcb568d0a6c33154c1568500325ad457b4d6f455` |
| candidate parent | `8179ce31afc8ec9a2469c801a0a5e022b4494518` (v2) |
| namespace | `drafts/v52/membership_impl_v3_2026_09_07/` |
| answers | closure check on `audit/v52-membership-v2-closure-2026-09-07` @ `712412a5947fa56374e05bf3e3a0b075d4578b6d` |
| that report's blob sha256 | `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be` — **verified, resolves** |
| audit branch (this report) | `audit/v52-membership-v3-closure-2026-09-07`, parented on `main` `3279b28c991095f9339fd22d1d99782a4582b613` |
| environment | Windows 10, CPython **3.14.3**, NumPy **2.5.2** — not the pinned research stack |

**Sidecar method.** `V3_CLOSURE_REPORT.md.sha256` holds the sha256 of the **committed blob** of this
file, computed as `git cat-file blob :audit_v52_membership_v3_closure_2026_09_07/V3_CLOSURE_REPORT.md
| sha256sum` against the staged object immediately before the commit, so it is the hash of the exact
bytes git stores. Every file in this namespace is stored with LF endings and contains no CR bytes, so
`sha256sum` on a Unix checkout reproduces it directly; on a Windows checkout, hash the raw blob.

This is a **delta closure check against exactly three criteria**. I did not re-audit the research, the
design, the preregistration, the statistics, the LoCoMo / LongMemEval evidence, the acceptance record,
or the first-round findings F-1 … F-12. Those were closed at `712412a5` and stay closed. NEW-4 from
that report is out of scope and is **not** entangled with any of the three criteria (it concerns
string labels such as `""`, `"nan"`, `"None"` being accepted as ordinary cluster labels — a labelling
question, orthogonal to conformance coverage, vacuous checks and the empty-cluster guard). I state
that explicitly rather than expanding silently.

**Boundaries observed.** No corpus, dataset, model or embedding was read, downloaded or touched. No
fitting, retrieval, ranking, real-data bootstrap or pilot. No sealing, no HMAC key, no `--mode run`,
no `--mode finalize`. Nothing under any `task4f1*` namespace, sealed payload, manifest or old audit
namespace was touched. No recursive delete was run anywhere in the checkout. `main`, the v1/v2
candidate branches and the two existing audit branches were not modified. I repaired nothing.

---

## 2. Per-criterion disposition

| criterion | disposition | concrete evidence |
|---|---|---|
| **NEW-1** — every published field checked against an independent reference, incl. the three per-seed vectors; schema fields verified; mutants R1/R2/R3/R6 caught; accepted numeric tolerance, not bit-level | **CLOSED** | I wrote my own mutant harness (`scripts/independent_mutants.py`) and applied it to a copy of the v3 core in a temp directory. **All four R-equivalents died**, each by name: R1 → `FAIL CONFORMANCE: per_seed_Delta_pp … max|diff| = 1.70e+02`; R2 → `per_seed_G_scaled_pp … 1.71e+02`; R3 → `per_seed_G_pp … 8.77e+00`; R6 (`np.divide`) → `per_seed_Delta_pp … 1.70e+02`. **Five further mutants of my own choosing, which the preparer did not anticipate, also all died** (B-1 … B-5, §3.1). The reference (`reference_quantities`, test L69-88) is mechanically confirmed independent: its AST touches **no** attribute of the core module object `m` and imports no NumPy — only `range`, `sum`, `zip`, `list.append`. Tolerance is `CONF_TOL = m.TOL = 1e-12` **absolute**, sourced from binding §6; no bit-level equality is demanded on any published value; negative controls prove each comparison can fail. Schema equality against `AGGREGATE_KEYS` is asserted with its own negative control. |
| **NEW-2** — the `… or True` gone, replaced by a check that genuinely fails; `cv_sigma_before = 123456.0` killed; suite swept for similar shapes | **CLOSED** | I applied the `123456.0` mutant myself: **exit 1, killed**, by two independent named failures (§3.2). My own sweep (`scripts/vacuity_sweep.py`, seven shapes V1–V7, broader than the preparer's one) finds **no** `or True` / `and True` shape anywhere in the v3 suite; run against the **v2** suite as a positive control it finds the original defect at line 132, confirming the sweep works. The preparer's stated scope ("one named shape") matches the code, and where the two differ the **code is stronger than the words**, not weaker (§3.2, PART 1). |
| **NEW-3** — `build_clusters([], 0)` raises a clear, documented `DesignViolation`, verified by a synthetic test | **CLOSED** | Called directly by me: `build_clusters([], 0)` → `DesignViolation: cluster grouping needs at least one question, got n_questions=0`, raised at `membership_scaling_core.py:394`, i.e. the first statement after the argument is listed — not from a deeper frame. Neighbouring inputs all give **named** violations, none leaks a library exception (§3.3). The behaviour is documented in the `build_clusters` docstring and inline at the guard, and covered by two synthetic tests (test L342-345). |

### Also verified (the three "ALSO" items)

| item | result |
|---|---|
| **(a)** README + module docstring claims narrowed; nothing claims any wrong computation is necessarily caught; what IS claimed is true | **PASS** — see §4 |
| **(b)** earlier hash-bound files preserved; commit `dcb568d0` touches only the v3 namespace | **PASS** — see §5 |
| **(c)** `GOVERNING_DOCUMENTS.md` binds normative documents by commit, path and sha256, and every stated hash resolves | **PASS** — see §6 |

---

## 3. What I actually ran

Baseline first, to establish the candidate reproduces on this machine:

```
$ python -B test_membership_scaling_core.py
… 99 lines beginning "ok"
ALL PASS                                             exit 0
```

99 `ok`, 0 `FAIL`. Normalising only the temp-directory path in the last check's detail string, my
run is **line-for-line identical** to the committed `evidence/synthetic_test_output.txt` (101 lines
each, 0 differing lines). The committed per-seed agreement `max|diff| = 3.55e-15` reproduces exactly,
and matches the README's stated figure.

I also replayed the preparer's own probe script unchanged: **22 applied, 21 killed, 1 survived
(`M16`)** — identical to the committed `evidence/mutation_probes_v3_results.json`, with zero
kill-status disagreements row by row. `M16`'s survival is correctly characterised: the
`covered != n_questions` guard is genuinely unreachable through the public API, because label
validation precedes it and `len(labels) == n_questions` is enforced first, so every question carries
exactly one label. A mutation test cannot kill an unreachable guard. That is defence in depth, not a
hole, and the preparer reports it as such rather than deleting the guard or reaching it by
monkeypatching.

### 3.1 My own mutants (CRITERION 1, verified by construction)

`scripts/independent_mutants.py` — written from scratch by me by reading the v3 core. It does not
import, call or copy `scripts/mutation_probes_v3.py`. Raw output in
`evidence/independent_mutants_output.txt`, machine-readable in
`evidence/independent_mutants_results.json`.

Group A reconstructs the four mutants named in my tasking plus the NEW-2 and NEW-3 mutants. Group B
is mine alone, chosen to probe whether the coverage is real or fitted to the known list. **Every
Group B mutant leaves all three published scalars exactly correct**, so only a check that actually
reaches the vector or count fields can see them.

| id | group | what it does | result |
|---|---|---|---|
| `A-R1-ratio-into-per-seed-delta` | A | `Δ/G` ratio into the permitted key `per_seed_Delta_pp` | **KILLED** |
| `A-R2-ratio-into-per-seed-g-scaled` | A | ratio into `per_seed_G_scaled_pp` | **KILLED** |
| `A-R3-per-seed-g-rescaled` | A | `per_seed_G_pp × 1.5`, scalars correct | **KILLED** |
| `A-R6-ratio-via-np-divide` | A | same ratio via `np.divide` — no `ast.Div` node | **KILLED** |
| `A-NEW2-cv-before-constant` | A | `cv_sigma_before = 123456.0` | **KILLED** |
| `A-NEW3-empty-guard-removed` | A | delete the `n_questions <= 0` guard | **KILLED** |
| `B-1-per-seed-g-and-gs-swapped` | **B, mine** | swap `per_seed_G_pp` and `per_seed_G_scaled_pp` in the returned dict — both keys permitted, both values real published quantities | **KILLED** (two named failures) |
| `B-2-per-seed-vectors-reversed` | **B, mine** | reverse each per-seed vector. The mean of a reversed vector is the same number, so every scalar, the linearity identity and the schema are untouched | **KILLED** (three named failures) |
| `B-3-per-seed-rounded-1e6` | **B, mine** | round the per-seed vectors to 6 decimals — visually right, ~1e-7 wrong | **KILLED**, `max|diff| = 3.54e-07` |
| `B-4-slots-counted-as-distinct` | **B, mine** | publish `n_question_slots` as DISTINCT questions. The conformance fixture has no repeated index, so **the conformance check alone cannot see this** | **KILLED**, by `a repeated index counts twice` and `F-5: multiplicity is preserved in the slot count` |
| `B-5-slots-off-by-one` | **B, mine** | `n_question_slots + 1` | **KILLED** (three named failures) |
| `B-6-per-seed-delta-inside-tolerance` | **B, mine** | perturb `per_seed_Delta_pp` by `+5e-13`, i.e. **inside** the accepted `1e-12` | **SURVIVES — expected, and not a defect** |

**11 of 12 killed; 0 unexpected survivors.**

`B-6` is included deliberately and its survival is the **correct** behaviour of a tolerance-based
comparison. Binding §6 fixes an absolute `1e-12`; demanding bit-level equality on floating-point sums
would itself be an unjustified new condition, and the tasking is explicit that such a demand would be
a defect rather than a virtue. I record `B-6` so the tolerance's actual reach is explicit rather than
assumed: a perturbation of published values below `1e-12` absolute is, by design, not detected.

`B-4` is the most informative of my own probes. It is the one mutant whose kill does **not** come from
the new conformance coverage — the conformance fixture uses `idx = arange(17)` with no repeats, so
`len(unique(idx)) == len(idx)` and the reference agrees with the mutant. It dies instead on two
pre-existing multiplicity checks. That is a genuine finding *in the candidate's favour*: the coverage
is not a single point of failure fitted to the known list.

`A-NEW3` is killed by an **unhandled `ValueError` crashing the script** (exit 1, no named `FAIL` line),
because `expect_violation` catches only `DesignViolation`. The mutant dies, which is what the criterion
requires; I note the mechanism precisely rather than letting a crash pass as a clean assertion failure.

### 3.2 Vacuity sweep and its reach (CRITERION 2, verified by construction)

`scripts/vacuity_sweep.py` — my own sweep, seven shapes, run over the v3 suite and, as a positive
control, over the **v2** suite. Output in `evidence/vacuity_sweep_output.txt`.

```
v3 suite:  check() calls: 64   expect_violation() calls: 28
           preparer's own sweep predicate over this file reports lines: NONE
           auditor's V1 (BoolOp with literal True): NONE
           auditor's V3 (constant-folding condition): NONE
           auditor's V5 (expect_violation with empty/absent needle): NONE
v2 suite:  preparer's own sweep predicate reports lines: [132]
           auditor's V1: line 132  →  "… > 0       or True"
```

My independent sweep finds the v2 defect and confirms it is gone from v3. It also confirms that
**every one of the 28 `expect_violation` calls asserts a non-empty message needle** — the message
assertion is nowhere vacuous.

The only shapes my sweep flags in v3 are five bare `check(name, True)` markers (test L158, 163, 214,
234, 253) and one `check(name, False, "no exception raised")` inside `expect_violation` (L59). These
are the "the preceding call did not raise" pattern: each follows a statement that would abort the
whole script if it raised, so they carry real information at script level. The preparer names and
exempts this pattern explicitly in the sweep code (`# the legitimate "the preceding call did not
raise" pattern`). **Not a defect.** One V7 textual hit at L152 is inside a string literal in the
sweep's own negative control, not executable code.

**Does the preparer's claim match the code?** The README says the sweep reports a condition that is
"a boolean expression **ending in** a literal `True`". `evidence/sweep_reach_probe_output.txt`
establishes the actual reach:

```
FLAGGED      check('x', a > 0 or True)                 the exact v2 defect: literal True LAST
FLAGGED      check('x', True or a > 0)                 literal True FIRST
FLAGGED      check('x', a > 0 and True)                an `and True` conjunct
not flagged  check('x', True)                          the exempted did-not-raise marker
not flagged  check('x', a > 0 or (1 == 1))             unconditionally true, NOT a literal True
not flagged  check('x', a > 0 or bool(1))              unconditionally true via a call
not flagged  check('x', a > 0 or 1)                    truthy literal that is not `True`
not flagged  check('x', a > 0)                         honest condition (control)
```

**The code is STRONGER than the words**, not weaker: it flags a literal `True` in any position, not
only last. It is weaker than "every unconditionally true condition" — which the preparer explicitly
does **not** claim, in the README ("that sweep covers that one shape and nothing else. It is not a
claim that every check in this suite is meaningful, and no such claim is made") and in the test
docstring. The claim as written is accurate.

I then ran an adversarial combined mutation to see whether the NEW-2 kill rests on one check:

| case | result |
|---|---|
| core mutant only (`cv_sigma_before = 123456.0`) | **KILLED**, exit 1, two named failures |
| core mutant **+** the replacement check neutered with `or (1 == 1)` — a shape the sweep provably cannot see | **STILL KILLED**, exit 1, by `F-1: a zero-mean sigma gives NaN, explicitly and with no epsilon added` |
| test neutered only, core untouched (control) | survives, exit 0 — correct; nothing is wrong |

The NEW-2 kill rests on **two independent checks**, not one. Neutering the replacement check with a
shape outside the sweep's reach does not save the mutant.

### 3.3 `build_clusters` boundary probes (CRITERION 3, verified by calling it)

`evidence/probe_new3_and_reference_output.txt`, PART 1. I called the function directly:

| input | outcome |
|---|---|
| `build_clusters([], 0)` | `DesignViolation: cluster grouping needs at least one question, got n_questions=0` @ core:394 |
| `build_clusters([], -1)`, `([], -7)` | same named `DesignViolation`, with the count echoed |
| `build_clusters([], 3)` — empty labels, positive count | `DesignViolation: cluster labels do not cover the questions one to one: 0 labels, 3 questions` @ core:397 |
| `build_clusters(['A','B'], 0)`, `(['A','B'], -2)` | same named `DesignViolation` |
| `build_clusters(['A'], 1)`, `(['A','B'], 2)`, `(['A','A'], 2)` | return correctly; `n_clusters` 1, 2, 1 |
| `cluster_bootstrap` on an empty `g` — the public path | `DesignViolation: cluster grouping needs at least one question, got n_questions=0` |

Every count/label boundary yields a **named** violation raised in `build_clusters` itself, not a
library exception from a deeper frame. The message is clear and states the offending value.

The single exception: a **non-iterable first argument** (`build_clusters(None, 0)`,
`build_clusters(3, 0)`) raises `TypeError: 'NoneType' object is not iterable` at core:389, because
`labels = list(cluster_of_question)` runs before the guard. This is an argument-*type* error, not one
of the count/label boundaries NEW-3 names, and the criterion is about `build_clusters([], 0)`. I record
it in §7 as an observation, explicitly **not** a closure blocker.

---

## 4. (a) Claims are narrowed, and what is claimed is true

I grep-swept the whole v3 namespace for absolute assurance language
(`necessarily caught|any wrong|guarantee|proves|proof|always caught|impossible|exhaustive|
complete coverage|all defects|…`). **Nothing anywhere claims that any wrong computation is
necessarily caught, or anything equivalent.** Every hit is a negation or a scoped statement:

- `membership_scaling_core.py:50` — `No claim is made that any wrong computation is necessarily caught.`
- `test_membership_scaling_core.py:20` — `**No claim is made that any wrong computation is necessarily caught.**`
- `README_IMPL_V3.md:54` — `**No claim is made that any wrong computation is necessarily caught.**`
- AST enumeration is called `explicitly NOT a proof` in all three places, with the reason given
  (`np.divide` is not a `Div` node), and mutant R6 is presented as the demonstration.
- `A word scan is not used as assurance anywhere.` — I confirm no forbidden-token loop exists in the
  v3 suite; the only `needle` is `expect_violation`'s error-message matcher, a different thing.
- Kill-count scope is stated three times (core docstring, probe docstring, README) as evidence about
  those variants only and not a correctness guarantee.

The three uses of "impossible" (core L156, L385, L504) are scoped claims about question loss to an
invalid label, and they are justified: label validation strictly precedes grouping and
`len(labels) == n_questions` is enforced, so the partition is total by construction. I verified this
is the same reason `M16` is unkillable, and the two statements are consistent with each other.

Every specific claim I checked is true:

| claim | verified |
|---|---|
| conformance recomputes **all seven** published fields | yes — 3 scalars, 3 vectors elementwise, `n_question_slots` |
| the reference is independent | yes — mechanically: no reference to `m`, no NumPy, builtins only |
| `CONF_TOL = m.TOL`, absolute `1e-12`, bitwise equality not required | yes; no bitwise assertion on any published value |
| `max|diff| = 3.55e-15` on each per-seed vector | yes, reproduced exactly |
| 99 checks, ALL PASS | yes, reproduced line-for-line |
| 22 mutations applied, 21 killed, 1 survived | yes, reproduced row-for-row |
| the one survivor `M16` is an unreachable guard | yes, verified by reading the control flow |
| R6 is killed by conformance, not by the AST check | yes — the only failing line is the conformance one |

**Wording problem, OUT OF SCOPE FOR CLOSURE (W-1).** The v3 test file's own docstring header was
carried over from v2 without editing. Byte-verbatim, `test_membership_scaling_core.py` L1 and L3-4
and L10:

```
"""Synthetic tests for membership_scaling_core v2. NO real data, NO corpus, NO model.

Supersedes drafts/v52/membership_impl_2026_09_07/test_membership_scaling_core.py (blob sha256
97e6e7206864dffe4638a19231bcc5ee706cda2906cf08890ac80aa7e1cd279f), left byte-unchanged.
```
```
modified; these are reimplementations against the v2 core, credited to their source.
```

This file is the **v3** suite and it tests the **v3** core; the file it names as superseded is the
**v1** test (I confirmed the hash `97e6e720…` is indeed the v1 test blob at `a6d70ff6`), skipping the
v2 test (`a0e9cc27191e3c7a9683cbd94007c17c9c6666eb8bea1a78f40e7ec09ce3ec12`) that it actually
supersedes. Cosmetically, `scripts/mutation_probes_v3.py:219` also still uses the v2 temp prefix
(`prefix="v52_mut_v2_"`). This is a **version-label staleness**, not an overstatement and not a false
technical claim — every hash it states is correct. It does not affect any criterion.

**Wording note (W-2), OUT OF SCOPE FOR CLOSURE.** README L45-46 describes the sweep as reporting a
condition "ending in a literal `True`" where the code flags a literal `True` in **any** position. The
code is stronger than the words. Recorded for accuracy; it is not a defect and I do not present it as
one.

---

## 5. (b) Earlier hash-bound files preserved; commit scope

All by raw blob, `git cat-file blob <commit>:<path> | sha256sum`:

| what | commit : path | expected | measured | result |
|---|---|---|---|---|
| v1 core | `a6d70ff6…` : `drafts/v52/membership_impl_2026_09_07/membership_scaling_core.py` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` | identical | **PASS** |
| v2 core | `8179ce31…` : `drafts/v52/membership_impl_v2_2026_09_07/membership_scaling_core.py` | `60141d05f2285d268a88d98344770c8cb5d166168a6fa29371a1ea330db0a1e1` | identical | **PASS** |
| v1 core **as seen from v3** | `dcb568d0…` : same path | same | identical | **PASS** |
| v2 core **as seen from v3** | `dcb568d0…` : same path | same | identical | **PASS** |
| prior closure report | `712412a5…` : `audit_v52_membership_v2_closure_2026_09_07/CLOSURE_CHECK_REPORT.md` | `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be` | identical | **PASS** |
| v1 impl review report | `68819424…` : `audit_v52_membership_impl_review_2026_09_07/IMPL_REVIEW_REPORT.md` | `e245f0da2b0577f8940dfd906746f618638b45481280f93facb1774270bc3e98` | identical | **PASS** |

```
$ git diff --name-status 8179ce31… dcb568d0… -- drafts/v52/membership_impl_2026_09_07/ \
                                                drafts/v52/membership_impl_v2_2026_09_07/
(empty)
```

The v1 and v2 namespaces are **byte-unchanged in their entirety**, not merely in the core file.

**Commit scope.** `git diff --name-status dcb568d0^ dcb568d0` lists exactly eight paths, **all** under
`drafts/v52/membership_impl_v3_2026_09_07/`, all additions:

```
A	drafts/v52/membership_impl_v3_2026_09_07/GOVERNING_DOCUMENTS.md
A	drafts/v52/membership_impl_v3_2026_09_07/README_IMPL_V3.md
A	drafts/v52/membership_impl_v3_2026_09_07/evidence/mutation_probes_v3_output.txt
A	drafts/v52/membership_impl_v3_2026_09_07/evidence/mutation_probes_v3_results.json
A	drafts/v52/membership_impl_v3_2026_09_07/evidence/synthetic_test_output.txt
A	drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py
A	drafts/v52/membership_impl_v3_2026_09_07/scripts/mutation_probes_v3.py
A	drafts/v52/membership_impl_v3_2026_09_07/test_membership_scaling_core.py
```

No `task4f1*`, no sealed payload, no manifest, no audit namespace. **PASS.**

Both audit namespaces live on their own branches, not on `main`, and are absent from the v3 tree
(`git ls-tree -r dcb568d0 | grep -c audit_v52_membership` → `0`), so v3 cannot have modified them.
Both audit branch tips are still exactly `712412a5947fa56374e05bf3e3a0b075d4578b6d` and
`68819424765ed3da89377c89980d7e42546bfe02`, and both candidate branch tips are still `a6d70ff6…` and
`8179ce31…`.

**One thing that could be mistaken for a finding, and is not.** `git diff main dcb568d0` shows
`docs/CONTINUITY_LEDGER.md` modified and the acceptance-binding document and its `.sha256` sidecar
deleted. That is **not** something the v3 commit did. The v3 branch is parented on
`16019724564b5ac8db4a4d2d8bb08f98feb45c09` (verified: that is the merge-base with `main`), which
predates those documents; the branch is simply behind `main`. The v3 commit itself touches nothing
outside its namespace, as shown above. This is exactly the situation `GOVERNING_DOCUMENTS.md` exists
to explain.

### v3 namespace blob hashes (raw git blobs, at `dcb568d0`)

| path | sha256 |
|---|---|
| `GOVERNING_DOCUMENTS.md` | `6b8747180c3e577bdb27971e4eb259c5852fe28c25803dc8bdf8f2c63d0c8768` |
| `README_IMPL_V3.md` | `eb35b0e7a7d895a8062cfc51179748a5a34eca3cd699457a3a721efbad228448` |
| `membership_scaling_core.py` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` |
| `test_membership_scaling_core.py` | `1d426abcc908718ae2d95f0a84e323603fd05199dc3da8809d03e6795f5b2d87` |
| `scripts/mutation_probes_v3.py` | `a5631f76cd264f986dca44881d80c81962e1d7b453f25679cc3e348c1865f5ea` |
| `evidence/mutation_probes_v3_output.txt` | `b9bdfdb8133b4ec90aa8de9190dea193ae9303b5178ca4be8a8b1fcd7aadf77c` |
| `evidence/mutation_probes_v3_results.json` | `5c3229f6f436f7e12a6f50357cd57c84c1545e43e50e17574224290df681c679` |
| `evidence/synthetic_test_output.txt` | `fe71ab3e30a6586346997e55c0d6697e0eb1846616d4255c3941eb9a8a082242` |

---

## 6. (c) `GOVERNING_DOCUMENTS.md` — every stated hash resolves

Each normative document was hashed at the commit the file names, and again at `main`
`3279b28c991095f9339fd22d1d99782a4582b613`. All eight hashes agree with the file, and all four
commits are ancestors of `main`.

| # | path on `main` | stated commit | stated sha256 | at that commit | at `main` |
|---|---|---|---|---|---|
| 0 | `…ACCEPTANCE_BINDING_2026-09-07.md` | `9b4af594…` | `a99d547d5255…` | **matches** | **matches** |
| 1 | `…DESIGN_REVISION_R2_2026-09-07.md` | `16019724…` | `39cbfcea3a93…` | **matches** | **matches** |
| 2 | `…DESIGN_REVISION_R1_2026-09-07.md` | `2eadc41b…` | `3d7a79b249e9…` | **matches** | **matches** |
| 3 | `…PREREG_DRAFT_2026-09-07.md` | `56c29416…` | `3da80e3424a8…` | **matches** | **matches** |

The review chain is bound by branch + commit + report hash, and both report hashes resolve (§5). The
candidate-lineage table's two core hashes resolve (§5). The file's own claim that the branch is based
on `16019724…` is correct — that is the merge-base of the v3 branch with `main`. The instruction it
gives ("Verify from raw Git blobs, not from a checkout") is correct and is the method I used.

**No finding.** Nothing in `GOVERNING_DOCUMENTS.md` fails to resolve.

---

## 7. Findings, classified

Nothing below blocks closure. All three criteria are CLOSED.

### Real defects

**None found within scope.**

### Observations — OUT OF SCOPE FOR CLOSURE

**O-1 — a non-iterable first argument to `build_clusters` leaks a `TypeError`.**
`build_clusters(None, 0)` and `build_clusters(3, 0)` raise `TypeError: 'NoneType' object is not
iterable` from `labels = list(cluster_of_question)` at `membership_scaling_core.py:389`, one line
above the NEW-3 guard. Every *count* and *label* boundary NEW-3 names is a named `DesignViolation`;
this is an argument-type error on a different axis. NEW-3 is closed regardless. Moving the guard above
the `list()` call, or wrapping it, would be an **optional improvement**, not a blocker, and I am not
presenting it as one.

**O-2 — NEW-4 from the prior report is still open.** `""`, whitespace-only strings, `"nan"` and
`"None"` remain accepted as ordinary cluster labels. It was out of scope for this round by
instruction, is not entangled with any of the three criteria, and v3 did not claim to address it.
Recorded only so it is not lost.

### Wording / claim problems — OUT OF SCOPE FOR CLOSURE

**W-1 — stale version labels in the v3 test docstring** (§4). `"""Synthetic tests for
membership_scaling_core v2.`, the `Supersedes …` line naming the **v1** test rather than the v2 one,
`reimplementations against the v2 core`, and `prefix="v52_mut_v2_"` in the probe script. Every hash
these lines state is correct; only the version labels are stale. No technical claim is false.

**W-2 — README describes the sweep as "ending in a literal `True`" where the code flags a literal
`True` in any position** (§3.2). The code is stronger than the words.

### Optional improvements (explicitly NOT blockers, and not obstacles to acceptance)

These would add further assurance. They are listed because an auditor should say what more could be
done, **not** because anything is missing that the criteria require.

1. Add a conformance fixture with a **repeated** index so `n_question_slots` is reached by the
   conformance path itself rather than only by the multiplicity checks (my `B-4` showed the current
   fixture cannot see that field's most plausible defect through conformance).
2. Have `expect_violation` catch `BaseException` and report the actual type, so a mutant that
   converts a `DesignViolation` into a library exception produces a named `FAIL` rather than a script
   crash (my `A-NEW3` died by crash).
3. Broaden the self-sweep beyond the one named shape — e.g. constant-folding conditions — if a future
   round wants stronger coverage of the vacuity class. The current narrow claim is honest as it stands.

---

## 8. What this verdict does and does not do

`CLOSURE PASS` means the three findings NEW-1, NEW-2 and NEW-3 raised by the check at `712412a5` are
closed, verified by construction on this machine.

It does **not** mean the core is correct. Kill counts are evidence about the specific fault variants
tested and nothing more. Across my 12 mutants and the preparer's 22, the demonstrated coverage is of
those variants only; no suite here is shown to be sound, and I make no such claim. `B-6` documents one
concrete class that is by design not detected: a perturbation of a published value below `1e-12`
absolute.

It does **not** authorize the experiment. No corpus-bound runner exists; none was written or reviewed
here. Closing the core is not authorization to run it. Task 4F1 remains sealed, blocked and untouched.

Tests ran on CPython 3.14.3 / NumPy 2.5.2, **not** the pinned research stack. A rerun on the pinned
stack is a separate obligation and I did not discharge it.

---

## 9. Reproducing this check

From a fresh clone, with the v3 namespace extracted to `$CAND`
(`git archive dcb568d0 drafts/v52/membership_impl_v3_2026_09_07 | tar -x`):

```
python -B $CAND/test_membership_scaling_core.py                       # baseline: 99 ok, exit 0
python -B $CAND/scripts/mutation_probes_v3.py $CAND out.json          # 22 applied, 21 killed
python -B scripts/independent_mutants.py $CAND \
         evidence/independent_mutants_results.json                    # 12 applied, 11 killed
python -B scripts/probe_new3_and_reference.py $CAND
python -B scripts/vacuity_sweep.py $CAND/test_membership_scaling_core.py <v2-test-file>
python -B scripts/sweep_reach_probe.py $CAND
```

All scripts write mutants to throwaway temp directories and never modify the candidate files.

| artefact | contents |
|---|---|
| `scripts/independent_mutants.py` | my 12 mutants (CRITERION 1) |
| `scripts/probe_new3_and_reference.py` | `build_clusters` boundary probes + reference-independence AST check (CRITERIA 3, 1) |
| `scripts/vacuity_sweep.py` | my seven-shape vacuity sweep (CRITERION 2) |
| `scripts/sweep_reach_probe.py` | sweep reach table + the combined adversarial mutation (CRITERION 2) |
| `evidence/candidate_suite_reproduction.txt` | my baseline run of the v3 suite |
| `evidence/preparer_probes_reproduction.txt` | my replay of the preparer's probe script |
| `evidence/independent_mutants_output.txt` / `.json` | raw output and machine-readable results |
| `evidence/probe_new3_and_reference_output.txt` | raw output |
| `evidence/vacuity_sweep_output.txt` | raw output, v3 and v2 |
| `evidence/sweep_reach_probe_output.txt` | raw output |
| `HASH_MANIFEST.json` | sha256 of every raw git blob this report asserts |
