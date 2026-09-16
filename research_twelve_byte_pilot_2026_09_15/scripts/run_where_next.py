#!/usr/bin/env python3
"""Two measurements that decide where the next effort should go.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

Today's audit left one clean diagnosis: the scaled query improves hit@10 but
NOT FR@3, the frozen estimand.  We put the evidence into the top ten and fail
to put it in the top three.  Two numbers decide what to do about that, and
both come from cached representations, so neither is a guess.

  Q1  HOW BIG IS THE SCALING LEVER, before any quantizer?
      `float` and `float_std` are the same 96 float64 coordinates; the only
      difference is that float_std divides each axis by its own std.  No bits,
      no SVD change, no extra information.  The gap between them is a pure
      measurement of how badly the raw SVD axes are scaled, and it is an upper
      bound on what any scale fix can buy at that stage.

  Q2  IS RERANKING WORTH ANYTHING AT ALL?
      If a perfect oracle reordered the top-M candidates that the 12-byte code
      already retrieves, what FR@3 would that reach?  This is the ceiling for
      EVERY second-stage idea -- text rerankers, learned scorers, LLM judges.
      If the ceiling is low the candidates are not there and reranking is the
      wrong investment; if it is high the ranking is the bottleneck.

Reported per benchmark at M = 3, 10, 20, 50, 100, alongside what the arms
actually achieve, so the headroom is visible rather than asserted.
"""
import glob
import json
import os
import pickle
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

MS = (3, 10, 20, 50, 100)
ARMS = ["sym", "asym", "b8", "qscale", "float", "float_std"]


def oracle_fr3_from_topM(scores, gold, M, n):
    """Best possible FR@3 if an oracle reorders the top-M by `scores`.

    Ties at the M-th place are taken in full, matching the rerank protocol.
    """
    g = set(int(x) for x in np.asarray(gold).ravel().astype(int))
    m = min(M, n)
    order = np.argsort(-scores, kind="stable")
    thr = scores[order[m - 1]]
    cand = np.nonzero(scores >= thr)[0]
    inside = sum(1 for i in cand if int(i) in g)
    return min(inside, 3) / len(g)      # oracle puts up to 3 golds first


def handle(C, queries, golds, acc):
    C = np.asarray(C, dtype=np.float64)
    n = C.shape[0]
    st = B.fit_archive(C)
    packed = np.packbits((C >= 0), axis=1, bitorder="big").astype(np.uint8)
    payload = B.encode_docs(C, st)
    R = np.where(np.unpackbits(packed, axis=1,
                               bitorder="big")[:, :96].astype(bool), 1.0, -1.0)
    std = np.asarray(st["std"], dtype=np.float64)
    for j, qv in enumerate(queries):
        q = np.asarray(qv, dtype=np.float64).reshape(-1)
        g = np.asarray(golds[j]).ravel().astype(int)
        sc = {"sym": (-np.count_nonzero(
                  np.unpackbits(packed, axis=1,
                                bitorder="big")[:, :96].astype(bool)
                  != (q >= 0)[None, :], axis=1)).astype(np.float64),
              "asym": B.cosine_from_code(R, q),
              "b8": B.b8_scores(payload, st, q),
              "qscale": R @ (q / std),
              "float": B.float_raw_scores(C, q),
              "float_std": B.float_std_scores(C, q, st["std"])}
        for a, s in sc.items():
            acc[f"{a}_hit1"].append(H.hit_at_k(s, g, 1))
            acc[f"{a}_hit3"].append(H.hit_at_k(s, g, 3))
            acc[f"{a}_hit10"].append(H.hit_at_k(s, g, 10))
            acc[f"{a}_fr3"].append(B.exact_frac(s, g, True))
        for M in MS:
            acc[f"oracle_fr3_from_sym_top{M}"].append(
                oracle_fr3_from_topM(sc["sym"], g, M, n))
            acc[f"oracle_fr3_from_qscale_top{M}"].append(
                oracle_fr3_from_topM(sc["qscale"], g, M, n))


