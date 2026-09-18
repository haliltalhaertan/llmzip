# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# CALIBRATION.md — where the real corpora sit in synthetic parameter space.
# Spectrum/shape/N/ngold numbers VERIFIED this session (calibrate.py, calibration.json).
# Real Delta values RELAYED frozen programme headlines. Placement = VERIFIED measurement
# against VERIFIED synthetic grid; directional reading is interpretation, labeled as such.

## 1. Measurements (per-archive variances averaged; locus proxy A_j = mean_q qC_j*goldC_j)
corpus      alpha  top16sh  effrk  kurt  skew   rho_raw  rho_norm  N~    ngold  Delta(RELAYED)
LME          0.89    0.469   48.5  0.98  0.08   +0.980   +0.761   493    1.89   +10.05
REALTALK     0.91    0.497   42.3  0.51  0.08   +0.916   +0.525   894    2.34    +5.30
LoCoMo       0.86    0.463   49.1  0.16  0.03   +0.937   +0.371   588    1.54    +6.66
PerLTQA_all  0.91    0.513   44.8  0.34  0.08   +0.935   +0.643   410    3.96    −6.27
PerLTQA sections (SAME 30 archives, query type differs; Delta RELAYED):
profile      —       —       —     —     —      +0.312   −0.314   —     1.00   +20.36
social       —       —       —     —     —      +0.931   +0.794   —     1.00    −0.78
dialogues    —       —       —     —     —      +0.867   +0.754   —     9.92    −1.50
events       —       —       —     —     —      +0.929   +0.596   —     1.00   −12.39

## 2. Placement verdicts
- SPECTRUM: all four corpora alpha 0.86–0.91, top16 share 0.46–0.51, effrank 42–49 — nearly
  IDENTICAL. Synthetic DIAL A at alpha≈0.9 predicts Delta≈0±2pp. Real Deltas (+10/+5/+6.7/−6.3)
  all lie far outside. VERIFIED mismatch: spectrum explains neither magnitudes nor signs.
- SHAPE: kurt 0.16–0.98, skew ≈0.05. Synthetic DIAL C says shape is inert (|effect|<0.5pp), so
  all corpora sitting at different kurtoses with different Deltas is EXPECTED under the
  generator — consistent with shape being a non-cause (agrees with killed hypothesis #2).
- N (410–894) and ngold (1–9.9): synthetic DIALs D/E say inert — consistent. VERIFIED caveat:
  everything is 3 orders of magnitude below the 100K–10M sealed target; DIAL D only spans 100–5000.
- LOCUS (the interesting one): profile rho_norm=−0.314 (bottom-loaded) with Delta=+20.36 vs
  events rho_norm=+0.596 (top-loaded) with Delta=−12.39 — same archives, and the direction
  MATCHES the synthetic locus dial (bottom→sign wins). Interpretation, not proof.
  BUT LME (+0.761), REALTALK (+0.525), LoCoMo (+0.371) all read top-loaded while sign-POSITIVE —
  naive generator placement predicts Delta≤0 for all three. VERIFIED contradiction with the naive
  locus story. The generator does not place the sign-positive benchmarks correctly.

## 3. Why the proxy cannot rescue the placement (VERIFIED in synthetic, cm_test.py)
The calibration proxy measured on synthetic archives with KNOWN truth: broadband-signal truth +
common-mode background reads rho_raw=+0.908 (mimicking the real +0.9s) with rho_norm=−0.235.
So (a) rho_raw≈+0.9 is MECHANICAL whenever queries resemble golds (E[q_j*g_j] scales with s_j^2)
and carries no locus information; (b) even rho_norm conflates shared background with
discriminative-signal locus. The real top-loaded readings of LME/RT/LoCoMo therefore cannot be
taken at face value — they are compatible with bottom-loaded DISCRIMINATIVE signal hiding under
top-heavy SHARED background. This is a methodological result, not a mechanism: it says the
obvious observational proxy is confounded (a tenth way correlations mislead), which is exactly
why the locus question must be settled by intervention (NEXT_BRIEF.md), not by this table.
