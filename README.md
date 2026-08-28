# LLM Token Zip / LLM Memory Research

Research archive for compact long-term memory retrieval for LLM/agent systems.

The project studies whether a memory system can keep a very small active routing representation while preserving evidence retrieval, exact provenance, and an auditable path back to the raw archive.

## Current research state — 2026-08-28

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
- `[NOT ESTABLISHED — CROSS-BENCHMARK GENERALIZATION]`

Task 4C3 stop rule is active: no Task 4C4, LoCoMo, larger-scale benchmark, or rescue experiment is launched from this audit without a separate Head Researcher decision and new preregistration.

## Repository map

- `docs/v51/` — V51 master checkpoint and protocol history, including the V1–V50 research narrative.
- `docs/v52/` — V52 protocol patches, accepted checkpoints, compute reports, frozen seals/manifests, and current status documents.
- `audit_v52_t4c1/` — independent Task 4C1 adversarial audit.
- `audit_v52_t4c2/` — independent Task 4C2 adversarial audit.
- `audit_v52_t4c3/` — accepted independent Task 4C3 audit, reproduction script, and hash verification log.
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
