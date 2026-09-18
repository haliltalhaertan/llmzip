[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# CODE_REVIEW.md — adversarial review of the coordinator's scripts

Read AFTER my own numbers were frozen (MY_NUMBERS.md). All blobs read via
`git show 557fc1e:research_f1_execution_2026_09_14/<path>`; verbatim copies in `coord_copy/`.
Locators are `file:line` in those copies, which are byte-identical to the blobs.

I worked through the specific checklist I was given, plus what I found on my own.

---

## The checklist I was asked to run

### 1. Does anything re-center already-centered data? — NO (clean)
`coord_f1_real_fr3.py:47-50` and `coord_frozen_repl.py:34-38` use `C` as loaded:
`D0 = C >= 0`, cosine on the raw cached `C`. No mean subtraction anywhere in either file
(VERIFIED: `grep -n 'mean' coord_f1_real_fr3.py` returns only `col_mean_squares` usage via the
module). `f1_competition.py:37-49` computes `v_j = mean_i(C_ij^2)` — that is the contract's
variance proxy, **not** a centering step, and it is correct.
I independently measured the caches ARE already centered (max |column mean| = 7.1e-16 LME,
4.4e-16 PerLTQA, 7.7e-16 REALTALK — MY_NUMBERS.md). Erratum E1 is genuinely fixed. VERIFIED.

### 2. Is the tie expectation formula correct, and does it match NT=20 in expectation? — FORMULA CORRECT, but see F-3
`coord_f1_real_fr3.py:32-42`:
```
thr = sort(s)[::-1][K-1]; strictly = #{s > thr}; slots = K - strictly; bc = #{s == thr}
E[FR] = (g_strict + g_tied * slots/bc) / |gold|
```
This is the exact expectation of `|gold ∩ topK|/|gold|` when the `bc` tied items compete uniformly
for `slots` remaining places: each tied item enters the top-K with probability `slots/bc`, and
expectation is linear, so no independence assumption is needed. Algebraically correct. VERIFIED by
derivation and by a 20 000-permutation Monte-Carlo check on 60 real LME queries
(`evidence/gate_and_mutations.json:tie_formula_vs_20000_perms`).

It matches the frozen NT=20 rule **in expectation only**. It is not the same estimator — see F-3.

### 3. Is the TOP/BOT axis-ordering rule right? — YES (clean)
`f1_competition.py:63-64`: `order = sorted(range(len(v)), key=lambda j: -v[j])`, `order[:k]` TOP,
`order[-k:]` BOT. Python's `sorted` is stable, so this is the contract's "stable descending" reading.
The docstring at `:60-62` correctly notes TOP64/BOT64 overlap in 32 axes by construction (first-64
and last-64 of 96) — that is the contract's literal instruction and he did not silently "fix" it.
I confirmed the frozen scorer's `C.var(axis=0)` coincides with `mean(C**2)` on centered data, and
that **0 of 480 archives have tied `v_j`**, so no ordering ambiguity is live. VERIFIED.

### 4. Is the average-rank Spearman tie handling correct? — YES (clean)
`f1_competition.py:155-193`. 1-based average ranks, ties averaged over the tied block
(`avg = (pos+1 + end+1)/2`), Pearson on ranks, `None` when a rank vector is constant.
This matches `scipy.stats.rankdata(method='average')` + `corrcoef`, which is what the auditor used.
My independent numpy implementation agrees bit-for-bit on all six coefficients. VERIFIED.
Minor: non-finite pairs are *dropped* (`:178-180`) rather than failing loudly. On this data no
Delta or gap is non-finite, so it never fires — but a silent drop is a latent hazard (see O-2).

### 5. Does the cluster bootstrap resample the correct level, and handle a missing cluster id? — YES (clean)
`f1_competition.py:247-251`: rows are grouped by `r.get("cluster")`, and a row with `cluster=None`
becomes its own singleton cluster `"__q_%d" % idx`. That is the sane handling and it matches the
contract's "LME's one-query-per-archive surface reduces to query/archive resampling".
Cluster assignment at the call site (`coord_f1_real_fr3.py`) is correct per benchmark:
LME `cluster=qid` (:77, one query per archive — correct), PerLTQA `cluster=rec["char"]` (:95,
archive — correct), REALTALK `cluster=d.get("chat_no")` (:110, conversation — correct).
Seed 96013, B=2000, percentile 2.5/97.5, full attempted/valid/invalid ledger with reasons
(`:273-277`) — all contract C8 requirements present. 2000/2000 valid on all three benchmarks,
matching my independent bootstrap. VERIFIED.
Minor: percentile is a nearest-index pick (`:268-269`) not an interpolated quantile, so his
intervals differ from mine in the 3rd decimal (e.g. LME strict his `[0.0561, 0.2221]` vs mine
`[0.0624, 0.2252]`). Both are legitimate percentile conventions and both are labelled
descriptive/post-hoc. Not a defect; noted for transparency (O-3).

### 6. Does any decision path use a float tolerance where exact comparison is required? — NO (clean)
The competition counts at `f1_competition.py:109-116` use bare `<` and `==` on Hamming distances.
Those are Python `int`s (built by `sum(1 for ...)` at `:72-73`), so `==` is **exact integer
equality** — correct, and the only place where exactness is load-bearing. The `efr` threshold
comparisons (`coord_f1_real_fr3.py:37-41`) use `==` on float scores, which is also the frozen
scorer's own convention (`step2_eval.py` uses `np.sum(base == s3)`), so it is faithful rather than
sloppy. No tolerance is used in any decision path that requires exactness. VERIFIED.

### 7. Does the min-gold control actually implement the bug it claims to demonstrate? — YES (clean)
`f1_competition.py:121-123`: `dmin = min(d[g] for g in G)`, then counts over **all** rows once
(`min_s`, `min_t`), with no per-gold averaging. That is exactly the behaviour the auditor's F1
describes ("collapse all gold rows to dmin=min(distance[gold]) and count once") and exactly what
the auditor's own `competition_variants.py:metrics()` computes as `min_all_strict/min_all_tie`.
It is wired through as a separate key (`min_strict_gap`/`min_tie_gap`, `:136`) and summarised via
`benchmark_summary(rows, strict_key="min_strict_gap", ...)` (`coord_f1_real_fr3.py:124`) — it does
not contaminate the primary. My independent min-gold reimplementation reproduces his three values
bit-for-bit (LME `0.09920150310037373`, PerLTQA `0.2774184734053319`, REALTALK `0.061255512317713624`).
The control is real, not a no-op. Mutation M4/M5 confirm it is load-bearing. VERIFIED.

### 8. Are the manifest and input inventory complete and honest? — SUBSTANTIALLY YES (one gap, F-4)
- `evidence/INPUT_CACHES.sha256`: 482 lines = 470 LME + 10 RT + 2 PerLTQA. Matches exactly the
  files the run actually opened. VERIFIED by count and by cross-checking the load paths in
  `coord_f1_real_fr3.py:71,84-89,102`.
- Archive-level identity: he does **not** claim a pin match. `CACHE_INVENTORY.md` states
  "Contract-pinned inputs (all ABSENT here)", lists all three tarball sha256 pins with
  `present? NO`, and concludes "A byte-identical real-data regeneration is IMPOSSIBLE in this
  environment". README:46 repeats it. This is exactly the honesty my brief asked me to check for,
  and it is present. VERIFIED — **credit where due.**
- LoCoMo: README:44 "No committed per-query float surface; that benchmark was not run", and
  `evidence/f1_results_fr3.json` carries the same note. Honest. I independently confirmed the
  LoCoMo pkls carry no per-query float retrieval surface. VERIFIED.
- Gap: the inventory covers the three benchmarks run but **contains no entry, and no explicit
  "not used" statement, for `drive/audit_layer/conv_*.json`** (the LoCoMo evidence maps). Minor,
  since LoCoMo was not run — but the contract's C9 asks for an exact input inventory and an
  unlisted-but-present input class is a small completeness gap. See F-4.

---

## Findings

### F-1 (MEDIUM) — the contract's own 1e-12 acceptance test was never executed
The contract states the six targets at full precision "tolerance `1e-12`". The coordinator's own
`CONTRACT_CHECKLIST.md` C7 restates them correctly (`0.14168629605302735`, …). But the execution
script hardcodes **rounded** constants:
`coord_f1_real_fr3.py:116` → `AUD = {"LME": (0.1417, 0.1405), ...}`.
Every `diff_strict`/`diff_tie` in `evidence/f1_results_fr3.json` is therefore a difference against
a 4-dp display value, and the contract's actual acceptance criterion is never evaluated anywhere in
the run. Against the real targets all six coefficients **fail 1e-12** by 4.9e-06 … 2.6e-04
(COMPARISON.md §2).

Mitigating, and I want to be fair about it: the README does **not** overclaim in prose. It says
"reproduced all six published auditor coefficients **to rounding**", labels the column
"auditor (4 dp)", prints every diff, and keeps F1 **OPEN**. So this is an *incomplete test*, not a
misrepresentation. The defect is that the tightest available check was skipped, in a project whose
stated rule is that self-declared correctness must be attacked.

### F-2 (MEDIUM–HIGH) — contract gate C3 was never applied; had it run, two benchmarks would have STOPPED
The contract requires the headline gates to reproduce to <=1e-12 **before** Claim-D computation, and
the spec is explicit: "A failed gate stops that benchmark."
`f1_competition.py:222-233` implements exactly this (`check_headline_gates(..., tol=1e-12)`).
**It is never called.** `grep -n 'check_headline_gates' coord_f1_real_fr3.py` → no match; the only
reference to the frozen headline values in the execution path is `FROZEN` at `:118`, used for a
*printed diff*, never for a pass/fail branch.

Applying the gate myself with my own measured headlines (`evidence/gate_and_mutations.json`):

| benchmark | SIGN measured vs gate | FLOAT measured vs gate | C3 gate |
|---|---|---|---|
| LME | 0.5421335697 vs 0.5419751773 → \|d\|=1.58e-04 | \|d\|=0 | **FAIL** |
| REALTALK | 0.2255348231 vs 0.2247750760 → \|d\|=7.60e-04 | \|d\|=2.8e-17 | **FAIL** |
| PerLTQA | 0.4889447962 vs 0.4889419949 → \|d\|=2.80e-06 | \|d\|=0 | **FAIL** |

All three fail C3 at 1e-12. Under a literal reading of the contract + spec, the Claim-D computation
should not have proceeded on any benchmark. The failure is *benign in origin* — it is the same
NT=20-vs-exact-expectation substitution as F-3, not a data error — but the governance point stands:
a frozen gate that exists in the package was bypassed, and bypassing it is what allowed the
substitution in F-3 to go unpriced.

### F-3 (MEDIUM) — the exact-expectation substitution is a deviation from the frozen convention and is under-disclosed
The frozen convention is the NT=20 seeded-permutation average (`step2_eval.py:8`, and REALTALK's
`details.json` protocol string pins `tie_seed=5_100_000+ci*100_000+t*100+99`). The coordinator
substituted the exact expectation (`coord_f1_real_fr3.py:8-9`). ERRATA_COORDINATOR.md discloses the
substitution and argues the residual "is consistent with sampling noise in the reference", citing
that the residual is smallest on the largest sample. That reasoning is sound as far as it goes, and
I independently confirm the direction.

What is missing is the **magnitude**. I measured the seed-to-seed spread of the frozen NT=20
estimator directly (six seed families, `evidence/perm_diagnosis.json`): LME strict ranges
`0.14110`–`0.14377`, i.e. a spread of **2.7e-03** — roughly nine orders of magnitude above the
contract's 1e-12 tolerance, and an order of magnitude larger than any discrepancy under discussion.
The auditor's published targets sit **inside** that spread for 3 of 4 measured arms.

The correct disclosure is therefore stronger than the one given: *the frozen NT=20 convention cannot
support a 1e-12 reproduction claim by anyone, and the contract's 1e-12 tolerance is only meaningful
against the auditor's exact stored row file.* That file — `INDEPENDENT_QUERY_ROWS.json` — is
**not in any readable branch** (it lived under `/mnt/data/e1v2_raw_audit/`, off this machine).
The coordinator's `CACHE_INVENTORY.md` does note this file is absent; it does not connect that
absence to the impossibility of the 1e-12 claim.

### F-4 (LOW) — Delta_q was recomputed where the contract says to reuse the frozen surface
Contract, Inputs: "Use the exact per-query `Delta_q` … **from the recovered/frozen evaluation
surface**." The auditor obeyed literally (`competition_variants.py` loads stored `delta`).
The coordinator recomputes Delta_q from caches (`coord_f1_real_fr3.py:45-51,59`). I did too — so I
am not privileged here — but the contract wording favours the auditor's reading.
Evidence this matters: swapping **only** the Delta source to the committed frozen REALTALK surface
moves the coefficients from 2.6e-04 off-target to **2.9e-07** off-target, a ~1000× improvement
(COMPARISON.md §4c). Recomputation is the dominant residual term.

### F-5 (LOW) — input inventory omits an input class
`evidence/INPUT_CACHES.sha256` has 0 entries matching `locomo` or `drive` (VERIFIED by grep).
`drive/audit_layer/conv_*.json` and `regen/locomo/*.pkl` are present on disk and are contract-relevant
(the LoCoMo leg). They were correctly not *used*, but C9 asks for an exact input inventory; an
explicit "present, not used, reason" line would close this. Cosmetic.

---

## Observations (not defects)

- **O-1.** `f1_competition.py` is genuinely spec-derived, pure stdlib, with no import of any
  lead/auditor module (`:7-9`), and `_unique_gold` (`:77-83`) range-checks gold indices and raises on
  an empty gold set rather than silently skipping. Good defensive practice.
- **O-2.** `spearman_rho` silently drops non-finite pairs (`:178-180`). Never fires on this data
  (I checked: no non-finite Delta or gap on any of the 9 440 rows). Latent hazard only.
- **O-3.** Bootstrap percentile is a nearest-index pick, not an interpolated quantile (`:268-269`).
  A legitimate convention; explains 3rd-decimal CI differences from my run. Both labelled descriptive.
- **O-4.** The superseded wrong scripts are preserved under `coordinator/superseded/` with the
  errata rather than deleted, and the retracted "AQS wins at large N" claim is explicitly withdrawn.
  This is the behaviour the project's governance asks for and it is present.
- **O-5.** README keeps F1 **OPEN** and lists three limitations (not independent, LoCoMo absent,
  archive identity unverifiable) without prompting. The self-assessment is more conservative than
  the brief I was given suggested.

## What I could NOT check
- Archive-level sha256 identity of the three pinned tarballs — only extracted trees exist here.
  I confirm the coordinator makes no pin-match claim.
- The auditor's `INDEPENDENT_QUERY_ROWS.json` — not committed anywhere I can read. This is the
  single artefact that would settle the 1e-12 question, and its absence is why F-1/F-3 cannot be
  resolved to PASS by anyone in this environment.
- The LoCoMo leg — no per-query float surface; I independently confirm it cannot be run here.
