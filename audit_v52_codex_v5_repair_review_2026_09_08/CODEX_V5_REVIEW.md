# Independent review — Codex v5 repair of the runner/ingestion package

**Candidate commit verified:** `07ec929243068914676a0f30efd10c9f294c7e71`
(branch `codex/v52-runner-ingest-repair-2026-09-08`, namespace
`drafts/v52/membership_runner_ingest_codex_v5_2026_09_08/`, tree `59652c83c3e57c150850d73223c38eddf9eafc9c`).

**VERDICT: `PASS WITH FINDINGS`.**

This verdict covers **only** this repair package — the six items the prior closure check left open, the
wiring they touch, and a regression pass over what earlier checks closed. It does **NOT** authorize the
real experiment, any corpus read, any fitting/retrieval/ranking/bootstrap, any pilot, any seal or HMAC,
any `--mode run` / `--mode finalize`, or M-1/M-2/M-3. Nothing was sealed and no real corpus file was
read, opened, downloaded, hashed or scanned by me. No candidate file was modified.

**Auditor disclosure.** I am cold-start on this work: I had not seen this repository, this package, its
predecessors or the prior audit before this session. I assumed nothing in the candidate was true and
wrote my own probes; I did not treat Codex's suites as my audit — I used them only as an *object* of
audit (probe D mutates the package on a temp copy to ask whether their checks can fail at all). §7 lists
what I did **not** verify.

**Specification for this review:** the prior closure check at
`6b3de298850edf7a7696683726316b83909f5b6e:audit_v52_runner_ingest_v4_closure_2026_09_08/V4_CLOSURE_REPORT.md`,
blob sha256 `8ccde7f464ec1206d0fce3feeb3305eb5226f0212e1d62f148bde4c52e3f0ea2` — **I recomputed this hash
myself from the raw Git blob and it matches.** Base candidate `86a8fd7a73a0d4e045666e692cd7e2016f134885`.

---

## 1. Per-item table

