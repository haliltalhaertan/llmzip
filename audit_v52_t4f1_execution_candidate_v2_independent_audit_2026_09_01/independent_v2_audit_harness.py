from __future__ import annotations

import ast
import csv
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize


AUDIT = Path(__file__).resolve().parent
REPO = AUDIT.parent
CANDIDATE = REPO / "task4f1_execution_candidate_v2_2026_09_01"
PREFLIGHT = REPO / "task4f1_execution_candidate_v2_preflight_2026_09_01"
V1 = REPO / "task4f1_execution_candidate_2026_08_31"
REFREEZE = REPO / "audit_v52_t4f0_restricted_refreeze_2026_08_31"
T4F0 = REPO / "audit_v52_t4f0_codex_2026_08_31"
CORPUS = REPO.parent / "BEAM_pinned_3e12035532eb85768f1a7cd779832b650c4b2ef9"
PYTHON = Path(sys.executable).resolve()
RUNNER = CANDIDATE / "v52_t4f1_beam_retrieval.py"
AUTH_ENV = "V52_T4F1_AUTH_HMAC_KEY_HEX"

EXPECTED = {
    "parent_commit": "d3c7aa09c9553cd5ac100e668923abab602e4257",
    "beam_commit": "3e12035532eb85768f1a7cd779832b650c4b2ef9",
    "beam_manifest": "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318",
    "restricted_seal": "596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c",
    "protocol": "f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1",
    "cohort": "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a",
    "dependency": "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e",
    "runner": "c50dfa7130918b8183c51edf68f5e2baac21a419f0d29bf2ec930f9de38e6139",
    "inventory": "9d7429893f50a729e4471684580660461e944e599c43df24172b2c4d1d66e22d",
    "candidate_seal": "4cc6313649da9ca4b10e64610a8ff40173c1ccacd663dda9fadabcdf059b996c",
    "preflight_inventory": "976ef3d483e96d33177ab0287bd3665e22b7a87d3862997a7e9cde7faeb7f85b",
    "preflight_report": "92618cf3acd3108534f7723126413f7d4664d85970eef7d05bbdc7aa7e2fee5c",
    "canary_archive": "25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025",
    "canary_query": "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869",
}

