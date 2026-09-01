# V52 Task 4F1 — Execution Candidate Cold-Start Independent Audit

**Date:** 2026-08-31
**Role:** cold-start independent implementation auditor
**Subject:** `../task4f1_execution_candidate_2026_08_31/v52_t4f1_beam_retrieval.py` (52,673 bytes, SHA256 `28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428`)
**Output namespace:** `audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31/`

---

## Verdict

**PASS WITH CONDITIONS — EXECUTION CANDIDATE MAY BE SEALED BY HEAD RESEARCHER; TASK 4F1 STILL NOT AUTHORIZED**

Every load-bearing gate passes. Three conditions (D1, D2, D3) are recorded below; none of them changes a
number the implementation would produce, and none is a computation defect. This verdict does **not**
authorize preregistration, execution, or outcome access.

One auditor-side protocol breach occurred during this audit (**Incident A1**) and is disclosed in full in
§7 and in `COMMAND_LOG.txt`. No outcome value was read and no candidate byte was changed.

---

## 1. What was verified

The question this audit answers is narrow: **do these exact implementation bytes faithfully execute the
already sealed 1,712-question Task 4F0 restricted-cohort protocol, and are they safe to place before a
later, separate preregistration decision?**

Repository state is as expected. `HEAD = d3c7aa09c9553cd5ac100e668923abab602e4257` on branch
`codex/research-lead-takeover-2026-08-31`. The worktree is dirty (four modified top-level documents and
the untracked 4F0/4F1 namespaces); this is **recorded, not repaired**. The repository is owned by another
local principal, so `git config --global --add safe.directory` was required to read git state — an
auditor-side config change only; no repository byte was touched.

All exact byte anchors from the mission statement reproduce independently: the implementation, the payload
inventory, the candidate seal, the preparation preflight evidence, the sealed 4F0 final seal, the sealed
cohort, the restricted protocol, the dependency lock, and the accepted pinned-tree manifest. The pinned
BEAM commit is `3e12035532eb85768f1a7cd779832b650c4b2ef9`.

---

## 2. Gate results

Full detail is in `GATE_TABLE.csv`; the per-gate evidence files are listed there. Summary:

| Gate | Subject | Verdict |
|---|---|---|
| 1 | Namespace and byte closure | PASS **with condition D1** |
| 2 | Environment enforcement | PASS |
| 3 | Corpus byte identity (192/192) | PASS |
| 4 | Cohort and source-ID join | PASS |
| 5 | Static and runtime leakage | PASS |
| 6 | Representation equivalence | PASS |
| 7 | Binary arms and invariance | PASS |
| 8 | ITQ implementation | PASS |
| 9 | Tie and nuisance semantics | PASS |
| 10 | Metrics and structural zero | PASS |
| 11 | Checkpoint and resume safety | PASS |
| 12 | Authorization guard | PASS **with condition D2** |
| 13 | Row schema and aggregation | PASS |
| 14 | Active bug hunt | PASS (no defect in the listed failure modes) |

### The load-bearing results, stated plainly

**Corpus identity is real, not nominal.** The materialized directory name was not trusted. For all 96
eligible archives, both `chat.json` and `probing_questions.json` were re-read as raw bytes and their Git
blob SHA1 reconstructed as `SHA1("blob " + len + NUL + payload)`. **192/192** match both blob ID and size
against the accepted pinned-tree manifest (205 selected entries).

**The cohort joins exactly.** 2,000 rows; unique `audit_question_id`; exactly **1,712** eligible; **96**
archives; `1M::5`, `1M::26`, `1M::33`, `1M::34` absent from the eligible set; every eligible row is
`EXACT_SOURCE_IDS`, non-abstention, with positive gold cardinality matching `gold_source_unit_count`.
Raw message IDs are unique within all 96 archives, and **every eligible frozen gold ID joins exactly once**
to its archive raw ID. 587 eligible questions carry more than three gold units, matching the sealed 4F0
structural-zero count. No question was ranked to establish any of this.

