[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# llmzip — referee report (decision round, not research round)

Basis: the coordinator's decision brief dated 2026-09-16 only. [BRIEF]
Method: no web, no paid APIs, no git, no pip in this turn. [CHECKED: process claim for this turn; no network/package/git commands issued]
Filesystem check: workspace root listed before writing; it contained 0 tracked files (`.` and `..` only). [CHECKED: `ls -la` on the workspace root in this session; see session log, not a retrieval measurement]
Recomputation: none — every number below is quoted or arithmetically derived from the brief with the derivation shown. No new benchmark was run. [CHECKED: no benchmark command issued this turn]

Tag key (every factual claim carries one): [BRIEF] = from the decision brief;
[CHECKED] = I recomputed it — how + file cited; [RECALLED] = literature memory, confidence stated, no web access;
[CONJECTURE] = my hypothesis + its falsifier. Proposed decision thresholds are labelled
[PROPOSED — not a measurement] and are not claims.

Referee stance: I do not advocate continue / pivot / stop. I price information per unit cost and
give the owner a numeric rule whose inputs are already mostly in hand. [CONJECTURE: the three
costings below are the only cheap decisive work left; falsifier: any of them requires a fresh
full SVD sweep over all archives on the owner's hardware]

---

## 1. Open-question table

“Cheap” = reuses stored artifacts, no new SVD/projection sweep, single-CPU minutes to hours.
“Expensive” = new representation sweep, new human adjudication, or a search over a space with a
0-for-N record. “Changes what we do” = a yes answer would move the stopping rule in §5.

| ID | Genuinely open question | Cheap / expensive | Would the answer change continue/narrow/stop? |
|----|-------------------------|-------------------|-----------------------------------------------|
| Q1 | Does any code ≤48 B/doc beat fairly-tokenized, fairly-parameterized BM25 on gold retrieval? [BRIEF: coarse BM25 55.32 vs fair BM25 61.70 on RealTalk Hit@10, +6.38 pp to BM25; 48 B code 57.87 loses to fair by 3.83 pp] | Cheap (rescore only, §2) | YES — directly drives the stopping rule |
| Q2 | Corrected PerLTQA ladder slope under k<n per archive? [BRIEF: current 52.98 → 54.82 → 51.87 falls; cause solved as rank overflow: 8 of 30 archives hold <384 docs, median 407 min 293, effective ranks 293–381 covering 26.8% of queries] | Cheap (8 archives only, §3) | PARTLY — removes a false law; does not by itself rescue competitiveness |
| Q3 | Does first-stage code quality survive a text reranker? I.e. does code+rerank beat BM25-alone, and does strong-vs-weak first stage matter post-rerank? [BRIEF: LME worse-first hamming96 53.86 ends 58.23, beating better-first qscale96 54.27→57.70; net code contribution −0.33/+0.33/+1.07 pp; rerank needs 76× text + 0.9–1.5× index; 14.9→17.6 ms vs 0.14 ms plain index] | Cheapest (reuse stored top-50s, §4) | YES — a “no” invalidates the premise even if Q1/Q2 look kind |
| Q4 | Is there a feature mix (e.g. word-only, no projection) competitive at ≤48 B? [BRIEF: RealTalk float-cosine no-projection word-only Hit@10 56.03 FR@3 31.19 vs full-Z 47.80/28.07; char+LSA costs 8.23 pp; word-only 56.03 beats the 24 B code 55.32 outright; auditor found char −12.25 pp rare-bucket on LoCoMo] | Cheap (ablation rescore, no new codes) | YES, but only via §5 narrow-gate — must beat *fair* BM25 (61.70), not the coarse one |
| Q5 | Is there any quantization/threshold beyond sign codes that helps? ITQ fails 4/4 [BRIEF: −2.27 pp RealTalk, −0.13 PerLTQA; rotation damage r=−0.78 with size; small −6.56 pp, large −23.13 pp; rotation costs 3.4–7.5× payload; sign(C/σ)==sign(C), 0 of 63,552 bits change [BRIEF]] | Expensive (open-ended search, 0-for-4 record) | NO unless Q1 first passes — do not fund before Q1/Q3 |
| Q6 | Is there a universal weighting (IDF^p successor / adaptive per-archive)? [BRIEF: IDF^p +4.78 pp FR@3 SIG rare-band RealTalk but −1.76 PerLTQA SIG; component shift +1.58 SIG PerLTQA, harmful RealTalk; programme regularity: no arm has EVER won on both benchmarks simultaneously] | Expensive (per-archive tuning × cross-benchmark validation) | NO as a universal claim — at best a single-slice narrow (see §5) |
| Q7 | LME channel ablation outcome (still running, 322/470) [BRIEF] | Cheap (finish the run) | Only as a tiebreaker for Q4; standalone it changes nothing |
| Q8 | What is valid LoCoMo gold, and does the LoCoMo rise survive it? [BRIEF: LoCoMo 35.11→41.21→44.15 rises, but gold is disputed] | Expensive (human adjudication, not compute) | NO before Q1/Q3 decide — disputed gold cannot rescue a programme that loses on undisputed benchmarks |
| Q9 | Is there a no-text deployment where 12–48 B must suffice and BM25 is inapplicable? | Cheap (owner product answer, not an experiment) | YES — the only non-empirical decider: if no such deployment exists, Q1+Q3 losses are terminal |

Detail per option (each carries action + prespecified criterion + honest cost + strongest failure reason):

- Q1 → see §2.
- Q2 → see §3.
- Q3 → see §4.
- Q4 — Next action: freeze one word-only arm (no projection, float cosine) plus one word+LSA-no-char arm; score RealTalk + PerLTQA with the *fair* tokenizer/BM25 from §2 as the comparator. [BRIEF numbers to beat: fair BM25 61.70 RealTalk Hit@10; word-only currently 56.03] Prespecified criterion [PROPOSED — not a measurement]: word-only (or variant) beats fair BM25 by ≥+2.0 pp FR@3 with CI excluding zero on RealTalk AND PerLTQA-corrected, at zero projection cost. Honest cost [CONJECTURE + falsifier]: tens of minutes rescore, no SVD; falsified if re-tokenization forces a full re-parse exceeding 4 CPU-hours on the owner's box. Strongest reason it fails: word-only 56.03 already trails fair BM25 61.70 [BRIEF, both numbers], so the gap to close is ~5 pp, and the brief's regularity (no arm wins both benchmarks [BRIEF]) predicts a RealTalk-only win at best.
- Q5 — Next action: single shifted-threshold arm only (global bias sweep on frozen C; no rotation, since rotation is 0-for-4 [BRIEF] and per-axis scaling provably cannot change a bit [BRIEF]). Criterion [PROPOSED]: beats sign code by ≥+1.5 pp FR@3 SIG on both RealTalk and PerLTQA-corrected. Cost [CONJECTURE]: moderate (threshold sweep is cheap; the validation across archives is not). Strongest reason it fails: the only mechanism that can change bits after scaling is rotation or shifted thresholds [BRIEF], and rotation made balanced-but-worse bits while costing multiples of the payload — there is no reason thresholds differ, and the search is unbounded.
- Q6 — Next action: none until Q1 passes; if funded, one prespecified adaptive rule (e.g. per-archive rare-mass switch) frozen before running. Criterion [PROPOSED]: wins on BOTH benchmarks simultaneously (breaks the 0-for-history regularity [BRIEF]). Cost: expensive (tuning × validation). Strongest reason it fails: every prior weighting flipped sign across benchmarks [BRIEF] — the base rate for “universal” is zero.
- Q7 — Next action: let the 322/470 run finish; freeze analysis before looking. Criterion [PROPOSED]: channel ranking replicates the RealTalk word>full-Z ordering with CIs excluding zero. Cost [CONJECTURE]: sunk + small. Strongest reason it fails: it answers “which channel hurts” (already known: char [BRIEF]), not “does any ≤48 B code beat fair BM25.”
- Q8 — Next action: owner-adjudicated gold sample before any rescore. Criterion [PROPOSED]: ladder slope recomputed on adjudicated gold keeps a monotone rise with CI excluding flat. Cost: expensive human time. Strongest reason it fails: even a clean rise does not answer Q1/Q3 on undisputed benchmarks.
- Q9 — Next action: owner states in one sentence whether a text-free deployment exists. Criterion: yes/no. Cost: zero compute. Strongest reason “narrow” still fails: rerank (§4/E) needs the 76× text plus index [BRIEF] — a text-free deployment cannot use the reranker that currently supplies the only competitive numbers, so it must win first-stage outright against fair BM25, which it currently does not.

---

## 2. Costing: the fair-baseline re-run (highest priority — verify or refute)

Why it is priority: every historical “we beat BM25” line used the coarse baseline [BRIEF], and the
fair tokenizer alone is worth +6.38 pp RealTalk Hit@10 (55.32→61.70) [BRIEF], flipping 48 B from
+2.55 to −3.83 [BRIEF]. No claim about competitiveness survives without this table.

Exactly what must be re-run:

1. Freeze and commit: tokenizer (`\b\w\w+\b`, 1–2 grams, stopwords removed) [BRIEF]; BM25
   parameters — report BOTH textbook k1=1.2/b=0.75 and the audit-flagged k1→0,b=0 variant
   (42.11 vs 37.67 on LoCoMo [BRIEF]) so “fair” is auditable, with textbook as primary.
2. Re-tokenize + rebuild the inverted index for RealTalk (10 archives, 705 queries, 8,944 docs
   [BRIEF]), PerLTQA (30 archives [BRIEF: “8 of 30”]), and LoCoMo; reuse the frozen eval script
   and frozen production anchors (k=96 reproduces anchors to −0.0000 [BRIEF]).
3. Rescore BM25 only — no new SVD, no C kernel, no new codes. Recompute Hit@10 and FR@3 deltas:
   every code arm (12/24/48 B) minus fair BM25, per benchmark, with the same CIs used for the
   −2.95 CI [−3.87,−2.01] SIG call [BRIEF].
4. Publish one table: rows = benchmarks, columns = coarse-BM25 delta vs fair-BM25 delta, so the
   audit trail shows which historical wins flip sign.

- Prespecified success criterion [PROPOSED — not a measurement, decided before running]: the
  “competitive” claim survives ONLY IF at least one code arm ≤48 B beats fair (textbook) BM25
  with the 95% CI excluding zero on BOTH RealTalk and PerLTQA-corrected on FR@3 (primary) with
  Hit@10 lower-CI > −1.0 pp as guardrail. Anything less (one benchmark only, Hit@10 only, CI
  including zero) = refuted as a general claim; single-slice survivals fall to the §5 narrow gate.
- Honest cost [CONJECTURE + falsifier]: minutes to low tens of minutes on one CPU — sparse
  rescore only. Basis: plain inverted-index latency 0.14 ms [BRIEF] bounds per-query scoring;
  no projection/rotation payload (3.4–7.5× [BRIEF]) is touched. Falsifier: a timed dry run on one
  RealTalk archive (re-tokenize + index + score) exceeding 30 minutes wall-clock on the owner's
  hardware refutes “minutes”; exceeding 4 CPU-hours total refutes “cheap.”
- Strongest reason it fails (as a rescue): it will likely CONFIRM the loss rather than refute it —
  the only measured fair point is already −3.83 pp Hit@10 at 48 B [BRIEF], and word-only-no-projection
  (56.03) also trails fair (61.70) [BRIEF, both numbers]. A second failure mode: the rerun passes on
  one benchmark and revives cherry-picking, which is why the criterion demands both benchmarks
  (regularity: no arm has ever won on both [BRIEF]).

---

## 3. Costing: the k<n ladder (PerLTQA redo with k = min(k_target, n−1))

What is wrong: PerLTQA archives are small (median 407, min 293 [BRIEF]); 8 of 30 hold <384 docs
[BRIEF]; surplus dims are constant-filled (effective ranks 293–381, 26.8% of queries [BRIEF])
while full 48 bytes are charged [BRIEF]. Standardized arms divide by σ≈0 and are punished;
unstandardized arms (asym rises 53.71→57.30→58.03; float_raw 55.03→58.55→60.43 [BRIEF]) are immune
— hence standardized arms fall (qscale 52.98→54.82→51.87; hamming; float_std [BRIEF]) while
unstandardized rise on identical subspaces [BRIEF]. Honest rule: k<n per archive; fixed global k
is wrong for heterogeneous archives [BRIEF].

Exactly what must be re-run:

1. Per-archive cap k′ = min(k_target, n−1) for the 8 violating PerLTQA archives [BRIEF]; truncate
   stored subspaces/codes (no fresh full SVD sweep if caches allow; else SVD only on those 8).
2. Rescore BOTH one standardized arm (qscale) and one unstandardized arm (asym or float_raw) so
   convergence of the two families confirms the defect is gone.
3. Republish the PerLTQA ladder (Hit@10 + FR@3) with per-archive k′ documented; keep RealTalk and
   LoCoMo ladders untouched (RealTalk 49.65→55.32→57.87 Hit@10, 22.41→29.75→32.79 FR@3 [BRIEF];
   LoCoMo rises [BRIEF] but gold disputed [BRIEF]).

- Prespecified reading of each outcome [PROPOSED — decided before running]:
  (a) PerLTQA rises (all three arms, CI excluding flat) → defect confirmed as the cause of the
  fall; the “bits beyond 24 B do not help” law is retracted as artifact. (b) Flat within CI →
  diminishing returns exhaust at ~24 B under honest accounting. (c) Still falls on unstandardized
  arms too → real capacity law, not a scorer artifact, and the strongest pro-stop evidence in the
  ladder. All three readings must be reported against fair BM25 (§2), not against the 12 B point.
- Honest cost [CONJECTURE + falsifier]: cheap — 8/30 archives, reuse of cached TF-IDF/SVD where
  stored; minutes to ~1 hour. Falsifier: if no subspace cache exists and 8 fresh SVDs exceed the
  owner's cheap-budget wall-clock, report it as expensive and do NOT silently substitute a cheaper
  approximation.
- Strongest reason it disappoints: the ladder ALREADY rises on RealTalk and LoCoMo [BRIEF] — a
  corrected PerLTQA rise adds tidiness and kills a false law, but buys ZERO competitiveness unless
  §2 flips. If PerLTQA-corrected still trails fair BM25, the programme paid for a cleaner loss.
  Do not fund this before §2 unless the 8-archive truncation is nearly free.

---

## 4. Costing: the rerank question (could invalidate the premise — do this cheapest)

What is at stake: the same BM25 text reranker on top-50s inverts first-stage order on LME
(worse-first hamming96 53.86→58.23 beats better-first qscale96 54.27→57.70 [BRIEF]) and the code's
net over plain BM25 alone is −0.33/+0.33/+1.07 pp [BRIEF] — while reranking demands the 76× raw
text plus 0.9–1.5× index and 14.9→17.6 ms vs 0.14 ms [BRIEF]. If first-stage quality does not
survive reranking, better codes are worthless wherever text is available.

Cheapest decisive design (no new codes, no new first-stage retrieval):

1. Reuse stored artifacts: per-query top-50 lists for (i) plain BM25 first stage, (ii) weak code
   first stage (e.g. hamming96), (iii) strong code first stage (e.g. qscale96 or best ≤48 B arm).
   Apply the IDENTICAL BM25 text reranker to each top-50 [BRIEF: same reranker is the control].
2. Report three post-rerank FR@3 numbers (primary) + Hit@10 guardrail, with CIs: BM25-alone(+rerank),
   weak-code+rerank, strong-code+rerank; plus the two deltas: (strong−weak | post-rerank) and
   (best code+rerank − BM25-alone(+rerank)).
3. Depth sensitivity: repeat at top-20 and top-100 by truncation/extension ONLY if the top-50
   result is within ±1 pp of the gate (else report top-50 alone and stop — do not buy precision
   the decision does not need).

- Prespecified criterion [PROPOSED — not a measurement, frozen before running]: first-stage
  quality is DECISIVE only if BOTH hold post-rerank: (a) strong−weak ≥ +1.0 pp FR@3 with CI
  excluding zero (quality survives the reranker), AND (b) best code+rerank − BM25-alone(+rerank)
  ≥ +1.0 pp FR@3 with CI excluding zero (the code earns its 76× text + index + latency cost
  [BRIEF]). If either fails — especially if the LME inversion replicates (worse-first ends better
  [BRIEF]) — the premise “a better 12 B code buys retrieval” is refuted wherever the reranker's
  text is available. Single-number shortcut: if best code+rerank − BM25-alone ≤ +0.5 pp, stop
  debating first stages.
- Honest cost [CONJECTURE + falsifier]: cheapest of the three — pure re-sorting of 50 docs/query
  (RealTalk: 705 queries × 50 [BRIEF]) with the existing scorer. Minutes. Falsifier: if stored
  top-50s are missing for any arm, the cost jumps to a re-retrieval and this ceases to be cheapest —
  then run BM25-alone(+rerank) vs best-code+rerank only and defer strong-vs-weak.
- Strongest reason it fails (as an experiment): the reranker is the SAME BM25 family as the
  baseline [BRIEF] — a weak/shared reranker can both dissolve real first-stage differences AND
  flatter BM25-first-stages by construction. A different (stronger) reranker could restore or
  further erase gaps. Mitigation is prespecified: the gate compares code+rerank against BM25-alone
  under the SAME rerank budget, so reranker weakness cannot fake a code win — but it can fake a
  code loss. A loss here is therefore necessary-but-not-sufficient for stop; pair it with §2.

---

## 5. Stopping rule (numeric, checkable — apply at the next checkpoint after §§2–4)

Primary metric: FR@3. Guardrail: Hit@10. Comparator: fair (textbook k1=1.2/b=0.75) BM25 from §2
[BRIEF for tokenizer/params]. Benchmarks: RealTalk + PerLTQA-corrected (k<n); LoCoMo excluded
from the gate while its gold is disputed [BRIEF]. CIs: the same 95% method behind the
−2.95 CI [−3.87,−2.01] SIG call [BRIEF].

- CONTINUE the full programme ONLY IF all four hold [PROPOSED — not measurements]:
  C1. Some code arm ≤48 B/doc beats fair BM25 on FR@3 by ≥ +2.0 pp with 95% CI excluding zero
      on BOTH RealTalk AND PerLTQA-corrected.
  C2. The same arm's Hit@10 lower CI is > −1.0 pp vs fair BM25 on both (no Hit@10 collapse; cf.
      LME 384-worst Hit@10 dip 88.72→89.15→86.60 alongside FR@3 gains [BRIEF]).
  C3. Best code+rerank beats BM25-alone (same rerank budget) by ≥ +1.0 pp FR@3, CI excluding
      zero (§4 gate).
  C4. The winner is the SAME arm/family on both benchmarks (breaks the never-won-both regularity
      [BRIEF]).
  Next action if met: fixed-budget scale test only (no new families). Cost of checking C1–C4:
  §§2–4 only (cheap). Strongest reason CONTINUE fails: C1–C4 jointly have base rate zero given
  current deltas (−3.83 pp Hit@10 at 48 B vs fair [BRIEF]; net rerank −0.33/+0.33/+1.07 [BRIEF]).

- NARROW to one capped slice ONLY IF idol: EITHER (N1) a prespecified slice (rare band or one
  benchmark) shows ≥ +2.0 pp FR@3 SIG over fair BM25 AND survives §4 at ≥ +1.0 pp, with the slice
  frozen before running; OR (N2) the owner asserts a text-free deployment (Q9=yes) AND some code
  ≤48 B beats fair BM25 first-stage outright by ≥ +2.0 pp SIG on that deployment's benchmark(s).
  Cap: one slice, one quarter, no new quantization families (Q5/Q6 stay unfunded). Strongest reason
  NARROW fails: every prior slice win flipped sign across benchmarks (IDF^p +4.78 vs −1.76;
  component shift +1.58 vs harmful [BRIEF]) — a single-slice win is the expected shape of noise
  under the never-won-both regularity [BRIEF].

- STOP otherwise. In particular STOP IF any of: (S1) no ≤48 B arm beats fair BM25 on both
  benchmarks (C1 fails); (S2) §4 gate fails (code+rerank − BM25-alone < +1.0 pp or strong−weak
  post-rerank ≈ 0 / inverted as in LME [BRIEF]); (S3) PerLTQA-corrected is flat-or-falling on
  unstandardized arms (real capacity law, §3c). Next action if STOP: publish the negative result
  (fair table + k<n correction + rerank inversion) and release compute. Cost of STOP: zero further
  benchmark spend. Strongest reason STOP is wrong: Q9 — a genuine text-free, index-free deployment
  values bits/doc over FR@3-vs-BM25, and §§2–4 do not price that product niche; the owner, not the
  benchmarks, decides Q9.

Readout on today's [BRIEF] numbers (not a new measurement — applying the rule to quoted inputs):
RealTalk 48 B vs fair BM25 is −3.83 pp Hit@10 [BRIEF] (C1/C2 area: failing); rerank net
−0.33/+0.33/+1.07 pp [BRIEF] sits at/below the +1.0 gate (C3: failing on 2 of 3, borderline on 1);
never-won-both holds [BRIEF] (C4: failing); word-only 56.03 trails fair 61.70 [BRIEF, both quoted]
(N-path: failing without a new slice). Under this rule the current readout is STOP unless Q9
(text-free deployment) affirmatively reframes the comparator. [CONJECTURE: §§2–4 confirm rather
than overturn this readout; falsifier: any §2/§3/§4 prespecified gate met as written]

---

## 6. Worthless list (interesting, cheap-or-not, but changes nothing)

1. Rotation-damage mechanism (r = −0.78 size correlation; −6.56 vs −23.13 pp; balance-vs-quality
   anti-correlation) [BRIEF]. Worthless because rotation is 0-for-4 and costs 3.4–7.5× payload
   [BRIEF] — why a losing transform loses does not move C1–C4.
2. Repair details of the retracted mean-ρ proof (96 coordinate axes ρ=1/0, mean 0.1920
   counterexample [BRIEF]). Worthless: already retracted; re-proof changes no retrieval number.
3. “Dimensions are not bytes” terminology cleanup [BRIEF]. Worthless beyond preventing the next
   misreading; no gate depends on it.
4. SVD rare-term survival (rare df=1 at 0.94× null vs common df≥50 at 3.79× [BRIEF]) beyond the
   correction “lifts common above chance rather than discarding rare” [BRIEF]. Worthless: no
   retrieval gate conditions on this ratio.
5. Second-order BM25 tuning past the fair point (k1→0,b=0 42.11 vs 37.67 LoCoMo [BRIEF]) once §2
   fixes textbook-primary + audit-variant reporting. Worthless: the +6.38 pp tokenizer flip
   [BRIEF] already decides the table; further tenths do not move ±2.0/±1.0 gates.
6. LME 384-worst Hit@10 non-monotonicity (88.72→89.15→86.60 [BRIEF]) debated without FR@3 and
   without §4. Worthless in isolation: the gate pairs FR@3-primary with Hit@10-guardrail precisely
   to stop single-metric relitigation.
7. Subspace distance 2.78 for the failed additive-penalty idea [BRIEF]. Worthless: safety gates
   passed but retrieval did not improve, CI includes zero, loses to BM25/float everywhere [BRIEF].
8. LoCoMo-ladder tidiness or PerLTQA-ladder tidiness pursued past the §3 prespecified reading.
   Worthless once §§2+4 fail: a cleaner slope on a disputed [BRIEF] or losing benchmark buys no
   decision.
9. Any new “beats coarse BM25” claim without the §2 fair table. Worthless by construction [BRIEF:
   all historical wins used coarse].
10. Budget-split ratios, Bloom-sketch sizes, or further ITQ variants after failure at every ratio /
    4-of-4 [BRIEF]. Worthless without a new falsifiable mechanism (only shifted thresholds qualify,
    Q5, and only after Q1 passes).

---

## 7. Cheapest decisive order (referee's pricing, not advocacy)

1. §2 fair-baseline re-run first (minutes; invalidates-or-grounds everything). [CONJECTURE on cost;
   falsifier in §2]
2. §4 rerank reuse second (minutes; uses §2's BM25-alone number; can invalidate the premise even if
   §2 surprises). [CONJECTURE on cost; falsifier in §4]
3. §3 PerLTQA k<n third (only the 8 archives; kills the false law whatever §§2/4 say).
   [CONJECTURE on cost; falsifier in §3]
4. Fund nothing else — especially Q5/Q6/Q8 — unless C1–C4 or the narrow gate is met as written.
   The still-running LME ablation (322/470 [BRIEF]) finishes in the background; it does not gate
   the decision.

Open items this report deliberately leaves unresolved: exact CPU-minute figures for §§2–4 on the
owner's hardware (stated as falsifiable conjectures, not measurements); LoCoMo adjudicated gold
(Q8); any literature beyond what the brief verified (round-2 recalls) — none of which move §§2–4.
[RECALLED, low-to-medium confidence, not load-bearing: BEIR-style “untrained dense loses to BM25”
expectation (Thakur et al. 2021) and ITQ-image-scope-mismatch (Gong & Lazebnik) are consistent with
the brief's verified items but are not used as gates here.]
