# Mathematical research, benchmark transfer, and error audits

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Read this before any worker report

This archive preserves **9 mathematical investigations, 4 benchmark runs, and 3 error audits**. Preservation is NOT endorsement of every claim. Every completed investigation includes its original `REPORT.md` and a **`COORDINATOR_REVIEW.md` that must be read alongside it**. Where they disagree, the coordinator correction governs pending further review. Original errors, failed conjectures, negative results and raw numeric outputs are retained deliberately.

**No literature priority or new deployable compression win is established.** Most valid results are elementary or standard inequalities assembled into scoped certificates, plus finite counterexamples. Passing a Python checker is not Lean/kernel verification, and two implementations from one worker are not two independent reviewers.

## Mathematical investigations

Paths below are relative to `math_discovery_2026_09_13/`.

| Investigation | Path | Supported result / main limitation |
|---|---|---|
| Ranking under bit deletion | `ranking_bounds/` | Pairwise gap perturbation bound and sufficient top-K stability; original top1 impossibility/quantifier claims restricted in review. |
| Why SIGN can win or lose | `sign_mechanism/` | Exact synthetic separations; original shared-gold top3 numbers were wrong. Independent conditional computation and corrected values retained. |
| Mixed bit allocation | `bit_allocation/` | Exact gain/loss toy instances; corrected hand-proof, greedy and storage-accounting overclaims. |
| Sharp per-gold profile bounds | `round2/sharp_bounds/` | Product-interval realizability and sharp single-gold extrema, duplicates allowed. Individual maxima cannot simply be averaged. |
| Greedy allocation failure | `round2/allocation_optimality/` | Strict greedy counterexample; diminishing returns is SUFFICIENT for separable-MSE greedy, not an iff guarantee. |
| Joint multi-gold extrema | `round3/joint_gold_bounds/` | Exact categorywise corner bounds for unweighted gold count; unequal weights and shared-archive sharpness need separate treatment. |
| All-N/K synthetic dominance | `round3/all_n_ranking/` | Corrected coupling theorem inside Model H only; negative-control win/loss bug and strictness prose corrected. |
| Normalization-aware SIGN bounds | `round4/norm_aware_sign_bounds/` | Valid elementary support/angle bounds and extra-scalar example; endpoint-attainment errors, loose certificates and floating-roundoff claims NOT accepted. |
| Rank-crossing certificates | `round4/rank_crossing_certificates/` | Sign-filtered rational score comparisons and conservative safe intervals; unresolved root regions are NOT certified. One real pair only, not a benchmark-wide top3 guarantee. |

## Benchmark transfer test

Common prospective exploratory specification: `theory_benchmark_test_v1/PLAN.md`. Existing baseline outcomes were known; this was NOT preregistration. The hypothesis used LOW48 (small query-magnitude coordinates) as a proposed nuisance proxy and positively scaled BOTH query and document coordinates. This is not an established mapping to Model H.

Effects below are **percentage-point changes in SIGN-minus-float gap between LOW48 t=4 and t=0.25**, not absolute codec improvements. SIGN is invariant under the construction. Nominal intervals are unadjusted archive-cluster bootstrap intervals; benchmarks are not pooled.

| Dataset | QA | Corrected effect (pp) | Nominal 95% interval (pp) | Status |
|---|---:|---:|---|---|
| LongMemEval | 470 | -6.44326 | [-9.27340,-3.68706] | Opposite to proxy prediction |
| REALTALK | 705 | -0.09361 | [-1.93300,+1.84903] | Inconclusive mean effect; original bootstrap-mean point estimate corrected |
| PerLTQA | 8265 | +2.46415 | [+1.55401,+3.44284] | Endpoint direction compatible; nonmonotone curve and strong section heterogeneity |
| LoCoMo | 1535 | -2.58291 | [-3.77676,-1.31321] | **CONDITIONAL / PROTOCOL-DEVIATION: historical float gate not met** |

See each dataset directory's `COORDINATOR_AGGREGATE.json`, `COORDINATOR_REVIEW.md`, raw `per_query.jsonl`, gate, scripts and original summary. Schemas intentionally preserved: LoCoMo has one row per QA with nested configurations, others use long-format rows. Do not sum physical rows as QA counts. HIGH48 reciprocal scaling is an exact algebraic mirror, not independent evidence.

## Critical retractions and audit results

- **Retracted pending primary source:** previously repeated LoCoMo SIGN-minus-float approximately +12pp. The searched programme material does not support it. Current independently reimplemented same-cache MC result is **+6.82838pp**, not historical replication. See `theory_benchmark_test_v1/audit_locomo_provenance/`. The coordinator-generated prompts propagated an unverified premise; do not blame a user-supplied measurement.
- **Theorem-to-intervention mismatch:** real vectors need individual document normalizations and an identified signal/nuisance mapping. Query-only magnitude is not such identification. `t` versus `t²` alone does not explain opposite dominance in the exact toy. See `audit_mapping/` and its correction.
- **Real-vector mechanism correction:** the selected LME witness still has a lower gold numerator after scaling; normalization is essential to its reversal. The worker's numerator-only explanation is false. See `audit_real_geometry/COORDINATOR_LME_WITNESS.json`. Selected-case coverage is 52 entries but 51 unique benchmark/QA pairs, not 52 unique queries.
- Endpoint agreement is not monotonicity, causal explanation, held-out prediction or compression improvement. A confidence interval spanning zero is inconclusive, not proof of absence.

## Provenance and reproduction

`SOURCE_INVENTORY.json` records every copied source path, SHA-256, size, completed-worker mapping, and exclusions. `worker_logs/` preserves final output and failed/restarted attempts, including model-stream timeouts and battery-interrupted sessions; `tasking/` preserves their exact prompts. Sources are byte-preserved. No credentials/provider session dumps are included.

`verify_archive.py` checks archive hashes, exact manifest coverage, inventory hashes, required review pairs, dataset QA/cell counts and independent aggregate estimates. It does NOT certify all mathematical proofs or rerun the full source-dependent pipelines. Many original scripts use absolute workspace paths and cached input arrays: restore the source layout or deliberately adapt paths before reproduction. Do not treat an import failure on another OS as a mathematical counterexample.

`MANIFEST.sha256` excludes itself and authenticates this archival copy. It is separate from untouched historic manifests and does not hide prior embedded-manifest mismatches.

## Exclusions

Ten derived REALTALK pickle checkpoints are not duplicated in Git; their hashes and reasons are recorded in `SOURCE_INVENTORY.json`. Their per-QA outcomes and generating code are included. Large original representation caches, datasets and environments are not new findings and are not re-uploaded here. Earlier heavy inputs remain documented in the [Drive backup](https://drive.google.com/drive/folders/1-8DYki9uXVPIVsKBAL2xCzw_LeUJH0q4). This does not claim every later local cache is already on Drive.

The previous research and V10 guard-repair records remain elsewhere on this same findings branch. **Main is unchanged.**