**The representation is exactly the sealed one.** This is the strongest result in the audit. Rather than
calling the candidate and checking its self-report, the pipeline was **re-implemented independently from
the sealed Task 4F0 specification** (word TF-IDF 1–2 with English stop words and sublinear TF; `char_wb`
3–5 sublinear; L2; `TruncatedSVD(32, random_state=5101)`; L2; hstack; `TruncatedSVD(96,
random_state=5204)`; L2; archive-mean centering) and run on the raw `100K/12/chat.json` bytes with the
fixed invented canary string. It produces:

- 392 units; archive shape 392×96; query shape 1×96; `rank(y96) = 96`; all values finite
- archive SHA256 `25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`
- query SHA256 `e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`

Both equal the sealed anchors, and the independent output equals the candidate's output **byte for byte**
— same message texts, same IDs, same matrices. Repeat fits and repeat transforms are byte-identical.
`probing_questions.json` was never opened; no gold, no ranking, no metric.

**Archive caching is sound.** `fit_archive_representation` takes exactly one argument — the ordered
archive memory-text list — so its output is a pure function of the archive. Reusing one fit across the
questions of that archive is therefore mathematically identical to refitting per question, and this was
confirmed numerically by exact array equality (`np.array_equal`) on both real and synthetic archives. The
model is a local of `evaluate_archive` with no module-level cache and no memoisation decorator, so a model
cannot be reached from a different conversation; a different conversation demonstrably yields a different
model and unit count.

**No leakage path exists, statically or at runtime.** The module contains no `answer`, `ideal`, `rubric`,
`grade`, `evaluator`, `judge`, `difficulty` or source-order token anywhere. Its only module-level
containers are `ENVIRONMENT_LOCK` and `THREAD_LOCK`, never mutated and never subscript-assigned. An
import-only harness (candidate bytes copied to the audit namespace, re-hashed to the sealed anchor,
imported with bytecode writing disabled) instrumented every fit function and drove two wholly synthetic
archives with invented texts, IDs, questions and gold. Observed: exactly one fit per archive; the fit
received only role-prefixed `str` lists; the synthetic query marker never reached a fit and appeared only
in `transform_queries`; `fit_itq` received exactly a centered C96 produced by a fit; `priority_arrays`
received the archive's full canonical key list, hash-identical to an independently recomputed list; and
`metrics_at_3` was first called only *after* the first ranking.

**The arms are correct.** Native thresholds centered coordinates at `>= 0`. Signed permutation uses seeds
43001–43005 with the declared NumPy order — `default_rng(seed).permutation(96)` *then*
`choice([-1.,+1.], size=96)` — and the swapped order provably does not reproduce it. For all five seeds
across seven synthetic queries, **distances, tie sets, full rankings and top-three sets all equal Native
exactly**. Haar uses the declared Gaussian → reduced QR → `Q * sign(diag(R))` with exact zero replaced by
`+1`; each matrix is orthogonal, dot products and both norm vectors are preserved within `1e-12`, the
rotation is common to archive and query, and an inconsistent transpose provably breaks preservation.

**ITQ matches the canonical audited implementation byte for byte.** The candidate's `fit_itq` was compared
against a verbatim transcription of `adapters/longmemeval_v52_adapter.py::fit_itq` — the canonical audited
Task 4C2 implementation. For all five seeds (101/202/303/404/505) the resulting rotations are identical
under raw-buffer SHA256: same `default_rng` initialization, same SVD orthogonal factor, same threshold
orientation (`B = +1` where `V @ R >= 0`), same covariance orientation (`C = B.T @ V`), same Procrustes
update (`R = Vt.T @ U.T`). Both the covariance-transposed and Procrustes-transposed variants differ. The
fit is archive-only, the rotation is common to archive and query, and the arm is declared descriptive-only.

