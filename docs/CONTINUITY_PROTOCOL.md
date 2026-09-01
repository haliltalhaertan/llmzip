# Continuity Protocol — crash-safe, multi-agent research operations

## Purpose

No research state is allowed to live only in an agent's chat, memory, terminal session, or uncommitted files. A replacement agent must be able to resume from Git alone, plus explicitly named external inputs, without guessing what occurred.

`ops/CURRENT_STATE.json` is the machine-readable present state. `docs/CONTINUITY_LEDGER.md` is the append-only transition record. `START_HERE_V52_4F1.md` is the human-readable entry point. They are jointly authoritative for operational resumption; frozen seals/manifests remain authoritative for their own bytes.

## Before any action

1. Checkout the exact tag or commit named in `ops/CURRENT_STATE.json`.
2. Confirm a clean worktree and record `git rev-parse HEAD`.
3. Run `python -B tools/verify_continuity_state.py`.
4. Read the authority-order files listed in the state manifest.
5. If any anchor, state, or ledger fact disagrees, stop. Create no result and report `CONTINUITY_BLOCKED` with the mismatch.

## Stage lifecycle

For every load-bearing step:

1. **Claim:** Head Researcher appends an `IN_PROGRESS` entry with one bounded scope and creates an isolated branch/worktree for each worker.
2. **Execute:** the worker changes only its declared scope; immutable candidate, seal, manifest, and prior-audit namespaces are read-only.
3. **Verify:** record commands, exit status, hashes, counts and permitted negative controls. Never record or summarize forbidden outcomes.
4. **Close:** append `PASS`, `BLOCKED`, `ABORTED`, or `CONTAMINATED`; update `CURRENT_STATE.json` to one next action; commit both together.
5. **Anchor:** tag the closed state and push the commit, tag and any permitted worker branch. A successor may trust only a pushed, hash-verified anchor.

Do not bundle unrelated stage transitions in one commit. A micro-edit may share a stage commit only when it has the same predecessor, scope and verification gate.

## Parallel work

- One Head Researcher is the sole writer of `CURRENT_STATE.json` and the ledger.
- Every worker has an isolated clone/worktree and branch. Workers exchange only declared handoff payloads, not shared mutable directories.
- An independent auditor must be cold-start: it may read committed artifacts and the audit prompt, but not another agent's claimed verdict or private chat reasoning.
- A worker cannot seal, preregister or run Task 4F1. The Head Researcher cannot call its own implementation work an independent audit.

## Recovery and incident rule

If an agent stops, crashes, loses context or returns an ambiguous result, the successor starts at the last pushed ledger entry and runs the verifier. Uncommitted work is untrusted and must be re-derived in a new namespace.

If a hard stop is crossed, immediately stop the affected activity; preserve command facts and file hashes; label the entry `CONTAMINATED`; do not inspect or interpret any outcome; and request a Head Researcher containment decision. Never delete or rewrite historical evidence to conceal the event.

## Task 4F1-specific boundary

The active state is V3 independent audit pending. Permitted work is limited to the V3 prompt's outcome-free static, synthetic and representation-canary checks. `--mode run`, `--mode finalize`, real ranking, real scoring, valid authorization/HMAC construction and outcome interpretation remain prohibited until separately authorized after a passing independent audit and preregistration decision.
