# V52 HEAD32/TAIL64 CAUSAL RESULT — COLD-START INDEPENDENT AUDIT

**Auditor:** independent cold-start session. No verdict, gate result, finding or number from any
prior session was supplied to this audit, and none was inferred. Every figure below was measured
by the auditor from repository bytes or produced by the auditor's own execution.

**Date:** 2026-09-04
**Audit branch:** `audit/v52-head-tail-causal-independent-2026-09-04`

---

## 0. Verdict

> ## `AUDIT PASS WITH CAVEATS`

The Head32/Tail64 causal lead **survives independent scrutiny in direction and in its
preregistered band verdict**. Two things in its presentation must be narrowed: the *precision*
attached to `rho_2`, and the word *"cross-benchmark"*.

**The exact claim I would accept:**

> On the two frozen benchmarks LoCoMo (n=1535) and LongMemEval (n=470), under the preregistered
> `HEAD32_TAIL64_HAAR` intervention with five Haar draws (seeds 56001–56005), restricting
> orthogonal mixing so that the leading 32 archive-local SVD coordinates mix only among
> themselves and the remaining 64 only among themselves preserves most of the native
> SIGN96-vs-Full-Haar retrieval advantage: `rho_2 ≈ 0.11` (LoCoMo) and `≈ 0.16` (LongMemEval),
> each with a five-draw standard error of roughly ±0.05 and ±0.02 respectively. Both land in the
> preregistered `rho_2 <= 0.25` band, and every individual seed does too. The effect depends on
> *which* coordinates form the 32-block, not merely on the existence of a 32/64 block structure.
> This is a consistent finding across two frozen datasets evaluated through one shared
> representation recipe, estimator and codebase — not two independent replications.

**Established vs. not falsified.** I report as **established**: artifact identity and
provenance (G1, G2, G3, G5, G9, G10); the numerical reproduction of the primary results on both
benchmarks (G4); the shard semantics (G8); and the position-dependence of the effect on LoCoMo
(G7). I report as **not falsified but not established**: the *magnitude* of `rho_2` at the
precision printed, and any generalization beyond these two frozen cohorts.

---

## 1. Binding to the target — digests I measured myself

I fetched `main` by name and verified the governing prompt before reading it:

| Item | Measured SHA-256 | Declared | |
|---|---|---|---|
| `prompts/V52_HEAD_TAIL_CAUSAL_INDEPENDENT_AUDIT_PROMPT_2026-09-04.md` @ `origin/main` | `a312ef675d16ee9dbbbddb463aad9794fd3fd5ff8a56813e76d7462f3a660528` | same | MATCH |

The repository's GitHub default branch does not serve this content; `main` and the research
branch were fetched by name and commits addressed directly.

**Audit target:** commit `7799502bc3a157f874b4b1aa76f803ec2bf6432f`, tree
`1a76eacd063331cef4498595956cf7b311151799`, on branch
`research/v52-sign-mechanism-locomo-2026-09-04`.

Note: the target commit is **not** the branch head. The branch head at audit time is
`eb8a44263575fb2fae9b58ed4d5f52f6b7c67abc`, thirteen commits later. `7799502b` is a verified
ancestor of that head. This audit binds to `7799502b`; the later commits are discussed only in
§G7 and §Scope, and no result from them is used as evidence here.

### Git blob ids at the target commit (all measured)

| Artifact | Measured blob | Declared | |
|---|---|---|---|
| Head/Tail preregistration | `0d34207be55a75194b585789c7139cbc8aeb264d` | same | MATCH |
| Spectral-band preregistration | `02aa91a12b4052bbb2f0a6617167c8851e4f71f7` | same | MATCH |
| LoCoMo head/tail summary | `228f756447e70c73f40b6074a44f13acabdabc08` | same | MATCH |
| LongMemEval head/tail summary | `86b3718a9af1d6f86a0a3478ad0b83bf6dd0caf8` | same | MATCH |
| Cross-benchmark checkpoint | `9923c5284c04dd9b2acb345dcb7f0c92e4584b06` | same | MATCH |
| LoCoMo runner | `cb16d4136c6280875b7c5875ffd89f9fc01cb810` | same | MATCH |
| LongMemEval shard runner | `184a8a4bbb7d991c875ee1dcb92aa85b5e718074` | same | MATCH |
| LoCoMo base module | `7c4140252fb7f846d617189925cdf534515743f4` | same | MATCH |
| LongMemEval base module | `79dd4a5ec462102da5d82530088a4b7e89bef437` | same | MATCH |

### SHA-256 and byte counts (all measured)

| Artifact | Measured SHA-256 | Measured bytes | Declared | |
|---|---|---:|---|---|
| Head/Tail preregistration | `6830c91b01d5df1a87b1a76f25b0101049b47c292c6ea867f48988998aa5ff05` | 6624 | `6830c91b…`, 6624 | MATCH |
| Cross-benchmark checkpoint | `9cc773d9153c3dbb6431044e4123c026a15aa6000a7796060590f8e18bc2b9c3` | 5190 | `9cc773d9…`, 5190 | MATCH |
| LongMemEval adapter v1 | `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722` | 23084 | same | MATCH |
| LongMemEval adapter v2 | `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218` | 17158 | same | MATCH |

Digests **not** previously declared, measured here for the record:

| Artifact | Measured SHA-256 |
|---|---|
| `V52_CAUSAL_SPECTRAL_BAND_HAAR_PREREG_2026-09-04.md` | `596bb8bcfa4c6aa16957c92a210931cd0171a25da9c48bb7ac0c2ed9a32e84ca` |
| `V52_HEAD_TAIL_CAUSAL_PROVENANCE_MANIFEST_2026-09-04.json` | `fbeb07f40ca912baf946b2939de56038972b04c4b471d7fa0f569dcf136961c3` |
| `locomo_head_tail_two_subspace_causal.py` | `835669586c5f96e24f54dba7a85ebad4ff4dc6f417d169dac01cbca58af080d5` |
| `longmemeval_head_tail_shard.py` | `548a8f8824fa5054e5191068cf404f91a35f9f09ef794be842825169e0328706` |
| `locomo_head_tail_outputs/locomo_head_tail_summary.json` | `71c45b615a4073c5eeeb9c38e0d4dca3c984e34989ba4f3b12d27df279cc2f8f` |
| `longmemeval_head_tail_outputs/longmemeval_head_tail_summary.json` | `691fa4cd2e6bdcebac17bbc58efde9e6ddcba7a5ca705e1344293e09316e1255` |