**The tie priority is the sealed formula, exactly.** `tie_priority` reproduces
`uint128_be(SHA256(b"V52_T4F0_TIE_PRIORITY_V1" + NUL + archive_id + NUL + memory_key)[:16])` on every
probe, while the no-separator, little-endian and last-16-byte variants all differ. The `(hi, lo)` `uint64`
split reproduces the true 128-bit ordering over 500 keys. `np.lexsort((canonical_order, priority_lo,
priority_hi, distances))` was verified by construction to give the precedence **distance → priority high 64
→ priority low 64 → canonical index**. The memory key serializes exactly as
`tier::conversation_id::decimal_raw_message_id` and depends on nothing else.

**Aggregation is correct and fails loudly.** On wholly synthetic tables: 320 rows per question (Native 20;
signed 5×20; Haar 5×20; ITQ 5×20); complete and unique `(question, method, seed, trial)` cells; trials
collapse inside `question × method × seed`, then seeds collapse inside `question × method`, then questions
carry equal weight over the 1,712 denominator with no seed, trial or archive-size weighting. An independent
recomputation of every aggregate matched to better than `1e-12`, and the signed-permutation aggregate
equals Native exactly. Malformed, missing, duplicate, trial-varying, metric-inconsistent and
structural-zero-violating rows each **block** rather than silently aggregate. Finalization prints no metric
value and sets `interpretation_authorized = false`.

---

## 3. The trial-semantics question, decided

Gate 9 asks for an explicit decision, so here it is.

The sealed protocol fixes one priority per memory key with **no trial input**, and states that the run uses
"20 fixed nuisance trials per question and arm" which "are collapsed within question; they are not
independent statistical units." The implementation follows this literally: it computes the ranking once per
`(question, method, seed)` and emits 20 rows differing only in the `trial` column. A source comment states
the reasoning, and a hard finalization check
(`[BUG - TRIAL-VARYING TOP3 UNDER FIXED PRIORITY]`) rejects any table in which the 20 rows disagree.

**This literal interpretation is faithful and scientifically non-misleading.** It is faithful because a
trial-dependent priority would be an *unsealed* addition to a frozen protocol — inventing variation the
protocol does not authorize. It is non-misleading because the 20 rows never survive into an inferential
denominator: they are averaged to a single value inside `question × method × seed` before seeds collapse,
and the final denominator is 1,712 equal-weight questions per arm, exactly as sealed. The rows are an
audit-trail replication artifact, not evidence.

I searched specifically for a hidden trial-dependent priority and found none: `tie_priority`,
`priority_arrays` and `rank_hamming` have no trial parameter in their signatures, and no trial value
reaches any seed, rotation, threshold or fitting call.

The one residual risk is presentational, not computational: a reader of the raw 547,840-row trial CSV who
does not read the protocol could mistake 20 identical rows for 20 observations. Condition C4 below
addresses that.

---

## 4. Defects and conditions

### D1 — Unbound payload in the candidate namespace *(minor; blocking for the "no unbound payload" claim only)*

`__pycache__/v52_t4f1_beam_retrieval.cpython-312.pyc` (62,703 bytes, SHA256
`0dca302e7faa4ff805747892daba9eb6df6e8fde778e0a11b844d79e4e443dac`) is present in the candidate namespace
but absent from `PAYLOAD_HASHES.json`. The namespace therefore holds 9 files where the seal accounts for 8.

Root cause: `candidate_package_preflight.py` computes closure as
`{path.name for path in ROOT.iterdir() if path.is_file()}` — top level only, files only — so a *directory*
containing unbound bytes is invisible to it and the tool reports closure PASS.

This does not affect any computed value: CPython invalidates a stale `.pyc` against source mtime and size,
and the audit re-hashed the source, not the cache. But the seal's closure claim is literally false as the
namespace stands.

