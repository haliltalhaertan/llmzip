#!/usr/bin/env python3
"""Gate 3 census: for each load-bearing authoritative value declared in
NORMATIVE_SOURCE_MAP.json, find every occurrence across the complete recursively
bound payload closure and classify the containing file as AUTHORITATIVE,
TYPED_MIRROR or UNTYPED_REPETITION. Outcome-free: operates on package text only.
"""
import json, re, sys
from pathlib import Path

V5 = Path(sys.argv[1]).resolve()
smap = json.loads((V5 / "NORMATIVE_SOURCE_MAP.json").read_text(encoding="utf-8"))
manifest = json.loads((V5 / "PAYLOAD_HASHES.json").read_text(encoding="utf-8"))
bound = sorted({i["name"] for i in manifest["files"]} |
               {"PAYLOAD_HASHES.json", "CANDIDATE_EXECUTION_SEAL.json"})
texts = {}
for n in bound:
    try:
        texts[n] = (V5 / n).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        texts[n] = None

def tokens_of(value):
    """Distinctive searchable literal tokens for an authoritative value."""
    out = []
    if isinstance(value, str):
        if len(value) >= 8:
            out.append(value)
    elif isinstance(value, (int, float)):
        pass
    elif isinstance(value, list):
        for v in value:
            out.extend(tokens_of(v))
    elif isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, str) and len(v) >= 8:
                out.append(v)
            elif isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and len(x) >= 4:
                        out.append(x)
                    elif isinstance(x, int):
                        out.append(str(x))
            elif isinstance(v, int) and v > 99:
                out.append(str(v))
    return [t for t in out if len(str(t)) >= 4]

rows = []
for field in smap["fields"]:
    concept = field["concept"]
    auth = field["authoritative_path"]
    mirrors = {m["path"] for m in field.get("mirrors", [])}
    for tok in sorted(set(str(t) for t in tokens_of(field["value"]))):
        for name in bound:
            t = texts[name]
            if t is None:
                continue
            hits = [i for i, line in enumerate(t.splitlines(), 1) if tok in line]
            if not hits:
                continue
            if name == auth or auth.endswith(name):
                cls = "AUTHORITATIVE"
            elif name in mirrors:
                cls = "TYPED_MIRROR"
            else:
                cls = "UNTYPED_REPETITION"
            rows.append({"concept": concept, "token": tok, "file": name,
                         "lines": hits, "class": cls,
                         "authoritative_path": auth,
                         "declared_mirrors": sorted(mirrors)})

untyped = [r for r in rows if r["class"] == "UNTYPED_REPETITION"]
summary = {
    "bound_payload_count": len(bound),
    "bound_payloads": bound,
    "concepts_declared": len(smap["fields"]),
    "occurrences_examined": len(rows),
    "untyped_repetition_count": len(untyped),
    "untyped_repetitions": untyped,
    "all_occurrences": rows,
}
print(json.dumps(summary, indent=2, sort_keys=True))
