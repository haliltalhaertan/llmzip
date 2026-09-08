# Delta closure check — runner + ingestion v3

**Auditor:** independent, cold start. Did not write the reviewed code and assumed no claim in it is true.
**Date:** 2026-09-08.
**Subject:** branch `impl/v52-runner-ingest-v3-2026-09-08`, commit
`64d774a66c8af154b9421c5bdd1b3964d0b82fe4`, namespace
`drafts/v52/membership_runner_ingest_v3_2026_09_08/`.
**Specification:** the delta closure check at `audit/v52-runner-ingest-v2-closure-2026-09-08` @
`823a361d1a72735783259e5a6fa1914c25870abf`, report blob sha256
`43969c4e1614a98b707dbc730a31b10bf83bac19ebaf87e069c25e141371b0df` (verified myself — §6),
verdict `CLOSURE PASS WITH FINDINGS`.

---

## VERDICT: `CLOSURE PASS WITH FINDINGS`

**What this verdict covers, stated explicitly.** It covers **ONLY** the three items the previous
closure check left open — **D-5** (the nine paths F12–F20 and the error interface), **D-1** (the
partial-evidence policy) and the **LongMemEval evidence accounting** — plus the wiring those touch,
and a brief regression pass over what earlier checks closed. It does **NOT** extend to:

- the **not-yet-written representation stage** (M-1/M-2/M-3) — I confirmed only that it was **not**
  added here (probes A2/A3);
- **the experiment as a whole** — its design, preregistration, estimand, statistics, accepted cohort,
  accepted manifests, accepted seed **values** or environment lock;
- the **closed computation core** (F-1…F-12, NEW-1/2/3), which I treated as independently closed and
  did not reopen. Its blob is byte-unchanged (§6).

**Why "WITH FINDINGS" and not a plain PASS.** All three items are closed in substance, and I say so
without hedging. Two carry residual defects, and one carries a **byte-verbatim false claim in the
shipped code** — the exact category the fix package explicitly set out to stop making:

- **D-5 is closed for the nine named paths, the ordering defect and the file-derived path, and it is
  NOT closed as the general property the module asserts.** Every one of F12–F20 is genuinely shut
  against my own canaries, and the F12 ordering defect is fixed at the root, measurably (§3.1). But
  the new interface was applied to `corpus_ingest_v3` and `authoritative/` completely and to
  `membership_runner_v3` only **partially**: **ten** interpolated expressions survive inside `raise`
  statements in that module, and I got sub-120-character canaries out through **two** further paths
  (P1, P2 — a tenth and an eleventh in the F-series class). The module nevertheless states, absolutely,
  that *"every message here is built by `errors.message`"* and that *"A string cannot enter a message
  without first raising `UnsafeErrorField`"*. Both are false as written. That **is** a third absolute
  claim, contrary to `FIX_PACKAGE_V3_2026-09-08.md:44`.
- **D-1's policy change is real and complete, and one class of partial gold loss still reaches the
  persisted manifest invisibly** — not through the path v3 rewrote, but through `_normalise_evidence`,
  which is **byte-identical in v1, v2 and v3** and silently discards evidence entries it cannot turn
  into an id (E9, probe part 3). Six shapes I constructed produce `declared == resolved`,
  `unresolved = 0`, `empty_gold = 0` and a gold set smaller than the source declares.
- **LongMemEval is cleanly closed**, the preparer's reading of the bound adapter is **CORRECT**, and I
  found nothing wrong with it.

Neither residual is a regression, and neither makes any earlier finding reopen.

**Whether this authorises anything.** No. Nothing was sealed, no HMAC was computed, no `--mode run` or
`--mode finalize` was invoked, no representation was fitted, no bootstrap or pilot was run on real
data, and **no real corpus file was read, opened, downloaded or hashed**. No candidate file was
modified. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## 1. Per-item table

