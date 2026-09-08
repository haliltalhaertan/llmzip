"""Part 2: byte-verbatim capture of the residual escapes, and the interpolation-site census."""
from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import sys
import traceback
from pathlib import Path

CO = Path(sys.argv[1]).resolve()
PKG3 = CO / "drafts" / "v52" / "membership_runner_ingest_v3_2026_09_08"
PKG2 = CO / "drafts" / "v52" / "membership_runner_ingest_v2_2026_09_08"
CORE = CO / "drafts" / "v52" / "membership_impl_v3_2026_09_07"
for _p in (PKG3, PKG2, CORE):
    sys.path.insert(0, str(_p))

import membership_scaling_core as core                                 # noqa: E402
import errors, safe_report                                             # noqa: E402
import membership_runner_v3 as R3                                      # noqa: E402
import corpus_ingest_v3 as I3                                          # noqa: E402
from authoritative import accepted_configuration as accepted           # noqa: E402

CAN = {"Q": "Where did Rashid park the blue van on the night of the storm?",
       "K": "canaryKeyOdessa1987"}


def full(fn):
    out, err = io.StringIO(), io.StringIO()
    tail = ""
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:
        cur, parts = e, []
        while cur is not None:
            parts.append(f"[{type(cur).__module__}.{type(cur).__name__}] {cur}")
            nxt = cur.__cause__ or cur.__context__
            cur = nxt if nxt is not cur else None
        tail = "\n".join(parts)
    return out.getvalue() + err.getvalue() + tail


def fake_map(n_q=1):
    cohort = {f"locomo_0_qa{i}": "locomo_conv_0" for i in range(n_q)}
    return {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
            "expected_cluster_ids": ["locomo_conv_0"],
            "expected_question_to_cluster": cohort, "n_questions": len(cohort)}


print("=" * 100)
print("PART 2 - byte-verbatim residual escapes and the interpolation census")
print("=" * 100)

print("\n-- P1. verify_source_identity: a non-numeric n_questions --")
m = dict(fake_map(), n_questions=CAN["Q"])
t = full(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], m))
print("BYTE-VERBATIM SURFACE:")
print(t)
print("LEAKED:", CAN["Q"] in t)

print("\n-- P1b. the same, via a mapping key that is a float --")
t = full(lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"],
                                           dict(fake_map(), n_questions=99.5)))
print(t)

print("\n-- P1c. is verify_source_identity reachable with an UNSTAMPED mapping? --")
print("signature:", R3.verify_source_identity.__code__.co_varnames[:4])
print("does it call _check_accepted_mapping or test the stamp?",
      "_accepted_manifest_sha256" in
      Path(PKG3 / "membership_runner_v3.py").read_text(encoding="utf-8")
      .split("def verify_source_identity")[1].split("\ndef ")[0])

print("\n-- P1d. and through compute_results (i.e. behind the stamp check)? --")
m2 = dict(fake_map(), n_questions=CAN["Q"])
m2["_accepted_manifest_sha256"] = accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["blob_sha256"]
records = [{"question_id": "locomo_0_qa0", "rotation_seed": int(s), "arm": a,
            "fractional_R3": 0.5} for s in core.ROTATION_SEEDS for a in core.ARMS]
t = full(lambda: R3.compute_results(records, ["locomo_0_qa0"], ["locomo_conv_0"], m2,
                                    Path(os.devnull), benchmark=accepted.LOCOMO,
                                    scheme="question", replicates=10000))
print(t)
print("LEAKED:", CAN["Q"] in t)

print("\n-- P2. validate_identifier echoes its `kind` argument --")
t = full(lambda: R3.validate_identifier(12345, CAN["Q"], 0))
print("BYTE-VERBATIM:", t)
print("LEAKED:", CAN["Q"] in t)
print("call sites of validate_identifier inside the package:")
src = (PKG3 / "membership_runner_v3.py").read_text(encoding="utf-8")
for i, line in enumerate(src.split("\n"), 1):
    if "validate_identifier(" in line and "def " not in line:
        print(f"  {i}: {line.strip()}")

print("\n-- P3. UnsafeErrorField / counts: the kwarg KEY --")
t = full(lambda: errors.message(errors.Code.UNKNOWN_BENCHMARK, **{CAN["K"]: CAN["Q"]}))
print("BYTE-VERBATIM:", t)
t = full(lambda: safe_report.counts(**{CAN["K"]: "x"}))
print("BYTE-VERBATIM:", t)

print("\n-- P4. census: every f-string / .format / % site that could reach an exception --")


def census(path, label):
    txt = path.read_text(encoding="utf-8")
    lines = txt.split("\n")
    tree = ast.parse(txt)
    raw = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Raise):
            for x in ast.walk(n):
                if isinstance(x, ast.JoinedStr):
                    for v in x.values:
                        if isinstance(v, ast.FormattedValue):
                            raw.append((n.lineno, ast.unparse(v.value)))
    print(f"\n{label}: {len(raw)} interpolated expressions inside `raise` statements")
    for ln, expr in raw:
        safe = expr.startswith(("len(", "safe_report.", "core.")) or expr.endswith(".shape")
        print(f"  {'SAFE ' if safe else 'RAW  '} line {ln}: {expr}")


for f in ("membership_runner_v3.py", "corpus_ingest_v3.py", "errors.py", "safe_report.py",
          "authoritative/resolve_sources.py", "authoritative/accepted_configuration.py"):
    census(PKG3 / f, f)

print("\n-- P5. total raw-interpolation sites (any f-string anywhere) per module, v2 vs v3 --")
for pkg, names in ((PKG2, ("membership_runner_v2.py", "corpus_ingest_v2.py")),
                   (PKG3, ("membership_runner_v3.py", "corpus_ingest_v3.py", "errors.py",
                           "safe_report.py"))):
    for nm in names:
        txt = (pkg / nm).read_text(encoding="utf-8")
        tree = ast.parse(txt)
        n = sum(1 for x in ast.walk(tree) if isinstance(x, ast.FormattedValue))
        nr = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                nr += sum(1 for x in ast.walk(node) if isinstance(x, ast.FormattedValue))
        print(f"  {pkg.name}/{nm}: {n} interpolations total, {nr} inside a `raise`")

print("\n-- P6. does any raise site expand a DATA-DERIVED kwarg dict (**something)? --")
for f in ("membership_runner_v3.py", "corpus_ingest_v3.py", "authoritative/resolve_sources.py"):
    txt = (PKG3 / f).read_text(encoding="utf-8")
    tree = ast.parse(txt)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") in ("raise_violation",
                                                                             "message"):
            for kw in node.keywords:
                if kw.arg is None:
                    print(f"  {f}:{node.lineno}  **{ast.unparse(kw.value)}")
print("  (all others use literal keyword names)")

print("\n-- P7. claim-accuracy: the file headers --")
for f in ("membership_runner_v3.py", "corpus_ingest_v3.py"):
    print(f"  {f} line 1: {(PKG3 / f).read_text(encoding='utf-8').splitlines()[0]}")
rl = (PKG3 / "membership_runner_v3.py").read_text(encoding="utf-8").splitlines()
for i, l in enumerate(rl[:30], 1):
    if "safe_report" in l or "Every message" in l:
        print(f"  membership_runner_v3.py:{i}: {l}")
print("\nDONE")