| # | Item the prior audit left open | Disposition | My own evidence |
|---|---|---|---|
| **1** | **Two byte-verbatim FALSE descriptions** — (a) `membership_runner_v4.py:18-19` *"Every message now goes through `safe_report`, which reports type, shape and digest and never content"*; (b) `errors.py:20-24` naming `membership_runner_v3`/`corpus_ingest_v3` and saying the tests *"find none"* | **CLOSED** | Both sentences are **gone from every file in the package**, and so are the two smaller N-4 wordings. I searched all 28 payload files for seven phrases — `Every message now goes`, `through \`safe_report\`, which reports type, shape and digest`, `membership_runner_v3`, `corpus_ingest_v3`, `find none`, `Nothing is guessed, coerced to a string or dropped`, `coerced to a string, or dropped` — and every count is **0** in runner, ingest, `errors.py`, `safe_report.py` and `README.md` (probe E1; the only surviving occurrences of the two v3 module names are the two `import … as R3/I3` lines in the inherited test suite, which are real imports, not claims). What replaces them is measurably true: the runner now says *"Source identity diagnostics and transform checks retain safe_report or fixed numeric messages; these paths are not a total conversion to errors.message"* — measured: `errors.raise_violation` ×35 vs 5 `safe_report.` call sites at lines 256/259/262/266/423, i.e. exactly the identity and transform paths named (probes A6, E2). I then checked every *remaining* assertion I could test — see §2. **All held.** One wording nick remains (F-4 in §3), not an overstatement of the kind this item was about |
| **2** | **Two structurally vacuous checks** — one asserting an error sentence's wording, one iterating an empty list | **CLOSED** | Both are gone. The wording check at old line 173-175 is replaced by a real behavioural probe: a `CoercionTrap` whose `__str__`/`__repr__` count their own calls is inserted at position 0, 1 and 2 of a valid evidence list and the check requires a named refusal, `trap.calls == 0` and no canary. The empty-comprehension check at old 325-327 is **removed**, not re-dressed, and the claim it pretended to make is delegated to a real audit-hook guard. **My own sweep:** I parsed all **61** `check(...)` calls in both suites; **none** has a condition decided at parse time and **none** iterates an empty literal (probe D-A). Three are "weak but not vacuous" (they compare fixed module constants) and I name them in §3. **My mutation test is the real evidence:** I copied the package to a temp tree, reintroduced **eight** defects one at a time and re-ran both suites in isolated subprocesses. **Seven of eight were caught** (probe D-B), including all five the repair targets. The eighth is F-2 in §3 |
| **3** | **The enum identity spoof** — `require_identifier_kind` gated on `isinstance`, so an object lying about `__class__` passed and its `.value` was printed | **CLOSED** | The gate is now `type(value) is IdentifierKind and any(value is member for member in IdentifierKind)`, and `errors._safe` independently requires `type(value) is IdentifierKind` **and** identity with one of the two members, returning a **hard-coded literal** rather than `.value`. **My own spoofs, all refused with `E-COH-013` / `UnsafeErrorField`, none echoing:** (i) the `__class__`-property spoof — I confirmed `isinstance(spoof, IdentifierKind) is True` while `type(spoof) is IdentifierKind` is False, and the spoof's `.value` property was **read 0 times** across all three entry points; (ii) a **metaclass `__instancecheck__`** spoof, which the prior audit did not try; (iii) `object.__new__(IdentifierKind)` — an object whose *real* type **is** the enum but which is not a member — refused by both the runner gate and `_safe`; (iv) mutating a **genuine** member's `_value_` to the canary — `_safe` still prints `kind=question_id`, because the label is hard-coded (probes B1.1–B1.10). Python itself blocks subclassing the enum. I found no spoof that gets through |
| **4** | **The error interface generally** — can any caller- or file-supplied value still reach an exception message, its `repr`, the `__cause__`/`__context__` chain, stdout, stderr, or a written file? | **CLOSED for the JSON/data path and for the supported Python API; one adversarial-only residual, unchanged and disclosed** | Every probe below captured **all six** surfaces (message, `repr`, the whole cause/context chain walked even through `from None`, stdout, stderr, and the set of files created under a fresh temp root). Canary: `Where did Rashid park the blue van on the night of the storm?` (60 chars, under the 120-char structural limit). **Value allowlist:** 16 hostile field values — `int`/`float` subclasses with canary `__str__`/`__repr__`/`__format__`, `Decimal`, `Fraction`, `complex`, `str`, `bytes`, `list`, `dict`, a foreign `Enum`, an `IntEnum`, an object with an evil `__repr__`, a class **whose name is the canary**, and `numpy.int64`/`float64`/`bool_` — **every one refused** with one of exactly **three fixed** `UnsafeErrorField` sentences that interpolate nothing (probes B3.1–B3.16, E2). Legitimate `None/True/False/int/float/nan/inf` still format (B3.20–B3.25). **Field-NAME allowlist:** an unknown name and a `str`-subclass name are refused without echoing the name — this closes the v3/v4 carried-forward residual where a kwarg key reached `UnsafeErrorField`'s own message (B2.5, B2.6). **Code allowlist:** a `__class__`-spoofed `Code`, a foreign enum, a raw string and `object.__new__(Code)` all refused (B2.1–B2.4). **`safe_report`:** nine shapes including a custom object bare, in a list, as a dict value, as a **dict key**, triply nested, in a tuple, a `str` subclass, and a class named after the canary — all described as `<object scalar digest=…>`; across five shapes **zero** custom `__repr__`/`__str__`/`__len__` hooks fired (B4.1–B4.11, E2). **JSON/data path:** a fully canaried synthetic LoCoMo source (question, answer, every turn) driven end-to-end plus five refusal paths, and a **poisoned seed record the pipeline itself wrote** with canaries in `benchmark`, `scheme`, `runner_version` and `replicates` — all content-free, **zero files written on every refusal**, and the 846-byte written ingest manifest carries no canary (C1.10–C1.11, C5, C6.2) |
| **5** | **Field allowlisting** — does it MISS a current call site (wrong error, lost diagnostics, crash)? | **CLOSED, with one narrow NEW finding at the supported-Python-API boundary** | **Static census (probe A):** I parsed every `errors.raise_violation`/`errors.message` call in all six modules. **No literal keyword name is outside `FIELD_NAMES`**, and the three dynamic expansions (`**lengths` in ingest, `**_diagnose(...)` ×2 in `resolve_sources`) build only allowlisted keys with `bool`/`int` values. **Dynamic census (probe B5/C):** I drove **25** reachable refusals end to end and each produced its **intended** code — `E-CFG-001/002/003/004/005/007/009`, `E-SRC-001/002/003/006/007/012/013`, `E-COH-002/003/005/011/012/013/014/015/016/017/018`, `E-OUT-003` — content-free. **The one miss (NEW, F-1 in §3):** `verify_source_identity` gates `n_questions` with `isinstance(n_declared, int)`, which an **`int` subclass** passes, but `errors._safe` requires `type(...) is int`; the refusal therefore becomes `UnsafeErrorField("an error field has an unsupported value type")` instead of `E-SRC-013 [declared=…, mapped=…, reason_index=2]`. It still fails closed and **still emits nothing**. Reached only by a Python caller hand-building a mapping — **no JSON value can produce it**. My isolated original-v4 control (probe H) shows that on the same input **v4 printed the canary verbatim** into the message; v5 is therefore strictly safer here and only less informative |
| **6** | **REGRESSION** | **NO REGRESSION FOUND** | **85 regression checks of my own, 0 failures** (probe C). Evidence normalisation: **14** accepted shapes match the bound producer exactly, including the whole-string fallback, `dia_id` before `id`, tuples, `dict.fromkeys` de-duplication and the three `str(did)` coercions; **19** malformed-item shapes (first/middle/last position, nested list/tuple, int/bool/None/bytes/nan/set/object item, dict with no ids, `dia_id` = `''`/`None`/`0`/`False`/`[]`) all refuse with `E-COH-011` and **no `__str__`/`__repr__` hook fired**; **10** unsupported structures refuse with `E-COH-012`, including a `dict` subclass whose `get` returns a canary. The **raw / declared / resolved / unresolved** counts are still four distinct published fields — measured `raw=2, declared=1, resolved=1, unresolved=0` on `["D1:0","D1:0"]`. Partial-evidence policy: one partial question **stops** the run with `E-COH-002`; a fully unresolvable question does **not** and stays visible as `empty_gold`; **no override argument exists** in `ingest_locomo`'s signature. Accepted seeds: 999 and the transposed `52001207→52001702` refused, wrong replicate count refused, the accepted seed freezes and reads back, `freeze` refuses to overwrite. Manifest resolution: the accepted LoCoMo blob (59268 B) loads; a **CRLF copy is refused and diagnosed without normalising** — byte-verbatim `E-SRC-001: these manifest bytes are not the accepted manifest [crlf_to_lf_would_match=True, got_bytes=60823, lf_to_crlf_would_match=False]`; a one-byte truncation refused; the **superseded** LME manifest refused **as superseded**; `raw`/`path` mutually exclusive; **no caller-supplied expected-hash parameter exists**. N-4 stamp: a query-derived `mu` is caught; a byte-equal copy passes by design; a non-string stamp is described, not echoed. Gates: `REAL_DATA_EXECUTION_ENABLED is False` and `run_on_real_corpus` refuses first. Identity-before-parse: a recording `dict` subclass shows reads `[('get', '_accepted_manifest_sha256')]` and **nothing else** before refusal. Cluster block, `compute_results` stamp check, and both writers' refusal to overwrite all hold. **Cohort/gold/seed semantics unchanged:** from the raw Git blobs, LoCoMo = **1535 questions / 10 clusters**, LongMemEval = **470 questions**; the LongMemEval accounting still uses `per_turn_gold_markers`, still carries `NOT_APPLICABLE` + `gold_units_resolved` + `completeness_guarded_by`, and `raw_evidence_items` was **not** added to it |

