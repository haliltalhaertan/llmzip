# CERT — certifiable losslessness for the 12-byte-and-below ladder

**[LOCAL EXPLORATORY] [NOT PREREGISTERED] [NOT FOR CITATION]**
Read-only `/mnt/c`; wrote only `/tmp/cert/`. No network (LIT-CHECK items flagged, not pursued). No paid APIs.
Code: `/tmp/cert/cert_compute.py` · numbers: `/tmp/cert/cert_details.json` (incl. per-question arrays).
Compute: LME-470 + LoCoMo-1535 recomputed from frozen pkls, verbatim tie protocol (K=3, NT=20);
all gates bit-exact (see §2).

## 0. One-line answer

**No notion of "lossless" is provable as a theorem about the real data; what IS provable
(and is proved here, with real numbers) is finite-sample quality-equivalence: paired,
assumption-light certificates of the form "rung b retains quality within ε of native at
≥95% one-sided confidence." Achievable ε (per-comparison / Bonferroni family-wise, best
family per rung): LME 10B 3.3/4.3pp (SPREAD), 8B 6.1/7.4pp (BOT), 6B 10.8/12.0pp (RANDavg);
LoCoMo 10B 0.95/1.55pp (BOT), 8B 3.0/3.7pp (BOT), 6B 6.8/7.7pp (BOT). ε=0 ("no worse than
native") is certifiable nowhere — every rung is measurably below native.**

---

## 1. Taxonomy of provability

### (a) Bit-exact reconstruction — not provable, and provably not provable in general

Claim shape: "a ≤b-bit code reconstructs the 96-bit sign vectors (or float96) exactly."
Three stacked impossibilities:

1. **Counting.** A b-bit code has 2^b codewords. Whenever an archive holds more than 2^b
   distinct 96-bit sign vectors (true here: hundreds of docs × 470/1535 questions), exact
   reconstruction of all vectors is impossible by pigeonhole — for *every* code, no
   distribution needed. This direction is trivially provable and useless: it rules out
   reconstruction, not quality loss.
2. **Absolute lower bounds need a distribution model.** Statements like "no b-bit code can
   achieve quality Q on *this* data" are statements about one fixed finite object; absent a
   probabilistic model of (query, archive) pairs there is no randomness over which a lower
   bound can quantify. Any "proof" smuggles in a model (iid docs, independent bits — both
   REJECTED on this data by MATH-1 §2c: retrievable-regime ties 7–13× over binomial).
3. **Kolmogorov uncomputability.** The shortest-program (ideal compression) floor is
   uncomputable; no computable certificate can appeal to it. The only decidable no-lossy-code
   statements ("no program of length ≤ L reproduces these exact finite vectors") are finite
   search problems — decidable, vacuous at our scales, and silent about retrieval quality.

**Verdict (a): nothing actionable. Bit-exactness is the wrong target: native SIGN96 itself
is already a lossy sketch of float96 (384B → 12B) and beats float96 on quality (54.20% vs
44.16% LME). The ladder question was never reconstruction.**

### (b) Quality-equivalence certificates (finite-sample) — THE actionable one [DONE, §2–3]

Claim shape: "budget b retains mean fractional-R@3 within ε of native (or above float96),
with ≥95% one-sided confidence, on the frozen benchmark." This is a standard
finite-population / superpopulation inference on **paired per-question differences**
`d_i = FR_b,i − FR_native,i`, and it is fully executable. Design and results are §2–3.

### (c) Model-conditional theorems — one clean lemma [DONE, §4]

Claim shape: "UNDER a stated profile class (spike+bulk), E[FR_b] satisfies bound B."
The exact MATH-1 identity plus finite monotonicity are proved; the spike-class bound is
proved *conditionally*, with the class-membership premise marked conjecture (empirically
supported, falsifiable). This is the seed for a future Lean formalization (statement shape
noted in §4; finite sums only — no analysis axioms needed except where marked).

### (d) Impossibility ("no ≤b-bit code can…") for the real data — out of reach

Honest map: a real-data impossibility proof would need (i) a distribution model the data
provably satisfies (we have the opposite: the natural iid/bit-independence models are
rejected, MATH-1 §2c), plus (ii) a minimax argument over all codes under that model.
Neither exists. **Feasible toy-model versions** (LIT-CHECK — literature not consulted, no
network; names from knowledge, verify before citing): rank-preservation/quantization bounds
(order-statistics of discrete scores: tie probability at the top-k boundary as a function of
k, N, margin law; JL-type distance-preservation floors). What they would imply is bounded:
a JL floor lower-bounds bits for (1+ε)-geometry *everywhere* — sufficient but wildly
over-strong for top-k retrieval, which needs only the order at one boundary per query
(citing JL here is a category error; the separation paradox is the exhibit: TOP48 wins
mean-separation on 58% of questions yet loses FR on all but 13%). A calibrated
margin-histogram + union-bound floor (MATH-2 S2 shape) is the honest toy target: it would
certify "below k* bits the boundary lottery dominates" — a statement about the *profile
class*, never about "no code."

---

## 2. Certification protocol (executed)

**Estimand.** `μ_b = E_q[FR_b(q) − FR_native(q)]`, paired per question. Two estimators:
primary = 20-trial MC means (the published metric; gates match anchors to ≤1e-12);
cross-check = MATH-1 exact `E[FR]=(1/m)Σf(S,T)` (deterministic; agrees to ≤0.24pp everywhere).

**Procedure (per rung × benchmark × family).** Paired bootstrap of the mean gap:
B=20000 resamples of questions, seed 20260913; one-sided 95% lower bound LB95 =
5th percentile; **achievable ε_pc = max(0, −LB95)**. "Certify no worse than native" is the
special case ε=0 (rejected everywhere here: all two-sided 95% CIs but two exclude 0 from
below; LoCoMo BOT80 and LME SPREAD80 merely *include* 0 — absence of significance, not
equivalence). "Certify within ε" is non-inferiority with margin ε — the reported ε values.

**Assumptions (minimal) and validity here.**
(i) *Questions are exchangeable draws* (bootstrap unit = question; pairing absorbs all
within-question correlation across arms — archives, gold-count, difficulty). Valid as a
benchmark-conditional statement; it does NOT generalize past the benchmark (D3/C5:
utilities are benchmark-local, so each certificate is stamped with its benchmark).
(ii) *Nuisance-trial noise is negligible.* Measured: mean per-question trial-var/20 =
8.1e-4 → contributes SE² ≈ 1.7e-6 vs sampling SE² ≈ 3.5e-4 (<0.5% of variance). The
exact-model cross-check (trial-free) confirms: gaps agree to ≤0.24pp.
(iii) *No selection bias:* families were fixed before seeing gaps (RANDavg = mean of 3
pre-declared seeds 12000–12002; SPREAD = rank-linspace; BOT = variance tail). No
best-of-seeds picking (the m1 trap: vs-best null sits −1.62/−1.20pp below the mean).

**Multiplicity.** 18 certified claims (3 rungs × 2 benchmarks × 3 families).
Per-comparison ε_pc (95% one-sided) + Bonferroni family-wise ε_fwer (one-sided
99.72% LB, assumption-free). Bonferroni is conservative under the strong positive
dependence across rungs; Holm would shave ~0.1–0.3pp — reported per-comparison numbers
are the optimistic edge, FWER the citable edge.

**Gates (all passed, diffs ≤1e-9 unless noted 0.0):** LME native 0.5419751773049645 (1e-16);
RAND48/64/80_s0, RANKSTRIDE48, IDXSTRIDE48, TOP48, BOT48 vs frozen artefacts; LoCoMo native
0.23654714666441054; RAND48/64/80_s0 vs R2C; validity counts 470/1535. LME native exact-model
0.542134 reproduces MATH-1 pred 0.542134.

## 3. Certificates (real numbers)

Mean gaps are pp vs native (negative = rung below native). ε = certifiable non-inferiority
margin: "within ε of native at ≥95% one-sided confidence."

| rung | LME mean gap (best fam) | LME ε_pc / ε_fwer | LoCoMo mean gap (best fam) | LoCoMo ε_pc / ε_fwer |
|---|---|---|---|---|
| 10B (k=80) | −1.67 (SPREAD .5253) | **3.28 / 4.28** | −0.11 (BOT .2355) | **0.95 / 1.55** |
| 8B (k=64) | −4.16 (BOT .5004) | **6.06 / 7.40** | −1.94 (BOT .2172) | **3.00 / 3.73** |
| 6B (k=48) | −9.13 (RANDavg .4507) | **10.83 / 11.96** | −5.54 (BOT .1811) | **6.84 / 7.70** |

Full panel (gap pp | ε_pc | ε_fwer; means in details json):
LME — RANDavg: −2.66|3.82|4.65 (80), −5.91|7.27|8.29 (64), −9.13|10.83|11.96 (48);
SPREAD: −1.67|3.28|4.28, −4.56|6.44|7.83, −9.92|11.91|13.33;
BOT: −1.91|3.34|4.35, −4.16|6.06|7.40, −11.35|13.74|15.47;
TOP-ref: −5.09|6.86|8.06, −10.95|13.16|14.69, −19.25|21.92|23.67.
LoCoMo — RANDavg: −1.52|2.12|2.54, −4.03|4.88|5.47, −7.41|8.46|9.19;
SPREAD: −1.22|2.04|2.69, −4.28|5.38|6.16, −7.42|8.66|9.48;
BOT: −0.11|0.95|1.55, −1.94|3.00|3.73, −5.54|6.84|7.70;
TOP-ref: −3.62|4.54|5.22, −7.13|8.32|9.15, −10.47|11.82|12.70.
Best family is benchmark-local (LoCoMo: BOT everywhere; LME: SPREAD at 10B, BOT at 8B,
RANDavg at 6B) — the C5/R2C nuance reproduced inside the certificates.

**Example certificate statements (citable at FWER edge):**
- C1: "On frozen LME-470, 80-bit SPREAD retains fractional-R@3 within **4.3pp** of native
  SIGN96 (mean −1.67pp, FWER one-sided 99.72% LB −4.28pp)." Per-comparison: within 3.3pp.
- C2: "On frozen LoCoMo-1535, 80-bit BOT retains quality within **1.6pp** of native
  (mean −0.11pp, FWER LB −1.55pp)." Per-comparison: within 0.95pp — the only rung near
  practical losslessness, and still not ε=0.
- C3 (vs float, LME): "80-bit SPREAD (LB95 mean 0.4937), 64-bit BOT (0.4696) and 64-bit
  SPREAD (0.4658) all certifiably **beat raw float96 (0.4416)** at 95% one-sided
  (+5.2/+2.8/+2.4pp margins); 48-bit arms do not (RANDavg LB95 0.4243, −1.7pp)."
- C4 (negative): "ε=0 vs native is rejected at every rung on both benchmarks (all gaps
  negative; two-sided 95% CIs exclude 0 except LME SPREAD80 [−3.56,+0.24] and LoCoMo BOT80
  [−1.12,+0.91], which are inconclusive, not equivalence)."