Nothing was audited on substitute bytes. `scripts/verify_target_digests.sh` re-runs all of the
above and exits 0; its output is `evidence/digest_verification.txt`.

---

## 2. Method and environment

The auditor reproduced the pinned numerical stack from the committed `environment.txt`
(numpy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, scipy 1.17.0) on **Python 3.11.15**. The CI
workflows used **Python 3.13**. This version difference is deliberate and useful: the results
below reproduced across two different Python versions and two different BLAS builds.

Both frozen datasets were downloaded independently by the auditor from their public sources and
byte-verified before use. Neither was taken from the repository or from any prior session.

---

## G1 — Preregistration genuinely preceded outcome access — **PASS (established)**

I did not rely on commit timestamps. Four structural facts, each measured:

1. **The preregistration blob appears in exactly one commit in the entire history**
   (`6fe2374`, "research(v52): preregister head-vs-tail two-subspace causal test") and has
   exactly one blob id. It was never amended, rewritten, or re-committed.
2. **`6fe2374` is a git ancestor** of the commit that introduced the LoCoMo runner (`90112d3`),
   the LongMemEval shard runner (`3d101fd`), the LoCoMo outputs (`cf5eca7`), the LongMemEval
   outputs (`12b53ae`), and the cross-benchmark checkpoint (`a118589`). Ancestry, not clock.
3. **Each result file names the preregistration blob it followed**, and that blob is the one
   actually on the branch: both summaries carry
   `"prereg_git_blob": "0d34207be55a75194b585789c7139cbc8aeb264d"`, which equals the measured
   blob id of the preregistration at the target commit.
4. **The CI itself hash-gates the preregistration before executing.** Both Head/Tail workflows
   contain, as a step that runs before the experiment:

   ```
   test "$(git hash-object research/v52/V52_CAUSAL_HEAD_TAIL_TWO_SUBSPACE_HAAR_PREREG_2026-09-04.md)" = "0d34207be55a75194b585789c7139cbc8aeb264d"
   ```

   plus equivalent gates on every frozen source module. The run cannot produce an outcome unless
   those exact preregistration bytes are present. I confirmed via the GitHub API that both
   Head/Tail runs completed `success` at head SHAs (`5a0e8023`, `c30c36d4`) that have `6fe2374`
   as an ancestor.

Additionally, the runners were each introduced in exactly one commit and **never modified
afterwards** — the code on the branch is the code that produced the outputs.

**Could any result have been produced before the preregistration bytes existed?** No. To do so
the author would have had to defeat the workflow's own hash gate, and would have had to leave a
different runner blob or a second prereg blob in history. Neither exists.

**Is the backward-disclosure complete?** The preregistration openly states (§1) that the
previous stage's outcomes were seen first and generated this hypothesis, and it quotes the two
prior `rho` values (`0.06523571501071657`, `0.14282724238436822`) and the qualitative
`HAAR_MID_LOW64` observation. I checked whether any **Head/Tail-specific** quantity leaked
backwards into the preregistration: it contains no `rho_2`, no `HEAD32_TAIL64_HAAR` mean, and no
per-seed value for seeds 56001–56005. The frozen native and Full-Haar constants it cites are
pre-existing constants inherited unchanged from the prior stage (verified: the identical
constants `0.13770827054136` and `0.38271666666667` appear in the prior stage's own summary
JSONs at this commit). The new seeds (56001–56005) are disjoint from the prior stage's
(55001–55005). **The disclosure is complete and no Head/Tail-specific quantity leaked backwards.**

---

## G2 — Frozen parameters actually frozen in the executed code — **PASS (established)**

Preregistration text compared line-by-line against the executed source. Every primary
parameter is faithfully implemented:

| Preregistered | Implementation | |
|---|---|---|
| `Head32 = 0..31`, `Tail64 = 32..95` | `HEAD=np.arange(0,32)`, `TAIL=np.arange(32,96)` in both runners | OK |
| Seeds `56001`–`56005` | `SEEDS=[56001,…,56005]` in both runners | OK |
| `R_2 = diag(Q_head32, Q_tail64)` | `R=zeros((96,96)); R[:32,:32]=haar_q(rng,32); R[32:,32:]=haar_q(rng,64)` | OK |
| Haar via IID normal + QR + deterministic diagonal-sign correction | `A=rng.standard_normal((d,d)); Q,R=qr(A); sg=where(diag(R)<0,-1,1); return Q*sg[None,:]` | OK |
| Head Gaussian **first**, Tail **second**, from **one** RNG stream | single `rng=default_rng(seed)`, head drawn then tail | OK |
| top-k | `TOPK = 3` | OK |
| zero-threshold sign quantization | `D = C >= 0`, `QB = Q >= 0` | OK |
| rotation applied **after centering, before sign quantization** | `C=(Y-mu)`; then `Cr=C@R`; then `D=Cr>=0` | OK |
| same `R_2` applied to archive **and** query | `Cr=C@R`, `Qr=QC@R` | OK |
| tie/nuisance scheme unchanged | `N_NUISANCE=20`; priority seeds identical to the frozen base (`stable_archive_seed(ci,t)+99` for LoCoMo; `5_100_000+lex*100_000+t*100+99` for LongMemEval) | OK |
| decision bands `0.25` / `0.75` | `if rho<=0.25 … elif rho>=0.75 …` in both runners | OK |
| cross-benchmark rule | same regime on both → `[CROSS-BENCHMARK HEAD-TAIL CAUSAL LEAD]` | OK |
| controls at `1e-12` (orthogonality, native reproduction, norms, dots) | `TOL=1e-12`, each enforced with `raise` | OK |
| signed-permutation Hamming invariance exact | `np.array_equal(dsp, dist0)` else `raise` | OK |
| cohort guards | `if valid != 1535: raise`; `if len(results)!=470 … raise` | OK |

**Divergences found. All three are diagnostic-only and cannot change the verdict:**

1. `longmemeval_head_tail_shard.py:29-30` **re-defines `haar_q` locally** instead of importing
   the frozen `base.haar_q`. I compared them: the two implementations are logically identical
   (same construction, same deterministic sign correction). The divergence is a maintenance
   hazard — had the base drifted, the two benchmarks would have silently used different Haar
   constructions — not an error in this execution.
2. `longmemeval_head_tail_shard.py:41-46` re-defines `pairwise` rather than importing
   `base.pairwise_counts`, and reports a **`tie_fraction`** column where LoCoMo reports a
   **`tie_count`** column. Same underlying quantity, different normalization. The preregistered
   §10 diagnostic ("pairwise gold-vs-nongold discrimination") is computed identically on both.
