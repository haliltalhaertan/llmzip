# Mathematical basis for 96x1 vs 48x2 (and mixed) bit allocation

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

All distributions below are SYNTHETIC toy PMFs. NOT benchmark output.
No frozen benchmark was recomputed; no frozen artifact was touched.

## 0. One useful result

Under a stated finite independent-coordinate model (M-IND, §2) with exact
pairwise ranking error as the objective (not MSE), the folk rule
"always spend bits on the highest-variance coordinates" is FALSE, with an exact
rational counterexample, while the opposite allocation can also win in a
different regime — with exact numbers for both. Concretely, with a 2-bit budget
over two coordinates (high-variance quaternary H, var 5; low-variance binary L,
var 1/4; query q = (1/100, 1)):

- Unweighted MSE prefers concentrating both bits on H: MSE(2,0) = 1/4 < MSE(1,1) = 1.
- Pairwise ranking error prefers spreading: P(1,1) = 1/14 ≈ 7.1% < P(2,0) = 2/7 ≈ 28.6%.
- Dropping H entirely beats upgrading it: P(0,2) = 3/14 ≈ 21.4% < P(2,0) = 2/7.

And with a 3-bit budget over three coordinates (gain regime, §5):

- P(2,1,0) = 1/30 ≈ 3.3% < P(1,1,1) = 1/10 = 10%: the second magnitude bit
  on the dominant coordinate pays for itself when the sacrificed coordinate
  is negligible (var 1/100).

So neither "always concentrate" nor "always spread" is a theorem. The computable
marginal-value criterion MV (§6) decides per instance; coordinate variance alone
does not. All values proved by exhaustive exact-rational enumeration
(`verify.py`, stdlib only; `results.json` is its raw output; 9/9 checks pass).

## 1. Question, protocol, and mandatory conventions

The programme's frozen retrieval protocol (citations: source file + section):

- Document C and query qC are 96-dim centered float vectors; native code SIGN96 =
  sign bits (12-byte payload); ranking by Hamming distance, top-3, fractional
  evidence recall averaged over 20 random tie-draws
  (`review_transfer/PROMPT_EXTERNAL_LLM_2026-09-13.md` §1; native anchors
  `race_2026-09-13/cert/cert_report.md` §2: LME 0.5419751773049645,
  LoCoMo 0.23654714666441054).
- Tie rule (frozen): per-question seeded random priorities
  `5_100_000+key*100_000+t*100+99`, `lexsort((priority, distance))`, K=3, NT=20
  (`audit_2026-09-13/audit1_cont/report.md`, Task C-real method section).
- The float anchor was ALREADY centered; the centering confound is dead
  (centering +0.149pp vs binarization +10.038pp; same file, Task B recap).
  It is not revisited here.
- Empirical payload comparison under test: SIGN96 12-byte payload vs float96
  384-byte payload, EXCLUDING global/shared costs (brief §1 + task statement).
  Observed sign−float gaps: LME ~+10pp, LoCoMo ~+12pp, REALTALK +5.2241pp,
  PerLTQA −6.275pp (genuine negative; `bench3/runs/b3b_fin/report.md` §2–§3).
- Learned selection / adaptive routing were killed/closed by earlier gates
  (`pilots/axis_attack_2026-09-12/round3/ROUND3_REPORT.md` §1, §5+m3) and are
  not revived here. Benchmarks remain separate (no cross-benchmark transport;
  cf. MATH-2 C5 / round-3 §3: utility transfer ≈ chance).

Target question (this pilot only): under a stated model, what is the expected
PAIRWISE RANKING ERROR effect of spending a second (magnitude) bit on one
coordinate versus keeping first (sign) bits on more coordinates at fixed
payload budget — i.e. 96x1 vs 48x2 vs mixed? Reconstruction MSE is the wrong
objective (cf. the TurboQuant "MSE ≠ recall" controversy,
`lit_scan_2026-09-13/LITERATUR_TARAMASI.md` §0.2); pairwise error is used.

Conventions fixed for this analysis (any E2 implementation must state the same):