| # | Item | Disposition | My evidence | Genuine negative control? |
|---|---|---|---|---|
| **D-5** | nine residual paths (F12–F20) still interpolated raw values; F12 was an ordering defect; F20 was file-derived | **CLOSED for F12–F20 and for the ordering; NOT closed as the asserted general property (N-1, N-2)** | B, C, D, P1–P5. All of F12–F20 driven with **my own** canaries as caller-supplied, file-supplied (a poisoned seed record the pipeline itself wrote) and **parsed corpus** values; surface captured = stdout + stderr + message + `repr` + the **whole** `__cause__`/`__context__` chain + **every file written**. v3 leaks on none; **0 files** written on any refusal. Ordering measured with a `dict` subclass that records key reads: v3 reads **only** `_accepted_manifest_sha256` before refusing (`reads=[('get','_accepted_manifest_sha256')]`), v2 reads `benchmark` first and leaks it. `corpus_ingest_v3` and `authoritative/resolve_sources` have **zero** interpolated expressions inside any `raise`. **But** `membership_runner_v3` still has **10 raw ones**, and two of them leak (P1, P2) | **Yes**, and I checked it is not vacuous. The preparer's controls call `R2`/`I2` and inspect real returns; four run in a subprocess. I verified the subprocess loads **v2's own** `authoritative` package (`…ingest_v2_…/authoritative/__init__.py`) and that it is the **unfixed** resolver (`hasattr(RS,'errors') == False`), and reproduced all four leaks (H1, H1b, H2). I also confirmed the shadowing hazard is real: in-process, `authoritative` resolves to **v3's** package, and my own in-process F16 control was consequently vacuous (H3, H3b) |
| **D-1** | partially unresolvable LoCoMo evidence was waived by a free-text citation that reached no artefact | **CLOSED (with a residual, N-3)** | E1–E9. `allow_partial_evidence` and `partial_evidence_citation` are **gone from the signature**, not renamed — `co_varnames` = `('source_path','mapping','enabled',…)`, and the only surviving module name matching waiver/allow/override/partial is the constant `PARTIAL_EVIDENCE_POLICY` (E1c). A partial resolution **stops** with `E-COH-002` carrying `affected_questions=1, declared_ids=2, unresolved_ids=1, cohort_size=…` and **nothing else**; **no file is written** (E2d). No gold repaired, no question excluded, no cohort changed: gold rows and cohort are **byte-identical to v2** on a clean source (E5). A **fully** unresolvable question is **not** classed as partial — it proceeds and is visible as `declared=1 resolved=0 unresolved=1 empty_gold=1` (E3b); a fully resolved source proceeds (E4). Checked against the **accepted 1535-question / 10-cluster manifest's shape**, not a toy: the full cohort resolves, the 6 out-of-cohort ids are counted not refused, and **one** partial question in 1535 stops the whole run (E7, E7b, E7c, E8) | **Yes.** The preparer's control drives **v2**'s `ingest_locomo(..., allow_partial_evidence=True, partial_evidence_citation="anything non-empty")` and shows v2 proceeds and the citation reaches no manifest. I reproduced the v2 signature difference myself (E1d) and byte-compared v2's and v3's gold rows on a clean source (E5) |
| **LongMemEval** | `evidence_ids_declared` was defined as the resolved count, so any loss was structurally invisible | **CLOSED** | F1–F8. `declared_reference_ids` is `null` with `declared_reference_ids_status: "NOT_APPLICABLE"`, plus `gold_units_resolved` and `completeness_guarded_by` (F1). The two benchmarks' accounting objects no longer share a field **set** (`{completeness_guarded_by, declared_reference_ids, declared_reference_ids_status, gold_units_resolved, model}` vs `{declared_reference_ids, model, resolved_reference_ids, unresolved_reference_ids}`) and the `model` token distinguishes them (F2, F3). **All four named guards exist and three of them fire** — `E-COH-007`, `E-COH-008`, `E-COH-009` — and the fourth (`units_enumerated_from_sessions`) holds structurally: `units=3, gold=[0,2]`, every gold row indexes an enumerated unit (F5). A non-boolean marker is **refused** (`E-COH-009`), not coerced — including `1`, `"true"` and `null` (F6, F8). For **well-formed** input, gold rows, memory ids and cohort are **byte-identical to v2** (F7). **The preparer's semantics determination is CORRECT** — see §4 | **Yes.** The preparer's control shows v2 coercing `has_answer: 1` and publishing `declared == resolved`. I reproduced it against `I2` myself: `evidence_ids_declared=1, evidence_ids_resolved=1, evidence_ids_unresolved=0` with one gold row silently dropped (F6-NEG) |
| **REGRESSION** | D-2, D-3, D-4, D-6, D-7, D-8, source trust, gates, identity-before-parse, cluster block, writers | **NO REGRESSION** | G1–G12. D-2 `E-CFG-010`; D-3 seed 999 **and** the transposed `52001170` refused, a hand-forged record caught on read; D-4 a CRLF manifest refused, and the **real CRLF checkout in my own worktree** (60823 B, `4a1f7c2d…`, 1555 CRLFs) refused with `crlf_to_lf_would_match=True`; the **superseded** manifest refused **as superseded** (`E-SRC-002`) under both benchmarks; D-6 query-derived centering and a **one-ULP** `D` both caught, a value-equal copy still passes; D-7 `E-COH-007`; D-8 `E-COH-006`; the LongMemEval cluster bootstrap still refused; identity still precedes parsing; all three writers still refuse to overwrite; the real-data gate still closed by default and still refuses first. **The N-4 residual is now closed:** an empty mapping into `compute_results` gives `E-SRC-006`, not `KeyError` (G7b) | **Yes.** Preparer's suite: **60 checks, 0 failures, 12 negative controls**, and it reproduces `evidence/v3_delta_tests.txt` **exactly** (empty diff). v2 suite 82 ok / 0 fail, reproduces `evidence/v2_regression.txt` exactly. Core suite 99 ok / 0 fail, reproduces `evidence/core_regression.txt` but for one temp-dir name. Both v1 suites `ALL PASS` |

