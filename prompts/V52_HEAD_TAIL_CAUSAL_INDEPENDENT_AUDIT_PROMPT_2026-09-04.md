# V52 — HEAD32/TAIL64 CAUSAL RESULT: COLD-START INDEPENDENT AUDIT

You are an **independent, cold-start auditor** of a preregistered causal-mechanism result in the
llmzip V52 program. You did not produce the result, you did not write the preregistration, and you
must not treat any prior chat, commit message, ledger entry, state file, checkpoint prose or
provenance manifest as evidence of anything. They are **claims to be tested**, not findings.

Türkçe cevap verebilirsiniz; kararı İngilizce yazın, kısa Türkçe özet ekleyebilirsiniz.

---

## 1. Why this audit exists

A `[CROSS-BENCHMARK HEAD-TAIL CAUSAL LEAD]` has been reported on two frozen benchmarks. The Head
Researcher has ruled that this result has reached a **load-bearing threshold**: no further experiment
in this line begins until an independent audit closes. Your verdict gates the next preregistration.

The result claims, in substance: rotating the leading 32 spectral coordinates among themselves and
the remaining 64 among themselves preserves most of the native SIGN96 retrieval advantage over
unrestricted Haar mixing, on both benchmarks.

Your job is to decide whether that claim survives independent scrutiny — **not** whether it is
appealing, and **not** whether the arithmetic in the summary files is self-consistent.

---

## 2. Exact audit target — bind to digests, not to branch names

```
repo    https://github.com/haliltalhaertan/llmzip
branch  research/v52-sign-mechanism-locomo-2026-09-04
commit  7799502bc3a157f874b4b1aa76f803ec2bf6432f
```

**The repository default branch does NOT point at `main`.** Fetch branches by name or address commits
directly. Never audit whatever the default branch happens to serve.

Verify each of these yourself before using it. Do not proceed on any item that fails.

| Artifact | Declared identity |
|---|---|
| Head/Tail preregistration | `research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md`, git blob `0d34207be55a75194b585789c7139cbc8aeb264d`, SHA256 `6830c91b01d5df1a87b1a76f25b0101049b47c292c6ea867f48988998aa5ff05`, 6624 bytes |
| Spectral-band preregistration (prior stage) | `research/v52/V52_CAUSAL_SPECTRAL_BAND_HAAR_PREREG_2026-09-04.md`, git blob `02aa91a12b4052bbb2f0a6617167c8851e4f71f7` |
| LoCoMo head/tail summary | `research/v52/locomo_head_tail_outputs/locomo_head_tail_summary.json`, git blob `228f756447e70c73f40b6074a44f13acabdabc08` |
| LongMemEval head/tail summary | `research/v52/longmemeval_head_tail_outputs/longmemeval_head_tail_summary.json`, git blob `86b3718a9af1d6f86a0a3478ad0b83bf6dd0caf8` |
| Cross-benchmark checkpoint | `research/v52/CROSS_BENCHMARK_HEAD_TAIL_CAUSAL_CHECKPOINT_2026-09-04.md`, git blob `9923c5284c04dd9b2acb345dcb7f0c92e4584b06`, SHA256 `9cc773d9153c3dbb6431044e4123c026a15aa6000a7796060590f8e18bc2b9c3`, 5190 bytes |
| Provenance manifest | `research/v52/V52_HEAD_TAIL_CAUSAL_PROVENANCE_MANIFEST_2026-09-04.json` |
| Runners | `research/v52/locomo_head_tail_two_subspace_causal.py` (blob `cb16d4136c6280875b7c5875ffd89f9fc01cb810`), `research/v52/longmemeval_head_tail_shard.py` (blob `184a8a4bbb7d991c875ee1dcb92aa85b5e718074`), and the two `*_spectral_band_haar_causal.py` base modules they import |
| Per-question / per-seed raw outputs | the `*_seed_results.csv`, `*_subset_r3.csv`, `*_pairwise.csv`, `*_hard_negative_rescue.csv` files in both `*_head_tail_outputs/` directories |

---

## 3. What you must establish — each independently, from bytes or from execution

### G1 — Preregistration genuinely preceded outcome access
Do not rely on commit timestamps alone; an author controls those. Establish the ordering
structurally: which commit first introduced the preregistration blob, which commits first introduced
each outputs directory, whether each result file names the preregistration blob it followed, and
whether that named blob is the one actually on the branch. State explicitly whether any result could
have been produced before the preregistration bytes existed.

Note that the Head/Tail preregistration openly declares that the **previous** stage's outcomes were
seen first and generated this hypothesis. Judge whether that disclosure is complete and whether any
Head/Tail-specific quantity leaked backwards into the preregistration.

### G2 — Frozen parameters are actually frozen in the executed code
Bands (`0..31` / `32..95`), seeds (`56001`–`56005`), rotation construction, the order in which the
head and tail matrices are drawn from the RNG stream, top-k, sign threshold, centering step, the
point in the pipeline where the rotation is applied, tie/nuisance semantics, decision bands
(`0.25` / `0.75`) and the cross-benchmark rule. Compare the preregistration text against the runner
source. Report every divergence, however small.

### G3 — Source and cohort identity
Dataset SHA-256s, byte counts, adapter digests, cohort sizes (`470` LongMemEval, `1535` LoCoMo),
and the audit-layer manifest. Confirm these are the accepted frozen sources and not re-derived ones.

