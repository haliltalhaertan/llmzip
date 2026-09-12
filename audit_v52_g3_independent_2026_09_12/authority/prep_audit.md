# Independent review — V52 membership execution preparation v1

**Candidate commit reviewed:** `ed4e22c520b7dc0ae2f43f915e0c621070c72a87`
**Branch:** `codex/v52-membership-execution-prep-2026-09-08`
**Namespace:** `drafts/v52/membership_execution_prep_v1_2026_09_08/`
**Parent:** `07ec929243068914676a0f30efd10c9f294c7e71`
**Review date:** 2026-09-08
**Reviewer:** independent session, cold start (see "Cold-start declaration" below)

---

## VERDICT: PASS WITH FINDINGS

**Scope of this verdict.** It applies **only to the three prepared computation functions as
written** — M-1 (`Representation`), M-2 (`score_archive` and its controls) and M-3
(`assemble_in_memory`) — exercised on synthetic fixtures in the accepted interpreter.

This verdict explicitly:

- **does NOT authorize real data.** No corpus was read, opened, hashed or scanned during this
  review, and nothing here licenses doing so.
- **does NOT accept the five open integration obligations.** They are classified below, not
  resolved. I resolved none of them and changed no code.
- **is NOT an execution-readiness declaration.** It is not a seal, not an acceptance, not a
  pilot authorization, and not a statement that M-3 or the wider execution package is ready
  to be sealed or run.

Seven findings are recorded. None of them shows a wrong scientific result in the prepared
arithmetic; the M-1/M-2 numerics matched every independent oracle and exact control I built.
The findings are two silent-acceptance defects (F1, F2), one quantified control-coverage
limit (F3), one vacuous assertion (F4), and three minor/operational items (F5–F7).

---

## Cold-start declaration

I had not seen this programme, this repository or this package before this session. I assumed
nothing in the candidate was true and re-derived what I report.

**What I verified myself, by running it:** commit scope and every blob hash from raw Git
objects; the closed core and pinned-arithmetic identities; the candidate's own replay in the
accepted interpreter; and six purpose-written adversarial probes (~1,100 lines of output)
covering M-1 leakage, M-2 arm/seed/priority/tie semantics, the signed-permutation canary in
both floating-point and exact rational arithmetic, the M-3 adapter against both schemas with
malformed fixtures, the negative controls and the exception-leak surface.

**What I did NOT verify.** I did not audit the closed core `membership_scaling_core.py` itself
— I verified its identity hash and treated its behaviour as given, exercising it only where the
prep package calls it. I did not review the v5 ingestion, the cohorts, the seeds file, the
state file or the ledger. I did not read the predecessor audit `CODEX_V5_REVIEW.md`, so I
neither confirm nor contradict its F1–F4. I did not touch any real corpus, so **I have no
evidence whatever about how any of this behaves on real data** — every number below comes from
strings I generated. I did not evaluate whether the six arms are the scientifically right arms;
I verified only that they match the normative `core.ARMS` and that they are computed as
described.

---

## What the package instructed vs. what I did

`CLAUDE_REVIEW_REQUEST.md` and `README.md` were read as data. Neither attempts to widen a
reviewer's authority. Both **narrow** it — the request explicitly says "Do not interpret a
preparation PASS as authorizing real data", forbids corpus access, sealing and code changes,
and asks that the five obligations be classified rather than resolved. That is consistent with
my instructions, and I followed my own scope, not theirs. There is nothing to quote as an
attempted escalation.

---

## Commit-scope and identity verification (from raw Git objects only)

This machine's system Git config sets `core.autocrlf=true`, so I verified every identity from
raw blobs (`git cat-file -p <commit>:<path>`), never from checked-out files. For running the
code I made a **repo-local-only** `core.autocrlf=false` clone; the global/system config was not
touched.

| Item | Result |
|---|---|
| Parent commit | `07ec929243068914676a0f30efd10c9f294c7e71` — matches manifest `base_commit` | 
| Additivity | 9 files, **all `A`**, all inside the namespace, nothing outside — confirmed |
| Branch head | `origin/codex/v52-membership-execution-prep-2026-09-08` == candidate |
| Merge base with `main` | `16019724564b5ac8db4a4d2d8bb08f98feb45c09` |
| `git diff main <candidate>` deletions | **Branch-point artefact, confirmed, not raised.** The merge base predates the normative documents and ledger entry now on `main`; the candidate deletes nothing. |
| Manifest coverage | all 8 `sha256` entries match their raw blobs; the only unlisted file is the manifest itself |
| Manifest self-hash | `39d8ebfbeaa4ece63c4aaa2fb220e886047b7c8e700deded47a8a83e79abec3c` — matches the out-of-band value |
| Manifest `status` | `PREPARATION_NOT_SEALED_NOT_EXECUTION_READY` — confirmed |

