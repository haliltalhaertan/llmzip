# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# FORMALISATION: the weighting framing

## 1. The structural claim (precise)

CLAIM (programme observation): cosine similarity weights axes by magnitude, so
high-variance axes dominate the FLOAT ranking; Hamming distance on sign bits
weights every axis 0/1, i.e. an implicit UNIFORM re-weighting of axes.

Formalised hypothesis H-W: let each archive have per-axis variance
`v_j = mean_i C_ij^2` (equals variance; VERIFIED: cached C is pre-centered,
column-mean abs max ~1e-16 on probed file). Let a query `q` with gold set `G`
have gold centroid `g = mean_{r in G} C_r` and per-axis query-gold support
`s_j = q_j * g_j` (signed; `sum_j s_j` = unnormalized query-gold dot product,
i.e. the numerator of cosine before normalisation).

H-W predicts: SIGN beats FLOAT exactly when the positive support `s_j`
concentrates on LOW-`v_j` axes (which cosine down-weights), and loses when
support concentrates on HIGH-`v_j` axes (which cosine already emphasises).

## 2. Measurable quantity (frozen choice)

PRIMARY — Q-SPEC (per query): `r_q = Pearson_j(log v_j, s_j)` over the 96 axes.
Benchmark summary `R = mean_q r_q` with 95% CI `mean +/- 1.96 sd/sqrt(n)`.

Why this definition:
- Signed `s_j` (not `|s_j|`): cosine ranking cares about signed support; axes
  with large negative `s_j` push gold DOWN. Signed support is what the
  normalisation in cosine re-weights.
- Null expectation is exactly 0 (random q/g gives E[s_j]=0 per axis), unlike
  `|s_j|`, which correlates with `v_j` mechanically (E|q_j g_j| propto
  sigma_j^2). So any nonzero R is signal, not scale artefact.
- `log v_j`: variances span orders of magnitude; log keeps the correlation
  from being dominated by the top 2-3 axes.

SECONDARY (robustness, same prediction sign):
- Q-ABS: `Pearson_j(log v_j, |s_j|)` (null > 0 mechanically; only ORDERS
  across benchmarks/sections are interpretable).
- Q-CENT: spectral centroid of positive support,
  `cent_q = sum_{j:s_j>0} rank_j s_j / sum_{j:s_j>0} s_j`, rank 1 = highest
  variance. Null ~48.5; <48.5 means support sits high-variance.
- Q-GOLD: `Pearson_j(log v_j, g_j^2)`: do the gold DOCUMENTS themselves live
  in high/low-variance subspaces (query-independent check)?

## 3. Falsification conditions (frozen)

- F1 (section split): profile (+20.36 pp CLAIMED) vs events (-12.39 pp
  CLAIMED) share archives/documents; H-W REQUIRES R_profile < R_events with
  non-overlapping CIs (same ordering required: profile lowest, events
  highest of the four sections). Failure = framing dead.
- F2 (benchmark order): R must order LME/LoCoMo/REALTALK below PerLTQA
  (negative/low vs positive/high). A sign flip in the wrong place = dead.
- F3 (intervention, in PREDICTION.md): whitened cosine must move toward sign.

## 4. Relation to standing facts

- Fact B (CLAIMED): low-variance axes retrieve better on sign-positive
  benchmarks. H-W is the proposed MECHANISM behind B: uniform weighting helps
  exactly because the support lives there. H-W adds the query-side half B
  lacks (B is archive-axis-only; H-W locates the QUERY signal in that
  spectrum) plus the F-split test B never faced.
- Fact C (CLAIMED): Haar rotation destroys the effect. H-W REQUIRES
  axis-dependence, so C is a necessary (not sufficient) condition. Consistent.
- Fact A (CLAIMED): advantage grows with m. Consistent: at small m only top
  axes exist, so uniform re-weighting has nothing to act on.
