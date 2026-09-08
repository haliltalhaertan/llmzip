# Delta closure check — runner + ingestion v4

**Auditor:** independent, cold start. Did not write the reviewed code and assumed no claim in it is true.
**Date:** 2026-09-08.
**Subject:** branch `impl/v52-runner-ingest-v4-2026-09-08`, commit
`86a8fd7a73a0d4e045666e692cd7e2016f134885`, namespace
`drafts/v52/membership_runner_ingest_v4_2026_09_08/`.
**Specification:** the delta closure check at `audit/v52-runner-ingest-v3-closure-2026-09-08` @
`dc4c47dafc6f4dfe40e8bfacebca910f6b8f75da`, report blob sha256
`079dc9726529595d4a17472afa7837f2b472b7643f89bf25003f9cef46404f7b` (verified myself — §6),
verdict `CLOSURE PASS WITH FINDINGS`.

---

## VERDICT: `CLOSURE PASS WITH FINDINGS`

**What this verdict covers, stated explicitly.** It covers **ONLY** the three items the v3 closure
check left open — **evidence normalisation** (`_normalise_evidence`), **the two remaining error
paths** (`validate_identifier`'s `kind`, `verify_source_identity`'s `n_questions` conversion) and
**claims and labels** — plus the wiring those touch, and a regression pass over what earlier checks
closed. It does **NOT** extend to:

- the **representation stage** (M-1/M-2/M-3) — I confirmed only that it was **not** added (probes
  A1–A3);
- **the experiment as a whole** — its design, preregistration, estimand, statistics, accepted cohort,
  accepted manifests, accepted seed **values** or environment lock;
- the **closed computation core** (blob `bc2282d3…`), which I treated as independently closed, did
  not reopen, and verified byte-unchanged (§6);
- anything the v2 and v3 closure checks already closed, except as regression.

**Why the verdict is what it is.**

- **Evidence normalisation is CLOSED.** This is the substantive item and it is genuinely fixed. Five
  of the six shapes the v3 check constructed are now refused; the sixth is not malformed at all under
  the bound contract and is now *truthfully accounted for* by a new published field. I wrote **29
  malformed shapes of my own**, including nine the preparer did not test, and **could not find one
  that passes through and produces an under-counted gold set**. Nothing is dropped from a list.
- **Both error paths are CLOSED.** `kind` is a member of a closed enumeration; the `int()` conversion
  is gone and replaced by an explicit type check that also excludes `bool`. Twelve `kind` canaries and
  nine `n_questions` canaries, plus fifteen adjacent manifest-field canaries, all refuse by named code
  with no content on **any** captured surface. I then hunted the other `int()` sites and the callers,
  caller-supplied and file-supplied, and found no escape.
- **Claims and labels are NOT fully closed, and that is the reason for "WITH FINDINGS".** Two module
  headers were corrected to `v4` and no fourth universal sentence is asserted — both true. But
  **two byte-verbatim statements that are asserted in this package's own voice are false**, and both
  are inherited rather than new:
  - `membership_runner_v4.py:18-19` still asserts *"Every message now goes through `safe_report`"* —
    a sentence the v2 and v3 checks each falsified, and which is false again here (the runner calls
    `errors.raise_violation` 35 times and `safe_report.*` 6 times);
  - `errors.py:20-24` still names **`membership_runner_v3`** and **`corpus_ingest_v3`** as the tested
    surface — modules that are not in this package — and says the tests *"find none"* against
    precisely the surface on which the v3 check **did** find two leaks. `errors.py` **was** edited in
    v4 (ten codes and ten sentences added), so this was an available line to fix.
- **No regression.** Everything the v2 and v3 checks closed still holds under my own probes, all four
  committed evidence files reproduce **exactly**, and the preparer's negative controls are real, not
  vacuous — their documented `sys.path` insertion-order fix is correct, and I verified why.

**One NEW defect, out of the closure scope, marked as such.** `require_identifier_kind` gates on
`isinstance(value, IdentifierKind)`, which an object that lies about its own `__class__` passes; the
value then reaches `errors._safe`'s `Enum` branch and is printed verbatim. Byte-verbatim capture in
§2/N-1. It is **not** reachable from any JSON value and no honest caller can construct it, so I
classify it **(ii) optional**, not a blocker — but it does mean the inventory sentence *"`kind` is a
member of `IdentifierKind`, a closed enumeration"* is enforced by `isinstance`, not by membership.

**Whether this authorises anything.** No. Nothing was sealed, no HMAC computed, no `--mode run` or
`--mode finalize` invoked, no representation fitted, no bootstrap or pilot run on real data, **no real
corpus file was read, opened, downloaded, hashed or scanned**, and no candidate file was modified.
Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## 1. Per-item table