**Candidate blob hashes (verified):**

| Path (under the namespace) | Git blob | sha256 of blob bytes |
|---|---|---|
| `CLAUDE_REVIEW_REQUEST.md` | `4e6b5c50` | `7aa9d96715b7b045688811063869bdcb44027f85d607a59a715b454f215e3c98` |
| `PAYLOAD_HASHES.json` | `bc6e5101` | `39d8ebfbeaa4ece63c4aaa2fb220e886047b7c8e700deded47a8a83e79abec3c` |
| `README.md` | `7ae67014` | `9959f57723a5ec510fa436728b1337fbef7719aba4f3eb38921b119dff1e8a8a` |
| `pipeline.py` | `6b41a424` | `db417ade3a4e2e1ceca342dbf5b4a0fde2562296b91932126ebeca01652be5ae` |
| `replay.py` | `db8a8d78` | `30be19caef5c2cfd642478f7e6515a8069ae42a7d70006ddcb81f9d5762162f9` |
| `test_pipeline.py` | `f87bc8ff` | `cfd3263686de93bf87ca8b5336ac080fd7f3d759bfe1341bfd2e49e735a9bd81` |
| `evidence/RESULTS.json` | `d42c39c3` | `178ec719013005c41cd127beef187b0dfcac37bda1a123a2f47bc36dd08adcb3` |
| `evidence/stderr.txt` | `fcb7b63d` | `4c3f8e9e43fee2b5b886f885d3a62800bf10bf69a82bba0ea668ea19bbbcbf02` |
| `evidence/stdout.txt` | `e69de29b` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |

**Declared provenance, independently confirmed from raw blobs:**

| Claim | Verified |
|---|---|
| Closed core `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` | sha256 `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` — matches the constant pinned in `pipeline.py`, and matches the file actually loaded at runtime |
| Pinned arithmetic `692f599e…:research/v52/locomo_sign_mechanism_replication.py` | sha256 `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` — commit and blob both exist and match |

---

## Replay

Run from a clean checkout in the accepted interpreter, **fresh output directory, synthetic
only**:

```
python -B drafts/v52/membership_execution_prep_v1_2026_09_08/replay.py <fresh-dir>
```

Exit code 0; 7/7 tests OK. My `stderr.txt` and `RESULTS.json` match the committed evidence
(modulo the wall-clock timing line). Interpreter 3.13.15, numpy 2.3.5, scipy 1.17.0,
scikit-learn 1.8.0, pandas 2.2.3.

**Does `replay.py` check what it claims?** Substantially yes, with two honest limits worth
stating.

- It *does* pin the interpreter to exactly 3.13.15 and the four package versions exactly,
  refusing otherwise; it *does* force `PYTHONHASHSEED=0` and the four thread variables to 1 in
  the child; it *does* refuse to reuse an output directory (`mkdir(exist_ok=False)`), which is
  genuine overwrite protection for the evidence folder; and it *does* record the sha256 of each
  `*.py` in the package alongside the exit code.
- **Limit 1:** the recorded `sources` hashes are of the files **as they sit on disk at replay
  time**, not of the Git blobs. On a default Windows checkout those differ (see F6). The hashes
  therefore attest "what ran", which is the useful property, but they are not by themselves
  evidence of which commit ran.
- **Limit 2:** `replay.py` reports `{"exit_code": 0, "test_methods": 7}` where `7` is a
  **hard-coded literal**, not a count read back from the run. If a test method were deleted,
  the replay banner would still say 7. The README is nonetheless accurate that seven is the
  method count and says so explicitly rather than inflating it.

---

## Per-area findings

