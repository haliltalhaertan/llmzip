# Coordinator review: bit-allocation toy results

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

The original verify.py reran 9/9 green. Independently written check_independent.py (no imports from worker implementation) enumerates all uniformly weighted ordered document pairs and confirms the five headline exact errors. Raw counts and error patterns are in coordinator_exact_results.json. Original REPORT.md/results.json preserved, not silently rewritten.

SUPPORTED, within synthetic asymmetric inner-product model:
A: spread (1,1) error 1/14; concentrated (2,0) 2/7; dropped-H (0,2) 3/14.
B: spread (1,1,1) error 1/10; mixed (2,1,0) 1/30.
These compare preservation of FULL-PRECISION INNER-PRODUCT ORDER, not external relevance labels or the frozen sign-query/Hamming top-3 protocol. They are finite counterexamples to universal allocation heuristics, not measured benchmark gains.

CORRECTIONS before broader use:
1. Setup-B prose derivation is wrong although its final numbers are correct. For (1,1,1), C3 is kept exactly: the claimed (delta C1,delta C2,delta C3)=(0,0,nonzero) cannot cause an estimated tie. Correct exhaustive counts: 256 ordered pairs, 16 true ties excluded; 16 flips plus 16 estimated ties -> (16+8)/240=1/10. Estimated ties arise from same-sign C1 conflation with delta C1=+/-2, delta C2=delta C3=0. Flips split between same-sign conflation interacting with C3 and opposite-sign amplification interacting with C2. For (2,1,0), the omitted-C3 tie account is valid: 16 estimated ties /2 /240=1/30.
2. M4's displayed sign-mismatch indicator must mean STRICT reversal M*Mhat<0, not sign(Mhat)!=sign(M) including zero. Otherwise ties get counted twice. Executable code correctly uses mutually exclusive tie/reversal branches.
3. Separability alone does NOT prove greedy bit allocation globally optimal for query-weighted MSE. One-step best improvement is tautological; multi-step global optimality requires e.g. diminishing marginal gains with compatible prerequisites. No such theorem was proved. Likewise optimizing individual pair contributions does not automatically optimize a shared-allocation union-bound sum.
4. The proposed top-K union bound requires consistently defined crossing events for a fixed true top-K set and compatible random tie resolution. The conditional average pair error reported here is not automatically that event probability. Treat the surrogate claim as unfinished, not a proved retrieval guarantee.
5. Shared-cost ledger omits reconstruction levels needed even by its ONE-bit conditional-mean decoder; levels must be predefined reproducibly or stored/charged. The claim of 48 index bits for an arbitrary 48-of-96 subset is not a justified encoding. No deployable total-byte accounting is established.
6. Proposed E2 comparison (ii)-(iii) holds the same 48 coordinates, so a nonpositive upgrade effect cannot prove damage from sacrificed coordinates. Comparisons to 96x1 also change query/scoring rules. Revise factorial ablations and neutral outcomes before experimental use.

Bottom line: two exact gain/loss toy instances are supported. Prose proof details, optimizer guarantees, top-K transfer and metadata costing are not all sound; no universal or benchmark superiority is approved.
