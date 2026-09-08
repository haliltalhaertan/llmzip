"""INDEPENDENT closure probes for the runner+ingest v2 fix package.

Written cold by the auditor. Does NOT reuse the preparer's fixtures or the previous auditor's probes.

Usage:  python probe_v2_closure.py <checkout-of-9b56968> <repo-root-with-.git>

Every "source" opened here is a small fake written by this script into a fresh temp directory. It has
the SHAPE of the real data and none of its content. No real corpus is read, opened, downloaded or
hashed. Manifests are read as RAW GIT BLOBS (cohort id lists, not corpus).

Bound source/manifest hash entries are overridden per probe, visibly and reversibly, because otherwise
nothing but the two real files could pass verify_source_bytes.
"""
import contextlib
import copy
import hashlib
import inspect
import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

PKG = Path(sys.argv[1]).resolve()
REPO = Path(sys.argv[2]).resolve()
V2 = PKG / "drafts" / "v52" / "membership_runner_ingest_v2_2026_09_08"
V1R = PKG / "drafts" / "v52" / "membership_runner_v1_2026_09_08"
V1I = PKG / "drafts" / "v52" / "membership_ingest_v1_2026_09_08"
CORE = PKG / "drafts" / "v52" / "membership_impl_v3_2026_09_07"

TMP = Path(tempfile.mkdtemp(prefix="probe_v2_"))

# ---------------------------------------------------------------- import-time audit hook (K2)
_OPENS = []
def _hook(event, args):
    if event == "open":
        _OPENS.append(str(args[0]))
sys.addaudithook(_hook)

for p in (V2, CORE, V1R, V1I):
    sys.path.insert(0, str(p))

import numpy as np
import membership_scaling_core as core
import membership_runner_v2 as R2
import corpus_ingest_v2 as I2
import safe_report
from authoritative import accepted_configuration as ACC
from authoritative import resolve_sources as RS

_IMPORT_OPENS = list(_OPENS)

import membership_runner as R1          # v1, unchanged - for my own negative controls
import corpus_ingest as I1              # v1, unchanged

RESULTS = []
def rec(pid, verdict, label, detail=""):
    RESULTS.append((pid, verdict, label, detail))
    print(f"[{verdict:7}] {pid:<10} {label}")
    if detail:
        for line in str(detail).splitlines():
            print(f"                       | {line}")

def raises(fn, *a, **k):
    try:
        return None, fn(*a, **k)
    except BaseException as exc:                                     # noqa: BLE001
        return exc, None

def msg(exc):
    return f"{type(exc).__name__}: {exc}"

# ---------------------------------------------------------------- canaries, all < 120 chars
CANARY = {
    "question": "What did Melanie say about her sister's wedding in Lisbon last spring?",   # 70
    "answer": "She said the ceremony was on a rooftop and it rained.",                      # 53
    "session": "Caroline: I finally told Melanie about the diagnosis.",                     # 53
    "id": "Melanie's private note about the Lisbon trip",                                   # 45
}
for _k, _v in CANARY.items():
    assert len(_v) < 120, (_k, len(_v))

def leaks(text):
    return sorted(k for k, v in CANARY.items() if v in str(text))

@contextlib.contextmanager
def capture():
    out, err = io.StringIO(), io.StringIO()
    box = {"exc": ""}
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            yield box
    except BaseException as exc:                                     # noqa: BLE001
        box["exc"] = "".join(traceback.format_exception(exc))
    finally:
        box["out"] = out.getvalue()
        box["err"] = err.getvalue()
        box["all"] = box["out"] + box["err"] + box["exc"]

# ---------------------------------------------------------------- git blob helpers
def blob(commit, path):
    r = subprocess.run(["git", "-C", str(REPO), "cat-file", "blob", f"{commit}:{path}"],
                       capture_output=True)
    assert r.returncode == 0, (commit, path, r.stderr[:200])
    return r.stdout

def sha(b):
    return hashlib.sha256(b).hexdigest()

# ---------------------------------------------------------------- rebinding helpers
@contextlib.contextmanager
def gate_open():
    old = core.REAL_DATA_EXECUTION_ENABLED
    core.REAL_DATA_EXECUTION_ENABLED = True
    try:
        yield
    finally:
        core.REAL_DATA_EXECUTION_ENABLED = old

@contextlib.contextmanager
def bind_source(bench, path):
    """Point the ACCEPTED source identity at my fake file. Reversible."""
    entry = ACC.ACCEPTED_SOURCES[bench]
    old = dict(entry)
    data = Path(path).read_bytes()
    entry.update({"filename": Path(path).name, "sha256": sha(data), "bytes": len(data)})
    try:
        yield
    finally:
        entry.clear(); entry.update(old)

@contextlib.contextmanager
def bind_manifest(bench, raw):
    """Point the ACCEPTED manifest hash at my fake manifest bytes. Reversible."""
    entry = ACC.ACCEPTED_MANIFESTS[bench]
    old = dict(entry)
    old_bm = copy.deepcopy(I2.BOUND_MANIFESTS)
    entry["blob_sha256"] = sha(raw)
    I2.BOUND_MANIFESTS[bench]["sha256"] = sha(raw)
    try:
        yield
    finally:
        entry.clear(); entry.update(old)
        I2.BOUND_MANIFESTS.clear(); I2.BOUND_MANIFESTS.update(old_bm)

# ---------------------------------------------------------------- fakes (SHAPE only, no real data)
def fake_locomo(n_conv=2, n_q=2, n_turns=3, evidence_for=None, canary=False):
    """evidence_for: {(conv, qpos): [evidence ids]} overrides."""
    convs = []
    for c in range(n_conv):
        conv = {"session_1_date_time": "1 Jan 2024", "session_1": [
            {"dia_id": f"D{c+1}:{t+1}", "speaker": "Caroline",
             "text": CANARY["session"] if canary else f"turn {t}"} for t in range(n_turns)]}
        qa = []
        for q in range(n_q):
            ev = (evidence_for or {}).get((c, q), [f"D{c+1}:1"])
            qa.append({"question_id": f"locomo_{c}_qa{q}",
                       "question": CANARY["question"] if canary else f"q{q}",
                       "answer": CANARY["answer"] if canary else f"a{q}",
                       "evidence": ev, "category": 1})
        convs.append({"conversation": conv, "qa": qa})
    return convs

def locomo_manifest(n_conv=2, n_q=2, benchmark=None):
    q2c = {f"locomo_{c}_qa{q}": f"locomo_conv_{c}" for c in range(n_conv) for q in range(n_q)}
    return {"source_id": "fake-locomo", "source_sha256": "0" * 64,
            "benchmark": benchmark or R2.LOCOMO,
            "expected_cluster_ids": [f"locomo_conv_{c}" for c in range(n_conv)],
            "expected_question_to_cluster": q2c, "n_questions": len(q2c)}

def fake_lme(n_q=2, sessions=2, turns=2, drop=None, ragged=None, has_answer_int=False):
    items = []
    for i in range(n_q):
        item = {"question_id": f"lme_q{i}", "question": f"q{i}",
                "haystack_session_ids": [f"s{j}" for j in range(sessions)],
                "haystack_dates": [f"2024-01-0{j+1}" for j in range(sessions)],
                "haystack_sessions": [[{"role": "user", "content": f"t{t}",
                                        "has_answer": (1 if has_answer_int and t == 0 else
                                                       (True if t == 1 else False))}
                                       for t in range(turns)] for j in range(sessions)]}
        if ragged:
            item[ragged] = item[ragged][:-1]
        if drop:
            item.pop(drop, None)
        items.append(item)
    return items

def lme_manifest(n_q=2):
    q2c = {f"lme_q{i}": "lme_sentinel" for i in range(n_q)}
    return {"source_id": "fake-lme", "source_sha256": "0" * 64, "benchmark": R2.LONGMEMEVAL,
            "expected_cluster_ids": ["lme_sentinel"], "expected_question_to_cluster": q2c,
            "n_questions": len(q2c)}

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json.dumps(obj).encode("utf-8"))
    return path

def raw_of(obj):
    return json.dumps(obj).encode("utf-8")

