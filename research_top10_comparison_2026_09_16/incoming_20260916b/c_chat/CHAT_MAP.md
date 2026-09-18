# CHAT MAP — incoming gpt-6-pro session (transcript + planning docs)

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Reader-only product. I ran no experiments; every number below is THEIR-CLAIM
unless tagged VERIFIED-BY-ME (with how) or NO-ARTIFACT (with the file I looked
for). "They measured X" is not "X is true". Their self-audit
(FINAL_SELF_AUDIT.json: max_metric_error 0.0, 82128 top-10 checks) is a
self-check, not independent verification.

## 0. Anchor check (frozen numbers)

- VERIFIED-BY-ME (read values in their `LLMZIP_HATA_YERI_OZET_2026-09-16.json`,
  no re-derivation): RealTalk sign96 Hit@10 46.68, qscale 49.64539007...,
  standardized-cosine 48.5106... — match frozen 46.68 / 49.6454 / 48.51.
  Their `LLMZIP_HIZ_GENELLEME_OZET_2026-09-16.json` shows PerLTQA
  weighted/qscale 80.0 and LME 88.51 — match frozen anchors.
  So they measured OUR system, not something else, on these arms.
- qscale FR@3 anchors (22.41 / 53.24 / 54.27) and BM25 54.18: NOT verified by
  me (no per-query artifact opened for these). No contradiction seen.
