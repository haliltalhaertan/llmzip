# PRE1 — Adversarial review: DRAFT PREREGISTRATION, twelve-byte budget race

**Reviewer role:** independent adversarial (pre-seal). **Verdict: NOT SEALABLE as written — 8 FAILs must be closed first.**
Draft honestly marks opens (§8 checklist), so the skeleton is right; the missing content is load-bearing, not cosmetic.
Methods: read-only inspection of the draft, the roadmap Design-2 spec, round-1..3 reports/errata, frozen protocol
script, Deney-1 harness sources, HR budget-decision ref, Codex revision unresolved-list; plus executed probes
(faiss 1.15.0 offline) quoted in the appendix. No network. Nothing modified outside /tmp/pre1.

**Materials checked:** `DRAFT_PREREG_TWELVE_BYTE_RACE.md` (2026-09-13) · `muse_strategy_roadmap.md` §3-Design 2 ·
`YOL_HARITASI_FINAL.md` · `ROUND2_REPORT.md` · `ROUND3_REPORT.md` · `DENEY1_REPORT.md` · `ERRATA_ROUND3_D5.md` ·
`missing1_kill_null.md` (m1) · `v52_t4c3_coordinate_axis_probe.py` (frozen eval) · `deney1_lme.py`/`deney1_loco.py`
(harness reimplementation) · HR decision `89d3169` (`V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`) ·
Codex revision `a73393a6` (`UNRESOLVED_DECISIONS.md`) · `RUN_LOG.md` · `V52_T4C3_question_level.csv`.

## FAIL findings (seal-blockers)

### F1 — RaBitQ32's 96→32 dimension reduction is unspecified, and the choice spans the full band scale
- **Draft ref:** §3 A4/A5 ("RaBitQ32, plain" / "+ random-rotation wrapper").
- **Evidence:** RaBitQ at d=32 needs 32 input dims from a 96-d pipeline; the draft names no rule. The HR decision's
  own table calls the candidate `TOP32_RABITQ32` (commit `89d3169`) — i.e. top-32-variance axes, the selection the
  pilots found anti-optimal (R2A: TOP48 0.3495 vs RAND48_s0 0.4729 on LME, ≈−12pp; R2C: TOP80 −3.6pp vs BOT80 −0.1pp
  on LoCoMo). Alternatives (bottom-32, spread-32, random-32, learned projection 96→32 with extra shared state) differ
  by ~10pp — five times the decisive band. Centering (centered-C vs raw) and the query-side 32-dim path are likewise
  unnamed, although the programme's founding anomaly (centered SIGN96 beats float96 by +10pp; roadmap §2.2) makes
  centering load-bearing. Codex P1 already warned: "Never silently choose top32 RaBitQ" (`a73393a6`).
- **Required fix:** freeze the exact 32-dim construction (axis-list rule or projection matrix + seed + shared-state
  bytes), the centering rule (same archive-mu as sign arms, or named deviation), and the query path (float query,
  same rotation/selection). If TOP32 is kept, justify it against the anti-optimality finding in the sealed text.

### F2 — No scoring estimator is fixed for RaBitQ/PQ arms; "identical tie seeds" does not cover it
- **Draft ref:** §2 (frozen SIGN-Hamming protocol), §5 ("identical tie seeds across arms").
- **Evidence:** The frozen eval (`v52_t4c3_coordinate_axis_probe.py:136-137`) scores integer Hamming distances with
  20-trial `lexsort(distance, priority)` tie-breaks. RaBitQ (rotation + asymmetric float estimator + per-vector
  scalars) and PQ (ADC float lookups) emit non-discrete distances: no estimator formula, no float-query construction,
  no symmetric-vs-ADC choice for PQ, no K=3-on-floats rule, no epsilon rule for near-ties. Each unspecified choice is
  a future degree of freedom worth potential pp. Reusing tie *seeds* without defining the tie *rule on floats*
  leaves the scoring undefined.
- **Required fix:** per-family frozen estimator (formula + exact faiss call sequence + code ref), float-query
  construction, top-3 := argmin on estimated distance with `lexsort(distance, trial-priority)` using the frozen
  20 priorities, an epsilon rule (e.g. exact-float-equality-only, or |Δ|<1e-9 ⇒ tie — pick one), and a fairness
  statement: score scales are never compared, only per-question fractional R@3 (the common metric); state the
  invariance argument (every arm maps (C, qC, gold) → top-3 → FR through identical aggregation).

