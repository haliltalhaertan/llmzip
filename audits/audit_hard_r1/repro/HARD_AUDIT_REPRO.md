# HARD_AUDIT_REPRO — [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Audit question: can a stranger reproduce the same results from the published package alone?
Workspace (own, writable): `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r1/repro`
Published package (READ ONLY): `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/`
Git worktree (READ ONLY, no commit): `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10`
Raw data/caches (READ ONLY): `/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/`, `/mnt/c/Users/MDP/dev/llmzip-work/bench3/`
Python: `~/muse-work/ml-python` (= `/usr/bin/python3` + `fpylibs:mlpy`), `PYTHONDONTWRITEBYTECODE=1`, per-probe cap 180 s.
Rule: NO-ARTIFACT — anything not executed is `NOT RUN`. No invented numbers.

## 0. Status ledger (append as you go)
- [x] Report file created first (this file), stepwise append rule in force.
- [x] §1 inventory (main repo + research root + refs)
- [x] §2 contracts + hardcoded-path table (read-only grep)
- [x] §3 decision_tests T1 isolated run (RAN 4 s, 20/20 cells identical)
- [x] §4 t3_ladder 2-archive run + cell-by-cell vs T3_PERLTQA_KLTN.json (RAN, direction match)
- [x] §5 data-path dependency list (all EXIST on this machine; all OUTSIDE package)
- [x] §6 fidelity k=96 cache bit-identity (probe 0/61056; full 8-arch NOT RUN)
- [x] §7 core harness/contracts sample + 8 challenge items
- [x] §8 coverage ledger + severity ranking

## 7. Core harness/contracts sample + mandated challenge items

Sampled (read-only unless noted): `audit_baseline_lib.py` (140 lines — `det_top10`
salt `top10-r1`, descending score → sha → row; `hrn` hit/recall/nDCG; `expected_*`
tie-expectations; my RT01 replica matches it exactly); main-repo `tools/` (seal
verifier + `test_verify_preregistration_seal.py`: 0 pytest tests, but direct execution
gives 38/38 negative controls BLOCK-correct, exit 0 — unrelated area, recorded as the
only executable repo test artifact); `adapters/` (2 longmemeval adapters, named only);
F1 execution code (`task4f1_*`, `research_f1_execution_2026_09_14/`: named only).
NOT REVIEWED: all F1/audit_v52/task4f1 internals, LME ablation internals (live job —
untouched per rule), semantic/PPLX arms, `lit_r2` maps beyond existence, full T2
recomputation, full ladder.py rerun, `coordinator/t3_perltqa_kltn.py` end-to-end.

1. **sym/σ.** CHALLENGE SUSTAINED (mechanism scope). `sym = sign(C)@sign(QC)` contains
   no σ anywhere (`t3_ladder.py:186-188`); I verified `sign(C/σ)==sign(C)` exactly
   (0/28128 differ on cached Kong C) — so σ-division CANNOT explain the sym 192→384
   decline (−5.17 published, −5.26 probe), which is the LARGEST of the three. The
   "tiny-σ" mechanism covers qscale only. The decline-persists FACT replicates; its
   CAUSAL explanation is incomplete. A trailing-noise-dims story would cover both arms
   but no such evidence is in the package (my hypothesis, not a finding).
2. **Rank-overflow correction.** Confirmed dead, retraction proper: probe shows 0
   constant dims with decline persisting. No causal replacement is established (see 1).
3. **Rerank vs candidate recall.** CAVEAT. T2's `*_bm25` arms rerank top-50 first-stage
   candidates (`actual_candidates=50` for every code arm, 164,256 rows audited) while
   `BM25_full` scores the full corpus (mean ~493–602 docs). DECISION_TESTS.md never
   mentions candidate depth; the depth-50-vs-full-corpus asymmetry is undisclosed
   there (REPORT's oracle section does disclose reachability: 172/705 RealTalk queries
   unreachable outside top-100). T2 numbers not recomputed (NOT RUN); the
   "optimizing the first stage is pointless" reading overreaches — recall@50 still
   gates every reranked arm.
4. **BM25 needs raw text.** PARTLY SUSTAINED (wording). BM25 scoring needs the index
   (670,511 B row, honestly separated); raw text at query time serves the reranker /
   display, not the scorer. The cost table itself is honest (index vs index+text rows);
   only the "needs ... raw text at query time" phrasing (FINAL_STATE §One thing)
   overcharges BM25. The pickle-inflation warning (12.6× artifact) is good practice.
