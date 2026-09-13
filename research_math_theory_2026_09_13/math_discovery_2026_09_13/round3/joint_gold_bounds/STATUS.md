# STATUS — exact joint multi-gold bounds (third pass)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

- Scope: prove-or-refute corner theorem for EXACT joint multi-gold topK bounds. No benchmark runs, no network, no external APIs, no git push/main changes. Prior sources read-only.
- Target workspace only: /home/mdp/muse-work/math3-joint-gold-bounds. Outputs: STATUS.md (this file), REPORT.md, verify.py, results.json (+ optional independent checker).
- Plan (bounded ~15 min):
  1. STATUS.md now (done with this write).
  2. Read ONLY round2/sharp_bounds/{COORDINATOR_REVIEW.md, REPORT.md}, narrowly.
  3. One theorem (corner max/min) or honest counterexample; edge cases s=0/r=0, K>=m, K=n, simultaneous ties, m>1.
  4. verify.py (runnable) + differently formulated independent checker/hand derivation + false-claim negative control (average-of-individual-maxima universally sharp → must reject on d=(2,2,0,0) example).
  5. results.json with exact Fractions; REPORT.md with scope limits, failed attempts, commands/exit codes.
- Claim limits: no scientific priority, no universal security/losslessness, no new benchmark win. Quantifiers explicit; proofs vs exhaustive witnesses vs conjectures kept distinct.
- Prior-session note: two conditional-ranking sessions failed on 180s stream idle timeout before producing files; that is a tooling fact, not evidence of mathematical failure. No assumption of existing partial proof.
- Weighted extension: test whether nonnegative gold weights preserve corner claim; seek smallest weighted counterexample if not.
