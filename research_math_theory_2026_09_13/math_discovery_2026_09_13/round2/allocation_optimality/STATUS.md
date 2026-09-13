[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# STATUS — math2 allocation-optimality (greedy replacement pass)

Scope: synthetic exact computation only. No benchmark runs, no Task4F1 access,
no external APIs, no installs, no web fetch. Sources outside
/home/mdp/muse-work/math2-* are READ ONLY. No push, no main edits.
Workspace: /home/mdp/muse-work/math2-allocation-optimality (this dir only).

## Plan (bounded ~20 min pass)
1. [done] Read bit_allocation COORDINATOR_REVIEW + REPORT + checker/results.
2. [active] STATUS.md early (this file).
3. Search small finite M-IND models for STRICT greedy-MV failure on P_err
   (unique argmax every step; global enumeration; tie=1/2; true ties excluded).
4. Prove/query-weighted separable-MSE greedy theorem under diminishing gains
   + prefix constraints (exchange argument); abstract separable counterexample
   without diminishing returns; test realizability with quantizer PMFs.
5. Write REPORT.md + verify.py + results.json + independent checker path +
   deliberately-broken variant that must FAIL closed.
6. Final short response with paths, result, checks, limits.

## Conventions (fixed)
- M-IND: independent coords, fixed full-precision query, asymmetric scoring
  s_hat = sum q_j x_hat_j, b_j in {0,1,2}, conditional-mean decoders.
- P_err(b): ordered-pair expectation, estimated-tie counts 1/2, true ties excluded.
- Greedy-MV: G0=0; each step unique argmax of P(G)-P(G+e_j) over feasible j.
- S(b) = sum q_j^2 e_j(b_j): separable query-weighted MSE surrogate.

## Log
- 20:25Z: read coordinator reviews (bit/ranking/sign) + REPORT + checker/results.
  Governing: Setup-B prose wrong (numbers right); M4 strict indicator;
  separability =/=> greedy optimality; union surrogate unfinished; ledger omits
  levels; E2 (ii)-(iii) confounded; sign-mechanism independence error noted.
- 20:30Z: d=2 shared-t grid (bin/quat/sparse x 9 queries x B=2,3): 0 failures.
- 20:35Z: d=3 sample (19 triples x 10 queries x B=2,3): 5 STRICT failures.
  Headline G* selected: (sparse,+-3/2,+-1/10) q=(1,1,1) B=3.
- 20:40Z: separable-S probe: sparse MSE gains INCREASING (361/100<729/100);
  8 realizable S-greedy failures / 66. Abstract counterexample fixed.
- 20:45Z: d=2 extended grid finished: 14 failures; smallest witness (Q4,S10)
  q=(3,2) B=3 recorded as secondary (final step forced — disclosed).
- 20:55Z: verify.py 17/17 PASS exit 0; checker.py ALL PASS exit 0 (incl.
  deliberately-corrupted table REJECTED). REPORT.md complete (2 theorems,
  hand proofs D/O/G + exchange, honest machine/hand split, failed
  conjectures preserved). DONE — no benchmark/E2/Task4F1 touched, source
  archive read-only, no push.