5. **RealTalk-only delta generalized.** SUSTAINED. T1 measured the +10.35 pp
   tokenizer+params effect on RealTalk only, yet DECISION_TESTS.md:116-117 directs
   "Every comparison table in this programme's history needs the −10.35 pp correction"
   — applied to benchmarks where no such measurement exists. Per-benchmark fair-BM25
   measurement is missing; the correction as a universal constant is unsupported.
6. **Best-of-4 selection on seen gold.** SUSTAINED as bias, verdict ROBUST. Own
   per-archive recomputation: global winner `frozen_idfonly` wins only 6/10 archives
   (`frozen_textbook` 2, `coarse_idfonly` 2). The natural no-selection comparator
   (`frozen_textbook`: fair tokenizer + textbook params, 61.70) trails the selected
   65.67 by 3.97 pp — the "7.80 pp behind / +10.35 handicap" headlines are
   selection-inflated by ~4 pp. C1 still FAILs under either comparator (48 B code
   trails even unselected BM25), so STOP's direction does not depend on it.
7. **STOP as closure / pre-registration.** MIXED. STOP is branch-honest: FINAL_STATE
   states branch + `main` untouched + "merge is the owner's call"; nothing shows
   owner approval, so quoting STOP as a project decision would be misrepresentation
   (none found in-package). Pre-registration is UNVERIFIABLE: REFEREE.md gates and
   DECISION_TESTS.json both enter git in the single commit `8bcdef5` (same day) —
   commit history cannot show gates predated results (consistent with the mandate:
   mtimes/snapshots don't establish pre-registration; nor do they prove movement —
   recorded as unknown). Bonus gap: T1's coded C1 check is point-only (`>=2.0`,
   `decision_tests.py:190-191`) while the prespecified gate requires CI-excluding-0;
   moot for this FAIL (−7.80 pp) but the implementation does not match its gate text.
8. **Literature absence vs novelty.** CAVEAT. The six "genuinely ours" items rest on
   "scanned literature" with no search protocol/query list/corpus in the sampled docs
   (`lit_r2/` existence only); absence is not proof. REPORT §7's own "unmeasured in
   the literature — neither confirmed nor refuted" is the honest framing; the
   FINAL_STATE "nothing covers these" headline overstates it. No numeric anchor was
   inherited without checking: every quoted cell above was re-read from the JSONs,
   with metric (Hit@10/FR@3) and cohort (n=705 / n=2217 / n=539) stated.

LoCoMo dispute handling is a bright spot: contradictory gold (n=1531 vs 1535, 156
unapplied corrections) is disclosed in FINAL_STATE, REPORT §7, and REFEREE Q8, and
the C3 gate's only pass (disputed-gold LoCoMo) is flagged rather than banked.

## 8. Coverage ledger + severity ranking

| area | status | evidence |
|---|---|---|
| T1 isolated rerun + cell compare | RAN — 20/20 identical | §3 |
| T1 independent RT01 reimplementation | RAN — exact match | §3, `audit_rt01_own.py` |
| T3 2-archive rerun + direction compare | RAN — 9/9 arms + 3/3 delta signs | §4, `iso_t3/T3_2ARCH.json` |
| T3 fidelity gate (2 arch) | RAN — 0/61056 | §6 |
| T3 full 8-arch gate 0/276480 | NOT RUN (inherited) | §6 |
| T3 multi-seed (2 arch × 3 seeds) | RAN — direction robust, Kong unstable | §4, `seed_sens_*.json` |
| T2 rerank recomputation | NOT RUN (metadata only) | §7.3 |
| ladder.py full rerun | NOT RUN (hours; k=768 documented-timeout) | §5 |
| coordinator/t3_perltqa_kltn.py e2e | NOT RUN (interface exists) | §4 |
| Package-only execution errors | NOT RUN in place (rule); path-audit instead | §5 |
| Repo seal controls | RAN — 38/38 (unrelated area) | §7 |
| F1/KV/inverse, adapters, LME live job, lit maps | NOT REVIEWED (named) | §7 |

Severity-ranked findings (evidence, not a verdict on the programme):
1. HIGH (reproducibility): package alone reproduces nothing — all scripts hard-code
   absolute machine paths outside the package; no setup docs. On this machine
   everything probed runs; anywhere else, nothing does. Fix: path parametrization +
   one SETUP.md + manifest of external inputs.
