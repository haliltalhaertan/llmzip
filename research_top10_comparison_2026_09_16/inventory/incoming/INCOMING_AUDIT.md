# INCOMING 2026-09-16 PACKAGE AUDIT (inventory of what was already measured)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Scope: the 2026-09-16 package produced by another LLM (gpt-6-pro), read from
`/mnt/c/Users/MDP/dev/llmzip-work/incoming_20260916/extracted/` (READ-ONLY).
Nothing outside my own directory was written. No benchmarks were run; no paid
APIs, web tools, or git commands were used. Python: `$HOME/muse-work/ml-python`.

Status labels (never upgraded): VERIFIED = re-derived this session from raw
per-query data or raw caches. CLAIM = producer states it; not re-derived here.
RELAYED = quoted second-hand; original not inspected.

My re-aggregation code: [recheck.py](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/inventory/incoming/recheck.py),
results: [recheck_results.json](/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/inventory/incoming/recheck_results.json).
A throwaway definition probe lives at `/tmp/derive_qsign2.py` (not a deliverable).

## 1. THE ONE DISCREPANCY — RESOLVED (VERIFIED)

There is no bug on either side. The two sides scored **different arms under one
name**. The difference is exactly one operation: per-document L2 normalization.

THEIR definition (`readout_diagnostic.py`, HATA package):

- Line 87: `sd=np.maximum(C.std(0),1e-12)` — population std (ddof=0 default),
  floored. **Same sigma the coordinator used.**
- Lines 31–33 `unit()`: per-row L2 normalization.
- Line 87: `Ds=unit(C/sd)` — scaled docs, then **each document row normalized**.
- Line 88: `Qb=np.where(Q>=0,1.,-1.)` — same sign convention as coordinator.
- Line 97: `'query_sign_doc_std':Qb@Ds.T/np.sqrt(96)` — cosine-like on doc side.

COORDINATOR's definition (`coordinator/verify_incoming.py`, lines 31–42):

- `sigma_docs`: `np.std(..., ddof=0)`, floor 1e-12 — identical sigma.
- Line 42: `"qsign_dstd": (C / sg[None, :]) @ qb` — raw dot, **no per-doc norm**.

Because `||C_d/sigma||` varies per document, the two rankings genuinely differ,
so deviations (LME +0.6383, PerLTQA −0.2662, RealTalk −0.8511 pp,
coordinator-minus-theirs) are expected. VERIFIED numerically: I re-implemented
THEIR formula against the raw caches and reproduced THEIR numbers to
+0.000000 pp on all three benchmarks (LME n=470 → 87.6595744681;
PerLTQA n=8265 → 79.7338173019; RealTalk n=705 → 50.3546099291).

Corollary (why `qscale` matched EXACTLY): their `doc_sign_query_std`
(line 96: `Qs@Db.T/np.sqrt(96)`, `Qs=unit(Q/sd)`) differs from the
coordinator's `B @ (q/sg)` only by a per-query positive scalar plus a global
1/sqrt(96) — both rank-invariant for a fixed query. The HIZ native path is a
third spelling of the same ranking (`validate_and_profile.py:56`:
`'weighted':B@(Q[i]/s.sd)`; `kernels.c:14-18` LUT holds `q/sd` unnormalized).
The coordinator's 0.000000 pp reproduction IS the numerical proof of this
rank-equivalence. The frozen pre-run formula agrees
(`PLAN_BEFORE_RUN.json`: `s(d,q)=sum_j (2*bit_dj-1)*qC_j/max(std(C[:,j],ddof=0),1e-12)`).

Note: `scripts/quality.py` (2026-09-15 benchmark) contains NO `query_sign_doc`
arm at all (lines 4–5: only float64/float_std64/float_std32/sign96/sign88_top/
sign80_top) — the fork lives entirely in `readout_diagnostic.py` + HIZ.

## 2. HEADLINE NUMBERS RE-AGGREGATED FROM THEIR OWN RAW CSVS (VERIFIED)

- HATA `readout_per_query.csv`: 94,400 rows = 9440 queries × 10 arms. My means
  match their `readout_summary.json` (all cells × 6 metrics) to max dev
  2.2e-16, and their `DIAGNOSIS_SUMMARY.json hit10_percent` to 1.1e-16.
- HIZ `quality_per_query.csv`: 65,826 rows = 10,971 queries × 6 arms. My means
  match `FINAL_SUMMARY.json hit10_percent` to max dev 0.0 pp (all 24 cells).
- qscale-minus-Hamming deltas CONFIRMED: LME +2.4333, PerLTQA +4.2388,
  RealTalk +2.9645 → rounds to their +2.43 / +4.24 / +2.96. (VERIFIED)
- LoCoMo CONFIRMED (n=1531): hamming 52.6380 / asym_raw 56.8256 /
  weighted 57.2175 / float32 61.0059 → 52.64 / 56.83 / 57.22 / 61.01. (VERIFIED)
- LoCoMo paired counts re-derived EXACTLY incl. win/loss splits: 156/78, 70/64,
  56/114; deltas +4.5795 / +0.3919 / −3.7884 pp. (VERIFIED)
- HATA paired-contrast spot checks (RealTalk standardized_cos→doc/query_sign_
  doc_std) match to all printed digits. (VERIFIED)

## 3. CRITICAL COMPARISON: qscale MINUS OLD ASYM (VERIFIED — decides the claim)

From THEIR raw data (HATA and HIZ agree to 4 decimals — expected, since HIZ
asserts exact old-metric equality per query, `validate_and_profile.py:71-73`):

| benchmark | new (qscale) | old asym | delta (pp) |
|---|---|---:|---:|
| LME | 88.51 | 85.74 | **+2.77** |
| PerLTQA | 80.00 | 80.19 | **−0.19** |
| RealTalk | 49.65 | 43.55 | **+6.10** |
| LoCoMo (HIZ only) | 57.22 | 56.83 | **+0.39** |