| Area | Verdict | Basis |
|---|---|---|
| M-1 representation — archive-only fitting | **PASS** | 11 fitted-state fingerprints (both vocabularies, both `idf_`, both components matrices, `explained_variance_`, `mu`, `C`, `D`, diagnostics) byte-identical before and after adversarial queries |
| M-1 — no query leakage into the transform | **PASS** | No `fit`/`fit_transform`/`partial_fit` call occurs during `queries()`; feature dimension unchanged by unseen vocabulary; a query batched with another gives bit-identical output to the same query alone |
| M-1 — memory-only fitting | **PASS** | Audit-hook instrumentation recorded **0** `open()` events of any kind during `Representation()` construction, and **0** write-mode opens across all six probes |
| M-1 — query reuses archive-fitted objects | **PASS** | Hand-rebuilding the query path from the fitted estimators reproduces `queries()` **bitwise** (max abs diff 0.0) |
| M-1 — pinned arithmetic parity | **PASS** | `lsa.random_state=5101`, `svd.random_state=5204`, `SOURCE_LATENT_DIM=32`, `n_components=96`, `TOPK=3`, `N_NUISANCE=20` all match the AST-extracted constants of `a6ecee02` |
| M-1 — closed core `scale_matrix` unchanged | **PASS** | `rep.D` bitwise equals `core.scale_matrix(rep.C)`; core loaded by explicit path with a verified hash |
| M-2 — six arms and their ORDER | **PASS** | Emitted order equals `core.ARMS` exactly: NATIVE, SCALED_NATIVE, B32_FRESH, SCALED_B32, RANDOM32_FRESH, SCALED_RANDOM32 |
| M-2 — ten paired seeds are the CURRENT panel | **PASS** | `ROTATION_SEEDS` 60001–60010 paired positionally with `PARTITION_SEEDS` 70001–70010, both taken from the core, not literals; no historical panel value appears |
| M-2 — scaling BEFORE rotation | **PASS** | Independent reconstruction of all six cells reproduces the candidate's scores exactly; `(C@D)@rs` and `(C@rs)@D` shown to differ (max diff 1.26e+01), so the order is load-bearing and correct |
| M-2 — nuisance priorities reused, not redrawn | **PASS** | Exactly **20** nuisance-seeded `default_rng` calls per `score_archive`, drawn once before the seed loop and reused across all 10 seeds × 6 arms |
| M-2 — random-membership draw order | **PASS** | `draw_rotation_blocks` takes q32 then q64 from one stream; `random_membership` uses an independent generator seeded by the partition seed, so no cross-contamination of draw order |
| M-2 — matched block identity | **FINDING F4** | The guarantee holds structurally (both rotations are built from the same `a`, `b` objects — verified), but the assertion as invoked is vacuous |
| M-2 — top-k tie handling | **PASS** | Bit-identical to the pinned `a6ecee02` implementation over 4,000 fuzz cases with all three branches exercised (343 small / 922 all-boundary / 2,735 partial), including all-distances-equal and rounded-priority tie cases |
| M-2 — fractional recall / gold accounting | **PASS** | Denominator is `len(gold)` (recall, capped below 1.0 when `\|gold\| > k`), consistent with the core validator's `[0,1]` range; gold validation rejects empty, bool, negative, out-of-range, duplicate, numpy-int, float and non-list |
| Native anchor — mandatory and ungenerated | **PASS** | Required positional argument; nothing in `pipeline.py` generates, defaults or derives it; wrong / missing / mis-length / out-of-range / NaN / non-`float` anchors all refused with distinct codes |
| Native anchor — tolerance | **PASS** | `abs(value - anchor) <= core.TOL` with `TOL = 1e-12`, confirmed at the boundary with a strictly interior anchor |
| Native / scaled-native sign and distance controls | **PASS** | `check_identity` passes on the fitted `D` and correctly detects a negated coordinate; NATIVE and SCALED_NATIVE Hamming distances identical for every query, hence the two arms coincide in every record (a designed invariance, not a bug) |
| Rotation norm/dot tests | **PASS** | Worst observed: norm 1.78e-15, dot 4.26e-14, against `TOL = 1e-12` |
| Signed-permutation canary — aborts on exact zeros | **PASS** | Aborts with `E-M-031` in both mixed-zero directions; does not fire on an all-zero coordinate (correct — `-0.0 >= 0` is True) |
| Signed-permutation canary — not chosen after seeing data | **PASS** | `perm` and `signs` are fixed source literals; no RNG, no data dependence, no replacement-canary selection anywhere in the module |
| Signed-permutation canary — coverage | **FINDING F3** | Covers only 48 of 96 coordinates |
| M-3 — both schemas, well-formed | **PASS** | LoCoMo and LongMemEval fakes both produce complete, correctly-ordered record sets with per-archive diagnostics carrying `archive_ordinal` plus all five `scale_matrix` diagnostics |
| M-3 — ordering | **PASS with obligation-3 caveat** | LoCoMo ordinal comes from ingestion (`conversation["index"]`); LongMemEval ordinal is `enumerate(cohort_ids)` — chosen by this package and demonstrably outcome-affecting |
| M-3 — malformed fixtures | **FINDING F7** | Missing schema keys raise bare `KeyError`/`TypeError`, not `E-M-*` |
| M-3 — empty cohort | **FINDING F2** | Silently returns a successful empty result |
| M-3 — record validation completeness | **PASS** | Validated twice (per archive, then whole cohort); a cohort id never scored is caught as 60 missing records |
| Negative controls — non-finite | **PASS** | NaN/±Inf in the archive, in `D`, in distances and in priorities are all refused (`DesignViolation`, `E-M-030`, `E-M-012`, `E-M-013`) |
| Negative controls — real gate | **PASS** | `run_on_real_corpus` refuses under every argument shape tried, including `enabled=True`, `force=True`, `authorized=True`; `core.REAL_DATA_EXECUTION_ENABLED` is `False`; `core.require_real_data_authorization()` raises |
| Exception leakage — caller TEXT | **PASS (notably good)** | The flag-then-raise-outside-the-handler pattern genuinely works: a text canary appears on **no** surface — not `str`, `repr`, traceback, `__cause__`/`__context__` (chain is empty), stdout or stderr |
| Exception leakage — caller IDENTIFIERS | **FINDING F1** | Question ids **do** reach `str(e)`, `repr(e)` and the traceback |
| Audit hook not claimed as a sandbox | **PASS** | README says the refusing entry point "is not a universal security boundary"; `pipeline.py` installs no audit hook at all; no over-claim found |
| No acquisition / writer / bootstrap / seal | **PASS** | No network, subprocess, pickle or serialization verbs in `pipeline.py`; the only filesystem call is one `read_bytes` for the core hash |