- One live mismatch to flag: their HATA report lists
  `float_docs_std_binary_query` ("qsign_dstd") RealTalk Hit@10 50.35
  (transcript tool output line ~5122 also computes 50.355). Our MASTER_LEDGER
  says coordinator replay gives 49.50 (−0.85pp, NOT reproduced). Adjudication:
  BOTH can be honestly computed — the transcript shows a differently-defined
  scorer (std applied to docs, query binarized) than whatever our replay
  assumed. CONTRADICTS-OURS in the narrow sense; root cause is a scorer
  DEFINITION mismatch, not fabrication. Resolve the definition before citing
  either number. (DO_NOT_REPEAT.md already says "resolve the scorer mismatch
  first" — agree.)

## Q1. Decision timeline (stated reasons; post-hoc marks)

Session: 15 Eyl 21:19 → 16 Eyl ~20:30. ~40 turns. "Human" writes Turkish,
often pasting other-agent docs; "Assistant" executes.

1. 15 Eyl 21:19 — Handoff ingested. Standing rule adopted: verify from
   artifacts, touch nothing frozen/main. (Assistant, transcript ~266-408.)
2. 15 Eyl 21:25 — Human orders: re-run benchmarks + CPU/RAM. Reason: stated
   directly ("sen tekrar benchmarka sok, cpu ram kullanımını falan da
   incele"). Everything quantitative after this hangs off this order.
3. 15 Eyl 21:59 — Human: "yani bizimki daha iyi dimi" (ours is better, right?).
   Assistant REFUSES the frame: only PerLTQA shows real float gain; reports
   per-benchmark table instead. First evidence of non-sycophancy.
4. 15 Eyl 22:02 — Human orders lit-scan + brainstorm "how can it be best in
   every way". Assistant returns 3 candidates with explicit status labels:
   (a) calibrated scoring on same SIGN96 bits, (b) projector change,
   (c) learned encoder as SEPARATE line (frozen protocol forbids it in-task).
   Reason stated: keep frozen tasks untouched.
5. 15 Eyl 22:53 — Gram-approach side test; zh shard never ran because `head`
   closed the pipe (failure → re-ran zh only). Minor, disclosed.
6. 16 Eyl 09:38-10:11 — Threshold-shift idea (HUMAN proposes 2-bit thresholds
   at 09:54; assistant formalizes 2-stage test). Baseline reproduced exactly
   first (zero→sym 46.68, float_q 43.55 = HIT10.json sym/asym — transcript
   ~2113-2130). Result: median −1.43pp, random −24pp; learned thresholds best
   43.87 vs 46.68 (−2.81pp). DECISION (assistant, ~2183-2290): shelve
   thresholds, keep zero. **Made AFTER seeing results** — but it is a NEGATIVE
   decision (abandoning own idea), so post-hoc-selection risk runs the honest
   way. They correctly refuse to generalize ("tested-conditions failure", not
   "no better threshold exists").
7. 16 Eyl 10:23-10:31 — Pivot (human: "başka bir fikire mi yönelelim"):
   change the READER not the code → learned-decoder / asymmetric scoring
   (qscale) line. **After results** (threshold failure) — openly so.
8. 16 Eyl 11:03 — "hatanın yerini bul": HATA_YERI diagnostic. 78-arch raw
   rebuild, 0 bit changes of 142,656 doc bits, 249,390 scalar checks match;
   loss localized to (i) wide-Z→SVD96 projection (esp. PerLTQA profiles),
   (ii) float→sign/Hamming step. 500-refit plan cut to 90-arch panel + 19
   extras excluded from means (raw_refit_scope.json) — disclosed, not hidden.
9. 16 Eyl 13:06 — External adversarial audit pasted ("denetlettim incele").
   Assistant counter-review (DENETIM_KARSI_INCELEME.md): ACCEPTS qscale-vs-sym
   hit@10 replication; REJECTS generality (old asym already ≥ qscale on
   PerLTQA; FR@3 no-transfer on LME/RealTalk; nDCG-tie formula bug confined to
   nDCG). Grounded in re-aggregation (65,826 rows), not rhetoric.
10. 16 Eyl 13:51 — Human pressure: "en iyisi bizimki olmalı". Assistant holds:
    not best vs asym/float on PerLTQA/LoCoMo. (Transcript ~11953-12035.)
11. 16 Eyl 14:04-14:19 — Brainstorm → "1. fikirden başla dikkatli ol" → FIKIR1
    rerank pilot with PLAN_BEFORE_RUN.json written BEFORE outcomes (sha-pinned;
    transcript ~12801, ~13719). Genuine pre-commitment for M=50. Result: BM25
    rerank helps but float+same-rerank ties; no generality claimed.
12. 16 Eyl 14:55 — Second pasted doc (oracle-ceiling gate). Assistant computes
    ceilings (LME→92.62, RealTalk→61.30 FR@3@100) and RRF complementarity
    (CODE-only 49 / BM25-only 67 queries). Keeps ceiling labeled oracle.
13. 16 Eyl 15:10 — Other-LLM paste: rare-bucket table (341/70.7/85.0) + Bloom
    split failure (33.33/34.61; 32-bit sketch ≈5 distinct values/query).
    Human asks for math investigation → MATEMATIK_INCELEME with
    PLAN_BEFORE_TESTS.json pre-written (archive choice: first-3
    lexicographic LME ids — VERIFIED-BY-ME by reading the file; genuinely
    outcome-blind selection rule).
14. 16 Eyl 15:32 — Other-LLM self-correction accepted after THEIR check
    (majority→48.37%; truncation-share 26%/59%/82%; identity verified to
    1.07e-14 on 200 matrices): "İkisi de doğru. Hatalarımı kabul ediyorum."
    Additive-penalty family (`Z'Z+λD`, distance 2.78 from own idf^p arm —
    confirmed different family) ADDED to plan. **After results**, labeled
    exploratory. Honest.
15. KISITLI_CEZA pilot (24 LME + 30 PerLTQA + 10 LoCoMo): no cross-dataset
    winner; reported as such. Penalty nullspace counterexample (v_diff with
    Z·v=0 stealing a dimension) caught ANALYTICALLY before benchmarking —
    exemplary failure-prevention, in KONTROL_VE_DENEY_EKI.md.
16. 16 Eyl 16:29 — "tüm bulgu dosyalarını drive ve githuba ekle": Drive OK
    (28/28 sha-verified readback); GitHub PARTIAL (index commit c0df0f9 only,
    DNS failure for payload — DELIVERY_RECEIPT.json discloses "PARTIAL").
17. 16 Eyl 16:55 — c31719b audit pasted; HUMAN over-claims ("O kapı
    matematiksel olarak kapalı", "48 bayt gerekiyor" — transcript
    21307-21454). Assistant's INCELEME.md (same turn, ~21460+) REFUTES all
    three strong claims with counterexamples. **After results**, correction
    direction (toward weaker claim). This is the D1 event — see below.
18. 16 Eyl 17:36 — Human orders 12/24/48 measurement → GERCEK report:
    LME 52.47/61.48/61.75, PerLTQA 52.98/54.82/51.87, LoCoMo 35.11/41.21/44.15
    FR@3; matched BM25 57.14/60.14/42.87. DECISION (report + transcript
    23039): "24 bayt geliştirme referansı, 48 bayt LoCoMo alternatifi —
    bunlar sonuçları gördükten sonra belirlenen adaylar; doğrulanmış seçim
    kuralları değil." Explicitly post-hoc-labeled. Model-state total 9.95 GB
    vs 2.78 MB codes disclosed.
19. 16 Eyl 18:32+ — "alt ajanlarla beyin fırtınası": NO subagent tool exists
    in their environment (stated in ARASTIRMA_PLANI.md §Statü and transcript
    ~23084-23086; failure, disclosed, no fake multi-agent output). Manual lit
    scan → ONERI_VE_DENEY_PLANI.md / ARASTIRMA_PLANI.md proposals, no new
    benchmarks run under them.

Post-hoc-selection audit: three decisions made after seeing results — (6)
shelve thresholds, (14) add penalty family, (18) 24B/48B reference picks.
All three are EXPLICITLY labeled exploratory/post-result in the artifacts.
The dangerous direction (picking winners as confirmed) was refused each time
(thresholds: refused to generalize failure; penalty: no production claim;
24B: "evrensel optimum değildir"). Genuine pre-commitments exist where cheap
(PLAN_BEFORE_RUN / PLAN_BEFORE_TESTS sha-pins). No hidden HARKing found.

## Q2. Failures / abandoned (most useful section)

1. Threshold shifting — FAILED with numbers: median −1.43pp, random −24pp,
   learned best 43.87 vs zero 46.68 (−2.81pp, RealTalk). Cause per them:
   unsettled (scale-vs-information reading disputed); shelved correctly
   without over-generalizing. (Transcript ~2113-2290.)
2. SVD+Bloom budget split — FAILED: 96+0=49.65 → 80+16=33.33, 64+32=34.61,
   48+48=33.48. Cause decomposed (human 15:32 self-correction, transcript
   17462-17472): at 80/16 truncation only 26% of loss, FUSION design 74%;
   at 48/48 truncation 82%. Plus sketch defect: 32-bit Bloom ≈5 distinct
   scores/query → ranks by tie-break. (Matches our FINDINGS_DIGEST
   retraction of "truncation sole cause" — convergent.)
3. RealTalk raw rebuild — FAILED: 1.23 GB private-backup download HTTP 413;
   public metadata listed but bytes unfetchable (no network). Fell back to
   hash-verified cached replay; labeled as such everywhere. (Transcript
   ~6062, ~6209.)
4. Subagents — UNAVAILABLE: no tool in environment; proposals
   (AJAN_GOREV_TASLAKLARI.md) honestly marked drafts-for-later, never
   presented as executed. (ARASTIRMA_PLANI.md §Statü; transcript ~23084.)
5. GitHub full mirror — FAILED (DNS); index-only commit c0df0f9; Drive full
   payload verified. Disclosed PARTIAL in DELIVERY_RECEIPT.json.
6. 500-refit plan — CUT to 90-arch panel (109 completed, 19 excluded from
   means); make_report.py crashed once (status 1); numpy-int64 JSON
   serialization bug; 1.8e-15 bit-equality gate tripped then fixed by
   matching summation order (54/54 exact after). All logged in transcript
   (~6384, ~19668, ~14407). Exemplary error logging.
7. Transfer arms — PerLTQA_zh qscale NEGATIVE vs sym; LoCoMo weighted only
   +0.39pp vs asym_old (CI [−1.69,+2.26]); rank-transform beats qscale on
   PerLTQA (80.48 vs 80.00). Reported, not buried. (Transcript ~9541, ~9009.)
8. Penalty idea almost failed BEFORE benchmarking: unconstrained
   `Z'Z+λD` can select Z-nullspace direction (exact 8×4 counterexample,
   SymPy+NumPy verified) → constrained variant (Vr R) derived instead; still
   no cross-dataset win. (KONTROL_VE_DENEY_EKI.md §§3-5.)
9. Resisted post-hoc claim: alpha=2 gives RealTalk FR@3 +1.80pp but "alpha=2
   is not the claim" — explicitly NOT claimed (transcript ~9631-9633).

## D1. sum rho = k → "no better 96 directions" (RETRACTED by us)

THEIR-CLAIM (assistant, MATEMATIK_INCELEME.md §4 + transcript ~17314-17340):
identity derived independently (rho_i = H_ii, sum = k, verified 1e-14 on 200
matrices), mean 0.192 for N=500/k=96 — WITH the correct caveat inline:
"Bu %19,2 arama başarısı değildir... Bazı kayıtlar çok daha iyi, bazıları
çok kötü korunabilir" plus a same-frequency counter-pair where the rare
feature is dropped in one matrix and fully kept in the other (§5). They NEVER
drew the "no better choice" inference in the math docs; KONTROL_VE_DENEY_EKI
§1 and INCELEME §1 repeat the mean-only reading.
THEIR-CLAIM (human-pasted other-agent text, transcript 21326-21376): made the
FULL error — "hiçbir 96 boyut seçimi şansı geçemez", "tüm fikirlerimiz baştan
ölüydü", "O kapı matematiksel olarak kapalı", "48 bayt gerekiyor".
VERIFIED-BY-ME (read INCELEME.md §§1-3): their assistant CORRECTED it in the
same turn with THREE counterexamples: (i) first-96-coordinate-axes U gives
rho=1.0 to 50 priority rows, 0.1022 mean to rest, mean still 0.192
(UᵀU=I checked); (ii) Z=I_512 Hadamard pair: identical per-feature
preservation 96/512=0.1875 and identical total error 416, but Hit@1 25% vs
100% (collision group 4 vs 1) — preservation⇏retrieval; (iii) 2-D rotation
flips Hamming winner with identical subspace and cosines (0.99968755 /
0.02499609) — axis choice inside a subspace matters for sign codes.
Verdict: THEY AVOIDED the error in authored work and CORRECTED the pasted
version. Our retraction (coordinate-axes mean-0.1920 point) is the SAME
counterexample as their (i) — independent convergence, coordinator's version
cited first in our digest. If anyone "corrected first", it is their INCELEME
author vs the pasted text, not vs us; our positions now AGREE. Credit them
for catching it explicitly (INCELEME §6 "Son durum").

## D2. Rare/common bucket circularity

Do they acknowledge it? YES, repeatedly:
- Human 16:55 self-correction (transcript 21359, 21437-21441): "O bantta
  BM25 tanım gereği sıfır alıyor (sorguların %97,8–100'ünde)... 'sıfırdan
  büyüğüz' demişiz. Anlamsız." — full acknowledgment, in their words.
- INCELEME.md §5 "Sıradan/ortak-kelime grubu": gold-conditioned grouping is
  diagnostic, not a runtime rule; no general-superiority or routing claim
  follows; "anlamlılık otomatik" rejected.
- MATEMATIK_INCELEME.md §2: grouping is "sonuç-bazlı tanısal", not trainable
  routing; §7/§10 design keeps FR@3-over-all-questions primary, rare band
  secondary.
Dependence check: their size-ladder table IS rare-band-only
(PerLTQA 72.15/65.17/70.12/72.61; LoCoMo 58.70/24.82/32.96/40.13/45.17 —
quoted in INCELEME §4 from the coordinator reply, NOT re-measured by them),
and the human drew "48 bayt gerekiyor" from it — but the assistant's INCELEME
quarantines it the same turn: +0.46pp ns ≠ equivalence/minimum proof;
LoCoMo full-Z still −13.53pp behind BM25 so "budget-only" doesn't generalize;
384-dim scoring branch (float vs sign vs qscale) undisclosed → "72.61'i
48 baytlık çalışan koda atfetmiyorum". GERCEK report decides on ALL-question
FR@3. So: acknowledged AND fenced. The degenerate half supports no
conclusion in their final position. NOTE: the "%97,8–100" figure itself is
NO-ARTIFACT (human message only; I found no .md/.json computing it —
searched all *.md and extracts for "97,8").

## D3. Handicapped BM25 (frozen tokenizer ~3pp; k1/b not neutral)

Full argument as found:
- k1 mismatch is DOCUMENTED: "Prior BM25 k1=1.2; pasted ceiling BM25 k1=1.5.
  Not silently interchangeable." (transcript ~15613; repeated ~15814:
  "Aynı isimle anılmaları aynı uygulama oldukları anlamına gelmiyor.")
- Human 16:55 claims: matched-tokenizer BM25 +3pp ("LoCoMo fark −13,88
  değil −17,2") and storage 213 MB not 64 MB (transcript 21360-21361).
  Both figures are NO-ARTIFACT: no computation in transcript history, and
  grep for "17,2" over all polished reports + INCELEME returns ZERO hits
  (only CHAT_TRANSCRIPT:21360). Name the gap honestly.
- What IS artifact-backed: INCELEME §5 "BM25 ve maliyet" — their 63.982 MB
  was a stats JSON, not a full index/RSS; 213-vs-64 MB compares different
  objects unless proven same; post-hoc best params need fresh validation.
  GERCEK report §4 discharges half the obligation: same-tokenizer,
  pre-fixed BM25 FR@3 measured (LME 57.14 / PerLTQA 60.14 / LoCoMo 42.87 vs
  best codes 61.75/54.82/44.15). ONERI E0 keeps the other half OPEN (matched
  full cost profile never measured).
- Textbook k1/b: ARASTIRMA_PLANI §6 + ONERI E0 require re-matching tokenizer,
  stopwords, n-grams, IDF, k1/b, ties query-by-query before calling BM25S
  "the same BM25" — i.e., defaults are NOT neutral. Agree; this matches our
  caution. Directionally they are RIGHT that our lexical baseline was
  under-cooked; the specific "+3pp/−17.2" magnitudes are UNVERIFIED.

## D4. Tie convention (−2.79 → −0.45 friendliest)

Their stated position (INCELEME §5 "Eşit puanlar"; DENETIM §5.3; transcript
11061-11065; pasted audit §§5/W-tables ~9556-9590):
- Uniform-tie expectation (hypergeometric closed form) is UNBIASED, not
  punitive (jitter test: +0.09/−0.12/−0.30pp ns). Giving sym the BEST
  tie-break is a harsher stress test / different estimand, NOT a bias
  measurement of the original.
- Oracle-break results: PerLTQA +2.47 SIG and LME +2.13 SIG survive; RealTalk
  +1.13 [−1.41,+3.56] ns does not. So "RealTalk leg not shown robust" is
  correct; "effect debunked/inflated-everywhere" is NOT licensed.
- Consistency with us: FULLY CONSISTENT in principle — friendliest break
  shrinks deltas toward zero, exactly our −2.79→−0.45 pattern. They would
  endorse our row's DIRECTION while insisting on our wording: "no robust
  superiority shown under oracle break", not "the effect was tie artifact".
- Provenance warning: the SPECIFIC "−2,79/−0,45" pair is NO-ARTIFACT on
  their side — grep finds it ONLY at CHAT_TRANSCRIPT:21362 (human message);
  zero hits in every polished .md and none in transcript tool outputs
  (the 14681 "2,79" is an unrelated PerLTQA column). So their material
  contains NO independent computation of our LME tie row. Do not cite them
  as confirming our −0.45.
- Method hygiene VERIFIED-BY-ME (read transcript ~12791, ~14349): their new
  pipelines use deterministic SHA256(doc-ordinal) priority while replaying
  historical uniform expectations separately (263,304 scalars re-matched) —
  disclosed, unmixed. Good practice; matches ours.

## Q3. Where they disagree with us — adjudication

1. "Projection bottleneck yok" (our handoff §3d: SIGN96 86.08 ≈ Z 86.1) vs
   their HATA panel (wide-Z→SVD96 +3.89pp float on 180 LME q; PerLTQA
   profile losses). BETTER EVIDENCE: SPLIT. Their loss exists in the FLOAT
   path they measured; our no-bottleneck holds for the SIGN scorer at hit@10
   on LME. Different scorer+metric slices — no genuine contradiction once
   scoped. Their scoping discipline here is GOOD; adopt it.
2. "10 bytes free on LME" (−1.11pp ns) vs their "anlamlı fark yok ≠
   eşdeğerlik" (transcript ~389; BENCHMARK report §: SIGN80 84.97,
   "ücretsiz sonucu çıkarılamaz"). THEY ARE RIGHT methodologically, and our
   digest already treats RealTalk as exploratory-wide-CI. No number dispute.
3. qscale novelty vs old asym: their table (DENETIM §1: PerLTQA qscale−asym
   FR@3 −0.29; LME +3.62?? vs sym +0.06) vs our ledger (asym +4.63pp FR@3
   over SIGN on PerLTQA; asym LOSES on LME −3.56). AGREE on substance: qscale
   ≠ general advance; benchmark sign-flips rule. Their "alpha=1 table
   contradiction" catch (LME best IS alpha=1 vs claim "never best") is a
   legitimate hit on the pasted audit, VERIFIED-BY-ME as internally stated
   (transcript 11071-11073); the underlying table itself is THEIR-CLAIM from
   the other agent, not verified here.
4. Cost framing: their "96 bytes global" critique (two separate 1-way tests
   ≠ combined design; per-benchmark pooled std ≠ universal vector) is
   CORRECT logic and matches our stance. No dispute.
5. If their numbers are right and ours wrong: the only candidate is qsign
   50.35 vs our 49.50 replay — adjudicated above as DEFINITIONAL, §0. Their
   anchors otherwise reproduce ours to 4dp. No silent correction of ours
   needed; one open definition to pin down.

## Q4. Undischarged obligations (we may inherit)

1. Combined global-std + 1-byte test (the "96-byte" design) — never run as
   one arm. (DENETIM §5.1.)
2. 384-dim ladder scoring-branch disclosure (float? sign? qscale?) + same
   3-branch protocol (float / packed-Hamming / packed-qscale) on fixed
   cohort, N<384 without cohort-switching. (INCELEME §6.)
3. Char on/off 2×2 with LSA fixed (12.25pp attribution needs it).
   (INCELEME §5.)
4. E0: matched BM25S vs 24B qscale vs float192 FULL cost profile
   (CPU/RSS/USS, files, setup/update, hot+cold, 1/10/100 archives). Quality
   half done; cost half open. (ONERI E0; transcript ~23326.)
5. Shared-encoder line (Hashing/CBE/Potion) with dev-only fit + name/date/
   number stress tests. Proposed only. (ARASTIRMA_PLANI §4; ONERI E3.)
6. Tau-shrinkage diagnostic for 192/384 regression (proposal, no run).
   (ONERI E4.)
7. nDCG versioned fix of frozen outputs (their bug proof: exact-count max
   err 1.12e-16 vs quoted formula diverging in 100/302 cases). (DENETIM §§3,6.)
8. LoCoMo n=1531 vs 1535 + 156 unapplied gold corrections. (Both sides note
   it; nobody resolved it.)
9. RealTalk raw rebuild (blocked on HTTP 413).
10. Independent audit of AVX-512 speed pack + LoCoMo transfer + 12/24/48
    pack (their own chemistry: "dış bağımsız denetçi onayı yok" — GERCEK
    §sonuç; HIZ report; DENETIM §6).
11. Penalty family: gold-blind R,w rule on held-out archives; rowspace
    diagnostics (||Zv||², eff. rank, bit constancy). (KONTROL §7.)

## Q5. Report-vs-transcript discrepancies

- Transcript-ONLY (no polished report): RealTalk rare-bucket table
  (24/224/116/341; 70.7 vs 85.0 +14.4 — human paste 15824-15843 from the
  OTHER agent; MATEMATIK_INCELEME §2 checks its ARITHMETIC only, explicitly
  "ham-kayıt doğrulaması değildir"). Absent from all LLMZIP_*_RAPORU. Treat
  as incoming claim, not their measurement. (CONTRADICTS nothing of ours
  numerically, but note our digest's rare band uses a different,
  max-IDF-shared definition: 24/224/116/341 happens to MATCH our counts
  24/224/116/341 — VERIFIED-BY-ME by reading FINDINGS_DIGEST §table. Same
  counts, so the table is consistent with ours; the +14.4 interpretation is
  theirs to fence, which they did.)
- Transcript-ONLY, no artifact at all: −2.79→−0.45 (21362), −17.2/+3pp
  BM25 (21360), 97.8–100% zeros (21359). Three human-message numbers with no
  computation history and no report landing. NO-ARTIFACT ×3 (files looked
  for: every *.md top-level + extracted AUDIT3/NADIRLIK/YOL_HARITASI trees).
- Report-ONLY (no transcript experiment): 12/24/48 full tables
  (LME/PerLTQA/LoCoMo FR@3 + 9.95 GB state + RSS) — actually HAVE transcript
  history (17:36 order → tool runs ~22822-23045), so NOT orphaned; the gap
  is external audit, openly stated.
- Quietly DROPPED from reports (good drops): human's "48 bayt gerekiyor"
  (21449), "kapı kapalı" (21370), "SVD atıyor" (21317) — all contradicted by
  the assistant's same-turn INCELEME and absent from polished reports.
  Self-correction worked.
- Consistent both places (NOT dropped): qsign_dstd 50.35 (tool output ~5122
  → HATA report line 50); RRF +5.67 CI [+3.23,+8.20] (transcript ~15248 →
  FIKIR1 report); 263,304 replayed scalars; alpha-LME contradiction flag.
- Perfect-selector 90.21/86.07/54.98: mentioned once as UNVERIFIED
  (transcript ~1054, "henüz doğrulamadım"); I found no landing in the four
  polished reports I grepped (BENCHMARK/FIKIR1/HATA/HIZ) — treat as
  unconfirmed, not as dropped evidence. NO-ARTIFACT (looked for: those four
  reports; full-text grep "90,21" hit only transcript).

## Bottom line for the coordinator

1. D1: they derived the identity, never made the error in authored work,
   and refuted the pasted over-claim with three counterexamples (one
   identical to ours). Positions converged.
2. D2: acknowledged in full ("Anlamsız"), fenced out of conclusions.
3. D3: direction right (matched BM25 control measured: PerLTQA 60.14 beats
   24B 54.82), magnitudes (+3pp/−17.2) unartifacted; cost half still open.
4. D4: principle identical to ours (oracle break = harsher estimand, not
   bias proof); our specific −2.79/−0.45 has no artifact on their side.
5. Most valuable: their failure log (thresholds, fusion-blame split,
   nullspace-trap catch, zh-transfer negative) + obligation list (§Q4) are
   import-ready; their anchors reproduce ours to 4dp except one definitional
   mismatch (qsign_dstd) to resolve before citing.
