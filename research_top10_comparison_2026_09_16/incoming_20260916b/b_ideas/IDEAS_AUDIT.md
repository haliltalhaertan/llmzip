# IDEAS AUDIT — experiment packages other than the ladder
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Auditor: programme worker (b_ideas). All numbers below are THEIR numbers unless
tagged VERIFIED-BY-ME. VERIFIED-BY-ME means I recomputed it from THEIR
machine-readable artifact (named file) — it does NOT mean independent
re-execution or that the claim is true of our system. Their self-audit is not
independent verification. Coordinator re-derivation is pending for everything here.

Frozen-anchor check (done first, by reading their OZET JSONs, not their prose):
- FIKIR1 OZET: LME qscale FR@3 54.27, PerLTQA 53.24, LME Hit@10 88.51,
  PerLTQA Hit@10 80.00 — VERIFIED-BY-ME (recomputed from
  LLMZIP_FIKIR1_OZET_2026-09-16.json). Reproduces frozen anchors exactly.
  So FIKIR1 measured OUR system (12-byte qscale96 baseline intact).
- KISITLI_CEZA OZET: PerLTQA production/qscale FR@3 53.24, Hit@10 80.00;
  LoCoMo production/qscale FR@3 35.84, Hit@10 57.22 — VERIFIED-BY-ME
  (recomputed from LLMZIP_KISITLI_CEZA_OZET_2026-09-16.json). Production
  columns reproduce anchors. BUT metric is expected uniform-tie FR@3, while
  frozen anchors are deterministic SHA-tiebreak — last-decimal differences
  vs other packages are expected; they warn about this themselves (§2).
  LME in this package is a 24-query size-spaced panel (production/qscale
  FR@3 60.69/64.03-scale numbers), NOT the full 470-query LME — do not
  compare its LME levels to the frozen 54.27.
- HATA_YERI OZET: PerLTQA doc_sign_query_std 80.00, RealTalk 49.6454,
  RealTalk standardized_cos 48.5106 — VERIFIED-BY-ME, reproduce frozen
  anchors exactly. RealTalk sign96 reads 46.6809 here vs frozen deterministic
  46.5248: THEIR-CLAIM table header says this package uses expected
  uniform-tie Hit@10, so a ~0.16 pp tie-convention delta is expected, not a
  contradiction. Do not mix tie conventions across packages.
- HIZ_GENELLEME OZET: LME weighted 88.51, PerLTQA weighted 80.00,
  LoCoMo weighted 57.22 — VERIFIED-BY-ME, consistent with FIKIR1's qscale
  Hit@10 levels (88.51/80.00/57.22). Cross-package consistency holds at the
  baseline level. LoCoMo float here is 61.01 — CONTRADICTS-OURS nothing,
  but do NOT mix with LOCOMO.json's 50.03 (different pipeline/gold cohort;
  MASTER_LEDGER §4 already forbids mixing; HIZ itself says text-only
  retrieval adaptation, exclusions pre-registered in-plan).
- IKI_FIKIR OZET: spot-checked LME base192 FR@3 61.48 / base96 52.47 /
  two_cos 54.41 — VERIFIED-BY-ME (read from LLMZIP_IKI_FIKIR_OZET_2026-09-16.json,
  matches report §2 table). 24-byte cohort (LME/PerLTQA-en_v2/LoCoMo-1531,
  NO RealTalk) — different byte budget, so frozen 12-byte anchors do not
  directly apply; internal base96 control is the bridge (see §3).

Global note on cohorts: FIKIR1/HATA/HIZ use deterministic-vs-expected tie
variants and overlapping-but-not-identical cohorts (FIKIR1 LoCoMo n=1531 keeps
stated exclusions; HIZ LoCoMo n=1531 with 446 adversarial-cat-5 + 4 + 5
excluded pre-scores). I treat each package's WITHIN-package paired contrasts
as its evidence and never compare levels across packages at last-decimal
precision.

---

## Package 1 — FIKIR1 (small code retrieves, raw text reranks)
Source: LLMZIP_FIKIR1_RAPORU_2026-09-16.md + extracted/LLMZIP_FIKIR1_METIN_YENIDEN_SIRALAMA_2026-09-16/ (PLAN_BEFORE_RUN.json, OZET.json, results/text_rerank_per_query.csv etc.)

- Single claim (THEIR-CLAIM, report §1): "Sabit qscale96 aday listesindeki 50
  kaydı özgün metinden BM25 ile yeniden sıralamak, üç test kümesinde de FR@3
  ortalamasını artırdı" — LME +3.43, PerLTQA +4.22, LoCoMo +6.97 pp over own
  qscale first stage. VERIFIED-BY-ME from OZET.json (57.70-54.27=3.43;
  57.46-53.24=4.22; 42.81-35.84=6.97).
- Prespecified success criterion: NONE numeric. Quoting their own plan
  verbatim (PLAN_BEFORE_RUN.json): "stop_rule": "If numeric/cache/cohort
  validation fails, stop affected dataset and report. A weak BM25 pilot can
  fail without disproving all text rerankers." The plan fixes M=50, metric
  (FR@3, no pooling), BM25(k1=1.2,b=0.75) and RRF60, and baselines ("same
  candidate list no rerank", "same reranker on float controls",
  "full-corpus BM25") — but sets no pass/fail threshold. So "did it pass?"
  is UNDEFINED by their own criterion; any pass/fail label would be post-hoc.
  Against the coordinator's decisive line (code contribution over PLAIN BM25
  alone), the result is: LME -0.33 pp, PerLTQA +0.33 pp, LoCoMo +1.07 pp
  (VERIFIED-BY-ME from OZET.json: qscale96_bm25 minus BM25_full).
  I.e. it CONFIRMS the coordinator's line almost exactly (the coordinator
  quoted -0.33/+0.33/+1.06; my recomputation gives -0.33/+0.33/+1.07, rounding).
