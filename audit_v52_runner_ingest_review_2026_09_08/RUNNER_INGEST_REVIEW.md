# Independent review — V52 membership runner v1 + corpus ingestion v1

**Reviewer:** independent auditor, cold start. Did not write the reviewed code and assumed no claim in it.
**Date:** 2026-09-08.

---

## VERDICT: `FAIL`

**`FAIL` here means: do not run this wiring on the real corpora until the defects in §4 are closed.**
It does not mean the work is unsound in conception, and it does not withdraw anything already closed.
Four of the seven scope items fail; the other three, and the whole identity/gate/writer layer, are
genuinely solid and I say so plainly in §3.

**Scope of this verdict, stated explicitly.** It covers **ONLY** the reviewed runner + ingestion
wiring — `drafts/v52/membership_runner_v1_2026_09_08/` and
`drafts/v52/membership_ingest_v1_2026_09_08/` at commit `22e44608`. It does **NOT** extend to:

- the **not-yet-written representation stage** (TF-IDF/LSA/SVD/rotation/Hamming, retrieval, ranking) —
  none of it exists in these two namespaces and none of it was reviewed;
- **the experiment as a whole** — its design, preregistration, estimand or statistics;
- the **closed computation core** (`membership_scaling_core.py`). F-1…F-12, NEW-1, NEW-2, NEW-3 were
  treated as independently closed and were **not** reopened. The core was read only to establish what
  the gate and the writer that the runner calls actually do;
- the **environment lock**, the **seed values** and the **manifest choice**, which are accepted Head
  Researcher decisions. This report comments only on how they are (or are not) implemented.

Nothing was sealed, no HMAC was computed, no `--mode run` or `--mode finalize` was invoked, no
representation was fitted, no bootstrap or pilot was run on real data, and **no real corpus file was
read, opened, downloaded or hashed**. No candidate file was modified.

---

## 1. Per-item dispositions

| # | Scope item | Disposition | One-line basis |
|---|---|---|---|
| 1 | Source identity before parse | **PASS** | Streamed sha256 + byte size run before `json.loads` on every corpus-opening path; a wrong-hash file that is also invalid JSON fails on IDENTITY (probe S1.1) |
| 2 | The bound cohort | **FAIL** | Missing / duplicate / misrouted ids are all refused by name, but I constructed a corrupted source the ingestion **accepts**: partially unresolvable evidence silently truncates the gold rows (D-1, probe S2.6) |
| 3 | The accepted configuration actually governs | **FAIL** | Manifests genuinely govern by hash; the **accepted seed values do not govern at all** (D-3), the run's replicate count is not checked against the frozen record (D-2), and on the locked (Windows) environment the accepted manifests cannot be loaded at all (D-4) |
| 4 | LongMemEval sentinel + cluster-bootstrap block | **PASS** | I could not reach the conversation-cluster bootstrap for LongMemEval by any route I tried; the refusal fires before seed and identity work (probes S4.2–S4.5) |
| 5 | Archive→query transform interface (N-4) | **FAIL** | The "bitwise inheritance" assertion **is** bypassable — `mu.copy()` passes — and it is a self-report unconnected to what `apply_archive_transform` actually consumed (D-6). Nothing is estimated from the query anywhere (that half is sound) |
| 6 | The gates | **PASS** | Import opens nothing (measured with an audit hook), gate closed by default and checked first, all three writers refuse to overwrite (probes S0.1–S0.6, S6.1–S6.5) |
| 7 | No raw content leaves | **FAIL** | Sub-120-character fragments escape verbatim through **seven** distinct exception paths, and `_describe()` dumps whole objects unbounded (D-5). The module's explicit claim to the contrary is falsified |

| Governance question | Answer |
|---|---|
| (a) Is the PROPOSED-vs-ACCEPTED relation coherent and unambiguous for a successor reading only the repository? | **Coherent — but NOT unambiguous. Yes, a reader could reasonably conclude the wrong thing.** See §5(a) |
| (b) Is the LongMemEval v2 precedence actually enforced in code? | **Yes — genuine hash enforcement in the ingestion.** Convention only in the runner, and a sibling script in the same `binding/` directory still loads v1. See §5(b) |

