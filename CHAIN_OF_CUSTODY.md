# Chain of Custody — repository rules

These rules exist because a real packaging defect occurred: `V52_T4C2_PRE_RUN_SEAL.json` was once committed as a semantically identical but re-serialized JSON copy. Its SHA256 changed even though the scientific content did not. Under a zero-trust protocol that is indistinguishable from tampering until the canonical bytes are checked.

## The rules

1. **`main` is canonical.** Only research state accepted by the Head Researcher belongs on `main`.
2. **`audit/...` branches are for independent auditors.** Auditor output reaches `main` only after explicit acceptance.
3. **Frozen artifacts are byte-exact. Reformatting is forbidden.** Seals, manifests, preregistrations, method specs and sealed compute scripts must be carried byte-for-byte. Never pretty-print, re-serialize, normalize line endings, strip trailing newlines, or round-trip them through JSON/YAML tooling.
4. **Every frozen file has a published SHA256.** The verifier checks committed artifacts and explicit cross-file bindings.
5. **Large raw data stays in Drive**, reachable from Git by SHA256 + Drive pointer. See `DATASETS_AND_LARGE_ARTIFACTS.md`.
6. **Adapters and sealed scripts belong in Git when practical**, byte-exact. The LongMemEval v1/v2 adapters are now present in Git and match their pinned SHA256 values.
7. **Every audit prompt begins with byte-level verification** before result interpretation.

## Required first instruction in every audit prompt

> Before interpreting any result, verify every committed frozen artifact byte-for-byte against the corresponding manifest SHA256. Treat any mismatch as a packaging / chain-of-custody defect until the canonical Drive copy is independently checked.

## How to verify

```bash
python3 tools/verify_frozen_artifacts.py
python3 tools/verify_frozen_artifacts.py --list
```

The verifier checks both per-file hashes and cross-manifest bindings. For Drive-only Task 4C3 anchors, it records the frozen expected hashes and reports them as external until exact bytes are committed.

## Frozen LongMemEval adapters — CLOSED GAP

Both adapters are now committed under `adapters/` and are checked by the verifier:

- `adapters/longmemeval_v52_adapter.py`
  - SHA256 `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
- `adapters/longmemeval_v52_adapter_v2.py`
  - SHA256 `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`

The independent Task 4C2 audit subsequently verified archive-only fitting and the ITQ Procrustes orientation. That former NOT-VERIFIABLE condition is closed.

## Task 4C3 accepted chain — 2026-08-28

The independent cold-start audit was accepted into `main` via PR #1 with verdict `PASS WITH CONDITIONS`.

Canonical compute commit: `7959c1df46b09f48bdbd1d1922bf62715e119839`

Task 4C3 Drive folder:
`https://drive.google.com/drive/folders/1ABFEBsp7KfNxtIRkdaqU-6ImTFbsXAnv`

Frozen anchors:

- `V52_T4C3_PRE_RUN_SEAL.json`
  - SHA256 `c7cf7aa028a80464561dcc020e54a50c029935382463110bd1df0b8ae50f4a97`
- `v52_t4c3_coordinate_axis_probe.py`
  - SHA256 `8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996`
- `V52_T4C3_POST_RUN_MANIFEST.json`
  - SHA256 `7bfeae589ffdf86012c04eec02017918cae92c3fa20a699c8d342f4baa39c00c`

The independent audit re-hashed all 26 manifest-declared Task 4C3 outputs contained in the canonical output archive: **26/26 matched, 0 mismatches**. The dataset itself was not independently re-downloaded and re-hashed in that audit environment; this remains a provenance condition, not an observed mismatch.

## Repairing a mismatch

Never repair by regenerating, reformatting or re-exporting a frozen file. Fetch the canonical byte source, confirm its hash independently, restore those exact bytes, and record the incident.
