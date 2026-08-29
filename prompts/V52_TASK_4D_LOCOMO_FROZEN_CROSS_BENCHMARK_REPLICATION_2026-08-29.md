# V52 TASK 4D — LOCOMO FROZEN CROSS-BENCHMARK REPLICATION

Date: 2026-08-29
Role: Mathematical Compute Specialist / Independent Compute Executor
Authorized by: Head Researcher

Canonical full prompt in Drive: https://docs.google.com/document/d/19nbkI9g0djWMoIO8DqdsNQowdLiO1-_hKYx-8831w58/edit?usp=drivesdk

## HEAD RESEARCHER DECISION

[HEAD RESEARCHER DECISION — NEW SCIENTIFIC BRANCH AUTHORIZED]

Task 4C3 is already independently audited and frozen. Task 4D is a new separately preregistered falsification branch. Its only purpose is to test whether the audited native-coordinate-axis effect transfers from LongMemEval to the independent full-real LoCoMo benchmark. Do not tune toward the LongMemEval result; null or reversed replication is an acceptable result.

## CANONICAL PARENT STATE

Repository: https://github.com/haliltalhaertan/llmzip
Canonical branch: `main`
Parent commit before this preregistration: `8f52c8072f4f781ad2539c461fae154c4c52753b`
Accepted Task 4C3 checkpoint: `docs/v52/task4c3/TASK4C3_ACCEPTED_CHECKPOINT_2026-08-28.md`
Independent audit: `audit_v52_t4c3/AUDIT_REPORT.md`
V51 LoCoMo checkpoint: https://drive.google.com/file/d/1zzwNHsZtiQ0RhJBqgLAI_4OF7v2uehrQ/view?usp=drivesdk

## FROZEN PRIOR RESULT — HYPOTHESIS SOURCE ONLY

LongMemEval Task 4C3: Native SIGN96 = 54.197517730496%; full-Haar96 mean = 38.271666666667%; D96 = -15.925851063830 pp; 5/5 Haar seeds below native; continuous geometry preserved to 1.1102230246251565e-15; signed-permutation control exact PASS; variance-heterogeneity alignment NOT CONSISTENT.

Do not use those values to select LoCoMo preprocessing, representation, thresholds, filters, seeds or stopping rules.

## PRIMARY QUESTION

On the frozen full-real LoCoMo evidence-retrieval benchmark, does zero-threshold sign/Hamming retrieval materially depend on preserving the native coordinate basis, such that a data-independent full 96D orthogonal Haar rotation degrades retrieval even though centered continuous geometry is unchanged?

## FROZEN LOCOMO COHORT

Use the exact V51 full-real LoCoMo protocol. Required pre-outcome checks:
- 10 official conversations;
- Cat1–Cat4 only;
- 1,540 primary questions;
- category counts 282 / 321 / 96 / 841;
- dataset SHA256 `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`;
- existing `dial481/locomo-audit` correction layer with explicit empty-correction semantics;
- V51 audit-clean/raw distinction;
- BLIP captions included exactly as frozen in V51;
- retrievable-gold evidence denominator.

If dataset identity, corrections, BLIP handling or gold mapping cannot be reproduced from canonical project artifacts, STOP before retrieval quality and return `[BLOCKED — LOCOMO CANONICAL ADAPTER / DATA IDENTITY NOT REPRODUCIBLE]`. Do not improvise an adapter.

## REPRESENTATION FAMILY

Use the same frozen encoder/source-block FAMILY as the accepted V52 LongMemEval geometry branch. For each LoCoMo archive/conversation, fit representation components from archive memory text only. QA answers, gold evidence, category labels and answer-session metadata must never enter fitting.

Intended 96D construction is the same mixed-family geometry from Tasks 4B/4C1/4C2/4C3: frozen source blocks -> concatenate -> archive-only `TruncatedSVD(96, random_state=5204)` when required by the mixed-96 family -> frozen L2 normalization -> archive mean `mu96` -> centered docs `C96=Y96-mu96` and query `qC96=QY96-mu96`.

Do not substitute a new embedding model or external API representation. Before outcomes, emit `V52_T4D_REPRESENTATION_TRANSFER_PROOF` showing the exact reused implementation/hashes and that query/gold labels do not enter archive fitting. If exact semantic transfer is impossible, STOP rather than use a near substitute.

