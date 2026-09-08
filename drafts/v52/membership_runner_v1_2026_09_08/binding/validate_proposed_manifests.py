"""Check the PROPOSED manifests against the runner's own contract. Synthetic, read-only.

WHAT THIS PROVES AND WHAT IT DOES NOT. It proves the manifests load under the declared schema, are
internally consistent, satisfy every identifier rule, and behave correctly through the runner's
benchmark and scheme gates. It does NOT prove the cohort matches the corpus: feeding a manifest its
own id columns is consistent by construction. The evidence that the cohort is right is the
cross-record agreement in `derive_expected_mappings.py`, not this file.

Usage: python validate_proposed_manifests.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent.parent / "membership_impl_v3_2026_09_07"))

import membership_runner as R                                                    # noqa: E402

FAIL = []


def _raises(fn) -> bool:
    try:
        fn()
    except R.DesignViolation:
        return True
    return False


def check(label, cond, detail=""):
    print(("ok    " if cond else "FAIL  ") + f"{label}   {detail}"[:140])
    if not cond:
        FAIL.append(label)


for name, benchmark, n_q, n_c in (("PROPOSED_mapping_locomo.json", R.LOCOMO, 1535, 10),
                                  ("PROPOSED_mapping_longmemeval.json", R.LONGMEMEVAL, 470, 1)):
    path = HERE / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"\n=== {name}  sha256 {digest}")
    m = R.load_expected_mapping(path, digest)
    check("loads under the declared schema against its own hash", m["benchmark"] == benchmark)
    check(f"declares {n_q} questions", m["n_questions"] == n_q, str(m["n_questions"]))
    check(f"declares {n_c} cluster id(s)", len(m["expected_cluster_ids"]) == n_c,
          str(len(m["expected_cluster_ids"])))

    qids = list(m["expected_question_to_cluster"])
    cids = [m["expected_question_to_cluster"][q] for q in qids]
    ident = R.verify_source_identity(qids, cids, m)
    check("passes the identity contract (schema and internal consistency only)",
          ident["question_to_cluster_matches"] and ident["cluster_id_set_matches"])
    check("every identifier survives the NEW-4 / NEW-5 rules unmodified",
          R.validate_identifier_columns(qids, cids) == (qids, cids))

    # A corruption that leaves the cluster count unchanged must still be caught.
    if n_c > 1:
        swapped = list(cids)
        i = next(k for k, c in enumerate(cids) if c == m["expected_cluster_ids"][0])
        j = next(k for k, c in enumerate(cids) if c == m["expected_cluster_ids"][1])
        swapped[i], swapped[j] = swapped[j], swapped[i]
        check("the count-preserving swap corruption is still caught on the REAL cohort",
              len(set(swapped)) == n_c and _raises(lambda: R.verify_source_identity(qids, swapped, m)))

    sidecar = json.loads((HERE / (name + ".provenance.json")).read_text(encoding="utf-8"))
    check("the provenance sidecar marks it PROPOSED, not bound",
          sidecar["binding_status"].startswith("PROPOSED"))
    check("the provenance sidecar records that no raw corpus was read",
          sidecar["raw_corpus_read"] is False)
    check("the provenance sidecar's recorded manifest hash matches the file",
          sidecar["manifest_sha256"] == digest)


print("\n=== gate behaviour on the proposed LongMemEval manifest")
lme = HERE / "PROPOSED_mapping_longmemeval.json"
m = R.load_expected_mapping(lme, hashlib.sha256(lme.read_bytes()).hexdigest())
qids = list(m["expected_question_to_cluster"])
cids = [m["expected_question_to_cluster"][q] for q in qids]
check("a LongMemEval CLUSTER bootstrap is refused before any seed is read",
      _raises(lambda: R.compute_results([], qids, cids, m, HERE / "no-such-seed.json",
                                        benchmark=R.LONGMEMEVAL, scheme="cluster")))
check("the sentinel cluster is a single, explicitly named component, not a fabricated conversation set",
      m["expected_cluster_ids"] == ["longmemeval_single_connected_component_inherited_task3a1"])

print()
if FAIL:
    print(f"{len(FAIL)} FAILING CHECK(S): {FAIL}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: schema, internal consistency and gate behaviour of two PROPOSED manifests. "
      "Not a binding, not corpus verification, and not authorization to run.")
raise SystemExit(0)
