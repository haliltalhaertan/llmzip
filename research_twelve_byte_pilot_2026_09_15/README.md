# Twelve-byte retrieval code — one measurement session

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]**

Date: 2026-09-15 · Benchmarks: LongMemEval, PerLTQA, RealTalk

`main` untouched. No frozen byte edited. No BEAM task run or read. No
retrieval-quality result from the frozen tasks (4C1–4D, 4F1) was produced,
consulted, or reproduced here. Every script self-checks against the frozen
`lib_b8` before reporting: `frac@3` must equal `exact_frac`, `hamming@96`
must equal production `sym`, and every packed-layout variant must be
bit-identical to the frozen scorer on **every** archive, not a sample.

**Start with [`HANDOFF_2026-09-15.md`](HANDOFF_2026-09-15.md).** It is the
narrative; this README is the map and the provenance.

---

## Layout

| path | contents |
|---|---|
| `scripts/` | 17 measurement scripts (`run_*.py`) |
| `results/` | their outputs (`*.json`), one file per script |
| `audit/` | an **independent adversarial audit** of the faiss work — separate code (`audit_*.py`), separate results (`AUDIT_*.json`) |
| `HANDOFF_2026-09-15.md` | what was established, what was retracted, what is open |

The auditor was briefed to break the claims, not confirm them. It re-derived
every number with its own code and did not import `scripts/`. Implementer is
not auditor; that separation is visible in the directory structure on
purpose.

## What this session settled

Five optimization directions are **measured shut** (more bytes; better bit
allocation; different chunk size; more SVD dimensions; compressing the
payload). One works: **deleting bits** — 10 bytes is free on LongMemEval
(−1.11 pp, ns) and not free on the other two. Build cost (4.85 s/archive)
exceeds scoring by 576×–163,000×, so all byte-level work lives in ~0.0002 %
of the compute. Details and confidence intervals in the handoff.

Two findings outrank the rest, both in §6 of the handoff: the "+10 pp SIGN
beats FLOAT" headline is measured against an **unstandardized** float, and
the sign code is **numerically fragile** (±0.5 pp from library or numerical
variation alone), which puts several previously reported effects inside the
noise band.

## Retractions recorded here

This directory publishes its own corrections rather than only its results.

| claim | status |
|---|---|
| "10 bytes is faster as well as smaller" | **withdrawn** — artifact of a uint8 layout; under uint32 both widths are 3 words. RAM win only. |
| faiss speedup "4.25–5.67×" | **withdrawn** — one archive per corpus, same query repeated into a warm cache. Correct value ≈ 3.4×. |
| binary vs float32 "1.3–7.3×" | **withdrawn** — conflated synthetic large-N runs with real archives. |
| binary vs float32 "1.31×" | **withdrawn by the audit** — `reps = min(nq, 60)` timed 50 of 90 archives with a single call. Correct value ≈ 1.51× at N ≈ 500. |
| "median 80 % of a top-10 is forced" | **corrected** — 90 %; the genuinely ambiguous share is 14.7 %, not 23 %. |
| **"the sign code is numerically fragile" (±0.5 pp band)** | **withdrawn — my own seed bug.** The producer seeds LSA32 with 5101 and the final SVD96 with **5204**; every rebuild script here used 5101. Under 5204 the rebuild is **bit-exact** (12/12 archives, `audit/AUDIT_SEED.json`). The consequence drawn from that band — that R8 +0.11, sign88 −0.28 and b8−sign88 +0.90 sit in noise — is withdrawn with it. |
| Gram-SVD quality verdict (+0.21 float / −1.67 sign) | **invalid** — compared the exact path against a non-production randomized draw (seed 5101). Re-run required. |
| "float_std is best or tied-best on every benchmark" | **narrowed** — raw float wins on PerLTQA en_v1 (+1.67) and zh (+4.32). |
| "standardization only hurts on Chinese" | **wrong** — en_v1 shows it too. A PerLTQA property, not a language one. |
| "six conditions" written as seven | **corrected** — 6 conditions over 4 dataset families. |
| "the oracle bounds the value of combining two scorings" | **withdrawn** — it bounds picking one of two finished lists, nothing more. |
| "the char channel carries the Chinese representation" | **withdrawn** — feature counts are not channel contribution; an ablation is owed. |
| "PerLTQA's b8 gain comes from dropping coordinates" (external hypothesis) | **refuted** — dropping hurts monotonically; the gain is the float query. |
| "MHR 2026 / 32 B / Recall@100 = 0.65" as the bar to beat | **unverified** — no primary source found, and cross-corpus recall is not comparable. |
| pooled hit@10 "73.54 %" | **should not have been computed** — the programme forbids pooling benchmarks, and this pool is 92 % PerLTQA by weight. Read the per-benchmark rows instead. |