---

## Findings

### F1 — Caller-supplied question identifiers reach exception messages (real defect, moderate)

The package takes deliberate care that caller **text** never reaches an exception surface, and
that care works (verified). Caller **identifiers** are not protected the same way. Three
reachable paths put a fixture-supplied id into `str(e)`, `repr(e)` and the traceback:

Minimal reproducer (synthetic, ids under 15 characters):

```python
# (a) LoCoMo: a conversation carrying a question that is not in cohort_ids
P.assemble_in_memory(
    {'benchmark': 'LoCoMo', 'cohort_ids': ['s0'], 'questions_with_empty_gold': [],
     'conversations': {'cv': {'index': 0, 'units': UNITS, 'questions': {
         's0': {'text': T[4], 'gold_rows': [4]},
         'CANARYID_ZQ8': {'text': T[9], 'gold_rows': [9]}}}}},
    {'s0': a0})
# -> KeyError: "'CANARYID_ZQ8'"      <- raised by [native_anchors[q] for q in qids]

# (b) LongMemEval: a cohort id with no question record
#     -> KeyError: "'CANARYID_ZQ8'"  <- raised by ingested['questions'][qid]

# (c) LoCoMo: a cohort id never scored
#     -> DesignViolation: "record validation failed: 60 missing record(s),
#        e.g. [('CANARYID_ZQ8', 60001, 'B32_FRESH'), ...]"
```

Paths (a) and (b) are also *bare* `KeyError`s, i.e. not `PipelineError`, so a caller catching
`PipelineError` will not catch them. Path (c) originates in the closed core's validator, which
formats `key` and `repr(r)[:120]` into its message — that is core behaviour, outside this
package's authority to change, but the prep package is what makes it reachable with
caller-controlled ids.

Whether question ids count as sensitive is a policy question I cannot settle. I raise it
because the package's own text-suppression design shows the authors treat exception surfaces as
a leak channel, and identifiers are corpus-derived. **Recommendation:** decide the policy
explicitly; if ids are in scope, validate `set(all question ids) == set(cohort_ids)` up front
and raise a code-only `PipelineError`.

### F2 — An empty cohort silently returns a successful empty result (real defect, moderate)

```python
P.assemble_in_memory({'benchmark': 'LongMemEval', 'cohort_ids': [],
                      'questions_with_empty_gold': [], 'questions': {}}, {})
# -> {'records': [], 'diagnostics': []}      no exception
```

Same for LoCoMo with an empty cohort, and for LoCoMo where `cohort_ids` is empty but
conversations are present. `core.validate_per_question_records([], [])` also accepts, because
its `expected` set is empty, so nothing is missing and nothing is invalid. `assemble_in_memory`
has no minimum-cohort guard.

This is the most consequential finding, because it is a **silent success**: a finalizer
consuming this record set would see a well-formed, apparently valid, zero-row result rather
than a refusal. Obligation 4 (the finalizer) is precisely where that would matter.
**Recommendation:** refuse an empty cohort with an `E-M-*` code, and require the number of
archives and records to be non-zero and consistent with the cohort size.

### F3 — The signed-permutation canary covers only half the coordinates (real defect, moderate; coverage)

The canary is correct where it looks, and I confirmed the property it tests is a genuine
mathematical fact rather than a floating-point artefact — in **exact `Fraction` arithmetic**
with no floating point anywhere, Hamming distance is invariant under the signed permutation
when there are no exact zeros, and provably not invariant when an archive coordinate is exactly
zero while the query coordinate is not.

