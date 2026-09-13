# STATUS — math-bit-allocation pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Workspace: `/home/mdp/muse-work/math-bit-allocation` (only writable workspace).
Sources elsewhere (e.g. `/mnt/c/Users/MDP/dev/llmzip-work`) are READ ONLY.
No Git push, no main changes, no paid APIs, no web fetch, no package installs,
no frozen benchmark/Task4F1 runs. Muse subscription tools only.

## Checkpoint 2026-09-13 ~20:05 UTC — priors read, plan fixed

Read (relevant parts, not giant raw datasets):
- `review_transfer/PROMPT_EXTERNAL_LLM_2026-09-13.md` (protocol, anchors, governance)
- `race_2026-09-13/cert/cert_report.md` (certificate table; model-conditional lemma
  with MATH-1 exact tie identity `E[FR]=(1/m)Σf(S,T)`; JL→retrieval transfer = category error)
- `audit_2026-09-13/audit1_cont/report.md` (frozen tie protocol: Hamming on sign(C)/sign(qC),
  `5_100_000+key*100_000+t*100+99` priorities, K=3, NT=20; centering confound DEAD:
  centering +0.149pp, binarization +10.038pp — will NOT be resurrected)
- `bench3/runs/b3b_fin/{report.md,summary.json}` (PerLTQA reversal −6.275pp verified genuine;
  profile section BOT64 inversion: discriminative signal can live in LOW-variance coords)
- `lit_scan_2026-09-13/{LITERATUR_TARAMASI.md,sources/coordinate_heterogeneity_2605.17524.md}`
  (heterogeneity paper: Prop 5 magnitude-bit gain grows with heterogeneity; Cor 3 rotation
  kills it; F/G decomposition with sub-Gaussian pairwise bound + union bound over K(N−K))
- `pilots/axis_attack_2026-09-12/round3/ROUND3_REPORT.md` (learned selection KILLED;
  adaptive routing CLOSED; tie-mass AUC 0.798 mechanism, gold-informed; utilities local)
- `prereg_race_2026-09-13/math1/math1_report.md` (Level-1 exact model REUSED as background,
  not re-proven; independence plug-in fails sign of TOP48 effect — my toy independence
  assumption is therefore KNOWN-FALSE on real data, stated explicitly as toy scope)
- `prereg_race_2026-09-13/math2/math2_report.md` (S-recommendations; T3 trap; S3 max-bound)

## Plan (bounded first pass)

Model M-IND: finite independent-coordinate toy, fixed full-precision query (asymmetric
scoring, cf. lit-scan §3 sign-full-RP direction — explicit DELTA from frozen symmetric
protocol), estimated inner-product scoring, random-tie-break 1/2 convention, payload
budget + separately-charged threshold metadata. Exact pairwise ranking error by
exhaustive rational enumeration (stdlib `fractions`), NOT MSE.

- THEOREM E (exact pairwise-error formula, finite sums proof).
- THEOREM D (divergence): Setup A (d=2, budget 2) — unweighted-MSE-optimal allocation
  (2+0 concentrate on high-variance coord) vs ranking-optimal (1+1 spread); exact numbers.
  This is the COUNTEREXAMPLE to 'always allocate to highest variance'.
- Gain regime: Setup B (d=3, budget 3) — (2,1,0) beats (1,1,1) for ranking (heterogeneity
  gain direction, consistent with Prop 5 intuition, but ranking-error not fidelity).
- Marginal-value criterion MV + swap value; surrogate named: query-weighted MSE
  S(b)=Σq²e and pair-sum union-bound proxy. Greedy-MV limits marked open, not claimed.
- verify.py (stdlib) → results.json; REPORT.md self-contained; one falsifiable E2 spec.

## Progress

- [x] Priors read; STATUS checkpoint written early
- [x] verify.py written + executed: ALL_PASS = True, 9/9, exit 0 (stdlib only)
- [x] results.json produced by verify.py run (valid JSON, all_pass true)
- [x] REPORT.md written (THEOREM D/E, counterexample, gain+loss regimes,
  MV/SV criterion + named surrogates, metadata accounting, F1-F3 failures,
  E2-RANK falsifiable spec, not-proven list)
- [x] Independent corroboration: separate seed-fixed Monte Carlo (/tmp scratch,
  n=400k) matches exact fractions 1/14, 2/7, 3/14 to <=5e-4

## Result in one line

Useful result (not negative): exact paired gain/loss regimes + counterexample
to highest-variance allocation + computable MV criterion, all machine-checked.
Nothing universal claimed; E2-RANK spec unfalsified-until-run.

## What is NOT being done

No benchmark recomputation, no frozen-artifact replacement, no learned/adaptive routing
revival, no JL-based lower-bound claims, no literature priority claims, no Lean.
All synthetic examples marked SYNTHETIC, never benchmark output.
