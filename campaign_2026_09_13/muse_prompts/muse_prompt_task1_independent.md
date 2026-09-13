# Muse session — independent recomputation of the missing Task1 statistics (read-only inputs)

You are one of several parallel Muse sessions on this machine. Do not touch other sessions' files.

## Environment

- **No network.** Python: `~/muse-work/faiss-python -c ...` (numpy 2.5.3). Write scratch under
  `~/muse-work/scratch/task1/`; report to `~/muse-work/reports/task1_independent_extension.md`
  (create dirs). Print the report as your final answer too.

## Background (facts, all verifiable locally)

A research programme froze, for each of 470 LongMemEval questions, a per-question centered
96-dim float64 matrix `C` (built from document features via TruncatedSVD(96, seed 5204), L2
normalized, archive-mean centered). Those matrices were previously unavailable; a local session
has now **regenerated them** by re-executing the byte-frozen producer and certified the
regeneration against previously published summary values (all bit-exact). The regenerated
matrices are at:

- LongMemEval: `/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/<question_id>.pkl` — 470 files,
  each a pickle dict with keys `question_id`, `C` (N×96 float64), `qC`, `gold`, `hetero`.
- LoCoMo: `/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_<i>.pkl` (10 conversations) — pickle
  dicts with keys `conv_id`, `C` (N×96 float64), `QC`, `qas`, ...

The frozen diagnostics definition source is
`/mnt/c/Users/MDP/dev/llmzip-work/harness/ref/measure_representation_diagnostics.py` (the
programme's own Task1 script — use ITS functions/definitions verbatim, e.g. `entropy`,
`variance_diagnostics`, `matrix_diagnostics`).

## Your task — compute these FOR EACH archive (470 LME matrices; 10 LoCoMo matrices), independently

Using the frozen script's definitions exactly:

1. `sign_entropy_ge` — mean over the 96 coordinates of the binary entropy (log2) of the
   coordinate's `>=0` occupancy `(C>=0).mean(axis=0)`, handling p ∈ {0,1} as zero entropy.
2. `sign_entropy_gt` — same with strict `(C>0).mean(axis=0)`.
3. `zero_mass` — `(C==0).mean()` over the whole matrix.
4. `cv_sigma` — std(σ)/mean(σ) over coordinates, σ = sqrt(variance per coordinate, ddof=0).
5. `D4` — on coordinates with variance > 0: correlation matrix via `np.corrcoef`; report
   `off_mass = ||offdiag||F/||full||F`, `median_abs` and `p95_abs` (numpy `quantile(..., 0.95,
   method='linear')`) of the upper-triangle absolute correlations. If fewer than 2 active
   coordinates, D4 is null.
6. `residual_mean_max_abs` — `max |column means of C|`.

Then report, for EACH benchmark, summaries across archives (equal archive weight): mean, sample
sd (ddof=1), min, max for each quantity.

## Independence requirement (important)

Before writing your own numbers, do NOT open `/mnt/c/Users/MDP/dev/llmzip-work/harness/task1_extend_lme.py`,
`.../regen/lme/task1_extension_lme.json`, `.../regen/lme/task1_extension_lme.csv`,
`.../regen/locomo/task1_locoMo_stats.json`. Compute first, write your report first; only then, as a
final section, you MAY compare against those files if they exist and note agreement/discrepancy
(if they do not exist yet, say so and stop there).

Report also: environment (python/numpy versions), any controls you ran on synthetic matrices to
show your implementation behaves correctly (e.g. exact zeros, known correlation), and one line on
what your computation cannot detect.
