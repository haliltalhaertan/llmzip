"""INDEPENDENT probe suite for the v4 delta closure check.

Cold start. Written by the auditor; shares no code with the preparer's suite.
FAKE FILES AND SYNTHETIC DATA ONLY. No real corpus is opened, read, downloaded, hashed or SCANNED.
Nothing is sealed, nothing is fitted, nothing is run on real data, no candidate file is modified.

Usage:  python -B probe_v4_closure.py <checkout-of-86a8fd7a>
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
PKG4 = ROOT / "drafts/v52/membership_runner_ingest_v4_2026_09_08"
PKG3 = ROOT / "drafts/v52/membership_runner_ingest_v3_2026_09_08"
CORE = ROOT / "drafts/v52/membership_impl_v3_2026_09_07"

# Deliberately the SAME insertion order the preparer documents, so that I test what they ship.
# The order is checked explicitly in probe S1 below.
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

TMP = Path(tempfile.mkdtemp(prefix="audit_v4_"))

# My OWN canaries, not the preparer's. All < 120 characters.
CANARY = "Where did Rashid park the blue van on the night of the storm?"          # 61
CANARY2 = "Melanie's sister got married in Lisbon on the 3rd of April 2019."        # 64
CANARY3 = "the bakery note left on the kitchen table"                              # 40

TALLY = {"PASS": 0, "FINDING": 0, "OBSERVE": 0, "INFO": 0}


def say(kind, label, detail=""):
    TALLY[kind] = TALLY.get(kind, 0) + 1
    line = f"{kind:<8} {label}"
    if detail:
        line += f"   |  {detail}"
    print(line[:400])


def ck(label, cond, detail="", failkind="FINDING"):
    say("PASS" if cond else failkind, label, detail)
    return cond


def surface(fn):
    """Capture EVERY surface: stdout, stderr, message, repr, and the whole cause/context chain."""
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


def files_under(d: Path):
    return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file())


def file_bytes_blob(d: Path) -> bytes:
    b = b""
    for p in sorted(d.rglob("*")):
        if p.is_file():
            b += p.name.encode() + b"\0" + p.read_bytes() + b"\0"
    return b


def wj(path: Path, obj) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8", newline="\n")
    return path


def mb(obj) -> bytes:
    return (json.dumps(obj, indent=2) + "\n").encode("utf-8")


class bind_source:
    def __init__(self, m, b, p):
        self.m, self.b, self.p = m, b, Path(p)

    def __enter__(self):
        self.s = dict(self.m.BOUND_SOURCES[self.b])
        self.m.BOUND_SOURCES[self.b] = dict(self.s, filename=self.p.name,
                                            sha256=hashlib.sha256(self.p.read_bytes()).hexdigest(),
                                            bytes=self.p.stat().st_size)

    def __exit__(self, *_):
        self.m.BOUND_SOURCES[self.b] = self.s


class bind_manifest:
    def __init__(self, b, raw):
        self.b, self.raw = b, raw

    def __enter__(self):
        self.s = dict(accepted.ACCEPTED_MANIFESTS[self.b])
        accepted.ACCEPTED_MANIFESTS[self.b] = dict(self.s, blob_sha256=hashlib.sha256(self.raw).hexdigest())

    def __exit__(self, *_):
        accepted.ACCEPTED_MANIFESTS[self.b] = self.s


class gate_open:
    def __enter__(self):
        self.s = core.REAL_DATA_EXECUTION_ENABLED
        core.REAL_DATA_EXECUTION_ENABLED = True

    def __exit__(self, *_):
        core.REAL_DATA_EXECUTION_ENABLED = self.s


def fake_locomo(evidence, n_turns=4, qtext="q", atext="a"):
    """A synthetic source of the SHAPE of LoCoMo. Content is mine, not the corpus's."""
    conv = {"speaker_a": "A", "speaker_b": "B",
            "session_1": [{"dia_id": f"D1:{t}", "speaker": "A", "text": f"turn {t}"} for t in range(n_turns)],
            "session_1_date_time": "1 Jan 2020"}
    return [{"sample_id": "conv-0", "conversation": conv,
             "qa": [{"question": qtext, "answer": atext, "category": 1, "evidence": evidence}]}]


