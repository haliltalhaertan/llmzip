# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# ADVERSARIAL_SPEC — acceptance bar for a repaired rank certifier

Same-model-family adversarial suite (NOT a different-family independent audit).
Target API: a module exposing `certify_pair(p, q, L, R)` with `p, q`
4-tuples of `Fraction`, `L, R` Fractions, returning a dict with keys
`status`, `direction`, `ties` (plus anything else). Statuses understood:
`STRICT | ISOLATED_TIES | PERSISTENT_TIE | VARIES | UNRESOLVED |
DOMAIN_FAIL | EMPTY | INVERTED`. Directions understood: `1 | -1 | 0 |
"VARIES" | None` (None only with non-resolving statuses).

## How to test a candidate (no expectation edits)

```
GATE_UNDER_TEST_PATH=/path/to/candidate.py \
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
PYTHONDONTWRITEBYTECODE=1 python3 -B run_suite.py --out results_v3.json
```

`cases.json` is frozen. Do NOT edit expectations after seeing outputs.
A candidate passes only if the runner exits 0 (safety) AND completeness
passes on all 14 must-resolve cases.

## Safety bar (41/41 must PASS; any FAIL = unsound, reject)

- G1 No false stabilization: a stable `+1`/`-1` claim on a case whose
  frozen exhaustive truth contains both signs is rejected (BULGU-1 rule).
  `VARIES` without both frozen signs is rejected.
- G2 Genuine ties only: every claimed exact tie has independent truth 0
  AND is a Q-root. Unparseable tie entries are rejected.
- G3 Coverage: every frozen interior tie-root is listed exactly or
  strictly inside a valid bracket; endpoint ties are listed exactly;
  no double coverage; `VARIES` needs crossing evidence (cross bracket or
  a listed exact tie with differing side verdicts); a stable claim with
  crossing evidence is rejected.
- G4 Unknown stays unknown: `UNRESOLVED`/`DOMAIN_FAIL`/`EMPTY`/`INVERTED`
  must not carry a `+/-1` direction. `P`-identically-zero admits only
  `PERSISTENT_TIE` (or honest `UNRESOLVED`).
- G5 Robustness: resolving verdicts on inverted-J or failed-domain inputs
  are rejected; degenerate-J (`L==R`) resolving claims must match the
  single-point truth exactly (no interior order may be certified).

## Completeness bar (usefulness, separate from safety)

14 must-resolve cases (POC scale family K=1/10/100/1000, reversed POC,
realizable + abstract tangents, common zero, both endpoint ties,
P-identically-zero, 3 searched classes) must resolve soundly.
`UNRESOLVED` here is sound but incomplete. Robustness (3) and
fuzz-supplemental (24, seed 777001) cases are safety-only.

## What this suite does NOT prove

Finite tests never imply general certification safety. Fuzz rows are
supplemental evidence with exact arithmetic, not absence proofs. Bulk
benchmarks, retrieval/recall, embeddings, and refits are out of scope
(Task4F1 seal). **NOT YET AUDITED V3**: no verdict on any repair exists
until its code actually runs through this suite; the archived-v2 results
below are the baseline, not a repair judgment.

## Baseline: archived v2 (`.../repairs/rank_cert/certify_v2.py`)

- 41 cases: 5 safety FAILs — `poc_K100`, `poc_K1000` (false
  `ISOLATED_TIES/-1` on a VARIES case; BULGU-1 reproduced), mirrored
  `poc_reversed_K100` (false `ISOLATED_TIES/+1`), `invalidJ_empty`
  (`STRICT/0` vs point truth `-1`), `invalidJ_inverted` (silently
  certifies inverted J as `ISOLATED_TIES/-1`).
- 36/41 pass safety, including the honest-budget K=1/K=10 twins,
  both tangents, common-zero VARIES, endpoint ties, persistent,
  strict/two-root searched classes, and all 24 fuzz rows.
- Original conservative certifier returns `UNRESOLVED` on the POC:
  sound unknown, completeness miss. That is the posture to preserve:
  MORE RESOLUTION MUST NEVER MEAN UNSOUND CERTIFICATION.