| # | Item | Disposition | My evidence | Genuine negative control? |
|---|---|---|---|---|
| **1** | **EVIDENCE NORMALISATION** — `_normalise_evidence` silently discarded any entry it could not turn into a reference id, so `declared == resolved`, `unresolved = 0` and a smaller-than-declared gold set looked complete | **CLOSED** | **Contract transcription is CORRECT** — I read `norm_evidence` from the raw blob of `research/v52/locomo_sign_mechanism_replication.py` @ `692f599e` (sha256 `a6ecee02e5d6…`, lines 107-124), retyped it into my probe as an oracle, and every accepted shape in v4 returns **exactly** what the producer returns: `None`/`[]`/`()` empty; a string's `D<n>:<n>` ids; the **whole-string fallback** when a string contains none; list/tuple of such strings or dicts carrying `dia_id`/`id`; `dia_id` before `id`; `dict.fromkeys` de-duplication (B1–B7, C30–C39). **The three cases are genuinely separated**: valid-empty returns `([], 0)` and raises nothing; a malformed **item** raises `E-COH-011`; an unsupported **structure** raises `E-COH-012`; the two are different codes with different sentences, and an empty list is not reported as a malformed item (B8–B11). **Nothing is dropped**: I wrote **29 shapes of my own** — malformed at **first / middle / last** position, a list containing a list, a list containing a tuple, nested lists, `float('nan')` as item and as top-level, `bool`, `bytes`, a `set`, `object()`, a generator, a dict subclass with no id keys, `dia_id` = `''`/`None`/`0`/`False`/`[]`, `id = ''`, a `str` subclass, a `dict` subclass, and a dict subclass whose `get` hands back a canary — **every one is refused, none leaks content** (C01–C33). **Three counts are three concepts and FOUR published fields**: on `["D1:0","D1:0"]` the written manifest carries `raw_evidence_items=2, declared_reference_ids=1, resolved_reference_ids=1, unresolved_reference_ids=0` (D13, D15, **T1–T3, measured on disk**); dedup of valid repeats is byte-identical to v3 (D14). **No question excluded, no gold repaired, no cohort changed**: on a clean source the gold rows are byte-identical to v3's (D16–D18), and on a synthetic source of the **accepted 1535-question / 10-cluster shape** the run resolves clean with `raw = declared = resolved = 1535` (R1, R5–R7). **"One valid + one malformed" now stops and writes nothing**: ten end-to-end cases, each refused, each content-free, each writing **zero bytes** (D01–D08) | **Yes, and it is not vacuous.** For every one of the 29 shapes and all ten end-to-end cases I drove **v3's own `corpus_ingest_v3`** in the same process and recorded what it did. I verified `I3.__file__` is the v3 package's file (S1–S3), that the modules v3 picks up from `sys.modules` are v4's but byte-identical for `safe_report`/`authoritative` and a **strict superset** for `errors` (S6–S9), and that `_normalise_evidence` in v3 contains **no `raise` and no reference to `errors` at all** (S10) — so v4's `errors` cannot change the control's behaviour. Measured: v3 returns `['D1:0']` and publishes `declared=resolved=1, unresolved=0, empty_gold=0, partial_loss=0` on exactly the sources v4 refuses (D01–D08, M1–M5, T8–T9) |
| **2** | **THE TWO REMAINING ERROR PATHS** | **CLOSED** | **`kind`:** `IdentifierKind` is an `Enum` with exactly `["question_id","cluster_id"]`; `require_identifier_kind` admits only a member (E1, E2). **Twelve** canary kinds — plain `str`, the canonical-looking `"question_id"`, `bytes`, `int`, `None`, a list, a dict, an object whose `__str__`/`__repr__` is the canary, a **dynamically built `Enum`** whose value is the canary, and a `str` subclass — all refuse with `E-COH-013` and **none echoes** (E3–E12). Genuine identifier faults still refuse by code with `kind=question_id, position=3` across nine bad values (E14), the bad identifier's own text is not echoed (E15), the duplicate path does not echo (E16), a valid id is returned unchanged (E17), and both in-package call sites pass enum literals (E18). **`n_questions`:** no `int()` conversion survives — the only textual occurrence is a comment quoting the old code; the check is `isinstance(n_declared, bool) or not isinstance(n_declared, int)` and the later comparison is `len(expected_map) != n_declared` with no coercion (F0b, and `grep` of every `int(` in the module). **Nine** `n_questions` canaries — canary `str`, the numeric string `"1"`, `1.0`, `True`, `None`, a list, a `str` subclass, an object with `__int__`, and the field **absent** — every one refuses with `E-SRC-012`, **content-free, with no `ValueError` and no `TypeError`** (F1–F9). The source contract's expected types are validated **explicitly** for all three fields (F10–F15) and **no new value is accepted by silent conversion**: `"1"` and `1.0` are refused where v3 accepted them (F16, F17). A well-formed manifest still passes (F18). Surface captured for **every** probe: message, `repr`, the whole `__cause__`/`__context__` chain, stdout, stderr, and files written — **zero files written on any refusal** (F26). **Other paths hunted:** AST census of every interpolation inside every `raise` in the package — runner **5 (2 raw, both `core.DIM`)**, ingest **0**, `resolve_sources` **0**, `accepted_configuration` **0**, vs **19 (10 raw)** in `membership_runner_v3.py` (G1, G1b); the seven plain `raise`s enumerated and read (G2); the other `int()` sites (`freeze_bootstrap_seed`, `compute_results`) driven with caller-supplied **and** file-derived canaries — all refuse content-free (L1–L5); the manifest internal-inconsistency and six-check problem paths driven with caller **and manifest**-supplied canaries — all describe by `<str len=… digest=…>` only (F19–F25, G8–G10); reaching `verify_source_identity` **behind** the stamp check via a hand-forged mapping still refuses content-free (G7) | **Yes.** Every `kind` and `n_questions` probe was run against **v3's** `membership_runner_v3` in the same process. Measured: v3 leaks the canary through `kind` on 6 of 12 (E3, E5, E8, E9, E10, E12) and raises `ValueError("invalid literal for int() with base 10: 'Where did Rashid park the blue van on the night of the storm?')` on `n_questions` (F1, F7). I verified v3's `validate_identifier` raises plain f-strings and never touches `errors`, and that `int()` is a builtin — so v4's `errors` module cannot make either control vacuous (S11, S12). v3 also **silently accepted** `"1"`, `1.0`, `True` and an `__int__` object (F2–F4, F8, F17b) |
| **3** | **CLAIMS AND LABELS** | **NOT fully closed — two asserted-and-false statements survive (N-2, N-3). No NEW universal claim is asserted.** | **No fourth universal is asserted**: the three earlier sentences appear **exactly once each**, inside the falsification inventory, in the intended way (H5, H6). **The stale version labels ARE corrected** in the two named places: `membership_runner_v4.py:1` = `"""Corpus-bound runner v4 …` (was `v2`), `corpus_ingest_v4.py:1` = `"""Corpus ingestion v4 …` (was `v2`), and `INGEST_VERSION = "corpus_ingest v4 2026-09-08"` (H1–H3). The inventory names what is untested (H8) and the bound contract is cited by file **and commit** (H9). **But two statements are asserted and untrue** — quoted byte-verbatim in §2 as N-2 and N-3: `membership_runner_v4.py:18-19` (*"Every message now goes / through `safe_report`"* — measured: `errors.raise_violation` ×35, `safe_report.*` ×6) and `errors.py:20-24` (names `membership_runner_v3` / `corpus_ingest_v3`, and says the tests *"find none"* on exactly the surface where the v3 check found two leaks). A third, smaller one: *"Nothing is guessed, coerced to a string or dropped"* — the accepted dict branch **does** coerce, `out.append(str(did))` (N-4) | **Partly.** The preparer's suite checks the labels and the inventory structurally (their §4). Two of their 70 checks are **structurally vacuous** and I say so (N-5): line 174 tests the *wording of an error sentence*, not behaviour; line 325-327 iterates an empty list so the assertion is unconditionally `True`. Both underlying claims happen to be **true** — I verified the coercion behaviour and the absence of any real-corpus path independently — but the tests do not test them |
| **REGRESSION** | the nine D-5 paths F12–F20, D-1, LongMemEval accounting, D-2, D-3, D-4, D-6, D-7, D-8, source trust, gates, identity-before-parse, the cluster block, the writers | **NO REGRESSION** | 35 regression checks of my own, all pass. D-4: a CRLF copy of the accepted manifest is refused **and diagnosed without normalising** — byte-verbatim `E-SRC-001: these manifest bytes are not the accepted manifest [crlf_to_lf_would_match=True, got_bytes=60823, lf_to_crlf_would_match=False]` (P4); the **superseded** manifest refused **as superseded** under both benchmarks (P3, P3b); a one-byte truncation refused (P5); no override argument exists (P6, P8). D-3: seed 999 and the transposed `52001170` refused, a hand-forged record caught on read (Q1–Q3). F20: nothing read out of a poisoned seed record reaches a message (Q4). D-2 (Q5), F12 ordering (Q6), the v3 N-4 residual still closed — empty mapping → `E-SRC-006`, not `KeyError` (Q7). The accepted configuration still runs end to end on the **accepted 1535-question / 10-cluster** cohort (Q8). D-6 stamp check (Q9), N-3 LongMemEval cluster block (Q10), writers refuse to overwrite (Q11, T6), gate closed by default and refuses first (Q12, A4, A5), core blob matches its bound hash (Q13). Identity-before-parse re-measured with a recording `dict` subclass: `reads=[('get','_accepted_manifest_sha256')]` and nothing leaks (G11). D-1: one partial question in 1535 stops the whole run; a fully unresolvable question does **not** and stays visible as `empty_gold` (R2, R3). LongMemEval accounting **unchanged**: `declared_reference_ids: null` + `NOT_APPLICABLE` + `gold_units_resolved` + the four `completeness_guarded_by` guards, and the two benchmarks' field **sets** still differ — `raw_evidence_items` was **not** added to LongMemEval (R13, R14). D-7 (`1`, `"true"`, `null` refused; ragged arrays refused) and D-8 (R10–R12, R15, R8). The content policy is byte-identical to v3 and still refuses a >120-character string (T7b) | **Yes.** The preparer's `test_runner_ingest_v4.py`: **70 checks, 0 failures, 13 negative controls**, reproducing `evidence/v4_delta_tests.txt` with an **empty diff** after temp-dir normalisation. `test_runner_ingest_v3.py` 60 ok / 0 fail reproduces `evidence/v3_regression.txt` **exactly**; `test_membership_scaling_core.py` 99 ok / 0 fail reproduces `evidence/core_regression.txt` **exactly**; the v2 suite 82 ok / 0 fail; both v1 suites `ALL PASS`. **The `sys.path` fix is correct**: the loop `for _p in (CORE, V3, HERE)` leaves `[HERE, V3, CORE]`, and `errors` is imported **before** any v3 module, so `errors` binds to v4's — verified by `errors.__file__` (M0). Their comment that this is behaviour-neutral is also correct: I confirmed `safe_report` and `authoritative/` are **byte-identical** v3↔v4, `errors` v4 is a **strict superset** (35 → 45 codes, additions only), and the three v3 behaviours the controls exercise never touch `errors` |

