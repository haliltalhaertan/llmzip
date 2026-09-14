# V52 static-storage V9 — no retained consumption snapshot

Status: **REPAIR CANDIDATE / NOT INDEPENDENTLY AUDITED / NOT FROZEN / NO MEASUREMENT AUTHORIZATION**.

Parent V8: `0cb4aba586d85974dc9d9a4ea4215abc6d30cbac`.

V9 repairs V8-LEAD-001 without rewriting V8.

- It pins the three V8 implementation modules by exact raw SHA256 and executes their authenticated source bytes in fresh private namespaces.
- `preflight_longmemeval_v9(...)` runs a full V8 fresh preflight once to establish readiness, then discards the returned snapshot.
- `V9Context` retains only paths and externally frozen hash identities. It has no `initial_snapshot` field.
- `fresh_snapshot()` reruns the complete pinned V8 chain every time.
- `authoritative_denominators()` obtains denominators only from that fresh snapshot.

This enforces the fresh-consumption requirement mechanically at the V9 API boundary rather than only in prose.

Threat-model boundary: like the reviewed parent guard, V9 is not a sandbox against arbitrary code that can rewrite the V9 module itself inside the trusted process. Runtime integration/runner pinning remains a separate open obligation.

Scope remains LongMemEval-only. LoCoMo remains blocked pending a separate reviewed anchor profile.

V9 creates no literal actual plan and measures no storage. Task4F1 remains `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
