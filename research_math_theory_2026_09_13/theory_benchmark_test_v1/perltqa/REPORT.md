# PerLTQA Model-H proxy-transfer pilot — REPORT

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

This is NOT preregistered and NOT yet independently audited. All results are
provisional until separate recompute + adversarial review.

## Outcome in one paragraph

Gate reproduced the frozen PerLTQA baseline bit-for-bit in practice
(per-QA max diff ~2e-16 ≤ 1e-12 tolerance, 8265 QAs, 30 archives): native
SIGN96 0.488941994930817 vs centered-float96 0.551692074528853
(delta −6.275pp). The predeclared primary, LOW48 endpoint contrast
mean[delta(t=4) − delta(t=0.25)] with delta = sign − float, is +0.02464 with
archive-cluster bootstrap 95% CI [0.01554, 0.03443] (2000 reps, seed
20260913): nonpositive is excluded, so the verdict under the sealed rule is
'consistent with this proxy transfer' — compatibility with the proposed
transfer hypothesis, NOT confirmation or causal explanation of Model H.
Three qualifications, all predeclared kinds of evidence, cut against any
strong reading: (1) the aggregate LOW48 curve is non-monotone (only the last
step rises); (2) 11.6% of individual QAs (961/8265) show an adjacent delta
decrease, so pointwise monotonicity cannot transfer unconditionally;
(3) sections disagree in sign — profile reverses sharply (−0.186), while
events (+0.049) and social (+0.086) carry the primary. The HIGH48 comparison
is the exact algebraic negation of LOW48 (verified bit-identical), hence
carries zero independent information — disclosed, not counted twice.

## Does the negative headline fit the theory?

The user asked this especially. Careful answer in three parts; none of them
redefines nuisance after seeing outcomes (LOW48/HIGH48 were fixed gold-free
by query magnitude before any intervention metric was computed).

1. The headline (sign loses by 6.275pp at t=1) has NO direct counterpart in
   Model H. The theorem's t=1 point is an equality INSIDE its toy law
   (identical outcomes on every realization); real embeddings have no
   identified theoretical t, and the raw (t=1) PerLTQA point is simply the
   unscaled data. A proxy-transfer failure here would falsify only the
   proxy/transfer, never the conditional theorem. The negative headline is
   therefore compatible with the theory being true AND with it being
   inapplicable — it does not discriminate.
2. The direction of the comparative static matches on aggregate: amplifying
   the low-magnitude proxy (LOW48, t=4) moves cosine DOWN relative to sign
   (float 0.5517 → 0.5192; delta −0.0627 → −0.0303), i.e. the sign/float gap
   closes in the theory-consistent direction. Suppressing it (t=0.25) moves
   the other way (float 0.5439, delta −0.0549).
3. But the section curves (exploratory, secondary) refuse a uniform story:
   events LOW48 delta runs −0.112 → −0.115 → −0.124 → −0.117 → −0.063
   (contrast +0.049, theory-consistent direction); social −0.017 → −0.018 →
   −0.008 → +0.014 → +0.069 (contrast +0.086, crosses zero: at t=4 sign
   WINS social); profile +0.240 → +0.231 → +0.204 → +0.128 → +0.053
   (contrast −0.186, REVERSED: amplifying LOW48 helps cosine vs sign);
   dialogues −0.011 → −0.013 → −0.015 → −0.021 → −0.020 (contrast −0.008,
   flat near floor). Single-gold QAs (n=5943) give +0.037; multi-gold
   (n=2322, dialogues) give −0.007. So the aggregate primary is an
   events+social majority vote that profile actively opposes. Under the
   sealed reading this heterogeneity is the finding: the proxy transfer is
   section-dependent, and sign invariance alone is (as predeclared) NOT
   claimed as theory evidence — it is a verified tautology (0 mismatches
   in 82,650 scaled arms).

## Gate (BEFORE intervention)

- Recomputed 20-seed fractional R@3 per QA from eval caches with verbatim
  producer conventions (tie priorities 5_100_000+ORD·100_000+t·100+99,
  lexsort ranks, exact-== float ties, original gold denominators).
- Per-QA max |diff| vs results_rerun.json: native 2.220e-16, float
  1.110e-16; violations 0; means match the exact (unrounded) gates at
  1e-12. Cross-stack gate resolved with NO tolerance relaxation
  (ml-python 3.14.4/numpy 2.5.3 = port-gate stack).
- Counts from code: 8265 QAs / 30 archives; sections 333/844/4346/2742;
  expanded 8593 → resolved 8305 → measured 8265; excluded Chen Zhi N=35
  (40 QAs); 288 unresolved (277 nobank dragon beautiful + 11 keymiss).

## Intervention (gold-free, sealed)

- Groups: LOW48/HIGH48 = first/last 48 coords by (abs(q_j), j); t in
  {0.25, 0.5, 1, 2, 4} applied to BOTH docs and query; no refit/recenter.
  FULL96 t=4 control. 8265 × 11 = 90,915 per_query.jsonl rows, no
  subsampling (asserted in code).
- Primary outcome: exact tie-bucket expected fractional R@3 (uniform
  tiebreak; float buckets by exact ==); 20-seed MC also stored at
  t ∈ {0.25, 1, 4} (endpoint MC contrast +0.02464 = exact to 5 decimals).
- Checks: sign byte-identical under all positive scalings (0/82,650
  mismatches); t=1 restores scores bit-exactly (max diff 0.0); FULL96 t=4
  cosine bit-identical (drift 0.0, rank orders unchanged);
  LOW48@t == HIGH48@1/t bit-exact for all pairs (global-scale invariance,
  so HIGH48 contrast = −LOW48 contrast by identity, CIs mirror likewise).
- Aggregate LOW48 float curve: 0.5439 / 0.5465 / 0.5517 / 0.5508 / 0.5192;
  delta curve: −0.0549 / −0.0576 / −0.0627 / −0.0619 / −0.0303.
- Pointwise monotonicity violations (any adjacent delta decrease, t
  increasing): LOW48 961/8265 (11.63%), HIGH48 1080/8265 (13.07%).

## Limits

30 archive clusters (few-cluster bootstrap caveat stands); one benchmark,
one seed family (SVD 5204); exact-expectation/MC gap reported, not gated;
sections already-known strata, exploratory only; four-benchmark family
exists but only PerLTQA run here — no familywise claims, no pooling.
Heavy caches stayed outside Git; nothing pushed; sources read-only and
re-hashed unchanged (17/17) after the run.

## Artifacts (workspace only)

runner.py, gate.json, PRE_RUN.json, per_query.jsonl (90,915 rows),
run_diag.json, summary.json, verification.py (32/32 PASS), REPORT.md,
gate_receipt.txt, run_receipt.txt, boot_receipt.txt,
verification_receipt.txt, ckpt_*.jsonl, STATUS.md, PLAN.md (byte-exact copy).
