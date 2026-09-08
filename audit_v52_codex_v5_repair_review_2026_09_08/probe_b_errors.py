"""Probe B -- independent adversarial probes of the Codex v5 error interface.

Items 3, 4, 5 of the audit brief. Synthetic only: no real corpus path is opened,
constructed or hashed. Every canary is < 120 characters.

Usage: python -B probe_b_errors.py <candidate package dir> <core dir>
Every probe captures: str(exc), repr(exc), the whole __cause__/__context__ chain,
stdout, stderr, and the set of files created under a fresh temp dir.
"""
from __future__ import annotations

import contextlib
import decimal
import fractions
import io
import json
import os
import sys
import tempfile
from enum import Enum
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
CORE = Path(sys.argv[2]).resolve()
sys.path[:0] = [str(PKG), str(CORE)]

import errors                                              # noqa: E402
import safe_report                                         # noqa: E402
import membership_runner_v4 as R                           # noqa: E402
import corpus_ingest_v4 as I                               # noqa: E402
import membership_scaling_core as core                     # noqa: E402

print("MODULE PROVENANCE")
for m in (errors, safe_report, R, I, core):
    print("   ", m.__name__, "->", Path(m.__file__).resolve())
print()

CANARY = "Where did Rashid park the blue van on the night of the storm?"
assert len(CANARY) < 120, len(CANARY)
TMP = Path(tempfile.mkdtemp(prefix="probe_b_")).resolve()

PASS = FAIL = INFO = 0


def files_now():
    out = set()
    for r, d, f in os.walk(TMP):
        for x in f:
            out.add(os.path.join(r, x))
    return out


def surface(fn):
    """Return (exc, value, captured-text, files-created)."""
    before = files_now()
    out, err = io.StringIO(), io.StringIO()
    exc = value = None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            value = fn()
        except BaseException as caught:                                       # noqa: BLE001
            exc = caught
    parts, seen, pending = [out.getvalue(), err.getvalue()], set(), []
    if exc is not None:
        pending.append(exc)
    while pending:
        node = pending.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        try:
            parts.append(str(node))
        except Exception as e:                                                # noqa: BLE001
            parts.append("<str failed %s>" % type(e).__name__)
        try:
            parts.append(repr(node))
        except Exception as e:                                                # noqa: BLE001
            parts.append("<repr failed %s>" % type(e).__name__)
        for nxt in (node.__cause__, node.__context__):
            if nxt is not None:
                pending.append(nxt)
    return exc, value, "\n".join(parts), files_now() - before


def clean(tag, fn, *, want_code=None, want_exc=None, allow_files=False):
    global PASS, FAIL
    exc, value, text, made = surface(fn)
    leak = CANARY in text
    codeok = want_code is None or (exc is not None and want_code in str(exc))
    excok = want_exc is None or isinstance(exc, want_exc)
    fileok = allow_files or not made
    ok = (not leak) and codeok and excok and fileok
    PASS += ok
    FAIL += (not ok)
    print(("PASS " if ok else "FAIL ") + tag)
    print("      exc=%s | %s" % (type(exc).__name__ if exc else None,
                                 (str(exc)[:160] if exc else repr(value)[:160])))
    if leak:
        print("      *** CANARY PRESENT ON CAPTURED SURFACE ***")
    if made:
        print("      files created: %s" % sorted(os.path.basename(p) for p in made))
    return exc, value, text


def info(tag, val):
    global INFO
    INFO += 1
    print("INFO " + tag + ": " + str(val)[:220])


print("=" * 100)
print("B1  ITEM 3 -- enum identity spoofs against require_identifier_kind / _safe")
print("=" * 100)


class ClassPropertySpoof:
    """The v4 defect fixture: lies about __class__ so isinstance() passes."""
    reads = 0

    @property
    def __class__(self):
        return errors.IdentifierKind

    @property
    def value(self):
        type(self).reads += 1
        return CANARY


