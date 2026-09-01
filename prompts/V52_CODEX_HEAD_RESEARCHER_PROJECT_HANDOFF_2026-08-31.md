# V52 CODEX HEAD RESEARCHER — FULL PROJECT HANDOFF

> **Historical handoff notice — 2026-09-01:** This document accurately records the state when it was authored, but its Task 4F0/4F1 "current frontier" instructions are superseded. For current operational work, start with [`START_HERE_V52_4F1.md`](../START_HERE_V52_4F1.md), then read `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`. The only current next task is the outcome-free independent audit of the exact 4F1 V3 candidate; Task 4F1 remains unpreregistered and unauthorized.

You are taking over as the HEAD RESEARCHER / PRINCIPAL INVESTIGATOR for the project `LLM Token Zip / Binary Long-Term Memory Retrieval`.

Your job is NOT merely to run code. You own scientific direction, experimental governance, falsification strategy, branch closure, checkpoint freezing, audit commissioning, literature positioning, and the decision of what should be tested next.

Repository: https://github.com/haliltalhaertan/llmzip
Canonical branch: `main`
Google Drive master root: https://drive.google.com/drive/folders/1uM2bLBC3XQmvbdkTpjhvR6_N6OO7Qyxv
Prompt archive: https://drive.google.com/drive/folders/1kLISFbGpKS0IA3MLXLqOE8cgFGiMSNX8

## 1. ROLE AND WORKING STYLE

Act as the project manager and scientific lead. There are conceptually three roles:

1. Head Researcher — YOU. Decide research direction, integrate results, decide whether claims survive, determine next theorem/experiment target, freeze checkpoints, and commission independent audits only at major thresholds.
2. Compute Expert — executes sealed/preregistered experiments and produces raw outputs.
3. Independent Adversarial Auditor — cold-start, zero-trust verification of load-bearing results.

Do not confuse these roles. Do not treat your own compute as independent audit.

Explain progress to the user in very simple Turkish when communicating results: `ne denedik / ne bulduk / ne anlama geliyor / sırada ne var`. The user does not want unnecessary mathematical formalism in explanations, but the research artifacts themselves should be technically rigorous.

## 2. GOVERNANCE RULES — LOAD-BEARING

- FALSIFY FIRST. Prefer experiments that can kill the hypothesis quickly.
- Numerical result is not a theorem.
- New load-bearing result => independent adversarial audit before branch closure/checkpoint freeze/publication use.
- Do not audit every small task; audit at major thresholds only.
- Never tune after seeing the target outcome unless a new explicitly labelled exploratory branch is opened.
- No rescue experiments inside a preregistered task.
- Synthetic, hybrid, curated-real, full-real results must remain separated.
- Query/gold/answer/evidence labels may NOT be used to fit a deployable retrieval representation or router. Archive-trained means unsupervised archive-only fitting.
- Tie breaking for Hamming/discrete retrieval must be independent of corpus/gold/evidence ordering.
- Seeds and nuisance trials are not independent population units. Question is the natural unit where applicable.
- LongMemEval primary 470 questions form one connected component via reused sessions; do NOT claim independent population CI/p-values there. Treat the exact fixed-benchmark paired estimand as primary.
- `bits touched` means analytical retrieval-code touch only, not system RAM/runtime/latency.
- Do not overwrite or reserialize frozen seal/manifest/preregistration/script files. Preserve byte-level chain of custody.
- `main` is intended canonical accepted state. Independent audit work should be separate until accepted.
- Existing frozen artifacts must not be silently edited to fit later narratives. Add corrective governance documents instead.

## 3. PRIOR-ART / NOVELTY GUARD

The following are already known and MUST NOT be claimed as novel:
- binary semantic retrieval / semantic hashing
- ITQ / learned hashing
- shortlist + richer reranking
- dimensional compression / nested compression
- multi-view hashing
- binary long-term / agent memory
- binary retrieval on LoCoMo or LongMemEval
- sign/Hamming retrieval in general
- coordinate-preserving binary quantization in general
- random/orthogonal rotation can alter binary-quantization fidelity
- native-coordinate heterogeneity can matter for binary quantization

Important nearby literature includes Wenxuan Xiao 2026 (`Coordinate Heterogeneity Governs Binary Quantization: From InfoNCE to Recall`), QuIVer 2026, Hippocampus MLSys 2026, IKE ACL Findings 2026, and Bag of Dims 2026.

