# Coordinate-scale uncertainty completion

2026-09-07. **POST-OUTCOME SENSITIVITY ANALYSIS — NOT SCIENTIFIC ACCEPTANCE.**

The user approved completion on frozen metric records. Plan, code and nine synthetic tests were committed and pushed at `54605e2801f9cb1035a218936d64c9e70909139c` BEFORE these bootstrap results were computed. The original experimental point outcomes were already known. This is therefore not a new pre-outcome preregistration and does not retroactively cure earlier endpoint/interpretation ambiguity.

## Execution and verification

- Three schemes, exactly10000 replicates each: paired questions on LoCoMo and LongMemEval, plus LoCoMo conversation-clustered resampling. Existing rotation seeds fixed59001..59010. All arms and seeds paired within a replicate.
- LoCoMo clusters sampled with replacement; every selected cluster contributes all its questions, preserving a pooled question-weighted statistic. Only10 observed clusters. LME conversation bootstrap NOT COMPUTED: shared-conversation identity is not established.
- Python3.12.14, NumPy2.3.5, single-thread settings. This is an analysis-only runtime, not the frozen raw-retrieval execution stack. Runtime and input/code/plan hashes are recorded in `outputs/RESULTS.json`.
- One invocation of `bootstrap.py --run`; all three schemes completed with no algorithmic failure. Three full replicate CSVs retained. No additional rotation, reranking, raw data download or Task4F1 operation.
- `verify_outputs.py` independently reconstructs all54 reported percentile values from CSV using standard-library sorting and a linear quantile formula; counts, hashes, extrema and paired interactions PASS. The contextual reviewer independently used PowerShell sorting for nine selected statistics, with matching results. This is cross-checking, not a cold-start audit of the retrieval experiment.

## Both estimands remain visible

A = mean of per-seed gain/loss ratios. B = ratio of seed-mean gain to seed-mean loss, the historical headline route. Each interaction I is full minus block within the same bootstrap replicate. Neither is silently declared the uniquely registered endpoint. Point per-seed gains, denominators and ratios are retained in JSON; original frozen rows and results remain unchanged.

The following entries are **2.5th–97.5th bootstrap percentiles**, not certified population confidence intervals. All are conditional on the fixed ten rotation seeds. LME A interaction additionally conditions on9999 finite replicates; its one undefined replicate remains counted and saved. Ratio singularities make ordinary percentile-interval interpretations unreliable even when all values are finite.

| Scheme | Full-mixing recovery B | Interaction A | Interaction B |
|---|---:|---:|---:|
| LoCoMo paired questions | [0.6354, 0.8372] | [-9.1606, 9.2686] | [-4.9072, 5.6063] |
| LoCoMo clustered conversations | [0.6197, 0.9041] | [-8.4800, 8.1536] | [-4.1138, 5.5721] |
| LongMemEval paired questions | [0.5679, 0.7618] | [-2.3657, 2.5143]* | [-0.4923, 0.5746] |

*Finite-conditional only. A full recovery envelopes are similar: [0.6357,0.8397], [0.6198,0.9076], [0.5670,0.7627] respectively. Do not use table widths as precision for mechanism effects; the block denominators create nonregular ratios.

## What changed in our interpretation

### Full-mixing improvement remains visible; MOST versus PARTIAL is not a robust population distinction

Full-arm loss denominators remain positive in every sampled seed/replicate in all three schemes. Full-arm recovery-share percentiles remain well above zero under these sensitivity procedures. This preserves a useful descriptive intervention-effect observation on the fixed pipeline.

However, all full-arm envelopes cross0.70. Thus the original LoCoMo MOST / LongMemEval PARTIAL labels remain point classifications of the frozen panel, not evidence of distinct underlying categories. Bootstrap band frequencies are saved for transparency; they are not hypothesis truth probabilities or a revised decision rule.

### The unstable block denominator also affects LongMemEval

| Scheme | Replicates with any negative seed-level block loss | Replicates with negative seed-mean block loss |
|---|---:|---:|
| LoCoMo question | 8910/10000 | 1962/10000 |
| LoCoMo cluster | 8410/10000 | 2670/10000 |
| LongMemEval question | 3305/10000 | 43/10000 |

In LongMemEval, one replicate has an exactly zero float64 seed denominator and three have a seed denominator with absolute value<=1e-12. A_block/A_I have9999 finite and1 undefined replicate. Finite extrema of A_I are approximately -9.62e12 and +9.10e12: evidence of numerical/singular ratio fragility, NOT enormous scientific effects. No values were clipped or removed. Exact-zero classification is numerical, not a proof about exact rational arithmetic; the near-zero diagnostic prevents 'finite' from being mistaken for stable.

Consequently our earlier point-panel statement that LME block ratios were interpretable because all original seed losses were positive must be narrowed: positivity did not survive question resampling. All six interaction percentile envelopes span zero, but this is NOT a conventional valid null-hypothesis test and does NOT prove absence of scale participation.

## Disposition

The missing LoCoMo paired/clustered and LME paired sensitivity calculations are now provided with openly post-outcome design choices. They strengthen the warning against a clean comparative mechanism verdict; they do not erase the full-arm score-change observation or refute every scale-based mechanism.

Still unresolved: independent audit of raw retrieval/provenance; adjudication of A versus B as the registered endpoint; inconsistent sections7/9 interpretation rules; LME conversation grouping; fixed-rotation conditioning and limited LoCoMo clusters. Completing this analysis does not yield an unqualified 'all preregistration obligations satisfied' verdict.

Next single action: independent adjudication of this completion package and prior review findings. Do not run more seeds, change thresholds or scale rules, or repair frozen results in place. New discriminating experiments, if later desired, need their own prospective decision. Canonical main/state/ledger were not changed. Drive backup not performed. Task4F1 run=0, finalize=0, HMAC=0; BEAM outcome access=false.