---

## 2. Every remaining assertion I could test, and whether it holds

| Asserted, byte-verbatim | True? | How I measured it |
|---|---|---|
| `errors.py`: *"Unknown names, foreign enums, numeric subclasses and other values receive fixed UnsafeErrorField messages."* | **TRUE** | 16 hostile values + 2 hostile names; exactly **three distinct** messages come back, none interpolating anything (E2) |
| `errors.py`: *"This module does not certify all exception paths in its callers, inspect provenance, or erase an existing `__context__` chain."* | **TRUE** (a limitation, correctly stated) | `raise … from None` sets `__suppress_context__`, not `__context__`; my capture walks the chain and finds it present but empty of content |
| `safe_report.py`: *"Other objects are opaque: their custom repr, type name and length hooks are not called."* | **TRUE** | Five shapes, **0** hook invocations; a class named after the canary is reported as `object` |
| `safe_report.py`: *"THE 120-CHARACTER LIMIT IS NOT USED AS A GUARANTEE ANYWHERE … The limit survives only in `assert_content_free`"* | **TRUE** | `_MAX_STRING` occurs on exactly three lines of the ingest, all inside the content policy (E2) |
| runner: *"Source identity diagnostics and transform checks retain safe_report or fixed numeric messages; these paths are not a total conversion to errors.message."* | **TRUE** | 5 `safe_report.` sites, all in `verify_source_identity` and `assert_query_transform_is_inherited` |
| ingest: *"Returned in-memory structures include source text."* | **TRUE** (and creditably stated) | `questions[qid]["text"]` carries the question text |
| README: *"`resolve_sources.py` is byte-identical to its predecessor."* | **TRUE** | `c2bc0824…` at both `86a8fd7a` and `07ec929` |
| README: *"Existing `authoritative/` values are unchanged except the package-version label."* | **TRUE** | The whole diff of `accepted_configuration.py` is **two lines**, both `PACKAGE_VERSION` |
| README: *"`IdentifierKind` is now defined in `errors.py` and re-exported by the runner."* | **TRUE** | `R.IdentifierKind is errors.IdentifierKind`; `class IdentifierKind` absent from the runner |
| README: *"Runtime version fields explicitly say Codex v5."* | **TRUE** | `membership_runner Codex v5 2026-09-08`, `corpus_ingest Codex v5 2026-09-08` |
| README: *"68 checks / 45 team checks + 5 original-v4 negative-control assertions / 99 checks, exit 0; all three stderr captures are empty."* | **TRUE** | My replay: 68 / 45(+5) / 99 `ok` lines, three exit-0s, all three stderr blobs = `e3b0c442…` (empty) |
| README: *"outer guards report zero denied data-file accesses"* / *"Inner guard explicitly exercises three expected denials"* | **TRUE** | `denied_data_events: 0` in all three guard lines; the inner guard's three denials are absorbed as *allowed* by the outer guard because the synthetic `…_NONEXISTENT` path lies under the guard root — I traced this and it is consistent, not a contradiction |
| README: *"The writer refuses an existing output folder."* | **TRUE** | `FileExistsError` on `--output <existing>` (F3) |
| README: *"`PAYLOAD_HASHES.json` inventories the final candidate files, excluding itself."* | **TRUE** | 27 entries, all matching, the only unlisted file being the manifest; a one-line tamper is detected (F4) |
| README: *"NumPy scalar objects and custom numeric subclasses are deliberately rejected as error fields; current call sites use builtin counts/constants."* | **First clause TRUE; second clause is the wording nick F-4** | numpy scalars rejected (B3.14–B3.16). But two current sites forward a value that is only `isinstance`-gated, not `type`-gated — see F-1/F-3 |

