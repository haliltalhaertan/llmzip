# V52 Task 4C2 — Independent Adversarial Audit (V2 prompt, adapter gap closed)

**Verdict:** `PASS WITH CONDITIONS`
**Audit level:** `FULL RAW-TABLE NUMERICAL REPRODUCTION + FULL SOURCE AUDIT`
**Audited commit:** `eb283f5` (canonical `main`)
**Date:** 2026-08-27

Both Task 4C1 mechanism conditions are now **CLOSED**. No bug was found. Every frozen
number reproduces to 6 decimals. The conditions attached to this PASS are
documentational and interpretive, not mechanism-blocking.

---

## 1. Chain of custody — PASS

`python3 tools/verify_frozen_artifacts.py` → **26 matched, 0 mismatched**, 2 Drive-only,
1 absent. Binding chain verified end to end:

| Binding | Result |
|---|---|
| post-run manifest → pre-run seal | `19883841…` ✓ |
| pre-run seal → sealed compute script | `3bb11260…` ✓ |
| adapter v1 → pinned SHA | `0a1a39a8…` ✓ (23,084 bytes) |
| adapter v2 → pinned SHA | `643082d6…` ✓ (17,158 bytes) |
| raw trial table (Drive) → manifest | `c6d58cdd…` ✓ (5,371,479 bytes) |

The seal's `script_sha256` equals the committed script's hash, and the manifest records
`script_hash_match: true` with identical pre/final script hashes — no post-seal mutation.

**Not independently verified:** the 277 MB dataset SHA256 was not recomputed (not
downloaded). The sealed script hard-aborts on mismatch, and `V52_T4C2_INPUT_CHECKS.json`
records the expected value, but this auditor did not confirm it from the bytes.

## 2. Adapter audit — previously NOT VERIFIABLE, now CLOSED

### 2.1 ITQ orientation — **CORRECT**

```python
B = np.where(V @ R >= 0, 1.0, -1.0)   # training code
C = B.T @ V
U2, _, VT2 = np.linalg.svd(C)
R = VT2.T @ U2.T
```

The ITQ objective is `min ||B − VR||²` over orthogonal `R`, i.e. `max tr(MR)` with
`M = BᵀV`. With `M = U S Vᵀ` the optimum is `R = V Uᵀ` — exactly `VT2.T @ U2.T`.
Verified numerically on a 400×96 centered matrix:

| quantity | value |
|---|---|
| `tr(MR)` under the adapter's rule | **33671.847** |
| `tr(MR)` under the transposed rule | 531.987 |
| nuclear norm of `M` (theoretical maximum) | **33671.847** |

The adapter attains the Procrustes optimum **exactly**. The objective decreases
monotonically under its rule and is **non-monotone** under the transposed rule.
`R` is orthogonal to 1.6e-15 with `det(R) = +1`; `fit_itq` is deterministic per seed and
seed-sensitive.

Encoding orientation is consistent: training uses `sgn(V @ R)`, and the 4C2 script uses
`D = (C_itq @ R) >= 0` for documents and `Q = (qC_itq @ R) >= 0` for the query — same
`R`, same orientation, same zero threshold. **No transpose bug. Condition CLOSED.**

### 2.2 Leakage — archive-only, label-free

`fit_input_payload(memories) -> [m["memory_text"]]` is a structural type barrier: fitting
receives strings only. `fit_archive_representation(memory_texts)` and
`fit_itq(V, n_iter, seed)` accept nothing else. An AST scan of the **executable** bodies
(docstrings stripped) finds **zero** label tokens; the apparent `answer`/`question` hits
are docstring prose stating the guarantee.

`memory_text` is `f"[{date}] {role}: {content}"` — `has_answer` and `session_position`
never enter it. `session_position` appears only inside `memory_id`, satisfying the
identity-only ruling. `has_answer` is read only to build `gold_ids` for scoring.

### 2.3 v2 → v1 import chain

`V1_PATH = HERE / 'longmemeval_v52_adapter.py'` — a sibling path, so v2 loads the
byte-exact committed v1. v2 overrides only `canonical_turn_id` and `build_archive`
(the memory-ID patch) and aliases the frozen fit functions. v2 does **not** redefine
`fit_itq`; the compute scripts call `adapter.v1.fit_itq`, so the audited function is the
one that ran. Adversarial hypothesis "v2 executes a different v1" is **refuted**.