---

## 2. Identities verified — from raw Git objects only

Every hash below was produced with `git cat-file blob <commit>:<path> | sha256sum` in a **fresh clone
of my own**, never from a checked-out file. This matters: `core.autocrlf=true` on this machine and the
repository ships **no `.gitattributes`**, so a Windows checkout hashes differently (see D-4).

**Commits**

| what | sha |
|---|---|
| candidate branch `impl/v52-membership-ingest-v1-2026-09-08` | `22e44608bab838974a6e65aa1a4297c815b5506b` |
| acceptance record on `main` (ledger L-075) | `aa42a96e004fdccdae61875a957ab5cfb1b313d6` |
| this audit branch is parented on | `aa42a96e004fdccdae61875a957ab5cfb1b313d6` |

**Blobs — all six required identities MATCH**

| path (at `22e44608`) | expected | observed | |
|---|---|---|---|
| `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` | `bc2282d3…404e72` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` | ✅ |
| `…/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_locomo.json` | `66379b9d…708671` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` | ✅ |
| `…/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` | `d5b8ed69…9ed3714` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` | ✅ |
| `…/binding/PROPOSED_mapping_longmemeval.json` (SUPERSEDED) | `bdf05c12…0844886` | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` | ✅ byte-unchanged |
| `…/binding/PROPOSED_bootstrap_seeds.json` | `3f01082d…8da4fea` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` | ✅ |
| `…/CONFIGURATION_IDENTITY_2026-09-08.md` | `33c1dc98…a55739` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` | ✅ |

The accepted manifests carry the accepted cohorts: LoCoMo `n_questions=1535` over 10 conversation
clusters; LongMemEval `n_questions=470` over the single sentinel cluster
`longmemeval_single_connected_component_inherited_task3a1` (probe S3.13b). The accepted seeds file
carries exactly `(LoCoMo, question) 52001107`, `(LoCoMo, cluster) 52001207`,
`(LongMemEval, question) 52002107`, all at `replicates=10000`, with no seed for LongMemEval × cluster
(probe S3.1). `core.BOOTSTRAP_REPLICATES == 10000` and `core.PERCENTILES == (2.5, 97.5)` (probe S3.14).

---

## 3. What is genuinely sound

Stated first and without hedging, because it is the larger part of this work.

- **Identity really does precede parsing.** I built a file that is simultaneously invalid JSON and
  wrong-hashed. It failed with `source identity mismatch for LoCoMo: bound … / … bytes, read … / …`
  — not with a JSON error (S1.1). A byte-identical but **renamed** source is also refused (S1.4), and
  the identity error message carries only hashes and sizes, no file content (S1.2). I looked for a
  path that reads or parses before hashing and did not find one: `verify_source_bytes` is the first
  statement of both `ingest_locomo` and `ingest_longmemeval`, and it calls the core gate before it
  touches the path at all (S0.3).
- **The gates are real, not declarative.** I armed a `sys.addaudithook` file-open hook *before*
  importing anything: 100 file opens occurred during the import of all three modules and **zero** were
  corpus-shaped (S0.1). The gate is closed by default (S0.2), `run_on_real_corpus` refuses, and with
  the flag deliberately flipped there is still nothing behind it (S0.5) — the stub is honest.
- **Cohort id resolution is careful and refuses by name.** Against corruptions I wrote myself: a
  missing bound id, a question moved to the wrong conversation, a question id duplicated across two
  conversations, a duplicated memory-unit id, a duplicated LongMemEval id, and a manifest whose
  `n_questions` disagrees — every one refused with a named `DesignViolation` naming the offending id
  (S2.1–S2.4, S2.14–S2.16).