---

## 3. Findings, classified

**None of these is a blocker and I do not present any of them as one.** No finding is a leak.

### F-1 — **(ii) OPTIONAL, NEW** — the narrowed value allowlist loses a diagnostic at one current call site

`membership_runner_v4.py` gates the manifest field with `isinstance(n_declared, bool) or not isinstance(n_declared, int)`; `errors._safe` then requires `type(value) in (bool, int, float)`. An `int` **subclass** passes the first and fails the second, so the refusal changes:

```
v5, n_questions = IntSub(5):  UnsafeErrorField: an error field has an unsupported value type
v5, n_questions = 5:          DesignViolation: E-SRC-013: the manifest contradicts itself [declared=5, mapped=1, reason_index=2]
```

**Class:** supported-Python-API defect (real, narrow). Not reachable from JSON — `json.loads` never produces an `int` subclass. It fails **closed**, emits nothing, and my isolated v4 control shows the same input made **v4 print the canary verbatim**:

> `E-SRC-013: the manifest contradicts itself [declared=Where did Rashid park the blue van on the night of the storm?, mapped=1, reason_index=2]`

so v5 is strictly safer here; the cost is a less informative exception of a different class (`RuntimeError`, not `DesignViolation`). **Minimum fix:** tighten the gate to `type(n_declared) is not int`, or pass `declared=int(n_declared)`.

### F-2 — **(ii) OPTIONAL, NEW** — one of the candidate's own probes passes for the wrong reason

`test_codex_v5.py:182` — `("spoofed code", lambda: errors.message(FakeCode()))`, checked as `exc is not None and CANARY not in emitted`. I reverted the closed-`Code` gate to the old `isinstance(code, Code)` on a temp copy and **both suites still passed** (probe D-B, mutant M8 — the only one of eight not caught). I then ran that mutant in an isolated process: it does **not** leak — `SENTENCES[code]` raises `KeyError(<FakeCode object …>)` whose repr is the default one — so this is a *test-discrimination* gap, **not** a security hole. **Minimum fix:** assert the exception type, e.g. `isinstance(exc, errors.UnsafeErrorField)`.

