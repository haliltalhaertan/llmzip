"""Probe A -- static census of every errors.* call site in the candidate package.

Checks:
  A1  every keyword name used at a call site is in errors.FIELD_NAMES
  A2  the static shape of each keyword VALUE expression (is it obviously a str? a
      safe_report call? len()? a literal?)
  A3  every interpolation inside every `raise` in the package
  A4  any **kwargs expansion with non-literal keys
Synthetic / static only. Reads committed source of the candidate package only.
"""
import ast
import os
import sys

ROOT = sys.argv[1]
sys.path.insert(0, ROOT)
import errors  # noqa: E402

FIELD_NAMES = errors.FIELD_NAMES
print("FIELD_NAMES count:", len(FIELD_NAMES))

MODULES = [
    "membership_runner_v4.py",
    "corpus_ingest_v4.py",
    "errors.py",
    "safe_report.py",
    os.path.join("authoritative", "resolve_sources.py"),
    os.path.join("authoritative", "accepted_configuration.py"),
]


def src(m):
    with open(os.path.join(ROOT, m), "rb") as f:
        return f.read().decode("utf-8")


def expr(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<unparse-failed>"


bad_names = []
value_shapes = {}
star_kwargs = []
call_rows = []

for m in MODULES:
    tree = ast.parse(src(m), filename=m)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = expr(node.func)
        if fn.split(".")[-1] not in ("raise_violation", "message"):
            continue
        if not (fn.startswith("errors.") or fn in ("raise_violation", "message")):
            continue
        for kw in node.keywords:
            if kw.arg is None:
                star_kwargs.append((m, node.lineno, expr(kw.value)))
                continue
            if kw.arg not in FIELD_NAMES:
                bad_names.append((m, node.lineno, kw.arg))
            v = expr(kw.value)
            shape = "other"
            if isinstance(kw.value, ast.Constant):
                shape = "const:" + type(kw.value.value).__name__
            elif isinstance(kw.value, ast.Call):
                f2 = expr(kw.value.func)
                shape = "call:" + f2
            elif isinstance(kw.value, ast.Compare):
                shape = "compare"
            elif isinstance(kw.value, (ast.BoolOp, ast.UnaryOp)):
                shape = "boolop"
            elif isinstance(kw.value, ast.Attribute):
                shape = "attr:" + v
            elif isinstance(kw.value, ast.Name):
                shape = "name:" + v
            elif isinstance(kw.value, ast.Subscript):
                shape = "subscript"
            value_shapes.setdefault(shape, []).append((m, node.lineno, kw.arg, v))
            call_rows.append((m, node.lineno, kw.arg, shape, v))

print()
print("A1  keyword names NOT in FIELD_NAMES:", bad_names if bad_names else "NONE")
print("A4  **kwargs expansions at errors.* call sites:", star_kwargs if star_kwargs else "NONE")
print()
print("A2  value-expression shapes across all errors.* call sites")
for shape in sorted(value_shapes):
    rows = value_shapes[shape]
    print(f"  {shape:38s} x{len(rows)}")

print()
print("A2b RISK: value expressions that are NOT obviously bool/int/float/None/IdentifierKind")
SAFE_CALLS = {"call:len", "call:int", "call:bool", "call:float"}
risky = []
for shape, rows in value_shapes.items():
    if shape in SAFE_CALLS:
        continue
    if shape.startswith("const:") and shape.split(":")[1] in ("bool", "int", "float", "NoneType"):
        continue
    if shape in ("compare", "boolop"):
        continue
    for r in rows:
        risky.append((shape, r))
for shape, (m, ln, arg, v) in sorted(risky):
    print(f"  {m}:{ln}  {arg} = {v}   [{shape}]")
print("  risky-count:", len(risky))

print()
print("A3  interpolations inside every `raise` statement (per module)")
for m in MODULES:
    tree = ast.parse(src(m), filename=m)
    total = 0
    raw = 0
    details = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.JoinedStr):
                for v in sub.values:
                    if isinstance(v, ast.FormattedValue):
                        total += 1
                        e = expr(v.value)
                        head = e.split("(")[0]
                        if (
                            head.startswith("len")
                            or "safe_report" in e
                            or e.endswith(".shape")
                            or e.endswith(".value")
                            or "describe" in e
                        ):
                            details.append(("cooked", node.lineno, e))
                        else:
                            raw += 1
                            details.append(("RAW", node.lineno, e))
    print(f"  {m:44s} interpolations={total} raw={raw}")
    for tag, ln, e in details:
        print(f"      {tag:6s} line {ln}: {e}")

print()
print("A5  plain (non-errors.raise_violation) raise statements in runner/ingest")
for m in ("membership_runner_v4.py", "corpus_ingest_v4.py"):
    tree = ast.parse(src(m), filename=m)
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise) and node.exc is not None:
            e = expr(node.exc)
            if "raise_violation" in e or "message(" in e:
                continue
            print(f"  {m}:{node.lineno}: raise {e[:180]}")

print()
print("A6  counts of errors.raise_violation vs safe_report.* per module")
for m in MODULES:
    s = src(m)
    print(f"  {m:44s} raise_violation={s.count('raise_violation(')}  safe_report.={s.count('safe_report.')}")
