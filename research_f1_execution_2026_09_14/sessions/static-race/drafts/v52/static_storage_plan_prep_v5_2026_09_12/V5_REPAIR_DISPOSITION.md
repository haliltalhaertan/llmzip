# V52 static-storage PLAN-prep V5 — repair disposition

Status: **REPAIR CANDIDATE / NOT AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION.**

Object repaired: `drafts/v52/static_storage_plan_prep_v4_2026_09_12` at
`81928414eaeb0e442d0750a56fd268025bc05722`. Its bytes are not rewritten, and neither are
V3's at `3fab24bce46203348935492ba8276b9920aea898`.

An independent cold-start audit of V4 returned REQUEST_CHANGES. It confirmed seven of
nine repair claims under attacks the shipped tests did not attempt — hard links, bind
mounts, character devices, unix sockets, procfs, a file growing under the reader — and
found two claims false on findings V4 listed as repaired. **Both were reproduced by this
session before being accepted.**

## The two that mattered

**AUD-009 was not closed.** A lone UTF-16 surrogate in `physical_locator` or
`relative_path` escaped as `UnicodeEncodeError`, while the module docstring asserted
"nothing else may escape". `Path.resolve()` raises a `ValueError` subclass while encoding
for the filesystem, and `safe_child` caught only `OSError`. V4 had already learned this
one frame later — `read_bytes` catches `ValueError` with the comment "embedded NUL, etc."
— so the guard was simply missing in one place. Reproduced here on a `pb.json` that is
pure ASCII and valid UTF-8.

**AUD-007 was opt-in.** `guarded_plan_sha256` and `guarded_contract_sha256` defaulted to
`None`, and omitting them skipped the check entirely — the V3 hole verbatim. Reproduced:
plan A guarded, plan B preflighted, accepted, with plan B's inflated population count
flowing into the returned denominator state. The contract digest was also never derived
from bytes: the parent guard opens `contract_path`, V4 compared two caller-supplied
strings, so `VerifiedBindings.contract_sha256` recorded a declaration and the disposition
called it an authentication.

## Repairs

| Finding | Repair |
|---|---|
| AUD-009 surrogate leak | `safe_child` catches `(OSError, ValueError)` |
| AUD-007 opt-in binding | all ten arguments required; omitting the digests is a `TypeError` from the signature |
| AUD-007 unauthenticated contract | `contract_path` is read and hashed; the chain bytes == expected == plan's == guarded is enforced |
| N2 array bound | `MAX_ARRAY_ENTRIES = 4096` split out from `MAX_ENTITIES = 1024`, matching the parent on both |
| N3 quadratic read | chunks are collected and joined once, not concatenated |
| N4 schema collision | physical-copy bindings move to version 4; `CONSUMPTION_BOUNDARY_V5.md` ships with it |
| N6 fixture dedup | one inode map covers fixtures and copies, so a fixture cannot share a file with a copy |
| N7 empty roster | an empty physical-copy roster is refused |

## Documentation corrections the audit asked for

- `read_bytes` no longer claims to "never follow a symlink". It does not, for the final
  component; artifact locators arrive already resolved by `safe_child`, so a symlink to a
  regular file inside the binding directory is accepted by design. The docstring now says
  that.
- The contract digest is described as authenticated only now that it is.
- The `MAX_ENTITIES` claim is stated per bound rather than as a blanket match.
- "nothing else may escape" is gone as an absolute; the boundary document lists what
  fails closed and names the one refusal that is a `TypeError` instead.

## Left open, deliberately

AUD-001 and AUD-008 are not repaired here. They are closed separately by
`drafts/v52/static_storage_anchor_guard_2026_09_12`, which must run between the plan
guard and this preflight. **Nothing in this module enforces that it ran**, and V5 still
reports denominator states without selecting among them. A caller that skips the anchor
guard gets an unanchored effective cost and no warning, which the boundary document now
says in the execution order.

The audit also noted that the corruption offset is bounded against the fixture bundle's
JSON container rather than the payload the control damages, and that the `UNKNOWN`
sentinel in `absence_basis` is case-sensitive and unstripped so `"unknown"` passes. Both
are accurate. Neither is repaired here: the first needs the CORRUPT control's target to
be declared, which is a schema question, and the second matches the parent guard's own
idiom. They are recorded rather than silently carried.

## Evidence

`test_storage_adapter_preflight_v5.py`, 31 tests, all passing on Python 3.11.15.
Differential against V4, same inputs:

```
V4   surrogate locator                 *** UnicodeEncodeError
V4   guard binding omitted             ACCEPTED
V4   contract digest matches no file   ACCEPTED
V5   surrogate locator                 PreflightError: cannot resolve path: UnicodeEncodeError
V5   guard binding omitted             TypeError: missing 2 required positional arguments
V5   guarded plan digest is plan B     PreflightError: guarded plan digest does not match
V5   contract file tampered            PreflightError: contract: SHA256 mismatch
```

## What this does not mean

Not: storage measured, `<=12` proven, actual plan approved, real adapter ready, retrieval
authorized, Task4F1 authorized, V5 audited. V5 needs its own independent cold-start
audit, and so does the anchor guard.

Task4F1 remains SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. No
corpus, query, gold or outcome was opened; nothing was fitted, measured, scored or
sealed; `main`, the ledger and state are untouched and no merge was made.
