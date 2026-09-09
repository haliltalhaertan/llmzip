# Cold-Start Independent Adversarial Audit — Continuity Lead claim set

**Audit date:** 2026-09-09
**Posture:** zero-trust, adversarial; goal was to break each claim, not confirm it.
**Base:** `origin/main` @ `a8e6d5d`, branch `audit/coldstart-continuity-claims-2026-09-09`.
**Actions taken:** read-only. No experiment run, no seal touched, no `main` write, no BEAM
retrieval-quality outcome read, no HMAC key set.

---

## 1. Top-level verdict

# BLOCKED

The frozen numbers (C-D) all reproduce exactly from committed bytes. But the claim set's
**interpretive layer is broken in four independent places**, and — decisively — the proposed
experiment (C-V) **duplicates an experiment this project already preregistered, piloted, ran on
both benchmarks, and had independently audited**, while reinstating the exact estimand defect
that project's own pilot caught. The claimant's picture of the research frontier is roughly
five days stale.

PROMPT 2 must not run.

---

## 2. Claim table

| ID | Verdict | Evidence |
|---|---|---|
| C-A | **[VALID]** — retraction correct, stated reason weak | see §3.1 |
| C-B | **[VALID]** | `docs/v52/task4c2/v52_t4c2_centering_geometry.py:258-287` |
| C-C | **[UNVERIFIABLE IN THIS ENVIRONMENT]** — but corroborated numerically | see §3.3 |
| C-D | **[VALID]** — all 7 quantities | see §3.4 |
| C-E | **[PARTIALLY VALID]** — value right, provenance claim wrong, rounding slip | see §3.5 |
| C-F | **[INVALID]** — the numbers *are* in the repo | see §3.6 |
| C-G | **[VALID]** — and already in the ledger | see §3.7 |
| C-H | **[VALID]** | see §3.8 |
| C-I | **[INVALID]** — false premise, right conclusion | see §3.9 — **strongest break** |
| C-J | **[INVALID]** — whitening was tested, and run | see §3.10 |
| C-K | **[VALID]** | numeric check, §4 |
| C-L | **[VALID]** — also already confirmed in-repo as an executed arm | §4 |
| C-M | **[VALID]** — with a scope caveat | §4 |
| C-N | **[PARTIALLY VALID]** — asymmetry real, stated as identity, is an approximation | §4 |
| C-O | **[INVALID]** — derivable from neither route, not merely "heuristic" | §4 |
| C-P | **[PARTIALLY VALID]** — missing the `max(·,0)` clip; caveat correct | §4 |
| C-Q | **[PARTIALLY VALID]** — every value right, every number wrong | see §3.11 |
| C-R | **[INVALID]** — internal inconsistency confirmed | see §3.12 |
| C-S | **[VALID]** with one ambiguity | see §3.13 |
| C-T | **[VALID]** | arXiv API: `2306.04050v2`, Valmeekam et al., 2023-06-06 |
| C-U | **[PARTIALLY VALID]** as physics; **status misrepresented** | see §3.14 |
| C-V | **[INVALID]** as a proposal — duplicative and defect-reinstating | see §3.15 |

---

## 3. Findings in detail

### 3.1 C-A — the retraction is correct, but not for the reason given

`encode_sanity` really does build a three-block `Dl|Dw|Dc` SimHash:

```
adapters/longmemeval_v52_adapter.py:179-190
    # Exact V51/V52 full96 component generation.
    Rl = np.random.default_rng(seed + 2).normal(size=(d, 32)).astype(np.float32)
    ...
    D96 = np.concatenate([Dl, Dw, Dc], axis=1)
```

The claimant retracted on the grounds that this path thresholds at `>= 0` without centering.
That is a weak tell — it is an incidental difference, not a proof of non-production status.
The decisive evidence is elsewhere, and it is two-sided:

1. **Name collision, documented.** `docs/v51/LLM_MEMORY_RESEARCH_MASTER_CHECKPOINT_V51.md:30`
   — *"**full96 = latent32 + word32 + char32 active for every memory.**"* The adapter's `D96`
   is the **V51** object. `LATENT_DIM = 32` (`adapters/longmemeval_v52_adapter.py:38`) confirms
   the 32+32+32 decomposition.
