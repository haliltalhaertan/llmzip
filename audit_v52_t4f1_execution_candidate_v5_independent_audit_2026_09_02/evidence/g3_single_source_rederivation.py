#!/usr/bin/env python3
"""Gate 3 re-derivation, independent of the candidate's own gate output.

Items:
  3.2 one authoritative path+locator per concept; no concept declared twice
  3.4 deprecated-literal survival scan over the whole bound closure (byte-level,
      case-insensitive and whitespace-insensitive, so prose wrapping cannot hide one)
  3.5 exactness of the registry exemption
  3.6 count of normative canary definitions in EXECUTION_SPEC.md
  3.8 coverage of every concept the co-chair required, per the audit prompt
  3.3 curated census of load-bearing repetitions that are NOT typed as derived mirrors
"""
import json, re, sys
from pathlib import Path

V5 = Path(sys.argv[1]).resolve()
smap = json.loads((V5 / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
manifest = json.loads((V5 / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
BOUND = sorted({i["name"] for i in manifest["files"]} |
               {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"})
TEXT = {}
for n in BOUND:
    try:
        TEXT[n] = (V5 / n).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        TEXT[n] = None

out = {"bound_payloads": BOUND, "bound_payload_count": len(BOUND)}

# ---- 3.2 single source per concept -------------------------------------------------
concepts, dup, no_source, untyped_mirror = [], [], [], []
for f in smap["fields"]:
    c = f["concept"]
    if c in concepts:
        dup.append(c)
    concepts.append(c)
    if not f.get("authoritative_path") or not f.get("locator"):
        no_source.append(c)
    for m in f.get("mirrors", []):
        if not m.get("path") or not m.get("locator"):
            untyped_mirror.append(c)
out["item_3_2"] = {
    "concept_count": len(concepts), "concepts": concepts,
    "duplicate_concepts": dup, "concepts_without_single_source": no_source,
    "mirrors_missing_path_or_locator": untyped_mirror,
    "authoritative_paths_outside_bound_closure": sorted(
        {f["authoritative_path"] for f in smap["fields"]
         if f["authoritative_path"] not in BOUND}),
    "pass": not dup and not no_source and not untyped_mirror,
}

# ---- 3.4 robust deprecated-literal survival scan -----------------------------------
def normalize(s):
    return re.sub(r"\s+", "", s).lower()

deprecated = [e["literal"] for e in smap["deprecated_literals"]
              if e.get("must_not_appear_as_requirement", True)]
registry_stripped = dict(smap); registry_stripped.pop("deprecated_literals", None)
exempt_norm = normalize(json.dumps(registry_stripped, indent=2, sort_keys=True))

survivors_exact, survivors_robust = [], []
for name in BOUND:
    t = TEXT[name]
    if t is None:
        continue
    hay_exact = t
    hay_norm = normalize(t)
    if name == "NORMATIVE_SOURCE_MAP.json":
        hay_exact = json.dumps(registry_stripped, indent=2, sort_keys=True)
        hay_norm = exempt_norm
    for lit in deprecated:
        if lit in hay_exact:
            survivors_exact.append({"file": name, "literal": lit})
        if normalize(lit) in hay_norm:
            survivors_robust.append({"file": name, "literal": lit, "detector": "normalized"})
out["item_3_4"] = {
    "deprecated_literal_count": len(deprecated),
    "deprecated_literals": deprecated,
    "survivors_exact_substring": survivors_exact,
    "survivors_case_and_whitespace_insensitive": survivors_robust,
    "pass": not survivors_exact and not survivors_robust,
}

# ---- 3.5 exemption exactness --------------------------------------------------------
# The lawful exemption must cover ONLY the deprecated_literals block. Verify that a
# deprecated literal planted anywhere ELSE inside the map is still visible to the scan.
probe_map = json.loads(json.dumps(smap))
probe_map["purpose"] = probe_map["purpose"] + " " + deprecated[0]
probe_stripped = dict(probe_map); probe_stripped.pop("deprecated_literals", None)
probe_text = json.dumps(probe_stripped, indent=2, sort_keys=True)
out["item_3_5"] = {
    "exemption_mechanism": "whole-file re-serialisation of the map minus deprecated_literals",
    "line_level_heuristic_used": False,
    "literal_planted_elsewhere_in_map_is_still_detected": deprecated[0] in probe_text,
    "exemption_widenable_by_line_trick": False,
    "pass": deprecated[0] in probe_text,
}

# ---- 3.6 exactly one normative canary definition ------------------------------------
spec = TEXT["EXECUTION_SPEC.md"]
headings = [l for l in spec.splitlines() if l.startswith("#") and "canary" in l.lower()]
# a definition asserts acceptance criteria: a canary digest equality or a margin bound
digest_assertions = []
for i, line in enumerate(spec.splitlines(), 1):
    low = line.lower()
    if re.search(r"\b[0-9a-f]{64}\b", line) and ("canary" in low or "sha256" in low or "equals" in low):
        digest_assertions.append(i)
canary_digests = re.findall(r"\b[0-9a-f]{64}\b", spec)
out["item_3_6"] = {
    "canary_headings": headings,
    "canary_heading_count": len(headings),
    "normative_canary_definition_sections": [h for h in headings if "normative" in h.lower()],
    "sixty_four_hex_literals_in_spec": sorted(set(canary_digests)),
    "canary_sign_digests_present": sorted(
        d for d in set(canary_digests)
        if d in ("7365b6c4ba7753ee5431f89816c3151a2618f475415024d8932c839609ded5b5",
                 "5e40a5d1f0d33bf16c4005ed8aa172464dd1fb205da983f5373c9940f4ccad2b")),
    "v3_raw_float_digests_present": sorted(
        d for d in set(canary_digests)
        if d in ("25089a07760a08d816f9ae0c8af2f02b284e1217807af4d0270acbb58f580025",
                 "e422490a26d0934f31b06f808391d545e50282642af8997a24cb1d4e94fab869")),
    "exactly_one_normative_canary_definition": len(headings) == 1,
    "pass": len(headings) == 1,
}

# ---- 3.8 required-coverage table ----------------------------------------------------
REQUIRED = {
    "schema versions": ["candidate_schema_version", "authorization_schema_version",
                        "archive_result_meta_schema", "post_run_manifest_schema",
                        "implementation_preflight_schema"],
    "submission/attestation precedence": ["candidate_submission_status", "post_audit_acceptance_state"],
    "runner identity": ["v4_to_v5_runner_identity"],
    "canary algorithm, digests and margin": ["canary_algorithm_and_digests"],
    "cohort anchors": ["cohort_anchor"],
    "dependency anchor": ["dependency_lock"],
    "corpus anchors": ["upstream_corpus_anchor"],
    "methods (arm identifiers)": [],
    "seeds": ["methods_seeds_trials_topk_priority"],
    "trials": ["methods_seeds_trials_topk_priority"],
    "top-k": ["methods_seeds_trials_topk_priority"],
    "tie priority": [],
    "metrics": ["metrics_and_structural_zero_rule"],
    "structural-zero rule": ["metrics_and_structural_zero_rule"],
    "aggregation": ["aggregation_rule"],
    "authorization commitment": ["authorization_commitment_state"],
    "signed fields": ["authorization_signed_fields"],
    "outcome boundary and stop rules": ["outcome_boundary_and_stop_rule"],
}
byname = {f["concept"]: f for f in smap["fields"]}
coverage = {}
for req, mapped in REQUIRED.items():
    present = [c for c in mapped if c in byname]
    coverage[req] = {"mapped_concepts": present, "declared": bool(present)}

# runner constants that gate execution but have no declared concept
RUNNER_ANCHORS = {
    "EXPECTED_BEAM_MANIFEST_SHA256": "650cc145b853314411b1f4a9b762e6f64b33132f74f93cbb0638490319d8d318",
    "EXPECTED_RESTRICTED_SEAL_SHA256": "596c8056342e75110a940ee838cb080e9cd830f269aca0d1d87a0c4d482f859c",
    "EXPECTED_PROTOCOL_SHA256": "f75e6c93adc33b9db19be7c58240c7a0b38e3082a4f5b79ef67aad7c66493cf1",
    "EXPECTED_PARENT_COMMIT": "d3c7aa09c9553cd5ac100e668923abab602e4257",
    "TIE_PREFIX": "V52_T4F0_TIE_PRIORITY_V1",
}
declared_values = json.dumps(smap["fields"], sort_keys=True)
undeclared_anchors = {}
for const, val in RUNNER_ANCHORS.items():
    if val not in declared_values:
        where = sorted(n for n in BOUND if TEXT[n] and val in TEXT[n])
        undeclared_anchors[const] = {"value": val, "appears_in_bound_payloads": where}

out["item_3_8"] = {
    "required_coverage": coverage,
    "required_categories_undeclared": sorted(k for k, v in coverage.items() if not v["declared"]),
    "load_bearing_runner_anchors_with_no_declared_concept": undeclared_anchors,
    "pass": all(v["declared"] for v in coverage.values()) and not undeclared_anchors,
}

# ---- 3.3 curated untyped-repetition census ------------------------------------------
# Only high-distinctiveness load-bearing literals; the map itself is exempt because it is
# the registry that declares the values, and PAYLOAD_HASHES entries that merely inventory a
# file's own digest are structural rather than normative restatements.
CURATED = [
    ("candidate_schema_version", "V52_T4F1_EXECUTION_CANDIDATE_SEAL_V4"),
    ("authorization_schema_version", "V52_T4F1_RUN_AUTHORIZATION_V4"),
    ("archive_result_meta_schema", "V52_T4F1_ARCHIVE_RESULT_META_V4"),
    ("post_run_manifest_schema", "V52_T4F1_POST_RUN_MANIFEST_V4"),
    ("implementation_preflight_schema", "V52_T4F1_IMPLEMENTATION_PREFLIGHT_V4"),
    ("candidate_submission_status", "PREPARED_NOT_INDEPENDENTLY_AUDITED"),
    ("v4_to_v5_runner_identity", "f96cba2c1f10a5f873e9f6cfa395dbce5432aa9d3940791ab8aa2d2f273621f8"),
    ("cohort_anchor", "9b70e16fc1d16ebff78bbcd321f67ab53a4384746114088621c274300812519a"),
    ("dependency_lock", "86a4db447ea3f9403231f53556be19ed07763c6e2eb0de42c83807505066655e"),
    ("upstream_corpus_anchor", "3e12035532eb85768f1a7cd779832b650c4b2ef9"),
    ("authorization_commitment_state", "PENDING_HEAD_RESEARCHER_PREREGISTRATION"),
    ("methods_seeds_trials_topk_priority", "43001"),
    ("methods_seeds_trials_topk_priority", "43005"),
    ("methods_seeds_trials_topk_priority", "101, 202, 303, 404, 505"),
]
STRUCTURAL_INVENTORY = {"PAYLOAD_HASHES.json"}
untyped = []
for concept, tok in CURATED:
    f = byname[concept]
    auth = f["authoritative_path"]
    mirrors = {m["path"] for m in f.get("mirrors", [])}
    for name in BOUND:
        t = TEXT[name]
        if t is None or name == "NORMATIVE_SOURCE_MAP.json":
            continue
        lines = [i for i, l in enumerate(t.splitlines(), 1) if tok in l]
        if not lines:
            continue
        if name == auth or auth.endswith(name) or name in mirrors:
            continue
        untyped.append({
            "concept": concept, "literal": tok, "file": name, "lines": lines,
            "authoritative_path": auth, "declared_mirrors": sorted(mirrors),
            "classification": "STRUCTURAL_INVENTORY_ENTRY" if name in STRUCTURAL_INVENTORY
                              else "UNTYPED_NORMATIVE_REPETITION",
        })
normative_untyped = [u for u in untyped if u["classification"] == "UNTYPED_NORMATIVE_REPETITION"]
out["item_3_3"] = {
    "curated_literals_examined": len(CURATED),
    "untyped_repetitions_total": len(untyped),
    "untyped_normative_repetitions": len(normative_untyped),
    "detail": untyped,
    "pass": not normative_untyped,
}

out["gate_3_overall_pass"] = all(out[k]["pass"] for k in
                                 ("item_3_2", "item_3_3", "item_3_4", "item_3_5", "item_3_6", "item_3_8"))
print(json.dumps(out, indent=2, sort_keys=True))
