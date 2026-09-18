#!/usr/bin/env python3
"""DECISIVE: was the 0.53 pp "fragility" drift a seed error of mine?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external reviewer claims the producer uses random_state=5101 for the
LSA32 stage and 5204 for the FINAL SVD96, and that my handoff conflated the
two.  Repo bytes agree with them (v52_t4c2_centering_geometry.py:37 is 5204;
v52_t4f1_beam_retrieval.py LATENT_SEED=5101 / MIXED_SEED=5204), and my
run_bottleneck.py used 5101 for the final SVD96.

If that is the whole story, rebuilding with 5204 should reproduce the cached
SIGN96 bits EXACTLY, and my "the sign code is numerically fragile" finding
collapses into "I used the wrong seed".

This rebuilds k archives from raw text under BOTH seeds and compares the
resulting sign bits to the frozen cache, bit for bit.
"""
import glob, json, os, pickle, sys
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_bottleneck as BN

CACHE = os.path.join(BN.SRC, "regen", "lme", "cache_repr", "%s.pkl")
SEEDS = (5101, 5204)


def rebuild(adapter, path, seed):
    item = json.loads(open(path, encoding="utf-8").read())
    memories, gold_ids, issues = adapter.build_archive(item)
    assert not issues, issues[:2]
    texts = adapter.fit_input_payload(memories)
    wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    q = str(item["question"])
    Qw = normalize(wv.transform([q])); Qc = normalize(cv.transform([q]))
    Ql = normalize(base_svd.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    sv = TruncatedSVD(n_components=96, random_state=seed)
    Y = normalize(sv.fit_transform(Z))
    QY = normalize(sv.transform(Zq))
    mu = Y.mean(axis=0, keepdims=True)
    return Y - mu, QY - mu


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    adapter = BN.load_adapter()
    files = sorted(glob.glob(BN.ITEMS))[:k]
    rows = []
    for f in files:
        tag = os.path.basename(f)[:-5]
        cp = CACHE % tag
        if not os.path.exists(cp):
            continue
        d = pickle.load(open(cp, "rb"))
        Cc = np.asarray(d["C"], float); Qc = np.asarray(d["qC"], float).reshape(1, -1)
        r = {"tag": tag, "N": int(Cc.shape[0])}
        for s in SEEDS:
            C, Q = rebuild(adapter, f, s)
            if C.shape != Cc.shape:
                r[str(s)] = None; continue
            db = int(np.count_nonzero((C >= 0) != (Cc >= 0)))
            qb = int(np.count_nonzero((Q >= 0) != (Qc >= 0)))
            r[str(s)] = {"doc_bit_diff": db,
                         "doc_bits": int(Cc.size),
                         "doc_bit_frac": db / Cc.size,
                         "query_bit_diff": qb,
                         "max_abs_coord_diff": float(np.abs(C - Cc).max())}
        rows.append(r)
        a, b = r.get("5101"), r.get("5204")
        print(f"  {tag} N={r['N']:4d}  "
              f"5101: {a['doc_bit_diff']:6d} bit farklı  |  "
              f"5204: {b['doc_bit_diff']:6d} bit farklı", flush=True)

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "question": "which seed reproduces the frozen SIGN96 cache",
           "n_archives": len(rows), "rows": rows}
    for s in SEEDS:
        tot = sum(r[str(s)]["doc_bit_diff"] for r in rows if r.get(str(s)))
        bits = sum(r[str(s)]["doc_bits"] for r in rows if r.get(str(s)))
        exact = sum(1 for r in rows if r.get(str(s))
                    and r[str(s)]["doc_bit_diff"] == 0
                    and r[str(s)]["query_bit_diff"] == 0)
        out[f"seed_{s}"] = {"archives_bit_exact": exact,
                            "archives": len(rows),
                            "total_bit_diff": tot, "total_bits": bits,
                            "bit_diff_frac": tot / bits if bits else None}
    with open(os.path.join(HERE, "AUDIT_SEED.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n=== SONUÇ ===")
    for s in SEEDS:
        v = out[f"seed_{s}"]
        print(f"  seed {s}: {v['archives_bit_exact']}/{v['archives']} arşiv "
              f"BİT-AYNI   ({v['bit_diff_frac']*100:.4f}% bit farkı)")
    print("\nwrote AUDIT_SEED.json")


if __name__ == "__main__":
    main()
