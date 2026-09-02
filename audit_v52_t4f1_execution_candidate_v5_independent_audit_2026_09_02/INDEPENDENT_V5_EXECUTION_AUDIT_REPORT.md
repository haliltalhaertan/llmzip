# V52 Task 4F1 — Execution Candidate V5 Cold-Start Independent Delta Audit Report

Audit date: 2026-09-02
Role: cold-start independent implementation auditor
Audit namespace: `audit_v52_t4f1_execution_candidate_v5_independent_audit_2026_09_02/`
Audited repository commit: `4244485c5aa874130026d44cd20104118361c9a7`
Audit branch: `audit/v52-t4f1-v5-independent-2026-09-02`

Instruction set: `prompts/V52_TASK_4F1_EXECUTION_CANDIDATE_V5_INDEPENDENT_DELTA_AUDIT_PROMPT_2026-09-02.md`
(SHA256 `a9d95906ca04aba83d812d80e4906fab181ff31d12bdd8c122385b7e0270e0bb`). No other repository
file was treated as an instruction. Every candidate, seal, manifest, README, spec, prior audit
report and prior co-chair review was treated as an untrusted hypothesis and re-derived from the
bytes. No prior LLM conversation, report or verdict was accepted as evidence.

---

## Verdict

`BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1`

The V4-to-V5 change set **is** genuinely declarative — established from the bytes, not imported
— so the delta route was correctly scoped. But the single-source normative gate that is the
entire reason V5 exists does not establish the claim it makes. Two of the prompt's BLOCKED
triggers are met on byte evidence: **missing concepts** (Gate 3.8) and **unlabelled second
normative sources** (Gate 3.3). Delta-route precondition 6 therefore fails.

CC-01 itself is genuinely repaired. That is not sufficient: V5's remediation is a general
mechanism, and the mechanism does not hold.

---

## Mandatory boundary declarations

| declaration | value |
| --- | --- |
| CLI `--mode run` count | `0` |
| CLI `--mode finalize` count | `0` |
| HMAC key environment set count | `0` |
| valid production authorization constructed | `false` |
| real retrieval ranking performed | `false` |
| retrieval quality computed / read / reported | `false` / `false` / `false` |
| candidate bytes modified | `false` |
| delta route justified | `true` for preconditions 1–5; **precondition 6 FAILS** |

Supporting counts, derived from the guarded command log rather than asserted: 13 guarded
launches, 6 commands refused before launch (all six from the harness self-test), 1 launch of
the permitted CLI `--mode preflight`. `run_archives`, `evaluate_archive` and `finalize_results`
were never called on real BEAM data; the only runner function invoked directly was
`verify_run_authorization`, on invalid fixtures, with the HMAC environment absent.
Machine-readable: `evidence/OUTCOME_BOUNDARY_TALLY.json`.

Every subprocess ran through `evidence/guarded_run.py`, which refuses — **before launch** — any
command containing `--mode run`, `--mode finalize`, `run_archives`, `evaluate_archive` or
`finalize_results`, refuses to launch at all while `V52_T4F1_AUTH_HMAC_KEY_HEX` is present, and
strips that variable from every child environment. Its refusal path was self-tested on six
forbidden command forms (`COMMAND_LOG.txt`, records 1–6).

No seal, manifest or authorization field was modified. The V5, V4, V3, V2 and V1 namespaces and
the sealed 4F0 namespace are byte-identical after the audit; every mutation experiment ran on a
throwaway copy under a scratch root. Verified by re-enumeration:
`evidence/G1_candidate_bytes_after_audit.json`.

---

## Environment

Built from source because the locked interpreter is not available prebuilt in this container
(the image ships 3.12.3; `uv` tops out at 3.12.11): CPython **3.12.13** from the python.org
source tarball (`Python-3.12.13.tgz`, SHA256
`0816c4761c97ecdb3f50a3924de0a93fd78cb63ee8e6c04201ddfaedca500b0b`, `PY_VERSION` confirmed in
`Include/patchlevel.h`). Locked dependencies installed exactly: NumPy 2.3.2, SciPy 1.16.1,
scikit-learn 1.7.1, psutil 7.0.0. All five single-thread controls plus `PYTHONHASHSEED=0` were
set by the harness, and every Python invocation used `-B` with `PYTHONDONTWRITEBYTECODE=1`.
The runner's own preflight confirms the interpreter and package versions it observed.

