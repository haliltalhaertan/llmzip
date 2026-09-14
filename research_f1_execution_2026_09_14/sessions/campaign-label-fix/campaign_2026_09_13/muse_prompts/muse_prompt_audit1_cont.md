[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Muse session — AUDIT-1 CONTINUATION (tie-convention robustness + provenance; killed-run salvage)

A previous AUDIT-1 session was externally SIGTERM-killed at ~13:50 after completing Task B
(decomposition — its numbers STAND) and a partial Task C. Salvage: `/tmp/audit1/` (also copied
read-only to `/mnt/c/Users/MDP/dev/llmzip-work/audit_2026-09-13/audit1/`). Original brief:
`/mnt/c/Users/MDP/dev/llmzip-work/muse_prompt_audit1.md` (read it).

**SCOPE CORRECTION:** the previous run believed materials were "absent from this checkout" — wrong.
The work area IS available read-only on `/mnt/c/Users/MDP/dev/llmzip-work/` (it is NOT in the repo
clone). Use it:
- `regen/lme/cache_repr/*.pkl` (per-qid C, qC, gold — inspect fields),
- `harness/deney1_lme.py`, `harness/deney1_loco.py` (frozen tie/eval protocol),
- `race_2026-09-13/`: **`rb2/race_sign.py` (frozen arm+tie code — mirror EXACTLY)**,
  `rb2/race_sign_details.json`, `official_run/sign/…`, `rb3/race_faiss.py`, `analysis/ANALYSIS.md`
  (identifies nearest competitor per benchmark), `RACE_REPORT.md`,
- LoCoMo per-archive codes: search `regen/locomo/` and `drive/` (frozen builder
  `drive/v52_t4d_locomo_frozen_cross_benchmark.py`, sha `3f7f091f…`); if a rebuild is needed and
  too heavy, cap to a disclosed subset (≥5 conversations) — never silently.

LOCAL only: read-only /mnt/c; write ONLY `/tmp/audit1/` (new files OK); no network; interpreter
`$HOME/muse-work/faiss-python` or `ml-python` as needed. Labels [LOCAL AUDIT].
End stdout with `AUDIT1_FINAL_VERDICT:`.

## State from killed run (reuse; do not redo Task B)
- `/tmp/audit1/taskB_numbers.json` — Task B DONE: floatY(uncentered) 0.4401063829787234,
  floatC(centered) 0.4415957446808511, signC native 0.5419751773049645 (reproduced exactly),
  centering +0.149pp, binarization +10.038pp, total +10.187pp; W/T/L sign-vs-floatC 122/304/44.
- `/tmp/audit1/taskC_ties.py` + `taskC_synthetic_perq.json` (121 hamming + 60 float synthetic rows:
  tie machinery validated; tie-free exact; mc20≈FR_exp mean diff −0.005 / −0.0012),
  `taskC_real_boundary_ties.json` (2820 rows: SIGN96+ITQ96 boundary stats; SIGN96 boundary tie
  share 0.234, 110/470).

## FINISH THESE
1. **Task C-real (the missing core):** arms {NATIVE(sign C96), SPREAD80, RAND80_s2, BOT80, TOP48}
   × {LME n=470, LoCoMo n=1535}. Per question compute a = #strictly closer than gold, t = #items
   at EXACTLY gold's distance, in the ARM's distance space — mirror `race_sign.py` constructions
   EXACTLY (document column logic + seeds: RAND80_s2 = panel seed 93022 [verify against
   race_sign.py]; SPREAD = repaired rank-linspace eff_k==k; BOT = bottom-k variance; TOP = top-k).
   Conventions: FR_pess = 1[a+t ≤ 2]; FR_exp = min(1,(3−a)/(t+1)) if a≤2 else 0; FR_opt = 1[a≤2].
   VALIDATE: FR_exp ≈ official mc-20 per-q FR arrays (report max|diff|; tie-free questions exact).
   Then the DECISIVE TABLE: SIGN − nearest-competitor gap (compute vs all four; highlight nearest;
   LME's official nearest = SPREAD80, LoCoMo's = BOT80 per ANALYSIS.md) under EACH convention.
   Verdict: does the race disposition (LME +1.67pp MID / LoCoMo +0.11pp MID) survive under
   pessimistic ties? Write the numbers verbatim.
2. **Task D:** provenance file+line for native 0.5419751773049645; float96 CENTERED 0.4415957447
   (note: uncentered complement 0.4401063829 is AUX); ITQ96 37.61%; Haar96 38.27% LME / 13.77%
   LoCoMo; D96 −15.9258 (cross-check `V52_T4C3_COMPUTE_REPORT.md` + t4d). Flag untraceable items.
3. Write `/tmp/audit1/report.md` (cover Task B recap + Task C + Task D) + `audit1_details_final.json`.
   If any exact reconstruction is infeasible, DISCLOSE precisely and give what is computable
   (e.g., from official per-q arrays) — never silently approximate.
