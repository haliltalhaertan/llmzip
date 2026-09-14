#!/usr/bin/env python3
"""Code-level certification — regenerated C vs the frozen sign codes actually consumed by the pipeline.

The frozen V52_T4C2_BINARY_GEOMETRY.zip (sha256 40026fe6...) contains, for all 470 questions, the
packed 96-bit sign codes of the frozen C/qC that the retrieval pipeline consumed:
  sign_doc_packed (N,12) uint8, sign_query_packed (12,), bitorder field.
If packbits(regenerated_C >= 0) equals sign_doc_packed bit-for-bit for all 470 questions, then the
regeneration is certified at the exact code level the pipeline used — the strongest available
certification short of the original float bytes.

Secondary: ITQ code variants (5 seeds) compared after refitting the frozen adapter v1's fit_itq on
the regenerated C (the same deterministic function the pipeline used), and gold/N cross-checks.

Outputs: regen/lme/code_certification.json
"""
import hashlib
import io
import json
import pickle
import sys
import zipfile
from pathlib import Path

import numpy as np

WORK = Path(r"C:/Users/MDP/dev/llmzip-work")
REPO = Path(r"C:/Users/MDP/dev/llmzip")
REGEN = WORK / "regen" / "lme"
ZIP = WORK / "drive" / "V52_T4C2_BINARY_GEOMETRY.zip"
ZIP_SHA = "40026fe6e773c20b284e926efda6e5e72f9193b5a4c98710687e1a162913c96d"


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    got = sha256_file(ZIP)
    print("zip sha:", got, "OK" if got == ZIP_SHA else "MISMATCH")
    if got != ZIP_SHA:
        sys.exit(1)

    import importlib.util
    spec = importlib.util.spec_from_file_location("adapter_v1", str(REPO / "adapters" / "longmemeval_v52_adapter.py"))
    a1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a1)

    zf = zipfile.ZipFile(ZIP)
    npz_names = sorted(n for n in zf.namelist() if n.endswith(".npz"))
    if len(npz_names) != 470:
        print("expected 470 npz, got", len(npz_names)); sys.exit(1)

    sign_ok = 0
    sign_bad = []
    q_ok = 0
    q_bad = []
    gold_ok = 0
    n_ok = 0
    bitorder_seen = set()
    zero_entries_total = 0
    docs_total = 0
    itq_ok_seed = {s: 0 for s in (101, 202, 303, 404, 505)}
    itq_bad = []
    itq_done = 0

    do_itq = "--itq" in sys.argv

    for name in npz_names:
        qid = name.split("/")[-1][:-4]
        with zf.open(name) as f:
            d = np.load(io.BytesIO(f.read()), allow_pickle=False)
        with open(REGEN / "cache_repr" / f"{qid}.pkl", "rb") as f:
            o = pickle.load(f)
        C = o["C"]; qC = o["qC"]
        bitorder_seen.add(str(d["bitorder"][0]))

        D = C >= 0
        pk = np.packbits(D, axis=1, bitorder="big")
        if pk.shape == d["sign_doc_packed"].shape and np.array_equal(pk, d["sign_doc_packed"]):
            sign_ok += 1
        else:
            # retry little-endian to detect a bitorder mismatch vs a content mismatch
            pk_l = np.packbits(D, axis=1, bitorder="little")
            sign_bad.append({"qid": qid, "little_matches": bool(pk_l.shape == d["sign_doc_packed"].shape and np.array_equal(pk_l, d["sign_doc_packed"])),
                             "shape_ours": list(pk.shape), "shape_theirs": list(d["sign_doc_packed"].shape)})
        qpk = np.packbits((qC >= 0)[None, :], axis=1, bitorder="big")[0]
        if np.array_equal(qpk, d["sign_query_packed"]):
            q_ok += 1
        else:
            q_bad.append(qid)

        gold_theirs = np.sort(np.asarray(d["gold_rows"], dtype=np.int64))
        gold_ours = np.sort(np.asarray(o["gold"], dtype=np.int64))
        if np.array_equal(gold_theirs, gold_ours):
            gold_ok += 1
        n_theirs = int(np.asarray(d["N_archive"]).ravel()[0])
        if n_theirs == int(C.shape[0]):
            n_ok += 1

        zero_entries_total += int((C == 0).sum())
        docs_total += int(C.shape[0])

        if do_itq:
            itq_doc = d["itq_doc_packed"]; seeds = [int(x) for x in np.asarray(d["itq_seeds"]).ravel()]
            for i, s in enumerate(seeds):
                R = a1.fit_itq(C, seed=s)
                pkq = np.packbits((C @ R) >= 0, axis=1, bitorder="big")
                if np.array_equal(pkq, itq_doc[i]):
                    itq_ok_seed[s] = itq_ok_seed.get(s, 0) + 1
                else:
                    itq_bad.append({"qid": qid, "seed": s})
            itq_done += 1
            if itq_done % 50 == 0:
                print(f"  itq progress {itq_done}/470", flush=True)

    rep = {
        "zip_sha256": got,
        "questions": len(npz_names),
        "sign_doc_packed_bit_exact": sign_ok,
        "sign_doc_mismatches": sign_bad[:20],
        "sign_doc_mismatch_count": len(sign_bad),
        "sign_query_packed_bit_exact": q_ok,
        "sign_query_mismatch_count": len(q_bad),
        "gold_rows_match": gold_ok,
        "N_archive_match": n_ok,
        "bitorder_field_values": sorted(bitorder_seen),
        "total_docs": docs_total,
        "exact_zero_entries_in_regenerated_C": zero_entries_total,
    }
    if do_itq:
        rep["itq_doc_packed_bit_exact_per_seed"] = itq_ok_seed
        rep["itq_mismatch_count"] = len(itq_bad)
        rep["itq_mismatches_sample"] = itq_bad[:10]
    OUT = REGEN / "code_certification.json"
    OUT.write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2)[:3000])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