- **The cluster-bootstrap block for LongMemEval held against every route I tried** (§ item 4 below).
- **All three writers refuse to overwrite.** `write_ingest_manifest`, `freeze_bootstrap_seed` and
  `write_results` are the only writers and each routes through `core.safe_write_json` (S6.1–S6.3).
  The seed record cannot be overwritten (S3.4) and cannot be reused across arms (S3.5); a run with no
  frozen record is refused (S3.6).
- **The manifest binding is real enforcement, not prose.** The superseded LongMemEval v1 is refused by
  hash, and is still refused when renamed to the v2 filename (S3.8, S3.10) — path is irrelevant, hash
  governs. That is the right design.
- **Nothing is estimated from the query anywhere.** `fit_archive_transform` takes only the archive;
  `apply_archive_transform` takes `(X, mu, D)` and estimates nothing; no other function in either
  module touches a query. A query-estimated centering vector is caught by the assertion (S5.2).
- **The preparer's own suites pass.** I ran both under the approved interpreter: `test_membership_runner.py`
  → `ALL PASS`; `test_corpus_ingest.py` → `ALL PASS`. They are honest about their own scope
  ("DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS … not authorization to run on real data").
- **Neither module prints or logs anything** (S7.13) — there is no `print()` and no `logging` import.
  The happy path emits nothing: `summarise()` produced only counts, hashes and cluster identifiers on
  every fake I built (S7.12).

---

## 4. Findings

Classified as instructed: **(i) real defect**, **(ii) optional improvement**, **(iii) wording /
claim-accuracy**. Nothing below is presented as a blocker unless it is one.

### D-1 — REAL DEFECT — partially unresolvable evidence silently truncates the gold rows *(item 2)*

`corpus_ingest.py:286-290`:

```python
gold_rows = list(dict.fromkeys(
    conv["id_to_row"][e] for e in _normalise_evidence(question.get("evidence"))
    if e in conv["id_to_row"]))
if not gold_rows:
    empty_gold.append(qid)
```

The `if e in conv["id_to_row"]` guard **silently discards** every evidence id that does not resolve.
Only the *fully* empty case is recorded, and only as a count.

I built a bound question declaring two evidence ids of which one is unresolvable. The ingestion
accepted it, returned `gold_rows=[0]` — one gold row kept, one dropped — and the persisted summary
reported `questions_with_empty_gold=0`. **A partial loss of ground truth is invisible in the only
artefact that ever reaches disk** (probe S2.6).

Why this matters: the gold rows are the ground truth the entire membership estimand is computed
against. A source whose evidence partially fails to resolve would produce a complete-looking run with
a quietly wrong denominator, and nothing in the pipeline would say so. This is exactly the class of
silent-repair failure the module's own docstring says it avoids.

**Minimum fix:** count the dropped evidence ids per question, carry the total into `summarise()`, and
refuse (or at least loudly flag) when it is non-zero. Do not simply reject — the producer's committed
rule may legitimately drop some — but it must not be invisible.

### D-2 — REAL DEFECT — the run's replicate count is not checked against the frozen seed record *(item 3)*

`compute_results(..., replicates=core.BOOTSTRAP_REPLICATES)` takes `replicates` as a caller argument
and never compares it to `seed_record["replicates"]`, which `freeze_bootstrap_seed` wrote.

I froze a record saying `replicates=10000`, then called `compute_results(..., replicates=7)`. It
succeeded. **The written result carries `bootstrap_seed_record.replicates = 10000` while the interval
in `uncertainty` was actually computed from 7 replicates** (probe S3.7). The persisted artefact
misstates how it was produced, and `write_results` cannot catch it because the schema is satisfied.

**Minimum fix:** one line in `compute_results` — refuse when `replicates != seed_record["replicates"]`.

### D-3 — REAL DEFECT (honestly disclosed) — the accepted seed *values* do not govern execution *(item 3)*

Neither module references `PROPOSED_bootstrap_seeds.json`, and the strings `52001107`, `52001207`,
`52002107` appear **nowhere** in `membership_runner.py` or `corpus_ingest.py` (probe S3.2 — the token
search returned the empty list). `freeze_bootstrap_seed` accepts any `int`. I froze
`seed=999` for `(LoCoMo, question)` — where the accepted value is `52001107` — and
`read_bootstrap_seed` handed it straight back (S3.3).