COMMANDS: list[dict[str, Any]] = []
COUNTS = {"mode_run": 0, "mode_finalize": 0, "hmac_env_set": 0}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def array_sha256(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def safe_subprocess(command: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    joined = " ".join(command).lower()
    if "--mode run" in joined or "--mode finalize" in joined:
        raise RuntimeError("AUDIT HARNESS REFUSED FORBIDDEN MODE")
    if AUTH_ENV in env:
        COUNTS["hmac_env_set"] += 1
        raise RuntimeError("AUDIT HARNESS REFUSED HMAC ENVIRONMENT")
    completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=False)
    COMMANDS.append({
        "command": command,
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    })
    return completed


def assert_blocked(callable_obj: Any, fragment: str) -> str:
    try:
        callable_obj()
    except RuntimeError as exc:
        text = str(exc)
        if fragment not in text:
            raise AssertionError(f"wrong block: {text!r}; expected {fragment!r}") from exc
        return text
    raise AssertionError(f"expected block containing {fragment!r}")


def import_runner() -> Any:
    spec = importlib.util.spec_from_file_location("independent_v2_candidate", RUNNER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def closure_and_upstream(env: dict[str, str]) -> dict[str, Any]:
    candidate_inventory = json.loads((CANDIDATE / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
    candidate_seal = json.loads((CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    declared = {item["name"]: item for item in candidate_inventory["files"]}
    recursive = {
        path.relative_to(CANDIDATE).as_posix(): path
        for path in CANDIDATE.rglob("*") if path.is_file()
    }
    expected_names = set(declared) | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"}
    payload_checks = []
    for name, item in sorted(declared.items()):
        path = CANDIDATE / name
        payload_checks.append({
            "name": name,
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "declared_match": path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"],
        })

    preflight_inventory_path = PREFLIGHT / "PREFLIGHT_HASHES.json"
    preflight_inventory = json.loads(preflight_inventory_path.read_text(encoding="utf-8"))
    preflight_checks = []
    for item in preflight_inventory["files"]:
        path = PREFLIGHT / item["name"]
        preflight_checks.append({
            "name": item["name"],
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "declared_match": path.stat().st_size == item["bytes"] and sha256(path) == item["sha256"],
        })

    package = safe_subprocess([str(PYTHON), "-B", str(CANDIDATE / "candidate_package_preflight.py")], cwd=REPO, env=env)
    if package.returncode != 0:
        raise RuntimeError(package.stderr or package.stdout)

    with tempfile.TemporaryDirectory(prefix="nested_closure_", dir=AUDIT) as temp_name:
        temp_candidate = Path(temp_name) / "candidate"
        shutil.copytree(CANDIDATE, temp_candidate)
        nested = temp_candidate / "nested" / "UNBOUND.txt"
        nested.parent.mkdir(parents=True)
        nested.write_text("synthetic unbound closure probe\n", encoding="utf-8")
        nested_result = safe_subprocess([str(PYTHON), "-B", str(temp_candidate / "candidate_package_preflight.py")], cwd=REPO, env=env)
        nested_rejected = nested_result.returncode != 0 and "payload closure mismatch" in (nested_result.stdout + nested_result.stderr)

    git_head = safe_subprocess(["git", "rev-parse", "HEAD"], cwd=REPO, env=env)
    if git_head.returncode != 0:
        raise RuntimeError(git_head.stderr)

    beam_manifest = json.loads((T4F0 / "pinned_tree_manifest.json").read_text(encoding="utf-8"))
    cohort_path = REFREEZE / "estimand_primary_cohort.csv"
    with cohort_path.open("r", encoding="utf-8", newline="") as handle:
        cohort_rows = list(csv.DictReader(handle))
    eligible = [row for row in cohort_rows if row["primary_evidence_cohort_eligible"] == "True"]
    archives = sorted({f"{row['tier']}::{row['conversation_id']}" for row in eligible})

    anchor_checks = {
        "runner": sha256(RUNNER) == EXPECTED["runner"] and RUNNER.stat().st_size == 56142,
        "inventory": sha256(CANDIDATE / "PAYLOAD_HASHES.json") == EXPECTED["inventory"] and (CANDIDATE / "PAYLOAD_HASHES.json").stat().st_size == 1180,
        "candidate_seal": sha256(CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json") == EXPECTED["candidate_seal"] and (CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json").stat().st_size == 6186,
        "preflight_inventory": sha256(preflight_inventory_path) == EXPECTED["preflight_inventory"] and preflight_inventory_path.stat().st_size == 1807,
        "preflight_report": sha256(PREFLIGHT / "IMPLEMENTATION_PREFLIGHT.json") == EXPECTED["preflight_report"] and (PREFLIGHT / "IMPLEMENTATION_PREFLIGHT.json").stat().st_size == 3564,
        "parent_commit": git_head.stdout.strip() == EXPECTED["parent_commit"],
        "beam_manifest": sha256(T4F0 / "pinned_tree_manifest.json") == EXPECTED["beam_manifest"] and beam_manifest.get("commit") == EXPECTED["beam_commit"],
        "restricted_seal": sha256(REFREEZE / "CANDIDATE_SEAL.json") == EXPECTED["restricted_seal"],
        "protocol": sha256(REFREEZE / "REFREEZE_PROTOCOL.md") == EXPECTED["protocol"],
        "cohort": sha256(cohort_path) == EXPECTED["cohort"],
        "dependency": sha256(CANDIDATE / "DEPENDENCY_LOCK.txt") == EXPECTED["dependency"],
        "status": candidate_inventory.get("status") == "PREPARED_NOT_INDEPENDENTLY_AUDITED" and candidate_seal.get("status") == "PREPARED_NOT_INDEPENDENTLY_AUDITED",
        "pending_key_commitment": candidate_seal.get("authorization_control", {}).get("key_commitment_sha256") == "PENDING_HEAD_RESEARCHER_PREREGISTRATION",
        "eligible_structure": len(cohort_rows) == 2000 and len(eligible) == 1712 and len(archives) == 96,
        "excluded_archives": set(candidate_seal["sealed_task4f0_boundary"]["excluded_archives"]) == {"1M::5", "1M::26", "1M::33", "1M::34"},
    }
    result = {
        "schema": "V52_T4F1_INDEPENDENT_V2_CLOSURE_EVIDENCE_V1",
        "candidate_recursive_file_count": len(recursive),
        "candidate_recursive_files": sorted(recursive),
        "expected_recursive_files": sorted(expected_names),
        "recursive_exact_set_match": set(recursive) == expected_names,
        "no_nested_files": all("/" not in name for name in recursive),
        "no_pycache": not any("__pycache__" in name for name in recursive),
        "payload_checks": payload_checks,
        "preparation_inventory_checks": preflight_checks,
        "package_preflight_pass": True,
        "nested_unbound_fixture_rejected": nested_rejected,
        "anchor_checks": anchor_checks,
        "seal_inventory_binding": candidate_seal["payload_inventory"]["sha256"] == sha256(CANDIDATE / "PAYLOAD_HASHES.json"),
        "seal_implementation_binding": candidate_seal["implementation"]["sha256"] == sha256(RUNNER),
    }
    result["status"] = "PASS" if (
        result["candidate_recursive_file_count"] == 8
        and result["recursive_exact_set_match"]
        and result["no_nested_files"]
        and result["no_pycache"]
        and all(item["declared_match"] for item in payload_checks)
        and all(item["declared_match"] for item in preflight_checks)
        and nested_rejected
        and all(anchor_checks.values())
        and result["seal_inventory_binding"]
        and result["seal_implementation_binding"]
    ) else "FAIL"
    return result


def function_map(source: str) -> tuple[ast.Module, dict[str, ast.FunctionDef]]:
    tree = ast.parse(source)
    return tree, {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}


def static_leakage_and_diff() -> dict[str, Any]:
    v1_source = (V1 / "v52_t4f1_beam_retrieval.py").read_text(encoding="utf-8")
    v2_source = RUNNER.read_text(encoding="utf-8")
    _, v1_functions = function_map(v1_source)
    tree, v2_functions = function_map(v2_source)
    numerical_functions = [
        "load_archive", "question_payload", "fit_archive_representation", "transform_queries",
        "tie_priority", "priority_arrays", "rank_hamming", "signed_permutation", "haar_rotation",
        "fit_itq", "metrics_at_3", "append_trial_rows", "array_sha256", "synthetic_preflight",
        "real_archive_canary",
    ]
    unchanged = {
        name: ast.dump(v1_functions[name], include_attributes=False) == ast.dump(v2_functions[name], include_attributes=False)
        for name in numerical_functions
    }
    fit = v2_functions["fit_archive_representation"]
    fit_source = ast.get_source_segment(v2_source, fit) or ""
    fit_args = [argument.arg for argument in fit.args.args]
    evaluate_source = ast.get_source_segment(v2_source, v2_functions["evaluate_archive"]) or ""
    tie_source = ast.get_source_segment(v2_source, v2_functions["tie_priority"]) or ""
    canary_source = ast.get_source_segment(v2_source, v2_functions["real_archive_canary"]) or ""
    run_source = ast.get_source_segment(v2_source, v2_functions["run_archives"]) or ""
    main_source = ast.get_source_segment(v2_source, v2_functions["main"]) or ""
    forbidden_fit = [token for token in ("question", "gold", "source_id", "answer", "rubric", "ability", "difficulty", "result") if token in fit_source.lower()]
    print_calls = [
        ast.get_source_segment(v2_source, node) or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print"
    ]
    allowed_changed = {
        "verify_execution_seal", "verify_run_authorization", "evaluate_archive", "verify_existing_archive",
        "finalize_results", "preflight", "run_archives", "main",
    }
    all_shared = set(v1_functions) & set(v2_functions)
    changed_shared = sorted(name for name in all_shared if ast.dump(v1_functions[name], include_attributes=False) != ast.dump(v2_functions[name], include_attributes=False))
    unexpected_changed = sorted(set(changed_shared) - allowed_changed)

    checks = {
        "numeric_function_ast_unchanged": all(unchanged.values()),
        "fit_accepts_only_memory_texts": fit_args == ["memory_texts"],
        "fit_forbidden_token_hits": forbidden_fit,
        "fit_call_archive_text_only": "fit_archive_representation(memory_texts)" in evaluate_source,
        "itq_archive_only": "fit_itq(centered_archive, seed)" in evaluate_source,
        "tie_signature_archive_and_memory_only": [arg.arg for arg in v2_functions["tie_priority"].args.args] == ["archive_id", "memory_key"],
        "tie_source_has_no_trial_or_outcome": "trial" not in tie_source.lower() and "outcome" not in tie_source.lower(),
        "canary_opens_no_question_file": "load_questions" not in canary_source and "probing_questions" not in canary_source,
        "canary_does_not_rank_or_metric": "rank_hamming" not in canary_source and "metrics_at_3" not in canary_source,
        "authorization_before_corpus_and_output": run_source.index("verify_run_authorization") < run_source.index("verify_beam_checkout") < run_source.index("output_dir.mkdir"),
        "finalize_authorization_before_corpus": main_source.index("verify_run_authorization") < main_source.index("verify_beam_checkout") < main_source.index("finalize_results"),
        "outcome_print_call_count": sum("retrieved" in call or "metric" in call or "fractional" in call or "any_at_3" in call or "all_at_3" in call for call in print_calls),
        "changed_functions": changed_shared,
        "unexpected_changed_functions": unexpected_changed,
    }
    return {
        "schema": "V52_T4F1_INDEPENDENT_V2_STATIC_LEAKAGE_EVIDENCE_V1",
        "checks": checks,
        "numerical_function_equality": unchanged,
        "allowed_v2_change_functions": sorted(allowed_changed),
        "v2_change_isolation_pass": all(unchanged.values()) and not unexpected_changed,
        "status": "PASS" if (
            all(unchanged.values()) and not unexpected_changed and fit_args == ["memory_texts"] and not forbidden_fit
            and checks["fit_call_archive_text_only"] and checks["itq_archive_only"]
            and checks["tie_signature_archive_and_memory_only"] and checks["tie_source_has_no_trial_or_outcome"]
            and checks["canary_opens_no_question_file"] and checks["canary_does_not_rank_or_metric"]
            and checks["authorization_before_corpus_and_output"] and checks["finalize_authorization_before_corpus"]
            and checks["outcome_print_call_count"] == 0
        ) else "FAIL",
    }


def independent_canary() -> dict[str, Any]:
    chat_path = CORPUS / "chats" / "100K" / "12" / "chat.json"
    raw = json.loads(chat_path.read_text(encoding="utf-8"))
    messages: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if {"role", "id", "content"}.issubset(value):
                messages.append(value)
                return
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(raw)
    memory_texts = [f"{message['role']}: {message['content']}" for message in messages]
    word = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)
    char = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    x_word = normalize(word.fit_transform(memory_texts))
    x_char = normalize(char.fit_transform(memory_texts))
    latent = TruncatedSVD(n_components=32, random_state=5101)
    x_latent = normalize(latent.fit_transform(x_word))
    source = sparse.hstack([sparse.csr_matrix(x_latent), x_word, x_char], format="csr")
    mixed = TruncatedSVD(n_components=96, random_state=5204)
    y96 = normalize(mixed.fit_transform(source))
    mean96 = np.asarray(y96.mean(axis=0, keepdims=True), dtype=np.float64)
    centered96 = np.asarray(y96 - mean96, dtype=np.float64)
    fixed_query = "Which project phase mentioned module 7 and a deadline?"
    q_word = normalize(word.transform([fixed_query]))
    q_char = normalize(char.transform([fixed_query]))
    q_latent = normalize(latent.transform(q_word))
    q_source = sparse.hstack([sparse.csr_matrix(q_latent), q_word, q_char], format="csr")
    q_y96 = normalize(mixed.transform(q_source))
    q_centered = np.asarray(q_y96 - mean96, dtype=np.float64)
    archive_digest = array_sha256(centered96)
    query_digest = array_sha256(q_centered)
    return {
        "archive_id": "100K::12",
        "archive_units": len(messages),
        "archive_shape": list(centered96.shape),
        "query_shape": list(q_centered.shape),
        "archive_sha256": archive_digest,
        "query_sha256": query_digest,
        "archive_digest_match": archive_digest == EXPECTED["canary_archive"],
        "query_digest_match": query_digest == EXPECTED["canary_query"],
        "question_file_opened": False,
        "gold_label_loaded": False,
        "ranking_performed": False,
        "retrieval_quality_computed": False,
    }


def method_evidence(module: Any) -> dict[str, Any]:
    synthetic = module.synthetic_preflight()
    rng = np.random.default_rng(99173)
    docs = rng.normal(size=(128, module.MIXED_DIM))
    queries = rng.normal(size=(3, module.MIXED_DIM))
    keys = [f"100K::synthetic::{index}" for index in range(128)]
    hi, lo = module.priority_arrays("100K::synthetic", keys)
    native_rankings = []
    native_distances = []
    for query in queries:
        ranking, distances = module.rank_hamming(docs >= 0, query >= 0, hi, lo)
        native_rankings.append(ranking)
        native_distances.append(distances)
    signed_exact = True
    for seed in module.SIGNED_PERM_SEEDS:
        permutation, signs = module.signed_permutation(seed)
        for index, query in enumerate(queries):
            ranking, distances = module.rank_hamming((docs[:, permutation] * signs) >= 0, (query[permutation] * signs) >= 0, hi, lo)
            signed_exact = signed_exact and np.array_equal(ranking, native_rankings[index]) and np.array_equal(distances, native_distances[index])
    haar_errors = []
    for seed in module.HAAR_SEEDS:
        rotation = module.haar_rotation(seed)
        haar_errors.append(max(
            float(np.max(np.abs(rotation.T @ rotation - np.eye(module.MIXED_DIM)))),
            float(np.max(np.abs(queries @ docs.T - (queries @ rotation) @ (docs @ rotation).T))),
        ))
    itq_errors = []
    itq_orientation_exact = []
    for seed in module.ITQ_SEEDS:
        observed = module.fit_itq(docs, seed)
        local_rng = np.random.default_rng(seed)
        initial = local_rng.normal(size=(module.MIXED_DIM, module.MIXED_DIM))
        u_matrix, _, vt_matrix = np.linalg.svd(initial, full_matrices=False)
        expected_rotation = u_matrix @ vt_matrix
        for _ in range(module.ITQ_ITERATIONS):
            binary = np.where(docs @ expected_rotation >= 0, 1.0, -1.0)
            covariance = binary.T @ docs
            u_matrix, _, vt_matrix = np.linalg.svd(covariance, full_matrices=False)
            expected_rotation = vt_matrix.T @ u_matrix.T
        itq_orientation_exact.append(np.array_equal(observed, expected_rotation))
        itq_errors.append(float(np.max(np.abs(observed.T @ observed - np.eye(module.MIXED_DIM)))))
    equal_doc_codes = np.zeros((4, module.MIXED_DIM), dtype=bool)
    query_code = np.zeros(module.MIXED_DIM, dtype=bool)
    tie_hi = np.asarray([9, 1, 1, 1], dtype=np.uint64)
    tie_lo = np.asarray([0, 8, 3, 3], dtype=np.uint64)
    tie_ranking, tie_distances = module.rank_hamming(equal_doc_codes, query_code, tie_hi, tie_lo)
    trial_rows: list[dict[str, Any]] = []
    module.append_trial_rows(
        trial_rows,
        {"audit_question_id": "100K::synthetic::fact::1", "tier": "100K", "conversation_id": "synthetic", "ability": "fact"},
        "NATIVE_SIGN96", None, 128, [str(index) for index in range(128)], native_rankings[0], native_distances[0], {"1", "2", "3", "4"},
    )
    replication_identity = len(trial_rows) == 20 and len({json.dumps({k: v for k, v in row.items() if k != "trial"}, sort_keys=True) for row in trial_rows}) == 1
    structural = module.metrics_at_3(["1", "2", "3"], {"1", "2", "3", "4"})
    canary = independent_canary()
    result = {
        "schema": "V52_T4F1_INDEPENDENT_V2_METHOD_EVIDENCE_V1",
        "candidate_synthetic_preflight": synthetic,
        "independent_signed_permutation_exact_hamming_and_ranking": signed_exact,
        "haar_max_continuous_or_orthogonality_error": max(haar_errors),
        "haar_tolerance": module.INVARIANCE_TOLERANCE,
        "itq_max_orthogonality_error": max(itq_errors),
        "itq_orientation_exact_independent_reconstruction": all(itq_orientation_exact),
        "tie_fixture_distances": tie_distances.tolist(),
        "tie_fixture_ranking": tie_ranking.tolist(),
        "tie_fixture_expected_ranking": [2, 3, 1, 0],
        "tie_canonical_index_last_resort": tie_ranking.tolist() == [2, 3, 1, 0],
        "deterministic_trial_replication_identity": replication_identity,
        "structural_all_at_3_zero_fixture": {"fractional": structural[0], "any": structural[1], "all": structural[2], "pass": structural == (0.75, 1, 0)},
        "independent_real_canary": canary,
        "real_retrieval_ranking_performed": False,
        "retrieval_quality_computed": False,
    }
    result["status"] = "PASS" if (
        synthetic["status"] == "PASS" and signed_exact and max(haar_errors) <= module.INVARIANCE_TOLERANCE
        and max(itq_errors) <= module.INVARIANCE_TOLERANCE and all(itq_orientation_exact)
        and result["tie_canonical_index_last_resort"] and replication_identity
        and result["structural_all_at_3_zero_fixture"]["pass"]
        and canary["archive_digest_match"] and canary["query_digest_match"]
    ) else "FAIL"
    return result


def authorization_evidence(module: Any) -> dict[str, Any]:
    os.environ.pop(AUTH_ENV, None)
    source = RUNNER.read_text(encoding="utf-8")
    _, functions = function_map(source)
    auth_source = ast.get_source_segment(source, functions["verify_run_authorization"]) or ""
    expected_fields = (
        "schema", "status", "retrieval_quality_outcome_access", "execution_script_sha256",
        "execution_candidate_seal_sha256", "cohort_sha256", "required_archive_count",
        "output_namespace_basename", "preregistration_seal_sha256", "authorization_id", "authorization_nonce",
    )
    template = CANDIDATE / "RUN_AUTHORIZATION_TEMPLATE.json"
    negative = PREFLIGHT / "NEGATIVE_STRUCTURALLY_COMPLETE_AUTH.json"
    cohort = REFREEZE / "estimand_primary_cohort.csv"
    template_block = assert_blocked(
        lambda: module.verify_run_authorization(template, RUNNER, CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json", cohort, AUDIT / "template-output"),
        "INVALID RUN AUTHORIZATION",
    )
    negative_block = assert_blocked(
        lambda: module.verify_run_authorization(negative, RUNNER, CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json", cohort, AUDIT / "NEGATIVE_STRUCTURAL_MUST_NOT_EXIST"),
        "HEAD RESEARCHER AUTHORITY KEY NOT SEALED",
    )
    seal = json.loads((CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json").read_text(encoding="utf-8"))
    static_checks = {
        "exact_signed_field_tuple": tuple(module.AUTH_SIGNED_FIELDS) == expected_fields,
        "exact_closed_document_field_set": "set(authorization) != exact_keys" in auth_source,
        "canonical_json_hmac_sha256": "hmac.new(secret, canonical_json_bytes(signed_payload), hashlib.sha256)" in auth_source,
        "constant_time_compare": "hmac.compare_digest" in auth_source,
        "script_binding": '"execution_script_sha256": sha256_file(script_path)' in auth_source,
        "candidate_seal_binding": '"execution_candidate_seal_sha256": sha256_file(execution_seal_path)' in auth_source,
        "cohort_binding": '"cohort_sha256": sha256_file(cohort_path)' in auth_source,
        "archive_count_binding": '"required_archive_count": EXPECTED_ARCHIVES' in auth_source,
        "output_basename_binding": '"output_namespace_basename": output_dir.name' in auth_source,
        "preregistration_and_id_nonce_signed": all(field in module.AUTH_SIGNED_FIELDS for field in ("preregistration_seal_sha256", "authorization_id", "authorization_nonce")),
        "key_32_bytes": "len(secret) != 32" in auth_source,
        "key_commitment_checked": "hashlib.sha256(secret).hexdigest() != commitment" in auth_source,
        "preflight_does_not_read_key": AUTH_ENV not in (ast.get_source_segment(source, functions["preflight"]) or ""),
        "candidate_fail_closed_pending_commitment": seal["authorization_control"]["key_commitment_sha256"] == "PENDING_HEAD_RESEARCHER_PREREGISTRATION",
        "hmac_environment_absent": AUTH_ENV not in os.environ,
    }
    return {
        "schema": "V52_T4F1_INDEPENDENT_V2_AUTHORIZATION_EVIDENCE_V1",
        "static_checks": static_checks,
        "template_direct_call_block": template_block,
        "negative_fixture_direct_call_block": negative_block,
        "hmac_environment_variable_set_count": COUNTS["hmac_env_set"],
        "valid_production_authorization_constructed": False,
        "governance_scope": "Byte-bound governance control; it does not protect against an attacker who can replace both the audited script and accepted seal outside the evidence chain.",
        "status": "PASS" if all(static_checks.values()) and COUNTS["hmac_env_set"] == 0 else "FAIL",
    }


def synthetic_rows(module: Any, *, tamper_metrics: bool = False, signed_top3_divergence: bool = False) -> list[dict[str, Any]]:
    methods = {
        "NATIVE_SIGN96": [None],
        "SIGNED_PERM_CONTROL96": list(module.SIGNED_PERM_SEEDS),
        "HAAR96_SIGN": list(module.HAAR_SEEDS),
        "ITQ96_CENTERED": list(module.ITQ_SEEDS),
    }
    rows = []
    for method, seeds in methods.items():
        for seed in seeds:
            for trial in module.NUISANCE_TRIALS:
                retrieved = ["1", "2", "3"]
                if tamper_metrics:
                    retrieved = ["9", "8", "7"]
                if signed_top3_divergence and method == "SIGNED_PERM_CONTROL96":
                    retrieved = ["3", "2", "1"]
                rows.append({
                    "audit_question_id": "100K::synthetic::fact::1",
                    "tier": "100K",
                    "conversation_id": "synthetic",
                    "ability": "fact",
                    "method": method,
                    "seed": "" if seed is None else seed,
                    "trial": trial,
                    "archive_units": 128,
                    "gold_count": 4,
                    "retrieved_top3_ids": json.dumps(retrieved, separators=(",", ":")),
                    "top3_distances": "[0,1,2]",
                    "fractional_source_evidence_recall_at_3": ".75",
                    "any_at_3": 1,
                    "all_at_3": 0,
                })
    return rows


def write_synthetic_checkpoint(module: Any, root: Path, provenance: dict[str, str], rows: list[dict[str, Any]], *, schema: str = "V52_T4F1_ARCHIVE_RESULT_META_V2") -> None:
    metadata = {
        "schema": schema,
        "archive_id": "100K::synthetic",
        "eligible_questions": 1,
        "archive_units": 128,
        "trial_rows": 320,
        "signed_control_question_seed_checks": 5,
        "continuous_max_abs_dot_diff": 0.0,
        "continuous_max_abs_norm_diff": 0.0,
        "outcomes_printed_to_console": False,
        "provenance": dict(provenance),
    }
    module.write_archive_result(root, "100K::synthetic", rows, metadata)


def checkpoint_and_aggregation_evidence(module: Any) -> dict[str, Any]:
    provenance = {
        "script_sha256": "1" * 64,
        "cohort_sha256": "2" * 64,
        "run_authorization_sha256": "3" * 64,
        "execution_candidate_seal_sha256": "4" * 64,
    }
    eligible = [{
        "audit_question_id": "100K::synthetic::fact::1",
        "tier": "100K",
        "conversation_id": "synthetic",
        "ability": "fact",
        "gold_source_unit_count": "4",
        "gold_source_ids_parsed": ["1", "2", "3", "4"],
    }]
    original_eligible = module.EXPECTED_ELIGIBLE
    original_archives = module.EXPECTED_ARCHIVES
    module.EXPECTED_ELIGIBLE = 1
    module.EXPECTED_ARCHIVES = 1
    try:
        with tempfile.TemporaryDirectory(prefix="checkpoint_", dir=AUDIT) as name:
            root = Path(name)
            rows = synthetic_rows(module)
            write_synthetic_checkpoint(module, root, provenance, rows)
            matching_accepted = module.verify_existing_archive(root, "100K::synthetic", 1, provenance)
            changed_hash_blocks = {}
            for key in provenance:
                changed = dict(provenance)
                changed[key] = "9" * 64
                changed_hash_blocks[key] = "ARCHIVE CHECKPOINT MISMATCH" in assert_blocked(
                    lambda changed=changed: module.verify_existing_archive(root, "100K::synthetic", 1, changed),
                    "ARCHIVE CHECKPOINT MISMATCH",
                )
            overwrite_archive_block = "REFUSE ARCHIVE OVERWRITE" in assert_blocked(
                lambda: write_synthetic_checkpoint(module, root, provenance, rows), "REFUSE ARCHIVE OVERWRITE"
            )

        with tempfile.TemporaryDirectory(prefix="stale_", dir=AUDIT) as name:
            stale = Path(name)
            write_synthetic_checkpoint(module, stale, provenance, synthetic_rows(module), schema="V52_T4F1_ARCHIVE_RESULT_META_V1")
            stale_v1_block = "ARCHIVE CHECKPOINT MISMATCH" in assert_blocked(
                lambda: module.verify_existing_archive(stale, "100K::synthetic", 1, provenance), "ARCHIVE CHECKPOINT MISMATCH"
            )

        with tempfile.TemporaryDirectory(prefix="incomplete_", dir=AUDIT) as name:
            incomplete = Path(name)
            archive_dir = incomplete / "archives"
            archive_dir.mkdir(parents=True)
            (archive_dir / "100K__synthetic.csv").write_text("synthetic incomplete\n", encoding="utf-8")
            incomplete_block = "INCOMPLETE ARCHIVE CHECKPOINT" in assert_blocked(
                lambda: module.verify_existing_archive(incomplete, "100K::synthetic", 1, provenance), "INCOMPLETE ARCHIVE CHECKPOINT"
            )

        with tempfile.TemporaryDirectory(prefix="hash_mismatch_", dir=AUDIT) as name:
            mismatch = Path(name)
            write_synthetic_checkpoint(module, mismatch, provenance, synthetic_rows(module))
            csv_path = mismatch / "archives" / "100K__synthetic.csv"
            csv_path.write_text(csv_path.read_text(encoding="utf-8") + "tamper\n", encoding="utf-8")
            content_hash_block = "ARCHIVE CHECKPOINT MISMATCH" in assert_blocked(
                lambda: module.verify_existing_archive(mismatch, "100K::synthetic", 1, provenance), "ARCHIVE CHECKPOINT MISMATCH"
            )

        with tempfile.TemporaryDirectory(prefix="finalize_", dir=AUDIT) as name:
            final_root = Path(name)
            write_synthetic_checkpoint(module, final_root, provenance, synthetic_rows(module))
            module.finalize_results(final_root, eligible, provenance)
            manifest = json.loads((final_root / "V52_T4F1_POST_RUN_MANIFEST.json").read_text(encoding="utf-8"))
            manifest_repeats_provenance = all(manifest.get(key) == value for key, value in provenance.items())
            manifest_overwrite_block = "REFUSE FINALIZATION OVERWRITE" in assert_blocked(
                lambda: module.finalize_results(final_root, eligible, provenance), "REFUSE FINALIZATION OVERWRITE"
            )
            schemas = {
                "question_seed_rows": sum(1 for _ in csv.DictReader((final_root / "V52_T4F1_question_seed_level.csv").open("r", encoding="utf-8", newline=""))),
                "question_rows": sum(1 for _ in csv.DictReader((final_root / "V52_T4F1_question_level.csv").open("r", encoding="utf-8", newline=""))),
                "aggregate_rows": sum(1 for _ in csv.DictReader((final_root / "V52_T4F1_aggregate.csv").open("r", encoding="utf-8", newline=""))),
                "trial_rows": manifest["trial_rows"],
                "question_denominator": manifest["question_denominator"],
            }

        with tempfile.TemporaryDirectory(prefix="derived_overwrite_", dir=AUDIT) as name:
            overwrite_root = Path(name)
            write_synthetic_checkpoint(module, overwrite_root, provenance, synthetic_rows(module))
            sentinel_path = overwrite_root / "V52_T4F1_question_seed_level.csv"
            sentinel = b"PREEXISTING_SYNTHETIC_RESULT_MUST_NOT_BE_OVERWRITTEN\n"
            sentinel_path.write_bytes(sentinel)
            module.finalize_results(overwrite_root, eligible, provenance)
            derived_existing_silently_overwritten = sentinel_path.read_bytes() != sentinel

        with tempfile.TemporaryDirectory(prefix="semantic_tamper_", dir=AUDIT) as name:
            tamper_root = Path(name)
            write_synthetic_checkpoint(module, tamper_root, provenance, synthetic_rows(module, tamper_metrics=True))
            semantic_metric_tamper_accepted = True
            try:
                module.finalize_results(tamper_root, eligible, provenance)
            except RuntimeError:
                semantic_metric_tamper_accepted = False

        with tempfile.TemporaryDirectory(prefix="signed_divergence_", dir=AUDIT) as name:
            divergence_root = Path(name)
            write_synthetic_checkpoint(module, divergence_root, provenance, synthetic_rows(module, signed_top3_divergence=True))
            signed_exact_top3_divergence_accepted = True
            try:
                module.finalize_results(divergence_root, eligible, provenance)
            except RuntimeError:
                signed_exact_top3_divergence_accepted = False
    finally:
        module.EXPECTED_ELIGIBLE = original_eligible
        module.EXPECTED_ARCHIVES = original_archives

    findings = [
        {
            "id": "B1",
            "severity": "BLOCKING",
            "title": "Derived finalization CSVs can be silently overwritten when the post-run manifest is absent",
            "observed": derived_existing_silently_overwritten,
            "sealing_blocker": derived_existing_silently_overwritten,
        },
        {
            "id": "B2",
            "severity": "BLOCKING",
            "title": "Finalizer accepts metric values not recomputed from frozen gold and retrieved IDs",
            "observed": semantic_metric_tamper_accepted,
            "sealing_blocker": semantic_metric_tamper_accepted,
        },
        {
            "id": "B3",
            "severity": "BLOCKING",
            "title": "Finalizer accepts Native/signed-control top-three divergence when aggregate metrics remain equal",
            "observed": signed_exact_top3_divergence_accepted,
            "sealing_blocker": signed_exact_top3_divergence_accepted,
        },
        {
            "id": "R1",
            "severity": "NON_BLOCKING_DEFENSE_IN_DEPTH",
            "title": "Path bindings use basename by declared protocol and concurrent external mutation remains a TOCTOU assumption",
            "observed": True,
            "sealing_blocker": False,
        },
    ]
    controls_pass = (
        matching_accepted and all(changed_hash_blocks.values()) and overwrite_archive_block and stale_v1_block
        and incomplete_block and content_hash_block and manifest_repeats_provenance and manifest_overwrite_block
        and schemas == {"question_seed_rows": 16, "question_rows": 4, "aggregate_rows": 4, "trial_rows": 320, "question_denominator": 1}
    )
    return {
        "schema": "V52_T4F1_INDEPENDENT_V2_CHECKPOINT_AGGREGATION_EVIDENCE_V1",
        "synthetic_only": True,
        "matching_provenance_accepted": matching_accepted,
        "each_changed_provenance_hash_blocked": changed_hash_blocks,
        "stale_v1_checkpoint_blocked": stale_v1_block,
        "incomplete_checkpoint_blocked": incomplete_block,
        "checkpoint_csv_hash_mismatch_blocked": content_hash_block,
        "archive_overwrite_blocked": overwrite_archive_block,
        "post_run_manifest_overwrite_blocked": manifest_overwrite_block,
        "final_manifest_repeats_provenance": manifest_repeats_provenance,
        "synthetic_aggregation_structure": schemas,
        "equal_question_weighting_code_path_exercised": True,
        "trial_rows_are_deterministic_replication_identities": True,
        "future_preregistration_must_state_replication_not_independent_samples": True,
        "active_bug_hunt_findings": findings,
        "required_controls_status": "PASS" if controls_pass else "FAIL",
        "sealing_status": "BLOCKED" if any(item["sealing_blocker"] for item in findings) else "PASS",
    }


def write_command_log() -> None:
    lines = [
        "V52 Task 4F1 V2 cold-start independent audit command log",
        "Audit date: 2026-09-01",
        "Safety harness: every subprocess command was rejected before launch if its joined argv contained a forbidden mode; the HMAC environment variable was also rejected.",
        "",
        "--mode run invocation count: 0",
        "--mode finalize invocation count: 0",
        f"{AUTH_ENV} set count: {COUNTS['hmac_env_set']}",
        "valid production authorization constructed: false",
        "real retrieval ranking performed: false",
        "retrieval-quality computed/read/reported: false/false/false",
        "candidate bytes modified: false",
        "",
    ]
    for index, item in enumerate(COMMANDS, 1):
        lines.extend([
            f"COMMAND {index}",
            "argv_json: " + json.dumps(item["command"], ensure_ascii=False),
            "cwd: " + item["cwd"],
            "returncode: " + str(item["returncode"]),
            "stdout:",
            item["stdout"].rstrip(),
            "stderr:",
            item["stderr"].rstrip(),
            "",
        ])
    (AUDIT / "COMMAND_LOG.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_hash_manifest() -> None:
    manifest_path = AUDIT / "INDEPENDENT_V2_EXECUTION_AUDIT_HASHES.json"
    files = []
    for path in sorted(AUDIT.rglob("*")):
        if not path.is_file() or path == manifest_path:
            continue
        files.append({
            "name": path.relative_to(AUDIT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })
    manifest = {
        "schema": "V52_T4F1_INDEPENDENT_V2_EXECUTION_AUDIT_HASHES_V1",
        "audit_date": "2026-09-01",
        "verdict": "BLOCKED — DO NOT SEAL / DO NOT PREREGISTER / DO NOT RUN TASK 4F1",
        "candidate_anchors": {
            "implementation_bytes": 56142,
            "implementation_sha256": EXPECTED["runner"],
            "payload_inventory_bytes": 1180,
            "payload_inventory_sha256": EXPECTED["inventory"],
            "candidate_execution_seal_bytes": 6186,
            "candidate_execution_seal_sha256": EXPECTED["candidate_seal"],
            "candidate_status": "PREPARED_NOT_INDEPENDENTLY_AUDITED",
            "authorization_key_commitment": "PENDING_HEAD_RESEARCHER_PREREGISTRATION",
        },
        "outcome_boundary": {
            "mode_run_invocation_count": 0,
            "mode_finalize_invocation_count": 0,
            "hmac_key_environment_variable_set_count": 0,
            "valid_production_authorization_constructed": False,
            "real_retrieval_ranking_performed": False,
            "retrieval_quality_computed": False,
            "retrieval_quality_read": False,
            "retrieval_quality_reported": False,
            "candidate_bytes_modified": False,
        },
        "file_count_excluding_self": len(files),
        "files": files,
        "self_reference_note": "This manifest hashes every recursive audit output except itself.",
    }
    write_json(manifest_path, manifest)


def main() -> None:
    AUDIT.mkdir(parents=True, exist_ok=True)
    os.environ.pop(AUTH_ENV, None)
    env = os.environ.copy()
    env.pop(AUTH_ENV, None)
    env.update({
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    closure = closure_and_upstream(env)
    leakage = static_leakage_and_diff()
    candidate_preflight_output = AUDIT / "INDEPENDENT_RERUN_PREFLIGHT.json"
    preflight_command = [
        str(PYTHON), "-B", str(RUNNER), "--mode", "preflight",
        "--corpus-root", str(CORPUS),
        "--beam-manifest", str(T4F0 / "pinned_tree_manifest.json"),
        "--cohort", str(REFREEZE / "estimand_primary_cohort.csv"),
        "--restricted-seal", str(REFREEZE / "CANDIDATE_SEAL.json"),
        "--protocol", str(REFREEZE / "REFREEZE_PROTOCOL.md"),
        "--dependency-lock", str(CANDIDATE / "DEPENDENCY_LOCK.txt"),
        "--execution-seal", str(CANDIDATE / "CANDIDATE_EXECUTION_SEAL.json"),
        "--preflight-output", str(candidate_preflight_output),
    ]
    preflight_result = safe_subprocess(preflight_command, cwd=REPO, env=env)
    if preflight_result.returncode != 0:
        write_command_log()
        raise RuntimeError(preflight_result.stderr or preflight_result.stdout)
    module = import_runner()
    methods = method_evidence(module)
    authorization = authorization_evidence(module)
    checkpoint = checkpoint_and_aggregation_evidence(module)
    write_json(AUDIT / "CLOSURE_EVIDENCE.json", closure)
    write_json(AUDIT / "LEAKAGE_AND_CHANGE_ISOLATION_EVIDENCE.json", leakage)
    write_json(AUDIT / "METHOD_EQUIVALENCE_EVIDENCE.json", methods)
    write_json(AUDIT / "AUTHORIZATION_CONTROL_EVIDENCE.json", authorization)
    write_json(AUDIT / "CHECKPOINT_AGGREGATION_EVIDENCE.json", checkpoint)
    write_command_log()
    summary = {
        "closure": closure["status"],
        "leakage_and_change_isolation": leakage["status"],
        "methods": methods["status"],
        "authorization": authorization["status"],
        "checkpoint_required_controls": checkpoint["required_controls_status"],
        "checkpoint_sealing_status": checkpoint["sealing_status"],
        "forbidden_invocation_counts": COUNTS,
    }
    write_json(AUDIT / "HARNESS_SUMMARY.json", summary)
    write_hash_manifest()
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
