# TASK 1 COMPLETION RECEIPT — LongMemEval & LoCoMo representation diagnostics

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Date:** 2026-09-12 (evening, Europe/Istanbul)
**Session:** local desktop working session (Hermes); no repository pushes; all outputs under `C:/Users/MDP/dev/llmzip-work/`.
**Labels:** `[LOCAL SESSION — NOT PUSHED]` `[CERTIFIED REGENERATION]` `[NOT AN INDEPENDENT AUDIT]`

---

## 0. Türkçe özet (executive summary)

Task1 `PARTIAL` durumdaki üç eksiği ve LoCoMo boşluğu kapatıldı. Yöntem: dondurulmuş üretici
scriptin (sha256 `8dce37b1…`) kanonik girdilerle **birebir yeniden koşulması** ve çıktının daha
önce yayınlanmış tüm değerlere karşı **sertifikasyonu**.

- **LongMemEval (470 soru):** Yeniden üretim, yayınlanmış heterojenlik CSV'sindeki 11 skaler alan
  ve iki 96'lık vektörün tamamında **sapma 0.0** (470/470). Eksik bileşenler artık hesaplandı:
  `zero_mass = 0.0` (tüm kohortta tek bir tam sıfır yok → `D1_gt ≡ D1_ge = 0.9970337299…`),
  `D4`: off-mass `0.15188848`, medyan|r| `0.00456888`, p95|r| `0.01644505`.
- **LoCoMo (10 konuşma):** Aynı aile temsil yeniden üretildi; dondurulmuş transfer-kanıtı
  sayımları **10/10** eşleşti; aynı istatistik ailesi hesaplandı (`zero_mass = 0.0`;
  CV_σ `0.48468867`; D4 off-mass `0.12849186`, medyan|r| `0.00330877`, p95|r| `0.01087587`).
- **Bağımsız hesap:** Ayrı bir Muse oturumu aynı sayıları bağımsız olarak yeniden hesapladı:
  tüm ortalamalar birebir; sd'ler ve arşiv-bazlı D4 değerleri son-ulp düzeyinde örtüşüyor.
- **Kod düzeyi sertifikasyon (LME):** Yeniden üretilen C'nin paketlenmiş 96-bit işaret kodları,
  boru hattının gerçekte tükettiği dondurulmuş NPZ kodlarıyla karşılaştırıldı: işaret kodları
  470/470 (doküman+query), ITQ kodları 470/470 × 5 seed (doküman+query) bit-birebir → bkz. §4b.
- Hâlâ geçerli sınırlar: bu bir **audit değildir**; sertifikasyon, yayınlanmış özetlere ve
  kodlara karşı kanıtlanmıştır, orijinal float byte'larına karşı değil (§7).

---

## 1. The gap being closed (from L-093)

`research/v52/preseal_diagnostics_2026_09_12/task1/RESULTS.json` (branch
`research/v52-preseal-diagnostics-2026-09-12` @ `4001fc9d`, manifest `5bf22716…`) is `PARTIAL`:

- `D1_gt` (strict >0 sign entropy) — `null`; zero mass unavailable.
- `zero_mass` — `null`; “`>=0` is not silently substituted for `>0`”.
- `D4` (correlation-matrix statistics: off-diagonal Frobenius ratio, median |r|, p95 |r|) — `null`;
  not recoverable from diagonal variances + aggregates.
- LoCoMo — no frozen matrix or sufficient statistics found at all.

`ops/CURRENT_STATE.json` → `next_single_action`: *“Recover exact mechanism-track frozen C arrays or
source-bound sufficient statistics for remaining Task1.”*

## 2. Source-recovery record (why regeneration)

1. **All 108 git branches:** no `.pkl`, no `.npy`/`.npz` except the diagnostics' own synthetic
   Task3 artifacts; the producer's `cache_repr/*.pkl` never existed in Git.