### F3 — The primary estimand is ill-defined (vs-best and vs-mean are conflated)
- **Draft ref:** §4 ("per-seed difference (SIGN12B − best ≤12B competitor) … seed-panel mean + per-seed range").
- **Evidence:** "Gap-to-best" (a max statistic) and "mean of per-seed gaps" are different estimands with different
  nulls (m1: −1.62/−1.20pp for the former). "Best" scope is unstated: max over aggregate FR across all arms/seeds?
  per-question oracle best (much larger lift)? per family? Widths are pooled (6/8/10B seeds in one panel mixes byte
  levels). Bootstrap re-selection is unstated — Deney-1 re-selected best-of-10 *inside* each resample (RUN_LOG:
  "resample içinde yeniden best-of-10"); without that, CIs around a max statistic are invalid.
- **Required fix:** exact formula: per-(family×width) gap table as primary display + ONE named primary contrast
  (e.g. SIGN12B minus max-aggregate over the named ≤12B set; per-question-oracle explicitly excluded); state
  bootstrap re-selects the argmax inside each resample; freeze B + bootstrap seed(s).

### F4 — Bands are calibrated for single comparisons but applied to a max statistic, with no multiplicity control and an incomplete decision table
- **Draft ref:** §4 bands (≥+2.0 / +1.0–2.0 / ±0.5 / ≤−1.0), kill (≥2.0pp loss "on either benchmark"), promote
  (≥−0.5pp "on both benchmarks" + ranges "not overlapping the alternate-width failure null").
- **Evidence:** m1 null (`missing1_kill_null.md`): no-edge arm vs best-of-9/10 = **−1.62pp (LME) / −1.20pp (LoCoMo),
  range to +1.91**. Consequences: (i) a truly-null arm reads −1.6pp, outside the ±0.5pp "parity" band — the band and
  the estimand are inconsistent; (ii) the 2.0pp kill line sits 0.09pp above the observed null max; (iii) the race
  maxes over ~27 competitor looks/benchmark (3 widths × ≥7 seeds + spread/BOT + RQ×2 + PQ) with an OR-kill across 2
  benchmarks — family-wise false-kill inflation with no control. Further: 4 zones × 2 benchmarks = 16 cells but only
  2 named actions (e.g. −1.2pp on one bench + parity on the other, or +1.5pp moderate, map to nothing); point-vs-CI
  rule unstated; "alternate-width failure null" undefined; curve "dominated everywhere" undefined (pointwise? CIs?
  which arms? marginal- or effective-byte axis?).
- **Required fix:** extend the m1 null simulation to the FULL sealed competitor set pre-seal (no race data needed);
  calibrate kill/promote lines to that null (or add a null-adjusted co-primary); adopt a family-wise rule (e.g. kill
  requires clearing the null-max, or a named multi-look correction); publish the complete 16-cell decision table with
  a point-vs-interval rule; define curve dominance (arm scope, axis, pointwise + CIs). Fix §6 "≥3pp premium would
  clear it" to m1's "~2.6pp" or quote m1 exactly.

### F5 — Third-party arms lack constructors, determinism controls, and a failure policy
- **Draft ref:** §3 A4/A5/A6; §5 pins; §8.2.
- **Evidence:** A4/A5 name no faiss class, constructor args, rotation source/seeds, or single-vs-panel ("both namings
  carried"; "verify rotation chain empirically" states no acceptance criterion — and a single random rotation is one
  draw from a high-variance distribution, cf. 4C3 −15.9pp rotation effects). A6 does not choose plain-PQ vs OPQ (HR
  decision discusses `OPQ_PQ96`; Codex P2 proposed plain-PQ-in / OPQ-descriptive — the draft picks neither). No
  k-means/OPQ/rotation RNG seeds, iteration counts, or thread controls. No small-archive fallback: observed in the
  pinned-version probe, `IndexPQ(96,12,8).train` FAILS at n=50 (faiss `Clustering::train_encoded` RuntimeError) and
  passes at n=300 with under-training warnings; LME min N=396 is safe (question-level CSV) but LoCoMo per-archive N
  is unevidenced in the bundle — so archive-local PQ on LoCoMo is a *known-unknown* with no pre-specified policy
  (Codex P2 required a "no-fallback failure policy": fail-arm vs fail-run vs exclude-questions).
