# V52 — Membership Under Scaling: Independent Implementation Review

Verdict: **`PASS WITH FINDINGS`**

Scope of the verdict: **the reviewed computation core only.** The corpus-bound runner has not been
written and is not reviewed. Nothing here approves the experiment, authorizes a run, seals anything,
or says the pipeline is ready. Task 4F1 was not touched in any way.

Date: 2026-09-07
Reviewer: cold-start independent implementation reviewer, commissioned by the Head Researcher
Preparer: the session that wrote the code. Nothing the preparer wrote — comments, README claims,
test names — was accepted as evidence. Every statement below rests on repository bytes or on code
this reviewer executed.

Review branch: `audit/v52-membership-impl-review-2026-09-07`, based on `main` at
`9b4af5949c4dc0e5054f8f522f1952ec47513f8f`. All work is confined to
`audit_v52_membership_impl_review_2026_09_07/`. No candidate file, no branch, no seal and no frozen
artifact was modified.

---

## 0. Provenance and hash discipline

The repository ships **no `.gitattributes`**, and this clone has `core.autocrlf=true`. Every hash
below is therefore taken over the **raw Git blob** (`git show <commit>:<path> | sha256sum`), never
over a checked-out file. That this matters was demonstrated, not assumed:

| object | sha256 |
|---|---|
| acceptance record, **raw blob** at `9b4af59` | `a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71` |
| the same file, **checked out on this Windows clone** | `91380902859942bb558f12f754a0103ec5aa3b06be0672ce277dbc30bb8990da` |

A reviewer who hashed the working tree would have reported a phantom mismatch.

**Candidate files** (`impl/v52-membership-under-scaling-2026-09-07` at `a6d70ff63ce44ea0f066a075853c9e93dec53122`,
`drafts/v52/membership_impl_2026_09_07/`) — blob hashes, all **matching** the commission:

| file | blob sha256 | expected |
|---|---|---|
| `membership_scaling_core.py` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` | match |
| `test_membership_scaling_core.py` | `97e6e7206864dffe4638a19231bcc5ee706cda2906cf08890ac80aa7e1cd279f` | match |

**Governing documents** (`main` at `9b4af59`), each blob hash equal to both the acceptance record's
own precedence table and the file's committed `.sha256` sidecar:

| document | blob sha256 | agrees with |
|---|---|---|
| `…ACCEPTANCE_BINDING_2026-09-07.md` | `a99d547d…0a71c71` | commission + sidecar |
| `…DESIGN_REVISION_R2_2026-09-07.md` | `39cbfcea…932f451669` | record §1 + sidecar |
| `…DESIGN_REVISION_R1_2026-09-07.md` | `3d7a79b2…ad217b3391` | record §1 + sidecar |
| `…PREREG_DRAFT_2026-09-07.md` | `3da80e34…06301e3399` | record §1 + sidecar |

The precedence chain R2 → R1 → draft is therefore intact and the controlling document is the one the
commission names.

**Candidate branch scope.** From its merge base `1601972` the implementation branch carries exactly
one commit and adds exactly four files, all under `drafts/v52/membership_impl_2026_09_07/`. It
touches no workflow, no `.github/` path, no seal, no Task 4F1 namespace and no `research/v52/` path.
(The two-point diff against `main` also shows the acceptance record as "removed"; that is branch
divergence — the record was written on `main` after the merge base — not a deletion by the preparer.)

**Environment.** Windows 10, Python 3.14.3, NumPy 2.5.2, Git 2.x. No virtualenv was needed and none
was committed.

**Boundary honoured.** No corpus was read or downloaded, no model was downloaded, no real fitting,
retrieval, ranking or bootstrap was performed, nothing was sealed, no experiment was run, and no
Task 4F1 action of any kind was taken. All data in every script is synthetic and generated in
process.

---

## 1. What was done

1. Fresh clone; branch cut from `main` at the commissioned commit.
2. Read the acceptance record first, then R2, then R1 §§1–7, then draft §§6–7, and derived the
   normative requirements from that order of precedence.
3. Read the candidate core and test suite in full, from the raw blobs.
4. **Reproduced the preparer's suite.** 74 checks, 74 pass, and my run is byte-identical to the
   shipped `synthetic_test_output.txt` except for the one line that prints a random temp path.
   (`evidence/preparer_suite_reproduction.txt`)
5. **Wrote and ran an independent adversarial suite** — 81 expectations and 21 recorded
   observations, with a negative control for every load-bearing check and an independently written
   reference implementation for the formulas and for *both* bootstraps.
   (`scripts/adversarial_core_tests.py`, `evidence/adversarial_core_*.{txt,json}`)
6. **Ran 13 mutation probes** against a throwaway copy of the core, scoring both suites on each.
   (`scripts/mutation_probes.py`, `evidence/mutation_probe_*.{txt,json}`)
7. **Statically audited the preparer's own self-checks** for conditions that cannot fail, and
   measured the scope of its "forbidden token" scan.
   (`scripts/preparer_selfcheck_audit.py`, `evidence/preparer_selfcheck_*.{txt,json}`)

---

## 2. Area-by-area result

| area | result | one-line basis |
|---|---|---|
| **A. Formulas and the percentage-point unit** | **PASS** | `g`, `gs`, the three means and the per-seed vectors match an independently written reference to `0.0`; `PP = 100.0` is applied exactly once, in `paired_matrices`, and nowhere else; the check is sharp (a doubly-applied factor is caught). |
| **B. Pairing of questions, arms and seeds** | **PASS** | One index set per replicate really is shared across arms *and* across the fixed seed panel — proved with perfectly anti-correlated seed columns that collapse to exactly `0.0`, against a negative control where independent per-seed resampling gives a `1.41 pp` wide interval. The seed panel is a matrix axis, never resampled. |
| **C. Scaling operator and degenerate-coordinate rules** | **PASS WITH FINDINGS** | `ddof=0` confirmed and distinguished from `ddof=1`; `ε` is a genuine fallback (`d = 1`, never `1/ε`, never dropped) at counts 3, 4 and 5; the per-archive flag has the correct `> 4` semantics including at the untested boundary of exactly 4; `D` takes only the archive. **But `cv_sigma_after` is the standard deviation of the post-scaling σ, not its CV** (F-1). |
| **D. Multiplicity, weighting and the denominator** | **PASS** | Conversations are drawn with replacement, `n_clusters` per replicate; all questions of each draw are taken; multiplicity is preserved; the mean divides by the total selected question **slots**. Verified against slot-, cluster- and distinct-question estimators on a fixture where all three differ, and end to end against an independent reimplementation of acceptance-record §4 (interval discrepancy `0.000e+00`). |
| **E. Rejection, output protection, execution gates** | **PASS WITH FINDINGS** | 13 record-level rejection cases all refuse; `safe_write_json` refuses files, zero-byte files and directories and leaves existing content intact; the module imports only `json`, `math`, `pathlib`, `numpy` and no `open`/`eval`/`exec` appears anywhere. **But cluster labels are unvalidated** (F-2), duplicate question ids escape the validator (F-3), and the real-data gate is declarative only (F-6). |
| **F. Tests, forbidden apparatus, and the preparer's self-check** | **PASS WITH FINDINGS** | The forbidden apparatus is genuinely absent from executable code — semantically, not just lexically. **The preparer's own self-check is not sound**: it missed 6 of 13 mutations, including a reintroduced `Δ/G` ratio and a wrong bootstrap denominator (F-4, F-5). |

---

## 3. Forbidden apparatus — verified semantically, not by keyword

The acceptance record §1 lists nine dead items. Verified **absent from executable code** by AST, not
by string search:

- **No ratio of `Δ` to `G` under any name.** Every division in the module was enumerated: exactly two
  exist, `1.0 / np.where(ok, sigma, 1.0)` and `sigma.std(ddof=0) / mean_sigma`. Neither operand is a
  reported quantity. No identifier in the module contains `rho`, `ratio`, `verdict`, `band`, `floor`
  or `category`.
- **The four withdrawn cut points do not occur at all** — not as literals, not in strings. Every
  occurrence of `1.0`, `-1.0` and `2` was located line by line and each is structural (the `ε`
  fallback `d = 1`, the Haar sign fix, `C.ndim != 2`, `json.dumps(indent=2)`, the `[0, 1]` score
  range). There is no `2.0` pp floor.
- **No comparison anywhere in the module tests a reported quantity against a threshold or band.**
- **The output schema is clean.** Its full key set is `{G_bar_pp, G_bar_scaled_pp, Delta_bar_pp,
  per_seed_G_pp, per_seed_G_scaled_pp, per_seed_Delta_pp, n_question_slots, scheme, replicates,
  percentiles, note, lo, hi, spans_zero, n_clusters, limit, degenerate_coords, flagged,
  cv_sigma_before, cv_sigma_after}` — no verdict, label, band or ratio key.
- **No categorical label appears in any string outside the module docstring.** The module docstring
  does name several of them, in order to declare them absent. That is judged acceptable: naming a
  thing to forbid it is not implementing it.
- **The withdrawn R2 §4 wording is gone.** `question_bootstrap` carries the *binding §2 replacement*
  ("does not model within-conversation dependence and may therefore understate uncertainty. No claim
  is made about interval width"), not the withdrawn phrase. `cluster_bootstrap` carries R2's accepted
  "its width is an outcome and is not forecast". `_percentiles` carries binding §3 verbatim in
  substance, including that an interval spanning zero is not evidence of absence and not a claim of
  practical equivalence.
- **`DEGENERATE_FLAG_THRESHOLD = 4` is a diagnostic, not a decision input.** It is read in exactly
  one place, to set `flagged`, and `flagged` is consumed by nothing.
- **Linearity is a tolerance check at `1e-12`, not a bitwise assertion**, as binding §6 requires.

### Is the preparer's own "forbidden token" self-check sound?

**No. It looks sound and is not.** Two independent demonstrations:

1. **Scope.** The scan is `src.lower().split('"""', 2)[2]`, which excludes the module docstring —
   1,321 characters, and the one region of the file that actually contains `indeterminate`, `ratio`,
   `relative scale unsuitable` and `verdict`. The exclusion is defensible in itself, but it means the
   check is carved precisely around its own counter-examples. (Function docstrings *are* inside the
   scanned region, which is a point in its favour.)
2. **Power.** Mutation **M1** adds a real `Δ/G` ratio to the returned schema under the neutral name
   `relative_change`. The preparer's entire 74-check suite **passes**. Only a semantic check catches
   it. A token scan cannot see a forbidden quantity that is spelled differently.

Two further scan lines are muddled rather than wrong: `"band" not in body.replace("block", "")` —
removing `block` has no bearing on whether `band` occurs — and
`"distinct" if False else "partition"`, a dead conditional left in a shipped needle argument.

---

## 4. Mutation results — the actual measure of both suites

Thirteen mutations were applied to a throwaway copy of the core (the candidate files in the
repository were never touched) and both suites were run against each.

| mutation | preparer's suite | this review |
|---|---|---|
| M1 reintroduce a `Δ/G` ratio under a neutral name | **misses** | kills |
| M2 divide by **distinct** questions instead of slots | **misses** | kills |
| M3 cluster-average instead of slot-weight, inside `cluster_bootstrap` | **misses** | kills |
| M4 resample each seed column independently | kills | kills |
| M5 fire the degenerate flag at 4 instead of above 4 | **misses** | kills |
| M6 turn the `ε` fallback into a clip | kills | kills |
| M7 use `ddof=1` | kills | kills |
| M8 apply the pp factor twice | kills | kills |
| M9 always report `spans_zero = False` | **misses** | kills |
| M10 report a genuine `CV(σ)` after rescaling | **misses** | kills |
| M11 allow results to be overwritten | kills | kills |
| M12 open the real-data gate by default | kills | kills |
| M13 stop reporting duplicates | kills | kills |

**Preparer's suite: 7 of 13. This review: 13 of 13.**

M2 and M3 matter most. The preparer's README headline — "Cluster multiplicity is demonstrated …
drawing A twice returns exactly `1.0` pp over `6` slots, and drawing A then B returns `3/8`" — is
true but does not demonstrate what it claims. On that fixture (three questions worth `1.0`, five
worth `0.0`) the slot-weighted and the distinct-question estimators return **the same numbers**, so
the test cannot tell them apart. The bound denominator survives only because a fixture with a third
cluster of a different size and value (`CCB`: slots `1.7778`, distinct `1.1429`, cluster-averaged
`2.6667`) separates them — and because the whole bootstrap path was re-derived independently.

**The code is nevertheless correct on this point.** Both bootstraps reproduce an independent
reimplementation of acceptance-record §4 with an interval discrepancy of exactly `0.000e+00`, on a
fixture with five unequal clusters.

---

## 5. Vacuous checks in the preparer's suite

Static audit of all 51 `check()` calls and 16 `expect_violation()` calls found five whose asserted
condition is a literal or a tautology. Four of the five are **assertion-by-non-raising** — the
preceding call on the same line would throw if the property failed, and the literal `True` is only a
reporting device. That idiom is acceptable, if opaque.

**One asserts nothing at all:**

```python
check("an interval that contains zero is flagged, not reinterpreted",
      m.question_bootstrap(g_rand - 8.0, g_rand - 8.0, seed=5, replicates=300)["G_bar_pp"]["spans_zero"] in (True, False))