2. MEDIUM (mechanism): σ-division does not explain the sym decline (largest delta);
   the "real mechanism" is partial. Fix: either evidence for trailing-noise (or
   other) covering sym, or downgrade to "qscale mechanism; sym unexplained".
3. MEDIUM (generality): −10.35 pp correction prescribed programme-wide from a
   RealTalk-only measurement; best-of-4 selection inflates headlines ~4 pp. Fix:
   per-benchmark fair-BM25 + preselected comparator. Verdict direction unaffected.
4. MEDIUM (interpretation): T2's top-50 funnel vs full-corpus BM25 undisclosed in
   DECISION_TESTS.md; recall@50 still gates. Fix: one-sentence disclosure + a
   depth-matched contrast.
5. LOW-MEDIUM (process): gates+results share one commit → prespecification
   unverifiable; T1 C1 check omits the prespecified CI. Fix: separate gate/results
   commits next round; add bootstrap to T1.
6. LOW (wording): "BM25 needs raw text at query time"; "nothing in the literature".
   Both already hedged elsewhere in the package; tighten the two headline sentences.

Bottom line: the two recomputable claims I tested (T1 numbers exactly; T3 shape,
gate mechanism, and retraction direction on a 2-archive probe) REPRODUCE on this
machine from isolated copies with redirected outputs. The STOP direction survives my
two bias corrections (selection, funnel). What does not survive is stronger:
package-only reproducibility (fails), the σ-mechanism as a complete explanation
(sym contradicts it), and the universal −10.35 pp correction. Nothing above was
committed, pushed, or written outside the own dir; sources/caches read-only;
LME job untouched; each probe ran in seconds, none near the 180 s cap.

## 3. decision_tests.py T1 — RAN (isolated copy, T1 only)

Adaptations (documented): copied `coordinator/decision_tests.py` + `LADDER.json` into
own `iso_t1/`; ran ONLY `t1()` via own `run_t1_only.py` (the script's `__main__` would
also run T2 and overwrite `HERE/DECISION_TESTS.json` — in the package that would
destroy the published artifact; in the copy OUT resolves inside own dir).
`PYTHONDONTWRITEBYTECODE=1`. No source file touched. Wall time 4 s (no 180 s issue).
No crash, no missing file, no absolute-path failure on this machine.

Cell-by-cell vs published `DECISION_TESTS.json` T1 (own comparison, exact float diff):

| cell | published | rerun | diff |
|---|---|---|---|
| BM25 coarse_textbook Hit@10 / FR@3 | 55.3191 / 33.9054 | same | 0.00e+00 |
| BM25 frozen_textbook Hit@10 / FR@3 | 61.7021 / 36.0483 | same | 0.00e+00 |
| BM25 coarse_idfonly Hit@10 / FR@3 | 57.3050 / 34.0506 | same | 0.00e+00 |
| BM25 frozen_idfonly Hit@10 / FR@3 | 65.6738 / 40.0230 | same | 0.00e+00 |
| code 12B/24B/48B x sym/qscale, Hit@10 + FR@3 (12 cells) | — | — | all 0.00e+00 |
| strongest variant | frozen_idfonly | frozen_idfonly | match |
| C1 verdict | False (FAIL) | False (FAIL) | match |

20/20 cells bit-identical. T1 is deterministic (no RNG): rerun agreement is expected,
not a stress test — the value is that the code path from raw RT JSONs reproduces.

Own-code cross-check (`audit_rt01_own.py`, no import of coordinator or audit lib;
own tokenizer/BM25/tie-break from the documented contract, TIE_SALT `top10-r1`
confirmed in `audit_baseline_lib.py:30`): RT01 frozen_idfonly Hit@10 = 61.1765 (n=85)
in BOTH implementations, diff 0.00e+00. The T1 scoring pipeline is independently verified.

T2 (rerank, 164k CSV + 20000-rep bootstrap): NOT RUN (not requested; only metadata
inspected, see §7 item 3). Full `decision_tests.py` end-to-end: NOT RUN (would have
executed T2/T3 paths; T1-only was the bounded brief).

## 4. t3_ladder.py 2-archive probe — RAN (isolated copy, redirected output)

Adaptations (documented): copied `ablation_r2/perltqa/t3_ladder.py` into own `iso_t3/`;
restricted `small` to the 2 smallest archives (`Kong Tingting` n=293, `Zhu Xiaolong`
n=343); redirected the hardcoded absolute write (line 235, raw work dir) to
`iso_t3/T3_2ARCH.json`. All reads are absolute machine paths (Dataset JSONs, both
bench3 caches) — all EXIST, read-only. Wall time ~12 s. No crash. `fast_topk`
self-check: 30/30 match vs `lib.det_top10`.

