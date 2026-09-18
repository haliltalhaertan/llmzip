#!/usr/bin/env python3
"""Code-level certification — parallel version (v2).

Phase sign: compare packbits(regenerated C >= 0) with the frozen sign_doc_packed /
sign_query_packed of V52_T4C2_BINARY_GEOMETRY.zip for all 470 questions (+ gold/N checks).
Phase itq : refit the frozen adapter v1 fit_itq on each regenerated C for the 5 stored seeds and
compare packbits((C@R)>=0) with the stored itq_doc_packed. Parallel over questions; appends to a
JSONL so progress survives interruption.

Outputs: regen/lme/code_certification_sign.json, regen/lme/code_certification_itq.json
"""
import argparse
import hashlib
import io
import json
import os
import pickle
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
REPO = Path(r"C:/Users/MDP/dev/llmzip")
REGEN = WORK / "regen" / "lme"
ZIP = WORK / "drive" / "V52_T4C2_BINARY_GEOMETRY.zip"
ZIP_SHA = "40026fe6e773c20b284e926efda6e5e72f9193b5a4c98710687e1a162913c96d"

ADAPTER = str(REPO / "adapters" / "longmemeval_v52_adapter.py")
ADAPTER_SHA = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _load_npz(zip_path, qid):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(f"codes/{qid}.npz") as f:
            return {k: v for k, v in np.load(io.BytesIO(f.read()), allow_pickle=False).items()}


def _itq_worker(qid):
    if sha256_file(Path(ADAPTER)) != ADAPTER_SHA:
        raise RuntimeError("adapter sha mismatch in worker")
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"a1_{os.getpid()}", ADAPTER)
    a1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a1)
    d = _load_npz(ZIP, qid)
    with open(REGEN / "cache_repr" / f"{qid}.pkl", "rb") as f:
        C = pickle.load(f)["C"]
    itq_doc = d["itq_doc_packed"]
    seeds = [int(x) for x in np.asarray(d["itq_seeds"]).ravel()]
    matches = []
    for i, s in enumerate(seeds):
        R = a1.fit_itq(C, seed=s)
        pk = np.packbits(np.asarray(C) @ R >= 0, axis=1, bitorder="big")
        matches.append(bool(np.array_equal(pk, itq_doc[i])))
    return {"qid": qid, "seeds": seeds, "matches": matches}


def phase_sign():
    got = sha256_file(ZIP)
    assert got == ZIP_SHA, got
    assert sha256_file(Path(ADAPTER)) == ADAPTER_SHA, "adapter sha mismatch"
    with zipfile.ZipFile(ZIP) as _zf:
        names = sorted(n for n in _zf.namelist() if n.endswith(".npz"))
    assert len(names) == 470
    sign_ok = q_ok = gold_ok = n_ok = 0
    bad = []
    zeros_total = docs_total = 0
    bitorders = set()
    for name in names:
        qid = name.split("/")[-1][:-4]
        d = _load_npz(ZIP, qid)
        with open(REGEN / "cache_repr" / f"{qid}.pkl", "rb") as f:
            o = pickle.load(f)
        C = o["C"]; qC = o["qC"]
        bitorders.add(str(d["bitorder"][0]))
        D = np.asarray(C) >= 0
        pk = np.packbits(D, axis=1, bitorder="big")
        if pk.shape == d["sign_doc_packed"].shape and np.array_equal(pk, d["sign_doc_packed"]):
            sign_ok += 1
        else:
            pk_l = np.packbits(D, axis=1, bitorder="little")
            bad.append({"qid": qid, "little_matches": bool(pk_l.shape == d["sign_doc_packed"].shape and np.array_equal(pk_l, d["sign_doc_packed"]))})
        qpk = np.packbits((np.asarray(qC) >= 0)[None, :], axis=1, bitorder="big")[0]
        if np.array_equal(qpk, d["sign_query_packed"]):
            q_ok += 1
        gt = np.sort(np.asarray(d["gold_rows"], dtype=np.int64))
        go = np.sort(np.asarray(o["gold"], dtype=np.int64))
        if np.array_equal(gt, go):
            gold_ok += 1
        if int(np.asarray(d["N_archive"]).ravel()[0]) == int(C.shape[0]):
            n_ok += 1
        zeros_total += int((np.asarray(C) == 0).sum())
        docs_total += int(C.shape[0])
    rep = {"zip_sha256": got, "questions": len(names), "sign_doc_packed_bit_exact": sign_ok,
           "sign_doc_mismatch_count": len(bad), "sign_doc_mismatches": bad[:20],
           "sign_query_packed_bit_exact": q_ok, "gold_rows_match": gold_ok, "N_archive_match": n_ok,
           "bitorder_field_values": sorted(bitorders), "total_docs": docs_total,
           "exact_zero_entries_in_regenerated_C": zeros_total}
    (REGEN / "code_certification_sign.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2)[:2000])


def phase_itq(workers):
    assert sha256_file(Path(ADAPTER)) == ADAPTER_SHA, "adapter sha mismatch"
    with zipfile.ZipFile(ZIP) as _zf:
        names = sorted(n.split("/")[-1][:-4] for n in _zf.namelist() if n.endswith(".npz"))
    out_jsonl = REGEN / "code_certification_itq.jsonl"
    done = set()
    if out_jsonl.exists():
        for ln in out_jsonl.read_text().splitlines():
            try:
                done.add(json.loads(ln)["qid"])
            except Exception:
                pass
    tasks = [q for q in names if q not in done]
    print(f"itq: {len(tasks)} pending, {len(done)} existing")
    with open(out_jsonl, "a") as out:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_itq_worker, q): q for q in tasks}
            n = 0
            for f in as_completed(futs):
                r = f.result()
                out.write(json.dumps(r) + "\n"); out.flush()
                n += 1
                if n % 25 == 0:
                    print(f"  itq progress {n}/{len(tasks)}", flush=True)
    # aggregate (dedupe by qid; last record wins)
    byq = {}
    for ln in out_jsonl.read_text().splitlines():
        if ln.strip():
            try:
                r = json.loads(ln)
                byq[r["qid"]] = r
            except Exception:
                pass
    records = list(byq.values())
    if len(records) != 470:
        print(f"WARNING: {len(records)} unique qids, expected 470"); sys.exit(1)
    seeds = sorted({s for r in records for s in r["seeds"]})
    per_seed = {str(s): sum(1 for r in records if r["matches"][r["seeds"].index(s)]) for s in seeds}
    rep = {"questions": len(records), "per_seed_exact": per_seed,
           "all_seeds_exact": sum(1 for r in records if all(r["matches"])),
           "mismatches": [{"qid": r["qid"], "seeds_failed": [s for s, m in zip(r["seeds"], r["matches"]) if not m]}
                          for r in records if not all(r["matches"])][:20]}
    (REGEN / "code_certification_itq.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2)[:2000])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["sign", "itq"])
    ap.add_argument("--workers", type=int, default=10)
    a = ap.parse_args()
    if a.phase == "sign":
        phase_sign()
    else:
        phase_itq(a.workers)


if __name__ == "__main__":
    main()