But the canary uses **one fixed sign vector**, `signs = [+1,-1,+1,-1,…]`. A zero-coordinate
sign break can only be observed at a coordinate the canary actually negates. After the reversal
permutation, new index `j` holds old index `95-j` and is negated when `j` is odd — so exactly
**48 of the 96 coordinates are negated, and 48 are never negated**. A break confined to the
other 48 passes undetected:

```python
C = rng.normal(size=(12, 96)); Q = rng.normal(size=(3, 96))
C[:, 0] = 0.0; Q[:, 0] = 1.0   ; P.controls(C, Q, np.eye(96))  # -> E-M-031  (aborts)
C[:, 1] = 0.0; Q[:, 1] = 1.0   ; P.controls(C, Q, np.eye(96))  # -> passes   (NOT detected)
```

This is a coverage limit, not a wrong result — the canary never reports a false pass on a
coordinate it covers, and it aborts rather than reinterpreting the zero, exactly as the README
says. But the README's phrasing ("The canary deliberately aborts if that happens") reads as
though the condition is detected in general, and it is detected on half the coordinate space.
**Recommendation:** either state the 48/96 coverage in the README, or use a sign vector that
negates every coordinate (e.g. all `-1`), which would make the control total. Choosing between
those is a design decision I am not authorized to make, and it must not be made by observing
data.

### F4 — `assert_matched_blocks(a, b, a, b)` is vacuous (real defect, minor)

`pipeline.py` calls the matched-Q control as `core.assert_matched_blocks(a, b, a, b)`. The core
implementation computes `max|q32_a - q32_b|` and `max|q64_a - q64_b|`; with the same objects on
both sides these are `0.0` by construction. **The assertion cannot fail for any input.** I
confirmed the control itself works when given genuinely different blocks (it raises
`DesignViolation`), so the function is fine — the call site is what is empty.

The underlying property does hold, structurally and verifiably: `rs` and `rr` are both built
from the same `a`, `b` objects, and I confirmed the identical `q32` block is embedded in the
constructed rotation. So this is a false-assurance issue rather than a correctness issue: the
line looks like a control and provides no evidence. **Recommendation:** either remove it as
noise, or make it meaningful by re-deriving one pair independently
(`a2, b2 = core.draw_rotation_blocks(seed)`) and asserting against that.

### F5 — Error code `E-M-005` is unreachable (real defect, minor, fail-closed)

In `Representation.__init__`, `require(d >= 1, 'E-M-005: insufficient features')` sits **inside**
the `try:` whose `except Exception:` sets `failed = True`, so the `PipelineError` it raises is
swallowed and re-reported as `E-M-006`. Reproducer:

```python
tiny = ['the a of and alpha alpha alpha'] * 100   # vocabulary collapses after stop-words
P.Representation(tiny)     # -> E-M-006: representation fit failed   (never E-M-005)
```

Fail-closed and harmless to results, but the specific diagnostic is dead and a maintainer
reading the code would reasonably expect it to fire.

### F6 — The core identity gate breaks on a default checkout on this platform (real defect, minor, operational, fail-closed)

This machine's system Git config sets `core.autocrlf=true` and the candidate tree contains no
`.gitattributes`. A default clone therefore materialises the closed core with CRLF line endings:

```
sha256(checked-out membership_scaling_core.py) = 5dc4c1672928a3e8dc8020c9a0132b53b9fbea1a4455b1d5bdc7ea95ff1bbb40
CORE_HASH pinned in pipeline.py                = bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72
```

so `import pipeline` fails at module scope with `RuntimeError: E-M-001: core identity mismatch`
and `replay.py` cannot run. I reproduced this, then obtained a byte-exact tree with a
**repo-local** `core.autocrlf=false` and confirmed replay then reproduces the committed evidence
exactly.

The behaviour is correct and fail-closed — a byte-pinned gate *should* refuse bytes that differ.
The finding is about **reproducibility**: an independent party following the README's replay
command on a default Windows clone will hit a hard failure with no hint of the cause. Adding a
`.gitattributes` is a repository-policy decision and I am explicitly forbidden from making it, so
I only record the fact. **Recommendation:** the Continuity Lead decides whether to normalise line
endings repo-wide or to document the required clone settings in the replay instructions.

### F7 — M-3 has no schema validation (real defect, minor)

`assemble_in_memory` indexes the ingestion result directly. Missing or wrong-typed keys surface
as bare `KeyError`/`TypeError` rather than `E-M-*` `PipelineError`s:

| Malformed fixture | Result |
|---|---|
| missing `questions_with_empty_gold` / `cohort_ids` / `questions` / `conversations` | `KeyError` |
| conversation missing `index`; unit missing `text`; question missing `gold_rows` / `units` | `KeyError` |
| `ingested` is a list / `None` | `TypeError` |
| non-empty `questions_with_empty_gold` | `E-M-026` ✓ |
| unknown benchmark | `E-M-028` ✓ |
| anchor coverage mismatch | `E-M-027` ✓ |

