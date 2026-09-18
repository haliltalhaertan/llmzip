[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# LEAK_PERLTQA — does the projection leak on PerLTQA too?

## (1) VERDICT

Yes. On all 30 PerLTQA archives (8265 queries) the honest projector loses
~19-23 pp vs the published test-fitted one: sym Hit@10 75.68 -> 52.85 and
qscale Hit@10 80.00 -> 58.83, archive-clustered bootstrap CI95 excludes zero
in all 4 cells. The collapse is real but SMALLER than RealTalk's ~28-30 pp.
Gate is clean: my rebuild matches production bit-for-bit (0/1,179,648 doc,
0/793,440 query signs), so the leak number is validated, not a rebuild bug.

## (2) Findings

| ID | Sev | Claim audited | Outcome |
|----|-----|---------------|---------|
| F1 | CRITICAL | PerLTQA Hit@10 honest | Inflated ~21-23 pp |
| F2 | HIGH | Rebuild validity gate | Clean bit-for-bit pass |
| F3 | MED | Leak vs archive size | Weak positive, n.s. |
| F4 | LOW | Contrast purity | Pure fitting effect |

- **F1**: pooled TRANS->INDEP: sym Hit@10 -22.83 pp [20.61,25.14], qscale
  Hit@10 -21.17 pp [18.81,23.66], sym FR@3 -19.75 pp, qscale FR@3 -18.21 pp;
  all 30/30 archives drop (min +8.9 pp, max +35.6 pp). Smaller than RealTalk.
- **F2**: G1 0/1,179,648 doc sign diffs; new G1b 0/793,440 query sign diffs;
  TRANS==published per-archive FULL to 0.00e+00; G2 replay exact (80.00/75.68).
- **F3**: leak-vs-N Pearson +0.13..+0.29, all p>0.12; no negative trend, unlike
  rotation-damage r=-0.78; 8 sub-384 archives leak +13..+26 pp.
- **F4**: scorers, sigma source, tie-breaks identical across arms; only the
  fit set differs (own archive vs pooled other 29). Design is fully inductive.

## (3) Per-finding detail

### Pipeline found (task item A)

- Recipe source: `/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/step2_build.py`
  `fit_archive` (lines 54-65): TFIDF word(1,2)+char_wb(3,5) -> LSA32
  (`random_state=5101`) -> hstack -> SVD96 (`random_state=5204`) -> L2 ->
  mean-center -> C. Query path (lines 140-149): same fitted
  `(wv, cv, svd, s96, mu)` transforms the question text.
- PerLTQA re-implementation audited:
  `top10_comparison_r1/ablation_r2/perltqa/fidelity_gate.py` (lines 70-83),
  `ablation.py` (lines 140-168, scoring 176-200). Both fit vectorizers, LSA
  and SVD96 **on the evaluated archive's own item texts** — same transductive
  structure round 2 convicted on RealTalk. Scorers (`ablation.py` lines
  180-184): `sym=-Hamming`, `qscale=Dpm@(QC/sigma)`, sigma=std of doc C.
- Published anchors (`REPORT.md` lines 11-14, `RESULTS.json` aggregate):
  FULL sym Hit@10 75.6806%, qscale Hit@10 80.0000%, qscale FR@3 ~53.24%.

### F2 — production-identity gate (task item B)

- Ran: `~/muse-work/ml-python gate_perltqa.py` (in this dir; copies
  `build_items`+`fit_archive` verbatim, plus `collect_questions` from
  `ablation.py` lines 73-88). Reads only raw jsons + `cache_arch_eval.pkl` /
  `cache_q_eval.pkl`; writes `GATE_REBUILD.json` here.
- Observed output (all 30 archives `diffbits=0`, `maxabs=0.000e+00`):
  - G1 doc signs: **0 / 1,179,648** (target 0/1,179,648 from REPORT.md line 10)
  - G1b query signs (new — covers the query path the TRANS arm depends on):
    **0 / 793,440**, max abs diff 0.0
  - G2 replay from cached C/qC: sym Hit@10 75.6806, qscale Hit@10 80.0000,
    qscale FR@3 53.2375 — all targets met -> **GATE PASS**.
- Conclusion: gate reached the round-2 bar (their 0/858,624 bits) and more
  (query side too). Proceeding to the leak measurement was legitimate.

### F1 — honest (inductive) measurement (task items C, D)

- Ran: `~/muse-work/ml-python inductive_perltqa.py 0 1` (24 s timing probe),
  then `inductive_perltqa.py 1 30` (~11 min). Method mirrors round-2
  `audit_hard_r2/ROUND_B_8roles_1318/code/t_inductive_all10.py` lines 30-64:
  TRANS fits on held-out archive texts; INDEP fits on pooled texts of the
  other 29 archives (~11.8k docs); both encode held-out docs+questions;
  sigma from held-out C under that arm; `abl.det_top10` + `abl.hrn`.
  Writes `INDUCTIVE_PERLTQA.json` (incremental, per-query binaries kept).
- All 30 archives done (requirement was >=6). Per-archive TRANS gate inside
  the run: doc sign diffs 0, query sign diffs 0, max|TRANS-published FULL|
  = 0.00e+00 on every archive (see `ANALYSIS.json`).
- Pooled results, 8265 queries (`analyze_inductive.py`; paired
  archive-clustered bootstrap, multinomial-30, 20000 reps, seed 20260916,
  same design as `ablation.py` lines 230-252):

```
sym Hit@10:    TRANS=75.68  INDEP=52.85  leak +22.83 pp CI95 [+20.61,+25.14] SIG
qscale Hit@10: TRANS=80.00  INDEP=58.83  leak +21.17 pp CI95 [+18.81,+23.66] SIG
sym FR@3:      TRANS=49.09  INDEP=29.35  leak +19.75 pp CI95 [+18.15,+21.41] SIG
qscale FR@3:   TRANS=53.24  INDEP=35.03  leak +18.21 pp CI95 [+16.77,+19.66] SIG
```

- Replication verdict: the collapse replicates (CIs far from zero, 30/30
  archives same direction). It is SMALLER than RealTalk k=96
  (sym -28.37 CI95 [21.76,35.03]; qscale -29.65 CI95 [23.06,37.07]): sym CIs
  overlap at the edges, qscale CIs barely touch. In relative terms PerLTQA
  INDEP retains ~70% (52.85/75.68) and ~74% (58.83/80.00) of TRANS, vs
  RealTalk's ~39-40% — so the PerLTQA projector degrades more gracefully,
  consistent with its larger, more diverse fit sets (median N=407 docs).
- Per-archive leaks (pp, TRANS-INDEP; full table in `ANALYSIS.json` run
  output): max Zhang Xiaohong symH10 +35.64 / Zhao Li qH10 +34.73; min Zhou
  Ting qH10 +8.88 / Tayo qFR3 +10.80. No archive escapes; range is wide
  (~9-36 pp), so single-archive spot checks would mislead.

### F3 — leak size vs archive size (task item E)

- N range 293-546, median 407 (matches brief); 8 archives <384 confirmed:
  N = 293, 343, 359, 371, 376, 377, 380, 381.
- Leak-vs-N (scipy.stats, n=30): symH10 Pearson +0.286 p=0.125 / Spearman
  +0.256 p=0.172; symFR3 +0.184 p=0.332; qH10 +0.243 p=0.196; qFR3 +0.126
  p=0.508. All weak-positive, none significant.
- Interaction with known rotation-damage r=-0.78: NOT mirrored — the leak
  does not shrink with archive size; if anything it grows slightly, and the
  8 smallest archives still leak +13..+26 pp (symH10). Small-archive results
  are not spared by the leak; a size-based excuse for PerLTQA is unsupported.

### F4 — contrast purity (method note, LOW)

- Identical across arms: scorer formulas, sigma-from-held-out-C convention
  (same as round 2), deterministic tie-break `top10-r1|archive|row`
  (verified equivalent to `abl.det_top10` in `ablation.py` lines 115-127),
  question strings, gold sets. The ONLY difference is the fit set, so the
  ~21 pp contrast is a pure test-fitting effect, not a scoring artefact.
- Background = all other 29 archives pooled (11,829-11,995 docs depending on
  held-out) — strictly inductive, harsher than any deployment that could reuse
  same-domain data, matching round 2's leave-one-archive-out choice.

## (4) What you could NOT check and why

- Other widths (k=48/192, t3_ladder.py ladder): probe ran k=96/FULL-arm only;
  each extra width x 30 backgrounds costs ~12 min. Sampling one width was a
  time-box choice, stated here, not a cleanliness claim.
- WORD_ONLY/NO_CHAR/NO_LSA arms under INDEP: unknown whether channel-ablation
  contrasts (REPORT.md's refuted-LSA verdict) survive honest fitting. The
  absolute-level inflation poisons cross-arm comparisons only if arms leak
  differentially — untested, would need 3x compute.
- asym scorer, ITQ rotation, LoCoMo/LME datasets: out of this role's scope;
  untouched (no sampling claim made about them).
- BM25 comparison on PerLTQA: the +10.35 fair-BM25 correction is RealTalk-only
  (known limitation); INDEP 58.83 (qscale Hit@10) vs any PerLTQA BM25 is
  UNVERIFIED — needs a PerLTQA BM25 run I did not do.
- Statistical detail: per-archive CIs and two-sided cluster p-values not
  computed (pooled CI suffices for the replication question); leak-vs-N
  p-values are uncorrected for 4 comparisons (all n.s. anyway).
- Read-only compliance: every command against
  `top10_comparison_r1/`, `_wt_top10/`, `audit_hard_r1/`, `audit_hard_r2/`,
  `bench3/` was a read (import, pickle/json load); all writes
  (`gate_perltqa.py`, `GATE_REBUILD.json`, `inductive_perltqa.py`,
  `INDUCTIVE_PERLTQA.json`, `analyze_inductive.py`, `ANALYSIS.json`,
  `NOTES.md`, this file) are inside this directory. No prior audit text was
  re-reported as new; round-2 numbers above are quoted as the comparison
  baseline, not as my measurements.

## Reproduce

```
cd /mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r3/leak_perltqa
~/muse-work/ml-python gate_perltqa.py          # ~100 s, expect GATE PASS
~/muse-work/ml-python inductive_perltqa.py 0 30  # ~12 min, incremental JSON
~/muse-work/ml-python analyze_inductive.py      # pooled + CI + correlation
```
