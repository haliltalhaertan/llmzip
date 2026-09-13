# RACE-1 D1 — Decision memo: RaBitQ 32-dim rule (A4)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Verdict: RATIFIED as proposed** (spread-32 PRIMARY; random-32 SECONDARY sensitivity;
TOP32 curve-point only; same centered C; float query through same reduction; 3-seed
rotation panel). One amendment: recorded non-verification on the cited 4C3 figure (no
bearing on the decision). Two pending items belong to the seal package, not to this rule.

## 1. Ratified rule (literal)

- **PRIMARY:** spread-32 = per-archive variance rank-linspace over the 96 pipeline dims,
  repaired construction (stride-2 cap erratum disclosed; `eff_k==k` assert, logged columns,
  no sentinels), selecting 32 dims fed to RaBitQ32.
- **SECONDARY (sensitivity, excluded from the primary max):** random-32 with frozen axes
  seeds [94201, 94202, 94203].
- **Curve point only (NOT a race member, excluded from all pairwise gates):** TOP32 with
  prespecified anti-optimality expectation.
- **Shared pins:** same archive-centered C as the sign arms (no centering deviation);
  float query through the same 32-dim reduction; rotation panel = 3 frozen seeds
  [94101, 94102, 94103] — a single rotation draw is prohibited.

## 2. Formal rationale note

1. **TOP32 is disqualified by pilot evidence, on both benchmarks.** Recomputed this session
   from the frozen Deney-1 per-question arrays (10 splits, test-FR, k=32 vs best-of-10
   RANDOM32): TOP32(var32) gaps average **-13.24pp (LME)** and **-4.66pp (LoCoMo)** vs
   best-of-10, against SPREAD32 at -1.73pp / -0.79pp (inside seed noise; cf. R2A TOP48
   -12.3pp and R2C BOT-beats-TOP both benchmarks). A construction that loses by ~5-13pp
   to the random band cannot be the primary representative of a codec family under test.
2. **Spread-32 is the deterministic, non-cherry-pickable default.** Spread sits inside the
   random band everywhere measured (spread≈random≈best is the most replicated pilot
   regularity), while fixing one construction removes the fixed-vs-max disadvantage from
   the primary (the disadvantage is instead stated: dual-bar reporting, C2).
3. **Random-32 (3 seeds) bounds axis-choice variance** without spending multiplicity: it is
   sensitivity-only, outside the primary max (multiplicity cap, C10).
4. **Three rotations, not one:** a single rotation is one draw from a high-variance
   distribution (mixing chain: pairing→Cov→width→burial, MATH-1; R2B 3.34pp seed range at
   k=64). The v2 draft cites a 4C3 -15.9pp rotation effect; that exact figure's source was
   NOT re-verified in the round-3 bundle this session — recorded here, immaterial: the
   panel decision follows from the mixing evidence alone.
5. **Centering/query pins** close F1's confound: the founding anomaly (centered SIGN96
   +10pp over float) makes any silent centering change a codec-confound; the float-query
   path keeps the task wrapper identical (§3 fairness sentence intact).

## 3. Erratum vs the HR name `TOP32_RABITQ32`

The HR budget decision (commit 89d3169) names the candidate `TOP32_RABITQ32` as the
"natural candidate". That name predates the R2A/R2C anti-optimality evidence and the D1
pilots; retaining TOP32 as primary would knowingly field the worst selection rule found
(§2.1). **Deviation adopted and flagged for HR sign-off per v2 §8.7/§8.12(a):** primary =
spread-32; the HR-named construction survives only as the TOP32 curve point with a
prespecified directional (anti-optimality) expectation — which doubles as a pipeline
validity check (if TOP32 ever wins, the pipeline is suspect, C2 logic).

## 4. Not decided here (seal package)

Faiss constructor/rotation-source call sequence + S7 acceptance criterion (F2/F5), and the
measured-bytes asserts (RQ32=12B) — required at seal, unchanged by this memo.

*D1: RATIFIED. Basis: DRAFT_PREREG_TWELVE_BYTE_RACE_v2.md §5/A4; recomputation from
`pilots/axis_attack_2026-09-12/round3/deney1_{lme,loco}_details.json` (this session).*
