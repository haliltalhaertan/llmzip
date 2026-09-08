# Delta closure check — runner + ingestion v2

**Auditor:** independent, cold start. Did not write the reviewed code and assumed no claim in it is true.
**Date:** 2026-09-08.
**Subject:** branch `impl/v52-runner-ingest-v2-2026-09-08`, commit `9b569687b394b0507fdeefc5abe456a9958e0788`,
namespace `drafts/v52/membership_runner_ingest_v2_2026_09_08/`.
**Specification:** the independent review at `audit/v52-runner-ingest-review-2026-09-08` @
`8c8ba7aefe2622efb4fbf65230f04dbfbec25449`, report blob sha256
`456645a61c7e44148ee454287e7db0e66adfa128539b17679ce1c94897764676` (verified — §5), verdict `FAIL`.

---

## VERDICT: `CLOSURE PASS WITH FINDINGS`

**What this verdict covers, stated explicitly.** It covers **ONLY** findings **D-1 … D-8** and the two
directly connected source-trust / governance items, and the wiring they touch, at commit `9b56968`.
It does **NOT** extend to:

- the **not-yet-written representation stage** (M-1/M-2/M-3) — I confirmed only that it was **not**
  added here (probe A5);
- **the experiment as a whole** — its design, preregistration, estimand, statistics, accepted cohort,
  accepted manifests, accepted seed **values** or environment lock. Those are Head Researcher
  decisions and I did not re-litigate them;
- the **closed computation core** — F-1…F-12 and NEW-1/2/3 were treated as independently closed and
  were **not** reopened. The core blob is byte-unchanged (§5).

**Why "WITH FINDINGS" and not a plain PASS.** Seven of the ten items are cleanly closed and I say so
without hedging. Two are closed in substance but carry a **byte-verbatim false claim** in the shipped
code, which is the exact category of problem the previous review's C-1…C-5 raised and which this
package explicitly set out to stop making:

- **D-5 is closed for corpus content and NOT closed for the module's own claim.** The seven v1 leak
  paths are genuinely shut. But **nine** further paths in the two v2 modules still interpolate a raw
  value into an exception message, and I got sub-120-character canaries out through every one of them
  (probes F12–F20). One of those nine reads its value **out of a file on disk** (the frozen seed
  record), and one is an **ordering defect**: `compute_results` echoes `mapping['benchmark']` verbatim
  **before** it checks the accepted-manifest stamp.
- **D-1's waiver is required and the loss is visible, but the waiver is NOT recorded in the persisted
  artefact**, contrary to what the module says in the very message that offers it (probe E6/E7).

Neither of those makes a wrong result possible, and neither reopens a v1 defect. Both are real defects
against this package's own stated behaviour, so the honest verdict is PASS **with findings**, not PASS.

**Whether this authorises anything.** No. Nothing was sealed, no HMAC was computed, no `--mode run` or
`--mode finalize` was invoked, no representation was fitted, no bootstrap or pilot was run on real
data, and **no real corpus file was read, opened, downloaded or hashed**. No candidate file was
modified. Task 4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.

---

## 1. Per-finding table