- Query encoding: FIXED full-precision query (asymmetric scoring). DELTA from the
  frozen symmetric protocol (which also binarizes qC) is deliberate: it isolates
  the value of DOC bits; symmetric scoring would entangle query quantization.
  Direction supported by the sign-full-RP literature cited in the lit scan (§3).
- Decoder/scoring: estimated inner product ŝ(d) = Σ_j q_j·x̂_j(d_j); rank by ŝ.
- Tie convention: estimated-score tie (M̂ = 0, M ≠ 0) counts 1/2 error = random
  tie-break expectation (mirrors the frozen 20-trial fractional protocol in
  expectation). True-score ties (M = 0) are EXCLUDED from the denominator
  (no true order exists).
- Payload budget B = Σ_j b_j doc-payload bits. Magnitude thresholds t_j and
  coordinate-index maps are charged SEPARATELY (§7); a "12-byte" figure that
  omits them is incomplete accounting.

## 2. Model M-IND (explicit assumptions)

- (M1) d independent coordinates. Generic doc: X = (X_1..X_d), X_j ~ P_j
  finite symmetric support, independent across j. Ordered doc pairs (A, B)
  drawn from the product law (A and B iid across docs AND the "gold" label is
  defined by the TRUE score: no circularity — allocation never enters the
  definition of the true order).
