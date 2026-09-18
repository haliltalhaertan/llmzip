[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REVERSAL_FACTS — PerLTQA section deltas re-derived first-hand (PREPARED, NOT ACCEPTED)

Source: `origin/research/e1-mechanism-checkpoint-frozen-2026-09-13:campaign_2026_09_13/bench3/b3b_perltqa/results.json`,
read via `git show` (no checkout). Recomputation: `analysis.py` (`perltqa_facts`, `perltqa_within_archive`),
outputs in `evidence/results_perltqa.json` (this namespace).
Metric (VERIFIED in `.../bench3/b3b_perltqa/step2_eval.py` on the same branch):
fractional recall @K=3 averaged over NT=20 random tie-break permutations;
`native` = SIGN96-Hamming, `float` = centered-float96-cosine; Delta_pp = 100*(native-float).

## 1. Byte identity (VERIFIED)

- SHA256 of the bytes we read: `ec9b8b2c7f384fe2f56c72fdc7a7216930a9db35eda2c4441496c8ad401bf958`
  — matches the E1-claimed input hash exactly (`E1_PERLTQA_WITHIN_ARCHIVE_FLIP_RESULT.json:input.results_sha256`,
  `E1_PERLTQA_JOINT_POLARITY_RESULT.json:input.results_sha256`,
  `E1_PERLTQA_TIE_SECTION_RESULT.json` input). Same bytes E1 used: VERIFIED.

## 2. Headline + four section deltas — every programme number CONFIRMED

| unit | n (re-derived) | mean native (re-derived) | mean float (re-derived) | Delta pp (re-derived) | programme claim | verdict |
|---|---|---|---|---|---|---|
| overall | 8265 | 0.48894199493081697 | 0.551692074528853 | -6.275007959803608 | SIGN 0.488941994930817 vs float 0.551692074528853 (-6.275) | CONFIRMED (diff ≤1e-14, summation order) |
| profile | 333 | 0.5076576576576577 | 0.3033033033033033 | +20.43543543543544 | +20.435, n=333 | CONFIRMED |
| social_relationship | 844 | 0.7490521327014219 | 0.7571090047393365 | -0.8056872037914609 | -0.806, n=844 | CONFIRMED |
| events | 4346 | 0.6915784629544408 | 0.815692590888173 | -12.411412793373222 | -12.411, n=4346 | CONFIRMED |
| dialogues | 2742 | 0.08543238078162008 | 0.10019511159043444 | -1.4762730808814364 | -1.476, n=2742 | CONFIRMED |

Composition check (VERIFIED): sum(n_s * Delta_s)/8265 = -6.275007959803619 vs overall
-6.275007959803608; residual -1.15e-14 pp. The -6.275 headline is exactly the section composition. Total n = 333+844+4346+2742 = 8265 VERIFIED.

E1 cross-checks (CLAIM → VERIFIED match): `E1_PERLTQA_TIE_SECTION_RESULT.json:by_section`
(20.435435435435437 / -0.8056872037914692 / -12.411412793373216 / -1.4762730808814348) and
`E1_PERLTQA_JOINT_POLARITY_RESULT.json:overall.mean_delta_pp` (-6.2750079598036175) agree to ≤1e-11.

## 3. Within-archive flip counts — CONFIRMED exactly

Re-derived character×section means reproduce `E1_PERLTQA_WITHIN_ARCHIVE_FLIP_RESULT.json:counts` field-for-field
(VERIFIED, all integers equal): 30 characters; 30 archives with profile+events;
profile Delta>0 in 23/30; events Delta<0 in 30/30; profile P64>0 in 28/30; events P64<0 in 30/30;
joint Delta flip 23/30; joint P64 flip 28/30; both flip together 22/30;
115 nonzero character×section pairs, 87 same-sign (0.7565217391304347).
The "different archives" explanation is REFUTED first-hand: same document matrix C96 per character
(`step2_eval.py`: one `arch[char]` structure serves all sections), yet the Delta sign flips by query section.

## 4. New first-hand facts (not in the E1 JSONs)

- Per-query Delta is 73.0% tied: overall W/T/L = 757/6035/1473 on sign(Delta)
  (`evidence/results_perltqa.json:facts.wtl`). By section — profile 93/221/19, social 85/662/97,
  events 230/3303/813, dialogues 349/1849/544. Profile wins via more wins AND fewer losses;
  events loses via losses (18.7% of its queries) against 76.0% ties.
- `tie` ⟺ `gap==0` exactly (ruleA and ruleB agree on all 8265 queries): construction identity in
  `step2_eval.py` (tie = bc>slots; gap = sd[K]-sd[K-1]; gap==0 iff bc>slots). VERIFIED in our recomputation.
- Gold cardinality (VERIFIED from per-q `gold_size`): profile/events/social are ALL single-gold
  (333/333, 4346/4346, 844/844 with gold_size==1); ONLY dialogues is multi-gold
  (2322/2742 multi, values 1..30), matching the R2 audit's multi_gold_n=2322 (CLAIM in
  `E1_V2_COMPETITION_CORRECTED_RESULT.json:benchmarks.PERLTQA.sections.dialogues`, cross-checked).
  Consequence: gold multiplicity CANNOT explain the profile/events flip (both single-gold) — H0 killed in §5.
- Float-commitment asymmetry (single-gold sections): float varies 0.303→0.816 across profile/social/events
  while native varies only 0.508→0.749. Delta's section ordering is dominated by float-level variation,
  not by SIGN-level variation. Descriptive, not causal (Delta contains float by construction) — recorded as
  context for the skeptic, not as mechanism.
- Committed-cache boundary (honest limit): per-query vectors (qC/C96), hence query norm, participation
  ratio, high/low-variance-axis alignment, gold-doc norm/spread, and float-side margins are
  UNAVAILABLE-UNDER-CACHE-GAP — the eval-time `/tmp/b3b/cache_*.pkl` vectors were never committed, and E1
  checkpoint §8 plus the R2 report both record the full per-query V2 rows as still pending. What the caches
  DO permit (distributions, not just means) is in `evidence/results_perltqa.json:geometry` and §5 below.

## 5. Section distributions that matter for the hypothesis (VERIFIED, from `geometry`)

- Native-competition fields overlap almost completely across sections: tie_bc p50/p75/p90 = 1/2/3 in ALL
  four sections; gap p50 = 1 in ALL four. Level differences are small and point the H1-hostile way:
  events (biggest loser, -12.41) has the LOWEST tie rate (0.2708), LOWEST mean tie_bc (1.5863), LARGEST mean
  gap (1.7092); profile (winner, +20.44) has tie rate 0.3123, mean tie_bc 1.7237, SMALLEST mean gap (1.1742).
- Character level, same archive: profile-Delta>0 chars (23) have HIGHER mean tie rate (0.3126) than
  profile-Delta≤0 chars (7, 0.2473) — backwards under any "ties hurt SIGN" story. Events Delta spans
  -27.08..-0.23 (all<0) with tie rates 0.18..0.37.
- Our independent code reproduces E1's character-level tie_rate-vs-Delta Spearman values for profile
  (+0.2475) and events (-0.3486) to 4dp (CLAIM in `E1_PERLTQA_TIE_SECTION_RESULT.json`, second-route check).

## 6. Branch-count note (non-load-bearing discrepancy)

Task text says 137 remote refs / ten `origin/research/e1-*` branches. VERIFIED this session:
140 remote refs; 8 `origin/research/e1-*` + 2 `origin/audit/e1-*` = 10 E1 refs total.
All reads above use the frozen checkpoint branch; the discrepancy affects nothing.
