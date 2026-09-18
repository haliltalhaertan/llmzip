# V8 lead follow-up verification

Status: **REQUEST_CHANGES / LEAD VERIFICATION, NOT INDEPENDENT AUDIT**.

Exact parent V8 candidate: `0cb4aba586d85974dc9d9a4ea4215abc6d30cbac`.

## V8-LEAD-001 — P2 BLOCKING — stale initial snapshot remains publicly reachable

V8 correctly makes its frozen snapshot recursively immutable and makes `refresh()` rerun the full pinned chain. But `V8Context` also publicly stores `initial_snapshot`.

Reproduction on the exact implementer source:
- construct a context with an immutable denominator snapshot `(copy=c, population=p, D_k=10)`;
- inspect the public context fields;
- `initial_snapshot.semantic_proof.denominators` remains directly readable without calling `refresh()`.

Thus the code says a future adapter **must** refresh, but the API still provides a mechanically usable stale snapshot. This repeats the earlier “documentation says call the second guard” failure class: compliant behavior is requested, not enforced.

Required repair: preflight may validate once but must discard that result. The returned context may retain only paths/hash identities. The only consumer-facing snapshot/denominator access must rerun the full pinned chain immediately before use.

No real measurement, Task4F1 access, retrieval, HMAC, seal, finalize or run occurred.
