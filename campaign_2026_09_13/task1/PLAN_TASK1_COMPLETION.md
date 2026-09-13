# PLAN — Task1 completion via certified regeneration (local working session, 2026-09-12)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Status: COMPLETE (fix round applied and re-issued; independent closure verification running at
time of writing; nothing pushed).** Every checklist item below is closed except the two final
verification/report lines, which are in progress at the time of this note.

## Why this exists

`ops/CURRENT_STATE.json` → `next_single_action` (after L-095):

> "Recover exact mechanism-track frozen C arrays or source-bound sufficient statistics for
> remaining Task1; no raw corpus reconstruction under current scope."

Task1 of `research/v52/preseal_diagnostics_2026_09_12` (branch `research/v52-preseal-diagnostics-2026-09-12`)
is PARTIAL: for LongMemEval the published `V52_T4C3_native_heterogeneity.csv` (recovered, sha256
`148ae5b7…`) yields D2 (CV of coordinate σ), D3 (top-variance fractions) and the `>=0` sign entropy
D1_ge. Still missing, and deliberately NOT silently substituted (the diagnostics script's own rule
`>=0 is not silently substituted for >0`):

1. **strict `>0` sign entropy** (D1_gt) — needs per-coordinate exact-zero mass of the frozen C matrix;
2. **`zero_mass`** — fraction of exact zeros in the frozen C matrix;
3. **D4** — correlation-matrix statistics (off-diagonal Frobenius ratio, median and p95 of |corr|),
   currently unrecoverable from diagonal variances + aggregates;
4. **LoCoMo side** — the same diagnostic family for the LoCoMo native representation
   ("LoCoMo frozen representation not found").

## Method chosen: certified regeneration of the frozen representation

Exhaustive search first (in progress, parallel):
- all 108 remote git branches (only the synthetic Task3 `.npy` files exist — no C matrices, no pkl);
- Google Drive (comprehensive inventory run in progress; earlier scoped recovery found no full matrix).

Path: the frozen producer `v52_t4c3_coordinate_axis_probe.py` (sha256 `8dce37b1…`, Drive
`1Mvd54Y3LjSbZClrADOHHvVBDifses74o`) constructs each C matrix **deterministically** from:
- canonical dataset `longmemeval_s_cleaned.json` (sha256 `d6f21ea9…`, 277,383,467 bytes, Drive
  `1npoK4DuxR-Gz2zXMVwKpIsfkssZFnghI`) — downloaded and hash-verified locally;
- adapters v1/v2 (byte-exact in git under `adapters/`);
- per-question feature fit + `TruncatedSVD(96, random_state=5204)` + L2 normalize + archive-mean centering.

The harness (`harness/lme_regen.py`) **imports and calls the frozen producer's own `buildrep`**
(not a reimplementation), after a gate that re-checks every hash the producer's own `verify()`
checks — dataset sha+bytes, adapter v1/v2, parent T4C2 script/seal/question-level/aggregate/trial
table, the parent post-run manifest bindings, cohort 500/470, and the two parent aggregate
reproduction values. The only omitted item is the producer's redundant historical chain-text string
check (`'match=29  mismatch=0'`, a relic of a chain file not present in git); all underlying hashes
it covered are checked directly. This omission is disclosed.

**Certification**: the regenerated 470 `hetero` records are compared against the published
`V52_T4C3_native_heterogeneity.csv` down to the last printed digit — every scalar field and both
96-length vectors (variance, `>=0` occupancy). Published vectors are `%.17g` text, which round-trips
float64 exactly, so deviations measure true numerical difference between the original run and this
re-execution. Acceptance: report the exact max deviations; treat the regeneration as
**certified-equivalent** only if all fields agree within ≤1e-12 relative (the programme's own TOL
convention), otherwise investigate before any use.

On success, the missing Task1 components (D1_gt, zero_mass, D4 for all 470 archives) are computed
**from the certified regeneration** with the diagnostics script's own definitions (binary entropy,
`np.corrcoef` on active coordinates, upper-triangle |r| median/p95), and the diagnostics RESULTS.json
is extended additively, clearly labelled: *statistics computed from a certified re-execution of the
frozen producer, not from frozen bytes; certification evidence attached*.

## LoCoMo side (same method, smaller)

Inputs already recovered/verified:
- raw `locomo10.json` — public source `raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json`,
  downloaded, sha256 `79fa87e9…`, 2,805,274 bytes — matches the mechanism-track pinned value;