spoof = ClassPropertySpoof()
info("B1.0 isinstance(spoof, IdentifierKind)", isinstance(spoof, errors.IdentifierKind))
info("B1.0 type(spoof) is IdentifierKind", type(spoof) is errors.IdentifierKind)
clean("B1.1 __class__ spoof refused by require_identifier_kind",
      lambda: R.require_identifier_kind(spoof), want_code="E-COH-013")
clean("B1.2 __class__ spoof refused by validate_identifier (whitespace id)",
      lambda: R.validate_identifier(" x", spoof, 0), want_code="E-COH-013")
clean("B1.3 __class__ spoof passed straight to errors._safe",
      lambda: errors.message(errors.Code.EMPTY_COHORT, kind=spoof),
      want_exc=errors.UnsafeErrorField)
info("B1.4 spoof.value read count after all three", ClassPropertySpoof.reads)


class MetaSpoof(type):
    def __instancecheck__(cls, obj):
        return True


class InstanceCheckSpoof(metaclass=MetaSpoof):
    value = CANARY


clean("B1.5 __instancecheck__ metaclass spoof refused",
      lambda: R.require_identifier_kind(InstanceCheckSpoof()), want_code="E-COH-013")

# An object whose REAL type is IdentifierKind but which is not one of the two members.
try:
    orphan = object.__new__(errors.IdentifierKind)
    orphan._value_ = CANARY
    orphan._name_ = "ORPHAN"
    info("B1.6 orphan type is IdentifierKind", type(orphan) is errors.IdentifierKind)
    clean("B1.7 non-member of the real enum type refused by require_identifier_kind",
          lambda: R.require_identifier_kind(orphan), want_code="E-COH-013")
    clean("B1.8 non-member of the real enum type refused by errors._safe",
          lambda: errors.message(errors.Code.EMPTY_COHORT, kind=orphan),
          want_exc=errors.UnsafeErrorField)
except Exception as exc:                                                      # noqa: BLE001
    info("B1.6 orphan construction failed", "%s: %s" % (type(exc).__name__, exc))

# Mutating a genuine member's .value -- does _safe echo it?
saved = errors.IdentifierKind.QUESTION_ID._value_
try:
    errors.IdentifierKind.QUESTION_ID._value_ = CANARY
    msg = errors.message(errors.Code.EMPTY_COHORT, kind=errors.IdentifierKind.QUESTION_ID)
    ok = CANARY not in msg
    PASS += ok
    FAIL += (not ok)
    print(("PASS " if ok else "FAIL ") + "B1.9 mutated member .value is NOT echoed (hardcoded label)")
    print("      msg=" + msg)
finally:
    errors.IdentifierKind.QUESTION_ID._value_ = saved

# Subclassing the enum is illegal in Python once it has members; confirm.
try:
    class Child(errors.IdentifierKind):
        EXTRA = CANARY
    info("B1.10 enum subclass with a new member", "ALLOWED -- unexpected")
except TypeError as exc:
    info("B1.10 enum subclass with a new member refused by Python", str(exc)[:120])

print()
print("=" * 100)
print("B2  ITEM 4 -- the closed Code enumeration and the closed field-name set")
print("=" * 100)


class CodeSpoof:
    @property
    def __class__(self):
        return errors.Code
    value = CANARY


clean("B2.1 spoofed Code (via __class__) refused",
      lambda: errors.message(CodeSpoof()), want_exc=errors.UnsafeErrorField)

foreign_code = Enum("ForeignCode", {"X": CANARY}).X
clean("B2.2 foreign enum as code refused",
      lambda: errors.message(foreign_code), want_exc=errors.UnsafeErrorField)
clean("B2.3 raw string as code refused",
      lambda: errors.message(CANARY), want_exc=errors.UnsafeErrorField)

try:
    code_orphan = object.__new__(errors.Code)
    code_orphan._value_ = CANARY
    clean("B2.4 non-member object of real Code type refused",
          lambda: errors.message(code_orphan), want_exc=errors.UnsafeErrorField)
