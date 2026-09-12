# Independent zero-trust audit — static-storage PLAN-prep V3

Object under audit: `3fab24bce46203348935492ba8276b9920aea898`
Branch of object: `codex/v52-static-storage-plan-prep-v3-2026-09-12`
V2 repair candidate referenced by the object: `ecd839b6519be9e56d3ead88c4bab8f7b30ff7b3`
Immediate git parent of the object: `695e403dbd37691205b465531c62effea99ecbd4`
Canonical context observed: `main@5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`, ledger `L-095`
Auditor environment: Python 3.11.15

## VERDICT: REQUEST_CHANGES

The three inherited P2 findings are CLOSED. The verdict is REQUEST_CHANGES because
one blocking defect was found in the pipeline V3 is a component of, and the declared
next step after a pass is literal actual-plan freezing, which would freeze that defect
into the plan.

PLANPREP3-AUD-001 is NOT a V3 regression. V3 did not introduce it and V3's namespace
is not where it should be fixed. It is raised here because passing V3 authorizes the
step that would make it permanent.

This verdict means none of: storage measured, <=12 proven, actual plan approved,
real adapter ready, retrieval ready, Task4F1 authorized.

## What was actually executed by this audit

The six V3 files were read from the exact commit. The two Python files were extracted
by `git show` and hashed:

- `storage_adapter_preflight_v3.py` sha256 `66782f39dc99cea225ac89eeb0498e5f88c7115e4f143f5fb949a12bfccbbeb2`
- `test_storage_adapter_preflight_v3.py` sha256 `6d8deddb3ddf7c3b546c792102b8756dc32af616b87034b963aad5174b09a58d`

The prepared suite was re-executed independently: 4 tests, exit code 0, all OK. The
receipt lists five covered controls against four test methods; this is consistent
rather than contradictory - the first method asserts both authenticated-byte
persistence and the two denominator states. No discrepancy is claimed.

Twelve adversarial probes were then written and executed against the preflight
directly. Raw output is in `raw_outputs/EXECUTION_RAW.txt`; the probe source is in
`raw_outputs/adversarial_probes.py`.

## Closure of the three inherited P2 findings

**PLANPREP2-AUD-001 authenticated consumption / TOCTOU — CLOSED (scope-limited).**
`read_bytes` opens the artifact once and returns that buffer; `authenticate` hashes
that same buffer; the buffer is carried in `VerifiedFixture.raw_bytes` and
`VerifiedPhysicalCopy.raw_bytes` inside `@dataclass(frozen=True)` containers. Python
`bytes` is immutable and the frozen dataclass blocks attribute rebinding, so the
authenticated content cannot be swapped after the check. Reproduced: mutating the
source file after preflight leaves the returned bytes unchanged. A residual
resolve-then-open window exists in `safe_child` -> `read_bytes`, but any substitution
in that window changes the digest and is rejected, so content authenticity holds.
The limitation V3 states about itself is accurate: the consumption boundary is a
design contract and no real adapter implements it. Closed for what V3 controls.

**PLANPREP2-AUD-002 strict JSON / ambiguous content — CLOSED.**
`_pairs` rejects duplicate keys; `parse_constant` rejects the NaN/Infinity literals
and `_bounded` independently requires `math.isfinite`; `fields()` enforces exact key
sets on every nested fixture section; depth, entity count and string length are
bounded. Reproduced: duplicate key rejected, nonfinite rejected, extra field inside
`transform` rejected.

**PLANPREP2-AUD-003 N=0 producing D_k=0 — CLOSED.**
`verify_physical_artifact` maps `count == 0` to `(pop_id, "EMPTY_NO_AMORTIZATION", None)`
and a positive count to `(pop_id, "POSITIVE", count)`. No division is performed and no
zero denominator is emitted. Reproduced on both branches of the condition.

## New findings

### PLANPREP3-AUD-001 — BLOCKING — the amortization denominator has no external anchor

`D_k` is derived as `populations[pop_id]["count"]`. The parent `measurement_plan_guard`
binds that count to the probe: `pop["count"] == p["N"] + (q if AFTER)`. That is a real
internal-consistency check and it holds.

There is no check above it. Probe `N` is validated only as `_integer(p["N"], "N")`,
i.e. anywhere in `[0, 2**63-1]`. Nothing requires probe `N` to equal, or be bounded by,
the archive's declared `N_i`. And `N_i` itself is validated only as a positive integer:
grep over the guard shows `N_i` used as an archive field, in the weighting labels, and
in the cost-reporting stage - never bound to the frozen archive-size source
`docs/v52/task4c2/V52_T4C2_feature_geometry.csv`. That CSV is named in inventory
documents and in the V1 spec JSON, and in no executable guard.

