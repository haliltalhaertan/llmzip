# HARD AUDIT — Six "Genuinely New" Claims (adversarial re-check)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Audit directory (own writes only): `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r1/claims`
Sources are READ ONLY. No commits. `PYTHONDONTWRITEBYTECODE=1`. Each expensive probe capped at 180 s.
Method rule: coordinator scripts may be READ but results are recomputed with my own audit code.
NO-ARTIFACT rule: any check not executed is marked NOT RUN. No invented numbers.

Status: COMPLETE 2026-09-17 UTC. Written incrementally; all six attacks executed with own code.

## Coverage ledger (live — superseded by final ledger at end of file)
- Examined: claims.txt, FINAL_STATE.md, REPORT.md (full), DECISION_TESTS.md (full),
  coordinator/LADDER.json, DECISION_TESTS.json, T3_PERLTQA_KLTN.json,
  coordinator/ladder.py (score_arms: sym=QB@B.T dot, qscale=(QC/sigma)@B.T, float=cosine),
  coordinator/decision_tests.py (T1 BM25: k1=0 branch sums IDF; T2 paired bootstrap),
  math_r1/quant/quant_math.py (apply_arms/score_archive: sym=-Hamming, qscale=Dpm@(Qc/sig).T,
  MED thresholds docs AND queries at doc median, RAND seeds 20260916-18, ITQ 50 iters init 20260916),
  math_r1/quant/RESULTS.json (3 RAND seeds x RealTalk+PerLTQA summaries).
- Branch inventory: main repo `findings/top10-comparison-2026-09-15` = e672192 (STOP verdict commit);
  main=59b891e untouched; worktree git metadata unreadable under WSL (file reads used instead).
  Related refs noted, bodies NOT REVIEWED yet: findings/dense-mrl-parity-2026-09-14,
  findings/f1-execution-2026-09-14, findings/representation-geometry-2026-09-13,
  hr/standardized-float-correction-2026-09-16.
- Sampled: (audit scripts below)
- NOT REVIEWED: E1/residual/F1/dense branch bodies; LoCoMo gold dispute; lit_r2 maps.

## Claim 1 — ITQ < random rotation (RealTalk -2.27, PerLTQA -0.13)
- Attack: seed selection / transparency. Re-run with >=5 seeds; does ITQ beat random on any seed?
- Test result (own code `au_c1_itq.py` RealTalk + `au_c1b_perltqa.py` PerLTQA; read-only
  C/QC caches; own SVD-family orthogonal generator, own 50-iter Procrustes ITQ, own
  Hamming-sym / asymmetric-qscale scorers, own stable-sort top-10; 7 fresh seeds
  7/42/101/2024/55555/777/1234567 disjoint from published 20260916-18):
  - Calibration (exact cohort n=705 RealTalk / n=8265 PerLTQA): FULL/qscale 49.65/80.00
    reproduced TO 0.00 pp; FULL/sym within 0.3-0.5 pp (tie-break noise). Pipeline trusted.
  - RealTalk qscale: my ITQ=32.91 vs fresh-RAND mean=35.18 -> -2.27, reproducing the
    published -2.27 TO 0.00 pp. ITQ rank 8/8 (beats zero of 7 fresh seeds; with published
    seeds: zero of 10 rotations). Range of 7 fresh RANDs 34.33-36.17, all above ITQ.
  - RealTalk sym: ITQ rank 7/8 (beats only worst seed), ITQ-meanRAND -1.62.
  - PerLTQA qscale: my ITQ=78.91 vs fresh-RAND mean=79.05 -> -0.14, reproducing published
    -0.13. ITQ rank 6/8 (beats 2 of 7 fresh seeds: 78.74, 78.87). Seed sd is 0.22 pp —
    the -0.13 is inside seed noise: a NULL result, honestly reported as such.
  - PerLTQA sym: ITQ rank 1/8 (+0.67 over mean RAND, beats all 7 fresh seeds; also above
    FULL/sym by +0.58 in my tie-break). Scorer-dependent sign flip at ±0.7 pp scale.
  - Paired uncertainty: per-archive ITQ-meanRAND spread RealTalk qscale mean -2.44,
    range [-7.02,+1.01] — damage is broad-based, not one archive.