### F-3 — **(ii) OPTIONAL** — one ingest error site has no local type gate

`corpus_ingest_v4.py` passes `manifest_n_questions=mapping["n_questions"]` at the `E-COH-005` site without a type check of its own; it relies entirely on the accepted-manifest hash pin. With a synthetic binding I confirmed a **string** `n_questions` there yields `UnsafeErrorField` rather than `E-COH-005` (probe G2.c). **Unreachable in practice:** the two pinned manifests carry exact ints (1535 and 470, read from the raw blobs), and this is *not* a v5 regression — v4's `_safe` also refused `str`.

### F-4 — **(iii) WORDING** — one README clause is slightly wider than the code

*"current call sites use builtin counts/constants"* is true of every literal site, but two sites (`declared=n_declared`, `manifest_n_questions=mapping["n_questions"]`) forward a caller- or file-derived value that is only `isinstance`-gated. **Minimum fix:** *"…apart from two manifest-count fields, which are `isinstance`-gated upstream."*

### Recorded, unchanged, and correctly disclosed — not re-opened

- `safe_report.counts()` still interpolates its kwarg **key** and a `type(...).__name__` into its own `TypeError`. Unchanged from v4/v3; the single call site uses literal keys (`missing=`, `unexpected=`) and `int` values, so it is reachable only by an adversarial arbitrary-code caller. **Class (iii)/adversarial.**
- `membership_scaling_core.safe_write_json` echoes the **output path** verbatim when refusing to overwrite. That is the closed core (`bc2282d3…`), byte-unchanged and out of this delta's scope; I record it, I do not raise it.
- The guarded launcher flags data files by suffix (`.json/.jsonl/.csv/.gz`) or a `beam`/`dataset` path part, and observes **Python** `open`/`scandir`/`listdir` only — not native or subprocess I/O. The module says exactly this. My negative control shows it is not decorative (F1: a `.json` read outside the root is denied and the launcher exits 1).
- Three checks are **weak but not vacuous** (probe D-A): `test_runner_ingest_v4.py:172` compares two fixed enum values; `test_codex_v5.py:170` and `:242` compare a counter and a module constant. All three *can* fail; none is structurally vacuous.

---

## 4. What I actually ran

Interpreter: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\locomo_reproduction_tmp_20260907\venv\Scripts\python.exe`
— Python `3.13.15`, numpy `2.3.5`, scipy `1.17.0`, scikit-learn `1.8.0`, pandas `2.2.3`, with `PYTHONHASHSEED=0`
and `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`. Used as an interpreter
only; nothing installed, nothing written inside it.

1. `git clone https://github.com/haliltalhaertan/llmzip.git` into my **own** scratch directory — not the
   preparer's tree and not any existing `scratchpad/llmzip_*` directory — plus a detached worktree at
   `07ec929`. I set `core.autocrlf=false` and `core.eol=lf` **locally in my own clone only**; I changed
   no global Git setting and added no `.gitattributes`. I verified the checkout is byte-faithful:
   nine payload files hash identically to their raw blobs (ok=9, bad=0).
2. `git cat-file blob <commit>:<path> | sha256sum` for every identity in §6 — never from a checkout.
3. `python -B p_manifest.py` — `PAYLOAD_HASHES.json` vs the extracted blobs: **27/27 match**, the only
   on-disk file not listed is the manifest itself.
4. `python -B probe_a_census.py` → `probe_a_out.txt`. Static AST census: field names, value-expression
   shapes, `**kwargs` expansions, interpolations inside every `raise`, and the `raise_violation` vs
   `safe_report` counts.
