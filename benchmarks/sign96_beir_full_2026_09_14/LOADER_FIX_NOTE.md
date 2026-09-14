# Full BEIR wave-1 loader correction

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

The first full-BEIR workflow attempt (`34872154251`, head `93472f9437124b3633889406d59d37e35b9b8aca`) exposed a loader/evaluation-boundary bug after rankings had already been frozen and before any benchmark metric was produced for the affected tasks.

## Observed failure

BEIR `queries.jsonl` may contain query IDs belonging to more than the requested evaluation split. The initial runner ranked every query, then—after opening `qrels/test.tsv`—incorrectly required every query in `queries.jsonl` to have a positive test qrel.

Examples from the failed attempt:

- SciFact ranked all 1,109 query rows and froze them before qrels; the test qrels cover 300 evaluated query IDs.
- ArguAna ranked all 1,406 query rows and froze them before qrels; five query rows were not positively judged in the test qrels.

The failure occurred at the post-freeze validation step. It did not use observed FLOAT96-vs-SIGN96 metric outcomes to choose or tune the correction.

## Correction

`run_beir_full_v2.py` preserves the original outcome-blind boundary:

1. Fit on corpus documents only.
2. Transform and rank every query from `queries.jsonl` without reading qrels.
3. Freeze and SHA-256 hash all top-100 rankings.
4. Only then open the requested split qrels.
5. Score only query IDs that occur with positive relevance in that split.

This matches the split semantics of standard BEIR evaluation. No task selection, representation definition, centering, FLOAT96 scoring rule, SIGN96 scoring rule, nuisance-trial count, top-k cutoff, or metric definition was changed in response to an outcome.

The corrected workflow must run from a new commit/run. Results from the failed loader attempt are not scientific outcomes and must not be mixed with the corrected run.
