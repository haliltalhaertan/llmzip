# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# TEST RESULT: controls + cheapest decisive tests of C1 and C2 (both INTERVENTIONS — RAN)

Scripts: [run_tests.py](/home/mdp/muse-work/brainstorm-mechanism/run_tests.py),
[run_se.py](/home/mdp/muse-work/brainstorm-mechanism/run_se.py).
Method: exact-tie-expectation FR@3 (order-independent, noise-free tie handling);
C matrices used as cached (already centered — NOT re-centered); sign = Hamming on
(C≥0)/(qC≥0); float = cosine on raw cached C.

## Controls (must reproduce frozen headlines first)

- LongMemEval (470 queries): SIGN=0.542134 FLOAT=0.441596 **Delta=+10.053783 pp —
exact match to frozen +10.053783 (VERIFIED).**
- PerLTQA sections: profile (n=333) Delta=**+20.355**; events (n=4346) Delta=**−12.394**;
dialogues (n=2742) −1.502; social (n=844) −0.780 — all match frozen values (VERIFIED).

## TEST-M1 (for C1): per-section axis-budget curves, profile vs events

Axes ranked per archive by mean(C²) descending; both arms restricted to same top-m axes.
Delta in pp:

| m | profile | events |
|---|---------|--------|
| 16 | −1.351 | −19.309 |
| 32 | −3.799 | −18.621 |
| 48 | +1.386 | −16.076 |
| 64 | +6.290 | −14.205 |
| 96 | +20.355 | −12.394 |

VERDICT: directional prediction confirmed (profile crosses 32→48 like LME/REALTALK;
events never crosses) — **but both curves rise with m** (profile +21.7, events +6.9
from m16→96). Approximate SEs (sd≈0.4/√n): profile ±2.2 pp, events ±0.6 pp — slopes
and the ~20–33 pp level gap are all far outside noise. C1 claims the shared slope; the
level needs a companion (C3/C6). C1 survives amended, not vindicated.

## TEST-M5 (for C2): margin-clip sweep, cosine → sign, on LongMemEval

Score(t) = Σ_j clip(p_j, ±t), p_j = normalized per-axis products; t=∞ is cosine,
t→0 is Hamming. Mean FR@3:

| t | 1e-6 | 2e-4 | 5e-4 | 1e-3 | 2e-3 | 5e-3 | 1e-2 | ∞ (cos) |
|---|------|------|------|------|------|------|------|---------|
| FR@3 | 0.5473 | 0.5454 | 0.5482 | **0.5626** | 0.5603 | 0.5441 | 0.5285 | 0.4416 |

Sign endpoint: 0.5421. Paired contrasts (n=470): peak−cos = **+12.099 ± 1.594 pp
(t=+7.59, decisive)**; peak−sign = **+2.046 ± 0.975 pp (t=+2.10, suggestive)**;
tiny−sign = +0.514 ± 0.344 pp (t=+1.49, inside noise).

VERDICT: C2's weak form (influence function is load-bearing — clipping alone recovers
*more* than the full sign advantage) is strongly supported. C2's strong form (monotone
improvement down to hard sign) is **rejected**: the optimum is interior (t≈1e-3), and
the peak-over-sign margin is borderline. My own favourite's literal endpoint is beaten
by a softer vote — recorded plainly as required.

## Uncertainty and limits

- Peak-over-sign (+2.05 pp) is t=+2.10: suggestive, needs a held-out benchmark before
anyone cites it (it is also the maximum over 8 thresholds — selection bias; honest
interval would be wider).
- M1 level/slope decomposition is descriptive on the same data that motivated it;
the confirmatory version is C3's synthetic protocol (specified, unrun).
- Nothing here touches N > 1548 (fact G); all claims are three orders of magnitude
below the sealed regime.