2. **V52 `SIGN96` is a different object.**
   `prompts/V52_TASK_4C2_INDEPENDENT_ADVERSARIAL_AUDIT_PROMPT_V2_2026-08-27.md:80-83` —
   *"`SIMPLE_SIGN96_GLOBAL` — threshold the exact same centered `C96/qC96` at zero, 96-bit code,
   global Hamming top-3"*.
3. **Numerical proof of identity.** `docs/v52/task4c2/V52_T4C2_TASK4C1_REPRODUCTION.csv` shows
   T4C2's `SIGN96_CENTERED` reproducing T4C1's frozen `SIMPLE_SIGN96_GLOBAL` to `-1.1e-16`. The
   C-B construction *is* the T4C1 method. `encode_sanity` is invoked only at
   `adapters/longmemeval_v52_adapter.py:424-425`, inside `write_outputs`, twice with the same
   trial, to test determinism. It is never on a retrieval path.

**Unretracted repo defect surfaced by this claim:** the comment at line 179 says
`"Exact V51/V52 full96 component generation"`. Attaching **V52** to a V51 object inside a
hash-pinned adapter is precisely what misled the claimant. This is a documentation defect in a
frozen artifact and should be recorded (it cannot be edited — the bytes are pinned).

### 3.2 C-B — VALID, verified line by line

```
v52_t4c2_centering_geometry.py:258  Z=sparse.hstack([sparse.csr_matrix(Xl),Xw,Xc],format='csr')
                              :260  svd96=TruncatedSVD(n_components=96,random_state=SVD_RANDOM_STATE)
                              :261  Y=normalize(svd96.fit_transform(Z))
                              :263  mu=Y.mean(axis=0,keepdims=True)
                              :266  C_sign=Y.copy(); C_sign-=mu
                              :287  signD=C_sign>=0
```

Answering the four sub-questions the claim was to be tested on:

- **`Xl`,`Xw`,`Xc`:** built in `adapters/longmemeval_v52_adapter.py:154-167` — `Xw` = L2-normalised
  word TF-IDF (1-2 grams, English stop words, sublinear tf); `Xc` = L2-normalised `char_wb` 3-5
  gram TF-IDF; `Xl = normalize(TruncatedSVD(d, random_state=5101).fit_transform(Xw))` with
  `d = min(32, N-1, V-1)`. **`Xl` is 32-dimensional, not 96** — load-bearing for C-I.
- **`normalize` axis:** sklearn default, `axis=1` — per-row (per-document) L2. Confirmed by
  `V52_T4C2_feature_geometry.csv` `centered_doc_norm_min/max` ≈ 0.81–1.03.
- **`mu` leakage:** none. `mu` is computed at line 263 from `Y`, which is built at 257-261 from
  `texts` (archive only). The query is transformed at line 275, *after*. The script's own AST gate
  records `archive_offset=1031; itq_offset=1962; query_offset=2196`
  (`V52_T4C2_leakage_audit.csv`, all 10 checks PASS, 0 blocking). I re-derived the ordering from
  source and agree.
- **SVD scope:** **per question**, not global — `evaluate_item` is called once per item and fits
  its own `svd96`. Confirmed independently at `adapters/longmemeval_v52_adapter.py:366`.

### 3.3 C-C — UNVERIFIABLE at byte level; upgraded to *corroborated*

`v52_t4c3_coordinate_axis_probe.py` exists in **no git ref**. I enumerated filenames across all
reachable commits: zero hits. Only its SHA256 `8dce37b1…` is recorded
(`audit_v52_t4c3/HASH_VERIFICATION_LOG.md`). Byte-level confirmation requires the Drive artifact.

However the claimant marked this a bare guess, and it is better than that. Two corroborations:

1. `audit_v52_t4c3/AUDIT_REPORT.md:46-47` — *"The sealed script uses the same per-question centered
   representation for the native and rotation interventions: `C96 = Y96 - mu96` and
   `qC96 = QY96 - mu96`, with `mu96` fit from archive documents only."*
2. T4C3's `NATIVE_SIGN96` Fractional R@3 = `54.197518%` (`AUDIT_REPORT.md:80`) equals T4C2's
   `SIGN96_CENTERED` = `0.5419751773049645` to every reported digit. Two independently sealed
   scripts landing on the same value to 6 dp is strong evidence of a shared representation.

**What would close it:** fetch the Drive bytes of `v52_t4c3_coordinate_axis_probe.py`, verify
SHA256 = `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`, and read its
representation block directly.

### 3.4 C-D — all seven quantities VALID