## 3. Same-input ablation — PASS, stronger than 4C1

The 4C2 script builds the centered input three **numerically independent** ways rather
than aliasing one array:

```python
C_float = np.subtract(Y, mu)
C_sign  = Y.copy(); C_sign -= mu
C_itq   = Y + (-mu)
```

then asserts pairwise `max|Δ| ≤ 1e-12` for archive and query, raising
`[BUG — NOT A CLEAN GEOMETRY ABLATION]` otherwise. The run completed, so the assertion
held on all 470 questions; `V52_T4C2_sanity_checks.csv` records `0.0`. `mu` is
`Y.mean(axis=0)` over archive documents only, and every query transform occurs strictly
after `mu` and after all ITQ fits. FLOAT96_UNCENTERED is `Y @ QY[0]` on L2-normalized
rows (= cosine); FLOAT96_CENTERED is explicit cosine on centered vectors — the two differ
by centering alone.

## 4. Independent numerical reproduction — EXACT

Recomputed from the byte-verified 47,000-row trial table and the committed question-level
table. Design is perfectly balanced: 470 questions × 20 trials × 5 seeds, every question
exactly 100 rows, 0 duplicate cells.

| Method | ANY R@3 | ALL R@3 | Fractional R@3 | Frozen | Δ pp |
|---|---:|---:|---:|---:|---:|
| FLOAT96_UNCENTERED | 61.063830 | 28.936170 | **44.010638** | 44.010638 | 0.000000 |
| FLOAT96_CENTERED | 61.276596 | 28.723404 | **44.159574** | 44.159574 | 0.000000 |
| SIGN96_CENTERED | 71.308511 | 38.457447 | **54.197518** | 54.197518 | 0.000000 |
| ITQ96_CENTERED | 54.276596 | 22.672340 | **37.614113** | 37.614113 | 0.000000 |

- `Fc − F0` = **+0.148936 pp**
- `S − Fc` = **+10.037943 pp** ← decision variable `G`
- `S − I` = **+16.583404 pp**
- `I − Fc` = **−6.545461 pp**

`G = 10.037943 ≥ 5.0` → pre-registered band
`[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`. **Compute-side verdict
confirmed.** Task 4C1 reproduction gate passes (|Δ| ≤ 5e-7 pp, consistent with rounding
the frozen 6-decimal figures).

**Weighting hypotheses refuted.** FLOAT96_UNCENTERED, FLOAT96_CENTERED and SIGN96 are
constant across the 5 seed rows within each (question, trial) — max distinct value = 1 —
while ITQ96 genuinely varies (max 4). Because the design is perfectly balanced, flat mean,
correctly nested mean, and the committed question-level collapse agree to ≤7e-17. The 5×
replication cancels exactly; seeds are not treated as independent evidence.

## 5. Robustness — a caveat the compute report does not state

W/T/L reproduces exactly: **SIGN96 vs FLOAT96_CENTERED = 122 / 304 / 44**, median paired
gap **+0.0000 pp**. On 64.7% of the cohort the two methods are identical.

Concentration of the +10.04 pp lead (descriptive composition sensitivity only, **not**
inference):

| removed | share of gap | remaining lead |
|---|---:|---:|
| top 10 questions | 21.2% | +8.0822 pp |
| top 25 questions | 53.0% | +4.9839 pp |
| top 50 questions | 88.6% | **+1.2806 pp** |

**This differs sharply from the SIGN-vs-ITQ contrast**, which the 4C1 audit found broad
(248/141/81, median +5.00 pp, still +8.55 pp after removing its top 50). So the two
phenomena have different robustness profiles: *SIGN vs ITQ is broad; SIGN vs centered
FLOAT is concentrated in roughly 10% of questions.* Both are real fixed-benchmark facts,
but the vs-FLOAT lead should not be described as uniformly distributed.

