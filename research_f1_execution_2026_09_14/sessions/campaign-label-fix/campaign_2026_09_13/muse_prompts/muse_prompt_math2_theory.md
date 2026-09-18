# Muse session — MATH-2: theory framing for the bit-budget floor (candidate lemmas, bounds, discriminating tests)

You are a mathematically-minded theorist. Survey what established mathematics can say about our
bit-budget question, propose CONCRETE candidate statements, and map each to a falsifiable check we
can run on frozen data. Read-only /mnt/c; write only /tmp/math2/. No network (flag LIT-CHECK).
[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]. No paid APIs; Muse-only constraint.

## Context in one paragraph

A frozen programme compresses document representations to 96-bit sign codes for top-3 evidence
retrieval (fractional R@3; LME 54.20% / LoCoMo 23.65%). Empirics (rounds 1-3): sub-12-byte subset
selections degrade gracefully with spread/random selection (10B −2.7pp; 8B −5.9; 6B −9.2);
variance-ordered selection is anti-optimal (−10pp; tie-mass mediation); coordinate mixing damages
monotonically in variance disparity; learned selection has no premium (killed); axis utilities are
benchmark-local. Details: /mnt/c/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/
round3/ROUND3_REPORT.md (+ missing_analyses/, ERRATA) and strategy/roadmap_2026-09-13/
muse_ideas_technical.md.

## Tasks

1. **Framework survey (from knowledge; LIT-CHECK flags).** What bodies of theory are actually
   relevant and what do they quantify, with the traps named: SimHash/1-bit embedding angle-error
   formulas (bit-flip prob = θ/π); order statistics of binomials; rate–distortion for retrieval
   vs for distances (JL-style lower bounds may NOT transfer to top-k retrieval — say so);
   top-k/ranking-preserving compression results; quantized-kNN sketching bounds; conformal/
   tie-break analyses. For each: one-line what-it-gives-us + one-line what-it-cannot.
2. **Candidate statements (3-5).** For our specific questions, propose statements like:
   - S1: "Expected FR under a subset S is monotone in a computed 'boundary informativeness'
     functional of S" (definition + testable proxy + how to measure on frozen data).
   - S2: an "effective floor" formula: minimal bits keeping tie-mass at the top-3 boundary below
     a level, as a function of archive size and margin distribution (derive or conjecture + what
     data would calibrate it).
   - S3: selection-lift lemma for the kill-rule estimator (E[max of k] gap bounds; we have a
     numerical version in missing_analyses/m1 — is there a clean closed form worth formalizing?).
   - S4: a prediction that DISCRIMINATES tie-crowding theory from rival "boundary-noise"
     explanations using only frozen data.
   For EACH: statement; why it earns its place; proof strategy & tools; difficulty; the ONE
   frozen-data check to run now; and what would falsify it.
3. **Recommend the top 1-2** to pursue (per value/cost; costs = Muse sessions, no paid APIs) and
   sketch what a Lean/Mathlib formalization of the cleanest would look like (statement shape
   only; note the programme's cost rule means no paid prover APIs — Muse-only).
4. **Beyond reach (honest list).** Which hoped-for theorems (e.g., "no ≤b-bit code beats native")
   are out of reach or ill-posed, and why.

Deliverables: /tmp/math2/math2_report.md + math2_details.json. Print MATH2_VERDICT: one line.
~2-3 hours scale.