The pinned BEAM corpus is deliberately not in Git. It was materialized from
`mohammadtavakoli78/BEAM` at commit `3e12035532eb85768f1a7cd779832b650c4b2ef9` over the git
protocol (direct HTTPS to github.com is unreliable through this proxy) and verified **before any
use** against the committed pinned-tree manifest.

---

## Delta-route preconditions

All six were tested independently. Five hold; the sixth fails.

**1. Runner byte identity — PASS.** `v52_t4f1_beam_retrieval.py` is 61,860 bytes with SHA256
`f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8` in both the V4 and V5
namespaces, equal to the accepted V4 runner.

**2. AST equality with docstrings stripped — PASS.** Trivially implied by byte identity and
confirmed independently: normalized ASTs compare equal, all 45 function/class definition
digests are identical, and every module constant is identical.

**3. Retrieval-execution inputs and estimand anchors unchanged — PASS.** Re-derived from bytes,
not read from the seal:

- pinned-tree manifest SHA256 `650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318`;
  all **205 / 205** selected blobs reconstructed from the raw corpus bytes via
  `SHA1("blob " + decimal_length + NUL + payload)` match both blob ID and size; observed total
  804,231,963 bytes equals the declared total exactly; zero size mismatches, zero blob-ID
  mismatches, zero absent files.
- cohort SHA256 `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a`, and the
  structure re-derived from the CSV: 2,000 total rows, 1,712 eligible, 96 archives over eligible
  rows, 100 over all rows, excluded set exactly `{1M::5, 1M::26, 1M::33, 1M::34}`.
- dependency lock `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e`, byte-identical
  between V4 and V5.
- sealed 4F0 anchors verified on disk: final seal `596c8056…f859c`, protocol `f75e6c93…93cf1`.

**4. V4 audit package authenticity — PASS.** At `audit/v52-t4f1-v4-independent-2026-09-01` @
`641568d8b78af97eb69c9dc4e0434e7b6564a26c`: the hashes file's own SHA256 is
`8dcb2fb8b23980fd3fe0e65a25834e1af259bdef855ed577ae40ab4a43ee4387`, matching the declared value;
**30 / 30** declared entries match the bytes on disk; zero mismatches, zero missing, zero
undeclared files (complete reverse coverage). Its `audited_candidate` block reproduces all eight
V4 payload hashes exactly as I independently enumerated them, so that audit binds real,
unmodified V4 bytes.

**5. Changes limited to declarative payloads and package preflight — PASS.** See Gate 2.

**6. Single-source gate passes against the complete V5 payload closure — FAIL.** See Gate 3.

---

## Gate 1 — recursive byte closure and bindings: PASS

Exactly **nine** regular files, **zero** subdirectories, zero nested files, zero non-regular
entries, zero `__pycache__` and zero `.pyc`. All six package hashes declared in the audit prompt
match the bytes: implementation `f96cba2c…621f8`, `PAYLOAD_HASHES.json` `171acc06…31b4e`,
`CANDIDATE_EXECUTION_SEAL.json` `e8f2f9e8…1a40cc`, `NORMATIVE_SOURCE_MAP.json` `d64b865c…97002`,
`EXECUTION_SPEC.md` `e6494763…9be54a4`, `candidate_package_preflight.py` `0b0a57f8…1e1bd94`.

`PAYLOAD_HASHES.json` declares 7 files excluding itself and the seal (9 total, consistent); all
7 sizes and hashes match. The seal's bindings resolve and agree: `implementation` (hash and
61,860 bytes), `payload_inventory` (hash and 1,343 bytes), `environment.sha256`, cohort anchors,
pinned BEAM commit and tree manifest, and `authorization_control.key_commitment_sha256` as the
literal `PENDING_HEAD_RESEARCHER_PREREGISTRATION`. `status_at_audit_submission` is
`PREPARED_NOT_INDEPENDENTLY_AUDITED`.

Rejection of unbound payloads was proved on temporary copies only (F1 nested unbound file, F1b
top-level unbound file, F1c `__pycache__` bytecode, F1d mutated bound payload — all four
blocked), and the real candidate is byte-identical afterwards.

---

## Gate 2 — V4-to-V5 declarative change isolation: PASS