## FROZEN METHODS

A. `NATIVE_SIGN96`: centered C96/qC96, zero threshold, global Hamming, top3, independent frozen tie priority.

B. `SIGNED_PERM_CONTROL96`: seeds 43001..43005, common coordinate permutation + common sign flips, same transform docs/query, zero threshold, global Hamming. It MUST exactly reproduce native distances/ranking/top3/metrics. Any mismatch => `[BUG — HAMMING-INVARIANT CONTROL FAILED]` and STOP.

C. `HAAR96_SIGN`: PRIMARY intervention. Full 96D only; NO block-size sweep. Seeds 43001,43002,43003,43004,43005. IID N(0,1) 96x96 -> QR -> deterministic diagonal-sign correction using exact Task 4C3 convention. Transform is data-independent and determined only by seed. Same transform docs/query; zero threshold; global Hamming; top3; same tie rule.

D. `ITQ96_CENTERED`: secondary reference only. Seeds 101,202,303,404,505. Archive-only canonical audited ITQ orientation; zero threshold; global Hamming. Primary verdict does not depend on ITQ.

E. Centered FLOAT invariance reference only: for each conversation/question/Haar seed verify orthogonality, norms, dot products, cosine scores, and score difference <=1e-12. Continuous top3/ranking must be invariant except exact tied-score sets. Failure => `[BUG — CONTINUOUS GEOMETRY NOT PRESERVED]` and STOP.

## FROZEN RANDOMNESS

Rotation seeds: 43001,43002,43003,43004,43005.
ITQ seeds: 101,202,303,404,505.
Tie/nuisance trials: 20 per applicable method/seed.
Tie priority must be deterministic and independent of corpus/gold/evidence order. Seeds/nuisance are not independent statistical units; collapse nuisance within question first, then rotation seeds within question for the mean-Haar comparison.

## METRICS

Primary: audit-clean Fractional Evidence Recall@3.
Secondary: ANY Evidence Recall@3; ALL Evidence Recall@3.
Use frozen V51 evidence-unit semantics only.

## PRIMARY EFFECT

`S_native` = mean question-level audit-clean Fractional Evidence Recall@3 for Native.
`S_haar(s)` = same metric for full-Haar seed s.
`S_haar = mean_s S_haar(s)`.
`D_LoCoMo = S_haar - S_native` in percentage points.

## PRE-REGISTERED DECISION RULE

- If `D_LoCoMo <= -5.0 pp` AND all 5/5 Haar seeds below native: `[STRONG CROSS-BENCHMARK REPLICATION — NATIVE AXES MATTER ON LOCOMO]`.
- If `D_LoCoMo < -1.0 pp` but strong rule is not fully satisfied: `[PARTIAL / MIXED DIRECTIONAL REPLICATION ON LOCOMO]`.
- If `|D_LoCoMo| <= 1.0 pp`: `[NO MATERIAL LOCOMO REPLICATION]`.
- If `D_LoCoMo > +1.0 pp`: `[FALSIFIED IN THIS DIRECTION — FULL HAAR IMPROVES SIGN RETRIEVAL ON LOCOMO]`.

These are falsification/engineering bands, not population significance thresholds.

## INFERENCE DISCIPLINE

Primary result is an exact fixed-benchmark paired estimand over 1,540 audit-clean questions. Do not treat seeds/nuisance as independent observations. No population p-value claim. Show all 10 conversation gaps individually. Conversation bootstrap may be secondary/coarse only.

Frozen descriptive strata: Cat1/Cat2/Cat3/Cat4; one-gold vs multi-gold if valid; all 10 conversation IDs; archive-size quartiles frozen before outcomes. No post-hoc subgroup search.

Composition sensitivity for native minus mean Haar96: W/T/L, median paired gap, mean paired gap, and residual mean after removing top 10/25/50 native-positive contributors.

Secondary descriptive diagnostics for Native/Haar96/ITQ96: unique/duplicate code fractions, largest collision bucket, exact query-code match, candidates at minimum Hamming distance, top3 boundary tie rate, native-rank Spearman, native top3 overlap, bit occupancy/dead bits. Do not infer collisions/ties/occupancy are causal. Do not rerun the failed 4C3 variance-CV quintile mechanism test as a new primary analysis.

