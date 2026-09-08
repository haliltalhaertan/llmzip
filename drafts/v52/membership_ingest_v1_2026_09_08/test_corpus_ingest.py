"""End-to-end tests for the corpus ingestion, on FAKE FILES ONLY.

DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS. No real corpus is opened. Every source in this file is a
small fake written into a temp directory by this script, with the same SHAPE as the real one and
none of its content. The bound source and manifest hashes are overridden per test to point at those
fakes, and the override is explicit so a reader can see it.

WHAT IS DEMONSTRATED, AND ONLY THIS: that importing the module opens nothing; that the real-data gate
refuses by default and is checked before any parse; that a wrong hash, a wrong size and a renamed file
are each refused BEFORE content is read; that the bound cohort is resolved id by id and that missing,
extra, misrouted, duplicated and position-mismatched ids are refused rather than repaired; that no
cohort is ever derived; that the content policy refuses anything that could carry source text; and
that the manifest writer keeps the closed schema and the refusal to overwrite.

Run: python -B test_corpus_ingest.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import corpus_ingest as ing                                                      # noqa: E402
import membership_runner as runner                                               # noqa: E402
import membership_scaling_core as core                                           # noqa: E402

FAILURES = []


def check(label, condition, detail=""):
    if condition:
        print(f"ok    {label}   {detail}"[:150])
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}   {detail}"[:150])


def expect(label, fn, needle, exc=core.DesignViolation):
    assert needle, "a negative test must name what it expects"
    try:
        fn()
    except exc as e:
        ok = needle.lower() in str(e).lower()
        check(label, ok, str(e)[:100] if ok else f"wrong message: {e}")
    except Exception as e:                                                       # noqa: BLE001
        check(label, False, f"raised {type(e).__name__}: {e}")
    else:
        check(label, False, "no exception raised")


TMP = Path(tempfile.mkdtemp(prefix="v52_ingest_"))
print("=" * 100)
print("DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS - corpus ingestion v1. Fake files only; no real corpus.")
print("=" * 100)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p: Path, obj) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return p


class bind_source:
    """Point a bound source entry at a fake file, visibly and temporarily."""

    def __init__(self, benchmark, path):
        self.benchmark, self.path = benchmark, Path(path)

    def __enter__(self):
        self.saved = dict(ing.BOUND_SOURCES[self.benchmark])
        ing.BOUND_SOURCES[self.benchmark].update(
            {"filename": self.path.name, "sha256": sha(self.path), "bytes": self.path.stat().st_size})
        return self

    def __exit__(self, *_):
        ing.BOUND_SOURCES[self.benchmark] = self.saved


class bind_manifest:
    def __init__(self, benchmark, path):
        self.benchmark, self.path = benchmark, Path(path)

    def __enter__(self):
        self.saved = dict(ing.BOUND_MANIFESTS[self.benchmark])
        ing.BOUND_MANIFESTS[self.benchmark] = {"path": str(self.path), "sha256": sha(self.path)}
        return self

    def __exit__(self, *_):
        ing.BOUND_MANIFESTS[self.benchmark] = self.saved


class gate_open:
    """Open the core gate for one block, and prove it is closed again afterwards."""

    def __enter__(self):
        self.saved = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.saved


# --------------------------------------------------------------------------------------------
print("\n-- 1. importing this module opens nothing ------------------------------------------------")
# --------------------------------------------------------------------------------------------
src = (HERE / "corpus_ingest.py").read_text(encoding="utf-8")
tree_lines = [l for l in src.splitlines() if l and not l[0].isspace()]
opens_at_module_level = [l for l in tree_lines
                         if ("open(" in l or "read_text" in l or "read_bytes" in l or "json.load" in l)
                         and not l.startswith(("def ", "class ", "#"))]
check("no module-level file read in the ingestion source", opens_at_module_level == [],
      str(opens_at_module_level)[:80])
check("the bound source table holds VALUES, not resolved paths",
      all(not isinstance(v.get("filename"), Path) for v in ing.BOUND_SOURCES.values()))
check("import did not enable the real-data gate", core.REAL_DATA_EXECUTION_ENABLED is False)
check("test discovery importing this file cannot reach a corpus: the module knows no corpus path",
      all("path" not in s for s in ing.BOUND_SOURCES.values()))

# --------------------------------------------------------------------------------------------
print("\n-- 2. the gate refuses before anything is parsed ------------------------------------------")
# --------------------------------------------------------------------------------------------
fake = write_json(TMP / "locomo10.json", [])
expect("the gate refuses source verification by default",
       lambda: ing.verify_source_bytes(fake, runner.LOCOMO), "not authorized")
expect("the gate refuses LoCoMo ingestion by default",
       lambda: ing.ingest_locomo(fake, TMP / "m.json"), "not authorized")
expect("the gate refuses LongMemEval ingestion by default",
       lambda: ing.ingest_longmemeval(fake, TMP / "m.json"), "not authorized")
expect("an explicit enabled=False is still refused",
       lambda: ing.verify_source_bytes(fake, runner.LOCOMO, enabled=False), "not authorized")
check("the gate is still closed after those probes", core.REAL_DATA_EXECUTION_ENABLED is False)

# --------------------------------------------------------------------------------------------
print("\n-- 3. source byte identity is checked BEFORE parsing --------------------------------------")
# --------------------------------------------------------------------------------------------
# A file that is not valid JSON at all: identity must fail first, with an identity message.
broken = TMP / "locomo10_broken" / "locomo10.json"
broken.parent.mkdir(parents=True, exist_ok=True)
broken.write_bytes(b"{ this is not json")
with gate_open():
    expect("a file whose hash does not match is refused, and it is never parsed",
           lambda: ing.ingest_locomo(broken, TMP / "m.json"), "source identity mismatch")
    expect("a missing file is refused by name",
           lambda: ing.verify_source_bytes(TMP / "absent" / "locomo10.json", runner.LOCOMO),
           "bound source not found")
    renamed = write_json(TMP / "renamed" / "locomo_copy.json", [])
    expect("a RENAMED source is refused rather than accepted",
           lambda: ing.verify_source_bytes(renamed, runner.LOCOMO), "renamed source")
    with bind_source(runner.LOCOMO, fake):
        truncated = write_json(TMP / "trunc" / "locomo10.json", [1])
        expect("a file of the right name but wrong size and hash is refused",
               lambda: ing.verify_source_bytes(truncated, runner.LOCOMO), "identity mismatch")
        ident = ing.verify_source_bytes(fake, runner.LOCOMO)
        check("a matching file passes and returns its identity",
              ident["source_sha256"] == sha(fake) and ident["source_bytes"] == fake.stat().st_size)
check("the gate closed again after the identity block", core.REAL_DATA_EXECUTION_ENABLED is False)

# --------------------------------------------------------------------------------------------
print("\n-- 4. LoCoMo end to end on a fake corpus --------------------------------------------------")
# --------------------------------------------------------------------------------------------
def fake_locomo(n_conv=3, n_q=4, n_turns=6):
    out = []
    for c in range(n_conv):
        conv = {"speaker_a": "A", "speaker_b": "B"}
        for s in (1, 2):
            conv[f"session_{s}"] = [
                {"dia_id": f"D{s}:{t}", "speaker": "A" if t % 2 else "B", "text": f"turn {t} of session {s}"}
                for t in range(n_turns)]
            conv[f"session_{s}_date_time"] = "1 Jan 2020"
        qa = [{"question": f"q{i}", "answer": f"a{i}", "category": (i % 4) + 1,
               "evidence": [f"D1:{i % n_turns}"]} for i in range(n_q)]
        qa.append({"question": "adversarial", "answer": "", "category": 5, "evidence": []})
        out.append({"sample_id": f"conv-{c}", "conversation": conv, "qa": qa})
    return out


loc_src = write_json(TMP / "loc" / "locomo10.json", fake_locomo())
cohort = {f"locomo_{c}_qa{i}": f"locomo_conv_{c}" for c in range(3) for i in range(4)}
loc_map = write_json(TMP / "loc" / "mapping.json", {
    "source_id": "fake", "source_sha256": "0" * 64, "benchmark": runner.LOCOMO,
    "expected_cluster_ids": [f"locomo_conv_{c}" for c in range(3)],
    "expected_question_to_cluster": cohort, "n_questions": len(cohort)})

with gate_open(), bind_source(runner.LOCOMO, loc_src), bind_manifest(runner.LOCOMO, loc_map):
    got = ing.ingest_locomo(loc_src, loc_map)
    check("every bound question id is resolved individually", len(got["cohort_ids"]) == 12)
    check("each question lands in the conversation the manifest names",
          all(qid in got["conversations"][cluster]["questions"] for qid, cluster in cohort.items()))
    check("memory units are ordered by session number then file order",
          [u["dia_id"] for u in got["conversations"]["locomo_conv_0"]["units"]][:3] == ["D1:0", "D1:1", "D1:2"])
    check("both sessions contribute units", len(got["conversations"]["locomo_conv_0"]["units"]) == 12)
    check("gold rows are resolved against this conversation's own units",
          got["conversations"]["locomo_conv_0"]["questions"]["locomo_0_qa1"]["gold_rows"] == [1])
    check("the category-5 question is NOT ingested - it is not in the bound cohort",
          "locomo_0_qa4" not in got["conversations"]["locomo_conv_0"]["questions"])
    check("...and it is reported as present in the source but outside the cohort",
          "locomo_0_qa4" in got["extra_ids_in_source"], f"{len(got['extra_ids_in_source'])} extra ids")
    check("NO cohort is derived: the ingest reports extras rather than selecting them",
          len(got["cohort_ids"]) == 12 and len(got["extra_ids_in_source"]) == 3)

    # a bound id that the source does not have
    short_map = write_json(TMP / "loc" / "mapping_missing.json", {
        **json.loads(loc_map.read_text(encoding="utf-8")),
        "expected_question_to_cluster": {**cohort, "locomo_0_qa99": "locomo_conv_0"},
        "n_questions": len(cohort) + 1})
    with bind_manifest(runner.LOCOMO, short_map):
        expect("a bound id absent from the source is REFUSED, not skipped",
               lambda: ing.ingest_locomo(loc_src, short_map), "absent from the source")

    # a bound id routed to the wrong conversation
    bad_map = write_json(TMP / "loc" / "mapping_misrouted.json", {
        **json.loads(loc_map.read_text(encoding="utf-8")),
        "expected_question_to_cluster": {**cohort, "locomo_0_qa0": "locomo_conv_1"}})
    with bind_manifest(runner.LOCOMO, bad_map):
        expect("a bound id routed to the wrong conversation is REFUSED",
               lambda: ing.ingest_locomo(loc_src, bad_map), "wrong conversation")

    # a duplicated question id inside the source
    dup = fake_locomo()
    dup[0]["qa"][1]["question_id"] = "locomo_0_qa0"
    dup_src = write_json(TMP / "dup" / "locomo10.json", dup)
    with bind_source(runner.LOCOMO, dup_src):
        expect("a duplicated question id in the SOURCE is refused",
               lambda: ing.ingest_locomo(dup_src, loc_map), "more than once")

    # a positional id that does not sit at its stated position
    moved = fake_locomo()
    moved[0]["qa"][2]["question_id"] = "locomo_0_qa0"
    moved[0]["qa"][0]["question_id"] = "locomo_0_qa2"
    moved_src = write_json(TMP / "moved" / "locomo10.json", moved)
    with bind_source(runner.LOCOMO, moved_src):
        expect("an id whose positional index contradicts its position is refused",
               lambda: ing.ingest_locomo(moved_src, loc_map), "positional index")

    # duplicate memory unit ids
    dupunit = fake_locomo()
    dupunit[0]["conversation"]["session_2"][0]["dia_id"] = "D1:0"
    dupunit_src = write_json(TMP / "dupunit" / "locomo10.json", dupunit)
    with bind_source(runner.LOCOMO, dupunit_src):
        expect("a duplicate memory unit id is refused",
               lambda: ing.ingest_locomo(dupunit_src, loc_map), "duplicate memory unit")

    summary = ing.summarise(got)
    check("the summary carries exactly the declared schema", set(summary) == ing.INGEST_MANIFEST_KEYS)
    check("the summary counts units and questions per cluster",
          summary["n_archive_units_total"] == 36 and summary["per_cluster_questions"]["locomo_conv_0"] == 4)

# --------------------------------------------------------------------------------------------
print("\n-- 5. LongMemEval end to end on a fake corpus ---------------------------------------------")
# --------------------------------------------------------------------------------------------
def fake_lme(n=5):
    out = []
    for i in range(n):
        qid = f"q{i:04d}" + ("_abs" if i >= 3 else "")
        out.append({"question_id": qid, "question": f"question {i}", "answer": f"answer {i}",
                    "question_type": "multi-session", "question_date": "2023/01/01",
                    "haystack_session_ids": ["s0", "s1"], "haystack_dates": ["d0", "d1"],
                    "haystack_sessions": [
                        [{"role": "user", "content": "hello", "has_answer": i == 0},
                         {"role": "assistant", "content": "hi"}],
                        [{"role": "user", "content": "again", "has_answer": True}]]})
    return out


lme_src = write_json(TMP / "lme" / "longmemeval_s_cleaned.json", fake_lme())
SENT = "longmemeval_single_connected_component_inherited_task3a1"
lme_cohort = {f"q{i:04d}": SENT for i in range(3)}
lme_map = write_json(TMP / "lme" / "mapping.json", {
    "source_id": "fake", "source_sha256": "0" * 64, "benchmark": runner.LONGMEMEVAL,
    "expected_cluster_ids": [SENT], "expected_question_to_cluster": lme_cohort,
    "n_questions": len(lme_cohort)})

with gate_open(), bind_source(runner.LONGMEMEVAL, lme_src), bind_manifest(runner.LONGMEMEVAL, lme_map):
    got_l = ing.ingest_longmemeval(lme_src, lme_map)
    check("every bound LongMemEval id is resolved", len(got_l["questions"]) == 3)
    check("each question carries its OWN archive", len(got_l["questions"]["q0000"]["units"]) == 3)
    check("memory ids follow the committed canonical form",
          got_l["questions"]["q0000"]["units"][0]["memory_id"] == "q0000::s0::s0::t0")
    check("gold rows come from has_answer being exactly True",
          got_l["questions"]["q0000"]["gold_rows"] == [0, 2]
          and got_l["questions"]["q0001"]["gold_rows"] == [2])
    check("the '_abs' items are present in the source but outside the bound cohort",
          got_l["extra_ids_in_source"] == ["q0003_abs", "q0004_abs"])
    s = ing.summarise(got_l)
    check("the LongMemEval summary reports ONE cluster", s["n_clusters"] == 1)
    check("the summary carries exactly the declared schema", set(s) == ing.INGEST_MANIFEST_KEYS)

check("the gate is closed again after both ingestions", core.REAL_DATA_EXECUTION_ENABLED is False)

# --------------------------------------------------------------------------------------------
print("\n-- 6. content never leaves memory ----------------------------------------------------------")
# --------------------------------------------------------------------------------------------
long_text = "x" * 400
expect("a long string is refused by the content policy",
       lambda: ing.assert_content_free({"a": long_text}), "may carry source content",
       exc=ing.ContentPolicyViolation)
expect("a long string nested in a list is refused too",
       lambda: ing.assert_content_free({"a": [{"b": long_text}]}), "may carry source content",
       exc=ing.ContentPolicyViolation)
expect("an object of an unexpected type is refused",
       lambda: ing.assert_content_free({"a": Path("x")}), "not allowed",
       exc=ing.ContentPolicyViolation)
check("short identifiers and counts pass the policy",
      ing.assert_content_free({"n": 12, "id": "locomo_0_qa0", "ok": True, "none": None}) is None)
check("the ingested structures DO hold text in memory - that is the point of ingestion",
      isinstance(got["conversations"]["locomo_conv_0"]["units"][0]["text"], str))
check("...but the summary derived from them holds none of it",
      all(len(str(v)) <= 400 for v in ing.summarise(got).values())
      and ing.assert_content_free(ing.summarise(got)) is None)

# --------------------------------------------------------------------------------------------
print("\n-- 7. the writer: closed schema, content policy, no overwrite ------------------------------")
# --------------------------------------------------------------------------------------------
out = TMP / "out" / "ingest_manifest.json"
p = ing.write_ingest_manifest(out, ing.summarise(got))
check("a valid summary is written", p.exists())
expect("a second write to the same path is REFUSED",
       lambda: ing.write_ingest_manifest(out, ing.summarise(got)), "refusing to overwrite")
bad = dict(ing.summarise(got)); bad.pop("source_sha256")
expect("a manifest missing a declared field is not written",
       lambda: ing.write_ingest_manifest(TMP / "out" / "a.json", bad), "schema mismatch")
bad2 = dict(ing.summarise(got)); bad2["question_text"] = long_text
expect("a manifest carrying an undeclared field is not written",
       lambda: ing.write_ingest_manifest(TMP / "out" / "b.json", bad2), "schema mismatch")
bad3 = dict(ing.summarise(got)); bad3["content_emitted"] = long_text
expect("a manifest whose declared field carries a long string is refused by the content policy",
       lambda: ing.write_ingest_manifest(TMP / "out" / "c.json", bad3), "may carry source content",
       exc=ing.ContentPolicyViolation)

# --------------------------------------------------------------------------------------------
print("\n-- 8. the bound values, and what is left untouched ------------------------------------------")
# --------------------------------------------------------------------------------------------
check("the LoCoMo source is bound by hash and size",
      ing.BOUND_SOURCES[runner.LOCOMO]["sha256"].startswith("79fa87e9")
      and ing.BOUND_SOURCES[runner.LOCOMO]["bytes"] == 2805274)
check("the LongMemEval source is bound by hash and size",
      ing.BOUND_SOURCES[runner.LONGMEMEVAL]["sha256"].startswith("d6f21ea9")
      and ing.BOUND_SOURCES[runner.LONGMEMEVAL]["bytes"] == 277383467)
check("the LoCoMo mapping is bound to the accepted manifest hash",
      ing.BOUND_MANIFESTS[runner.LOCOMO]["sha256"].startswith("66379b9d"))
check("the LongMemEval mapping is bound to the accepted v2 manifest hash",
      ing.BOUND_MANIFESTS[runner.LONGMEMEVAL]["sha256"].startswith("d5b8ed69"))
check("this module imports no fitting, retrieval or ranking machinery",
      not any(m in src for m in ("TfidfVectorizer", "TruncatedSVD", "sklearn", "haar_q", "hamming_dist")))
check("no cohort selection rule is reimplemented here",
      "category" not in src.replace("category != 5", "").replace("categories", ""),
      "the producer's rule is documented, not re-executed")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILING CHECK(S): {FAILURES}")
    raise SystemExit(1)
print("ALL PASS")
print("Scope: DEVELOPMENT-ENVIRONMENT SYNTHETIC TESTS on fake files. No real corpus was opened, and "
      "this is not authorization to run the ingestion on one.")
raise SystemExit(0)
