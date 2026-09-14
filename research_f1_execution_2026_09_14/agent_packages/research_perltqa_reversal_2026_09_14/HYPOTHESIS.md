[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# HYPOTHESIS — frozen BEFORE the cross-benchmark test (PREPARED, NOT ACCEPTED)

Frozen on PerLTQA-side evidence only (`evidence/results_perltqa.json`, `REVERSAL_FACTS.md`).
DO NOT EDIT after running `analysis.py --parts xbench`; corrections belong in
`CROSS_BENCHMARK_TEST.md` § "Post-hoc corrections" (separate section, hypothesis text stays).

## H1 (primary, falsifiable): native-Hamming boundary-competition density sets the Delta sign

Statement: queries whose native SIGN96 K=3 boundary is crowded — many documents tied at the
cutoff (large `tie_bc`), zero Hamming margin to the next rival (`gap==0`), boundary-tie flag set —
lose under SIGN relative to centered float; queries with clean boundaries win. Mechanism sketch:
sign quantization collapses fine float separations, so a gold document sitting in a dense Hamming
neighbourhood is flipped out of the top-3 by tie-break noise, while a gold document isolated in
Hamming space survives quantization. Same archive, different query → different neighbourhood → sign flip.

Predictor (uses ONLY native-ranking fields, never Delta):
- Rule A: predict Delta<0 iff `tie==1`, else Delta>0.
- Rule B (= A by construction): predict Delta<0 iff `gap==0`.
- Rule C: predict Delta<0 iff `tie_bc>=3`.
- Association: Spearman rho(Delta, tie_bc) < 0 and rho(Delta, gap) > 0, overall and within each section.

Falsification criteria (decided now):
- F1 (levels): section ordering must satisfy denser-competition ⟺ more-negative-Delta. Concretely,
  events (most negative Delta) must show the highest tie rate / tie_bc and smallest gap; profile the reverse.
- F2 (per-query): rules must beat the always-predict-majority baseline on nonzero-Delta queries,
  overall and within profile and events separately.
- F3 (cross-benchmark, tested next in CROSS_BENCHMARK_TEST.md): the same rules/associations must hold
  directionally on LongMemEval and REALTALK. If H1 predicts a reversal pattern where none occurs
  (e.g. high-tie strata winning on LME/REALTALK), H1 is wrong. LoCoMo per-query recomputation is
  expected UNAVAILABLE (no committed per-query float surface); if so that leg is recorded as untestable,
  not as support.

PerLTQA-side pre-registration of the awkward fact: at section-mean level the ordering ALREADY looks
H1-hostile (events: lowest tie rate 0.2708, lowest mean tie_bc 1.5863, largest mean gap 1.7092, yet most
negative Delta; profile: densest/smallest-gap, yet positive). H1 therefore enters the cross-benchmark
test as the underdog: it can survive only if per-query/character-level structure rescues it
(e.g. within-events modulation) while conceding the level shift needs a second factor. A clean kill is
an acceptable deliverable.

## H0 (negative control): gold multiplicity drives the reversal

Statement: multi-gold queries behave differently and compose the headline. Predictor: gold_size>1.
Status at freeze: ALREADY KILLED on PerLTQA — profile/events/social are 100% single-gold
(`REVERSAL_FACTS.md` §4), so multiplicity cannot separate +20.44 from -12.41. Retained only to check
the dialogues section (84.7% multi-gold, Delta -1.48) and as a cross-benchmark covariate (LME/REALTALK
gold_count groups are computed in the xbench leg).

## P64 baseline (descriptive, explicitly NOT causal, not competing as mechanism)

sign(P64)=sign(BOT64-TOP64) predicts sign(Delta): 68.9% on nonzero-both queries overall
(profile 86.4%, events 77.1%, social 62.1%, dialogues 62.6%), 29/30 characters, 4/4 sections.
Per E1's own verdict this is a regime marker, not a cause; it is included so H1's added value
(or lack of it) is judged against the strongest retrieval-contrast predictor available, including the
majority-class prior (nonzero-Delta queries are 66.0% losses overall: 1473/(757+1473)).

## What H1 cannot say (declared limits at freeze)

- Vector-level properties (query norm, participation ratio, axis alignment, gold-doc norm, float margins)
  are UNAVAILABLE-UNDER-CACHE-GAP; H1 tests only the ranking-geometry shadow of those quantities.
- H1 says nothing about WHY profile queries land in (apparently denser yet winning) neighbourhoods —
  answering that needs the pending frozen V2 per-query rows (per-gold strictly-closer-rival and
  gold-distance tie-mass gaps by section, Q-magnitude distributions by section).
- The "predicts 30/30 events but only 23/30 profile" asymmetry, if observed, means: competition
  modulates loss depth inside the losing regime (events slope) while a second, unmeasured factor sets
  the regime level (profile intercept). That reading is licensed only if F3 does not kill H1 outright.