**Condition:** delete `__pycache__/` before sealing, and change the closure check to walk recursively
(`ROOT.rglob("*")`) so directories cannot hide unbound bytes.

### D2 — The run authorization is an interlock, not a cryptographic control *(material; procedural)*

Every field `verify_run_authorization` requires — implementation SHA256, candidate-seal SHA256, cohort
SHA256, `required_archive_count: 96`, and an arbitrary `output_namespace_basename` — is computable by
anyone holding the candidate namespace. There is no signature, no secret, and no Head-Researcher-held
credential. The runner will happily compute all three hashes for the operator.

The consequence is precise: the guard **reliably prevents accidental or malformed execution** (verified
21/21, all blocking before output-directory creation), but it **does not prevent unauthorized execution**
by anyone with file access — and this requires no Python source modification, so it is not covered by the
byte-binding argument. This audit produced an unintended existence proof (Incident A1, §7).

**Condition:** the Head Researcher's authorization should bind a value **not derivable from the candidate
namespace** — a signature, or a nonce fixed in the accepted Task 4F1 preregistration and recorded in the
preregistration seal — and/or the output namespace should be created solely by the Head Researcher. This
is a preregistration-artifact condition, not an implementation change, and does not require new candidate
bytes.

### D3 — Archive checkpoints carry no provenance *(minor)*

Archive metadata records schema, archive id, question and row counts, invariance tolerances, array digests,
RSS, elapsed time and the CSV hash — but **not** `script_sha256`, `cohort_sha256`, or
`run_authorization_sha256`. `verify_existing_archive` therefore accepts any internally consistent
checkpoint on resume and at finalization.

Within the CLI boundary this is contained: every write path re-verifies the script hash against the seal,
and both `run` and `finalize` refuse a namespace that already holds a post-run manifest. The exposure is a
checkpoint placed manually from a different build, which would be indistinguishable.

**Condition:** stamp `script_sha256`, `cohort_sha256` and `run_authorization_sha256` into each archive
metadata file and verify them on resume and at finalization.

### C4 — Trial-row presentation *(recommendation, not a defect)*

Because the 20 trial rows per `(question, method, seed)` are identical by construction (§3), the raw trial
CSV should not be circulated without the protocol note. **Recommendation:** the Task 4F1 preregistration
should state, in the results-reporting section, that trial rows are deterministic replication identities
and that the inferential denominator is 1,712 questions per arm.

### D5 — Exact-zero sign edge case *(advisory; correctly guarded — no action required)*

`-0.0 >= 0` is `True` in IEEE-754, so a coordinate that is exactly `0.0` does **not** flip its bit under a
`-1` sign. If exactly one of a (document, query) pair at some column is exactly zero and that column draws
sign `-1`, signed-permutation Hamming invariance breaks at that bit. I confirmed by construction that this
is reachable in principle.

The candidate does not silently absorb it. The per-question hard control
(`[BUG - HAMMING-INVARIANT CONTROL FAILED]`) raises and aborts the archive. That is the correct failure
mode — a blocked run rather than a corrupted control arm. It is recorded here so that if the control ever
fires in production it is diagnosed as this edge case and not misread as a code defect. Probability on real
float64 SVD output is negligible; it did not occur on either real archive fitted during this audit.

### D6 — Minor observations *(no action required)*

- `canonical_raw_id` accepts a negative Python `int` (`-5` → `"-5"`) but rejects the string `"-5"`
  (`str.isdigit()` is `False`). Asymmetric, and unreachable for BEAM: all raw IDs across all 96 archives are
  non-negative, verified.
- The sealed 4F0 arms block names seeds for Haar and ITQ but not for `SIGNED_PERM_CONTROL96`. The candidate
  reuses 43001–43005 and declares this as an interpretation in the execution seal. Immaterial: the control
  must equal Native exactly for every seed, enforced both as a runtime abort and at finalization, so no seed
  choice can change any reported number.
