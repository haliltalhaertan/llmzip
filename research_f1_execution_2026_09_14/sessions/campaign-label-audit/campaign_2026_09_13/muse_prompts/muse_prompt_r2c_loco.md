# Muse session — R2C: LoCoMo replication of the axis-attack findings

Fresh independent executor. Read-only for /mnt/c; scratch /tmp/r2c/. No network.
Python with numpy (and sklearn if needed): `~/muse-work/ml-python`
(python 3.14.4, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1).

## Context

An exploratory pilot on the frozen LongMemEval benchmark found: (a) bit-budget curves for the
native SIGN96 code under several selection strategies; (b) top-variance selection is much worse
than random/spread; (c) coordinate-mixing damage is monotone in variance disparity. Your job:
**replicate the core findings on the frozen LoCoMo benchmark** using the frozen Task-4D evaluation
protocol, exactly.

## Inputs (all under /mnt/c/Users/MDP/dev/llmzip-work)

- **frozen T4D producer** (source of truth for the eval protocol): `drive/v52_t4d_locomo_frozen_cross_benchmark.py`
  — study its `topks_by_hamming`, `retrieval_metrics` (audit-clean fractional), `evidence_rows`,
  `load_audit_corrections`, priority/trial scheme, and which questions are included (Cat1–4 and the
  156 audit corrections).
- raw: `drive/locomo10.json` (sha256 starts `79fa87e9…`, 2,805,274 bytes)
- audit layer: `drive/audit_layer/` (20 files; manifest sha starts `90a4e94c…`)
- **our regenerated matrices** (already verified: counts 10/10 vs the frozen transfer proof):
  `regen/locomo/locomo_0.pkl` … `locomo_9.pkl` — keys: `conv_id`, `C` (N,96) float64,
  `QC` (nQ,96) float64, `qas` (list), `id_to_row` (dict), `C_sha256`.
  Inspect `qas` to map questions → evidence ids → rows (the frozen script does this via
  `evidence_rows(ids, id_to_row)`).
- **frozen anchors** (accepted T4D checkpoint): Native SIGN96 Fractional Evidence Recall@3 =
  `0.23654714666441054`; Full-Haar96 mean = `0.13770827054136`.

## Task

1. **Reconstruct the exact evaluation protocol from the T4D script** and mirror it verbatim on our
   `C`/`QC` (do NOT re-fit representations; use the pkls). Include: distance definition, priority
   scheme + trial count (mirror `stable_archive_seed`-based trials as the script defines), K=3,
   audit-clean corrections handling, and the question inclusion rule.
2. **GATE:** reproduce Native fractional R@3 = `0.23654714666441054` EXACTLY (report the diff; if
   > 1e-12, debug against the script until it matches — the matrices and inputs are certified).
   If feasible, also reproduce Full-Haar96 mean = `0.13770827054136` (the script has `hspec`/
   `happly`; use its rotation seeds).
3. **Arms** (gold-free selection; same protocol; per conversation where the arm is per-archive):
   - for k in {16, 32, 48, 64, 80}: `TOP` = top-k variance axes; `RANDOM` = 3 seeds
     (`default_rng(12000+s).choice(96,k,replace=False)`, s=0,1,2); `BOT` = bottom-k; `SPREAD` =
     rank-stride-2 subset (`argsort(var)` then `[::-1][::2][:k]`).
   - block-2 pairing contrast at 96 bits: `RANDOM pairing`, `MATCHED-variance pairing`, and
     `ANTIMATCHED` (i-th highest with i-th lowest variance) — 3 seeds; construction identical to
     the T4D block machinery (same rng draw order, perm + per-block QR + sign fix), only the
     pairing order differs.
   - Report Fractional R@3 per arm + gap vs native (pp). If cheap, also a per-category (1–4)
     native-vs-best breakdown.
4. **Outputs:** print the gate diffs, the full arm table (with per-seed values where seeded), the
   per-category breakdown if computed, and a final JSON block with every number. Save details to
   `/tmp/r2c/details.json` and print its size.

Honesty rules: state any deviation from the frozen protocol you had to make; if the gate cannot be
reproduced, report exactly where it breaks with numbers (that is itself a finding). No writes under
/mnt/c; do not modify the pkls or inputs.