2. **Google Drive inventory (independent sweep, 193 API calls, 216 files / 583 MB enumerated):**
   - FOUND: `V52_T4C2_BINARY_GEOMETRY.zip` (sha256 `40026fe6…`, matches the pinned value) — per-question
     **packed 96-bit sign codes of C and qC** + 5-seed ITQ code variants for all 470 questions;
     `V52_T4C3_native_heterogeneity.csv` (`148ae5b7…`) and `V52_T4C3_rotated_heterogeneity.csv`.
   - NOT FOUND: float-valued C/qC, or literal `cache_repr/*.pkl` anywhere.
   - LoCoMo: only aggregate/summary artifacts, no codes.
3. Producer whitelist excluded the caches; therefore the only faithful path to the **missing**
   components is re-executing the frozen producer and **certifying** the result. This is the
   “source-bound sufficient statistics” route — not corpus reconstruction: the canonical dataset
   and audit layer are used exactly as published.

## 3. Inputs and gates (all independently re-hashed locally)

| artifact | sha256 (prefix) | status |
|---|---|---|
| producer `v52_t4c3_coordinate_axis_probe.py` | `8dce37b1…` | OK |
| canonical dataset `longmemeval_s_cleaned.json` (277,383,467 B) | `d6f21ea9…` | OK |
| adapters v1 / v2 | `0a1a39a8…` / `643082d6…` | OK |
| parent T4C2 script / seal / question-level / aggregate / trial table | `3bb11260…` / `19883841…` / `69c21b2f…` / `0a7c3ac8…` / `c6d58cdd…` | OK |
| `V52_T4C3_ALL_OUTPUTS.zip` internal manifest | 26/26 output hashes | OK |
| `V52_T4C3_PRE_RUN_SEAL.json` / post manifest | `c7cf7aa0…` / `7bfeae58…` | OK |
| hard gaps: tests? no — gate otherwise | | PASS |

Cohort checks: 500 total / 470 primary; parent aggregate reproduction values (SIGN96_CENTERED,
ITQ96_CENTERED) reproduced to ≤1e-12 inside the gate.

The harness (`harness/lme_regen.py`) re-implements the frozen producer `verify()` **substance** —
the only omitted item is the producer's redundant historical chain-text string check
(`'match=29  mismatch=0'`, a relic of a chain file not present in Git); every hash it covered is
checked directly. Disclosed.

## 4. Certification of the regeneration

**(a) Statistics level** (`regen/lme/certification_report.json`) — regenerated `hetero` records vs
`V52_T4C3_native_heterogeneity.csv`, all 470 questions, published vectors are `%.17g` (round-trip
exact):

| field | max relative deviation |
|---|---|
| 10 scalar fields (variance_cv, entropy, participation ratio, max/median ratio, off-diag Frobenius, mean abs corr, occupancy mean/min/max/MAD) | **0.0** |
| variance_vector (96 per question) | **0.0** |
| occupancy_vector (96 per question) | **0.0** |

Distinct float64 values print distinguishably under `%.17g`, so equality to the last printed digit
of a field implies bit-equality **of that functional** (verified by execution: `%.17g` round-trips
float64 exactly, including edge cases). This does not imply bit-equality of the whole matrix — see
§7 for exactly which functionals remain uncertified in principle.

**BLAS contingency (disclosed).** The all-`0.0` result was obtained under the pinned stack
(Python 3.13.15 / NumPy 2.3.5 / SciPy 1.17.0 / sklearn 1.8.0). An independent recomputation from the
same regenerated pickles under a different BLAS (NumPy 2.5.3 in WSL) shows last-bit deviations on
one cancellation-amplified scalar (`cov_offdiag_frobenius_energy_ratio`: 329/470 questions, worst
`2.27e-14`; variance vectors 0/470). The reproduction gate in substance is therefore **≤1e-12**;
the exact `0.0` under the pinned stack is evidence of numerical stack identity, not a claim about
hidden internal bytes. Both framings are recorded in `certification_report.json`.

**(b) Code level** (`regen/lme/code_certification_sign.json`, `..._itq.json`) — regenerated
`packbits(C>=0)` vs the frozen NPZ sign codes actually consumed by the pipeline (all 470 questions,
231,606 documents):