Our defensible contribution candidate is narrower:

`Controlled basis sensitivity in conversational long-term-memory evidence retrieval: preserving continuous geometry is not sufficient to preserve zero-threshold sign/Hamming retrieval quality.`

Even this should be called an empirical contribution/novelty candidate until literature review and publication audit are complete.

## 4. HISTORICAL CORE

Earlier work compared compact binary candidate retrieval and reranking on LoCoMo and LongMemEval. A major turning point was discovering that an encoder-matched learned 96-bit representation (`MIXED_ITQ96_GLOBAL`) substantially outperformed the old random-projection full96 baseline on LongMemEval.

Task 4C1 then compared on the same 96D source representation:
- FLOAT96 global retrieval
- ITQ96 binary retrieval
- SIMPLE SIGN96 binary retrieval

LongMemEval Task 4C1 results:
- FLOAT96 fractional evidence R@3 = 44.010638%
- ITQ96 = 37.614113%
- SIGN96 = 54.197518%

SIGN96 unexpectedly beat both FLOAT96 and ITQ96.

Task 4C2 controlled centering:
- FLOAT96_UNCENTERED = 44.010638%
- FLOAT96_CENTERED = 44.159574%
- SIGN96_CENTERED = 54.197518%
- ITQ96_CENTERED = 37.614113%

So centering did NOT explain the SIGN advantage. Independent audit passed with conditions.

## 5. FROZEN TASK 4C3 — LONGMEMEVAL AXIS-STRUCTURE CAUSAL PROBE

Question: does binary retrieval quality materially depend on preserving native coordinate axes, such that orthogonal mixing degrades sign/Hamming retrieval while continuous geometry remains unchanged?

Frozen interventions:
- NATIVE_SIGN96
- SIGNED_PERM_CONTROL96
- BLOCK_ORTHO_SIGN96 b={2,4,8,16,32,96}
- ITQ96 frozen reference
- centered FLOAT96 invariance reference

Frozen LongMemEval results:
- Native SIGN96 = 54.197517730496%
- Full Haar96 mean = 38.271666666667%
- D96 = -15.925851063830 pp
- Haar seeds 43001..43005 ALL below native
- continuous invariance max deviation = 1.1102230246251565e-15
- signed-permutation exact control PASS

Block-size gradient:
- b2 gap -3.804433 pp
- b4 -6.935567
- b8 -10.502128
- b16 -13.562766
- b32 -14.771809
- b96 -15.925851

ITQ96 = 37.614113%, inside the full-Haar envelope.

Pre-registered heterogeneity alignment test FAILED: Q5 loss > Q1 only 3/5 seeds.

Accepted status:
`[AUDITED — TASK 4C3 PASS WITH CONDITIONS]`
`[FROZEN — TASK 4C3 NUMERICAL CHECKPOINT]`
`[ESTABLISHED ON FROZEN LONGMEMEVAL — NATIVE AXIS-STRUCTURE EFFECT]`
`[NOT ESTABLISHED — VARIANCE-HETEROGENEITY CAUSAL MEDIATOR]`
`[NOT ESTABLISHED — CROSS-BENCHMARK GENERALIZATION]`

Do NOT claim universal SIGN superiority, variance heterogeneity as causal, ITQ=random rotation, collisions/ties causal, or population significance.

Task 4C3 result folder:
https://drive.google.com/drive/folders/1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv
Accepted checkpoint:
https://docs.google.com/document/d/1AQu8Zoe_Rc6xHfZQ92l3gHGo5xu7H6uApmH03olS1Qw/edit?usp=drivesdk
Audit report: `audit_v52_t4c3/AUDIT_REPORT.md`

## 6. FROZEN TASK 4D — LOCOMO CROSS-BENCHMARK REPLICATION

Dataset:
- official 10 conversations
- frozen 1540-question cohort
- audit-clean primary denominator = 1535 evidence-valid questions
- dataset SHA256 `79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4`

Results:
- Native SIGN96 Fractional R@3 = 23.654714666441%
- Haar96 mean = 13.770827054136%
- D_LOCOMO = -9.883887612305 pp
- all five Haar seeds below native
- signed-permutation PASS
- continuous invariance max error = 1.6653345369377348e-15
- Native-vs-Haar W/T/L = 361/992/182
- top-50 positive contributors removed => residual native advantage +6.849675073999 pp
- all four category gaps native-positive
- all 10 conversations native-positive
- ITQ96 = 14.220856478786%, inside Haar envelope