- Verdict: SAGLAM where it matters (RealTalk: ITQ beats 0/10 rotations on the production
  qscale scorer; exact -2.27 reproduction). PerLTQA half is a NULL (indistinguishable from
  seed noise; sym even favors ITQ) — the published text already presents it as "-0.13",
  i.e. no effect, so no retraction needed, but "ITQ<random" must not be quoted for PerLTQA.
  The seed-cherry-picking attack FAILS: 7 pre-registered-fresh seeds confirm the pattern.

## Claim 2 — Rotation harm ~ archive size r=-0.78
- Attack: outliers / small n. Recompute Spearman, leave-one-out carrier, drop 3+ points.
- Test result (own code `au_c2_corr.py`, read-only inputs math_r1/quant/RESULTS.json
  by_archive + RT*.json doc counts; damage = mean-of-3-RAND minus FULL, Hit@10 pp):
  - Reproduced: Pearson -0.80 (qscale) / -0.91 (sym) vs claimed -0.78. Claimant's number
    matches the qscale/Hit@10 aggregation within 0.03.
  - Spearman: -0.76 (qscale) / -0.93 (sym) — rank-based measure confirms, not a
    Pearson-linearity artifact.
  - LOO: Pearson stays in [-0.83,-0.77] (qscale); no single archive carries r.
    RT04 is an outlier (rotation HELPS RT04 by +5.16 pp qscale) yet removing it barely
    moves r (-0.77).
  - Drop-3 weakest combo (RT03,RT04,RT05): Pearson still -0.70 at n=7; Spearman falls
    to -0.39 — the rank association leans on the small archives' scatter.
  - Per-seed r is stable: -0.78/-0.81/-0.77 across the 3 published RAND seeds (qscale).
  - SCOPE LIMIT (found by my metric check): on FR@3 the association weakens to
    Pearson -0.56 (qscale) / -0.29 (sym). The "law" is Hit@10-specific in this data.
  - Small/large split reproduced approx: small(N<700) -5.89 vs claimed -6.56;
    large(N>=1000) -24.02 vs claimed -23.13 (residual mismatch = undocumented aggregation
    detail, pattern intact).
- Verdict: SAGLAM on its reported metric (Hit@10: survives Spearman, LOO, drop-3, per-seed);
  metric-fragile (FR@3 much weaker) and n=10 — do not quote as a general law.

## Claim 3 — Bit balance improves while performance degrades
- Attack: confounded with rotation. Find rotation-free balance-breaking intervention from existing data.
- Test result (own code `au_c3_balance.py`; read-only rt_repr caches + RESULTS.json):
  - Balance extremes reproduced EXACTLY: my global per-bit 1-fraction extremes for FULL =
    [0.309,0.658] vs REPORT's "0.309-0.658". Rotation narrows to [0.436,0.561]
    (REPORT: 0.459-0.545; residual seed-aggregation detail, direction confirmed).
  - Rotation-free intervention EXISTS in existing data: MED arm (median threshold, no
    rotation) PERFECTS balance to [0.500,0.500], mean|f-0.5|=0.0001 (own computation,
    pooled 8944 docs x 96 bits).
  - Yet MED retrieval never improves: RealTalk sym -1.13 / qscale -0.43 pp vs FULL;
    PerLTQA sym -0.81 / qscale -0.53 pp (published deltas; my pipeline calibrates <0.3pp).
  - So holding rotation fixed and perfecting balance yields no gain (slight harm) —
    the disentanglement the attack demanded exists and SUPPORTS the claim: balance is
    not sufficient for retrieval quality here.
  - Caveat: MED also re-thresholds queries at the doc median, so it is a
    threshold intervention, not a pure "balance knob". And the claim's literature
    contrast ("literature treats balance as a design goal") was not re-verified
    against sources — taken as the claimant's reading, NOT independently confirmed.