| file | state |
| --- | --- |
| `v52_t4f1_beam_retrieval.py` | **IDENTICAL** `f96cba2c…621f8` |
| `DEPENDENCY_LOCK.txt` | **IDENTICAL** `86a4db44…66655e` |
| `NORMATIVE_SOURCE_MAP.json` | NEW |
| `CANDIDATE_EXECUTION_SEAL.json`, `EXECUTION_SPEC.md`, `PAYLOAD_HASHES.json`, `README.md`, `RUN_AUTHORIZATION_TEMPLATE.json` | CHANGED (declarative) |
| `candidate_package_preflight.py` | CHANGED (the only executable delta) |

The retrieval runner is byte-identical. The only executable delta is the out-of-band package
checker: one added function `single_source_gate`, one added constant
`V4_ACCEPTED_RUNNER_SHA256`, a changed `main` (adds the gate call and renames the seal status
field it reads), and `sha256` unchanged. The runner neither imports nor mentions
`candidate_package_preflight` anywhere in its bytes, so the checker cannot influence execution.
The checker's authorization checks are unchanged from V4.

Nothing in representation fitting, query transformation, ranking, the signed/Haar/ITQ
algorithms, seeds, thresholds, tie priority, trial generation, metric definitions, aggregation,
checkpointing, finalization or authorization behaviour changed: all 45 runner definition digests
and every runner module constant are identical, and the module constants I re-read directly
(`HAAR_SEEDS`, `SIGNED_PERM_SEEDS`, `ITQ_SEEDS`, `ITQ_ITERATIONS`, `NUISANCE_TRIALS`, `TOP_K`,
`TIE_PREFIX`, `LATENT_DIM/SEED`, `MIXED_DIM/SEED`, `INVARIANCE_TOLERANCE`, `CANARY_SIGN_MARGIN`,
the canary sign digests, `AUTH_SCHEMA`, `AUTH_SIGNED_FIELDS`, and all seven `EXPECTED_*` anchors)
carry their V4 values. **No numerical-semantic drift.**

The implementer's `V4_TO_V5_DECLARATIVE_CHANGE.json` agrees with this derivation in every
per-file state. I record that agreement as corroboration only; the finding rests on my own
comparison.

---

## Gate 3 — single-source normative gate: FAIL

The candidate's own gate output was not accepted as evidence. It was re-derived.
For the record, the candidate's gate does pass: *"18 concepts each with one normative source; 5
typed mirrors equal; 0 deprecated literals surviving; runner byte-identical to the accepted V4
runner."*

### What genuinely holds

**3.1 / 3.2 — PASS.** All 9 bound payloads enumerated. 18 concepts, no concept declared twice,
every concept naming a non-empty authoritative path and locator, every declared mirror carrying
both a path and a locator.

**3.4 — PASS.** Zero surviving deprecated literals in the bound closure, under both an exact
substring detector and a stricter case-insensitive, whitespace-insensitive detector of my own.
Both superseded V3 raw-float digests and all four stale V3 schema labels are absent as
requirements from every bound text, JSON and Python payload, prose included.

**3.5 — PASS.** The registry exemption is exact and *not* widenable by a line-level trick: the
checker re-serialises the whole source map minus its `deprecated_literals` block and scans that
serialisation, rather than skipping lines. I confirmed a literal planted anywhere else inside
the map is still visible to the scan.

**3.6 — PASS. CC-01 is genuinely gone.** `EXECUTION_SPEC.md` contains exactly one canary
heading, `## Canary specification (NORMATIVE — sole source)`. The only 64-hex canary literals in
the spec are the two sign-code digests; neither V3 raw-float digest appears. The earlier
reference at line 44 is a pointer to that section, not a second definition.

### 3.3 — FAIL: nineteen unlabelled repetitions of declared load-bearing values

The map's own stated rule is that *"every repetition elsewhere is a typed derived mirror"* and
that *"an unlabelled second normative source is a gate failure."* Nineteen repetitions of
declared authoritative values sit in bound payloads that are neither the authoritative path nor
a declared mirror for that concept. All of them currently compare **equal**, so there is no
contradiction and no drift — but the prompt is explicit that the claim to verify is not "no
contradiction found".

The most load-bearing instances:

