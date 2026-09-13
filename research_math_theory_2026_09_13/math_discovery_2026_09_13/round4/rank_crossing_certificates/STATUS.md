[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS.md — exact rank-change / top-K stability certificates

Task: ONE rigorous result on exact pairwise rank changes and top-K set
stability under the actual joint-scaling normalized scoring law
f_i(z) = (a_i + b_i z)/sqrt(u_i + v_i z), z = t^2, common query norm removed.

State: DONE (first pass, within budget). All four deliverables written in
/home/mdp/muse-work/math4-rank-crossing-certificates:
REPORT.md (Theorems 1-3 + procedure + witnesses + limits),
verify.py (49/49 PASS), results.json (written by the run), this file.

Result: pairwise equality characterized with sign discipline (cubic P_ij +
spurious-root filter + P-identically-zero case); ranking constant between
genuine events (tangent touch does not imply reversal); top-K set stability
necessary/sufficient over K*(n-K) cross pairs with prio vs expected-tie
recall kept as separate objects; finite exact procedure (Sturm +
rational-root split, honest UNRESOLVED, numpy never certified); practical
output a certified safe interval (LME gold/rival rival-above on z in
[1/16,1]; flip bracket post-hoc, not prediction).

Honest incompletes (in REPORT.md §9): same-sign Sturm>=1 interiors stay
UNRESOLVED (e.g. LME (1,16)); 1+1-dim search UNRESOLVED in grid (18048/18048
evals, budget 40000); no dimension-minimality claim; certs cover exact
rational readings, not BLAS float order; no codec, no benchmark, no novelty
claim.

Constraints obeyed: workspace writes ONLY here; old sources read-only; no
sweeps/new arms, no Git push/main edits, no Task4F1, no installs/network/model
APIs. Run: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PYTHONDONTWRITEBYTECODE=1 /home/mdp/muse-work/ml-python -B verify.py ->
checks=49 fail=0 ALL PASS. No __pycache__ emitted.

Corrections adopted (govern worker prose): numerator alone does NOT explain
the LME15745da0 flip (norms essential); t vs t^2 alone explains nothing about
Model-H dominance; query magnitude NOT a proved nuisance label; +12pp LoCoMo
retracted (+6.82838pp same-cache MC only); no literature novelty claim.
