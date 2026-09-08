# Source-contract decision and synthetic implementation

Status: USER-APPROVED CONTRACT / SYNTHETIC IMPLEMENTATION / NOT EXECUTION READY.

The user explicitly approved the preceding reconciliation in this conversation.
This is the implementation author's record of chat authorization, not a signed
independent attestation. Continuity Lead retains sole ownership of main/state/ledger.
Base preparation: ed4e22c520b7dc0ae2f43f915e0c621070c72a87.

## Accepted interpretation

- LoCoMo: preserve the accepted 1,535 IDs and their archive mapping. Apply historical
  correction replacement for their gold, including a present-but-empty correction.
  Never reselect/drop questions, union raw and corrected evidence, or fall back from
  an empty correction. Empty/unresolved gold stops. This supersedes the L-075
  no-correction-reading restriction only as necessary for gold resolution, not cohort
  selection. Actual file reading remains unauthorized.
- LongMemEval: priority ordinal is zero-based lexical rank over ALL 500 source IDs.
  Sharding preserves source order after excluding `_abs`, then uses position modulo
  ten over 470 primary IDs. Bound manifest ordering must not select priorities.
- Existing arms, rotation/partition/bootstrap seeds, core and old payloads unchanged.

## Source anchors, read as code only

LoCoMo: 692f599eedeb7e7a649443f24ff507e8c4d1c17d,
research/v52/locomo_sign_mechanism_replication.py (load_dataset).
LongMemEval: 0c9916bd7786d7ddb332f5b6da3d96d61a6223f0,
research/v52/longmemeval_coordinate_scale_shard.py and
research/v52/longmemeval_boundary_localization_shard.py (run_shard/eval_one).
The former's header says sorted primary sharding; both actual functions preserve
source order. The accepted rule here explicitly follows those functions.

## Delivered boundary

Pure helpers consume normalized fake dictionaries/lists. No source reader, old
ingester mutation, correction-file loader, model import, scoring call, writer,
bootstrap, native-anchor construction or real driver is implemented here.
The full correction inventory identity, historical normalization parity and raw
source identity remain required BEFORE a production connector can be accepted.
Caller-supplied structures are not authenticated by these pure helpers.

This resolves the two policy choices and tests their pure semantics; it does NOT
close execution-prep audit F1-F7, the nine test gaps, native-anchor provenance,
finalizer integration, independent acceptance or the pre-run seal. No whole-package
PASS is claimed. Synthetic reduced count overrides are not production authorization.

Next: integrate these contracts in a new complete candidate with identity-bound
correction input and source ordering, repair remaining audit findings, then independent
review. No corpus access, fitting, ranking, pilot, HMAC, seal or real run authorized.
