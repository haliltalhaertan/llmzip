# Additive correction to the independent report

The parent reviewer correctly identified an omitted reconstruction route in REPORT.md at commit `aef8944d24672a8e39d1b967a96c09bb64f1d7bd`. A replicate has any nonpositive seed denominator if and only if its saved minimum denominator is <= 0. Thus nonpositive-any-seed counts ARE independently reconstructible from the persisted CSV, regardless of the overlap of negative and zero marginal counts. The report's discussion of marginal-count overlap is mathematically true but incomplete and potentially misleading in this package, which saves minima. Treat this correction as authoritative for that point; the original report is retained unchanged for transparency.

The amended stdlib checker counts `den_full_min <= 0` and `den_block_min <= 0` directly, without resampling:

| Scheme | Any seed nonpositive, full | Any seed nonpositive, block |
|---|---:|---:|
| LoCoMo question | 0/10000 | 8910/10000 |
| LoCoMo cluster | 0/10000 | 8410/10000 |
| LongMemEval question | 0/10000 | 3306/10000 |

These independently computed counts are saved in CHECK_RESULTS.json under `independent_any_seed_nonpositive_counts`. The producer JSON still lacks a dedicated nonpositive field, but the evidence needed to reconstruct it is present. This is a presentation omission, not missing diagnostic evidence for nonpositivity.

The parent reported an initial error in its separate PowerShell cross-check: `$_[field]` returned null, which was then treated as zero, yielding an impossible full-arm count of 10000. It caught that inconsistency and repeated with `$_ .PSObject.Properties[field].Value` (without the space after `$_`) and an explicit missing-field error. Its corrected counts agree with the independent Python results above. No result file was changed by that parent error. The Python checker uses explicit CSV dictionary keys and float conversion; missing keys raise rather than become zeros.

Interior exact-zero and near-zero counts remain generally unreconstructible from minima/maxima/means: a negative minimum does not tell whether another seed equals or nearly equals zero. This correction does not establish those complete counts, replay bootstrap draws, or widen the review to retrieval/provenance. All previously implemented checks pass again. REVIEW_HASHES.json now binds this correction, the revised checker/output, and the unchanged original report.