The three declared refusals work. The gap is that everything else is undefended, and the README
describes M-3 as having "complete record validation" — that is true of the *records* it produces
but not of the *ingestion result* it consumes.

---

## Non-blocking observations

**(ii) Optional improvements**

- `E-M-030` (positive-diagonal requirement) is unreachable through the public path, because
  `score_archive` always passes `rep.D`, and `scale_matrix` never emits a non-positive diagonal
  (degenerate coordinates keep `d = 1.0`). It is reachable only by calling `controls` directly,
  which the candidate's own test does.
- The port of `topks_by_hamming` omits the pinned source's `if need <= 0:` branch. **This is
  behaviour-preserving and I verified it.** By definition of the k-th order statistic, the set
  `{i : d_i < d_(k)}` has at most `k-1` elements, so `need = k - |strict| >= 1` always; the branch
  is dead code in the pinned source. I also confirmed it empirically: `need <= 0` occurred 0 times
  in 20,000 randomised tie-heavy cases. Worth a source comment so a future reader does not read
  the omission as a divergence.
- NATIVE and SCALED_NATIVE are provably identical arms (a positive diagonal cannot change a
  zero-threshold sign code, and `E-M-024` asserts it every question). Carrying both is a
  deliberate invariance control, but it means two of the six "arms" contribute one arm's worth of
  information. Worth stating in the README so downstream aggregation does not treat them as
  independent.

**(iii) Wording / claim accuracy**

- The README is unusually honest and I found no overclaim. It discloses its own development
  failures (the rejected NumPy metadata guard; a test that wrongly demanded bit equality between
  SVD `fit_transform` and `transform`, corrected to a 1e-12 numerical comparison), states that
  seven is a method count and not an inflated case count, states that its tests are
  implementation-team checks and not audit, and states that the refusing entry point is not a
  security boundary. All of these match what I observed.
- One qualification: "complete record validation" (README line 18) is accurate for emitted
  records and inaccurate for consumed ingestion results — see F7.
- One qualification: the canary description implies general detection of the zero-coordinate
  break — see F3.

**Test gaps (what the package does not test that it should)**

1. **Nuisance-priority reuse is never asserted.** The most important M-2 determinism property
   has no test. I verified it by instrumenting `default_rng`; the package should assert it.
2. **No malformed-fixture tests for M-3 at all.** Both connector tests use well-formed fakes.
3. **`E-M-026`, `E-M-027`, `E-M-028` are all untested** — every one of M-3's own declared
   refusals.
4. **The empty cohort is untested** — which is how F2 survived.
5. **The exception-leak suppression is untested.** The flag-then-raise pattern is a deliberate,
   subtle and *correct* design, and a refactor could silently break it (moving the `raise` inside
   the `except` would attach `__context__`). It deserves a regression test.
6. **`E-M-022` (anchor value type/range) is untested**; only `E-M-021` and `E-M-025` are.
7. **Parity fuzzing is thin.** `test_old_source_arithmetic` uses `n ∈ {2,3,4,110}` with
   distances drawn from `U(0,96)`, which rarely stresses the boundary branches. My 4,000-case
   fuzz with `hi ∈ {1,2,3,5,97}` was needed to exercise the all-boundary branch 922 times.
8. **The canary's partial coverage is untested and undocumented** (F3).
9. `test_topk_oracle` compares **sets**, so ordering within a returned selection is unasserted.
   That is defensible — the docstring says the function returns selection sets and `fractional`
   consumes a set — but it should be stated rather than left implicit.

---

## The five open obligations — classification only

**I resolved none of these. I changed no code, decided no scientific policy, and ran no data.**
The question I answer for each is narrow: *does the package's own code and documentation avoid
silently deciding it?*