3. The LongMemEval `hard_negative_rescue.csv` omits the raw numerator columns
   (`head_bad_full_good`, `head_good_full_bad`) that the LoCoMo file carries. The two reported
   ratios are computed the same way. Cosmetic asymmetry in a §10 secondary diagnostic.

One further observation, not a divergence: `L_full` is computed as `native - FROZEN_FULL_HAAR_R3`
using the **recomputed** native rather than the frozen native constant. Since the native
reproduction error is exactly `0.0` on both benchmarks, the two are bit-identical here, so the
estimand matches §8 exactly.

---

## G3 — Source and cohort identity — **PASS (established)**

Verified by the auditor from independently downloaded bytes, not from the repository:

| Item | Measured | Declared | |
|---|---|---|---|
| LoCoMo dataset SHA-256 | `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4` | same | MATCH |
| LoCoMo dataset bytes | 2 805 274 | 2 805 274 | MATCH |
| LoCoMo audit-layer manifest SHA-256 | `90a4e94c9247d8ace7aaf62acdda7315744b111d84e42658cccfeb0a3c89df06` | same | MATCH |
| LongMemEval dataset SHA-256 | `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442` | same | MATCH |
| LongMemEval dataset bytes | 277 383 467 | 277 383 467 | MATCH |
| LongMemEval adapter v1 / v2 SHA-256 | as §1 | same | MATCH |
| LoCoMo evidence-valid denominator | 1535 | 1535 | MATCH |
| LongMemEval primary cohort | 470 | 470 | MATCH |

The audit-layer manifest deserves emphasis: I did not take the manifest hash on trust. I
re-downloaded all 20 audit files, recomputed each file's size and SHA-256, re-serialized the
canonical sorted JSON myself, and hashed it. The result is `90a4e94c…3c89df06`, matching. The
cohort sizes are not merely declared — they are enforced by `raise` in the runners and were
re-hit by the auditor's own executions.

These are the accepted frozen sources, not re-derived ones: the LoCoMo dataset and audit layer
are fetched from fixed upstream URLs and hash-gated; the LongMemEval dataset is fetched from a
fixed HuggingFace URL and gated on both byte count and SHA-256.

---

## G4 — Re-derivation from raw outputs and end-to-end re-execution — **PASS, with a stated gap**

### G4a — A real gap in the committed raw artifacts

The audit brief asks for the per-seed R@3 to be rebuilt from **per-question** CSVs. **Those do
not exist.** I enumerated every committed output file at the target commit. The lowest-level
persisted artifacts are already aggregates:

| File | Bytes | Granularity |
|---|---:|---|
| `locomo_head_tail_seed_results.csv` | 271 | one row per seed |
| `locomo_head_tail_subset_r3.csv` | 513 | one row per (seed, subset) |
| `locomo_head_tail_pairwise.csv` | 1528 | one row per (seed, subset) |
| `locomo_head_tail_hard_negative_rescue.csv` | 406 | one row per seed |

The runners **do** compute per-question values — `locomo_head_tail_two_subspace_causal.py:105`
builds rows carrying `question_id` — but line 151 collapses them with a `groupby(...).mean()`
before writing, and the per-question frame is never persisted. The same is true of the
LongMemEval aggregator. **No per-question record of this experiment survives in the repository.**

This is a genuine reproducibility deficiency and I record it as such: from committed bytes
alone, the deepest available check is cross-file consistency, which proves only internal
coherence. I therefore did **not** pass this gate on inspection. I closed it by the stronger
route the brief asks for instead.

### G4b — Cross-file consistency (what the committed bytes alone support)

Rebuilding the summary from `*_seed_results.csv` and cross-checking against the independently
written `*_subset_r3.csv` (`evidence/rederivation_from_raw_csvs.txt`): all five per-seed values
on each benchmark match the summary JSON exactly, and the `Full96` rows of `subset_r3.csv` agree
with `seed_results.csv` to within 2.78e-17 on LoCoMo (three seeds differ in the last ULP) and
exactly on LongMemEval. The ULP-level disagreement is itself mild evidence that the two files
were produced by genuinely separate accumulation paths rather than copied.

Rebuilt from the CSVs, on both benchmarks: `mean(seed R@3)`, `L_full`, `L_2`, `rho_2` and the
regime string all reproduce the declared values **exactly** (bit-for-bit float equality).

### G4c — End-to-end re-execution from the committed runners — the decisive test

**LoCoMo.** I executed the committed runner
(`research/v52/locomo_head_tail_two_subspace_causal.py`, blob `cb16d413…`) unmodified, on the
frozen inputs it downloaded and hash-verified itself, in the pinned package stack on Python
3.11.15. Result (`evidence/locomo_end_to_end_rerun_diff.txt`):

| Output file | Committed vs auditor |
|---|---|
| `locomo_head_tail_seed_results.csv` | **byte-identical** |
| `locomo_head_tail_subset_r3.csv` | **byte-identical** |
| `locomo_head_tail_pairwise.csv` | **byte-identical** |
| `locomo_head_tail_hard_negative_rescue.csv` | **byte-identical** |
| `locomo_head_tail_summary.json` | differs in **one** field |
| `LOCOMO_HEAD_TAIL_CAUSAL_CHECKPOINT.md` | differs in the same field |

The sole difference is the control diagnostic `continuous_dot_max_abs_error`:
committed `1.6653345369377348e-15`, auditor `1.5543122344752192e-15`. Both are BLAS-dependent
floating-point roundoff measurements, and both sit roughly **three orders of magnitude below**
the runner's own `1e-12` tolerance. No primary quantity differs.

Every primary number reproduced bit-for-bit:
`native_R3 = 0.23654714666441054`, `head_tail_haar_mean_R3 = 0.22592744129014436`,
`L_full = 0.09883887612305053`, `L_2 = 0.01061970537426618`,
**`rho_2 = 0.10744461886682183`**, and all five per-seed values.

**LongMemEval.** I executed the committed shard runner
(`research/v52/longmemeval_head_tail_shard.py`, blob `184a8a4b…`) unmodified as five shards plus
the aggregate step, on the 277 383 467-byte dataset the runner downloaded and hash-verified
itself. Each shard reported exactly 94 questions (5 x 94 = 470)
(`evidence/longmemeval_end_to_end_rerun_diff.txt`):

