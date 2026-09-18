[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# MY_NUMBERS.md — frozen at step 1, written BEFORE reading any coordinator script or value

Produced by `my_f1.py` (this directory), written only from the TEXT of:
- `R2_COMPETITION_RERUN_CONTRACT.md` (TOP64/BOT64 rule, per-gold competition rule, avg-rank Spearman, bootstrap conventions)
- `E1_PREANALYSIS_SPEC_V2.md` (Delta_q, `v_j = mean_i(C_ij^2)`)
- `bench3/b3b_perltqa/step2_eval.py` (K=3, NT=20, `met()` third element = FR@3)

At the time of writing this file I had read NONE of:
`coordinator/coord_f1_real_fr3.py`, `coordinator/coord_frozen_repl.py`,
`agent_packages/.../f1_competition.py`, `evidence/f1_results_fr3.json`.
I had read `ERRATA_COORDINATOR.md` (prose only, supplied in my brief) — see honesty note at the bottom.

Run: WSL Ubuntu, numpy, 38.7 s wall. Raw stdout preserved in `evidence/my_run.log`;
full machine-readable output in `evidence/results.json`.

## The six primary Claim-D coefficients (VERIFIED — I computed these)

| benchmark | n | rho(Delta_q, STRICT_GAP_q) | rho(Delta_q, TIE_GAP_q) |
|---|---:|---|---|
| LME      | 470  | `0.1416251737011647`  | `0.14069387548880735` |
| PerLTQA  | 8265 | `0.25413844391463014` | `0.27982715404990666` |
| REALTALK | 705  | `0.09793425648573494` | `0.12307477776090332` |

## Headline gate values I measured (VERIFIED)

| benchmark | FR@3 SIGN96 | FR@3 centered float96 | delta (pp) |
|---|---|---|---|
| LME      | `0.5421335697399526`  | `0.4415957446808511`  | `+10.053782505910167` |
| PerLTQA  | `0.48894479616364206` | `0.551692074528853`   | `-6.274727836521104`  |
| REALTALK | `0.22553482307028402` | `0.17253405381064957` | `+5.300076925963451`  |

## Min-gold (R1 bug) control — what the forbidden metric gives on the same rows (VERIFIED)

| benchmark | strict rho under min-gold | tie rho under min-gold | multi-gold n/rate |
|---|---|---|---|
| LME      | `0.09920150310037373` | `0.09863003060835299` | 296/470 = `0.6297872340425532` |
| PerLTQA  | `0.2774184734053319`  | `0.28506408072939843` | 2322/8265 = `0.2809437386569873` |
| REALTALK | `0.061255512317713624`| `0.08752108650096173` | 386/705 = `0.5475177304964539` |

## Mandatory non-gold sensitivity variant (contract §"Also compute a mandatory sensitivity variant")

| benchmark | strict rho (gold excluded from competitors) | tie rho |
|---|---|---|
| LME      | `0.1411410420423395`  | `0.1490845367749897` |
| PerLTQA  | `0.25429895729431806` | `0.2798102912113063` |
| REALTALK | `0.09813121163764911` | `0.12256908387438058` |

## PerLTQA section summaries (VERIFIED)

| section | n | strict | tie |
|---|---:|---|---|
| dialogues | 2742 | `0.13059437038567112` | `0.11123863113109236` |
| events | 4346 | `0.3980235604927669` | `0.3892597323356448` |
| profile | 333 | `0.057497403356242496` | `0.018965472076063236` |
| social_relationship | 844 | `0.30422818141655533` | `0.29916699086757836` |

## Descriptive cluster bootstrap (seed 96013, B=2000, percentile 2.5/97.5) — DESCRIPTIVE/POST-HOC

Cluster level used: LME = question_id (one query per archive, contract says this reduces to
query/archive resampling); REALTALK = `chat_no`; PerLTQA = `char` (archive).
2000/2000 replicates valid in all three; 0 invalid.

| benchmark | strict CI | tie CI |
|---|---|---|
| LME | [`0.06238792814020837`, `0.22518502178382113`] | [`0.05658330000330699`, `0.2228041356853288`] |
| PerLTQA | [`0.2248040498710948`, `0.2838761921738789`] | [`0.2573206982247258`, `0.304526327261728`] |
| REALTALK | [`0.027079003462290467`, `0.14777803227571418`] | [`0.06369998882251122`, `0.17767097805692783`] |

## Centering measurement (VERIFIED — bears on coordinator erratum E1)

Max over archives of `|column mean|` of the cached C:
LME `7.095e-16`, PerLTQA `4.411e-16`, REALTALK `7.684e-16`.
The caches ARE already centered. Any further centering is a bug. My code does not center.

## Method decisions I made and why (recorded before seeing any comparison)

1. **FR@3 tie handling.** The frozen scorer averages `NT=20` seeded permutations. I used the
   EXACT expectation `E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|`, where
   `lt = #{d < d_(K)}`, `bc = #{d == d_(K)}`, `slots = K - lt`. Reason: it is the
   NT→∞ limit, it is exactly order-independent, and the frozen seeds for the LME and
   REALTALK legs are not reconstructible from the local caches. **This is a deliberate
   substitution and I flag it as a deviation from the frozen convention, not as equivalence.**
   It will shift results by O(sampling noise of a 20-sample mean).
2. **TOP/BOT.** `v_j = mean_i(C_ij^2)`, `np.argsort(-v, kind='stable')`, first 64 / last 64,
   then column indices sorted ascending (order within an arm cannot matter for Hamming).
   Note: the frozen scorer uses `C.var(axis=0)`; on centered data these coincide.
3. **Competition counts.** Integer Hamming distances, so `<` and `==` are EXACT integer
   comparisons. No tolerance anywhere. `tie_all` includes the gold row itself (the contract's
   `count_i[d_A(i) == d_A(g)]` has no exclusion; the non-gold variant is reported separately).
4. **REALTALK validity filter.** I dropped queries with empty gold, out-of-range gold rows, or
   non-finite/zero-norm query vectors. This yielded exactly 705 usable queries, matching the
   frozen `n_valid=705` gate, so the filter is not doing anything idiosyncratic.
5. **LoCoMo NOT RUN.** The local caches carry no committed per-query float96 retrieval surface
   for LoCoMo, so `Delta_q` cannot be formed there without a refit, which the contract forbids.
   I therefore report three benchmarks, not four, and say so.
6. **Archive identity UNVERIFIABLE.** The contract pins sha256 of three `.tar.gz` archives.
   Only extracted trees exist locally. I cannot verify archive-level identity and do not claim to.

## Honesty note on my own independence

I read `ERRATA_COORDINATOR.md` before this file was frozen, because it was quoted in my
commissioning brief and I could not un-read it. It told me (a) the caches are already centered
and (b) the frozen metric is FR@3 not ALL@3. Both facts I also verified directly from the
caches and from `step2_eval.py:15-19`. It did NOT contain any of the six coefficients, and
it did not contain the exact-expectation formula in a form I copied — I derived that from the
`lt / bc / slots` variables that already exist in the frozen scorer. My knowledge of the
coordinator's *headline* pp values from the brief is a genuine contamination risk for the
headline row above; it is NOT a contamination risk for the six coefficients, which I had
never seen at full precision.

FROZEN. Not edited after this point.