| # | Finding | Disposition | My evidence | Genuine negative control? |
|---|---|---|---|---|
| **D-1** | partially unresolvable LoCoMo evidence silently truncated the gold rows | **CLOSED (with a claim-accuracy defect, N-1)** | E1–E12. Declared/resolved/unresolved counted separately and published unconditionally; a partial loss **stops** with a named `DesignViolation`; the waiver needs a non-empty citation. Gold rows and cohort **byte-identical** to v1 on a clean source (E11). But the waiver + citation reach **no** persisted artefact (E6) and the closed schema **forbids** adding them (E7) | **Yes.** Preparer's `test_runner_ingest_v2.py:192-201` calls `I1.ingest_locomo` / `I1.summarise` and inspects the returns. I reproduced it myself against v1 (probe E12) |
| **D-2** | the replicate count was not checked against the frozen record | **CLOSED** | D1–D7. `freeze_bootstrap_seed` refuses 7; `read_bootstrap_seed` catches a hand-edited record claiming 7; `compute_results` refuses `replicates=7` against a 10000 record; `compute_results` takes only a record **path**, so no pre-made record can be handed in | **Yes.** Suite lines 293-301 run `R1.compute_results(..., replicates=7)` and read `bootstrap_seed_record["replicates"] == 10000`. My own D7 reproduced it |
| **D-3** | the accepted seed values governed nothing | **CLOSED** | C1–C10. Seed 999 refused; **transposed** `52001170` refused; `52001107` accepted; a hand-edited record and a record forged by hand are both refused **on read**; `(LongMemEval, cluster)` refused because it is absent from the accepted configuration. I found no route into `compute_results` that bypasses `read_bootstrap_seed` | **Yes.** Suite lines 240-244 call `R1.freeze_bootstrap_seed(..., 999, ...)` and `R1.read_bootstrap_seed`. My own C10 reproduced it |
| **D-4** | manifests could not be loaded from a default Windows checkout | **CLOSED** | B1–B14. Manifests resolve from `git cat-file blob`; the **real CRLF checkout in my own worktree** (60823 B, `4a1f7c2d…`, 1555 CRLFs) is **REFUSED** with the CRLF diagnosis, as `path=` and as `raw=`; a genuinely substituted manifest is refused and diagnosed as *content*; the byte-preserving materialisation round-trips to `66379b9d…` with 0 CRLFs; the only two line-ending manipulations in the package are inside `_diagnose`, which never returns a fallback (B10/B11); **no `.gitattributes`** at the commit; the clone's local config sets no EOL override and `core.autocrlf` is still the system `true` | **Yes.** Suite lines 354-359 call `I1.load_bound_mapping` on a CRLF file and expect "hash mismatch". Independently confirmed against the live checkout (B4/B5) |
| **D-5** | exception messages carried source-derived text verbatim, unbounded, un-policed | **NOT CLOSED** (closed for corpus content; **9 residual paths**, one of them file-derived) | F1–F25 + P1–P8. All seven v1 paths are shut and `_describe` is gone. **But** canaries under 120 characters escape verbatim through `compute_results` (mapping benchmark **before** the stamp check; unknown `benchmark`; unknown `scheme`), `freeze_bootstrap_seed`/`accepted_bootstrap_for`, `load_accepted_mapping`, `resolve_sources.resolve_accepted_manifest`, `verify_source_bytes` (benchmark and **path**), and **`read_bootstrap_seed`, which interpolates values read out of a JSON file on disk**. 70 raw interpolation sites survive (P8) | **Yes.** Suite lines 387-445 drive `R1` through six leak paths and assert `leaked(...)` is truthy. I reproduced three myself (F23, F24, P1) |
| **D-6** | the N-4 assertion was bypassable and a self-report | **CLOSED** (one residual, N-3) | G0–G8. `apply_archive_transform` returns `(transformed, stamp)`; the assertion takes only the stamp — `mu_used`/`D_used` are **gone** from the signature; a **query-derived centering** is caught, and so is a **one-ULP** perturbation of `D`; a non-stamp argument is refused and not echoed. Residual: `transform_stamp` is public, so a caller that deliberately re-derives it can still report an untrue stamp (G6) | **Yes.** Suite lines 475-481 call `R1.assert_query_transform_is_inherited(mu, D, mu.copy(), D.copy())` and `(mu, D, mu, D)` and assert both return `None`. My own G7 reproduced both |
| **D-7** | ragged LongMemEval haystacks truncated silently | **CLOSED** | H1–H6. All three arrays length-checked **before** `zip`, with the three lengths in the message; a short `haystack_dates`, `haystack_session_ids` or `haystack_sessions` is refused; an entirely empty haystack is refused rather than accepted as zero units | **Yes.** Suite lines 530-537 call `I1.ingest_longmemeval` on a ragged item and assert `len(units) == 0`. My own H6 reproduced it |
| **D-8** | a raw `KeyError` instead of a named refusal | **CLOSED** (one residual, N-4) | I1–I4. All four required LongMemEval fields give a named `DesignViolation` carrying only a field name and a count; a non-mapping item is named; no canary in any of them. Residual: `compute_results` still does an unguarded `mapping["benchmark"]`, so an empty mapping raises `KeyError: 'benchmark'` (P3) | **Yes.** Suite lines 546-547 call `I1.ingest_longmemeval` and expect `KeyError`. My own I4 reproduced it |
| **SOURCE TRUST** | the expected manifest hash must not be an arbitrary caller input; ONE authoritative source directory; PROPOSED-vs-accepted and LongMemEval v2 precedence unambiguous | **CLOSED** (one residual, N-2) | J1–J17. `load_accepted_mapping(benchmark, *, raw, path)` — the `expected_sha256` argument is **gone**; exactly-one-of is enforced; the **superseded** v1 LongMemEval manifest is refused **as superseded, with the reason**, under either benchmark; every hash and seed value lives only in `authoritative/`; the acceptance record, the configuration identity, the closed core and the accepted seeds file all hash to exactly what `accepted_configuration.py` claims; `PROPOSED_VS_ACCEPTED` states in code how to read "PROPOSED" in the older files. Residual: the accepted-manifest "stamp" is a plain dict key holding a **public constant**, so a hand-built mapping still passes (J8/J9) | **Yes.** Suite lines 307-309 call `R1.load_expected_mapping(f, sha(f))` and show any file loads against any caller hash. My own J7 loaded the **superseded** manifest through v1 |
| **GOVERNANCE (b)** | LongMemEval v2 precedence enforced in code | **CLOSED for this package** | J5/J6. Enforcement no longer depends on a caller hash at all. The v1-namespace `binding/validate_proposed_manifests.py` still points at the superseded file — that is a **v1-namespace** script the package deliberately left byte-unchanged; I did not run it | **Yes** (same control as SOURCE TRUST) |

