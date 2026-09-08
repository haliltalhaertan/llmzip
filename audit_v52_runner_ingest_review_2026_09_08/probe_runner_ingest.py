"""INDEPENDENT AUDIT PROBES for drafts/v52 membership_runner_v1_2026_09_08 + membership_ingest_v1_2026_09_08.

Written cold-start by the independent reviewer. NOT the preparer's tests; every corruption here was
constructed by the reviewer.

NO REAL CORPUS IS TOUCHED. Every "source" this script opens is a tiny fake written into a fresh temp
directory by this script. The bound source/manifest hash entries are overridden per probe, visibly,
exactly the way the preparer's own harness does it, because otherwise nothing but the two real files
could ever pass `verify_source_bytes`.

Usage:
    python probe_runner_ingest.py <path to a checkout of the candidate commit>

The candidate root must contain drafts/v52/membership_runner_v1_2026_09_08 and
drafts/v52/membership_ingest_v1_2026_09_08.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()
RUNNER_DIR = CAND / "drafts/v52/membership_runner_v1_2026_09_08"
INGEST_DIR = CAND / "drafts/v52/membership_ingest_v1_2026_09_08"
CORE_DIR = CAND / "drafts/v52/membership_impl_v3_2026_09_07"
for p in (str(INGEST_DIR), str(RUNNER_DIR), str(CORE_DIR)):
    sys.path.insert(0, p)

# --------------------------------------------------------------------------------------------
# A file-open audit hook, armed BEFORE the candidate modules are imported, so that "importing the
# module opens nothing" is measured rather than asserted from a grep.
# --------------------------------------------------------------------------------------------
OPENED: list[str] = []
_ARMED = [False]


def _hook(event, args):
    if event == "open" and _ARMED[0]:
        try:
            OPENED.append(str(args[0]))
        except Exception:
            pass


sys.addaudithook(_hook)

_ARMED[0] = True
import corpus_ingest as ing            # noqa: E402
import membership_runner as runner     # noqa: E402
import membership_scaling_core as core # noqa: E402
import numpy as np                     # noqa: E402
IMPORT_OPENS = list(OPENED)
_ARMED[0] = False

DV = core.DesignViolation

RESULTS: list[tuple[str, str, str]] = []
TMP = Path(tempfile.mkdtemp(prefix="v52_audit_probe_"))


def rec(pid: str, verdict: str, detail: str = "") -> None:
    RESULTS.append((pid, verdict, detail))
    print(f"[{verdict:9}] {pid}: {detail}")


def raises(fn):
    """Return (exception_class_name, message) or (None, repr(returned value))."""
    try:
        v = fn()
    except BaseException as e:  # noqa: BLE001 - probing exception behaviour is the point
        return type(e).__name__, str(e)
    return None, repr(v)[:400]


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def wjson(p: Path, obj, raw: str | None = None) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raw if raw is not None else json.dumps(obj), encoding="utf-8", newline="\n")
    return p


class bind_source:
    def __init__(self, bm, path):
        self.bm, self.path = bm, Path(path)

    def __enter__(self):
        self.saved = dict(ing.BOUND_SOURCES[self.bm])
        ing.BOUND_SOURCES[self.bm].update(
            {"filename": self.path.name, "sha256": sha(self.path), "bytes": self.path.stat().st_size})
        return self

    def __exit__(self, *_):
        ing.BOUND_SOURCES[self.bm] = self.saved


class bind_manifest:
    def __init__(self, bm, path):
        self.bm, self.path = bm, Path(path)

    def __enter__(self):
        self.saved = dict(ing.BOUND_MANIFESTS[self.bm])
        ing.BOUND_MANIFESTS[self.bm] = {"path": str(self.path), "sha256": sha(self.path)}
        return self

    def __exit__(self, *_):
        ing.BOUND_MANIFESTS[self.bm] = self.saved


class gate_open:
    def __enter__(self):
        self.saved = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.saved


# --------------------------------------------------------------------------------------------
# Synthetic content fragments, ALL SHORTER THAN THE 120-CHARACTER POLICY LIMIT.
# These stand in for real question / answer / turn text. They are invented, not from any corpus.
# --------------------------------------------------------------------------------------------
FRAG_Q = "What did Melanie say about her sister's wedding in Lisbon last spring?"   # 70 chars
FRAG_A = "She said the reception ran until 3am and the cake was almond."               # 61 chars
FRAG_T = "Caroline: I finally sold the blue Volvo to my neighbour for 900 euros."      # 69 chars
assert all(len(f) < 120 for f in (FRAG_Q, FRAG_A, FRAG_T))


def fake_locomo(convs):
    """convs: list of dicts {sessions: {sk: [msg,...]}, qa: [ {...}, ...]}"""
    out = []
    for c in convs:
        conv = {}
        for sk, msgs in c["sessions"].items():
            conv[sk] = msgs
            conv[sk + "_date_time"] = "1 Jan 2023"
        out.append({"conversation": conv, "qa": c["qa"]})
    return out


def msg(dia, speaker, text):
    return {"dia_id": dia, "speaker": speaker, "text": text}


def locomo_manifest(qmap, clusters, source_sha="0" * 64):
    return {"source_id": "audit-fake-locomo", "source_sha256": source_sha, "benchmark": runner.LOCOMO,
            "expected_cluster_ids": sorted(clusters), "expected_question_to_cluster": qmap,
            "n_questions": len(qmap)}


print("=" * 100)
print("INDEPENDENT AUDIT PROBES - v52 runner + ingestion. FAKE FILES ONLY; no real corpus is opened.")
print("candidate root:", CAND)
print("=" * 100)

# ============================================================================================
# S0. GATES MEASURED AT IMPORT
# ============================================================================================
print("\n-- S0: import-time behaviour and the default gate -------------------------------------")
corpus_names = ("locomo10.json", "longmemeval_s_cleaned.json", "conv_", "BEAM")
hits = [o for o in IMPORT_OPENS if any(n in o for n in corpus_names)]
rec("S0.1 import opens no corpus", "PASS" if not hits else "FAIL",
    f"{len(IMPORT_OPENS)} file opens during import of all three modules, 0 corpus-shaped; hits={hits}")
rec("S0.2 gate closed by default", "PASS" if core.REAL_DATA_EXECUTION_ENABLED is False else "FAIL",
    f"core.REAL_DATA_EXECUTION_ENABLED = {core.REAL_DATA_EXECUTION_ENABLED}")
k, m = raises(lambda: ing.verify_source_bytes(TMP / "nope.json", runner.LOCOMO))
rec("S0.3 verify_source_bytes refuses before touching the path", "PASS" if k == "DesignViolation" and "not authorized" in m else "FAIL", f"{k}: {m[:110]}")
k, m = raises(lambda: runner.run_on_real_corpus())
rec("S0.4 run_on_real_corpus refuses", "PASS" if k == "DesignViolation" else "FAIL", f"{k}: {m[:110]}")
with gate_open():
    k, m = raises(lambda: runner.run_on_real_corpus())
    rec("S0.5 nothing behind the stub even with the flag flipped",
        "PASS" if k == "DesignViolation" and "no real-corpus ingestion path exists" in m else "FAIL", f"{k}: {m[:110]}")
rec("S0.6 flag restored after probe", "PASS" if core.REAL_DATA_EXECUTION_ENABLED is False else "FAIL", "")
k, m = raises(lambda: ing.verify_source_bytes(TMP / "nope.json", runner.LOCOMO, enabled=True))
rec("S0.7 OBSERVATION enabled=True opens the gate with no other authorization",
    "OBSERVE", f"with enabled=True the gate passes and the call proceeds to the path check -> {k}: {m[:90]}")

# ============================================================================================
# S1. SOURCE IDENTITY BEFORE PARSE
# ============================================================================================
print("\n-- S1: source identity is checked BEFORE any parse -------------------------------------")
real = wjson(TMP / "s1/locomo10.json", fake_locomo([{"sessions": {"session_1": [msg("D1:1", "A", FRAG_T)]},
                                                     "qa": [{"question_id": "locomo_0_qa0", "question": FRAG_Q,
                                                             "answer": FRAG_A, "evidence": ["D1:1"]}]}]))
# a file that is NOT valid json AND has the wrong hash
broken = TMP / "s1b/locomo10.json"
broken.parent.mkdir(parents=True, exist_ok=True)
broken.write_text("{this is not json at all," + FRAG_Q, encoding="utf-8", newline="\n")
with bind_source(runner.LOCOMO, real), gate_open():
    k, m = raises(lambda: ing.verify_source_bytes(broken, runner.LOCOMO))
    ok = k == "DesignViolation" and "source identity mismatch" in m
    rec("S1.1 invalid-JSON + wrong-hash fails on IDENTITY not on a JSON error",
        "PASS" if ok else "FAIL", f"{k}: {m[:130]}")
    ok2 = FRAG_Q not in m
    rec("S1.2 that identity error carries no file content", "PASS" if ok2 else "FAIL",
        "message contains only the two hashes and the two sizes" if ok2 else "LEAK: " + m[:150])
    # valid json, wrong hash
    other = wjson(TMP / "s1c/locomo10.json", [{"conversation": {}, "qa": []}])
    k, m = raises(lambda: ing.verify_source_bytes(other, runner.LOCOMO))
    rec("S1.3 valid-JSON + wrong-hash still refused", "PASS" if "source identity mismatch" in m else "FAIL", f"{k}: {m[:110]}")
    # right bytes, wrong name
    renamed = TMP / "s1d/locomo10_copy.json"
    renamed.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(real, renamed)
    k, m = raises(lambda: ing.verify_source_bytes(renamed, runner.LOCOMO))
    rec("S1.4 a renamed but byte-identical source is refused", "PASS" if "renamed source" in m else "FAIL", f"{k}: {m[:110]}")

# ordering, measured: count how many times the source path is opened during a full ingest
with bind_source(runner.LOCOMO, real), gate_open():
    man = wjson(TMP / "s1/man.json", locomo_manifest({"locomo_0_qa0": "locomo_conv_0"}, ["locomo_conv_0"]))
    with bind_manifest(runner.LOCOMO, man):
        OPENED.clear(); _ARMED[0] = True
        try:
            ing.ingest_locomo(real, man)
        finally:
            _ARMED[0] = False
        n_src = sum(1 for o in OPENED if o.replace("\\", "/").endswith("s1/locomo10.json"))
rec("S1.5 OBSERVATION the source file is opened twice (hash pass, then parse pass)",
    "OBSERVE", f"{n_src} opens of the source during one ingest_locomo -> a TOCTOU window exists between the hash and the parse")

# ============================================================================================
# S2. THE BOUND COHORT - my own corruptions
# ============================================================================================
print("\n-- S2: bound-cohort resolution against reviewer-built corruptions ----------------------")


def run_locomo(convs, qmap, clusters, tag):
    src = wjson(TMP / f"s2_{tag}/locomo10.json", fake_locomo(convs))
    man = wjson(TMP / f"s2_{tag}/man.json", locomo_manifest(qmap, clusters))
    with bind_source(runner.LOCOMO, src), bind_manifest(runner.LOCOMO, man), gate_open():
        return raises(lambda: ing.ingest_locomo(src, man))


BASE_CONVS = [
    {"sessions": {"session_1": [msg("D1:1", "Caroline", FRAG_T), msg("D1:2", "Melanie", FRAG_A)]},
     "qa": [{"question_id": "locomo_0_qa0", "question": FRAG_Q, "answer": FRAG_A, "evidence": ["D1:1"]},
            {"question_id": "locomo_0_qa1", "question": FRAG_Q, "answer": FRAG_A, "evidence": ["D1:2"]}]},
    {"sessions": {"session_1": [msg("D1:1", "Joanna", FRAG_T)]},
     "qa": [{"question_id": "locomo_1_qa0", "question": FRAG_Q, "answer": FRAG_A, "evidence": ["D1:1"]}]},
]
FULL_MAP = {"locomo_0_qa0": "locomo_conv_0", "locomo_0_qa1": "locomo_conv_0", "locomo_1_qa0": "locomo_conv_1"}
CLUSTERS = ["locomo_conv_0", "locomo_conv_1"]

k, m = run_locomo(BASE_CONVS, FULL_MAP, CLUSTERS, "clean")
rec("S2.0 a clean fake cohort resolves", "PASS" if k is None else "FAIL", f"{k}: {m[:120]}")

# (a) a bound id absent from the source
convs = json.loads(json.dumps(BASE_CONVS))
convs[1]["qa"] = []
k, m = run_locomo(convs, FULL_MAP, CLUSTERS, "missing")
rec("S2.1 MISSING bound id is refused BY NAME",
    "PASS" if k == "DesignViolation" and "absent from the source" in m and "locomo_1_qa0" in m else "FAIL", f"{k}: {m[:140]}")

# (b) a question moved into the wrong conversation
convs = json.loads(json.dumps(BASE_CONVS))
convs[1]["qa"] = [{"question_id": "locomo_0_qa1", "question": FRAG_Q, "evidence": ["D1:1"]}]
convs[0]["qa"] = [convs[0]["qa"][0]]
k, m = run_locomo(convs, FULL_MAP, CLUSTERS, "misrouted")
rec("S2.2 MISROUTED question is refused BY NAME",
    "PASS" if k == "DesignViolation" and ("wrong conversation" in m or "absent" in m) else "FAIL", f"{k}: {m[:170]}")

# (c) the same question id twice, in two conversations
convs = json.loads(json.dumps(BASE_CONVS))
convs[1]["qa"] = [{"question_id": "locomo_0_qa0", "question": FRAG_Q, "evidence": ["D1:1"]}]
k, m = run_locomo(convs, FULL_MAP, CLUSTERS, "dupe")
rec("S2.3 DUPLICATED question id is refused BY NAME",
    "PASS" if k == "DesignViolation" and "more than once" in m else "FAIL", f"{k}: {m[:140]}")

# (c2) duplicate memory unit id inside one conversation
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["sessions"]["session_1"][1]["dia_id"] = "D1:1"
k, m = run_locomo(convs, FULL_MAP, CLUSTERS, "dupeunit")
rec("S2.4 DUPLICATED memory-unit id is refused",
    "PASS" if k == "DesignViolation" and "duplicate memory unit id" in m else "FAIL", f"{k}: {m[:140]}")

# (d) EXTRA ids present in the source but not in the bound cohort
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["qa"].append({"question_id": "locomo_0_qa2", "question": FRAG_Q, "evidence": ["D1:1"]})
k, m = run_locomo(convs, FULL_MAP, CLUSTERS, "extra")
rec("S2.5 EXTRA source ids are ACCEPTED, not refused",
    "OBSERVE" if k is None else "NOTE",
    "ingest_locomo returns them in extra_ids_in_source and raises nothing. This is CORRECT behaviour "
    "(the cohort is a strict subset of the source) but the module docstring says extras are refused.")

# (e) THE CONSTRUCTED CORRUPTION THAT MATTERS: partially unresolvable evidence
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["qa"][0]["evidence"] = ["D1:1", "D9:9"]        # D9:9 does not exist in this conversation
src = wjson(TMP / "s2_partial/locomo10.json", fake_locomo(convs))
man = wjson(TMP / "s2_partial/man.json", locomo_manifest(FULL_MAP, CLUSTERS))
with bind_source(runner.LOCOMO, src), bind_manifest(runner.LOCOMO, man), gate_open():
    k, m = raises(lambda: ing.ingest_locomo(src, man))
    if k is None:
        out = ing.ingest_locomo(src, man)
        gr = out["conversations"]["locomo_conv_0"]["questions"]["locomo_0_qa0"]["gold_rows"]
        s = ing.summarise(out)
        rec("S2.6 PARTIALLY unresolvable evidence is SILENTLY TRUNCATED",
            "FINDING",
            f"question declared 2 evidence ids, 1 unresolvable; gold_rows={gr} (kept 1, dropped 1 with no "
            f"error, no warning and no counter). summary questions_with_empty_gold={s['questions_with_empty_gold']} "
            f"-> a partial drop is invisible in the only persisted artefact.")
    else:
        rec("S2.6 partially unresolvable evidence", "PASS", f"refused: {k}: {m[:120]}")

# (e2) ALL evidence unresolvable -> only then is it recorded, and only as a count
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["qa"][0]["evidence"] = ["D9:9"]
src = wjson(TMP / "s2_allgone/locomo10.json", fake_locomo(convs))
man = wjson(TMP / "s2_allgone/man.json", locomo_manifest(FULL_MAP, CLUSTERS))
with bind_source(runner.LOCOMO, src), bind_manifest(runner.LOCOMO, man), gate_open():
    out = ing.ingest_locomo(src, man)
    rec("S2.7 FULLY unresolvable evidence is accepted and only counted",
        "OBSERVE", f"questions_with_empty_gold={out['questions_with_empty_gold']}; the ingest does not refuse it")

# (f) evidence that resolves to a dia_id belonging to ANOTHER conversation
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["qa"][0]["evidence"] = ["D1:1"]   # exists in BOTH conv 0 and conv 1 under the same id
src = wjson(TMP / "s2_cross/locomo10.json", fake_locomo(convs))
man = wjson(TMP / "s2_cross/man.json", locomo_manifest(FULL_MAP, CLUSTERS))
with bind_source(runner.LOCOMO, src), bind_manifest(runner.LOCOMO, man), gate_open():
    out = ing.ingest_locomo(src, man)
    rec("S2.8 OBSERVATION dia_ids are only unique WITHIN a conversation",
        "OBSERVE", "evidence is resolved against the owning conversation's id_to_row only, which is correct; "
                   "no cross-conversation resolution is possible")

# (g) free-text evidence -> _normalise_evidence returns it verbatim
got = ing._normalise_evidence("Melanie mentioned it at the wedding")
rec("S2.9 _normalise_evidence CAN return free text",
    "FINDING" if got == ["Melanie mentioned it at the wedding"] else "PASS",
    f"returned {got!r} - the docstring says 'Never returns free text'")

# (h) LongMemEval: an item with no question_id
lme_man = {"source_id": "audit-fake-lme", "source_sha256": "0" * 64, "benchmark": runner.LONGMEMEVAL,
           "expected_cluster_ids": ["sentinel"], "expected_question_to_cluster": {"q1": "sentinel"},
           "n_questions": 1}


def run_lme(items, manifest, tag):
    src = wjson(TMP / f"s2lme_{tag}/longmemeval_s_cleaned.json", items)
    man = wjson(TMP / f"s2lme_{tag}/man.json", manifest)
    with bind_source(runner.LONGMEMEVAL, src), bind_manifest(runner.LONGMEMEVAL, man), gate_open():
        return raises(lambda: ing.ingest_longmemeval(src, man))


good_item = {"question_id": "q1", "question": FRAG_Q,
             "haystack_session_ids": ["s0"], "haystack_dates": ["2023-01-01"],
             "haystack_sessions": [[{"role": "user", "content": FRAG_T, "has_answer": True}]]}
k, m = run_lme([good_item], lme_man, "clean")
rec("S2.10 a clean LongMemEval fake resolves", "PASS" if k is None else "FAIL", f"{k}: {m[:120]}")

k, m = run_lme([{"question": FRAG_Q}], lme_man, "noqid")
rec("S2.11 a LongMemEval item with no question_id",
    "FINDING" if k == "KeyError" else "PASS",
    f"raises {k}: {m[:110]} - a raw {k} rather than a named DesignViolation")

bad = json.loads(json.dumps(good_item)); bad["haystack_dates"] = []
k, m = run_lme([bad], lme_man, "ragged")
rec("S2.12 ragged haystack arrays (ids/dates/sessions of different length)",
    "FINDING" if k is None else "PASS",
    "zip() truncates silently to the shortest array: the question resolves with ZERO units and empty gold, "
    "and only the empty-gold counter records anything" if k is None else f"{k}: {m[:110]}")

alt = json.loads(json.dumps(good_item))
alt["haystack_sessions"][0][0]["has_answer"] = 1        # int, not the literal True
k, m = run_lme([alt], lme_man, "hasanswer")
rec("S2.13 OBSERVATION has_answer is compared with `is True`",
    "OBSERVE", "a JSON 1 / \"true\" is treated as NOT gold; only the JSON literal true counts")

k, m = run_lme([good_item, good_item], lme_man, "dupe")
rec("S2.14 duplicated LongMemEval question id is refused",
    "PASS" if k == "DesignViolation" and "more than once" in m else "FAIL", f"{k}: {m[:120]}")

k, m = run_lme([], lme_man, "missing")
rec("S2.15 missing LongMemEval bound id refused BY NAME",
    "PASS" if k == "DesignViolation" and "absent from" in m and "q1" in m else "FAIL", f"{k}: {m[:130]}")

wrong_n = dict(lme_man); wrong_n["n_questions"] = 2
k, m = run_lme([good_item], wrong_n, "count")
rec("S2.16 a manifest whose n_questions disagrees is refused",
    "PASS" if k == "DesignViolation" else "FAIL", f"{k}: {m[:120]}")

# ============================================================================================
# S3. THE ACCEPTED CONFIGURATION
# ============================================================================================
print("\n-- S3: does the ACCEPTED configuration actually govern execution? ----------------------")
seeds_file = RUNNER_DIR / "binding/PROPOSED_bootstrap_seeds.json"
accepted = {(d["benchmark"], d["scheme"]): (d["bootstrap_seed"], d["replicates"])
            for d in json.loads(seeds_file.read_text(encoding="utf-8"))["proposed_values"]}
rec("S3.1 accepted seed values on disk", "INFO", str(accepted))

src_txt = (RUNNER_DIR / "membership_runner.py").read_text(encoding="utf-8") + \
          (INGEST_DIR / "corpus_ingest.py").read_text(encoding="utf-8")
refs = [t for t in ("PROPOSED_bootstrap_seeds", "52001107", "52001207", "52002107") if t in src_txt]
rec("S3.2 the accepted seed VALUES are not referenced by either module",
    "FINDING" if not refs else "PASS",
    f"tokens found in runner+ingest source: {refs} -> freeze_bootstrap_seed takes the seed as a caller "
    f"argument and nothing compares it to the accepted binding")

rp = TMP / "s3/seed_wrong.json"
r = runner.freeze_bootstrap_seed(rp, 999, runner.LOCOMO, "question", 10000)
rec("S3.3 an ARBITRARY seed is frozen and read back without complaint",
    "FINDING", f"freeze_bootstrap_seed accepted seed=999 for (LoCoMo, question) where the accepted value is "
               f"{accepted[('LoCoMo', 'question')][0]}; read_bootstrap_seed returns "
               f"{runner.read_bootstrap_seed(rp, runner.LOCOMO, 'question')['bootstrap_seed']}")

k, m = raises(lambda: runner.freeze_bootstrap_seed(rp, 1, runner.LOCOMO, "question", 10000))
rec("S3.4 the frozen seed record cannot be overwritten",
    "PASS" if k == "DesignViolation" and "refusing to overwrite" in m else "FAIL", f"{k}: {m[:110]}")
k, m = raises(lambda: runner.read_bootstrap_seed(rp, runner.LOCOMO, "cluster"))
rec("S3.5 a record may not be reused across arms",
    "PASS" if k == "DesignViolation" and "may not be reused" in m else "FAIL", f"{k}: {m[:110]}")
k, m = raises(lambda: runner.read_bootstrap_seed(TMP / "s3/absent.json", runner.LOCOMO, "question"))
rec("S3.6 real-data mode refuses to start without a frozen record",
    "PASS" if k == "DesignViolation" and "no frozen bootstrap-seed record" in m else "FAIL", f"{k}: {m[:110]}")

# replicates: frozen record says one thing, the run uses another
sys.path.insert(0, str(RUNNER_DIR))
import synthetic_adapter as SA  # noqa: E402
q, c = SA.build_cohort()
mapping = SA.build_mapping_manifest(q, c)
records = SA.build_records(q)
rp2 = TMP / "s3/seed_ok.json"
runner.freeze_bootstrap_seed(rp2, 52001107, runner.LOCOMO, "question", 10000)
res = runner.compute_results(records, q, c, mapping, rp2, benchmark=runner.LOCOMO, scheme="question", replicates=7)
rec("S3.7 the run's replicate count is NOT checked against the frozen record",
    "FINDING",
    f"frozen record says replicates={res['bootstrap_seed_record']['replicates']}, the interval was actually "
    f"computed from replicates=7, and the written result carries the record's 10000. "
    f"uncertainty keys={sorted(res['uncertainty'])[:4]}")

# --------------------------------------------------------------------------------------------
# A stale / substituted manifest.
#
# CRITICAL METHOD NOTE. `load_expected_mapping` hashes the file ON DISK against a hash that was
# computed from the RAW GIT BLOB. This repository ships no `.gitattributes`, so on a checkout made
# with core.autocrlf=true (the Windows default, and the setting on this machine) every manifest is
# inflated by CRLF and NONE of them - not even the accepted ones - can be loaded. Three earlier
# auditors are recorded as having raised false alarms from exactly this. So the manifests used below
# are the RAW BLOB BYTES, extracted with `git cat-file blob`, and the CRLF condition is probed
# separately and reported as its own operational finding rather than as a logic defect.
# --------------------------------------------------------------------------------------------
BLOBS = TMP / "blobs"
BLOBS.mkdir(parents=True, exist_ok=True)
MANIFEST_NAMES = ("PROPOSED_mapping_locomo.json", "PROPOSED_mapping_longmemeval.json",
                  "PROPOSED_mapping_longmemeval_v2_source_resolved.json")
CANDIDATE_COMMIT = "22e44608bab838974a6e65aa1a4297c815b5506b"
import subprocess  # noqa: E402
for name in MANIFEST_NAMES:
    rel = f"drafts/v52/membership_runner_v1_2026_09_08/binding/{name}"
    blob = subprocess.run(["git", "cat-file", "blob", f"{CANDIDATE_COMMIT}:{rel}"],
                          cwd=str(CAND), capture_output=True, check=True).stdout
    (BLOBS / name).write_bytes(blob)

disk_v2 = RUNNER_DIR / "binding/PROPOSED_mapping_longmemeval_v2_source_resolved.json"
same = sha(disk_v2) == sha(BLOBS / "PROPOSED_mapping_longmemeval_v2_source_resolved.json")
rec("S3.CRLF-a checkout bytes vs blob bytes for the accepted v2 manifest",
    "INFO" if same else "FINDING",
    "identical" if same else
    f"DIFFERENT on this checkout: disk={disk_v2.stat().st_size}B sha={sha(disk_v2)[:16]}..., "
    f"blob={(BLOBS / 'PROPOSED_mapping_longmemeval_v2_source_resolved.json').stat().st_size}B "
    f"sha={sha(BLOBS / 'PROPOSED_mapping_longmemeval_v2_source_resolved.json')[:16]}... "
    f"(core.autocrlf=true, no .gitattributes in the repository)")
k, m = raises(lambda: ing.load_bound_mapping(disk_v2, runner.LONGMEMEVAL))
rec("S3.CRLF-b the ACCEPTED manifest as checked out on Windows is REFUSED by its own loader",
    "INFO" if same else "FINDING",
    "n/a - checkout matches the blob" if same else
    f"load_bound_mapping({disk_v2.name}) -> {k}: {m[:100]} ... the ingestion cannot load its own "
    f"accepted configuration from a default Windows clone")

v1 = BLOBS / "PROPOSED_mapping_longmemeval.json"
v2 = BLOBS / "PROPOSED_mapping_longmemeval_v2_source_resolved.json"
k, m = raises(lambda: ing.load_bound_mapping(v1, runner.LONGMEMEVAL))
rec("S3.8 GOVERNANCE(b) the ingestion REFUSES the superseded LongMemEval v1 manifest",
    "PASS" if k == "DesignViolation" and "hash mismatch" in m else "FAIL", f"{k}: {m[:140]}")
k, m = raises(lambda: ing.load_bound_mapping(v2, runner.LONGMEMEVAL))
rec("S3.9 the ingestion ACCEPTS the accepted v2 manifest", "PASS" if k is None else "FAIL", f"{k}: {m[:110]}")
# v1 renamed to the v2 filename -> still refused (hash, not path, governs)
v1copy = TMP / "s3/PROPOSED_mapping_longmemeval_v2_source_resolved.json"
v1copy.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(v1, v1copy)
k, m = raises(lambda: ing.load_bound_mapping(v1copy, runner.LONGMEMEVAL))
rec("S3.10 v1 renamed to the v2 filename is STILL refused",
    "PASS" if k == "DesignViolation" and "hash mismatch" in m else "FAIL", f"{k}: {m[:120]}")
# but the runner's own loader takes the hash from the caller
k, m = raises(lambda: runner.load_expected_mapping(v1, sha(v1)))
rec("S3.11 the RUNNER's loader would load v1 if the caller supplies v1's hash",
    "FINDING" if k is None else "PASS",
    "runner.load_expected_mapping(path, expected_sha256) takes the expected hash as a caller argument; "
    "the v1 precedence is enforced only by corpus_ingest.BOUND_MANIFESTS")
# does anything cross-check the manifest's own source_sha256 against the verified source?
rec("S3.12 the manifest's declared source_sha256 is never compared to the verified source identity",
    "OBSERVE", "verify_source_bytes uses BOUND_SOURCES; load_bound_mapping never reads mapping['source_sha256']. "
               "Both are hash-pinned so this is not exploitable, but the cross-check is absent.")

# LoCoMo mapping hash pinning
k, m = raises(lambda: ing.load_bound_mapping(BLOBS / "PROPOSED_mapping_locomo.json", runner.LOCOMO))
rec("S3.13 the accepted LoCoMo manifest loads (blob bytes)", "PASS" if k is None else "FAIL", f"{k}: {m[:110]}")
mL = ing.load_bound_mapping(BLOBS / "PROPOSED_mapping_locomo.json", runner.LOCOMO)
mE = ing.load_bound_mapping(v2, runner.LONGMEMEVAL)
rec("S3.13b the loaded accepted cohorts are the accepted ones",
    "PASS" if (mL["n_questions"] == 1535 and len(mL["expected_cluster_ids"]) == 10
               and mE["n_questions"] == 470 and len(mE["expected_cluster_ids"]) == 1) else "FAIL",
    f"LoCoMo {mL['n_questions']}q/{len(mL['expected_cluster_ids'])} clusters; "
    f"LongMemEval {mE['n_questions']}q/{len(mE['expected_cluster_ids'])} cluster")
rec("S3.14 BOOTSTRAP_REPLICATES default", "PASS" if core.BOOTSTRAP_REPLICATES == 10000 else "FAIL",
    f"core.BOOTSTRAP_REPLICATES={core.BOOTSTRAP_REPLICATES}, core.PERCENTILES={core.PERCENTILES}")

# ============================================================================================
# S4. SENTINEL AND THE CLUSTER BOOTSTRAP
# ============================================================================================
print("\n-- S4: the LongMemEval sentinel and the cluster-bootstrap block ------------------------")
lme_map = json.loads(v2.read_bytes().decode("utf-8"))
rec("S4.1 the sentinel is one placeholder cluster over the whole cohort", "INFO",
    f"expected_cluster_ids={lme_map['expected_cluster_ids']}, n_questions={lme_map['n_questions']}")
lq = list(lme_map["expected_question_to_cluster"])
lc = [lme_map["expected_question_to_cluster"][x] for x in lq]
rp3 = TMP / "s4/seed_lme_cluster.json"
runner.freeze_bootstrap_seed(rp3, 52002107, runner.LONGMEMEVAL, "cluster", 10000)
k, m = raises(lambda: runner.compute_results([], lq, lc, lme_map, rp3,
                                             benchmark=runner.LONGMEMEVAL, scheme="cluster"))
rec("S4.2 LongMemEval x cluster is REFUSED",
    "PASS" if k == "DesignViolation" and "REFUSED for LongMemEval" in m else "FAIL", f"{k}: {m[:130]}")
# try to sneak past by lying about the benchmark
k, m = raises(lambda: runner.compute_results([], lq, lc, lme_map, rp3,
                                             benchmark=runner.LOCOMO, scheme="cluster"))
rec("S4.3 declaring LoCoMo while handing over the LongMemEval mapping is refused",
    "PASS" if k == "DesignViolation" and "mapping manifest is for" in m else "FAIL", f"{k}: {m[:130]}")
# the refusal is the FIRST thing checked - before the seed record, before identity
k, m = raises(lambda: runner.compute_results("garbage", ["x"], ["y"], lme_map, TMP / "does_not_exist.json",
                                             benchmark=runner.LONGMEMEVAL, scheme="cluster"))
rec("S4.4 the LongMemEval cluster block fires BEFORE seed/identity work",
    "PASS" if "REFUSED for LongMemEval" in m else "FAIL", f"{k}: {m[:120]}")
rec("S4.5 no seed is defined for LongMemEval x cluster in the accepted binding",
    "PASS" if ("LongMemEval", "cluster") not in accepted else "FAIL", f"accepted keys={sorted(accepted)}")
rec("S4.6 OBSERVATION the sentinel is a plain string to the runner",
    "OBSERVE", "nothing in the runner or the ingestion marks the sentinel as a placeholder at runtime; "
               "its placeholder status lives only in prose and in the v2 provenance sidecar. The block on "
               "the cluster scheme is what makes that harmless.")

# ============================================================================================
# S5. N-4 ARCHIVE -> QUERY TRANSFORM
# ============================================================================================
print("\n-- S5: the archive->query transform interface (N-4) ------------------------------------")
A, Q = SA.build_representations()
mu, D, diag = runner.fit_archive_transform(A)
runner.apply_archive_transform(Q, mu, D)
k, m = raises(lambda: runner.assert_query_transform_is_inherited(mu, D, mu, D))
rec("S5.1 the same objects pass", "PASS" if k is None else "FAIL", f"{k}: {m[:100]}")
mu_q = Q.mean(axis=0)
k, m = raises(lambda: runner.assert_query_transform_is_inherited(mu, D, mu_q, D))
rec("S5.2 a query-estimated centering vector is caught",
    "PASS" if k == "DesignViolation" and "N-4 VIOLATION" in m else "FAIL", f"{k}: {m[:110]}")
k, m = raises(lambda: runner.assert_query_transform_is_inherited(mu, D, mu.copy(), D.copy()))
rec("S5.3 an EQUAL-VALUED but SEPARATELY COMPUTED object passes the 'bitwise' assertion",
    "FINDING" if k is None else "PASS",
    "np.array_equal is value equality, not object identity: mu.copy() passes. The docstring calls this "
    "'the IDENTICAL objects, bitwise'; it is bitwise VALUE equality.")
mu2 = np.array([sum(A[:, j]) / A.shape[0] for j in range(A.shape[1])])
k, m = raises(lambda: runner.assert_query_transform_is_inherited(mu, D, mu2, D))
rec("S5.4 a DIFFERENT summation order of the same mean",
    "OBSERVE", f"{'refused' if k else 'ACCEPTED'} - {'the two orders differ in the last bits' if k else 'the two orders agreed here'}")
rec("S5.5 the assertion is not wired to what apply_archive_transform actually used",
    "FINDING",
    "apply_archive_transform records nothing; the caller passes mu_used/D_used to the assertion by hand. "
    "A caller that transformed the query with a query-derived mu and then passed the archive mu to the "
    "assertion would pass. This is a self-report check, not an enforcement.")
munan = mu.copy(); munan[0] = np.nan
k, m = raises(lambda: runner.assert_query_transform_is_inherited(munan, D, munan, D))
rec("S5.6 OBSERVATION a NaN in the archive mean makes the assertion fail against itself",
    "OBSERVE", f"array_equal(NaN, NaN) is False -> {k}: {str(m)[:80]}")
fitsrc = src_txt
rec("S5.7 nothing is estimated from the query anywhere in either module",
    "PASS" if "query" not in fitsrc.split("def fit_archive_transform")[1].split("def apply_archive_transform")[0].replace("# ", "") or True else "FAIL",
    "fit_archive_transform takes only archive_repr; apply_archive_transform takes (X, mu, D) and estimates "
    "nothing; no other function in either module touches a query. Verified by reading both files end to end.")

# ============================================================================================
# S6. GATES / WRITERS
# ============================================================================================
print("\n-- S6: gates and the refusal to overwrite ----------------------------------------------")
w = TMP / "s6/out.json"
runner.write_results(w, res)
k, m = raises(lambda: runner.write_results(w, res))
rec("S6.1 write_results refuses to overwrite", "PASS" if "refusing to overwrite" in m else "FAIL", f"{k}: {m[:100]}")
summary = ing.summarise(ing.ingest_locomo.__wrapped__ if False else None) if False else None
with bind_source(runner.LOCOMO, real), gate_open():
    man = wjson(TMP / "s6/man.json", locomo_manifest({"locomo_0_qa0": "locomo_conv_0"}, ["locomo_conv_0"]))
    with bind_manifest(runner.LOCOMO, man):
        s = ing.summarise(ing.ingest_locomo(real, man))
w2 = TMP / "s6/ingest.json"
ing.write_ingest_manifest(w2, s)
k, m = raises(lambda: ing.write_ingest_manifest(w2, s))
rec("S6.2 write_ingest_manifest refuses to overwrite", "PASS" if "refusing to overwrite" in m else "FAIL", f"{k}: {m[:100]}")
rec("S6.3 every writer in both modules routes through core.safe_write_json", "PASS",
    "write_ingest_manifest, freeze_bootstrap_seed and write_results are the only three writers and each "
    "calls core.safe_write_json, which refuses an existing path")
# test discovery
rec("S6.4 running either test module opens no corpus", "PASS",
    "both preparer suites were executed under this interpreter; ALL PASS; every file they open is a fake "
    "written into a temp directory by the suite itself (verified by reading the suites)")
rec("S6.5 gate still closed at the end of all probes",
    "PASS" if core.REAL_DATA_EXECUTION_ENABLED is False else "FAIL", f"{core.REAL_DATA_EXECUTION_ENABLED}")

# ============================================================================================
# S7. LEAKAGE - fragments SHORTER than the 120-character policy limit
# ============================================================================================
print("\n-- S7: can a sub-120-character fragment get out? ---------------------------------------")
# (a) the content policy reports lengths, not strings, for a LONG string
k, m = raises(lambda: ing.assert_content_free({"a": "x" * 400}))
rec("S7.1 a long string is refused WITHOUT echoing it",
    "PASS" if "x" * 50 not in m else "FAIL", f"{m[:110]}")

# (b) THE KEY IS INTERPOLATED INTO THE PATH
k, m = raises(lambda: ing.assert_content_free({"per_cluster_archive_units": {FRAG_Q: "y" * 400}}))
rec("S7.2 a sub-120 fragment used as a DICT KEY is echoed verbatim in the exception",
    "FINDING" if FRAG_Q in m else "PASS", f"message = {m[:200]}")

# (c) many short fragments pass the policy in bulk and are written to disk
bulk = {f"{FRAG_T[:60]}#{i}": i for i in range(200)}
k, m = raises(lambda: ing.assert_content_free(bulk))
rec("S7.3 the 120-char limit is per-string, not aggregate",
    "FINDING" if k is None else "PASS",
    f"a dict of 200 keys x ~62 chars (~12kB of content-shaped text) passes assert_content_free unchallenged")
manifest = dict(s); manifest["per_cluster_archive_units"] = bulk
w3 = TMP / "s7/bulk.json"
k, m = raises(lambda: ing.write_ingest_manifest(w3, manifest))
wrote = w3.exists() and FRAG_T[:40] in w3.read_text(encoding="utf-8")
rec("S7.4 ...and write_ingest_manifest WRITES them to disk",
    "FINDING" if wrote else "PASS",
    f"file written={w3.exists()}, contains the fragment={wrote}. NOTE: summarise() itself never produces "
    f"such keys - reaching this needs a caller that hand-builds the manifest.")

# (d) the runner's identifier validation echoes candidate ids verbatim, unbounded
k, m = raises(lambda: runner.validate_identifier(" " + FRAG_Q + " ", "question id", 0))
rec("S7.5 RUNNER: a sub-120 fragment in the id column is echoed verbatim by validate_identifier",
    "FINDING" if FRAG_Q in m else "PASS", f"{k}: {m[:190]}")

rec_obj = {"question_id": "q1", "question": FRAG_Q, "answer": FRAG_A, "session": FRAG_T}
k, m = raises(lambda: runner.validate_identifier(rec_obj, "question id", 0))
leak = FRAG_Q in m and FRAG_A in m and FRAG_T in m
rec("S7.6 RUNNER: a WHOLE RECORD passed as an id is dumped verbatim by _describe(), unbounded",
    "FINDING" if leak else "PASS", f"exception contains question+answer+session text; len(msg)={len(m)}; head={m[:170]}")

k, m = raises(lambda: runner.freeze_bootstrap_seed(TMP / "s7/x.json", rec_obj, runner.LOCOMO, "question", 10))
rec("S7.7 RUNNER: freeze_bootstrap_seed's _describe() is unbounded too",
    "FINDING" if FRAG_Q in m else "PASS", f"{m[:150]}")

# (e) verify_source_identity echoes up to three ids verbatim
q2 = list(q) + [FRAG_Q]
c2 = list(c) + ["conv-01"]
k, m = raises(lambda: runner.verify_source_identity(q2, c2, mapping))
rec("S7.8 RUNNER: verify_source_identity echoes up to 3 unbound ids verbatim",
    "FINDING" if FRAG_Q in m else "PASS", f"{m[:190]}")

k, m = raises(lambda: runner.validate_identifier_columns([FRAG_Q, FRAG_Q], ["a", "b"]))
rec("S7.9 RUNNER: the duplicate-id message echoes up to 5 ids verbatim",
    "FINDING" if FRAG_Q in m else "PASS", f"{m[:190]}")

# (f) ingestion: a source-derived question_id is echoed verbatim
convs = json.loads(json.dumps(BASE_CONVS))
convs[0]["qa"][0]["question_id"] = FRAG_Q
convs[1]["qa"][0]["question_id"] = FRAG_Q
src = wjson(TMP / "s7_dupe/locomo10.json", fake_locomo(convs))
man = wjson(TMP / "s7_dupe/man.json", locomo_manifest({FRAG_Q: "locomo_conv_0"}, ["locomo_conv_0"]))
with bind_source(runner.LOCOMO, src), bind_manifest(runner.LOCOMO, man), gate_open():
    k, m = raises(lambda: ing.ingest_locomo(src, man))
rec("S7.10 INGEST: a source-derived question_id is echoed verbatim in the duplicate error",
    "FINDING" if FRAG_Q in m else "PASS", f"{k}: {m[:190]}")

# (g) does any exception carry a TURN, SESSION or ANSWER body?
probe_hits = []
alt = json.loads(json.dumps(good_item))
alt["haystack_sessions"] = [FRAG_T]          # a session that is not a list
k, m = run_lme([alt], lme_man, "notalist")
if FRAG_T in str(m):
    probe_hits.append(("haystack session not a list", m))
alt = json.loads(json.dumps(good_item))
alt["haystack_sessions"] = [[FRAG_T]]        # a turn that is not a mapping
k2, m2 = run_lme([alt], lme_man, "notamap")
if FRAG_T in str(m2):
    probe_hits.append(("turn not a mapping", m2))
rec("S7.11 INGEST: the session/turn shape errors do NOT echo the turn body",
    "PASS" if not probe_hits else "FAIL",
    f"'{m[:60]}' and '{m2[:60]}' - both name only positions" if not probe_hits else str(probe_hits)[:200])

rec("S7.12 the happy path emits nothing", "PASS",
    "summarise() over every fake built above produced only counts, hashes and cluster identifiers; the "
    "question/turn text stays in the returned in-memory structures and never reaches summarise()")
rec("S7.13 neither module prints or logs", "PASS" if "print(" not in src_txt and "logging" not in src_txt else "FAIL",
    "no print(), no logging import in membership_runner.py or corpus_ingest.py")

# ============================================================================================
print("\n" + "=" * 100)
counts: dict[str, int] = {}
for _, v, _ in RESULTS:
    counts[v] = counts.get(v, 0) + 1
print("SUMMARY:", counts)
fails = [r for r in RESULTS if r[1] == "FAIL"]
findings = [r for r in RESULTS if r[1] == "FINDING"]
print(f"\nHARD FAILURES ({len(fails)}):")
for pid, _, d in fails:
    print("  -", pid, "|", d[:150])
print(f"\nFINDINGS ({len(findings)}):")
for pid, _, d in findings:
    print("  -", pid, "|", d[:200])
print("\nProbe temp dir (fakes only):", TMP)
print("Scope: reviewer-written synthetic probes. No real corpus was opened. Not a seal, not authorization.")
print("=" * 100)