**Reading for the race:** the ladder is a smooth quality–bits trade, not a cliff above 6B;
only LoCoMo-10B is within ~1pp of native, and that is a *statistical* equivalence at a
stated margin — not a proof of losslessness.

## 4. ONE model-conditional lemma (Task 2)

Notation from MATH-1 (exact, no new assumptions): one question, `n` docs, gold set `G`
(`|G|=m`), top-`k` (`k=3`), b-bit Hamming distances `d`. Per gold `g`:
`S_g = #{i: d_i < d_g}`, `T_g = #{i: d_i = d_g}`, `f(S,T) = 0 | 1 | (k−S)/T` on
`S≥k | S+T≤k | otherwise`. MATH-1 identity: `E[FR] = (1/m)·Σ_g f(S_g,T_g)` [PROVED, gate-checked].

**Profile class P(C) (spike+bulk, stated premise):** call gold `g` *free* if
`S_g+T_g ≤ k`; *spiked* if `S_g < k` and `T_g ≥ C` (gold sits in a duplicate cluster of
size ≥ C); *buried* if `S_g ≥ k`. Class P(C) = profiles where every non-free,
non-buried gold is spiked (bulk docs may do anything — no independence assumed anywhere).

> **Lemma (retrievable mass + tie tax).** Let `R_free, R_spike, R_buried` be the fractions
> of free/spiked/buried golds. Then, pointwise in the profile:
> (a) `E[FR] ≤ R_free + R_spike` (retrievable-mass upper bound) and `E[FR] ≥ R_free`
> (free-mass lower bound);
> (b) `f` is nonincreasing in `S` (fixed `T`) and in `T` (fixed `S < k`);
> (c) **under premise P(C):** `E[FR] ≤ R_free + (k/C)·R_spike` (tie tax: each spiked gold
> contributes at most `k/C`; at `k=3, C=2` that is 1.5 — weak; at `C=4` it is 0.75 —
> binding exactly when clusters are large).

