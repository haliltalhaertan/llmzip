"""Fully synthetic finalization fixtures. No real BEAM data, IDs, distances or metrics."""
from __future__ import annotations
import csv, importlib.util, json, sys
from pathlib import Path
from audit_harness import CANDIDATE

def load_candidate():
    spec = importlib.util.spec_from_file_location("v3mod", CANDIDATE/"v52_t4f1_beam_retrieval.py")
    m = importlib.util.module_from_spec(spec); sys.modules["v3mod"]=m; spec.loader.exec_module(m)
    return m

# synthetic questions: (qid, tier, conv, ability, gold ids, native retrieved ids)
SYNTH = [
    ("SQ1","100K","901","single_hop", ["1"],              ["1","20","30"]),      # complete overlap, 1 gold
    ("SQ2","100K","901","multi_hop",  ["1","2","3","4"],  ["1","2","40"]),  # >3 gold, structural ALL@3=0
    ("SQ3","500K","902","temporal",   ["5","6"],          ["5","60","70"]),      # partial overlap
    ("SQ4","500K","902","single_hop", ["7"],              ["80","90","100"]),    # zero overlap
]
METHODS = [("NATIVE_SIGN96",[""]),("SIGNED_PERM_CONTROL96",["43001","43002","43003","43004","43005"]),
           ("HAAR96_SIGN",["43001","43002","43003","43004","43005"]),
           ("ITQ96_CENTERED",["101","202","303","404","505"])]

def eligible_rows():
    out=[]
    for qid,tier,conv,ability,gold,_ in SYNTH:
        out.append({"audit_question_id":qid,"tier":tier,"conversation_id":conv,"ability":ability,
                    "gold_source_unit_count":str(len(gold)),"gold_source_ids_parsed":list(gold),
                    "audit_category":"EXACT_SOURCE_IDS","primary_evidence_cohort_eligible":"True"})
    return out

def trial_rows(m, mutate=None):
    """mutate(row, ctx) may alter a row to create a negative control."""
    rows=[]
    for qid,tier,conv,ability,gold,native in SYNTH:
        goldset={m.canonical_raw_id(g) for g in gold}
        for method,seeds in METHODS:
            for seed in seeds:
                for trial in range(20):
                    if method in ("NATIVE_SIGN96","SIGNED_PERM_CONTROL96"):
                        ids=list(native); dists=[3,7,11]
                    elif method=="HAAR96_SIGN":
                        ids=["201","202","203"]; dists=[5,9,13]
                    else:
                        ids=["301","302","303"]; dists=[4,8,12]
                    frac,anyv,allv = m.metrics_at_3(ids, goldset)
                    row={"audit_question_id":qid,"tier":tier,"conversation_id":conv,"ability":ability,
                         "method":method,"seed":seed,"trial":str(trial),"archive_units":"400",
                         "gold_count":str(len(gold)),
                         "retrieved_top3_ids":json.dumps(ids),"top3_distances":json.dumps(dists),
                         "fractional_source_evidence_recall_at_3":repr(float(frac)),
                         "any_at_3":repr(float(anyv)),"all_at_3":repr(float(allv))}
                    if mutate: mutate(row,{"qid":qid,"method":method,"seed":seed,"trial":trial,"gold":gold})
                    rows.append(row)
    return rows

PROV={"script_sha256":"s"*64,"cohort_sha256":"c"*64,
      "run_authorization_sha256":"a"*64,"execution_candidate_seal_sha256":"e"*64}

def write_checkpoints(m, outdir: Path, rows):
    by_arch={}
    for r in rows: by_arch.setdefault(f"{r['tier']}::{r['conversation_id']}",[]).append(r)
    for aid,arows in by_arch.items():
        nq=len({r["audit_question_id"] for r in arows})
        meta={"schema":"V52_T4F1_ARCHIVE_RESULT_META_V3","archive_id":aid,"eligible_questions":nq,
              "archive_units":400,"trial_rows":nq*320,
              "signed_control_question_seed_checks":nq*5,
              "continuous_max_abs_dot_diff":0.0,"continuous_max_abs_norm_diff":0.0,
              "outcomes_printed_to_console":False,"provenance":dict(PROV)}
        m.write_archive_result(outdir, aid, arows, meta)

def patch(m):
    m.EXPECTED_ELIGIBLE=len(SYNTH); m.EXPECTED_ARCHIVES=2
    return m
