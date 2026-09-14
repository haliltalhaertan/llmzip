# Muse session — D3: cross-benchmark utility transfer matrix (LME ⇄ LoCoMo)

You are an independent analyst. Implement + run in /tmp/d3/; report [LOCAL EXPLORATORY]
[NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]. Read-only on /mnt/c; no network.
Numpy only. This is informational for the roadmap: is the axis-utility structure shared between
benchmarks, or benchmark-local?

## Materials & protocol

- LME per-axis: pilots/axis_attack_2026-09-12/per_axis_matrices.npz — 'drop'(470x96)=FR with axis
  removed, 'alone'(470x96), 'delta'(470x96), 'var_rank'(470x96), 'qids'. Native per-q FRs:
  pilots/axis_attack_2026-09-12/pilot_results.json['per_question_native_FR'].
  Eval machinery: follow round2/session_scripts/r2b.py `fr_subset` EXACTLY (lex-ordinal
  priorities 5_100_000+lx*100_000+t*100+99, 20 trials, top-3, fractional).
- LoCoMo per-axis: pilots/axis_attack_2026-09-12/round3/deney1_loco_peraxis.npz — 'native',
  'drop', 'alone', 'pool', 'var_rank', 'qids' (1535 valid). Eval machinery: follow
  round2/session_scripts/r2c_replicate.py (stable_archive_seed(ci,t)+99, top-3, 20 trials,
  audit corrections; valid=1535; native anchor 0.23654714666441054).
- Both benchmarks' utilities here are FULL-DATA (gold-informed; declared). Transfer analysis only.

## Steps

1. GATES first: reproduce LME native mean = 0.5419751773049645 and LoCoMo native mean =
   0.23654714666441054 with YOUR OWN evaluators (recompute from pkls), tolerance 1e-12. Abort
   if fail.
2. Utility vectors (96,): for each benchmark: U_drop = mean(native − drop); U_alone =
   mean(alone*pool/3) (LME: pool computed from pkls as count of agreeing docs; LoCoMo: from npz
   'pool'); U_var = mean(−var_rank). (No delta for LoCoMo.)
3. Structure comparison: Spearman rank correlation between LME and LoCoMo utilities (drop,
   alone, var); top-k set overlaps (Jaccard + raw intersection count) for k in {32,48,64}.
4. Transfer arms: source utility → top-k cols → evaluate on the TARGET benchmark full set
   (LME→LoCoMo and LoCoMo→LME; k in {32,48,64}; families drop/alone/var). Comparators
   evaluated on the same target: NATIVE, target's own-utility arm (same family/k), RANDOM
   panels (10 seeds, formula 91000+10*0+j reused across (all sets), same construction as
   deney1 scripts), and the repaired SPREAD_k (rank-linspace over target's own U_var ordering).
5. Report per (family,k): target-native, source→target value, target-own value, random panel
   mean/best, spread value; gaps in pp. Pre-declared reading (no kill/promote): "transfers
   favorably" if source→target >= min(target-own, random-best) − 1.0pp; "fails" if within
   ±1.0pp of random-mean or below; state honestly which.
6. Also LME→LoCoMo → LME circuity check: are the two transfer directions symmetric in
   correlational structure? (report; no claim)

## Output

/tmp/d3/d3_report.md + /tmp/d3/d3_details.json; stdout ends with D3_VERDICT: <one-line summary:
share of (family,k) cells that transfer favorably vs fail; notable asymmetries>. Full tables in
the report. State confidence labels. ~1-2 hours scale.
