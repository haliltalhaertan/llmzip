"""Probe G -- item 5, pinned down: which CURRENT call sites can the narrowed field
allowlist break, and what class of caller is needed to reach each one?

Usage: python -B probe_g_item5.py <candidate pkg> <core dir>
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
CORE = Path(sys.argv[2]).resolve()
sys.path[:0] = [str(PKG), str(CORE)]
import errors                                              # noqa: E402
import membership_runner_v4 as R                           # noqa: E402
import corpus_ingest_v4 as I                               # noqa: E402
from authoritative import accepted_configuration as accepted    # noqa: E402

CANARY = "Where did Rashid park the blue van on the night of the storm?"
TMP = Path(tempfile.mkdtemp(prefix="probe_g_")).resolve()


class IntSub(int):
    def __str__(self):
        return CANARY
    __repr__ = __str__


MAP = {"source_id": "s", "source_sha256": "0" * 64, "benchmark": R.LOCOMO,
       "expected_cluster_ids": ["c0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "c0"}, "n_questions": 1}


def run(tag, fn):
    try:
        v = fn()
        print("  %-58s -> RETURNED %s" % (tag, repr(v)[:80]))
    except BaseException as exc:                                              # noqa: BLE001
        print("  %-58s -> %s: %s" % (tag, type(exc).__name__, str(exc)[:150]))
        print("  %-58s    canary on surface: %s"
              % ("", CANARY in (str(exc) + repr(exc))))


print("G1  runner.verify_source_identity, field `declared=n_declared`")
print("    the gate is `isinstance(n_declared, int)`; errors._safe requires `type(...) is int`")
run("G1.a exact int 5 (mismatched) -> intended E-SRC-013",
    lambda: R.verify_source_identity(["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=5)))
run("G1.b int SUBCLASS 5 (mismatched)",
    lambda: R.verify_source_identity(["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=IntSub(5))))
run("G1.c int SUBCLASS 1 (matching, no error path taken)",
    lambda: R.verify_source_identity(["locomo_0_qa0"], ["c0"],
                                     dict(MAP, n_questions=IntSub(1)))["n_questions"])
run("G1.d str n_questions -> intended E-SRC-012",
    lambda: R.verify_source_identity(["locomo_0_qa0"], ["c0"], dict(MAP, n_questions=CANARY)))

print()
print("G2  ingest COHORT_SIZE_MISMATCH, field `manifest_n_questions=mapping['n_questions']`")
print("    this site has NO type gate of its own; it relies on the accepted manifest hash pin")


def synth(n_questions):
    src = TMP / "locomo10.json"
    src.write_text(json.dumps([{"sample_id": "c0", "conversation": {
        "speaker_a": "A", "speaker_b": "B",
        "session_1": [{"dia_id": "D1:0", "speaker": "A", "text": "t"}],
        "session_1_date_time": "1 Jan 2020"},
        "qa": [{"question": "q", "answer": "a", "category": 1, "evidence": ["D1:0"]}]}]),
        encoding="utf-8")
    mapping = {"source_id": "s", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
               "expected_cluster_ids": ["locomo_conv_0"],
               "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"},
               "n_questions": n_questions}
    raw = (json.dumps(mapping, indent=2) + "\n").encode()
    om = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
    os_ = dict(I.BOUND_SOURCES[accepted.LOCOMO])
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(
        om, blob_sha256=hashlib.sha256(raw).hexdigest())
    I.BOUND_SOURCES[accepted.LOCOMO] = dict(
        os_, filename=src.name, sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
        bytes=src.stat().st_size)
    try:
        loaded = R.load_accepted_mapping(accepted.LOCOMO, raw=raw)
        return I.ingest_locomo(src, loaded, enabled=True)
    finally:
        accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = om
        I.BOUND_SOURCES[accepted.LOCOMO] = os_


run("G2.a n_questions = 1 (matches)         -> ingests", lambda: bool(synth(1)))
run("G2.b n_questions = 2 (mismatch, int)   -> intended E-COH-005", lambda: synth(2))
run("G2.c n_questions = '1' (mismatch, str; a JSON-SHAPED value)", lambda: synth("1"))
run("G2.d n_questions = 1.0 (mismatch, float; JSON-shaped)", lambda: synth(1.0))
print()
print("NOTE: G2.c/G2.d require a manifest whose bytes hash to the ACCEPTED value, which the")
print("      hash pin forbids for the two real accepted manifests (n_questions = 1535 / 470,")
print("      both exact ints -- verified from the raw Git blobs in probe C, C3.7/C3.8).")
print("TEMP:", TMP)
