[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# DELIVER 3 — Sidecar and anchor recheck (PREPARED, NOT ACCEPTED)

Method (VERIFIED — ran it myself this session): SHA256 recomputed over RAW GIT
BLOBS (`git cat-file blob HEAD:<path>`), never checked-out files, per the CRLF
trap documented at VERIFIED `docs/v52/V52_CLAUDE_TO_CODEX_HANDOVER_2026-09-07.md:142-155`
("hash raw Git blobs … never checked-out files"; repo ships no `.gitattributes`,
so a default Windows `core.autocrlf=true` checkout corrupts hashes). Receipts:
`sidecar_recheck_receipt.txt`, `anchor_recheck_receipt.txt`,
`geometry_manifest_receipt.txt` in this namespace.

## Totals

| Check | Scope | Result (VERIFIED) |
|---|---|---|
| `*.sha256` sidecars on HEAD | 20 sidecars, 0 missing subjects | 20/20 OK, 0 mismatch |
| `ops/CURRENT_STATE.json` `anchors[]` path+digest | 32 anchors | 32/32 OK, 0 mismatch |
| Geometry MANIFEST (manifest, not sidecar) | 73 listed path+hash lines on `origin/findings/representation-geometry-2026-09-13` | 73/73 OK, 0 mismatch |

Mismatches: none. Missing subjects: none.

## Notes

- The 20 sidecars cover `docs/v52/*.md` (13), preregistration seals V1/V2/V3
  (3), and four `prompts/*` files (VERIFIED `git ls-tree -r --name-only HEAD |
  grep '\.sha256$'`). None of the stale-pointer documents (README, START_HERE,
  MANIFEST, CURRENT_STATE, CONTINUITY_PROTOCOL, status snapshots) carries a
  sidecar — so Deliver 2's direct-amendment proposals do not collide with the
  additive-only rule.
- `research_representation_geometry_2026_09_13/MANIFEST.sha256` exists ONLY on
  branch `origin/findings/representation-geometry-2026-09-13` (VERIFIED absent
  from HEAD tree; present on that branch). Per the task instruction it was NOT
  treated as a sidecar with a missing subject — it was verified as a manifest:
  every listed `path+hash` recomputed from that branch's blobs, 73/73 match.
  Its scope is that branch's research namespace, not main's chain of custody.
- Correction package therefore rests on a checked base: frozen artifacts
  byte-exact, anchors resolving, no chain-of-custody defect found. This
  re-verification covers hash integrity only; it does not audit, seal, or
  authorize anything.
