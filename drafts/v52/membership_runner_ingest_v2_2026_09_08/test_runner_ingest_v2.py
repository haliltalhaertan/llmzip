"""Delta tests for the v2 fix package. Every finding gets a NEGATIVE CONTROL on v1 and closure on v2.

DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. Fake files and synthetic data only. No real corpus is opened,
nothing is fitted, retrieved, ranked or bootstrapped on real data, nothing is sealed.

The shape of every finding test is the same and is deliberate: reproduce the OLD behaviour against the
v1 modules, which are present unchanged on this branch, then show the v2 behaviour on the same input.
A fix asserted only against the new code cannot show that it fixed anything.

Run: python -B test_runner_ingest_v2.py
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
V1_RUNNER = HERE.parent / "membership_runner_v1_2026_09_08"
V1_INGEST = HERE.parent / "membership_ingest_v1_2026_09_08"
CORE = HERE.parent / "membership_impl_v3_2026_09_07"
for _p in (HERE, V1_RUNNER, V1_INGEST, CORE):
    sys.path.insert(0, str(_p))

import numpy as np                                                               # noqa: E402

import membership_scaling_core as core                                           # noqa: E402
import safe_report                                                               # noqa: E402
import membership_runner_v2 as R2                                                # noqa: E402
import corpus_ingest_v2 as I2                                                    # noqa: E402
import membership_runner as R1                                                   # noqa: E402  (v1, unchanged)
import corpus_ingest as I1                                                       # noqa: E402  (v1, unchanged)
from authoritative import accepted_configuration as accepted                     # noqa: E402
from authoritative import resolve_sources                                        # noqa: E402

FAILURES = []
TMP = Path(tempfile.mkdtemp(prefix="v52_v2_"))
REPO = Path(subprocess.run(["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True).stdout.strip())

# Synthetic canaries. Every one is SHORTER than the 120-character policy limit, because that limit was
# never a guarantee and every leak the review demonstrated used a fragment under it.
CANARIES = {
    "question": "What did Melanie say about her sister's wedding in Lisbon last spring?",   # 70
    "answer": "She said the ceremony was moved to a vineyard outside Sintra.",             # 61
    "session": "Melanie: I finally booked the flights for the wedding weekend.",           # 60
}


def check(label, condition, detail=""):
    if condition:
        print(f"ok    {label}   {detail}"[:155])
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}   {detail}"[:155])


def expect(label, fn, needle, exc=core.DesignViolation):
    assert needle, "a negative test must name what it expects"
    try:
        fn()
    except exc as e:
        ok = needle.lower() in str(e).lower()
        check(label, ok, str(e)[:100] if ok else f"wrong message: {e}")
        return str(e)
    except Exception as e:                                                       # noqa: BLE001
        check(label, False, f"raised {type(e).__name__}: {e}")
        return str(e)
    else:
        check(label, False, "no exception raised")
        return ""


def capture(fn):
    """Run fn and return everything it could have emitted: stdout, stderr and any exception text."""
    out, err = io.StringIO(), io.StringIO()
    raised = ""
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fn()
    except BaseException as e:                                                   # noqa: BLE001
        raised = f"{type(e).__name__}: {e}"
    return out.getvalue() + err.getvalue() + raised


def leaked(text: str) -> list[str]:
    return [name for name, frag in CANARIES.items() if frag in text]


def write_json(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


class bind_source:
    def __init__(self, module, benchmark, path):
        self.m, self.b, self.p = module, benchmark, Path(path)

    def __enter__(self):
        self.saved = dict(self.m.BOUND_SOURCES[self.b])
        self.m.BOUND_SOURCES[self.b] = dict(
            self.saved, filename=self.p.name,
            sha256=hashlib.sha256(self.p.read_bytes()).hexdigest(), bytes=self.p.stat().st_size)
        return self

    def __exit__(self, *_):
        self.m.BOUND_SOURCES[self.b] = self.saved


class bind_manifest:
    """Point the ACCEPTED manifest entry at a fake, so end-to-end tests can use synthetic cohorts."""

    def __init__(self, benchmark, raw: bytes):
        self.b, self.raw = benchmark, raw

    def __enter__(self):
        self.saved = dict(accepted.ACCEPTED_MANIFESTS[self.b])
        accepted.ACCEPTED_MANIFESTS[self.b] = dict(
            self.saved, blob_sha256=hashlib.sha256(self.raw).hexdigest())
        return self

    def __exit__(self, *_):
        accepted.ACCEPTED_MANIFESTS[self.b] = self.saved


class gate_open:
    def __enter__(self):
        self.saved = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.saved


def fake_locomo(n_conv=2, n_q=3, n_turns=4, evidence=None, canary=False):
    out = []
    for c in range(n_conv):
        conv = {"speaker_a": "A", "speaker_b": "B"}
        for s in (1,):
            conv[f"session_{s}"] = [
                {"dia_id": f"D{s}:{t}", "speaker": "Melanie" if t % 2 else "B",
                 "text": CANARIES["session"] if canary else f"turn {t}"} for t in range(n_turns)]
            conv[f"session_{s}_date_time"] = "1 Jan 2020"
        qa = []
        for i in range(n_q):
            qa.append({"question": CANARIES["question"] if canary else f"q{i}",
                       "answer": CANARIES["answer"] if canary else f"a{i}",
                       "category": (i % 4) + 1,
                       "evidence": evidence if evidence is not None else [f"D1:{i % n_turns}"]})
        out.append({"sample_id": f"conv-{c}", "conversation": conv, "qa": qa})
    return out


def fake_mapping(n_conv=2, n_q=3, benchmark=None):
    benchmark = benchmark or accepted.LOCOMO
    cohort = {f"locomo_{c}_qa{i}": f"locomo_conv_{c}" for c in range(n_conv) for i in range(n_q)}
    return {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": benchmark,
            "expected_cluster_ids": [f"locomo_conv_{c}" for c in range(n_conv)],
            "expected_question_to_cluster": cohort, "n_questions": len(cohort)}


def mapping_bytes(obj) -> bytes:
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


print("=" * 100)
print("DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS - v2 fix package. Fake files only; no real corpus.")
print("=" * 100)

# --------------------------------------------------------------------------------------------
print("\n== D-1  partially unresolvable evidence ====================================================")
# --------------------------------------------------------------------------------------------
# One question declares two evidence ids; one does not resolve. Exactly the review's S2.6.
src = write_json(TMP / "d1" / "locomo10.json",
                 fake_locomo(n_conv=1, n_q=1, evidence=["D1:0", "D9:99"]))
m_obj = fake_mapping(n_conv=1, n_q=1)
m_raw = mapping_bytes(m_obj)
m_file = TMP / "d1" / "mapping.json"
m_file.write_bytes(m_raw)

with gate_open(), bind_source(I1, R1.LOCOMO, src):
    saved = dict(I1.BOUND_MANIFESTS[R1.LOCOMO])
    I1.BOUND_MANIFESTS[R1.LOCOMO] = {"path": str(m_file),
                                     "sha256": hashlib.sha256(m_file.read_bytes()).hexdigest()}
    try:
        old = I1.ingest_locomo(src, m_file)
        old_summary = I1.summarise(old)
        check("D-1 NEGATIVE CONTROL: v1 ACCEPTS the partial loss",
              old["conversations"]["locomo_conv_0"]["questions"]["locomo_0_qa0"]["gold_rows"] == [0],
              "one gold row kept, one evidence id silently dropped")
        check("D-1 NEGATIVE CONTROL: v1's persisted summary reports questions_with_empty_gold = 0",
              old_summary["questions_with_empty_gold"] == 0,
              "the partial loss is invisible in the only artefact that reaches disk")
        check("D-1 NEGATIVE CONTROL: v1 publishes no evidence accounting at all",
              not any(k.startswith("evidence_ids") for k in old_summary))
    finally:
        I1.BOUND_MANIFESTS[R1.LOCOMO] = saved

with gate_open(), bind_source(I2, accepted.LOCOMO, src), bind_manifest(accepted.LOCOMO, m_raw):
    mapping = R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    expect("D-1 CLOSED: v2 STOPS with a named violation on an unexpected partial resolution",
           lambda: I2.ingest_locomo(src, mapping), "partially unresolvable evidence")
    expect("D-1: a waiver without a citation is refused",
           lambda: I2.ingest_locomo(src, mapping, allow_partial_evidence=True),
           "requires partial_evidence_citation")
    got = I2.ingest_locomo(src, mapping, allow_partial_evidence=True,
                           partial_evidence_citation="synthetic test fixture; no real citation exists")
    summary = I2.summarise(got)
    check("D-1: with a cited waiver it proceeds, and the loss is COUNTED not hidden",
          summary["evidence_ids_declared"] == 2 and summary["evidence_ids_resolved"] == 1
          and summary["evidence_ids_unresolved"] == 1,
          safe_report.counts(**{k: summary[k] for k in
                                ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved")}))
    check("D-1: the affected question count is published in the manifest",
          summary["questions_with_partial_evidence_loss"] == 1)
    check("D-1: the waiver and its citation travel with the ingest",
          got["partial_evidence_waiver"]["allowed"] is True
          and got["partial_evidence_waiver"]["citation"].startswith("synthetic"))
    check("D-1: the gold/adapter semantics are unchanged - resolved ids still map to their own rows",
          got["conversations"]["locomo_conv_0"]["questions"]["locomo_0_qa0"]["gold_rows"] == [0])
    check("D-1: no question was excluded, no gold repaired, no cohort changed",
          len(got["cohort_ids"]) == 1 and got["questions_with_empty_gold"] == [])

    clean_src = write_json(TMP / "d1" / "clean" / "locomo10.json", fake_locomo(n_conv=1, n_q=1))
    with bind_source(I2, accepted.LOCOMO, clean_src):
        clean = I2.summarise(I2.ingest_locomo(clean_src, mapping))
    check("D-1: a fully resolvable source needs no waiver and reports zero unresolved",
          clean["evidence_ids_unresolved"] == 0 and clean["questions_with_partial_evidence_loss"] == 0)

# --------------------------------------------------------------------------------------------
print("\n== D-2 / D-3  the accepted configuration governs ===========================================")
# --------------------------------------------------------------------------------------------
p1 = TMP / "d3" / "v1_seed.json"
rec = R1.freeze_bootstrap_seed(p1, 999, R1.LOCOMO, "question", 10000)
check("D-3 NEGATIVE CONTROL: v1 accepts seed 999 where 52001107 is the accepted value",
      rec["bootstrap_seed"] == 999)
check("D-3 NEGATIVE CONTROL: v1 reads it straight back",
      R1.read_bootstrap_seed(p1, R1.LOCOMO, "question")["bootstrap_seed"] == 999)

expect("D-3 CLOSED: v2 refuses a seed that is not the accepted one",
       lambda: R2.freeze_bootstrap_seed(TMP / "d3" / "a.json", 999, accepted.LOCOMO, "question", 10000),
       "is not the accepted seed")
expect("D-3: a transposed digit is refused",
       lambda: R2.freeze_bootstrap_seed(TMP / "d3" / "b.json", 52001170, accepted.LOCOMO, "question", 10000),
       "is not the accepted seed")
expect("D-2: a replicate count that is not the accepted one is refused at freezing time",
       lambda: R2.freeze_bootstrap_seed(TMP / "d3" / "c.json", 52001107, accepted.LOCOMO, "question", 7),
       "is not the accepted count")
good = R2.freeze_bootstrap_seed(TMP / "d3" / "ok.json", 52001107, accepted.LOCOMO, "question", 10000)
check("D-3: the accepted seed is accepted", good["bootstrap_seed"] == 52001107)
check("D-3: the accepted values come from the authoritative module, not from this file",
      accepted.ACCEPTED_BOOTSTRAP[(accepted.LOCOMO, "question")]["seed"] == 52001107)
expect("D-3: a scheme the design does not define has no accepted configuration and is refused",
       lambda: R2.accepted_bootstrap_for(accepted.LONGMEMEVAL, "cluster"),
       "no accepted bootstrap configuration exists")

tampered = TMP / "d3" / "tampered.json"
tampered.write_text(json.dumps(dict(json.loads((TMP / "d3" / "ok.json").read_text(encoding="utf-8")),
                                    bootstrap_seed=999)), encoding="utf-8", newline="\n")
expect("D-3: a hand-edited seed record is caught when it is read",
       lambda: R2.read_bootstrap_seed(tampered, accepted.LOCOMO, "question"),
       "does not match the accepted configuration")

# D-2 end to end: the replicate count must match the frozen record.
records = [{"question_id": f"locomo_{c}_qa{i}", "rotation_seed": int(s), "arm": a,
            "fractional_R3": 0.5 + 0.01 * i}
           for c in range(2) for i in range(3) for s in core.ROTATION_SEEDS for a in core.ARMS]
qids = [f"locomo_{c}_qa{i}" for c in range(2) for i in range(3)]
cids = [f"locomo_conv_{c}" for c in range(2) for _ in range(3)]
m2_obj = fake_mapping()
m2_raw = mapping_bytes(m2_obj)

with bind_manifest(accepted.LOCOMO, m2_raw):
    mp2 = R2.load_accepted_mapping(accepted.LOCOMO, raw=m2_raw)
    seed_path = TMP / "d2" / "seed.json"
    R2.freeze_bootstrap_seed(seed_path, 52001107, accepted.LOCOMO, "question", 10000)
    expect("D-2 CLOSED: a run whose replicate count contradicts the frozen record is refused",
           lambda: R2.compute_results(records, qids, cids, mp2, seed_path,
                                      benchmark=accepted.LOCOMO, scheme="question", replicates=7),
           "contradicts the frozen seed record")
    res = R2.compute_results(records, qids, cids, mp2, seed_path,
                             benchmark=accepted.LOCOMO, scheme="question", replicates=10000)
    check("D-2: the matching count runs and the artefact states what was actually used",
          res["bootstrap_seed_record"]["replicates"] == 10000)

    # v1 negative control on the same shape.
    p1b = TMP / "d2" / "v1_seed.json"
    R1.freeze_bootstrap_seed(p1b, 52001107, R1.LOCOMO, "question", 10000)
    m1f = write_json(TMP / "d2" / "m1.json", m2_obj)
    mp1 = R1.load_expected_mapping(m1f, hashlib.sha256(m1f.read_bytes()).hexdigest())
    old_res = R1.compute_results(records, qids, cids, mp1, p1b,
                                 benchmark=R1.LOCOMO, scheme="question", replicates=7)
    check("D-2 NEGATIVE CONTROL: v1 ran 7 replicates and persisted a record saying 10000",
          old_res["bootstrap_seed_record"]["replicates"] == 10000,
          "the artefact misstated how it was computed")

# --------------------------------------------------------------------------------------------
print("\n== source trust: the expected hash is not a caller argument =================================")
# --------------------------------------------------------------------------------------------
m1f = write_json(TMP / "trust" / "m.json", m2_obj)
check("NEGATIVE CONTROL: v1 loads any file against any hash the CALLER supplies",
      R1.load_expected_mapping(m1f, hashlib.sha256(m1f.read_bytes()).hexdigest())["benchmark"]
      == accepted.LOCOMO)
expect("CLOSED: v2 has no caller hash argument, and refuses bytes that are not the accepted ones",
       lambda: R2.load_accepted_mapping(accepted.LOCOMO, raw=b'{"benchmark": "LoCoMo"}'),
       "do not match the accepted hash")
expect("v2 refuses being given both raw bytes and a path",
       lambda: R2.load_accepted_mapping(accepted.LOCOMO, raw=b"{}", path=m1f), "exactly one")

sup = resolve_sources.git_blob(
    REPO, "e61c414e6bfc2dab1ad56cd93f66e1f2fddf71bf",
    "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_longmemeval.json")
msg = expect("the SUPERSEDED LongMemEval v1 manifest is refused AS SUPERSEDED, not as a hash mismatch",
             lambda: R2.load_accepted_mapping(accepted.LONGMEMEVAL, raw=sup), "superseded")
check("...and the refusal names what supersedes it and why",
      "d5b8ed69" in msg and "placeholder" in msg.lower())
check("the accepted LongMemEval v2 manifest loads from Git's original bytes",
      R2.load_accepted_mapping(
          accepted.LONGMEMEVAL,
          raw=resolve_sources.git_blob(REPO, accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL]["commit"],
                                       accepted.ACCEPTED_MANIFESTS[accepted.LONGMEMEVAL]["path"])
      )["n_questions"] == 470)
check("the accepted LoCoMo manifest loads the same way, with 1535 questions in 10 conversations",
      R2.load_accepted_mapping(
          accepted.LOCOMO,
          raw=resolve_sources.git_blob(REPO, accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["commit"],
                                       accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["path"])
      )["n_questions"] == 1535)
check("the acceptance record is reachable from the authoritative module",
      accepted.ACCEPTANCE_RECORD["sha256"].startswith("c5d2e639")
      and accepted.ACCEPTANCE_RECORD["ledger_entries"] == ["L-074", "L-075"])
check("the PROPOSED-vs-ACCEPTED relation is stated in one place, in this package",
      "does NOT describe their status now" in accepted.PROPOSED_VS_ACCEPTED)

# --------------------------------------------------------------------------------------------
print("\n== D-4  raw-byte discipline ================================================================")
# --------------------------------------------------------------------------------------------
loc_entry = accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]
blob = resolve_sources.git_blob(REPO, loc_entry["commit"], loc_entry["path"])
crlf = blob.replace(b"\n", b"\r\n")
check("the CRLF form differs from the accepted blob, as the review measured",
      hashlib.sha256(crlf).hexdigest() != loc_entry["blob_sha256"],
      f"blob {len(blob)} B vs CRLF {len(crlf)} B")
crlf_file = TMP / "d4" / "PROPOSED_mapping_locomo.json"
crlf_file.parent.mkdir(parents=True, exist_ok=True)
crlf_file.write_bytes(crlf)

with gate_open():
    saved = dict(I1.BOUND_MANIFESTS[R1.LOCOMO])
    I1.BOUND_MANIFESTS[R1.LOCOMO] = {"path": str(crlf_file), "sha256": loc_entry["blob_sha256"]}
    try:
        expect("D-4 NEGATIVE CONTROL: v1 refuses its OWN accepted manifest from a CRLF checkout",
               lambda: I1.load_bound_mapping(crlf_file, R1.LOCOMO), "hash mismatch")
    finally:
        I1.BOUND_MANIFESTS[R1.LOCOMO] = saved

msg = expect("D-4 CLOSED: v2 also refuses it - the hash check is NOT relaxed",
             lambda: R2.load_accepted_mapping(accepted.LOCOMO, path=crlf_file),
             "do not match the accepted hash")
check("D-4: ...but v2 DIAGNOSES the cause instead of leaving a bare mismatch",
      "line-ending-translated checkout" in msg)
check("D-4: and says explicitly that it refuses rather than normalising",
      "REFUSED rather than normalised" in msg)
check("D-4: the accepted bytes still load through the same path",
      R2.load_accepted_mapping(accepted.LOCOMO, raw=blob)["n_questions"] == 1535)
mat = resolve_sources.materialize_accepted_manifest(REPO, accepted.LOCOMO, TMP / "d4" / "materialised")
check("D-4: byte-preserving materialisation reproduces the accepted hash on disk",
      hashlib.sha256(mat.read_bytes()).hexdigest() == loc_entry["blob_sha256"], mat.name)
check("D-4: and a materialised file loads",
      R2.load_accepted_mapping(accepted.LOCOMO, path=mat)["n_questions"] == 1535)
check("D-4: no .gitattributes was added by this package",
      not (HERE / ".gitattributes").exists() and not (REPO / ".gitattributes").exists())

# --------------------------------------------------------------------------------------------
print("\n== D-5  nothing carries content out ========================================================")
# --------------------------------------------------------------------------------------------
canary_src = write_json(TMP / "d5" / "locomo10.json", fake_locomo(n_conv=1, n_q=1, canary=True))
record_with_text = {"question_id": CANARIES["question"], "answer": CANARIES["answer"],
                    "session": CANARIES["session"]}

v1_paths = {
    "S7.5 validate_identifier whitespace": lambda m: m.validate_identifier(" " + CANARIES["question"], "question id", 0),
    "S7.6 validate_identifier -> describe": lambda m: m.validate_identifier(record_with_text, "question id", 0),
    "S7.7 freeze_bootstrap_seed -> describe": lambda m: m.freeze_bootstrap_seed(
        TMP / "d5" / f"{id(m)}.json", record_with_text, m.LOCOMO, "question", 10000),
    "S7.9 duplicate ids": lambda m: m.validate_identifier_columns(
        [CANARIES["question"], CANARIES["question"]], ["c", "c"]),
}
for name, fn in v1_paths.items():
    check(f"D-5 NEGATIVE CONTROL: v1 leaks through {name}",
          bool(leaked(capture(lambda f=fn: f(R1)))),
          str(leaked(capture(lambda f=fn: f(R1)))))
    check(f"D-5 CLOSED: v2 leaks nothing through {name}",
          not leaked(capture(lambda f=fn: f(R2))),
          "no canary in stdout, stderr or exception text")

# S7.8 extra ids, through the identity contract
def extra_ids(m):
    mm = fake_mapping(n_conv=1, n_q=1)
    mm = dict(mm, _accepted_manifest_sha256=accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]["blob_sha256"])
    m.verify_source_identity(["locomo_0_qa0", CANARIES["question"]], ["locomo_conv_0", "locomo_conv_0"], mm)


check("D-5 NEGATIVE CONTROL: v1 leaks through S7.8 verify_source_identity extras",
      bool(leaked(capture(lambda: extra_ids(R1)))))
check("D-5 CLOSED: v2 leaks nothing through S7.8", not leaked(capture(lambda: extra_ids(R2))))

# S7.2 the content policy leaking through its own error
policy_payload = {CANARIES["question"]: "x" * 400}
check("D-5 NEGATIVE CONTROL: v1's assert_content_free echoes a sub-120 KEY in its own error",
      bool(leaked(capture(lambda: I1.assert_content_free(policy_payload)))))
check("D-5 CLOSED: v2's assert_content_free reports the key by digest",
      not leaked(capture(lambda: I2.assert_content_free(policy_payload))))

# S7.10 duplicate question id in the source, and the whole ingestion path
dup = fake_locomo(n_conv=1, n_q=2, canary=True)
dup[0]["qa"][1]["question_id"] = CANARIES["question"]
dup[0]["qa"][0]["question_id"] = CANARIES["question"]
dup_src = write_json(TMP / "d5" / "dup" / "locomo10.json", dup)


def v1_dup():
    with gate_open(), bind_source(I1, R1.LOCOMO, dup_src):
        saved = dict(I1.BOUND_MANIFESTS[R1.LOCOMO])
        I1.BOUND_MANIFESTS[R1.LOCOMO] = {"path": str(m_file),
                                         "sha256": hashlib.sha256(m_file.read_bytes()).hexdigest()}
        try:
            I1.ingest_locomo(dup_src, m_file)
        finally:
            I1.BOUND_MANIFESTS[R1.LOCOMO] = saved


def v2_dup():
    with gate_open(), bind_source(I2, accepted.LOCOMO, dup_src), bind_manifest(accepted.LOCOMO, m_raw):
        I2.ingest_locomo(dup_src, R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw))


check("D-5 NEGATIVE CONTROL: v1 leaks through S7.10 the duplicate-id error", bool(leaked(capture(v1_dup))))
check("D-5 CLOSED: v2 leaks nothing through S7.10", not leaked(capture(v2_dup)))

# the happy path, and what actually gets written
with gate_open(), bind_source(I2, accepted.LOCOMO, canary_src), bind_manifest(accepted.LOCOMO, m_raw):
    mapping = R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)
    text = capture(lambda: I2.write_ingest_manifest(TMP / "d5" / "out.json",
                                                    I2.summarise(I2.ingest_locomo(canary_src, mapping))))
    check("D-5: the happy path emits no canary on stdout or stderr", not leaked(text), text[:60])
    written = (TMP / "d5" / "out.json").read_text(encoding="utf-8")
    check("D-5: the written manifest carries no canary", not leaked(written))
    check("D-5: ...even though the ingested structures DO hold the text in memory",
          CANARIES["question"] in I2.ingest_locomo(canary_src, mapping)["conversations"]
          ["locomo_conv_0"]["questions"]["locomo_0_qa0"]["text"],
          "that is what ingestion is for; the claim is about messages and files")
check("D-5: safe_report.describe never reproduces the value",
      not leaked(safe_report.describe(CANARIES["question"]))
      and "digest=" in safe_report.describe(CANARIES["question"])
      and "len=70" in safe_report.describe(CANARIES["question"]))
check("D-5: the 120-character limit is NOT presented as a guarantee anywhere in v2",
      "The limit was never a guarantee" in (HERE / "corpus_ingest_v2.py").read_text(encoding="utf-8")
      and "IS NOT USED AS A GUARANTEE" in (HERE / "safe_report.py").read_text(encoding="utf-8"))

# --------------------------------------------------------------------------------------------
print("\n== D-6  the transform is checked by construction ===========================================")
# --------------------------------------------------------------------------------------------
rng = np.random.default_rng(5204)
archive = rng.normal(0.3, 1.7, size=(48, core.DIM))
query = rng.normal(-1.1, 0.4, size=(9, core.DIM))
mu, D, _ = R2.fit_archive_transform(archive)

check("D-6 NEGATIVE CONTROL: v1's assertion passes on COPIES, though it claims IDENTICAL objects",
      R1.assert_query_transform_is_inherited(mu, D, mu.copy(), D.copy()) is None)
mu_q, D_q, _ = R1.fit_archive_transform(np.vstack([query, query + 1e-9]))
_, _ = None, None
check("D-6 NEGATIVE CONTROL: v1 passes when the query was transformed with a QUERY-derived mu "
      "and the ARCHIVE mu was reported instead",
      R1.assert_query_transform_is_inherited(mu, D, mu, D) is None,
      "the assertion never saw what apply_archive_transform consumed")

q_t, stamp = R2.apply_archive_transform(query, mu, D)
R2.assert_query_transform_is_inherited(mu, D, stamp)
check("D-6 CLOSED: the stamp produced by the real transform call verifies", True)
check("D-6: the transformed query is unchanged in value by the fix",
      np.allclose(q_t, (query - mu) @ D))
bad_q, bad_stamp = R2.apply_archive_transform(query, mu_q, D_q)
expect("D-6: a query transformed with QUERY-derived parameters is caught",
       lambda: R2.assert_query_transform_is_inherited(mu, D, bad_stamp), "N-4 VIOLATION")
_, wrong_D_stamp = R2.apply_archive_transform(query, mu, D * (1 + 2 ** -52))
expect("D-6: a 1-ULP perturbation of D is caught",
       lambda: R2.assert_query_transform_is_inherited(mu, D, wrong_D_stamp), "N-4 VIOLATION")
check("D-6: copies of the same VALUES produce the same stamp - the check is on bytes, not identity",
      R2.transform_stamp(mu, D) == R2.transform_stamp(mu.copy(), D.copy()),
      "value-based by design; the fix is that the caller can no longer report a value it did not use")
expect("D-6: a caller that hands back something that is not a stamp is refused",
       lambda: R2.assert_query_transform_is_inherited(mu, D, (mu, D)), "must be the string returned")
check("D-6: the docstring no longer claims object identity",
      "IDENTICAL objects, bitwise" not in (HERE / "membership_runner_v2.py").read_text(encoding="utf-8"))
check("D-6: nothing is estimated from the query - that half was sound and is unchanged",
      np.allclose(mu, archive.mean(axis=0)))

# --------------------------------------------------------------------------------------------
print("\n== D-7 / D-8  structural validation ========================================================")
# --------------------------------------------------------------------------------------------
SENT = "longmemeval_single_connected_component_inherited_task3a1"


def lme_items(ragged=False, drop_qid=False):
    item = {"question_id": "q0", "question": "qq", "answer": "aa",
            "haystack_session_ids": ["s0", "s1"], "haystack_dates": [] if ragged else ["d0", "d1"],
            "haystack_sessions": [[{"role": "user", "content": "hello", "has_answer": True}],
                                  [{"role": "user", "content": "again"}]]}
    if drop_qid:
        item = {k: v for k, v in item.items() if k != "question_id"}
        item["question_id_typo"] = "q0"
    return [item]


lme_map_obj = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LONGMEMEVAL,
               "expected_cluster_ids": [SENT], "expected_question_to_cluster": {"q0": SENT},
               "n_questions": 1}
lme_raw = mapping_bytes(lme_map_obj)
ragged_src = write_json(TMP / "d7" / "longmemeval_s_cleaned.json", lme_items(ragged=True))
noqid_src = write_json(TMP / "d8" / "longmemeval_s_cleaned.json", lme_items(drop_qid=True))
lme_file = write_json(TMP / "d7" / "m.json", lme_map_obj)

with gate_open(), bind_source(I1, R1.LONGMEMEVAL, ragged_src):
    saved = dict(I1.BOUND_MANIFESTS[R1.LONGMEMEVAL])
    I1.BOUND_MANIFESTS[R1.LONGMEMEVAL] = {"path": str(lme_file),
                                          "sha256": hashlib.sha256(lme_file.read_bytes()).hexdigest()}
    try:
        old = I1.ingest_longmemeval(ragged_src, lme_file)
        check("D-7 NEGATIVE CONTROL: v1 truncates a ragged haystack to ZERO units, silently",
              len(old["questions"]["q0"]["units"]) == 0)
    finally:
        I1.BOUND_MANIFESTS[R1.LONGMEMEVAL] = saved

with gate_open(), bind_source(I1, R1.LONGMEMEVAL, noqid_src):
    saved = dict(I1.BOUND_MANIFESTS[R1.LONGMEMEVAL])
    I1.BOUND_MANIFESTS[R1.LONGMEMEVAL] = {"path": str(lme_file),
                                          "sha256": hashlib.sha256(lme_file.read_bytes()).hexdigest()}
    try:
        expect("D-8 NEGATIVE CONTROL: v1 raises a raw KeyError for a missing question_id",
               lambda: I1.ingest_longmemeval(noqid_src, lme_file), "question_id", exc=KeyError)
    finally:
        I1.BOUND_MANIFESTS[R1.LONGMEMEVAL] = saved

with gate_open(), bind_manifest(accepted.LONGMEMEVAL, lme_raw):
    lmap = R2.load_accepted_mapping(accepted.LONGMEMEVAL, raw=lme_raw)
    with bind_source(I2, accepted.LONGMEMEVAL, ragged_src):
        expect("D-7 CLOSED: v2 refuses ragged parallel arrays before zipping them",
               lambda: I2.ingest_longmemeval(ragged_src, lmap), "different lengths")
    with bind_source(I2, accepted.LONGMEMEVAL, noqid_src):
        expect("D-8 CLOSED: v2 gives a named DesignViolation for a missing question_id",
               lambda: I2.ingest_longmemeval(noqid_src, lmap), "not a mapping with a question_id")
    ok_src = write_json(TMP / "d7" / "ok" / "longmemeval_s_cleaned.json", lme_items())
    with bind_source(I2, accepted.LONGMEMEVAL, ok_src):
        got_l = I2.ingest_longmemeval(ok_src, lmap)
        check("D-7/D-8: a well-formed item still ingests, with both sessions contributing",
              len(got_l["questions"]["q0"]["units"]) == 2
              and got_l["questions"]["q0"]["gold_rows"] == [0])
    expect("D-8: a missing question_id error carries no content",
           lambda: I2._longmemeval_units({"question_id": "q"}), "missing the required field")

# --------------------------------------------------------------------------------------------
print("\n== unchanged behaviour that must stay unchanged =============================================")
# --------------------------------------------------------------------------------------------
check("the gate is closed", core.REAL_DATA_EXECUTION_ENABLED is False)
expect("the gate still refuses by default", lambda: I2.verify_source_bytes(src, accepted.LOCOMO),
       "not authorized")
expect("the real-corpus entry point is still a refusing stub", lambda: R2.run_on_real_corpus(),
       "not authorized")
expect("a LongMemEval cluster bootstrap is still refused",
       lambda: R2.compute_results([], ["q0"], [SENT],
                                  dict(lme_map_obj,
                                       _accepted_manifest_sha256=accepted.ACCEPTED_MANIFESTS[
                                           accepted.LONGMEMEVAL]["blob_sha256"]),
                                  TMP / "nope.json",
                                  benchmark=accepted.LONGMEMEVAL, scheme="cluster"),
       "REFUSED for LongMemEval")
out2 = TMP / "final" / "m.json"
with gate_open(), bind_source(I2, accepted.LOCOMO, clean_src), bind_manifest(accepted.LOCOMO, m_raw):
    s2 = I2.summarise(I2.ingest_locomo(clean_src, R2.load_accepted_mapping(accepted.LOCOMO, raw=m_raw)))
I2.write_ingest_manifest(out2, s2)
expect("writers still refuse to overwrite", lambda: I2.write_ingest_manifest(out2, s2),
       "refusing to overwrite")
check("the closed core is untouched by this package",
      hashlib.sha256((CORE / "membership_scaling_core.py").read_bytes()).hexdigest()
      == accepted.BOUND_CORE["blob_sha256"]
      or hashlib.sha256((CORE / "membership_scaling_core.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
      == accepted.BOUND_CORE["blob_sha256"])

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): {FAILURES}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS for findings D-1 through D-8 and the directly "
      "connected source-trust items. Fake files only. Not a seal and not authorization to run.")
raise SystemExit(0)
