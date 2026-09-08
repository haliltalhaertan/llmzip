# Claude audit handoff — Codex v5 repair

The user assigned implementation to Codex and audit to Claude. Audit this candidate; do not accept
the implementation-team tests as your own audit. Prefer a fresh Claude context. If prior involvement
is retained, disclose it rather than claiming cold-start independence.

Branch: `codex/v52-runner-ingest-repair-2026-09-08`.
Namespace: `drafts/v52/membership_runner_ingest_codex_v5_2026_09_08/`.
Resolve the exact pushed commit supplied in the handoff and record it before reading/running.
Base: `86a8fd7a73a0d4e045666e692cd7e2016f134885`.
Prior audit: `6b3de298850edf7a7696683726316b83909f5b6e`, path and hash in README.

1. Verify raw Git blob hashes against PAYLOAD_HASHES.json; verify the diff adds only this namespace.
   Read the governing chain in authoritative/accepted_configuration.py. Preserve all old bytes.
2. Inspect the delta: false descriptions, both vacuous tests, enum identity spoof, closed error
   labels/scalars/canonical enum, and custom diagnostic object handling. Check legitimate inputs and
   existing error paths still work. Examine whether field allowlisting misses a current call site.
3. Replay validate_candidate.py in the recorded interpreter with a fresh output folder, synthetic only.
   Independently challenge the changed behavior; reproduce original-v4 defects in isolated processes
   to avoid sys.modules cross-version contamination. Assess tests, not their counts or names.
4. Treat accepted evidence normalization and scientific computation as preserved; check regressions
   without reopening the experiment, changing cohort/gold/seeds, or adding M-1/M-2/M-3.
5. Do not demand a universal confidentiality guarantee the candidate does not claim. Distinguish
   JSON/data-path defects, supported Python API defects, and adversarial arbitrary-code callers.
6. Report exact actionable failures with minimal synthetic reproduction and classify nonblocking
   observations separately. Do not change candidate files. Save your report/tests/hash inventory in
   your own audit namespace and push that audit branch; do not auto-remediate or merge.

Forbidden: real corpus reads/scans/hashes/downloads, real fitting/retrieval/ranking/bootstrap,
past experiment replay, pilot, seal, HMAC, run/finalize or Task 4F1 actions.
Permitted: code/documents/bound metadata identities, synthetic files and tests only.

Return: verified candidate commit; PASS/FAIL limited to this repair; findings; audit commit and raw
report hash. A PASS does not authorize the real experiment. Canonical main/ledger remains the
designated Continuity Lead's responsibility; Codex has not changed it.
