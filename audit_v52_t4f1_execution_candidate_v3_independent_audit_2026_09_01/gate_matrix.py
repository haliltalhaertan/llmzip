import sys, json, math, shutil, tempfile
sys.path.insert(0,'.')
from pathlib import Path
from audit_harness import *
from synthetic_fixture import *

DERIVED=["V52_T4F1_question_seed_level.csv","V52_T4F1_question_level.csv",
         "V52_T4F1_aggregate.csv","V52_T4F1_POST_RUN_MANIFEST.json"]
SENTINEL=b"SENTINEL-DO-NOT-OVERWRITE\n"
results=[]

def attempt(name, gate, expect_block, mutate=None, pre=None, elig=None, note_=""):
    m=patch(load_candidate())
    d=Path(tempfile.mkdtemp(prefix="synth_"))
    try:
        rows=trial_rows(m, mutate) if mutate else trial_rows(m)
        write_checkpoints(m,d,rows)
        preset={}
        if pre: preset=pre(d)
        err=None
        try:
            m.finalize_results(d, elig(m) if elig else eligible_rows(), dict(PROV))
        except Exception as e:
            err=f"{type(e).__name__}: {e}"
        blocked = err is not None
        # sentinel integrity
        sent_ok=all(p.read_bytes()==v for p,v in preset.items())
        # which derived outputs exist
        made=[n for n in DERIVED if (d/n).exists() and (d/n) not in preset]
        ok = (blocked==expect_block) and sent_ok
        results.append({"test":name,"gate":gate,"expected_block":expect_block,"blocked":blocked,
                        "error":(err or "")[:180],"sentinels_intact":sent_ok,
                        "derived_outputs_created":made,"pass":ok,"note":note_})
        print(f"[{'PASS' if ok else 'FAIL'}] {gate} {name}: blocked={blocked} sentinel_ok={sent_ok} :: {(err or 'no error')[:110]}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

# ---------- GATE 4 (B1) ----------
def mk_pre(names, tmp=False):
    def _p(d):
        out={}
        for n in names:
            p = d/(n+".tmp") if tmp else d/n
            p.write_bytes(SENTINEL); out[p]=SENTINEL
        return out
    return _p
for n in DERIVED:
    attempt(f"pre-existing destination {n}","G4",True,pre=mk_pre([n]),note_="B1 destination blocks before any byte changed")
for n in DERIVED:
    attempt(f"pre-existing temp {n}.tmp","G4",True,pre=mk_pre([n],tmp=True),note_="B1 temp path blocks")

def pre_partial(d):
    out={}
    for n in DERIVED[:2]:
        (d/n).write_bytes(SENTINEL); out[d/n]=SENTINEL
    return out
attempt("partial/crash-left derived set","G4",True,pre=pre_partial,note_="must block, not repair or replace")

# rerun after success
def rerun():
    m=patch(load_candidate()); d=Path(tempfile.mkdtemp(prefix="synth_rerun_"))
    try:
        rows=trial_rows(m); write_checkpoints(m,d,rows)
        m.finalize_results(d,eligible_rows(),dict(PROV))
        first={n:(d/n).read_bytes() for n in DERIVED}
        err=None
        try: m.finalize_results(d,eligible_rows(),dict(PROV))
        except Exception as e: err=f"{type(e).__name__}: {e}"
        same=all((d/n).read_bytes()==first[n] for n in DERIVED)
        ok = err is not None and same
        results.append({"test":"rerun after successful finalization","gate":"G4","expected_block":True,
                        "blocked":err is not None,"error":(err or "")[:180],"sentinels_intact":same,
                        "derived_outputs_created":[],"pass":ok,"note":"outputs byte-identical after blocked rerun"})
        print(f"[{'PASS' if ok else 'FAIL'}] G4 rerun after success: blocked={err is not None} unchanged={same} :: {(err or '')[:100]}")
    finally: shutil.rmtree(d, ignore_errors=True)
rerun()

# ---------- GATE 5 (B2) ----------
def mut_ids_only(row,ctx):
    if ctx["qid"]=="SQ1" and ctx["method"]=="HAAR96_SIGN" and ctx["trial"]==0 and ctx["seed"]=="43001":
        row["retrieved_top3_ids"]=json.dumps(["999","998","997"])   # metrics untouched
attempt("changed retrieved IDs, stored metrics unchanged","G5",True,mutate=mut_ids_only)

def mk_metric_mut(field,val):
    def _m(row,ctx):
        if ctx["qid"]=="SQ1" and ctx["method"]=="HAAR96_SIGN" and ctx["trial"]==0 and ctx["seed"]=="43001":
            row[field]=val
    return _m
for f,v in [("fractional_source_evidence_recall_at_3","1.0"),("any_at_3","1.0"),("all_at_3","1.0")]:
    attempt(f"changed stored metric {f}, IDs unchanged","G5",True,mutate=mk_metric_mut(f,v))
for f,v in [("fractional_source_evidence_recall_at_3","nan"),("fractional_source_evidence_recall_at_3","inf"),
            ("fractional_source_evidence_recall_at_3","2.0"),("any_at_3","0.5")]:
    attempt(f"malformed metric {f}={v}","G5",True,mutate=mk_metric_mut(f,v))

def mk_id_mut(ids):
    def _m(row,ctx):
        if ctx["qid"]=="SQ1" and ctx["method"]=="HAAR96_SIGN" and ctx["trial"]==0 and ctx["seed"]=="43001":
            row["retrieved_top3_ids"]=json.dumps(ids)
    return _m
for label,ids in [("duplicate IDs",["1","1","2"]),("non-string ID",[1,2,3]),
                  ("noncanonical ID '007'",["007","2","3"]),("boolean ID",[True,"2","3"]),
                  ("malformed ID 'abc'",["abc","2","3"])]:
    attempt(f"{label}","G5",True,mutate=mk_id_mut(ids))

def mut_goldcount(row,ctx):
    if ctx["qid"]=="SQ1": row["gold_count"]="9"
attempt("gold cardinality inconsistency","G5",True,mutate=mut_goldcount)

# ---------- GATE 6 (B3) ----------
def mk_ctrl(kind):
    def _m(row,ctx):
        if ctx["method"]=="SIGNED_PERM_CONTROL96" and ctx["qid"]=="SQ1" and ctx["seed"]=="43003" and ctx["trial"]==5:
            ids=json.loads(row["retrieved_top3_ids"]); d=json.loads(row["top3_distances"])
            if kind=="membership":
                ids=[ids[0],ids[1],"555"]
                m2=patch(load_candidate())
                fr,a,al=m2.metrics_at_3(ids,{"1"})
                row["fractional_source_evidence_recall_at_3"]=repr(float(fr))
                row["any_at_3"]=repr(float(a)); row["all_at_3"]=repr(float(al))
            elif kind=="order": ids=[ids[1],ids[0],ids[2]]
            elif kind=="distance": d=[d[0],d[1],d[2]+1]
            row["retrieved_top3_ids"]=json.dumps(ids); row["top3_distances"]=json.dumps(d)
    return _m
attempt("signed control top3 ID membership divergence","G6",True,mutate=mk_ctrl("membership"),note_="metrics recomputed consistent -> must still block")
attempt("signed control top3 ID ORDER divergence (metrics equal)","G6",True,mutate=mk_ctrl("order"))
attempt("signed control DISTANCE divergence (IDs+metrics equal)","G6",True,mutate=mk_ctrl("distance"))

def drop_cell():
    m=patch(load_candidate()); d=Path(tempfile.mkdtemp(prefix="synth_drop_"))
    try:
        rows=[r for r in trial_rows(m) if not (r["audit_question_id"]=="SQ1" and r["method"]=="NATIVE_SIGN96" and r["trial"]=="7")]
        write_checkpoints(m,d,rows); err=None
        try: m.finalize_results(d,eligible_rows(),dict(PROV))
        except Exception as e: err=f"{type(e).__name__}: {e}"
        ok=err is not None
        results.append({"test":"missing native seed/trial cell","gate":"G6","expected_block":True,"blocked":ok,
                        "error":(err or "")[:180],"sentinels_intact":True,"derived_outputs_created":[],"pass":ok,"note":""})
        print(f"[{'PASS' if ok else 'FAIL'}] G6 missing cell: {(err or '')[:110]}")
    finally: shutil.rmtree(d, ignore_errors=True)
drop_cell()

def dup_cell():
    m=patch(load_candidate()); d=Path(tempfile.mkdtemp(prefix="synth_dup_"))
    try:
        rows=trial_rows(m); rows.append(dict(rows[0])); write_checkpoints(m,d,rows); err=None
        try: m.finalize_results(d,eligible_rows(),dict(PROV))
        except Exception as e: err=f"{type(e).__name__}: {e}"
        ok=err is not None
        results.append({"test":"duplicate result cell","gate":"G6","expected_block":True,"blocked":ok,
                        "error":(err or "")[:180],"sentinels_intact":True,"derived_outputs_created":[],"pass":ok,"note":""})
        print(f"[{'PASS' if ok else 'FAIL'}] G6 duplicate cell: {(err or '')[:110]}")
    finally: shutil.rmtree(d, ignore_errors=True)
dup_cell()

emit("G4_G5_G6_G7_matrix.json",{"gates":["G4","G5","G6","G7"],"synthetic_only":True,
  "total":len(results),"passed":sum(1 for r in results if r["pass"]),
  "failed":[r for r in results if not r["pass"]],"results":results})
print("\nTOTAL", len(results), "PASSED", sum(1 for r in results if r['pass']), "FAILED", sum(1 for r in results if not r['pass']))
