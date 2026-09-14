[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Dense MRL channel — spectral geometry parity, and why the front closes

Additive research directory. `main` is untouched at
`5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`; nothing here is merged, no frozen
artifact is rewritten, the continuity ledger and `ops/CURRENT_STATE.json` are
not modified.

## The question

Would splitting the 96-bit (12-byte) budget as 48 lexical + 48 dense beat
96 lexical? That requires the dense model's **first 48 nominal coordinates** to
carry enough variance — which only MRL-trained models are built to do.

## Status — read this before using anything here

| item | audit verdict | usable? |
|---|---|---|
| `measurement/` (three arms + report) | **FAIL-FIXABLE → repaired** | Yes, within stated scope |
| the closing verdict itself | `VALID` (numerically sound) | Yes |
| the "alignment" metric | **withdrawn** | **No. Confounded — see report §6b** |

### The verdict

**The dense channel fails all three pre-declared thresholds. The front closes.**

Same axis fraction (1/8), the apples-to-apples comparison:

```
                                f nominal   isotropic null   enrichment
lexical SIGN96  f_12  (12/96)     35.66%        12.50%         2.85x
arctic-m-v1.5   f_96  (96/768)    20.65%        12.49%         1.65x
mxbai-large     f_128 (128/1024)  12.60%        12.49%         1.01x
arctic-xs       f_48  (48/384)    12.10%        12.51%         0.97x   (control)
```

The 48-bit budget question, best arm: `f_48 = 10.61%` against a lowest
threshold of `17.83%`. Margin 7.2 pp. No threshold was moved after the number
was seen.

The verdict survives the most generous possible framing for the dense side
(lexical nominal vs dense **sorted**, report §11): best dense arm 24.36%
against lexical 35.66%.

### Why it is not MRL's fault

`arctic-m-v1.5` does show real nominal-axis ordering: `p_B nominal = +0.3292`
against `−0.0169` for the non-MRL control, and `f_48` enrichment 1.70× against
0.97×. MRL training does what it promises. The underlying spectrum is simply
not concentrated enough: `p_B = 0.329` against the lexical side's `0.861`.

## Layout

```
measurement/
  measure_mrl_parity.py      the measurement (parity with the frozen script)
  MRL_PARITY_*.json          three arms, raw per-archive output
  OLCUM_RAPORU_TR.md         the report (Turkish) — READ THIS FIRST
  null_baseline.py, null2.py isotropic null baselines
  trunc_sensitivity.py       truncation sensitivity, design 1 (confounded)
  verify_trunc256.py         truncation sensitivity, design 2 (clean)
  verify_muse.py             independent verification of the audit findings
audit/
  muse-task-v55.md           the adversarial brief (13 numbered claims)
  MUSE_DENETIM_V55.md        the auditor's report
reference/
  bug_loader.py, det_test.py demonstrations of defects in an external proposal
```

## Parity with the frozen measurement

`loglog_fit` and `archive_texts_only` were **copied verbatim** from
`measure_spectrum.py` (the frozen lexical measurement). Same 15 archives in the
frozen `V52_T4C2_feature_geometry.csv` order, same text construction, same
pipeline (row L2 → center → `np.var(C, axis=0)`, ddof=0), same exponent
convention (`p = -slope`, no division). The `N_archive` gate passed on every
archive in every arm.

## Independent audit

Muse Code (`muse-spark-1.3`, `xhigh`), read-only, cold start, adversarial brief
of 13 numbered claims. Verdict **`FAIL-FIXABLE`**: the closing verdict is
numerically sound, three real text/metric defects. All four findings were
independently reproduced before acceptance; no finding was invented.

| finding | verified | repair |
|---|---|---|
| "alignment" metric confounded (null baseline is 87.8–90.4%, all three observations below it) | yes | argument withdrawn, §6b |
| the 0.005 pp scope justification does not reproduce (real: ~0.04 pp) | yes | corrected, §4 |
| ~17% truncation asymmetry undisclosed | yes | added, §9 |
| `matryoshka_dimensions` config evidence | yes | added to §7a — strengthens the report |

The auditor also supplied a cleaner truncation design (same texts, 512 vs 256)
that removes the selection confound in ours; its numbers reproduced digit for
digit (`+0.0500 pp`, `−0.0067 pp`).

**Independence limit.** Auditor and measurer are from the same model family.
Cold start and an adversarial brief were used, but this is **partial
independence, not full independence.**

## What this does NOT say

**Variance share is not retrieval.** What was measured is how much of the
representation's variance survives truncation. Retrieval quality depends on
whether *discriminative* information survives, and that was not measured — it
is inside the sealed Task4F1 boundary.

The correct record: **a pre-declared proxy criterion was not met.** The hybrid
architecture was not proven useless for retrieval.

## Boundary compliance

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS
FORBIDDEN`. Only `haystack_sessions`, `haystack_dates` and
`haystack_session_ids` were read; `answer`, `answer_session_ids`, `question`
and `question_type` were never touched. No recall, accuracy, ranking
correctness or benchmark was computed. Verified by the auditor (claim İ-11).

Measurements are a **declared re-fit**: the frozen production artifact's
physical serialisation was never located.