Result (n=539 queries) vs published 8-archive aggregate (n=2217) — cohorts differ, so
this compares SHAPE/DIRECTION, not equality:

| arm | probe 2-arch Hit@10 / FR@3 | published 8-arch Hit@10 / FR@3 | same direction? |
|---|---|---|---|
| k96/sym | 80.89 / 51.07 | 78.12 / 51.69 | — (baseline) |
| k96/qscale | 81.63 / 56.68 | 81.33 / 56.38 | close |
| k96/asym | 80.33 / 56.58 | 81.87 / 57.09 | close |
| k192/sym | 78.85 / 55.13 | 77.94 / 53.88 | yes |
| k192/qscale | 84.42 / 59.12 | 82.18 / 57.71 | yes |
| k192/asym | 84.04 / 61.33 | 84.71 / 60.79 | yes |
| k384/sym | 75.88 / 49.88 | 74.65 / 48.71 | yes |
| k384/qscale | 81.82 / 56.49 | 79.70 / 54.11 | yes |
| k384/asym | 84.97 / 62.77 | 84.89 / 61.09 | yes |

Contested step 192→384 FR@3: probe sym −5.26 / qscale −2.63 / asym +1.44 vs published
sym −5.17 / qscale −3.60 / asym +0.30. All three SIGNS match: standardized arms fall,
unstandardized rises. `const_dims@384` = 0 on both probe archives — the rank-overflow
retraction replicates (decline persists with no constant dims).

Provenance note: package `T3_PERLTQA_KLTN.json` is byte-identical (sha256 `339fd9e6…`)
to raw-dir `top10_comparison_r1/coordinator/T3_PERLTQA_KLTN.json`, and its schema
(`arms[].n`, flat `gate{diff,bits}`) matches the ablation `t3_ladder.py` writer, NOT
the coordinator `t3_perltqa_kltn.py` writer (which would emit `n_queries`, `k_eff`,
per-archive gate). So this probe exercised the actual production path. The sibling
script `coordinator/t3_perltqa_kltn.py` (step2-builder interface) was NOT RUN
end-to-end; its imports (`build_items`/`fit_archive`) exist in step2_build.py
(verified read-only), but whether it reproduces the JSON is NOT RUN.

Multi-seed distribution (own `audit_seed_sens_own.py`, final-SVD seeds {5204,1,999},
LSA seed fixed 5101): query-weighted 2-archive 192→384 FR@3 deltas — sym
−5.25/−4.68/−2.78, qscale −2.63/−3.69/−2.21, asym +1.44/+1.48/+1.96. Direction robust
across seeds on this cohort. Caveat: single-archive deltas are seed-unstable —
Kong Tingting alone flips sign (qscale +1.33/−3.20/+1.57); Zhu Xiaolong is stable
(qscale −5.28/−4.02/−4.73). The published 8-archive single-seed aggregate has no
reported seed uncertainty; per-archive deltas at n≈200–300 should carry wide
intervals. Full 8-archive × multi-seed: NOT RUN (over the 180 s probe cap).

## 5. Data-path dependency list (all checked read-only; LME cache untouched)

| path read by probed scripts | exists? | inside package? |
|---|---|---|
| `top10_comparison_r1/data/RT{01..10}.json` (T1) | EXISTS | NO (raw work dir) |
| `top10_comparison_r1/audit/audit_baseline_lib.py` (T1/T3) | EXISTS | NO |
| `coordinator/LADDER.json` beside script (T1 code arms) | EXISTS | YES |
| `incoming_20260916b/.../text_rerank_per_query.csv` 164,256 rows (T2) | EXISTS | NO (external drop) |
| `bench3/PerLTQA/Dataset/en_v2/perltqa_en_v2.json` + `perltmem_en_v2.json` (T3) | EXIST | NO |
| `bench3/runs/b3b_perltqa/cache_{arch,q}_eval.pkl` (T3) | EXIST | NO |
| `bench3/runs/b3a_realtalk/rt_repr/RT*.pkl` (ladder.py) | EXIST | NO |
| `drive/v52_t4d_locomo_frozen_cross_benchmark.py` (ladder.py) | EXISTS | NO |
| `bench3/runs/b3b_perltqa/step2_build.py` (t3_perltqa_kltn.py) | EXISTS | NO |
| `model/` 2.4 GB weights (other arms) | NOT CHECKED | excluded by design (sha in MODEL_DOWNLOAD.json) |

