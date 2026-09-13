# Task1 independent extension — recomputation from regenerated matrices

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Independent session. All quantities computed by importing the frozen programme script
`/mnt/c/Users/MDP/dev/llmzip-work/harness/ref/measure_representation_diagnostics.py`
and calling its `matrix_diagnostics` / `entropy` verbatim per archive (no reimplementation
of the definitions). Summaries across archives use equal archive weight: mean, sample sd
(ddof=1), min, max. The forbidden comparison files were not opened until after these
numbers were computed and saved to `/tmp/task1indep/results.json`.

## Environment

- python 3.14.4, numpy 2.5.3, interpreter `~/muse-work/faiss-python`
- frozen `controls()` status: PASS
- inputs: 470 LME pickles (`.../regen/lme/cache_repr/<qid>.pkl`, N×96 float64, N 396–616);
  10 LoCoMo pickles (`.../regen/locomo/locomo_<i>.pkl`, N = 419, 369, 663, 629, 680, 675, 689, 681, 509, 568)
- all archives: 96/96 coordinates active (variance > 0); D4 valid for 480/480 archives

## LongMemEval (470 archives)

| quantity | mean | sd (ddof=1) | min | max |
|---|---|---|---|---|
| sign_entropy_ge | 0.9970337299075775 | 0.0009689546162983157 | 0.9910369335593018 | 0.9985525937037742 |
| sign_entropy_gt | 0.9970337299075775 | 0.0009689546162983157 | 0.9910369335593018 | 0.9985525937037742 |
| zero_mass | 0.0 | 0.0 | 0.0 | 0.0 |
| cv_sigma | 0.4974774992684583 | 0.008836428595739187 | 0.47551345862128686 | 0.552632578553556 |
| D4 off_mass | 0.15188848165900984 | 0.004794137366943122 | 0.14136795136168004 | 0.18360279501925347 |
| D4 median_abs | 0.004568877386692503 | 0.0005389887508335249 | 0.0032450178521927784 | 0.00647873137859092 |
| D4 p95_abs | 0.01644504773681544 | 0.0023304207234860984 | 0.010925721125563198 | 0.028766378907234855 |
| residual_mean_max_abs | 1.7884038244736246e-16 | 1.1883756002350206e-16 | 2.5679164182262735e-17 | 7.095054637350397e-16 |

## LoCoMo (10 conversations)

| quantity | mean | sd (ddof=1) | min | max |
|---|---|---|---|---|
| sign_entropy_ge | 0.9981814455753918 | 0.0008680842710106539 | 0.9963954013256103 | 0.9988823024676217 |
| sign_entropy_gt | 0.9981814455753918 | 0.0008680842710106539 | 0.9963954013256103 | 0.9988823024676217 |
| zero_mass | 0.0 | 0.0 | 0.0 | 0.0 |
| cv_sigma | 0.48468867201587706 | 0.022868871405231406 | 0.4383418544288973 | 0.5084442294219229 |
| D4 off_mass | 0.1284918632163776 | 0.0033124558926795875 | 0.12410413373959321 | 0.13334246917797715 |
| D4 median_abs | 0.003308774681940944 | 0.00045878520433187484 | 0.0023902879396356354 | 0.003843345382805438 |
| D4 p95_abs | 0.01087587274446762 | 0.0016840365617067483 | 0.007684031768217595 | 0.013267398542722585 |
| residual_mean_max_abs | 1.8559881690794553e-16 | 7.527877973297204e-17 | 8.614978839851016e-17 | 3.601135979678062e-16 |

Notes: `zero_mass` is exactly 0 in all 480 archives (no exact-zero entries in any C), hence
`sign_entropy_ge == sign_entropy_gt` bit-for-bit in every archive. `residual_mean_max_abs`
is at float64 rounding level (~1e-16), consistent with archive-mean centering.

## Synthetic controls (same frozen functions)

- All-zero 4×96: ge = gt = 0, zero_mass = 1, cv_sigma = None, D4 = None, residual = 0.
- Perfect-correlation pair (cols `[-1,0,0,1]`, `[-2,0,0,2]`, rest constant): active = 2,
  off_mass = 0.707106781187 (= 1/sqrt(2) exactly), median = p95 = 1.
- Alternating-rows ±1 (50×96): ge = gt = 1.0, zero_mass = 0.
- Single active coordinate: active = 1, D4 = None (degenerate branch works).
- Column `[-2,0,1,1]` among zero columns: ge ≠ gt contribution visible (0.008451 vs 0.010417
  means), confirming the ge/gt distinction is live when zeros exist.
- Manual cross-check (no `matrix_diagnostics`): first LME archive `001be529.pkl` recomputed
  directly with numpy — ge = 0.998188280130, identical to the frozen-function value; exact
  zero count 0/49344; `(C>0)==(C>=0)` everywhere.

## What this computation cannot detect

It sees only the centered matrices C, so it cannot verify how C was produced (SVD seed,
normalization, centering) nor anything about retrieval, fairness, or semantic importance.

## Post-hoc comparison (computed first, compared after)

- `.../regen/lme/task1_extension_lme.json` and `.csv`: do not exist yet — no comparison possible.
- `.../harness/task1_extend_lme.py`: exists; not executed or imported (independence).
- `.../regen/locomo/task1_locoMo_stats.json`: exists. D1_ge, D1_gt, zero_mass, D2_cv_sigma
  summaries agree bit-for-bit (mean/sd/min/max exact). D4 off_mass/median_abs/p95_abs agree
  to ~1e-17 absolute (last-ulp summation-order differences, e.g. off_mass mean
  0.1284918632163776 vs 0.12849186321637757) — substantively identical, not bit-exact.
  That file has no `residual_mean_max_abs` key, so no comparison for that quantity.

## Deliverable note

Requested write targets `~/muse-work/scratch/task1/` and `~/muse-work/reports/` are
read-only in this session (`touch`/`cp` fail with "Read-only file system"; those dirs hold
other sessions' files). Scratch (`compute.py`, `controls.py`, `results.json`, `report.md`)
is at `/tmp/task1indep/` instead; this report text is the deliverable.
