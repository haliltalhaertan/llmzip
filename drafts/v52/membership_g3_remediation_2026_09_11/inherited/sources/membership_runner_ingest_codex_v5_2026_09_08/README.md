# Codex v5 repair — runner/ingestion

Status: **IMPLEMENTED / IMPLEMENTATION-TEAM TESTS PASS / CLAUDE AUDIT PENDING**.
Not a seal, not a scientific acceptance, not permission to run on real data.

## Scope and ownership

The user asked Codex to repair the remaining issues using subagents, leaving the audit to Claude.
Two implementation-team agents reviewed error/evidence paths and test adequacy in parallel; the
parent integrated the changes and ran the final validation. Their work is not an independent audit.
No M-1/M-2/M-3 implementation, raw corpus inspection, real retrieval, real bootstrap, pilot, HMAC,
seal, canonical ledger edit, or main-branch edit was performed. Only this new namespace is added.

Base candidate: `86a8fd7a73a0d4e045666e692cd7e2016f134885`.
Source closure report:
`6b3de298850edf7a7696683726316b83909f5b6e:audit_v52_runner_ingest_v4_closure_2026_09_08/V4_CLOSURE_REPORT.md`.
Its SHA256 is `8ccde7f464ec1206d0fce3feeb3305eb5226f0212e1d62f148bde4c52e3f0ea2`.
Remote main observed at start: `a5bc6bd272402a8b6d7e823fde21a6b367a6f0bd` (not edited).

## Actual repair

| Item | Change | Evidence |
|---|---|---|
| Stale/overbroad docstrings | Runner, ingest, error formatter and diagnostic descriptions now describe their distinct roles and limits; accepted dict-ID string conversion is acknowledged | Review source delta; no prose keyword test is claimed to prove behavior |
| Vacuous evidence test | Replace sentence-word check with malformed object at first/middle/last positions; require named refusal, no result and zero coercion hooks | Both candidate suites |
| Vacuous no-corpus test | Remove empty-list comprehension; install Python audit-event guards, observe a nonempty fake-source ledger, and deliberately refuse synthetic nonexistent outside paths | `guarded_suite.py`, `test_codex_v5.py` |
| IdentifierKind spoof | Exact enum type and member identity, canonical labels; no isinstance-only acceptance | Fake `__class__`, payload access counter, valid/invalid identifier probes |
| Adjacent formatter bypasses | Closed field labels; exact builtin scalar types; refuse foreign enums, numeric subclasses, spoofed code and malicious type names with fixed errors | Five isolated original-v4 control assertions plus repaired candidate probes |
| Diagnostic custom objects | Opaque custom/nested objects; no custom repr/type name/length hooks in `describe` | Four diagnostic regression cases |

`membership_runner_v4.py` / `corpus_ingest_v4.py` filenames are intentionally retained inside the
new namespace for import compatibility. Runtime version fields explicitly say **Codex v5**.
`IdentifierKind` is now defined in `errors.py` and re-exported by the runner. The error formatter
accepts builtin bool/int/float/None diagnostics and canonical IdentifierKind values. NumPy scalar
objects and custom numeric subclasses are deliberately rejected as error fields; current call sites
use builtin counts/constants. This is a diagnostic API narrowing, not a numerical estimand change.

Evidence normalization, accepted gold behavior, source mapping, accepted seeds, core computation and
real-data gates remain inherited. Ingestion code changes are descriptions/version labels only;
its callees receive the formatter hardening. Existing `authoritative/` values are unchanged except
the package-version label. `resolve_sources.py` is byte-identical to its predecessor.

## Validation

Final evidence is in **`evidence_final/`**. `evidence/` is the earlier successful implementation
run before final version-label/doc cleanup; it is retained as a development record, not the final
source-to-result binding.

- Adapted inherited runner/ingest suite: **68 checks**, exit 0.
- New adversarial suite: **45 team checks**, plus **5 original-v4 negative-control assertions**
  in an isolated process, exit 0. These counts are not unique defect counts or proof of completeness.
- Unchanged core regression suite: **99 checks**, exit 0; not a reopened independent core audit.
- All three stderr captures are empty; outer guards report zero denied data-file accesses.
- Inner guard explicitly exercises three expected denials against nonexistent synthetic paths.
- Environment: Python 3.13.15, NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3;
  `PYTHONHASHSEED=0`, OMP/OPENBLAS/MKL/NUMEXPR thread variables set to 1. No installation performed.

To replay, use that interpreter, byte-preserving checkout and a **new** output directory:

```text
python -B drafts/v52/membership_runner_ingest_codex_v5_2026_09_08/validate_candidate.py --output <new-directory>
```

No argument performs read-only payload verification. The writer refuses an existing output folder.
Saved stdout may contain synthetic temporary path names; exact whole-log equality between replays is
not required. Compare outcomes, exit codes and named assertions, not ephemeral paths.

## Identity and governing chain

`PAYLOAD_HASHES.json` inventories the final candidate files, excluding itself. Hash its raw Git blob
and all payloads from the candidate commit; do not normalize line endings to obtain a match.
`authoritative/accepted_configuration.py` points at the acceptance document and configuration with
exact commit/path/SHA256, the two accepted manifests, superseded LME v1, bootstrap seeds and core.
The historical PROPOSED strings do not supersede the external acceptance; no historical bytes change.
No new cohort, seed, statistical band, scientific interpretation or environment selection is made here.

## Limits to carry into Claude's audit

- No claim that every Python exception is sanitized: `from None` suppresses display, not the stored
  context chain. OS/library failures and caller behavior are not a universal confidentiality proof.
- Diagnostic digests reveal equality and may permit guessing low-entropy values. They are not secrecy.
- The output structural schema/length policy cannot recognize arbitrary short source content.
- Python I/O hooks observe Python events, not arbitrary native I/O. The old-control child installs
  its own guard; this is synthetic test evidence, not a machine-wide sandbox claim.
- Existing stamps are not cryptographic authority against an adversarial Python caller mutating
  globals/objects. No new security claim is made for them.
- The closed core, scientific protocol and real experiment remain outside this delta. No genuine
  outcome was produced. M-1/M-2/M-3 are still absent and require their own authorized work.

The next step is Claude's scoped implementation audit, not an automatic new remediation cycle or run.