- `finalize` prints the literal string "all 96 archives finalized" rather than a computed count. In
  production the count is enforced to be 96 before that line executes, so the message is true.

---

## 5. Exact hashes

**Candidate namespace** (independently re-hashed):

| File | Bytes | SHA256 |
|---|---|---|
| `v52_t4f1_beam_retrieval.py` | 52,673 | `28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428` |
| `PAYLOAD_HASHES.json` | 1,115 | `278dbf80d6388a7dcd2605791283442615d5a951b2ef1e1ce1b6c92b4dd392b7` |
| `CANDIDATE_EXECUTION_SEAL.json` | 4,098 | `a1277e4665936ea691505a2d386c1d6a4824c2ebc5e5e56d6a94aba1f58876cd` |
| `EXECUTION_SPEC.md` | 7,682 | `d7a74dca526fcd1f7363deaa8d334842e43b539dc4859a4d96867d1dc5471311` |
| `DEPENDENCY_LOCK.txt` | 330 | `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e` |
| `README.md` | 1,217 | `b0030f29ab37d2bc5fbe60b06e8035eeec519b509debd289a8ce2ad387aec6ea` |
| `RUN_AUTHORIZATION_TEMPLATE.json` | 633 | `df581d47668f435682435f6fd908e6d9319f77aeee2ce17a2d67ee19b5ea73cd` |
| `candidate_package_preflight.py` | 3,235 | `b6b162d6eba08bb218c9c465a134a7316831f5b1eb69f76f190edc42d6b597cf` |
| `__pycache__/…cpython-312.pyc` **(unbound, D1)** | 62,703 | `0dca302e7faa4ff805747892daba9eb6df6e8fde778e0a11b844d79e4e443dac` |

**Upstream anchors** (all verified equal to the mission statement):

| Artifact | SHA256 |
|---|---|
| Sealed 4F0 final seal | `596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c` |
| Sealed cohort | `9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a` |
| Restricted protocol | `f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1` |
| Dependency lock | `86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e` |
| Accepted pinned-tree manifest | `650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318` |
| Preparation preflight evidence | `138f291ee53a70c0c4f37d4797e683acd1db77d5f362db676b5517e0d8f91f49` |
| Pinned BEAM commit | `3e12035532eb85768f1a7cd779832b650c4b2ef9` |
| llmzip parent commit | `d3c7aa09c9553cd5ac100e668923abab602e4257` |

**Canary digests** (independently reproduced): archive
`25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025`, query
`e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869`.

Hashes of this audit's own outputs are in `INDEPENDENT_EXECUTION_AUDIT_HASHES.json`.

---

## 6. What could not be tested without outcomes

These are genuine limits of a pre-outcome audit, not omissions:

1. **No retrieval-quality value of any kind** — Native, Haar, ITQ, at any level — was computed, read or
   reported. Nothing in this audit speaks to whether the axis probe will show an effect.
2. **Full-scale execution was not exercised.** Only two real archives were fitted (`100K::12`, 392 units,
   and `500K::12`, for the different-archive check). Wall-clock, memory and numerical behaviour on the
   largest archives (up to 23,716 units) are unverified, including whether the `1e-12` Haar tolerance holds
   there. The tolerance is absolute, and dot-product magnitudes grow with archive size, so this is worth a
   deliberate first-archive check at run time.
3. **Whether any real archive contains an exact-zero centered coordinate (D5) is unknown.** It would abort
   that archive rather than corrupt it, but it is a run-availability risk that only execution can settle.
4. **Real-data ranking behaviour** — actual tie frequencies, gold-hit distributions, distance
   distributions — is entirely untested, by design.
5. **The aggregation path was exercised at test scale.** `finalize_results` was driven end-to-end on
   synthetic tables with `EXPECTED_ELIGIBLE` temporarily reduced in an imported copy, because the production
   constant demands 547,840 real rows. The production constants (1712 / 96 / 2000 / 3) and the fact that the
   aggregate denominator is `EXPECTED_ELIGIBLE` with no weighting term were asserted separately and
   statically. The logic is fully covered; the scale is not.
