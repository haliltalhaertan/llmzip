# Coordinator review — theorem/intervention mapping audit

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Worker verify.py rerun:87/87 pass. Coordinator independently recomputed the rational counterexample with a separate root-free comparator: C1-C2 rank signs at z=1/64,1/16,1/4,1,4,16,64 are [+,-,-,+,+,+,+]. Arbitrary joint-scaled cosine admits nonmonotone pair ordering.

The general ranking formula is correct: remove common positive query norm to obtain (a_i+z*b_i)/sqrt(u_i+z*v_i), z=t^2, assuming nonzero transformed norms. Real benchmark normalization depends on individual document terms. LOW48 by query magnitude is not a proved nuisance label; endpoint contrast is not universal pointwise monotonicity. These invalidate an unqualified transfer claim.

IMPORTANT QUALIFICATION TO AUDIT: t versus t^2 and changing query alone do NOT explain an opposite SIGN-vs-cosine direction. In the exact Model-H document family, also scaling the two query nuisance coordinates yields gap 2-2*t^2*D with still-common document norm; t^2 is positive monotone and crosses1 at t=1. The same SIGN-dominance regimes (cosine better below1, sign better above1) therefore survive. Coordinator checked all five D values at six rational t values (30 cells); analytic extension follows directly from D in {-2,-1,0,1,2}. The lower tie threshold shifts to sqrt(1/2), but the crossover against SIGN does not. Thus the audit overstates 'different parameter' as a standalone explanation; lost structural assumptions/unsupported proxy identification are central, and several changes interact. Document-only scaling of arbitrary real vectors would not by itself restore the theorem.

The pairwise cell ordering is a sufficient condition for per-realization top-K dominance; it is not necessary for expected top-K dominance of all distributions. Independence/uniform tie randomness is not needed for a pathwise coupling once deterministic relative-order conditions hold, though it supports strict expected witnesses. Avoid labeling every synthetic assumption necessary.

Crossing polynomial degree<=3 gives a generic upper bound on isolated candidate equality roots only when polynomial is nonzero; an identically zero polynomial may describe persistent ties (and requires sign filtering). A witnessed 2+2-dimensional example is not proved dimension-minimal; worker's smaller-dimension search was unfinished.

No new real-vector runs in this audit; no empirical causal attribution among numerator/norm/proxy components established. After-only hashes are not a before/after integrity proof. Original report preserved unchanged with these corrections. LoCoMo provenance correction remains governing. No benchmark theory confirmation or new codec result.