| Quantity | Claimed | Source (verified) |
|---|---|---|
| NATIVE_SIGN96 | 54.197518% | `audit_v52_t4c3/AUDIT_REPORT.md:80`; `V52_T4C2_aggregate.csv` = 0.5419751773049645 |
| ITQ96_CENTERED | 37.614113% | `AUDIT_REPORT.md:81`; aggregate.csv = 0.376141134751773 |
| FLOAT96_UNCENTERED | 44.010638% | `V52_T4C2_aggregate.csv` = 0.4401063829787234 |
| HAAR b=96 mean | 38.271667% | `audit_v52_t4c3/AUDIT_REPORT.md:82` |
| D96 | −15.925851 pp | `AUDIT_REPORT.md:86,116,220` |
| G = SIGN96_C − FLOAT96_C | +10.037943 pp | `audit_v52_t4c2/AUDIT_REPORT.md:18`; `V52_T4C2_POST_RUN_MANIFEST.json:14` = 10.037943262411343 |
| Block gradient b=2..96 | 50.393085 / 47.261950 / 43.695390 / 40.634752 / 39.425709 / 38.271667 | `audit_v52_t4c3/AUDIT_REPORT.md:111-116` |

Note the claimed FLOAT96_UNCENTERED source ("T4C2 script constants") is wrong — it is an output,
not a constant. Immaterial.

### 3.5 C-E — PARTIALLY VALID: two errors, neither fatal to the conclusion

**Error 1 — the number was never derivation-only.** `FLOAT96_CENTERED = 44.159574%` is directly
measured and committed in at least four places:

- `docs/v52/task4c2/V52_T4C2_aggregate.csv` → `0.44159574468085105`
- `docs/v52/task4c2/V52_T4C2_centering_effect.csv`
- `docs/v52/task4c2/V52_T4C2_COMPUTE_REPORT.md:12`
- `docs/PROJECT_STATUS_2026-08-27.md:14`

The claimant subtracted to get a number sitting in plain sight. That is a search failure, and it
is the same class of failure as C-F.

**Error 2 — rounding.** `54.19751773049645 − 10.037943262411343 = 44.15957446808511`, which to
6 dp is **44.159574**, not `44.159575`. The claimant rounded up incorrectly, producing a value
that looks *different* from the canonical committed one.

**The conclusion survives.** `V52_T4C2_centering_effect.csv` gives
`centered_minus_uncentered_pp = 0.14893617021276562` for Fractional_R3 — the claimed "+0.149 pp"
is exact. Centering buys float almost nothing; the SIGN advantage is not a centering artifact.

### 3.6 C-F — INVALID

The claim was that the LoCoMo numbers are repo-external and unverified. They are not:

- `docs/CONTINUITY_LEDGER.md:850` — native rebuilt at `0.23654714666441043` against frozen
  `0.23654714666441054` (Δ = 1.1e-16). **→ 23.65%** ✓
- `docs/CONTINUITY_LEDGER.md:917` — *"The LoCoMo denominator `0.13770827054136` has NO
  higher-precision source committed anywhere"*. **→ 13.77%** ✓
- `docs/CONTINUITY_LEDGER.md:352` — *"mapping the accepted LongMemEval and LoCoMo results to
  **+15.926 pp and +9.884 pp**"*. **→ Δ = 9.88 pp** ✓ (sign convention: positive = native better;
  the brief's "−9.88" is the same magnitude under the opposite convention)

There is more in the repo than the brief contained: `docs/CONTINUITY_LEDGER.md:1105` records a
ten-seed Full-Haar panel — LoCoMo mean `0.139131`, sd `0.0052`, with the inherited `0.137708`
lying 0.27 sd away. The claimant reported these as unverifiable while the repo carries both the
values *and* their dispersion.

### 3.7 C-G — VALID, and not new

The invariance is stated at `audit_v52_t4c3/AUDIT_REPORT.md:57`, and I confirmed it independently:
over random vectors, permuting coordinates and flipping signs identically on documents and query
leaves Hamming distance exactly unchanged (max difference 0). An "exact pass" was mathematically
compelled. It is a harness unit test.

Is it *presented* as evidence? Partly — `AUDIT_REPORT.md` §"Continuous invariance and positive
control" says the controls *"strongly disfavor a generic ranking-direction, threshold-sign,
tie-priority, or transform-application bug"*. That is a legitimate use: the test **can** fail if
the harness misapplies a transform, so passing it is real information about implementation, and
no information about the science. The report does not overclaim.

