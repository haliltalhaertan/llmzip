#!/usr/bin/env python3
"""Gate 3.7: is any load-bearing constant of the runner absent from the map entirely,
and does any declared deprecated literal survive anywhere (robust search)?"""
from __future__ import annotations
import ast, json, re, sys, unicodedata
from pathlib import Path

REPO = Path("/home/user/llmzip")
CAND = REPO / "task4f1_execution_candidate_v6_2026_09_03"
src = (CAND / "v52_t4f1_beam_retrieval.py").read_text()
smap = json.loads((CAND / "NORMATIVE_SOURCE_MAP.json").read_text())
map_blob = json.dumps(smap)

# --- which module constants does any concept mention (by name or by value)? --------
tree = ast.parse(src)
consts = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        seg = ast.get_source_segment(src, node.value) or ""
        consts[node.targets[0].id] = seg

locators = " ".join(f.get("locator", "") + " " + json.dumps(f.get("value")) for f in smap["fields"])
missing = []
for name, seg in consts.items():
    try:
        val = ast.literal_eval(seg)
    except Exception:
        val = None
    def present(v):
        if isinstance(v, (list, tuple, set, frozenset)):
            return all(present(x) for x in v)
        if isinstance(v, dict):
            return all(present(x) for x in v.values())
        if v is None:
            return False
        return json.dumps(v)[1:-1] in map_blob if isinstance(v, str) else str(v) in map_blob
    named = (name in locators) or (val is not None and present(val))
    missing.append({"constant": name, "source": seg[:90], "named_or_valued_in_map": named})
undeclared = [m for m in missing if not m["named_or_valued_in_map"]]

# --- robust deprecated-literal search across the closure AND the attestation -------
def fold(t: str) -> str:
    t = unicodedata.normalize("NFKC", t)
    t = "".join(ch for ch in t if not unicodedata.category(ch) in ("Cf",))   # zero-width/format
    return re.sub(r"[^0-9A-Za-z]+", "", t).casefold()   # drop ALL non-alphanumerics, not just space

targets = [d["literal"] for d in smap["deprecated_literals"]]
manifest = json.loads((CAND / "PAYLOAD_HASHES.json").read_text())
scope = sorted({i["name"] for i in manifest["files"]} | {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"})
survivors = []
for name in scope + ["../docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json"]:
    p = (CAND / name).resolve()
    if name == "NORMATIVE_SOURCE_MAP.json":
        reg = dict(smap); reg.pop("fields", None); reg.pop("deprecated_literals", None)
        raw = json.dumps(reg, indent=2, sort_keys=True)
    else:
        try:
            raw = p.read_text(encoding="utf-8")
        except Exception:
            raw = p.read_bytes().decode("utf-8", "replace")
    hay = fold(raw)
    for lit in targets:
        if fold(lit) in hay:
            survivors.append({"file": name, "literal": lit})

out = {
    "runner_constants_total": len(consts),
    "runner_constants_not_named_or_valued_anywhere_in_map": [u["constant"] for u in undeclared],
    "undeclared_constant_detail": undeclared,
    "deprecated_literals_checked": targets,
    "scope_including_detached_attestation": scope + ["docs/v52/task4f1/V6_ACCEPTANCE_ATTESTATION_2026-09-03.json"],
    "deprecated_survivors_robust_search": survivors,
    "no_deprecated_literal_survives_in_shipped_bytes": not survivors,
}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("runner constants not represented anywhere in the map:")
for u in undeclared:
    print(f"  {u['constant']:36} = {u['source'][:70]}")
print(f"\ndeprecated literals surviving (robust search over closure + attestation): {len(survivors)}")
