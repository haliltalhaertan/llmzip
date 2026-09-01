#!/usr/bin/env python3
"""Gate 5: static (AST) + runtime leakage audit, and Gate 6b cache equivalence.

Import-only harness.  The candidate namespace is never written to: the module
bytes are copied into the audit namespace, re-hashed against the sealed anchor,
and imported with bytecode writing disabled.

All runtime fixtures are wholly synthetic: invented texts, invented raw ids,
invented questions, invented gold sets.  No real archive, no real question, no
real gold, no retrieval-quality value is produced by this script.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
CAND = ROOT / "task4f1_execution_candidate_2026_08_31"
OUT = ROOT / "audit_v52_t4f1_execution_candidate_independent_audit_2026_08_31"
SRC = CAND / "v52_t4f1_beam_retrieval.py"
ANCHOR = "28735991a3d54144ec1268693e233f2fc45278049f8df7fb177d74b852bf5428"

work = OUT / "_harness"
work.mkdir(parents=True, exist_ok=True)
copy = work / "candidate_under_audit.py"
shutil.copyfile(SRC, copy)
copy_hash = hashlib.sha256(copy.read_bytes()).hexdigest()
assert copy_hash == ANCHOR, f"harness copy diverged: {copy_hash}"

report = {
    "schema": "V52_T4F1_STATIC_RUNTIME_LEAKAGE_AUDIT_V1",
    "module_sha256_under_audit": copy_hash,
    "module_sha256_matches_sealed_anchor": copy_hash == ANCHOR,
}

# =====================================================================
# STATIC AST ANALYSIS
# =====================================================================
source = SRC.read_text(encoding="utf-8")
tree = ast.parse(source)

funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

FIT_SINKS = {
    "fit_archive_representation", "fit_itq", "signed_permutation", "haar_rotation",
    "tie_priority", "priority_arrays", "transform_queries", "rank_hamming",
    "metrics_at_3", "load_archive", "question_payload", "append_trial_rows",
}


def enclosing(node):
    for name, fn in funcs.items():
        for sub in ast.walk(fn):
            if sub is node:
                return name
    return "<module>"


callsites = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        fname = None
        if isinstance(node.func, ast.Name):
            fname = node.func.id
        elif isinstance(node.func, ast.Attribute):
            fname = node.func.attr
        if fname in FIT_SINKS:
            callsites.append({
                "callee": fname,
                "caller": enclosing(node),
                "line": node.lineno,
                "args": [ast.unparse(a) for a in node.args],
                "kwargs": {k.arg: ast.unparse(k.value) for k in node.keywords if k.arg},
            })

# every call into the two SVD fits and the archive mean
svd_sites = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
            node.func.attr in {"fit_transform", "fit", "transform", "mean"}:
        svd_sites.append({
            "method": node.func.attr,
            "receiver": ast.unparse(node.func.value),
            "caller": enclosing(node),
            "line": node.lineno,
            "args": [ast.unparse(a) for a in node.args],
            "kwargs": {k.arg: ast.unparse(k.value) for k in node.keywords if k.arg},
        })

# fit_archive_representation body: which names it reads
fit_fn = funcs["fit_archive_representation"]
fit_params = [a.arg for a in fit_fn.args.args]
fit_free_names = sorted({
    n.id for n in ast.walk(fit_fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
})
fit_assigned = sorted({
    n.id for n in ast.walk(fit_fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
})
fit_external = sorted(set(fit_free_names) - set(fit_assigned) - set(fit_params))

itq_fn = funcs["fit_itq"]
itq_params = [a.arg for a in itq_fn.args.args]

FORBIDDEN_TOKENS = ["answer", "ideal", "rubric", "grade", "evaluator", "judge",
                    "difficulty", "score", "label", "source_order", "sources_order"]
token_hits = {}
for tok in FORBIDDEN_TOKENS:
    hits = [(i + 1, ln.strip()[:140]) for i, ln in enumerate(source.splitlines())
            if tok in ln.lower()]
    if hits:
        token_hits[tok] = hits

# module-level mutable state (cross-archive contamination surface)
module_state = []
for node in tree.body:
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        for t in targets:
            if isinstance(t, ast.Name):
                val = ast.unparse(node.value) if node.value is not None else ""
                mutable = isinstance(node.value, (ast.List, ast.Dict, ast.Set)) or \
                    val.startswith(("[", "{", "defaultdict", "list(", "dict(", "set("))
                module_state.append({"name": t.id, "value_expr": val[:120], "mutable": bool(mutable)})

caching_decorators = [
    {"function": name, "decorator": ast.unparse(d)}
    for name, fn in funcs.items() for d in fn.decorator_list
]

report["static"] = {
    "callsites_into_sinks": callsites,
    "svd_and_mean_callsites": svd_sites,
    "fit_archive_representation_parameters": fit_params,
    "fit_archive_representation_only_param_is_memory_texts": fit_params == ["memory_texts"],
    "fit_archive_representation_external_names": fit_external,
    "fit_archive_representation_reads_no_query_or_gold": not any(
        tok in n.lower() for n in fit_external
        for tok in ("quer", "gold", "question", "answer", "label")),
    "fit_itq_parameters": itq_params,
    "fit_itq_first_parameter_is_centered_archive": itq_params[0] == "centered_archive",
    "forbidden_token_hits": token_hits,
    "no_answer_rubric_evaluator_difficulty_tokens": not any(
        t in token_hits for t in ("answer", "ideal", "rubric", "grade", "evaluator",
                                  "judge", "difficulty", "source_order", "sources_order")),
    "module_level_assignments": module_state,
    "module_level_container_constants": [m for m in module_state if m["mutable"]],
    "module_level_containers_are_never_mutated": not [
        n for n in ast.walk(tree)
        if isinstance(n, (ast.Assign, ast.AugAssign))
        for tgt in ((n.targets if isinstance(n, ast.Assign) else [n.target]))
        if isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Name)
        and tgt.value.id in {m["name"] for m in module_state if m["mutable"]}
    ] and not [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id in {m["name"] for m in module_state if m["mutable"]}
        and n.func.attr in {"update", "append", "add", "setdefault", "pop", "clear", "extend"}
    ],
    "no_module_level_mutable_cache": all(
        m["name"] in {"ENVIRONMENT_LOCK", "THREAD_LOCK"} for m in module_state if m["mutable"]),
    "caching_decorators": caching_decorators,
    "no_lru_cache_or_memoization": not any(
        "cache" in d["decorator"].lower() for d in caching_decorators),
}

# =====================================================================
# RUNTIME INSTRUMENTED CANARY (wholly synthetic)
# =====================================================================
spec = importlib.util.spec_from_file_location("candidate_under_audit", copy)
mod = importlib.util.module_from_spec(spec)
sys.modules["candidate_under_audit"] = mod
spec.loader.exec_module(mod)
import numpy as np

TRACE: list[dict] = []
SEQ = {"n": 0}


def step():
    SEQ["n"] += 1
    return SEQ["n"]


def describe(value):
    if isinstance(value, np.ndarray):
        return {"type": "ndarray", "shape": list(value.shape), "dtype": str(value.dtype)}
    if isinstance(value, (list, tuple)):
        kinds = sorted({type(v).__name__ for v in value})
        return {"type": type(value).__name__, "len": len(value), "element_types": kinds}
    if isinstance(value, set):
        return {"type": "set", "len": len(value), "element_types": sorted({type(v).__name__ for v in value})}
    if isinstance(value, str):
        return {"type": "str", "len": len(value)}
    return {"type": type(value).__name__}


def wrap(name, fn, capture=None, post=None):
    def inner(*a, **k):
        entry = {"seq": step(), "fn": name,
                 "args": [describe(x) for x in a],
                 "kwargs": {kk: describe(vv) for kk, vv in k.items()}}
        if capture:
            entry.update(capture(a, k))
        TRACE.append(entry)
        result = fn(*a, **k)
        if post:
            post(result)
        return result
    return inner


SYNTH_QUERY_MARK = "ZZSYNTHQUERYZZ"
SYNTH_GOLD = {"90001", "90002", "90003", "90004"}

orig_fit = mod.fit_archive_representation
orig_transform = mod.transform_queries
orig_itq = mod.fit_itq


FIT_OUTPUT_HASHES: set[str] = set()


def fit_capture(a, k):
    texts = a[0] if a else k["memory_texts"]
    joined = "\n".join(texts)
    return {
        "payload_sha256": hashlib.sha256(joined.encode("utf-8")).hexdigest(),
        "contains_synthetic_query_marker": SYNTH_QUERY_MARK in joined,
        "contains_any_gold_id": any(g in joined for g in SYNTH_GOLD),
        "all_elements_are_str": all(isinstance(t, str) for t in texts),
        "all_have_role_prefix": all(t.startswith(("user: ", "assistant: ")) for t in texts),
        "first_text_prefix": texts[0][:14],
    }


def itq_capture(a, k):
    arr = a[0] if a else k["centered_archive"]
    return {
        "payload_sha256": hashlib.sha256(np.ascontiguousarray(arr).tobytes()).hexdigest(),
        "is_ndarray": isinstance(arr, np.ndarray),
        "shape": list(np.shape(arr)),
        "seed": (a[1] if len(a) > 1 else k.get("seed")),
    }


def transform_capture(a, k):
    texts = a[1] if len(a) > 1 else k["query_texts"]
    return {
        "query_count": len(texts),
        "contains_synthetic_query_marker": any(SYNTH_QUERY_MARK in t for t in texts),
    }


mod.fit_archive_representation = wrap(
    "fit_archive_representation", orig_fit, fit_capture,
    post=lambda m: FIT_OUTPUT_HASHES.add(
        hashlib.sha256(np.ascontiguousarray(m.centered96).tobytes()).hexdigest()))
mod.transform_queries = wrap("transform_queries", orig_transform, transform_capture)
mod.fit_itq = wrap("fit_itq", orig_itq, itq_capture)
mod.signed_permutation = wrap("signed_permutation", mod.signed_permutation)
mod.haar_rotation = wrap("haar_rotation", mod.haar_rotation)
mod.rank_hamming = wrap("rank_hamming", mod.rank_hamming)
mod.priority_arrays = wrap(
    "priority_arrays", mod.priority_arrays,
    lambda a, k: {"archive_id": a[0],
                  "key_count": len(a[1]),
                  "keys_sha256": hashlib.sha256(chr(10).join(a[1]).encode("utf-8")).hexdigest()})
mod.metrics_at_3 = wrap("metrics_at_3", mod.metrics_at_3)

# ---- build two disjoint synthetic archives on disk ----
corpus = work / "synthetic_corpus"
if corpus.exists():
    shutil.rmtree(corpus)

WORDS_A = ["alpha", "beacon", "cobalt", "dynamo", "ember", "fjord", "granite", "harbor",
           "indigo", "juniper", "kelvin", "lantern", "marble", "nimbus", "onyx", "pylon"]
WORDS_B = ["quartz", "raven", "silica", "tundra", "umber", "vellum", "willow", "xenon",
           "yarrow", "zephyr", "anvil", "bramble", "citrine", "dovetail", "esker", "fennel"]


def build_archive(tier, conv, words, n_units, id_base):
    d = corpus / "chats" / tier / conv
    (d / "probing_questions").mkdir(parents=True, exist_ok=True)
    messages = []
    for i in range(n_units):
        role = "user" if i % 2 == 0 else "assistant"
        body = " ".join(words[(i + j) % len(words)] + f"{(i * 7 + j * 13) % 97}"
                        for j in range(9))
        messages.append({"id": id_base + i, "role": role,
                         "content": f"synthetic {tier} unit {i} {body} topic{i % 23} cluster{i % 11}"})
    (d / "chat.json").write_text(json.dumps({"conversation": {"messages": messages}}), encoding="utf-8")
    questions = {"single-session-user": [
        {"question": f"{SYNTH_QUERY_MARK} synthetic probe {q} about {words[q % len(words)]} "
                     f"topic{q % 23} cluster{q % 11}",
         "answer": "SYNTHETIC-ANSWER-MUST-NEVER-BE-READ",
         "ideal_answer": "SYNTHETIC-IDEAL-MUST-NEVER-BE-READ",
         "rubric": "SYNTHETIC-RUBRIC-MUST-NEVER-BE-READ",
         "difficulty": "SYNTHETIC-DIFFICULTY"} for q in range(6)]}
    (d / "probing_questions" / "probing_questions.json").write_text(
        json.dumps(questions), encoding="utf-8")
    return [str(id_base + i) for i in range(n_units)]


ids_a = build_archive("100K", "synthA", WORDS_A, 150, 90001)
ids_b = build_archive("500K", "synthB", WORDS_B, 140, 70001)


def cohort_rows(tier, conv, ids, n):
    rows = []
    for q in range(n):
        gold = [ids[(q * 5 + j) % len(ids)] for j in range(1 + q % 3)]
        rows.append({
            "audit_question_id": f"{tier}::{conv}::single-session-user::{q + 1}",
            "tier": tier, "conversation_id": conv, "ability": "single-session-user",
            "gold_source_unit_count": str(len(set(gold))),
            "gold_source_ids_parsed": sorted(set(gold)),
        })
    return rows


rows_a = cohort_rows("100K", "synthA", ids_a, 4)
rows_b = cohort_rows("500K", "synthB", ids_b, 3)

res_a, meta_a = mod.evaluate_archive(corpus, "100K::synthA", rows_a)
trace_after_a = len(TRACE)
res_b, meta_b = mod.evaluate_archive(corpus, "500K::synthB", rows_b)

fit_calls = [t for t in TRACE if t["fn"] == "fit_archive_representation"]
transform_calls = [t for t in TRACE if t["fn"] == "transform_queries"]
itq_calls = [t for t in TRACE if t["fn"] == "fit_itq"]
metric_calls = [t for t in TRACE if t["fn"] == "metrics_at_3"]
rank_calls = [t for t in TRACE if t["fn"] == "rank_hamming"]
priority_calls = [t for t in TRACE if t["fn"] == "priority_arrays"]

first_metric_seq = min(t["seq"] for t in metric_calls)
first_rank_seq = min(t["seq"] for t in rank_calls)

# cache equivalence: refit the same archive independently, compare bytes
raw_a, keys_a, texts_a = mod.load_archive(corpus / "chats/100K/synthA/chat.json", "100K", "synthA")
model_1 = orig_fit(texts_a)
model_2 = orig_fit(texts_a)
refit_identical = hashlib.sha256(np.ascontiguousarray(model_1.centered96).tobytes()).hexdigest() == \
    hashlib.sha256(np.ascontiguousarray(model_2.centered96).tobytes()).hexdigest()

# per-question refit == cached single fit (query independence)
qtexts = [mod.question_payload(r, mod.load_questions(
    corpus / "chats/100K/synthA/probing_questions/probing_questions.json"))[0] for r in rows_a]
cached_q = orig_transform(model_1, qtexts)
per_question = np.vstack([orig_transform(orig_fit(texts_a), [qt]) for qt in qtexts])
cache_equivalent = bool(np.array_equal(cached_q, per_question))

# order sensitivity: a permuted archive must produce a different fit (proves order is used)
shuffled = list(reversed(texts_a))
model_shuf = orig_fit(shuffled)
order_matters = hashlib.sha256(np.ascontiguousarray(model_shuf.centered96).tobytes()).hexdigest() != \
    hashlib.sha256(np.ascontiguousarray(model_1.centered96).tobytes()).hexdigest()

report["runtime"] = {
    "synthetic_only": True,
    "archives_evaluated": ["100K::synthA", "500K::synthB"],
    "fit_call_count": len(fit_calls),
    "exactly_one_fit_per_archive": len(fit_calls) == 2,
    "fit_payloads": [{k: v for k, v in c.items() if k not in ("args", "kwargs")} for c in fit_calls],
    "fit_received_only_str_lists": all(c["args"][0]["type"] == "list" and c["all_elements_are_str"]
                                       for c in fit_calls),
    "fit_texts_all_role_prefixed": all(c["all_have_role_prefix"] for c in fit_calls),
    "fit_never_saw_query_marker": not any(c["contains_synthetic_query_marker"] for c in fit_calls),
    "fit_never_saw_gold_id": not any(c["contains_any_gold_id"] for c in fit_calls),
    "fit_arity_always_one": all(len(c["args"]) == 1 and not c["kwargs"] for c in fit_calls),
    "distinct_fit_payload_hashes": len({c["payload_sha256"] for c in fit_calls}) == 2,
    "transform_call_count": len(transform_calls),
    "transform_always_after_fit": all(
        t["seq"] > max(f["seq"] for f in fit_calls if f["seq"] < t["seq"]) for t in transform_calls),
    "query_marker_only_in_transform": all(c["contains_synthetic_query_marker"] for c in transform_calls),
    "itq_call_count": len(itq_calls),
    "itq_receives_ndarray_only": all(c["is_ndarray"] and len(c["args"]) >= 1 for c in itq_calls),
    "itq_payload_shapes": sorted({tuple(c["shape"]) for c in itq_calls}),
    "itq_payload_is_exactly_a_centered_archive_C96": all(
        c["payload_sha256"] in FIT_OUTPUT_HASHES for c in itq_calls),
    "itq_payload_shape_is_units_by_96": all(c["shape"][1] == 96 for c in itq_calls),
    "itq_distinct_payloads_equals_archive_count": len({c["payload_sha256"] for c in itq_calls}) == 2,
    "itq_seeds_observed": sorted({c["seed"] for c in itq_calls}),
    "priority_receives_full_canonical_key_list": [c["key_count"] for c in priority_calls] == [150, 140],
    "priority_key_payload_independent_of_gold": all(
        c["keys_sha256"] == hashlib.sha256(chr(10).join(
            mod.canonical_memory_key(*c["archive_id"].split("::"), rid)
            for rid in mod.load_archive(
                corpus / "chats" / c["archive_id"].split("::")[0] /
                c["archive_id"].split("::")[1] / "chat.json",
                *c["archive_id"].split("::"))[0]).encode("utf-8")).hexdigest()
        for c in priority_calls),
    "priority_is_pure_function_of_archive_id_and_key": (
        mod.tie_priority("A", "k") == mod.tie_priority("A", "k")
        and mod.tie_priority("A", "k") != mod.tie_priority("B", "k")
        and mod.tie_priority("A", "k") != mod.tie_priority("A", "k2")),
    "priority_archive_ids": sorted({c["archive_id"] for c in priority_calls}),
    "metrics_first_call_after_first_ranking": first_metric_seq > first_rank_seq,
    "gold_reaches_only_metrics_at_3": all(
        any(a["type"] == "set" for a in t["args"]) for t in metric_calls),
    "rank_hamming_call_count": len(rank_calls),
    "row_count_archive_a": len(res_a),
    "row_count_archive_a_expected": len(rows_a) * 320,
    "row_count_archive_a_ok": len(res_a) == len(rows_a) * 320,
    "row_count_archive_b_ok": len(res_b) == len(rows_b) * 320,
    "cross_archive_no_shared_fit": trace_after_a < len(TRACE) and len(fit_calls) == 2,
    "refit_byte_identical": refit_identical,
    "cached_fit_equals_per_question_refit": cache_equivalent,
    "archive_order_is_load_bearing": order_matters,
    "meta_a_centered_archive_sha256": meta_a["centered_archive_sha256"],
    "meta_b_centered_archive_sha256": meta_b["centered_archive_sha256"],
    "meta_archive_digests_differ": meta_a["centered_archive_sha256"] != meta_b["centered_archive_sha256"],
    "meta_declares_outcomes_not_printed": meta_a["outcomes_printed_to_console"] is False
    and meta_b["outcomes_printed_to_console"] is False,
    "signed_control_checks_a": meta_a["signed_control_question_seed_checks"],
    "signed_control_checks_a_expected": len(rows_a) * 5,
}

flags = {k: v for k, v in report["static"].items() if isinstance(v, bool)}
flags.update({k: v for k, v in report["runtime"].items() if isinstance(v, bool)})
report["all_static_flags_pass"] = all(v for k, v in report["static"].items() if isinstance(v, bool))
report["all_runtime_flags_pass"] = all(v for k, v in report["runtime"].items() if isinstance(v, bool))
report["status"] = "PASS" if report["all_static_flags_pass"] and report["all_runtime_flags_pass"] else "FAIL"

(OUT / "STATIC_RUNTIME_LEAKAGE_AUDIT.json").write_text(
    json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")

for k, v in sorted(flags.items()):
    if not v:
        print("FAIL FLAG:", k)
print("status:", report["status"])
print("fit calls:", len(fit_calls), "| itq calls:", len(itq_calls),
      "| rank calls:", len(rank_calls), "| metric calls:", len(metric_calls))
shutil.rmtree(corpus, ignore_errors=True)