| check | result |
|---|---|
| `sign_doc_packed` bit-exact (all docs, all questions) | **470/470 questions, 0 mismatched bytes** |
| `sign_query_packed` bit-exact | **470/470** |
| `gold_rows` / `N_archive` cross-match | 470/470 / 470/470 |
| exact zeros in regenerated C | **0** (independent zero-mass confirmation; cold-start scan: 0/22,234,176 entries) |
| ITQ code variants (5 seeds, refit from regenerated C via the frozen adapter's own `fit_itq`) | **470/470 questions × 5/5 seeds, 0 mismatches** (2350 refits) |
| `itq_query_packed` (ITQ query codes, 5 seeds) | **470/470 × 5/5 seeds, 0 mismatches** (`code_certification_itq_query.json`; doc codes independently re-derived in the same pass, 470/470; `bitorder` = "big") |
| ITQ cross-stack sample (10 questions × 5 seeds under NumPy 2.5.3 / WSL) | **50/50 exact** (`regen/lme/itq_crossstack_sample_result.txt`) |

So the regenerated matrices are certified **at the exact bit level the retrieval pipeline
consumed**: the 96-bit sign code of every one of 231,606 documents, every query code, and every
stored ITQ code variant (5 seeds; document *and* query channels — the latter added after the
cold-start review noted the query channel was the one uncovered NPZ field) reproduce
bit-identically from the regeneration. (Scope qualifier
per §7: this certifies the consumed codes and the functionals of §4a; hidden float bytes are not
claimed and this is not an audit.)

**(c) LoCoMo** (`regen/locomo/counts_report.json`) — per-conversation feature-count blocks vs the
frozen T4D representation transfer proof: **10/10 exact** (N, fit docs, query counts, word/char/
latent/concat feature counts, mixed96 dim, no_nan). Two independent local executions agree
(this session and a parallel subagent session), including the frozen native R@3 anchor
`0.23654714666441054` reproduced with absolute error 0.0.

**Second-party value-level re-execution (Muse `01a09725-8449-…`, different stack):** a fresh
session independently re-ran the frozen producer's `load_dataset`/`build_representation` on the
re-verified inputs (sha256 of `locomo10.json` and the 20-file audit manifest both re-matched
exactly) under python 3.14.4 / numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1 — a *different* library
stack from the producer run — and compared value-for-value against `counts_report.json` /
`task1_locoMo_stats.json`. **Structural quantities bit-exact**: N, all 8 feature-count fields,
C_shape, `zero_mass` ≡ 0.0 with 0 exact zeros in every matrix, `>=0` vs `>0` occupancy vectors
indistinguishable (deviation 0.0 — no exact zeros), `sign_entropy_ge ≡ sign_entropy_gt` (abs 0.0),
D1_ge and D2_cv_sigma summary means abs-diff 0.0. Numeric scalars agree to **≤3e-15 absolute**
(worst relative deviation 1.91e-14 on the variance vectors; other scalars ≤2.53e-15 abs) —
statistical identity to ~15 digits across stacks. The one cross-stack non-reproduction is raw
`C_sha256` bytes (0/10 match): last-bit SVD/LAPACK drift, now quantified and disclosed instead of
hidden. Report: `reports/muse_locomo_reval_2026-09-12.md`.

## 5. Task1 extension results — the previously missing numbers

**LongMemEval (470 archives, equal archive weight; `regen/lme/task1_extension_lme.json`/`.csv`):**

| quantity | mean | sd (ddof=1) | min | max |
|---|---:|---:|---:|---:|
| sign_entropy_gt | 0.9970337299075775 | 0.0009689546162983 | 0.9910369335593018 | 0.9985525937037742 |
| sign_entropy_ge | 0.9970337299075775 | 0.0009689546162983 | 0.9910369335593018 | 0.9985525937037742 |
| zero_mass | 0.0 | 0.0 | 0.0 | 0.0 |
| D4 off_mass | 0.15188848165900984 | 0.0047941373669431 | 0.14136795136168004 | 0.18360279501925347 |
| D4 median_abs | 0.004568877386692503 | 0.0005389887508335 | 0.0032450178521927784 | 0.00647873137859092 |
| D4 p95_abs | 0.01644504773681544 | 0.0023304207234861 | 0.010925721125563198 | 0.028766378907234855 |

Cross-checks vs published values: `D1_ge` abs diff **0.0**; `D2_cv_sigma` abs diff **0.0**.
`zero_mass = 0.0` in all 470 matrices ⇒ `D1_gt ≡ D1_ge` **bit-for-bit** in every archive; the
strict `>0` form is therefore resolved by measurement, not by assuming it away.
Controls: 4/4 PASS (exact zero mass; gt/ge separation with hand values; D4 definition replication;
zero-free equivalence).

**LoCoMo (10 conversations; `regen/locomo/task1_locoMo_stats.json`):**

| quantity | mean | sd (ddof=1) | min | max |
|---|---:|---:|---:|---:|
| sign_entropy_gt/ge | 0.9981814455753918 | 0.0008680842710107 | 0.9963954013256103 | 0.9988823024676217 |
| zero_mass | 0.0 | 0.0 | 0.0 | 0.0 |
| cv_sigma (D2) | 0.48468867201587706 | 0.0228688714052314 | 0.4383418544288973 | 0.5084442294219229 |
| top16/32/48 variance share (D3) | 0.4634647 / 0.7508988 / 0.8276080 | — | — | — |
| D4 off_mass | 0.1284918632163776 | 0.0033124558926796 | 0.12410413373959321 | 0.13334246917797715 |
| D4 median_abs | 0.003308774681940944 | 0.0004587852043319 | 0.0023902879396356354 | 0.003843345382805438 |
| D4 p95_abs | 0.01087587274446762 | 0.0016840365617067 | 0.007684031768217595 | 0.013267398542722585 |

Descriptive cross-benchmark observation (no inference): LME vs LoCoMo — CV_σ 0.4975 vs 0.4847;
top32 share 0.7599 vs 0.7509; D4 median|r| 0.00457 vs 0.00331. Both fixed benchmarks only.

## 6. Independent computations

- **Independent executor (Muse session `01a0970e-db02-…`):** imported the frozen diagnostics
  functions verbatim, computed all extension quantities from the regenerated matrices *before*
  looking at this session's outputs. Agreement: all 7 LME means exact; sds and per-archive D4
  agree to the last ulp (~1e-17 or better, summation-order); sign entropy and zero_mass exact in
  the sampled set. Its controls: all-zero, perfect-correlation (off_mass =
  1/√2 exactly), alternating ±1, single active coordinate, ge/gt live-ness, plus a direct numpy
  recomputation of one archive (0 exact zeros in 49,344 entries).
- **Red-team review of the certification method (Muse session `01a0970e-dbda-…`, xhigh):** its
  central scientific finding, reproduced by execution: **no frozen artifact can distinguish exact
  `+0.0` entries from tiny positives** — it constructed a matrix family (tiled columns
  `[2,1,−1,−2]` vs `[2t,0,−t,−t]`, `t=√(5/3)`) that passes every certification check jointly
  (all hetero fields ≤4.3e-15, occupancy bit-identical, `packbits(C>=0)` bit-identical) while
  having `zero_mass` 0.25 vs 0.0. Therefore `zero_mass = 0` and D4's quantiles are **not
  certifiable against original bytes in principle**; they rest on the determinism argument
  (identical pipeline re-execution) — which the same review independently corroborated at three
  levels (hetero fields, sign codes, ITQ codes). It also verified `%.17g` round-trip exactness,
  re-verified every pinned input hash, and found+reproduced real harness defects (NaN-passthrough
  in `certify`; adapter loaded without a sha gate; stale-resume adoption; a dead expression and
  self-referential hash labels in the LoCoMo script; two bugs in the v1 extension controls, since
  fixed). **All cheap fixes were applied and the artifacts re-issued** (NaN-safe `certify` with
  `isfinite` rejection and a 470-pkl sha256 manifest; adapter sha-gated in `code_cert_v2.py`;
  ZipFile handles closed; dedupe in the ITQ aggregate; LoCoMo vectors now published and hash
  labels corrected; framing text above). Residual items that remain open are listed in §7.
- Local byte-level verification receipts for the three most recent accepted packages
  (`reports/local_verification_receipts.md`): 536/536 declared hashes matched across 502 files;
  all three verifiers PASS (G3 suite 54/5961 in a gate-satisfying environment; disclosed caveat:
  the pipeline module hard-requires a checkout-relative interpreter path).
- **Second independent verification pass (Muse `01a0970e-d9e2-…`):** repeated the package
  verification from WSL with `git archive`-based extraction: preseal 49/49 (+23/+14 sub-manifests),
  itq-haar 18/18 + verifier PASS, G3 432/432 + `package_integrity` PASS. Its one flagged "README
  discrepancy" (54/5961 vs 53/5959) was **adjudicated by the orchestrating session as a false
  positive**: the README distinguishes the initial candidate's evidence (`evidence/final`,
  53/5959) from the delta's updated suite (`evidence/a1_fixed`, 54/5961) — both files verified
  present with exactly those counts.