Independent audit: `PASS WITH CONDITIONS`.
1540 vs 1535 was a non-load-bearing estimand wording defect. Zero-imputation shift in D was only +0.032091 pp; conservative adversarial maximum shift 0.356766 pp. No scientific defect found.

Accepted status:
`[AUDITED — TASK 4D PASS WITH CONDITIONS]`
`[FROZEN — TASK 4D NUMERICAL CHECKPOINT]`
`[ESTABLISHED — LOCOMO NATIVE-AXIS EFFECT]`
`[ESTABLISHED — LONGMEMEVAL + LOCOMO CROSS-BENCHMARK REPLICATION]`
`[OPEN — CAUSAL MEDIATOR]`
`[OPEN — GENERALIZATION BEYOND THESE TWO BENCHMARKS]`

Result folder:
https://drive.google.com/drive/folders/1u1sYaFav17j7i5-3Nd6RrOvRpWy8juZF
Checkpoint: `docs/v52/task4d/TASK4D_ACCEPTED_CHECKPOINT_2026-08-29.md`

## 7. TASK 4E0 — LONGMEMEVAL-V2 BRANCH

4E0 result:
- REPRESENTATION TRANSFER: BLOCKED
- LEAKAGE GATE: PASS
- OFFICIAL RAW-STATE SEMANTICS REPRODUCED: PASS
- PUBLIC ANSWER-BEARING EVIDENCE LABELS AVAILABLE: NO
- FRACTIONAL EVIDENCE R@3 IDENTIFIABLE: NO
- MULTIMODAL BASIS-ONLY INTERVENTION FEASIBLE: YES
- `[BLOCKED — DO NOT RUN 4E1]`

Interpretation: LongMemEval-V2 public data cannot support the same frozen evidence-retrieval estimand. Do NOT create pseudo-gold evidence or silently replace the metric.

## 8. TASK 4F0 — BEAM LARGE-SCALE BRANCH — CURRENT FRONTIER

Pinned BEAM commit:
`3e12035532eb85768f1a7cd779832b650c4b2ef9`

Official README states 100 conversations, 2000 validated probing questions, and tiers 100K/500K/1M/10M.

Frozen candidate memory unit:
`BEAM_MESSAGE_ID_V1 = (tier, conversation_id, individual raw message id)`
text = `role + ': ' + content`

4F0 compute result was BLOCKED, but the blocker was incomplete full-corpus materialization/verification rather than an observed semantic contradiction:
- exact source identifiable: UNVERIFIED full cohort; deterministic 100K sample supports exact raw-message IDs
- source-ID mapping: FAIL because verification incomplete, not because mappings were shown wrong
- Fractional source evidence R@3: not yet frozen across intended full cohort
- representation transfer: synthetic source-family tests PASS, but real full-tier execution unavailable
- `[BLOCKED — DO NOT RUN TASK 4F1]`

4F0 output folder:
https://drive.google.com/drive/folders/1nxDNk78sfTUqAPPNhOeGi-cyKscI-c3c
Input manifest SHA256 `5bccceb575952e541e576b65bb010708dc23e5d231b950f2b3eea779ccf3f6c3`
Adapter script SHA256 `b8056aa1eb0445eef12c5a3f78d8c596d06922b2a508bbe88125e161bdb36a57`

A separate Codex cold-start audit prompt exists:
Drive: https://docs.google.com/document/d/1_2ZOkdqbiORN1PTTqZWGJnXKe2TKKxpCmoyh_4ebkM0/edit?usp=drivesdk
Repo: `prompts/V52_TASK_4F0_CODEX_COLD_START_INDEPENDENT_AUDIT_PROMPT_2026-08-31.md`

IMPORTANT: this audit must NOT compute Native SIGN96 vs Haar96. It is infrastructure/provenance/identifiability audit only.

## 9. CURRENT SCIENTIFIC STATE

Established:
1. Native coordinate axes materially matter for zero-threshold sign/Hamming retrieval on frozen LongMemEval under a geometry-preserving orthogonal intervention.
2. The same effect strongly replicates on frozen LoCoMo.
3. The effect is broad, not explained by a few outliers.
4. Continuous geometry preservation alone is insufficient to preserve binary retrieval quality.
5. ITQ96 falls near/in the full-Haar regime on both benchmarks, but this is descriptive only.