What the mechanism *does* enforce is write-once and no-reuse-across-arms, and that works (S3.4, S3.5).
What it does not do is check that the seed is **the accepted one**. A transposed digit produces a
result that passes every check in the system.

**This is disclosed, not hidden.** `PROPOSED_bootstrap_seeds.json` itself says the mechanism
"does not, and cannot, establish that the value was chosen before the result", and the acceptance
record binds the values by document rather than by code. So this is a **gap**, not an overstatement.
But the accepted machine-readable file sits in the same namespace, three directories away, and
consulting it would cost one function call.

**Minimum fix:** have `freeze_bootstrap_seed` load the accepted seeds file (hash-pinned, as the
manifests already are) and refuse a `(benchmark, scheme)` seed that is not the accepted value.

### D-4 — REAL DEFECT (operational; fails safe) — the accepted manifests cannot be loaded from a default Windows checkout *(item 3)*

`load_expected_mapping` hashes the file **on disk** against a hash computed from the **raw Git blob**.
The repository ships no `.gitattributes`; `core.autocrlf=true` here (the Windows default). Measured:

| file | blob | checkout |
|---|---|---|
| `PROPOSED_mapping_locomo.json` | 59268 B, `66379b9d…` | 60823 B, `4a1f7c2d…` (1555 CRLFs) |
| `PROPOSED_mapping_longmemeval_v2_source_resolved.json` | 36598 B, `d5b8ed69…` | 37079 B, `8e8c017b…` (481 CRLFs) |

So on a default clone, `load_bound_mapping` refuses **its own accepted configuration** (probe
S3.CRLF-a/b). Against the raw blob bytes everything behaves correctly — LoCoMo and LongMemEval v2 load,
v1 is refused (S3.9, S3.13, S3.8) — which is how I established this is an environment defect and not a
logic defect.

The accepted environment lock is a Windows interpreter (`MSC v.1944 64 bit (AMD64)`), so this is not
hypothetical. **This is also the exact trap the brief warned three earlier auditors fell into**; I
flag it as a repository defect precisely so a fourth does not.

Mitigating: it **fails closed and loudly**. It cannot cause a wrong result, only a blocked run.
`GOVERNING_AND_LINEAGE.md` already warns humans to hash raw blobs — but the *code* has no such
allowance, and the runner's docstring explicitly declines an import-time core hash check for this very
reason (lines 113-115) while leaving the manifests hash-checked at runtime anyway.

**Minimum fix:** add `*.json -text` (or `* -text`) to a `.gitattributes`, **or** have
`load_expected_mapping` hash `raw.replace(b"\r\n", b"\n")`, **or** document a mandatory
`git -c core.autocrlf=false clone`. The first is the cleanest.

### D-5 — REAL DEFECT — exception messages carry source-derived text verbatim, unbounded, and un-policed *(item 7)*

This is the item I pressed hardest, and it is where the strongest claim in the package is falsified.

**`corpus_ingest.py:35-36`, byte-verbatim:**

> `Question, answer, dialogue and session text is held in memory and handed to the caller. It is never`
> `printed, logged, put in an exception message, or written to disk.`

The content policy (`assert_content_free`) is applied **only** inside `write_ingest_manifest`. It is
never applied to any exception message, in either module. Using synthetic fragments all **shorter than
the 120-character limit** — e.g. `"What did Melanie say about her sister's wedding in Lisbon last spring?"` (70 chars) —
I got content out through seven distinct paths:

| probe | path | what escapes |
|---|---|---|
| S7.2 | `assert_content_free` itself | a sub-120 dict **key** is interpolated into `_path` and echoed verbatim when a sibling value fails: `payload.per_cluster_archive_units.What did Melanie say about her sister's wedding in Lisbon last spring?: a string of 400 characters…` |
| S7.5 | `runner.validate_identifier` (whitespace branch) | the candidate id verbatim, in full |
| S7.6 | `runner.validate_identifier` → `_describe()` | **a whole record dict**, unbounded — question + answer + session text in one 482-char message |
| S7.7 | `runner.freeze_bootstrap_seed` → `_describe()` | same unbounded dump for a non-int seed |
| S7.8 | `runner.verify_source_identity` | up to 3 unbound ids verbatim (`extra_q[:3]`) |
| S7.9 | `runner.validate_identifier_columns` | up to 5 duplicate ids verbatim (`dupes[:5]`) |
| S7.10 | `corpus_ingest.ingest_locomo` | a source-derived `question_id` verbatim in the duplicate error |

`_describe()` (`membership_runner.py:127-128`) is the worst of these: `f"{type(value).__name__}({value!r})"`
with no length cap and no policy check, reached from the two validators whose entire purpose is to fire
when something that is *not* an identifier turns up in an identifier column. **The error path that
exists to catch a malformed id column is also the path that prints the malformed content.**

Severity, stated fairly: in the *ingestion*, the only source-derived value that reaches an exception is
`question_id` — I confirmed the LongMemEval session/turn shape errors name only positions and never the
turn body (S7.11), and the happy path is clean (S7.12). So the realistic exposure is "identifiers, plus
whatever a corrupt source put in the id field, plus whatever a caller passes into the runner's
validators". That is narrower than "the corpus leaks". It is still a real leak, it is unbounded, and
the quoted claim is false as written.

**Minimum fix:** route every interpolated value through a truncating, policy-checked formatter (report
type + length + a hash, not the value); cap `_describe()`.

### D-6 — REAL DEFECT — the N-4 inheritance assertion is bypassable and is a self-report *(item 5)*

**`membership_runner.py:330`, byte-verbatim:**

> `N-4: the query must be transformed by the IDENTICAL objects, bitwise.`

Two independent bypasses:

1. `np.array_equal` is **value** equality, not object identity. `assert_query_transform_is_inherited(mu, D, mu.copy(), D.copy())` **passes** (probe S5.3). "IDENTICAL objects" is not what is checked; bitwise value equality is.
2. More seriously, **the assertion is not connected to anything.** `apply_archive_transform` records nothing about what it consumed; the caller hands `mu_used` / `D_used` to the assertion by hand. A caller that transformed the query with a query-derived `mu` and then passed the archive `mu` to the assertion would pass cleanly (S5.5). Nothing in either module calls the assertion.

So N-4 is discharged by convention, not by construction. Today this is harmless — the consumer (the
representation stage) does not exist, and `fit`/`apply` themselves are correct. **It must not stay this
way once the representation stage lands.**

**Minimum fix:** have `apply_archive_transform` return, or stamp, the `(id(mu), id(D))` or a digest of
what it actually used, and have the assertion check *that* rather than a caller-supplied echo.

### D-7 — REAL DEFECT (minor) — ragged LongMemEval haystack arrays truncate silently *(item 2)*

`_longmemeval_units` zips `haystack_session_ids`, `haystack_dates` and `haystack_sessions` with no
length check. `zip()` stops at the shortest. I passed an item with `haystack_dates=[]`: it resolved
with **zero** archive units and empty gold, and only the empty-gold counter recorded anything (S2.12).
**Fix:** assert the three lengths are equal.

### D-8 — REAL DEFECT (minor) — a raw `KeyError` instead of a named refusal *(item 2)*

`ingest_longmemeval:361` does `str(item["question_id"])`. An item without that key raises
`KeyError: 'question_id'` (S2.11). The codebase's own standard is a named `DesignViolation` — this is
the same class of issue the core closed as F-3 and NEW-3.

### Claim-accuracy problems (category iii — wording, not behaviour)

**C-1. `corpus_ingest.py:17-18`, byte-verbatim:**

> `  3. resolve EVERY bound question id INDIVIDUALLY against the source, refusing missing, extra and`
> `     duplicated ids rather than repairing them;`