Nothing was missing on THIS machine — but every read except `LADDER.json` resolves to
an absolute `/mnt/c/Users/MDP/dev/llmzip-work/...` path OUTSIDE the package. A stranger
with only the 45 MB package can run NONE of T1/T2/T3/ladder: all fail at the first
`open()` with `FileNotFoundError`. Broken-path verdict for package-only execution:
RAN-only-on-this-machine; exact in-package error text NOT captured (scripts were
deliberately never executed in place per source-protection rule — the failure point is
established by read-only path audit, i.e. `W = "/mnt/c/..."` prefixes + the table above).

Instructions sufficiency: FINAL_STATE Layout lists directories but gives no setup
procedure (no environment, install, path-remapping, hardware/time expectations; the
k=768 drop after a 3000 s timeout exists only as a code comment in ladder.py:56-62).
REPORT/DECISION_TESTS describe WHAT was run, not HOW to run it. PUBLICATION_VERIFY.md
covers package integrity (756 manifest entries, CRLF artifact, LME partial-run
disclosure — read, sound) — not reproducibility. A reader cannot set up these
experiments from the reports alone; the hidden dependencies are the entire absolute
path table above plus `~/muse-work/ml-python` (numpy/sklearn/scipy; no
sentence_transformers — T1/T3 probes confirm it is not needed for these two).

## 6. Fidelity gate k=96 — RAN on 2-archive probe; full gate NOT RUN

Probe: `FIDELITY GATE (k=96 vs cached): 0 differing of 61056 bits` (Kong Tingting +
Zhu Xiaolong, cached production C). Published full gate: 0 of 276480 bits over 8
archives — NOT re-verified (bounded probe; would need the full 8-archive run).
The gate comparison itself (`(C>=0) != (Cc>=0)`) is the bit-identity check the brief
claims; the probe confirms the mechanism works and passes on unseen-by-me archives,
but the 276480 number is inherited, not re-measured. No `sentence_transformers`
needed anywhere in T1/T3 paths (pure sklearn TF-IDF/SVD).

## 1. Inventory (READ-ONLY git commands, no checkout/fetch/commit)

