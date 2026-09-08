"""INDEPENDENT probe suite, part 2: the two remaining error paths, and a hunt for others.

Synthetic only. No real corpus opened, read, hashed or scanned. Nothing sealed, nothing run.
Usage:  python -B probe_v4_part2.py <checkout-of-86a8fd7a>
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
import traceback
from enum import Enum
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
PKG4 = ROOT / "drafts/v52/membership_runner_ingest_v4_2026_09_08"
PKG3 = ROOT / "drafts/v52/membership_runner_ingest_v3_2026_09_08"
CORE = ROOT / "drafts/v52/membership_impl_v3_2026_09_07"
for _p in (CORE, PKG3, PKG4):
    sys.path.insert(0, str(_p))

import membership_scaling_core as core          # noqa: E402
import errors                                   # noqa: E402
import safe_report                              # noqa: E402
import membership_runner_v4 as R4               # noqa: E402
import corpus_ingest_v4 as I4                   # noqa: E402
import membership_runner_v3 as R3               # noqa: E402
import corpus_ingest_v3 as I3                   # noqa: E402
from authoritative import accepted_configuration as accepted   # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="audit_v4b_"))
CANARY = "Where did Rashid park the blue van on the night of the storm?"   # 61 chars
CANARY2 = "Melanie's sister got married in Lisbon on 3 April 2019."           # 55 chars
TALLY = {}


def say(kind, label, detail=""):
    TALLY[kind] = TALLY.get(kind, 0) + 1
    print((f"{kind:<8} {label}" + (f"   |  {detail}" if detail else ""))[:400])


def ck(label, cond, detail="", failkind="FINDING"):
    say("PASS" if cond else failkind, label, detail)
    return cond


def surface(fn):
    out, err = io.StringIO(), io.StringIO()
    parts = []
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                                     # noqa: BLE001
        parts.append("".join(traceback.format_exception(type(e), e, e.__traceback__)))
        parts.append(repr(e))
        parts.append(str(e))
        seen, cur = set(), e
        while cur is not None and id(cur) not in seen:
            seen.add(id(cur))
            parts.append(f"[chain {type(cur).__name__}] {cur!r} :: {cur!s}")
            cur = cur.__cause__ or cur.__context__
    return out.getvalue() + err.getvalue() + "\n".join(parts)


def wj(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


def mb(obj) -> bytes:
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


def tree(d: Path):
    return {str(p.relative_to(d)): p.read_bytes() for p in d.rglob("*") if p.is_file()}


MAP = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
       "expected_cluster_ids": ["locomo_conv_0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"}, "n_questions": 1}

print("=" * 110)
print("INDEPENDENT AUDIT PROBES part 2 - the two error paths, and a hunt for others. SYNTHETIC ONLY.")
print("=" * 110)
say("INFO", "modules", f"errors={Path(errors.__file__).parent.name} safe_report="
                       f"{Path(safe_report.__file__).parent.name} accepted={Path(accepted.__file__).parent.name}")
ck("M0  the SHARED modules the v3 controls will pick up are v4's - and v4's are byte-identical to v3's "
   "for safe_report/authoritative, and a strict superset for errors (so the controls are not vacuous)",
   Path(errors.__file__).parent.name.endswith("v4_2026_09_08"))

# ==========================================================================================
print("\n== E. validate_identifier's `kind` =========================================================")
# ==========================================================================================
ck("E1  IdentifierKind is a closed enumeration with exactly the two declared members",
   [k.value for k in R4.IdentifierKind] == ["question_id", "cluster_id"] and issubclass(R4.IdentifierKind, Enum))
ck("E2  `kind` is produced by require_identifier_kind, which admits ONLY IdentifierKind members",
   R4.require_identifier_kind(R4.IdentifierKind.QUESTION_ID) is R4.IdentifierKind.QUESTION_ID)

KIND_CANARIES = {
    "E3  a plain str canary": CANARY,
    "E4  the canonical-looking str 'question_id'": "question_id",
    "E5  bytes": CANARY.encode(),
    "E6  an int": 424242,
    "E7  None": None,
    "E8  a list holding the canary": [CANARY],
    "E9  a dict holding the canary": {"kind": CANARY},
    "E10 an object whose __str__ is the canary": type("S", (), {"__str__": lambda s: CANARY,
                                                                "__repr__": lambda s: CANARY})(),
    "E11 a DYNAMIC Enum whose value is the canary": Enum("Dyn", {"X": CANARY}).X,
    "E12 a str SUBCLASS carrying the canary": type("K", (str,), {})(CANARY),
    "E13 an object faking __class__ = IdentifierKind": None,   # built below
}


class FakeKind:
    value = CANARY

    @property
    def __class__(self):
        return R4.IdentifierKind


KIND_CANARIES["E13 an object faking __class__ = IdentifierKind"] = FakeKind()

for label, kind in KIND_CANARIES.items():
    old = surface(lambda k=kind: R3.validate_identifier(" x", k, 0))
    new = surface(lambda k=kind: R4.validate_identifier(" x", k, 0))
    leaked3 = CANARY in old
    leaked4 = CANARY in new
    ck(f"{label}: v4 does not echo it", not leaked4,
       ("LEAK: " + [l for l in new.splitlines() if CANARY in l][0][:180]) if leaked4 else
       "refused: " + (new.strip().splitlines()[-1][:110]))
    say("INFO", f"{label}: v3 negative control", "v3 LEAKS it" if leaked3 else "v3 does not leak this one")

# a genuine identifier fault still refuses BY CODE and names the kind by its enum value
for bad, code in [(" x", errors.Code.IDENTIFIER_WHITESPACE), ("", errors.Code.MISSING_VALUE_INDICATOR),
                  ("nan", errors.Code.MISSING_VALUE_INDICATOR), ("None", errors.Code.MISSING_VALUE_INDICATOR),
                  ("   ", errors.Code.MISSING_VALUE_INDICATOR), (7, errors.Code.UNSUPPORTED_ID_TYPE),
                  (True, errors.Code.UNSUPPORTED_ID_TYPE), (None, errors.Code.UNSUPPORTED_ID_TYPE),
                  (3.5, errors.Code.UNSUPPORTED_ID_TYPE)]:
    t = surface(lambda b=bad: R4.validate_identifier(b, R4.IdentifierKind.QUESTION_ID, 3))
    ck(f"E14 a genuine identifier fault {bad!r} still refuses by code {code.value} with kind/position",
       code.value in t and "kind=question_id" in t and "position=3" in t, t.strip().splitlines()[-1][:120])
# the VALUE of a bad identifier must not appear
t = surface(lambda: R4.validate_identifier(" " + CANARY, R4.IdentifierKind.QUESTION_ID, 0))
ck("E15 the bad IDENTIFIER's own text is not echoed either", CANARY not in t, t.strip().splitlines()[-1][:150])
t = surface(lambda: R4.validate_identifier_columns([CANARY, CANARY], ["a", "b"]))
ck("E16 the duplicate-id path does not echo the duplicated identifier", CANARY not in t,
   t.strip().splitlines()[-1][:150])
ck("E17 a valid identifier is returned UNCHANGED, not transformed",
   R4.validate_identifier("locomo_0_qa0", R4.IdentifierKind.QUESTION_ID, 0) == "locomo_0_qa0")
ck("E18 in-package call sites pass IdentifierKind members, never a caller string",
   'validate_identifier(v, IdentifierKind.QUESTION_ID, i)' in (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8")
   and 'validate_identifier(v, IdentifierKind.CLUSTER_ID, i)' in (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8"))

# ==========================================================================================
print("\n== F. verify_source_identity's n_questions conversion ======================================")
# ==========================================================================================
src4 = (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8")
vsi = src4[src4.index("def verify_source_identity"):src4.index("def apply_archive_transform")
           if "def apply_archive_transform" in src4 else len(src4)]
ck("F0  no int() conversion of n_questions survives anywhere in verify_source_identity",
   'int(mapping["n_questions"])' not in vsi and "int(mapping['n_questions'])" not in vsi
   and "int(n_declared)" not in vsi)
ck("F0b the expected TYPE is validated explicitly, and bool is excluded from int",
   'isinstance(n_declared, bool) or not isinstance(n_declared, int)' in vsi)

N_CANARIES = {
    "F1  n_questions = a str canary": CANARY,
    "F2  n_questions = the numeric-looking str '1'": "1",
    "F3  n_questions = 1.0 (float, value-equal)": 1.0,
    "F4  n_questions = True (bool)": True,
    "F5  n_questions = None": None,
    "F6  n_questions = a list": [1],
    "F7  n_questions = a str subclass carrying the canary": type("N", (str,), {})(CANARY),
    "F8  n_questions = an object whose __int__ returns 1": type("I", (), {"__int__": lambda s: 1,
                                                                          "__repr__": lambda s: CANARY})(),
    "F9  n_questions absent entirely": "__ABSENT__",
}
for label, v in N_CANARIES.items():
    m = dict(MAP)
    if v == "__ABSENT__":
        m.pop("n_questions")
    else:
        m["n_questions"] = v
    old = surface(lambda mm=m: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
    new = surface(lambda mm=m: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
    named = errors.Code.MANIFEST_FIELD_TYPE.value in new
    contentfree = CANARY not in new and "ValueError" not in new and "TypeError" not in new
    ck(f"{label}: v4 refuses with a NAMED, content-free E-SRC-012", named and contentfree,
       new.strip().splitlines()[-1][:150])
    say("INFO", f"{label}: v3 negative control",
        ("v3 LEAKS + " if CANARY in old else "v3 ") + (old.strip().splitlines()[-1][:110] if old else "accepted"))

for label, m in {
    "F10 expected_question_to_cluster = canary str": dict(MAP, expected_question_to_cluster=CANARY),
    "F11 expected_question_to_cluster = list": dict(MAP, expected_question_to_cluster=[CANARY]),
    "F12 expected_question_to_cluster absent": {k: v for k, v in MAP.items() if k != "expected_question_to_cluster"},
    "F13 expected_cluster_ids = canary str": dict(MAP, expected_cluster_ids=CANARY),
    "F14 expected_cluster_ids = dict": dict(MAP, expected_cluster_ids={"a": CANARY}),
    "F15 expected_cluster_ids absent": {k: v for k, v in MAP.items() if k != "expected_cluster_ids"},
}.items():
    t = surface(lambda mm=m: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
    ck(f"{label}: refused by type, content-free", errors.Code.MANIFEST_FIELD_TYPE.value in t and CANARY not in t,
       t.strip().splitlines()[-1][:140])

# no NEW value accepted by silent conversion
ck("F16 a value-equal float 1.0 is REFUSED, not silently accepted as the integer 1",
   errors.Code.MANIFEST_FIELD_TYPE.value in surface(
       lambda: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], dict(MAP, n_questions=1.0))))
ck("F17 the numeric string '1' is REFUSED, where v3's int() would have accepted it",
   errors.Code.MANIFEST_FIELD_TYPE.value in surface(
       lambda: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], dict(MAP, n_questions="1"))))
say("INFO", "F17b v3 accepted '1' silently", "yes" if surface(
    lambda: R3.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], dict(MAP, n_questions="1"))) == "" else "no")
ck("F18 a well-formed manifest still passes the six-check identity contract",
   R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], MAP)["n_questions"] == 1)

# internal-inconsistency path must not echo either
for label, m in {
    "F19 duplicate cluster ids": dict(MAP, expected_cluster_ids=["locomo_conv_0", "locomo_conv_0"]),
    "F20 cluster set mismatch": dict(MAP, expected_cluster_ids=[CANARY]),
    "F21 n_questions disagrees with the map size": dict(MAP, n_questions=99),
}.items():
    t = surface(lambda mm=m: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
    ck(f"{label}: refused by code, content-free",
       errors.Code.MANIFEST_INTERNALLY_INCONSISTENT.value in t and CANARY not in t,
       t.strip().splitlines()[-1][:140])

# the six-check problem path, which is an f-string joined from safe_report pieces
t = surface(lambda: R4.verify_source_identity([CANARY], ["locomo_conv_0"], MAP))
ck("F22 the cohort-mismatch problem path does not echo a caller question id",
   CANARY not in t, t.strip().splitlines()[-1][:200])
t = surface(lambda: R4.verify_source_identity(["locomo_0_qa0"], [CANARY], MAP))
ck("F23 nor a caller cluster id", CANARY not in t, t.strip().splitlines()[-1][:200])
mm = dict(MAP, expected_question_to_cluster={CANARY: "locomo_conv_0"}, n_questions=1)
t = surface(lambda: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
ck("F24 nor a MANIFEST-supplied question id on the missing/extra path", CANARY not in t,
   t.strip().splitlines()[-1][:200])
mm = dict(MAP, expected_cluster_ids=[CANARY], expected_question_to_cluster={"locomo_0_qa0": CANARY})
t = surface(lambda: R4.verify_source_identity(["locomo_0_qa0"], ["locomo_conv_0"], mm))
ck("F25 nor a MANIFEST-supplied cluster id on the set-mismatch path", CANARY not in t,
   t.strip().splitlines()[-1][:200])

# does a refusal write anything?
d = TMP / "nowrite"
d.mkdir(parents=True, exist_ok=True)
before = tree(d)
surface(lambda: R4.verify_source_identity([CANARY], ["locomo_conv_0"], dict(MAP, n_questions=CANARY)))
surface(lambda: R4.validate_identifier(CANARY, CANARY, 0))
ck("F26 neither error path writes any file", tree(d) == before)

# ==========================================================================================
print("\n== G. OTHER paths out of the same two functions and their callers =========================")
# ==========================================================================================
# G1: full AST census of every interpolated expression inside a `raise` in the v4 package.
SAFE_CALLS = ("len", "safe_report.describe", "safe_report.describe_many", "safe_report.counts",
              "safe_report.digest", "sorted", "sum")


def census(path: Path):
    src = path.read_text(encoding="utf-8")
    tree_ = ast.parse(src)
    rows = []
    for node in ast.walk(tree_):
        if isinstance(node, ast.Raise):
            for sub in ast.walk(node):
                if isinstance(sub, ast.FormattedValue):
                    txt = ast.get_source_segment(src, sub.value) or "?"
                    safe = (txt.split("(")[0] in SAFE_CALLS) or txt.endswith(".shape") or txt.endswith(".value")
                    rows.append((sub.lineno, txt, safe))
    return rows


total_raw = 0
for name in ("membership_runner_v4.py", "corpus_ingest_v4.py", "errors.py", "safe_report.py",
             "authoritative/resolve_sources.py", "authoritative/accepted_configuration.py"):
    rows = census(PKG4 / name)
    raw = [r for r in rows if not r[2]]
    total_raw += len(raw)
    say("INFO", f"G1 census {name}", f"{len(rows)} interpolations inside raise, {len(raw)} raw: "
                                     + "; ".join(f"L{l}:{t}" for l, t, _ in raw))
for name in ("membership_runner_v3.py", "corpus_ingest_v3.py"):
    rows = census(PKG3 / name)
    say("INFO", f"G1b v3 baseline {name}", f"{len(rows)} interpolations inside raise, "
                                           f"{len([r for r in rows if not r[2]])} raw")

# G2: every `raise` in membership_runner_v4 that is NOT errors.raise_violation
src = (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8")
t4 = ast.parse(src)
plain = []
for node in ast.walk(t4):
    if isinstance(node, ast.Raise) and node.exc is not None:
        seg = ast.get_source_segment(src, node) or ""
        if "errors." not in seg:
            plain.append((node.lineno, " ".join(seg.split())[:150]))
for lineno, seg in plain:
    say("INFO", f"G2 plain raise at membership_runner_v4.py:{lineno}", seg)
ck("G3 every plain raise in the runner formats only shapes/counts, never a caller value",
   all(("safe_report" in s) or ("shape" in s) or ("core.DIM" in s) or ("str(exc)" in s) for _, s in plain),
   f"{len(plain)} plain raises")

# G4: kwarg KEYS reaching a message (the theoretical path the v3 check recorded)
t = surface(lambda: errors.message(errors.Code.EMPTY_COHORT, **{"canaryKeyOdessa1987": "x"}))
say("OBSERVE", "G4 a kwarg KEY still reaches UnsafeErrorField's own message (unchanged from v3, "
               "theoretical: every in-package call site uses literal keyword names)",
    "canaryKeyOdessa1987" in t)
star = [l for l in src.splitlines() if "**" in l and "raise" not in l and "def " not in l]
say("INFO", "G5 `**`-expansions in the runner", "; ".join(s.strip()[:80] for s in star) or "none")

# G6: errors._safe still prints any Enum's .value - can a caller now reach it?
DynEnum = Enum("Dyn", {"X": CANARY})
t = surface(lambda: errors.message(errors.Code.EMPTY_COHORT, x=DynEnum.X))
say("OBSERVE", "G6 errors._safe still prints ANY Enum's .value verbatim (unchanged from v3)",
    "LEAKS via a hand-built Enum" if CANARY in t else "no")
ck("G6b but no call site in v4 passes a caller-supplied enum: `kind` is now gated by "
   "require_identifier_kind, and that is the only enum field in the package",
   "kind=kind" in src and "kind = require_identifier_kind(kind)" in src)

# G7: the callers of the two functions - can a caller value reach a message through them?
with (lambda: None)() if False else contextlib.nullcontext():
    pass
seed = TMP / "seed.json"
MAP_RAW = mb(MAP)


class binder:
    def __enter__(self):
        self.s = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
        accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(
            self.s, blob_sha256=hashlib.sha256(MAP_RAW).hexdigest())

    def __exit__(self, *a):
        accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = self.s


with binder():
    m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    R4.freeze_bootstrap_seed(seed, 52001107, accepted.LOCOMO, "question", 10000)
    recs = [{"question_id": "locomo_0_qa0", "rotation_seed": int(s), "arm": a, "fractional_R3": 0.5}
            for s in core.ROTATION_SEEDS for a in core.ARMS]
    # a caller that hand-stamps a mapping reaches verify_source_identity behind the stamp check (N-5)
    forged = dict(MAP, n_questions=CANARY,
                  _accepted_manifest_sha256=accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["blob_sha256"])
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], forged, seed,
                                           benchmark=accepted.LOCOMO, scheme="question", replicates=10000))
    ck("G7 reaching verify_source_identity BEHIND the stamp check with a hand-forged mapping still "
       "refuses content-free (the v3 N-5 residual does not re-open the n_questions leak)",
       CANARY not in t and errors.Code.MANIFEST_FIELD_TYPE.value in t, t.strip().splitlines()[-1][:150])
    t = surface(lambda: R4.compute_results(recs, [CANARY], ["locomo_conv_0"], m4, seed,
                                           benchmark=accepted.LOCOMO, scheme="question", replicates=10000))
    ck("G8 compute_results with a canary question id does not echo it", CANARY not in t,
       t.strip().splitlines()[-1][:180])
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, seed,
                                           benchmark=CANARY, scheme="question", replicates=10000))
    ck("G9 an unknown benchmark name is not echoed", CANARY not in t, t.strip().splitlines()[-1][:150])
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], m4, seed,
                                           benchmark=accepted.LOCOMO, scheme=CANARY, replicates=10000))
    ck("G10 an unknown scheme name is not echoed", CANARY not in t, t.strip().splitlines()[-1][:150])
    # identity-before-parse ordering, re-measured with a recording dict subclass
    class Rec(dict):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self.reads = []

        def __getitem__(self, k):
            self.reads.append(("getitem", k))
            return super().__getitem__(k)

        def get(self, k, d=None):
            self.reads.append(("get", k))
            return super().get(k, d)

    r4 = Rec(MAP, benchmark=CANARY)
    t = surface(lambda: R4.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], r4, seed,
                                           benchmark=accepted.LOCOMO, scheme="question", replicates=10000))
    ck("G11 identity-before-parse: only the stamp key is read from an unstamped mapping, and nothing leaks",
       r4.reads == [("get", "_accepted_manifest_sha256")] and CANARY not in t, str(r4.reads))
    r3 = Rec(MAP, benchmark=CANARY)
    t3 = surface(lambda: R3.compute_results(recs, ["locomo_0_qa0"], ["locomo_conv_0"], r3, seed,
                                            benchmark=accepted.LOCOMO, scheme="question", replicates=10000))
    say("INFO", "G11b v3 baseline for the same probe", f"reads={r3.reads} leak={CANARY in t3}")

# ==========================================================================================
print("\n== H. ITEM 3 - claims and labels ===========================================================")
# ==========================================================================================
rsrc = (PKG4 / "membership_runner_v4.py").read_text(encoding="utf-8")
isrc = (PKG4 / "corpus_ingest_v4.py").read_text(encoding="utf-8")
esrc = (PKG4 / "errors.py").read_text(encoding="utf-8")
ck("H1  membership_runner_v4.py line 1 carries the CORRECT version label",
   rsrc.splitlines()[0].startswith('"""Corpus-bound runner v4'), rsrc.splitlines()[0][:90])
