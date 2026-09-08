"""Probe E -- item 1 (claim accuracy) and the loose ends from probes B/D.

Usage: python -B probe_e_claims.py <candidate pkg> <core dir> <v4 base pkg>
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
CORE = Path(sys.argv[2]).resolve()
V4 = Path(sys.argv[3]).resolve()
sys.path[:0] = [str(PKG), str(CORE)]
import errors                       # noqa: E402
import safe_report                  # noqa: E402
import membership_runner_v4 as R    # noqa: E402
import corpus_ingest_v4 as I        # noqa: E402

CANARY = "Where did Rashid park the blue van on the night of the storm?"
PASS = FAIL = 0


def truth(tag, cond, note=""):
    global PASS, FAIL
    PASS += bool(cond)
    FAIL += (not cond)
    print(("PASS " if cond else "FAIL ") + tag + (("   " + str(note)[:240]) if note else ""))


rsrc = (PKG / "membership_runner_v4.py").read_text(encoding="utf-8")
isrc = (PKG / "corpus_ingest_v4.py").read_text(encoding="utf-8")
esrc = (PKG / "errors.py").read_text(encoding="utf-8")
ssrc = (PKG / "safe_report.py").read_text(encoding="utf-8")
readme = (PKG / "README.md").read_text(encoding="utf-8")

print("=" * 100)
print("E1  the two byte-verbatim FALSE sentences from the prior audit")
print("=" * 100)
for phrase in ["Every message now goes", "through `safe_report`, which reports type, shape and digest",
               "membership_runner_v3", "corpus_ingest_v3", "find none",
               "Nothing is guessed, coerced to a string or dropped",
               "coerced to a string, or dropped"]:
    hits = {n: s.count(phrase) for n, s in
            [("runner", rsrc), ("ingest", isrc), ("errors", esrc), ("safe_report", ssrc),
             ("README", readme)]}
    truth("E1 phrase %r absent from every candidate document" % phrase[:48],
          sum(hits.values()) == 0, hits)

print()
print("=" * 100)
print("E2  are the sentences the candidate DOES assert true?")
print("=" * 100)

# errors.py: 'Unknown names, foreign enums, numeric subclasses and other values receive
#             fixed UnsafeErrorField messages.'
msgs = set()
from enum import Enum, IntEnum       # noqa: E402


class Sub(int):
    pass


probes = [("unknown name", lambda: errors.message(errors.Code.EMPTY_COHORT, **{"nope": 1})),
          ("foreign enum", lambda: errors.message(errors.Code.EMPTY_COHORT,
                                                  position=Enum("F", {"P": CANARY}).P)),
          ("int subclass", lambda: errors.message(errors.Code.EMPTY_COHORT, position=Sub(1))),
          ("str value", lambda: errors.message(errors.Code.EMPTY_COHORT, position=CANARY)),
          ("bad code", lambda: errors.message(CANARY))]
for tag, fn in probes:
    try:
        fn()
        truth("E2 %s raises UnsafeErrorField" % tag, False, "did not raise")
    except errors.UnsafeErrorField as exc:
        msgs.add(str(exc))
        truth("E2 %s raises UnsafeErrorField" % tag, True, str(exc))
truth("E2 the UnsafeErrorField messages are FIXED (a closed set, no interpolation)",
      len(msgs) == 3 and all(CANARY not in m and "nope" not in m for m in msgs), sorted(msgs))

# safe_report: 'Other objects are opaque: their custom repr, type name and length hooks are
#               not called.'
CALLS = []


class Hook:
    def __repr__(self):
        CALLS.append("repr")
        return CANARY
    __str__ = __repr__

    def __len__(self):
        CALLS.append("len")
        return 7


for val in (Hook(), [Hook()], {"k": Hook()}, (Hook(),), {Hook(): 1}):
    out = safe_report.describe(val)
    assert CANARY not in out, out
truth("E2 describe(): no custom repr/len hook is called on any of five shapes",
      CALLS == [], CALLS)
truth("E2 describe(): a class whose NAME is the canary is reported as 'object'",
      "object" in safe_report.describe(type(CANARY, (), {})())
      and CANARY not in safe_report.describe(type(CANARY, (), {})()),
      safe_report.describe(type(CANARY, (), {})()))

# safe_report: 'The limit survives only in assert_content_free'
uses = [n for n, l in enumerate((isrc).splitlines(), 1) if "_MAX_STRING" in l]
truth("E2 _MAX_STRING appears only in the content policy", len(uses) <= 4, uses)
print("     _MAX_STRING lines: %s" % [isrc.splitlines()[n - 1].strip()[:80] for n in uses])

# runner: 'Source identity diagnostics and transform checks retain safe_report ...
#          these paths are not a total conversion to errors.message.'
sr_lines = [n for n, l in enumerate(rsrc.splitlines(), 1) if "safe_report." in l]
print("     safe_report call sites in the runner: lines %s" % sr_lines)
truth("E2 runner: safe_report is used, and the docstring does NOT claim universality",
      len(sr_lines) >= 4 and "not a total conversion to errors.message" in rsrc)

# README: 'resolve_sources.py is byte-identical to its predecessor'
a = hashlib.sha256((PKG / "authoritative" / "resolve_sources.py").read_bytes()).hexdigest()
b = hashlib.sha256((V4 / "authoritative" / "resolve_sources.py").read_bytes()).hexdigest()
truth("E2 README: resolve_sources.py byte-identical to the v4 predecessor", a == b, a)

# README: 'Existing authoritative/ values are unchanged except the package-version label'
ac = (PKG / "authoritative" / "accepted_configuration.py").read_text(encoding="utf-8")
av = (V4 / "authoritative" / "accepted_configuration.py").read_text(encoding="utf-8")
d = [l for l in __import__("difflib").unified_diff(av.splitlines(), ac.splitlines(), lineterm="")
     if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
truth("E2 README: accepted_configuration differs ONLY in PACKAGE_VERSION",
      len(d) == 2 and all("PACKAGE_VERSION" in x for x in d), d)

# README: 'IdentifierKind is now defined in errors.py and re-exported by the runner'
truth("E2 README: IdentifierKind defined in errors.py, re-exported by the runner",
      R.IdentifierKind is errors.IdentifierKind
      and "class IdentifierKind" in esrc and "class IdentifierKind" not in rsrc)

# README: 'Runtime version fields explicitly say Codex v5'
truth("E2 README: runtime version fields say Codex v5",
      "Codex v5" in R.RUNNER_VERSION and "Codex v5" in I.INGEST_VERSION,
      (R.RUNNER_VERSION, I.INGEST_VERSION))

print()
print("=" * 100)
print("E3  M8 follow-up: does the undetected mutant actually LEAK, or is the check merely")
print("    unable to discriminate?")
print("=" * 100)
tmp = Path(tempfile.mkdtemp(prefix="probe_e_"))
mut = tmp / "errors_isinstance.py"
mut.write_text(esrc.replace(
    "    if type(code) is not Code or not any(code is member for member in Code):",
    "    if not isinstance(code, Code):"), encoding="utf-8")
script = tmp / "run.py"
script.write_text(
    "import sys\n"
    "sys.path.insert(0, %r)\n" % str(tmp) +
    "import errors_isinstance as E\n"
    "CANARY = %r\n" % CANARY +
    "class FakeCode:\n"
    "    @property\n"
    "    def __class__(self):\n"
    "        return E.Code\n"
    "    value = CANARY\n"
    "try:\n"
    "    print('RESULT', E.message(FakeCode()))\n"
    "except BaseException as exc:\n"
    "    print('EXC', type(exc).__name__, '|', str(exc), '|', repr(exc))\n",
    encoding="utf-8")
p = subprocess.run([sys.executable, "-B", str(script)], capture_output=True, text=True)
print("     isolated mutant run ->", (p.stdout + p.stderr).strip()[:300])
truth("E3 the isinstance-only Code gate does NOT leak the canary (so the suite's "
      "'spoofed code' check passes for the wrong reason, it is not a security hole)",
      CANARY not in (p.stdout + p.stderr))

print()
print("=" * 100)
print("E4  committed evidence/ vs evidence_final/")
print("=" * 100)
for name in sorted(x.name for x in (PKG / "evidence_final").iterdir()):
    a = hashlib.sha256((PKG / "evidence" / name).read_bytes()).hexdigest()[:12]
    b = hashlib.sha256((PKG / "evidence_final" / name).read_bytes()).hexdigest()[:12]
    print("     %-46s evidence=%s evidence_final=%s %s"
          % (name, a, b, "SAME" if a == b else "DIFFER"))
ev = json.loads((PKG / "evidence" / "RESULTS.json").read_text(encoding="utf-8"))
evf = json.loads((PKG / "evidence_final" / "RESULTS.json").read_text(encoding="utf-8"))
truth("E4 both committed RESULTS.json report status PASS and no seal/run",
      ev["status"] == evf["status"] == "PASS" and not evf["seal"]
      and not evf["real_experiment_run"] and not evf["real_corpus_access_authorized"])

print()
print("=" * 100)
print("E5  FIELD_NAMES hygiene")
print("=" * 100)
used = set()
for mod in ("membership_runner_v4.py", "corpus_ingest_v4.py",
            "authoritative/resolve_sources.py"):
    tree = ast.parse((PKG / mod).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = ast.unparse(node.func)
            if fn.split(".")[-1] in ("raise_violation", "message"):
                for kw in node.keywords:
                    if kw.arg:
                        used.add(kw.arg)
# the three dynamic dicts
used |= {"crlf_to_lf_would_match", "lf_to_crlf_would_match", "got_bytes",
         "haystack_session_ids", "haystack_dates", "haystack_sessions"}
missing = sorted(used - set(errors.FIELD_NAMES))
unused = sorted(set(errors.FIELD_NAMES) - used)
truth("E5 every field name a call site can emit IS in the closed set", not missing, missing)
print("     declared-but-currently-unused names (%d): %s" % (len(unused), unused))

print()
print("SUMMARY  PASS=%d FAIL=%d" % (PASS, FAIL))