Crucially, the project already knows this. `docs/CONTINUITY_LEDGER.md:352`:
*"The signed-permutation control is **invalidating rather than supportive**."* C-G re-derives a
position the ledger recorded on 2026-09-08.

### 3.8 C-H — VALID

No neural embedding path exists. Repo-wide grep for `768|sentence-transformer|SentenceTransformer|
BGE|bge-|openai|embedding model` outside `literature/` returns only commit hashes
(`3e12035532eb85768f…`), a timing figure, and one substantive hit:
`audit_v52_t4c1/AUDIT_REPORT.md:207` — the float baseline *"is booked as **768 continuous
bytes**/item"*. That is 96 float64 × 8 bytes. The brief's "768-dimensional float32 embedding"
is almost certainly a misreading of this line, of Xiao's 768-d datasets (his Tables 13 and 18
are both "768-d"), or both. Prereg forbids substitution:
`audit_v52_t4f0_restricted_refreeze_2026_08_31/REFREEZE_PROTOCOL.md:38` — *"no pretrained
embeddings"*.

### 3.9 C-I — INVALID. The strongest break in the set.

The claim: *"the representation is already 96-dimensional, nothing is selected from 768, no
dimension is discarded."*

From `docs/v52/task4c2/V52_T4C2_feature_geometry.csv`, row 0 (`question_id 001be529`):

```
N_archive = 514 ,  word_columns = 39940 ,  char_columns = 59943 ,  combined_columns = 99915
```

Across the cohort (`V52_T4C2_collision_diagnostics.csv`): `N_archive` ranges **396 → 231,606**,
median 495.5, and **zero** archives have N ≤ 96.

So `Z` carries ~10⁵ columns, `rank(Z) = min(N, ncols) ≥ 396`, and `TruncatedSVD(96)` keeps 96.
**At minimum 300 components are discarded per question; at maximum 231,510.** This is a far more
aggressive dimensionality reduction than the 768→96 the claimant denied. "Atılan boyut yok" is
flatly false.

**The conclusion nevertheless survives, on a different argument.** The T4C3 rotation `R` is 96×96
applied *after* `svd96`. It does not re-select a subspace; the 96-D subspace is fixed before any
arm branches, and both native and rotated arms live in it. So the b=96 arm *is* a within-subspace
rotation, and D96 = −15.93 pp *is* an orientation effect. The right sentence is **"the rotation is
applied downstream of a fixed subspace selection"**, not **"no dimension is discarded"**. The
claimant reached a correct conclusion through a false premise — which is why C-R, which depends
on the premise, fails.

### 3.10 C-J — INVALID

Two separate errors.

**(a) The cited evidence does not say what the claim says.**
`v52_t4c2_centering_geometry.py:117` is a **static scope guard**, not a prohibition:

```python
extra_method_terms=['whiten','euclidean','shortlist','rerank','locomo','sign_uncentered','alternative_threshold']
lower=b.lower(); bad=[x for x in extra_method_terms if x in lower]
```

It token-scans the source of `evaluate_item` and fails closed if any term appears
(`V52_T4C2_leakage_audit.csv`: *"no forbidden rescue retrieval method … bad=[]"*). Note the list
contains `'locomo'` — nobody thinks LoCoMo is scientifically forbidden. It is a guard against
that one sealed script silently growing arms. Real prohibitions live elsewhere, e.g.
`REFREEZE_PROTOCOL.md:38`, `V52_TASK_4C3_COORDINATE_AXIS_CAUSAL_PROBE_2026-08-27.md:193`
(*"Do not whiten or rescale coordinates"*) — and those bind *those tasks*, not the program.

**(b) The substantive claim is false: whitening was tested, and run, on both benchmarks.**
The coordinate-scale line is `diag(1/σ)` rescaling — precisely C-V's `W`:

- `docs/CONTINUITY_LEDGER.md` L-046: draft written, *"The intervention rests on the identity
  `sign(xD) = sign(x)` for positive diagonal D"* — this is C-L, carried **as an executable arm**
  (`SCALED_NATIVE` must be bit-identical to `NATIVE` or the run aborts).
