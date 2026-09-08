# Verification — implementation team only

2026-09-08: replay.py completed all four suites in separate sequential processes.
All eleven recorded dependency versions matched; Python3.13.15 matched.

- Audit regression: 12 unittest methods PASS; includes4000 exact-array top-k
  comparisons with the hash-verified historical arithmetic AST, all three branches.
- New in-memory end-to-end integration: 5 unittest methods PASS; LoCoMo corrected
  gold through scoring, both10000-replicate bootstraps and create-only synthetic
  output; LongMemEval all-source ordinal through scoring and question bootstrap.
- Source contracts: 10 unittest methods PASS.
- Closed core regression: exit0, ALL PASS (custom checks, not unittest methods).

No initial failure occurred in the parent integration/replay runs. Agent development
ran an initial10-method audit suite successfully before adding two further methods;
the delivered suite has12. This is implementation testing, not a cold-start audit.

F3 gate implementation expands from48 flipped coordinates to96 predetermined
single-coordinate canaries. Test cases cover both zero directions and cancellation.
No real zero occurrence inspected; a real failure must stop, not change convention.

Identity: core and contracts loaded as verified raw Git bytes. Working-tree line
endings are not normalized or blessed. Replay source hashes record the on-disk
candidate Python bytes actually used. Payload inventory separately records all
delivered files except itself. No readiness/seal claim follows from either.

No real corpus or historical outcome read. No production run/finalize, HMAC, seal,
pilot, download or data-source hashing. Synthetic representation/scoring/bootstrap
did run. Existing core test creates a temporary synthetic JSON file; integration
test creates and removes its own synthetic output folder. These are not results of
the proposed experiment. Independent review and production obligations remain open.