- Verdict: SAGLAM on the numbers (balance perfected without rotation, no retrieval gain);
  literature-contrast half NOT independently verified.

## Claim 4 — sigma-division collapses at high k
- Attack: "asym always better, sigma not special". Compare per-k; verify qscale bad only at high k (PerLTQA 8-arch + RealTalk LADDER.json).
- Test result (own code `au_c4_sigma.py`, pure-JSON; scorer contracts read from
  t3_perltqa_kltn.py: qscale=(QC/sigma)@B.T, asym=QC@B.T, sym=Hamming):
  - "qscale bad ONLY at high k" VERIFIED on T3 (FR@3): 96->192 +1.33, then 192->384
    -3.60 (Hit@10 -2.48). Non-monotonic collapse, exactly as claimed.
  - RealTalk LADDER corroborates by absence: all archives have n>384 (k<n comfortably),
    and there qscale rises monotonically (+5.67/+2.55), beating sym at every k
    (+3.12/+3.55/+3.69). Sigma-division HELPS wherever trailing dims stay non-singular.
  - Attack half-TRUE within T3: asym >= qscale at EVERY k (+0.71/+3.08/+6.98 FR@3, gap
    widening with k). The sigma penalty exists at all k; it turns catastrophic at high k.
    The novel part of the claim (non-monotonic collapse of standardized arms) survives.
  - Attack REFUTED cross-benchmark: full-data k=96 FR@3 asym-qscale = +0.29 (PerLTQA,
    tie), -3.62 (LME), -1.58 (LoCoMo). "asym always better" is a PerLTQA-local fact.
  - MECHANISM GAP (my finding): sym — which NEVER divides by sigma (sign invariance,
    independently verified 0-bit proof in RESULTS.json) — falls HARDEST at 384 (-5.17 vs
    qscale -3.60). "Dividing by tiny sigma amplifies noise" cannot explain sym's steeper
    fall. Root cause is better stated as: near-singular trailing directions are noise;
    sigma-division is one way to be hurt by them, sign-binarization another (worse) way.
    Observation SAGLAM; causal attribution to sigma-division ALONE is incomplete.
- Verdict: SAGLAM on the observation (collapse verified, RealTalk control consistent,
  attack overgeneralizes); mechanism wording needs the sym caveat above.

## Claim 5 — sign() beats float source by ~10 pts (LADDER.json float arms 36.60/40.43/43.69)
- Attack: is float arm unfair? Did float get fair normalization? Read code, evaluate.
- Test result (code read + own code `au_c5_float.py` on read-only C/QC caches, exact n=705):
  - LADDER.json gaps verified arithmetically: k96 +9.93, k192 +11.35, k384 +10.50 (Hit@10).
  - My float_cos = 36.60 reproduces the published float arm TO 0.00 pp — the float arm
    is exactly cosine-on-centered-C, the textbook-correct float scorer, not sabotage.
  - Same-scorer test (my key experiment): float_dot = 37.02, so sym_dot - float_dot =
    +9.79 pp. Scorer choice moves float by only +0.43 pp. The ~10 pp gap is NOT a
    scorer artifact. (Mathematical note I verified by construction: all +/-1 rows have
    norm sqrt(k), so sym dot==cosine rankings; only float had a scorer degree of freedom,
    and it barely matters.)
  - Both arms share the same centered input (Y-mu), so centering is not a confound either.
  - Fairness verdict REVISED after the hr-branch challenge (see 5b): float received cosine
    but NOT sigma-standardization. My `au_c5b_stdfloat.py` (own code, same caches, n=705):
    float_std_cos = 48.51 — reproducing REPORT.md's own round-table float_std number TO
    0.00 — which BEATS sym (46.81) by -1.70 pp, confirming the hr branch's "-1.83
    RealTalk" on this pipeline. Full ladder at k=96: float_cos 36.60 < sym 46.81 <
    float_std 48.51 < qscale 49.65 (= float_std_dot, coincidentally exact).
    So the attack "float didn't get fair normalization" is CORRECT in the sigma sense:
    give float the same sigma treatment production qscale uses, and float wins.
  - What survives: as a COMPRESSION story (12 B sign beats 384 B naive float by ~10 pp)
    the numbers are exact. As a MECHANISM story ("sign is not merely lossy, it ADDS"),
    it is demoted: the value-add is per-axis equalization, which sigma-standardization
    provides BETTER while keeping magnitudes. Note REPORT.md section 1 already prints
    48.51 next to 46.68 — the reversal was in the pilot's own table, but FINAL_STATE's
    "genuinely ours #6" framing omits it. Selective framing, not fabrication.