- Controls present or missing: HONOURS the control rule — this is the ONLY
  package that does. Same fixed BM25 reranker is applied to hamming96,
  asym96, qscale96, float_std32, float_raw32 first stages AND a full-corpus
  BM25 arm is run (report §5 table, all 15 cells). The controls destroy any
  "code earns its place" reading: LME hamming96_bm25 (58.23) BEATS
  qscale96_bm25 (57.70) although hamming is the worse first stage; LME and
  PerLTQA reranked scores sit within ~0.3 pp of plain BM25_full (58.03/57.13);
  LoCoMo float_std32_bm25 (43.22) beats qscale96_bm25 (42.81). The gain is
  the RERANKER's, not the code's. Report says this itself (§5: "bütün
  iyileşmeyi küçük kodun özel bir başarısı diye yorumlayamayız") — credit.
  Missing: B8 codec not reranked (they disclose); RealTalk text-rerank absent
  (numeric caches only — disclosed, not hidden); no unseen data (disclosed).
- Cost accounted: YES, honestly, and it kills the idea as a system. Report
  §7–§8: qscale→BM25 adds +2.37ms LME / +0.77 PerLTQA / +0.59 LoCoMo wall
  time; full BM25 alone is 0.10–0.14 ms (their inverted-index control is
  ~100x faster end-to-end on the panel — panel timings, not SLA); auxiliary
  state dwarfs the code (LME: 3.14 MB packed code+sigma vs 64 MB BM25 JSON /
  351 MB Python IDF objects vs 238 MB raw text). They state explicitly the
  dict design can cost more than the code saves. This matches the earlier
  112x-dictionary / 14.9→17.6 ms accounting in spirit and extends it.
- Verdict: CONFIRMS the coordinator's decisive line; REFINES it with LoCoMo
  (+1.07 pp over plain BM25, the only positive of the three, still smaller
  than the float+BM25 edge). The code does not earn its place under BM25
  reranking on any benchmark at 12 bytes. The package's own decision ("araştırmaya
  değer" but "en iyi kalite/hız/bellek sistemini göstermiyor", keep float/BM25
  controls next round) is the correct reading. Do not cite the +3.43/+4.22/+6.97
  first-stage deltas as system wins — the pre-registered full-BM25 control
  exists precisely to forbid that.

## Package 2 — KISITLI_CEZA (constrained additive penalty Z'Z + λD, rowspace-limited)
Source: LLMZIP_KISITLI_CEZA_RAPORU_2026-09-16.md + extracted/LLMZIP_KISITLI_CEZA_PILOT_2026-09-16/ + design notes KONTROL_VE_DENEY_EKI.md (§§3–5) and MATEMATIK_INCELEME.md (cited, not re-audited here).

- Single claim (THEIR-CLAIM, report §1): the constrained penalty is SAFE
  (96 effective dims, 0 constant-bit columns, all numeric gates pass — nullspace
  risk from the free-penalty analysis does not materialise) but NOT SUPERIOR:
  "güvenlikli ve doğru çözülmüş olması, arama üstünlüğü anlamına gelmiyor."
  LoCoMo penalty-vs-exact0 +1.65 (γ=0.25) / +2.15 pp (γ=1.0); PerLTQA small/
  uncertain (+0.40/+0.67); LME-24 panel no net penalty effect (-1.25/0.00).
  VERIFIED-BY-ME from OZET.json (PerLTQA exact0/qscale 52.98 → penalty1 53.66
  = +0.68 ≈ reported +0.67; LoCoMo 35.11 → 37.26 = +2.15; LME-24 64.03 → 64.03
  = 0.00; production/qscale columns 53.24/35.84 reproduce anchors).
- Prespecified success criterion: NONE numeric. Quoting their plan verbatim
  (PLAN_BEFORE_RUN.json): "lambda_rule": "lambda=gamma*(96th descending
  eigenvalue of ZZ^T)/lambda_max(Vr^T D Vr); gamma=0.25 and 1.0, fixed, no
  best-parameter selection", plus "stop": "any source/fidelity/null/isotropic
  gate fail: record archive failure, no silent exclusion or candidate headline
  until explained". Gates (not quality bars) are the criterion: eigenresidual
  <1e-8, orthonormality <1e-8, effective rank 96, isotropic D=I control must
  agree to 1e-8. They report all gates passed. So "did it pass" splits: safety
  gates PASS (their criterion), quality has no prespecified bar — and on the
  live programme question ("does it work as retrieval?") the answer is NO
  (details below).
