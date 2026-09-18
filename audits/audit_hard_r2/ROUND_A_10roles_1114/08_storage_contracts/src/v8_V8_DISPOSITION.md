# V52 static-storage V8 — runtime semantic pin and fresh-consumption repair

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION**.

Parent V7: `5eac888b5be36d96fd8219b91bcca8c402c34d16`.
V8 is additive and must not rewrite V7, V6, the older anchor guard, the reviewed contract, `main`, ledger, or state.

## Repairs

### V7-LEAD-001

V8 replaces import-cache loading with `_exec_pinned_module()`:
- source file bytes are authenticated first;
- those exact bytes are compiled directly;
- code executes in a fresh private `ModuleType` namespace;
- a temporary unique `sys.modules` entry exists only while execution needs it for class/decorator resolution;
- the entry is removed afterwards;
- `importlib.import_module` and `.pyc` are not used as authority.

A preloaded/monkey-patched module at the expected path therefore cannot substitute runtime semantics.

### V7-LEAD-002

V8 does not expose V6/V7 frozen dataclasses as the consumption authority.

It converts the verified result into recursively immutable values:
- `NamedTuple` containers;
- `tuple` nested records;
- immutable `bytes`, `str`, and `int` leaves.

Before freezing, every V6 physical denominator must exactly equal the freshly derived V7 semantic proof. Roster coverage must also match.

`V8Context.refresh()` re-runs the complete pinned chain:

`parent guard -> pinned LongMemEval anchor semantics -> V6 external binding preflight -> immutable cross-checked snapshot`.

A future adapter must call `refresh()` immediately before consumption and use that returned fresh snapshot, not an older V6/V7 dataclass.

## Scope

LongMemEval only. LoCoMo remains blocked until a separate reviewed anchor profile exists.

V8 does not create a literal actual plan and does not measure storage.

Still open:
- independent V8 audit;
- canonical repo execution of repo-dependent tests;
- unresolved fitted/projector artifacts;
- unresolved persistent ID/offset representation where applicable;
- actual physical-copy/share evidence;
- final serialization identity;
- real adapter/runner integration;
- external freeze record;
- LoCoMo source-specific anchor profile.

Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
