# Coordinator review — all-N/K ranking in Model H

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reran worker verify.py: exit 0, all listed checks pass. The main parametric theorem follows directly from the stated pair tables under shared tie priorities: for 0<t<1 cosine never has more nongolds ahead of gold than sign; for t>1 the reverse; at t=1 rankings agree. This holds realization-wise for gold inclusion, and hence under expectation for all N and K. Equal document norms justify dot/cosine ordering in this particular synthetic law.

Strictness proof wording needs two cases. Choose A=1, exactly K nongolds with B=2 and rest B<=1 (positive mass when 1<=K<N). For t<1, cosine includes gold surely while sign includes it with probability K/(K+1). For t>1, cosine excludes gold surely while sign includes it with probability K/(K+1). Thus expected inequalities are strict for nontrivial N,K and t!=1, although not strict on every realization. The original single sentence about the better method 'never' having these nongolds precede is false for t>1, but the corrected argument establishes the claim. At t=1 equality always.

NEGATIVE-CONTROL BUG: verify.py line176 passes P(W)=11/16 as the 'strictly closer nongold' probability to topk_multinom, swapping wins/losses. Thus its 33129/524288 is NOT the original unconditional-multinomial error from first pass. Correct unconditional input u=1/16, v=1/4 produces 491159/524288 (coordinator independently recomputed with exact Fractions), still different from valid shared-gold value 1763/2048. The negative-control conclusion survives, but its implementation and displayed value are wrong. This does not affect the two correct conditional main computations.

The final stdout also describes competitor motion as ahead->tied->behind as t increases, reversing the prose direction. Relative to gold for D>0 the actual direction is behind->tied->ahead. REPORT.md's explicit tables and main inequalities are correct.

No real-data explanation, centering realization, literature priority, universal codec comparison or improved retrieval benchmark demonstrated. The theorem is specific to the stipulated signal/nuisance law. Multiple checking paths are worker authored, not an external independent proof audit. Original files are retained unchanged with these corrections.