Extra ids are **not** refused — they are returned as `extra_ids_in_source` and nothing is raised
(probe S2.5). And this is **correct behaviour**: the bound cohort is a strict subset of the source
(1535 of a larger LoCoMo QA set, by the `category != 5` rule), so refusing extras would break every
legitimate run. The *code* is right; the *sentence* is wrong. It also sits uncomfortably beside D-1,
which is a repair.

**C-2. `corpus_ingest.py:35-36`** — quoted in full under D-5. False as written.

**C-3. `corpus_ingest.py:37-38`, byte-verbatim:**

> ``write_ingest_manifest` is the only writer and it refuses any payload that could carry content: every value is checked against a`
> `conservative policy before a byte is written`

"any payload that could carry content" overstates it. The limit is **per string, not aggregate**: I
passed a dict of 200 keys of ~62 characters each — roughly 12 kB of content-shaped text — and
`assert_content_free` accepted all of it, and `write_ingest_manifest` wrote it to disk (probes S7.3,
S7.4). To be fair to the preparer: `summarise()` never produces such keys, so reaching this needs a
caller that hand-builds the manifest. The policy is a useful backstop; it is not the guarantee the
sentence claims.

**C-4. `corpus_ingest.py:218`, byte-verbatim:**

> `Evidence ids only, in the producer's committed normalisation. Never returns free text.`

False. `_normalise_evidence("Melanie mentioned it at the wedding")` returns
`['Melanie mentioned it at the wedding']` — the fallback `return found if found else [value]`
(line 221-222) returns the raw string when no `D\d+:\d+` pattern matches (probe S2.9). The returned
text is then only used as a dict lookup and discarded, so this is not itself a leak — but the
docstring is wrong, and it is wrong in a way that would let a future caller trust it.

**C-5. `membership_runner.py:330`** — quoted under D-6.

### Optional improvements (category ii — not blockers)

- **O-1.** The source file is opened **twice** per ingest — once streamed for the hash, once via
  `read_text` for the parse (measured: 2 opens, probe S1.5). A TOCTOU window exists between them. Low
  risk on a local read-only corpus; worth closing by parsing the bytes already read. Note also that
  `read_text` pulls the whole 277 MB LongMemEval file into memory as a `str` after having just
  streamed it — the streaming in `verify_source_bytes` buys nothing if the next line does that.
- **O-2.** `BOUND_MANIFESTS[...]["path"]` is never used by any code path — only the hash governs. It is
  documentary. Harmless, but a reader may believe the path is enforced.
- **O-3.** The manifest's own `source_sha256` is never compared against the identity returned by
  `verify_source_bytes` (probe S3.12). Both are hash-pinned so this is not exploitable today; the
  cross-check would be cheap defence in depth.
- **O-4.** `has_answer` is compared with `is True` (`corpus_ingest.py:346`), so a JSON `1` or `"true"`
  is silently not gold (probe S2.13). Probably deliberate strictness; worth stating in the docstring
  rather than leaving to be discovered.
- **O-5.** `assert_query_transform_is_inherited` fails against itself if the archive mean contains a
  `NaN`, because `np.array_equal(NaN, NaN)` is `False` (probe S5.6).
- **O-6.** In `ingest_locomo`, the conversation index embedded in a LoCoMo qid (`locomo_<i>_qa<j>`) is
  never checked against the conversation it was found in — only `j` is. This is **not** exploitable,
  because the separate `cluster_id != expected_cluster` check catches every corruption I could
  construct; noted only so a successor does not assume `i` is validated.

---

## 5. The two governance questions

### (a) The PROPOSED-vs-ACCEPTED relation — coherent, but not unambiguous

**The reasoning is sound and I want to credit it.** `BOUND_CONFIGURATION_ACCEPTANCE_2026-09-08.md` §1
states the relation explicitly and defensibly: the files are left byte-unchanged so their hashes keep
resolving in L-072/L-073, and what binds them is the external record plus L-074/L-075. That is the
right call — editing an accepted file to say "ACCEPTED" would break every hash that references it.