Main repo `/mnt/c/Users/MDP/dev/llmzip`, checked-out branch
`findings/dense-mrl-parity-2026-09-14` @ `36c7bf0` ("Dense MRL channel measured").
Local branches include `findings/top10-comparison-2026-09-15` (the audited pilot),
`main` @ `59b891e`, plus `findings/f1-execution-*`, `hr/*`, `archive/*`, `mathpin`,
`muse-base-v9`, and several `agents/muse/ultra-*` remote-tracking refs (full list in
tool output; sampled, not exhaustively reviewed).
`git -C _wt_top10 status` fails from WSL because the worktree admin dir embeds a
Windows path (`.../.git/worktrees/_wt_top10/C:/Users/...`); ref evidence therefore comes
from the main repo: `git worktree list` shows `_wt_top10` prunable at `e672192`
("final(twelve-byte-pilot): complete state, verdict STOP"), and
`git log findings/top10-comparison-2026-09-15` shows the 5-commit stack
`c31719b audit -> a68fcdc retract -> 74e21e1 findings -> 8bcdef5 decision -> e672192 final`.
STOP originates from coordinator commit `8bcdef5`, on branch
`findings/top10-comparison-2026-09-15` only — nothing in the log shows owner approval or
merge into `main` (`59b891e`). Any presentation of STOP as a project decision (rather
than one branch's unapproved recommendation) would be misrepresentation. NOT verified:
whether any other branch or document claims closure; that is NOT REVIEWED.

Research root `/mnt/c/Users/MDP/dev/llmzip-work/` holds the published-package source
worktree `_wt_top10/`, raw `top10_comparison_r1/`, `bench3/`, `incoming_20260916b/`,
`drive/`, plus many sibling audit dirs — sampled only (see §8).

Key file sizes (lines): FINAL_STATE.md 142, REPORT.md 343, coordinator/decision_tests.py
220, coordinator/ladder.py 255, ablation_r2/perltqa/t3_ladder.py 236,
coordinator/t3_perltqa_kltn.py 176.

## 2. Contracts + hardcoded-path analysis (no execution; `grep` over READ-ONLY package)

FINAL_STATE.md Layout (§Layout) lists REPORT.md, DECISION_TESTS.md, LADDER_REALTALK.md,
EXTERNAL_AUDIT3_RESPONSE.md, PUBLICATION_VERIFY.md, coordinator/, decision_r1/,
lit_r2/, digest_r1/, math_r1/, ablation_r2/, ideas_r1/, incoming_20260916b/,
FILE_MANIFEST.json; excludes `model/` (2.4 GB HF weights, sha in MODEL_DOWNLOAD.json)
and `*.npz` regenerable intermediates; files >3 MB gzipped with manifest sha256 of
uncompressed bytes. REPORT.md states every number was re-derived by the coordinator
from stored per-query ids with paired archive-clustered bootstrap (20000 reps, seed
20260916). PROTOCOL.md (top10 r1, a different sub-experiment) pins tie rule
`SHA256('top10-r1|'+archive+'|'+row)`, metric Hit@10, and model revision — read as
context, not as the T1/T3 contract.

Hardcoded-path table (all absolute, all `/mnt/c/Users/MDP/dev/llmzip-work/...`):

| script (package copy) | read path | exists? | write path | verdict |
|---|---|---|---|---|
| coordinator/decision_tests.py:39-42 | incoming_20260916b/.../text_rerank_per_query.csv (T2) | EXISTS | — | portable only on this machine |
| decision_tests.py:105,160 | LADDER.json beside script + top10_comparison_r1/data/RTnn.json (T1) | EXISTS | — | same |
| decision_tests.py:108 | top10_comparison_r1/audit/audit_baseline_lib.py (T1) | EXISTS | — | same |
| decision_tests.py:38 OUT | — | — | HERE/DECISION_TESTS.json (beside script) | running the package copy unmodified OVERWRITES the published JSON -> MUST copy first |
| coordinator/ladder.py:42-45 | drive/v52_t4d_locomo_frozen_cross_benchmark.py; top10_comparison_r1/audit/audit_baseline_lib.py; top10_comparison_r1/data; bench3/runs/b3a_realtalk/rt_repr/RTnn.pkl | ALL EXIST | — | same-machine only; `drive/` + `bench3/` + `top10_comparison_r1/` are all OUTSIDE the package, i.e. hidden dependencies for a stranger with only the package |
| ladder.py:163-251 | — | — | HERE/LADDER_CACHE.jsonl (append) + HERE/LADDER.json | same overwrite problem; plus k=768 dropped in-code comment (RT06 27 min, died at 3000 s) — a stranger rerunning the documented grid would not reproduce without reading that comment |
| ablation_r2/perltqa/t3_ladder.py:19,22-24 | top10_comparison_r1/audit (sys.path); bench3/PerLTQA/Dataset/en_v2/*.json; bench3/runs/b3b_perltqa/cache_{arch,q}_eval.pkl | ALL EXIST | — | same-machine only |
| t3_ladder.py:235 | — | — | ABSOLUTE `/mnt/c/.../top10_comparison_r1/coordinator/T3_PERLTQA_KLTN.json` — OUTSIDE the package | worst case: unmodified run writes into the raw work dir, not the package; MUST copy + redirect output |

Consequence for the audit rule: NO original script is executed in place. Each probe below
copies the script into the own dir, redirects its output there, runs a bounded subset
(T1 only / 2 smallest archives), and every adaptation is documented. A stranger with
ONLY the package (no `/mnt/c/.../top10_comparison_r1`, `/bench3`, `/incoming_*`,
`/drive`) could run NONE of these scripts — see §5.

Published anchors captured before probing (for cell-by-cell compare):
T3_PERLTQA_KLTN.json arms (Hit@10 / FR@3, n=2217): k96/sym 78.12/51.69, k96/qscale
81.33/56.38, k96/asym 81.87/57.09; k192/sym 77.94/53.88, k192/qscale 82.18/57.71,
k192/asym 84.71/60.79; k384/sym 74.65/48.71, k384/qscale 79.70/54.11, k384/asym
84.89/61.09; gate diff 0 / 276480 bits; delta192->384 FR@3: sym -5.17, qscale -3.60,
asym +0.30. DECISION_TESTS.json T1 BM25: coarse_textbook 55.32/33.91,
frozen_textbook 61.70/36.05, coarse_idfonly 57.30/34.05, frozen_idfonly 65.67/40.02
(strongest); T1 is pure-Python BM25 over 10 RT archives, no model weights needed.
PerLTQA small-archive census (own read of cache_arch_eval.pkl, 30 archives): 8 with
n<384, smallest Kong Tingting n=293, Zhu Xiaolong n=343 — these two are the §4 probe.