except Exception as exc:                                                      # noqa: BLE001
    info("B2.4 Code orphan construction failed", "%s: %s" % (type(exc).__name__, exc))

clean("B2.5 unknown field NAME carrying the canary is refused, name not echoed",
      lambda: errors.message(errors.Code.EMPTY_COHORT, **{"z" + "q": 1}),
      want_exc=errors.UnsafeErrorField)


class StrSub(str):
    def __str__(self):
        return CANARY
    __repr__ = __str__


ss = StrSub("position")
info("B2.6a kwargs key subclass preserved?", type(dict(**{ss: 1}).popitem()[0]).__name__)
clean("B2.6 str-subclass field name (allowlisted spelling) refused",
      lambda: errors.message(errors.Code.EMPTY_COHORT, **{ss: 1}),
      want_exc=errors.UnsafeErrorField)

print()
print("=" * 100)
print("B3  ITEM 4 -- the value allowlist in errors._safe")
print("=" * 100)


class EvilInt(int):
    def __str__(self):
        return CANARY
    __repr__ = __str__

    def __format__(self, spec):
        return CANARY


class EvilFloat(float):
    def __str__(self):
        return CANARY
    __repr__ = __str__


class EvilBool(int):
    pass


for tag, val in [
        ("B3.1 int subclass", EvilInt(3)),
        ("B3.2 float subclass", EvilFloat(1.5)),
        ("B3.3 Decimal", decimal.Decimal("1.5")),
        ("B3.4 Fraction", fractions.Fraction(1, 2)),
        ("B3.5 complex", complex(1, 2)),
        ("B3.6 plain str", CANARY),
        ("B3.7 bytes", CANARY.encode()),
        ("B3.8 list", [CANARY]),
        ("B3.9 dict", {"k": CANARY}),
        ("B3.10 foreign enum", Enum("F", {"P": CANARY}).P),
        ("B3.11 IntEnum member", __import__("enum").IntEnum("G", {"P": 3}).P),
        ("B3.12 object with evil repr", type("T", (), {"__repr__": lambda s: CANARY})()),
        ("B3.13 class whose NAME is the canary", type(CANARY, (), {})()),
]:
    clean(tag + " refused as an error field", lambda v=val: errors.message(
        errors.Code.EMPTY_COHORT, position=v), want_exc=errors.UnsafeErrorField)

try:
    import numpy as _np
    for tag, val in [("B3.14 numpy int64", _np.int64(3)),
                     ("B3.15 numpy float64", _np.float64(1.5)),
                     ("B3.16 numpy bool_", _np.bool_(True))]:
        clean(tag + " refused as an error field", lambda v=val: errors.message(
            errors.Code.EMPTY_COHORT, position=v), want_exc=errors.UnsafeErrorField)
except ImportError:
    info("B3.14 numpy", "not importable")

for tag, val in [("B3.20 None", None), ("B3.21 True", True), ("B3.22 int", 7),
                 ("B3.23 float", 1.5), ("B3.24 nan", float("nan")),
                 ("B3.25 inf", float("inf"))]:
    msg = errors.message(errors.Code.EMPTY_COHORT, position=val)
    ok = msg.startswith("E-COH-018:") and CANARY not in msg
    PASS += ok
    FAIL += (not ok)
    print(("PASS " if ok else "FAIL ") + tag + " accepted as a legitimate diagnostic")
    print("      " + msg)

print()
print("=" * 100)
print("B4  ITEM 4 -- safe_report.describe / digest / positions / counts")
print("=" * 100)


class Hooked:
    calls = 0

    def __repr__(self):
        type(self).calls += 1
        return CANARY
    __str__ = __repr__

    def __len__(self):
        type(self).calls += 1
        return 99


