#!/usr/bin/env python3
"""Gate 2 (V3->V4 change isolation) and Gate 8 (leakage) AST analysis."""
from __future__ import annotations
import ast, json, sys
from pathlib import Path

V3 = Path(sys.argv[1]); V4 = Path(sys.argv[2]); OUT = Path(sys.argv[3])
t3, t4 = ast.parse(V3.read_text()), ast.parse(V4.read_text())

def top_defs(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[n.name] = n
    return out

def consts(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            out[n.targets[0].id] = ast.dump(n.value)
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None:
            out[n.target.id] = ast.dump(n.value)
    return out

d3, d4 = top_defs(t3), top_defs(t4)
c3, c4 = consts(t3), consts(t4)

# --- permitted V4 change surface ---
PERMITTED_FUNCS = {"real_archive_canary", "sign_code_sha256", "describe_numerical_backend", "verify_environment"}
PERMITTED_CONSTS = {"EXPECTED_REAL_CANARY_ARCHIVE_SIGN_SHA256", "EXPECTED_REAL_CANARY_QUERY_SIGN_SHA256",
                    "CANARY_SIGN_MARGIN", "AUTH_SCHEMA",
                    "EXPECTED_REAL_CANARY_ARCHIVE_SHA256", "EXPECTED_REAL_CANARY_QUERY_SHA256"}
# functions where only a schema *version string literal* may differ
SCHEMA_LITERAL_FUNCS = {"verify_execution_seal", "write_archive_result", "verify_existing_archive",
                        "finalize_results", "preflight"}
SCHEMA_PAIRS = [("V52_T4F1_EXECUTION_CANDIDATE_SEAL_V3", "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4"),
                ("V52_T4F1_ARCHIVE_RESULT_META_V3", "V52_T4F1_ARCHIVE_RESULT_META_V4"),
                ("V52_T4F1_POST_RUN_MANIFEST_V3", "V52_T4F1_POST_RUN_MANIFEST_V4"),
                ("V52_T4F1_IMPLEMENTATION_PREFLIGHT_V3", "V52_T4F1_IMPLEMENTATION_PREFLIGHT_V4")]

def normalize_schema(dump: str) -> str:
    for old, new in SCHEMA_PAIRS:
        dump = dump.replace(f"'{old}'", "'<SCHEMA>'").replace(f"'{new}'", "'<SCHEMA>'")
    return dump

added = sorted(set(d4) - set(d3)); removed = sorted(set(d3) - set(d4))
changed, changed_only_schema, identical = [], [], []
for name in sorted(set(d3) & set(d4)):
    a, b = ast.dump(d3[name]), ast.dump(d4[name])
    if a == b:
        identical.append(name)
    elif normalize_schema(a) == normalize_schema(b):
        changed_only_schema.append(name)
    else:
        changed.append(name)

const_changed = sorted(k for k in set(c3) & set(c4) if c3[k] != c4[k])
const_added = sorted(set(c4) - set(c3)); const_removed = sorted(set(c3) - set(c4))

# --- numerical / estimand core must be byte-identical at AST level ---
CORE = ["fit_archive_representation", "transform_queries", "rank_hamming", "signed_permutation",
        "haar_rotation", "fit_itq", "metrics_at_3", "append_trial_rows", "evaluate_archive",
        "tie_priority", "priority_arrays", "load_archive", "load_questions", "question_payload",
        "iter_messages", "canonical_raw_id", "canonical_memory_key", "array_sha256",
        "ArchiveRepresentation", "synthetic_preflight", "load_and_verify_cohort",
        "verify_beam_checkout", "archive_relative_paths", "git_blob_sha1", "verify_run_authorization"]
core_report = {n: ("IDENTICAL" if n in identical else
                   "SCHEMA_LITERAL_ONLY" if n in changed_only_schema else
                   "CHANGED" if n in changed else "MISSING") for n in CORE}
CORE_CONSTS = ["LATENT_DIM","LATENT_SEED","MIXED_DIM","MIXED_SEED","TOP_K","HAAR_SEEDS","SIGNED_PERM_SEEDS",
               "ITQ_SEEDS","ITQ_ITERATIONS","NUISANCE_TRIALS","INVARIANCE_TOLERANCE","TIE_PREFIX",
               "EXPECTED_TOTAL_ROWS","EXPECTED_ELIGIBLE","EXPECTED_ARCHIVES","EXCLUDED_ARCHIVES","TIERS",
               "TRIAL_FIELDS","REAL_CANARY_QUERY","AUTH_SIGNED_FIELDS","AUTH_HMAC_ENV","ENVIRONMENT_LOCK",
               "THREAD_LOCK","EXPECTED_COHORT_SHA256","EXPECTED_BEAM_COMMIT","EXPECTED_BEAM_MANIFEST_SHA256",
               "EXPECTED_PROTOCOL_SHA256","EXPECTED_RESTRICTED_SEAL_SHA256","EXPECTED_DEPENDENCY_LOCK_SHA256",
               "EXPECTED_PARENT_COMMIT"]
core_const_report = {k: ("IDENTICAL" if c3.get(k) == c4.get(k) else "CHANGED") for k in CORE_CONSTS}

# --- Gate 3.7: canary call graph must not reach ranking / metric / gold ---
def calls_in(node):
    return {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
FORBIDDEN_IN_CANARY = {"rank_hamming", "metrics_at_3", "append_trial_rows", "load_questions",
                       "question_payload", "evaluate_archive", "priority_arrays", "fit_itq",
                       "haar_rotation", "signed_permutation", "write_csv", "finalize_results"}
def transitive(name, seen=None):
    seen = seen or set()
    if name in seen or name not in d4: return seen
    seen.add(name)
    for c in calls_in(d4[name]):
        transitive(c, seen)
    return seen
canary_graph = sorted(transitive("real_archive_canary"))
canary_violations = sorted(set(canary_graph) & FORBIDDEN_IN_CANARY)

# --- Gate 8: environment reads and secret leakage ---
env_reads = []
for n in ast.walk(t4):
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get":
        v = n.func.value
        if isinstance(v, ast.Attribute) and v.attr == "environ":
            if n.args and isinstance(n.args[0], ast.Constant):
                env_reads.append(n.args[0].value)
            elif n.args and isinstance(n.args[0], ast.Name):
                env_reads.append(f"<name:{n.args[0].id}>")
# where is AUTH_HMAC_ENV read?
hmac_read_funcs = []
for name, node in d4.items():
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get":
            v = n.func.value
            if isinstance(v, ast.Attribute) and v.attr == "environ" and n.args and \
               isinstance(n.args[0], ast.Name) and n.args[0].id == "AUTH_HMAC_ENV":
                hmac_read_funcs.append(name)
# does describe_numerical_backend read anything but the two known keys?
backend_env = [n.args[0].value for n in ast.walk(d4["describe_numerical_backend"])
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "get"
               and isinstance(n.func.value, ast.Attribute) and n.func.value.attr == "environ"
               and n.args and isinstance(n.args[0], ast.Constant)]

report = {
  "gate2": {
    "functions_added": added, "functions_removed": removed,
    "functions_changed_beyond_schema_literal": changed,
    "functions_changed_schema_literal_only": changed_only_schema,
    "functions_identical_count": len(identical),
    "constants_added": const_added, "constants_removed": const_removed, "constants_changed": const_changed,
    "changes_outside_permitted_surface": sorted(
        (set(changed) - PERMITTED_FUNCS) | (set(added) - PERMITTED_FUNCS) | set(removed)
        | ((set(const_changed) | set(const_added) | set(const_removed)) - PERMITTED_CONSTS)),
    "numerical_core_ast_status": core_report,
    "numerical_core_constant_status": core_const_report,
    "numerical_core_all_identical": all(v == "IDENTICAL" for v in core_report.values())
                                    and all(v == "IDENTICAL" for v in core_const_report.values()),
  },
  "gate3_canary_static": {
    "canary_transitive_call_graph": canary_graph,
    "forbidden_calls_reachable_from_canary": canary_violations,
    "canary_clean": canary_violations == [],
  },
  "gate8_leakage": {
    "all_environ_get_keys": sorted(set(env_reads)),
    "AUTH_HMAC_ENV_read_in_functions": sorted(set(hmac_read_funcs)),
    "describe_numerical_backend_env_keys": sorted(set(backend_env)),
    "backend_reads_only_coretype": sorted(set(backend_env)) == ["OPENBLAS_CORETYPE"],
  },
}
OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2, sort_keys=True))
