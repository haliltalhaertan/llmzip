# LLM Token Zip / LLM Memory Research

Research archive for compact long-term memory retrieval for LLM/agent systems.

The project studies whether a memory system can keep a very small active routing representation while preserving evidence retrieval, exact provenance, and an auditable path back to the raw archive.

## Current research state — 2026-08-27

The project has progressed from V1 synthetic routing experiments through V51 full-LoCoMo preparation and V52 LongMemEval validation.

Current load-bearing result under independent-audit workflow:

- V52 Task 4C1: the same-family ITQ compression frontier below 96 bits failed on LongMemEval; 96 bits remained the smallest width within the frozen 0.5/1.0/2.0 pp tolerance bands.
- SIMPLE_SIGN96 produced a large retrieval lead over ITQ96, creating a new geometry question.
- V52 Task 4C2 added an exact centered continuous control. Centering changed Fractional Evidence R@3 by only +0.148936 pp, while SIGN96 remained +10.037943 pp above centered FLOAT96.
- Task 4C2 compute verdict: `[LEAD — SIGN/HAMMING ADVANTAGE SURVIVES CENTERED FLOAT CONTROL]`.
- Task 4C2 remains pending independent adversarial audit before checkpoint freeze.

This repository already contains the independent Task 4C1 audit under `audit_v52_t4c1/`.

## Repository map

- `docs/v51/` — V51 master checkpoint and protocol material.
- `docs/v52/` — V52 compute reports, protocol patches, novelty/prior-art notes, and Task 4C2 handoff.
- `code/` — frozen/recovered experimental scripts that are safe to keep in Git.
- `prompts/` — head-researcher / compute / audit handoff prompts.
- `literature/` — project-specific literature reviews and novelty guards.
- `recovery/` — File Library / Drive recovery and external-context records.
- `audit_v52_t4c1/` — independent Task 4C1 adversarial audit already committed by the auditor.
- `PROJECT_DOCUMENTATION_MANIFEST.md` — inventory of the documentation snapshot and Drive provenance.
- `DATASETS_AND_LARGE_ARTIFACTS.md` — large datasets/raw tables/packages intentionally kept outside Git.

## Research discipline

The project uses a falsification-first workflow. Synthetic, hybrid, curated-real and full-real evidence are kept distinct. Numerical results are not promoted to theorems. Deployable routing fits may not use QA answers, gold evidence labels, or answer-session labels. Binary/Hamming ties must use an independent frozen priority. Seeds/nuisance trials are not treated as independent statistical units.

For LongMemEval, all 470 primary questions are connected through session reuse, so current conclusions are fixed-benchmark paired estimands rather than population-level statistical inference.

## Canonical large dataset

LongMemEval cleaned-S:

- file: `longmemeval_s_cleaned.json`
- SHA256: `d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442`
- bytes: `277383467`
- canonical primary cohort: 470 non-`_abs` questions.

The dataset and raw large artifacts are not committed to Git; see `DATASETS_AND_LARGE_ARTIFACTS.md`.