## PRE-RUN SEAL

Before ANY retrieval-quality outcome, write/hash `V52_T4D_PRE_RUN_SEAL.json`. It must pin task/date, canonical parent commit, Git prompt path/blob SHA if available, Drive prompt URL, dataset identity, correction layer, source-block identifiers/hashes, BLIP rule, cohort counts, representation recipe, methods, seeds, top-k, metric semantics, tie-priority rule, decision bands, continuous invariance tolerance and no-rescue list. Hash the sealed compute script and include its SHA256. Final run must use byte-identical script bytes; any edit requires a new pre-outcome seal.

## NO-RESCUE / NO-EXPANSION

After outcomes begin, do not add/change block sizes, seeds, nuisance trials, bit widths, thresholds, centering, embeddings, source-block weighting, whitening/PCA variants, supervised/query-adaptive rotations, reranking/shortlists, top-k, LoCoMo subsets/categories, correction sets, metrics selected after seeing results, LongMemEval-V2, million-memory scaling, or latency/system benchmarks. Weak/null/reversed is the result.

## REQUIRED OUTPUTS

Create a new canonical Task 4D Drive folder and save at minimum: pre-run seal, sealed compute script, post-run manifest, input checks, representation transfer proof, raw trial results, question-level, aggregate, Haar seed results, signed-perm control, continuous invariance, ITQ-Haar envelope, collision/tie/rank diagnostics, frozen strata, composition sensitivity, compute report, Head Researcher handoff, and `V52_T4D_ALL_OUTPUTS.zip`. Post-run manifest must hash outputs and bind to seal/script.

## REQUIRED HEAD RESEARCHER HANDOFF

Return exactly:
`TASK: V52 TASK 4D — LOCOMO FROZEN CROSS-BENCHMARK REPLICATION`
`STATUS: COMPLETE / BLOCKED / BUG`
`DATASET SHA: ...`
`COHORT: ... / 1540`
`SIGNED-PERM CONTROL: PASS/FAIL`
`CONTINUOUS INVARIANCE: PASS/FAIL; MAX ERROR=...`
`NATIVE FRACTIONAL R@3: ...%`
`HAAR96 MEAN FRACTIONAL R@3: ...%`
`D_LOCOMO: ... pp`
`HAAR SEEDS: seed:value; ...`
`ALL FIVE HAAR SEEDS BELOW NATIVE: YES/NO`
`PRE-REGISTERED VERDICT: ...`
`NATIVE-vs-HAAR W/T/L: ...`
`MEDIAN PAIRED GAP: ... pp`
`TOP50-REMOVED RESIDUAL NATIVE ADVANTAGE: ... pp`
`ITQ96 FRACTIONAL R@3: ...%`
`ITQ vs HAAR ENVELOPE: BELOW/WITHIN/ABOVE`
`CATEGORY STRATA DIRECTION: ...`
`10 CONVERSATION GAPS: ...`
`MAX OBSERVED PROTOCOL DEFECT EFFECT: ...`
`OUTPUT DRIVE FOLDER: ...`
`PRE-RUN SEAL SHA256: ...`
`SEALED SCRIPT SHA256: ...`
`POST-RUN MANIFEST SHA256: ...`

Then exactly one recommendation: `[AUDIT REQUIRED — LOAD-BEARING CROSS-BENCHMARK RESULT]` or `[NO AUDIT YET — BLOCKED/BUG MUST BE FIXED BEFORE INTERPRETATION]`.

## INTERPRETATION CEILING

Even if strong replication occurs, the maximum unaudited statement is: on the frozen full-real LoCoMo protocol, the same native-basis vs data-independent full-Haar intervention used in audited LongMemEval shows a material directional effect on zero-threshold sign/Hamming evidence retrieval while centered continuous geometry remains invariant.

Do not claim universal native-axis superiority, population generalization, variance heterogeneity or collision/ties as the cause, ITQ=Haar, all LLM embeddings have meaningful native coordinates, or production speed/RAM superiority.

A strong/partial cross-benchmark result is load-bearing and MUST receive a new independent adversarial audit before freeze/publication.

## STOP RULE

Stop after Task 4D outputs and handoff. Do not launch LongMemEval-V2, Task 4E, system scaling, mechanism rescue or publication drafting. Head Researcher decides next branch.