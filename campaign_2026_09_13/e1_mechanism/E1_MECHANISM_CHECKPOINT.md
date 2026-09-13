# E1 mechanism checkpoint — what survived the adversarial narrowing

Labels: **[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**.

Status: **CHECKPOINT CANDIDATE / POST-HOC MECHANISM NARROWING / NOT CAUSAL / NOT INDEPENDENTLY AUDITED**.

Base campaign snapshot: `findings/campaign-2026-09-13 @ 8f6e0fab4c2fb2eeb8dcd5087376a6736e1865f1`.
E1 V1 frozen design: `d1e429ccc227f233389dfc97c368cbea3752b1ec`.
E1 V2 frozen design: `775a09c1ba6fd8c28f1e98ec1826d31a7f2c3484`.

Task4F1 remained untouched.

## 1. Why E1 changed the question

The campaign already established that SIGN96 can beat centered float96 strongly on LongMemEval and REALTALK, while verified PerLTQA reverses the ordering. The scientific target is therefore no longer a universal statement such as “SIGN is better than float”. It is:

> **what changes the sign of SIGN96 − centered-float96 across retrieval regimes?**

A post-hoc bridge noticed that the sign of `BOT−TOP` retrieval polarity matches the sign of `SIGN−float` in six already-observed benchmark/section units. That bridge is discovery evidence only; it is not confirmatory.

## 2. Mechanism stories tested and narrowed

### A. “Low-variance axes are individually more informative” — REFUTED

Pre-existing round-1 LongMemEval evidence already says all 96 axes have positive marginal discrimination and the strongest individual axes tend to be high-variance axes. Yet TOP48 is much worse jointly than BOT48/random/spread.

Therefore the phenomenon is not licensed as “low-variance axes contain more semantic signal”.

### B. “A single scalar archive heterogeneity score explains SIGN advantage” — NOT SUPPORTED on LME

A 470/470 exact join between canonical T4C2 per-question outcomes and pre-existing Task1 geometry gave Spearman correlations with per-question SIGN−float delta:

- `cv_sigma`: −0.0096;
- top-32 variance share: +0.0213;
- sign entropy: +0.0336;
- archive N: +0.0084;
- continuous-coordinate correlation summaries: weak negative, about −0.07 to −0.10.

So archive-wide concentration as a one-number explanation is essentially absent inside LongMemEval.

### C. “The amount/concentration of marginal axis signal explains SIGN advantage” — NOT SUPPORTED on LME

Using the pre-existing 470×96 gold-informed per-axis discrimination matrix:

- positive-signal effective dimension rho ≈ +0.037;
- positive top-16/top-32 share ≈ −0.03;
- total positive mass ≈ +0.030;
- largest magnitude among the tested summaries was only about −0.114 for negative mass.

Marginal single-axis signal distribution is therefore not a useful query-level explanation.

### D. “BOT axes are specially complementary in the full code, and that explains Delta” — SPECIFIC QUERY-LEVEL VERSION NOT SUPPORTED on LME

The pre-existing `drop[q,j]` surface measures the FR when one bit is removed from the full 96-bit code. BOT bits have larger average contextual drop-loss than TOP bits, while TOP bits are slightly stronger alone. However:

`rho(Delta_q, drop_loss_BOT − drop_loss_TOP) ≈ +0.030`.

So the simple differential-complementarity prediction is practically null. Absolute TOP and BOT drop importance both correlate positively with Delta, but their difference does not explain the variation.

### E. “Simple native Hamming boundary-tie rate causes the PerLTQA reversal” — REFUTED

PerLTQA verified results show:

- profile: tie rate 31.23%, SIGN−float +20.44pp;
- events: tie rate 27.08%, SIGN−float −12.41pp.

Events loses despite **lower** native boundary-tie incidence. Untied events still lose by about −9.81pp; untied profile still wins by about +19.65pp.

Ties amplify some losses — tied events are about −19.41pp — but they do not create the profile/events sign reversal.

## 3. The signal that survived: joint retrieval polarity `P64 = BOT64 − TOP64`

The same already-computed TOP/BOT retrieval arms allow a stronger test without rebuilding representations.

### Query level: consistently positive but weak

Spearman `rho(Delta_q, P64_q)`:

- LongMemEval: **+0.108**;
- PerLTQA: **+0.109**;
- REALTALK: **+0.075**.

This repeatability is interesting, but the effect is too weak to support an individual-query predictor story.

### Aggregated regime level: materially stronger

PerLTQA, aggregated by character/archive (30):

- Spearman ≈ **+0.319**;
- P64 and SIGN−float have the same sign in **29/30** characters.

REALTALK, aggregated by chat (10):

- Spearman ≈ **+0.418**;
- same sign in **9/10** chats.

PerLTQA section means all have matching signs:

- profile: Delta positive, P64 positive;
- social: both negative;
- events: both negative;
- dialogues: both negative.

REALTALK category means have the same rank order for Delta and P64, but n=3 and this is descriptive only.

**Licensed interpretation:** `BOT−TOP` retrieval polarity behaves more like a **regime marker** than a strong per-query predictor.

## 4. Semantic section is not the whole regime variable

To separate semantic composition from archive variation, P64−Delta was re-evaluated across character/chat units **within fixed semantic strata**.

PerLTQA, 30 characters within each section:

- profile rho ≈ +0.262;
- events ≈ +0.313;
- social ≈ +0.277;
- dialogues ≈ +0.142.

So the archive-level relationship does not vanish after holding section fixed.

REALTALK is mixed across its three categories: category 2 retains a moderate chat-level rho ≈ +0.382, categories 1/3 are weaker.

Thus semantic task type is not the entire regime variable, but archive/chat geometry alone is also not uniformly predictive.

## 5. Archive-only geometry is definitely insufficient

PerLTQA offers a particularly strong control because profile/events/social/dialogue queries for a character use the **same character archive and same document C96**.

Holding the archive fixed across the 30 characters:

- events SIGN−float is negative in 30/30;
- events P64 is negative in 30/30;
- profile SIGN−float is positive in 23/30;
- profile P64 is positive in 28/30;
- in 22/30 characters **both Delta and P64 flip together** from profile-positive to events-negative.

Across 115 non-zero character×section pairs, Delta and P64 have the same sign in 87 (75.65%).

Therefore any sufficient explanation must contain a **query/semantic-regime × archive interaction**. Static archive geometry alone cannot explain the phenomenon.

## 6. P64 is not merely a boundary-tie artefact

Conditioning PerLTQA on native K=3 boundary-tie status:

- untied queries (n=5852): `rho(Delta,P64) ≈ +0.102`;
- tied queries (n=2413): `rho ≈ +0.127`.

The profile-positive / events-negative Delta and P64 regimes remain in the untied subset. Therefore P64 is not generated solely by the native boundary-tie indicator.

This does **not** close richer ranking-competition mechanisms such as strictly-closer rivals and gold-distance tie mass, which were already more informative than scalar tie rate in the earlier D2 mechanism audit.

## 7. Current best hypothesis — licensed narrowly

The strongest surviving statement is:

> **SIGN advantage is a query–archive regime interaction. `BOT−TOP` retrieval polarity is a descriptive marker of that regime, not an individual-query law. The underlying cause is not explained by scalar variance concentration, marginal axis strength, simple low-variance complementarity, or aggregate boundary-tie incidence. Joint sign-bit redundancy/effective binary dimension and query-specific ranking competition remain the main unresolved candidates.**

This is a mechanism candidate, not causal proof.

## 8. What is still missing

The load-bearing V2 metrics requiring raw frozen C96/qC caches have **not** been run across the benchmarks because those caches are excluded from the GitHub campaign snapshot and were not found through the connected Drive search:

- TOP64/BOT64 sign-bit `PHI_GAP`;
- binary `EFFDIM_GAP`;
- duplicate-code gaps from exact sign codes across all benchmarks;
- query-magnitude metrics `Q_ABS_CV`, `Q_EFF`;
- strictly-closer-rival and gold-distance tie-mass TOP-vs-BOT gaps using raw distances.

Do not regenerate missing frozen caches by refitting merely to fill this gap.

LoCoMo also lacks an accessible committed per-query centered-float result surface, so the E1 Delta/P64 test was not synthesized for LoCoMo.

## 9. Governance decision

Stop opening additional post-hoc mechanism probes at this checkpoint. The next valid scientific actions are:

1. **independent audit** of this exact checkpoint and the cited Action logs/results;
2. recover/locate the frozen raw C96/qC caches without refitting and execute the already-frozen V2 metrics;
3. if a concrete mechanism metric survives, test it on an **unseen fifth benchmark** with the rule frozen before outcomes.

No new codec race is justified yet.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
