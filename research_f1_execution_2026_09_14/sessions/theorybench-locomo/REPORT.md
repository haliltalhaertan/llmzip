# LoCoMo Model-H proxy-transfer test — REPORT

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Verdict: NEGATIVE for this proxy/transfer; theorem untouched

Primary (sealed): LOW48 endpoint contrast mean[delta(t=4)-delta(t=.25)],
delta = sign minus float, exact tie-expectation, 1535 valid QAs:

    contrast = -0.025829067783465175, 95% cluster CI [-0.03776758909603851, -0.013132051635781277]

The interval excludes zero on the NEGATIVE side: amplifying low-|q| coords
helps float relative to sign (delta falls). The sealed rule requires > 0 for
"consistent with proxy transfer". Result: negative. Per the shared plan this
falsifies the LOW48-proxy transfer, NOT the conditional Model-H theorem
(theoretical t is unidentified on real data; LOW48 is query magnitude, not a
proven nuisance subspace). No post-hoc redefinition of groups.

## Gate (before intervention): PASS, all 1e-12

    sign MC mean  0.23654714666441054  (anchor diff 0.0)
    sign exp mean 0.2369591212262222   (matches audit perq NATIVE96 exp)
    per-QA MC vs deney1_loco_peraxis.npz native: maxabs 1.11e-16
    per-QA exp vs taskC_LoCoMo_perq NATIVE96 exp: maxabs 0.0
    per-QA MC vs official race fr_off: bitwise 0.0
    counts: Cat1-4 1540, valid 1535, excluded 5, archives 10 (recounted by code)
    cats valid: 1:282 2:320 3:92 4:841; golds: 1103 single / 432 multi

No frozen LoCoMo centered-float96 arrays exist in scope (sign-only artifacts;
empty *float*/*cos* filename search), so the float baseline is a sealed FRESH
measurement, not a gated anchor:

    float baseline R@3: exp 0.16826334541318252, MC 0.16826334541318252
    max|float MC - exact| 2.2e-16: effectively zero float ties, so MC == exact
    throughout (contrasts/curves identical to ~1e-16).

## Intervention curves (means over 1535 QAs; exact; MC same)

    LOW48  delta: t.25 0.076780  t.5 0.075803  t1 0.068696  t2 0.057106  t4 0.050951 (falls)
    HIGH48 delta: t.25 0.050951  t.5 0.057106  t1 0.068696  t2 0.075803  t4 0.076780 (rises)
    FULL96 delta: flat 0.068696; sign flat 0.236959; float flat 0.168263
    LOW48 float: 0.160179 0.161156 0.168263 0.179853 0.186008 (rises with t)
    HIGH48 float: mirror image. Sign is t-invariant by construction (verify, not evidence).

Structural identity (not empirical support): LOW48(t) == HIGH48(1/t) exactly,
because (t*L,H) = t*(L,H/t) and cosine is globally scale-invariant. Hence the
HIGH48 contrast +0.025829067783465175, CI [0.013806961403717179,
0.038355008092817805] is the entailed mirror of the primary, not independent
confirmation. HIGH48 was a predeclared comparison, never a guaranteed control.

Pointwise monotonicity violations (any decreasing adjacent delta, exact):
LOW48 151/1535 (9.84%), HIGH48 101/1535 (6.58%), FULL96 0/1535.
Model-H pointwise monotonicity does not transfer unconditionally.

Controls: sign distances byte-identical across all t (maxdiff 0.0 — tautology of
positive scaling, recorded not celebrated); FULL96 float bitwise 0.0 (t grid is
all powers of two, so fp scaling is exact); t=1 restores all scores bitwise
(maxabs 0.0 everywhere).

Uncertainty: archive-cluster bootstrap, B=2000, seed 20260913, question-weighted;
only 10 clusters so intervals are coarse — raw effects reported alongside.
No pooling, no familywise claims (1 of 4 benchmark comparisons).

Diagnostics (neither is Model-H true t): query concentration
sum q^4/(sum q^2)^2 mean 0.0839 (min 0.0354, max 0.4851); doc RMS low/high
0.0763/0.1126, ratio mean 0.68.

## Artifacts (this workspace only; sources read-only, unchanged)

run_locomo.py, gate.json, gate_native_arrays.npz, PRE_RUN.json, per_query.jsonl
(1535 rows), summary.json, verification.py, REPORT.md, STATUS.md,
receipt_gate/intervene/bootstrap/verify.txt, ckpt/ (10 archive checkpoints).

    verification.py: CHECKS total=33 pass=33 fail=0 (gate 5, counts/schema 8,
    identity+invariance 6, pipeline consistency 5, groups 1, manual spot-QA
    recompute 7 incl. brute-force permutation tie-law check, hashes 3).
    source pkl/producer/PLAN hashes after == before.

Provisional until separate recompute + adversarial review. No training,
embeddings, API calls, network, installs, or pushes. Threads=1 env throughout.
