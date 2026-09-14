# V52 static-storage PLAN-prep V4 — repair disposition

Status: **REPAIR CANDIDATE / NOT AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION.**

Base pinned by its own immutable ref: `3fab24bce46203348935492ba8276b9920aea898`.
Audit that produced these findings:
`audit/v52-static-storage-plan-prep-v3-independent-2026-09-12` at
`b06247df2124edc6953aacf0f7eb69eed99ac1e0`, with `CORRECTION_01.md` superseding parts of
the original report. V3's bytes are not rewritten; this is a new namespace beside it.

## Finding classification, as the takeover procedure requires

| Finding | Class | Repaired here |
|---|---|---|
| AUD-001 no external anchor for `N_i` / headline aggregate | **scientific** | NO - belongs to the plan guard and the plan schema |
| AUD-008 denominator rule yields a menu | **scientific** | NO - same package as AUD-001 |
| AUD-006 non-regular file hangs the open | adapter-boundary | YES |
| AUD-007 no binding between guarded and preflighted plan | adapter-boundary | YES |
| AUD-002 corruption offset unbounded | schema | YES |
| AUD-005 zero-byte artifact without absence evidence | schema | YES |
| AUD-009 OSError/ValueError escape as non-PreflightError | auditability | YES |
| AUD-003 missing plan sub-fields raise KeyError | auditability | YES |
| AUD-010 version fields accept bool and float | schema | YES |
| AUD-011 two copies may bind to one file | auditability | YES |
| AUD-004 divergent MAX_ENTITIES | bookkeeping | YES |

**V4 does not close the two scientific findings and does not claim to.** Until the guard
package lands, this preflight still reports denominator states without selecting among
them, which is why it cannot support an effective-cost figure.

## What changed

- `read_bytes` opens with `O_RDONLY|O_NOFOLLOW|O_NONBLOCK`, `fstat`s the handle it will
  actually read, and refuses anything that is not a regular file. The file checked is the
  file read, and a FIFO is refused instead of blocking. Every `OSError` becomes a
  `PreflightError`.
- `preflight` now takes `expected_contract_sha256` and optional `guarded_plan_sha256` /
  `guarded_contract_sha256`. When the caller states what the parent guard validated, a
  mismatch is a refusal. The plan must itself carry `contract_sha256` matching the
  expected contract, and `VerifiedBindings` now carries the contract digest, so the
  returned object records which contract it was authenticated against.
- `unique_index` takes a `required` tuple and raises `PreflightError` on a missing
  sub-field rather than `KeyError`.
- `corruption.byte_offset` is bounded by the artifact's own length, so the CORRUPT
  control cannot be declared as a no-op. `xor_mask` keeps its correct `[1,255]` bound.
- A zero-byte physical artifact requires a stated `absence_basis`; a non-empty one
  requires that field to be null.
- Physical copies are deduplicated by `(st_dev, st_ino)`, so two declared copies cannot
  resolve to one file, symlink included.
- Version fields go through `exact_version`, which requires the `int` type, so `True` and
  `1.0` are refused.
- `MAX_ENTITIES` is 1024, matching the parent guard, and a new
  `MAX_TOTAL_ARTIFACT_BYTES` bounds the bytes retained across the whole call.
- `VerifiedFixture` and `VerifiedPhysicalCopy` gain `reverify()`, which re-hashes the
  carried bytes. `frozen=True` blocks rebinding only, as `CORRECTION_01.md` recorded; a
  consumer that wants the guarantee must call `reverify()` the way the parent guard
  re-authenticates its own plan object.

## Evidence

`test_storage_adapter_preflight_v4.py`, 23 tests, all passing on Python 3.11.15.

The suite is differential where it can be. `test_aud006_v3_really_hangs_on_the_same_input`
runs the identical fixture against V3 in a subprocess and requires it to time out; if V3
returns, the test fails. The other repairs were confirmed against V3 separately: the same
corruption offset, zero-byte artifact, `version=True` and duplicate-file plans are all
still ACCEPTED by V3 and all refused by V4.

One defect in this session's own first draft is recorded rather than smoothed: the
duplicate-copy check built its message with an eager f-string that indexed the very
dictionary the guard clause was testing for absence, so every physical copy raised
`KeyError`. The tests caught it before the first commit.

## What this does not mean

Not: storage measured, `<=12` proven, actual plan approved, real adapter ready,
retrieval authorized, Task4F1 authorized, V4 audited. This package needs an independent
cold-start audit, and the scientific findings need their own package first.

Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No
corpus, query, gold or outcome was opened; nothing was fitted, measured, scored or
sealed; `main`, the ledger and state are untouched and no merge was made.