**But a successor reading only the repository could reasonably conclude the wrong thing, and I say so
plainly. Four concrete reasons, each verified:**

1. **Every file in `binding/` carries the same status string.** The accepted LoCoMo sidecar, the
   accepted LongMemEval **v2** sidecar, the **superseded** v1 sidecar and the accepted seeds file all
   say `"binding_status": "PROPOSED - NOT BOUND; requires Head Researcher approval"`. Listing the
   directory gives a successor **no way to tell accepted from superseded from never-accepted**.
2. **The v1 sidecar contains no mention of supersession at all.** The only in-directory marker is the
   `supersedes` block inside the **v2** sidecar — you must open the file you were not looking for to
   discover that the one you *were* looking at is dead.
3. **A shipped script actively asserts the misleading label.**
   `binding/validate_proposed_manifests.py:70-71` checks
   `sidecar["binding_status"].startswith("PROPOSED")` under the printed label, byte-verbatim:
   > `"the provenance sidecar marks it PROPOSED, not bound"`

   So a successor who runs the namespace's own validator is *told, in a passing check*, that the
   accepted manifests are not bound — and the check would **fail** if anyone ever corrected the status.
4. **Nothing in the runner namespace points at the acceptance record.** I grepped: no file under
   `drafts/v52/membership_runner_v1_2026_09_08/` mentions `BOUND_CONFIGURATION_ACCEPTANCE`. The
   accepted manifests and seeds physically live in that namespace; the document that accepts them lives
   in a *different* one (`membership_ingest_v1_2026_09_08/`). A successor working on the runner need
   never open it.

**This is a category (ii)/(iii) issue, not a blocker.** The cheapest fix that changes nothing
hash-bound: add one new `binding/README_BINDING_STATUS.md` naming, per file, which of accepted /
superseded / never-accepted applies and pointing at the acceptance record and L-074/L-075 — and update
`validate_proposed_manifests.py` so its label stops asserting "not bound".

### (b) Is the LongMemEval v2 precedence enforced in code? — Yes in the ingestion; convention in the runner; and one script still loads v1

**Enforcement — real.** `corpus_ingest.BOUND_MANIFESTS[runner.LONGMEMEVAL]["sha256"]` is pinned to
`d5b8ed69…` (the v2 hash), and `load_bound_mapping` routes through
`runner.load_expected_mapping(path, that_pinned_hash)`. I tested what actually happens if someone
passes the v1 file:

- passing v1's path → `DesignViolation: expected-mapping manifest hash mismatch … bound d5b8ed69…, read bdf05c12…` (probe S3.8) — **refused**;
- passing v1 **renamed to the v2 filename** → still refused (S3.10). Hash governs, not path. Good;
- passing v2 → loads, 470 questions, 1 sentinel cluster (S3.9, S3.13b).

Since the ingestion is the only thing that reaches a corpus, the acceptance record's "must not be
loaded" is genuinely enforced where it matters. **This is enforcement, not convention.**

**Two gaps around it:**

1. **The runner alone does not enforce it.** `load_expected_mapping(path, expected_sha256)` takes the
   expected hash as a *caller argument*; a caller supplying v1's path **and** v1's hash loads v1
   without complaint (probe S3.11). The precedence lives entirely in `corpus_ingest.BOUND_MANIFESTS`.
2. **A sibling script in the same `binding/` directory still loads v1 — and only v1.**
   `validate_proposed_manifests.py` iterates over `("PROPOSED_mapping_locomo.json", "PROPOSED_mapping_longmemeval.json")`
   (line 41-42) and again at line 79 does
   `R.load_expected_mapping(lme, hashlib.sha256(lme.read_bytes()).hexdigest())` on the **v1** file —
   self-hashing, so the hash check there is vacuous. The string `v2_source_resolved` appears **zero**
   times in that script. The acceptance record says v1 "must not be loaded by the ingestion or the
   runner"; this script is strictly neither, so it is not a violation of the letter — but the only
   validator in the binding directory validates the **superseded** LongMemEval manifest, and a
   successor running it would be validating the wrong file. Category (ii): repoint it at v2.