**Artifacts built with the wrong seed** — `run_bottleneck.py`,
`run_chunksweep.py`, `run_svdopt.py::method_A`, `run_svdvalidate.py` and their
results — are flagged in place rather than deleted or silently re-run, so the
committed results still match the code that produced them. Everything that
reads the frozen caches instead of rebuilding (`run_hit10.py` and the whole
quality table, `run_ksweep`, `run_dropsweep`, `run_codesize`, `run_costfull*`,
`run_faster`, all faiss scripts) is unaffected.

`results/FAISS.json` is kept deliberately although its protocol is flawed and
superseded by `FAISS_DEEP.json`; the record of the wrong measurement is part
of the provenance.

## Large artifacts NOT in git

Per `DATASETS_AND_LARGE_ARTIFACTS.md`, binary payloads stay out of the
review surface. Two data bridges were used to carry exported codes into the
isolated `venv_faiss` environment:

| bridge | files | bytes | manifest SHA256 |
|---|---|---|---|
| `faissdeep/` | 181 | 23,654,989 | `2ea6dd830658b601a22309a3fdf5650a89e6c2c857df0963e496686f469a5d35` |
| `faissdata/` | 20 | 440,662,524 | `610d662090515970763f6b39e7ad4e4354476a730527173db298218e7d607342` |

(Manifest hash = SHA256 over each file's basename followed by its bytes, in
sorted order.)

**Known gap, not yet closed:** no script in this tree generates
`faissdeep/`. It was produced as an undocumented one-off, and it covers only
**50 of 470** LongMemEval archives. That subsampling is the most likely
reason LongMemEval is the one benchmark whose tie-breaking delta disagrees in
sign (−1.00 pp, CI [−3.0, 0.0], n = 50). Writing the exporter and widening
the bridge is open item 3b in the handoff. The audit reconstructed and
verified the bridge independently (`audit/AUDIT_CORRECTNESS.json`,
0/90 byte mismatches), so its provenance is established even though its
generator is not committed.

## Environments

Two, deliberately separated, because the sign code's numerical fragility
makes a dependency change a scientific risk rather than an operational one:

- **frozen** — numpy 2.3.5 / scipy 1.17.0 / scikit-learn 1.8.0, no faiss.
  Reproduces the production pipeline. **Not modified by this session**
  (verified before and after).
- **`venv_faiss`** — faiss 1.15.0 / numpy 2.5.3, isolated. Only the exported
  `.npz` bridges cross between them.

## One result that is a warning, not an improvement

A compiled binary index returns **bit-identical** Hamming distances
(0 mismatches in 4,056,452 cells) yet reports hit@10 **+0.41 pp higher**,
because it breaks ties by ascending document index while the frozen metric
breaks them uniformly at random — and document storage order carries signal
(permutation test, p < 1/60, z = 5.78). It is valid for production and
**invalid for measurement**. Anyone benchmarking with such an index will
report a number that is too high without doing anything visibly wrong.

## Added 2026-09-16

**Six conditions over four dataset families**, not three benchmarks:
LongMemEval, PerLTQA (en_v2 / en_v1 / zh), RealTalk, LoCoMo. Every one runs
through the same scorer, which asserts `frac@3 == lib_b8.exact_frac` on every
query. The PerLTQA releases are **not matched cohorts** (30 archives / 8,265
queries vs 31 / 8,548), so differences between them are not a clean language
or release effect.

Three results worth the reader's attention, each with its limit stated in
[`HANDOFF_2026-09-15.md`](HANDOFF_2026-09-15.md) §12-14:

- **The projector identity `V = Z^T A`** (§13). The same transform, without
  storing the wide projector: zero query sign-bit change on six archives,
  projector 451 MB → 2.2 MB, projection 3.47× faster. Proposed by an external
  reviewer, measured here. Unlike the exact-Gram path in §7, it selects no new
  factorization. But `Z` (46.5 MB sparse) is still needed, the speedup is the
  projection step alone, and the gain belongs to any arm over this
  representation — including float.
- **The PerLTQA outlier is the scorer, not the bits** (§12c). `sign88` is not
  a Hamming arm: it keeps the query in float. Dropping coordinates *hurts*
  monotonically on PerLTQA; it is simply outweighed. The open question is why
  binarising the query costs 4.43 pp there and nothing elsewhere.
- **LoCoMo does not reproduce its own historical anchor** (§12b) on an exactly
  matching query set. Flagged, unexplained, `ANCHOR_MISMATCH` in
  `LOCOMO.json`.

Section 16 of the handoff lists every claim withdrawn or narrowed. Most were
found by an independent auditor or an external reviewer, not by the author.
