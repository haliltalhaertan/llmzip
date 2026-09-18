[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Muse session — AUDIT-1: confound decomposition + tie-convention robustness (independent audit)

You are an independent auditor for the llmzip programme's headline findings. LOCAL only:
read-only /mnt/c; write ONLY /tmp/audit1/; no network; interpreter `$HOME/muse-work/faiss-python`
(numpy/scipy/sklearn). Label outputs [LOCAL AUDIT]. Do NOT modify anything, do NOT run race runners.

## The two suspicions being audited

S1. **"+10pp" confound.** The headline says "native SIGN96 (12B) beats raw float96 (384B) by
   +10.0pp (LME)". But native = **center + sign**. float96's exact frozen definition has never
   been re-derived in this programme; if float96 is the UNcentered float vector, then the +10pp
   is a SUM of (centering gain) + (binarization gain) and the attribution is undocumented.
   → Decompose it.
S2. **Tie-convention sensitivity.** Our eval uses fractional R@3 with 20 random tie draws
   (expected value over tie orders). The race verdicts (LME +1.67pp MID / LoCoMo +0.11pp MID)
   have never been checked against alternative tie conventions. With large tie shares this
   convention could carry the result.
   → Recompute under pessimistic (adversarial) and optimistic tie resolutions.

S3. **Anchor provenance** (small): every anchor number must be traceable to a frozen source.

## Materials

- `llmzip-work/regen/lme/cache_repr/*.pkl` (per-qid; fields include C, qC, gold, hetero — INSPECT
  which fields exist; look for mu or anything enabling Y96 = C96 + mu96).
- `llmzip-work/regen/locomo/*.pkl`, `drive/audit_layer/conv_*.json`, `drive/locomo10.json`.
- Frozen eval protocol: `harness/deney1_lme.py` + `harness/deney1_loco.py` (tie protocol,
  K=3, fractional FR; LoCoMo fallback-qid mapping — mirror EXACTLY, do not rebuild).
- Producer: `drive/v52_t4c3_coordinate_axis_probe.py` (Y96/C96 definitions, buildrep).
- Frozen anchors to reproduce: LME native 0.5419751773049645; LoCoMo native 0.23654714666441054;
  float96 44.16% (LME); ITQ96 37.61% (LME); Haar96 38.27% (LME) / LoCoMo Haar 13.77%.
- Provenance sources: `drive/V52_T4C3_COMPUTE_REPORT.md`, `drive/t4d/V52_T4D_COMPUTE_REPORT.md`,
  `regen/task1_RESULTS_extended.json`, `harness/task1_extend_lme.py`, strategy/roadmap docs.

## Task A — Definition audit (do FIRST; quote file+line)

1. Locate the EXACT frozen definition of "float96" (the 44.16% anchor): which object is ranked
   (Y96 or C96; normalized how), which distance metric, which code computed it. Quote the file
   and line. If it cannot be located, state that explicitly and reconstruct from the extension
   code — quote what you find.
2. Same for native SIGN96 (54.20%): which object, sign of what, metric. And Haar96.
3. Report any ambiguity in one paragraph.

## Task B — Decomposition (LME full 470; LoCoMo full 1535 if feasible, else sampled with n disclosed)

Construct from stored artifacts (via frozen paths only): C96 (stored), mu96 → Y96 = C96 + mu96.
If mu96 is not stored, obtain it via the frozen producer path (lme_regen-style buildrep / T4D
path for LoCoMo); if too heavy, sample qids (≥100 LME) and DISCLOSE.
Evaluate fractional R@3 (K=3, same incumbent tie protocol as deney1) for:
  1. sign(C96) — native; MUST reproduce 0.5419751773049645 / 0.23654714666441054 (≤1e-12).
  2. float(C96) — centered float; metric per Task A's frozen choice (mirror it; if none found
     for C, use the same metric as float96's definition and ALSO report the other of {L2, cosine}).
  3. sign(Y96) — uncentered binary.
  4. float(Y96) — the float96 anchor; MUST reproduce 44.16% (state the precision it reproduces at).
Decomposition table (pp): [float(Y)→float(C)] = centering gain; [float(C)→sign(C)] = binarization
gain; cross-check via [float(Y)→sign(Y)] and [sign(Y)→sign(C)]. State which component carries
the +10pp and with what residual; report all four numbers with n.

## Task C — Tie-convention robustness (bounded arm set)

Arms: {NATIVE(sign C96), SPREAD80, RAND80_s2, BOT80, TOP48} × {LME, LoCoMo} (frozen arm
constructions from deney1; reuse its code paths).
Per question per arm compute from the arm's distance structure: a = #items strictly closer than
gold; t = #items with distance EXACTLY equal to gold's.
Conventions: FR_pess = 1[a+t ≤ 2]; FR_exp = min(1, (3−a)/(t+1)) if a ≤ 2 else 0;
FR_opt = 1[a ≤ 2].
- Validate: the incumbent mc-20 fractional FR ≈ FR_exp; report max |diff| over questions and
  any systematic pattern (state tolerance logic).
- Table: per arm×benchmark FR for {pess, exp, opt}; then the primary contrast SIGN − best
  competitor under EACH convention; conclusion: does the race disposition survive under
  pessimistic ties? Write the decisive numbers verbatim.

## Task D — Anchor provenance (small)

For: native 0.5419751773049645; float96 44.16%; ITQ96 37.61%; Haar96 38.27% / LoCoMo 13.77%;
−15.9pp (LME Haar) and −9.8839pp (LoCoMo). Cite file + line for each definition/derivation in
the frozen materials. Flag any untraceable item explicitly.

## Output

`/tmp/audit1/report.md` + `/tmp/audit1/audit1_details.json` (per-question arrays for Task C).
Every number with n; every gate result; harsh honesty; list everything NOT checkable and why.
End stdout with `AUDIT1_VERDICT:` — S1 decomposition numbers; S2 robustness verdict; S3
traceability; any DIFF/anomaly.