```

`x in (True, False)` is true for every boolean. This is exactly the check that mutation **M9**
walks past. The property it names — that an interval containing zero is reported as containing zero
— is a binding §3 requirement, and it is currently untested by its own suite. It does hold in the
candidate; this review tests it directly.

---

## 6. Findings

Full table in `FINDINGS.md`. Summary:

### Must be fixed before this core is used to produce any record (2)

- **F-1 — `cv_sigma_after` is a standard deviation, not a CV.** `scale_matrix` computes
  `cv_sigma_before` as `σ.std/σ.mean` (a genuine CV) but `cv_sigma_after` as
  `(C @ D).std(axis=0).std(ddof=0)` — the spread of the post-scaling σ with **no division by its
  mean**. R1 §1 requires `CV(σ)` before *and* after. The two coincide only when every post-scaling σ
  is 1, i.e. when no coordinate took the `ε` fallback — which is precisely the case the diagnostic
  exists to describe. Measured on a 20-degenerate-coordinate archive: reported `0.406116`, true CV
  `0.512989`. R1 §4 requires every diagnostic to be published unconditionally, so this would enter
  the record under a wrong name. It cannot change any of the three reported quantities.
  *Fix: divide by `post_sigma.mean()`, or rename the key to `sd_sigma_after`.*

- **F-2 — cluster labels are not validated, and a bad label silently changes the denominator.**
  `cluster_bootstrap` checks only that `len(labels) == n_questions`. A `NaN` label becomes a cluster
  whose member set is **empty** (because `labels == nan` is false everywhere), so every replicate
  that draws it silently omits those questions from both the numerator and the slot denominator —
  demonstrated: a draw of three clusters covering all ten questions produced `n_question_slots = 8`.
  Mixed-type labels (`1` and `"1"`) split one conversation into two clusters. When every draw lands
  on the empty cluster the failure surfaces as a misleading `"empty question selection"`.
  This is exactly the class of silent acceptance the acceptance record §7 bars.
  *Fix: reject non-finite, null and mixed-type labels, and require every cluster to be non-empty.*

### Real, not blocking (4)

- **F-3** duplicate question ids pass `validate_per_question_records` unnoticed (its `expected` set
  comprehension de-duplicates them). The result is never silently wrong — every variant tested
  aborts — but it aborts with an unhandled `IndexError`, not a `DesignViolation` naming the cause.
- **F-4** the preparer's forbidden-token self-check is not sound (§3 above).
- **F-5** the preparer's cluster-multiplicity fixture cannot distinguish slot-weighting from
  distinct-question weighting, and the README states otherwise (§4 above).
- **F-6** `require_real_data_authorization` is **declarative only**: no function in the core calls
  it, and its default argument is bound at import, so assigning
  `module.REAL_DATA_EXECUTION_ENABLED = True` does **not** open it. The direction of that surprise is
  fail-closed, and the core genuinely has no corpus-touching path, so nothing is unsafe today. But
  the gate as written enforces nothing; it becomes real only when the unwritten runner calls it, and
  the module constant is not the live switch a reader would assume.

### Cosmetic / hardening (6)

- **F-7** `aggregate` silently accepts negative indices (they wrap: `idx=[-1]` equals `idx=[9]`) and
  silently truncates float indices. Not reachable from either bootstrap.
- **F-8** an out-of-range index raises `IndexError`, not `DesignViolation`.
- **F-9** a boolean score passes validation as `float(True) = 1.0`.
- **F-10** an empty (`n=0`) or single-row archive is accepted silently and yields `D = I`.
- **F-11** one dead conditional (`"distinct" if False else "partition"`) and one no-op string
  transform (`body.replace("block", "")`) left in the shipped test file.
- **F-12** the linearity tolerance is **absolute** at `1e-12`. That is what binding §6 says, and it
  is honoured literally. Measured headroom under an adversarial worst case (±100 pp gaps, 4,000
  slots, 400 replicates) is about **19.5×** — comfortable, but not large. Recorded so that a future
  larger panel does not trip it for a reason unrelated to the science.

### Requirements this core correctly leaves to the unwritten runner (not defects)

- Only four arms enter the three quantities; `NATIVE` and `SCALED_NATIVE` are controls and do not
  appear in `G` or `G_scaled`. Binding §4 step 6's "all six arms" is satisfied vacuously for them.
  The validator does require records for all six arms at all ten seeds, matching R1 §2's
  `n_questions × 10 × 6` schema.
- No bootstrap RNG seed is fixed as a module constant; it is a caller argument. Reproducibility of
  the published interval therefore depends on the runner, and the seed should be preregistered.
- The mandatory `[LONGMEMEVAL SINGLE-COMPONENT FINDING — INHERITED FROM TASK 3A.1; PROVENANCE
  VERIFIED, NOT RECOMPUTED HERE]` tag is not emitted anywhere. That is a reporting obligation on the
  runner, and R2 §4's prohibition on defining a cluster bootstrap for LongMemEval is likewise the
  runner's to honour — this core will happily cluster-bootstrap anything it is handed.
- Nothing in the core applies `D` to a query outside `check_identity`; the runner must apply the
  identical `D` and estimate nothing from the query.
- `σ` exactly equal to `ε` takes the divide branch (`d = 1e12`), because R1 §1 says the fallback
  applies when `σ < ε`. Faithful to the design, and a razor edge worth knowing about.

---

## 7. Verdict

**`PASS WITH FINDINGS`.**

The computation core implements the accepted design. The three quantities, their percentage-point
unit, the pairing across arms and across the fixed seed panel, the scaling operator's `ddof`,
fallback and flag semantics, and — most importantly — the cluster bootstrap's bound algorithm
including its slot denominator, are all correct, and each was confirmed against an independently
written reference rather than against the preparer's own tests. The apparatus the acceptance record
declares dead is genuinely absent from executable code, semantically and not merely lexically.

**Real blockers that must be fixed before this core could ever be used to produce a record: two —
F-1 and F-2.** Neither can change any of the three primary quantities on well-formed input; both
would put a wrong number into the unconditionally-published record (`cv_sigma_after`) or let a
malformed input silently change a denominator (cluster labels). Both are small, local fixes.

**Everything else is cosmetic or hardening**, except F-4 and F-5, which are findings about the
*preparer's evidence*, not about the code: the suite passes 74/74 but stops 7 of 13 mutations, and
the README's cluster-multiplicity claim overstates what its fixture can show. The code survives
because it is right, not because those tests proved it.

**Single next concrete step:** hand F-1 and F-2 back to the preparer as a two-line correction plus
a cluster-label validator, with the boundary and mutation tests from
`audit_v52_membership_impl_review_2026_09_07/scripts/` adopted into the candidate suite; then this
review can be closed by re-running both suites against the corrected blobs. The runner remains
unwritten and unauthorized, and nothing in this review moves that.
