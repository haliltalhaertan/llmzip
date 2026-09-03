#!/usr/bin/env python3
"""Precondition 3: do the declarative payloads actually agree with the normative source?

The V6 gate never compares a concept's declared value against the runner constant it
names, and never checks that a declared mirror contains the value. This does that
comparison independently, by AST-reading the runner's module constants.
"""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

CAND = Path("/home/user/llmzip/task4f1_execution_candidate_v6_2026_09_03")
runner_src = (CAND / "v52_t4f1_beam_retrieval.py").read_text()
tree = ast.parse(runner_src)
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        try:
            consts[node.targets[0].id] = ast.literal_eval(node.value)
        except Exception:
            pass
# frozenset({...}) / tuple(range(20)) need a second pass
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name in consts:
            continue
        seg = ast.get_source_segment(runner_src, node.value) or ""
        try:
            consts[name] = eval(seg, {"frozenset": frozenset, "range": range, "tuple": tuple,
                                      "HAAR_SEEDS": consts.get("HAAR_SEEDS")})
        except Exception:
            pass

smap = json.loads((CAND / "NORMATIVE_SOURCE_MAP.json").read_text())
seal = json.loads((CAND / "CANDIDATE_EXECUTION_SEAL.json").read_text())
fields = {f["concept"]: f for f in smap["fields"]}

checks = []
def check(label, declared, actual):
    ok = declared == actual
    checks.append({"check": label, "declared_in_map": declared, "actual_in_runner": actual, "agrees": ok})

check("upstream_corpus_commit", fields["upstream_corpus_commit"]["value"], consts.get("EXPECTED_BEAM_COMMIT"))
check("upstream_tree_manifest_anchor", fields["upstream_tree_manifest_anchor"]["value"], consts.get("EXPECTED_BEAM_MANIFEST_SHA256"))
check("parent_commit_anchor", fields["parent_commit_anchor"]["value"], consts.get("EXPECTED_PARENT_COMMIT"))
check("restricted_seal_anchor", fields["restricted_seal_anchor"]["value"], consts.get("EXPECTED_RESTRICTED_SEAL_SHA256"))
check("restricted_protocol_anchor", fields["restricted_protocol_anchor"]["value"], consts.get("EXPECTED_PROTOCOL_SHA256"))
check("dependency_lock", fields["dependency_lock"]["value"], consts.get("EXPECTED_DEPENDENCY_LOCK_SHA256"))
check("authorization_schema_version", fields["authorization_schema_version"]["value"], consts.get("AUTH_SCHEMA"))
check("authorization_signed_fields", fields["authorization_signed_fields"]["value"], list(consts.get("AUTH_SIGNED_FIELDS", ())))
check("tie_priority.prefix", fields["tie_priority"]["value"]["prefix"], consts.get("TIE_PREFIX", b"").decode())

co = fields["cohort_anchor"]["value"]
check("cohort.total_rows", co["total_rows"], consts.get("EXPECTED_TOTAL_ROWS"))
check("cohort.eligible_questions", co["eligible_questions"], consts.get("EXPECTED_ELIGIBLE"))
check("cohort.archive_count", co["archive_count"], consts.get("EXPECTED_ARCHIVES"))
check("cohort.excluded_archives", sorted(co["excluded_archives"]), sorted(consts.get("EXCLUDED_ARCHIVES", ())))
check("cohort.sha256", co["sha256"], consts.get("EXPECTED_COHORT_SHA256"))

ms = fields["methods_seeds_trials_topk"]["value"]
check("methods.haar_seeds", ms["haar_seeds"], list(consts.get("HAAR_SEEDS", ())))
check("methods.itq_seeds", ms["itq_seeds"], list(consts.get("ITQ_SEEDS", ())))
check("methods.itq_iterations", ms["itq_iterations"], consts.get("ITQ_ITERATIONS"))
check("methods.top_k", ms["top_k"], consts.get("TOP_K"))
check("methods.trials", ms["trials"], len(consts.get("NUISANCE_TRIALS", ())))
check("methods.latent_dim", ms["latent_dim"], consts.get("LATENT_DIM"))
check("methods.latent_seed", ms["latent_seed"], consts.get("LATENT_SEED"))
check("methods.mixed_dim", ms["mixed_dim"], consts.get("MIXED_DIM"))
check("methods.mixed_seed", ms["mixed_seed"], consts.get("MIXED_SEED"))
check("methods.invariance_tolerance", ms["invariance_tolerance"], consts.get("INVARIANCE_TOLERANCE"))

ca = fields["canary_algorithm_and_digests"]["value"]
check("canary.archive_sign_sha256", ca["archive_sign_sha256"], consts.get("EXPECTED_REAL_CANARY_ARCHIVE_SIGN_SHA256"))
check("canary.query_sign_sha256", ca["query_sign_sha256"], consts.get("EXPECTED_REAL_CANARY_QUERY_SIGN_SHA256"))
check("canary.sign_margin", ca["sign_margin"], consts.get("CANARY_SIGN_MARGIN"))

# seal mirrors that the gate does not verify
check("seal.pinned_beam_commit mirror", seal["sealed_task4f0_boundary"].get("pinned_beam_commit") if isinstance(seal.get("sealed_task4f0_boundary"), dict) else None, consts.get("EXPECTED_BEAM_COMMIT"))
check("seal.cohort eligible mirror", seal["sealed_task4f0_boundary"].get("eligible_questions") if isinstance(seal.get("sealed_task4f0_boundary"), dict) else None, consts.get("EXPECTED_ELIGIBLE"))

# arm identifiers: declared vs runner
arms = fields["arm_identifiers"]["value"]
found = sorted({a for a in arms if a in runner_src})
check("arm_identifiers all present in runner", sorted(arms), found)

Path(sys.argv[1]).write_text(json.dumps({"checks": checks,
    "agreements": sum(c["agrees"] for c in checks), "total": len(checks)}, indent=2, sort_keys=True, default=str) + "\n")
for c in checks:
    print(f"{'AGREE   ' if c['agrees'] else 'DISAGREE'} {c['check']}")
    if not c["agrees"]:
        print(f"           map={c['declared_in_map']!r}\n           runner={c['actual_in_runner']!r}")
print(f"\n{sum(c['agrees'] for c in checks)}/{len(checks)} agree")