- **Required fix:** exact constructors + literal seeds + panel sizes; determinism controls (faiss/RNG/iteration/thread
  pins); the fallback rule; the faiss version + wheel hash in the manifest (close §8.2).

### F6 — The byte worksheet is promised (§8.3) but its operative content is missing
- **Draft ref:** §1 rule; §3 arm table ("≤12 (measure & report)"); §8.3/§8.5.
- **Evidence:** No per-arm declared/measured method; §8.5 ("asserts `code_size` semantics against measured serialized
  bytes") names no tie-break when the two disagree; shared-state bytes unlisted (centering mu 768B/archive; PQ
  codebooks 12×256×8×float32 = **98,304 B/archive ≈ 200 B/vector at LME median N=490** — so the draft's "small
  archives" framing understates: even median-LME amortizes ~200B/vec); subset index sets unruled (global-random vs
  per-archive spread/BOT — cf. R2C protocol note); LUT persistence status unstated; "per-archive effective cost"
  undefined and homeless (footnote vs primary-table column).
- **Required fix:** worksheet table [arm | code B | scalar B | header B | declared | measured-by(method) |
  shared-state B/archive | amortized B/vec at stated N | verdict] + a code_size-vs-serialization disagreement rule +
  amortized cost as a PRIMARY-table column + dual-axis recall-vs-bytes curve (marginal and effective).

### F7 — No sealable run package (plan, manifest, frozen analysis, stop rules, provenance, amendment policy)
- **Draft ref:** whole draft; §8.6 (HR line, blank).
- **Evidence:** No runner command/paths (harness precedent hardcodes `BASE = Path('C:/Users/MDP/dev/llmzip-work')`,
  `deney1_lme.py:15` — must not recur); no output manifest (reuse the HASHES_ROUND3.txt 6/6-OK pattern); analysis
  unfrozen (bootstrap B/seeds/strata/cluster definition); stop rules beyond aborts absent (faiss missing, PQ-train
  failure, cohort mismatch); "certified matrices" and cohort lists unnamed (no paths/hashes); no-reseed-after-outcome
  rule absent (roadmap week-2 note); no seal-hash binding (V52 `PRE_RUN_SEAL.json` pattern). The blank HR line is
  correct pre-seal posture — everything else must exist before it is signed.
- **Required fix:** assemble the package (run plan + manifest pattern + frozen analysis spec + stop/fallback rules +
  provenance hashes + amendment/no-reseed policy + seal-hash binding). Nothing runs until package sealed + HR signed.

### F8 — Disclosure (§7) omits outcomes and the race's own NOES licenses
- **Draft ref:** §7 boilerplate; §6 science context.
- **Evidence:** (a) The race INTRODUCES alternate distance metrics (ADC, RaBitQ estimator) — a NOES prereg-or-nothing
  class (frozen `NORES` list, `v52_…probe.py:20`); the boilerplate says pilots didn't touch them but never LICENSES
  them for the race — this preregistration is that license and must name the per-arm estimators. (b) c2/m2/m3 negative
  outcomes undisclosed (c2 closed, NOT prereg-ready: ROUND3 §5, m3 p_bonf=0.18; m2 gold-free 0/10 splits ≥0.65) —
  approaches listed, outcomes missing. (c) The Design-1 gate that killed A3 was itself exploratory (DENEY1 header:
  NOT PREREGISTERED) — status undisclosed. (d) The SPREAD-cap erratum, material to A1's "repaired rank-linspace,"
  is unnamed (the roadmap boilerplate HAD enumerated R2D errata items; the draft compresses to "acknowledged").
  (e) §6 numbers lack per-number citations; "≥3pp premium would clear" misquotes m1 ("~2.6pp").
- **Required fix:** extend the boilerplate with (a)–(d); cite every §6 number to its table/file; fix the 3pp figure.

## CAVEAT findings (fix or explicitly accept in the sealed text)

- **C1 — LoCoMo-only BOT-tail arm creates an asymmetric bar.** R2C justifies it (BOT80 −0.1pp on LoCoMo), but the
  draft must state its widths/seeds/single-vs-panel and acknowledge the LoCoMo bar is thereby stricter. (§3 A1)
