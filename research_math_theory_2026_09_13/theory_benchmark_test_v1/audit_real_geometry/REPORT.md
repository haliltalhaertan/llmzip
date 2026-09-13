[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# REPORT — where the mathematical inference failed (real-geometry audit)

Workspace: `/home/mdp/muse-work/theory-audit-real-geometry` · `verify.py` (exit 0, 27/27) ·
`results.json` · `selected_ids.json` · `STATUS.md`. All prior sources read-only; nothing old edited.

## 0. Outcome first

The conditional synthetic theorems are intact; every transfer step from theorem to
benchmark is broken or unidentified. Independently recomputed from stored per-query
tables: LME −6.44326pp (nominal CI [−9.2734,−3.6871]), LoCoMo −2.58291pp (CONDITIONAL,
[−3.7768,−1.3132]), REALTALK −0.093606pp ([−1.9330,+1.8490], inconclusive, not a
falsification), PerLTQA +2.46415pp ([+1.5540,+3.4428]). Reciprocal identity
LOW48(t)==HIGH48(1/t) holds exactly (maxdiff 0.0, all four benchmarks): HIGH48 is
algebra, not evidence. The derived scaled-cosine group decomposition equals direct
cosine ordering and exact FR@3 on all 52 subset queries × 5 t (worst abs diff
6.7e−16, 0 rank mismatches, 0 FR mismatches; exact-`==` ties, no tolerance).
Sign encodings are invariant across t by construction (0 violations).
Concrete flip witnesses show the reversing term is the amplified LOW48 group-dot
numerator — i.e. the alleged "nuisance" group carries gold-favoring signal
(H3 fails on real arrays). No causal account of baseline gaps is established;
witnesses are oracle/descriptive, never predictive, never population rates.

**Özet (Türkçe):** Koşullu sentetik teoremler geçerli; teoriden gerçek veriye giden her
köprü kırık ya da tanımsız. Dört birincil etki bağımsızca yeniden hesaplandı
(LME −6.44pp, LoCoMo −2.58pp koşullu, REALTALK −0.09pp belirsiz, PerLTQA +2.46pp).
HIGH48 karşılıklılık özdeşliği tam (0.0) — bağımsız kanıt değil. Türetilen ölçekli
kosinüs grup ayrışımı, 52 sorguda doğrudan sıralamayla birebir uyuştu. İşareti
değiştiren terim, sözde "bozucu" LOW48 grubunun altın belge lehine nokta çarpımı;
bu etiket gerçek dizilerde çöküyor. Nedensel açıklama yok; tanıklar yalnızca
betimleyici.

## 1. What was tested, and what the math actually proves

Model H (sign_mechanism REPORT §3 + all_n_ranking REPORT §2, corrected) proves a
conditional statement: **if** docs/queries obey the stated Rademacher-nuisance law
with equal norms, shared nuisance scale t, and labeled signal/nuisance coordinates,
**then** sign-vs-cosine dominance flips with t (pairwise 13/16 vs 31/32 at t=1/2 and
11/16 at t=10 — re-verified exactly in `verify.py` §A; corrected shared-gold
transport N6 SIGN 1763/2048, cosine(t=1/2) 4067/4096, cosine(t=10) 1483/2048 per
COORDINATOR_REVIEW). The benchmark PLAN (PLAN.md:9) explicitly states Model H
"proves an ordering for synthetic signal/nuisance vectors, NOT arbitrary benchmark
vectors" and that proxies "mean low/high query magnitude, NOT proven
nuisance/signal dimensions" (PLAN.md:21). The failure is therefore not in the
theorem — it is in five transfer assumptions (H1–H5) plus four inference overreaches,
evidence below. Coordinator corrections supersede worker prose throughout.

## 2. Technical evidence

### 2.1 Raw primaries independently recomputed (§B, 7050+1535+10575+90915 rows)

| benchmark | n | contrast pp | nominal 95% CI pp | reciprocal maxdiff | violators |
|---|---|---|---|---|---|
| LME | 470 | −6.443262 | [−9.2734,−3.6871] | 0.0 | 114/470 |
| LoCoMo | 1535 | −2.582907 | [−3.7768,−1.3132] | 0.0 | 151/1535 |
| REALTALK | 705 | −0.093606 | [−1.9330,+1.8490] | 0.0 | 41/705 |
| PerLTQA | 8265 | +2.464151 | [+1.5540,+3.4428] | 0.0 | 961/8265 |

Point estimates match coordinator values to <1e-9; CIs reproduced with the
prespecified seed/method (archive-cluster, 2000 reps, seed 20260913). Four primaries
unadjusted; no pooling/familywise claims. LoCoMo stays CONDITIONAL (float historical
gate not met — substituted fresh baseline; PLAN required abort). REALTALK CI covers
substantial effects in both directions: no support, not falsification.

### 2.2 Rank-equivalent decomposition (derived, not quoted)

For group G scaled by t>0 on both C and q, with D_G=C_G·q_G, D_C=complement dot,
nGd/nCd doc norm-squares, nGq/nCq query norm-squares:

s_t(d) = (t²·D_G(d) + D_C(d)) / ( √(t²·nGd(d)+nCd(d)) · √(t²·nGq+nCq) )

On the disclosed subset (lexicographic first-10 valid qids per benchmark, outcome-
blind, + ≤3 illustrative outcome-selected violators labeled as such;
`selected_ids.json` written BEFORE computation; one overlap RT01_q002 counted twice
→ 41 deterministic rows, disclosed): formula vs direct scaled cosine over the full
t grid gives worst abs diff 3.9–6.7e−16 (a few ulps), **0 rank mismatches, 0 exact
FR@3 mismatches** (per-query tie buckets S/T under exact `==`; no invented
tolerance). Residual ulps and rank differences counted, not approximated away.

### 2.3 Flip witnesses (ORACLE/DESCRIPTIVE ONLY)

LME `15745da0` (gold doc 56 vs rival 368), LOW48, nGq share only 1.0%:

| t | gold score | rival score | leader |
|---|---|---|---|
| 0.25 | +0.83267 | +0.89243 | rival |
| 1.0 | +0.78322 | +0.83186 | rival |
| 4.0 | +0.54574 | +0.53903 | gold (+0.0067) |

Reversing term: gold group-dot 0.01860 > rival 0.01601; ×t²=16 the numerator gains
+0.298 vs +0.256, overcoming gold's complement deficit (0.732 vs 0.791) while both
denominators grow. The flip is carried by LOW48-group signal favoring gold —
the proxy label "nuisance" is false on this array. Same pattern (group-dot term
reverses prediction; FR 0→1 across endpoints on the selected flip) in LoCoMo
`locomo_0_qa33`, REALTALK `RT01_q026`, PerLTQA `PQ000_PRF_q001` (full numbers in
`results.json` → geometry → witness). Gold/rival were chosen USING the observed
flip: description of one array, not a model, not a rate.

### 2.4 H-assumption evidence table (proven-from-arrays vs unidentified)

| # | assumption | result on direct arrays | status |
|---|---|---|---|
| H1 | equal doc norms (Model H needs them for dot==cosine order) | norm CV 0.024–0.037, max/min up to 1.29 (41 det queries) | PROVEN-FAILED |
| H2 | fixed signal alignment | gold cosine@t=1 spans [−0.20,+0.96] across subset | PROVEN-FAILED |
| H3 | LOW48 is pure nuisance | gold group-dot share of total spans [−0.49,+3.81]; sign varies | PROVEN-FAILED |
| H4 | independent queries | 470/470, 705/10, 1535/10, 8265/30 QA-per-cluster; CIs cluster-based | iid PROVEN-FAILED; deeper sharing UNIDENTIFIED |
| H5 | t = synthetic nuisance scale; t=1 = balance point | t=1 is unmodified embeddings; sign invariant (0 viol.); float moves by reweight+renorm; reciprocal exact | PROVEN-MISMATCH |
| — | true signal/nuisance partition of the 96 coords | no labels exist; proxy gold-free by design | UNIDENTIFIED |
| — | causal mechanism of baseline gaps | post-hoc diagnosis only | UNIDENTIFIED |

## 3. Ranked error ledger

1. `LOW48 ≈ nuisance coords` → H3 range + LME witness (group-dot flips rival→gold)
   → correction: query-magnitude proxy, sometimes signal-bearing → Model-H theorem
   still valid (conditional) → next test: predeclared per-QA regression of
   endpoint contrast on gold-minus-rival group-dot advantage from frozen tables.
2. `equal norms, dot==cosine` → H1 (ratio ≤1.29) → correction: normalization is
   load-bearing; synthetic reduction inapplicable → exhibit still valid → next test:
   same-subset flips under raw dots vs cosine; differing flip sets implicate norms.
3. `aggregate trend ⇒ pointwise law` → 114/470, 151, 41/705, 961 adjacent-decrease
   → correction: report aggregate-only; monotonicity rejected for this proxy →
   aggregates stand as observed → next test: violator rate vs rival-margin size
   (near-tie QAs should flip more).
4. `HIGH48 = independent control` → reciprocal maxdiff exactly 0.0 ×4 →
   correction: 4 tests, not 8; HIGH48 is a sanity identity → identity stands →
   next: stop citing it as corroboration.
5. `REALTALK negative = falsified` → CI [−1.93,+1.85] → correction: no-support,
   not absence → pointwise rejection (41) stands → next: predeclared equivalence
   bounds or wider archive sample.
6. `LoCoMo = gated PASS` → float historical gate missing (fresh baseline
   substituted) → correction: CONDITIONAL/PROTOCOL-DEVIATION → numbers stand as
   exploratory → next: locate historical float arrays; resolve +12pp vs +6.83pp
   provenance before any confirmatory use.
7. `unconditional multinomial transport` (original sign_mechanism §5) →
   ALGEBRA ERROR: shared-gold dependence ignored → correction: conditional-on-gold
   values (N6 1763/2048 etc.); both directions survive → pairwise/exhibits stand →
   next: none.
8. `sign invariance supports theory` → TAUTOLOGY: positive scale preserves signs
   by construction (verified, 0 viol.) → correction: construction check only; the
   whole outcome is float reweighting → stands as check → next: none.
9. `Model H explains baseline gaps` → no labels, post-hoc → correction: withhold
   all causal claims; witnesses labeled oracle → nothing causal stands → next:
   preregister H1–H3-style directional tests (with corrected signs) before running.

Separation audit: algebra error #7; wrong assumptions #1–#3, H1/H2; unidentifiable
mapping #9 + partition row; metric mismatch #3 (aggregate-vs-pointwise) and
exact-vs-MC (reported separately, never gated to each other); numerical bugs: two
of my own (uncommented header banner; mixed D-convention gap formula 2−2tD vs
2+tD) — both caught by execution, fixed, disclosed; inference overreach #4, #5,
#6, #8. No 'proven cause' is claimed from correlation anywhere above.

## 4. Commands, counts, provenance (exact)

- `sha256sum` PLAN + 4 COORDINATOR_REVIEWs + sign_mechanism/all_n_ranking
  REPORT+REVIEW (before reads): a0f9e8e6…, 537960d5…, dba3a662…, 3aaabbc7…,
  a80f3bcd…, b5c2752f…, 351a679b…, 137c7aae…, 2e3d7242….
- Reads (file+line cited): PLAN.md:9,21,35; run_lme.py:163–170 (C/qC/gold),
  run_locomo.py:36–66 + load_all (C/QC/id_to_row + RAW/AUDIT), 
...[truncated 911 chars]