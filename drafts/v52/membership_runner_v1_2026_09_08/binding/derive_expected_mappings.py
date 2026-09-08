"""Derive the PROPOSED expected-mapping manifests from committed records. Replayable.

READ-ONLY, AND NO RAW CORPUS. Every input is a committed Git blob, read with `git cat-file blob` and
hash-checked before use. No dataset file is opened, no retrieval is run, and nothing here is bound to
the experiment: the outputs are PROPOSALS and carry `binding_status: "PROPOSED"`.

PROVENANCE LABEL - the distinction the Head Researcher asked to be kept explicit:

  INHERITED FROM PRODUCER METADATA. The LoCoMo question -> conversation mapping is read off the
  producer's own question-id scheme `locomo_<conversation_index>_qa<n>` as it appears in committed
  per-question output records. It is NOT independently derived from `locomo10.json`. If the producer
  assigned a question to the wrong conversation at generation time, this mapping inherits that error
  and cannot detect it. An independent derivation would have to parse the corpus, which is a separate
  narrowly scoped task and is not authorized here.

  The two LoCoMo records used are independent of each other in the sense that matters for a
  transcription error - one is the original research output, the other an independent bit-exact
  reproduction by a different agent - and they are cross-checked here. They are NOT independent of the
  producer's labelling, because both descend from it.

Usage: python derive_expected_mappings.py <path-to-repo> [out_dir]
"""
from __future__ import annotations

import collections
import csv
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path(__file__).resolve().parent

REPRO_BRANCH_COMMIT = "692f599eedeb7e7a649443f24ff507e8c4d1c17d"      # codex/v52-locomo-reproduction-audit-2026-09-07
MAIN_ANY = "origin/main"

# Every input, with the sha256 of its RAW GIT BLOB. A mismatch aborts.
INPUTS = {
    "locomo_original": (
        REPRO_BRANCH_COMMIT, "research/v52/locomo_scale_outputs/locomo_scale_per_question.csv.gz",
        "b7abd942c13cf9ce1b1c4a13e3ff39fb26a26e8b2f2749dd92d76f0b2a474602"),
    "locomo_reproduced": (
        REPRO_BRANCH_COMMIT,
        "audit_v52_locomo_reproduction_2026_09_07/reproduced_outputs/locomo_scale_per_question.csv.gz",
        "efed0c46cd0f34e45daa5fcdf5d08fc51a61ffaafd6ca1d522c6c4c98fc7834f"),
    "locomo_source_identity": (
        REPRO_BRANCH_COMMIT, "audit_v52_locomo_reproduction_2026_09_07/actual_source_identity.json",
        "ecb8384624aee0cc3cc11830e547c2f8f02a7a0f43a0f2894e3d9bec0226a28f"),
    "longmemeval_scale": (
        REPRO_BRANCH_COMMIT, "research/v52/longmemeval_scale_outputs/longmemeval_scale_per_question.csv.gz",
        "1db682a277b8fe7f0b3aa7cf02831bf07f0d5c4c340796a57c93df5441df3157"),
    "longmemeval_t4c2": (
        MAIN_ANY, "docs/v52/task4c2/V52_T4C2_question_level.csv",
        "69c21b2ffaea1e92923bf3f0e83287e12d07a5f34b4b42afde1752d6b50b3b51"),
}

LOCOMO_ID = re.compile(r"^locomo_(\d+)_qa(\d+)$")


def blob(name: str) -> bytes:
    commit, path, expect = INPUTS[name]
    raw = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", f"{commit}:{path}"],
                         capture_output=True, check=True).stdout
    got = hashlib.sha256(raw).hexdigest()
    if got != expect:
        raise SystemExit(f"ABORT: {name} blob hash mismatch\n  expected {expect}\n  got      {got}")
    print(f"  verified  {name:22s} {expect[:16]}…  {path}")
    return raw


def rows(raw: bytes, gz: bool):
    text = gzip.decompress(raw) if gz else raw
    return list(csv.DictReader(io.StringIO(text.decode("utf-8"))))


print("Reading committed blobs (no corpus is opened):")
loc_a = rows(blob("locomo_original"), gz=True)
loc_b = rows(blob("locomo_reproduced"), gz=True)
src = json.loads(blob("locomo_source_identity").decode("utf-8"))
lme_a = rows(blob("longmemeval_scale"), gz=True)
lme_b = rows(blob("longmemeval_t4c2"), gz=False)