---

## 2. The findings, classified

Classified as instructed: **(i) real defect**, **(ii) optional improvement**, **(iii) wording /
claim-accuracy**. **None of these is a blocker**, and I do not present any of them as one.

### N-1 — (ii) OPTIONAL, **NEW**, outside the closure scope — the closed set is enforced by `isinstance`, not by membership

`require_identifier_kind` gates on `isinstance(value, IdentifierKind)`. An object that overrides
`__class__` passes that gate, and `errors._safe` then takes its `Enum` branch and prints `.value`
verbatim. Byte-verbatim from probe J3:

> `E-COH-016: the identifier has leading or trailing whitespace; it is REJECTED rather than stripped, because stripping would merge it with its neighbour [kind=Where did Rashid park the blue van on the night of the storm?, length=2, position=0]`

The object required (probe J1/J2, `isinstance(fake, IdentifierKind) == True` while
`type(fake).__name__ == 'FakeKind'`):

```python
class FakeKind:
    value = "<canary>"
    @property
    def __class__(self):
        return R4.IdentifierKind
```

**Severity, stated fairly.** No JSON value can do this; no parsed corpus content can do this; both
in-package call sites pass enum literals (J6, E18). It is strictly weaker than the v3 P1/P2 escapes,
which needed only a plain string. It belongs to the same class the v3 check called *"a caller
overriding its own check"* and left optional. **Minimum fix:** `if value in IdentifierKind` or
`if type(value) is IdentifierKind`, and/or make `errors._safe` require `type(value) is` a declared
enum. It also means the inventory sentence at `membership_runner_v4.py:81-82` — *"`kind` is a member
of `IdentifierKind`, a closed enumeration, not a caller string"* — is enforced by `isinstance`, which
is not quite membership.

