[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Why sign can beat centered cosine, and why it can reverse — REPORT

Workspace: `/home/mdp/muse-work/math-sign-mechanism/` · `verify.py` (stdlib only)
· `results.json` (machine output of `verify.py`) · `STATUS.md` (checkpoint).

## 0. One useful result (honest version)

A single 3-coordinate heteroskedastic model yields **both directions** with
exact arithmetic, under genuinely centered cosine ranking with normalization:

- **Sign wins** when nuisance magnitudes are large relative to the signal:
  cosine's magnitude weighting lets query-aligned nuisance outvote the
  relevance-bearing coordinate; sign's one-coordinate-one-vote rule preserves
  the signal's vote share.
- **Sign loses** when nuisance magnitudes are small but nuisance signs oppose
  the signal on many coordinates: cosine's magnitude weighting correctly
  downweights near-zero uninformative coordinates that sign must count equally.

The gap is carried **entirely by tie structure**: in the symmetric model the
strict-win masses of the two rules coincide exactly (11/16); sign converts
cosine's would-be losses into ties at large nuisance scale, and cosine
resolves sign's ties (and its one loss) into wins at small scale. The pairwise
gaps transport to top-3 fractional recall in the same direction (exact
multinomial computation, N=6 and N=10). Two strict d=3 exhibits (no ties at
all) prove neither direction is a tie-protocol artifact.

## 1. Setup and conventions (explicit assumptions)

- Document C and query qC are centered vectors (the float anchor was already
  centered: AUDIT-1 Task B, centering +0.149pp vs binarization +10.038pp —
  the centering confound is dead and is NOT revisited here).
- Float ranking = cosine on centered vectors, `cos(C,q)=(C.q)/(||C|| ||q||)`
  — normalization is always applied; no dot-product substitutes anywhere.
- Sign ranking = Hamming distance on `sign(C), sign(qC)` with the frozen
  convention `sign(x) = +1 iff x >= 0` (cf. `race_sign.py` model `C>=0`).
- Pairwise numbers use **random (expected) tiebreak** = the frozen 20-draw
  protocol's expectation (MATH-1 identity); pessimistic/optimistic variants
  are reported wherever they change a conclusion.
- Relevance is defined **exogenously** (a designated signal coordinate / gold
  document), never as "whatever a rule retrieves" (no circularity).
- All synthetic objects are labelled SYNTHETIC and are never presented as
  benchmark output. No claim below describes real LME/LoCoMo/REALTALK/PerLTQA
  vectors; the model is a sufficient-condition exhibit, not a fit.

## 2. THEOREM 1 — both orderings are realizable in d=3 (strict, exact)

> **THEOREM 1 (deterministic exhibits).** With centered cosine (normalized)
> vs Hamming-sign ranking, both strict separations occur with zero ties:
> (a) sign ranks the gold first while cosine ranks a distractor first;
> (b) vice versa. Both orderings are decided by exact rational arithmetic.

*Proof by exhibit (machine-checked in `verify.py`, §E1/E2).*

E1 (sign wins): `q=(1,1,1)`, gold `R=(1,0.1,0.1)`, distractor `I=(-1,5,5)`.
Signs: R `(+,+,+)` Hamming 0; I `(-,+,+)` Hamming 1 — sign strict for R.
Cosine: dots `R.q=1.2 > 0`, `I.q=9 > 0`, `||R||^2=1.02`, `||I||^2=51`.
`cos(I) > cos(R)` ⟺ `81/51 > 1.44/1.02` ⟺ `82.62 > 73.44` ✓ (squaring valid:
both dots positive). Display values: cos(R)≈0.685994, cos(I)≈0.727607.

E2 (sign loses): `q=(1,1,1)`, gold `R=(1,-0.1,-0.1)`, distractor
`I=(-1,0.1,0.1)`. Signs: R Hamming 2, I Hamming 1 — sign strict for I (wrong).
Dots `+0.8` vs `-0.8` with equal norms (`1.02`) — cosine strict for R. ∎

*Mechanism reading.* E1: the distractor's two query-aligned nuisance
coordinates have magnitude 5 each; they contribute `10/√51 ≈ 1.4` of
normalized alignment and drown the `-1` signal deficit. Sign counts the
signal coordinate's vote equally. E2: the two nuisance oppositions are each
magnitude 0.1 — cosine nearly ignores them (dots keep the signal's sign);
sign spends 2 of its 3 votes on them and outvotes the signal coordinate.
**Magnitude-blindness helps in E1 and hurts in E2.** Convention-robustness:
no ties exist in either exhibit, so pessimistic/expected/optimistic
tie rules all agree — neither direction is a tie-protocol artifact.

## 3. THEOREM 2 — one-parameter probabilistic model with both regimes

> **THEOREM 2 (heteroskedastic-nuisance regimes + transport).** Fix
> `q=(1,1,1)`, signal scale `s=1`, one signal coordinate and `p=2` nuisance
> coordinates (SYNTHETIC model H): gold `R=(1, t·ε2, t·ε3)`, non-gold
> `I=(-1, t·δ2, t·δ3)`, `ε,δ` iid Rademacher, shared nuisance scale `t>0`.
> Then, by exhaustive 16-state enumeration (exact rationals):
> (i) sign's expected pairwise correctness is `13/16 = 0.8125` for ALL `t>0`
> (magnitude-blindness); (ii) cosine's is `31/32 = 0.96875` at `t=1/2`
> (sign LOSES) and `11/16 = 0.6875` at `t=10` (sign WINS); (iii) with one
> gold and `N-1` exchangeable non-golds, exact `E[FR@3]` preserves both
> directions at `N=6` (0.9368 vs 0.9994 / 0.8200) and `N=10`
> (0.7492 vs 0.9959 / 0.4299).

*Proof.* (i) Sign distances: gold `2-A`, non-gold `3-B` with
`A,B ~ Bin(2,1/2)` iid agreement counts. Win ⟺ `A≥B` (mass 11/16), tie ⟺
`B=A+1` (mass 4/16), loss 1/16 — independent of `t` (for `t>0`; at `t=0`
nuisance signs degenerate via the `>=0` rule, so `t>0` is a stated
assumption). Expected correctness `11/16 + (1/2)(4/16) = 13/16`.
(ii) Norms are equal (`1+2t²` regardless of coin states — signs never move
mass), so cosine ordering ⟺ dot ordering `2 + t·D > 0` with
`D = ε2+ε3-δ2-δ3 ∈ {-4,-2,0,2,4}` (masses 1,4,6,4,1 over 16).
At `t=1/2`: threshold `-4`; win 15/16, tie (`D=-4`) 1/16, loss 0 →
`15/16+1/32 = 31/32`. At `t=10`: threshold `-0.2`; win (`D≥0`) 11/16,
tie 0, loss 5/16 → `11/16`. (iii) Transport lemma (single gold,
exchangeable non-golds with `(u,v)` = P(strictly closer)/P(tied)):
`E[FR@3] = Σ Multinomial(N-1;u,v,w)[i,j]·f(i,j+1)` with MATH-1 `f`
(`0 | 1 | (3-S)/T`; the single-gold exchangeable case is re-derived by the
tied-block symmetry argument, cf. MATH-1 §1a which proves the general
identity). Pairwise `(u,v)`: sign `(1/16,4/16)`; cosine `t=1/2 → (0,1/16)`,
`t=10 → (5/16,0)`. Exact Fractions give the table in §5. ∎

*The tie-conversion mechanism (exact correspondence at `t=10`).*
`D≥0` (11/16): both rules win. `D=-2` (4/16): cosine LOSES, sign TIES
(`B=A+1`) — sign's coarseness converts losses to half-wins. `D=-4` (1/16):
both lose. Hence strict-win masses coincide at 11/16 = 11/16 and the entire
`13/16 vs 11/16` gap is tie conversion. At `t=1/2` the mirror holds: cosine's
finer granularity converts sign's 4/16 ties and 1/16 loss into wins
(`D=-4` becomes a tie instead of a loss; everything else wins).

*Boundary disclosure.* Under the **pessimistic** convention (ties = losses)
the WIN regime ties exactly (`11/16 = 11/16`) instead of winning; under
optimistic it wins (`15/16 vs 11/16`); the LOSE regime holds under all three
conventions. The strict exhibits of Theorem 1 (no ties) cover what the
probabilistic win cannot: a convention-proof strict separation.

## 4. COUNTEREXAMPLE V — top-variance selection can strictly hurt (fresh)

> **COUNTEREXAMPLE (synthetic 6-doc archive, exact).** Selecting the 2
> highest-variance coordinates yields `FR@3 = 3/5 = 0.6` while the 2
> lowest-variance coordinates yield `1.0` (full 4-coordinate code also `1.0`).
> Population variances: `[72.33, 47.22, 1.0, 1.0]` — the variance ranking is
> strict and uncontested.

Archive (query signs `++++`; S=`#strictly closer`, T=tie bucket incl. gold):
gold `G=(10,-10,1,1)`; distractors `(9,-9,-1,-1)`, `(-9,9,-1,1)`,
`(-9,-9,1,-1)`, `(9,-9,-1,1)`, `(8,-10,1,-1)`.
TOP2 `{0,1}`: gold distance 1, tied with 4 distractors → `S=0,T=5`,
`f=3/5`. BOT2 `{2,3}`: gold distance 0 alone → `S=0,T=1`, `f=1`.
*Why it differs from MATH-1's TOP48 collapse:* MATH-1 showed the collapse
empirically on frozen LME vectors and traced it to tie-spike burial in
distance profiles. Here the archive is forward-constructed and the mechanism
is query-blindness of variance: coordinates 0–1 carry large archive spread
orthogonal to what the query needs, while the discriminative coordinates
2–3 have variance 1. Variance conflates "spread the query doesn't care
about" with "signal". (Verified exactly in `verify.py`, §V.)

## 5. Verified numbers (from executed `verify.py`; exact Fractions)

| object | value (exact) | value (display) |
|---|---|---|
| E1 Hamming gold / distr; cosine order | 0 / 1; distr first | cos 0.685994 vs 0.727607 |
| E2 Hamming gold / distr; cosine order | 2 / 1; gold first | dots +0.8 vs −0.8 |
| Model H sign expected pairwise (all t>0) | 13/16 | 0.8125 |
| Model H cosine expected pairwise, t=1/2 | 31/32 | 0.96875 |
| Model H cosine expected pairwise, t=10 | 11/16 | 0.6875 |
| E[FR@3] N=6: sign / cos-lo / cos-hi | 491159/524288 / 1047983/1048576 / 429913/524288 | 0.9368 / 0.9994 / 0.8200 |
| E[FR@3] N=10: sign / cos-lo / cos-hi | 64355864171/85899345920 / … (≈) / 7385637809/17179869184 | 0.7492 / 0.9959 / 0.4299 |
| Model V FR: TOP2 / BOT2 / full | 3/5 / 1 / 1 | 0.6 / 1.0 / 1.0 |

Exact command and output: `cd /home/mdp/muse-work/math-sign-mechanism &&
python3 verify.py` → exit 0, `ALL CHECKS PASSED`; per-section lines quoted
in `results.json`. Interpreter: system `python3` 3.14.4, stdlib only
(`fractions`, `itertools`, `math` for display, `json`). No numpy/scipy import
was needed, so the ml-python environment was not activated (checked it exists
but left unused — fewer dependencies is better for a proof artifact).

## 6. Failed attempts (recorded, not hidden)

- **F1 (falsified conjecture: "any heteroskedasticity breaks cosine").**
  In d=2 with symmetric signal `R=(u,vR)`, `I=(-u,vI)`, `vR,vI ≥ 0`,
  cosine is ALWAYS correct: `(v+u)² ≥ u²+v²` keeps gold's cosine above
  `1/√2` while `(v-u)² < u²+v²` keeps the distractor's below it (exact,
  spot-checked in `verify.py`). Cosine normalization is a genuine defense:
  a huge nuisance magnitude mostly dilutes *itself* through the norm. This
  forced the `p=2` nuisance design (signal share must be dilutable).
- **F2 (falsified conjecture: "large nuisance anywhere breaks cosine").**
  With `σ=0` (gold nuisance-free) and `τ→∞`, cosine still wins
  (limit ≈ 0.8125 beats sign's 0.726 at p=5 in one computed case) — the
  distractor's nuisance lottery stays below the gold's fixed cosine. The
  working regime needs *shared* large nuisance (`σ=τ=t→∞`), where both
  rules' strict masses coincide and only tie structure differs.
- **F3 (serialization, not math).** First `verify.py` run passed every
  mathematical assert but crashed writing `results.json` (`Fraction` is not
  JSON-serializable) plus a `float('13/16')` display bug — fixed by
  stringifying exact values (floats for display only). Decisions never
  depended on floats: cosine comparisons use root-free cross-multiplication
  (`a²·s2 vs b²·r2` on same-sign dots, sign logic otherwise).

## 7. PerLTQA events-vs-profile: TESTABLE hypotheses (no causal claims)

The verified PerLTQA reversal (B3B-FIN: sign − float = −6.275pp overall;
events −12.41pp at n=4346 vs profile +20.44pp at n=333; tie-shift ±0.02pp)
is taken as EMPIRICAL OBSERVATION. The models above suggest — but do not
establish — three discriminating tests on the frozen PerLTQA artifacts
(read-only; NOT executed here):

- **H1 (nuisance-scale / mixed-granularity).** *Prediction:* per-QA
  `delta = FR_sign − FR_float` correlates negatively with the gold item's
  nuisance load, e.g. gold-item token length relative to its archive mean,
  or the query's cosine mass on top-variance SVD directions. *Procedure:*
  from frozen `per_q` rows, regress `delta` on length-ratio within the
  single-gold events slice; pass = significantly negative slope, fail =
  flat. Connects to Theorem 2's `t` axis and the B3B-FIN profile-BOT64
  inversion note (discriminative signal in low-variance directions).
- **H2 (gold-size floor is NOT the driver).** *Prediction:* dropping all
  multi-gold dialogue QAs (mean gold 9.92, both arms ≤0.10) leaves the
  headline negative (events single-gold −12.41pp alone exceeds it).
  *Procedure:* recompute section-conditioned means from stored `per_q`
  (no rerun needed); pass = events-only delta < −5pp. Already half-evident
  from the published section table — framed here as the explicit kill test
  for the "it's just the dialogue floor" alternative.
- **H3 (query-side weight concentration).** *Prediction:* profile queries
  (short, field-targeted questions) put cosine mass on few coordinates where
  sign's equal voting helps; event queries (narrative overlap) spread mass
  onto high-variance verbiage directions where E1-style drowning occurs.
  *Procedure:* per-QA effective rank / participation ratio of `|qC|`Bin the
  frozen caches; pass = participation ratio predicts `delta` sign within
  sections. Uses only stored vectors — no new embedding runs.

None of H1–H3 is tested here; each has a stated pass/fail rule so a future
session (or a skeptic) can kill it cheaply.

## 8. Scope, novelty, and limits (read before citing — which you must not)

- **What is proven:** Theorems 1–2 and Counterexample V are proved exactly
  (analytic exhibits + exhaustive enumeration over stated finite models).
  Assumptions are inside the statements (`t>0`, Rademacher coins,
  exchangeable non-golds, single gold for transport, `>=0` sign rule).
- **What is NOT proven:** anything about real benchmark vectors. The model
  assumes iid Rademacher nuisance signs — MATH-1 §2c *rejected* iid
  bit-independence on real LME data (retrievable-regime ties 7–13× over
  binomial). This work is therefore a **sufficiency exhibit** (such regimes
  exist and separate the rules in both directions), not a fitted explanation
  of LME (+10pp), LoCoMo (+12pp), REALTALK (+5.2pp), or PerLTQA (−6.3pp).
- **No retrieval lower bounds are inferred from distance preservation**
  (no JL/geometry-preservation argument appears anywhere by design).
- **Novelty delimiting (provisional, no priority claimed):** MATH-1 owns the
  exact conditional identity `E[FR]=(1/m)Σf(S,T)`, the empirical spike
  rejection, and the mixing Cov→width→burial chain — reused here as the
  transport formula, not re-claimed. MATH-2 S4 proposed stratifying frozen
  flips by margin vs tie-mass; this report's forward generative model is
  complementary (it predicts what such a stratification should find: the
  `t` axis moves tie-mass at fixed margins). The lit-scan heterogeneity
  paper (arXiv 2605.17524, Prop 5: magnitude bits gain value with
  heterogeneity) is consistent with the LOSE regime and in tension with the
  WIN regime — that tension is flagged as an untested discriminating
  prediction (48×2-bit vs 96×1-bit at matched 12B should flip with `t`),
  not as a disagreement. No literature priority review was performed
  (per protocol: novelty statements are provisional).
- **Closed gates respected:** no learned selection / adaptive routing appears
  (killed by m1/m3); centering is not re-litigated; no universal-losslessness
  claim is made (CERT verdict stands); benchmarks were not rerun or touched.

## 9. Files and reproduction

- `/home/mdp/muse-work/math-sign-mechanism/verify.py` — all checks, stdlib only.
- `/home/mdp/muse-work/math-sign-mechanism/results.json` — exact values as written by that run.
- `/home/mdp/muse-work/math-sign-mechanism/STATUS.md` — early checkpoint.
- Command: `cd /home/mdp/muse-work/math-sign-mechanism && python3 verify.py`
  (exit 0, `ALL CHECKS PASSED`, ~instant; writes `results.json`).
- Read-first sources (all under `/mnt/c/Users/MDP/dev/llmzip-work/`,
  read-only): `review_transfer/PROMPT_EXTERNAL_LLM_2026-09-13.md` (§§1–2, §6.1);
  `race_2026-09-13/cert/cert_report.md` (§§1–4, lemma + verdicts);
  `audit_2026-09-13/audit1_cont/report.md` (Tasks B–D);
  `bench3/runs/b3b_fin/report.md` (§§2–6, PerLTQA sections);
  `lit_scan_2026-09-13/LITERATUR_TARAMASI.md` (§§0–1);
  `pilots/axis_attack_2026-09-12/round3/ROUND3_REPORT.md`;
  `prereg_race_2026-09-13/math1/math1_report.md` (§§1–2);
  `prereg_race_2026-09-13/math2/math2_report.md` (S1–S5, §4).