**Proof sketch with gap labels.**
(a) [PROVED] Pointwise `f(S_g,T_g) ≤ 1{S_g<k}` (case check: 0≤0; 1≤1; `(k−S)/T ≤ 1`
since `T > k−S` in the partial regime) — average for the upper bound; `f ≥ 1{S+T≤k}`
likewise for the lower. No probability beyond linearity.
(b) [PROVED] In `S`: 1 → partial → 0 as `S` crosses `k−T, k`; within partial,
`(k−S)/T` strictly decreases. In `T` (fixed `S<k`): 1 while `T ≤ k−S`, then
`(k−S)/T` strictly decreases. Finite case analysis.
(c) [PROVED **conditionally**] For spiked `g`: `f = (k−S_g)/T_g ≤ k/T_g ≤ k/C`
(using `S_g ≥ 0`, premise `T_g ≥ C`); buried contribute 0 ≤ k/C, free contribute ≤ 1.
Average. [GAP — the premise] Membership in P(C) for real b-bit profiles is
**conjecture as a universal**; as an empirical regularity it is **supported**:
MATH-1 §2c retrievable-regime tie buckets 12.7× (TOP48) / 6.7× (RAND48) over binomial,
i.e. retrievable golds disproportionately sit in clusters — but "every" was not shown,
and bulk-only questions (no duplicates) leave P(C) vacuous (`R_spike=0`, bound = (a)).
Discriminating data (unchanged from MATH-1 §4): dedup ablation shrinking retrievable `T`
toward binomial would promote the premise to mechanism.

