# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Candidate mechanisms for the SIGN96 advantage (6 candidates, ranked)

Assertion labels: **VERIFIED** = computed this session (see TEST_RESULT.md);
**CLAIM** = stated in the programme brief; **RELAYED** = second-hand from brief data.
Controls reproduced exactly this session: LongMemEval Delta +10.053783 pp (VERIFIED),
PerLTQA profile +20.355 / events −12.394 pp (VERIFIED).

Notation: sign arm = Hamming on (C≥0) vs (qC≥0); float arm = cosine on raw centered C;
Delta = FR@3(sign) − FR@3(float), in percentage points (pp).

---

## Rank 1. C1 — Variance-democracy ("one axis, one vote" over anisotropic axes)

1. MECHANISM: Embedding axes have highly unequal variances, so cosine similarity is a
plutocracy: a few high-variance axes contribute most of every dot product. Hamming distance
is a democracy: each axis gets exactly one vote regardless of variance. Wherever retrieval
signal lives disproportionately in low-variance axes, the democracy counts votes the
plutocracy rounds down to zero, and sign wins.
2. EXPLAINS: (A) VERIFIED direction — the m-gain is the enfranchisement of low-variance
axes: at m=8/16 only high-variance axes vote and both arms see the same plutocratic
geometry (sign loses); each added low-variance axis is ~0 votes for float but 1 full vote
for sign. (B) Both arms agree on *which* axes matter because axis informativeness is
geometry; the arms differ only in how votes aggregate — exactly why the float arm shows the
same axis effect, larger. (C) A Haar rotation re-mixes variance across axes, destroying the
anisotropy the democracy exploits, while preserving cosine geometry — so only sign
collapses. (D) AQS re-weights votes by |q_j|, reintroducing plutocracy inside tied shells,
and therefore commits wrongly. Shared m-slope of profile and events in TEST-M1 (both rise
with m: profile −1.35→+20.36, events −19.31→−12.39, VERIFIED).
3. FORBIDS: A benchmark (or PerLTQA section) whose Delta(m) curve is flat or *falling* in m
over 16→96 while computed with top-variance-ranked axes. Numerically: slope(Delta_96 −
Delta_16) ≤ 0 on any of the four benchmarks kills the enfranchisement story. (Observed:
LME +21.9, LoCoMo +10.8, REALTALK +8.9, PerLTQA +5.7 — CLAIM from brief; profile +21.7 and
events +6.9 this session, VERIFIED.)
4. WHY THE NINE DEATHS ARE CONSISTENT: #1 (variance heterogeneity per se) died because
heterogeneity without the voting-rule interaction predicts nothing — C1 is the interaction,
not the marginal. #7 (ALIGN) bet on *high*-variance axes; C1 bets the opposite tier, so
ALIGN's 0/30 deciles is C1-consistent. #8 (gap levels) measured gaps in the plutocratic
metric, which C1 says is the wrong geometry for the sign arm. #9 (doc-norm) is cosine's
normalization, orthogonal to C1's per-axis vote weights. #5 (Hamming-boundary density)
measured crowding, not vote weighting. #2/#3/#4/#6 never touched the aggregation rule.
5. CHEAPEST DECISIVE TEST (INTERVENTION — RAN this session): dimension-matched budget
curves restricted to PerLTQA `profile` vs `events` sections separately (same archives,
same ranking, m ∈ {16,32,48,64,96}). Script:
[run_tests.py](/home/mdp/muse-work/brainstorm-mechanism/run_tests.py).
6. PREDICTION BEFORE TESTING (directional, recorded before running): profile crosses to
positive at m ≤ 64 (it behaves like a sign-positive benchmark); events stays negative at
all m. OBSERVED (VERIFIED): profile −1.35/−3.80/+1.39/+6.29/+20.36 (crosses 32→48);
events −19.31/−18.62/−16.08/−14.21/−12.39 (never crosses). Direction confirmed — but with
a major amendment (see TEST_RESULT.md): the two curves share the *slope*; the reversal is
a ~20–33 pp *level* shift C1 alone does not explain. C1 needs a companion for the level.

---

## Rank 2. C2 — The influence-function bridge (only the per-axis nonlinearity matters)