---

## 2. The findings, classified

Classified as instructed: **(i) real defect**, **(ii) optional improvement**, **(iii) wording /
claim-accuracy**. Nothing is presented as a blocker unless it is one. **None of these is a blocker.**

### N-1 — (iii) CLAIM-ACCURACY — v3 *does* make a third absolute claim, and it is false

`FIX_PACKAGE_V3_2026-09-08.md:43-44`, byte-verbatim:

> `v2 said *"no value is interpolated into any message"* — false. **v3 does not make a third absolute`
> `claim.**`

That is not what the shipped code says. `membership_runner_v3.py:69-72`, byte-verbatim:

> `replaced by the mechanism: every message here is built by `errors.message` from a FIXED CODE, that`
> `code's FIXED SENTENCE, and fields restricted to numbers, booleans, None and enum members already`
> `validated against a closed set. A string cannot enter a message without first raising`
> `` `UnsafeErrorField`. ``

Both sentences are absolute claims about the code, and **both are false**:

- `errors.message` builds **only some** of that module's messages. Ten interpolated expressions
  survive inside `raise` statements in `membership_runner_v3.py` (probe P4): `kind` and `position`
  at lines 190, 196 and 201, and `mapping['n_questions']` at line 290. Those messages are built by an
  f-string, not by `errors.message`.
- A string **can** enter a message without `UnsafeErrorField` firing. Byte-verbatim from probe P2:

  > `Where did Rashid park the blue van on the night of the storm? at 0 has unsupported type <int scalar digest=5994471abb01>; this runner supports string identifiers only, …`

`errors.py:20-21` compounds it, byte-verbatim:

> `WHAT IS AND IS NOT CLAIMED. The tested surface is: every exception raised by `membership_runner_v3`,`