def records_for(qids):
    out = []
    for i, q in enumerate(qids):
        for s in core.ROTATION_SEEDS:
            for a in core.ARMS:
                out.append({"question_id": q, "rotation_seed": s, "arm": a,
                            "fractional_R3": 0.1 + 0.001 * i + 0.0001 * core.ARMS.index(a)})
    return out


print("=" * 100)
print("SECTION A - environment, imports, gates")
print("=" * 100)

rec("A0", "INFO", "interpreter / numpy",
    f"{sys.version.split()[0]} {sys.version.split('(')[-1][:30]} | numpy {np.__version__} | "
    f"PYTHONHASHSEED={os.environ.get('PYTHONHASHSEED')} OMP={os.environ.get('OMP_NUM_THREADS')}")

corpusish = [o for o in _IMPORT_OPENS
             if any(t in o.lower() for t in ("locomo10", "longmemeval", "conv_", ".json"))]
rec("A1", "PASS" if not corpusish else "FINDING",
    "importing all three v2 modules opens no corpus-shaped file",
    f"{len(_IMPORT_OPENS)} opens during import, {len(corpusish)} corpus-shaped: {corpusish[:3]}")

e, _ = raises(I2.verify_source_bytes, TMP / "nope.json", R2.LOCOMO)
rec("A2", "PASS" if isinstance(e, core.DesignViolation) and "not authorized" in str(e) else "FINDING",
    "the real-data gate is closed by default and is checked first", msg(e))

e, _ = raises(R2.run_on_real_corpus)
rec("A3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "run_on_real_corpus refuses", msg(e))
with gate_open():
    e, _ = raises(R2.run_on_real_corpus)
rec("A4", "PASS" if isinstance(e, core.DesignViolation) and "no real-corpus ingestion path" in str(e)
    else "FINDING", "with the gate deliberately open there is still nothing behind it", msg(e))

repr_tokens = [t for t in ("TfidfVectorizer", "TruncatedSVD", "sklearn", "def fit_representation",
                           "def retrieve", "def rank", "hamming")
               if any(t in (V2 / f).read_text(encoding="utf-8", errors="replace")
                      for f in ("membership_runner_v2.py", "corpus_ingest_v2.py", "safe_report.py"))]
rec("A5", "PASS" if not repr_tokens else "FINDING",
    "the representation stage (M-1/M-2/M-3) was NOT added to this package", f"tokens found: {repr_tokens}")


print()
print("=" * 100)
print("SECTION B - D-4  RAW BYTE DISCIPLINE")
print("=" * 100)

# B1/B2 - the commits named in accepted_configuration really resolve to the accepted blobs
for bench, entry in ACC.ACCEPTED_MANIFESTS.items():
    b = blob(entry["commit"], entry["path"])
    ok = sha(b) == entry["blob_sha256"]
    rec(f"B1.{bench}", "PASS" if ok else "FINDING",
        "the (commit " + entry["commit"][:8] + ", path) pair named in accepted_configuration "
        f"resolves to the accepted blob hash for {bench}",
        f"{len(b)} bytes, sha256 {sha(b)}")

raw_loc = blob(ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["commit"], ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["path"])
raw_lme = blob(ACC.ACCEPTED_MANIFESTS[R2.LONGMEMEVAL]["commit"], ACC.ACCEPTED_MANIFESTS[R2.LONGMEMEVAL]["path"])

e, m = raises(R2.load_accepted_mapping, R2.LOCOMO, raw=raw_loc)
rec("B2", "PASS" if e is None and m["n_questions"] == 1535 else "FINDING",
    "the accepted LoCoMo manifest loads from Git's ORIGINAL BYTES",
    f"n_questions={m['n_questions'] if m else None}, clusters={len(m['expected_cluster_ids']) if m else None}"
    if e is None else msg(e))

e, m = raises(R2.load_accepted_mapping, R2.LONGMEMEVAL, raw=raw_lme)
rec("B3", "PASS" if e is None and m["n_questions"] == 470 else "FINDING",
    "the accepted LongMemEval v2 manifest loads from Git's ORIGINAL BYTES",
    f"n_questions={m['n_questions'] if m else None}, clusters={len(m['expected_cluster_ids']) if m else None}"
    if e is None else msg(e))

# B4 - the CRLF checkout case, using the REAL checked-out file in this worktree
co = PKG / ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["path"]
co_bytes = co.read_bytes()
crlf_n = co_bytes.count(b"\r\n")
same_after_norm = sha(co_bytes.replace(b"\r\n", b"\n")) == ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["blob_sha256"]
rec("B4", "INFO", "this checkout IS CRLF-translated (the D-4 condition is live here)",
    f"checkout {len(co_bytes)} B sha {sha(co_bytes)[:16]}… vs blob {len(raw_loc)} B "
    f"sha {ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]['blob_sha256'][:16]}…, {crlf_n} CRLFs, "
    f"normalises to the accepted hash: {same_after_norm}")

e, _ = raises(R2.load_accepted_mapping, R2.LOCOMO, path=co)
ok = (isinstance(e, core.DesignViolation) and "CRLF" in str(e) and "REFUSED" in str(e))
rec("B5", "PASS" if ok else "FINDING",
    "a CRLF-translated checkout of the accepted manifest is REFUSED, with the line-ending diagnosis",
    msg(e))

e, _ = raises(R2.load_accepted_mapping, R2.LOCOMO, raw=co_bytes)
rec("B6", "PASS" if isinstance(e, core.DesignViolation) and "CRLF" in str(e) else "FINDING",
    "the same CRLF bytes handed in directly as `raw` are also refused (no second, softer door)", msg(e))

e, _ = raises(RS.verify_manifest_bytes, co_bytes, R2.LOCOMO)
rec("B7", "PASS" if isinstance(e, RS.SourceResolutionError) else "FINDING",
    "resolve_sources.verify_manifest_bytes itself refuses the CRLF bytes (the check is not relaxed)",
    msg(e))

# B8 - content substitution must NOT be excused by the diagnosis
tampered = raw_loc.replace(b"locomo_conv_0", b"locomo_conv_9", 1)
e, _ = raises(RS.verify_manifest_bytes, tampered, R2.LOCOMO)
ok = (isinstance(e, RS.SourceResolutionError) and "not a line-ending translation" in str(e))
rec("B8", "PASS" if ok else "FINDING",
    "a genuinely substituted manifest is refused and diagnosed as CONTENT, not as line endings",
    msg(e)[:300])

# B9 - materialisation path
mat = RS.materialize_accepted_manifest(REPO, R2.LOCOMO, TMP / "mat")
mb = mat.read_bytes()
e, m = raises(R2.load_accepted_mapping, R2.LOCOMO, path=mat)
ok = (e is None and sha(mb) == ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["blob_sha256"] and len(mb) == len(raw_loc))
rec("B9", "PASS" if ok else "FINDING",
    "the documented byte-preserving materialisation produces a file that loads",
    f"{len(mb)} bytes, sha {sha(mb)[:16]}…, CRLFs={mb.count(chr(13).encode()+chr(10).encode())}, "
    f"load error={msg(e) if e else 'none'}")

# B10 - is there ANY route that normalises?  grep the package for a normalising accept
srcs = {f: (V2 / f).read_text(encoding="utf-8", errors="replace")
        for f in ("membership_runner_v2.py", "corpus_ingest_v2.py",
                  "authoritative/resolve_sources.py", "authoritative/accepted_configuration.py")}
norm_sites = [(f, i + 1, l.strip()) for f, s in srcs.items() for i, l in enumerate(s.splitlines())
              if ("replace(" in l and ("\\r\\n" in l or "rn" in l)) or "splitlines" in l or "newline=" in l]
rec("B10", "INFO", "every line-ending manipulation site in the package",
    "\n".join(f"{f}:{i} {t}" for f, i, t in norm_sites) or "none")
# the only ones must be inside _diagnose
bad = [x for x in norm_sites if x[0] != "authoritative/resolve_sources.py"]
rec("B11", "PASS" if not bad else "FINDING",
    "line-ending manipulation exists ONLY inside resolve_sources._diagnose (message, never a fallback)",
    f"{bad}")

ga = subprocess.run(["git", "-C", str(REPO), "ls-tree", "-r", "--name-only",
                     "9b569687b394b0507fdeefc5abe456a9958e0788"], capture_output=True, text=True)
has_ga = [l for l in ga.stdout.splitlines() if "gitattributes" in l.lower()]
rec("B12", "PASS" if not has_ga else "FINDING",
    "no .gitattributes was added anywhere at the candidate commit", f"{has_ga}")

cfg = subprocess.run(["git", "-C", str(REPO), "config", "--show-origin", "--get-all", "core.autocrlf"],
                     capture_output=True, text=True)
rec("B13", "INFO", "core.autocrlf as this machine reports it (unchanged, still true)",
    cfg.stdout.strip() or "(unset)")
loc = subprocess.run(["git", "-C", str(REPO), "config", "--local", "--list"],
                     capture_output=True, text=True)
eol_local = [l for l in loc.stdout.splitlines() if "autocrlf" in l or "eol" in l or "safecrlf" in l]
rec("B14", "PASS" if not eol_local else "FINDING",
    "the clone's LOCAL git config sets no line-ending override", f"{eol_local}")


print()
print("=" * 100)
print("SECTION C - D-3  the accepted seed values must govern")
print("=" * 100)

seeddir = TMP / "seeds"
seeddir.mkdir(parents=True, exist_ok=True)

e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "s999.json", 999, R2.LOCOMO, "question", 10000)
ok = isinstance(e, core.DesignViolation) and "52001107" in str(e) and not (seeddir / "s999.json").exists()
rec("C1", "PASS" if ok else "FINDING", "seed 999 is REFUSED and nothing is written", msg(e))