Consequence: the chain is internally consistent and externally unanchored. A declared
`N` that exceeds the real archive dilutes `effective_persistent_bytes_per_vector`
without limit, and both guards pass. The staircase panel deliberately uses probe `N`
values that differ from `N_i`, so simple equality cannot be the fix.

This is the one field the entire cost claim rests on, and it is the one field with no
external binding. It is also exactly the shape the measurement contract set out to
prevent: the contract states that `D_k` is the real group cardinality and not a
theoretical sharing estimate, and no mechanical check enforces that sentence.

Suggested direction, not a prescription: bind each archive's `N_i` to the frozen CSV
by digest and row identity in the guard; mark every probe as either the archive's
full-size probe or a declared diagnostic staircase point; and allow a physical copy's
denominator to derive only from a full-size population, with diagnostic points barred
from contributing a denominator at all.

### PLANPREP3-AUD-002 — MODERATE — the CORRUPT control can be made vacuous

`validate_fixture_payload` bounds `xor_mask` to `[1, 255]`, which correctly excludes
the no-op mask 0. `byte_offset` carries the default bound `[0, 2**63-1]` and is not
constrained against the length of whatever it corrupts. An out-of-range offset yields
a control that corrupts nothing while still being declared and authenticated.

This matters more than its size suggests. The item-necessity discipline recorded as
F2 rests on BASELINE / REMOVE / RESTORE / CORRUPT, and CORRUPT is the leg that proves
an item's bytes are load-bearing. A vacuous CORRUPT turns a necessity proof into a
passing no-op. Reproduced: `byte_offset = 10**12` accepted.

### PLANPREP3-AUD-003 — LOW — preflight's fail-closed claim exceeds its implementation

Plan sub-fields are read without validation: `plan_fixture["sha256"]`,
`plan_copy["artifact_sha256"]`, `plan_copy["population_ids"]`, `populations[id]["count"]`.
`unique_index` checks only that an `id` key exists. Missing sub-fields therefore raise
`KeyError`, not `PreflightError`. Reproduced for all three.

In the declared execution order the parent guard runs first and rejects these plans
with exact-field checks, so this is not a live hole today. It is a defense-in-depth
gap: `CONSUMPTION_BOUNDARY_V3.md` states an unconditional fail-closed list, and a
caller that catches `PreflightError` would not catch these. Two guards whose safety
depends on always being called in order should each be safe alone.

### PLANPREP3-AUD-004 — LOW — divergent constants between the two guards

`measurement_plan_guard.MAX_ENTITIES = 1024`; `storage_adapter_preflight_v3.MAX_ENTITIES = 4096`.
The stricter one gates first, so there is no hole. Two guards that must agree about the
same plan carrying different limits is latent drift, and the V2 capacity repair was
sized against the 1024 figure.

### PLANPREP3-AUD-005 — LOW — a zero-byte physical artifact is accepted without evidence

`source_raw_byte_length` is bounded at minimum 0 and a zero-length artifact passes.
The measurement contract requires that writing zero bytes be accompanied by verifying
that the corresponding persistent requirement does not exist. No such evidence is
required here.

## Probes that looked like defects and are not

Seven probes were rejected by the parent guard rather than by preflight, and are
recorded here so the finding count is not inflated: empty plan rosters (`_index`
nonempty); arbitrary extra top-level plan keys and missing required plan sections
(exact top-level `_fields`); duplicate `population_ids` within one physical copy
(`_refs` calls `_unique`); and a population count raised without raising the probe
(`pop["count"] == p["N"] + q`). The combined pipeline is materially stronger than
preflight read alone. The residue of that last one is PLANPREP3-AUD-001: raising the
probe `N` as well passes everything.

## Honesty of V3's own claims

V3's self-limitations were checked against its code and found accurate. It says the
consumption boundary is design-only and not implemented in a real adapter; that is
true. It says fitted artifacts, ID/offset representation, physical copies, sharing
populations and serializer identity remain unresolved; nothing in the six files
contradicts that. The test receipt does not overstate: it labels itself local,
synthetic and non-independent, and it separates unrelated environment stderr from the
unittest result rather than hiding behind it.

## Scope statement

No Task4F1 corpus, query, gold or outcome was opened. No retrieval scoring, recall,
HMAC, seal, finalize or run was performed. No model was fitted. No file outside this
audit namespace was created or modified. `main`, the ledger and `ops/CURRENT_STATE.json`
are untouched and no merge was made. Task4F1 remains
SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN.