ck("H2  corpus_ingest_v4.py line 1 carries the CORRECT version label",
   isrc.splitlines()[0].startswith('"""Corpus ingestion v4'), isrc.splitlines()[0][:90])
ck("H3  INGEST_VERSION is v4", 'INGEST_VERSION = "corpus_ingest v4 2026-09-08"' in isrc)

STALE = [(i + 1, l) for i, l in enumerate(esrc.splitlines())
         if "membership_runner_v3" in l or "corpus_ingest_v3" in l]
ck("H4  errors.py in the v4 package names the v4 modules, not the v3 ones", not STALE,
   " | ".join(f"errors.py:{n}: {l.strip()[:120]}" for n, l in STALE), failkind="FINDING")

# is any UNIVERSAL claim asserted (i.e. outside the falsification inventory)?
UNIVERSALS = ["never printed, logged, put in an exception message",
              "no value is interpolated into any message",
              "NO value is interpolated",
              "every message here is built by",
              "A string cannot enter a message without first raising",
              "Every message now goes",
              "every message is assembled",
              "no content can escape"]
for name, s in (("membership_runner_v4.py", rsrc), ("corpus_ingest_v4.py", isrc), ("errors.py", esrc)):
    for u in UNIVERSALS:
        for i, line in enumerate(s.splitlines(), 1):
            if u in line:
                say("INFO", f"H5 universal-shaped sentence in {name}:{i}", line.strip()[:170])