### G4 — Re-derive the primary numbers from RAW outputs, not from the summary JSONs
This is the core of the audit. Recomputing `rho_2` from the summary's own `seed_R3` values proves
only that the summary is internally consistent. Go one level lower: rebuild the per-seed R@3 from the
per-question / per-seed CSVs, then rebuild the seed mean, `L_full`, `L_2` and `rho_2` from those.
State whether they reproduce the declared values.

**Additionally, re-run at least one benchmark end-to-end from the committed runner** on the frozen
inputs and report whether you reproduce the declared numbers bit-for-bit. If you cannot obtain the
inputs, say so plainly and mark that gate `NOT ESTABLISHED` rather than passing it on inspection.

### G5 — Does the declared verdict follow mechanically from the preregistered rule?
Check the band assignment and the cross-benchmark rule application. Check that no band, threshold,
seed set or estimand was altered after outcome access. Check the no-rescue/no-tuning list in the
preregistration against what the committed code and outputs actually contain.

### G6 — Statistical honesty of the reported quantity
The primary estimate is a mean over **five** Haar draws. Assess whether the reported precision is
supported by that number of draws: compute the seed dispersion, compare it to the estimated
quantity, and report the per-seed range of `rho_2`. State separately (a) whether the **verdict** is
robust across seeds and (b) whether the **magnitude** is as precise as its presentation suggests.
If any single seed inverts the sign of the estimated loss, say so.

### G7 — Does the intervention establish what the claim says it establishes?
The claim attributes the effect to **spectral position** (leading block vs tail block). Assess
whether the executed design distinguishes that from the alternative that *any* 32/64 block-diagonal
structure would do as well, irrespective of which coordinates fall in which block. Identify which
existing arms bear on this and which control is absent. State what the evidence licenses and what it
does not.

### G8 — Does sharding change semantics?
LongMemEval was executed in 5 shards. Establish whether the shard partition is disjoint and
exhaustive, whether per-question tie-break randomness depends on shard membership or on a
shard-invariant global index, and whether the aggregate is order-independent. A claim of "exact
equivalence" must be demonstrated, not asserted.

### G9 — Leakage, tuning, and independence
Look for outcome-dependent selection anywhere: seed replacement, boundary search, threshold
learning, arm selection after the fact, discarded runs, re-runs not reported. Assess whether the two
benchmarks are independent enough to support the word "cross-benchmark", given that they share the
representation recipe, the estimator, and most of the code. State what "cross-benchmark" is entitled
to mean here.

### G10 — Provenance and reproducibility
Verify the declared git blob ids, SHA-256s and byte counts in the provenance manifest. Assess
whether the recorded CI run/job/artifact identifiers make the result independently re-obtainable, and
whether anything material rests on artifacts you cannot reach.

### G11 — Construct the strongest argument AGAINST the result
Required, not optional. Write the best case that the reported lead is an artifact — of the estimator,
the cohort, the intervention's construction, the seed count, or the interpretation — and then say
whether that case defeats the result, weakens it, or fails.

---

## 4. Absolute prohibitions

- Never invoke any Task 4F1 execution candidate with `--mode run` or `--mode finalize`.
- Never call `run_archives`, `evaluate_archive` or `finalize_results` on real BEAM data.
- Never set `V52_T4F1_AUTH_HMAC_KEY_HEX` or construct a production authorization.
- Never see, compute, write or interpret any Task 4F1 (BEAM) retrieval outcome. Task 4F1 is
  `BLOCKED`; outcome access is `FORBIDDEN`. **LoCoMo and LongMemEval are a different track and are in
  scope; BEAM/4F1 is not.**
- Never modify the sealed preregistration, its seals, any execution candidate, any manifest, the
  pinned corpus, any historical audit namespace, or the research artifacts you are auditing. You
  audit; you do not edit.
- Do not build a generalized prose scanner.

---

## 5. Verdict

Return exactly one:

- `AUDIT PASS — HEAD-TAIL CAUSAL LEAD INDEPENDENTLY SUPPORTED` — every gate established; the lead
  stands at the strength claimed, and the next experiment may proceed.
- `AUDIT PASS WITH CAVEATS` — the lead stands but its wording, precision or scope must be narrowed.
  State the exact narrowed claim you would accept.
- `AUDIT BLOCKED` — at least one gate fails, or a defect materially undermines the result. Name each
  defect with the file and line or the reproduction command.
- `AUDIT INCONCLUSIVE` — you could not obtain what you needed. Say exactly what was missing.

A verdict must distinguish **"established"** from **"not falsified"**. Say which you are reporting.

---

## 6. Output — push it

```
branch  audit/v52-head-tail-causal-independent-2026-09-04
files   audit_v52_head_tail_causal_independent_2026_09_04/AUDIT_REPORT.md
        audit_v52_head_tail_causal_independent_2026_09_04/GATE_TABLE.md
        audit_v52_head_tail_causal_independent_2026_09_04/AUDIT_HASHES.json
        evidence/ and scripts/ for anything you computed or re-ran
        a .sha256 sidecar for the report
```

The report must state: the commit and the digests **you measured yourself**; a gate-by-gate table
G1–G11 with PASS / FAIL / NOT ESTABLISHED and the evidence path for each; your verdict; the exact
claim you would accept; and an explicit outcome-boundary declaration (zero `--mode run`, zero
`--mode finalize`, no authorization constructed, no HMAC key set or inspected, no BEAM retrieval
performed, no Task 4F1 outcome computed, read or reported, nothing modified).

A chat-only reply is recorded as unverifiable and will not close this gate.

An honest `AUDIT BLOCKED` is more valuable to this project than a `PASS` that was easier to write.