| Output file | Committed vs auditor |
|---|---|
| `longmemeval_head_tail_seed_results.csv` | **byte-identical** |
| `longmemeval_head_tail_subset_r3.csv` | **byte-identical** |
| `longmemeval_head_tail_hard_negative_rescue.csv` | **byte-identical** |
| `longmemeval_head_tail_summary.json` | differs in **one** field |
| `LONGMEMEVAL_HEAD_TAIL_CAUSAL_CHECKPOINT.md` | differs in the same field |
| `longmemeval_head_tail_pairwise.csv` | 2 of 15 rows differ in the last ULP |

Again every primary number reproduced bit-for-bit:
`native_R3 = 0.5419751773049646` (reproduction error exactly `0.0`),
`head_tail_haar_mean_R3 = 0.5170209219858156`, `L_full = 0.1592585106382946`,
`L_2 = 0.024954255319148966`, **`rho_2 = 0.15669024668844653`**, and all five per-seed values.

The two differences are both non-primary: `continuous_dot_max_abs_error` (committed
`6.661338147750939e-16`, auditor `7.771561172376096e-16` — the same BLAS-dependent roundoff
control as on LoCoMo, ~4 orders below the `1e-12` tolerance), and two rows of the *secondary*
`gold_minus_nongold_same_sign_advantage` diagnostic differing at ~3e-17 from float summation
order. Neither can move `rho_2` or the band verdict.

**Conclusion for G4.** The primary numbers are not merely internally consistent — they are
independently regenerable from public frozen inputs by the committed code, across a different
Python version and BLAS. The gate passes on execution. The absence of persisted per-question
artifacts remains a recorded deficiency (see §Recommendations).

---

## G5 — Does the verdict follow mechanically from the preregistered rule? — **PASS (established)**

Band assignment recomputed by the auditor from the rebuilt `rho_2` values, applying §8 of the
preregistration directly:

| Benchmark | `rho_2` (rebuilt) | `<= 0.25`? | Regime derived | Regime declared | |
|---|---:|---|---|---|---|
| LoCoMo | `0.10744461886682183` | yes | `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]` | same | MATCH |
| LongMemEval | `0.15669024668844653` | yes | `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]` | same | MATCH |

Both benchmarks land in the same regime, so §9's first branch applies and yields
`[CROSS-BENCHMARK HEAD-TAIL CAUSAL LEAD]` with the shared regime stated. The checkpoint declares
exactly that. The rule is applied mechanically with no discretion exercised.

**Nothing was altered after outcome access.** Bands (`0.25`/`0.75`), seed set (56001–56005),
band boundaries (`0..31`/`32..95`) and the estimand (`rho_2 = L_2 / L_full`) are identical in the
preregistration text and in both runners, and the preregistration blob is provably unamended
(G1). The §11 no-rescue/no-tuning list was checked item by item against the committed code and
outputs:

| §11 prohibition | Present in code or outputs? |
|---|---|
| alternate Head/Tail boundary sizes | **absent** — only `0..31`/`32..95` appears |
| learned boundary location | **absent** |
| variance-based resorting | **absent** — coordinates keep their existing SVD order |
| whitening / variance reweighting | **absent** |
| learned thresholds | **absent** — sign threshold is the literal `>= 0` |
| supervised rotations | **absent** — rotations are Haar from fixed seeds only |
| alternate top-k or distance metrics | **absent** — `TOPK=3`, Hamming only |
| extra / replacement random seeds | **absent** — exactly the five preregistered seeds |
| reranking or shortlist methods | **absent** |

---

## G6 — Statistical honesty of the reported quantity — **PASS ON VERDICT / FAIL ON REPORTED PRECISION**

The primary estimate is a mean over **five** Haar draws. Computed by the auditor
(`evidence/rederivation_from_raw_csvs.txt`):

| | LoCoMo | LongMemEval |
|---|---:|---:|
| `rho_2` (point) | 0.107445 | 0.156690 |
| per-seed R@3 s.d. | 0.010303 | 0.008776 |
| standard error of the mean (n=5) | 0.004608 | 0.003925 |
| **s.e. of `rho_2`** | **0.046620** | **0.024643** |
| per-seed `rho_2` range | **−0.0672 … +0.1748** | 0.0735 … 0.2039 |
| range width | 0.2420 | 0.1304 |
| approx. 95% CI (t, 4 d.f.) | **[−0.022, 0.237]** | [0.088, 0.225] |
| distance from the 0.25 boundary | 3.06 s.e. | 3.79 s.e. |

**(a) Is the verdict robust across seeds? Yes.** Every one of the ten individual seed-level
`rho_2` values (five per benchmark) is below the preregistered `0.25` boundary — the maximum
single-seed value anywhere is 0.2039 (LongMemEval, seed 56004). The verdict does not depend on
averaging: it holds draw by draw. Both benchmark means sit 3–4 standard errors inside the band.

**(b) Is the magnitude as precise as its presentation suggests? No.** This is the audit's
principal statistical finding. `rho_2` is reported as `0.10744461886682183` in the summary JSON
and as `0.107444619` in the checkpoint — nine to seventeen significant figures for a quantity
whose five-draw standard error is `0.047`. That is roughly seven orders of magnitude of spurious
precision. The checkpoint's derived phrasing "preserves **at least 75%**" is a band statement and
is fine, and the checkpoint does not itself print a percentage retained. But the retention
figure a reader will derive from the printed `rho_2` — `1 − 0.107444619 = 89.3%` on LoCoMo —
should be read as "roughly 85–90%, ±5 points," and the LoCoMo interval is wide enough to include
*complete* preservation (`rho_2 = 0`).

**Yes — a single seed inverts the sign of the estimated loss.** On LoCoMo, seed **56001** gives
R@3 `0.24319099434005997`, which is **above** the native `0.23654714666441054`. Its per-seed
`L_2` is negative and its per-seed `rho_2` is **−0.0672**: on that draw the intervention
*outperformed* the unrotated native representation. This is not reported anywhere in the
checkpoint or the summary, and it should be, because it is the clearest available signal that
`L_2` on LoCoMo is small relative to draw-to-draw noise.

**An error not counted at all.** `rho_2`'s denominator `L_full = native − FROZEN_FULL_HAAR_R3`
treats the Full-Haar reference as an exact constant. It is not: the spectral-band
preregistration §4C describes it as "the already frozen accepted mean Full-Haar result," i.e.
itself a mean over some number of Haar draws inherited from an earlier task. Neither its draw
count nor its dispersion is recorded in any Head/Tail artifact, and both constants are stored
truncated to 14 significant figures (`0.13770827054136`, `0.38271666666667`). `rho_2` is
therefore a ratio estimator with a noisy denominator of unquantified variance, which the reported
uncertainty ignores entirely. The truncation itself is harmless (~1e-15); the unquantified
sampling error of the denominator is not, and it can only widen the intervals above.