- audit layer (`conv_*.json` + `errors_conv_*.json`) — recovered from Drive `locomo-audit-main.zip`,
  **20/20 files byte-verified against the T4D pre-run seal**; canonical audit manifest sha
  `90a4e94c…` recomputable;
- frozen producer: `v52_t4d_locomo_frozen_cross_benchmark.py` (extracted from `V52_T4D_ALL_OUTPUTS.zip`);
  representation = same family: mixed96 = [latent32, word, char] → archive-only TruncatedSVD(96,
  random_state=5204) → L2 → archive-mean center; **fit unit = conversation** (10 conversations),
  all Cat1–Cat4 queries share the conversation's fit.

Cross-validation targets for the LoCoMo regeneration: per-conversation feature counts pinned in the
T4D representation transfer proof (e.g. conv_0: word 5704, char 14154, latent 32, mixed_concat 19890,
N 419), frozen native R@3 `0.23654714666441054` present in both the T4D report and mechanism-track
outputs. Provenance memo being produced by a parallel subagent
(`reports/locomo_representation_provenance.md`).

## Governance notes (binding on every step)

- Task 4F1: untouched. SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN. No BEAM paths touched.
- No retrieval metrics are recomputed anywhere: this work touches representation statistics only,
  never top-3 IDs, distances, recalls, or arm outcomes.
- No pushes to GitHub; no writes to Drive; all outputs stay under `C:/Users/MDP/dev/llmzip-work/`
  (plus a local branch of the repo if and when the Head Researcher wants a commit).
- This session is NOT an audit and NOT an independent verification: it is a working session whose
  outputs carry their own certification evidence; the programme's independence rules still require
  a separate cold-start review before any of this is cited as canonical.
- Labels used: `[LOCAL SESSION — CERTIFIED REGENERATION]` for the statistics; raw numbers always
  accompanied by the certification report.

## Status checklist

- [x] Frozen producer recovered + hash-verified (8dce37b1…)
- [x] Canonical dataset recovered + hash-verified (d6f21ea9…)
- [x] Parent T4C2 artifacts hash-verified (script/seal/q/agg/trial all OK)
- [x] Pinned environment built (Python 3.13.15 / NumPy 2.3.5 / SciPy 1.17.0 / sklearn 1.8.0 / pandas 2.2.3)
- [x] Gate PASS via harness
- [x] Full 470-question regeneration
- [x] Certification report vs published CSV (all fields 0.0 deviation)
- [x] Code-level certification: sign codes 470/470 bit-exact; ITQ phase running
- [x] Task1 extension statistics (D1_gt, zero_mass, D4) — LME (dual independent computation, exact agreement)
- [x] LoCoMo regeneration + Task1 statistics — LoCoMo (counts 10/10; dual execution)
- [x] Drive inventory sweep complete (subagent) — finds: NPZ sign codes; no float matrices anywhere
- [x] Local verification receipts (536/536 hashes; 3/3 packages PASS)
- [x] Muse twelve-byte audit complete (10 VERIFIED / C4-mixed / C7-corrections / C10-UNVERIFIABLE)
- [x] Muse independent Task1 computation (bit-equal agreement)
- [x] Muse verification receipts (independent, WSL; corroborates + G3 false-positive adjudicated)
- [x] Muse red-team review of certification (done; all cheap fixes applied + artifacts re-issued:
      NaN-safe certify w/ manifest, adapter sha gates, ITQ aggregate dedupe, LoCoMo vectors, framing)
- [x] Muse cold-start adversarial review (verdict: "supports its substance"; all 5 defects resolved)
- [x] ITQ query-channel certification (`itq_query_packed` 470/470 × 5 seeds; previously uncovered)
- [x] ITQ cross-stack sample (numpy 2.5.3: 50/50 exact) + LoCoMo second-party value re-execution
      (different stack; structural bit-exact, scalars ≤3e-15 abs; C_sha256 cross-stack drift disclosed)
- [x] Nihai hash manifest (HASHES_TASK1.txt, 60 giriş, `sha256sum -c` temiz)
- [x] Muse closure verification of the fix round (**5 PASS / 1 CAVEAT / 0 FAIL**; caveat resolved —
      claim wording corrected + leaf updates self-documented in the artifact)
- [x] Final local report for the Head Researcher (Turkish summary `OZET_TASK1_TR.md`)

## Files

- `harness/lme_regen.py` — gate/prep/run/certify (this plan's implementation)
- `reports/` — subagent reports (drive inventory, LoCoMo provenance, verification receipts)
- `regen/lme/` — items/, cache_repr/ (470 pkls), certification_report.json
- `drive/` — all recovered inputs (hash-verified)
