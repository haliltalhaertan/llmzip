# V52 static-storage inventory — independent audit disposition

Status: **FIX PREPARED / NOT INDEPENDENTLY RE-REVIEWED / NOT_READY / NO MEASUREMENT AUTHORIZATION**

Independent audit:
- branch: `audit/v52-static-storage-inventory-independent-2026-09-12`
- commit: `22b58b609f766c028a344813eacec4abab0a7804`
- verdict: `REQUEST_CHANGES`
- package: `audit_v52_static_storage_inventory_2026_09_12/`
- `HASHES.json` SHA256 (sidecar): `a1ae82bb7114409aaf9fc58bb234f2ac93fa5934bbdfce47c86a57d07bf3579a`

Audit target:
- parent branch: `codex/v52-static-storage-contract-2026-09-12`
- target commit: `f9404f2b1e56e5a63878978c19f30283b18324fd`
- live canonical main observed before repair: `5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`

## Finding disposition

- `INV-AUD-001` P2 — **ACCEPTED_AND_CORRECTED**. LoCoMo representation proof is now recorded as manifest-bound:
  - proof Drive id `11cKt4hDPBazhrOSZxSgcT5Dw-w5kdpNi`
  - proof SHA256 `957e9e022f6f42ebf3e4f68eaa69cf1ec1f48367100a959a0ba9623caf5e1ddd`
  - post-run manifest Drive id `1Lk5ZLaceKuc3OF-v0X52OfItU0PqVlmp`
  - post-run manifest SHA256 `a97e411c1ed24c5c93590638fcb51248936d8428a38e4d76cf0c6b74a9399b9c`
  - upload receipt Drive id `1BJgsMU37aw5yFnZ2g76kuNYMJkfR6HIP`
  - locally re-read manifest bytes matched `a97e...`, and its atomic output map binds the proof to `957e...`.
- `INV-AUD-002` P2 — **ACCEPTED_AND_CORRECTED**. Per-item `deterministic_regeneration_status` and evidence/blocker fields added in V2 inventory.
- `INV-AUD-003` P2 — **ACCEPTED_AND_CORRECTED**. T4C2 nested NPZ diagnostic bundle explicitly catalogued as `FOUND_BUT_EXCLUDED_DIAGNOSTIC_ARTIFACT`.
- `INV-AUD-004` P2 — **ACCEPTED_AND_CORRECTED**. Five-way ID/offset mapping taxonomy added; persistent mapping bytes remain `UNKNOWN`.
- `INV-AUD-005` P3 — **ACCEPTED_AND_CORRECTED**. Separate expanded `SEARCH_LOG_V2.json` added with terms, namespaces, container hits and exclusion reasons.

## Epistemic boundary

These repairs only improve source inventory accuracy and auditability. They do **not** establish:
- fitted model bytes are present,
- physical copy counts,
- true sharing denominators,
- marginal/effective storage values,
- <=12 compliance,
- retrieval readiness or quality,
- scientific approval,
- seal/run authorization.

A fresh independent source-resolution review is required before advancing to a real adapter/measurement plan.

Task4F1 remains **SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN**.