def load(name, acc):
    if name == "lme":
        for f in sorted(glob.glob(H.LME_GLOB)):
            d = pickle.loads(open(f, "rb").read())
            handle(d["C"], [np.asarray(d["qC"], float).reshape(-1)],
                   [np.asarray(d["gold"]).ravel().astype(int)], acc)
    elif name == "realtalk":
        excluded = set(json.load(open(H.EXCL_RT))["excluded_ids"])
        for f in sorted(glob.glob(H.RT_GLOB)):
            o = pickle.loads(open(f, "rb").read())
            qc = np.asarray(o["QC"], float)
            qs, gs = [], []
            for qi, qid in enumerate(o["qids"]):
                gold = [int(x) for x in o["gold_rows"][qi]]
                if gold and qid not in excluded:
                    qs.append(qc[qi])
                    gs.append(np.asarray(gold))
            if qs:
                handle(o["C"], qs, gs, acc)
    elif name == "locomo":
        g = os.path.join(H.SRC, "regen", "locomo", "locomo_*.pkl")
        for f in sorted(glob.glob(g)):
            d = pickle.load(open(f, "rb"))
            i2r = d["id_to_row"]
            qs, gs = [], []
            for j, qa in enumerate(d["qas"]):
                rows = sorted({int(i2r[x]) for x in qa["raw_evidence"]
                               if x in i2r})
                if rows:
                    qs.append(np.asarray(d["QC"], float)[j])
                    gs.append(np.asarray(rows, dtype=int))
            if qs:
                handle(d["C"], qs, gs, acc)
    else:
        arch = pickle.load(open(H.ARCH_PKL, "rb"))
        Q = pickle.load(open(H.Q_PKL, "rb"))
        by = defaultdict(list)
        for qid, v in Q.items():
            by[v["char"]].append(qid)
        for ch in sorted(by):
            ids = sorted(by[ch])
            handle(arch[ch]["C"],
                   [np.asarray(Q[q]["qC"], float) for q in ids],
                   [np.asarray(Q[q]["gold"]).ravel().astype(int) for q in ids],
                   acc)
        del arch, Q


def main():
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmarks": {}}
    for name in ("perltqa", "lme", "realtalk", "locomo"):
        acc = defaultdict(list)
        load(name, acc)
        v = {k: float(np.mean(x) * 100) for k, x in acc.items()}
        v["n_queries"] = len(acc["sym_fr3"])
        res["benchmarks"][name] = v
        print(f"\n=== {name}  n={v['n_queries']} ===")
        print("  Q1  olcek kaldiraci (ayni 96 float64, tek fark eksen olcegi)")
        print(f"      {'kol':>10s}{'hit@1':>8s}{'hit@3':>8s}"
              f"{'hit@10':>8s}{'FR@3':>8s}")
        for a in ARMS:
            print(f"      {a:>10s}{v[a+'_hit1']:8.2f}{v[a+'_hit3']:8.2f}"
                  f"{v[a+'_hit10']:8.2f}{v[a+'_fr3']:8.2f}")
        print(f"      float_std - float :  hit@1 "
              f"{v['float_std_hit1']-v['float_hit1']:+.2f}   FR@3 "
              f"{v['float_std_fr3']-v['float_fr3']:+.2f}")
        print("\n  Q2  kusursuz yeniden siralama TAVANI (FR@3)")
        print(f"      {'M':>6s}{'sym adaylarindan':>20s}"
              f"{'qscale adaylarindan':>22s}")
        for M in MS:
            print(f"      {M:>6d}{v[f'oracle_fr3_from_sym_top{M}']:20.2f}"
                  f"{v[f'oracle_fr3_from_qscale_top{M}']:22.2f}")
        print(f"      gercek FR@3: sym {v['sym_fr3']:.2f}  "
              f"qscale {v['qscale_fr3']:.2f}  "
              f"float_std {v['float_std_fr3']:.2f}")
        print(f"      -> top-10 adaylardan kazanilabilecek: "
              f"{v['oracle_fr3_from_qscale_top10']-v['qscale_fr3']:+.2f} pp",
              flush=True)

    with open(os.path.join(HERE, "WHERE_NEXT.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("\nwrote WHERE_NEXT.json")


if __name__ == "__main__":
    main()