6. **The Head Researcher's future authorization artifact** does not exist and could not be reviewed.

---

## 7. Incident A1 — auditor protocol breach, disclosed

The first version of my authorization negative-test script contained a design error. Three cases intended
to probe bypass paths built payloads in which **every** bound field held its correct value — real script,
seal and cohort hashes, count 96, and a namespace basename equal to that case's own output directory. Those
payloads were therefore **valid** `V52_T4F1_RUN_AUTHORIZATION_V1` files, which the hard no-outcome boundary
forbids constructing. The script ran as a background job.

As a result, one case ran `--mode run --archive 100K::12` and produced one real archive result, and another
ran `--mode run` over the full list and produced results for 26 archives before I terminated it.

Containment, verified:

- I detected the error while the job was still running and terminated all Python processes immediately.
- Every artifact was written under a system temporary directory, never inside the repository. The directory
  was enumerated **by file name only** and deleted.
- **No retrieval-quality value was read, printed, summarised, or carried into any audit artifact.** The
  runner emits no metric values by design; the harness captured only status lines and block reasons; the
  partial run's own report was never written because the process was killed first.
- The candidate namespace was re-hashed after the incident and is byte-identical to its pre-audit state,
  including the pre-existing `.pyc`. `git status` shows no new repository file other than this audit
  namespace. No candidate byte was changed at any point.
- The script was rewritten with a hard `assert_defective()` invariant that recomputes the runner's required
  field set and refuses to emit any payload the runner would accept. The rewritten 27-case suite is the
  evidence of record; the original is superseded and not included in the outputs.

One incidental structural observation is recorded but **expressly not relied upon**: the partial run
proceeded through 26 archives without triggering the signed-permutation or Haar hard controls. That is an
integrity observation rather than a retrieval-quality value; no gate verdict depends on it, and it is not
offered as evidence for any gate.

Two further superseded probe revisions (A2, A3) are logged in `COMMAND_LOG.txt`. Both were errors in my own
check design — three vacuous or mislabelled flags in the leakage script, and two mathematically wrong
probes in the method script (an orthogonal map preserves inner products under repeated application; ITQ has
converged well before iteration 99). Both were corrected; no candidate byte was involved.

The material audit finding produced by the incident is **D2**.

---

## 8. Remaining conditions before sealing

1. **D1** — remove `__pycache__/` from the candidate namespace and make the closure check recursive. This
   changes `candidate_package_preflight.py` and `PAYLOAD_HASHES.json`, and therefore the seal; the
   implementation bytes need not change.
2. **D2** — bind the Head Researcher's run authorization to a value not derivable from the candidate
   namespace, and/or have the Head Researcher create the output namespace. Preregistration-artifact
   condition; no implementation change required.
3. **D3** — stamp script, cohort and authorization hashes into archive checkpoint metadata. Optional
   hardening; requires an implementation change and therefore a re-audit of the changed bytes if adopted.
4. **C4** — state the trial-row semantics in the Task 4F1 preregistration's reporting section.
5. **Run-time** — verify the `1e-12` Haar tolerance and memory behaviour on the first large archive before
   committing to the full 96-archive sweep (limit 2 above).

If the Head Researcher adopts only D1 and D2 (neither of which touches the implementation bytes), the
implementation as it stands is sealable.

---

## 9. Scope of this verdict

PASS WITH CONDITIONS means: these exact implementation bytes faithfully execute the sealed Task 4F0
restricted-cohort protocol, and they are safe to place before a later, separate preregistration decision.

It does **not** authorize Task 4F1 preregistration, execution, or outcome access. No valid run
authorization was created, and none exists in this audit namespace. The candidate seal was not modified.
