[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS.md — Theory provenance audit (LoCoMo baseline provenance error)
Workspace: /home/mdp/muse-work/theory-audit-locomo-provenance
Date (UTC): 2026-09-13
Mode: LOCAL EXPLORATORY PILOT, NOT PREREGISTERED, NOT FOR CITATION, DISCLOSE-BEFORE-USE.
Constraints: sources READ ONLY; no git push/main changes; no installs/network; no paid APIs/embeddings/new training/routing; frozen Task4F1 measurement; Muse subscription only; threads=1, PYTHONDONTWRITEBYTECODE=1.

## State
- STARTED. First pass bounded ~20 min, early evidence prioritized; partial/blocker reported rather than fabricated.
- STATUS.md written first per task order. REPORT.md / verify.py / results.json pending this pass.

## Primary job (from task)
- Close baseline PROVENANCE ERROR vs mathematics: shared plan required BOTH historical native + centered float96 replication before interventions. LoCoMo worker reproduced SIGN .23654714666441054 but substituted fresh float .16826334541318252 for missing old float arrays, then continued. Earlier programme text repeatedly said SIGN-float ~+12pp vs current arithmetic +6.82838pp. Trace each exact statement; do not assume +12 true/false a priori.
- Independent small correct centered-cosine + frozen fractional R@3 from original LoCoMo cache C/q + original exclusions, preserving stored Hamming gate; code independent of theorybench-locomo evaluator. Compare perQA table; diagnose provenance differences only, NOT select a matching +12.
- Test whether historical number refers to Haar/ITQ/other baseline/units via exact source lines. Negative search states searched scope.
- Deliver: provenance chain, original-vs-current metric definitions, exact independent current baseline, source status for +12. If no primary source for +12 → UNSUPPORTED, recommend retract pending source. State gate bypass explicitly; current recompute cannot retroactively satisfy missing historical anchor.
- Known LOW48 contrasts (given, not re-derived here yet): LME -6.44326pp CI[-9.2734,-3.6871]; REALTALK -.093606pp CI[-1.9330,+1.8490]; PerLTQA +2.46415pp CI[1.5540,3.44284]; LoCoMo -2.58291pp CI[-3.77676,-1.31321] CONDITIONAL (float historical gate not met). Four primaries unadjusted; no pooling/familywise. Positive diagonal scale ⇒ SIGN invariant by construction; outcome is float-scoring change. HIGH48(1/t)=LOW48(t) up to positive global scale, no independent evidence. Not a compression method. All further diagnosis post-hoc, not preregistered/held-out.

## Plan for this pass
1. Hash + read: T/PLAN.md, T/locomo/{REPORT,COORDINATOR_REVIEW,COORDINATOR_AGGREGATE,summary,gate,PLAN}, M/round3/all_n_ranking + sign_mechanism reports/reviews. Record file+line for claims; hash bytes before/after.
2. Trace +12pp: grep exact strings ("12", "+12", "12pp", "0.12", "SIGN-float", "SIGN minus float") in W/{drive,scratch,pilots,reports,review_transfer,bench3/runs/b3a_realtalk/report.md} + git log (read-only) of /mnt/c/Users/MDP/dev/llmzip. Scope-limited, no giant venv/Git/binary scans; inspect contents not filenames.
3. Independent check: original LoCoMo cache C/q + exclusions + Hamming gate → centered cosine + frozen fractional R@3; compare perQA; report exact current baseline.
4. Ranked error ledger (algebra / wrong assumptions / unidentifiable mapping / metric mismatch / numerical bugs / inference overreach); no 'proven cause' from correlation; counterexample-first with exact rational synthetics + ≥1 real executable check.
5. Outputs: REPORT.md (plain-English or Turkish summary + technical evidence), verify.py, results.json, STATUS.md (this file), independent checker as required; exact executed commands + counts.

## Log
- 21:2x UTC: workspace + source roots listed. STATUS.md created. Plan/coordinator files read+hashed.
- +12pp traced: only disclaimed repeat (b3a_realtalk/report.md:28-30) + prompt-brief premises; cert_report.md:213 (no LoCoMo float anchor ever frozen); T4D Haar gap −9.8839pp is the only sourced historical gap (different estimand, opposite sign). Git pickaxe empty.
- Independent recompute (`verify.py --write`, exit 0): sign MC .23654714666441054 / float MC .16826334541318252 / gap +6.82838pp; per-QA maxabs vs worker 0.0; perq has no float arm; 24 source hashes stable; cited-md before/after hashes identical.
- REPORT.md / results.json written. Verdict: +12pp UNSUPPORTED (retract pending source); LoCoMo pilot CONDITIONAL/PROTOCOL-DEVIATION; current arithmetic confirmed, not historical.

## Outputs
- REPORT.md, verify.py, results.json, STATUS.md (this file) in this workspace only. Frozen sources untouched.