### N-2 — (iii) CLAIM-ACCURACY — a falsified sentence is asserted for the third time

`membership_runner_v4.py:18-19`, byte-verbatim:

> `  D-5  exception messages interpolated values verbatim and unbounded. Every message now goes`
> `       through `safe_report`, which reports type, shape and digest and never content.`

This is **not** inside the falsification inventory (lines 67-92); it is in the `WHAT CHANGED` block, in
the module's own present-tense voice. It is false: `membership_runner_v4.py` calls
`errors.raise_violation` **35** times and `safe_report.*` **6** times (probe H10), so most messages do
not go through `safe_report` at all. The v2 closure check and the v3 closure check each falsified this
same sentence; it is unchanged in v4. **Minimum fix:** delete it or restate it as *"exception messages
now go through `errors.py`; `safe_report` is used where a value must be described rather than named."*
Wording only; no behaviour changes.

### N-3 — (iii) CLAIM-ACCURACY + STALE LABEL — `errors.py` names the v3 modules and says the tests found nothing

`errors.py:20-24` in the **v4** package, byte-verbatim:

> `WHAT IS AND IS NOT CLAIMED. The tested surface is: every exception raised by `membership_runner_v3`,`
> `` `corpus_ingest_v3`, `authoritative.resolve_sources` and this module, together with stdout, stderr, the ``
> `` `__cause__`/`__context__` chain, and every file those modules write. Against that surface, the tests ``
> `drive synthetic canaries - caller-supplied, file-supplied and corpus-parsed, all shorter than the`
> `120-character structural limit - and find none.`

Two problems. It names **`membership_runner_v3`** and **`corpus_ingest_v3`**, which are not modules of
this package — the stale label the brief asks about, in the one file the two corrected headers did not
cover. And *"find none"* is false **of that named surface**: the v3 closure check found two leaks
(P1, P2) in `membership_runner_v3` and quoted one byte-verbatim. `errors.py` **was** edited in v4 (ten
codes and ten sentences added, additions only — probe S8/S9), so the line was available. **Minimum
fix:** name `membership_runner_v4` and `corpus_ingest_v4`, and scope the "find none" to the v4 tests.

### N-4 — (iii) CLAIM-ACCURACY — "coerced to a string" is not quite right about the accepted branch

`corpus_ingest_v4.py:326`, byte-verbatim:

> `# Neither is repaired, coerced to a string, or dropped. Nothing is guessed.`

and `FIX_PACKAGE_V4_2026-09-08.md:20`, byte-verbatim:

> `Nothing is guessed, coerced to a string or dropped.`

Both read as absolute. The **accepted** dict branch does coerce: `out.append(str(did))`
(`corpus_ingest_v4.py:358`). Measured (N3–N5):

