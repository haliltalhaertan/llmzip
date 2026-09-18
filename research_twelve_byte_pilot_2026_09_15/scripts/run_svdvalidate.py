#!/usr/bin/env python3
"""Does the exact Gram SVD match the frozen pipeline's retrieval quality?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

run_svdopt.py showed the Gram path is 16.7x faster and needs no 75 MB
projector, but ALSO that it produces different codes -- because sklearn's
randomized TruncatedSVD is itself an approximation, so "exact" is not the
same object as "production".  Speed is worthless if quality moves, so this
re-measures the whole of LongMemEval under the exact path and compares
against the frozen, independently cached numbers:

    sym   hit@10 = 86.08 %      float hit@10 = 82.55 %

Neither method is assumed better.  The output is the paired difference with
a confidence interval; a difference whose interval covers zero means the
speedup is free, and anything else means it is a representation change that
needs its own authorisation.

Usage: python run_svdvalidate.py [shard] [n_shards]
"""
import glob
import json
import os
import sys
import time

import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_ksweep as KS  # noqa: E402
import run_bottleneck as BN  # noqa: E402
import run_svdopt as OPT  # noqa: E402
# !!! SEED DEFECT: OPT.method_A uses random_state=5101, which is the LSA32
# seed, not the production SVD96 seed 5204.  This script therefore compared
# the exact Gram path against a NON-PRODUCTION randomized draw.  Its
# published numbers (+0.21 pp float, -1.67 pp sign) are INVALID as a
# statement about production and must be re-run.  See audit_seed.py.


def main():
    shard = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    nshard = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    files = sorted(glob.glob(BN.ITEMS))
    assert len(files) == 470, len(files)
    if nshard > 1:
        files = files[shard::nshard]
    ad = BN.load_adapter()
    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "shard": [shard, nshard], "rows": [], "skipped": []}
    t0 = time.perf_counter()
    for i, f in enumerate(files):
        try:
            item = json.loads(open(f, encoding="utf-8").read())
            mem, gold_ids, issues = ad.build_archive(item)
            if issues:
                raise RuntimeError(f"issues {issues[:1]}")
            texts = ad.fit_input_payload(mem)
            row_of = {m["memory_id"]: k for k, m in enumerate(mem)}
            gold = np.asarray([row_of[g] for g in gold_ids], dtype=int)
            wv, cv, bs, Xw, Xc, Xl = ad.fit_archive_representation(texts)
            Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
            q = str(item["question"])
            Qw = normalize(wv.transform([q]))
            Zq = sparse.hstack([
                sparse.csr_matrix(normalize(bs.transform(Qw))),
                Qw, normalize(cv.transform([q]))], format="csr")
            tA = time.perf_counter()
            YA, QA, pA = OPT.method_A(Z, Zq)
            tA = time.perf_counter() - tA
            tB = time.perf_counter()
            YB, QB, pB = OPT.method_B(Z, Zq)
            tB = time.perf_counter() - tB
            sA, sB = OPT.arms(YA, QA), OPT.arms(YB, QB)
            r = {"qid": item["question_id"], "N": int(Z.shape[0]),
                 "t_A": tA, "t_B": tB, "proj_A": pA, "proj_B": pB}
            for a in ("float", "sym"):
                r[f"A_{a}"] = KS.hit_from_facts(
                    *KS.bucket_facts(sA[a], gold), 10)
                r[f"B_{a}"] = KS.hit_from_facts(
                    *KS.bucket_facts(sB[a], gold), 10)
            out["rows"].append(r)
        except Exception as e:  # noqa: BLE001
            out["skipped"].append({"file": os.path.basename(f),
                                   "error": repr(e)})
        if (i + 1) % 10 == 0:
            el = time.perf_counter() - t0
            print(f"  {i + 1}/{len(files)} {el:.0f}s "
                  f"({el / (i + 1):.2f}s/item)", flush=True)
    out["elapsed_seconds"] = time.perf_counter() - t0
    name = ("SVDVALIDATE.json" if nshard == 1
            else f"SVDVALIDATE_shard{shard}of{nshard}.json")
    with open(name, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"wrote {name}", flush=True)


if __name__ == "__main__":
    main()