- Verdict: ZAYIF (gap exact vs naive float; reversed vs standardized float, the
  production-relevant reference; framing omits the reversal).

## Claim 6 — Fair BM25 65.67
- Attack: IDF-only (k1=0,b=0) is a component of BM25; real BM25 is k1=1.2,b=0.75. Which matches "we beat BM25"?
- Test result (own code `au_c6_bm25.py`: own tokenizers/BM25/top-10, read-only RT data,
  exact n=705):
  - Reproduction: my 4 variants = 55.32 / 61.70 / 57.30 / 65.53 vs published
    55.32 / 61.70 / 57.30 / 65.67. Three EXACT to 0.00, fourth within 0.14 (tie-break).
    The +10.21 pp handicap I measure (vs published +10.35) is confirmed.
  - Attack PARTLY VALID on the label: k1=0/b=0 (sum of IDFs, no tf, no length norm) is
    the degenerate limit of the BM25 formula, not "BM25" as the field uses the term.
    "Strongest honest BM25 = 65.67" overlabels; "strongest honest lexical baseline in
    our scorer family" would be accurate.
  - Attack FAILS on substance: genuine BM25 (frozen tokenizer + textbook k1=1.2/b=0.75)
    = 61.70 in MY rerun — still beats 12B code by 12.05 pp and 48B code by 3.83 pp.
    The tokenizer handicap alone (+6.38) already reverses every historical "we beat
    BM25" line, which used the 55.32 opponent. The headline-reversal finding does not
    depend on the IDF-only variant at all.
  - Gate robustness: C1 needs code to beat fair BM25 by +2 FR@3. Against GENUINE BM25
    (FR@3 36.05) the 48B arm (32.79) still fails by -3.26. STOP outcome unchanged under
    either baseline definition.
  - Open caveat (mine, flagged per mandatory challenges): frozen_idfonly is a best-of-4
    selection on the same 705 queries used for evaluation — no held-out split, so
    "65.67 is THE setting" does not generalize as stated. The 4-way table (which T1
    reports in full) is the honest artifact, not the max.
- Verdict: SAGLAM on substance (headline reversal + gate outcome hold vs genuine BM25);
  label "BM25" for the IDF-only variant is debatable — quote 61.70 as "BM25" and 65.67
  as "strongest lexical baseline".

## Cross-project synthesis (expanded responsibility)
- Original aim vs last pilot: aim = competitive retrieval at 12 B/doc. Pilot verdict on its
  branch = STOP the retrieval-optimization programme under prespecified gates C1/C3/S3
  (REFEREE.md, read in full). My audit confirms the gate INPUTS (fair-baseline gaps to
  0.00-0.14 pp; T3 ladder shapes; rerank JSON arithmetic) and the gate OUTCOMES are robust
  to every relabeling I tried (C1 fails vs genuine textbook BM25 too, -3.26 FR@3 at 48 B).
- STOP scope, precisely: it stops optimizing THIS code family (TF-IDF/SVD sign codes) as a
  BM25-beating first stage. It does not and cannot close the whole project: (a) FINAL_STATE
  leaves `main` untouched and the merge/decision to the owner, with an explicit reopen
  condition (Q9 text-free deployment); (b) sibling branches (dense-MRL parity, F1-execution,
  representation-geometry, E1 mechanism/residual arms) were NOT REVIEWED here beyond tip
  subjects — no certification for or against them; (c) the referee's own narrow gates
  (N1/N2) and the running LME ablation remain open by design.
