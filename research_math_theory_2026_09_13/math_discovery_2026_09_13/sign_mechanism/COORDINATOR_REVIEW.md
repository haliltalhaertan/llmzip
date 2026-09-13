# Coordinator correction — shared-gold dependence

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Original worker REPORT.md/results.json are preserved unchanged for provenance; they are NOT fully approved.

CONFIRMED ERROR: Theorem 2(iii) and the top-3 table use unconditional pairwise win/tie/loss probabilities in a multinomial distribution across distractors. In the stated model all comparisons share the SAME random gold vector. Distractor comparisons are independent conditional on that gold, but generally dependent after marginalizing it. Exchangeability alone does not justify a multinomial distribution. The original verify.py rerun passes because it implements the same incorrect independence assumption.

Correction: enumerate each of four gold nuisance-sign states, compute conditional (closer,tied,farther) probabilities, compute the conditional multinomial top-3 expectation, then average over gold states. See independently written and executed check_conditional_transport.py and conditional_transport_results.json.

Correct exact results for Model H:
- N=6: SIGN 1763/2048; cosine(t=1/2) 4067/4096; cosine(t=10) 1483/2048.
- N=10: SIGN 475849/655360; cosine(t=1/2) 2535999/2621440; cosine(t=10) 36089/65536.
The two directions survive correction: cosine-low > SIGN > cosine-high in both cases. Original numeric top-3 values must not be quoted.

The 16-state PAIRWISE calculation and strict 3D exhibits remain valid as algebraic comparisons of the stated vectors. Their given vectors are assumed already expressed in centered coordinates; a full archive-centering realization was not supplied. No benchmark causal explanation or universal superiority has been established. Independent-sign assumptions were previously rejected as a literal model of LME, so use these as existence/mechanism examples only.

Additional cautions: top-variance failure is a synthetic counterexample, not a scientific priority claim. H1/H3 prose does not consistently align the predicted sign of empirical effects with the toy regimes; these hypotheses need revision before any predeclared empirical use. Avoid claiming the entire probabilistic gap is tie-only in both regimes: the stated equal strict-win mass is specifically the large-nuisance comparison.