- **Cold-start adversarial review of this package (Muse `01a09720-8229-…`, xhigh):** independent
  re-derivation of a 12-question / 2-conversation sample *before* opening this package's own
  outputs; full recounts; schema conformance. Confirmed: sign-bit exactness in all samples; stats
  exact 6/6; a full exact-zero scan — **0 zeros in 22,234,176 LME entries** plus all 10 LoCoMo
  matrices (independent confirmation of `zero_mass = 0.0` as measured on the regeneration); 470
  pkls / 470 CSV rows / ΣN = 231,606 / 470 ITQ records all recounted; 5,717 of 5,720 non-null
  frozen leaves in the extended RESULTS identical — the 3 diffs are intentional builder updates
  (the two LME `*_reason` for-null strings cleared where the nulls are now filled; the LoCoMo
  `status` advanced), each self-documented in the artifact's `intentional_frozen_leaf_updates`
  block. Raised five defects, all now resolved:
  (D1/D2) "bit-equal" wording overstated for per-archive D4 rows and three LME sds (they agree to
  the last ulp, not bit-exactly) — wording corrected in §0/§6; (D3) extended RESULTS filled only
  top-level summaries — now fills all 470 per-archive rows; (D4) a stale filename in §8 — fixed;
  (D5) §4b needed §7's qualifier inline — added. Its verdict: "the package supports its
  substance" with the corrections applied. Report: `reports/muse_coldstart_review_2026-09-12.md`.