e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "st.json", 52001170, R2.LOCOMO, "question", 10000)
rec("C2", "PASS" if isinstance(e, core.DesignViolation) and "52001107" in str(e) else "FINDING",
    "the TRANSPOSED digit 52001170 is refused", msg(e))

e, r = raises(R2.freeze_bootstrap_seed, seeddir / "good.json", 52001107, R2.LOCOMO, "question", 10000)
rec("C3", "PASS" if e is None and r["bootstrap_seed"] == 52001107 else "FINDING",
    "the ACCEPTED seed 52001107 is accepted", msg(e) if e else json.dumps(r))

# C4 - hand-edit a frozen record
bad_rec = json.loads((seeddir / "good.json").read_text())
bad_rec["bootstrap_seed"] = 999
write_json(seeddir / "edited.json", bad_rec)
e, _ = raises(R2.read_bootstrap_seed, seeddir / "edited.json", R2.LOCOMO, "question")
rec("C4", "PASS" if isinstance(e, core.DesignViolation) and "accepted" in str(e) else "FINDING",
    "a HAND-EDITED frozen record carrying seed 999 is caught on read", msg(e))

bad_rec2 = json.loads((seeddir / "good.json").read_text()); bad_rec2["bootstrap_seed"] = 52001170
write_json(seeddir / "edited2.json", bad_rec2)
e, _ = raises(R2.read_bootstrap_seed, seeddir / "edited2.json", R2.LOCOMO, "question")
rec("C5", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a hand-edited record carrying the transposed seed is caught on read", msg(e))

# C6 - a record never produced by freeze at all
write_json(seeddir / "forged.json", {"bootstrap_seed": 999, "benchmark": R2.LOCOMO,
                                     "scheme": "question", "replicates": 10000,
                                     "frozen_before_any_result": True, "runner_version": "hand-made"})
e, _ = raises(R2.read_bootstrap_seed, seeddir / "forged.json", R2.LOCOMO, "question")
rec("C6", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a record forged by hand (never through freeze_bootstrap_seed) is refused on read", msg(e))

e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "lme_c.json", 52002107, R2.LONGMEMEVAL, "cluster", 10000)
rec("C7", "PASS" if isinstance(e, core.DesignViolation) and "no accepted bootstrap" in str(e) else "FINDING",
    "(LongMemEval, cluster) is refused - its ABSENCE from the accepted config is the authority", msg(e))

e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "b.json", True, R2.LOCOMO, "question", 10000)
rec("C8", "PASS" if isinstance(e, core.DesignViolation) else "FINDING", "a bool seed is refused", msg(e))
e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "np.json", np.int64(52001107), R2.LOCOMO, "question", 10000)
rec("C9", "OBSERVE", "a numpy int64 carrying the accepted value", msg(e) if e else "ACCEPTED")

# C10 - my own v1 negative control, run against the v1 module
v1seed = TMP / "v1seeds"; v1seed.mkdir(parents=True, exist_ok=True)
e1, r1 = raises(R1.freeze_bootstrap_seed, v1seed / "s.json", 999, R1.LOCOMO, "question", 10000)
e2, r2 = raises(R1.read_bootstrap_seed, v1seed / "s.json", R1.LOCOMO, "question")
ok = e1 is None and e2 is None and r2["bootstrap_seed"] == 999
rec("C10", "PASS" if ok else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 accepts seed 999 and reads it back (old behaviour reproduced)",
    f"v1 froze and returned bootstrap_seed={r2['bootstrap_seed'] if r2 else None}")


print()
print("=" * 100)
print("SECTION D - D-2  the replicate count must match the frozen record")
print("=" * 100)

e, _ = raises(R2.freeze_bootstrap_seed, seeddir / "r7.json", 52001107, R2.LOCOMO, "question", 7)
rec("D1", "PASS" if isinstance(e, core.DesignViolation) and "10000" in str(e) else "FINDING",
    "freezing a record with replicates=7 is refused", msg(e))