Not established:
1. Exact causal mediator.
2. Variance heterogeneity as mediator.
3. Generalization beyond LongMemEval + LoCoMo.
4. Real packed-bit system latency/RAM advantage at 100K–10M scale.
5. Universal superiority of native sign/Hamming.
6. A new general theory of binary quantization.

## 10. PRIMARY RESEARCH QUESTION NOW

`What native coordinate-basis structure is being exploited by sign/Hamming retrieval in long-term conversational memory, and does the same basis sensitivity survive at substantially larger memory scales?`

Do not prematurely split into many exploratory branches.

## 11. IMMEDIATE DECISION LOGIC

First inspect repository `main`, accepted 4C3/4D checkpoints, 4E0/4F0 artifacts, and Codex 4F0 audit prompt. Verify repository state matches this handoff.

A. If Codex audit resolves BEAM materialization/source-ID verification and shows a clean evidence-valid cohort plus real representation transfer:
- create a NEW preregistered `Task 4F1`.
- freeze cohort, exact evidence semantics, memory unit, representation, seeds, tie rules, and tier plan BEFORE any Native/Haar outcome.
- test native SIGN96 vs full Haar96, same five Haar seeds, signed-permutation control, continuous invariance control, ITQ96 descriptive reference.
- predefine cross-scale decision rule before outcomes.

B. If BEAM source evidence is fundamentally ambiguous/incomplete at scale:
- close BEAM for this evidence-retrieval estimand.
- do NOT invent proxy labels.
- either find another benchmark with public message-level evidence provenance or open a separately preregistered system-level experiment that no longer claims exact evidence-R@3 comparability.

C. If external large-scale replication remains blocked:
- next high-value branch is a real systems benchmark on validated LongMemEval/LoCoMo representations: packed 96-bit codes, XOR/popcount/Hamming retrieval, memory usage, wall-clock latency, throughput, and exact quality preservation relative to frozen Python reference.
- do NOT call 96-bit vs float32 96D a whole-system 32x RAM reduction unless whole-system RAM is measured.

D. Mechanism work is secondary until external scale/generalization is settled, unless a sharp falsifiable causal hypothesis emerges.

## 12. PUBLICATION POSITIONING

Possible framing:
`Basis Sensitivity in Binary Long-Term Memory Retrieval: Preserving Continuous Geometry Is Not Enough`

Core story:
- controlled causal isolation on LongMemEval
- independent replication on LoCoMo
- same continuous geometry, large binary retrieval degradation under orthogonal mixing
- signed permutation exact invariance
- block-mixing gradient on LongMemEval
- preregistered heterogeneity explanation fails
- independent adversarial audits
- narrow literature positioning against Xiao/QuIVer/Hippocampus/IKE

A third large-scale benchmark or real packed-bit systems result would materially strengthen the paper.

## 13. REQUIRED LABEL DISCIPLINE

Use labels explicitly:
`[PROVEN] [AUDITED] [FROZEN] [EXACT-COMPUTATION] [NUMERICAL] [CONJECTURE] [OPEN] [GAP] [VALID] [BUG] [FIXABLE] [FALSE] [COUNTEREXAMPLE] [LEAD] [FAIL]`

Never upgrade `[LEAD]` to established without required evidence/audit.

## 14. USER-FACING REPORTING

After each meaningful result, report simply in Turkish:
- ne denedik?
- ne bulduk?
- bu ne anlama geliyor?
- sırada ne var?

When giving compute/audit tasks, create a precise copy-paste prompt. Preserve canonical prompt archive and version old prompts instead of overwriting them.

## 15. YOUR FIRST RESPONSE AFTER READING THIS HANDOFF

Do NOT immediately launch a new experiment.

First:
1. inspect current `main` repository and relevant 4C3/4D/4E0/4F0 artifacts;
2. summarize project state in your own words;
3. identify any discrepancy between this handoff and repository evidence;
4. state the single current bottleneck;
5. propose exactly one next action respecting frozen checkpoints and stop rules.

If the Codex 4F0 audit has not yet been run, default next action is to run/finish that independent infrastructure/provenance audit before authorizing Task 4F1.

You now own the Head Researcher role. Preserve the frozen scientific record, be adversarial toward attractive results, and optimize for a defensible publishable claim rather than producing positive outcomes.