---

## G7 — Does the intervention establish what the claim says it establishes? — **PASS via auditor-supplied control**

The checkpoint's licensed interpretation attributes the effect to **spectral position**:

> "Head-vs-tail spectral separation, rather than exact individual principal axes or the
> Mid32/Low32 boundary, is load-bearing…"

The competing explanation the executed design must rule out: *any* 32/64 block-diagonal
structure preserves the advantage, because block-diagonality alone constrains the mixing —
irrespective of which coordinates land in which block. **At the audit target commit the executed
design contains no arm that varies which coordinates form the 32-block.** Every Head/Tail arm
uses `0..31` vs `32..95`. On the researcher's own evidence, this control is absent.

**Arms that bear on the question.** The prior spectral-band stage's secondary arms — present on
the branch at this commit and cited by the Head/Tail preregistration §10 as "frozen descriptive
references only" — do vary position, normalized on the same `L_full`:

| Prior-stage arm | LoCoMo `rho` | LongMemEval `rho` |
|---|---:|---:|
| `HAAR_MID_LOW64` — fix Head32 (`0..31`), rotate the rest | **0.030** | **0.177** |
| `HAAR_HIGH_MID64` — fix Low32 (`64..95`), rotate the rest | 0.518 | 0.311 |
| `HAAR_HIGH_LOW64` — fix Mid32 (`32..63`), rotate the rest | 0.672 | 0.571 |

Which 32 coordinates are protected matters by a factor of 3–20×. But these arms are weaker
support than they look: they use a *different* intervention shape (one block held at identity,
not both blocks Haar-rotated), they cover only three contiguous band positions, and — decisively
— their outcomes were **seen before** the Head/Tail preregistration was written, so they are
hypothesis-generating, not confirmatory.

**The control I supplied.** I ran the missing contrast myself on LoCoMo
(`scripts/auditor_random_partition_control.py`, result
`evidence/g7_random_partition_control.json`). Holding the cohort, representation, centering,
sign threshold, top-k, tie/nuisance scheme, seeds and estimand exactly as in the frozen code, I
compared:

- `HEAD32_TAIL64_HAAR` — Haar blocks on `{0..31}` and `{32..95}` (the preregistered arm);
- `RANDPART_32_64_HAAR` — Haar blocks on a **random 32-subset** of the 96 coordinates and its
  complement, five independent partitions, one per seed.

| Arm | mean R@3 | `rho_2` | advantage retained | per-seed `rho_2` |
|---|---:|---:|---:|---|
| `HEAD32_TAIL64_HAAR` | 0.22592744129014436 | **0.1074** | **89.3%** | −0.067 … 0.175 |
| `RANDPART_32_64_HAAR` | 0.14276241798269007 | **0.9489** | **5.1%** | 0.877 … 1.022 |

A random 32/64 split retains essentially none of the advantage — its mean R@3 of `0.1428` is
close to the Full-Haar floor of `0.1377`, and **all five** random partitions land in the
opposite preregistered band (`rho_2 >= 0.75`). The separation is **8.8×**. In the same run and
the same harness, the Head/Tail arm reproduced the committed
`rho_2 = 0.10744461886682183` bit-for-bit, which validates the control's machinery.

**What the evidence licenses.** That the effect depends on *which* coordinates form the
32-block, not merely on the existence of a 32/64 block structure, is now **established on
LoCoMo**. **What it does not license:** (i) I ran this control on LoCoMo only, so the
position-dependence is not established by me on LongMemEval; (ii) nothing here shows 32 is the
*optimal* or a *uniquely privileged* boundary — the checkpoint concedes this explicitly and
correctly; (iii) "leading SVD coordinates" is a property of the archive-local SVD basis, not of
any encoder or neuron axis, and the checkpoint's interpretation ceiling already says so.

**Scope note.** Thirteen commits after the audit target, the branch contains a preregistered
"matched random-partition null control" of its own (`483e5eb` … `88af865`), executed in CI runs
`33907122988` and `33907122993`. That work postdates the audit target and is outside this
audit's binding; I neither used nor verified its outcomes, and it requires its own audit. I note
only that the researcher independently identified the same missing control.

---

## G8 — Does sharding change semantics? — **PASS on semantics / NOT ESTABLISHED on "EXACT"**

The LongMemEval summary declares `"execution": "SHARDED_EXACT"`. Three separate questions:

**1. Is the partition disjoint and exhaustive? Yes — established.**
`longmemeval_head_tail_shard.py:76` selects `chosen=[x for i,x in enumerate(prim) if i%nshards==idx]`.
Over `prim` (the 470 non-`_abs` primary questions), `i % 5 == idx` for `idx ∈ {0..4}` is a
partition of `0..469` by construction. The aggregator independently enforces it
(`:95`): `if len(results)!=470 or len(set(qids))!=470: raise`. Per-shard integrity is also
checked (`:83`). I confirmed via the Actions API that exactly five shard artifacts exist,
indices 0–4, each produced exactly once. Verified directly against the frozen dataset
(`evidence/shard_partition_verification.txt`): 500 items, 470 primary, five shards of exactly
94, disjoint and exhaustive.

**2. Does per-question tie-break randomness depend on shard membership? No — established, and
this is the important one.** Priorities are seeded at `:51` as
`default_rng(5_100_000 + lex*100_000 + t*100 + 99)`, where `lex` comes from
`lex={q:i for i,q in enumerate(sorted(all question_ids))}` at `:76` — a **global lexicographic
ordinal over all 500 question ids**, computed identically in every shard because every shard
loads the whole dataset. It does not depend on the shard index, on the shard's membership, or on
position within the shard. I verified this is byte-for-byte the same seeding expression used by
the monolithic base runner (`longmemeval_spectral_band_haar_causal.py:179`, with the same
`sorted(...)` construction at `:242`). Per-question values are therefore shard-invariant by
construction, and every other input to `eval_one` is a function of the item alone.

Independent corroboration: the sharded run reproduced the frozen native R@3 with
`absolute_reproduction_error` of exactly `0.0` — the sharded pipeline recovered a constant
computed by the earlier non-sharded pipeline to the last bit.

