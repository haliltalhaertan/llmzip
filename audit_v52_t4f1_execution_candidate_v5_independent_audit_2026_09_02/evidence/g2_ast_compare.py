#!/usr/bin/env python3
"""Gate 2: V4 -> V5 executable change isolation.

Compares the two candidate packages byte-wise, and AST-compares every Python payload
with docstrings stripped. Also proves the runner never imports the package checker.
"""
import ast, hashlib, json, sys
from pathlib import Path

V4 = Path(sys.argv[1]).resolve()
V5 = Path(sys.argv[2]).resolve()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class StripDocstrings(ast.NodeTransformer):
    def _strip(self, node):
        self.generic_visit(node)
        body = node.body
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
           and isinstance(body[0].value.value, str):
            node.body = body[1:] or [ast.Pass()]
        return node
    visit_Module = _strip
    visit_FunctionDef = _strip
    visit_AsyncFunctionDef = _strip
    visit_ClassDef = _strip


def normalized_ast(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tree = StripDocstrings().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.dump(tree, annotate_fields=True, include_attributes=False)


def defs(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            src = ast.dump(StripDocstrings().visit(node), include_attributes=False)
            out[node.name] = hashlib.sha256(src.encode()).hexdigest()
    return out


def module_constants(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    try:
                        out[t.id] = repr(ast.literal_eval(node.value))
                    except Exception:
                        out[t.id] = "<non-literal>:" + ast.dump(node.value, include_attributes=False)[:200]
    return out


def imports(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.add(node.module or "")
    return sorted(names)


v4_files = {p.name: p for p in V4.iterdir() if p.is_file()}
v5_files = {p.name: p for p in V5.iterdir() if p.is_file()}
report = {
    "v4_namespace": V4.name, "v5_namespace": V5.name,
    "only_in_v4": sorted(set(v4_files) - set(v5_files)),
    "only_in_v5": sorted(set(v5_files) - set(v4_files)),
    "byte_identical": [], "byte_differs": [],
}
for name in sorted(set(v4_files) & set(v5_files)):
    (report["byte_identical"] if sha(v4_files[name]) == sha(v5_files[name])
     else report["byte_differs"]).append(name)

runner = "v52_t4f1_beam_retrieval.py"
checker = "candidate_package_preflight.py"

report["runner"] = {
    "v4_sha256": sha(v4_files[runner]), "v5_sha256": sha(v5_files[runner]),
    "byte_identical": sha(v4_files[runner]) == sha(v5_files[runner]),
    "ast_identical_docstrings_stripped": normalized_ast(v4_files[runner]) == normalized_ast(v5_files[runner]),
    "v5_imports": imports(v5_files[runner]),
    "imports_package_checker": any("candidate_package_preflight" in m for m in imports(v5_files[runner]))
                               or "candidate_package_preflight" in v5_files[runner].read_text(encoding="utf-8"),
}

v4c, v5c = defs(v4_files[checker]), defs(v5_files[checker])
v4k, v5k = module_constants(v4_files[checker]), module_constants(v5_files[checker])
report["package_checker"] = {
    "v4_sha256": sha(v4_files[checker]), "v5_sha256": sha(v5_files[checker]),
    "ast_identical_docstrings_stripped": normalized_ast(v4_files[checker]) == normalized_ast(v5_files[checker]),
    "definitions_only_in_v4": sorted(set(v4c) - set(v5c)),
    "definitions_only_in_v5": sorted(set(v5c) - set(v4c)),
    "definitions_changed": sorted(k for k in set(v4c) & set(v5c) if v4c[k] != v5c[k]),
    "definitions_unchanged": sorted(k for k in set(v4c) & set(v5c) if v4c[k] == v5c[k]),
    "constants_only_in_v5": {k: v5k[k] for k in sorted(set(v5k) - set(v4k))},
    "constants_only_in_v4": {k: v4k[k] for k in sorted(set(v4k) - set(v5k))},
    "constants_changed": {k: {"v4": v4k[k], "v5": v5k[k]} for k in sorted(set(v4k) & set(v5k)) if v4k[k] != v5k[k]},
    "imported_by_runner": False,
}

# runner module constants: the numerical / scientific anchors must be identical
report["runner_module_constants_identical"] = module_constants(v4_files[runner]) == module_constants(v5_files[runner])
report["runner_module_constants"] = module_constants(v5_files[runner])
report["runner_definition_digests_identical"] = defs(v4_files[runner]) == defs(v5_files[runner])
report["runner_definition_count"] = len(defs(v5_files[runner]))

print(json.dumps(report, indent=2, sort_keys=True))