- (M2) Query q ∈ ℚ^d FIXED (analysis is conditional on q; the criterion is
  therefore query-dependent — consistent with the programme's "utilities are
  benchmark-local" lesson, MATH-2 §2/S5 and round-3 D3/C5).
- (M3) True score s(d) = Σ q_j x_j; estimate ŝ(d) = Σ q_j x̂_j with per-coordinate
  quantizer: b_j = 0 → x̂_j = 0 (dropped); b_j = 1 → sign bit (threshold 0),
  level = E[X_j | sign] (exact conditional mean); b_j = 2 → sign + magnitude
  bit 1[|X_j| ≥ t_j], level = E[X_j | region].
- (M4) Pairwise error P_err(b) = E[w·err]/E[w·1[M≠0]] over ordered pairs,
  err = 1[sign(M̂)≠sign(M)] + (1/2)·1[M̂=0, M≠0], M = s(A)−s(B), M̂ = ŝ(A)−ŝ(B).

STATUS OF THE ASSUMPTIONS (no hiding): independence (M1) is KNOWN-FALSE on real
programme data — MATH-1's independence plug-in overpredicts every arm by
+4..+26pp and flips the TOP48−RAND48 sign
(`prereg_race_2026-09-13/math1/math1_report.md` §1b, §2c: retrievable-regime
tie buckets 12.7x/6.7x over binomial; duplicate/spike clusters). M-IND is a
toy scaffold for isolating the allocation logic (variance vs query-weight vs
margin geometry), NOT a fitted data model. No claim below transfers to
benchmarks without the E2 experiment (§10). No distance-preservation / JL
machinery is used anywhere (that transfer is a category error per MATH-2 T3
and `race_2026-09-13/cert/cert_report.md` §1(d)).

## 3. THEOREM E — exact pairwise-error formula (finite, assumption-free given profile)

Statement: fix q and the (possibly correlated, arbitrary) joint law of (A, B).
Let w(A,B) be the pair mass, M, M̂ as above. Then with the §1 tie convention,
  P_err = Σ_{A,B: M≠0} w·[1(sign flip) + ½·1(M̂=0)] / Σ_{A,B: M≠0} w.
Proof: ordered pairs partition into {M>0}, {M<0}, {M=0} (finite sums; no
measure theory). On {M≠0} the contribution is 1/0/½ by the stated tie rule by
definition; on {M=0} pairs are excluded by definition. ∎
Note: this reuses the MATH-1 Level-1 conditional-uniform-tie insight
(`prereg_race_2026-09-13/math1/math1_report.md` §1a) at the pair level; the
identity itself is background, not a novelty claim. Under M1 the sums factor
into per-coordinate PMFs, which is what `verify.py:pairwise_error` enumerates
exactly in ℚ (stdlib `fractions`; no floating point in the computation).

## 4. Setup A — LOSS regime; COUNTEREXAMPLE to 'always allocate to highest variance'

SYNTHETIC toy: H ∈ {−3,−1,+1,+3} w.p. 1/4 each (Var = 5); L ∈ {−1/2,+1/2}
w.p. 1/2 each (Var = 1/4); q = (1/100, 1); t = 2 (any t ∈ (1,3) is equivalent;
robustness checked, A5). 1-bit levels: Ĥ = ±2 (conditional mean), L̂ exact.
2-bit on H is lossless here. Budget B = 2.

THEOREM D (divergence of MSE-optimal and ranking-optimal allocation).
On the Setup-A instance: (i) unweighted MSE is minimized at (2,0)
(concentrate on highest-variance H): MSE(2,0) = 1/4 < MSE(1,1) = 1 < MSE(0,2) = 5;
(ii) pairwise ranking error is minimized at (1,1) (spread):
P(1,1) = 1/14 < P(0,2) = 3/14 < P(2,0) = 2/7. Hence the MSE-optimal allocation
strictly maximizes ranking error among the fixed-budget options, and the
variance-ordered rule ("bits to highest variance first") picks the
ranking-worst allocation. In particular even DROPPING H beats upgrading it
(3/14 < 2/7).
Proof (exact rational arithmetic; machine-checked in `verify.py`, checks
A1–A4; hand derivation reproduced so a reader need not trust code):
Denominator: M = ΔH/100 + ΔL = 0 ⟺ ΔL = 0 and ΔH = 0 (since |ΔH|/100 ≤ 0.06
< 1 = min nonzero |ΔL|): P(M=0) = (1/2)(1/4) = 1/8; denom = 7/8 throughout.
(i) MSE: E[(H−Ĥ)²] for 1-bit = 2·[(1/4)(3−2)² + (1/4)(2−1)²] = 1; so
MSE(1,1) = 1 + 0 = 1; MSE(2,0) = 0 + Var(L) = 1/4; MSE(0,2) = 5 + 0 = 5. ∎
(ii) P(2,0): M̂ = ΔH/100 (H exact, L dropped). If ΔL = ±1 (prob 1/2),
sign(M) = sign(ΔL) (margin 1 dwarfs ε|ΔH| ≤ 0.06) while M̂ = ΔH/100 is
0 (prob P(ΔH=0) = 1/4 → ½ err) or an independent sign (prob 3/4 → ½ err):
conditional err 1/2. Numerator (1/2)(1/2) = 1/4; P = (1/4)/(7/8) = 2/7. ∎
P(1,1): L̂ exact; if ΔL ≠ 0, |εΔĤ| ≤ 0.04 < 1 so sign(M̂) = sign(M) always.
Error only when ΔL = 0 AND ΔĤ = 0 AND ΔH ≠ 0, i.e. same-sign conflation
({3,1},{1,3},{−3,−1},{−1,−3}: 1/4 of H-pairs) → M̂ = 0 vs M ≠ 0 → ½:
numerator (1/2)(1/4)(1/2) = 1/16; P = (1/16)/(7/8) = 1/14. ∎
P(0,2): M̂ = ΔL exact. ΔL ≠ 0 (1/2) always correct (true margin sign = sign(ΔL)).
ΔL = 0, ΔH ≠ 0: M̂ = 0, M ≠ 0 → ½: (1/2)(3/4)(1/2) = 3/16; P = 3/14. ∎
Mechanism in one line: the sacrificed coordinate L carries the query-weighted
margin (q_L²Var(L) = 1/4 dwarfs q_H²Var(H) = 5/10000); variance ignores the
query, ranking cannot. This is the toy analogue of the PerLTQA profile
inversion (discriminative signal in LOW-variance coords,
`bench3/runs/b3b_fin/report.md` §3/§5) — analogy only, not evidence.

Marginal values at (0,0) (computed): P(0,0) = 1/2; P(1,0) = 5/14 → MV_H = 1/7;
P(0,1) = 3/14 → MV_L = 2/7. So MV_L > MV_H despite Var(H) = 20·Var(L):
greedy-by-MV picks the low-variance coordinate first (check A6) — the trap is
specifically the variance heuristic, not greedy marginal-value filling (whose
general optimality is NOT claimed, §6).

## 5. Setup B — GAIN regime (concentration wins)

SYNTHETIC toy: C1 ∈ {−3,−1,+1,+3} w.p. 1/4 (Var 5); C2 ∈ {−3/2,+3/2} w.p. 1/2
(Var 9/4); C3 ∈ {−1/10,+1/10} w.p. 1/2 (Var 1/100); q = (1,1,1); t = 2.
1-bit: C1 → ±2 (conflation), C2/C3 exact. Budget B = 3.
Result (checks B1–B3): P(1,1,1) = 1/10 = 10% > P(2,1,0) = 1/30 ≈ 3.3%.
Derivation: P(M=0): ΔC1+ΔC2 ∈ ℤ and ΔC3 ∈ {0,±1/5}, so M = 0 ⟺ ΔC1+ΔC2 = 0
(only (0,0): ΔC1 ∈ {0,±2,±4,±6}, ΔC2 ∈ {0,±3}) and ΔC3 = 0:
(1/4)(1/2)(1/2) = 1/16; denom 15/16. P(1,1,1): conflation flips —
|ΔC1| = 2 (prob 1/4) estimated as |ΔĈ1| = 4 against opposing ΔC2 = ∓3
(prob 1/4): true M = ∓1±1/5 keeps sign, estimate M̂ = ±1±1/5 flips:
mass 2·(1/8)(1/4) = 1/16 (ΔC3, |ΔC3| ≤ 1/5 < 1, never changes a sign here);
plus tie-tax (0,0,ΔC3≠0) → M̂ = 0: (1/4)(1/2)(1/2)(1/2) = 1/32.
Numerator 3/32; P = (3/32)/(15/16) = 1/10. ∎ P(2,1,0): C1, C2 exact, C3
dropped (|ΔC3| ≤ 1/5): error only via (0,0,ΔC3≠0) → M̂ = 0: 1/32;
P = (1/32)/(15/16) = 1/30. ∎ MSE agrees here (MSE(1,1,1) = 1,
MSE(2,1,0) = 1/100) — Setup B is the regime where heterogeneity-style
concentration is right under BOTH objectives; it does not contradict §4.
Lesson: the gain direction exists exactly when the sacrificed coordinates are
margin-negligible AND a dominant coordinate suffers conflation damage —
i.e. high effective heterogeneity. This parallels the heterogeneity paper's
Prop 5b intuition (magnitude-bit gain grows with heterogeneity;
`lit_scan_2026-09-13/sources/coordinate_heterogeneity_2605.17524.md` §5/lines
95–104) but is a different quantity (pairwise ranking error under M-IND, not
fidelity under Gaussianity) and comes WITH the §4 loss regime, which bounds it.

## 6. Computable marginal-value criterion (and the surrogates it is / is not optimal for)

Criterion: for allocation b, MV_j(b) = P_err(b) − P_err(b+e_j) (exact, via
THEOREM E enumeration; DP/convolution over per-coordinate contribution laws
scales it beyond toys). Fixed-budget swap value SV_{i→j}(b) = P_err(b) −
P_err(b−e_i+e_j). Decision rule: spend the next bit where MV is largest;
under a fixed budget, apply swaps with SV > 0. On Setup A at (1,1) the swap
(1,1)→(2,0) has SV = 1/14 − 2/7 = −3/14 < 0: REJECT concentration. On Setup B
at (1,1,1) the swap →(2,1,0) has SV = 1/10 − 1/30 = +1/15 > 0: ACCEPT.
Variance-ordering gives the wrong answer on A; MV gives the right answer on
both toys (EMPIRICAL OBSERVATION on two instances, not a theorem).
Surrogate ledger (name them, do not overclaim):
(S-a) Query-weighted MSE S(b) = Σ_j q_j²·e_j(b_j): separable; single-step
greedy is optimal for S BY CONSTRUCTION of MV applied to S. On Setup A,
S(1,1) = 1/10000 < S(0,2) = 1/2000 < S(2,0) = 1/4 — S tracks ranking while
unweighted MSE does not (OBSERVATION, two toys; S is retrieval-adjacent, not
retrieval-optimal).
(S-b) Pair-sum union-bound proxy for top-K: P(top-K error) ≤ Σ over the
K(N−K) gold-vs-rival pairs P_err(pair). Standard union bound (proof: one
line); per-pair MV allocation is optimal for the BOUND, not for retrieval —
the bound is loose exactly when pair errors correlate (duplicate clusters;
MATH-1 §2c), so joint retrieval optimality is NOT claimed.
OPEN (not found, not claimed): general greedy-MV optimality for true P_err
fails in general (coordinates interact through the margin sum); no
counterexample was constructed in this pass — recorded as open, with the
conjecture that conflation interactions like §5 can break greedy from some
starting allocations.

## 7. Threshold / shared-metadata accounting (no fake 12-byte claim)

Per-doc payload B = Σb_j is NOT the full cost. Per allocation (see
`results.json:metadata_accounting`):
(1,1)/(1,1,1): 0 thresholds, 0 shared bits. (2,0)/(2,1,0): 1 threshold value
t_j at precision T (e.g. 8-bit log-quantized or 32-bit float) PLUS the index
map of which coordinates were upgraded. At programme scale: 48x2-bit at
96 payload bits needs 48 per-coordinate thresholds (or 1 global t plus the
documented decision to share it, plus 48 index bits if the subset is
per-archive). 96x1 needs 0. Any E2 report must tabulate payload bits and
threshold/shared bytes in SEPARATE columns; the "12-byte" figure is payload
only (same exclusion the brief already discloses for SIGN96 vs float96).

## 8. Failed attempts and falsifications (recorded, not hidden)

- F1: first hand-derivation predicted P_A(1,1) = 0 ("spread is lossless").
  `verify.py` returned 1/14. Root cause: same-sign conflation — 1-bit maps
  {3,1} → 2, so ΔH = ±2 pairs estimate as ΔĤ = 0 and tie. The code was right;
  the proof in §4 is the corrected version. Lesson: conflation damage has TWO
  faces (magnification flips as in §5, and same-sign ties as here).
- F2: first hand-derivation predicted P_B(1,1,1) = 1/15, omitting the
  (0,0,ΔC3≠0) tie-tax (1/32 numerator mass). Code returned 1/10; corrected
  derivation in §5. Both errors were mine, both caught before reporting —
  this is why the report reproduces derivations instead of citing code output.
- F3 (attempted, abandoned): a symmetric-query variant (binarized q) was
  considered to match the frozen protocol exactly, but it entangles query
  quantization with doc-bit value and doubles the enumeration state; parked
  as a named variant in the E2 spec rather than pursued half-rigorously.
- Robustness tried: threshold sweep t ∈ {3/2, 2, 5/2} leaves all Setup-A
  orderings identical (check A5) — expected, since every t ∈ (1,3) keeps the
  2-bit code lossless on this support; threshold SENSITIVITY on continuous
  laws is untested (listed in §11).
- Circularity check: the true order is defined by full-precision scores with
  the allocation playing no role; error is measured against it. No assumption
  encodes the desired outcome. Finite computation is used as proof ONLY for
  the stated finite instances (exact ℚ enumeration = proof by exhaustion);
  nothing universal is claimed from it.

## 9. Sources, scope, and novelty limits

- Reused (background, not claimed): MATH-1 Level-1 exact tie identity and the
  conditional-uniform-tie protocol facts (`prereg_race_2026-09-13/math1/`
  `math1_report.md` §1a); the frozen tie/centre/anchor facts from the audit
  and cert reports (§1 citations); heterogeneity-paper Prop 5b/Cor 3/F-G
  framing as INTUITION source (`lit_scan_2026-09-13/...` §1, §5, Table 4/5).
- Added here (candidate-genuine, bounded): (a) pairwise-error (not fidelity,
  not MSE) formulation with explicit quantizer/query/tie/budget conventions;
  (b) THEOREM D divergence + highest-variance counterexample with exact
  rationals; (c) paired gain/loss regimes in one framework; (d) MV/SV
  criterion with named surrogates and explicit non-optimality boundary;
  (e) separate threshold/shared-cost accounting rule.
- NOT claimed: literature priority (per brief, prior novelty statements are
  provisional; no priority review was performed — no network, no new search);
  any transfer to LME/LoCoMo/REALTALK/PerLTQA numbers; any universal
  losslessness or floor (out of reach per cert report §1(a)/(d)); JL-based
  bounds (deliberately unused); learned/adaptive allocation (stays closed).
- Scope: two SYNTHETIC instances, one fixed query each, d ≤ 3, b_j ≤ 2,
  asymmetric scoring. Everything else is conjecture or future work.

## 10. One falsifiable future experiment (SPECIFICATION ONLY — not run)

E2-RANK (frozen LME C96/qC caches + frozen producer; read-only benchmark use):
arms = (i) native 96x1 symmetric Hamming (anchor 0.5419751773049645, gate:
reproduce to ≤1e-12 or stop); (ii) 48x2 top-48-variance sign–magnitude,
per-archive t_j = median|C_j|, asymmetric full-q inner-product scoring,
20-trial random ties; (iii) 48x1 same-48-coords ablation (bits-vs-coords
separation); (iv) 48x2 spread-48. Report payload bits AND threshold/shared
bytes in separate columns (§7). Falsification rule (pre-register before
running): magnitude-bit gain is CONFIRMED iff FR(ii) − FR(iii) > +1.0pp with
paired-bootstrap 95% CI excluding 0 AND the pessimistic/expected/optimistic
tie re-resolutions agree in sign (audit1_cont convention audit); if
FR(ii) − FR(iii) ≤ 0, the loss regime (Setup-A-like: sacrificed sign coords
carried the margin) is confirmed for this benchmark/codec — either outcome is
a result. Symmetric-query 48x2 is a SEPARATE arm, not a substitute. This spec
is unfalsified-until-run and claims nothing until then.

## 11. What is NOT proven; exact reproduction

Not proven: optimality of greedy-MV for true P_err (§6 OPEN); threshold
sensitivity on continuous laws; anything about real benchmark data (M1 is
known-false there); symmetric-query behaviour; mixed 64x1.5 allocation
(mentioned in lit scan E2 — untouched here); cross-benchmark transport.
Negative result honesty: no universal "48x2 beats 96x1" or reverse theorem
was found, nor should one be expected — the answer is provably
instance-dependent already at d = 2 (THEOREM D).
Reproduction (executed this session, stdlib only):
  $ cd /home/mdp/muse-work/math-bit-allocation && python3 verify.py
  === bit-allocation toy verification ===
  PASS A1_MSE_prefers_2_0 :: MSE(2,0)=1/4 < MSE(1,1)=1
  PASS A2_rank_prefers_1_1 :: P(1,1)=1/14 vs P(2,0)=2/7
  PASS A3_drop_H_beats_upgrade_H :: P(0,2)=3/14 < P(2,0)=2/7
  PASS A4_P20_equals_2_over_7 :: P(2,0)=2/7
  PASS A5_threshold_robust_t_in_(1,3) :: t=3/2,2,5/2 all give P(2,0)=2/7, P(1,1)=1/14
  PASS A6_greedy_MV_picks_L_first :: MV_L(0,0)=2/7 > MV_H(0,0)=1/7
  PASS B1_P111_equals_1_over_10 :: P(1,1,1)=1/10
  PASS B2_P210_equals_1_over_30 :: P(2,1,0)=1/30
  PASS B3_concentration_wins_ranking :: P(2,1,0)=1/30 < P(1,1,1)=1/10
  ALL_PASS = True
  (exit 0; wrote results.json — 9/9 checks, all exact ℚ, no numpy/scipy import.)
Completion claim rests on that executed run, not on the derivations alone.