5. `python -B probe_b_errors.py` → `probe_b_out.txt`. **PASS=64 FAIL=8 INFO=10.** *Seven of the eight
   FAIL lines are my own wrong expectations, and I say so rather than dressing them up:* B5.16–B5.19,
   B5.31 used `"conversation_cluster"` as a scheme name when the accepted schemes are `("question",
   "cluster")`; B5.20 and B5.22 expected a later code than the one that legitimately fires first
   (`E-SRC-007` before the mapping stamp; the core's authorization refusal before `E-GAT-001`). All are
   re-run correctly in probe C. **The one real FAIL is B5.30 = finding F-1.**
6. `python -B probe_c_paths.py` → `probe_c_out.txt`. **PASS=85 FAIL=0 INFO=5.** Seeds, gates,
   identity-before-parse, manifest resolution, evidence normalisation, end-to-end canaried ingest,
   the written manifest, the LongMemEval accounting, the N-4 stamp.
7. `python -B probe_d_vacuity.py` → `probe_d_out.txt`. Static sweep of all 61 `check(...)` calls, then
   **eight mutants** on temp copies, both suites re-run in isolated subprocesses per mutant. Baseline
   copy passes; **7/8 caught**; the survivor is F-2.
8. `python -B probe_e_claims.py` → `probe_e_out.txt`. **PASS=24 FAIL=0.** Claim accuracy, the fixed
   `UnsafeErrorField` message set, `evidence/` vs `evidence_final/`, `FIELD_NAMES` hygiene.
9. `python -B probe_f_harness.py` → `probe_f_out.txt`. **PASS=5 FAIL=0.** Guard negative and positive
   controls, the output-folder refusal, tamper detection, the `compute_results` stamp check.
10. `python -B probe_g_item5.py` → `probe_g_out.txt`, and `python -B probe_h_v4control.py` →
    `probe_h_out.txt`. The item-5 sites pinned down, with the original-v4 control **in its own process**
    (I checked `errors.__file__` and `membership_runner_v4.__file__` resolve to the v4 base directory,
    precisely because several package versions share the module names `errors`, `safe_report` and
    `authoritative`).
11. **Replay of the candidate's own harness**, LF worktree, fresh output folder:
    `python -B …/validate_candidate.py` → `PAYLOAD PASS 27 files`; then
    `python -B …/validate_candidate.py --output <new dir>` → status `PASS`, three suites exit 0.
    `test_runner_ingest_v4.stdout` = `2dbd5760…` and `test_codex_v5.stdout` = `88a07bdf…` reproduce the
    committed `evidence_final/` blobs **byte-for-byte**; the core suite's stdout differs only in
    temp-directory names and is **identical after normalising them**. Saved as `replay_*` in this
    namespace.

**Does the harness check what it claims?** Yes, with the scope it states. `validate_candidate.py`
verifies the payload inventory (and catches a one-line tamper), pins the interpreter and package
versions, runs the three suites under the guard, and re-verifies four inherited files against the raw
`86a8fd7a` blobs — it does **not** claim to be an audit, and its `RESULTS.json` says
`"evidence_kind": "implementation-team synthetic tests; NOT independent audit"` and
`"claude_independent_audit": "PENDING"`. `guarded_suite.py` observes Python `open`/`scandir`/`listdir`
data events and denies those outside its temp root — I proved both directions with my own synthetic
suites. Neither overstates itself. One caveat worth naming: `validate_candidate.py` relies on `assert`,
so running it under `-O` would silently skip its checks; the documented invocation uses `-B`.

---

## 5. The branch-point artefact — confirmed, not raised as a finding

`git diff --name-status origin/main 07ec929` shows 125 `A`, **6 `D`** and 2 `M`. I confirmed this is a
branch-point artefact and not a deletion: the merge base is `16019724564b5ac8db4a4d2d8bb08f98feb45c09`,
and each of the six "deleted" documents is **absent at the merge base** (`git cat-file -e` fails for all
six), i.e. they were added on `main` after the branch point. The two `M` files are
`docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json` — the same effect. Against its **actual parent**
`86a8fd7a` the commit is **purely additive: 28 files, every entry `A`, all inside the codex_v5
namespace, nothing outside.** I raise no finding here.

---

## 6. Identities verified — from raw Git objects only

Every hash below was produced with `git cat-file blob <commit>:<path> | sha256sum` in a fresh clone of my
own. This machine's **system** Git config sets `core.autocrlf=true` and the repository ships no
`.gitattributes`, so a default Windows checkout hashes differently; I never hashed a checkout for
identity.

**Commits**

| what | sha |
|---|---|
| the candidate | `07ec929243068914676a0f30efd10c9f294c7e71` |
| its parent — the v4 candidate (base) | `86a8fd7a73a0d4e045666e692cd7e2016f134885` |
| the prior closure check (the specification) | `6b3de298850edf7a7696683726316b83909f5b6e` |
| merge base of the candidate with `main` | `16019724564b5ac8db4a4d2d8bb08f98feb45c09` |
| `origin/main` — this audit branch is parented on it | `a5bc6bd272402a8b6d7e823fde21a6b367a6f0bd` |

**The candidate package's 28 blobs at `07ec929` — all 27 manifest entries match `PAYLOAD_HASHES.json`**

| path | sha256 |
|---|---|
| `CLAUDE_AUDIT_PROMPT.md` | `7bdae4f4465c122ce2e6b90966b2b28c1118c7effde94e33d12aef2215d77734` ✅ matches the brief |
| `PAYLOAD_HASHES.json` | `8879e78e88df01395fef6c45c088f265fcd6cf7692b22b75872ee48137d02955` ✅ matches the brief |
| `README.md` | `5c5a2d452baa835b16e7af0dd7b5171ee6d7e1ac7776a89d8f25ae26376abde7` |
| `errors.py` | `1f5912611d8fbd943a55ab90e737e2e3c6f0b6f14048cc439881dbd90ea9930c` |
| `safe_report.py` | `be4b3156edce0799d60dbb2a88a7e39314c450f38d417d044de85a803e6d126e` |
| `membership_runner_v4.py` | `32c56c6c394169e587c454ae9978accc2c7a33bffcf37698a92029a7886813a3` |
| `corpus_ingest_v4.py` | `bcb79852aee522fcd96427cfbdf520c7aa7fcd87b6727fdd309fade5bc1fcc29` |
| `authoritative/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty) |
| `authoritative/accepted_configuration.py` | `47ccc1717a9be6f0cb42008cd38d625dbc3b6ba73f717e6b11c09ee93627fee9` |
| `authoritative/resolve_sources.py` | `c2bc0824f62acd68dcedb4713abcdcd91e4014194082a62d359ec92ac564a992` ✅ **identical to v4's** |
| `test_runner_ingest_v4.py` | `1e0c853c090e506c93aa9a0ab13292fb4ff0bd5396d300cec857878a2844c461` |
| `test_codex_v5.py` | `0558211434694308fb2c3f1983b63731010945079d2bc575143e10037d7ec6a2` |
| `guarded_suite.py` | `66d4c382c924c01494d2caf10580ed13614bc3eee03accdfba882befa33e8b7b` |
| `validate_candidate.py` | `a318ce188bd4c58aeb04281bab5b85c442db307d70990bf558225d432091e23a` |
| `evidence_final/RESULTS.json` | `fb7b23d367e434c4487e922a6687ba248cefdd4ccba1e65bfbf95eab33c1543f` |
| `evidence_final/test_runner_ingest_v4.stdout.txt` | `2dbd57606e84b256e3031d5abe450a36b9b7e91e821ecd36298b61c62398c8c4` ✅ **my replay reproduces this exactly** |
| `evidence_final/test_codex_v5.stdout.txt` | `88a07bdf08cb242747eb277455500147a4e30ab4f6f1d47e2e48248ffd20e250` ✅ **my replay reproduces this exactly** |
| `evidence_final/test_membership_scaling_core.stdout.txt` | `3c47beaac8dd7cbe385d88011fe0c5adb21ccd6c3d08eb8eb5f99a0eb260ffd1` (temp-path dependent; identical after normalisation) |
| `evidence_final/*.stderr.txt` (×3) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (all empty) |
| `evidence/` (×7) | development record; `RESULTS.json` `747075b8…`, two stdout blobs differ from `evidence_final/`, three stderr blobs and `test_codex_v5.stdout.txt` are identical to it. The README says `evidence/` is superseded, and it is |

**The v4 base blobs at `86a8fd7a` I diffed against** — `membership_runner_v4.py` `3ea4444e…`,
`corpus_ingest_v4.py` `10e691b8…`, `errors.py` `b99132ac…`, `safe_report.py` `c7f4f0a0…`,
`accepted_configuration.py` `fc533825…`, `resolve_sources.py` `c2bc0824…`,
`test_runner_ingest_v4.py` `fbe249eb…`. All match the prior audit's §6.

**Inherited, byte-unchanged at `07ec929`**

| path | sha256 |
|---|---|
| `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` — matches `accepted.BOUND_CORE` |
| `…/binding/PROPOSED_mapping_locomo.json` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` (59268 B; 1535 q / 10 clusters) |
| `…/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` (470 q) |
| `…/binding/PROPOSED_mapping_longmemeval.json` (SUPERSEDED) | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` — refused **as superseded** |
| `…/binding/PROPOSED_bootstrap_seeds.json` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` |
| the prior closure report @ `6b3de298` | `8ccde7f464ec1206d0fce3feeb3305eb5226f0212e1d62f148bde4c52e3f0ea2` ✅ matches the brief |

---

## 7. What I did NOT verify, stated rather than implied

- I did **not** read, open, download, hash or **scan** `locomo10.json`, `longmemeval_s_cleaned.json`, any
  `audit/conv_*.json`, or anything under a BEAM or dataset directory. Every source, manifest and seed
  record my probes touched is a small fake written by the probes into a fresh temp directory; the
  accepted manifests were read only as **raw Git blobs** (id lists and counts, not corpus). Bound
  source/manifest bindings were overridden per probe, visibly and restored in `finally` blocks. The one
  file I created named `locomo10.json` lives inside my own temp root and contains only canary strings.
- I have **not** verified that the bound cohorts correspond to anything in the real corpora, nor the two
  bound source hashes or byte sizes against the real files.
- I did **not** re-audit the computation core, the design, the preregistration, the estimand, the
  statistics, the accepted cohort, or the accepted seed **values**. I confirmed the core blob is
  byte-unchanged and matches `BOUND_CORE`; I did not reopen it.
- I did **not** prove that no leak path exists. I enumerated every interpolated expression inside every
  `raise` in the package by AST, read every plain `raise`, drove 25 reachable refusals plus ~40
  adversarial constructions, and report what I found. The runner's two remaining raw interpolations are
  both `core.DIM`, a module constant.
- I did **not** re-verify the LongMemEval single-component inheritance tag, which is asserted as
  inherited from Task 3A.1 and provenance-verified elsewhere.
- The mutation test in probe D is a lower bound on suite strength, not a completeness proof: eight
  mutants is eight mutants.

---

## 8. Files in this namespace

| file | what it is |
|---|---|
| `CODEX_V5_REVIEW.md` | this report |
| `CODEX_V5_REVIEW.md.sha256` | sha256 of the **committed blob** of this report (method below) |
| `p_manifest.py` | `PAYLOAD_HASHES.json` verification against the extracted raw blobs |
| `probe_a_census.py` / `probe_a_out.txt` | static AST census of every `errors.*` call site and every `raise` |
| `probe_b_errors.py` / `probe_b_out.txt` | item 3 and item 4 — enum spoofs, the closed `Code` set, the value allowlist, `safe_report` |
| `probe_c_paths.py` / `probe_c_out.txt` | item 6 — 85 regression checks |
| `probe_d_vacuity.py` / `probe_d_out.txt` | item 2 — static vacuity sweep plus the eight-mutant test |
| `probe_e_claims.py` / `probe_e_out.txt` | item 1 — claim accuracy, evidence dirs, `FIELD_NAMES` hygiene |
| `probe_f_harness.py` / `probe_f_out.txt` | the harness: guard controls, output-folder refusal, tamper detection |
| `probe_g_item5.py` / `probe_g_out.txt` | item 5 pinned down, site by site |
| `probe_h_v4control.py` / `probe_h_out.txt` | the original-v4 control for item 5, in its **own** process |
| `replay_RESULTS.json`, `replay_test_*.stdout.txt` | my replay of `validate_candidate.py` into a fresh folder |

Replay: `python -B probe_<x>.py <candidate package dir> <core dir> [<worktree root>]` from a
byte-preserving (LF) checkout of `07ec929`; probe D also takes the `drafts/v52` directory and the
interpreter path.

**Method for the report hash.** The value in `CODEX_V5_REVIEW.md.sha256` is the sha256 of the **raw Git
blob** of `CODEX_V5_REVIEW.md`, computed as
`git cat-file blob <commit>:audit_v52_codex_v5_repair_review_2026_09_08/CODEX_V5_REVIEW.md | sha256sum`
— **not** of the checked-out file, which differs on a default Windows checkout. Because the hash cannot
be inside the file it describes, it is committed in a second commit that changes nothing else, and the
sidecar names the commit whose blob it pins.

---

## 9. What this authorises

Nothing beyond the repair package. No seal, no HMAC, no `--mode run`, no `--mode finalize`, no
representation fitting, no retrieval, ranking, bootstrap or pilot on real data, no corpus read. M-1/M-2/M-3
are still absent and require their own authorized work. Task 4F1 remains
`SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`. `main` and the Continuity Ledger are
untouched by me; updating them is the Continuity Lead's responsibility.
