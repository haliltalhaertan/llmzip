# STATUS — math-ranking-bounds pilot

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

- Workspace: `/home/mdp/muse-work/math-ranking-bounds` (writes only here + /tmp).
- Sources elsewhere are READ ONLY. No push, no main changes, no paid APIs, no web, no installs, no frozen-benchmark runs.
- Target: provable ranking stability under bit removal/quantization (top-k set/recall preservation, ties included).

## Plan (bounded first pass)

1. Formalize: full b=96 bits, retained S (|S|=k), removed R (r=b-k). Pairwise perturbation bound (T1), top-K set invariance under gap>r (T2), per-gold deep-free/deep-buried survival (T3), array-specific loss sandwich (T4), hypergeometric tie math (T5), distribution-free impossibility with explicit quantifiers (T6, honest negative) + r=1 optimistic-preservation boundary.
2. `verify.py` (stdlib only): exhaustive over b=3 (n=2,3; K=1,2) all doc/query combos × all subsets + b=4 n=2 spot + brute-permutation hypergeometric checks + lifted 96-bit witnesses.
3. `results.json`: raw deterministic counts. `REPORT.md`: self-contained statements + proofs + failed attempts + scope/novelty limits.

## Checkpoint log

- 2026-09-13 20:05 UTC: read PROMPT_EXTERNAL_LLM, cert report+compute, audit1_cont report, b3b_fin report, ROUND3 report, MATH-1 + MATH-2 reports, lit-scan head. Workspace empty; python3 3.14 system available; going stdlib-only so no ml-python import needed.
- 20:20 UTC: verify.py executed GREEN (122,368 T1/T2 checks; 604,160 T3; 424,448 T4; 171 T5; witnesses W1/W2/C1). First draft r=1 opt-preservation lemma FALSIFIED by sweep, replaced with restricted-entry lemma + C1 counterexample (recorded in REPORT §5). REPORT.md self-contained; results.json written. Deliverable complete: REPORT.md, verify.py, results.json, STATUS.md.