for tag, val in [("B4.1 custom object", Hooked()),
                 ("B4.2 list containing it", [Hooked()]),
                 ("B4.3 dict value", {"k": Hooked()}),
                 ("B4.4 dict key", {Hooked(): 1}),
                 ("B4.5 nested list", [[[Hooked()]]]),
                 ("B4.6 tuple", (Hooked(),)),
                 ("B4.7 set", {1, 2}),
                 ("B4.8 str subclass", StrSub("x")),
                 ("B4.9 class named after the canary", type(CANARY, (), {})())]:
    before = Hooked.calls
    out = safe_report.describe(val)
    ok = CANARY not in out
    PASS += ok
    FAIL += (not ok)
    print(("PASS " if ok else "FAIL ") + tag + " described opaquely")
    print("      describe -> " + out + "   (repr/len hooks fired: %d)" % (Hooked.calls - before))

out = safe_report.describe_many([Hooked(), Hooked(), Hooked(), Hooked()])
ok = CANARY not in out
PASS += ok
FAIL += (not ok)
print(("PASS " if ok else "FAIL ") + "B4.10 describe_many opaque")
print("      " + out)
out = safe_report.positions([(0, Hooked()), (1, CANARY)])
ok = CANARY not in out
PASS += ok
FAIL += (not ok)
print(("PASS " if ok else "FAIL ") + "B4.11 positions opaque")
print("      " + out)

# The carried-forward residual: counts() interpolates its kwarg KEY and the type NAME.
exc, _, text, _ = surface(lambda: safe_report.counts(**{"k": type(CANARY, (), {})()}))
print("INFO B4.12 safe_report.counts type-name interpolation -> %s" % (str(exc)[:160],))
INFO += 1
exc, _, text, _ = surface(lambda: safe_report.counts(**{CANARY: "x"}))
print("INFO B4.13 safe_report.counts kwarg-key interpolation -> %s" % (str(exc)[:160],))
INFO += 1
info("B4.14 is safe_report.counts reachable from a call site?",
     "runner uses it at verify_source_identity with literal keys missing=/unexpected=")

print()
print("=" * 100)
print("B5  ITEM 5 -- does the field allowlist / scalar narrowing MISS a current call site?")
print("=" * 100)

