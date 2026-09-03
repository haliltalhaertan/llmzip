import ast, hashlib, json, subprocess, sys, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from probe_rig import stage, gate, REPO, CAND, sha256

out = {}
# ---------------- Gate 1: nested unbound file must be rejected -------------------
before = {p.relative_to(CAND).as_posix(): sha256(p) for p in sorted(CAND.rglob("*")) if p.is_file()}
root = stage()
(root / "nested").mkdir()
(root / "nested" / "unbound.txt").write_text("unbound nested payload\n")   # NOT rebound
rc, msg = gate(root)
out["gate1_nested_unbound_file_rejected"] = rc != 0
out["gate1_rejection_message"] = msg.splitlines()[-1][:200] if msg else ""
shutil.rmtree(root.parent, ignore_errors=True)
after = {p.relative_to(CAND).as_posix(): sha256(p) for p in sorted(CAND.rglob("*")) if p.is_file()}
out["gate1_real_candidate_byte_identical_after"] = (before == after)
out["gate1_recursive_file_count"] = len(after)
out["gate1_no_pycache"] = not any("__pycache__" in k for k in after)

# ---------------- Gate 2: executable delta isolation ------------------------------
V4 = REPO / "task4f1_execution_candidate_v4_2026_09_01"
V5 = REPO / "task4f1_execution_candidate_v5_2026_09_02"
runner = "v52_t4f1_beam_retrieval.py"
out["gate2_runner_sha_v4"] = sha256(V4 / runner)
out["gate2_runner_sha_v5"] = sha256(V5 / runner)
out["gate2_runner_sha_v6"] = sha256(CAND / runner)
out["gate2_runner_bytes_identical_v4_v5_v6"] = len({out["gate2_runner_sha_v4"], out["gate2_runner_sha_v5"], out["gate2_runner_sha_v6"]}) == 1

def strip_docstrings(src: str) -> str:
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body = node.body[1:] or [ast.Pass()]
    return ast.dump(ast.fix_missing_locations(tree), annotate_fields=True)

r6 = (CAND / runner).read_text()
out["gate2_runner_ast_equal_docstrings_stripped_v4_v6"] = strip_docstrings((V4/runner).read_text()) == strip_docstrings(r6)
out["gate2_runner_ast_equal_docstrings_stripped_v5_v6"] = strip_docstrings((V5/runner).read_text()) == strip_docstrings(r6)

# the only executable delta must be the out-of-band checker
changed = []
for name in sorted({p.name for p in CAND.iterdir()} | {p.name for p in V5.iterdir()}):
    a, b = V5 / name, CAND / name
    sa = sha256(a) if a.is_file() else None
    sb = sha256(b) if b.is_file() else None
    if sa != sb:
        changed.append({"file": name, "v5": sa, "v6": sb})
out["gate2_v5_to_v6_changed_files"] = changed
out["gate2_changed_executable_files"] = [c["file"] for c in changed if c["file"].endswith(".py")]

# does the runner ever import or reference the checker?
tree = ast.parse(r6)
imports = set()
for n in ast.walk(tree):
    if isinstance(n, ast.Import):
        imports.update(a.name for a in n.names)
    elif isinstance(n, ast.ImportFrom):
        imports.add(n.module or "")
out["gate2_runner_imports"] = sorted(i for i in imports if i)
out["gate2_runner_imports_checker"] = any("candidate_package_preflight" in i for i in imports)
out["gate2_runner_mentions_checker_textually"] = "candidate_package_preflight" in r6

# checker never imports the runner either
ck = ast.parse((CAND / "candidate_package_preflight.py").read_text())
ck_imports = set()
for n in ast.walk(ck):
    if isinstance(n, ast.Import): ck_imports.update(a.name for a in n.names)
    elif isinstance(n, ast.ImportFrom): ck_imports.add(n.module or "")
out["gate2_checker_imports"] = sorted(i for i in ck_imports if i)

Path(sys.argv[1]).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
for k, v in out.items():
    if k not in ("gate2_v5_to_v6_changed_files",):
        print(f"{k}: {v}")
print("\nV5 -> V6 changed files:")
for c in changed: print(f"  {c['file']}")