- What it actually measured / payload / λ=0 control (Q3):
  * Measured: full-rowspace exact eigensolver (all Z Z^T eigenvectors above
    max×1e-12, NOT old-top-96-only) with H=diag(s²)+λV_r^T D V_r, D = word
    unigrams len≥2 with archive df∈{1,2} weight 1, everything else 0
    (THEIR-CLAIM, §3; genuinely new vs our multiplicative IDF^p — coordinator
    already verified subspace distance 2.78, I take that as given, not
    re-derived). Cohort 64 archives / 9,820 queries (30 PerLTQA-full, 10
    LoCoMo-1531, 24-arch LME size-spaced panel with 24 queries). Seen data only.
  * Payload: YES, kept at 96 bits / 12 bytes per doc (THEIR-CLAIM §8:
    "Kod boyutu toplam 29905 kayıt için 358.860 bayt" = 29,905×12; gates log
    effective rank 96, 0 constant columns). Mean/sigma arrays are per-encoder
    extras as in production — not counted in the 12 B, same convention as ours.
  * λ=0 control: exact-solver-no-penalty arm. VERIFIED-BY-ME from OZET.json:
    PerLTQA exact0/qscale 52.98 vs production 53.24 (-0.26 pp); LoCoMo 35.11
    vs 35.84 (-0.73 pp); Hit@10 79.89 vs 80.00 / 55.39 vs 57.22. So the exact
    solver ALMOST reproduces production (within ~0.3–0.7 pp FR@3, ~0.1–1.8 pp
    Hit@10) but NOT bit-exact — expected, since randomized-SVD96 vs exact
    full-rowspace eigendecomposition are different algorithms; the report is
    explicit that exact0 effects and penalty effects are reported SEPARATELY
    (§4) and does not book solver drift as penalty gain. Isotropic D=I control
    agrees with λ=0 to 0 bits/scores (THEIR-CLAIM §7; NO-ARTIFACT for me — I
    did not open per-archive residual files, only OZET.json; treat as their
    claim with stated 1e-8 gate).
  * Did it work: NO as a retrieval improvement. Paired CIs (their bootstrap,
    exploratory): LoCoMo penalty1-vs-exact0 +2.15 [0.57;3.93] excludes 0 BUT
    they themselves report the paired sign test p=0.1094 (8 up/2 down archives)
    and refuse a significance claim — honest, credit. Vs the PRODUCTION
    reference (the comparison that matters for us) LoCoMo +1.42 [-0.55;3.36]
    INCLUDES 0; PerLTQA +0.42 [-0.38;1.19] includes 0; LME-24 0.00 [-6.25;6.25].
    Hit@10 moves are tiny (PerLTQA 80.00→80.23, LoCoMo 57.22→57.87, LME panel
    100→95.83 on n=24 — noise). And it NEVER approaches the strong controls in
    the same table (§4): BM25 beats penalty1 everywhere (LME-24 67.36 vs 64.03;
    PerLTQA 57.14 vs 53.66; LoCoMo 41.75 vs 37.26), exact0/float_std beats
    penalty1/qscale everywhere (68.19/56.24/38.85 vs 64.03/53.66/37.26).
    Mechanism diagnostics (rare-df≤2 group +2.48 PerLTQA / +4.21 LoCoMo with
    -0.82 in PerLTQA other-shared; pair decomposition 2,979 lost-by-projection
    pairs of which 1,088 recover on standardisation vs 6,967 lost-by-qscale
    pairs) are post-hoc subgroup/pair analyses — interesting, correctly labelled
    non-causal, not a system result.