# Every field name that appears at a literal call site was checked statically in probe A.
# Here: drive each REACHABLE refusal and confirm the intended code comes out, not
# UnsafeErrorField.
MAP = {"source_id": "synthetic", "source_sha256": "0" * 64, "benchmark": R.LOCOMO,
       "expected_cluster_ids": ["c0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "c0"}, "n_questions": 1}


def stamped(m):
    d = dict(m)
    d["_accepted_manifest_sha256"] = None
    return d


cases = [
    ("B5.1 UNKNOWN_BENCHMARK", lambda: R.require_benchmark(CANARY), "E-CFG-001"),
    ("B5.2 UNKNOWN_SCHEME", lambda: R.require_scheme(CANARY), "E-CFG-002"),
    ("B5.3 IDENTIFIER_KIND_UNKNOWN", lambda: R.require_identifier_kind(CANARY), "E-COH-013"),
    ("B5.4 UNSUPPORTED_ID_TYPE", lambda: R.validate_identifier(
        12345, R.IdentifierKind.QUESTION_ID, 3), "E-COH-014"),
    ("B5.5 MISSING_VALUE_INDICATOR", lambda: R.validate_identifier(
        "  nan ", R.IdentifierKind.QUESTION_ID, 3), "E-COH-015"),
    ("B5.6 IDENTIFIER_WHITESPACE", lambda: R.validate_identifier(
        " c1", R.IdentifierKind.CLUSTER_ID, 0), "E-COH-016"),
    ("B5.7 COLUMNS_NOT_ALIGNED", lambda: R.validate_identifier_columns(["a"], []), "E-COH-017"),
    ("B5.8 EMPTY_COHORT", lambda: R.validate_identifier_columns([], []), "E-COH-018"),
    ("B5.9 DUPLICATE_QUESTION_ID", lambda: R.validate_identifier_columns(
        ["a", "a"], ["c", "c"]), "E-COH-003"),
    ("B5.10 MANIFEST_ARGUMENTS", lambda: R.load_accepted_mapping(R.LOCOMO), "E-SRC-003"),
    ("B5.11 MANIFEST_NOT_ACCEPTED", lambda: R.load_accepted_mapping(
        R.LOCOMO, raw=b"{}"), "E-SRC-001"),
    ("B5.12 MANIFEST_FIELD_TYPE n_questions str", lambda: R.verify_source_identity(
        ["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=CANARY)), "E-SRC-012"),
    ("B5.13 MANIFEST_FIELD_TYPE n_questions float", lambda: R.verify_source_identity(
        ["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=1.0)), "E-SRC-012"),
    ("B5.14 MANIFEST_FIELD_TYPE expected map", lambda: R.verify_source_identity(
        ["locomo_0_qa0"], ["c0"], dict(MAP, expected_question_to_cluster=CANARY)), "E-SRC-012"),
    ("B5.15 MANIFEST_INTERNALLY_INCONSISTENT reason 2", lambda: R.verify_source_identity(
        ["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=5)), "E-SRC-013"),
    ("B5.16 SEED_RECORD_MALFORMED seed type", lambda: R.freeze_bootstrap_seed(
        TMP / "s1.json", CANARY, R.LOCOMO, "conversation_cluster", 2000), "E-CFG-007"),
    ("B5.17 SEED_NOT_ACCEPTED", lambda: R.freeze_bootstrap_seed(
        TMP / "s2.json", 999, R.LOCOMO, "conversation_cluster", 2000), "E-CFG-004"),
    ("B5.18 SEED_RECORD_ABSENT", lambda: R.read_bootstrap_seed(
        TMP / "nope.json", R.LOCOMO, "conversation_cluster"), "E-CFG-009"),
    ("B5.19 NO_ACCEPTED_BOOTSTRAP", lambda: R.accepted_bootstrap_for(
        R.LONGMEMEVAL, "conversation_cluster"), "E-CFG-003"),
    ("B5.20 MAPPING_NOT_FROM_ACCEPTED_PATH", lambda: I.ingest_locomo(
        TMP / "x.json", MAP, enabled=True), "E-SRC-006"),
    ("B5.21 SOURCE_ABSENT", lambda: I.verify_source_bytes(
        TMP / "absent.json", R.LOCOMO, enabled=True), "E-SRC-007"),
    ("B5.22 NO_INGESTION_PATH gate", lambda: R.run_on_real_corpus(), "E-GAT-001"),
    ("B5.23 CONTENT_POLICY long string", lambda: I.assert_content_free({"k": "x" * 200}),
     "E-OUT-003"),
    ("B5.24 EVIDENCE_STRUCTURE_UNSUPPORTED", lambda: I._normalise_evidence(3), "E-COH-012"),
    ("B5.25 EVIDENCE_ITEM_MALFORMED", lambda: I._normalise_evidence(["D1:0", 3]), "E-COH-011"),
]
for tag, fn, code in cases:
    clean(tag, fn, want_code=code)

print()
print("--- B5.30 supported-Python-API corner: an int SUBCLASS passes isinstance() gates ---")
clean("B5.30 int-subclass n_questions reaches errors._safe as `declared=`",
      lambda: R.verify_source_identity(["locomo_0_qa0"], ["c0"],
                                       dict(MAP, n_questions=EvilInt(5))),
      want_code="E-SRC-013")
clean("B5.31 int-subclass replicates in freeze_bootstrap_seed",
      lambda: R.freeze_bootstrap_seed(TMP / "s3.json", 52001107, R.LOCOMO,
                                      "conversation_cluster", EvilInt(7)),
      want_code="E-CFG-005")

print()
print("SUMMARY  PASS=%d FAIL=%d INFO=%d" % (PASS, FAIL, INFO))
print("TEMP ROOT USED:", TMP)
