[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MUTATIONS.md — adversarial mutation testing of the coordinator's own code

Method: `coordinator/f1_competition.py` copied verbatim to `coord_copy/`, then mutated in memory
one change at a time and re-run **end-to-end on the real LME caches (470 queries)** through his own
`query_row` / `benchmark_summary` / `cluster_bootstrap`. A mutation is CAUGHT if the reported
coefficients move by >1e-12 or the code raises.

Baseline through his module: strict `0.1416251737011647`, tie `0.14069387548880735` —
matches my independent numpy implementation at 1e-12. Receipts: `evidence/gate_and_mutations.json`,
`evidence/silent_mutation_followup.json`, logs `evidence/gate_mut.log`.

| # | mutation | effect on reported numbers | result |
|---|---|---|---|
| M1 | swap TOP/BOT (`order[:k],order[-k:]` → reversed) | strict `+0.14163` → `-0.14163` (Δ −2.83e-01) | **CAUGHT** |
| M2 | tie test `==` → `<= dg + 1e-9` | Δ = 0 | equivalent mutant — see below |
| M3 | strict test `<` → `< dg - 1e-9` | Δ = 0 | equivalent mutant — see below |
| M4 | min-gold `min(d[g])` → `d[G[0]]` (first gold, not min) | min-gold rho `0.09920` → `0.02305` (Δ −7.6e-02) | **CAUGHT** |
| M5 | min-gold control aliased to the primary metric (true no-op) | min-gold rho `0.09920` → `0.14163` (= primary) | **CAUGHT** |
| M6 | axis order descending → ascending | strict `+0.14163` → `-0.14163` | **CAUGHT** |
| M7 | average-rank ties → ordinal (first) ranks | strict → `0.13294` (Δ −8.68e-03), tie → `0.10651` (Δ −3.42e-02) | **CAUGHT** |
| M8 | re-center C inside `col_mean_squares` | Δ = 0 | equivalent mutant — see below |
| M9 | gap sign flip (TOP−BOT → BOT−TOP) | strict `+0.14163` → `-0.14163` | **CAUGHT** |
| M10 | bootstrap forced to query level (ignore cluster id) | REALTALK CI `(0.1181, 0.1957)` → `(0.0698, 0.2853)` | **CAUGHT** |

**7 of 10 mutations caught. 3 produced no change — and I investigated all three rather than
reporting them as defects.** Two of the three turned out to be provably equivalent mutants; the
third is equivalent *and* exposes a real inaccuracy in the coordinator's errata.

## M2 / M3 — equivalent mutants, NOT undetected defects

The tolerance I injected cannot change anything because the distances are **exact Python `int`s**:
`f1_competition.py:72-73` builds them with `sum(1 for ...)`. VERIFIED by type check
(`evidence/silent_mutation_followup.json:distances_are_python_ints` → all `int`).
For integers `a, b`: `a < b - 1e-9` ⟺ `a < b`, and (reached only after the `<` branch fails)
`a <= b + 1e-9` ⟺ `a == b`. The mutants are semantically identical to the originals.

This is the **good** outcome for the checklist item "does any decision path use a float tolerance
where exact comparison is required": the answer is no, and the reason it is no is structural
(integer distances), not accidental. A tolerance *cannot* corrupt this code path.

## M8 — equivalent mutant, and it falsifies part of the coordinator's errata

M8 re-centers `C` inside `col_mean_squares`, i.e. on the axis-ranking path only. The cached data is
already centered to ~1e-16, so `v_j` shifts by ~1e-32, the TOP64/BOT64 axis sets are unchanged, and
nothing moves. Equivalent mutant.

So I ran the stronger version — re-centering in the **retrieval arms** themselves, which is the
error ERRATA_COORDINATOR.md describes as "E1. Double centering". Result
(`evidence/silent_mutation_followup.json:recenter_in_arms`, 470 LME queries):

| | LME delta |
|---|---|
| no re-centering (his corrected code) | `+10.053783 pp` |
| re-centered (the E1 error re-introduced) | `+10.053783 pp` |
| change | **`0.000000 pp`** |

**Finding F-6 (LOW, factual correction).** Re-centering already-centered data is a **no-op on this
data**, to 6 decimal places. ERRATA_COORDINATOR.md presents a table attributing the shift
`+9.677305 → +10.053783 pp` to the two errata jointly ("Effect of the two errors"). My measurement
shows erratum **E1 contributes zero**; the entire shift is attributable to erratum **E2** (ALL@3 vs
FR@3). The errata is not *wrong* — both were real coding errors and both were really fixed — but its
effect attribution is misleading, and a reader would conclude double-centering mattered when it
provably did not. Worth a one-line correction.

## Bonus check — the tie-expectation formula, proved exactly (not Monte Carlo)

My first pass compared his `E[FR@K]` formula to a 20 000-sample permutation average and saw
max |diff| = 5.1e-03, which the script labelled "FORMULA MISMATCH". **That label was my own
threshold error** — 5.1e-03 is exactly the Monte Carlo standard error at NT=20 000. I corrected it
by brute force instead of sampling: enumerating **all n! tie-break orders** on five hand-built
boundary cases (3-way tie at the K boundary, tie spanning the boundary with multi-gold, all-tied,
no ties):

| scores | gold | formula | exhaustive all-permutation average | diff |
|---|---|---|---|---|
| `[5,5,5,1,0]` | `[0]` | 1.000000000000 | 1.000000000000 | 0 |
| `[5,4,4,4,0]` | `[1,2]` | 0.666666666667 | 0.666666666667 | 0 |
| `[9,4,4,4,4]` | `[1,4]` | 0.500000000000 | 0.500000000000 | 0 |
| `[3,3,3,3,3]` | `[0,1,2]` | 0.600000000000 | 0.600000000000 | 3.3e-16 |
| `[7,6,5,4,3]` | `[2,3]` | 0.500000000000 | 0.500000000000 | 0 |

**The formula is exactly the NT→∞ limit of the frozen tie rule.** It is mathematically correct and
order-independent, as the coordinator claims. (This vindicates the formula itself; the separate
issue — that substituting it for the NT=20 estimator forfeits the 1e-12 reproduction — stands as
CODE_REVIEW F-3.)

## What mutation testing establishes

The load-bearing logic is genuinely load-bearing: axis ordering, gap direction, per-gold averaging,
average-rank tie handling, the min-gold control, and the bootstrap cluster level **all move the
published numbers when broken**. In particular M5 — making the min-gold control a silent no-op —
is caught loudly (the control collapses onto the primary), so the headline F1 claim "the bug
materially distorts the coefficients" cannot be an artefact of a dead control.

No mutation passed unnoticed that represented a real defect.