---

## 6. OUT OF SCOPE observation

**Marked clearly so it is not confused with a scope finding.** `ops/CURRENT_STATE.json` at
`aa42a96e` (line ~1535) records that L-074 and `CONFIGURATION_IDENTITY_2026-09-08.md` state
`threadpoolctl.threadpool_info()` returns an empty list and that this **"is WRONG as written"**. The
configuration identity document still carries the wrong sentence at the reviewed commit (it is
hash-bound, so it cannot be edited without breaking L-074). The correction exists only in the ledger.
This is a documentation-consistency matter in an accepted Head Researcher document; I did not
re-litigate it, did not verify the threadpool claim myself, and it is **outside** the seven scope items.

---

## 7. What I actually ran

Environment: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\locomo_reproduction_tmp_20260907\venv\Scripts\python.exe`
(Python 3.13.15, numpy 2.3.5), with `PYTHONHASHSEED=0` and
`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`. Used as an interpreter
only; nothing was installed, changed, or written inside it. Note: **the venv has no `pytest`**, so the
two test modules were run as plain scripts, which is how they are written.

1. Fresh `git clone` into my own scratch directory (**not** the preparer's work tree, and not any
   preparer scratchpad), plus a detached worktree at `22e44608` for probing.
2. `git cat-file blob <commit>:<path> | sha256sum` for all six required identities — §2.
3. `python test_membership_runner.py` → `ALL PASS`.
4. `python test_corpus_ingest.py` → `ALL PASS`.
5. `python probe_runner_ingest.py <candidate root>` — my own 77 probes, output in `probe_output.txt`.
   Final tally: **44 PASS, 21 FINDING, 10 OBSERVE, 2 INFO, 0 unexplained FAIL.**

All corruptions in the probe file were written by me; I did not replay the preparer's fixtures. Every
"source" the probes open is a small fake written into a fresh temp directory by the probe script
itself, with the shape of the real data and none of its content. The bound source/manifest hash
entries are overridden per probe, visibly and reversibly, because otherwise nothing but the two real
files could ever pass `verify_source_bytes` — and those were not touched.

**What I could not verify, stated rather than implied:**

- I have **not** verified that the bound cohorts correspond to anything in the real corpora. That would
  require reading `locomo10.json` and `longmemeval_s_cleaned.json`, which is prohibited here. Every
  cohort statement in this report is about the manifests as committed artefacts.
- I have **not** verified the two bound source hashes (`79fa87e9…`, `d6f21ea9…`) or the byte sizes
  against the real files, for the same reason. I verified only that the code pins them.
- I did **not** run `validate_proposed_manifests.py` (it loads manifests from the checkout, which D-4
  shows would fail here, and it is not part of the seven items) — my statements about it are from
  reading its source at the candidate commit.
- I did **not** re-audit the computation core, the design, the preregistration or the statistics.

---

## 8. Files in this namespace

| file | what it is |
|---|---|
| `RUNNER_INGEST_REVIEW.md` | this report |
| `RUNNER_INGEST_REVIEW.md.sha256` | sha256 of the **committed blob** of this report |
| `probe_runner_ingest.py` | my probe suite — replayable: `python probe_runner_ingest.py <checkout of 22e44608>` |
| `probe_output.txt` | its raw output, as produced |

**Method for the report hash.** The value in `RUNNER_INGEST_REVIEW.md.sha256` is the sha256 of the
**raw Git blob** of `RUNNER_INGEST_REVIEW.md`, computed as
`git cat-file blob <commit>:audit_v52_runner_ingest_review_2026_09_08/RUNNER_INGEST_REVIEW.md | sha256sum`
— **not** of the checked-out file, which differs on Windows for exactly the reason set out in D-4.
Because the hash cannot be inside the file it describes, it is committed in a second commit that
changes nothing else, and the sidecar names the commit whose blob it pins.