- Controls present or missing: PARTLY honours. Present: unchanged-production
  control, exact λ=0 control (solver effect isolated — exemplary), isotropic
  D=I control, BM25 + old ASYM/Hamming/float_std on the same queries+metric
  (strong references KEPT, and they sink the arm — reported, not hidden).
  Missing: B8 not built this round (disclosed, "B8'i geçtiği söylenemez");
  RealTalk raw experiment absent; NO control giving the SAME penalty boost to
  the competitor (penalty is representation-internal; there is no float+penalty
  or BM25+penalty arm — but since the arm never beats float/BM25 at all, the
  missing symmetric-enhancement control does not flatter it; the failure mode
  is opposite to FIKIR1's).
- Cost accounted: NO — explicitly not. Report §8: "Tek-geçişli zaman sayaçları
  ... bunlar baştan sona latency/RSS karşılaştırması veya 'daha hızlı' iddiası
  değildir"; no comparative peak RAM, no resident-service build; dual encoder
  must hold sparse Z and A outside the 12 B. They forbid speed claims — credit
  for restraint, but the honest-cost question is UNANSWERED for this arm; any
  follow-up must cost the full-rowspace fit (they warn it is not free).
- Verdict: Genuinely new mathematics, correctly controlled for solver drift,
  cleanly NEGATIVE on retrieval. Answers the live reviewer question: the
  constrained Z'Z+λD variant with df≤2-word protection does not rescue the
  12-byte code — LoCoMo-vs-exact0 is the only positive and it vanishes against
  production, float, and BM25. The valuable residue is diagnostic (both
  projection-loss AND scale-loss pairs exist; "all lost in SVD" vs "only
  scales" is a false dilemma — §6), not a contender. Do not gamma-sweep this
  (they prespecified no-selection for a reason); if revisited at all, revisit
  as mechanism study with a routing-free protection prior, per their §9.

## Package 3 — IKI_FIKIR Idea A (96 coords × 2 bit vs 192 × 1 bit at fixed 24 B)
Source: LLMZIP_IKI_FIKIR_RAPORU_2026-09-16.md §§2–3 + OZET.json + PLAN_BEFORE_RUN.json.

- Single claim (THEIR-CLAIM, §8 decision): do NOT adopt 96×2 as default —
  "PerLTQA'da küçük/belirsiz iyileşme olsa bile ... diğer verilerde kayıp
  veriyor." Numbers: FR@3 96×2-cos minus 192×1: LME -7.07 [-9.86;-4.31],
  PerLTQA +0.67 [-0.11;1.46] (ns), LoCoMo -3.75 [-5.08;-2.68]
  (VERIFIED-BY-ME from OZET.json: 54.41-61.48=-7.07; 55.49-54.82=+0.67;
  37.46-41.21=-3.75). Hit@10 same pattern (LME -1.49, PerLTQA +2.16,
  LoCoMo -4.51 — recomputed from OZET.json).
- Prespecified success criterion: NONE numeric in the plan I could find
  (evaluation fixes primary=deterministic FR@3, references, no-gold-in-fit,
  no-silent-exclusions; quantizer fixed without task data; "never silently
  choose winner" between cos and dot — honoured, both reported). The verdict
  is a post-hoc decision, but it is the CORRECT post-hoc decision (a negative
  result reported as negative). Inner-dot secondary agrees (LME -6.72,
  PerLTQA +0.47, LoCoMo -3.82 — recomputed).
- Controls present or missing: WEAK on the control question. Present: same-96
  at 12 B control (96×1: LME 52.47 / PerLTQA 52.98 / LoCoMo 35.11) showing
  2-bit-at-24B beats 1-bit-at-12B on the same 96 coords (+1.94/+2.51/+2.35 —
  recomputed) — i.e. extra bits help the SAME subspace, but buying MORE
  directions (192×1) helps more on 2/3 benches. Missing: NO competitor arm
  gets the 2-bit treatment (no float+quant, no BM25+anything at 24 B; old
  BM25/float references are "reused as historical quality only, not new cost
  claims" — their words, evaluation §). Since the arm LOSES to the 24 B
  reference on LME/LoCoMo, the missing symmetric control does not create a
  false win; but the PerLTQA +0.67 (ns) cannot be claimed as "precision beats
  width" without a width-matched competitor enhancement.
- Cost accounted: YES for the measured arms (CPU ms/query panel means:
  96×2 ≈ base192 within ~0.2 ms; RSS within ~0.4 MB — report §6 tables; 24 B
  payload held for every coded row, norms recomputed from code). Honest and
  narrow: panel latencies are not whole-benchmark means/p95 (they say so).
- Verdict: Clean NEGATIVE on the width-vs-precision question at 24 B with
  this fixed Gaussian Lloyd-Max prototype (thresholds ±0.9816/0, levels
  ±1.5104/±0.4528, task-blind — a principled fixed choice, not tuned). Does
  not contradict our 12-byte programme directly (different budget, no
  RealTalk), but CONFIRMS the programme prior that halving directions hurts
  more than precision helps on LME/LoCoMo. The PerLTQA +0.67 ns is the now
  familiar PerLTQA-points-one-way ghost — same sign-reversal family as
  IDF^p/SHIFT_m1/NO_CHAR. No follow-up at this design; any revival needs a
  different quantizer family (their plan names RaBitQ/TurboQuant as the
  controls they did NOT run — do not mistake this prototype's failure for
  those methods' failure).

## Package 4 — IKI_FIKIR Idea B1 (compact algebraic LSA decoder)
Source: report §4 + PLAN_BEFORE_RUN.json idea_B1 + OZET.json compact192 column.

- Single claim (THEIR-CLAIM, §4/§8): the refactored per-archive encoder
  (R=WᵀB, B=(WWᵀ)⁺WR, query path via W_qWᵀB, identity Z_qZᵀ=W_qWᵀ+H_qHᵀ+L_qLᵀ)
  reproduces ALL 10,266 top-10 lists exactly while shrinking serialised model
  state 46% (LME) / 32% (PerLTQA) / 28% (LoCoMo). VERIFIED-BY-ME in part:
  OZET.json compact192 FR@3/Hit@10 columns are bit-identical to base192 on all
  three benches (e.g. LME 61.4752/89.1489 both); top-10-identity itself is
  their claim from per-query artifacts I did not row-check (NO-ARTIFACT for
  me beyond OZET aggregates — name it: per-query top-10 CSVs under
  extracted/.../LLMZIP_IKI_FIKIR_2026-09-16/results/, residual 1.320e-13 /
  query-coord diff 6.645e-14 quoted from report §7).
- Prespecified success criterion: NUMERIC GATE, the only real gate in the
  batch — quoting plan verbatim: "gates": "relative projector reconstruction
  <1e-8; compare every query projection and top10 to baseline." Reported max
  relative residual 1.320e-13 < 1e-8 → PASS on their criterion. (Whether
  top-10 identity over SEEN queries equals production-safety is a separate,
  unanswered question — they say new-doc/streaming/retrain policies untested.)
- Controls: not applicable in the rival sense — this arm claims ZERO quality
  change by construction (algebraic refactor, same codes). The control IS the
  baseline identity check, and it is the right one. Honourable explicit limit:
  "arşive-özel ... daha küçük bir uygulamasıdır", NOT shared/cross-archive
  (they refuse the stronger claim).
- Cost accounted: PARTLY, with a disclosed hole. Model-file bytes honestly
  shrink (table §4, pickle5 lengths). BUT: (a) pickle bytes are not RAM —
  they say so; hot-process RSS drops only modestly (LME 204→184 MB,
  PerLTQA/LoCoMo ~3–4 MB — the 161 MB runtime base dominates); (b) build
  peak RSS is HIGHER for compact (e.g. LME 240→263 MB) and build CPU is flat
  (1.07→1.02 s LME, slightly worse elsewhere — report Ek table); vocab/char
  dicts and L/B/A/mean/sigma/texts remain. So: persistent-state win, no
  serving-RSS or build-cost win. Not a retrieval result; do not file it as one.
- Verdict: PASS as lossless refactor; the only "adoptable" item in the batch
  IF our bottleneck is stored model state rather than serving RAM or build.
  Rank it accordingly (below). Requires our-side equivalence replay before any
  use (their implementer = their verifier; no independent audit).

## Package 5 — IKI_FIKIR Idea B2 (shared random circulant encoder, hashing+IDF)
Source: report §5 + OZET.json shared_seed* columns.

- Single claim (THEIR-CLAIM, §5/§8): FAIL — "Daha küçük olmak kaliteyi
  korumadı", do not substitute. FR@3 main seed vs 24 B reference: LME 29.17
  vs 61.48 (-32.3), PerLTQA 26.90 vs 54.82 (-27.9), LoCoMo 18.59 vs 41.21
  (-22.6) (VERIFIED-BY-ME from OZET.json). Seeds 2/3 agree within ~3 pp —
  no seed-cherry-pick (primary seed pre-fixed — credit). Hash-features-
  unprojected cosine (64.44/57.93/44.87) is reported SEPARATELY and explicitly
  not as a 24 B result — good labelling, do not misquote it as a code result.
- Prespecified success criterion: none numeric beyond the shared protocol
  (primary deterministic FR@3, 3 fixed seeds, no best-seed selection).
  Outcome FAIL by any quality bar.
- Controls: the arm is its own control story (feature family AND transform
  changed together — they refuse single-cause attribution, §5). No rival gets
  the shared encoder; irrelevant, since it loses by ~25 pp.
- Cost accounted: YES (CPU/RSS panel rows、小er RSS ~163–164 MB vs ~171–204;
  shared filter charged once). Cheaper and ~25 pp worse — correctly rejected.
- Verdict: Clean NEGATIVE for this fixed prototype ONLY. Not evidence against
  shared/learned/neural encoders in general (they say so). No follow-up on
  this prototype. (Note for DO_NOT_REPEAT: logs as "shared hashing+circulant
  prototype at 192-bit/qscale fails badly", not as "all shared encoders fail".)

## Package 6 — HATA_YERI (where does the loss live: readout + stage diagnostics)
Source: LLMZIP_HATA_YERI_RAPORU_2026-09-16.md + OZET.json (checked above).

- Single claim (THEIR-CLAIM, §1): no arithmetic/packing error found; moving
  from numeric representation to two-sided sign/Hamming loses correctly-ranked
  evidence (directly measured), and restoring query-side magnitudes
  (doc-bits + standardised numeric query = qscale family) recovers
  +2.43 (LME) / +4.24 (PerLTQA) / +2.96 pp (RealTalk) Hit@10 over SIGN96 —
  recomputed from OZET.json (88.51-86.08; 80.00-75.76; 49.65-46.68), matches.
  Second loss: PerLTQA wide-Z→SVD96 -3.47 pp net (364 worse / 77 better).
  Both claims are diagnostic decompositions, and per the honesty rules they
  are "they measured X" (same-author checks: 249,390 scalar replays, 0
  mismatches; 78-archive raw-text rebuild, 0 sign-bit changes) — I verified
  the LEVELS against frozen anchors, not the pair counts.
- Prespecified success criterion: none — status is literally
  "COMPLETED_LOCAL_DIAGNOSTIC; NOT_PRODUCTION_APPROVAL;
  NOT_INDEPENDENTLY_AUDITED" (OZET.json). Correct label; judge as diagnosis.
- Controls: GOOD within its scope — the 2×2 (doc-magnitude × query-magnitude)
  ablation in a FIXED standardised space is the right design, and it HONOURS
  the "same enhancement to competitor" spirit in the one place it matters:
  it shows standardisation alone does not fix Hamming ("sadece sayıları
  standardize edip yine iki tarafı işarete indirgemek ... iyileştirmez" §7 —
  verified identity sign(C/σ)==sign(C) already in our digest). BUT the +
  readout is query-side only: doc-side float (+full standardised cosine
  88.30/83.96/48.51) still beats or ties the doc-bit readout on every bench
  (LME 88.30 vs 88.51 — the one tie; PerLTQA 83.96 vs 80.00; RealTalk 48.51
  vs 49.65 — RealTalk is the exception where qscale beats float_std).
  So the readout narrows but does not close the float gap — they say so (§4).
- Cost accounted: PARTLY. Extra state counted (sigma arrays 391,680 B vs
  3,034,056 B codes over 510 archives — recomputed ratio ~12.9% overhead,
  disclosed). CPU/RSS/end-to-end NOT measured here ("new_scorer_runtime_not_
  measured": true in OZET.json) — deferred to HIZ package, which is the
  correct cross-reference.
- Verdict: SOLID diagnostic, duplicates nothing (our digest has the
  sign(C/σ)==sign(C) identity and the RT09_q000 anecdote's SHAPE, but not the
  full 2×2 magnitudes table or the PerLTQA -3.47 SVD-stage decomposition —
  those are new measurements on seen data). Supports keeping qscale readout
  (already production) without overclaiming it. The PerLTQA SVD-stage loss
  (-3.47, 364/77) is worth our CPU (see ranking) because it localises a
  non-quantization loss our quantization-layer work cannot fix.

## Package 7 — HIZ_GENELLEME (qscale transfer to LoCoMo + SIMD speed)
Source: LLMZIP_HIZ_GENELLEME_RAPORU_2026-09-16.md + OZET.json (checked above).

- Single claim (THEIR-CLAIM, §1): qscale transfers to LoCoMo over Hamming
  (+4.58 pp Hit@10, [3.00;6.37], 156/78/1297) with a real SIMD implementation
  1.71–1.86x faster than a fair float32 SGEMV on prepare+score, yet still
  1.60–2.02x slower than Hamming; end-to-end text→top10 is encoder-dominated
  (no 2x system speedup). VERIFIED-BY-ME in part: LoCoMo 57.22-52.64=4.58
  from OZET.json; latency ratios recomputed from report §4 table
  (e.g. LME 3.22/1.76=1.83 ✓; Hamming-vs-SIMD 1.76/0.89≈1.97x — inside their
  1.60–2.02 band). Scalar-first-then-SIMD history preserved (they admit the
  first C version LOST to float) — credit.
- Prespecified success criterion: none numeric (PLAN_BEFORE_RUN fixes scorer,
  seeds 5101/5204, LoCoMo cohort/exclusions pre-scores, fair-float rules —
  all honoured as far as artifacts show; no pass/fail bar). LoCoMo is
  "public-data transfer, NOT blind/unseen" (their words §3 — LoCoMo was in
  project history; 1531-cohort with pre-written exclusions). Do not cite as
  unseen confirmation (our LEDGER §4 already says so).
- Controls: MIXED. Present: Hamming, old asym, standard float32 on identical
  queries (same 10,971-Q float32==float64 check). The two contrasts that
  matter both cut against a "qscale wins" story: vs old asym on LoCoMo only
  +0.39 [-1.66;2.25] (ns — "ölçek dengelemenin ek üstünlüğü güçlü biçimde
  doğrulanmadı", their honest sentence §3); vs float_std -3.79 [-4.41;-3.13]
  (float still clearly better, FR@100 gap 84.14 vs 78.75 too). So the package
  HONOURS controls and the controls say: most of the Hamming gap is "don't
  binarize the query", not "our σ-scaling". Missing: no BM25/float+B.M25 on
  LoCoMo here (covered by FIKIR1/KISITLI instead — do not demand every package
  carry every control; read them together).
- Cost accounted: YES — the best cost work in the batch (dedicated CPU/RSS
  design: pinned CPU0, 1 thread, 8 hot iters, rotated order, fair C-called
  SGEMV float without the weak-reference trick; end-to-end panel with fresh
  processes; per-query 3,072 B LUT + 8B×docs score buffer disclosed; code
  transpose keeps 12 B/doc single-resident). Honest limit stated: AVX-512-only
  speedups, shared/virtualized box, no p95/SLO, no queueing.
- Verdict: CONFIRMS qscale as the right readout (transfer + fair speed win
  over float) while REFUSING the two overclaims (not faster than Hamming,
  not better than float; system latency is encoder-bound). No regularity break
  (see Q5). Worth our CPU only as engineering input (SIMD LUT recipe), not as
  evidence for a quality claim.

## Design-only notes (no new numbers — read, do not re-run)
- KONTROL_VE_DENEY_EKI.md: the synthetic 8×4 counterexample (v_diff with
  Zv=0 selected by the FREE penalty, objective 11→7) + constrained solution
  (v_sum,e3, objective 8) + 200 randomised dual-factorisation checks
  (max residual <1.91e-13). No benchmark runs; scope-correct ("Yenilik kanıtı
  değil", "sentetik risk ... gerçek serbest-kol başarısızlığı diye
  sunulmuyor"). Its PRESCRIPTION (λ=0 / D=I / gap / residual gates, rowspace
  residual ||V-V_rV_rᵀV||, rank/effective-rank/bitconstancy transport checks,
  FR@3-primary-per-bench, keep ASYM/B8/float/BM25, no benchmark-chosen tuning)
  is EXACTLY what KISITLI_CEZA executed — audit that loop as closed.
  The IDF^p-vs-termonorm warning (§6: same df ≠ same norm; idf^p ≠ norm
  rescaling) is a valid caveat on our IDF^p arm's interpretation — flag to
  programme, no action.
- ONERI_VE_DENEY_PLANI.md: explicitly "[NO NEW BENCHMARK RUN]". The 12/24/48
  ladder it summarises (LME 52.47/61.48/61.75, PerLTQA 52.98/54.82/51.87,
  LoCoMo 35.11/41.21/44.15, BM25 57.14/60.14/42.87 FR@3) is CONSISTENT with
  IKI_FIKIR's base96/base192 levels (52.47/61.48 LME etc. — VERIFIED-BY-ME
  match). Its E0–E4 agenda correctly predicted the batch (E0=X rival cost —
  done in FIKIR1/HIZ; E1 compact encoder — done=B1; E2 width-vs-precision —
  done=Idea A; E3 shared encoder — done=B2; E4 tau-damping — NOT done, see
  ranking). Do not "re-propose" E0–E3.

---

## Q2 summary — the control question (standing rule)

| Package | Same enhancement to competitor? | Effect |
|---|---|---|
| FIKIR1 text-rerank | YES — BM25 rerank on hamming/asym/qscale/float_std/float_raw + full-BM25 | Gain ATTRIBUTED TO RERANKER; code contribution -0.33/+0.33/+1.07. Rule HONOURED, system claim correctly WITHDRAWN. |
| KISITLI_CEZA penalty | Rival-strong arms KEPT (BM25, float_std, asym, Hamming same queries) but no penalty-given-to-rival arm | No false win possible (arm loses to all of them). Rule effectively HONOURED in outcome; form missing but harmless. |
| IKI Idea A 96×2 | NO rival enhancement (no 2-bit float/BM25; old refs historical-only) | PerLTQA +0.67 ns unclaimable as method win. Rule VIOLATED in form; outcome negative anyway. |
| IKI B1 compact | N/A (zero-change refactor; baseline-identity IS the control) | Correct design. |
| IKI B2 shared | N/A (loses by ~25 pp to everything) | Correctly rejected. |
| HATA readout | SPIRIT YES (2×2 magnitude ablation; float still shown beating it) | No overclaim. |
| HIZ transfer/speed | YES (Hamming/asym/float same queries; asym+0.39 ns and float-3.79 reported) | Correctly limits claim. |

Standing-rule bottom line: only FIKIR1 could have produced a false "superior
system" (a tool added to ours, rival left behind) — and it is the one package
that ran the full symmetric controls and talked itself OUT of the claim. Every
other positive-looking delta in the batch (KISITLI LoCoMo-vs-exact0 +2.15,
IKI-A PerLTQA +0.67, HIZ LoCoMo-vs-Hamming +4.58) either vanishes against the
kept strong reference or is already our production scorer beating our old
scorer. There is no superior system behind any of these deltas.

## Q4 summary — honest cost (does the batch account, or only quality?)

| Arm | Total storage incl. aux | Latency incl. aux | Accounted? |
|---|---|---|---|
| FIKIR1 qscale→BM25 | YES: codes+σ MB vs raw/offset/BM25-JSON/IDF-object MB per bench (LME IDF objects 351 MB ≫ 3.1 MB codes) | YES: panel ms (LME 14.886→17.622; PerLTQA 2.743→3.605; LoCoMo 2.575→3.280) + BM25-alone 0.10–0.14 ms | YES — the model honest-cost exhibit |
| KISITLI penalty | Payload 12 B held; array totals in meta; fit-time U,s,K + sparse-Z/A costs named but NOT benchmarked; no RSS/latency comparison | Explicitly NOT measured ("no speed-superiority claims") | NO — open hole for any follow-up |
| IKI-A 96×2 | 24 B held, norms from code; model-file MB + hot RSS + build peak/CPU | Panel CPU/RSS (no regression) | YES (narrow panel, labelled) |
| IKI-B1 compact | Model-file MB shrink 28–46%; RSS only -3–20 MB (base dominates); build peak HIGHER | Build CPU flat/slower | PARTLY — persistent win real, serving/build wins absent |
| IKI-B2 shared | Shared filter once + per-archive IDF/mean/σ + RSS rows | Panel CPU/RSS | YES — cheaper and far worse |
| HATA readout | σ overhead 0.39 MB / 3.03 MB codes stated; full-service RSS excluded (named) | NOT measured (OZET flag), deferred to HIZ | PARTLY (points to HIZ) |
| HIZ qscale-SIMD | 12 B kept; σ 0.40 MB / 3.10 MB; LUT 3,072 B/query + score bufs; full RSS excluded (named) | YES: prepare+score µs (fair), top-10-incl µs, end-to-end ms (encoder-bound) | YES — best in batch |

No package hides its aux state; the two that cannot price it (KISITLI,
HATA-latency) SAY so in writing. Quote KISITLI §8 ("karşılaştırmalı peak RAM
... ölçülmedi") and HATA OZET ("new_scorer_runtime_not_measured": true)
rather than inferring.

## Q5 — cross-benchmark sign (does anything win everywhere?)

Programme regularity ("no arm has ever won on both benchmarks simultaneously",
FINDINGS_DIGEST §"OPEN, UNRESOLVED") SURVIVES — with one already-known
exception correctly scoped:

- FIKIR1 qscale→BM25 beats ITS OWN first stage on all three (the only
  everywhere-positive headline) but loses-to-ties plain BM25 (-0.33/+0.33/+1.07)
  and loses to float+BM25 on LME/LoCoMo. NOT a regularity break: the
  everywhere-winner is the BM25 reranker, not an arm of our code. Flag LOUDLY
  in the opposite direction: anyone quoting +3.43/+4.22/+6.97 as "wins
  everywhere" is misreading; the pre-registered BM25-full control forbids it.
- KISITLI penalty1-vs-exact0 is ≥0 on all three (0.00/+0.67/+2.15) but only
  LoCoMo excludes 0 under ONE of two reported tests (bootstrap yes, sign test
  p=0.11 no), and vs production all three CIs include 0. NOT a break —
  exploratory, inconsistent across references, never beats float/BM25.
- IKI-A 96×2: -7.07/+0.67ns/-3.75. Textbook sign instability, not a break.
- HIZ/HATA qscale-vs-Hamming wins on all four benches (+2.43/+4.24/+2.96/+4.58
  Hit@10). This is the ONE everywhere-win — but it is OUR OWN production
  scorer (qscale) vs OUR OWN old scorer (sym Hamming), known since hit10/
  QSCALE.json (coordinator-reproduced EXACTLY per DO_NOT_REPEAT), NOT a new
  arm. It still trails float_std on LME/PerLTQA/LoCoMo and BM25 nearly
  everywhere. So: regularity holds for NEW arms; the qscale exception predates
  this batch and changes nothing about the code-vs-rival standing.
- NOTHING in the batch is a new arm that wins on both (all) benchmarks
  against production + strong references. If such an arm existed it would be
  the headline — it does not exist here.

---

## WHAT IS WORTH OUR CPU NEXT (ranked; reason each earns its rank)

1. **PerLTQA wide-Z→SVD96 stage loss (-3.47 pp, 364 worse/77 better; HATA_YERI
   §6).** Reason: it is the only item that localises a NON-quantization,
   NON-readout loss with a committed direction (projection, not bits). Our
   quantization-layer programme (4/4 failed per digest) cannot touch it by
   construction. Cheapest next step is re-derivation from THEIR per-query
   artifact (results/raw_stage_per_query.csv) on seen data — no new fit —
   then a targeted projection-side intervention, NOT another threshold/rotation
   sweep (already in DO_NOT_REPEAT). Small CPU, new territory.
2. **FIKIR1's disclosed control set as regression harness, not the reranker.**
   Reason: the 15-cell (5 first-stages × rerank Variants + full-BM25) table on
   frozen cohorts is the first harness in programme history that ENFORCES the
   standing rule mechanically. Reuse the DESIGN (same-enhancement-to-rival +
   full-rival-alone) for every future "add a tool" proposal. Do NOT spend CPU
   on BM25-rerank itself (LME -0.33 kills it; LoCoMo +1.07 does not pay the
   351 MB/2.4 ms bill).
3. **B1 compact refactor — CONDITIONAL on our bottleneck being stored model
   state.** Reason: only passing gate in the batch (residual 1.3e-13 < 1e-8,
   10,266 top-10 identity claimed), 28–46% file shrinkage. But serving RSS
   barely moves and build peak rises — so promote ONLY if cold-store/transfer
   size is the constraint, with our-side equivalence replay first (their
   verifier = their implementer). No quality CPU;pure engineering replay.
4. **HIZ SIMD LUT recipe as engineering input (no quality campaign).** Reason:
   fair 1.7–1.9x prepare+score win over float32 SGEMV is real engineering, and
   end-to-end encoder-dominance tells us where NOT to optimise (scorer, not
   encoder, is ~10% of text→top10). Borrow the kernel; do not re-litigate
   qscale-vs-float quality (float still wins).
5. **KISITLI mechanism diagnostics (pair decomposition + rare-group
   concentration) as READING, not as runs.** Reason: the "both losses exist"
   decomposition (2,979 projection-lost vs 6,967 scale-lost pairs) is the
   batch's best hypothesis generator, and it is already computed — read the
   pairs file before designing anything. No new gamma/lambda CPU: the arm
   itself is negative and the plan's no-selection rule should stand.
6. **E4 tau-damping (ONERI §E4: q_j/√(σ²+τ²) for high-dim 192/384
   regression) — the only proposed-but-untested idea in the batch's lineage.**
   Reason: it targets the documented 192/384-dim regression
   (float_std192 57.78 → 384 54.49 PerLTQA) that nothing here explains. Ranked
   LAST because it is a hypothesis with the programme's worst prior (every
   scale tweak so far reversed across benches; 96-dim alpha sweeps already
   in DO_NOT_REPEAT) — run ONLY with FIKIR1-style symmetric controls
   (same damping to float + full-rival-alone) and a calibration split fixed
   BEFORE seeing results, per their own prescription.

Explicitly NOT worth CPU: 96×2 revival with the same Gaussian prototype;
B2-shared revival; any gamma sweep of KISITLI; BM25-rerank as a system;
re-proving qscale-vs-Hamming anywhere.

## Duplicates of work already in DO_NOT_REPEAT.md (do not file as new)

- qscale Hit@10 levels (LME 88.51 / PerLTQA 80.00 / RealTalk 49.65) reproduced
  in FIKIR1/HATA/HIZ — matches "qscale Hit@10 ... coordinator-reproduced
  EXACTLY ... do not re-run" (hit10/QSCALE.json + verify_incoming.json).
- Threshold/rotation lesson re-confirmed (HATA §7 sign(C/σ)==sign(C) identity;
  KONTROL_EKI §6–7 ITQ/rotation warnings) — already listed (threshold sweeps;
  ITQ-vs-random null; bit-balance feature note). Cite, don't rerun.
- Raw-text rebuild fidelity (HATA 78 archives, 0 bit changes, 249,390 scalar
  matches) overlaps "Raw-text rebuilds: 78 arch / 8313 queries, 0 sign-bit
  changes" (HATA_YERI report + DIAGNOSIS_SUMMARY.json entry) — same lineage,
  confirm no double-count.
- LoCoMo frozen-arm transfer (HIZ weighted 57.22 vs hamming 52.64,
  n=1531-cohort) sits under the "LoCoMo transfer of frozen arms ... NOT
  unseen" entry (hit10/LOCOMO.json + HIZ_GENELLEME_OZET) — keep the caveats,
  do not promote to confirmation.
- qsign_dstd-style "numeric-query readout" family (HATA/HIZ qscale columns)
  is adjacent to the "qsign_dstd ... NOT reproduced ... resolve the scorer
  mismatch first" entry — note the scorer here is qscale (C/σ-weighted sum,
  pinned definition C=Y-mean, σ docs-only), NOT qsign_dstd; no conflict, no
  merge.
- ONERI E0–E3 agenda items are now EXECUTED (E0→FIKIR1/HIZ cost arms,
  E1→B1, E2→Idea A, E3→B2) — move from "proposed" to the verdicts above; only
  E4 remains open (rank 6).
- KISITLI's IDF^p-vs-penalty distinction (subspace distance 2.78,
  coordinator-verified) does NOT duplicate the IDF^p arm — confirm as new
  negative, file once, no sweep.

## Honesty appendix (what I did and did not do)

- DID: read all four Turkish reports + KONTROL_VE_DENEY_EKI.md +
  ONERI_VE_DENEY_PLANI.md fully; recomputed every headline delta in §§1–5
  from the three OZET JSONs + HATA/HIZ OZET JSONs (python3, exact
  subtraction, shown inline); checked baseline levels against the four frozen
  anchors; cross-checked FIKIR1↔HIZ baseline consistency; quoted prespecified
  criteria verbatim from PLAN_BEFORE_RUN.json files (no paraphrase for the
  criterion itself).
- DID NOT: re-execute any pipeline; row-check per-query CSVs (levels only);
  open per-archive residual/gate files (isotropic/bit-constancy claims are
  THEIR-CLAIM with stated gates); re-derive bootstrap CIs (quoted as their
  exploratory intervals with their own caveats); read CHAT_TRANSCRIPT.md
  (1.4 MB, out of budget) or FINAL_SELF_AUDIT.json beyond scope — their
  self-audit is not relied upon anywhere above.
- If their numbers are right and ours wrong anywhere: the one place to look
  is RealTalk sign96 46.68 (their expected-tie) vs our frozen deterministic
  46.5248 — NOT an error on either side, different tie conventions, both
  labelled. No other anchor conflict found. No exit-0-only evidence was
  accepted as quality proof above (gates reported as gates, verification
  replays reported as author-checks, not independent audit).
