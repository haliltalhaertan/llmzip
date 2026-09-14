# MUTATIONS.md — Step 4: adversarial mutation testing

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Harness: mutate.py (this directory). Full data (LME 470 queries, PerLTQA 8265),
m=48, using THEIR functions (their_core_copy.py) unless the mutation replaces the
piece. Baseline reproduces the reported m=48 Delta exactly (LME +0.290780,
PerLTQA −9.469667 — VERIFIED).

| # | mutation | LME shift | PerLTQA shift | detected? |
|---|----------|-----------|---------------|-----------|
| M1 | swap TOP/BOT | −14.13 pp | −4.17 pp | YES, loudly |
| M2 | ascending axis sort | −14.13 pp | −4.17 pp | YES, loudly |
| M3 | naive first-K (no tie expectation) | +0.89 pp | +1.48 pp | YES — and informative: tie handling moves Delta ~1 pp, so the exact expectation is load-bearing, correctly so (Step 3c proves it right) |
| M4 | pooled ranking (one global order) | −0.06 pp | −0.12 pp | YES, but barely — per-archive variance profiles are near-identical across archives, so even a pooling leak would shift results only ~0.1 pp. Downgrades the leak scenario to negligible either way |
| M5 | remove nan guard | 0.000000 (NaN cells: 0) | 0.000000 (NaN cells: 0) | NO — passes unnoticed |

## M5 assessment (the one that got away)

M5 is a FINDING but a benign one: combined with the S7 sweep (zero zero-norm
events on all four benchmarks × all nine budgets × TOP/BOT), the guard is proven
dead code on this data, and its mapping (−2.0, below cosine range) is sound for any
data where it could fire. It passes unnoticed because there is nothing to catch.
Recommendation: keep the guard, add a counter/assert so a future dataset with
degenerate norms fails loudly instead of silently ranking rows last.

No mutation revealed a silent wrong-number path: every mutation capable of changing
retrieval semantics moved the reported Delta by an amount far above rounding.