Strata (all frozen, none invented): `SIGN − FLOAT_c` is positive in **all 15** strata
(+4.20 to +15.21 pp). The centering effect is near zero and **not uniformly positive** —
negative in 3 of 15 strata (knowledge-update −0.694, archive Q3 −0.556, reuse-low −0.529).

## 6. Binary geometry diagnostics — reported facts verified

| | SIGN96 | ITQ96 |
|---|---:|---:|
| unique-code fraction | **0.99551** | **0.89411** |
| duplicate-code fraction | 0.00449 | 0.10589 |
| largest collision bucket (mean) | 2.243 | 5.521 |
| query exact-code match | 0.00000 | 0.00010 |
| candidates at min distance | 1.153 | 1.451 |
| top-3 boundary tie rate | **0.23404** | **0.38723** |
| mean bit occupancy | 0.49544 | 0.50005 |
| min / max occupancy | 0.44933 / 0.49961 | 0.49639 / 0.50351 |
| dead constant bits | **0** | **0** |
| mean abs deviation from 0.5 | 0.00456 | 0.00107 |

ITQ96 bits are *better* balanced than SIGN96 and there are no dead bits in either — the
"ITQ produces pathological bits" explanation is not supported. SIGN96 has **fewer** ties
than ITQ96 under a tie priority both share, so tie asymmetry cannot favour SIGN96.
Descriptive only; no causal inference drawn.

## 7. Neighborhood reordering — descriptively supported

`V52_T4C2_rank_geometry.csv` holds 2,355 rows = 471 × 5, where the 471st id is an
explicitly labelled `__SUMMARY__` row (all 470 cohort questions present; no hidden
question). Its `N_archive` of 231,606 equals the exact cohort sum, and its ρ equals the
question-weighted mean of the per-question rows to ~1e-17 — no weighting trickery.

Per-seed ρ: 0.174462, 0.167225, 0.171594, 0.169888, 0.179227. Question-weighted mean
across seeds **0.172479**; per-question max only 0.477; 0.2% negative.

Supported: *"ITQ rotation massively reorders the retrieval neighborhood relative to native
sign/Hamming geometry, and that reordering coincides with a large evidence-retrieval
loss."* **Not** established, and not claimed: that ITQ destroys useful coordinates.
Causality is reserved for Task 4C3.

## 8. Adversarial hypotheses — all 12 refuted

| # | Hypothesis | Result |
|---|---|---|
| 1 | seal ≠ manifest claim | Refuted (`19883841…` matches) |
| 2 | script ≠ seal SHA | Refuted |
| 3 | adapter ≠ pinned SHA | Refuted (both byte-exact) |
| 4 | v2 executes a different v1 | Refuted (sibling `V1_PATH`) |
| 5 | archive fitting sees the query | Refuted (type barrier + ordering) |
| 6 | archive fitting sees gold/answer | Refuted (AST scan of executable bodies) |
| 7 | ITQ fitting sees query/gold | Refuted (matrix-only signature) |
| 8 | ITQ orientation transposed/inconsistent | Refuted (attains Procrustes optimum) |
| 9 | SIGN/ITQ differ in centered input | Refuted (3 independent builds, ≤1e-12) |
| 10 | centered FLOAT differs in representation | Refuted (same `Y`, `mu`; cosine both sides) |
| 11 | seeds weighted to bias the comparison | Refuted (balanced; flat = nested to 7e-17) |
| 12 | nuisance rows as independent evidence | Refuted (question is the reporting unit) |

## 9. Inference discipline — respected

No population p-value, confidence interval, superiority, equivalence or non-inferiority
claim appears in the package or in this audit. All W/T/L, strata and concentration figures
above are descriptive fixed-benchmark counts. The concentration analysis is labelled
composition sensitivity only.

## 10. Conditions attached to this PASS

1. **Dataset SHA256 not independently recomputed** by this auditor (277 MB not downloaded).
2. **`V52_T4C2_same_input_proof.csv` still absent from Git** (22 KB, compact). The
   source-level assertion and `sanity_checks.csv` cover its conclusion, but the per-row
   artifact should be committed.
3. **Concentration caveat (§5) is not stated in the compute report or handoff** and should
   be added before the result is communicated further.
4. Mechanism remains **descriptive**. No causal claim is licensed by this package.