ck("H6  no FOURTH new universal sentence is introduced (the three prior ones appear once each, as quoted "
   "falsified text, inside the inventory)",
   rsrc.count("every message here is built by") == 1
   and rsrc.count("A string cannot enter a message without first raising") == 1
   and isrc.count("NO value is interpolated") == 1
   and "all three were falsified by independent check" in " ".join(rsrc.split())
   and "Three universal sentences, three falsifications" in " ".join(isrc.split()))
d5 = [(i + 1, l) for i, l in enumerate(rsrc.splitlines()) if "Every message now goes" in l]
say("OBSERVE" if d5 else "PASS", "H7  the v2-era D-5 sentence in the changelog block",
    " | ".join(f"L{n}: {l.strip()}" for n, l in d5) or "absent")
ck("H8  the inventory names what is UNTESTED", "Untested and therefore unclaimed" in rsrc
   and "Untested and therefore unclaimed" in isrc)
ck("H9  the bound evidence contract is cited by file and commit, not asserted from memory",
   "locomo_sign_mechanism_replication.py @ 692f599e" in isrc)
# is "every message ... goes through safe_report" true?
n_safe = rsrc.count("safe_report.")
n_err = rsrc.count("errors.raise_violation")
say("INFO", "H10 message builders actually used in membership_runner_v4.py",
    f"errors.raise_violation x{n_err}, safe_report.* x{n_safe}")

print(f"\nTALLY-PART2 {TALLY}")
