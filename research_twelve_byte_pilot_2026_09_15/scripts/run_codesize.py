#!/usr/bin/env python3
"""Is the 12-byte SIGN96 payload itself compressible, losslessly?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

This asks a different question from everything else in this session: not
"does quality survive" -- compression here is LOSSLESS, so retrieval output is
bit-identical -- but "how many bytes does the archive of codes actually need".

Two cost models, reported separately, because they are not interchangeable:

  RANDOM ACCESS   any single document's code must be decodable on its own.
                  Only per-code coding counts.  This is the conservative model.
  BLOCK DECODE    the whole archive is decoded before scoring.  Legitimate
                  here: Hamming scoring already touches every code in the
                  archive, so we never need one code in isolation.

Every compressed size is a SELF-CONTAINED stream -- the dictionary/model is
inside the number reported.  No per-vector division anywhere: totals only.

Layouts tried, because bit-matrices compress very differently by orientation:
  row     documents x 12 bytes, as stored
  col     transposed to 96 bit-planes (one plane per coordinate)
  colsort bit-planes after ordering documents by code similarity
"""
import bz2
import glob
import gzip
import json
import lzma
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

CODECS = {"gzip": lambda b: gzip.compress(b, 9),
          "bz2": lambda b: bz2.compress(b, 9),
          "lzma": lambda b: lzma.compress(b, preset=9 | lzma.PRESET_EXTREME)}


def pack(C):
    return np.packbits((np.asarray(C, dtype=np.float64) >= 0), axis=1,
                       bitorder="big").astype(np.uint8)


def bitplanes(bits):
    """[N,96] bool -> bytes of 96 planes, each ceil(N/8) bytes."""
    return np.packbits(bits.T, axis=1, bitorder="big").tobytes()


def similarity_order(bits):
    """Greedy nearest-neighbour tour in Hamming space (cheap, deterministic)."""
    n = bits.shape[0]
    b = bits.astype(np.uint8)
    used = np.zeros(n, dtype=bool)
    cur = 0
    used[0] = True
    order = [0]
    for _ in range(n - 1):
        d = np.count_nonzero(b != b[cur], axis=1).astype(np.int32)
        d[used] = 1 << 30
        cur = int(d.argmin())
        used[cur] = True
        order.append(cur)
    return np.asarray(order)


def first_order_bits(bits):
    """Sum_j H(p_j) -- the entropy if coordinates were independent."""
    p = bits.mean(axis=0)
    p = np.clip(p, 1e-12, 1 - 1e-12)
    h = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
    return float(h.sum()), float(p.min()), float(p.max())


def measure(C):
    N = C.shape[0]
    payload = pack(C)
    bits = np.unpackbits(payload, axis=1, bitorder="big")[:, :96].astype(bool)
    raw = N * 12
    out = {"N": N, "raw_bytes": raw}
    h1, pmin, pmax = first_order_bits(bits)
    out["first_order_bits_per_code"] = h1
    out["bit_balance_min"] = pmin
    out["bit_balance_max"] = pmax
    uniq = len(set(map(bytes, payload)))
    out["duplicate_code_fraction"] = 1.0 - uniq / N
    layouts = {"row": payload.tobytes(), "col": bitplanes(bits)}
    order = similarity_order(bits)
    layouts["colsort"] = bitplanes(bits[order])
    # colsort must also carry the permutation to be decodable
    perm_bytes = int(np.ceil(N * np.log2(max(N, 2)) / 8))
    for lay, blob in layouts.items():
        for cname, fn in CODECS.items():
            size = len(fn(blob))
            if lay == "colsort":
                size += perm_bytes
            out[f"{lay}_{cname}_bytes"] = size
            out[f"{lay}_{cname}_ratio"] = size / raw
    # random-access model: compress each 12-byte code on its own
    ra = sum(len(gzip.compress(payload[i].tobytes(), 9)) for i in range(N))
    out["random_access_gzip_bytes"] = ra
    out["random_access_gzip_ratio"] = ra / raw
    return out


def agg(rows):
    keys = [k for k in rows[0] if k != "N"]
    o = {"n_archives": len(rows), "total_N": int(sum(r["N"] for r in rows))}
    tot_raw = sum(r["raw_bytes"] for r in rows)
    o["total_raw_bytes"] = int(tot_raw)
    for k in keys:
        if k.endswith("_bytes"):
            o["total_" + k] = int(sum(r[k] for r in rows))
            o["ratio_" + k[:-6]] = float(sum(r[k] for r in rows) / tot_raw)
        elif k.endswith("_ratio"):
            continue
        else:
            o["mean_" + k] = float(np.mean([r[k] for r in rows]))
    return o


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "lossless": True,
           "note": "compressed sizes are self-contained streams; "
                   "colsort additionally charges the permutation; "
                   "totals only, never bytes-per-vector",
           "benchmarks": {}}

    rows = []
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    for char in sorted(arch):
        rows.append(measure(np.asarray(arch[char]["C"], dtype=np.float64)))
    res["benchmarks"]["perltqa"] = agg(rows)
    del arch
    print("perltqa done", flush=True)

    rows = []
    for f in sorted(glob.glob(H.LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        rows.append(measure(np.asarray(d["C"], float)))
    res["benchmarks"]["lme"] = agg(rows)
    print("lme done", flush=True)

    rows = []
    for f in sorted(glob.glob(H.RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        rows.append(measure(np.asarray(o["C"], float)))
    res["benchmarks"]["realtalk"] = agg(rows)
    print("realtalk done", flush=True)

    with open("CODESIZE.json", "w") as fh:
        json.dump(res, fh, indent=2)
    for b, v in res["benchmarks"].items():
        print(f"\n== {b} == N={v['total_N']} raw={v['total_raw_bytes']:,} B")
        print(f"   birinci-derece entropi: "
              f"{v['mean_first_order_bits_per_code']:.2f} bit/kod (96 bit'ten)")
        for lay in ("row", "col", "colsort"):
            s = "  ".join(f"{c}={v['ratio_' + lay + '_' + c]:.3f}"
                          for c in CODECS)
            print(f"   {lay:8s} {s}")
        print(f"   random-access gzip ratio="
              f"{v['ratio_random_access_gzip']:.3f}")
    print("\nwrote CODESIZE.json", flush=True)


if __name__ == "__main__":
    main()
