"""NARROW DATA-IDENTITY TASK A - verify the LoCoMo question -> conversation mapping against the raw source.

AUTHORIZED SCOPE, AND THE LIMITS OBSERVED HERE
----------------------------------------------
Permitted: read the locally pinned `locomo10.json`, process ONLY the fields needed to establish the
question-identity / conversation relationship, and compare against the previously derived mapping.

NOT permitted and NOT done: representation learning, fitting, retrieval, ranking, evaluation,
real-data bootstrap, pilot. Nothing here imports or calls any producer adapter or shard module -
calling the producer's own mapping function would not be an independent derivation, so this file
re-derives the relationship from the raw structure alone. **No question text, answer text or dialogue
text is ever printed, logged or written out.** Only integer indices, counts, categories and set sizes
leave this script. Nothing from the raw source is uploaded.

THE IDENTITY RULE, WRITTEN OUT BECAUSE IT IS POSITIONAL
-------------------------------------------------------
The producer's question id has the form `locomo_<c>_qa<n>`, and both components are POSITIONS, not
stored keys:

  c  = 0-based index of the conversation in the TOP-LEVEL JSON LIST of `locomo10.json`.
       It is NOT the conversation's own `sample_id`. Index 0 is `sample_id` "conv-26", index 9 is
       "conv-50". Reordering the top-level list would silently change every id's meaning.
  n  = 0-based index of the question in THAT conversation's RAW `qa` list - the full list, before any
       cohort filtering. This script proves it is the raw list and not a filtered one, rather than
       assuming it: in conversations 0, 1, 6 and 9 the cohort's index set is NOT contiguous and its
       maximum exceeds the cohort size, which is impossible if `n` indexed a filtered list.

Usage: python verify_locomo_mapping.py <path-to-locomo10.json> <path-to-mapping.json> [json-out]
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
from pathlib import Path

SOURCE_SHA256 = "79fa87e90f04081343b8c8debecb80a9a6842b76a7aa537dc9fdf651ea698ff4"
SOURCE_BYTES = 2805274
QID = re.compile(r"^locomo_(\d+)_qa(\d+)$")

src_path = Path(sys.argv[1])
map_path = Path(sys.argv[2])
out_path = Path(sys.argv[3]) if len(sys.argv) > 3 else None

# --- identity of the source, before anything is read out of it --------------------------------
h = hashlib.sha256()
with src_path.open("rb") as f:
    for block in iter(lambda: f.read(8 << 20), b""):
        h.update(block)
digest, size = h.hexdigest(), src_path.stat().st_size
print(f"source: {src_path.name}  {size} bytes  sha256 {digest}")
if digest != SOURCE_SHA256 or size != SOURCE_BYTES:
    raise SystemExit(f"ABORT: source identity mismatch; expected {SOURCE_SHA256} / {SOURCE_BYTES} bytes")
print("source identity: VERIFIED against the pinned hash\n")

raw = json.loads(src_path.read_text(encoding="utf-8"))
mapping = json.loads(map_path.read_text(encoding="utf-8"))["expected_question_to_cluster"]

# --- the cohort, as index sets ----------------------------------------------------------------
cohort = collections.defaultdict(set)
for qid, cluster in mapping.items():
    m = QID.fullmatch(qid)
    if not m:
        raise SystemExit(f"ABORT: question id {qid!r} does not match the positional scheme")
    c, n = int(m.group(1)), int(m.group(2))
    if cluster != f"locomo_conv_{c}":
        raise SystemExit(f"ABORT: {qid!r} is assigned to {cluster!r}, which its own id contradicts")
    cohort[c].add(n)

# --- structural facts of the raw source (metadata only, never content) -------------------------
n_conv = len(raw)
qa_len = [len(e["qa"]) for e in raw]
sample_ids = [e["sample_id"] for e in raw]
cat5 = [{i for i, q in enumerate(e["qa"]) if q.get("category") == 5} for e in raw]
no_evidence = [{i for i, q in enumerate(e["qa"]) if not (q.get("evidence") or [])} for e in raw]

print(f"raw source: {n_conv} conversations, qa list lengths {qa_len}, total {sum(qa_len)}")
print(f"cohort    : {len(cohort)} conversations, {sum(len(v) for v in cohort.values())} questions\n")

checks, failed = [], []


def check(label, cond, detail=""):
    checks.append({"check": label, "pass": bool(cond), "detail": str(detail)})
    print(("ok    " if cond else "FAIL  ") + f"{label}   {detail}"[:150])
    if not cond:
        failed.append(label)


check("the raw source has exactly as many conversations as the mapping has clusters",
      n_conv == len(cohort), f"{n_conv} vs {len(cohort)}")
check("every conversation index in the mapping exists in the raw source",
      all(0 <= c < n_conv for c in cohort))
check("every question index resolves to a real question of the conversation its id names",
      all(all(n < qa_len[c] for n in s) for c, s in cohort.items()),
      "0 out-of-range indices")

non_contiguous = [c for c, s in cohort.items() if s != set(range(len(s)))]
check("the index is into the RAW qa list, not a filtered one (proved, not assumed)",
      bool(non_contiguous),
      f"conversations {sorted(non_contiguous)} have non-contiguous index sets whose maximum exceeds "
      f"the cohort size, which a filtered index could not produce")

check("no cohort question sits on a category-5 position",
      all(not (cohort[c] & cat5[c]) for c in cohort),
      f"{sum(len(cat5[c]) for c in range(n_conv))} category-5 questions in the source, none selected")

# --- the reconstructed selection rule, and its residual ---------------------------------------
predicted = [{i for i in range(qa_len[c]) if i not in cat5[c] and i not in no_evidence[c]}
             for c in range(n_conv)]
residual = {c: sorted(cohort[c] ^ predicted[c]) for c in range(n_conv) if cohort[c] ^ predicted[c]}
n_residual = sum(len(v) for v in residual.values())
check("the rule 'category != 5 AND evidence non-empty' reproduces the cohort",
      n_residual <= 1,
      f"{n_conv - len(residual)} of {n_conv} conversations reproduced exactly; "
      f"{n_residual} unexplained position(s): {residual}")

# --- is the assignment forced by the raw source, or merely consistent with it? -----------------
# For each cohort conversation i and each raw conversation j, ask whether i's index set could have
# come from j at all. Then count perfect matchings. One matching means the raw source DETERMINES the
# assignment; more than one means it only constrains it.
def compatible(i, j, strict):
    if max(cohort[i]) >= qa_len[j] or (cohort[i] & cat5[j]):
        return False
    return len(cohort[i] ^ predicted[j]) <= 1 if strict else True


def count_matchings(strict, cap=4):
    found = []

    def walk(i, used, acc):
        if len(found) >= cap:
            return
        if i == n_conv:
            found.append(acc)
            return
        for j in range(n_conv):
            if j not in used and compatible(i, j, strict):
                walk(i + 1, used | {j}, acc + (j,))

    walk(0, frozenset(), ())
    return found


loose = count_matchings(strict=False)
strict = count_matchings(strict=True)
identity = tuple(range(n_conv))
check("range and category-5 structure alone already narrow the assignment",
      len(loose) < 4, f"{len(loose)} candidate assignments found (search capped at 4)")
check("with the reconstructed selection rule the assignment is UNIQUELY DETERMINED",
      len(strict) == 1 and strict[0] == identity,
      f"{len(strict)} perfect matching(s); it is the identity permutation" if strict else "none")

per_conv = {f"locomo_conv_{c}": len(cohort[c]) for c in range(n_conv)}
print(f"\nper-conversation cohort sizes: {per_conv}")
print(f"top-level index -> sample_id : {dict(enumerate(sample_ids))}")

print()
if failed:
    print(f"{len(failed)} FAILING CHECK(S): {failed}")
verdict = "MAPPING CONFIRMED AGAINST THE RAW SOURCE" if not failed else "MAPPING NOT CONFIRMED"
print(verdict)
print("Scope: question-identity and conversation membership only. No representation, fitting, "
      "retrieval, ranking, evaluation or bootstrap was performed, and no source text was emitted.")

if out_path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "task": "narrow data-identity task A - LoCoMo",
        "verdict": verdict,
        "source": {"file": src_path.name, "bytes": size, "sha256": digest, "identity": "VERIFIED"},
        "mapping_file": str(map_path.name),
        "identity_rule": {
            "form": "locomo_<c>_qa<n>",
            "c": "0-based index in the TOP-LEVEL JSON LIST of locomo10.json, NOT the sample_id",
            "n": "0-based index in that conversation's RAW qa list, before cohort filtering",
            "proved_raw_not_filtered_by": f"non-contiguous index sets in conversations {sorted(non_contiguous)}",
            "index_to_sample_id": dict(enumerate(sample_ids))},
        "reconstructed_selection_rule": "category != 5 AND evidence non-empty",
        "selection_rule_residual": residual,
        "assignment_uniqueness": {
            "candidates_under_range_and_category_structure": len(loose),
            "candidates_under_the_selection_rule": len(strict),
            "is_identity_permutation": bool(strict and strict[0] == identity)},
        "per_conversation_cohort_sizes": per_conv,
        "raw_qa_lengths": qa_len,
        "checks": checks,
        "not_performed": ["representation learning", "fitting", "retrieval", "ranking",
                          "evaluation", "real-data bootstrap", "pilot", "producer adapter import"],
        "content_emitted": "none - integer indices, counts and categories only",
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"\nwrote {out_path}")

raise SystemExit(1 if failed else 0)
