"""Probe C -- item 5 (allowlisting vs current call sites) and item 6 (regression).

Corrects the wrong expectations in probe B (accepted schemes are "question"/"cluster").
Synthetic only. Every source, manifest and record is written by this script into a fresh
temp directory. No real corpus filename is ever opened; bound bindings are overridden
visibly and restored in a finally block.

Usage: python -B probe_c_paths.py <candidate package dir> <core dir> <repo root>
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
CORE = Path(sys.argv[2]).resolve()
REPO = Path(sys.argv[3]).resolve()
sys.path[:0] = [str(PKG), str(CORE)]

import errors                                              # noqa: E402
import safe_report                                         # noqa: E402
import membership_runner_v4 as R                           # noqa: E402
import corpus_ingest_v4 as I                               # noqa: E402
import membership_scaling_core as core                     # noqa: E402
from authoritative import accepted_configuration as accepted   # noqa: E402
from authoritative import resolve_sources                      # noqa: E402

CANARY = "Where did Rashid park the blue van on the night of the storm?"
TMP = Path(tempfile.mkdtemp(prefix="probe_c_")).resolve()
PASS = FAIL = INFO = 0


def files_now():
    out = set()
    for r, d, f in os.walk(TMP):
        for x in f:
            out.add(os.path.join(r, x))
    return out


def surface(fn):
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
        parts.extend([str(node), repr(node)])
        for nxt in (node.__cause__, node.__context__):
            if nxt is not None:
                pending.append(nxt)
    return exc, value, "\n".join(parts), files_now() - before


def clean(tag, fn, want_code=None, want_exc=None, allow_files=False):
    global PASS, FAIL
    exc, value, text, made = surface(fn)
    leak = CANARY in text
    codeok = want_code is None or (exc is not None and want_code in str(exc))
    excok = want_exc is None or isinstance(exc, want_exc)
    ok = (not leak) and codeok and excok and (allow_files or not made)
    PASS += ok
    FAIL += (not ok)
    print(("PASS " if ok else "FAIL ") + tag)
    print("      exc=%s | %s" % (type(exc).__name__ if exc else None,
                                 (str(exc)[:200] if exc else repr(value)[:200])))
    if leak:
        print("      *** CANARY PRESENT ***")
    if made and not allow_files:
        print("      files created: %s" % sorted(os.path.basename(p) for p in made))
    return exc, value, text


def truth(tag, cond, note=""):
    global PASS, FAIL
    PASS += bool(cond)
    FAIL += (not cond)
    print(("PASS " if cond else "FAIL ") + tag + (("   " + str(note)[:200]) if note else ""))


def info(tag, val):
    global INFO
    INFO += 1
    print("INFO " + tag + ": " + str(val)[:300])


print("=" * 100)
print("C1  seed / replicate paths (accepted schemes are %r)" % (accepted.SCHEMES,))
print("=" * 100)
clean("C1.1 seed of the wrong TYPE refuses by code", lambda: R.freeze_bootstrap_seed(
    TMP / "s1.json", CANARY, R.LOCOMO, "cluster", 10000), want_code="E-CFG-007")
clean("C1.2 transposed seed 52001207->52001702 refused", lambda: R.freeze_bootstrap_seed(
    TMP / "s2.json", 52001702, R.LOCOMO, "cluster", 10000), want_code="E-CFG-004")
clean("C1.3 seed 999 refused", lambda: R.freeze_bootstrap_seed(
    TMP / "s3.json", 999, R.LOCOMO, "cluster", 10000), want_code="E-CFG-004")
clean("C1.4 wrong replicate count refused", lambda: R.freeze_bootstrap_seed(
    TMP / "s4.json", 52001207, R.LOCOMO, "cluster", 2000), want_code="E-CFG-005")
clean("C1.5 (LME, cluster) has no accepted bootstrap", lambda: R.accepted_bootstrap_for(
    R.LONGMEMEVAL, "cluster"), want_code="E-CFG-003")
clean("C1.6 absent seed record refused", lambda: R.read_bootstrap_seed(
    TMP / "nope.json", R.LOCOMO, "cluster"), want_code="E-CFG-009")

rec_path = TMP / "seed_ok.json"
exc, rec, _, made = surface(lambda: R.freeze_bootstrap_seed(
    rec_path, 52001207, R.LOCOMO, "cluster", 10000))
truth("C1.7 the ACCEPTED seed freezes and writes exactly one file",
      exc is None and rec["bootstrap_seed"] == 52001207 and len(made) == 1, rec)
clean("C1.8 freeze refuses to OVERWRITE an existing record", lambda: R.freeze_bootstrap_seed(
    rec_path, 52001207, R.LOCOMO, "cluster", 10000), want_exc=Exception)
exc, back, _, _ = surface(lambda: R.read_bootstrap_seed(rec_path, R.LOCOMO, "cluster"))
truth("C1.9 the frozen record reads back", exc is None and back["bootstrap_seed"] == 52001207)

# D-3 / F20: poison the record the pipeline itself wrote and read it back.
poisoned = TMP / "seed_poison.json"
poisoned.write_text(json.dumps({"bootstrap_seed": 52001207, "benchmark": CANARY,
                                "scheme": CANARY, "replicates": 10000,
                                "frozen_before_any_result": True,
                                "runner_version": CANARY}), encoding="utf-8")
clean("C1.10 FILE-supplied canaries in the seed record never reach a message",
      lambda: R.read_bootstrap_seed(poisoned, R.LOCOMO, "cluster"), want_code="E-CFG-006")
poisoned2 = TMP / "seed_poison2.json"
poisoned2.write_text(json.dumps({"bootstrap_seed": 999, "benchmark": R.LOCOMO,
                                 "scheme": "cluster", "replicates": CANARY}), encoding="utf-8")
clean("C1.11 drifted+canaried record refuses content-free",
      lambda: R.read_bootstrap_seed(poisoned2, R.LOCOMO, "cluster"), want_code="E-CFG-008")

print()
print("=" * 100)
print("C2  the real-data gate, identity-before-parse, the cluster block, writers")
print("=" * 100)
exc, _, text, _ = surface(lambda: R.run_on_real_corpus())
truth("C2.1 gate closed by default and refuses first",
      core.REAL_DATA_EXECUTION_ENABLED is False and exc is not None
      and "not authorized" in str(exc), str(exc)[:120])


class Recorder(dict):
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.reads = []

    def get(self, key, *d):
        self.reads.append(("get", key))
        return super().get(key, *d)

    def __getitem__(self, key):
        self.reads.append(("getitem", key))
        return super().__getitem__(key)


rec = Recorder({"benchmark": R.LOCOMO, "n_questions": CANARY,
                "expected_cluster_ids": [CANARY], "source_id": CANARY,
                "source_sha256": CANARY,
                "expected_question_to_cluster": {CANARY: CANARY}})
exc, _, text, _ = surface(lambda: I._check_accepted_mapping(rec, R.LOCOMO))
truth("C2.2 identity is checked BEFORE any field is parsed",
      exc is not None and "E-SRC-006" in str(exc) and CANARY not in text
      and rec.reads == [("get", "_accepted_manifest_sha256")], rec.reads)

exc, _, text, _ = surface(lambda: R.bootstrap_conversation_clusters()
                          if hasattr(R, "bootstrap_conversation_clusters") else None)
info("C2.3 LongMemEval cluster-block text present in module",
     "N-3: the conversation-cluster bootstrap is REFUSED for LongMemEval"
     in (PKG / "membership_runner_v4.py").read_text(encoding="utf-8"))

target = TMP / "written.json"
core.safe_write_json(target, {"a": 1})
exc, _, _, _ = surface(lambda: core.safe_write_json(target, {"a": 2}))
truth("C2.4 core writer refuses to overwrite", exc is not None, str(exc)[:120])

print()
print("=" * 100)
print("C3  manifest resolution: CRLF refusal, superseded, truncation, no override")
print("=" * 100)
raw_locomo, entry = resolve_sources.resolve_accepted_manifest(REPO, R.LOCOMO)
info("C3.0 accepted LoCoMo manifest bytes (from git blob)", "%d bytes sha=%s"
     % (len(raw_locomo), hashlib.sha256(raw_locomo).hexdigest()[:16]))
truth("C3.1 accepted manifest loads through the accepted path",
      isinstance(R.load_accepted_mapping(R.LOCOMO, raw=raw_locomo), dict))
crlf = raw_locomo.replace(b"\n", b"\r\n")
exc, _, text, _ = surface(lambda: R.load_accepted_mapping(R.LOCOMO, raw=crlf))
truth("C3.2 a CRLF copy is REFUSED and diagnosed without normalising",
      exc is not None and "E-SRC-001" in str(exc) and "crlf_to_lf_would_match=True" in str(exc),
      str(exc)[:220])
exc, _, _, _ = surface(lambda: R.load_accepted_mapping(R.LOCOMO, raw=raw_locomo[:-1]))
truth("C3.3 a one-byte truncation is refused",
      exc is not None and "E-SRC-001" in str(exc), str(exc)[:160])
sup = list(accepted.SUPERSEDED_MANIFESTS.values())[0]
sup_commit = accepted.ACCEPTED_MANIFESTS[sup["benchmark"]]["commit"]
sup_raw = resolve_sources.git_blob(REPO, sup_commit, sup["path"])
truth("C3.4a the superseded blob resolves to its recorded hash",
      hashlib.sha256(sup_raw).hexdigest() == sup["blob_sha256"],
      hashlib.sha256(sup_raw).hexdigest())
exc, _, _, _ = surface(lambda: R.load_accepted_mapping(R.LONGMEMEVAL, raw=sup_raw))
truth("C3.4 a SUPERSEDED manifest is refused AS SUPERSEDED",
      exc is not None and "E-SRC-002" in str(exc), str(exc)[:160])
exc, _, _, _ = surface(lambda: R.load_accepted_mapping(R.LOCOMO, raw=raw_locomo,
                                                       path=TMP / "x"))
truth("C3.5 raw and path are mutually exclusive; no third override",
      exc is not None and "E-SRC-003" in str(exc), str(exc)[:120])
import inspect                                                                # noqa: E402
sig = inspect.signature(R.load_accepted_mapping)
truth("C3.6 no caller-supplied expected-hash argument exists",
      not any("sha" in p or "hash" in p or "expected" in p for p in sig.parameters), sig)

lme_raw, _ = resolve_sources.resolve_accepted_manifest(REPO, R.LONGMEMEVAL)
lme_map = R.load_accepted_mapping(R.LONGMEMEVAL, raw=lme_raw)
loc_map = R.load_accepted_mapping(R.LOCOMO, raw=raw_locomo)
info("C3.7 accepted cohort shapes (manifest metadata only, no corpus)",
     "LoCoMo n_questions=%s clusters=%s | LME n_questions=%s clusters=%s"
     % (loc_map["n_questions"], len(loc_map["expected_cluster_ids"]),
        lme_map["n_questions"], len(lme_map["expected_cluster_ids"])))
truth("C3.8 cohort semantics unchanged: 1535 questions / 10 clusters and 470 questions",
      loc_map["n_questions"] == 1535 and len(loc_map["expected_cluster_ids"]) == 10
      and lme_map["n_questions"] == 470)

print()
print("=" * 100)
print("C4  evidence normalisation -- valid empty / malformed item / unsupported structure")
print("=" * 100)
producer_cases = [
    (None, ([], 0)), ([], ([], 0)), ((), ([], 0)),
    ("D1:0", (["D1:0"], 1)),
    ("see D1:0 and also D2:3", (["D1:0", "D2:3"], 1)),
    ("not-an-id-shape", (["not-an-id-shape"], 1)),
    (["D1:0", "D1:0"], (["D1:0"], 2)),
    (("D1:0", "D2:1"), (["D1:0", "D2:1"], 2)),
    ([{"dia_id": "D1:0"}], (["D1:0"], 1)),
    ([{"id": "D1:0"}], (["D1:0"], 1)),
    ([{"dia_id": "D1:0", "id": "D9:9"}], (["D1:0"], 1)),
    ([{"dia_id": 12345}], (["12345"], 1)),
    ([{"dia_id": 1.5}], (["1.5"], 1)),
    ([{"dia_id": ["D1:0"]}], (["['D1:0']"], 1)),
]
for src, want in producer_cases:
    got = I._normalise_evidence(src)
    truth("C4 accepted shape %r -> %r" % (src, want), got == want, got)


class Trap:
    calls = 0

    def __str__(self):
        type(self).calls += 1
        return CANARY
    __repr__ = __str__


class DictTrap(dict):
    def get(self, k, *d):
        return CANARY


malformed = [
    ("first", [Trap(), "D1:0"]), ("middle", ["D1:0", Trap(), "D2:0"]),
    ("last", ["D1:0", Trap()]),
    ("nested list", ["D1:0", ["D2:0"]]), ("nested tuple", ["D1:0", ("D2:0",)]),
    ("int item", ["D1:0", 3]), ("bool item", ["D1:0", True]),
    ("None item", ["D1:0", None]), ("bytes item", ["D1:0", b"D2:0"]),
    ("nan item", ["D1:0", float("nan")]), ("set item", ["D1:0", {1}]),
    ("object item", ["D1:0", object()]),
    ("dict no ids", ["D1:0", {"x": CANARY}]),
    ("dia_id empty", [{"dia_id": ""}]), ("dia_id None", [{"dia_id": None}]),
    ("dia_id 0", [{"dia_id": 0}]), ("dia_id False", [{"dia_id": False}]),
    ("dia_id []", [{"dia_id": []}]), ("id empty", [{"id": ""}]),
]
Trap.calls = 0
for tag, val in malformed:
    clean("C4.M %s -> named refusal, no coercion" % tag,
          lambda v=val: I._normalise_evidence(v), want_code="E-COH-011")
truth("C4.M0 no __str__/__repr__ hook was called on a malformed item", Trap.calls == 0,
      Trap.calls)

unsupported = [3, 3.5, True, b"x", {1}, object(), {"dia_id": "D1:0"}, DictTrap(),
               (x for x in []), float("nan")]
for val in unsupported:
    clean("C4.S %s -> unsupported STRUCTURE" % type(val).__name__,
          lambda v=val: I._normalise_evidence(v), want_code="E-COH-012")

print()
print("=" * 100)
print("C5  end-to-end LoCoMo ingest on a fully canaried SYNTHETIC source")
print("=" * 100)


def synth_source(path, evidence):
    payload = [{"sample_id": "conv-0",
                "conversation": {"speaker_a": CANARY, "speaker_b": CANARY,
                                 "session_1": [{"dia_id": "D1:0", "speaker": CANARY,
                                                "text": CANARY},
                                               {"dia_id": "D1:1", "speaker": CANARY,
                                                "text": CANARY}],
                                 "session_1_date_time": "1 Jan 2020"},
                "qa": [{"question": CANARY, "answer": CANARY, "category": 1,
                        "evidence": evidence}]}]
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def with_synth_bindings(evidence, fn_name="ok", n_questions=1):
    src = synth_source(TMP / ("locomo10.json"), evidence)
    mapping = {"source_id": "synthetic", "source_sha256": "0" * 64,
               "benchmark": accepted.LOCOMO, "expected_cluster_ids": ["locomo_conv_0"],
               "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"},
               "n_questions": n_questions}
    raw = (json.dumps(mapping, indent=2) + "\n").encode()
    old_m = dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
    old_s = dict(I.BOUND_SOURCES[accepted.LOCOMO])
    accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = dict(
        old_m, blob_sha256=hashlib.sha256(raw).hexdigest())
    I.BOUND_SOURCES[accepted.LOCOMO] = dict(
        old_s, filename=src.name, sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
        bytes=src.stat().st_size)
    try:
        loaded = R.load_accepted_mapping(accepted.LOCOMO, raw=raw)
        return I.ingest_locomo(src, loaded, enabled=True)
    finally:
        accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO] = old_m
        I.BOUND_SOURCES[accepted.LOCOMO] = old_s


exc, out, text, _ = surface(lambda: with_synth_bindings(["D1:0", "D1:0"]))
truth("C5.1 happy path ingests with no leak on stdout/stderr", exc is None and CANARY not in text)
if out is not None:
    acc = I.summarise(out)["evidence_accounting"]
    truth("C5.2 four counts published: raw=2 declared=1 resolved=1 unresolved=0",
          acc["raw_evidence_items"] == 2 and acc["declared_reference_ids"] == 1
          and acc["resolved_reference_ids"] == 1 and acc["unresolved_reference_ids"] == 0, acc)

for tag, ev in [("one valid + one malformed", ["D1:0", 3]),
                ("unsupported structure", 3),
                ("dict with no id", ["D1:0", {"x": CANARY}]),
                ("all unresolvable -> empty gold, run continues", ["D9:9"]),
                ("partial: one resolves one does not", ["D1:0", "D9:9"])]:
    exc, out, text, made = surface(lambda e=ev: with_synth_bindings(e))
    leaked = CANARY in text
    print("C5.E %-45s exc=%s code=%s leak=%s files_written=%d"
          % (tag, type(exc).__name__ if exc else None,
             (str(exc)[:60] if exc else "-"), leaked, len(made)))
    global_ok = not leaked
    truth("C5.E %s content-free" % tag, global_ok)

exc, out, _, _ = surface(lambda: with_synth_bindings(["D9:9"]))
truth("C5.3 a fully unresolvable question does NOT stop the run; it stays visible as empty_gold",
      exc is None and out is not None and out["questions_with_empty_gold"] == ["locomo_0_qa0"],
      None if out is None else out["questions_with_empty_gold"])
exc, out, _, _ = surface(lambda: with_synth_bindings(["D1:0", "D9:9"]))
truth("C5.4 a PARTIAL evidence loss STOPS the run with E-COH-002",
      exc is not None and "E-COH-002" in str(exc), str(exc)[:180])
truth("C5.5 no accepted partial-evidence override argument exists",
      not any("partial" in p for p in inspect.signature(I.ingest_locomo).parameters),
      inspect.signature(I.ingest_locomo))

print()
print("=" * 100)
print("C6  the written ingest manifest and the writers")
print("=" * 100)
exc, out, _, _ = surface(lambda: with_synth_bindings(["D1:0", "D1:0"]))
man_path = TMP / "ingest_manifest.json"
exc2, _, text2, made2 = surface(lambda: I.write_ingest_manifest(man_path, I.summarise(out)))
truth("C6.1 the ingest manifest writes", exc2 is None and man_path.exists(), str(exc2)[:160])
if man_path.exists():
    body = man_path.read_text(encoding="utf-8")
    truth("C6.2 the written manifest carries NO canary", CANARY not in body,
          "%d bytes" % len(body))
    info("C6.3 written manifest keys", sorted(json.loads(body)))
exc3, _, _, _ = surface(lambda: I.write_ingest_manifest(man_path, I.summarise(out)))
truth("C6.4 the ingest writer refuses to OVERWRITE", exc3 is not None, str(exc3)[:120])

print()
print("=" * 100)
print("C7  LongMemEval evidence accounting is UNCHANGED (field sets still differ)")
print("=" * 100)
info("C7.1 EVIDENCE_MODEL", json.dumps(I.EVIDENCE_MODEL, sort_keys=True)[:400])
src_txt = (PKG / "corpus_ingest_v4.py").read_text(encoding="utf-8")
truth("C7.2 declared_reference_ids: null + NOT_APPLICABLE retained for LongMemEval",
      "NOT_APPLICABLE" in src_txt and "gold_units_resolved" in src_txt
      and "completeness_guarded_by" in src_txt)
truth("C7.3 raw_evidence_items was NOT added to the LongMemEval model",
      "raw_evidence_items" not in json.dumps(I.EVIDENCE_MODEL[R.LONGMEMEVAL]),
      I.EVIDENCE_MODEL[R.LONGMEMEVAL])

print()
print("=" * 100)
print("C8  N-4 transform stamp")
print("=" * 100)
import numpy as np                                                            # noqa: E402
A = np.random.RandomState(0).normal(size=(20, core.DIM))
Q = np.random.RandomState(1).normal(size=(5, core.DIM))
mu, D, _diag = R.fit_archive_transform(A)
_Xq, stamp = R.apply_archive_transform(Q, mu, D)
exc, _, _, _ = surface(lambda: R.assert_query_transform_is_inherited(mu, D, stamp))
truth("C8.1 the stamp produced by apply_archive_transform is accepted", exc is None,
      str(exc)[:150])
mu_q = Q.mean(axis=0)
_Xbad, bad_stamp = R.apply_archive_transform(Q, mu_q, D)
exc, _, _, _ = surface(lambda: R.assert_query_transform_is_inherited(mu, D, bad_stamp))
truth("C8.2 a QUERY-derived mu is caught by the stamp (N-4)",
      exc is not None and "N-4 VIOLATION" in str(exc), str(exc)[:120])
exc, _, _, _ = surface(lambda: R.assert_query_transform_is_inherited(
    mu, D, R.transform_stamp(mu.copy(), D.copy())))
truth("C8.3 a byte-equal COPY of the archive parameters still passes (value stamp, by design)",
      exc is None, str(exc)[:120])
exc, _, text, _ = surface(lambda: R.assert_query_transform_is_inherited(mu, D, [CANARY]))
truth("C8.4 a non-string CANARY stamp is described, not echoed", CANARY not in text,
      str(exc)[:200])

print()
print("SUMMARY  PASS=%d FAIL=%d INFO=%d" % (PASS, FAIL, INFO))
print("TEMP ROOT:", TMP)
