#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] BENCH-3A STEP 0 — port fidelity gate.

Reconstructs C96/qC for sampled LME questions using ONLY the frozen producer's
own buildrep (imported from drive/v52_t4c3_coordinate_axis_probe.py, never
reimplemented), then compares against regen/lme/cache_repr/<qid>.pkl.

Gate per qid: max|C-Cref| <= 1e-10 AND sign(C)==sign(Cref) 100%; same for qC.
Writes /tmp/b3a/port_gate.json. Exits nonzero on gate failure.
"""
import hashlib
import importlib.util
import json
import os
import pickle
import re
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

WORK = Path("/mnt/c/Users/MDP/dev/llmzip-work")
REPO = Path("/mnt/c/Users/MDP/dev/llmzip")
PRODUCER = WORK / "drive" / "v52_t4c3_coordinate_axis_probe.py"
A2 = REPO / "adapters" / "longmemeval_v52_adapter_v2.py"
DATASET = WORK / "drive" / "longmemeval_s_cleaned.json"
ITEMS = WORK / "regen" / "lme" / "items"
CACHE = WORK / "regen" / "lme" / "cache_repr"
OUTDIR = Path("/tmp/b3a")
TOL = 1e-10

PIN = {
    "producer": "8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996",
    "a2": "643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218",
    "dataset": "d6f21ea9d60a0d56f34a05b609c79c88a451d2ae03597821ea3d5a9678c3a442",
}
DATASET_BYTES = 277383467


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_producer():
    spec = importlib.util.spec_from_file_location("frozen_t4c3_producer", str(PRODUCER))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    prov = {}
    for key, path in (("producer", PRODUCER), ("a2", A2), ("dataset", DATASET)):
        got = sha256_file(path)
        ok = got == PIN[key]
        prov[key] = {"sha256": got, "pinned": PIN[key], "match": ok}
        print(f"[{ 'OK' if ok else 'MISMATCH'}] {key} {got}")
        if not ok:
            print("GATE ABORT: provenance hash mismatch");
            sys.exit(2)
    dbytes = DATASET.stat().st_size
    prov["dataset"]["bytes"] = dbytes
    print(f"[{'OK' if dbytes == DATASET_BYTES else 'MISMATCH'}] dataset bytes {dbytes}")
    if dbytes != DATASET_BYTES:
        sys.exit(2)

    raw = DATASET.read_bytes()
    ids = sorted(m.decode() for m in re.findall(rb'"question_id"\s*:\s*"([^"]+)"', raw))
    assert len(ids) == 500, len(ids)
    lex = {q: i for i, q in enumerate(ids)}
    prim = [q for q in ids if not q.endswith("_abs")]
    assert len(prim) == 470, len(prim)
    sample = prim[:5]
    print("sample (first 5 lexical primary):", sample)

    prod = load_producer()
    assert prod.buildrep.__module__ == "frozen_t4c3_producer", "buildrep not from frozen producer"
    ock = OUTDIR / "port_check"
    ock.mkdir(parents=True, exist_ok=True)

    rows = []
    all_pass = True
    for qid in sample:
        outp = ock / f"{qid}.pkl"
        if outp.exists():
            outp.unlink()
        got_qid = prod.buildrep(str(ITEMS / f"{qid}.json"), lex[qid], str(A2), str(outp))
        assert got_qid == qid, (got_qid, qid)
        o = pickle.loads(outp.read_bytes())
        ref = pickle.loads((CACHE / f"{qid}.pkl").read_bytes())
        row = {"qid": qid, "lex": lex[qid]}
        for key in ("C", "qC"):
            a = np.asarray(o[key], dtype=np.float64)
            b = np.asarray(ref[key], dtype=np.float64)
            assert a.shape == b.shape, (key, a.shape, b.shape)
            md = float(np.max(np.abs(a - b)))
            sm = float(np.mean(np.sign(a) == np.sign(b)))
            row[f"{key}_shape"] = list(a.shape)
            row[f"{key}_maxabsdiff"] = md
            row[f"{key}_signmatch"] = sm
            row[f"{key}_pass"] = bool(md <= TOL and sm == 1.0)
        gold_eq = bool(np.array_equal(np.asarray(o["gold"]).ravel(), np.asarray(ref["gold"]).ravel()))
        row["gold_equal"] = gold_eq
        row["pass"] = bool(row["C_pass"] and row["qC_pass"] and gold_eq)
        all_pass = all_pass and row["pass"]
        rows.append(row)
        print(json.dumps(row))

    gate = {
        "label": "[LOCAL EXPLORATORY PILOT]",
        "task": "BENCH-3A STEP 0 port fidelity gate",
        "method": "frozen producer buildrep imported directly (buildrep.__module__ == frozen_t4c3_producer); no reimplementation",
        "tolerance": TOL,
        "provenance": prov,
        "lex_scope": "ordinal over all 500 dataset question_ids (incl _abs), as in lme_regen.run",
        "per_qid": rows,
        "gate_pass": bool(all_pass),
    }
    (OUTDIR / "port_gate.json").write_text(json.dumps(gate, indent=2))
    print("wrote /tmp/b3a/port_gate.json GATE_PASS =", all_pass)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
