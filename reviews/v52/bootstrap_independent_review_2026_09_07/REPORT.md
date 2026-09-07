# Independent bounded review of persisted bootstrap completion

Disposition: PASS for the checks established below, with explicit evidence limitations. No implementation or persisted-summary error was found within this scope. This is not scientific acceptance, a raw-retrieval audit, or an independent replay of the real-data bootstrap algorithm.

Reviewed snapshot: `398c2ea4b661bf094afca25d543e96a9e50c615a`. Target: `reviews/v52/coordinate_scale_uncertainty_2026_09_07/` only. The reviewer received a bounded task description and read the package directly; producer claims were treated as claims to check. No repository AGENTS.md was discovered in the checkout or checked ancestor locations. No historical memory was used.

## Gates and evidence

| Gate | Result | Evidence and limit |
|---|---|---|
| Package integrity | PASS | All 10 manifest entries match exact local SHA256 and byte lengths. Script and plan also match RESULTS.json identities. |
| Frozen input identity | PASS | Both compressed metric files match the two recorded complete SHA256 digests. They were hashed as bytes only; raw retrieval correctness and corpus provenance were not checked. |
| Precomputation checkpoint structure | PASS, bounded | `54605e2801f9cb1035a218936d64c9e70909139c` is an ancestor of the reviewed snapshot. Its package subtree contains exactly plan, bootstrap.py, and test_bootstrap.py; all three blobs equal reviewed bytes and no output files occur there. Git structure supports checkpoint-before-output-commit ordering. It does not independently establish execution wall-clock chronology, successful remote push before computation, or exactly one invocation. Those remain producer execution-record claims. |
| Persisted numerical summaries | PASS | New stdlib-only checker reconstructs all 54 percentile values, finite/undefined counts, extrema, band frequencies and positive-interaction frequencies using all 10000 planned rows as denominator, and every paired interaction. Row IDs, sample-size ranges, and fixed question sample sizes also match. Deliberately incorrect quantile is rejected. |
| Reconstructible denominator diagnostics | PASS | Per-scheme/arm negative-any-seed counts, crossing-zero counts, seed extrema, aggregate negative/zero/near-zero counts and aggregate extrema match CSV. Means lie within the saved seed extrema for every row. |
| Interior seed denominator zero/near-zero counts | NOT ESTABLISHED independently | CSV saves only minimum, maximum and mean of ten seed denominators. Interior exact-zero and near-zero values cannot generally be recovered. JSON's one LME seed-zero and three near-zero counts are therefore not independently verified. Blank A_block/A_I values for one LME replicate are independently verified; that does not itself verify their numerical cause. |
| Paired weighting and unequal clusters | PASS static and synthetic | All 60 seed/arm values share one multinomial count vector. Question draws equal N with uniform probabilities. Cluster draws equal 10 with uniform probabilities; cluster sums are divided by the drawn total question count. This implements pooled question weighting, including variable cluster sample sizes. Nine inspected producer synthetic tests pass, including explicit duplicated-row and unequal nonconstant cluster controls. No real-data resampling was performed. |
| Undefinedness and ratio routes | PASS static and synthetic | Component float-zero division gives NaN. A uses ordinary mean, propagating any undefined seed; B divides mean gain by mean loss; interactions require both sides. Negative denominators remain visible and ratios are not clipped. Infinite final statistics raise an error. A and B noncommutation and aggregate-zero behavior are tested. These are float64 rules, not exact-rational guarantees. |
| Report interpretation | PASS with limitations | A/B ambiguity, post-outcome choices, fixed rotation conditioning, ten observed clusters, missing LME mapping and lack of mechanism acceptance are prominent. Tabulated envelopes and negative counts agree with recomputation. All six interaction envelopes span zero. No valid significance test or absence-of-mechanism conclusion follows. |

## Reporting qualifications

The analysis plan asks for nonpositive denominator counts as well as negative/zero/near-zero counts. The JSON does not give a separate nonpositive-any-seed field. Such a count can depend on overlap of the negative-any-seed and zero-any-seed sets, so it cannot generally be recovered by adding their counts. This is a narrow reporting completeness gap, not evidence that the saved quantiles are wrong. Aggregate nonpositive counts can be derived by adding the disjoint negative and zero aggregate counts.

The report's statement that LME has a seed exactly zero and three seed-near-zero replicates remains producer-reported at this gate. The exceptionally large finite A interaction extrema are directly visible and independently verified in the CSV; their interpretation as ratio fragility is consistent with the code, but complete per-seed attribution requires information not saved in these aggregate rows.

The recorded `algorithmic_failures: 0` is written by the producer, not an independent failure log. The completed 30000 rows and synthetic controls are consistent with successful execution, but this review does not establish that the real-data replicate arrays were generated by the reviewed code and RNG seeds. That would require an authorized replay or stronger execution evidence. No such replay is part of this review.

The report uses “conversation-clustered” while the plan correctly limits identity to persisted archive-ordinal producer metadata. Treat that as the operational grouping of these saved records, not an independently validated raw-corpus conversation join.

## Reproduction and boundaries

From the repository root, run:

```powershell
& 'C:/Users/MDP/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B reviews/v52/bootstrap_independent_review_2026_09_07/check.py
& 'C:/Users/MDP/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B reviews/v52/coordinate_scale_uncertainty_2026_09_07/test_bootstrap.py
```

The first command imports only the standard library, reads persisted files and Git objects, and writes CHECK_RESULTS.json inside this review namespace. It performs no resampling and imports no producer module. The second was inspected before execution and invokes nine pure synthetic tests only; it imports bootstrap.py without calling main or load. Observed result: checker PASS; 9 tests OK. CHECK_RESULTS.json records all reconstructed percentile values. REVIEW_HASHES.json binds review files and excludes itself.

No `bootstrap.py --run`, real-data draws, retrieval-runner imports, raw-corpus download, BEAM/Task4F1 action, original-package edit, main edit or push was performed. Only this review namespace was written. Remaining raw-retrieval, original endpoint/decision-rule and provenance obligations stay open; this bounded no-found-errors result cannot close them.
