# LLM Token Zip / LLM Memory Research

Research archive for compact long-term memory retrieval for LLM/agent systems.

**New researcher or LLM? Start with [`START_HERE_V52_4F1.md`](START_HERE_V52_4F1.md).** It binds the current branch, exact next task, source order, external corpus requirement and the hard no-outcome boundary for Task 4F1.

**Crash-safe continuation:** [`ops/CURRENT_STATE.json`](ops/CURRENT_STATE.json) and [`docs/CONTINUITY_PROTOCOL.md`](docs/CONTINUITY_PROTOCOL.md) define the machine-readable state, append-only handoff process and multi-agent isolation rule. Verify them with `python -B tools/verify_continuity_state.py` before resuming work.

The project studies whether a memory system can keep a very small active routing representation while preserving evidence retrieval, exact provenance, and an auditable path back to the raw archive.

## Current research state — 2026-09-01 (section frozen at that date; superseded by ledger L-003 through L-096 — see `docs/CONTINUITY_LEDGER.md` and `ops/CURRENT_STATE.json`)

The project has progressed from V1 synthetic routing experiments through V51 full-LoCoMo preparation and V52 LongMemEval validation.

Current accepted state under the independent-audit workflow:

- V52 Task 4C1: the same-family ITQ compression frontier below 96 bits failed on LongMemEval; 96 bits remained the smallest width inside the frozen 0.5/1.0/2.0 pp tolerance bands.
- V52 Task 4C2: centering explains essentially none of the SIGN96-vs-FLOAT96 lead. Independent audit: `PASS WITH CONDITIONS`; Task 4C2 numerical checkpoint frozen.
- V52 Task 4C3: data-independent orthogonal coordinate mixing preserves centered continuous geometry to numerical precision but materially hurts zero-threshold SIGN/Hamming evidence retrieval on the frozen 470-question LongMemEval benchmark.
  - Native SIGN96 Fractional Evidence Recall@3: `54.197517730496%`
  - Full-Haar96 mean: `38.271666666667%`
  - `D96 = -15.925851063830 pp`
  - all five preregistered Haar96 seeds below native
  - signed-permutation control exact PASS
  - continuous orthogonal invariance max deviation `1.1102230246251565e-15`
- Independent Task 4C3 audit: `PASS WITH CONDITIONS`; accepted into `main` via PR #1.
- `[FROZEN — TASK 4C3 NUMERICAL CHECKPOINT]`
- `[ESTABLISHED ON FROZEN LONGMEMEVAL — NATIVE AXIS-STRUCTURE EFFECT]`
- `[NOT ESTABLISHED — VARIANCE-HETEROGENEITY CAUSAL MEDIATOR]`
- V52 Task 4D independently replicated the directional native-axis effect on frozen LoCoMo:
  - Native SIGN96 Fractional Evidence Recall@3: `23.654714666441%`
  - Full-Haar96 mean: `13.770827054136%`
  - `D_LoCoMo = -9.883887612305 pp`
  - independent audit: `PASS WITH CONDITIONS`; numerical checkpoint frozen.
- `[CROSS-BENCHMARK REPLICATION ESTABLISHED — LONGMEMEVAL + LOCOMO]`
- V52 Task 4E0 LongMemEval-V2: blocked because the frozen representation and evidence estimand do not transfer faithfully from public data. This is not a negative scientific result.
- V52 Task 4F0 BEAM feasibility audit: `PASS WITH CONDITIONS — ORIGINAL BLOCKED VERDICT CORRECT BUT RESOLVABLE`.
  - 100 conversations, 2,000 questions and 327,116 raw message units materialized.
  - four 1M archives contain 1,720 divergent duplicate message keys.
  - an outcome-independent restricted cohort of 1,712 evidence-identifiable questions is available.
  - representation transfer and 100K/500K/1M/10M scale feasibility pass on clean archives.
  - no Native-vs-Haar retrieval outcome was inspected.

Head Researcher decision: accept the superseding Task 4F0 restricted-refreeze audit and seal the exact 1,712-question cohort/protocol boundary. Task 4F1 remains blocked until its outcome-bearing fitting/ranking implementation is separately byte-bound and independently audited. See `docs/RESEARCH_PROGRAM_STATUS_2026-08-31.md`.

Task 4F1 implementation governance update: the V1 audit was contaminated by an auditor-side accidental outcome-capable execution; V2 then received an outcome-free `BLOCKED` verdict for three synthetic finalization/checkpoint defects. V3 repairs those defects and had, at the time of writing, passed only implementer-side outcome-free preflight and synthetic regressions. [SUPERSEDED 2026-09-01: the cold-start V3 independent audit closed the same day with verdict BLOCKED (branch `audit/v52-t4f1-v3-independent-2026-09-01`, commit `a590f629`; ledger L-003). The programme has since proceeded through the V4, V5 and V6 audits, the V7 package (audit incomplete, no verdict), the V8 prepared profile (unaudited), and Seal V3 (2026-09-04).] No Task 4F1 result has been accessed.

## Repository map

- `docs/v51/` — V51 master checkpoint and protocol history, including the V1–V50 research narrative.
- `docs/v52/` — V52 protocol patches, accepted checkpoints, compute reports, frozen seals/manifests, and current status documents.
- `audit_v52_t4c1/` — independent Task 4C1 adversarial audit.
- `audit_v52_t4c2/` — independent Task 4C2 adversarial audit.
- `audit_v52_t4c3/` — accepted independent Task 4C3 audit, reproduction script, and hash verification log.
- `audit_v52_t4f0_codex_2026_08_31/` — complete Task 4F0 independent audit package, compact evidence tables, scripts and hash inventory; the 804 MB materialized BEAM corpus is intentionally excluded.
- `adapters/` — exact-byte frozen LongMemEval v1/v2 adapters with pinned SHA256 values.
- `prompts/` — prompt lineage and audit/compute prompts.
- `literature/` — project-specific deep literature reviews and novelty guards.
- `recovery/` — File Library / Drive recovery and provenance records.
- `CHAIN_OF_CUSTODY.md` — zero-trust byte-preservation and audit governance rules.
- `DATASETS_AND_LARGE_ARTIFACTS.md` — canonical locations for datasets, raw tables, ZIP bundles, and heavy artifacts kept in Drive.

## Research discipline

The project uses a falsification-first workflow. Synthetic, hybrid, curated-real and full-real evidence are kept distinct. Numerical results are not promoted to theorems. Deployable routing fits may not use QA answers, gold evidence labels, or answer-session labels. Binary/Hamming ties must use an independent frozen priority. Seeds/nuisance trials are not treated as independent statistical units.

For LongMemEval, all 470 primary questions are connected through session reuse, so current conclusions are fixed-benchmark paired estimands rather than population-level statistical inference.

## Canonical large dataset

LongMemEval cleaned-S:

- file: `longmemeval_s_cleaned.json`
- SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- bytes: `277383467`
- canonical primary cohort: 470 non-`_abs` questions.

The dataset and heavy raw artifacts are not committed as normal Git files; their exact Drive locations and frozen hashes are recorded in `DATASETS_AND_LARGE_ARTIFACTS.md` and the task manifests.