| value | v4 returns | the frozen producer returns |
|---|---|---|
| `[{"dia_id": 12345}]` | `(['12345'], 1)` | `['12345']` |
| `[{"dia_id": 1.5}]` | `(['1.5'], 1)` | `['1.5']` |
| `[{"dia_id": ["D1:0"]}]` | `(["['D1:0']"], 1)` | `["['D1:0']"]` |

**This is not a defect.** It is the bound contract's own behaviour, byte-for-byte, and it is not a
silent loss: a coerced id cannot resolve, so it lands in `unresolved` and the run **stops** with
`E-COH-002` (N7, content-free — N8). The sentences are true of the two **refusal** cases; they read as
statements about the function. **Minimum fix:** *"a malformed item is neither repaired, coerced nor
dropped; an accepted dict id is stringified exactly as the bound producer stringifies it."*

### N-5 — (ii) OPTIONAL — two of the preparer's 70 checks are structurally vacuous

Both underlying claims are **true** — I verified them independently — but neither check tests them.

- `test_runner_ingest_v4.py:173-175` — `check("no malformed item is coerced to a string, guessed at,
  or dropped", "str(" not in errors.SENTENCES[...] and "cannot be turned into a reference id" in ...)`.
  This inspects the **text of an error sentence**. It would pass unchanged if `_normalise_evidence`
  dropped everything. (My C01–C33 test the behaviour; and see N-4 for what the behaviour actually is.)
- `test_runner_ingest_v4.py:325-327` — `check("no real corpus was opened and no corpus scan was made
  by this suite", not any(… for p in [Path(x) for x in []]) and True)`. The comprehension is over an
  empty list, so the assertion is unconditionally `True`. I verified the claim myself instead: the v4
  package references the two real filenames only as constants in `accepted_configuration.py`, and
  every source the suite opens is written by the suite into its own temp directory.

### The v3 report's sixth shape — judged, not waved through

The v3 check listed six shapes that slipped through. Five are now refused (M1–M5). The sixth,
`"see D1:0 and also the bakery note"`, still ingests (M6, D11): `raw=1 declared=1 resolved=1
unresolved=0 empty_gold=0`. **I judge this correct and not a residual.** The frozen producer returns
exactly `['D1:0']` for that string (M7, M8) — a free-text string is **one** raw item under the bound
contract, and the prose is not a second declared reference. v4 now publishes
`raw_evidence_items = 1`, which is a truthful account of what the source presented; v3 published no
raw count at all. The preparer's fix table lists "seven malformed shapes" and does not mention this
one, so a reader could infer all six of the v3 table were refused — that is a **(iii)** wording nick on
that row, nothing more.

### Carried forward from v3, unchanged, theoretical — recorded, not re-opened

- A kwarg **key** still reaches `UnsafeErrorField`'s own message. Byte-verbatim (K2):
  `error field 'canaryKeyOdessa1987' is a str; only numbers, booleans, None and validated enum members may appear in an error message`.
  Every in-package call site uses literal keyword names; the only `**`-expansions have literal keys.
- `errors._safe` prints **any** `Enum`'s `.value` verbatim (K1):
  `E-COH-018: the cohort is empty; there is nothing to validate [x=Where did Rashid park the blue van on the night of the storm?]`.
  Reachable only by a caller that hand-builds an `Enum` — or, now, by N-1.
- The N-5 residual of the v3 check (the accepted stamp is a public constant) survives, and I confirmed
  it does **not** re-open the `n_questions` path: reaching `verify_source_identity` behind the stamp
  with a hand-forged mapping still refuses `E-SRC-012` content-free (G7).

---

## 3. What I verified in detail

### 3.1 The bound contract, checked against the raw blob rather than the preparer's prose

I read `norm_evidence` from `git cat-file blob 692f599e:research/v52/locomo_sign_mechanism_replication.py`
(whole-file sha256 `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b`, function at lines
107-124), retyped it into my probe as an independent oracle, and compared v4 against it shape by shape.
**The preparer's transcription is correct on every point I could check**, including the whole-string
fallback they say they preserved deliberately — `_normalise_evidence("not-an-id-shape")` returns
`(["not-an-id-shape"], 1)` and the producer returns `["not-an-id-shape"]` (B4). `dia_id` before `id`
(B6), tuples accepted (B7), `dict.fromkeys` de-duplication (C39, D14), and the `str(did)` coercion
(N3–N5) all match the producer exactly.

### 3.2 The interpolation census, re-run by AST

| module | interpolations inside a `raise` | raw (not `len` / `safe_report` / `.shape` / `.value`) |
|---|---|---|
| `membership_runner_v4.py` | **5** | **2** — both `core.DIM`, a module constant |
| `corpus_ingest_v4.py` | **0** | 0 |
| `authoritative/resolve_sources.py` | **0** | 0 |
| `authoritative/accepted_configuration.py` | **0** | 0 |
| `errors.py` | 2 | 2 (kwarg key, type name) |
| `safe_report.py` | 2 | 2 (kwarg key, type name) |
| *(baseline)* `membership_runner_v3.py` | 19 | **10** |