# ---------------------------------------------------------------------------------------------
# LoCoMo - the mapping, and the checks that it is what it claims to be
# ---------------------------------------------------------------------------------------------
def locomo_map(recs, label):
    out = {}
    for r in recs:
        if r["dataset"] != "LoCoMo":
            raise SystemExit(f"ABORT: {label} carries dataset {r['dataset']!r}, expected LoCoMo only")
        m = LOCOMO_ID.fullmatch(r["question_id"])
        if not m:
            raise SystemExit(f"ABORT: {label} question id {r['question_id']!r} does not match the "
                             f"producer scheme locomo_<conversation>_qa<n>; the mapping cannot be "
                             f"inherited and must not be guessed")
        out[r["question_id"]] = f"locomo_conv_{int(m.group(1))}"
    return out


map_a, map_b = locomo_map(loc_a, "original"), locomo_map(loc_b, "reproduced")
if map_a != map_b:
    raise SystemExit("ABORT: the original and reproduced LoCoMo records disagree about the mapping")
print(f"\nLoCoMo: two independent records agree exactly — {len(map_a)} questions")

per_conv = collections.Counter(map_a.values())
conv_ids = sorted(per_conv, key=lambda s: int(s.rsplit("_", 1)[1]))
src_convs = sorted(f["file"] for f in src["files"] if re.fullmatch(r"audit/conv_\d+\.json", f["file"]))
if len(src_convs) != len(conv_ids):
    raise SystemExit(f"ABORT: the source-identity record lists {len(src_convs)} conversation files but "
                     f"the id scheme yields {len(conv_ids)} conversations")
print(f"  conversations from the id scheme : {len(conv_ids)}")
print(f"  conversation files in the source : {len(src_convs)}  (independent cross-check, agrees)")
print(f"  per-conversation counts          : {dict((c, per_conv[c]) for c in conv_ids)}")
print(f"  total                            : {sum(per_conv.values())}")

corpus = next(f for f in src["files"] if f["file"] == "locomo10.json")

locomo_manifest = {
    "source_id": "LoCoMo locomo10.json (V52 pinned corpus)",
    "source_sha256": corpus["sha256"],
    "benchmark": "LoCoMo",
    "expected_cluster_ids": conv_ids,
    "expected_question_to_cluster": map_a,
    "n_questions": len(map_a),
}

# ---------------------------------------------------------------------------------------------
# LongMemEval - cohort only. R2 line 141 defines no conversation-cluster bootstrap for it.
# ---------------------------------------------------------------------------------------------
ids_a = {r["question_id"] for r in lme_a if r["dataset"] == "LongMemEval"}
ids_b = {r["question_id"] for r in lme_b}
if ids_a != ids_b:
    raise SystemExit("ABORT: the two LongMemEval cohort records disagree")
print(f"\nLongMemEval: two independent records agree exactly — {len(ids_a)} questions")
print("  no conversation id is present in either record, and none is invented:")
print("  R2 line 141 defines NO conversation-cluster bootstrap for LongMemEval, so no")
print("  question -> conversation map is required. The single connected component inherited")
print("  from Task 3A.1 is recorded as ONE sentinel cluster, which the runner refuses to resample.")

SENTINEL = "longmemeval_single_connected_component_inherited_task3a1"
lme_manifest = {
    "source_id": "LongMemEval V52 pinned cohort (single dependency component, inherited from Task 3A.1)",
    "source_sha256": "UNRESOLVED-see-BINDING_PROPOSAL-section-1",
    "benchmark": "LongMemEval",
    "expected_cluster_ids": [SENTINEL],
    "expected_question_to_cluster": {q: SENTINEL for q in sorted(ids_a)},
    "n_questions": len(ids_a),
}

# ---------------------------------------------------------------------------------------------
for name, manifest, provenance in (
        ("PROPOSED_mapping_locomo.json", locomo_manifest,
         "INHERITED FROM PRODUCER METADATA - read off the question-id scheme locomo_<conv>_qa<n> in two "
         "committed per-question records that agree exactly. NOT independently derived from locomo10.json."),
        ("PROPOSED_mapping_longmemeval.json", lme_manifest,
         "COHORT INHERITED FROM PRODUCER METADATA - the 470 question ids, agreeing exactly across two "
         "committed records. NO conversation structure is claimed or invented; the single sentinel cluster "
         "records the single connected component inherited from Task 3A.1 and is never resampled.")):
    payload = dict(manifest)
    path = OUT / name
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
    side = OUT / (name + ".provenance.json")
    side.write_text(json.dumps({
        "binding_status": "PROPOSED - NOT BOUND; requires Head Researcher approval",
        "provenance": provenance,
        "raw_corpus_read": False,
        "derived_by": "binding/derive_expected_mappings.py",
        "inputs": {k: {"commit": v[0], "path": v[1], "blob_sha256": v[2]} for k, v in INPUTS.items()},
        "manifest_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {name}  sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")

print("\nBoth manifests are PROPOSALS. Nothing here binds them to the experiment.")