1. MECHANISM: Write both arms as Σ_j f(q_j·d_j) over normalized products. Float uses
f(x)=x (identity); sign uses f(x)=sign(x) (hard clip). The entire Delta is the choice of
influence function f: identity lets a few large-magnitude axes outvote dozens of small
agreements, while any saturating f caps their influence. Nothing else — not centering,
not normalization, not ties — carries the effect.
2. EXPLAINS: (A) Adding low-variance axes adds small-|x| votes that identity down-weights
and saturating f counts fully. (D) AQS (f(x)=sign(d_j)·q_j, saturating on one side only)
is a half-bridge: it caps doc magnitudes but not query magnitudes, landing at a worse
operating point (−3.56 pp, CLAIM). (B)-partially: axis ranking is shared because the
products q_j·d_j live in the geometry; only f differs. Plus one new VERIFIED fact: an
interior clip t=1e-3 beats *both* endpoints on LME.
3. FORBIDS: Clipped-cosine Σ clip(p_j,±t) at small t recovering <2 pp of the LME gap
(peak−cos = +12.099 ± 1.594 pp VERIFIED, t=+7.59 — the forbiddance is far away). Strong
form additionally forbade non-monotonicity in t; the data VIOLATED the strong form
(peak at t=1e-3, dip toward t→0), so C2 survives only amended: the optimal f is soft
saturation, not hard sign.
4. WHY THE NINE DEATHS ARE CONSISTENT: every death was a correlational per-query rule;
C2 is a global functional interpolation with a single scalar t, fitted nowhere and
evaluated on all queries at once — there is no per-query rule to overfit. #3 ("17x
unstable") is C2-consistent: sign flips are exactly large-|x| events being capped.
#8 died measuring gaps under f(x)=x; C2 says re-measure gaps under saturating f.
5. CHEAPEST DECISIVE TEST (INTERVENTION — RAN this session): sweep clip threshold t over
normalized per-axis products on all 470 LongMemEval queries, endpoints = exact sign and
cosine arms. Same script as C1.
6. PREDICTION BEFORE TESTING: FR@3(t) rises monotonically as t falls, from 0.4416
(cosine) to ≈0.5421 (sign). OBSERVED (VERIFIED): 0.4416 → 0.5285 → 0.5441 → 0.5603 →
**0.5626 (peak, t=1e-3)** → 0.5482 → 0.5454 → 0.5473 (t→0) vs sign 0.5421. Monotonicity
holds from ∞ down to 1e-3, then breaks: peak−sign = +2.046 ± 0.975 pp (t=+2.10,
suggestive, not conclusive); peak−cos = +12.099 ± 1.594 pp (decisive). C2's weak form
(influence function is load-bearing) is strongly supported; its strong form (sign is the
optimal limit) is rejected — the optimum is interior.

---

## Rank 3. C3 — Query-as-mixture (the PerLTQA flip is query construction, not documents) ⭐ handles fact F