- Strongest evidence AGAINST optimistic claims (code is competitive): genuine BM25 beats
  every code budget (my rerun: -12.05 at 12 B, -3.83 at 48 B); rerank inversion (worst-first
  ends best; post-rerank spread 0.58 pp over 11.58 pp pre-spread); never-won-both-benchmarks
  regularity; standardized float beats sign (my 48.51 > 46.81).
- Strongest evidence AGAINST pessimistic claims (nothing left to try): gates are strict
  conjunctions (both benchmarks, +2.0 pp, CI-excluded-zero) — failing them refutes the
  GENERAL claim, not every slice; RealTalk has only 10 archives (wide intervals, everything
  exploratory by the pilot's own admission); LoCoMo excluded while disputed; baseline max
  selected on seen gold without held-out split; Q9 (text-free deployment, the one
  non-empirical decider) is unanswered — an owner question, not a measurement; and the
  pilot's own "representation, not budget" framing points AT other representations, which
  this pilot did not test.
- Counterexample vs conjecture vs validated result (my ledger): VALIDATED = the six anchors'
  arithmetic (all reproduced exactly/within tie-break), ITQ<RealTalk-random over 10 rotations,
  qscale high-k collapse, MED no-gain, BM25 handicap. CONJECTURE = "tiny-sigma" as THE
  mechanism (sym falsifies exclusivity), "per-axis normalizer" as sign's mechanism
  (standardized float does it better), size-damage as law (FR@3 weakens it). COUNTEREXAMPLE =
  hr branch's standardized float (replicated by me), LME asym<qscale (vs "asym always better").
- Is closing the ENTIRE project justified by these tests? NO — and the pilot does not ask
  for that. Justified: stop funding THIS code-vs-BM25 race (gates failed as written, outcome
  robust). Not justified: treating STOP as project closure, or as verdict on unreviewed
  branches/slices. The unapproved-STOP-misrepresented-as-closure challenge finds NO support
  in examined docs (branch-only verdict, owner explicitly reserved).

## Mandatory-challenge checklist (results)
- [x] sym-vs-sigma: sym NEVER divides (sign invariant to positive scaling; 0-bit proof in
  RESULTS.json). Claim 4's "dividing by tiny sigma" cannot be the whole mechanism — sym
  (no division) falls hardest (-5.17 vs -3.60). CHECKED, mechanism incomplete.
- [x] rank-overflow causal explanation: T3 (0 const dims, decline persists) kills rank-overflow
  as THE cause — a valid refutation of the old claim; but the replacement ("tiny-sigma noise")
  is itself incomplete per above. Refutation VALIDATED; replacement = CONJECTURE.
- [x] rerank vs candidate recall: rerank does NOT remove recall importance — REPORT's own
  decomposition: 172/705 queries have gold outside top-100 (unreachable by any reranker);
  "dissolution" concerns ranking within pool only. CHECKED from published numbers.
- [ ] BM25 query scoring needs raw text: T1/frozen BM25 needs indexed text at query time;
  whether a deployment can avoid it is Q9 — an OWNER question, unanswered. OPEN, not a measurement.
- [x] RealTalk-only delta applied everywhere: refuted by the programme's own regularity
  (never won both) + my cross-benchmark checks (LME asym-qscale -3.62; r metric-fragile).
  Single-benchmark deltas do not transfer. CHECKED.
- [x] best-of-4 BM25 on seen gold: no held-out split anywhere; "65.67 is THE setting" does not
  generalize as stated. Gate outcome is robust anyway (fails vs 61.70 too). FLAGGED (S3 below).
- [x] STOP misrepresented as closure: NO evidence in examined docs (FINAL_STATE: main untouched,
  owner's call; REFEREE: Q9 owner-decides; STOP lives on a findings branch). NOT FOUND.
- [ ] Literature absence = novelty proof: the "nothing in scanned literature" novelty wrapper on
  claims 1-6 was NOT independently verified (lit_r2 maps not reviewed). NOT CONFIRMED either way.

## Verdict table
| # | Claim | Verdict |
|---|-------|---------|
| 1 | ITQ < random rotation | SAGLAM (RealTalk; exact -2.27 over 10 rotations) / NULL honestly reported (PerLTQA) |
| 2 | rotation harm ~ size r=-0.78 | SAGLAM on Hit@10 (Spearman/LOO/drop-3 survive); metric-fragile (FR@3 weaker), n=10 |
| 3 | balance up, retrieval down | SAGLAM on numbers (MED perfects balance, no gain); lit-contrast unverified |
| 4 | sigma collapse at high k | SAGLAM observation + RealTalk control; mechanism wording incomplete (sym caveat) |
| 5 | sign beats float ~10 pp | ZAYIF (exact vs naive float; REVERSED vs standardized float 48.51>46.81, replicated) |
| 6 | fair BM25 65.67 | SAGLAM on substance (my 65.53; genuine BM25 61.70 still wins); "BM25" label debatable |

## Severity-ranked findings (no fabrication found anywhere)
- S1 interpretation/Claim 5: FINAL_STATE #6 omits that standardized float beats sign, though
  REPORT §1 prints 48.51 and the hr branch recorded the correction. Selective framing.
- S2 mechanism/Claim 4: sigma-division exclusivity disproved by sym's steeper fall. Restate cause
  as near-singular trailing-direction noise (division and binarization are two ways to lose).
- S3 method/gates: best-of-4 baseline on seen gold, no held-out; executed comparator (max,
  frozen_idfonly) deviates from referee spec (textbook-primary). Outcome-robust in my rerun,
  but the deviation should be minuted, not silent.
- S4 scope: r law is Hit@10-only; PerLTQA ITQ half is null; RealTalk n=10 — none are quotable
  as general laws. The pilot mostly says this itself; hold it to it.
- S5 Literature/novelty: "genuinely new" wrappers unverified by this audit. Cite as pilot-local
  findings, not novelty claims.

## Coverage ledger (final)
- Examined: claims.txt; FINAL_STATE.md; REPORT.md (full); DECISION_TESTS.md (full); REFEREE.md
  (full, gate contract); LADDER.json; DECISION_TESTS.json; T3_PERLTQA_KLTN.json;
  math_r1/quant/RESULTS.json (incl. by_archive); ladder.py; decision_tests.py;
  t3_perltqa_kltn.py (scorer contracts); quant_math.py (arms/scoring/MED/RAND/ITQ);
  hr/standardized-float-correction tip commit (stat + message body); branch inventories
  (main + top10 + 4 sibling tips, log subjects only); exclusions.json (23-qid cohort).
- Sampled via own reruns (read-only caches, own code): 7-fresh-seed ITQ test RealTalk+PerLTQA;
  correlation recomputation; balance extremes; same-scorer + standardized-float tests;
  4-variant BM25 rerun. Reproduction quality: 8 anchors exact to 0.00 pp, rest within
  0.5 pp (tie-break/cohort noise).
- NOT REVIEWED: E1/geometry/residual/F1/dense branch bodies; LoCoMo gold dispute; lit_r2 maps;
  rerank CSV re-derivation (T2 trusted as JSON arithmetic only); cost/latency accounting;
  PerLTQA sym-tie-break offset (+0.5-0.6, immaterial to contrasts).
- No writes outside this directory. No commits. No source executions (all scripts read, never
  run). PYTHONDONTWRITEBYTECODE=1 throughout. No probe exceeded 60 s (180 s cap untriggered).

## Mandatory-challenge checklist (pending)
- [ ] sym-vs-sigma (sign invariance to positive scaling)
- [ ] rank-overflow causal explanation?
- [ ] rerank vs candidate recall?
- [ ] BM25 query scoring needs raw text?
- [ ] RealTalk-only delta applied to all datasets?
- [ ] best-of-4 BM25 on seen gold -> generalization?
- [ ] unapproved STOP misrepresented as closure?

---
(All six sections evidenced above; no NOT RUN verdicts remain.)