- **Five schema-version concepts.** `EXECUTION_SPEC.md` restates all five (lines 132–134), and
  line 76 states the authorization schema as a requirement in normative prose (*"`run` and
  `finalize` require a separate JSON authorization with schema `V52_T4F1_RUN_AUTHORIZATION_V4`"*).
  `EXECUTION_SPEC.md` is a declared mirror for none of the five: `candidate_schema_version` lists
  the seal and the checker, `authorization_schema_version` lists only the authorization template,
  and the remaining three declare **zero** mirrors while the spec restates them.
- **`dependency_lock`** declares **zero** mirrors, yet its value appears in
  `EXECUTION_SPEC.md:19`, `CANDIDATE_EXECUTION_SEAL.json:54` and — as the enforcement constant
  `EXPECTED_DEPENDENCY_LOCK_SHA256` — in the runner at line 42.
- **`cohort_anchor`** declares the runner and the authorization template as mirrors, but not the
  seal (`sealed_task4f0_boundary`, line 116) or `EXECUTION_SPEC.md:16`, both of which restate it
  under headings that read as normative (*"Exact input bindings"*).
- **`v4_to_v5_runner_identity`** is restated by `candidate_package_preflight.py:21` as the
  hard-coded enforcement constant `V4_ACCEPTED_RUNNER_SHA256`, and by `README.md:79`. Neither is
  a declared mirror. The checker's copy is the one the gate actually enforces against.
- **`candidate_submission_status`** declares **zero** mirrors while the value appears in
  `README.md` (three times), the checker's enforcement check at line 130, and as a `status`
  field in `PAYLOAD_HASHES.json:42` — a second JSON file carrying a status-shaped field, which is
  the structural shape of CC-01 itself.
- **`authorization_commitment_state`** is restated in `EXECUTION_SPEC.md:89` and `README.md:17`,
  neither declared for it.
- **`methods_seeds_trials_topk_priority`** is restated by the seal's `arms` and
  `execution_interpretations` blocks (seeds 43001–43005 at lines 3, 6 and 66–70; ITQ seeds and
  `itq_iterations: 100`), while only `EXECUTION_SPEC.md`'s Arms section is declared as a mirror.
  The seal's `execution_interpretations` block additionally restates the aggregation rule, the
  `>= 0` threshold, the Haar QR sign correction, the ITQ fit payload, the UTF-8 memory key, the
  archive fit cache, the nuisance-trial semantics and the tie-priority trial dependency — none
  of it typed anywhere.

### 3.8 — FAIL: the coverage list is under-declared

Against the required concept set, two categories have **no** declared concept at all:

- **methods (arm identifiers).** `NATIVE_SIGN96`, `SIGNED_PERM_CONTROL96`, `HAAR96_SIGN` and
  `ITQ96_CENTERED` appear only in the seal's untyped `arms` block and the spec's Arms section.
  The method set is validated at finalization, so it is load-bearing.
- **tie priority.** The concept locator names `TIE_PREFIX`, but the declared `value` omits both
  the prefix and the formula, while `EXECUTION_SPEC.md`'s "Tie and trial interpretation" section
  states the full normative formula — and that section is not typed as a mirror for anything.

And five load-bearing constants that the runner enforces have **no declared concept whatsoever**:

| runner constant | value | appears in bound payloads |
| --- | --- | --- |
| `EXPECTED_BEAM_MANIFEST_SHA256` | `650cc145…d8318` | seal, `EXECUTION_SPEC.md`, runner |
| `EXPECTED_RESTRICTED_SEAL_SHA256` | `596c8056…2f859c` | seal, `EXECUTION_SPEC.md`, runner |
| `EXPECTED_PROTOCOL_SHA256` | `f75e6c93…493cf1` | seal, `EXECUTION_SPEC.md`, runner |
| `EXPECTED_PARENT_COMMIT` | `d3c7aa09…e4257` | seal, `EXECUTION_SPEC.md`, runner |
| `TIE_PREFIX` | `V52_T4F0_TIE_PRIORITY_V1` | `EXECUTION_SPEC.md`, runner |

The pinned-tree manifest anchor is the sharpest case. `upstream_corpus_anchor` covers only the
BEAM commit, yet `EXECUTION_SPEC.md:22` states in terms that *"Manifest commit identity alone is
insufficient"* — the manifest is separately load-bearing by the package's own account, is
restated in three bound payloads, and is declared nowhere.

Two authoritative paths also lie outside the bound payload closure and so can never be checked
by the gate: the cohort CSV (legitimate, and I verified it independently) and
`"docs/v52/task4f1/ detached attestation"`, which is not a resolvable file path at all.

### 3.7 — PARTIAL: the gate blocks a verbatim CC-01 but not two trivial variants

Reintroducing CC-01 verbatim in a temporary copy is blocked, correctly, by the deprecated-literal
scan (F3). Two mechanical variants of the *same* reintroduction are **not**:

- **F3b — line wrapping.** Each V3 digest wrapped across two prose lines, exactly as Markdown
  wraps long literals. The scan matches per line, so the gate **passes** and CC-01 is back.
- **F3c — uppercase hex.** The same digests in uppercase. The scan is case-sensitive, so the
  gate **passes** and CC-01 is back.

---

## Gate 4 — status and attestation semantics: FAIL

**Holds:** the seal carries no bare `status` field; `status_at_audit_submission` is
`PREPARED_NOT_INDEPENDENTLY_AUDITED`; `status_semantics` states the field is never edited to
express acceptance; all 17 `required_independent_gates` are `PENDING`. Editing the submission
status to express acceptance is blocked (F4b), and adding `status: ACCEPTED_…` is blocked (F4c's
sibling F4).

**Fails**, on three independent grounds:

1. **The declared sole authority holds no V5 record.** The map names
   `"docs/v52/task4f1/ detached attestation"` as authoritative for `post_audit_acceptance_state`
   with value `NOT_YET_ACCEPTED_FOR_V5`. That directory contains exactly one file —
   `V4_HEAD_RESEARCHER_ACCEPTANCE_2026-09-02.json` (SHA256 `f04eecd5…6c547`) — and it contains no
   V5 record. The value therefore exists only in the map, whose authoritative path for it does
   not carry it. The gate never checks this: step 2 only tests that the string is non-empty.

2. **The bound package and its declared authority contradict each other on V4.** The V5 seal
   states V4's disposition as *"audit evidence valid, package seal withdrawn by co-chair CC-01"*.
   The detached attestation still asserts `authoritative_status:
   SEALED_BY_HEAD_RESEARCHER_2026-09-02` and records no withdrawal, no CC-01 and no revocation.
   Under the package's own precedence rule — *"the detached attestation is authoritative for
   current state"* — the authoritative current state says V4 is sealed. V5 has replaced an
   in-package contradiction with a cross-boundary one.

3. **Acceptance can re-enter the seal under any other field name (F4c).** Adding
   `current_acceptance_state: ACCEPTED_BY_HEAD_RESEARCHER_AND_CO_CHAIR_2026_09_02` and
   `independent_audit_result: PASS` to the seal **passes** the gate. The check is
   `if "status" in seal and seal["status"] != seal["status_at_audit_submission"]`, which is
   vacuous on the real package (there is no `status` key) and blind to every other field name.

Separately: the seal's `stop_rule` requires *"a fresh outcome-free independent **V4** audit"* —
naming the wrong audit generation in a V5 package. `outcome_boundary_and_stop_rule` declares only
the three authorization fields as its value, so the stop-rule text itself has no authoritative
value against which that error could be caught.

---

## Gate 5 — package-preflight behaviour: PARTIAL

Eighteen fixtures of my own construction, each on a fresh throwaway copy; the source namespace is
byte-identical afterwards. Twelve behaved as expected, six did not:

| fixture | expected | blocked |
| --- | --- | --- |
| F0 untouched package | pass | pass ✓ |
| F1 / F1b / F1c / F1d unbound, `__pycache__`, mutated payload | block | block ✓ |
| F2 runner byte-changed with inventory and seal consistently updated | block | block ✓ |
| F3 CC-01 verbatim | block | block ✓ |
| **F3b CC-01 with wrapped digests** | block | **passes ✗** |
| **F3c CC-01 with uppercase digests** | block | **passes ✗** |
| F4 seal `status: ACCEPTED…` | block | block ✓ |
| F4b submission status edited to acceptance | block | block ✓ |
| **F4c acceptance under alias field names** | block | **passes ✗** |
| F5 fail-closed commitment replaced by a real hash | block | block ✓ |
| **F6 deprecated registry emptied and CC-01 re-added** | block | **passes ✗** |
| **F7 canary concept deleted from the map** | block | **passes ✗** |
| F8 typed mirror `signed_fields` truncated | block | block ✓ |
| F9 canary concept declared twice | block | block ✓ |
| **F10 new contradictory normative aggregation statement** | block | **passes ✗** |

The implementer's `SINGLE_SOURCE_GATE_FIXTURES.json` was read **only** for coverage, never used
as my evidence. Its ten cases are all exact-match adversaries, one per code path the gate
implements; none of the six classes above appears in it. That is the vacuity risk Gate 7 names:
the fixtures test the implementation rather than the claim.

---

## Gate 6 — preserved implementation gates

Runner byte-identity **is** established (Gate 2), so the V4 audit's results may be cited. Stating
plainly which conclusions rest on citation rather than on my own re-derivation:

**Cited from the V4 audit, not re-derived here:** B1 (no-replace finalization and crash-temp
behaviour), B2 (exact frozen-gold metric recomputation), B3 (exact Native/signed-control
top-three IDs and distances), output schema and aggregation, and the static leakage audit. These
are evidence about V4 bytes; they transfer only because the runner is byte-identical, and the
V4 audit package that carries them is authentic (30/30, verified above).

**Re-derived by me, resting on no citation:**

- **Authorization fail-closed.** Statically: `verify_run_authorization` requires the seal's
  `key_commitment_sha256` to be 64 lowercase-hex characters and raises
  `[BLOCKED - HEAD RESEARCHER AUTHORITY KEY NOT SEALED]` before ever reading the key environment.
  V5's commitment is the 39-character literal `PENDING_HEAD_RESEARCHER_PREREGISTRATION`, so **no
  authorization document can pass, by construction** — this needs no fixture and I built none
  that approached validity. Dynamically, on invalid fixtures with the HMAC environment absent:
  the inert in-package template and three synthetic authorizations (no signature; arbitrary
  invalid HMAC; superseded V3 schema label) were all refused, and **no output directory was
  created** in any case.
- **Canary anchors.** The permitted CLI `--mode preflight` reproduced, on real BEAM data, both
  bound sign-code digests exactly: archive `7365b6c4…ded5b5` and query `5e40a5d1…ccad2b`,
  archive shape `[392, 96]`, query shape `[1, 96]`, 392 archive units, status `PASS`. It did so
  on a **different numerical backend** than the V4 audit's six dispatches — scipy-openblas 0.3.30
  with no `OPENBLAS_CORETYPE` set — which independently corroborates the V4 remediation's premise
  that sign codes are dispatch-stable where raw floats were not. The report also confirms
  `gold_labels_loaded: false`, `question_file_opened: false` and
  `retrieval_quality_computed: false`: the tool held the boundary itself.
  The archive sign margin reproduced identically at `4.088828967405535e-07`; the query margin
  differed in its last few digits (`…5938162` vs the seal's `…5919399`), a ~1e-15 relative
  difference far inside the declared ~1.2e-13 cross-dispatch spread and ~3.4e6 below the 1e-9
  guard. The **bound** quantities — the sign digests — are identical. Not drift.
- Recursive closure, change isolation, the single-source re-derivation, attestation semantics,
  the corpus manifest, the cohort anchor and every fixture above.

---

## Gate 7 — active bug hunt

Seven defects, each reproduced on bytes:

1. **Deprecated-literal scan defeated by line splitting** (F3b). `EXECUTION_SPEC.md` and
   `README.md` are Markdown; wrapping a 64-hex digest across two lines is ordinary formatting,
   not an attack. CC-01 returns and the gate passes.
2. **Deprecated-literal scan defeated by casing** (F3c). The scan is case-sensitive; hex digests
   are equally valid in uppercase.
3. **Acceptance state re-enters the seal under an alias field** (F4c). The acceptance guard keys
   on the single field name `status`.
4. **Vacuous on an emptied registry** (F6). Nothing requires `deprecated_literals` to be
   non-empty or to match an expected set. Emptying it silences the only scan that caught CC-01;
   with the registry empty, CC-01 verbatim passes.
5. **Vacuous on a dropped concept** (F7). Deleting `canary_algorithm_and_digests` from the map is
   not detected. Coverage is never checked against any required set, so the map can shrink to
   nothing load-bearing while the gate keeps reporting "N concepts each with one normative
   source". Only four concepts are hard-referenced by the checker; the other fourteen are
   free-floating.
6. **A new untyped normative source is not detected** (F10). This is the decisive one. Appending
   a fresh normative aggregation statement to `EXECUTION_SPEC.md` that **contradicts** the
   declared rule — *"seeds and trials are independent statistical units"*, the exact scientific
   error the aggregation rule exists to prevent — **passes** the gate. The mechanism built to
   prevent a recurrence of CC-01 does not detect a recurrence of CC-01 in any concept its author
   did not anticipate. It confirms the absence of *known-superseded literals*; it does not
   establish single-sourcing.
7. **The byte-identical runner reads a seal field V5 removed.** V4's seal carried top-level
   `status: PREPARED_NOT_INDEPENDENTLY_AUDITED`; V5 renamed it to `status_at_audit_submission`.
   The runner is byte-identical and still reads `execution_seal.get("status")` at line 1219, so
   its own preflight provenance record now emits `execution_seal_status: null` where V4 emitted
   the string — reproduced in my CLI preflight output. No gate is lost (the runner never gated on
   that field), but a declarative payload change silently degraded the byte-identical runner's
   emitted provenance, and neither the V5 change scope nor the source map declares the runner's
   read of the old locator. "Executable behaviour change: NONE" is true of the code and not quite
   true of the record it writes.

Also examined and **not** found defective: a mirror typed as derived but actually normative (all
typed mirrors compare equal where mechanically checkable, and F8 confirms disagreement blocks);
the registry exemption (exact, whole-file re-serialisation, not widenable — F9 confirms duplicate
concepts block); and the runner's influence surface (the checker is never imported).

---

## Non-blocking observations

- `README.md:1` is titled *"Execution Implementation Candidate V4"* inside the V5 package. Not an
  enumerated deprecated literal, and cosmetic, but the package's front matter misnames itself.
- The canary mirror for `README.md` is located as *"V5 change summary"*, while the actual canary
  restatement (`packbits`, `CANARY_SIGN_MARGIN = 1e-9`) sits in the "V4 change versus V3" section.
  The locator does not resolve to the text it types.
- The gate prints *"5 typed mirrors equal"* against 13 declared mirrors. Accurate as written, but
  it invites reading the gate as broader than it is.

---

## Custody

Outputs were pushed incrementally to `audit/v52-t4f1-v5-independent-2026-09-02`, created fresh
from the audited commit `4244485`, under explicit Head Researcher custody instruction. Only this
audit namespace was committed; no tracked project file was modified (verified before each commit
by a path-excluded `git diff HEAD`); no `__pycache__`, corpus bytes or virtualenv were staged.
No commit to `main`, no merge, no pull request. Tags were not attempted.

Remote `main` advanced during the audit from `4244485` to
`c44495f6fc365ee1957e8029c42fc6fd45d0b0bd`, a single descendant commit touching only
`docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json`. The V5 candidate namespace is
byte-identical at both commits, so this audit's conclusions apply unchanged at `c44495f`.

---

## What would clear this

Not a re-audit of the same mechanism. The gate needs to establish its claim rather than confirm
the absence of known-bad literals:

1. Derive the deprecated-literal scan over normalized text (case-folded, whitespace-stripped) and
   over each payload's whole byte stream, not line by line.
2. Require the deprecated registry to be non-empty and to cover a declared expected set, so it
   cannot be emptied silently.
3. Check coverage against an enumerated required concept list, so a concept cannot be dropped.
   Add the six currently missing concepts: the pinned-tree manifest anchor, the restricted
   protocol and 4F0 final-seal anchors, the parent-commit anchor, the tie-priority formula, and
   the arm identifiers.
4. Type every existing repetition, or delete it. Nineteen are listed above with file and line.
   Concepts declaring zero mirrors while three payloads restate them are the priority.
5. Make the acceptance guard positive rather than name-based: enumerate the seal's permitted
   top-level keys and reject any unknown key, instead of testing one field name.
6. Resolve the attestation authority: publish a V5 record, record V4's withdrawal, and make the
   authoritative path a resolvable file rather than a directory description.
7. Fix the seal's `stop_rule` reference to the V4 audit generation, and either restore the seal
   field the runner reads or declare the divergence explicitly.

None of this requires touching the runner, so the delta route remains available to a V6.
