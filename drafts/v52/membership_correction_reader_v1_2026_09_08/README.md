# Fail-closed correction reader: synthetic preparation

Base commit: 271f63dfd4dc19c274b6d1488b68de00a86867e1.
Status: SYNTHETIC_READER_NOT_EXECUTION_READY.

## Authorization and scope

User approved the proposed rule in this conversation: unsupported/malformed
correction input or repeated correction IDs must stop; no skipped records,
last-write-wins selection, gold repair or cohort changes. This is the author's
record of chat authorization, not independent acceptance. Implementation and
testing are restricted to generated inputs. No real source access is authorized.

This package implements a byte-reader, not a filesystem acquisition layer. Tests
write/read temporary generated JSON files, then provide those bytes to the reader.
The module itself opens no file or network. A real entry point refuses E-R-016.
The byte API cannot determine whether callers supplied synthetic or real content;
the restriction is governance, not a claim of automatic origin detection.

## Contract

`parse_verified(payloads, expected)` requires an exact filename set and validates
all expected byte sizes and SHA256s before parsing any JSON. Expected identities
are caller-supplied: a matching result is NOT proof of an accepted inventory.
Production must bind the previous source-identity package independently; the test
inventory is generated from fake bytes and must never be presented as that binding.

JSON must be UTF-8, top-level lists of objects with nonblank string question_id.
IDs with leading/trailing whitespace are rejected, not trimmed. Repeated IDs
across or within files are rejected even if their values agree. Duplicate JSON
object keys are rejected recursively, including ignored metadata. Nonstandard
NaN/Infinity literals and float overflow to infinity are rejected.

Evidence presence is preserved: absent key produces {}; null or [] produces a
present empty list. Strings use historical D-digit:digit regex extraction, with
literal fallback when no match exists. Lists may contain nonblank strings or
identifier dictionaries. Dictionary dia_id/id values are nonblank literal strings,
not regex-parsed or coerced. Both aliases may be present only when literally equal;
otherwise reject, never select an alias. Other identifier-object metadata is not
projected. Blank evidence, unsupported types and malformed objects stop. Stable
deduplication follows the existing unique-reference contract. Per-string duplicate
references are deduplicated early; declared counts are unique normalized IDs, not
raw occurrence counts. No trimming or relabeling of evidence is performed.

Return values contain only question IDs and optional normalized correct_evidence.
Other row metadata, including correct_answer and error_type, is outside this gold
projection and not returned. Rejecting malformed gold-relevant fields does not
mean all unrelated metadata schemas are validated.

ReaderError messages are code-only, raised outside decoder exception handlers to
avoid implicit decoder context. No confidentiality claim covers hostile custom
Python objects, concurrent caller mutation, caller logging or traceback locals.

## Verification

Approved Python3.13.15, -B, stdlib-only execution:

    python -B -m unittest discover -s drafts/v52/membership_correction_reader_v1_2026_09_08 -p "test_*.py" -v

23 test methods PASS: 17 agent-written negative/positive reader tests, six parent
bridge/edge tests. Generated-file bridge executes the SHA256-verified raw Git
contracts.py at56e67018b61c32fd0392f0d8f4234e731faf8ce9, hash
15d5f102d6207755d180ca0477d02b1e8bb41a5985fd091bded4771503e99ae4.
Replacement resolves to corrected rows, absence uses raw, present-null/empty stops
E-S-009, and partial resolution stops E-S-014 without dropping references.

Development runs: initial17 methods passed; bridge brought22 passing methods;
finite-float parsing and its regression brought23 passing methods. These are
implementation-team tests, not independent experiment acceptance. Existing
scientific experiments were not replayed and no broader-suite claim is made.

A different subagent statically reviewed the three code/test files and identified
no confirmed defect in this byte-reader scope. Its initial note about numeric
overflow overlapped the parent's float guard addition; it then inspected the
latest guard and regression and confirmed that nuance addressed. It did not rerun
tests. This parent-authored summary is not a separately signed cold-start audit.

Production inventory binding, filesystem acquisition, whole-candidate integration,
Native anchor provenance, finalizer and independent acceptance remain open. No
historical correction/corpus/outcome file was read; no real fitting, scoring,
bootstrap, pilot, HMAC or seal. Main/state/ledger and old packages remain unchanged.