| # | Obligation | Does the code avoid silently deciding it? | What must be decided, and by whom |
|---|---|---|---|
| 1 | Native-anchor provenance and granularity | **Mostly yes — one disclosed constraint.** Provenance is genuinely undecided: the anchor is a mandatory argument and nothing in the module generates, defaults, caches or derives it (verified: no generation keyword exists). **But the signature does fix the granularity** to exactly one `float` per question id, and fixes the comparison tolerance to `core.TOL = 1e-12`. The README states this ("Current function requires per-question anchors"), so it is disclosed, not silent. | Whether the governing control's frozen anchor artefact is per-question and compatible with a `float` in `[0,1]` compared at 1e-12. **Decided by:** the authority owning the governing frozen anchor artefact, before any production connector is accepted. |
| 2 | LoCoMo gold divergence (historical producer applies audit corrections; accepted v5 ingestion reads raw evidence) | **Yes, fully.** There is zero correction machinery in the package — no `audit`, `correction`, `conv_*` or raw-evidence handling of any kind. Gold enters only as caller-supplied `gold_rows` and is validated as indices (`validate_gold`: list, int, in range, no duplicates, non-empty) and nothing more. The package neither loads corrections nor reinterprets gold. | Which gold semantics are normative — corrected or raw — and whether the divergence changes any selected gold. **Decided by:** the gold-semantics authority, before a real connector is enabled. Note the README's own careful caveat: the source-level difference is *not* evidence that any particular selected gold is wrong, since no corpus was accessed. |
| 3 | LongMemEval archive ordinal, production nuisance-priority ordering, deterministic ten-shard assignment | **Partly — and this is the one to watch.** No sharding policy is invented (no `shard`/`fold`/`split` machinery exists — obligation genuinely open on that limb). **But the LongMemEval archive ordinal *is* decided here**, as `enumerate(cohort_ids)`, and I demonstrated that this is **outcome-affecting, not cosmetic**: permuting only `cohort_ids` on an otherwise identical fixture changed 2 of 120 emitted scores (e.g. `('s0', 60009, 'SCALED_RANDOM32')` 0.280000 → 0.310000). The mechanism is ordinal → `stable_archive_seed` → the 20 nuisance priority vectors → top-k tie-breaking → score. It is **disclosed** in README obligation 3, so it is not silent — but it is a load-bearing default, not an inert placeholder. By contrast the LoCoMo ordinal is bound upstream (`conversation["index"]` from ingestion), which is the safer shape. | The historical convention for LongMemEval archive ordinal and nuisance-priority ordering, plus the ten-shard assignment rule. **Decided by:** the authority holding the historical convention, and bound explicitly rather than inherited from cohort order. **This must be settled before any real run, because it moves the numbers.** |
| 4 | Finalizer consuming these records through the accepted bootstrap/output path, with provenance and overwrite protection | **Yes, fully.** No bootstrap call, no aggregation, no clustering, no writer, no output path of any kind. The only filesystem operation in `pipeline.py` is a single `read_bytes` to hash-verify the closed core. Records are returned in memory and nothing else. | The finalizer itself, its provenance capture and its overwrite protection. **Decided by:** the Continuity Lead / runner owner. **Caveat from F2:** whatever finalizer is written must not treat an empty record set as a valid result, because M-3 currently produces one without complaint. |
| 5 | Full negative-control coverage, integration review, lock regression, acceptance, pre-run seal | **Yes, fully — and my review supports keeping it open.** There is no HMAC, no seal, no manifest-writing and no acceptance machinery in the package (the single `lock` regex hit is a substring of "blocks"). The manifest status reads `PREPARATION_NOT_SEALED_NOT_EXECUTION_READY` and the README says plainly this is not a readiness declaration. Independently, the nine test gaps listed above are concrete evidence that negative-control coverage is in fact incomplete. | Completion of negative-control coverage (start with the nine gaps above), real-ingestion-to-computation integration review, full accepted-lock regression, independent acceptance, and the pre-run seal. **Decided by:** the Continuity Lead, with independent acceptance by a party other than the implementation team. |

**Summary of the classification.** Obligations 2, 4 and 5 are cleanly open — the code contains
nothing that could decide them. Obligation 1 is open on provenance but the code constrains
granularity and tolerance, disclosed. Obligation 3 is the only one where the code makes a
choice with numerical consequences (the LongMemEval ordinal); it is **disclosed in the README,
so it is not a silent decision**, but it is load-bearing and I recommend it be treated as the
highest-priority item of the five.

**No obligation was found to have been silently decided.** The one that comes closest —
obligation 3 — is explicitly flagged by the package's own README.

---

## What I ran

All probes ran in the accepted interpreter with `PYTHONHASHSEED=0` and
`OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS=1`, each as **its own process** (several packages in this
programme share module names, and in-process imports have previously shadowed one another and
produced a vacuous control). Nothing was installed; nothing was written into the venv. All
inputs are strings and arrays generated in the probe files. No corpus, dataset, BEAM directory
or historical result was read, opened, hashed or scanned.