- L-047: synthetic pilot run; **it found a defect in the draft's own primary estimand**.
- L-048: promoted to candidate preregistration.
- L-055 (2026-09-07): **runs completed on both benchmarks.** `frac_full = 0.7261` on LoCoMo
  → `[SCALE ACCOUNTS FOR MOST OF THIS ARM'S DAMAGE]`; `frac_full = 0.6563` on LongMemEval
  → `[PARTIAL]`, 0.044 short of the 0.70 band. Controls: native reproduction error 0.0 / 1.1e-16;
  `SCALED_NATIVE` bit-identical to `NATIVE` on both; 92,100 / 28,200 rows; zero degenerate
  coordinates.

"Never tested because forbidden" is wrong on both halves.

### 3.11 C-Q — PARTIALLY VALID: every value right, every number wrong

Verified against arXiv (`export.arxiv.org` API + `arxiv.org/html/2605.17524v2`):

- **Identity ✓** — arXiv:2605.17524, Wenxuan Xiao (sole author), submitted 2026-05-17, v2
  2026-05-29, cs.LG/cs.DB, *"21 pages, 1 figure, 19 tables"*.
- **Version history ✓** — current title *"Covariance Structure and Coordinate Heterogeneity
  Govern Binary Quantization of Contrastive Embeddings"*; the repo's
  `literature/V52_T4C2_DEEP_LITERATURE_REVIEW_BINARY_GEOMETRY_2026-08-27.md:7` cites the earlier
  *"Coordinate Heterogeneity Governs Binary Quantization: From InfoNCE to Recall"*. The claimant's
  v1/v2 account is correct.
- **Numbering ✗ — off by one throughout:**

| Claimed | Actual |
|---|---|
| Theorem 3 — rotation equalises variances | **Theorem 2** (Rotation uniformizes coordinate variances) |
| Corollary 4 — rotation harms heterogeneity-aware BQ | **Corollary 3** (Rotation harms heterogeneity-aware BQ) |
| Corollary 5 — rotation helps linear-corrected BQ | **Corollary 4** (Rotation helps linear-corrected BQ) |
| Table 15 — cohere Hamming 0.440 → Ham+Rot 0.381 | **Table 16** (Table 15 is Gaussian-vs-Copula; cohere row there is 0.681/0.687/0.679) |