1. MECHANISM: An `events` query ("what happened when…") is semantically a *mixture* of
many documents' content: its vector is approximately a positive linear combination of the
docs it touches. Cosine is linear and therefore reads mixtures faithfully; sign
thresholding is a coordinate-wise nonlinearity that scrambles mixtures. A `profile` query
("what is X's occupation") is *atomic*: it points at one or two documents, and exact
orthant match is precise. Same archive, same documents — the query's construction flips
the winner.
2. EXPLAINS: (F) directly and exclusively among these candidates: profile (+20.36) vs
events (−12.39) on shared archives and a shared document matrix (CLAIM), with
within-character sign consistency (events negative 30/30, profile positive 23/30, CLAIM).
(D): AQS (linear projection sign_codes·qC) turns every query mixture-like at decision
time — it helps exactly where queries are mixtures and hurts where they are atomic; net
−3.56 on atomic-heavy LongMemEval (CLAIM). (G)-as-warning: mixture-queries get *more*
mixture-like as archives grow, so the sign advantage should decay with archive size on
event-style queries.
3. FORBIDS: Synthetic-query intervention on one fixed archive: build single-doc
pseudo-queries (q = C[r] + small noise, gold = {r}) and 5-doc-mixture pseudo-queries
(q = Σ_{r∈S} w_r·C[r], gold = S) for the same rows. C3 forbids Delta(single-doc) ≤ 0 AND
forbids Delta(mixture) ≥ Delta(single-doc). Kill line: mixture pseudo-queries still
favoring sign by ≥ the single-doc margin. Predicted numbers: Delta(single) > 0,
Delta(mixture) < 0, separation ≥ 5 pp.
4. WHY THE NINE DEATHS ARE CONSISTENT: #4 (gold multiplicity) died because it counted
gold-set *size*; C3 is about query *construction* (atomic vs mixture), which is
near-orthogonal to |gold| — consistent with single-gold profile and events differing by
33 pp (CLAIM #4-killer). #5 died measuring Hamming-space density; mixtures live in
continuous space. #7 (ALIGN) correlated queries with high-variance axes; a mixture query
mechanically aligns with high-variance axes (sums concentrate there), so ALIGN's failure
is expected under C3 once mixture-ness, not alignment, is the driver.
5. CHEAPEST DECISIVE TEST (INTERVENTION — NOT RUN, next in queue): synthetic pseudo-query
protocol above, on 2 PerLTQA character archives × 200 pseudo-queries each; no new data
needed, uses cached C matrices only.
6. PREDICTION BEFORE TESTING: Delta(single-doc pseudo) ≥ +5 pp; Delta(5-mixture pseudo)
≤ −5 pp; same rows, same archive.

---

## Rank 4. C4 — Spurious-magnitude distrust (large |C_ij| is mostly query-irrelevant)

1. MECHANISM: On high-variance axes, a document's large |C_ij| encodes what the document
*is about in general* (its topic/length energy), not what any particular query asks.
Cosine trusts these magnitudes, so retrieval is dragged toward high-energy distractors;
sign discards every magnitude and can therefore only be dragged by vote counts. Taming
magnitudes without quantizing should recover most of the sign gain inside the float arm.
2. EXPLAINS: (A) low-m tail axes have small magnitudes to distrust, so tamed and raw
float converge there while raw float suffers at high-m — sign's edge accumulates with m.
(D) AQS restores raw |q_j| magnitudes and re-admits the distractor drag (−3.56, CLAIM).
(B)-partially: bottom-variance axes retrieve better for both arms (CLAIM) because they
carry the least spurious energy.
3. FORBIDS: Per-axis rank-Gaussianized (or 1%-winsorized) C fed to plain cosine on
LongMemEval recovering <2 pp of the +10.05 pp gap kills C4; C4 demands ≥5 pp
(≥50% of the gap) recovered by magnitude-taming alone with zero quantization.
4. WHY THE NINE DEATHS ARE CONSISTENT: #2 (continuous kurtosis ≈0.93, RELAYED) is
C4-neutral: C4 needs only that *large* magnitudes be query-irrelevant, not heavy-tailed.
#9 died at section level (profile: informative norm, sign still wins); C4 survives
because it is about *per-axis* magnitudes, and archive-level norm AUC does not constrain
per-axis drag — though honestly this is C4's tightest corner (see TOP_PICK.md attack).
#1/#7 die the same way as under C1 (marginals, wrong tier).
5. CHEAPEST DECISIVE TEST (INTERVENTION — NOT RUN): per-axis rank transform of each
archive's C (map each column through its own empirical CDF → standard normal), then
exact cosine FR@3; one scalar outcome on LongMemEval.
6. PREDICTION BEFORE TESTING: rank-Gaussianized float reaches FR@3 ≥ 0.49 on LongMemEval
(i.e. recovers ≥50% of the 10.05 pp gap), with Hamming ties untouched (tie rate stays
at the float arm's ~0, proving the gain is magnitudes, not ties).

---

## Rank 5. C6 — Continuous fan-out asymmetry (broad queries need ranking, narrow ones need matching)

1. MECHANISM: An events query sits inside a broad continuous neighborhood: dozens of
documents are moderately cosine-similar (shared narrative vocabulary), and the gold is
one face in a crowd — fine-grained magnitude ranking (float) wins. A profile query sits
in a narrow neighborhood: two or three documents agree in sign pattern and the rest do
not — exact orthant matching (sign) wins. The driver is continuous-space fan-out, a
property of the query, invisible to Hamming-space statistics.
2. EXPLAINS: (F) the level shift (broad events −12.39 vs narrow profile +20.36, CLAIM +
VERIFIED controls). (E): the BOT64-competition correlate triples on sign-positive
benchmarks once Delta==0 mass is removed but stands still on PerLTQA (CLAIM) — because
PerLTQA mixes two fan-out regimes whose correlations cancel. (D): in broad neighborhoods
the tied shell is genuinely ambiguous and any commit is a gamble; conservatism (exact
expectation over ties) is the least-bad policy.
3. FORBIDS (observational, cheap): for events queries, per-query Delta vs continuous
gold-mass-in-top-50 (fraction of |gold| inside the query's 50 continuous nearest
neighbors, float geometry) must correlate NEGATIVELY (broad → float wins), rho ≤ −0.15,
while on profile queries |rho| ≤ 0.10. A zero or positive events correlation kills C6.
4. WHY THE NINE DEATHS ARE CONSISTENT: #5 is the key one — it died measuring density in
*Hamming* space (tie rate, boundary counts, gaps), where events looks sparsest. C6
predicts exactly that paradox: a query can be Hamming-sparse (few exact ties) and
continuous-broad (many moderate-cosine neighbors) simultaneously, because Hamming
thresholds away the moderate-similarity mass that cosine sees. #5's killer numbers
(events: lowest tie rate 0.2708, largest gap 1.7092 — RELAYED) are C6-consistent, not
C6-hostile. #4 died on |gold| counts; fan-out is about the distractor field, not gold
count.
5. CHEAPEST DECISIVE TEST (observational): two correlations on cached PerLTQA
(events/profile) — no representation change; ~10 lines on top of run_tests.py.
6. PREDICTION BEFORE TESTING: rho_events ≤ −0.15; rho_profile ∈ [−0.10, +0.10].

---

## Rank 6. C5 — Orthant-crowding / scale (sign's resolution is fixed at 2^m cells)

1. MECHANISM: The sign arm can distinguish at most 2^m orthants; the float arm has
continuous resolution. At small m (8–32) many documents share each orthant, collisions
are frequent, and sign loses everywhere (CLAIM-A, all four benchmarks negative at m≤32).
Adding axes subdivides orthants exponentially, collisions fall, sign gains. At fixed m=96
the residual Delta is set by archive size N: larger N → more collisions → smaller Delta.
2. EXPLAINS: (A) the universal low-m loss and high-m gain with a single parameter
(collisions), no variance story needed. (G) the programme's central scale warning: it
predicts the +10 pp LongMemEval effect *decays* toward and past zero as N → 100K–10M —
the only candidate that sticks its neck out about the sealed experiment's regime. (F)-as-level:
broad (events) queries land in occupied orthants; narrow (profile) queries land alone.
3. FORBIDS: archive-subsampling intervention — randomly keep 1/2 and 1/4 of each
LongMemEval archive's documents (gold always retained), re-measure Delta. C5 forbids
Delta(full) ≥ Delta(1/2) ≥ Delta(1/4); kill line: Delta unchanged or shrinking as N
shrinks (subsampling slope ≤ 0). Predicted: Delta rises ≥2 pp per halving.
4. WHY THE NINE DEATHS ARE CONSISTENT: #5 measured *local* K=3 boundary ties; C5 is
about *global* orthant occupancy (docs sharing the query's exact code) — a different
statistic, and local ties need not track global occupancy when N ≪ 2^96 (occupancy is
~0 everywhere; the action is in near-code shells, which is why C5 is ranked last: at
N≈500/2^96 the literal collision story is quantitatively thin and must lean on
near-collisions). #6 (lag-2 speaker proximity, RELAYED) is near-shell structure C5
expects. #8 (gap sign same, Delta opposite): gaps are local, occupancy is global.
5. CHEAPEST DECISIVE TEST (INTERVENTION — NOT RUN): N-subsampling sweep on LongMemEval
(full/half/quarter × 3 seeds), exact-tie FR@3 throughout.
6. PREDICTION BEFORE TESTING: Delta(1/4) − Delta(full) ≥ +4 pp.

---

## Ranking rationale (span × cheapness)

| rank | candidate | facts spanned | test cost | status |
|------|-----------|---------------|-----------|--------|
| 1 | C1 variance-democracy | A,B,C,D + M1 slope | cheap (RAN) | supported, needs level-companion |
| 2 | C2 influence bridge | A,D,B + overshoot | cheapest (RAN) | weak form supported, strong form rejected |
| 3 | C3 query-as-mixture | F,D,(G) | moderate (synthetic) | untested, only F-level theory |
| 4 | C4 magnitude distrust | A,D,B | cheap (one transform) | untested |
| 5 | C6 fan-out asymmetry | F,E,D | cheapest (2 corrs) | untested |
| 6 | C5 orthant crowding | A,G,F-level | moderate (subsample) | untested, thin at N≪2^96 |

Two of six tests are INTERVENTIONS already run (C1, C2); three further intervention
protocols are specified but unrun (C3, C4, C5); C6 is observational.
