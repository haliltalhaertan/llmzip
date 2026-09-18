[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Muse session — D5: ADVERSARIAL DESIGN REVIEW of Round-3 (Deney 1/2/4/5 + verifications)

You are an independent adversarial reviewer (R2D-style). Read the artifacts below and produce a
harsh, specific critique. You may NOT re-run experiments (no writes outside /tmp/d5); you MAY
read any file and check arithmetic/consistency yourself. Report [REVIEW] [READ-ONLY; NOT AUTHORITATIVE].

## Materials (read)

- Deney 1 (multi-split robustness, learned-selection KILL):
  pilots/axis_attack_2026-09-12/round3/DENEY1_REPORT.md + deney1_lme_details.json +
  deney1_loco_details.json + harness/deney1_lme.py + harness/deney1_loco.py
- Deney 2 (tie-mass, c1): round3/muse_sessions/d2/d2_report.md (+d2_details.json, d2.py)
- Deney 4 (fresh-Q): round3/muse_sessions/d4/d4_report.md (+json)
- D1V verification: round3/muse_sessions/d1v/d1v_report.md (+d1v_details.json, d1v_verify.py, d1v_run.log)
- D3 transfer: round3/muse_sessions/d3/d3_report.md (+d3_details.json, d3.py)
- Deney 5 (c2 predictor): round3/muse_sessions/c2/c2_report.md (+c2_details.json, c2.py). NOTE:
  c2's pre-declared gate fires on its letter (LME +3.09pp, LoCoMo +1.48pp @0.20) but the
  vs-random comparison splits (LME above random range; LoCoMo inside it) — review whether the
  "promote with qualification" reading is the right disposition.
- Context: round2/ROUND2_REPORT.md + round2/r2d_design_review.md + round2/r2v_verification.md;
  the roadmap at strategy/roadmap_2026-09-13/muse_strategy_roadmap.md; round2/session_scripts/
  r2b.py, r2a.py, r2c_replicate.py (NOTE correct path — earlier sessions failed to find this
  under 'round2/' top level).
- D1V's declared cannot-check list (6 items) — verify those are real limits, not oversights.

## Checks to attempt (at minimum)

1. **Kill-rule integrity (Deney 1):** re-derive the three triggers from the details JSONs
   (arithmetic!), verify the report's claims match the JSONs (−1.25pp / 2/10 / −0.15pp), verify
   the calibration of the bootstrap (does the "best-of-10 within resample" make the CI fair?),
   and check the SPREAD-vs-random comparisons for the repaired construction (eff_k==k, col
   uniqueness; the report's "no arm beats best random" claim).
2. **D2 honesty:** is the "licenses c2" reading defensible given single learner / n=130 / tie
   exclusion? Are ANY of the 3 model-T features effectively gold-informed (they use gold distance
   — check the report declares them analysis-only)? Does T−M AUC comparison have a hidden
   advantage (feature count, nonlinearity)? What would a skeptic attack first?
3. **D4 scope honesty:** strict-separation claims vs n=2 fresh seeds; the unresolved R2D confound;
   anything overclaimed in the fresh means.
4. **D1V arithmetic (independently spot-check 3 of its exact claims from the raw files).**
5. **D3 reading:** does the report's "favorable/fails" per-cell classification match its numbers?
6. **Cross-artifact consistency:** same numbers quoted differently anywhere? Column sets
   identical across Deney 1 splits vs D2 arms? File hashes present where claimed?
7. **What's missing (list):** analyses that SHOULD have been in this batch but weren't (e.g.,
   multiple comparisons across 10 splits; family-wise error; the "SPREAD ≈ random" construction
   confound; anything about the var-worst exception at s9-k64).

## Deliverables

- /tmp/d5/d5_review.md: numbered findings, each with severity (FAIL / CAVEAT / NOTE), exact
  evidence (file+value), and a required-correction line. End with: (a) list of claims that are
  citation-safe as-is; (b) claims that need corrections; (c) the 3 most important missing
  analyses. Be specific; no generic advice.
- /tmp/d5/d5_details.json: structured version of the findings. Print a compact summary to stdout
  (D5_BEGIN/D5_END markers).