- **C2 — Width mapping and seed panels implicit.** State the bytes↔bits↔width_idx table (10B=80b=idx2,
  8B=64b=idx1, 6B=48b=idx0); justify ≥7 vs Deney-1's 10 (10 preferred — R2B's 3.34pp range at k=64); state whether
  SPREAD is single-fixed or paneled and carry the fixed-vs-max disadvantage language (ROUND3 C2/C3: co-report
  vs-mean) so a null reading can't be mis-headlined. (§3 A1/A2, §4)
- **C3 — The nb_bits-trap narrative needs re-grounding.** Observed on faiss 1.15.0: `IndexRaBitQ` has NO `nb_bits`
  attribute at all — the silent-trap mechanism as described may belong to a different class/version. Keep the
  `code_size` abort regardless; cite the pinned API. (Appendix, §8.5)
- **C4 — Thread/environment pins.** Frozen script pins OMP/MKL/OPENBLAS/NUMEXPR=1; faiss OpenMP reductions can flip
  near-ties at the top-3 boundary. Pin threads=1 and record full env (python/numpy/faiss/BLAS/OS) in the manifest. (§5)
- **C5 — LoCoMo conversation-cluster bootstrap undefined.** Define clusters (conversations? sizes? count?) and which
  CI (question-paired vs cluster) governs decisions. (§4)
- **C6 — Curve underspecified.** Name exact x-points ({6,8,10,12 native, 44 ext}? k=16/24 confirmatory per roadmap
  P4?) and require dual axes (marginal + effective bytes, cf. F6). (§4)
- **C7 — Wording without content.** "Both namings carried" (A5) and "verify rotation chain empirically" mean nothing
  sealable — replace with the F5 spec; the empirical check needs an acceptance criterion. (§3)
- **C8 — Anchor last-digit.** Draft LoCoMo/LME anchors match to 1e-16 « 1e-12 tolerance, but the LME anchor's last
  digit (...645) differs from the frozen script constant (...646, line 19). Cite the canonical source
  (question-level CSV / parent aggregate) to pre-empt seal-time mismatch debate. (§2)

## NOTE findings (minor; no action strictly required)

- **N1 —** A2 seed namespace (93000+…) is disjoint from Deney-1's (91000+…) — good; state it as deliberate. (§3 A2)
- **N2 —** Kill-OR/promote-AND are logically consistent (kill ⇒ ¬promote) — keep the structure; the holes are the
  unmapped middle cells (F4). (§4)
- **N3 —** PQ LUTs are query-time compute, not persistent bytes — the worksheet needs one line saying so. (F6)
- **N4 —** R2A's single-seed lesson is already internalized as the vs-best primary — credit; m1 calibration (F4) is
  the remaining step. (§4)
- **N5 —** Sub-12B curve numbers in §6 check out against cited sources (10B −2.7 / 8B −5.9 / 6B −9.2 LME; BOT80 −0.1
  LoCoMo; 59/60 validity) — they need citations, not corrections. (§6)

## (a) Minimal changes required before seal (ordered, actionable)

1. Freeze the scoring spec: F1's 32-dim rule + F2's per-family estimators, query paths, float tie/epsilon rule,
   K=3 semantics, fairness statement. Blocks everything below.
2. Freeze the estimand + calibrated decision rules: F3's exact formula (per-cell table + one named primary,
   re-select-inside-bootstrap) and F4's null extension to the sealed competitor set, calibrated bands, family-wise
   rule, complete 16-cell table, dominance definition. Pre-seal notebook, no race data.
3. Freeze third-party arms: F5 constructors/seeds/panels/determinism/fallback + faiss version + wheel hash.
4. Write the F6 byte worksheet with the dual (marginal + amortized) numbers as primary-table columns.
5. Assemble the F7 seal package (run plan, manifest pattern, frozen analysis, stop rules, provenance hashes,
   no-reseed/amendment policy, seal-hash binding).
6. Extend §7 and cite §6 per-number (F8); resolve C1–C8 each as fix-or-accept in the sealed text.
7. HR signature on the package → seal → run §(b) smokes green → run once.

## (b) Smoke tests that must pass BEFORE seal

