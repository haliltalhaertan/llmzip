[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — Model-H proxy transfer on LongMemEval (exploratory, NOT audited)

## Outcome
Gate reproduced exactly (5/5 checks, max diff 1.1e-16): native SIGN96 MC-20 mean
0.5419751773049645 (anchor, 470 QA) and centered FLOAT96 MC-20 mean
0.44159574468085105 (stored T4C2 array) with exact seed/index/tie conventions.
Primary endpoint contrast for LOW48 is **negative**: mean[delta(t=4)-delta(t=.25)]
= -0.0644, 95% cluster bootstrap CI [-0.0927,-0.0369] (2000 reps, seed 20260913,
470 single-QA clusters). The interval excludes zero on the negative side, so the
predeclared LOW48-as-nuisance proxy prediction (contrast > 0) is **not supported
— negative result for this proxy transfer**. This does not refute the conditional
Model-H theorem (synthetic signal/nuisance law only); it falsifies only the
LOW48 query-magnitude proxy mapping. Sign invariance held bitwise (0 mismatches)
and is reported as a protocol check, not theory evidence.

## Gate (before interventions)
- native MC-20 vs pilot_results.json: max diff 1.110e-16 PASS
- native MC-20 vs T4C2 sign column: max diff 1.110e-16 PASS
- native MC-20 vs race_sign_details NATIVE96 fr: max diff 0.0 PASS
- float MC-20 vs T4C2 float column: max diff 1.110e-16 PASS
- sign exact expectation vs race NATIVE96 model: max diff 0.0 PASS
- Counts: expected 470, evaluated 470, unresolved 0, excluded 0.
- Exact vs MC at baseline (reported, not gated to each other): sign exact mean
  0.5421335697 vs MC 0.5419751773; float exact 0.4415957447 vs MC 0.4415957447.
- No cross-stack relaxation: Linux numpy 2.5.3 recomputation met the 1e-12 gate
  as-is (diffs are summation-order ulps only).

## Full curve (exact expectation means over 470 QA; sign_exact constant everywhere)
- LOW48: t=.25 delta +0.116850; t=.5 +0.109226; t=1 +0.100538; t=2 +0.069509; t=4 +0.052417.
- HIGH48: exact mirror (t=.25 +0.052417 ... t=4 +0.116850) — mathematically required,
  since LOW48@t and HIGH48@1/t coincide up to a global positive scale.
- FULL96: delta +0.100538 at all t (bitwise cosine invariance; all t are powers of 2,
  so scaling is exact in binary floating point).
- MC-20 sensitivity at t in {.25,1,4} tracks exact within ~2e-4 (e.g. LOW48@t4 float
  exact 0.489716 vs MC 0.4897163121); t=1 MC reproduces the gate arrays bitwise.

## Monotonicity and controls
- Fraction of QAs with any decreasing adjacent delta: LOW48 114/470 (0.2426),
  HIGH48 66/470 (0.1404), FULL96 0/470. Pointwise Model-H monotonicity does not
  transfer unconditionally.
- HIGH48 contrast +0.0644 CI [+0.0369,+0.0927] is the predeclared comparison, not a
  rescued hypothesis: groups were never redefined after seeing outcomes.
- t=1 identity bitwise (maxdiff 0.0); sign byte-identical for all positive t
  (0 mismatches over 7050 configs); FULL96@t4 cosine scores bitwise identical
  (maxabsdiff 0.0, 0 changed QAs).

## Diagnostics stored per row
qconc = sum q^4/(sum q^2)^2 and doc RMS(group)/RMS(complement) on original C are in
per_query.jsonl/csv (7050 rows); group indices in groups.json. Association of these
diagnostics with intervention behavior was not tested and must not be read as an
explanation of any reversal.

## Verification
verification.py: 45 gate/artifact checks + 24 manual outcome recomputes (3
representative QAs × {sign,float exact+MC at baseline, LOW48@t4 sign/float/signMC}
via sorted()-tuple code path) + full groups.json rule recompute + sign/FULL96
constancy over all 470 + bootstrap reproduction — all PASS (see
receipts/verification.log). Source hashes re-taken after the run; sources unchanged.

## Artifacts (workspace only)
run_lme.py, PRE_RUN.json, PLAN.md (+sha256), gate.json, per_query.jsonl/csv (7050),
groups.json, summary.json, verification.py, REPORT.md, STATUS.md,
receipts/{run.log,verification.log}, checkpoints/{pkl_manifest.json,ckpt_*.json}.
No push, no model/API calls, no embeddings, no installs.