This reproduces the coordinator's independent-data finding (+2.77 / −0.19 /
+6.10) almost digit-for-digit. Plain reading: "scale balancing" adds a large
gain on RealTalk, a moderate gain on LME, and nothing (slightly negative) on
PerLTQA. On the only transfer set (LoCoMo) the gap is +0.39 pp whose own
exploratory archive-bootstrap CI is [−1.66, 2.25] — covers zero. Their own HIZ
report (§1, §3) states this plainly: "ölçek dengelemenin eski asym üzerine ek
kalite kazancı burada küçük ve belirsizdir." The PerLTQA story is therefore:
qscale's +4.24 pp over Hamming was ALREADY available via old asym (+4.43 pp
over Hamming: 80.19 vs 75.76); qscale itself trails old asym there by 0.19 pp.

## 4. LOCOMO ADAPTER / COHORT (VERIFIED from file; comparability flags are CLAIM)

Builder: `HIZ scripts/new_data.py:5-32`; record:
`results/locomo_adapter_before_scores.json` (written BEFORE scoring — good).
Cohort: 1986 total → 1531 kept; excluded 446 `adversarial_category5` + 4
`no_evidence` + 5 `invalid_or_unknown_evidence` (my count of the file; sums to
455 = 1986−1531). Policy (`new_data.py:32`): text-only
`[session timestamp] speaker: text`, no generated observations/summaries, no
answer in index; exact explicit evidence IDs, all must resolve; 4
semicolon/space-joined evidence strings normalized and logged
(`normalizations`, 4 entries). Order matters: category-5 check runs FIRST
(line 18), so a cat-5 question with empty evidence counts as cat-5.
Per-archive kept/docs: L00 150/419, L01 81/369, L02 152/663, L03 197/629,
L04 177/680, L05 123/675, L06 149/689, L07 191/681, L08 156/509, L09 155/568.

Non-comparability flags (all stated in their own report, §§3–5 — CLAIM here,
I did not re-run their encoder):
(a) text-only retrieval adaptation, NOT official LoCoMo answer-F1;
(b) 23% exclusion dominated by adversarial cat-5 — by design, but a different
population from "all LoCoMo questions";
(c) their own report: LoCoMo "was previously mentioned/tested in this project"
— transfer, NOT blind/hidden; plus their counter-review notes gold-label
content was never hand-checked;
(d) only 10 archive clusters → wide bootstrap CIs; exchangeability assumed,
not audited;
(e) per-archive encoder refit on LoCoMo texts (same protocol as other
benchmarks — this part IS comparable; `core.py:26-47`, seeds 5101/5204).

## 5. CLAIMS THAT CANNOT BE CHECKED FROM WHAT THEY SHIPPED

1. AVX-512 SIMD speedups (1.71–1.86× over float32 prepare+score; 1.60–2.02×
   slower than Hamming) — machine-bound (AMD EPYC 9V74, shared/virtualized
   cgroup, 8 warm rounds). Code ships (`kernels.c:41-64`); timings do not
   transfer. (CLAIM)
2. End-to-end text→top10 ms table (≈15.3/2.5/2.6 ms, "no 2× win") — same
   machine-bound status; 51 queries only. (CLAIM)
3. Memory: 3.504 MB codes+scales vs 99.75 MB float32 (≈28.47×) — arithmetic
   from shipped counts, but explicitly NOT total process RSS (their §6).
   (CLAIM as system fact; arithmetic not re-added here)
4. `validation_counts`: float32==float64 on all 6 metrics over 10,971 queries;
   258,720 transposed codes bit-identical; scalar/SIMD byte-identical —
   asserted in JSON, needs native rebuild + data to replay; not replayed here.
   (CLAIM)
5. DENETIM nDCG refutation (`check_ndcg_ties.py`, 302 cases / 5888 orders,
   quoted-formula max error 2.4) — script SHIPS so it is re-runnable, but I did
   not run it; and it tests the QUOTED formula, not the original `lib_b8.py`
   (their own §3 says the original was not executed). (CLAIM)
6. Raw-stage fidelity: 48 LME + 30 PerLTQA rebuilt, 0 sign-bit changes, 249,390
   scalar checks 0 mismatches — RealTalk raw explicitly NOT rebuilt (their
   scope note). (CLAIM beyond the shipped CSVs)
7. LITERATUR oracle-selection bounds (`complementarity.json`: e.g. LME
   hindsight max 90.21) — post-hoc gold-using upper bounds, not a method; no
   rerun involved by construction. (CLAIM, correctly labeled by producer as
   NOT_NEW_MODEL_PERFORMANCE)
8. Anything about PerLTQA en_v1/zh transfer — explicitly NOT tested (their HIZ
   §7). Gap, not a claim.
9. Absolute AVX-512 numbers must not be cited against other CPUs — producer
   states scalar fallback exists with no speed claim. (RELAYED caution — heed)

## GAPS (file missing or unreadable — contents NOT invented)

- `prior_benchmark/.../data/` and `prior_diagnosis` caches are NOT shipped
  (only `build_selection.json`/`restore_receipt.json` configs); their scripts
  expect a `data/` tree that is absent, so their pipeline is not re-runnable
  from the shipment alone. (VERIFIED absent — my probe v1 failed on it before
  I pointed at the real caches.)
- No blind/hidden test anywhere; all parties declare pilot status. (VERIFIED
  from their tags, present in every JSON.)
- DENETIM §5.7 storage-label ambiguity (sign88 11 B vs listed budget) left
  unresolved by its own author. (CLAIM of ambiguity — relaying their caveat.)
