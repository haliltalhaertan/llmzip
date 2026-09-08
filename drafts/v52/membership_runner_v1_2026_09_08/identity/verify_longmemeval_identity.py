"""NARROW DATA-IDENTITY TASK B - resolve and verify the LongMemEval source identity.

AUTHORIZED SCOPE. Resolve what `dataset_sha256` covers, verify the file's identity if it is present,
and check the accepted 470-question cohort against it using ID FIELDS ONLY.

NOT permitted and NOT done: representation learning, fitting, retrieval, ranking, evaluation,
real-data bootstrap, pilot, and any download. No adapter is imported. **No question, answer or
session content is printed, logged or written out** - only question ids, counts and set sizes. Nothing
from the raw source is uploaded.

WHAT THE HASH COVERS - the chain, resolved from committed source rather than assumed
-------------------------------------------------------------------------------------
  `docs/v52/task4c2/v52_t4c2_centering_geometry.py` line 127 computes
      'dataset_sha256': sha256_file(args.dataset)
  and `sha256_file` (line 57) streams the file in 8 MiB blocks and hashes those bytes. So the value
  is the **sha256 of the RAW FILE BYTES**, not of any parsed, normalised or transformed form.

  Line 23 pins `EXPECTED_DATASET_SHA = d6f21ea9...` and line 24 `EXPECTED_DATASET_BYTES = 277383467`.
  `tools/verify_frozen_artifacts.py` binds that same hash to the path
  `data/longmemeval_s_cleaned.json` under `DATASET_EXTERNAL`, and `README.md` names the file, its
  size and its cohort. `adapters/longmemeval_v52_adapter.py` records the acquisition URL.

Usage: python verify_longmemeval_identity.py <path-to-longmemeval_s_cleaned.json> <mapping.json> [json-out]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

DATASET_SHA256 = "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442"
DATASET_BYTES = 277383467
DATASET_FILENAME = "longmemeval_s_cleaned.json"
ACQUISITION_URL = ("https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/"
                   "resolve/main/longmemeval_s_cleaned.json")

src_path = Path(sys.argv[1])
map_path = Path(sys.argv[2])
out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

checks, failed = [], []


def check(label, cond, detail=""):
    checks.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print(("ok    " if cond else "FAIL  ") + f"{label}   {detail}"[:150])
    if not cond:
        failed.append(label)


print("what dataset_sha256 covers, resolved from committed source:")
print("  v52_t4c2_centering_geometry.py:127  'dataset_sha256': sha256_file(args.dataset)")
print("  v52_t4c2_centering_geometry.py:57   sha256_file streams RAW FILE BYTES in 8 MiB blocks")
print("  -> RAW FILE, not transformed data")
print(f"  bound path  : data/{DATASET_FILENAME}  (tools/verify_frozen_artifacts.py, DATASET_EXTERNAL)")
print(f"  bound size  : {DATASET_BYTES} bytes    (EXPECTED_DATASET_BYTES, line 24)")
print(f"  acquisition : {ACQUISITION_URL}\n")

if not src_path.exists():
    print(f"FILE NOT PRESENT at {src_path}")
    print("Reporting the missing file and its verified acquisition path. NOT downloading, and NOT "
          "filling the placeholder by guess.")
    raise SystemExit(2)

h = hashlib.sha256()
with src_path.open("rb") as f:
    for block in iter(lambda: f.read(8 << 20), b""):
        h.update(block)
digest, size = h.hexdigest(), src_path.stat().st_size
print(f"local file: {src_path.name}  {size} bytes  sha256 {digest}")

check("the local file's size matches the bound size", size == DATASET_BYTES, f"{size}")
check("the local file's RAW-BYTE sha256 matches the bound dataset_sha256", digest == DATASET_SHA256)
check("the file name matches the bound path's basename", src_path.name == DATASET_FILENAME, src_path.name)

if failed:
    print("\nidentity NOT verified; not proceeding to the cohort check")
    raise SystemExit(1)

raw = json.loads(src_path.read_text(encoding="utf-8"))
ids = [str(item["question_id"]) for item in raw]
non_abs = {q for q in ids if not q.endswith("_abs")}
cohort = set(json.loads(map_path.read_text(encoding="utf-8"))["expected_question_to_cluster"])

check("every question id in the file is unique", len(set(ids)) == len(ids), f"{len(ids)} items")
check("the accepted cohort is exactly the non-'_abs' question ids",
      non_abs == cohort, f"{len(non_abs)} non-_abs vs {len(cohort)} in the cohort")
check("no cohort question id is absent from the dataset", not (cohort - set(ids)))
check("no non-'_abs' question id is missing from the cohort", not (non_abs - cohort))

print()
verdict = "SOURCE IDENTITY RESOLVED AND VERIFIED" if not failed else "SOURCE IDENTITY NOT VERIFIED"
print(verdict)
print("Scope: file identity and question-id cohort only. No representation, fitting, retrieval, "
      "ranking, evaluation or bootstrap was performed, no download occurred, and no source text was "
      "emitted. NOTE: this file supplies NO conversation grouping, and none is inferred - R2 line 141 "
      "defines no conversation-cluster bootstrap for LongMemEval.")

if out_path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "task": "narrow data-identity task B - LongMemEval",
        "verdict": verdict,
        "what_the_hash_covers": {
            "answer": "the RAW FILE BYTES",
            "evidence": ["v52_t4c2_centering_geometry.py:127 'dataset_sha256': sha256_file(args.dataset)",
                         "v52_t4c2_centering_geometry.py:57 sha256_file streams the file in 8 MiB blocks",
                         "v52_t4c2_centering_geometry.py:23-24 EXPECTED_DATASET_SHA and EXPECTED_DATASET_BYTES",
                         "tools/verify_frozen_artifacts.py DATASET_EXTERNAL binds it to data/longmemeval_s_cleaned.json",
                         "README.md names the file, hash, byte size and the 470 non-_abs cohort"],
            "not_transformed_data": True},
        "source": {"file": src_path.name, "bytes": size, "sha256": digest, "identity": "VERIFIED",
                   "acquisition_url": ACQUISITION_URL},
        "cohort": {"items_in_file": len(ids), "non_abs": len(non_abs), "accepted_cohort": len(cohort),
                   "exact_match": non_abs == cohort},
        "conversation_grouping": ("NOT present in the source and NOT inferred; R2 line 141 defines no "
                                  "conversation-cluster bootstrap for LongMemEval"),
        "checks": checks,
        "not_performed": ["download", "representation learning", "fitting", "retrieval", "ranking",
                          "evaluation", "real-data bootstrap", "pilot", "adapter import"],
        "content_emitted": "none - question ids, counts and set sizes only",
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out_path}")

raise SystemExit(1 if failed else 0)