**Why this is the cleanest true theorem available.** (a)–(b) are exact and assumption-free;
(c) isolates the single load-bearing empirical premise (cluster floor C) instead of the
rejected global ones (A1/A2 independence). It explains the separation paradox in one line:
TOP48's means win while its mass sits in `R_spike` with large `T` — taxed by (c) — whereas
RAND48 holds more `R_free`. It does NOT predict which construction maximizes `R_free`:
that is benchmark-local (C5) and stays empirical.

**Lean shape (future; Muse-only cost rule — no prover APIs used).** All quantities are
`ℕ`-valued `(S_g, T_g)` over `Fin n`; `f` is a `ℚ`-valued piecewise definition;
(a)–(c) are `∀` statements over finite sums (`Finset.sum / card`) — no measure theory,
no analysis axioms; monotonicity is `decide`-adjacent case analysis. The premise P(C)
enters as an explicit hypothesis. Estimated formalization: definitions + ~50 lines.

## 5. Limits, repro, files

- Certificates are **benchmark-conditional** (frozen LME-470 / LoCoMo-1535, exploratory,
  not preregistered): they quantify the ladder on *these* questions, not future data.
  Cross-benchmark transport is disclaimed (D3/C5).
- LME float96 anchor 0.4416 cited from frozen lineage, not recomputed; no LoCoMo float
  anchor exists in the frozen artefacts, so C3 is LME-only.
- LIT-CHECK: no network; literature pointers in §1(d) (order-statistics tie laws, JL
  floors, MATH-2 S2) are from knowledge — flagged, not pursued, verify before citing.
- Repro: `python3 /tmp/cert/cert_compute.py` (~40 s; asserts halt on any gate failure);
  outputs `/tmp/cert/cert_details.json` (cert table + per-question mc/ex arrays for
  NATIVE + 9 family arms per benchmark + bootstrap spec).
- Relation to prior nulls: m1 no-edge vs-best nulls (−1.62pp LME / −1.20pp LoCoMo) govern
  *learned-selection* claims, a different estimand; our families are pre-declared, so no
  null correction applies — but the same discipline (no best-of-seeds) is why RANDavg,
  not best-seed, is certified.

CERT_VERDICT is printed below (chat) and follows from the table in §3 + lemma in §4.