**Regression check on what the previous review PASSED** (K1–K5, brief, as instructed): identity still
precedes parsing (a file that is both wrong-hashed and invalid JSON fails on IDENTITY); the gate is
still closed by default and checked first; importing all three v2 modules opens **122** files and
**zero** are corpus-shaped; all three writers still refuse to overwrite; the LongMemEval
conversation-cluster bootstrap is refused by all four routes I could reach; a misrouted question is
still refused by name. **No regression found.**

---

## 2. The findings, in full

Classified as instructed: **(i) real defect**, **(ii) optional improvement**, **(iii) wording /
claim-accuracy**. Nothing is presented as a blocker unless it is one.

### N-1 — REAL DEFECT (iii-plus-i) — the D-1 waiver is not recorded in the persisted artefact, and the code says it is

`corpus_ingest_v2.py:382-383`, byte-verbatim:

> `              "allow_partial_evidence=True WITH the citation that permits it; it is then recorded "`
> `              "in the manifest rather than waived silently (D-1)")`

and `FIX_PACKAGE_V2_2026-09-08.md:20`, byte-verbatim: `a `partial_evidence_citation`, which travels into the result`.

Measured (probe E5/E6/E7). With a cited waiver the ingestion succeeds and
`ingest_locomo` returns `partial_evidence_waiver = {'allowed': True, 'citation': '…'}` **in memory**.
`summarise()` does not carry it, `INGEST_MANIFEST_KEYS` does not contain it, and
`write_ingest_manifest` **actively refuses** a summary that has it added:

```
ingest manifest schema mismatch: missing [], unexpected ['partial_evidence_waiver']
```

So the waiver is recorded in the **caller's** value, not "in the manifest". What *does* reach disk is
the loss itself — `evidence_ids_unresolved=1`, `questions_with_partial_evidence_loss=1` — which is the
substance of D-1 and is why I call D-1 closed. But a successor reading the only artefact that reaches
disk can see **that** ground truth was lost and cannot see **under what authority** it was waived, and
the module tells them the opposite. **Minimum fix:** add the waiver and its citation to
`INGEST_MANIFEST_KEYS` and to `summarise()`, or correct the sentence.

### N-2 — REAL DEFECT (i, residual) — nine paths in the two v2 modules still interpolate raw values into exception text

**`membership_runner_v2.py:68`, byte-verbatim:**

> `On content: no value is interpolated into any message in this module. That is a property of the code`

**`corpus_ingest_v2.py:46`, byte-verbatim:**

> `  * NO value is interpolated into any message raised or printed by this module. Every message is`

Both are false as written. Using synthetic fragments **all shorter than 120 characters** — e.g.
`"What did Melanie say about her sister's wedding in Lisbon last spring?"` (70 chars) — I got content
out through nine distinct paths that the preparer's suite does not test:

| probe | path | what escapes |
|---|---|---|
| F12 | `compute_results`, `membership_runner_v2.py:473` | `mapping['benchmark']` verbatim — **and this fires BEFORE the `_accepted_manifest_sha256` stamp check on line 474**, so an arbitrary caller dict reaches it |
| F13 | `compute_results:462` | an unknown `benchmark` argument, verbatim |
| F14 | `compute_results:464` | an unknown `scheme` argument, verbatim |
| F15 | `accepted_bootstrap_for:309` (reached from `freeze_bootstrap_seed`) | an unknown `benchmark`, verbatim |
| F16 | `load_accepted_mapping` → `resolve_sources.verify_manifest_bytes:119` | an unknown `benchmark`, verbatim |
| F17 | `resolve_sources.resolve_accepted_manifest:75` | an unknown `benchmark`, verbatim |
| F18 | `corpus_ingest_v2.verify_source_bytes:136` | an unknown `benchmark`, verbatim |
| F19 | `corpus_ingest_v2.verify_source_bytes:140` | the missing source **path**, verbatim and uncapped |
| F20 | `read_bootstrap_seed:364-365` | **`record.get('benchmark')` and `record.get('scheme')` read out of a JSON file on disk**, verbatim and uncapped |

Byte-verbatim from F20's message:

> `the frozen seed record is for (What did Melanie say about her sister's wedding in Lisbon last spring?, She said the ceremony was on a rooftop and it rained.), not (LoCoMo, question); …`

**Severity, stated fairly.** Eight of the nine take a **caller-supplied** argument, and F20 takes a
value from a file the pipeline itself writes. I could **not** get any *parsed corpus* value —
question, answer, dialogue or session text — into a message anywhere in either module: F21 and F22
drove the D-1 partial-loss refusal and the missing-cohort refusal on a source in which **every**
question, answer and turn was a canary, and neither leaked. Nothing reaches a written file: the two
modules have exactly three writers, all through `core.safe_write_json`, and the fully-canaried happy
path wrote a 732-byte manifest with no canary in it (F10/F11).

