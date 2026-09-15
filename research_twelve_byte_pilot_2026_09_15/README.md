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
| pooled hit@10 "73.54 %" | **should not have been computed** — the programme forbids pooling benchmarks, and this pool is 92 % PerLTQA by weight. Read the per-benchmark rows instead. |

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
