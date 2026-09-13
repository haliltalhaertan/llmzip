"""Supplement to code_cert_v2.py: certify itq_query_packed (the one NPZ channel
not covered by phase sign/itq) plus the bitorder metadata.

For every question: load regenerated C/qC from regen/lme/cache_repr/<qid>.pkl,
load frozen itq_seeds / itq_query_packed / itq_doc_packed from
V52_T4C2_BINARY_GEOMETRY.zip; for each seed refit R = adapter.fit_itq(C, seed)
(imported verbatim from the frozen adapter), then compare
  packbits((qC @ R) >= 0, bitorder="big")  vs  itq_query_packed[i]
and re-check doc codes in the same pass (belt-and-braces: phase itq already did,
but this pass independently re-derives them).

Parallel over questions (workers), OMP single-thread per worker.
Out: regen/lme/code_certification_itq_query.json + .jsonl
"""
import hashlib
import importlib.util
import io
import json
import multiprocessing as mp
import os
import sys
import zipfile
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
REPO = Path(r"C:/Users/MDP/dev/llmzip")
ZIP = WORK / "drive" / "V52_T4C2_BINARY_GEOMETRY.zip"
ZIP_SHA = "40026fe6e773c20b284e926efda6e5e72f9193b5a4c98710687e1a162913c96d"
PKLS = WORK / "regen" / "lme" / "cache_repr"
OUT_JSON = WORK / "regen" / "lme" / "code_certification_itq_query.json"
OUT_JSONL = WORK / "regen" / "lme" / "code_certification_itq_query.jsonl"
ADAPTER = str(REPO / "adapters" / "longmemeval_v52_adapter.py")
ADAPTER_SHA = "0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _worker(qid):
    import importlib.util as _iu
    assert sha256_file(Path(ADAPTER)) == ADAPTER_SHA, "adapter sha mismatch"
    spec = _iu.spec_from_file_location(f"a1q_{os.getpid()}", ADAPTER)
    a1 = _iu.module_from_spec(spec)
    spec.loader.exec_module(a1)
    import pickle
    with open(PKLS / f"{qid}.pkl", "rb") as f:
        o = pickle.loads(f.read())
    C = o["C"]; qC = o["qC"]
    with zipfile.ZipFile(ZIP) as zf:
        d = np.load(io.BytesIO(zf.read(f"codes/{qid}.npz")), allow_pickle=False)
    seeds = [int(x) for x in np.asarray(d["itq_seeds"]).ravel()]
    bitorder = str(d["bitorder"][0])
    qmatch = []; dmatch = []
    for i, s in enumerate(seeds):
        R = a1.fit_itq(C, seed=s)
        pq = np.packbits(np.asarray(qC) @ R >= 0, bitorder="big")
        qmatch.append(bool(pq.shape == d["itq_query_packed"][i].shape and np.array_equal(pq, d["itq_query_packed"][i])))
        pk = np.packbits(np.asarray(C) @ R >= 0, axis=1, bitorder="big")
        dmatch.append(bool(pk.shape == d["itq_doc_packed"][i].shape and np.array_equal(pk, d["itq_doc_packed"][i])))
    return {"qid": qid, "seeds": seeds, "bitorder": bitorder,
            "q_match": qmatch, "d_match": dmatch}


def main(workers):
    got = sha256_file(ZIP)
    assert got == ZIP_SHA, got
    assert sha256_file(Path(ADAPTER)) == ADAPTER_SHA, "adapter sha mismatch"
    with zipfile.ZipFile(ZIP) as zf:
        names = sorted(n.split("/")[-1][:-4] for n in zf.namelist() if n.endswith(".npz"))
    assert len(names) == 470, len(names)
    done = set()
    if OUT_JSONL.exists():
        for ln in OUT_JSONL.read_text().splitlines():
            if ln.strip():
                try:
                    done.add(json.loads(ln)["qid"])
                except Exception:
                    pass
    pending = [q for q in names if q not in done]
    print(f"itq-query cert: {len(pending)} pending, {len(done)} existing", flush=True)
    bo_set = set()
    if pending:
        ctx = mp.get_context("spawn")
        with OUT_JSONL.open("a", encoding="utf-8") as fo, ctx.Pool(workers) as pool:
            k = 0
            for rec in pool.imap_unordered(_worker, pending):
                fo.write(json.dumps(rec) + "\n"); fo.flush()
                k += 1
                if k % 25 == 0:
                    print(f"  progress {k}/{len(pending)}", flush=True)
    # aggregate (dedupe by qid, last wins)
    byq = {}
    for ln in OUT_JSONL.read_text().splitlines():
        if ln.strip():
            try:
                r = json.loads(ln); byq[r["qid"]] = r
            except Exception:
                pass
    recs = list(byq.values())
    assert len(recs) == 470, len(recs)
    seeds = sorted({s for r in recs for s in r["seeds"]})
    bo_set = {r["bitorder"] for r in recs}
    qexact = {str(s): sum(1 for r in recs for i, s2 in enumerate(r["seeds"]) if s2 == s and r["q_match"][i]) for s in seeds}
    dexact = {str(s): sum(1 for r in recs for i, s2 in enumerate(r["seeds"]) if s2 == s and r["d_match"][i]) for s in seeds}
    bad = [r["qid"] for r in recs if not all(r["q_match"])]
    rep = {"questions": len(recs), "itq_seeds": seeds, "bitorder_values": sorted(bo_set),
           "itq_query_exact_per_seed": qexact, "itq_query_all_seeds_exact": sum(1 for r in recs if all(r["q_match"])),
           "itq_query_mismatches": bad,
           "itq_doc_exact_per_seed_recheck": dexact,
           "itq_doc_all_seeds_exact_recheck": sum(1 for r in recs if all(r["d_match"])),
           "adapter_sha256": ADAPTER_SHA, "zip_sha256": got,
           "note": "Supplement to code_cert_v2 phase itq: certifies itq_query_packed (5 seeds) -- the one NPZ channel previously uncovered -- and re-derives itq_doc_packed in the same pass."}
    OUT_JSON.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2))
    ok = (rep["itq_query_all_seeds_exact"] == 470 and rep["itq_doc_all_seeds_exact_recheck"] == 470)
    print("ITQ_QUERY_CERT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    w = 12
    if "--workers" in sys.argv:
        w = int(sys.argv[sys.argv.index("--workers") + 1])
    main(w)
