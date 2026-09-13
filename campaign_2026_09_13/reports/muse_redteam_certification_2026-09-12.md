# Certification red-team review: LME + LoCoMo "certified regeneration"

**Session note.** This environment is write-locked (no report file could be saved to `~/muse-work/reports/`), so the report below is delivered as the answer instead. A sibling session was actively writing files mid-review (`task1_extend_lme.py` fixed 22:20, `code_cert_v2.py` + `code_certification_sign.json` + `code_certification_itq.jsonl` appearing 22:29–22:30); findings distinguish what I read at which version. **Verified by execution** means I ran it (commands quoted); **by reading** means code/text inspection only. No regeneration was run; nothing was modified.

**Status snapshot (execution).** `certification_report.json` present (all deviations `0.0`, 470/470). `code_certification.json` (the filename in the brief): polled 8× at 60 s intervals — **absent all 8 polls**. Siblings instead wrote `code_certification_sign.json` (22:30) and `code_certification_itq.jsonl` (22:30, 20/470 lines at read time). `task1_extension_lme.json/csv` appeared 22:20. `extension_run.log` at first read contained only a traceback (quoted below).

All pinned input hashes re-verified by execution (`sha256sum`): producer `8dce37b1…` ✓, dataset `d6f21ea9…` + 277383467 bytes ✓, heterogeneity CSV `148ae5b7…` ✓, adapters `0a1a39a8…` / `643082d6…` ✓, T4D script == seal `sealed_compute_script_sha256` (`3f7f091f…`, match verified) ✓, geometry zip holds 470 `.npz` with keys `sign_doc_packed (N,12) uint8`, `sign_query_packed (12,)`, `itq_* (5 seeds [101…])`, `gold_rows`, `N_archive`, `bitorder '<U3' ['big']` ✓.

## 1. Logical validity

**Covered by the LME hetero cert** (per question): full diagonal variance vector (96), `>=0` occupancy vector (96), and 10 derived scalars (CV, variance entropy, participation ratio, max/median, cov off-diag energy ratio, mean |corr|, occupancy mean/min/max/MAD). `%.17g` round-trips float64 exactly — verified by execution (100k random + edges incl. `5e-324`, `1/3`, `π`: all bit-exact). CSV scalars are also repr-exact (`'1.0160257012999805'`), so the all-`0.0` claim is meaningful, not formatting-limited.

**NOT covered by any original-byte evidence:** exact-zero mass `(C==0).mean()`; strict-`>0` occupancy/entropy; off-diagonal sign/quantile structure (median/p95 of |corr|); per-entry magnitudes beyond column sums-of-squares; `qC` magnitudes (query signs later covered by the sign-cert, magnitudes never); row norms; anything about `C`'s 22.2M entries not captured by column means-of-squares, column sign-counts, and two cov scalars.

**Family (a) — constructed, verified end-to-end (execution).** N=400, 96 columns tiling `[2,1,-1,-2]` vs `[2t,0,-t,-t]`, `t=√(5/3)`. Every LME check passes within ≤4.3e-15 (TOL 1e-12), occupancy bit-identical, **and `packbits(C>=0)` bit-identical (verified)** — yet:

- `zero_mass`: 0.0000 vs 0.2500; `sign_entropy_gt`: 1.000000 vs 0.811278 (`ge` identical at 1.0).
- Output quoted: all 10 scalar reldevs `0.00e+00`–`1.48e-16`, `variance_vector maxrel=4.26e-15`, `occupancy maxabs=0.00e+00`.

This defeats the hetero cert **and** the sign-code cert jointly: `+0.0` and small positives share the same `>=0` bit, so exact zeros are invisible to every frozen artifact. The sibling sign-cert result (`sign_doc 470/470`, `sign_query 470/470`, `exact_zero_entries_in_regenerated_C: 0`) therefore does **not** certify `zero_mass == 0` for the originals — that number rests purely on re-execution determinism.

**Family (b) — constructed at correlation level, verified (execution), with one honest caveat.** Two PSD 6×6 unit-diagonal matrices from `Ra.npy`/`Rb.npy`: mean|corr| reldev `1.78e-16`, RMS exactly equal, but median gap `0.0912`, p95 gap `0.0707` (Ra median 0.236/p95 0.633 vs Rb 0.327/0.704; eigmin >0.03 both). Two scalars cannot pin 15 (here; 4560 in production) pair magnitudes — the constraint manifold has ~13+ free dimensions. Caveat: I matched variance/cov-scalar structure but did not jointly force identical occupancy vectors into the same pair, so this is a proof of D4-underdetermination, not a literal full-cert-passing pair. A full joint collision (45k entries vs ~200 constraints) almost surely exists but is a real optimization project, not a hand construction.

