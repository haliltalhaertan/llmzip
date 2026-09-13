# Coordinator review — second-pass sharp bounds

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran `python3 -B verify.py coordinator_results.json` and `python3 -B check_independent.py`; both exit 0. Counts reproduced: 4432 interval-realization pairs, 6492 K=3 per-gold bound cells, 380 K=1 spot cells, 36 monotonicity cells. Both worker-authored checking programs rejected the stated false joint-attainability variant. These are two implementation paths by the same worker, not institutionally independent auditing or formal kernel verification.

Supported analytic claims: retained distances satisfy L_i=max(0,d_i-r), U_i=min(s,d_i). With arbitrary binary codebooks and duplicates allowed, every product choice of retained distances is realizable with a common query and fixed retained-coordinate set. For ONE gold, uniform tie-breaking expected inclusion has exact worst/best cases at gold=U,rivals=L and gold=L,rivals=U. A fixed-priority coupling is a clean proof of monotonicity; averaging over priorities preserves it. The K=3 example d=(4,0,4,4,4), b=4,r=2 has exact inclusion 1/2, whereas the old lower indicator is zero.

Caveats: sharpness is over all compatible binary codebooks, not over subsets of a fixed observed codebook. Additional structure (distinct vectors, pairwise distances, centering/SVD realizability) can shrink the feasible set. No empirical benchmark coverage or literature priority established.

Multi-gold warning is valid: independent per-gold extrema need not be attainable together; example gives avg individual maxima=1 versus joint=3/4. However the report's suggestion that a DP/flow may be needed for the stated unweighted multi-gold objective is not established. Improving a gold's rank under a fixed tie priority cannot reduce the total number of golds in top-K (it can displace a gold or nongold); similarly worsening a nongold cannot reduce it. This suggests exact joint extrema also occur at categorywise corners (ALL golds low/nongolds high for max, reverse for min). This direct monotonicity extension should be separately formalized/tested before calling the joint optimization open or hard. It does not invalidate the counterexample to averaging individual extrema.

Preserve worker report as originally emitted and read with this note. First-pass T6 quantifier/K limits remain unchanged.
