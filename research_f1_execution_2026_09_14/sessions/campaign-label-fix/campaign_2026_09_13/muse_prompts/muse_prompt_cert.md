# Muse session — CERT: mathematically certifiable losslessness for the compression ladder

You are a mathematical statistician. Question under study: "Can we PROVE losslessness of the
12-byte (and below) compression?" Produce a precise taxonomy of what is provable, design the
certification protocol we can actually execute on frozen data, and write ONE clean
model-conditional lemma with honest proof status. Read-only /mnt/c; write only /tmp/cert/.
No network (flag LIT-CHECK). No paid APIs. [LOCAL EXPLORATORY] [NOT PREREGISTERED].

## Setting (all frozen; read artifacts under /mnt/c/Users/MDP/dev/llmzip-work/)

- Retrieval: sign codes, Hamming, top-3, fractional evidence R@3, 20-trial tie protocol;
  LME-470 (anchor 0.5419751773049645) + LoCoMo-1535 (0.23654714666441054); raw float96 = 384 bytes
  (quality 44.16% LME); native SIGN96 = 12B (54.20%). Sub-ladder: 10B ≈ −2.7pp (LME) / ≈−0.1pp
  (LoCoMo); 8B −5.9 / −1.9; 6B −9.2 / −5.5.
- Validation machinery: math1 (exact conditional-uniform tie model P=f(S,T); per-question
  r≥0.9968; duplicate-spike finding), m1 (no-edge null ≈ −1.62/−1.20pp vs-best), deney1 details
  (per-question arrays; panels), reports under pilots/.../round3/ + prereg_race_2026-09-13/math1/.

## Task 1 — Taxonomy of provability (write this carefully)

For each notion of "lossless", state precisely what CAN be proven and what cannot:
(a) bit-exact reconstruction (info-theoretic; why absolute lower bounds need a distribution model;
    Kolmogorov uncomputability; what IS provable for given finite artifacts — e.g. no-lossy-code
    statements for specific finite sets are decidable but useless);
(b) **quality-equivalence certificates (finite-sample)**: THE actionable one. Design the exact
    statistical procedure to certify, on the frozen benchmarks, statements of the form
    "budget b retains quality within ε of native (or beats float96) with ≥95% one-sided
    confidence", using per-question PAIRED data and minimal assumptions (paired bootstrap /
    permutation / TOST under exchangeability; state the assumptions and their validity here).
    Also: multiplicity across the ladder (12/10/8/6B × 2 benchmarks) — how to keep family-wise
    validity; and the difference between "certify no worse than native" vs "certify within ε".
    COMPUTE, from freshly recomputed per-question data (feasible: a handful of arms × 2 benchmarks
    from the frozen pkls; reuse tie protocol), the ACHIEVABLE ε at 95% for each rung b, per
    benchmark, per construction family (spread/random panels; note LoCoMo BOT nuance). Produce
    example certificate statements with real numbers.
(c) model-conditional theorems: see Task 2.
(d) impossibility ("no ≤b-bit code can...") for the real data: out of reach — write the honest
    map + which toy-model versions are feasible (LIT-CHECK: rank-preservation/quantization
    bounds literature) and what they would/wouldn't imply.

## Task 2 — ONE clean model-conditional lemma (proof attempt)

Using MATH-1's exact identity + spike+bulk histogram parametrization (read math1_report.md),
state the cleanest true theorem you can, e.g.: monotonicity/bounds of E[FR_b] as a function of
profile features (margin distribution, tie-mass, N) under a stated profile class; or an explicit
bound relating b-bit selection to the (S,T) distribution. Provide the proof sketch with every gap
marked (proved / plausible / conjecture). This should be the seed of the future Lean formalization
(statement shape noted; Muse-only cost rule — no prover APIs).

## Outputs

/tmp/cert/cert_report.md + cert_details.json; print CERT_VERDICT: <achievable ε per rung per
benchmark; the lemma statement + status; one-line answer to "can we prove losslessness">.
~2-3 hours scale.