**Adequacy verdict for the intended use.** D2/D3/`D1_ge` (variance/occupancy functionals): certified. `D1_gt`/`zero_mass`: **not certified against original bytes** — the extension's `zero_mass mean 0.0`, `D1_gt == D1_ge` (means both `0.9970337299075775`, diff `0.0`) are properties of the regeneration promoted by a determinism argument. D4: the two hetero cov scalars do not constrain median/p95 (shown); the pending ITQ-refit evidence is magnitude-sensitive and is the best distinguisher, but it is refit-based (circular by construction — a variant in the same code basin passes) and was 20/470 when read. LoCoMo is weaker still: `counts_report.json` checks only 8 integer fields per conversation against the transfer proof — **zero value-level evidence** for any of the 10 C matrices (the proof contains no value payload; the `R@3 0.2365…` target is never checked by the harness, by design). `C_sha256` in LoCoMo pkls is self-computed at write time, not a match against anything.

## 2. Hash/identity chain holes (with verification status)

- **NaN hole in `certify` (execution-verified).** [lme_regen.py](/mnt/c/Users/MDP/dev/llmzip-work/harness/lme_regen.py:214) `if d > stats[k]` with `d = NaN` is `False`, so a NaN regenerated field leaves `stats` at `0.0` — a corrupt regen certifies clean. Same for the vector paths (L221/L226; `np.max` → NaN, `NaN > 0` False; quoted output: `nan-hole: stats stays 0.0`, `vec nan rel = nan ; nan > 0.0 = False`). Fix: `>=` + explicit `isfinite` rejection. (Production impact: unlikely — `no_nan` culture — but the cert's headline `0.0` cannot exclude it.)
- **All-`0.0` is environment-contingent (execution-verified).** Recomputing `cov_offdiag_frobenius_energy_ratio` from the *same* pkls under this machine's numpy 2.5.3/BLAS: last-bit differs on **329/470** questions, `mean_abs` on **222/470**, variance vectors on **0/470**; worst reldev `2.27e-14` at `gpt4_5dcc0aab` (≪ TOL, but ≠ 0). E.g. `001be529`: stored/csv `…80831` vs recomputed `…81025`. The regen env matched the original env's BLAS summation bit-exactly (a cancellation-amplified quantity surviving 470/470 is itself evidence of numerical identity of the pipeline) — but an independent auditor recomputing hetero **will see nonzero deviations**. The report should present the gate as `≤1e-12`, not `0.0`-implies-identity.
- **Vacuous/misleading gates (reading).** `lme_regen.py:116` prints `[OK] parent post-run manifest bindings` whenever `problems` is empty *including* dataset/cohort problems — misattribution (gate still fails overall, message wrong). The "replicates `verify()` substance" claim omits the producer's **leakage audit** (`leak()` + `blocking` gate, producer L86-87) without disclosure — only the chain-text omission is disclosed. `certify` never checks `qC`, `gold`, `N`, shapes, dtypes, or key completeness. `code_cert*.py` load the adapter from the live `REPO` checkout with **no sha gate** (v1 L47-50; v2 L31/50-52) — the "frozen adapter" premise is asserted, not checked, in exactly the scripts that need it.
- **Claims not produced by shown code (reading).** PLAN's "ITQ code variants (if present)": v1 only runs with `--itq` (default off); the brief's `code_certification.json` was never written — evidence lives in the sibling split files. LoCoMo `stats()` producer-sha is computed live (L196, good) but the "certified construction" label overstates counts-only evidence. `counts_report.json`'s `counts_match_transfer_proof: true` is 8 ints, no floats.
- **Silent fallbacks (reading).** `locomo_regen.py:99-107` parses proof lines by `startswith("{") and "conv_id" in line` — a reformatted proof silently yields `counts_match: None`/mismatch rather than a hard identity failure. `code_cert_v2.py:113-118` resume swallows *all* parse exceptions per line. `lme_regen.py:172` / producer `:100-102` resume by file existence: stale/corrupt pkls or item files are silently adopted, never re-hashed.

## 3. Residual risk register

| # | Demand before citing as canonical | Close locally? |
|---|---|---|
| 1 | Complete ITQ-refit comparison to 470/470 (currently 20/470) and aggregate it | Cheap (compute) |
| 2 | Fix NaN-hole + re-issue cert with `isfinite` guards; restate gate as ≤1e-12, not identity | Cheap |
| 3 | Hash-gate the adapter inside `code_cert_v2.py` (pin `0a1a39a8…`); close unclosed `ZipFile` (L69) | Cheap |
| 4 | Independent re-derivation of one question's C on a second BLAS/library stack to bound pipeline determinism (my 329/470 finding makes this non-theoretical) | Cheap–moderate |
| 5 | LoCoMo: any value-level anchor at all (e.g. publish per-conversation variance/occupancy vectors recomputable from pkls; get a second-party re-execution) — currently zero | Moderate (needs external corroboration) |
| 6 | Proof that ORIG `zero_mass == 0`: **impossible from frozen bytes** — no artifact distinguishes +0.0 from +ε (family (a) passes hetero+sign jointly). Only routes: byte-identical pipeline proof (item 4 across the full SVD stack, still an argument, not bytes) or finding the original cache | Impossible as certification; bound by reasoning |
| 7 | D4 median/p95 as *original* facts: same impossibility in principle (family (b)), mitigated only by the conjunction hetero+sign+ITQ shrinking the collision space | Impossible strictly; strengthen conjunction |
| 8 | Governance: keep `[LOCAL SESSION — NOT AN AUDIT]` labels and the cold-start-review requirement; do not let `470/470 bit-exact` (signs) be quoted as `matrices equal` | Free (wording) |

## 4. Script bugs (exact lines; none fixed)

**`harness/lme_regen.py`** (read 21:34 rev): (i) NaN-passthrough, L214-218/L221-223/L226-228 — failure mode above. (ii) Stale-resume adoption, L172 `if ip.exists() and not cp.exists()` (+`prep` L148, producer L101-102) — a leftover pkl from another code version is certified as fresh; no content hash anywhere on `items/` or `cache_repr/`. (iii) L116 misattributed OK/MISMATCH label for the post manifest. (iv) `certify` omits `qC`/`gold`/`N`/shape/dtype (later covered for signs/gold/N only by the sibling sign phase, magnitudes never). (v) Hard-coded `Path(r"C:/…")` — not runnable from WSL/POSIX (observed: runs happened under Windows Python, per `\r\n` log + `C:\` paths); portability, not logic. (vi) Relative-deviation denominator `max(abs(want),1e-300)` (L216/L221) is degenerate when `want == 0` (any nonzero `got` → ~1e300) — fail-noisy rather than fail-safe, acceptable but undocumented.

**`harness/code_cert_lme.py`** (v1, superseded): adapter loaded L47-50 with no sha check; ITQ section only under `--itq` (L70/L134) so default output lacks the strongest magnitude check; `bitorder_seen.add(str(…))` L79 unverified formatting (v2 output later confirmed values `["big"]`, matching npz dtype `<U3` seen by execution). No per-question shape/dtype log.

**`harness/code_cert_v2.py`** (22:29, current): L69 `zipfile.ZipFile(ZIP)` never closed; adapter hash still ungated (L31/L50-52); docstring L10 omits the `.jsonl` artifact; resume set L112-119 + aggregate L132-138 can double-count duplicated qids; `_itq_worker` L61 relies on `@`-binds-tighter-than-`>=` (correct but brittle to future edits); no `C` dtype/shape/`C_sha` recorded per question.

**`harness/locomo_regen.py`**: L204 `… if False else None` — `first32_top32_intersection_mean` is hardcoded `null` (dead expression, shipped in the stats JSON). L142-146 `C_sha256` is computed from the just-regenerated bytes — self-referential, certifies nothing, and its name invites misreading as a match. L134-137 counts-only comparison (8 ints) is the *entire* value evidence. L93 prints an expected-corrections count (156) it never asserts. L170 uses `diag.np` (works, fragile).

**`harness/task1_extend_lme.py` — v1 (my read pre-22:20) had two verified control bugs:** L34 expected zero-mass `(2*2)/(4*96)` vs actual `0.98958…` (the 94 all-zero columns were forgotten — `extension_run.log` traceback confirms the failure), and L47-48 asserted `median_abs == p95_abs == 1.0` for a matrix with a single perfect pair among 4560 — executed: actual median `0.0671`, p95 `0.1970`, both asserts FAIL. The 22:20 revision (current) fixes these (punched-zero ones-matrix expecting `2/384`; hand-computed `gt==0`/`ge==1/96`; D4 wiring replica) — but note case C replicates the formula inline, so it guards wiring/drift, not the definition itself.

**Bottom line.** The re-execution is genuine (frozen `buildrep`, all input hashes verify, 470/470 hetero-`0.0` + 470/470 sign-bit match corroborate a numerically identical pipeline), and the governance framing is honest about what is missing. But "certified-equivalent" overclaims for exactly the intended new numbers: `zero_mass`/`D1_gt` have **no** original-byte evidence (family (a) passes hetero + sign-code jointly — verified), D4's quantiles are underdetermined by the checked scalars (verified), LoCoMo has no value evidence at all, and the headline `0.0`s are BLAS-contingent (329/470 differ at last bit under a different numpy — verified, worst `2.27e-14`, within TOL). Cite D2/D3/`D1_ge` freely; cite `D1_gt`/`zero_mass`/D4 only with the determinism caveat and the open items 1–4 above; treat LoCoMo statistics as provisional pending item 5.# Certification red-team review: LME + LoCoMo "certified regeneration"

**Session note.** This session is write-locked (report file could not be saved under `~/muse-work/reports/`), so the review is delivered as the answer. A sibling session was actively writing mid-review (`task1_extend_lme.py` fixed 22:20, `code_cert_v2.py` + `code_certification_sign.json` + `code_certification_itq.jsonl` appearing 22:29–22:30); findings distinguish versions. **Verified by execution** = I ran it (commands quoted); **by reading** = code/text inspection. No regeneration was run; nothing was modified.

**Status snapshot (execution).** `certification_report.json` present (all deviations `0.0`, 470/470). `code_certification.json` (the filename in the brief): polled 8× at 60 s intervals — **absent all 8 polls**. Siblings instead wrote `code_certification_sign.json` (22:30) and `code_certification_itq.jsonl` (22:30, 20/470 lines at read time). `task1_extension_lme.json/csv` appeared 22:20. `extension_run.log` at first read contained only a traceback (quoted in §4).

All pinned input hashes re-verified by execution (`sha256sum`):

```
8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996  v52_t4c3_coordinate_axis_probe.py
148ae5b727ce1aedc6c84ee9c00727f1454b0e0710d100ac8154fdf8d00924cb  V52_T4C3_native_heterogeneity.csv
d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442  longmemeval_s_cleaned.json (277383467 bytes ✓)
0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722  adapter v1
643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218  adapter v2
```

T4D script == seal `sealed_compute_script_sha256` (`3f7f091f…`, match verified by execution) ✓. Geometry zip holds 470 `.npz` with keys `sign_doc_packed (N,12) uint8`, `sign_query_packed (12,)`, `itq_* (5 seeds [101 202 303 404 …])`, `gold_rows`, `N_archive`, `bitorder '<U3' ['big']` ✓ (via `zipfile`+`np.load`, no sklearn needed). First npz `N=514` matches regen pkl `001be529` shape `(514, 96)` ✓.

## 1. Logical validity

**Covered by the LME hetero cert** (per question): full diagonal variance vector (96), `>=0` occupancy vector (96), and 10 derived scalars (CV, variance entropy, participation ratio, max/median, cov off-diag energy ratio, mean |corr|, occupancy mean/min/max/MAD). `%.17g` round-trips float64 exactly — verified by execution (100k random + edges incl. `5e-324`, `1/3`, `π`: all bit-exact):

```
roundtrip exact: True maxreldiff: 0.0
edge roundtrip OK
```

CSV scalars are also repr-exact (`'1.0160257012999805'`), so the all-`0.0` claim is meaningful, not formatting-limited.

**NOT covered by any original-byte evidence:** exact-zero mass `(C==0).mean()`; strict-`>0` occupancy/entropy; off-diagonal sign/quantile structure (median/p95 of |corr|); per-entry magnitudes beyond column sums-of-squares; `qC` magnitudes (query signs later covered by the sign-cert, magnitudes never); row norms; anything about `C`'s ~22.2M entries not captured by column sums-of-squares, column sign-counts, and two cov scalars.

**Family (a) — constructed, verified end-to-end (execution).** N=400, 96 columns tiling `[2,1,-1,-2]` vs `[2t,0,-t,-t]`, `t=√(5/3)`. Every LME check passes within ≤4.3e-15 (TOL 1e-12), occupancy exactly identical, **and `packbits(C>=0)` bit-identical (verified by execution)** — yet:

```
--- LME-cert fields (must all be ~0 to pass) ---
variance_cv                            reldev=0.00e+00
normalized_variance_entropy            reldev=0.00e+00
variance_participation_ratio           reldev=1.48e-16
max_median_variance_ratio              reldev=0.00e+00
cov_offdiag_frobenius_energy_ratio     reldev=0.00e+00
mean_abs_coordinate_correlation        reldev=2.22e-16
sign_occupancy_mean/min/max/MAD        reldev=0.00e+00 (all four)
variance_vector maxrel=4.26e-15 occupancy maxabs=0.00e+00
--- intended-use functionals (NOT certified) ---
zero_mass: 0.0000 vs 0.2500
sign_entropy_gt: 1.000000 vs 0.811278 | sign_entropy_ge: 1.000000 vs 1.000000
sign-code bit-identical: True (shapes (400, 12) (400, 12))
```

This defeats the hetero cert **and** the sign-code cert jointly: `+0.0` and small positives share the same `>=0` bit, so exact zeros are invisible to every frozen artifact. The sibling sign-cert result (`sign_doc 470/470`, `sign_query 470/470`, `exact_zero_entries_in_regenerated_C: 0`, `total_docs: 231606`) therefore does **not** certify `zero_mass == 0` for the originals — that number rests purely on re-execution determinism.

**Family (b) — constructed at correlation level, verified (execution), with one honest caveat.** Two PSD 6×6 unit-diagonal matrices: mean|corr| reldev `1.78e-16`, RMS exactly equal, but median gap `0.0912`, p95 gap `0.0707` (Ra median 0.236/p95 0.633 vs Rb 0.327/0.704; eigmin `3.42e-02`/`1.10e-01`):

```
Ra mean=0.312410644235 rms=0.379798813009 median=0.236033 p95=0.633228
Rb mean=0.312410644235 rms=0.379798813009 median=0.327192 p95=0.703913
reldev mean=1.78e-16 rms=0.00e+00
```

Two scalars cannot pin 15 (here; 4560 in production) pair magnitudes — the constraint manifold has ~13+ free dimensions. Caveat: I matched variance/cov-scalar structure but did not jointly force identical occupancy vectors into the same pair, so this is a proof of D4-underdetermination, not a literal full-cert-passing pair. A full joint collision (45k entries vs ~200 constraints) almost surely exists but is a real optimization project, not a hand construction.

**Adequacy verdict for the intended use.** D2/D3/`D1_ge` (variance/occupancy functionals): certified. `D1_gt`/`zero_mass`: **not certified against original bytes** — the extension's `zero_mass mean 0.0`, `D1_gt == D1_ge` (means both `0.9970337299075775`, diff `0.0`) are properties of the regeneration promoted by a determinism argument. D4: the two hetero cov scalars do not constrain median/p95 (shown); the pending ITQ-refit evidence is magnitude-sensitive and is the best distinguisher, but it is refit-based (a variant in the same code basin passes) and was 20/470 when read. LoCoMo is weaker still: `counts_report.json` checks only 8 integer fields per conversation against the transfer proof — **zero value-level evidence** for any of the 10 C matrices (the proof contains no value payload; the `R@3 0.2365…` target is never checked by the harness, by design). `C_sha256` in LoCoMo pkls is self-computed at write time (recomputed hash matches stored, verified), not a match against anything. LoCoMo pkl spot check (execution): `C (419,96) float64`, `zero_mass 0.0`, finite, column-mean maxabs `2.04e-16`, stats file consistent (`D1_gt==D1_ge`, `zero_mass mean 0.0`).

## 2. Hash/identity chain holes (with verification status)

- **NaN hole in `certify` (execution-verified).** [lme_regen.py](/mnt/c/Users/MDP/dev/llmzip-work/harness/lme_regen.py:214) `if d > stats[k]` with `d = NaN` is `False`, so a NaN regenerated field leaves `stats` at `0.0` — a corrupt regen certifies clean. Same for the vector paths (L221/L226); quoted output: `nan-hole: stats stays 0.0`, `vec nan rel = nan ; nan > 0.0 = False`. Fix: `>=` + explicit `isfinite` rejection. (Production impact unlikely, but the headline `0.0` cannot exclude it.)
- **All-`0.0` is environment-contingent (execution-verified).** Recomputing `cov_offdiag_frobenius_energy_ratio` from the *same* pkls under this machine's numpy 2.5.3/BLAS: last-bit differs on **329/470** questions, `mean_abs` on **222/470**, variance vectors on **0/470**; worst reldev `2.27e-14` at `gpt4_5dcc0aab` (≪ TOL, but ≠ 0). E.g. `001be529`: stored/csv `…80831` vs recomputed `…81025` (per-field breakdown: 9/10 fields stored==mine, only the `C.T@C` cancellation-amplified ratio differs). The regen env matched the original env's BLAS summation bit-exactly — itself evidence of numerical identity of the pipeline — but an independent auditor recomputing hetero **will see nonzero deviations**. Present the gate as `≤1e-12`, not `0.0`-implies-identity.
- **Vacuous/misleading gates (reading).** `lme_regen.py:116` prints `[OK] parent post-run manifest bindings` whenever `problems` is empty *including* dataset/cohort problems — misattribution (gate still fails overall, message wrong). The "replicates `verify()` substance" claim omits the producer's **leakage audit** (`leak()` + `blocking` gate, producer L86-87) without disclosure — only the chain-text omission is disclosed. `certify` never checks `qC`, `gold`, `N`, shapes, dtypes, or key completeness. `code_cert*.py` load the adapter from the live `REPO` checkout with **no sha gate** (v1 L47-50; v2 L31/50-52) — the "frozen adapter" premise is asserted, not checked, in exactly the scripts that need it (`fit_itq` itself is deterministic given `V`: `default_rng(seed)` + fixed 100-iteration SVD loop — read, L112-124 of the adapter — but SVD sign conventions are library-version-sensitive, so the ITQ check is version-fragile).
- **Claims not produced by shown code (reading).** PLAN's "ITQ code variants (if present)": v1 runs only with `--itq` (default off); the brief's `code_certification.json` was never written — evidence lives in the sibling split files. LoCoMo `stats()` producer-sha is computed live (L196, good) but the "certified construction" label overstates counts-only evidence.
- **Silent fallbacks (reading).** `locomo_regen.py:99-107` parses proof lines by `startswith("{") and "conv_id" in line` — a reformatted proof silently yields `None`/mismatch rather than a hard identity failure. `code_cert_v2.py:113-118` resume swallows *all* parse exceptions per line. `lme_regen.py:172` / producer L101-102 resume by file existence: stale/corrupt pkls or item files are silently adopted, never re-hashed.

## 3. Residual risk register

| # | Demand before citing as canonical | Close locally? |
|---|---|---|
| 1 | Complete ITQ-refit comparison to 470/470 (20/470 at read) and aggregate it | Cheap (compute) |
| 2 | Fix NaN-hole + re-issue cert with `isfinite` guards; restate gate as ≤1e-12, not identity | Cheap |
| 3 | Hash-gate the adapter inside `code_cert_v2.py` (pin `0a1a39a8…`); close unclosed `ZipFile` (L69) | Cheap |
| 4 | Independent re-derivation of one question's C on a second BLAS/library stack to bound pipeline determinism (§2 finding makes this non-theoretical) | Cheap–moderate |
| 5 | LoCoMo: any value-level anchor at all (e.g. publish per-conversation variance/occupancy vectors recomputable from pkls; second-party re-execution) — currently zero | Moderate (needs external corroboration) |
| 6 | Proof that ORIG `zero_mass == 0`: **impossible from frozen bytes** — no artifact distinguishes +0.0 from +ε (family (a) passes hetero+sign jointly). Only routes: byte-identical pipeline proof (item 4, still an argument) or finding the original cache | Impossible as certification; bound by reasoning |
| 7 | D4 median/p95 as *original* facts: same in-principle gap (family (b)); mitigated only by the hetero+sign+ITQ conjunction shrinking the collision space | Impossible strictly; strengthen conjunction |
| 8 | Governance: keep `[LOCAL SESSION — NOT AN AUDIT]` labels and the cold-start-review requirement; never let `470/470 bit-exact` (signs) be quoted as `matrices equal` | Free (wording) |

## 4. Script bugs (exact lines; none fixed)

**`harness/lme_regen.py`**: (i) NaN-passthrough, L214-218/L221-223/L226-228 — failure mode §2. (ii) Stale-resume adoption, L172 `if ip.exists() and not cp.exists()` (+`prep` L148, producer L101-102) — a leftover pkl from another code version is certified as fresh; no content hash on `items/` or `cache_repr/`. (iii) L116 misattributed OK/MISMATCH label for the post manifest. (iv) `certify` omits `qC`/`gold`/`N`/shape/dtype (signs/gold/N later covered only by the sibling sign phase, magnitudes never). (v) Hard-coded `Path(r"C:/…")` — unrunnable from WSL/POSIX (runs happened under Windows Python: `\r\n` log, `C:\` paths); portability, not logic. (vi) Denominator `max(abs(want),1e-300)` (L216/L221) is degenerate when `want == 0` — fail-noisy, undocumented.

**`harness/code_cert_lme.py`** (v1, superseded): adapter loaded L47-50 with no sha check; ITQ section only under `--itq` (L70/L134) so default output lacks the strongest magnitude check. No per-question shape/dtype log.

**`harness/code_cert_v2.py`** (22:29, current): L69 `zipfile.ZipFile(ZIP)` never closed; adapter hash still ungated (L31/L50-52); docstring L10 omits the `.jsonl` artifact; resume set L112-119 + aggregate L132-138 can double-count duplicated qids; `_itq_worker` L61 relies on `@`-binds-tighter-than-`>=` (correct but brittle); no `C` dtype/shape/`C_sha` recorded per question.

**`harness/locomo_regen.py`**: L204 `… if False else None` — `first32_top32_intersection_mean` hardcoded `null` (dead expression shipped in JSON). L142-146 `C_sha256` computed from just-regenerated bytes — self-referential, invites misreading as a match. L134-137 counts-only comparison (8 ints) is the *entire* value evidence. L93 prints an expected-corrections count (156) it never asserts. L170 uses `diag.np` (works, fragile).

**`harness/task1_extend_lme.py` — v1 (pre-22:20) had two verified control bugs:** L34 expected zero-mass `(2*2)/(4*96)` vs actual `0.98958…` (94 all-zero columns forgotten — `extension_run.log` traceback: `AssertionError: 0.9895833333333334`); L47-48 asserted `median_abs == p95_abs == 1.0` for a matrix with one perfect pair among 4560 — executed: median `0.0671`, p95 `0.1970`, both FAIL. The 22:20 revision fixes these (punched-zero ones-matrix expecting `2/384`; hand-computed `gt==0`/`ge==1/96`; D4 wiring replica) — but case C replicates the formula inline, so it guards wiring/drift, not the definition. Current-revision residual nits: `main()` has no dtype/shape/distinct-question gate beyond the 470 file count (filenames make collisions unlikely); cross-checks cover only 2 means; no `NaN` guard needed (diagnostics raises fail-safe).

**Bottom line.** The re-execution is genuine (frozen `buildrep`, all input hashes verify, 470/470 hetero-`0.0` + 470/470 sign-bit match corroborate a numerically identical pipeline) and the governance framing is honest about what is missing. But "certified-equivalent" overclaims for exactly the intended new numbers: `zero_mass`/`D1_gt` have **no** original-byte evidence (family (a) passes hetero + sign-code jointly — verified), D4's quantiles are underdetermined by the checked scalars (verified), LoCoMo has no value evidence at all, and the headline `0.0`s are BLAS-contingent (329/470 differ at last bit under a different numpy — verified, worst `2.27e-14`, within TOL). Cite D2/D3/`D1_ge` freely; cite `D1_gt`/`zero_mass`/D4 only with the determinism caveat and open items 1–4; treat LoCoMo statistics as provisional pending item 5.

*Quoted commands (all read-only): `sha256sum` on producer/CSV/dataset/adapters; `python3` (numpy 2.5.3, system) for round-trip, NaN-hole, family-(a) hetero+`packbits`, Ra/Rb feature gaps, 470-pkl BLAS sweep, extension-control bug reproductions, LoCoMo pkl/stats consistency, `C_sha256` recomputation; `zipfile`/`np.load` npz inventory; 8×60 s poll loop for `code_certification.json` (absent throughout; terminal `DONE`). Frozen-producer/SVD re-execution was never attempted (out of scope + forbidden).*