**3. Is the aggregate order-independent? Not exactly — and "EXACT" overstates it.**
The aggregate is `np.mean` over 470 float64 values whose **order** is shard-concatenated
(`sorted(rglob("shard_*.pkl"))` → indices 0,5,10,… then 1,6,11,… ) rather than 0,1,2,…. Floating-point
summation is not associative, so bit-exact equality with a monolithic run is not guaranteed. I
bounded the effect (`evidence/shard_order_independence.txt`): reordering 470 values in exactly
this way shifts the mean by at most **2.22e-16** over 3000 random trials — about four orders of
magnitude below the runner's own `1e-12` tolerance and some fifteen orders below the 0.50-wide
decision band.

**Empirical check.** My own independent 5-shard execution (§G4c) produced a
`longmemeval_head_tail_seed_results.csv` that is **byte-identical** to the committed one, so in
this instance the sharded aggregation did land bit-exactly on the committed values. That is a
demonstration for this run; it is not a proof of bit-exact equivalence to a monolithic run in
general, which is what the label asserts.

**Finding:** the *semantics* are shard-invariant and that is demonstrated, not asserted. The
literal word **"EXACT"** in `"SHARDED_EXACT"` is an assertion of bit-level equivalence that is
not demonstrated anywhere in the artifacts and is not guaranteed by the construction. The
correct label is "sharded, semantics-invariant, aggregate reproducible to ~1e-16." Nothing in
the verdict turns on this.

---

## G9 — Leakage, tuning, and independence — **PASS on selection / CAVEAT on "cross-benchmark"**

**Outcome-dependent selection: none found, and I looked in the place it would show.** I
enumerated the **complete** workflow-run history of the research branch through the GitHub
Actions API — 11 runs total (`evidence/ci_provenance_verified.md`). For the Head/Tail stage:

- `V52 LoCoMo head-tail two-subspace causal` — **one** run (33884713242), run_number 1,
  **run_attempt 1**, conclusion `success`.
- `V52 LongMemEval head-tail two-subspace causal` — **one** run (33884860024), run_number 1,
  **run_attempt 1**, conclusion `success`.

There is no failed, cancelled, superseded or re-run Head/Tail execution anywhere in the branch's
history. There is no second attempt of any shard. The result was obtained on the first and only
execution of each benchmark. Failures that *do* appear in the history (runs 33864225295,
33864665619, 33864691367, 33883822273) all belong to the earlier spectral-band and
shard-recovery stages and remain visible rather than scrubbed — which is itself evidence the
history has not been curated.

Checked and absent: seed replacement (the five preregistered seeds are the five executed);
boundary search (only `0..31`/`32..95` exists in the code); threshold learning (`>= 0` literal);
post-hoc arm selection (the primary arm is the only decision arm, and §10 diagnostics are
declared non-decision-changing in advance); discarded runs (see above).

**What "cross-benchmark" is entitled to mean here — this word needs narrowing.** LoCoMo and
LongMemEval are genuinely different corpora with different cohort sizes (1535 vs 470), different
adapters, and different absolute difficulty (native R@3 0.237 vs 0.542). But they share: the
same representation recipe (TF-IDF/SVD-96 → archive-only centering → zero-threshold sign), the
same estimator (fractional R@3 at k=3 over 20 nuisance tie-break draws), the same Hamming
retrieval rule, the same `rho_2` construction, the same five Haar seeds, and most of the same
code — the LongMemEval shard runner and the LoCoMo runner are near-transcriptions of one another.

A shared-pipeline bug, or a bias inherent to the sign-quantized Hamming estimator, would express
itself on both benchmarks identically and would be indistinguishable from a real cross-benchmark
effect. **"Cross-benchmark" here is entitled to mean "consistent across two frozen datasets
evaluated through one shared representation, estimator and codebase." It is not entitled to mean
"independently replicated,"** which implies methodological as well as data independence. The two
benchmarks are a *dataset* replication, not an *independent* one. I would require this
distinction in the wording.

---

## G10 — Provenance and reproducibility — **PASS (one time-limited leg, one unreachable leg)**

Every git blob id, SHA-256 and byte count in
`V52_HEAD_TAIL_CAUSAL_PROVENANCE_MANIFEST_2026-09-04.json` was re-measured and matches (§1,
`evidence/digest_verification.txt`).

CI identifiers verified **against the GitHub API**, not against the manifest
(`evidence/ci_provenance_verified.md`):

| Manifest field | Declared | API-measured | |
|---|---|---|---|
| LoCoMo `actions_run_id` | 33884713242 | exists, `success`, correct workflow and branch | MATCH |
| LoCoMo `artifact_id` | 9941357062 | exists | MATCH |
| LoCoMo `artifact_digest` | `sha256:c8518840ee0afdd…89b2b` | identical | MATCH |
| LongMemEval `actions_run_id` | 33884860024 | exists, `success` | MATCH |
| LongMemEval `shards` | 5 | 5 shard artifacts, indices 0–4, one each | MATCH |
| LongMemEval `artifact_id` | 9941639442 | exists | MATCH |
| LongMemEval `artifact_digest` | `sha256:073aa74930afb…f4961` | identical | MATCH |

Two limitations, neither load-bearing:

1. **Time-limited.** The workflows set `retention-days: 30`; the API reports both artifacts
   expire **2026-10-04**. After that date the CI-artifact leg is no longer independently
   re-obtainable. This does not undermine the result, because the primary numbers are
   regenerable from public frozen inputs — which is exactly what I did.
2. **Unreachable.** The manifest asserts Google Drive file ids and
   `drive_byte_identity_verified_before_outcome: true`. I have no access to that Drive and
   **cannot verify any of it**. I treat those fields as unverified narrative. Nothing material in
   this audit rests on them: the preregistration-before-outcome ordering is established
   structurally by git ancestry and the CI hash-gate (G1), independently of the Drive claim.

One provenance gap worth recording: the committed `environment.txt` is a `pip freeze` and does
not record the **Python version**. The workflows show 3.13. I nonetheless reproduced the results
on 3.11.15, so the result is demonstrably not Python-version-sensitive — but the artifact should
pin the interpreter.

The manifest's `task4f1_execution_touched: false` is consistent with everything I observed; I did
not rely on it (see §Outcome boundary).

---

## G11 — The strongest argument that the reported lead is an artifact

This section is required. I first build the best case *against* the result, then adjudicate it.

### The case against

**1. The estimator is a ratio with a noisy denominator of unrecorded variance.**
`rho_2 = (native − mean_5(intervention)) / (native − FullHaar)`. The numerator rests on five Haar
draws; the denominator is an inherited constant whose own draw count and dispersion appear
nowhere in these artifacts. Ratio estimators with noisy denominators are biased in finite
samples, and the direction of that bias here is unknown because the denominator's variance was
never measured. Every uncertainty figure in §G6 is therefore a *lower* bound.