The ten raw interpolations the v3 check counted in `membership_runner_v3.py` are down to **two**, and
both are `core.DIM`. The seven plain (non-`errors`) `raise`s in the runner were read individually
(G2): one re-raises an already code-built `SourceResolutionError` message with `from None`, two format
`core.DIM` and a `.shape`, one joins `safe_report` descriptions, and three are constant strings.

### 3.3 The three delivery routes for a canary

- **Caller-supplied** — 12 `kind` canaries, 9 `n_questions` canaries, 15 adjacent manifest-field
  canaries, canary question ids, cluster ids, benchmark and scheme names, a canary seed and a canary
  replicate count. All clean except N-1's `__class__` spoof.
- **Read back out of a JSON file the pipeline itself writes** — I called `R4.freeze_bootstrap_seed`
  to write a real record, then wrote a poisoned one with canaries in `benchmark`, `scheme`,
  `runner_version` and `replicates`, and drove `read_bootstrap_seed` and `compute_results`. All clean
  (Q4, L4).
- **Parsed corpus text** — a fully canaried synthetic source (question, answer and every turn a
  canary) down the happy path and ten evidence-refusal paths, plus the LongMemEval refusals. All
  clean, **zero files written** on every refusal, and the 840-byte written ingest manifest carries no
  canary (T4).

---

## 4. What I could NOT verify, stated rather than implied

- I did **not** read, open, download, hash or **scan** `locomo10.json`, `longmemeval_s_cleaned.json`,
  any `audit/conv_*.json`, or anything under a BEAM or dataset directory. **In particular I did not
  scan the real corpus to find out whether any of the malformed evidence shapes occur in it** — the
  preparer deliberately did not, and neither did I. What I can say is that v4 refuses them
  unconditionally wherever they appear, which is what makes the question unnecessary.
- I have **not** verified that the bound cohorts correspond to anything in the real corpora, nor the
  two bound source hashes or byte sizes against the real files.
- I did **not** re-audit the computation core, the design, the preregistration or the statistics.
- I did **not** prove that no further leak path exists. I enumerated every interpolated expression
  inside every `raise` in the package by AST, read every plain `raise`, drove the two named functions
  and their callers, and report what I found.
- Every "source", manifest and record my probes opened is a small fake written by the probe scripts
  into a fresh temp directory: the **shape** of the data, none of its content. Bound source and
  manifest hash entries are overridden per probe, visibly and reversibly. The accepted LoCoMo and
  LongMemEval manifests were read as **raw Git blobs** — id lists, not corpus — to build synthetic
  sources of their exact shape with canary text as content.

---

## 5. What I actually ran

Environment: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\locomo_reproduction_tmp_20260907\venv\Scripts\python.exe`
— Python `3.13.15`, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3 — with
`PYTHONHASHSEED=0` and `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`
(echoed at the top of `probe_output_part1.txt`). Used as an interpreter only; nothing installed,
changed or written inside it. It has no `pytest`, so the suites run as plain scripts, which is how
they are written.

1. `git clone https://github.com/haliltalhaertan/llmzip.git` into my own scratch directory — **not**
   the preparer's work tree and **not** any `scratchpad/llmzip_*` directory — plus detached worktrees
   at `86a8fd7a` and `64d774a6`. I set `core.autocrlf=false` **locally in my own clone only**; I
   changed no global Git setting and added no `.gitattributes`.
2. `git cat-file blob <commit>:<path> | sha256sum` for every identity in §6. Never from a checkout.
3. `python -B probe_v4_closure.py <checkout>` — my own probes, part 1 (the harness, the scope guard,
   the bound contract, 29 malformed shapes, ten end-to-end cases). Output `probe_output_part1.txt`.
   Tally: **PASS=141, FINDING=4, OBSERVE=1, INFO=8**. All four FINDING lines are **my own check bugs
   or wrong expectations**, and I say so rather than dressing them up: `S5` inspects `sys.path` *after*
   the modules under test have run their own inserts (the modules were still resolved correctly —
   S1–S3); `S11` looks for `raise DesignViolation(f` on one line where v3 wraps it over two;
   `D09`/`D10` expected v3 to hide an unsupported **structure**, but v3 makes that case visible as
   `empty_gold=1` — as the v3 report itself said — so the control was mine to get wrong, not a v4
   defect.
4. `python -B probe_v4_part2.py <checkout>` — the two error paths, the AST census and the hunt for
   other paths (`probe_output_part2.txt`). Tally: **PASS=65, FINDING=4, OBSERVE=3, INFO=47**. Of the
   four FINDING lines, **`E13` is the real one (N-1)**; `F0` matches the *comment* that quotes the old
   `int(mapping["n_questions"])` code, not a call; `G3` is an over-strict heuristic of mine over three
   constant-string `raise`s; `H4` is N-3.
5. `python -B probe_v4_part3.py <checkout>` — byte-verbatim captures, the other `int()` sites, the v3
   report's six shapes, and the `str()` coercion (`probe_output_part3.txt`). **PASS=19, OBSERVE=4,
   INFO=4**, no FINDING.
6. `python -B probe_v4_part4.py <checkout> <repo>` — regression (`probe_output_part4.txt`).
   **PASS=35, INFO=4**, no FINDING.