— which asserts the rule in `errors.py:8-13` (*"A message is assembled from three things and nothing
else"*) covers every exception the runner raises. It does not.

Two further stale statements, both byte-verbatim:

- `membership_runner_v3.py:1` — `"""Corpus-bound runner v2 for the V52 membership-under-scaling experiment - PREPARATION ONLY.`
- `corpus_ingest_v3.py:1` — `"""Corpus ingestion v2 for the V52 membership-under-scaling experiment - WRITTEN, NOT AUTHORIZED TO RUN.`
- `membership_runner_v3.py:18-19` — `D-5  exception messages interpolated values verbatim and unbounded. Every message now goes` / `through `safe_report`, which reports type, shape and digest and never content.` — carried forward from v2, where the previous check already falsified it, and still false in v3.

**Minimum fix:** either route the ten remaining sites through `errors.message`, or replace "every
message here is built by `errors.message`" with what the code does — *"every message in
`corpus_ingest_v3` and `authoritative/` is built by `errors.message`; in this module the identifier
validators and the manifest-consistency check still use `safe_report` inside an f-string, and their
caller-supplied `kind` and `n_questions` arguments are not policed"* — and refresh the two `v2`
headers. This is a wording fix; it changes no behaviour.

### N-2 — (i) REAL DEFECT, residual — two more caller-supplied escapes in `membership_runner_v3.py`

Same class as F13/F14, which the previous review counted as leaks, so I count these too. Both are
**caller-supplied**, neither is reachable from parsed corpus content, and neither reaches a file.

| probe | path | what escapes, byte-verbatim |
|---|---|---|
| **P1** | `verify_source_identity`, `membership_runner_v3.py:289` — `int(mapping["n_questions"])` | `invalid literal for int() with base 10: 'Where did Rashid park the blue van on the night of the storm?'` — an **uncaught `ValueError`**, not a `DesignViolation`, so the interface never sees it |
| **P2** | `validate_identifier`, `membership_runner_v3.py:190/196/201` — the `kind` argument | `Where did Rashid park the blue van on the night of the storm? at 0 has unsupported type <int scalar digest=…>; …` |

**Severity, stated fairly.** `verify_source_identity` is a **public entry point with no stamp check**
(probe P1c: `_accepted_manifest_sha256` does not appear in its body), so a caller reaches P1 directly.
It is also reachable **behind** the stamp check via `compute_results` if the caller hand-stamps a
mapping (P1d) — but that is N-5, which is optional. On the intended path the mapping comes from
`load_accepted_mapping`, where the closed schema guarantees `n_questions` is the accepted integer, so
**no honest call can reach either**. Both in-package call sites of `validate_identifier` pass the
literals `"question id"` / `"cluster id"` (P2). **Minimum fix:** validate `n_questions` as an `int`
before `int()` is called, and make `kind` an enum member rather than a free string.

Two more sites echo a **kwarg key** — `errors.py:141` (`error field 'canaryKeyOdessa1987' is a str`)
and `safe_report.py:96` (`counts() takes ints only; canaryKeyOdessa1987 is str`). I checked every
`raise_violation`/`message` call site in the package: all use literal keyword names, and the only
three `**`-expansions (`**lengths` at `corpus_ingest_v3.py:464`, `**_diagnose(...)` twice in
`resolve_sources.py`) also have literal keys (probe P6). **Not data-reachable** — theoretical only,
recorded so a future author does not expand a data-derived dict into a message.

`errors._safe` also accepts **any** `Enum` and prints `.value` verbatim (probe D3 — a dynamically
built `Enum("Dyn", {"X": <canary>})` produced
`E-CFG-001: … [x=Where did Rashid park the blue van on the night of the storm?]`). No such enum exists
in the package; the docstring's *"enum members that have already been VALIDATED against a closed set"*
is enforced by convention, not by `_safe`. Theoretical, recorded for the same reason.

### N-3 — (i) REAL DEFECT, residual on D-1 — a partial gold loss that still slips through, invisibly

**In scope**, because the instruction asked me to try to construct one. I found six shapes.
`_normalise_evidence` silently discards any evidence entry it cannot turn into an id, so those entries
never enter `declared` at all — and the partial-loss detector, which compares `resolved` against
`unresolved`, therefore never sees them. Measured (probe E9), all on a source where the surviving id
resolves:

| evidence value | persisted result | gold rows |
|---|---|---|
| `[{"dia_id": "D1:0"}, {"note": "second gold turn"}]` | `declared=1 resolved=1 unresolved=0 empty_gold=0` | `[0]` — one entry lost |
| `[{"dia_id": "D1:0"}, {"dia_id": ""}]` | same | `[0]` |
| `[{"dia_id": "D1:0"}, {"dia_id": null}]` | same | `[0]` |
| `["D1:0", 12345]` | same | `[0]` |
| `["D1:0", null]` | same | `[0]` |
| `"see D1:0 and also the bakery note"` | same | `[0]` |

This is exactly the condition `E-COH-002`'s own sentence names — *"the gold set would be silently
smaller than the source declares"* — and it does not fire. The four shapes that **are** caught behave
correctly: a duplicated declared id with one unresolvable **stops**; a dict, an int and a nested list
produce `declared=0, empty_gold=1`, which is visible.

**It is inherited, not introduced.** `_normalise_evidence` is **byte-identical** in v1, v2 and v3 —
sha256 of the function source `cc8170e724ce798a743dee9ee2c5cc97…`, 737 bytes in all three — and v2 and
v3 return identical lists on all six shapes (probe part 3). So this is **not a regression** and does
not reopen D-1's stated fix, which was about the waiver and about stopping rather than proceeding.

**What I could NOT check:** whether the real `locomo10.json` actually contains evidence entries in any
of these shapes. Reading it is prohibited here. What I can say is that the code path exists, accepts
them, and reports the result as a complete accounting. **Minimum fix:** count an unusable evidence
entry as `unresolved` rather than dropping it — i.e. have `_normalise_evidence` return every entry it
was given, or return a `(ids, dropped_count)` pair, and fold `dropped_count` into
`evidence_tally["unresolved"]` and into the partial-loss test.

### N-4 — (ii) OPTIONAL — `questions_with_partial_evidence_loss` is now a structural constant

`corpus_ingest_v3.py:432` and `:540` both return a hard-coded `[]`, so the persisted field is always
`0`. For LoCoMo that is honest by construction — a partial loss now stops, so if the summary exists
the count really is zero — and for LongMemEval the concept does not apply. It is noted only because a
field name that can never be non-zero invites a reader to conclude something was measured. Not a
defect; not a blocker.

### The three optional residuals N-3/N-4/N-5 from the previous check — judging the preparer's reason

The preparer's reason, `FIX_PACKAGE_V3_2026-09-08.md:53-55`, byte-verbatim:

> `Reported as required: none of them causes wrong data to be **accepted** on a real call path. Each`
> `requires a caller to construct and pass a value it did not obtain from the function that produces it`
> `— a caller doing that is not a wrong-data path, it is a caller overriding its own check.`

I judged **only** that reason, and I could not falsify it:

- **N-3** (`transform_stamp` forgeable) — survives (probe I1): a caller that transforms with a
  query-derived `mu` and then calls `transform_stamp(mu_archive, D_archive)` still passes. It requires
  the caller to compute a stamp it did not use. Every *honest*-caller error is still caught (G5b, G5c).
  The preparer's reason **holds**.
- **N-4** (unguarded `KeyError`) — **no longer reachable**. An empty mapping into `compute_results`
  now gives `E-SRC-006` and no `KeyError` (I2, G7b). The preparer's statement is correct.
- **N-5** (the stamp is a public constant) — survives (probe I3): a hand-built mapping carrying
  `accepted.ACCEPTED_MANIFESTS[b]["blob_sha256"]` passes both stamp checks, and can then substitute an
  arbitrary **cohort** and an arbitrary `source_id`/`source_sha256` into the persisted
  `source_identity`. That is the strongest case against the reason, and I state it plainly. But it
  requires the caller to hand-write a manifest it did not obtain from `load_accepted_mapping` and to
  copy a constant it had to look up — which is the caller overriding its own check, exactly as the
  preparer says. It is **not** an accidental path, and an honest caller cannot reach it.
  **I do not promote N-5 to a blocker.** It remains optional, as the previous check left it.

---

## 3. What I verified in detail

### 3.1 The ordering claim in `compute_results` — measured, not read

The claim (`membership_runner_v3.py:491-494`) is that *"nothing from the mapping is read, compared or
formatted until the mapping has been shown to be the accepted one."* I passed a `dict` subclass that
logs every `__getitem__` and `get`, holding canaries in `benchmark`, `n_questions`, `source_id`,
`source_sha256` and the cohort:

```
C1  v3 reads ONLY the stamp key from an unstamped mapping before refusing
    reads=[('get', '_accepted_manifest_sha256')]
C3  NEG: v2 reads mapping['benchmark'] BEFORE the stamp and leaks it
    reads=[('getitem', 'benchmark'), ('getitem', 'benchmark')]  leaked=['Q']
```

**The claim holds**, with one pedantic caveat: the stamp key itself is of course read and compared —
that *is* the check. No other key is touched, and nothing from the mapping reaches the surface.

### 3.2 The three delivery routes for a canary

- **Caller-supplied** — F12/F13/F14/F15/F16, `verify_source_identity`, `validate_identifier`, a
  canary file **name**, a canary path segment. All clean except P1/P2 (N-2).
- **Read back out of a JSON file the pipeline itself writes** — I called
  `R3.freeze_bootstrap_seed` to write a real record, then wrote a poisoned one with canaries in
  `benchmark`, `scheme` and `runner_version`, and drove `read_bootstrap_seed` (F20), plus a
  non-mapping record, a canary `bootstrap_seed` and a canary `replicates`. **All clean.**
- **Parsed corpus text** — a fully canaried synthetic source (question, answer and every turn a
  canary) down the happy path, the cohort-failure path, the duplicate-memory-unit path with canary
  `dia_id`s, and six LongMemEval refusal paths. **All clean**, **0 files written** on every refusal,
  and the written 837-byte ingest manifest carries no canary — while the in-memory structures still
  hold the text, which is what ingestion is for.

### 3.3 The interpolation census (probe P4/P5)

| module | interpolations inside a `raise` | raw (not `len`/`safe_report`/`.shape`) |
|---|---|---|
| `corpus_ingest_v3.py` | **0** | 0 |
| `authoritative/resolve_sources.py` | **0** | 0 |
| `authoritative/accepted_configuration.py` | **0** | 0 |
| `membership_runner_v3.py` | 19 | **7** (`kind`×3, `position`×3, `mapping['n_questions']`) |
| `errors.py` | 2 | 2 (kwarg key, type name) |
| `safe_report.py` | 2 | 2 (kwarg key, type name) |

For comparison, at the same commit: `membership_runner_v2.py` has **57** and `corpus_ingest_v2.py`
**39** interpolations inside `raise` statements. The reduction is real and large; it is simply not
total, and the module says it is.

---

## 4. LongMemEval — the bound-semantics determination, checked against the committed adapter

The preparer cites `adapters/longmemeval_v52_adapter_v2.py` lines 37-38 and 45. I read that file from
the **raw Git blob** at `64d774a6` (sha256 `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`,
byte-unchanged from `9b56968`). Byte-verbatim:

> line 37-38: `            if 'has_answer' in turn and not isinstance(turn['has_answer'], bool):` /
> `                issues.append({'code':'INVALID_HAS_ANSWER_TYPE','session_index':si,'turn_index':ti})`
>
> line 45: `                'has_answer': bool(turn.get('has_answer', False)) if isinstance(turn.get('has_answer', False), bool) else False,`

and line 48: `            if rec['has_answer']: gold_ids.append(mid)`.

**The determination is CORRECT.** Gold is derived **from the turns themselves** by a per-turn boolean;
nothing in a LongMemEval item declares a list of gold references that could dangle, so there is no
declared count to report, and a non-boolean marker is recorded as an issue and then coerced to `False`
— silently dropping a gold unit. v3's refusal (`E-COH-009`) is the right analogue of an unresolvable
reference, and reporting `declared_reference_ids: null` with an explicit `NOT_APPLICABLE` status is
more honest than v2's tautology. I found no error in the preparer's reading.

Two nuances, neither a defect: the two accounting objects still share the **key name**
`declared_reference_ids` (LongMemEval's is `null` with a status beside it, which I judge honest, not
misleading); and `has_answer` **absent** or `False` is legitimately not-gold and correctly proceeds
with `empty_gold` recording it (F8).

---

## 5. What I actually ran

Environment: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\locomo_reproduction_tmp_20260907\venv\Scripts\python.exe`
— Python `3.13.15`, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3 — with
`PYTHONHASHSEED=0` and `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`
(echoed at the top of `probe_output.txt`). Used as an interpreter only; nothing installed, changed or
written inside it. The venv has no `pytest`, so the suites were run as plain scripts, which is how
they are written.

1. `git clone https://github.com/haliltalhaertan/llmzip.git` into my own scratch directory (**not** the
   preparer's work tree and **not** any `scratchpad/llmzip_*` directory), plus detached worktrees at
   `64d774a6` and `9b56968`. Those worktrees are CRLF-translated, which is what made the D-4
   regression check real.
2. `git cat-file blob <commit>:<path> | sha256sum` for every identity in §6. Never from a checkout.
3. `python -B test_runner_ingest_v3.py` → `ALL PASS`, **60 `ok`, 0 failures, 12 negative controls**.
   Raw output `preparer_suite_v3_run.txt`; diff against the committed `evidence/v3_delta_tests.txt`
   after normalising temp-directory names: **empty**.
4. `python -B test_runner_ingest_v2.py` → 82 ok / 0 fail, reproduces `evidence/v2_regression.txt`
   exactly (`v2_suite_run.txt`). `python -B test_membership_scaling_core.py` → 99 ok / 0 fail,
   reproduces `evidence/core_regression.txt` but for one temp-dir name (`core_suite_run.txt`).
   `test_membership_runner.py` and `test_corpus_ingest.py` → `ALL PASS` each.
5. `python -B probe_v3_closure.py <checkout> <repo>` — **my own 145 probes**, output
   `probe_output.txt`. Tally: **PASS=120, FINDING=9, OBSERVE=8, INFO=8**. Of the 9 FINDING lines,
   `B-NEG F16` is a **vacuous control of my own** (in-process, v3's `authoritative` shadows v2's —
   the exact hazard the preparer names; the subprocess control H2 shows v2 really does leak through
   F16), `D6` is N-2/P1, `I3b` is N-5 behaving as expected, and the remaining six are N-3.
6. `python -B probe_v3_part2.py <checkout>` — byte-verbatim capture of the two residual escapes and
   the AST interpolation census (`probe_output_part2.txt`).
7. `python -B probe_v3_part3.py <checkout>` — the `_normalise_evidence` inheritance check
   (`probe_output_part3.txt`).

Every "source", manifest and record my probes opened is a small fake written by the probe scripts into
a fresh temp directory: the shape of the real data, none of its content. Bound source and manifest
hash entries are overridden per probe, visibly and reversibly (`bind_source` / `bind_manifest`
context managers), because otherwise nothing but the two real files could pass `verify_source_bytes`.
Those two files were **not** touched. The accepted LoCoMo manifest was read as a **raw Git blob** —
a cohort id list, not corpus — to build a synthetic source of its exact **shape** (1535 questions,
10 clusters, and the real question-id-to-cluster assignment), with canary text as content.

**What I could NOT verify, stated rather than implied:**

- I have **not** verified that the bound cohorts correspond to anything in the real corpora, and I have
  **not** verified the two bound source hashes or byte sizes against the real files. Reading them is
  prohibited here.
- I have **not** verified whether the real `locomo10.json` contains evidence entries in any of the six
  shapes that slip through N-3. I verified only that the code accepts them and reports a complete
  accounting.
- I did **not** re-audit the computation core, the design, the preregistration or the statistics.
- I did **not** attempt to prove that no twelfth leak path exists. I enumerated every interpolated
  expression inside every `raise` in the package by AST and probed the ones that are not `len()`,
  `safe_report.*` or a `.shape`; I report what I found.

---

## 6. Identities verified — from raw Git objects only

Every hash below was produced with `git cat-file blob <commit>:<path> | sha256sum` in a fresh clone of
my own. This machine's **system** Git config sets `core.autocrlf=true`
(`file:C:/Program Files/Git/etc/gitconfig`, unchanged by me), and the repository ships **no
`.gitattributes`** at `64d774a6` (`gitattributes_count=0`), so a Windows checkout hashes differently —
that is finding D-4 itself. I changed no global or local Git setting and added no `.gitattributes`.

**Commits**

| what | sha |
|---|---|
| candidate branch `impl/v52-runner-ingest-v3-2026-09-08` | `64d774a66c8af154b9421c5bdd1b3964d0b82fe4` |
| its parent — the v2 candidate | `9b569687b394b0507fdeefc5abe456a9958e0788` |
| the previous closure check (the specification) | `823a361d1a72735783259e5a6fa1914c25870abf` |
| `origin/main` — this audit branch is parented on it | `88d66989a752e5e02b282f328f4cfb635a95c22d` |

**The candidate commit is purely additive.** `git diff --stat 9b569687 64d774a6` = **12 files,
2490 insertions, 0 deletions**, all under
`drafts/v52/membership_runner_ingest_v3_2026_09_08/`. `git diff --name-status` over the **whole v2
package** is empty.

**Blobs — byte-unchanged at `64d774a6` (compared against `9b56968` blob-for-blob)**

| path | sha256 | |
|---|---|---|
| `audit_v52_runner_ingest_v2_closure_2026_09_08/V2_CLOSURE_REPORT.md` @ `823a361d` | `43969c4e1614a98b707dbc730a31b10bf83bac19ebaf87e069c25e141371b0df` | ✅ matches the brief |
| `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` | ✅ closed core, byte-unchanged |
| `…/membership_runner_v1_2026_09_08/membership_runner.py` | `b322f85147733ead9494c33e5c78c02c2361a1986241de54c0c2aa6cc137a6d0` | ✅ v1 byte-unchanged |
| `…/membership_ingest_v1_2026_09_08/corpus_ingest.py` | `7dc084d8795c7e7d07270b866fdbc5e9c597508cbf331862b4075f9943fdf219` | ✅ v1 byte-unchanged |
| `…/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` | ✅ accepted manifest, 59268 B, 1535 q / 10 clusters |
| `…/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` | ✅ accepted manifest, 36598 B |
| `…/binding/PROPOSED_mapping_longmemeval.json` (SUPERSEDED) | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` | ✅ 36589 B |
| `…/binding/PROPOSED_bootstrap_seeds.json` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` | ✅ 3605 B |
| `…/membership_runner_v1_2026_09_08/CONFIGURATION_IDENTITY_2026-09-08.md` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` | ✅ byte-unchanged |
| `adapters/longmemeval_v52_adapter_v2.py` | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | ✅ byte-unchanged (the semantics source, §4) |
| `…/membership_runner_ingest_v3_2026_09_08/safe_report.py` | identical to the v2 package's `safe_report.py` (diff empty) | ✅ |
| `…/membership_runner_ingest_v3_2026_09_08/authoritative/accepted_configuration.py` | identical to the v2 package's (diff empty) | ✅ |

**The v3 package's own blobs** at `64d774a6`:

| path | blob |
|---|---|
| `FIX_PACKAGE_V3_2026-09-08.md` | `6e7422641585769554a40c8955eb85b1c7b9c41c` |
| `errors.py` | `9588748b1a2d047373a8b59f9ea7406c5340e136` |
| `safe_report.py` | `25c7cd5b314b4606402d1a04aae1f86526bbc752` |
| `membership_runner_v3.py` | `619ca8159ecf5bcc7f5d8b855cb2e356e2ccca40` |
| `corpus_ingest_v3.py` | `c5ade8435df22365b00326fa8a9109eb88e82bcc` |
| `authoritative/accepted_configuration.py` | `e780878a71111f2a418bed50b5f1b9f628c08331` |
| `authoritative/resolve_sources.py` | `a84dde67add0b8d7333bbe9ffa321d6a3c97a1c3` |
| `test_runner_ingest_v3.py` | `6501a6cad75ba57488ec87f3e19dacc7afab9dfa` |

(These are Git object ids, not sha256 of the content; they pin the exact objects I reviewed.)

---

## 7. Files in this namespace

| file | what it is |
|---|---|
| `V3_CLOSURE_REPORT.md` | this report |
| `V3_CLOSURE_REPORT.md.sha256` | sha256 of the **committed blob** of this report |
| `probe_v3_closure.py` | my main probe suite — replayable: `python -B probe_v3_closure.py <checkout of 64d774a6> <repo root with .git>` |
| `probe_output.txt` | its raw output, as produced |
| `probe_v3_part2.py` / `probe_output_part2.txt` | byte-verbatim capture of the residual escapes, and the AST interpolation census |
| `probe_v3_part3.py` / `probe_output_part3.txt` | the `_normalise_evidence` v1/v2/v3 inheritance check |
| `preparer_suite_v3_run.txt` | my own run of the preparer's `test_runner_ingest_v3.py` |
| `v2_suite_run.txt`, `core_suite_run.txt` | my own regression runs of the v2 and core suites |

**Method for the report hash.** The value in `V3_CLOSURE_REPORT.md.sha256` is the sha256 of the **raw
Git blob** of `V3_CLOSURE_REPORT.md`, computed as
`git cat-file blob <commit>:audit_v52_runner_ingest_v3_closure_2026_09_08/V3_CLOSURE_REPORT.md | sha256sum`
— **not** of the checked-out file, which differs on Windows for exactly the reason set out in D-4.
Because the hash cannot be inside the file it describes, it is committed in a second commit that
changes nothing else, and the sidecar names the commit whose blob it pins.