MAP = {"source_id": "fake", "source_sha256": "0" * 64, "benchmark": accepted.LOCOMO,
       "expected_cluster_ids": ["locomo_conv_0"],
       "expected_question_to_cluster": {"locomo_0_qa0": "locomo_conv_0"}, "n_questions": 1}
MAP_RAW = mb(MAP)

print("=" * 110)
print("INDEPENDENT AUDIT PROBES - v4 delta closure. SYNTHETIC ONLY. No real corpus opened or scanned.")
print("=" * 110)
print(f"python              {sys.version.split()[0]}")
print(f"PYTHONHASHSEED      {os.environ.get('PYTHONHASHSEED')}")
print("threads             " + " ".join(f"{k}={os.environ.get(k)}" for k in
      ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS")))
print(f"checkout            {ROOT}")
print(f"tmp                 {TMP}")

# ==========================================================================================
print("\n== S. the harness itself - is the negative control vacuous? ================================")
# ==========================================================================================
ck("S1  I3/I4 and R3/R4 are DIFFERENT files (control is not testing v4 against itself)",
   Path(I3.__file__).parent != Path(I4.__file__).parent and Path(R3.__file__).parent != Path(R4.__file__).parent,
   f"I3={Path(I3.__file__).parent.name} I4={Path(I4.__file__).parent.name}")
ck("S2  I3 really is the v3 package's module", Path(I3.__file__).parent.name.endswith("v3_2026_09_08"),
   Path(I3.__file__).name)
ck("S3  R3 really is the v3 package's module", Path(R3.__file__).parent.name.endswith("v3_2026_09_08"),
   Path(R3.__file__).name)
say("INFO", "S4  sys.path[0:3]", " | ".join(Path(p).name for p in sys.path[:3]))
ck("S5  the LAST-inserted dir is searched FIRST, so v4 wins - the documented order is what ships",
   Path(sys.path[0]).name.endswith("v4_2026_09_08"))
# The shared modules the v3 package will pick up from sys.modules
h = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ck("S6  safe_report is byte-identical in v3 and v4, so v3 running against v4's is behaviour-neutral",
   h(PKG3 / "safe_report.py") == h(PKG4 / "safe_report.py"))
ck("S7  authoritative/ is byte-identical in v3 and v4, so the v3-closure shadowing hazard is neutral here",
   h(PKG3 / "authoritative/accepted_configuration.py") == h(PKG4 / "authoritative/accepted_configuration.py")
   and h(PKG3 / "authoritative/resolve_sources.py") == h(PKG4 / "authoritative/resolve_sources.py"))
e3 = (PKG3 / "errors.py").read_text(encoding="utf-8")
e4 = (PKG4 / "errors.py").read_text(encoding="utf-8")
c3 = set(re.findall(r"^    ([A-Z_]+) = \"(E-[A-Z]+-\d+)\"", e3, re.M))
c4 = set(re.findall(r"^    ([A-Z_]+) = \"(E-[A-Z]+-\d+)\"", e4, re.M))
ck("S8  errors.py v4 is a STRICT SUPERSET of v3's code set (v3 paths still resolve against it)",
   c3 < c4, f"v3={len(c3)} codes, v4={len(c4)} codes, added={len(c4 - c3)}")
ck("S9  errors.py v4 changed ONLY by addition (no v3 code or sentence altered)",
   all(l in e4 for l in e3.splitlines() if l.strip() and "membership_runner_v3" not in l))
# the three control behaviours must not route through `errors` at all, or the control IS vacuous
src3i = (PKG3 / "corpus_ingest_v3.py").read_text(encoding="utf-8")
src3r = (PKG3 / "membership_runner_v3.py").read_text(encoding="utf-8")
ne3 = src3i[src3i.index("def _normalise_evidence"):src3i.index("def ingest_locomo")]
ck("S10 v3's _normalise_evidence contains NO raise at all, so v4's errors module cannot change it",
   "raise" not in ne3 and "errors." not in ne3)
vi3 = src3r[src3r.index("def validate_identifier(") : src3r.index("def validate_identifier_columns")]
ck("S11 v3's validate_identifier raises plain f-strings, not errors.message - control is real",
   "errors." not in vi3 and "raise DesignViolation(f" in vi3)
say("INFO", "S12 v3 int(mapping['n_questions']) is a builtin conversion, unaffected by errors.py",
    "int(mapping[" in src3r)

# ==========================================================================================
print("\n== A. scope guard - the representation stage was NOT added =================================")
# ==========================================================================================
names4 = sorted(p.name for p in PKG4.rglob("*") if p.is_file())
say("INFO", "A1  files in the v4 namespace", ", ".join(names4))
allsrc = "".join((PKG4 / n).read_text(encoding="utf-8", errors="replace")
                 for n in ("membership_runner_v4.py", "corpus_ingest_v4.py", "errors.py", "safe_report.py"))
ck("A2  no representation fitting / retrieval / ranking / embedding entry point added",
   not re.search(r"def\s+(fit_representation|build_representation|embed|retrieve|rank|encode_corpus)\b", allsrc))
ck("A3  no M-1/M-2/M-3 module appears in the namespace",
   not any(re.search(r"\bM-?[123]\b", n) for n in names4))
ck("A4  the real-data gate is still closed by default", core.REAL_DATA_EXECUTION_ENABLED is False)
ck("A5  run_on_real_corpus still refuses", "not authorized" in surface(lambda: R4.run_on_real_corpus()))

# ==========================================================================================
print("\n== B. ITEM 1 - the BOUND contract, transcribed correctly? ==================================")
# ==========================================================================================
# The frozen producer's norm_evidence, retyped by me from the raw blob at 692f599e lines 107-124.
_DIA = re.compile(r"D\d+:\d+")


def producer_norm_evidence(x):
    if x is None:
        return []
    if isinstance(x, str):
        vals = _DIA.findall(x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = _DIA.findall(z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


ck("B1  claimed VALID EMPTY: None -> ([],0), and the producer agrees it is empty",
   I4._normalise_evidence(None) == ([], 0) and producer_norm_evidence(None) == [])
ck("B2  claimed VALID EMPTY: [] and () -> ([],0), producer agrees",
   I4._normalise_evidence([]) == ([], 0) and I4._normalise_evidence(()) == ([], 0)
   and producer_norm_evidence([]) == [] and producer_norm_evidence(()) == [])
ck("B3  claimed VALID: a string yields its D<n>:<n> ids, exactly as the producer does",
   I4._normalise_evidence("D1:0 and D2:7")[0] == producer_norm_evidence("D1:0 and D2:7") == ["D1:0", "D2:7"])
ck("B4  claimed WHOLE-STRING FALLBACK is preserved and matches the producer byte for byte",
   I4._normalise_evidence("not-an-id-shape") == (["not-an-id-shape"], 1)
   and producer_norm_evidence("not-an-id-shape") == ["not-an-id-shape"])
ck("B5  claimed VALID: list of id strings, and dicts carrying dia_id or id - identical to the producer",
   I4._normalise_evidence(["D1:0", {"dia_id": "D1:1"}, {"id": "D1:2"}])[0]
   == producer_norm_evidence(["D1:0", {"dia_id": "D1:1"}, {"id": "D1:2"}]))
ck("B6  dia_id takes precedence over id, exactly as the producer's `or` does",
   I4._normalise_evidence([{"dia_id": "D1:0", "id": "D9:9"}])[0] == ["D1:0"]
   == producer_norm_evidence([{"dia_id": "D1:0", "id": "D9:9"}]))
ck("B7  a tuple is accepted like a list (the producer accepts both)",
   I4._normalise_evidence(("D1:0", "D1:1")) == (["D1:0", "D1:1"], 2))

# --- the three cases genuinely separated -------------------------------------------------
say("INFO", "B8  E-COH-011 sentence", errors.SENTENCES[errors.Code.EVIDENCE_ITEM_MALFORMED])
say("INFO", "B9  E-COH-012 sentence", errors.SENTENCES[errors.Code.EVIDENCE_STRUCTURE_UNSUPPORTED])
ck("B10 valid-empty, malformed-item and unsupported-structure are three DIFFERENT outcomes",
   I4._normalise_evidence(None) == ([], 0)
   and errors.Code.EVIDENCE_ITEM_MALFORMED.value in surface(lambda: I4._normalise_evidence([7]))
   and errors.Code.EVIDENCE_STRUCTURE_UNSUPPORTED.value in surface(lambda: I4._normalise_evidence(7)))
ck("B11 valid-empty is NOT reported as a malformed item (an empty list is not a fault)",
   errors.Code.EVIDENCE_ITEM_MALFORMED.value not in surface(lambda: I4._normalise_evidence([])))

# ==========================================================================================
print("\n== C. ITEM 1 - MY OWN malformed shapes, including ones the preparer did not test ===========")
# ==========================================================================================


class StrSub(str):
    pass


class DictSub(dict):
    pass


class LyingDict(dict):
    """A dict subclass whose `get` hands back a canary. Tests whether the value can reach a message."""

    def get(self, k, d=None):
        return CANARY if k == "dia_id" else d


class EqAlways(str):
    """A str subclass that collides with everything under dict.fromkeys - would silently collapse ids."""

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return True


MY_SHAPES = {
    # (label, value, what I expect to be true)
    "C01 malformed at FIRST position": [7, "D1:0", "D1:1"],
    "C02 malformed at MIDDLE position": ["D1:0", None, "D1:1"],
    "C03 malformed at LAST position": ["D1:0", "D1:1", 7.5],
    "C04 a list containing another list": ["D1:0", ["D1:1"]],
    "C05 a list containing a tuple": ["D1:0", ("D1:1",)],
    "C06 a nested list of lists": [["D1:0"], ["D1:1"]],
    "C07 float('nan') as a list item": ["D1:0", float("nan")],
    "C08 a bool as a list item": ["D1:0", True],
    "C09 bytes as a list item": ["D1:0", b"D1:1"],
    "C10 a dict with an unrelated key only": ["D1:0", {"note": CANARY3}],
    "C11 a dict with dia_id = ''": ["D1:0", {"dia_id": ""}],
    "C12 a dict with dia_id = None": ["D1:0", {"dia_id": None}],
    "C13 a dict with dia_id = 0 (falsy int)": ["D1:0", {"dia_id": 0}],
    "C14 a dict with dia_id = False": ["D1:0", {"dia_id": False}],
    "C15 a dict with dia_id = [] (falsy list)": ["D1:0", {"dia_id": []}],
    "C16 a dict with id = '' and no dia_id": ["D1:0", {"id": ""}],
    "C17 a dict SUBCLASS with no id keys": ["D1:0", DictSub({"note": CANARY3})],
    "C18 a set as a list item": ["D1:0", {"D1:1"}],
    "C19 a None-only list": [None],
    "C20 an object() as a list item": ["D1:0", object()],
}
for label, value in MY_SHAPES.items():
    txt4 = surface(lambda v=value: I4._normalise_evidence(v))
    try:
        r3 = I3._normalise_evidence(value)
        v3_silent = True
    except BaseException as e:                                                    # noqa: BLE001
        r3, v3_silent = repr(e), False
    refused = errors.Code.EVIDENCE_ITEM_MALFORMED.value in txt4
    clean = not any(c in txt4 for c in (CANARY, CANARY2, CANARY3, "D1:0", "D1:1"))
    ck(f"{label}: v4 REFUSES with E-COH-011", refused, f"v3 silently returned {r3}" if v3_silent else f"v3: {r3}")
    ck(f"{label}: refusal carries no content", clean, txt4.strip().splitlines()[-1][:150] if not clean else "")

UNSUPPORTED = {
    "C21 top-level int": 7,
    "C22 top-level float nan": float("nan"),
    "C23 top-level dict": {"dia_id": "D1:0"},
    "C24 top-level dict SUBCLASS": DictSub({"dia_id": "D1:0"}),
    "C25 top-level set": {"D1:0"},
    "C26 top-level bytes": b"D1:0",
    "C27 top-level bool True": True,
    "C28 top-level object()": object(),
    "C29 top-level generator": (x for x in ["D1:0"]),
}
for label, value in UNSUPPORTED.items():
    txt4 = surface(lambda v=value: I4._normalise_evidence(v))
    try:
        r3 = I3._normalise_evidence(value)
        neg = f"v3 silently returned {r3}"
    except BaseException as e:                                                    # noqa: BLE001
        neg = f"v3 raised {e!r}"
    ck(f"{label}: v4 REFUSES with E-COH-012", errors.Code.EVIDENCE_STRUCTURE_UNSUPPORTED.value in txt4, neg)
    ck(f"{label}: refusal carries no content",
       not any(c in txt4 for c in (CANARY, CANARY2, CANARY3, "D1:0")))

# --- the exotic ones the brief asks for --------------------------------------------------
print("\n-- exotic shapes --")
sub = StrSub("D1:0")
r = I4._normalise_evidence([sub])
ck("C30 a str SUBCLASS is treated as a string (contract-faithful, matches the producer)",
   r[0] == ["D1:0"] and producer_norm_evidence([sub]) == ["D1:0"], f"{r}")
r = I4._normalise_evidence([StrSub("no-id-here")])
ck("C31 a str SUBCLASS with no id falls back whole-string, exactly as the producer does",
   r == (["no-id-here"], 1) and producer_norm_evidence([StrSub("no-id-here")]) == ["no-id-here"])
r = I4._normalise_evidence([DictSub({"dia_id": "D1:0"})])
ck("C32 a dict SUBCLASS carrying dia_id is accepted, as the producer accepts it",
   r == (["D1:0"], 1) and producer_norm_evidence([DictSub({"dia_id": "D1:0"})]) == ["D1:0"])
txt = surface(lambda: I4._normalise_evidence([LyingDict()]))
ck("C33 a dict subclass whose get() hands back a canary: nothing of it reaches the message",
   CANARY not in txt, txt.strip().splitlines()[-1][:150] if CANARY in txt else "no leak")
say("INFO", "C33b what a lying dict subclass yields", repr(I4._normalise_evidence([LyingDict()])))

# non-string dict ids: contract says str(did); v4 keeps that. Is a loss possible?
for lbl, v in [("C34 dia_id = 12345 (int)", [{"dia_id": 12345}]),
               ("C35 dia_id = 1.5 (float)", [{"dia_id": 1.5}]),
               ("C36 dia_id = nan (truthy float)", [{"dia_id": float("nan")}]),
               ("C37 dia_id = ['D1:0'] (list)", [{"dia_id": ["D1:0"]}]),
               ("C38 dia_id = {'a':1} (dict)", [{"dia_id": {"a": 1}}])]:
    got = I4._normalise_evidence(v)
    prod = producer_norm_evidence(v)
    ck(f"{lbl}: v4 matches the frozen producer exactly (str() coercion is the bound contract)",
       got[0] == prod, f"v4={got}  producer={prod}")
    ck(f"{lbl}: raw count is published, so the entry is NOT invisible", got[1] == len(v))

# dict.fromkeys collision - the one way a VALID list could still shrink silently
bad = [EqAlways("D1:0"), "D1:9"]
got = I4._normalise_evidence(bad)
prod = producer_norm_evidence(bad)
ck("C39 a pathological str subclass collapses two ids under dict.fromkeys - IDENTICAL in v4 and the "
   "frozen producer, and raw_items still exposes the difference",
   got[0] == prod and got[1] == 2, f"v4={got}  producer={prod}")

# ==========================================================================================
print("\n== D. ITEM 1 - end to end: can an UNDER-COUNTED gold set still be published? ===============")
# ==========================================================================================
CASES = {
    "D01 one valid + one malformed dict (the named case)": ["D1:0", {"note": CANARY3}],
    "D02 one valid + one empty-id dict": ["D1:0", {"dia_id": ""}],
    "D03 one valid + one null-id dict": ["D1:0", {"dia_id": None}],
    "D04 one valid + one int": ["D1:0", 12345],
    "D05 one valid + one null": ["D1:0", None],
    "D06 malformed FIRST, two valid after": [{"note": "x"}, "D1:0", "D1:1"],
    "D07 malformed MIDDLE": ["D1:0", 7, "D1:1"],
    "D08 malformed LAST": ["D1:0", "D1:1", ["D1:2"]],
    "D09 unsupported structure at the top": {"dia_id": "D1:0"},
    "D10 unsupported structure - int": 42,
}
with gate_open(), bind_manifest(accepted.LOCOMO, MAP_RAW):
    m3 = R3.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    m4 = R4.load_accepted_mapping(accepted.LOCOMO, raw=MAP_RAW)
    for i, (label, ev) in enumerate(CASES.items()):
        d3 = TMP / f"c{i}_v3"
        d4 = TMP / f"c{i}_v4"
        s3p = wj(d3 / "locomo10.json", fake_locomo(ev, qtext=CANARY, atext=CANARY2))
        s4p = wj(d4 / "locomo10.json", fake_locomo(ev, qtext=CANARY, atext=CANARY2))
        before4 = file_bytes_blob(d4)
        # --- NEGATIVE CONTROL on v3 ---
        with bind_source(I3, accepted.LOCOMO, s3p):
            try:
                s3 = I3.summarise(I3.ingest_locomo(s3p, m3))
                ea3 = s3["evidence_accounting"]
                v3_desc = (f"declared={ea3['declared_reference_ids']} resolved={ea3['resolved_reference_ids']} "
                           f"unresolved={ea3['unresolved_reference_ids']} "
                           f"empty_gold={s3['questions_with_empty_gold']} "
                           f"partial_loss={s3['questions_with_partial_evidence_loss']}")
                v3_lossless = (ea3["declared_reference_ids"] == ea3["resolved_reference_ids"]
                               and ea3["unresolved_reference_ids"] == 0
                               and s3["questions_with_empty_gold"] == 0
                               and s3["questions_with_partial_evidence_loss"] == 0)
            except BaseException as e:                                            # noqa: BLE001
                v3_desc, v3_lossless = f"v3 raised {type(e).__name__}", False
        ck(f"{label}: NEGATIVE CONTROL - v3 publishes it as complete and lossless", v3_lossless, v3_desc)
        # --- v4 ---
        with bind_source(I4, accepted.LOCOMO, s4p):
            txt = surface(lambda p=s4p: I4.ingest_locomo(p, m4))
        refused = ("E-COH-011" in txt) or ("E-COH-012" in txt)
        ck(f"{label}: v4 STOPS", refused, txt.strip().splitlines()[-1][:130] if not refused else "")
        ck(f"{label}: v4 leaks no content on the refusal",
           not any(c in txt for c in (CANARY, CANARY2, CANARY3)))
        ck(f"{label}: v4 wrote NO file", file_bytes_blob(d4) == before4,
           str(set(files_under(d4)) - set(files_under(d4))))

    # --- the free-text string: the sixth shape from the v3 closure report --------------
    d = TMP / "freetext"
    p = wj(d / "locomo10.json", fake_locomo(f"see D1:0 and also {CANARY3}", qtext=CANARY))
    with bind_source(I4, accepted.LOCOMO, p):
        s4 = I4.summarise(I4.ingest_locomo(p, m4))
    ea = s4["evidence_accounting"]
    say("OBSERVE", "D11 the v3 report's SIXTH shape - a free-text string with one embedded id - still "
                   "ingests in v4 and is NOT refused",
        f"raw={ea['raw_evidence_items']} declared={ea['declared_reference_ids']} "
        f"resolved={ea['resolved_reference_ids']} unresolved={ea['unresolved_reference_ids']} "
        f"empty_gold={s4['questions_with_empty_gold']}")
    say("INFO", "D11b the frozen producer does the same on that string", repr(producer_norm_evidence(
        f"see D1:0 and also {CANARY3}")))
    ck("D11c the published raw_evidence_items truthfully says ONE entry was presented",
       ea["raw_evidence_items"] == 1)

    # --- three counts really are three concepts ---------------------------------------
    d = TMP / "three"
    p = wj(d / "locomo10.json", fake_locomo(["D1:0", "D1:0", "D1:99"]))
    with bind_source(I4, accepted.LOCOMO, p):
        txt = surface(lambda: I4.ingest_locomo(p, m4))
    say("INFO", "D12 raw 3 / declared 2 / resolved 1 -> the unresolved one now STOPS the run",
        "E-COH-002" in txt)
    d = TMP / "three2"
    p = wj(d / "locomo10.json", fake_locomo(["D1:0", "D1:0"]))
    with bind_source(I4, accepted.LOCOMO, p):
        ea = I4.summarise(I4.ingest_locomo(p, m4))["evidence_accounting"]
    ck("D13 THREE published fields are three different numbers for a VALID repeated id",
       ea["raw_evidence_items"] == 2 and ea["declared_reference_ids"] == 1
       and ea["resolved_reference_ids"] == 1 and ea["unresolved_reference_ids"] == 0, str(ea))
    ck("D14 the set/dedup semantics for VALID repeats are UNCHANGED from v3",
       I3._normalise_evidence(["D1:0", "D1:0"]) == I4._normalise_evidence(["D1:0", "D1:0"])[0])
    ck("D15 four accounting fields are published, not two",
       set(ea) == {"model", "raw_evidence_items", "declared_reference_ids",
                   "resolved_reference_ids", "unresolved_reference_ids"}, str(sorted(ea)))

    # --- nothing excluded, repaired or changed on a clean source ----------------------
    dc3, dc4 = TMP / "cl3", TMP / "cl4"
    pc3 = wj(dc3 / "locomo10.json", fake_locomo(["D1:0", "D1:1"], qtext=CANARY))
    pc4 = wj(dc4 / "locomo10.json", fake_locomo(["D1:0", "D1:1"], qtext=CANARY))
    with bind_source(I3, accepted.LOCOMO, pc3):
        g3 = I3.ingest_locomo(pc3, m3)
    with bind_source(I4, accepted.LOCOMO, pc4):
        g4 = I4.ingest_locomo(pc4, m4)
    q3 = g3["conversations"]["locomo_conv_0"]["questions"]
    q4 = g4["conversations"]["locomo_conv_0"]["questions"]
    ck("D16 on a CLEAN source the gold rows are byte-identical to v3 - nothing repaired",
       json.dumps(q3, sort_keys=True) == json.dumps(q4, sort_keys=True))
    ck("D17 the cohort is unchanged", g3["cohort_ids"] == g4["cohort_ids"]
       and g3["extra_ids_in_source"] == g4["extra_ids_in_source"])
    ck("D18 no question is excluded", len(q4) == 1 and I4.summarise(g4)["n_questions"] == 1)
    ck("D19 a fully-unresolvable question is still NOT treated as partial - it proceeds and is visible",
       True)
    d = TMP / "fullyun"
    p = wj(d / "locomo10.json", fake_locomo(["D9:9"]))
    with bind_source(I4, accepted.LOCOMO, p):
        s = I4.summarise(I4.ingest_locomo(p, m4))
    ck("D19b  ...measured", s["questions_with_empty_gold"] == 1
       and s["evidence_accounting"]["unresolved_reference_ids"] == 1
       and s["evidence_accounting"]["raw_evidence_items"] == 1, str(s["evidence_accounting"]))

print(f"\nTALLY-PART1 {TALLY}")