7. `python -B probe_v4_part5.py <checkout>` — the written ingest manifest (`probe_output_part5.txt`).
   One FINDING line is mine: `T7` used a 61-character canary against a 120-character structural limit;
   `T7b` confirms a 121-character string **is** refused with `E-OUT-003`.
8. `python -B test_runner_ingest_v4.py` → `ALL PASS`, **70 `ok`, 0 failures, 13 negative controls**
   (`suite_v4_run.txt`); diff against `evidence/v4_delta_tests.txt` after normalising temp-directory
   names: **empty**. `test_runner_ingest_v3.py` → 60 ok / 0 fail, reproduces `evidence/v3_regression.txt`
   **exactly** (`suite_v3_run.txt`). `test_membership_scaling_core.py` → 99 ok / 0 fail, reproduces
   `evidence/core_regression.txt` **exactly** (`suite_core_run.txt`). `test_runner_ingest_v2.py` →
   82 ok / 0 fail (`suite_v2_run.txt`). `test_membership_runner.py` and `test_corpus_ingest.py` →
   `ALL PASS` each.

---

## 6. Identities verified — from raw Git objects only

Every hash below was produced with `git cat-file blob <commit>:<path> | sha256sum` in a fresh clone of
my own. This machine's **system** Git config sets `core.autocrlf=true`, and the repository ships no
`.gitattributes`, so a Windows checkout hashes differently — that is finding D-4 itself.

**Commits**

| what | sha |
|---|---|
| candidate branch `impl/v52-runner-ingest-v4-2026-09-08` | `86a8fd7a73a0d4e045666e692cd7e2016f134885` |
| its parent — the v3 candidate | `64d774a66c8af154b9421c5bdd1b3964d0b82fe4` |
| the v2 candidate | `9b569687b394b0507fdeefc5abe456a9958e0788` |
| the previous closure check (the specification) | `dc4c47dafc6f4dfe40e8bfacebca910f6b8f75da` |
| the frozen producer (the bound evidence contract) | `692f599eedeb7e7a649443f24ff507e8c4d1c17d` |
| `origin/main` — this audit branch is parented on it | `c894caa92c16818f86926a5c7e6f776b6b051cb7` |

**The candidate commit is purely additive.** `git diff --stat 64d774a6 86a8fd7a` = **12 files, 2460
insertions, 0 deletions**, all `A` (added), all under
`drafts/v52/membership_runner_ingest_v4_2026_09_08/`. `git diff --name-only` restricted to everything
**outside** that namespace is **empty**, and `git diff --name-status` over the **whole v3 package** is
empty.

**Blobs — byte-unchanged at `86a8fd7a` (compared blob-for-blob against `64d774a6`)**