- **Second-party LoCoMo value re-execution (Muse `01a09725-8449-…`, different stack):** all
  structural quantities bit-exact, numeric scalars ≤3e-15 absolute (details in §4c); cross-stack
  `C_sha256` byte drift quantified (0/10) and disclosed. Report:
  `reports/muse_locomo_reval_2026-09-12.md`.
- **ITQ cross-stack sample (orchestrator-executed):** 10 questions × 5 seeds refit under
  numpy 2.5.3 (WSL) → stored `itq_doc_packed` codes matched **50/50 exactly**
  (`regen/lme/itq_crossstack_sample_result.txt`), closing the cold-start review's blocked
  "ITQ refit re-execution" item at sample depth.
- **Closure verification of the fix round (Muse `01a09734-35d7-…`, read-only):** re-tested every
  fix end-to-end — NaN-safe `upd` (dynamic probe: NaN/inf/None recorded, never silently kept);
  adapter sha pins byte-equal to the real adapter file in both scripts; ITQ query channel
  independently spot-refit (**25/25 query + 25/25 doc exact**, different stack, zero flips);
  full `sha256sum -c` of the manifest clean; receipt wording checks pass. Verdict:
  **5 PASS / 1 CAVEAT / 0 FAIL**; its single caveat — the "0 diffs" phrasing vs 3 intentional
  frozen-leaf updates — was resolved by correcting the claim wording here and self-documenting
  the updates inside the artifact (`intentional_frozen_leaf_updates`). The review also flagged a
  stale "7/7 bit-equal" string embedded in the extended RESULTS' `independent_recomputation`
  field — regenerated with corrected wording.

## 7. Caveats and residual limits (read before citing)

1. **This is not frozen-byte recovery; it is the strongest certification the published artifacts
   permit.** Certified at three levels: (i) all 12 published heterogeneity functionals reproduce
   (0.0 under the pinned stack; ≤1e-12 in substance — see §4a BLAS note); (ii) the consumed
   packed sign codes are bit-identical for every document and query (470/470); (iii) the stored
   ITQ codes are bit-identical under refits (470/470 × 5 seeds, document and query channels;
   cross-stack sample 50/50). Whether hidden internals byte-for-byte
   equal the originals is neither claimed nor claimable.
