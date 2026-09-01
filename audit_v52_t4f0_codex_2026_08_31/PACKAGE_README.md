# Audit package index

Primary decision files:

- `V52_T4F0_CODEX_INDEPENDENT_AUDIT_REPORT.md`
- `EXECUTIVE_VERDICT.txt`
- `DEFECT_TABLE.csv`
- `SCALE_FEASIBILITY.csv`
- `REPRESENTATION_REPEATABILITY.csv`
- `LEAKAGE_AUDIT.csv`

Corpus and evidence files:

- `pinned_tree_manifest.json` and `materialization_hash_log.json`
- `corpus_audit_summary.json` and `conversation_inventory.csv`
- `question_census.csv` and `question_taxonomy_counts.csv`
- `source_id_join.csv`, `duplicate_message_ids.csv`, and `question_annotation_anomalies.csv`
- `estimand_summary.json` and `estimand_primary_cohort.csv`

Representation evidence:

- `representation_{100K,500K,1M,10M}_{A,B}.json`

Audit scripts:

- `materialize_pinned_beam.py`
- `audit_beam_corpus.py`
- `analyze_beam_anomalies.py`
- `derive_estimand_cohort.py`
- `audit_representation_transfer.py`

`AUDIT_OUTPUT_HASHES.json` inventories every other delivered file. The 804 MB materialized corpus is intentionally not duplicated into this delivery; its pinned path/blob/hash inventory is preserved in the two materialization manifests. No frozen Task 4C3/4D/4F0 artifact was modified.