| path | sha256 | |
|---|---|---|
| `audit_v52_runner_ingest_v3_closure_2026_09_08/V3_CLOSURE_REPORT.md` @ `dc4c47da` | `079dc9726529595d4a17472afa7837f2b472b7643f89bf25003f9cef46404f7b` | ✅ matches the brief |
| `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` | ✅ closed core, byte-unchanged, and matches `accepted.BOUND_CORE` |
| `…/membership_runner_v1_2026_09_08/membership_runner.py` | `b322f85147733ead9494c33e5c78c02c2361a1986241de54c0c2aa6cc137a6d0` | ✅ v1 byte-unchanged |
| `…/membership_ingest_v1_2026_09_08/corpus_ingest.py` | `7dc084d8795c7e7d07270b866fdbc5e9c597508cbf331862b4075f9943fdf219` | ✅ v1 byte-unchanged |
| `…/membership_runner_ingest_v2_2026_09_08/membership_runner_v2.py` | `56be6a6b9711ecb03cd3021e86be5299dc57c01f18e964788cef678e63e89504` | ✅ v2 byte-unchanged |
| `…/membership_runner_ingest_v2_2026_09_08/corpus_ingest_v2.py` | `6b8d89ae822506bc937e3ccc9e3427aca9c28cbcd5c68c269049ebb077ade82d` | ✅ v2 byte-unchanged |
| `…/membership_runner_ingest_v3_2026_09_08/membership_runner_v3.py` | `29379aaccb31c7e634e75290d0108f0ac49c90028733a7000d686e9302770fc0` | ✅ v3 byte-unchanged |
| `…/membership_runner_ingest_v3_2026_09_08/corpus_ingest_v3.py` | `4d3450cf20af5233b4d92e627773b070779e2127c517f7441f94a8db5b530523` | ✅ v3 byte-unchanged |
| `…/membership_runner_ingest_v3_2026_09_08/errors.py` | `b115fdf99545ff6eff540d2d28abce5d9dbfd92b82cc306ea954743a1b7ef20a` | ✅ v3 byte-unchanged |
| `…/membership_runner_ingest_v3_2026_09_08/safe_report.py` | `c7f4f0a0735b8022723251af26607ea8d74654e8d692ec70145f300578bce44c` | ✅ v3 byte-unchanged |
| `…/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` | ✅ accepted manifest, 59268 B, 1535 q / 10 clusters |
| `…/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` | ✅ accepted manifest, 36598 B, 470 q |
| `…/binding/PROPOSED_mapping_longmemeval.json` (SUPERSEDED) | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` | ✅ refused as superseded |
| `…/binding/PROPOSED_bootstrap_seeds.json` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` | ✅ byte-unchanged |
| `…/membership_runner_v1_2026_09_08/CONFIGURATION_IDENTITY_2026-09-08.md` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` | ✅ byte-unchanged |
| `adapters/longmemeval_v52_adapter_v2.py` | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | ✅ byte-unchanged |
| `research/v52/locomo_sign_mechanism_replication.py` @ `692f599e` | `a6ecee02e5d6a8735a922ec2d5f0a024b3c024e0cdf03b336e16e4357f20e74b` | ✅ the bound evidence contract |

**The v4 package's own blobs at `86a8fd7a`** (sha256 of the blob content; Git object id in brackets)

| path | sha256 | oid | bytes |
|---|---|---|---|
| `FIX_PACKAGE_V4_2026-09-08.md` | `d7c451bf22bfc6da1f9989c2e5182be78c02c0bcb0135fae1803d4360ab499ff` | `09d4630f80b4` | 5143 |
| `membership_runner_v4.py` | `3ea4444e36280dccca545d5e230eb3604841f10f1decf1b6003b53549da63b9f` | `d8459b0bacef` | 35787 |
| `corpus_ingest_v4.py` | `10e691b8223a9fe6ca20622e202b8dbb78c1bfdddba0482ddcea8312d7f15381` | `e390ce99d63d` | 37535 |
| `errors.py` | `b99132ac72f25215dcd2bf4b72a798e7834dbc098431dc8fc21bbb1bf4989f14` | `677181aec180` | 11277 |
| `safe_report.py` | `c7f4f0a0735b8022723251af26607ea8d74654e8d692ec70145f300578bce44c` | `25c7cd5b314b` | 4265 |
| `authoritative/__init__.py` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1` | 0 |
| `authoritative/accepted_configuration.py` | `fc533825902fa9a523eab4f810ed05c78ce6ca949e83faa75bf45e7c46a432bc` | `e780878a7111` | 9024 |
| `authoritative/resolve_sources.py` | `c2bc0824f62acd68dcedb4713abcdcd91e4014194082a62d359ec92ac564a992` | `a84dde67add0` | 6621 |
| `test_runner_ingest_v4.py` | `fbe249eb94a4a6c6d953e0bd2da87a0fba9178b94ed7b08b5e2117b83896791f` | `ef90a016d704` | 20221 |
| `evidence/v4_delta_tests.txt` | `51fb872041e13f991b53b3751ce81560e3175f35e8a63000eee13823a6412921` | `40b02e581c92` | 6285 |
| `evidence/v3_regression.txt` | `3e33dd06b32d3de9d1b6fa17a085b65904a8696c031f7abb0929c32422144fd0` | `3bca23be11be` | 5999 |
| `evidence/core_regression.txt` | `a4f599bc53e012f7216116e8cfe7c662e27ac7521d908fb4aa517252c31a24ea` | `033308a8d481` | 8525 |

`safe_report.py` and `authoritative/` are **byte-identical to the v3 package's** (probes S6, S7).
`errors.py` differs from v3's **only by addition**: ten `Code` members and ten `SENTENCES` entries,
with no existing code or sentence altered (S8, S9) — which is why the v3 modules can run against it
without the negative controls becoming vacuous.

---

## 7. Files in this namespace

| file | what it is |
|---|---|
| `V4_CLOSURE_REPORT.md` | this report |
| `V4_CLOSURE_REPORT.md.sha256` | sha256 of the **committed blob** of this report |
| `probe_v4_closure.py` / `probe_output_part1.txt` | the harness/vacuity check, the scope guard, the bound contract, 29 malformed shapes, ten end-to-end cases |
| `probe_v4_part2.py` / `probe_output_part2.txt` | the two error paths, the AST census, the hunt for other paths, the claim and label checks |
| `probe_v4_part3.py` / `probe_output_part3.txt` | byte-verbatim captures, the other `int()` sites, the v3 report's six shapes, the `str()` coercion |
| `probe_v4_part4.py` / `probe_output_part4.txt` | regression, incl. the accepted 1535-question / 10-cluster shape and the CRLF manifest |
| `probe_v4_part5.py` / `probe_output_part5.txt` | the written ingest manifest and the four published counts on disk |
| `suite_v4_run.txt` | my own run of the preparer's `test_runner_ingest_v4.py` |
| `suite_v3_run.txt`, `suite_core_run.txt`, `suite_v2_run.txt` | my own regression runs of the v3, core and v2 suites |

All probes are replayable: `python -B probe_v4_closure.py <checkout of 86a8fd7a>` (part 4 also takes
`<repo root with .git>`).

**Method for the report hash.** The value in `V4_CLOSURE_REPORT.md.sha256` is the sha256 of the **raw
Git blob** of `V4_CLOSURE_REPORT.md`, computed as
`git cat-file blob <commit>:audit_v52_runner_ingest_v4_closure_2026_09_08/V4_CLOSURE_REPORT.md | sha256sum`
— **not** of the checked-out file, which differs on Windows for exactly the reason set out in D-4.
Because the hash cannot be inside the file it describes, it is committed in a second commit that
changes nothing else, and the sidecar names the commit whose blob it pins.
