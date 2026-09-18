#!/usr/bin/env python3
"""Reproduce V52 T4D function-source hashes from the extracted frozen script.

Algorithm (quoted from the sealed script, lines 391-392):
    def source_function_hash(fn) -> str:
        return sha256_bytes(inspect.getsource(fn).encode("utf-8"))

Equivalent stdlib fallback (no sklearn import needed) replicates
inspect.getsource: linecache.getlines + inspect.getblock + textwrap.dedent.
"""
import hashlib, importlib.util, inspect, linecache, sys, textwrap

SCRIPT = r"C:/Users/MDP/dev/llmzip-work/drive/v52_t4d_locomo_frozen_cross_benchmark.py"
EXPECT = {
    "fit_archive_representation": "48297fd495f400c02ad1a33769fd8f91d8930f6c7ff7f0e412981032d03ce564",
    "fit_input_payload": "4573ebdb2e5f04b414f110ab59ce256a225dd732a7a7aff064e29562fcbe25d4",
}

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

# --- Path 1: exact replication of the script's own routine ---------------
def source_function_hash_module(fn) -> str:
    return sha(inspect.getsource(fn).encode("utf-8"))

spec = importlib.util.spec_from_file_location("t4d_frozen", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # main() is guarded by __name__ == "__main__"

print("python", sys.version.split()[0])
for name in ("fit_archive_representation", "fit_input_payload"):
    fn = getattr(mod, name)
    h = source_function_hash_module(fn)
    src = inspect.getsource(fn)
    print(f"[module-inspect] {name}: {h} {'PASS' if h == EXPECT[name] else 'FAIL'}")
    print(f"  getsource repr: {src!r}")

# --- Path 2: byte-level stdlib replication (findsource+getblock+dedent) ---
lines = linecache.getlines(SCRIPT)
tree = None
import ast
tree = ast.parse("".join(lines))
funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
for name in ("fit_archive_representation", "fit_input_payload"):
    node = funcs[name]
    lnum = node.lineno - 1
    block = inspect.getblock(lines[lnum:])
    text = textwrap.dedent("".join(block))
    h = sha(text.encode("utf-8"))
    print(f"[stdlib-block]   {name}: start_line={node.lineno} -> {h} {'PASS' if h == EXPECT[name] else 'FAIL'}")
    print(f"  block bytes: {len(text.encode('utf-8'))}, repr head/tail: {text[:40]!r} ... {text[-40:]!r}")

# --- Path 3: hand-exact quoting of the function text per proof -----------
for name, start, end in (("fit_input_payload", 191, 193), ("fit_archive_representation", 196, 217)):
    seg = "".join(lines[start - 1:end])
    h = sha(textwrap.dedent(seg).encode("utf-8"))
    print(f"[file-lines {start}-{end}] {name}: {h} {'PASS' if h == EXPECT[name] else 'FAIL'}")