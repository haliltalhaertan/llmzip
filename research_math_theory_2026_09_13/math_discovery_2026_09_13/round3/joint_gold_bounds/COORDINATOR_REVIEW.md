# Coordinator review — joint multi-gold corner theorem

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran verify.py with coordinator_results.json: 4400 cells, zero violations. Reran worker's alternate permutation/codebook implementation: 2478 permutation cells, 19 explicit binary codebooks, zero failures. Both reject the false average-individual-maxima claim. These are worker-authored implementations, not external institutional independence or Lean kernel verification.

The fixed-priority coupling proof is sound for UNWEIGHTED gold count (and fractional recall dividing by fixed positive m). Improving a gold cannot reduce the count of golds in the first K; worsening a nongold cannot reduce it. Combined with product-interval realizability for arbitrary binary codebooks with duplicates allowed, categorywise corners give attained min/max, including multiple golds. Exact bucket evaluation after sorting avoids combinatorial search. The original d=(2,2,0,0), G={0,1}, b=4,s=2,K=3 witness has baseline/min 1/2 and joint max 3/4, not individual-average max 1.

Weighted counterexample is valid: two golds of weights 1 and 2 at a tied top1 yield expected 3/2, while moving the light gold behind gives 2. Nonnegative weights alone do not preserve the categorywise corner argument.

IMPORTANT CORPUS SCOPE: Section 4 claims aggregation is sharp because each question's codebook varies independently. This is an ADDITIONAL assumption, not guaranteed by real benchmarks: questions can share document codes, archives, common transformations and a subset-selection rule. Per-question bounds still aggregate to valid corpus bounds, but simultaneous attainability (corpus sharpness) needs the product-feasibility assumption or a separate proof. Do not transfer sharpness blindly to shared-archive data.

Sharpness here ranges over codebooks compatible with query-distance profiles, not coordinate subsets of an already fixed codebook. Additional structure can tighten feasibility. No benchmark coverage measured, no actual byte storage claim, no literature priority established. Original report retained unchanged with these qualifications.
