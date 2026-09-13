[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Replacing "greedy optimal" with real allocation theory + counterexamples

SYNTHETIC toy PMFs only. NOT benchmark output. No relevance labels, no
cosine/Hamming benchmark, no transfer to LME/LoCoMo/REALTALK/PerLTQA.
Worker REPORT.md files are treated as fallible; coordinator notes govern
until independently resolved. Nothing here claims literature novelty or a
universal "48x2 better" rule.

## 0. One substantive result

**THEOREM 1 (strict greedy failure, exact).** In the finite M-IND model
(independent coords, fixed full-precision query, asymmetric inner-product
scoring, conditional-mean 0/1/2-bit decoders, pairwise ORDER error with
estimated-tie = 1/2 and true ties excluded), fixed-budget greedy by largest
one-step ranking-error decrease is NOT globally optimal. Explicit witness
(instance G*, §2): d=3, budget B=3, greedy makes three STRICTLY unique
one-step-optimal moves (marginal gains 163/718, 41/718, 19/359, every step
contested) ending at (1,1,1) with P=117/718, while the UNIQUE global optimum
is (2,1,0) with P=41/718. Gap: 38/359. All rationals exact (two independent
code paths + hand derivations of the decisive entries, §3-§4).

**THEOREM 2 (separable-MSE greedy sufficiency, proved by exchange).**
For S(b) = sum q_j^2 e_j(b_j) with e_j nonincreasing and DIMINISHING gains
(e_j(0)-e_j(1) >= e_j(1)-e_j(2)) plus the prefix constraint (2nd bit needs
1st), fixed-budget greedy by largest one-step S-decrease is globally optimal
(§5). Diminishing is load-bearing: it FAILS for a realizable
conditional-mean quantizer (sparse coord gains 361/100 < 729/100, §6), and
without it even abstract separable greedy fails strictly (gains A=(5,100),
B=(6,6): greedy (0,2)=12 vs OPT (2,0)=105), including a REALIZABLE
quantizer-distribution failure ((Q,S10), B=2: greedy (1,1)=829/100 vs OPT
(0,2)=5, both steps strict, §6).

Consequence for the first pass: §6 "greedy-MV" claims (variance heuristic
aside) had no optimality proof and none exists in general — the MV/SV rule
is a heuristic with now-quantified failure modes, exact on the two old toys
only. The per-pair union-bound "optimality" inherits the same gap.

## 1. Conventions (quantifiers fixed before any claim)

- (M1) Docs: X = (X_1..X_d), X_j ~ P_j finite symmetric support,
  independent across j. Ordered pairs (A,B) iid from the product law.
- (M2) Query q in Q^d FIXED; analysis conditional on q.
- (M3) b_j in {0,1,2}: 0 -> xhat=0; 1 -> sign bit, level E[X_j|sign];
  2 -> sign + magnitude bit 1[|X_j|>=t_j], level E[X_j|region]. Threshold
  t_j fixed per coordinate (t=2 throughout unless stated).
- (M4) P_err(b) = E[w err]/E[w 1[M/=0]], err = 1[strict reversal] +
  (1/2) 1[Mhat=0, M/=0], M = s(A)-s(B), Mhat = shat(A)-shat(B).
- Greedy-MV (fixed budget B): G_0 = 0; step k: among feasible j
  (G_j<2) pick the UNIQUE argmax of MV_j = P(G)-P(G+e_j). A step with a
  tied argmax is a TIE BRANCH (greedy undefined without a tie law); every
  strict-failure claim below requires a unique argmax at each contested
  step, else it is reported as branch-dependent, not strict.
- S(b) = sum_j q_j^2 e_j(b_j), e_j(b) = E[(X_j-xhat_j(b))^2], unweighted
  MSE the q=1 case. S-greedy defined analogously on S-decreases.

Cost ledger rule (§7): payload B = sum b_j is doc-payload only. Decoder
levels (ALL of them, including 1-bit conditional means), thresholds t_j,
and the upgraded-coordinate index map are shared costs in separate columns.

## 2. Instance G* (main witness)

- C1 (sparse): -10 w.p. 1/20, -1 w.p. 9/20, +1 w.p. 9/20, +10 w.p. 1/20.
- C2: +-3/2 w.p. 1/2 each. C3: +-1/10 w.p. 1/2 each.
- q = (1,1,1), t = 2, budget B = 3.
- Decoder levels: 1-bit C1 -> +-19/10 (E[X|X>0] = (9/20+10/20)/(1/2));
  2-bit C1 -> exact (regions {10}->{10},{1}->{1},{-1}->{-1},{-10}->{-10});
  C2, C3 binary -> exact already at 1 bit (levels equal values).
- Scale: 16 docs, 256 ordered pairs per allocation; 7 allocations sum to 3.

## 3. Hand proofs (decisive entries)

LEMMA D (denominator). True-tie mass = 41/400, so denom = 359/400 for all
allocations. Proof: DeltaC1 in {0,+-2,+-9,+-11,+-20}, DeltaC2 in {0,+-3},
DeltaC3 in {0,+-1/5}. Nonzero |DeltaC1+DeltaC2| >= 1 (attained at 2-3) >
1/5 >= |DeltaC3|, so M=0 iff DeltaC1+DeltaC2=0 and DeltaC3=0; the first
forces (0,0) since 2/=3 in magnitude. P(DeltaC1=0) = (1+81+81+1)/400 =
41/100; times 1/2, 1/2 gives 41/400. [Check G1 confirms.]

LEMMA O (optimum value). P(2,1,0) = 41/718. Proof: C1,C2 exact, C3 dropped
(|DeltaC3|<=1/5). If DeltaC1+DeltaC2/=0 its magnitude is >=1 so dropping C3
never flips the sign. Error only via DeltaC1+DeltaC2=0 (mass (41/100)(1/2)
= 41/200) with DeltaC3/=0 (1/2) giving Mhat=0: numerator (41/200)(1/2)(1/2)
= 41/800; divide by 359/400 -> 41/718. [Check G3 confirms.]

LEMMA G (greedy endpoint value). P(1,1,1) = 117/718. Proof by C1-pair
cases (C2,C3 exact; DeltaChat1 in {0,+-19/5}; R = DeltaC2+DeltaC3):
(a) Same-sign conflated pairs (10,1),(1,10),(-1,-10),(-10,-1), total mass
9/100, DeltaC1=+-9 estimated as 0. Subcases: R=0 (mass 1/4) -> Mhat=0 tie:
mass (9/100)(1/4) = 9/400, contributes half = 9/800 to the numerator.
R=∓3 opposing C2 (mass 1/4): M=+-6+DeltaC3 vs Mhat=∓3+DeltaC3, always
flipped: mass (9/100)(1/4) = 9/400 = 18/800. R=∓1/5 with DeltaC2=0 (mass
1/8): M=+-9∓1/5 vs Mhat=∓1/5, flipped: mass (9/100)(1/8) = 9/800. (Aligned
R: correct.)
(b) Opposite-sign small pairs (1,-1),(-1,1), mass 81/200, DeltaC1=+-2
AMPLIFIED to +-19/5. With opposing DeltaC2=∓3 (mass 1/4): M=∓1+DeltaC3 vs
Mhat=+-4/5+DeltaC3, flipped for all DeltaC3 (|DeltaC3|<=1/5 keeps both
signs): mass (81/200)(1/4) = 81/800. (Aligned/zero C2: correct.)
(c) All other C1 pairs correct: large opposite-sign (DeltaC1=+-20,+-11):
Mhat=+-19/5+R with |R|<=16/5, sign preserved; identical values: D=0.
Numerator total: 9/800 (ties) + 18/800 + 9/800 + 81/800 (flips) = 117/800.
P = (117/800)/(359/400) = 117/718. QED. [Check G4 confirms.]
CORRECTION RECORD: an early draft of this derivation dropped the (a)-R=∓1/5
flip row (9/800); the exact enumeration (117/800 numerator) caught it, and
the case list above is the corrected one. Preserved here per protocol.

COLLAPSE (exactness, one line each): C2,C3 binary => 1-bit reconstructions
already exact => P(0,2,0)=P(0,1,0), P(0,2,1)=P(0,1,1)=P(0,1,2),
P(1,2,0)=P(1,1,0). No enumeration needed for these equalities.
TRIVIAL: P(0,0,0)=1/2 (Mhat==0 identically). [Check G2 confirms.]

## 4. Greedy trace (strict) + global table

From P(0,0,0)=1/2=359/718:
- Step 0 contenders: MV(C1)=1/2-120/359=119/718; MV(C2)=1/2-98/359=163/718;
  MV(C3)=1/2-159/359=41/718. Unique max C2. STRICT.
- Step 1 from (0,1,0)=196/718: ->(1,1,0)=158/718 (MV 38/718=19/359);
  ->(0,2,0)=196/718 (MV 0, by COLLAPSE); ->(0,1,1)=155/718 (MV 41/718).
  Unique max C3 (41>38>0). STRICT.
- Step 2 from (0,1,1)=155/718: ->(1,1,1)=117/718 (MV 38/718=19/359);
  ->(0,2,1), ->(0,1,2) both 155/718 (MV 0, by COLLAPSE). Unique max C1.
  STRICT. Greedy final: (1,1,1), P=117/718.
[Check G5 confirms picks/MVs/strictness.]

Budget-3 table (exact; each entry double-path verified, G0):
(0,1,2)=155/718; (0,2,1)=155/718; (1,0,2)=199/718; (1,1,1)=117/718;
(1,2,0)=158/718; (2,0,1)=163/718; (2,1,0)=41/718.
UNIQUE global optimum (2,1,0); greedy suboptimal by 38/359. [G6, G7.]
Mechanism in one line: C2's sign bit looks best alone (163/718), and C3's
sign bit best next (41/718), but the pair (C1-2bit, C2-1bit) jointly kills
both conflation damage (C1 exact) and the residual tie-tax (C3 dropped
costs only 41/800) — a lookahead interaction no one-step rule can see.

Status split (honest): LEMMAS D/O/G, COLLAPSE equalities, and P(0,0,0) are
hand-proved above. The remaining intermediate entries (P(1,0,0)=120/359,
P(0,1,0)=98/359, P(0,0,1)=159/359, P(1,1,0)=79/359, P(0,1,1)=155/718,
P(1,0,2)=199/718, P(2,0,1)=163/718) are EXACT FINITE WITNESSES verified by
two independent exact paths (pair loop vs gap convolution, G0/G8) — a
reader can re-derive each by the stated enumeration rule, but no compact
hand proof is given here; they are not conjectures (two code paths agree
exactly) and not hand-lemmas either.

## 5. THEOREM 2 (separable query-weighted MSE: sufficient condition + proof)

Statement: let S(b) = sum_j q_j^2 e_j(b_j), b_j in {0,1,2}, sum b_j = B.
Assume (i) monotone: e_j(0)>=e_j(1)>=e_j(2) (all bit-gains >= 0); (ii)
diminishing: g_j(1)>=g_j(2)>=0 where g_j(k)=q_j^2(e_j(k-1)-e_j(k));
(iii) prefix: the 2nd bit on j requires the 1st. Then fixed-budget greedy
by largest one-step S-decrease is globally optimal.
Proof (exchange, induction on chains+B): B<=1 trivial (greedy takes the max
first-bit gain over exactly the feasible singletons). Let i_1=(j,1) be
greedy's first pick, gain g = max first-bit gain. Claim: some optimal
B-set O contains (j,1). Else j's chain is empty in O; since |O|=B=|G| and
O/=G some chain j' holds strictly more O-items than greedy-final items;
let o=(j',c) be its chain-top in O (c in {1,2}, o not in G). Then
O' = O-{o}+{(j,1)} is feasible (j-chain was empty; removing a chain-top
preserves prefix-closedness) with value change g - g_{j'}(c) >=
g - g_{j'}(1) >= 0 (diminishing + maximality of g). So O' is optimal and
shares one more item with G; iterate to get optimal O containing (j,1).
Then O-{(j,1)} is optimal for the REDUCED problem (j's first bit removed;
j's 2nd bit now unconditionally available with gain g_j(2); B-1 budget):
any better reduced set R would lift to R+{(j,1)}, feasible with higher
value, contradiction. Greedy's subsequent picks are exactly greedy on the
reduced problem (same remaining numbers, same availability), optimal by
the induction hypothesis. QED.
Notes: (a) diminishing is used once, in g>=g_{j'}(c); without it the
exchange fails — §6 shows it failing really happens. (b) The first-pass
claim "single-step greedy is optimal for S BY CONSTRUCTION" is exactly the
tautology the coordinator flagged; the theorem above replaces it. (c) S is
retrieval-adjacent, NOT retrieval-optimal: S-tracks-ranking on the old
toys is observation, and THEOREM 1 shows true-P_err greedy fails where
S-greedy may succeed — do not conflate the objectives.

## 6. Separability is not enough: two counterexamples

ABSTRACT (no distribution needed — proves diminishing is load-bearing):
gains A=(5,100), B=(6,6), B=2. Greedy: step 0 takes B (6>5, strict); step 1
contenders A-first 5 vs B-second 6, takes B (strict) -> (0,2) = 12. OPT is
(2,0) = 105. Strict failure from increasing returns alone. [Check S3.]
REALIZABLE (stated quantizer distributions): sparse coord e =
(109/10, 729/100, 0), gains 361/100 < 729/100 — INCREASING, so diminishing
is not automatic for conditional-mean quantizers (quaternary (5,1,0) gains
4>=1 and binary (9/4,0,0) gains do diminish; the sparse law breaks it).
[S1, S2.] Consequently S-greedy fails on real quantizer laws: (Q4,S10),
q=(1,1), B=2: step 0 takes Q4 (4 > 361/100, strict); step 1 from (1,0):
S10-first 361/100 vs Q4-second 1, takes S10 (strict) -> (1,1) = 829/100;
OPT (0,2) = 5 (unique: 5 < 829/100 < 109/10). Fully hand-checkable: only
three budget-2 allocations. [Check S4.]
Lesson: "separable => greedy works" is false twice over (abstractly and
realizably); diminishing + prefix is the precise repair, and §5 proves it.

## 7. Shared-cost ledger (corrected: 1-bit levels included)

The first-pass ledger charged thresholds only for 2-bit coords and omitted
decoder LEVEL storage entirely. Corrected rule: every coded coord needs its
level values stored/charged at precision T (or predefined reproducibly and
cited). For G*: 1-bit C1 needs +-19/10 (ONE value up to sign); 2-bit C1
needs 4 region means (-10,-1,1,10) + t_C1; C2/C3 binary need their single
values. Per-allocation: (2,1,0): payload 3 bits + 1 threshold + 6 level
values + upgraded-coord index map; (1,1,1): payload 3 bits + 0 thresholds
+ 3 level values + no map. Payload-equal allocations differ in shared cost
— any "3-bit" comparison that omits this is incomplete accounting, same as
the brief's SIGN96-vs-float disclosure. [Check C1.]
No deployable total-byte accounting is established (T unspecified); no
"48 index bits for an arbitrary 48-of-96 subset" encoding is claimed.

## 8. Correct global optimizer + complexity boundary

- True P_err: NO separability (margin sum couples coords; THEOREM 1 is the
  witness). Exact global optimizer = full enumeration over 3^d allocations
  (7 for G* at B=3; 3^d total). DP/knapsack is valid ONLY for separable
  objectives (S): O(d B 3).
- Gap-law convolution (Path B) is an exact RE-DERIVATION, not a claimed
  polynomial method: joint (M,Mhat) support is bounded by the PRODUCT of
  per-coord gap supports (<= K_j^2 each, K_j = support size) — exponential
  in d in general. No "convolution is polynomial" claim is made.
- Marginal ranking-error interactions block every separability shortcut;
  per-pair MV allocation optimizes a union-bound SURROGATE, not retrieval.

## 9. Search bounds (no universality claimed either way)

- d=2 shared-t grid (binaries/quats/sparse x 9 queries x B in {2,3}): 0
  failures. (A failed conjecture that d=2 shared-t suffices is recorded,
  not hidden.)
- d=2 extended grid (+zero-mass/uneven supports, per-coord thresholds,
  12 queries, B in {2,3,4}): 14 failures. Smallest witness: (Q4,S10),
  q=(3,2), B=3: greedy (2,1) P=213/1427 vs OPT (1,2) P=163/1427, steps 0-1
  strict, final step forced (only one feasible move) — DISCLOSED as weaker
  than G*; recorded as secondary witness [G8, G9], not the headline.
- d=3 sample (19 triples x 10 queries x B in {2,3}): 5 failures, including
  headline G* (all steps contested+strict, all MVs positive).
- S-greedy probe: 8 failures in 66 models (all via increasing MSE gains).
- Not searched: d>=4, continuous laws, threshold sensitivity on continuous
  support, symmetric (binarized) query, mixed budgets. "No greedy failure
  exists at d=2 shared-t with positive MVs throughout" is UNRESOLVED
  (absence in a grid is not a theorem); "greedy works universally" is
  REFUTED (G*). Do not call finite testing a universal proof — this report
  claims one strict witness + one sufficiency theorem, nothing global.

## 10. Reproduction (executed this session, stdlib only)

  $ cd /home/mdp/muse-work/math2-allocation-optimality && python3 verify.py
  17/17 PASS (G0-G9, S1-S4, C1-C3), ALL_PASS=True, exit 0; wrote results.json.
  $ python3 checker.py
  14 alloc recomputations + greedy steps 0-1 + 2 MSE spots + broken-variant
  rejection, CHECKER ALL PASS, exit 0.
Coverage counted: 14 main nodes x 256 ordered pairs double-path; 7
budget-3 allocs enumerated; 4 d2-witness allocs double-path; 6 S-allocs
(3 distinct budget-2 values); 1 deliberately corrupted table REJECTED
(validator printed MISMATCH at (2,1,0) and returned False; true table
accepted). Failing-everything check: corrupt path exercised, fail-closed
confirmed — a validator that accepted the perturbed optimum would exit 1.

## 11. What is NOT proven; limits

- No benchmark claim (M1 known-false on programme data per MATH-1; no E2
  run here). No symmetric-query result. No top-K transfer (union-bound
  surrogate unfinished per coordinator). No literature novelty/priority.
  No learned/adaptive routing (stays closed). Threshold sensitivity on
  continuous laws untested. Mixed 64x1.5 untouched.
- Coordinator corrections applied: Setup-B prose derivation not reused;
  M4 strict-reversal indicator used in code (mutually exclusive
  tie/reversal branches); no "upper envelope"/optimality-of-T4 style claim
  appears here; no universal 48x2 direction (THEOREM D's instance-dependence
  stands; G* adds greedy-failure instance-dependence on top).