| Probe | Covers | Raw output |
|---|---|---|
| `probes/probe_01_m1_representation.py` | M-1 archive-only fitting, query-leak attempts, memory-only, fitted-object reuse, pinned parity, core identity, n=95/96/97 boundary, `E-M-005` reachability | `evidence/probe_01.txt` |
| `probes/probe_02_m2_scoring.py` | Arms and order, seed panel, scaling-before-rotation, priority reuse, matched blocks, 4,000-case tie-parity fuzz vs pinned, gold accounting, anchor semantics, sign/distance/rotation controls | `evidence/probe_02.txt` |
| `probes/probe_03_canary_zeros.py` | Signed-permutation canary: IEEE zero semantics, all-zero vs mixed-zero, per-coordinate coverage, **exact `Fraction` control**, zero prevalence on the fitted path | `evidence/probe_03.txt` |
| `probes/probe_04_m3_adapter.py` | Both ingestion schemas with fake objects, ordering and ordinal sensitivity, 16 malformed fixtures, per-archive diagnostics, record-validation completeness | `evidence/probe_04.txt` |
| `probes/probe_05_negative_controls.py` | Leak canaries across `str`/`repr`/`__cause__`/`__context__`/traceback/stdout/stderr/written files; non-finite refusals; real-gate refusals; audit-hook limits | `evidence/probe_05.txt` |
| `probes/probe_06_obligations_and_edges.py` | Empty cohort, anchor tolerance boundary, and the code-level evidence behind each of the five obligations | `evidence/probe_06.txt` |
| `replay.py` (the candidate's own) | Reproduced in a fresh output directory | `evidence/replay_independent_*` |

Probe 05 and probe 06 each required one syntax/regex fix in **my own probe code** before they
ran; the committed probe files are the corrected versions that produced the committed output.
No candidate byte was changed at any point.

---

## Hash inventory

**Verified — candidate and its declared provenance** (all computed from raw Git blobs):

| Object | sha256 |
|---|---|
| `PAYLOAD_HASHES.json` (out-of-band value, matched) | `39d8ebfbeaa4ece63c4aaa2fb220e886047b7c8e700deded47a8a83e79abec3c` |
| `README.md` | `9959f57723a5ec510fa436728b1337fbef7719aba4f3eb38921b119dff1e8a8a` |
| `CLAUDE_REVIEW_REQUEST.md` | `7aa9d96715b7b045688811063869bdcb44027f85d607a59a715b454f215e3c98` |
| `pipeline.py` | `db417ade3a4e2e1ceca342dbf5b4a0fde2562296b91932126ebeca01652be5ae` |
| `replay.py` | `30be19caef5c2cfd642478f7e6515a8069ae42a7d70006ddcb81f9d5762162f9` |
| `test_pipeline.py` | `cfd3263686de93bf87ca8b5336ac080fd7f3d759bfe1341bfd2e49e735a9bd81` |
| `evidence/RESULTS.json` | `178ec719013005c41cd127beef187b0dfcac37bda1a123a2f47bc36dd08adcb3` |
| `evidence/stderr.txt` | `4c3f8e9e43fee2b5b886f885d3a62800bf10bf69a82bba0ea668ea19bbbcbf02` |
| `evidence/stdout.txt` (empty file) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| closed core `membership_scaling_core.py` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` |
| pinned arithmetic `locomo_sign_mechanism_replication.py` @ `692f599e` | `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` |

**Commits verified:**

| Commit | Role |
|---|---|
| `ed4e22c520b7dc0ae2f43f915e0c621070c72a87` | candidate under review |
| `07ec929243068914676a0f30efd10c9f294c7e71` | candidate parent, matches manifest `base_commit` |
| `16019724564b5ac8db4a4d2d8bb08f98feb45c09` | merge base of candidate with `main` (explains the branch-point artefact) |
| `c3cfb98a5dfb38db53cefa929a22eb66fd69441a` | `origin/main` at review time; parent of this audit commit |
| `692f599eedeb7e7a649443f24ff507e8c4d1c17d` | pinned arithmetic source commit |
| `dcb568d0a6c33154c1568500325ad457b4d6f455` | core provenance commit as declared in the README (not independently re-derived; I verified the core **blob** hash instead) |

**This report.** `EXECUTION_PREP_V1_REVIEW.md.sha256` holds the sha256 of the **committed blob
bytes** of this file — i.e. of the byte stream Git stores, obtained as
`git cat-file -p <audit-commit>:audit_v52_execution_prep_v1_review_2026_09_08/EXECUTION_PREP_V1_REVIEW.md | sha256sum`.
The audit worktree was created with a **repo-local** `core.autocrlf=false`, so the working-tree
bytes and the blob bytes are identical and the value can equally be reproduced with
`sha256sum` on the checked-out file in an LF checkout. It is **not** the Git object id (which
is a SHA-1 over a `blob <len>\0` header plus the content).

---

## Scope reminder

This is a preparation review. It authorizes nothing. Canonical integration, the state file, the
ledger and `main` remain the Continuity Lead's responsibility, and no part of this document
should be read as acceptance, as a seal, or as permission to touch real data.
