# Muse session — PREREG DRAFT REVIEW: twelve-byte budget race (adversarial)

You are an independent adversarial reviewer. A docket draft is about to be submitted for internal
approval. Your job: **hunt for everything that would embarrass the programme if the race runs as
written** — ambiguities, infeasibilities, statistical traps, unspecified semantics, fairness holes.
Read-only on /mnt/c; writes only /tmp/pre1/. No network.

## Materials

- THE DRAFT: /mnt/c/Users/MDP/dev/llmzip-work/DRAFT_PREREG_TWELVE_BYTE_RACE.md
- Programme context + design source: /mnt/c/Users/MDP/dev/llmzip-work/strategy/roadmap_2026-09-13/
  muse_strategy_roadmap.md (§3 Design 2 = this race's spec) + YOL_HARITASI_FINAL.md (status).
- Round-1..3 findings the draft leans on: review_transfer/EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13/
  pilots/axis_attack_2026-09-12/ROUND3_REPORT.md (+ round3/ reports incl. DENEY1_REPORT.md,
  missing_analyses/*, ERRATA_ROUND3_D5.md) and round2/ROUND2_REPORT.md.
- Frozen protocol sources: same bundle's protocol_sources/ (v52_t4c3_coordinate_axis_probe.py =
  the eval block; adapters; question-level CSV) + round3_sources/harness/deney1_*.py for how the
  harness reimplements it.
- Native anchors: LME 0.5419751773049645; LoCoMo 0.23654714666441054.
- m1 kill-null facts: no-edge arm vs best-of-10 gap ≈ −1.62pp (LME) / −1.20pp (LoCoMo).

## Specific review mandates (at minimum; add your own)

1. **Budget/byte accounting.** Is "≤12 marginal persistent bytes" operational for EVERY arm —
   sign subsets (trivial), RaBitQ32 (code + any per-vector scalar?), PQ (12×8-bit codes; LUTs are
   shared state — is that consistent with the draft's shared-state rule?), extended-RaBitQ
   exclusion logic? Any arm where the accounting is ambiguous? Require an explicit per-arm
   worksheet spec.
2. **Evaluation semantics per codec — check hard.** The frozen protocol is SIGN-Hamming + the
   20-trial tie rule + top-3. The draft computes nothing for how RaBitQ32/PQ arms are SCORED
   (their distances are not sign-Hamming; RaBitQ uses rotation + asymmetric estimator; PQ uses
   ADC). Unspecified = future degrees of freedom. Demand: a fixed estimator per arm family, fixed
   tie handling for non-integer/non-discrete distances, fixed K=3 semantics, and a fairness
   statement (can recall be compared across these score types — e.g., per-question FR is the
   common metric; state the invariance argument).
3. **Statistics.** Bands (±0.5/1.0/2.0) vs the m1 finding (no-edge arms sit at ≈−1.6pp vs-best):
   is the primary estimand ("SIGN12B − best competitor") well-defined, incl. per-seed range and
   bootstraps? Multiplicity across 2 benchmarks × multiple competitors? What happens if results
   are benchmark-split (draft says report heterogeneity — is the decision rule still well-defined)?
4. **Gates/aborts.** Completeness: native reproduction; measured_bytes==declared; construction
   asserts; third-party pins; negative controls. Anything missing (e.g., determinism controls for
   k-means/rotation seeds; environment pins for faiss)?
5. **Feasibility.** faiss-cpu RaBitQ/PQ availability in the pinned stack; WSL/Windows path and
   determinism pitfalls the harness has previously hit; run-machinery gaps (who writes results
   where; artifact outputs; reproducibilty notes). Flag anything that must be tested BEFORE seal
   (smoke tests) vs discovered during the run.
6. **Disclosure completeness** (§7 boilerplate) vs rounds 1–3 actual approaches.
7. **Missing sections** a sealable prereg typically needs (run plan, artifact manifest, analysis
   scripts pre-fixed, stop rules, authorisation line). List them.

## Output

/tmp/pre1/pre1_report.md: numbered findings (severity FAIL/CAVEAT/NOTE; evidence; exact required
fix). End with: (a) "minimal changes required before seal" — an ordered, actionable list;
(b) "smoke tests that must pass BEFORE seal" list; (c) anything in the draft that is already
solid and should NOT be churned. Also a structured JSON /tmp/pre1/pre1_details.json.
Print a compact summary to stdout (PRE1_BEGIN/PRE1_END). ~1-2 hours scale.
