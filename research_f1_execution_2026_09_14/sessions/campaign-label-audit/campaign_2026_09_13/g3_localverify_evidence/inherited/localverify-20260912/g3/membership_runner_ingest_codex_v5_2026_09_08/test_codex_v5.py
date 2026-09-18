"""Implementation-team adversarial regressions. Run with python -B test_codex_v5.py.

No real source is opened, hashed or scanned. Audit events guard corpus filenames
before opening; observations describe this Python process, not arbitrary native IO.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from enum import Enum

HERE = Path(__file__).resolve().parent
TMP = Path(tempfile.mkdtemp(prefix="v52_codex_v5_synthetic_" )).resolve()
CANARY = "Where did the synthetic canary hide its purple suitcase?"
EVENTS = []
DENIED = []
EXPECTED_DENIALS = []
SOURCE_NAMES = {"locomo10.json", "longmemeval_s_cleaned.json"}
FORBIDDEN = TMP.parent / (TMP.name + "_NONEXISTENT")


def guard(event, args):
    if event not in ("open", "os.scandir", "os.listdir") or not args:
        return
    raw = args[0]
    if not isinstance(raw, (str, bytes, os.PathLike)):
        return
    path = Path(os.fsdecode(raw)).absolute()
    is_source = path.name.lower() in SOURCE_NAMES or path.name.lower().startswith("conv_") and path.suffix == ".json"
    is_blocked_tree = FORBIDDEN == path or FORBIDDEN in path.parents or any(
        part.lower() in {"beam", "dataset", "datasets"} for part in path.parts)
    if is_source or is_blocked_tree:
        EVENTS.append((event, path))
        if TMP not in path.parents or is_blocked_tree:
            DENIED.append((event, path))
            raise PermissionError("synthetic-suite scope guard refused access")


sys.addaudithook(guard)
OLD = "--old-control" in sys.argv
PACKAGE = HERE.parent / "membership_runner_ingest_v4_2026_09_08" if OLD else HERE
sys.path[:0] = [str(PACKAGE), str(HERE.parent / "membership_impl_v3_2026_09_07")]
import errors
if OLD:
    import membership_runner_v4 as R
    import corpus_ingest_v4 as I
else:
    import membership_runner_g3 as R
    import corpus_ingest_g3 as I
import safe_report
from authoritative import accepted_configuration as accepted


def capture(fn):
    out, err = io.StringIO(), io.StringIO()
    exc, value = None, None
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            value = fn()
        except BaseException as caught:
            exc = caught
    # Walk BOTH links even when 'from None' suppresses displayed context. Avoid
    # traceback source lines: their literals are test code, not emitted content.
    parts, seen = [out.getvalue(), err.getvalue()], set()
    pending = [exc] if exc is not None else []
    while pending:
        node = pending.pop()
        if id(node) in seen:
            continue
        seen.add(id(node))
        parts.extend([str(node), repr(node)])
        pending.extend(x for x in (node.__cause__, node.__context__) if x is not None)
    return exc, value, "\n".join(parts)


COUNT = 0


def check(label, condition):
    global COUNT
    assert condition, label
    COUNT += 1
    print("ok   " + label)


class FakeKind:
    value_reads = 0

    @property
    def __class__(self):
        return R.IdentifierKind

    @property
    def value(self):
        self.value_reads += 1
        return CANARY


class FakeCode:
    @property
    def __class__(self):
        return errors.Code

    value = CANARY


class EvilInt(int):
    def __str__(self):
        return CANARY

    def __repr__(self):
        return CANARY

    def __format__(self, spec):
        return CANARY


class CoercionTrap:
    calls = 0

    def __str__(self):
        self.calls += 1
        return CANARY

    __repr__ = __str__


if OLD:
    fake = FakeKind()
    e, _, emitted = capture(lambda: R.validate_identifier(" x", fake, 0))
    check("old isinstance gate is demonstrably spoofed", isinstance(fake, R.IdentifierKind) and type(fake) is not R.IdentifierKind)
    check("old identifier route emits canary", e is not None and CANARY in emitted)
    foreign = Enum("Foreign", {"PAYLOAD": CANARY}).PAYLOAD
    check("old formatter emits foreign enum", CANARY in errors.message(errors.Code.EMPTY_COHORT, position=foreign))
    check("old formatter emits numeric subclass", CANARY in errors.message(errors.Code.EMPTY_COHORT, position=EvilInt(3)))
    check("old formatter emits arbitrary field key", CANARY in errors.message(errors.Code.EMPTY_COHORT, **{CANARY: 1}))
    print("OLD CONTROL PASS")
    raise SystemExit(0)


control = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--old-control"],
                         capture_output=True, text=True, check=False)
check("isolated original-v4 controls fail the repaired contract", control.returncode == 0 and "OLD CONTROL PASS" in control.stdout)
print(control.stdout.strip())

for position in range(3):
    trap = CoercionTrap()
    evidence = ["D1:0", "D1:1"]
    evidence.insert(position, trap)
    exc, value, emitted = capture(lambda: I._normalise_evidence(evidence))
    check(f"malformed position {position} refuses without coercion or loss",
          isinstance(exc, R.DesignViolation) and value is None and "E-COH-011" in emitted
          and CANARY not in emitted and trap.calls == 0)

for source, expected in [(None, ([], 0)), ([], ([], 0)), (["D1:0", "D1:0"], (["D1:0"], 2)),
                         ([{"dia_id": 12345}], (["12345"], 1)),
                         ([{"dia_id": 1.5}], (["1.5"], 1)),
                         ([{"dia_id": ["D1:0"]}], (["['D1:0']"], 1))]:
    check("accepted producer behavior retained", I._normalise_evidence(source) == expected)

fake = FakeKind()
check("spoof fixture exercises isinstance weakness", isinstance(fake, R.IdentifierKind) and type(fake) is not R.IdentifierKind)
for identifier in (" x", "valid_id"):
    exc, _, emitted = capture(lambda: R.validate_identifier(identifier, fake, 0))
    check("spoofed kind refused before identifier processing", isinstance(exc, R.DesignViolation)
          and "E-COH-013" in emitted and "E-COH-016" not in emitted and CANARY not in emitted)
check("spoof payload never accessed", fake.value_reads == 0)
for kind in R.IdentifierKind:
    check("genuine identifier member retained", R.validate_identifier("valid_id", kind, 0) == "valid_id")

foreign = Enum("Foreign", {"PAYLOAD": CANARY}).PAYLOAD
evil_type = type(CANARY, (), {})
probes = [
    ("foreign enum", lambda: errors.message(errors.Code.EMPTY_COHORT, position=foreign)),
    ("numeric subclass", lambda: errors.message(errors.Code.EMPTY_COHORT, position=EvilInt(3))),
    ("payload class name", lambda: errors.message(errors.Code.EMPTY_COHORT, position=evil_type())),
    ("dynamic field key", lambda: errors.message(errors.Code.EMPTY_COHORT, **{CANARY: 1})),
    ("dynamic key with bad value", lambda: errors.message(errors.Code.EMPTY_COHORT, **{CANARY: CANARY})),
    ("spoofed code", lambda: errors.message(FakeCode())),
    ("enum-as-position", lambda: R.validate_identifier(" x", R.IdentifierKind.QUESTION_ID, foreign)),
    ("foreign kind", lambda: R.validate_identifier(" x", foreign, 0)),
]
for label, fn in probes:
    exc, _, emitted = capture(fn)
    check(label + " refused without content", exc is not None and CANARY not in emitted)
for value in (None, True, False, 0, 3, -4, 1.5):
    check("builtin scalar diagnostic retained", "E-COH-018" in errors.message(errors.Code.EMPTY_COHORT, position=value))
for kind in R.IdentifierKind:
    check("canonical enum diagnostic retained", "kind=" + kind.value in errors.message(errors.Code.EMPTY_COHORT, kind=kind))

trap = CoercionTrap()
for value in (trap, [trap], {"nested": trap}, evil_type()):
    exc, result, emitted = capture(lambda: safe_report.describe(value))
    check("diagnostic custom objects remain opaque", exc is None and CANARY not in result
          and CANARY not in emitted and trap.calls == 0)

# Test the guard against a unique NONEXISTENT synthetic path. The hook refuses
# before the OS open/scan; no real corpus path is used as a negative control.
for event, fn in [("open", lambda: (FORBIDDEN / "locomo10.json").read_bytes()),
                  ("os.scandir", lambda: os.scandir(FORBIDDEN)),
                  ("os.listdir", lambda: os.listdir(FORBIDDEN))]:
    before = len(DENIED)
    exc, _, emitted = capture(fn)
    check("scope guard blocks " + event, isinstance(exc, PermissionError) and len(DENIED) == before + 1)
    EXPECTED_DENIALS.append(DENIED[-1])

# Exercise real ingestion code on one source CREATED HERE, with reversible fake
# hash/manifest bindings. No bootstrap, fitting, retrieval, or real-data entrypoint.
source = TMP / "locomo10.json"
payload = [{"sample_id": "conv-0", "conversation": {"speaker_a": "A", "speaker_b": "B",
            "session_1": [{"dia_id": "D1:0", "speaker": "A", "text": CANARY}],
            "session_1_date_time": "1 Jan 2020"},
            "qa": [{"question": CANARY, "answer": CANARY, "category": 1, "evidence": ["D1:0", "D1:0"]}]}]
source.write_text(json.dumps(payload), encoding="utf-8")
mapping = {"source_id": "synthetic", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
           "expected_cluster_ids": ["locomo_conv_0"],
           "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"}, "n_questions": 1}
raw = (json.dumps(mapping, indent=2) + "\n").encode()
old_manifest = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
old_source = dict(I.BOUND_SOURCES[accepted.LOCOMO])
try:
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(old_manifest, blob_sha256=hashlib.sha256(raw).hexdigest())
    I.BOUND_SOURCES[accepted.LOCOMO] = dict(old_source, filename=source.name,
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(), bytes=source.stat().st_size)
    loaded = R.load_accepted_mapping(accepted.LOCOMO, raw=raw)
    result = I.summarise(I.ingest_locomo(source, loaded, enabled=True))
    accounting = result["evidence_accounting"]
    check("synthetic ingest retains distinct evidence counts", accounting["raw_evidence_items"] == 2
          and accounting["declared_reference_ids"] == accounting["resolved_reference_ids"] == 1
          and accounting["unresolved_reference_ids"] == 0)
finally:
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = old_manifest
    I.BOUND_SOURCES[accepted.LOCOMO] = old_source

check("source observation ledger is nonempty", any(event == "open" and path == source for event, path in EVENTS))
check("all successful observed source operations stay in synthetic root",
      all(TMP in path.parents for event, path in EVENTS if (event, path) not in EXPECTED_DENIALS))
check("no unexpected blocked access hidden by capture", DENIED == EXPECTED_DENIALS)
check("real-data execution gate remains closed", R.core.REAL_DATA_EXECUTION_ENABLED is False)
print(f"ALL PASS: {COUNT} implementation-team synthetic checks (not independent audit)")