- **Values ✓ — all six confirmed.** From **Table 12** (*"Effect of Haar rotation on sign entropy
  and BQ recall"*): `Cohere … 0.486 0.481 −0.005`; `BGE-M3 … 0.782 0.775 −0.007`;
  `GIST 0.000 0.511 +0.511 | 0.152 0.459 +0.307`. From **Table 16**: `cohere 0.440 0.381 0.616
  0.495 −0.060`.

The content mapping is exact, so the claimant did read the paper; the citation apparatus is
uniformly wrong and would not survive review.

### 3.12 C-R — INVALID; the suspected internal inconsistency is real

C-R claims novelty rests on operating in a `K ≪ D` "compressive" regime Xiao does not cover. Both
readings fail:

- Read as **99,915 → 96** (the SVD): `K ≪ D` holds spectacularly, but that is ordinary LSA. It
  says nothing about *binary quantization*, which is where the claimed novelty sits.
- Read as **96 float dims → 96 bits**: that is exactly **1 bit per coordinate** — the regime
  Xiao's abstract opens with (*"compresses high-dimensional embeddings into one or two bits per
  coordinate"*). Not `K ≪ D` at all.

So the framing is a residue of the retracted 768→96 picture, exactly as suspected. Worse, the
repo already forbids the claim —
`literature/V52_T4C2_DEEP_LITERATURE_REVIEW_BINARY_GEOMETRY_2026-08-27.md:7`:

> *"we must NOT claim that 'rotation destroys useful coordinate heterogeneity' is a novel
> mechanism discovered by this project."*

**A defensible novelty axis does exist and the claimant missed it:** Xiao's theory is built on
**InfoNCE/contrastive embeddings** (*"connecting the Gaussian structure recently established for
InfoNCE-trained representations"*), across 18 datasets / 9 embedding families — all learned. The
llmzip representation is **unsupervised TF-IDF + per-archive SVD**, with no contrastive training
and no Gaussianity guarantee. That is a genuine out-of-scope regime, and it is a better claim
than `K ≪ D`. It is also weaker than the claimant wants: it is a *scope extension*, not a new
mechanism.

### 3.13 C-S — VALID, with one ambiguity

The 14 attributions are correct as stated. Six are cross-checkable in-repo
(`literature/V52_T4C2_DEEP_LITERATURE_REVIEW_BINARY_GEOMETRY_2026-08-27.md:59,67,75,123,124,126,
127,129,130`): Charikar STOC 2002, Weiss NeurIPS 2008, Kulis & Darrell NeurIPS 2009, Gong &
Lazebnik CVPR 2011, Gao & Long SIGMOD 2024.

**Ambiguity:** "Norouzi 2012 (Multi-Index Hashing)" — there are two 2012 Norouzi papers. The repo
(line 130) cites *Hamming Distance Metric Learning* (Norouzi, Fleet, Salakhutdinov, NeurIPS 2012);
the claimant cites *Fast Search in Hamming Space with Multi-Index Hashing* (Norouzi, Punjani,
Fleet, CVPR 2012). Both are real; they are different papers. Disambiguate before publication.

Beyond the two arXiv IDs I fetched, the remaining attributions were checked against the repo and
against prior knowledge, not against fetched primary sources.

### 3.14 C-U — hypothesis coherent; **status misrepresented**

**(a) Internally consistent?** Yes. Sign-thresholding discards magnitude, so every coordinate gets
one vote regardless of singular value; rotation makes each new coordinate a blend of high- and
low-variance components, correlating the bits. Both directions follow.

**(b) Explains both observations?** Yes, without contradiction — and C-N (verified, §4) supplies
the missing formal step: flat Hamming targets the *unweighted* mean `(1/K)Σpᵢ`, cosine targets the
*variance-weighted* `Σσᵢ²ρᵢ/Σσᵢ²`. Under a decaying singular spectrum these differ sharply. In my
numeric check with `σᵢ = e^{-3i/K}`, the two targets landed at 0.598 vs 0.285.

**(c) Falsifiable?** Yes — and *it has already been falsified in part.*

**(d) A simpler alternative the claimant missed?** I tried the four the brief named. Two die:

- **Tie mass / tie-break priority — REFUTED.** From `V52_T4C2_tie_diagnostics.csv`:
  `SIGN96_CENTERED` has a top-3 boundary tie in **23.4%** of rows (median 1 candidate at the
  boundary); `ITQ96_CENTERED` has **38.7%** (median 2). SIGN has *less* tie mass than the method
  it beats, and one shared priority vector serves every method per (question, trial). Tie luck
  cannot manufacture +10 pp.
- **Structural recall@3 ceiling — REFUTED.** `metrics3` is `hit/len(gold)` (uncapped), so
  |gold| > 3 is capped below 1. But gold cardinality is `{1:174, 2:228, 3:38, 4:14, 5:10, 6:6}`
  over 470 questions, giving a ceiling of **97.766%** — barely binding. And the effect is present
  where the ceiling is exactly 1.0: on the 174 one-gold questions SIGN = 65.09% vs FLOAT_c =
  55.17%, **gap +9.91 pp**. (Independently: `V52_T4C2_gold_cardinality.csv` one-gold row =
  9.913793.) The ceiling explains nothing.

Hubness and post-`normalize()` spherical centering remain live and untested, and I could not
break them here.

**But the status claim is what fails.** C-U is offered as a fresh hypothesis. It is instead the
project's **preregistered literature prediction**, recorded before outcomes
(`docs/CONTINUITY_LEDGER.md:923`):

> *"The draft records, in advance, that IsoHash, ITQ, RaBitQ and Xiao's heterogeneity account
> together predict a positive interaction — removing heterogeneity before rotating should help
> full mixing much more than block mixing…"*

And it has been tested with a **partially negative** result (L-055, §3.10): rescaling recovers
`0.7261` of the full-mixing damage on LoCoMo but only `0.6563` on LongMemEval, **below the
preregistered 0.70 band**. The ledger's own reading: *"this supports that relative coordinate
scale **PARTICIPATES** in cross-band mixing damage; it establishes no mechanism, no exclusivity."*
Also recorded: real archives sit at `CV(σ) ≈ 0.49–0.50`, and *"real recovery 0.66–0.73 is lower
than the pilot model predicted anywhere"* — i.e. pure spectrum-equalisation **under-predicts**.

There is a second, stronger result the claim set does not mention at all
(`docs/CONTINUITY_LEDGER.md:776`): the Head32/Tail64 arm gives `rho_2 = 0.1074` against
`RANDPART_32_64_HAAR` at `0.9489`, Δ = 0.841 against a prespecified falsification threshold of
0.25. *"It is the identity of the coordinates, not the block sizes, that carries the effect."*
That is a sharper mechanism claim than C-U, already independently audited, and C-U neither cites
nor accommodates it.

### 3.15 C-V — INVALID as a proposal

- **(a) Do the arms make the claimed distinction?** In isolation, yes — the logic is sound.
- **(b) Does the sanity arm follow necessarily from C-L?** Yes. `sign(C·diag(1/σ)) ≡ sign(C)`
  bit-for-bit; I verified in float64 including `σ = 1e±300` and exact zeros under the `>= 0`
  convention. Already independently demonstrated in-repo: L-047 *"`sign(xD) = sign(x)` held
  EXACTLY in float64 … with zero degenerate coordinates"*, and L-055 *"`SCALED_NATIVE`
  bit-identical to `NATIVE` on both"*.
- **(c) Missing arms?** Yes — see §5.
- **(d) Gold/query leakage?** No. `σ` from archive documents only, computed before the query
  transform, mirrors the accepted `mu` pattern.
- **(e) Is `σ` itself a leakage channel?** No more than `mu`. But it is an **unsealed
  per-question archive statistic**, so it needs the same explicit "archive-only, pre-query"
  gate the accepted arms carry.

**Why it is nonetheless blocked:** the experiment is a strict subset of
`V52_COORDINATE_SCALE_PARTICIPATION_PREREG` — preregistered (L-046/L-048), piloted (L-047),
executed on both benchmarks (L-055), audit-prompted (L-055). Running it again yields nothing new.

**And it reinstates a defect the project already caught.** C-V's implicit estimand is a
percentage-point comparison ("≈54% ⇒ hypothesis confirmed"). `docs/CONTINUITY_LEDGER.md` L-047:

> *"The draft made the percentage-point interaction I = delta_full minus delta_block the primary
> quantity … It is almost entirely a **FLOOR ARTIFACT** … Full mixing gains more percentage points
> only because it had more loss available."*

The remedy adopted was `frac` — each arm's share of *its own* loss recovered — with bands
explicitly admitting `frac > 1` (L-047 finding 4: rescaled rotated codes **beat** native at low
heterogeneity, frac 1.407). C-V's fixed "≈54%" target has no such allowance.

---

## 4. Mathematics — independently derived, not taken from the claim

| ID | Result |
|---|---|
| **C-K** | **VALID.** Associativity exact (max dev 1.8e-14). For iid Gaussian `R` and orthogonal `U`, `RU ≡ᵈ R` — row covariance of `RU` deviates from `I` by 6.5e-3 at n=2e5, consistent with sampling noise. Holds on either side. |
| **C-L** | **VALID.** `(C/σ ≥ 0) ≡ (C ≥ 0)` bit-identical over 5,000×96 including injected exact zeros, and at `σ = 1e-300` and `1e+300`. |
| **C-M** | **VALID.** `P[sign match] = 1 − arccos(ρ)/π` — max |empirical − theory| = **6.4e-4** over ρ ∈ {−0.9,−0.4,0,0.3,0.75,0.95}, 4e5 draws each. **Caveat the claim omits:** this is the bivariate-Gaussian orthant identity. SIGN96 coordinates are SVD components of TF-IDF, neither Gaussian nor random hyperplanes, so it governs an idealised model, not the pipeline. |
| **C-N** | **PARTIALLY VALID.** The asymmetry is real (numbers in §3.14). But `Σσᵢ²ρᵢ/Σσᵢ²` is an **approximation**, not an identity: it needs matched per-coordinate doc/query scales, and `E[ratio] ≈ ratio of E[·]` for the norms. Stating it as exact is an overclaim. |
| **C-O** | **INVALID — worse than "heuristic".** Two standard routes exist. **(A) delta-method plug-in** for `T = Σσᵢ²ρᵢ`: since `dp/dρ = 1/(π√(1−ρ²))`, the weight on `bᵢ` is `αᵢ ∝ σᵢ²·π√(1−ρᵢ²)` — **no** `p(1−p)` denominator. **(B) SNR / matched-filter** on Bernoulli observations: `αᵢ ∝ (dp/dρ)/Var(bᵢ) = 1/(π√(1−ρᵢ²)·pᵢ(1−pᵢ))` — `√(1−ρ²)` in the **denominator**. The claimed `σᵢ²·π√(1−ρᵢ²)/(pᵢ(1−pᵢ))` takes the numerator from (A) and the denominator from (B). Numerically: cosine similarity to (A) = 0.9933, to (B) = 0.5054, exactly equal to neither. Inverse-variance weighting does not apply here at all — each `ρᵢ` enters a fixed weighted sum once; there are no redundant estimates of a common scalar to trade off. |
| **C-P** | **PARTIALLY VALID.** Reverse water-filling is `bᵢ = max(½log₂(σᵢ²/θ), 0)`. The claim drops the clip. With `σ² = e^{-8i/K}`, K=96, B=96, the unclipped formula assigns **negative bits to 40 of 96 coordinates** (min −2.386). The stated caveat — MSE-optimal ≠ retrieval-optimal — is correct and important. |

---

## 5. Missing arms in the proposed experiment

Even setting duplication aside, C-V omits:

1. **`SIGN96_WHITENED_ROTATED` under the *block* gradient (b=2..32), not only full Haar.** The
   block gradient is the project's sharpest signal; testing whitening only at b=96 cannot separate
   heterogeneity from block structure.
2. **A `HEAD32/TAIL64` arm.** Already the load-bearing result on the mechanism branch
   (`rho_2 = 0.107` vs `RANDPART = 0.949`). Any spectrum-equalisation hypothesis must predict
   this contrast or it is under-determined.
3. **A `RANDPART` matched control.** Without it, C-V cannot distinguish "coordinate identity" from
   "any partition of that shape" — the confound the head-tail auditor had to run itself.
4. **`CV(σ)` before and after rescaling, declared as a diagnostic and not a decision input.**
   Present in the accepted prereg; absent from C-V.
5. **A `frac`-scale estimand with bands admitting `frac > 1`** — see §3.15.
6. **Gentler `σ^{-1/2}` alongside `σ^{-1}`.** Listed as an open design question in L-046 and
   resolved there; C-V hard-codes `σ^{-1}` with no rationale.
7. **Per-archive vs global `σ`.** Also settled upstream; C-V leaves it implicit.

---

## 6. Errors found that the claimant has not retracted

1. **C-I** — "no dimension is discarded". False; ≥300 discarded per question (§3.9).
2. **C-R** — the `K ≪ D` novelty frame, a residue of the retracted 768→96 picture, and forbidden
   by the repo's own literature file (§3.12).
3. **C-J** — whitening described as forbidden-and-untested; it was preregistered, piloted and run
   on both benchmarks (§3.10).
4. **C-F** — LoCoMo numbers described as repo-external; all three are committed (§3.6).
5. **C-E** — `FLOAT96_CENTERED` described as derivation-only; committed in four places. Plus a
   6th-decimal rounding slip (§3.5).
6. **C-Q** — every theorem/corollary/table number off by one (§3.11).
7. **C-O** — presented as a sound-but-heuristic derivation; derivable from neither route (§4).
8. **C-P** — missing the `max(·,0)` clip (§4).
9. **C-U/C-V** — presented as a new hypothesis and a new experiment; both are ~5 days stale
   against `docs/CONTINUITY_LEDGER.md` L-046…L-057 and L-076.

**Repo-side defect (not the claimant's):** `adapters/longmemeval_v52_adapter.py:179` labels a V51
object *"Exact V51/V52 full96"*. Hash-pinned, so it must be recorded rather than edited.

---

## 7. One-sentence conclusion

**The computation must not be run:** its numeric foundation is sound, but the experiment it
proposes was already preregistered, piloted, executed on both benchmarks and independently
audited five days earlier, and C-V would re-run it under the percentage-point estimand that
project's own pilot proved to be a floor artifact.

---

## 8. Conditions that would have to be met before any successor experiment

1. Read `docs/CONTINUITY_LEDGER.md` L-046 through L-057 and L-072 through L-081, and
   `ops/CURRENT_STATE.json → mechanism_research_track`, before proposing anything in this line.
2. Retract C-I, C-J, C-F, C-R; correct C-E, C-O, C-P, C-Q.
3. State what a new experiment adds over `V52_COORDINATE_SCALE_PARTICIPATION_PREREG`, or drop it.
4. Any successor uses the `frac` estimand with bands admitting `frac > 1`.
5. Close C-C by fetching the Drive bytes of `v52_t4c3_coordinate_axis_probe.py` and verifying
   SHA256 `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`.
6. Re-frame novelty as contrastive → unsupervised TF-IDF/SVD scope extension, not `K ≪ D`.