**2. Five draws cannot support the claimed magnitude, and on LoCoMo one draw contradicts it.**
The LoCoMo `rho_2` has a five-draw standard error of 0.047 against a point estimate of 0.107 —
a signal-to-noise ratio near 2. The approximate 95% interval, [−0.022, 0.237], **contains zero**.
Seed 56001 produces a *negative* loss: on that draw the "damaged" representation beat the native
one. A quantity that flips sign across a fifth of its draws is not a quantity whose magnitude has
been measured; it is a quantity whose *direction* has been weakly indicated.

**3. The hypothesis was generated by looking at the outcome of the previous stage, on the same
two cohorts.** The preregistration says so openly (§1): the prior `HAAR_MID_LOW64` arm — which
is precisely "leave Head32 alone, rotate the tail" — was already known to be mild on both
benchmarks. The Head/Tail experiment then tests a near-relative of that observation on the *same
two datasets*, with the *same representation*, through the *same code*. Fresh seeds do not make a
cohort fresh. On a garden-of-forking-paths reading, this stage is closer to a well-controlled
confirmation of an already-seen pattern than to an out-of-sample test, and its nominal
"preregistered" status protects against outcome-dependent *analysis*, not against
outcome-dependent *hypothesis choice*.

**4. The two benchmarks are not independent evidence.** As argued in G9, they share the
representation recipe, the estimator, the retrieval rule, the seeds and most of the code. Any
artifact of sign-quantized Hamming retrieval over an SVD-96 basis would appear on both. The word
"cross-benchmark" invites a reader to double-count what is close to one methodological
observation made twice.

**5. The effect could be a generic property of block-diagonal mixing rather than of spectral
position.** If restricting a Haar rotation to two blocks were enough to preserve sign-retrieval
quality for *any* block assignment, the "spectral position" story would be decoration on a
much duller fact about constrained orthogonal mixing.

**6. The absolute numbers are small.** LoCoMo native R@3 is 0.237 and `L_2` is 1.06 percentage
points. Effects of about one point, measured near a weak baseline with fractional credit and 20
randomized tie-break draws per question, are exactly where estimator quirks live.

### Adjudication

**Argument 5 fails outright.** It is the sharpest form of the alternative and it is the one I
could test directly. A matched random 32/64 block-diagonal Haar retains **5.1%** of the
advantage against Head32/Tail64's **89.3%** — an 8.8× separation, with all five random
partitions landing in the *opposite* preregistered band (§G7). Block-diagonality alone explains
essentially none of the effect. Spectral position is doing the work. This argument is not merely
weakened; it is falsified on LoCoMo.

**Argument 6 fails.** It is a plausibility complaint, not a defect, and the end-to-end
reproduction answers it: I regenerated the LoCoMo outputs bit-for-bit from public inputs under a
different Python version and BLAS (§G4c). Whatever the numbers are, they are not noise from an
unstable pipeline, and the four raw CSVs matched byte-for-byte.

**Arguments 1 and 2 succeed against the magnitude, and only against the magnitude.** They do not
touch the band verdict, because the verdict is robust in a way the point estimate is not: all ten
individual seed-level `rho_2` values, five per benchmark, fall inside the preregistered `<= 0.25`
band, and both means sit 3–4 standard errors from its boundary. What these arguments defeat is
the presentation of `rho_2` to nine or seventeen significant figures, and any reading of the
derived "89.3% retained" as a measured quantity. That is a real and required narrowing.

**Arguments 3 and 4 succeed against the scope and the wording, not against the finding.** They
are correctly and voluntarily bounded by the artifacts themselves: the preregistration's §1
discloses the backward look, and the checkpoint's interpretation ceiling already disclaims
universality, boundary optimality, production superiority, and any neuron-axis correspondence.
What remains is that "cross-benchmark" oversells the independence of the two observations, and
that this stage confirms an outcome-suggested hypothesis on the cohorts that suggested it. Both
are wording and scope constraints, not defects in execution.

**Verdict on the case against: it WEAKENS the result — materially, on precision and on scope —
but it does not defeat it.** The direction and the preregistered band verdict survive. What does
not survive is the number of digits and the word "cross-benchmark."

---

## Verdict

> ## `AUDIT PASS WITH CAVEATS`

Reported as **established**, not merely "not falsified": artifact identity and provenance
(G1, G2, G3, G5, G9, G10); the numerical reproduction of the primary result on both benchmarks
by independent end-to-end execution (G4); shard semantic invariance (G8); and the
position-dependence of the effect on LoCoMo (G7, by a control I supplied).

Reported as **not falsified but NOT established**: the magnitude of `rho_2` at the precision
presented; position-dependence on LongMemEval (I did not run that control); and any
generalization beyond these two frozen cohorts.

### The exact claim I would accept

> On the two frozen benchmarks LoCoMo (n=1535) and LongMemEval (n=470), under the preregistered
> `HEAD32_TAIL64_HAAR` intervention with five Haar draws (seeds 56001–56005), constraining
> orthogonal mixing so that the leading 32 archive-local SVD coordinates mix only among
> themselves and the remaining 64 only among themselves preserves most of the native
> SIGN96-vs-Full-Haar retrieval advantage: `rho_2 ≈ 0.11 ± 0.05` (LoCoMo) and `≈ 0.16 ± 0.02`
> (LongMemEval), one standard error over five draws, denominator uncertainty not included. Both
> benchmarks, and every individual seed, fall in the preregistered `rho_2 <= 0.25` band, so the
> band verdict `[HEAD-TAIL TWO-SUBSPACE SUFFICIENCY LEAD]` holds on both. The effect depends on
> *which* coordinates form the 32-block and not merely on the presence of a 32/64 block
> structure. This is a consistent result across two frozen datasets sharing one representation
> recipe, estimator and codebase — a dataset-level replication, not an independent one. It does
> not establish that 32 is an optimal or privileged boundary, and it carries the interpretation
> ceiling already stated in the checkpoint.

### Required narrowings

1. **Stop reporting `rho_2` to 9–17 significant figures.** Report `0.107 ± 0.047` (LoCoMo) and
   `0.157 ± 0.025` (LongMemEval), five draws, and state that the denominator's own sampling error
   is not included. Full-precision values belong in the JSON for reproducibility, not in prose as
   if they were measurements.
2. **Disclose that LoCoMo seed 56001 inverts the sign of `L_2`.** It is the single most
   informative fact about the stability of the LoCoMo magnitude and it currently appears nowhere
   in the checkpoint.
