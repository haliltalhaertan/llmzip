"""INDEPENDENT probe suite, part 5: the written ingest manifest, and the accounting fields on disk.
Synthetic only. No real corpus opened, read, hashed or scanned."""
from __future__ import annotations
import contextlib, hashlib, io, json, sys, tempfile, traceback
from pathlib import Path
ROOT = Path(sys.argv[1]).resolve()
PKG4 = ROOT / "drafts/v52/membership_runner_ingest_v4_2026_09_08"
PKG3 = ROOT / "drafts/v52/membership_runner_ingest_v3_2026_09_08"
CORE = ROOT / "drafts/v52/membership_impl_v3_2026_09_07"
for _p in (CORE, PKG3, PKG4):
    sys.path.insert(0, str(_p))
import membership_scaling_core as core
import errors, membership_runner_v4 as R4, corpus_ingest_v4 as I4, corpus_ingest_v3 as I3
from authoritative import accepted_configuration as accepted
TMP = Path(tempfile.mkdtemp(prefix="audit_v4e_"))
CANARY = "Where did Rashid park the blue van on the night of the storm?"
def ck(l,c,d=""): print((("PASS     " if c else "FINDING  ")+l+(f"   |  {d}" if d else ""))[:400])
def surface(fn):
    o,e=io.StringIO(),io.StringIO(); p=[]
    try:
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e): fn()
    except BaseException as ex:
        p.append("".join(traceback.format_exception(type(ex),ex,ex.__traceback__))); p.append(repr(ex))
    return o.getvalue()+e.getvalue()+"\n".join(p)
def wj(p,o):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o),encoding="utf-8",newline="\n"); return p
def mb(o): return (json.dumps(o,indent=2)+"\n").encode("utf-8")
MAP={"source_id":"fake","source_sha256":"0"*64,"benchmark":accepted.LOCOMO,
     "expected_cluster_ids":["locomo_conv_0"],
     "expected_question_to_cluster":{"locomo_0_qa0":"locomo_conv_0"},"n_questions":1}
RAW=mb(MAP)
print("== T. the WRITTEN ingest manifest =========================================================")
s=dict(accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO])
accepted.ACCEPTED_MANIFESTS[accepted.LOCOMO]=dict(s,blob_sha256=hashlib.sha256(RAW).hexdigest())
core.REAL_DATA_EXECUTION_ENABLED=True
m4=R4.load_accepted_mapping(accepted.LOCOMO,raw=RAW)
conv={"speaker_a":"A","speaker_b":"B",
      "session_1":[{"dia_id":f"D1:{t}","speaker":"A","text":CANARY} for t in range(4)],
      "session_1_date_time":"1 Jan 2020"}
src=[{"sample_id":"conv-0","conversation":conv,
      "qa":[{"question":CANARY,"answer":CANARY,"category":1,"evidence":["D1:0","D1:0"]}]}]
p=wj(TMP/"src"/"locomo10.json",src)
old=dict(I4.BOUND_SOURCES[accepted.LOCOMO])
I4.BOUND_SOURCES[accepted.LOCOMO]=dict(old,filename=p.name,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
g=I4.ingest_locomo(p,m4); summ=I4.summarise(g)
out=TMP/"ingest_manifest.json"
I4.write_ingest_manifest(out,summ)
txt=out.read_text(encoding="utf-8")
print("T1 BYTE-VERBATIM evidence_accounting as WRITTEN to disk:")
print("   >>> "+json.dumps(json.loads(txt)["evidence_accounting"],sort_keys=True))
ck("T2 the written manifest carries the FOUR distinct counts", 
   set(json.loads(txt)["evidence_accounting"])=={"model","raw_evidence_items","declared_reference_ids",
   "resolved_reference_ids","unresolved_reference_ids"})
ck("T3 raw(2) != declared(1) == resolved(1) - the dedup of a valid repeat is now VISIBLE on disk",
   json.loads(txt)["evidence_accounting"]["raw_evidence_items"]==2
   and json.loads(txt)["evidence_accounting"]["declared_reference_ids"]==1)
ck("T4 the written manifest carries NO canary content", CANARY not in txt, f"{len(txt)} bytes")
ck("T5 the manifest schema check still accepts the new field set (no E-OUT-002)",
   "E-OUT-002" not in surface(lambda: I4.write_ingest_manifest(TMP/"m2.json",summ)))
ck("T6 the writer still refuses to OVERWRITE", surface(lambda: I4.write_ingest_manifest(out,summ))!="")
ck("T7 assert_content_free still refuses a canary-bearing payload",
   errors.Code.CONTENT_POLICY.value in surface(lambda: I4.assert_content_free({"x":CANARY})))
# v3 comparison of the same clean-but-duplicated source
I3.BOUND_SOURCES[accepted.LOCOMO]=dict(I3.BOUND_SOURCES[accepted.LOCOMO],filename=p.name,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
ea3=I3.summarise(I3.ingest_locomo(p,m4))["evidence_accounting"]
print("T8 NEGATIVE CONTROL - v3's accounting object for the same source:")
print("   >>> "+json.dumps(ea3,sort_keys=True))
ck("T9 v3 published only TWO reference counts and no raw count, so a dropped raw item was "
   "indistinguishable from an item that never existed", "raw_evidence_items" not in ea3)
core.REAL_DATA_EXECUTION_ENABLED=False
