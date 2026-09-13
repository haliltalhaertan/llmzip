# Coordinator review: ranking-bounds first pass

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

The supplied verify.py was rerun as `python3 -B verify.py coordinator_results.json` and reproduced the reported counts without violations. This is finite checking, NOT Lean/kernel formal verification or a literature novelty check.

Supported elementary result: deleting r sign coordinates changes any pairwise Hamming-distance gap by at most r. Therefore a strict top-K boundary gap greater than r guarantees identical top-K membership for every subset deleting r coordinates. This is a sufficient condition, not a necessary condition and not an empirical claim about actual benchmark margins.

Corrections/limits required before quoting the original REPORT.md broadly:
- T6's two-document construction explicitly uses K=1. It does not directly prove the stated numerical loss for the programme's K=3 setting. Do not advertise the 1 -> 1/2 example as top-3 evidence.
- `forall S exists archive` does not prove `forall data-dependent selector exists archive on which its selected S fails`. The parenthetical claim about data-dependent choices needs separate quantifiers/argument.
- T1-prime's possibility of reversal below margin r needs enough retained coordinates to realize the negative retained gap. Empty S cannot produce a strict reversal. Treat the inequality as universal and the realizability construction as conditional on dimensions.
- T4 is a valid coarse sandwich but its optimality among all bounds using the full profile is NOT proved by T6. Statements that it is an 'upper envelope' or that no stronger profile-based bounds exist are unsupported.
- T5 trial-mean variance divided by trial count assumes independent random priorities across trials. Fixed seeded trial results are deterministic; the variance is with respect to the idealized randomization law, not an additional empirical guarantee.
- The tiny exhaustive sweep mostly yields a zero lower bound. No practical safety rate for real 96-bit benchmark profiles has been measured.

Preserve original reports as worker outputs; this note qualifies their claims. No scientific priority claim is approved.