r7 = json.loads((seeddir / "good.json").read_text()); r7["replicates"] = 7
write_json(seeddir / "r7edit.json", r7)
e, _ = raises(R2.read_bootstrap_seed, seeddir / "r7edit.json", R2.LOCOMO, "question")
rec("D2", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a hand-edited record claiming replicates=7 is caught on read", msg(e))

# full compute_results chain on a fake cohort
man = locomo_manifest(2, 2)
mraw = raw_of(man)
with bind_manifest(R2.LOCOMO, mraw):
    mapping = R2.load_accepted_mapping(R2.LOCOMO, raw=mraw)
    qids = list(mapping["expected_question_to_cluster"])
    cids = [mapping["expected_question_to_cluster"][q] for q in qids]
    recs = records_for(qids)
    e, _ = raises(R2.compute_results, recs, qids, cids, mapping, seeddir / "good.json",
                  benchmark=R2.LOCOMO, scheme="question", replicates=7)
    ok = isinstance(e, core.DesignViolation) and "contradicts the frozen seed record" in str(e)
    rec("D3", "PASS" if ok else "FINDING",
        "compute_results REFUSES a run whose replicate count contradicts the frozen record", msg(e))

    e, res = raises(R2.compute_results, recs, qids, cids, mapping, seeddir / "good.json",
                    benchmark=R2.LOCOMO, scheme="question", replicates=10000)
    ok = e is None and res["bootstrap_seed_record"]["replicates"] == 10000
    rec("D4", "PASS" if ok else "FINDING",
        "the honest run (10000) succeeds and the persisted record states 10000",
        msg(e) if e else f"n_questions={res['n_questions']} seed={res['bootstrap_seed_record']['bootstrap_seed']}")

    e, _ = raises(R2.compute_results, recs, qids, cids, mapping, seeddir / "good.json",
                  benchmark=R2.LOCOMO, scheme="question", replicates=True)
    rec("D5", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
        "a bool replicate count is refused", msg(e))

    # D6 - is there ANY route into compute_results that skips read_bootstrap_seed?
    sig = inspect.signature(R2.compute_results)
    rec("D6", "PASS" if "seed_record" not in sig.parameters else "FINDING",
        "compute_results takes only a seed record PATH, so the record cannot be handed in pre-made",
        str(sig))

# D7 - my own v1 negative control
with bind_manifest(R2.LOCOMO, mraw):
    pass
v1man = TMP / "v1man.json"; v1man.write_bytes(mraw)
m1 = R1.load_expected_mapping(v1man, sha(mraw))
q1 = list(m1["expected_question_to_cluster"]); c1 = [m1["expected_question_to_cluster"][q] for q in q1]
R1.freeze_bootstrap_seed(v1seed / "d2.json", 52001107, R1.LOCOMO, "question", 10000)
e, res1 = raises(R1.compute_results, records_for(q1), q1, c1, m1, v1seed / "d2.json",
                 benchmark=R1.LOCOMO, scheme="question", replicates=7)
ok = e is None and res1["bootstrap_seed_record"]["replicates"] == 10000
rec("D7", "PASS" if ok else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 runs 7 replicates and persists a record claiming 10000",
    msg(e) if e else f"record.replicates={res1['bootstrap_seed_record']['replicates']}, "
                     f"actually ran replicates=7")


print()
print("=" * 100)
print("SECTION E - D-1  evidence accounting")
print("=" * 100)

def run_ingest(src_obj, man_obj, **kw):
    src = write_json(TMP / f"e{len(RESULTS)}" / "locomo10.json", src_obj)
    mraw = raw_of(man_obj)
    with gate_open(), bind_source(R2.LOCOMO, src), bind_manifest(R2.LOCOMO, mraw):
        mapping = R2.load_accepted_mapping(R2.LOCOMO, raw=mraw)
        return raises(I2.ingest_locomo, src, mapping, **kw), mapping

# E1 clean
(e, ing), mp = run_ingest(fake_locomo(2, 2), locomo_manifest(2, 2))
summ = I2.summarise(ing) if e is None else None
ok = (e is None and ing["evidence_tally"] == {"declared": 4, "resolved": 4, "unresolved": 0}
      and summ["evidence_ids_unresolved"] == 0 and summ["questions_with_partial_evidence_loss"] == 0)
rec("E1", "PASS" if ok else "FINDING", "a CLEAN source reports declared==resolved, unresolved 0",
    msg(e) if e else json.dumps({k: summ[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_empty_gold", "questions_with_partial_evidence_loss")}))

# E2 partial loss, no waiver -> must STOP
partial = fake_locomo(2, 2, evidence_for={(0, 0): ["D1:1", "D1:99"]})
(e, ing), mp = run_ingest(partial, locomo_manifest(2, 2))
ok = isinstance(e, core.DesignViolation) and "PARTIALLY unresolvable" in str(e)
rec("E2", "PASS" if ok else "FINDING",
    "a PARTIAL evidence loss STOPS the ingestion with a NAMED violation", msg(e))

# E3 waiver without citation
(e, ing), mp = run_ingest(partial, locomo_manifest(2, 2), allow_partial_evidence=True)
ok = isinstance(e, core.DesignViolation) and "requires partial_evidence_citation" in str(e)
rec("E3", "PASS" if ok else "FINDING", "a waiver WITHOUT a citation is refused", msg(e))
(e, ing), mp = run_ingest(partial, locomo_manifest(2, 2), allow_partial_evidence=True,
                          partial_evidence_citation="")
rec("E4", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "an EMPTY-STRING citation is refused too", msg(e))

# E5 waiver with citation
(e, ing), mp = run_ingest(partial, locomo_manifest(2, 2), allow_partial_evidence=True,
                          partial_evidence_citation="LOCOMO_SELECTION_RULE_NOTE_2026-09-08.md sec 3")
summ = I2.summarise(ing) if e is None else None
ok = (e is None and ing["evidence_tally"] == {"declared": 5, "resolved": 4, "unresolved": 1}
      and summ["questions_with_partial_evidence_loss"] == 1 and summ["evidence_ids_unresolved"] == 1)
rec("E5", "PASS" if ok else "FINDING",
    "with a CITED waiver the loss is published: declared/resolved/unresolved and a partial-loss count",
    msg(e) if e else json.dumps({k: summ[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_empty_gold", "questions_with_partial_evidence_loss")}))

# E6 - IS THE WAIVER ITSELF RECORDED IN THE PERSISTED ARTEFACT?
in_summary = [k for k in (summ or {}) if "waiver" in k or "citation" in k]
in_schema = [k for k in I2.INGEST_MANIFEST_KEYS if "waiver" in k or "citation" in k]
rec("E6", "PASS" if in_summary and in_schema else "FINDING",
    "the WAIVER and its CITATION appear in the written manifest",
    f"summary keys carrying it: {in_summary or 'NONE'}; schema keys: {in_schema or 'NONE'}; "
    f"in-memory only: partial_evidence_waiver={ing['partial_evidence_waiver'] if ing else None}")

# can it even be added?
if summ is not None:
    tampered_summary = dict(summ); tampered_summary["partial_evidence_waiver"] = {"allowed": True}
    e2, _ = raises(I2.write_ingest_manifest, TMP / "w1.json", tampered_summary)
    rec("E7", "OBSERVE", "the closed manifest schema forbids adding the waiver to the artefact", msg(e2))

# E8 - slip-through attempt: ALL evidence unresolvable (not 'partial')
allbad = fake_locomo(2, 2, evidence_for={(0, 0): ["D1:98", "D1:99"]})
(e, ing), mp = run_ingest(allbad, locomo_manifest(2, 2))
summ8 = I2.summarise(ing) if e is None else None
ok = e is None and summ8["evidence_ids_unresolved"] == 2 and summ8["questions_with_empty_gold"] == 1
rec("E8", "PASS" if ok else "FINDING",
    "SLIP-THROUGH ATTEMPT: a TOTAL evidence loss is not 'partial' - is it still visible?",
    msg(e) if e else json.dumps({k: summ8[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_empty_gold", "questions_with_partial_evidence_loss")}))

# E9 - slip-through attempt: free-text evidence (the C-4 fallback)
freetext = fake_locomo(2, 2, evidence_for={(0, 0): "Melanie mentioned it at the wedding"})
(e, ing), mp = run_ingest(freetext, locomo_manifest(2, 2))
summ9 = I2.summarise(ing) if e is None else None
rec("E9", "OBSERVE", "SLIP-THROUGH ATTEMPT: free-text evidence (no D<n>:<n> match)",
    msg(e) if e else json.dumps({k: summ9[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_empty_gold", "questions_with_partial_evidence_loss")}))

# E10 - slip-through attempt: evidence declared TWICE, resolving to ONE row
dupev = fake_locomo(2, 2, evidence_for={(0, 0): "see D1:1 and also D1:1"})
(e, ing), mp = run_ingest(dupev, locomo_manifest(2, 2))
summ10 = I2.summarise(ing) if e is None else None
rec("E10", "OBSERVE", "SLIP-THROUGH ATTEMPT: the same evidence id declared twice in a string",
    msg(e) if e else json.dumps({k: summ10[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_partial_evidence_loss")}))

# E11 - GOLD / COHORT SEMANTICS UNCHANGED between v1 and v2 on a clean source
clean = fake_locomo(2, 2)
src = write_json(TMP / "cmp" / "locomo10.json", clean)
mraw = raw_of(locomo_manifest(2, 2))
v1m = TMP / "cmp" / "man.json"; v1m.write_bytes(mraw)
old_src = dict(I1.BOUND_SOURCES[R1.LOCOMO]); old_man = dict(I1.BOUND_MANIFESTS[R1.LOCOMO])
I1.BOUND_SOURCES[R1.LOCOMO].update({"filename": "locomo10.json", "sha256": sha(src.read_bytes()),
                                    "bytes": len(src.read_bytes())})
I1.BOUND_MANIFESTS[R1.LOCOMO].update({"path": str(v1m), "sha256": sha(mraw)})
with gate_open():
    m_v1 = R1.load_expected_mapping(v1m, sha(mraw))
    ing1 = I1.ingest_locomo(src, v1m)
I1.BOUND_SOURCES[R1.LOCOMO].clear(); I1.BOUND_SOURCES[R1.LOCOMO].update(old_src)
I1.BOUND_MANIFESTS[R1.LOCOMO].clear(); I1.BOUND_MANIFESTS[R1.LOCOMO].update(old_man)

(e, ing2), mp = run_ingest(clean, locomo_manifest(2, 2))
g1 = {q: v["gold_rows"] for c in ing1["conversations"].values() for q, v in c["questions"].items()}
g2 = {q: v["gold_rows"] for c in ing2["conversations"].values() for q, v in c["questions"].items()}
ok = g1 == g2 and ing1["cohort_ids"] == ing2["cohort_ids"] and len(g1) == 4
rec("E11", "PASS" if ok else "FINDING",
    "GOLD ROWS and COHORT are BYTE-IDENTICAL between v1 and v2 on a clean source "
    "(nothing newly excluded, repaired or re-cohorted)",
    f"v1 gold={g1}\nv2 gold={g2}\ncohort equal={ing1['cohort_ids'] == ing2['cohort_ids']}")

# E12 - my own v1 negative control for D-1 itself
partial_src = write_json(TMP / "negd1" / "locomo10.json",
                         fake_locomo(2, 2, evidence_for={(0, 0): ["D1:1", "D1:99"]}))
old_src = dict(I1.BOUND_SOURCES[R1.LOCOMO])
I1.BOUND_SOURCES[R1.LOCOMO].update({"filename": "locomo10.json",
                                    "sha256": sha(partial_src.read_bytes()),
                                    "bytes": len(partial_src.read_bytes())})
I1.BOUND_MANIFESTS[R1.LOCOMO].update({"path": str(v1m), "sha256": sha(mraw)})
with gate_open():
    e, ingp = raises(I1.ingest_locomo, partial_src, v1m)
s1 = I1.summarise(ingp) if e is None else None
I1.BOUND_SOURCES[R1.LOCOMO].clear(); I1.BOUND_SOURCES[R1.LOCOMO].update(old_src)
I1.BOUND_MANIFESTS[R1.LOCOMO].clear(); I1.BOUND_MANIFESTS[R1.LOCOMO].update(old_man)
ok = (e is None and s1["questions_with_empty_gold"] == 0
      and not any("evidence" in k for k in s1))
rec("E12", "PASS" if ok else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 ACCEPTS the partial loss, reports empty_gold=0 and "
    "publishes NO evidence accounting",
    msg(e) if e else f"v1 summary keys = {sorted(s1)}")


print()
print("=" * 100)
print("SECTION F - D-5  error and output paths  (pressed hardest)")
print("=" * 100)

def probe_leak(pid, label, fn, expect_clean=True):
    with capture() as box:
        fn()
    got = leaks(box["all"])
    verdict = "PASS" if (not got) == expect_clean else "FINDING"
    rec(pid, verdict, label,
        f"canaries in stdout/stderr/exception text: {got or 'none'}"
        + (f"\nmessage: {box['all'].strip().splitlines()[-1][:220]}" if box["all"].strip() else ""))
    return got

# --- the seven v1 paths, re-run against v2 with MY canaries
probe_leak("F1", "validate_identifier: whitespace branch",
           lambda: R2.validate_identifier(" " + CANARY["id"], "question id", 0))
probe_leak("F2", "validate_identifier: unsupported type (a whole record dict) - v1's _describe path",
           lambda: R2.validate_identifier({"question": CANARY["question"], "answer": CANARY["answer"],
                                           "session": CANARY["session"]}, "question id", 0))
probe_leak("F3", "freeze_bootstrap_seed: a non-int seed carrying a record dict",
           lambda: R2.freeze_bootstrap_seed(TMP / "f3.json",
                                            {"q": CANARY["question"]}, R2.LOCOMO, "question", 10000))
probe_leak("F4", "validate_identifier_columns: duplicate ids",
           lambda: R2.validate_identifier_columns([CANARY["id"], CANARY["id"]], ["c", "c"]))

_m = locomo_manifest(2, 2)
probe_leak("F5", "verify_source_identity: unbound (extra) ids",
           lambda: R2.verify_source_identity(list(_m["expected_question_to_cluster"]) + [CANARY["id"]],
                                             [_m["expected_question_to_cluster"][q]
                                              for q in _m["expected_question_to_cluster"]] + ["locomo_conv_0"],
                                             _m))
probe_leak("F6", "verify_source_identity: missing ids",
           lambda: R2.verify_source_identity(list(_m["expected_question_to_cluster"])[:-1],
                                             [_m["expected_question_to_cluster"][q]
                                              for q in list(_m["expected_question_to_cluster"])[:-1]],
                                             _m))
probe_leak("F7", "assert_content_free: a sub-120 dict KEY beside a failing sibling",
           lambda: I2.assert_content_free({CANARY["question"]: 1, "x": "y" * 400}))

def _dup():
    src = write_json(TMP / "f8" / "locomo10.json",
                     [{"conversation": {"session_1": [{"dia_id": "D1:1", "speaker": "a", "text": "t"}]},
                       "qa": [{"question_id": CANARY["id"], "question": CANARY["question"],
                               "answer": CANARY["answer"], "evidence": ["D1:1"]},
                              {"question_id": CANARY["id"], "question": "q", "answer": "a",
                               "evidence": ["D1:1"]}]}])
    mraw = raw_of(locomo_manifest(1, 1))
    with gate_open(), bind_source(R2.LOCOMO, src), bind_manifest(R2.LOCOMO, mraw):
        I2.ingest_locomo(src, R2.load_accepted_mapping(R2.LOCOMO, raw=mraw))
probe_leak("F8", "ingest_locomo: a duplicate source question_id that IS a text fragment", _dup)

def _lme_bad():
    src = write_json(TMP / "f9" / "longmemeval_s_cleaned.json",
                     [{"question_id": CANARY["id"], "question": CANARY["question"],
                       "haystack_session_ids": ["s0"], "haystack_dates": [],
                       "haystack_sessions": [[{"role": "user", "content": CANARY["session"],
                                               "has_answer": True}]]}])
    mraw = raw_of({"source_id": "f", "source_sha256": "0" * 64, "benchmark": R2.LONGMEMEVAL,
                   "expected_cluster_ids": ["lme_sentinel"],
                   "expected_question_to_cluster": {CANARY["id"]: "lme_sentinel"}, "n_questions": 1})
    with gate_open(), bind_source(R2.LONGMEMEVAL, src), bind_manifest(R2.LONGMEMEVAL, mraw):
        I2.ingest_longmemeval(src, R2.load_accepted_mapping(R2.LONGMEMEVAL, raw=mraw))
probe_leak("F9", "ingest_longmemeval: ragged haystack whose ids/content are canaries", _lme_bad)

def _happy():
    src = write_json(TMP / "f10" / "locomo10.json", fake_locomo(1, 1, canary=True))
    mraw = raw_of(locomo_manifest(1, 1))
    with gate_open(), bind_source(R2.LOCOMO, src), bind_manifest(R2.LOCOMO, mraw):
        ing = I2.ingest_locomo(src, R2.load_accepted_mapping(R2.LOCOMO, raw=mraw))
        s = I2.summarise(ing)
        I2.write_ingest_manifest(TMP / "f10" / "out.json", s)
        assert CANARY["question"] in json.dumps(ing["conversations"]), "text must still be in memory"
probe_leak("F10", "the HAPPY path with every canary in the source: nothing on stdout/stderr", _happy)
written = (TMP / "f10" / "out.json").read_text(encoding="utf-8") if (TMP / "f10" / "out.json").exists() else ""
rec("F11", "PASS" if not leaks(written) else "FINDING",
    "the WRITTEN manifest from a fully-canaried source carries no canary",
    f"{len(written)} bytes written, canaries: {leaks(written) or 'none'}")

print("--- paths the preparer did not test ---")
# F12 - compute_results echoes mapping['benchmark'] BEFORE the accepted-stamp check
def _f12():
    R2.compute_results([], [], [], {"benchmark": CANARY["question"]}, TMP / "nope.json",
                       benchmark=R2.LOCOMO, scheme="question")
probe_leak("F12", "compute_results: mapping['benchmark'] is interpolated verbatim, BEFORE the stamp check",
           _f12)

# F13 - unknown benchmark / scheme echo the caller's string verbatim
probe_leak("F13", "compute_results: an unknown `benchmark` argument is echoed verbatim",
           lambda: R2.compute_results([], [], [], {}, TMP / "n.json",
                                      benchmark=CANARY["question"], scheme="question"))
probe_leak("F14", "compute_results: an unknown `scheme` argument is echoed verbatim",
           lambda: R2.compute_results([], [], [], {}, TMP / "n.json",
                                      benchmark=R2.LOCOMO, scheme=CANARY["answer"]))
probe_leak("F15", "accepted_bootstrap_for / freeze_bootstrap_seed echo an unknown benchmark verbatim",
           lambda: R2.freeze_bootstrap_seed(TMP / "f15.json", 1, CANARY["question"], "question", 10000))
probe_leak("F16", "load_accepted_mapping echoes an unknown benchmark verbatim",
           lambda: R2.load_accepted_mapping(CANARY["question"], raw=b"{}"))
probe_leak("F17", "resolve_sources.resolve_accepted_manifest echoes an unknown benchmark verbatim",
           lambda: RS.resolve_accepted_manifest(REPO, CANARY["answer"]))
probe_leak("F18", "corpus_ingest.verify_source_bytes echoes an unknown benchmark verbatim",
           lambda: I2.verify_source_bytes(TMP / "x.json", CANARY["question"], enabled=True))

# F19 - a source PATH containing a fragment
def _f19():
    p = TMP / "f19" / (CANARY["id"].replace("/", "_") + ".json")
    p.parent.mkdir(parents=True, exist_ok=True)
    I2.verify_source_bytes(p, R2.LOCOMO, enabled=True)
probe_leak("F19", "corpus_ingest.verify_source_bytes echoes the missing source PATH verbatim", _f19)

# F20 - values read back OUT OF THE FROZEN SEED RECORD FILE are interpolated verbatim
def _f20():
    write_json(TMP / "f20.json", {"bootstrap_seed": 1, "benchmark": CANARY["question"],
                                  "scheme": CANARY["answer"], "replicates": 10000})
    R2.read_bootstrap_seed(TMP / "f20.json", R2.LOCOMO, "question")
probe_leak("F20", "read_bootstrap_seed interpolates FILE-DERIVED benchmark/scheme values verbatim", _f20)

# F21 - can PARSED CORPUS content (question/answer/session text) reach a message anywhere?
def _f21():
    # every ingestion failure mode I can reach, on a fully-canaried source
    src = write_json(TMP / "f21" / "locomo10.json",
                     fake_locomo(2, 2, evidence_for={(0, 0): ["D1:1", "D1:99"]}, canary=True))
    mraw = raw_of(locomo_manifest(2, 2))
    with gate_open(), bind_source(R2.LOCOMO, src), bind_manifest(R2.LOCOMO, mraw):
        I2.ingest_locomo(src, R2.load_accepted_mapping(R2.LOCOMO, raw=mraw))
probe_leak("F21", "the D-1 partial-loss refusal on a fully-canaried source", _f21)

def _f22():
    src = write_json(TMP / "f22" / "locomo10.json", fake_locomo(2, 2, canary=True))
    mraw = raw_of(locomo_manifest(3, 2))          # manifest expects a conversation the source lacks
    with gate_open(), bind_source(R2.LOCOMO, src), bind_manifest(R2.LOCOMO, mraw):
        I2.ingest_locomo(src, R2.load_accepted_mapping(R2.LOCOMO, raw=mraw))
probe_leak("F22", "the missing-cohort-id refusal on a fully-canaried source", _f22)

# F23 - my own v1 negative controls for D-5
def _v1_desc():
    R1.validate_identifier({"question": CANARY["question"], "answer": CANARY["answer"],
                            "session": CANARY["session"]}, "question id", 0)
got = probe_leak("F23", "MY OWN v1 NEGATIVE CONTROL: v1 _describe() dumps a whole record dict",
                 _v1_desc, expect_clean=False)
got2 = probe_leak("F24", "MY OWN v1 NEGATIVE CONTROL: v1 validate_identifier whitespace branch",
                  lambda: R1.validate_identifier(" " + CANARY["id"], "question id", 0),
                  expect_clean=False)
got3 = probe_leak("F25", "MY OWN v1 NEGATIVE CONTROL: v1 assert_content_free echoes a sub-120 KEY",
                  lambda: I1.assert_content_free({CANARY["question"]: 1, "x": "y" * 400}),
                  expect_clean=False)


print()
print("=" * 100)
print("SECTION G - D-6  the archive-learned transform must be shown to have been USED")
print("=" * 100)

rng = np.random.default_rng(7)
A = rng.normal(size=(40, core.DIM))
Q = rng.normal(size=(5, core.DIM))
mu, D, diag = R2.fit_archive_transform(A)

sig = inspect.signature(R2.assert_query_transform_is_inherited)
rec("G0", "PASS" if list(sig.parameters) == ["mu_archive", "D_archive", "query_stamp"] else "FINDING",
    "the assertion no longer takes caller-supplied mu_used/D_used echoes", str(sig))

tq, stamp = R2.apply_archive_transform(Q, mu, D)
e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, stamp)
rec("G1", "PASS" if e is None else "FINDING", "the honest path passes", msg(e) if e else "ok")

mu_q = Q.mean(axis=0)
_, bad_stamp = R2.apply_archive_transform(Q, mu_q, D)
e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, bad_stamp)
ok = isinstance(e, core.DesignViolation) and "N-4 VIOLATION" in str(e)
rec("G2", "PASS" if ok else "FINDING",
    "a WRONG CENTERING (query-derived mu) is caught - the exact v1 bypass", msg(e))

D_bad = D.copy(); D_bad[0, 0] = np.nextafter(D_bad[0, 0], np.inf)
_, bad_stamp2 = R2.apply_archive_transform(Q, mu, D_bad)
e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, bad_stamp2)
rec("G3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a WRONG D, perturbed by ONE ULP, is caught", msg(e)[:160])

_, cstamp = R2.apply_archive_transform(Q, mu.copy(), D.copy())
e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, cstamp)
rec("G4", "OBSERVE" if e is None else "FINDING",
    "copies still pass - but v2 no longer claims 'IDENTICAL objects', it claims the same BYTES",
    "passes, as the v2 docstring now states")

e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, {"mu": mu})
rec("G5", "PASS" if isinstance(e, core.DesignViolation) and "must be the string" in str(e) else "FINDING",
    "a non-stamp argument is refused (and is not echoed)", msg(e))

# G6 - residual: can a caller still FORGE a stamp without calling apply?
forged = R2.transform_stamp(mu, D)
_, _ = R2.apply_archive_transform(Q, mu_q, D)                 # transformed with a QUERY mu
e, _ = raises(R2.assert_query_transform_is_inherited, mu, D, forged)
rec("G6", "OBSERVE" if e is None else "PASS",
    "RESIDUAL: transform_stamp is public, so a caller that deliberately re-derives the stamp can "
    "still report an untrue one",
    "forged stamp accepted" if e is None else msg(e))

# G7 - v1 negative control, mine
e1, _ = raises(R1.assert_query_transform_is_inherited, mu, D, mu.copy(), D.copy())
e2, _ = raises(R1.assert_query_transform_is_inherited, mu, D, mu, D)   # after a query-mu transform
rec("G7", "PASS" if e1 is None and e2 is None else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 passes on copies AND passes when the archive mu is merely "
    "reported after a query-derived transform", "both v1 calls returned without raising")
sig1 = inspect.signature(R1.apply_archive_transform)
rec("G8", "INFO", "v1 apply_archive_transform returned no stamp",
    f"v1 {sig1} -> array only; v2 {inspect.signature(R2.apply_archive_transform)} -> (array, stamp)")


print()
print("=" * 100)
print("SECTION H - D-7  parallel-array validation before zip")
print("=" * 100)

def lme_run(items, man=None, **kw):
    src = write_json(TMP / f"h{len(RESULTS)}" / "longmemeval_s_cleaned.json", items)
    mraw = raw_of(man or lme_manifest(len(items)))
    with gate_open(), bind_source(R2.LONGMEMEVAL, src), bind_manifest(R2.LONGMEMEVAL, mraw):
        mapping = R2.load_accepted_mapping(R2.LONGMEMEVAL, raw=mraw)
        return raises(I2.ingest_longmemeval, src, mapping, **kw)

e, _ = lme_run(fake_lme(1, 2, 2, ragged="haystack_dates"))
ok = isinstance(e, core.DesignViolation) and "different lengths" in str(e) and "D-7" in str(e)
rec("H1", "PASS" if ok else "FINDING", "a short haystack_dates is refused BEFORE zip, with the lengths",
    msg(e))
e, _ = lme_run(fake_lme(1, 2, 2, ragged="haystack_session_ids"))
rec("H2", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a short haystack_session_ids is refused", msg(e)[:200])
e, _ = lme_run(fake_lme(1, 2, 2, ragged="haystack_sessions"))
rec("H3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a short haystack_sessions is refused", msg(e)[:200])
empty = fake_lme(1, 0, 0)
e, _ = lme_run(empty)
rec("H4", "PASS" if isinstance(e, core.DesignViolation) and "no haystack sessions" in str(e) else "FINDING",
    "an entirely EMPTY haystack (all three length 0) is refused, not accepted as zero units", msg(e))
e, ing = lme_run(fake_lme(2, 2, 2))
rec("H5", "PASS" if e is None and all(len(v["units"]) == 4 for v in ing["questions"].values()) else "FINDING",
    "a well-formed LongMemEval source still ingests", msg(e) if e else "2 questions, 4 units each")

# H6 - my own v1 negative control
def _v1_lme():
    items = fake_lme(1, 2, 2, ragged="haystack_dates")
    src = write_json(TMP / "h6" / "longmemeval_s_cleaned.json", items)
    mraw = raw_of(lme_manifest(1)); p = TMP / "h6" / "m.json"; p.write_bytes(mraw)
    o1 = dict(I1.BOUND_SOURCES[R1.LONGMEMEVAL]); o2 = dict(I1.BOUND_MANIFESTS[R1.LONGMEMEVAL])
    I1.BOUND_SOURCES[R1.LONGMEMEVAL].update({"filename": "longmemeval_s_cleaned.json",
                                             "sha256": sha(src.read_bytes()),
                                             "bytes": len(src.read_bytes())})
    I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].update({"path": str(p), "sha256": sha(mraw)})
    try:
        with gate_open():
            return I1.ingest_longmemeval(src, p)
    finally:
        I1.BOUND_SOURCES[R1.LONGMEMEVAL].clear(); I1.BOUND_SOURCES[R1.LONGMEMEVAL].update(o1)
        I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].clear(); I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].update(o2)
e, ing1 = raises(_v1_lme)
n_units = sum(len(v["units"]) for v in ing1["questions"].values()) if e is None else None
rec("H6", "PASS" if e is None and n_units == 2 else ("PASS" if e is None else "FINDING"),
    "MY OWN v1 NEGATIVE CONTROL: v1 silently truncates the ragged haystack",
    msg(e) if e else f"v1 accepted it and produced {n_units} archive units (should be 4)")

# H7 - LongMemEval evidence accounting is a tautology
e, ing = lme_run(fake_lme(1, 1, 2, has_answer_int=True))
s = I2.summarise(ing) if e is None else None
rec("H7", "OBSERVE",
    "LongMemEval evidence_ids_declared is DEFINED as the resolved count, so unresolved is always 0",
    msg(e) if e else json.dumps({k: s[k] for k in
        ("evidence_ids_declared", "evidence_ids_resolved", "evidence_ids_unresolved",
         "questions_with_empty_gold", "questions_with_partial_evidence_loss")})
    + f"\n(one turn carries has_answer=1 (int) and is silently NOT gold; gold rows="
      f"{[v['gold_rows'] for v in ing['questions'].values()] if e is None else None})")


print()
print("=" * 100)
print("SECTION I - D-8  missing required fields")
print("=" * 100)

for field in ("question_id", "haystack_session_ids", "haystack_dates", "haystack_sessions"):
    items = fake_lme(1, 2, 2)
    items[0].pop(field)
    if field == "question_id":
        man = lme_manifest(1)
        e, _ = lme_run(items, man)
        ok = isinstance(e, core.DesignViolation) and not isinstance(e, KeyError)
    else:
        e, _ = lme_run(items)
        ok = isinstance(e, core.DesignViolation) and "missing the required field" in str(e)
    rec(f"I1.{field}", "PASS" if ok else "FINDING",
        f"a missing {field!r} gives a NAMED DesignViolation, not a raw KeyError", msg(e))
    if e is not None:
        rec(f"I2.{field}", "PASS" if not leaks(str(e)) else "FINDING",
            f"the {field!r} refusal carries no content", f"canaries: {leaks(str(e)) or 'none'}")

e, _ = lme_run([["not", "a", "dict"]])
rec("I3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING",
    "a non-mapping LongMemEval item is refused by name", msg(e))

# my own v1 negative control
def _v1_key():
    items = fake_lme(1, 2, 2); items[0].pop("question_id")
    src = write_json(TMP / "i4" / "longmemeval_s_cleaned.json", items)
    mraw = raw_of(lme_manifest(1)); p = TMP / "i4" / "m.json"; p.write_bytes(mraw)
    o1 = dict(I1.BOUND_SOURCES[R1.LONGMEMEVAL]); o2 = dict(I1.BOUND_MANIFESTS[R1.LONGMEMEVAL])
    I1.BOUND_SOURCES[R1.LONGMEMEVAL].update({"filename": "longmemeval_s_cleaned.json",
                                             "sha256": sha(src.read_bytes()),
                                             "bytes": len(src.read_bytes())})
    I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].update({"path": str(p), "sha256": sha(mraw)})
    try:
        with gate_open():
            return I1.ingest_longmemeval(src, p)
    finally:
        I1.BOUND_SOURCES[R1.LONGMEMEVAL].clear(); I1.BOUND_SOURCES[R1.LONGMEMEVAL].update(o1)
        I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].clear(); I1.BOUND_MANIFESTS[R1.LONGMEMEVAL].update(o2)
e, _ = raises(_v1_key)
rec("I4", "PASS" if isinstance(e, KeyError) else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 raises a raw KeyError", msg(e))


print()
print("=" * 100)
print("SECTION J - SOURCE TRUST and governance")
print("=" * 100)

sig = inspect.signature(R2.load_accepted_mapping)
ok = "expected_sha256" not in sig.parameters and set(sig.parameters) == {"benchmark", "raw", "path"}
rec("J1", "PASS" if ok else "FINDING",
    "the expected manifest hash is NOT a caller argument any more", f"v2 {sig} | v1 "
    f"{inspect.signature(R1.load_expected_mapping)}")

e, _ = raises(R2.load_accepted_mapping, R2.LOCOMO, raw=raw_loc, path=str(co))
rec("J2", "PASS" if isinstance(e, core.DesignViolation) else "FINDING", "both raw and path is refused", msg(e))
e, _ = raises(R2.load_accepted_mapping, R2.LOCOMO)
rec("J3", "PASS" if isinstance(e, core.DesignViolation) else "FINDING", "neither raw nor path is refused", msg(e))

raw_sup = blob(ACC.ACCEPTED_MANIFESTS[R2.LONGMEMEVAL]["commit"],
               "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_mapping_longmemeval.json")
rec("J4", "INFO", "superseded v1 LongMemEval manifest blob", f"{len(raw_sup)} bytes sha {sha(raw_sup)}")
e, _ = raises(R2.load_accepted_mapping, R2.LONGMEMEVAL, raw=raw_sup)
ok = isinstance(e, core.DesignViolation) and "SUPERSEDED" in str(e) and "Reason:" in str(e)
rec("J5", "PASS" if ok else "FINDING",
    "the SUPERSEDED LongMemEval v1 manifest is refused AS SUPERSEDED, with the reason", msg(e)[:400])
e, _ = raises(R2.load_accepted_mapping, R2.LOCOMO, raw=raw_sup)
rec("J6", "PASS" if isinstance(e, core.DesignViolation) and "SUPERSEDED" in str(e) else "FINDING",
    "it is refused as superseded even when offered under the OTHER benchmark", msg(e)[:200])

# J7 - my own v1 negative control for the source-trust item
p_sup = TMP / "sup.json"; p_sup.write_bytes(raw_sup)
e, m = raises(R1.load_expected_mapping, p_sup, sha(raw_sup))
rec("J7", "PASS" if e is None else "FINDING",
    "MY OWN v1 NEGATIVE CONTROL: v1 loads the SUPERSEDED manifest happily when the caller supplies "
    "its hash", msg(e) if e else f"loaded, n_questions={m['n_questions']}")

# J8 - can a hand-built mapping still reach compute_results / the ingestion?
forged_map = dict(locomo_manifest(2, 2))
forged_map["_accepted_manifest_sha256"] = ACC.ACCEPTED_MANIFESTS[R2.LOCOMO]["blob_sha256"]
qf = list(forged_map["expected_question_to_cluster"])
cf = [forged_map["expected_question_to_cluster"][q] for q in qf]
e, _ = raises(R2.compute_results, records_for(qf), qf, cf, forged_map, seeddir / "good.json",
              benchmark=R2.LOCOMO, scheme="question", replicates=10000)
rec("J8", "OBSERVE" if e is None else "PASS",
    "RESIDUAL: the accepted-manifest 'stamp' is a plain dict key whose value is a PUBLIC constant, "
    "so a hand-built mapping can still be pushed through compute_results",
    "hand-built mapping ACCEPTED" if e is None else msg(e)[:200])
e, _ = raises(I2._check_accepted_mapping, forged_map, R2.LOCOMO)
rec("J9", "OBSERVE" if e is None else "PASS",
    "the same forged stamp satisfies corpus_ingest._check_accepted_mapping",
    "accepted" if e is None else msg(e)[:200])
e, _ = raises(R2.compute_results, records_for(qf), qf, cf, locomo_manifest(2, 2), seeddir / "good.json",
              benchmark=R2.LOCOMO, scheme="question", replicates=10000)
rec("J10", "PASS" if isinstance(e, core.DesignViolation) and "did not come through" in str(e) else "FINDING",
    "an UNSTAMPED mapping is refused by compute_results", msg(e)[:200])

# J11 - one authoritative directory; nothing else holds a competing value
dupes = []
for f in ("membership_runner_v2.py", "corpus_ingest_v2.py", "safe_report.py"):
    t = (V2 / f).read_text(encoding="utf-8", errors="replace")
    for tok in ("66379b9d", "d5b8ed69", "bdf05c12", "3f01082d", "79fa87e9", "d6f21ea9",
                "52001107", "52001207", "52002107"):
        if tok in t:
            dupes.append((f, tok))
rec("J11", "PASS" if not dupes else "FINDING",
    "no accepted hash or seed VALUE is duplicated outside authoritative/", f"{dupes}")

# J12 - the acceptance record and the configuration identity really hash to what is claimed
ar = ACC.ACCEPTANCE_RECORD
b = blob(ar["commit"], ar["document"])
rec("J12", "PASS" if sha(b) == ar["sha256"] else "FINDING",
    "ACCEPTANCE_RECORD names a document that really hashes to the stated value",
    f"{len(b)} bytes, sha {sha(b)}, claimed {ar['sha256']}")
ci = ar["configuration_identity"]
b = blob(ci["commit"], ci["document"])
rec("J13", "PASS" if sha(b) == ci["sha256"] else "FINDING",
    "the configuration identity document hashes to the stated value", f"sha {sha(b)}")
bc = ACC.BOUND_CORE
b = blob(bc["commit"], bc["path"])
rec("J14", "PASS" if sha(b) == bc["blob_sha256"] else "FINDING",
    "BOUND_CORE resolves to the closed core blob bc2282d3…", f"sha {sha(b)}")
b = blob(*(lambda d: (d["commit"], d["path"]))({"commit": "6911a03af68cb48a5090690b05acec59a67ce211",
    "path": "drafts/v52/membership_runner_v1_2026_09_08/binding/PROPOSED_bootstrap_seeds.json"}))
rec("J15", "PASS" if sha(b) == "3f01082d2659d6485a460ef9edad0ae70f653c9a25b4e27680bb8bb058da4fea"
    else "FINDING", "RNG_RULE's cited seeds blob resolves to the hash it states", f"sha {sha(b)}")
seeds_doc = json.loads(b.decode("utf-8"))
rec("J16", "INFO", "the accepted seed file's own values vs. accepted_configuration.ACCEPTED_BOOTSTRAP",
    json.dumps({str(k): v for k, v in ACC.ACCEPTED_BOOTSTRAP.items()}) + "\nfile: "
    + json.dumps(seeds_doc)[:600])
rec("J17", "PASS" if ACC.PROPOSED_VS_ACCEPTED and "PROPOSED" in ACC.PROPOSED_VS_ACCEPTED else "FINDING",
    "the package states, in code, how to read 'PROPOSED' in the older files",
    ACC.PROPOSED_VS_ACCEPTED[:200] + "…")


print()
print("=" * 100)
print("SECTION K - regressions in what the previous review PASSED")
print("=" * 100)

# K1 identity before parse
bad = TMP / "k1" / "locomo10.json"
bad.parent.mkdir(parents=True, exist_ok=True)
bad.write_bytes(b"{ this is not json at all")
with gate_open():
    e, _ = raises(I2.verify_source_bytes, bad, R2.LOCOMO, enabled=True)
ok = isinstance(e, core.DesignViolation) and "source identity mismatch" in str(e)
rec("K1", "PASS" if ok else "FINDING",
    "a file that is BOTH wrong-hashed and invalid JSON fails on IDENTITY, not on parsing", msg(e))

# K2 the LongMemEval cluster block, by every route I can reach
routes = []
e, _ = raises(R2.compute_results, [], [], [], {"benchmark": R2.LONGMEMEVAL}, TMP / "n.json",
              benchmark=R2.LONGMEMEVAL, scheme="cluster")
routes.append(("compute_results", isinstance(e, core.DesignViolation) and "N-3" in str(e)))
e, _ = raises(R2.freeze_bootstrap_seed, TMP / "k2.json", 52002107, R2.LONGMEMEVAL, "cluster", 10000)
routes.append(("freeze_bootstrap_seed", isinstance(e, core.DesignViolation)))
e, _ = raises(R2.accepted_bootstrap_for, R2.LONGMEMEVAL, "cluster")
routes.append(("accepted_bootstrap_for", isinstance(e, core.DesignViolation)))
e, _ = raises(R2.read_bootstrap_seed, seeddir / "good.json", R2.LONGMEMEVAL, "cluster")
routes.append(("read_bootstrap_seed", isinstance(e, core.DesignViolation)))
rec("K2", "PASS" if all(ok for _, ok in routes) else "FINDING",
    "the LongMemEval conversation-cluster bootstrap is refused by every route I could reach",
    str(routes))

# K3 all writers refuse to overwrite
p = TMP / "k3.json"; p.write_text("{}")
w = []
e, _ = raises(R2.freeze_bootstrap_seed, p, 52001107, R2.LOCOMO, "question", 10000)
w.append(("freeze_bootstrap_seed", "refusing to overwrite" in str(e)))
e, _ = raises(I2.write_ingest_manifest, p, {k: 0 for k in I2.INGEST_MANIFEST_KEYS})
w.append(("write_ingest_manifest", "refusing to overwrite" in str(e)))
e, _ = raises(R2.write_results, p, {k: 0 for k in R2.RESULT_KEYS})
w.append(("write_results", "refusing to overwrite" in str(e)))
rec("K3", "PASS" if all(ok for _, ok in w) else "FINDING",
    "all three writers still refuse to overwrite", str(w))

# K4 nothing is estimated from the query
srcq = inspect.getsource(R2.fit_archive_transform) + inspect.getsource(R2.apply_archive_transform)
rec("K4", "PASS" if "query" not in srcq.split('"""')[-1] else "OBSERVE",
    "fit_archive_transform sees no query; apply estimates nothing", "checked by source inspection")

# K5 v2 modules still refuse an unbound/misrouted/duplicate id by name
m = locomo_manifest(2, 2)
qs = list(m["expected_question_to_cluster"]); cs = [m["expected_question_to_cluster"][q] for q in qs]
cs2 = list(cs); cs2[0] = "locomo_conv_1"
e, _ = raises(R2.verify_source_identity, qs, cs2, m)
rec("K5", "PASS" if isinstance(e, core.DesignViolation) and "WRONG conversation" in str(e) else "FINDING",
    "a misrouted question is still refused by name", msg(e)[:200])

print()
print("=" * 100)
n = {}
for _, v, _, _ in RESULTS:
    n[v] = n.get(v, 0) + 1
print("TALLY:", ", ".join(f"{k}={v}" for k, v in sorted(n.items())))
print("FINDINGS:")
for pid, v, label, _ in RESULTS:
    if v == "FINDING":
        print(f"  {pid}: {label}")
print("OBSERVATIONS:")
for pid, v, label, _ in RESULTS:
    if v == "OBSERVE":
        print(f"  {pid}: {label}")
print("=" * 100)
print("temp dir:", TMP)