But this is the same standard the previous review applied to v1 — it counted `validate_identifier`'s
caller-supplied id and `verify_source_identity`'s caller-supplied extras as leaks — so it must be
applied here too. **The claim is false, and the F12 ordering is a genuine defect** (the stamp check
should precede any use of the mapping's contents). **Minimum fix:** route these nine through
`safe_report`, move the stamp check above line 471, and soften the two docstring sentences to what the
code does.

### N-3 — OPTIONAL IMPROVEMENT (ii, residual on D-6) — the transform stamp is forgeable by a determined caller

`transform_stamp(mu, D)` is a public module-level function, so a caller can transform the query with a
query-derived `mu`, then call `transform_stamp(mu_archive, D_archive)` and hand *that* to the
assertion. It passes (probe G6). This is **not** a reopening of D-6: the review's prescribed minimum
fix was exactly what was implemented, and the realistic failure — an honest caller whose code
transforms with the wrong parameters — is now caught (G2, G3). It is noted so a successor building the
representation stage does not treat the stamp as unforgeable.

### N-4 — OPTIONAL IMPROVEMENT (ii, residual on D-8) — one unguarded `KeyError` survives, in the runner

`membership_runner_v2.py:471` does `mapping["benchmark"]` with no guard. A mapping without that key
raises `KeyError: 'benchmark'` (probe P3) — the same class D-8 closed in the ingestion. Minor: a
mapping is meant to come from `load_accepted_mapping`, which guarantees the key.

### N-5 — OPTIONAL IMPROVEMENT (ii, residual on source trust) — the accepted-manifest "stamp" is a public constant

`compute_results:474` and `corpus_ingest_v2._check_accepted_mapping` both test
`mapping.get("_accepted_manifest_sha256") == accepted.ACCEPTED_MANIFESTS[b]["blob_sha256"]`. The
right-hand side is a public constant in the same importable module, so a caller can hand-build a
mapping with any cohort it likes, set that one key, and both checks pass (probes J8, J9). An
**unstamped** mapping is correctly refused (J10). This is qualitatively better than v1 — no legitimate
API call can now load a non-accepted manifest, whereas v1's `load_expected_mapping(path, hash)` would
load anything the caller vouched for (J7) — so the source-trust item is closed. Defence in depth would
be to make the stamp a keyed digest over the manifest bytes plus something not exported.

### NEW — OUT OF THE CLOSURE SCOPE — LongMemEval's evidence accounting is a tautology

Marked clearly as **NEW and outside D-1…D-8**, because D-1 is scoped to LoCoMo evidence.
`ingest_longmemeval` builds `evidence_tally` as `{"declared": sum(len(gold_rows)), "resolved":
sum(len(gold_rows)), "unresolved": 0}` (`corpus_ingest_v2.py:499-501`). `declared` is **defined** as
`resolved`, so `evidence_ids_unresolved` is structurally always 0 for LongMemEval and
`questions_with_partial_evidence_loss` is a hard-coded `[]`. Combined with the pre-existing
`has_answer is True` strictness (the previous review's O-4), a LongMemEval question with two
gold-bearing turns of which one carries `has_answer: 1` (JSON integer) loses one gold row and the
persisted manifest reports `declared=1, resolved=1, unresolved=0, partial=0, empty_gold=0` — the loss
is **completely invisible** (probe H7). This is inherited v1 behaviour, not something v2 introduced,
and it does **not** block closure of D-1. It is reported because the manifest field names now promise
an accounting that, for this benchmark, does not exist.

### Things I checked and found genuinely sound — stated plainly

- **The v1 modules, the closed core and both accepted manifests are byte-unchanged** at `9b56968`
  (§5). The commit is **purely additive**: `git diff --stat 22e44608 9b56968` is 12 files, **2535
  insertions, 0 deletions**.
- **No representation stage was added.** No `TfidfVectorizer`, `TruncatedSVD`, `sklearn`, retrieval,
  ranking or Hamming code exists in the package — only prose saying so (A5, and a repo-wide grep).
- **D-4's byte discipline is real, not asserted.** I tested it against the actual CRLF checkout in my
  own worktree, not a synthetic one, and it refuses; the two `\r\n` replacements in the package are
  confined to `_diagnose` and produce a *message*, never an accept.
- **`_describe` is gone.** Every one of the seven paths the previous review exploited now emits a
  digest and a shape.
- **The preparer's own suite is honest and reproduces exactly.** I ran `test_runner_ingest_v2.py`
  under the approved interpreter: **82 `ok` lines, 0 failures**, of which **19** are negative controls.
  Diffed against the committed `evidence/v2_delta_tests.txt`: **identical but for one temp-directory
  name**. The three earlier suites still pass (`ALL PASS` each).
- **The negative controls genuinely execute v1.** They `import membership_runner as R1` /
  `import corpus_ingest as I1` from the unchanged v1 namespaces and inspect real return values — they
  are not asserted. I independently reproduced **nine** of them myself against v1 (C10, D7, E12, F23,
  F24, P1, G7, H6, I4, J7) and every one behaved as the suite claims.
- **The claim corrections are real.** "IDENTICAL objects, bitwise", "It is never printed, logged, put
  in an exception message, or written to disk", and the "refusing extra ids" sentence are all gone,
  and the 120-character limit is now labelled in the code as `a blunt check, NOT a guarantee`.

---

## 3. Attempts to break it that did NOT succeed — stated so the absence is informative

- **A partial evidence loss that slips through unseen (D-1).** I tried four shapes. A *total* loss
  (all declared ids unresolvable) is not classed as "partial" — but it lands in `empty_gold` **and**
  in `evidence_ids_unresolved=2`, so it is visible (E8). Free-text evidence with no `D<n>:<n>` match
  behaves the same way (E9). Declaring the same id twice in a string inflates `declared` from 1 to 2
  with `resolved` also 2 — a cosmetic over-count, no loss, no invisibility (E10). I did not find a
  LoCoMo shape that loses gold rows without saying so in the persisted manifest.
- **A non-accepted seed into a run by any route (D-3).** `freeze_bootstrap_seed` refuses it;
  hand-editing the frozen record is caught on read; a record written entirely by hand is caught on
  read; `compute_results` takes only a path and always reads through `read_bootstrap_seed`. I found
  no fourth door.
- **A CRLF manifest through a softer door (D-4).** `path=`, `raw=` and `verify_manifest_bytes`
  directly all refuse.
- **A wrong centering or a wrong D past the N-4 assertion (D-6)** — a query-derived `mu` and a
  one-ULP `D` are both caught.
- **Corpus content into a message (D-5)** — see N-2: caller-supplied and file-supplied values escape,
  parsed corpus content does not.

---

## 4. What I actually ran

Environment: `C:\Users\MDP\Documents\ChatGPT\LLM_TOKEN_ZIP\work\locomo_reproduction_tmp_20260907\venv\Scripts\python.exe`
— Python `3.13.15 [MSC v.1944 64 bit (AMD64)]`, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0,
pandas 2.2.3 — with `PYTHONHASHSEED=0` and
`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=NUMEXPR_NUM_THREADS=1`. Used as an interpreter
only; nothing installed, changed or written inside it. The venv has no `pytest`, so the suites were
run as plain scripts, which is how they are written.

1. `git clone https://github.com/haliltalhaertan/llmzip.git` into my own scratch directory (**not**
   the preparer's work tree and **not** any `scratchpad/llmzip_*` directory), plus a detached
   worktree at `9b56968`. That worktree is CRLF-translated, which is what made the D-4 test real.
2. `git cat-file blob <commit>:<path> | sha256sum` for every identity in §5. Never from a checkout.
3. `python test_runner_ingest_v2.py` → `ALL PASS`, 82 `ok`, 0 failures, 19 negative controls.
   Raw output: `preparer_suite_v2_run.txt`. Diff against the committed evidence: one temp-dir name.
4. `python test_membership_scaling_core.py`, `test_membership_runner.py`, `test_corpus_ingest.py`
   → `ALL PASS` each.
5. `python probe_v2_closure.py <checkout> <repo>` — **my own 123 probes**, output in
   `probe_output.txt`. Tally: **95 PASS, 12 FINDING, 9 OBSERVE, 7 INFO, 0 unexplained error.**
   (Of the 12 FINDING lines, `F25` was a mis-built control of my own — corrected as `P1` in part 2 —
   and `J11` is a false alarm: `52001107` appears in `membership_runner_v2.py` only twice, both times
   in docstring prose *describing finding D-3*, at lines 13 and 327, never as a value the code reads.
   The remaining ten are N-1 and N-2.)
6. `python probe_v2_closure_part2.py <checkout> <repo>` — 9 further probes, output in
   `probe_output_part2.txt`, including the corrected v1 control and the enumeration of the 70
   surviving interpolation sites.

All corruptions and every "source" opened by the probes are small fakes written by the probe scripts
into a fresh temp directory: the shape of the real data, none of its content. Bound source/manifest
hash entries are overridden per probe, visibly and reversibly, because otherwise nothing but the two
real files could pass `verify_source_bytes`. Those two files were not touched. Manifests were read as
**raw Git blobs** — cohort id lists, not corpus.

**What I could NOT verify, stated rather than implied:**

- I have **not** verified that the bound cohorts correspond to anything in the real corpora, and I
  have **not** verified the two bound source hashes (`79fa87e9…`, `d6f21ea9…`) or byte sizes against
  the real files. Reading them is prohibited here. I verified only that the code pins them and that
  the values in `authoritative/accepted_configuration.py` match the accepted documents.
- I did **not** run `binding/validate_proposed_manifests.py`; my statement about it is carried over
  from the previous review and from reading its source.
- I did **not** re-audit the computation core, the design, the preregistration or the statistics.
- I did **not** attempt to prove that no tenth leak path exists; I report the nine I found.

---

## 5. Identities verified — from raw Git objects only

Every hash below was produced with `git cat-file blob <commit>:<path> | sha256sum` in a fresh clone of
my own. `core.autocrlf=true` in this machine's system config
(`file:C:/Program Files/Git/etc/gitconfig true`, unchanged) and the repository ships **no
`.gitattributes`**, so a Windows checkout hashes differently — that is finding D-4 itself.

**Commits**

| what | sha |
|---|---|
| candidate branch `impl/v52-runner-ingest-v2-2026-09-08` | `9b569687b394b0507fdeefc5abe456a9958e0788` |
| its parent — the v1 candidate reviewed as FAIL | `22e44608bab838974a6e65aa1a4297c815b5506b` |
| the previous review (the specification for this check) | `8c8ba7aefe2622efb4fbf65230f04dbfbec25449` |
| `origin/main` — this audit branch is parented on it (ledger L-076) | `6c5e0840c262443e372f6c71cf8eea2fd47ea253` |

**Blobs**

| path | sha256 | |
|---|---|---|
| `audit_v52_runner_ingest_review_2026_09_08/RUNNER_INGEST_REVIEW.md` @ `8c8ba7ae` | `456645a61c7e44148ee454287e7db0e66adfa128539b17679ce1c94897764676` | ✅ matches the brief |
| `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` @ `9b56968` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` | ✅ closed core, byte-unchanged from `22e44608` |
| `…/membership_runner_v1_2026_09_08/membership_runner.py` @ `9b56968` | `b322f85147733ead9494c33e5c78c02c2361a1986241de54c0c2aa6cc137a6d0` | ✅ v1 byte-unchanged |
| `…/membership_ingest_v1_2026_09_08/corpus_ingest.py` @ `9b56968` | `7dc084d8795c7e7d07270b866fdbc5e9c597508cbf331862b4075f9943fdf219` | ✅ v1 byte-unchanged |
| `…/binding/PROPOSED_mapping_locomo.json` @ `9b56968` | `66379b9dcf01f954cd1b7dac84bf16230f7c606f6092a4dc53cbcfe8b9708671` | ✅ accepted manifest, byte-unchanged (59268 B) |
| `…/binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json` @ `9b56968` | `d5b8ed6999eea0773fa2d7167054889d869efc283b1b7f4a475771ded9ed3714` | ✅ accepted manifest, byte-unchanged (36598 B) |
| `…/binding/PROPOSED_mapping_longmemeval.json` (SUPERSEDED) @ `9b56968` | `bdf05c12b4bc9298f54442932dd291b2d245370e18afa6df52d61af1a0844886` | ✅ byte-unchanged (36589 B) |
| `…/binding/PROPOSED_bootstrap_seeds.json` @ `9b56968` | `3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea` | ✅ byte-unchanged |
| `…/membership_runner_v1_2026_09_08/CONFIGURATION_IDENTITY_2026-09-08.md` @ `9b56968` | `33c1dc98ae3d0ea5d7d4fdf7d91755c9a85c94eb2790754b0d750c765ca55739` | ✅ byte-unchanged |

**The references inside `authoritative/accepted_configuration.py` resolve** — each checked by me
against the commit and path the module itself names (probes B1, J12–J15):

| what the module claims | resolved |
|---|---|
| `ACCEPTANCE_RECORD` → `…/BOUND_CONFIGURATION_ACCEPTANCE_2026-09-08.md` @ `22e44608` | `c5d2e63956426f61f28b19856e1298ac964b3a8228b7acf72ae32128f79e1d83` ✅ |
| `configuration_identity` @ `e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf` | `33c1dc98…5ca55739` ✅ |
| `ACCEPTED_MANIFESTS[LoCoMo]` @ `6911a03af68cb48a5090690b05acec59a67ce211` | `66379b9d…b9708671`, 59268 B, 1535 questions / 10 clusters ✅ |
| `ACCEPTED_MANIFESTS[LongMemEval]` @ `e61c414e…` | `d5b8ed69…d9ed3714`, 36598 B, 470 questions / 1 cluster ✅ |
| `BOUND_CORE` @ `dcb568d0a6c33154c1568500325ad457b4d6f455` | `bc2282d3…404e72` ✅ |
| `RNG_RULE.source_of_the_values` @ `6911a03a…` | `3f01082d…58da4fea` ✅ |

**No `.gitattributes` exists anywhere at `9b56968`**, and no global or local Git setting was changed
by this package or by me.

---

## 6. Files in this namespace

| file | what it is |
|---|---|
| `V2_CLOSURE_REPORT.md` | this report |
| `V2_CLOSURE_REPORT.md.sha256` | sha256 of the **committed blob** of this report |
| `probe_v2_closure.py` | my probe suite — replayable: `python probe_v2_closure.py <checkout of 9b56968> <repo root with .git>` |
| `probe_output.txt` | its raw output, as produced |
| `probe_v2_closure_part2.py` | the follow-up probes (corrected v1 control, interpolation-site enumeration) |
| `probe_output_part2.txt` | its raw output, as produced |
| `preparer_suite_v2_run.txt` | my own run of the preparer's `test_runner_ingest_v2.py` |

**Method for the report hash.** The value in `V2_CLOSURE_REPORT.md.sha256` is the sha256 of the **raw
Git blob** of `V2_CLOSURE_REPORT.md`, computed as
`git cat-file blob <commit>:audit_v52_runner_ingest_v2_closure_2026_09_08/V2_CLOSURE_REPORT.md | sha256sum`
— **not** of the checked-out file, which differs on Windows for exactly the reason set out in D-4.
Because the hash cannot be inside the file it describes, it is committed in a second commit that
changes nothing else, and the sidecar names the commit whose blob it pins.