- **S1** Native reproduction in the RACE runner (not a pilot harness): both anchors, ≤1e-12, both benchmarks.
- **S2** Byte replay in the pinned env: RaBitQuantizer(96)=20, (32)=12, IndexPQ(96,12,8)=12, ext-2bit=44; plus a
  deliberate declaration-vs-measurement mismatch shown to abort.
- **S3** The silent-trap negative control in the pinned API: the actual no-op mechanism demonstrated and caught.
- **S4** PQ archive-local train on the min-N archive of EACH benchmark (or the F5 fallback fires as specified).
- **S5** Determinism: retrain + rerun with fixed seeds/threads ⇒ bit-identical codes and FR.
- **S6** Float-score tie rule executable: 20 frozen priorities applied as lexsort(distance, priority) with
  per-question persistence validated on one archive.
- **S7** A4/A5 rotation-chain acceptance criterion executed (not "verify empirically" prose).
- **S8** Construction asserts incl. the BOT arm: eff_k==k, logged cols, no sentinels — plus a broken-construction
  negative control.
- **S9** Manifest dry run: hash-check pattern (HASHES_ROUND3.txt-style) over dummy artifacts.
- **S10** Thread pin (OMP/MKL/OPENBLAS=1 or named equivalent) + full env recorded; runner uses repo-relative paths
  (no `C:/` hardcodes).

## (c) Already solid — do NOT churn

§1's verbatim HR budget text (matches `89d3169` word-for-word in the operative clauses); both anchors + ≤1e-12
gates (match frozen TOL and anchors); per-benchmark-never-pooled reporting; A3's exclusion executing the Deney-1
kill with correct numbers (−1.25pp/2-of-10 LME; −0.15pp LoCoMo); A7's out-of-contrast curve-only status (matches the
HR "cannot enter"); §5's tie-seed/persistence/negative-control principles; the §8 open-items skeleton (fill it,
don't restructure); the vs-best primary direction with question-paired (+ LoCoMo cluster) bootstraps; the
4F1/BEAM, 4C1–4D, no-corpus-retrieval, archive-local boundary lines; the blank-until-signed HR line.

## Appendix — executed verification (commands + raw output)

- `faiss-python -c "import faiss; ... RaBitQuantizer(96).code_size"` → `faiss 1.15.0`, `RQ96 code_size= 20`,
  `RQ32 code_size= 12`. Corroborates the HR table (20/12) and roadmap "d=32 max at 12B" (4B code + 8B scalars).
- `IndexPQ(96,12,8).code_size` → `12`; `IndexRaBitQ(96).code_size` → `20`, `hasattr(nb_bits)` → `False` (basis of C3).
- `IndexPQ(96,12,8).train`: n=50 → `RuntimeError ... Clustering::train_encoded ...` (FAIL); n=300 → OK with
  `clustering 300 points to 256 centroids: please provide at least 9984 training points` warnings (basis of F5/S4).
- LME `N_archive` from `V52_T4C3_question_level.csv` (n=470): min 396, p5 446, median 490, max 616; frac<256 = 0
  (LME PQ-train safe; LoCoMo N unevidenced in bundle → F5/C-unknown).
- Derived (arithmetic, shown): PQ shared state per archive = 12 subquantizers × 256 centroids × 8 dims × 4B =
  98,304 B/archive ≈ 200 B/vector at N=490 (basis of F6). Sign-mu shared state = 96 × 8B = 768 B/archive.
- Textual diffs confirmed by read: HR decision `89d3169` ("TOP32_RABITQ32 … 12 … natural candidate"; "8-byte …
  two float32 … not removable" per L-087 `489e5f9`); Codex `UNRESOLVED_DECISIONS.md` P1–P5/I1–I3/A1–A2 all OPEN
  (never silently choose top32; no-fallback policy; per-arm scoring; shared-vs-effective bytes); m1 null numbers
  as quoted in F4; Deney-1 A3 numbers as quoted; `deney1_lme.py:15` hardcoded `C:/` path (F7); frozen script
  `TOL=1e-12`, `EXP_NATIVE …49646`, tie formula `5_100_000+lex*100_000+t*100+99`, `NORES` including 'alternate
  distance metrics' (F2/F8, C8).

*End of PRE1 report. Severity counts: FAIL 8 · CAVEAT 8 · NOTE 5. Output files: `/tmp/pre1/pre1_report.md`,
`/tmp/pre1/pre1_details.json`.*
