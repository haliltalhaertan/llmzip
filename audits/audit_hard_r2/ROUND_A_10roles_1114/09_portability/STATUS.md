# STATUS 09_portability — clean-room portability audit — COMPLETE

Role: 09_portability. READ-ONLY sources; outputs only in this dir. No commits/push/repair.
Python: ~/muse-work/ml-python, PYTHONDONTWRITEBYTECODE=1, single-thread BLAS.
Lock note: `bash compute.sh` unusable (compute.lock parent read-only, verified); all probes ran
direct with equivalent bounds (single-thread env, each <<180 s; observed 3.5-3.6 s).

## Phase checklist
- [x] P0 init: read REFS_BEFORE.txt, ROUND_PLAN.json, prompt.txt; created STATUS.md
- [x] P1 inventory: package/coordinator/data layouts, FILE_MANIFEST 756 entries, no SETUP docs
- [x] P2 contracts: prior repro HARD_AUDIT_REPRO.md re-tested as clean-room (not asserted)
- [x] P3 clean-room T1: package-only copies (sha-verified, 0 symlinks); 3-line path-only patch
      (outputs/T1_path_patch.diff); 35/35 cells bit-identical (outputs/T1_cleanroom_compare.json)
- [x] P4 T2/T3 blockers: real FileNotFoundError traces; ambient sizes recorded, not claimed missing
      (outputs/T2_T3_blockers.json; INPUT_INVENTORY.csv 13 rows)
- [x] P5 manifest vs contents vs Git blobs + ZIP scope: sets 756/800/800; 12-file sample 12/12
      Git==workdir; 1/5 gzip round-trip True; 70 decision-layer files outside manifest coverage;
      no top-10 ZIP (outputs/manifest_verify.json; outputs/git_minus_manifest_full.txt)
- [x] P6 deliverables: REPORT.md, COVERAGE.csv (15 rows), SETUP_GAPS.md, INPUT_INVENTORY.csv,
      evidence/evidence_index.json (19 files sha256); original FILE_MANIFEST.json sha unchanged
      (92286bb6… before == after)