2. **In-principle limits — proven by red-team construction.** No frozen artifact distinguishes
   exact `+0.0` entries from tiny positives, and correlation quantiles (median/p95) are
   underdetermined by the checked scalars: constructed families pass every check jointly while
   differing (`zero_mass` 0.25 vs 0.0; median |r| gap 0.09 on a 6×6 analogue). Consequently:
   - cite **D2 / D3 / D1_ge freely** (directly certified functionals);
   - cite **`D1_gt` / `zero_mass` / D4** as *determinism-argument results on the certified
     regeneration* — the numbers are as computed; their identity with the originals is supported
     by the triple-level reproduction, not by a byte certificate (which cannot exist here).
3. **LoCoMo value-level evidence now exists — and its cross-stack limit is quantified.** An
   independent re-execution on a *different* library stack (Muse `01a09725-8449-…`; python 3.14.4
   / numpy 2.5.3 / scipy 1.18.1 / sklearn 1.9.1) reproduced every structural quantity bit-exactly
   and every numeric scalar to ≤3e-15 absolute (worst relative 1.91e-14 on variance vectors).
   The residual non-reproduction is raw `C_sha256` bytes across LAPACK versions (0/10) — expected
   last-bit SVD drift; the `C_sha256` fields inside the stats/counts files are this session's own
   recomputed values (self-consistent, not a pinned external target). Treat LoCoMo statistics as
   *construction-certified + second-party value-verified*, byte-identity not claimed (and not
   claimable cross-stack).
4. No retrieval metrics were recomputed: no top-3 IDs, distances, recalls or arm outcomes were
   touched anywhere in this work.
5. Fixed-benchmark descriptive statistics only; no population inference; no causal claims.
6. Independent **audit** status is separate: per programme rules a cold-start review is still
   required before these numbers become canonical.
7. Task 4F1 untouched throughout (SEALED / RUN BLOCKED / OUTCOME ACCESS FORBIDDEN).

## 8. Files (all under `C:/Users/MDP/dev/llmzip-work/`)

- `harness/lme_regen.py`, `harness/locomo_regen.py`, `harness/code_cert_v2.py`, `harness/task1_extend_lme.py`,
  `harness/build_extended_results.py`, `harness/code_cert_itq_query.py` (and the superseded `harness/code_cert_lme.py` v1, kept for history)
- `regen/lme/certification_report.json`, `regen/lme/code_certification_sign.json`,
  `regen/lme/code_certification_itq.json`, `regen/lme/code_certification_itq_query.json` (+ `.jsonl`, 470 records each)
- `regen/lme/task1_extension_lme.json` / `.csv` (470 rows), `regen/lme/cache_repr/*.pkl` (470)
- `regen/locomo/counts_report.json`, `regen/locomo/task1_locoMo_stats.json`, `regen/locomo/locomo_*.pkl` (10)
- `regen/muse_independent/` — Muse bağımsız rapor + compute/controls/results.json
- `reports/muse_twelve_byte_audit_2026-09-12.md`, `reports/muse_redteam_certification_2026-09-12.md`,
  `reports/muse_coldstart_review_2026-09-12.md`, `reports/muse_locomo_reval_2026-09-12.md`,
  `reports/local_verification_receipts.md`, `reports/locomo_representation_provenance.md`,
  `reports/drive_inventory.md` (+csv), `reports/muse_sessions/` (raw session transcripts)
- `regen/lme/itq_crossstack_sample.py` / `_result.txt`; `PLAN_TASK1_COMPLETION.md` — method/plan record

### Provenance hashes of this session's own artifacts

`HASHES_TASK1.txt` (60 entries: harness scripts, all regeneration/certification JSON+CSV outputs,
Muse reports + raw session transcripts, draft documents; self-excluded by convention; every entry
verifies via `sha256sum -c`). The receipt's own hash is recorded in
the delivery message after the final edit (the file changes with every amendment; no receipt hash
is asserted inside it).