3. **Qualify "cross-benchmark"** as "two frozen datasets under one shared pipeline," not as
   independent replication.
4. **Replace `"SHARDED_EXACT"`** with a claim that is true as stated — semantics are
   shard-invariant (demonstrable), the aggregate reproduces to ~1e-16 (measurable). "EXACT" as
   bit-level equivalence is asserted, not shown.

### Recommendations (not gate conditions)

- **Persist per-question outputs.** The runners compute them and throw them away. Their absence
  meant the raw-level rebuild the audit brief asked for was impossible from committed bytes, and
  the gate had to be closed by full re-execution instead. A per-question CSV would cost a few
  hundred kilobytes.
- **Pin the Python version** in `environment.txt`, not just the packages.
- **Import `haar_q` and `pairwise` from the frozen base** in the LongMemEval shard runner rather
  than re-declaring them, so the two benchmarks cannot silently drift.
- **Record the Full-Haar reference's provenance** — draw count and dispersion — wherever it is
  used as a denominator.
- If the magnitude of `rho_2` (as opposed to its band) is ever to be load-bearing, five Haar
  draws are not enough. That is a new preregistration, not a re-run of this one.

---

## Outcome-boundary declaration

For the whole of this audit:

- **Zero** invocations of any Task 4F1 execution candidate with `--mode run`.
- **Zero** invocations of any Task 4F1 execution candidate with `--mode finalize`.
- `run_archives`, `evaluate_archive` and `finalize_results` were **never called**, on real BEAM
  data or on anything else.
- `V52_T4F1_AUTH_HMAC_KEY_HEX` was **never set, never read, never inspected**. No production
  authorization was constructed. No HMAC key was seen or derived.
- **No BEAM retrieval was performed.** No Task 4F1 (BEAM) retrieval outcome was seen, computed,
  written, or interpreted. Task 4F1 remains `BLOCKED` and outcome access remains `FORBIDDEN`; I
  did not approach it. Only LoCoMo and LongMemEval — the in-scope track — were executed.
- **Nothing was modified.** No sealed preregistration, seal, execution candidate, manifest,
  pinned corpus, historical audit namespace, or audited research artifact was edited, moved, or
  rewritten. The audited tree was read via `git archive` into a scratch directory outside the
  repository; all executions wrote only into that scratch directory. The only files this audit
  adds to the repository are those under
  `audit_v52_head_tail_causal_independent_2026_09_04/`.
- **No generalized prose scanner was built.**
- Both frozen datasets were obtained from their own public sources by the committed runners'
  own download-and-hash-verify paths, and were byte-verified before use.

---

## Files in this audit package

| Path | Contents |
|---|---|
| `AUDIT_REPORT.md` | this report |
| `AUDIT_REPORT.md.sha256` | sidecar digest of this report |
| `GATE_TABLE.md` | G1–G11 summary table |
| `AUDIT_HASHES.json` | every digest measured by this audit, machine-readable |
| `evidence/digest_verification.txt` | output of the digest re-verification script |
| `evidence/locomo_end_to_end_rerun_diff.txt` | committed vs auditor-regenerated LoCoMo outputs |
| `evidence/longmemeval_end_to_end_rerun_diff.txt` | committed vs auditor-regenerated LongMemEval outputs |
| `evidence/locomo_rerun_outputs/` | the auditor's regenerated LoCoMo output files |
| `evidence/longmemeval_rerun_outputs/` | the auditor's regenerated LongMemEval output files |
| `evidence/rederivation_from_raw_csvs.txt` | independent rebuild of the primary numbers + G6 dispersion |
| `evidence/g7_random_partition_control.json` | the auditor's matched random-partition control |
| `evidence/shard_order_independence.txt` | empirical bound on the shard reordering effect |
| `evidence/shard_partition_verification.txt` | shard partition disjointness/exhaustiveness from the dataset |
| `scripts/verify_shard_partition.py` | script producing the above |
| `scripts/build_audit_hashes.py` | generates `AUDIT_HASHES.json` |
| `evidence/ci_provenance_verified.md` | Actions run/job/artifact verification and run history |
| `scripts/verify_target_digests.sh` | re-verifies every identity this audit binds to |
| `scripts/rederive_primary_from_raw.py` | rebuilds `L_full`, `L_2`, `rho_2` and the dispersion stats |
| `scripts/auditor_random_partition_control.py` | the G7/G11 random-partition control |
| `scripts/shard_order_independence.py` | the G8 reordering bound |

---

## Kısa Türkçe özet

Karar: **`AUDIT PASS WITH CAVEATS`** (kararın tamamı yukarıda İngilizce olarak verilmiştir).

Hedef commit `7799502b`'e bağlı tüm blob kimlikleri, SHA-256 değerleri ve bayt sayıları
tarafımca ölçüldü ve eşleşti. Ön kayıt (preregistration) blob'unun sonuçlardan **yapısal olarak**
önce geldiği doğrulandı: blob geçmişte tek bir commit'te bulunuyor, hiç değiştirilmemiş, ve CI
iş akışı çalışmadan önce blob'un hash'ini zorunlu kılıyor. LoCoMo ve LongMemEval deneylerini
işlenmiş kodla baştan sona yeniden çalıştırdım; birincil sayılar bit düzeyinde yeniden üretildi
(tek fark, toleransın çok altında kalan bir BLAS yuvarlama tanısı).

İki daraltma gerekli: (1) `rho_2` değeri beş çekilişe dayandığı için 9–17 anlamlı basamakla
sunulmamalı — LoCoMo'da standart hata ±0.047 ve **56001 tohumu kaybın işaretini tersine
çeviriyor**; (2) "cross-benchmark" ifadesi bağımsız tekrar anlamına gelmemeli, çünkü iki
kıyaslama aynı temsil, aynı tahmin edici ve büyük ölçüde aynı kodu paylaşıyor.

Buna karşılık, sonucun en güçlü alternatif açıklaması — "herhangi bir 32/64 blok yapısı da aynı
işi görürdü" — tarafımdan eklenen kontrol ile **çürütüldü**: rastgele 32/64 bölümlemesi avantajın
yalnızca %5.1'ini korurken Head32/Tail64 %89.3'ünü koruyor. Spektral konum gerçekten belirleyici.

Task 4F1 (BEAM) hiçbir şekilde çalıştırılmadı, hiçbir sonuç görülmedi veya hesaplanmadı; hiçbir
mühürlü artefakt değiştirilmedi.
