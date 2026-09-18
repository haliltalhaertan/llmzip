"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Cross-verify the incoming 2026-09-16 (gpt-6-pro) package against OUR independent
baseline run, then independently reproduce its central NEW claim (qscale).

Part A: our per_query_top10.jsonl arm means vs their DIAGNOSIS numbers.
Part B: independent implementation of their new arms from the SAME caches,
        using OUR scorer/metric/tie rule (audit_baseline_lib, already replay-gated):
          qscale      = sum_j b_dj * qC_j / sigma_j     (doc bits, numeric scaled query)
          qsign_dstd  = sum_j (C_dj/sigma_j) * b_qj     (numeric scaled doc, query bits)
        sigma from DOCUMENTS ONLY, per archive, ddof=0, floor 1e-12. No gold fitting.
"""
import glob, json, os, pickle, sys, time
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "audit"))
from audit_baseline_lib import (decode_pm1, det_top10, expected_hit, hrn,
                                pack_signs_bool)

R = "/mnt/c/Users/MDP/dev/llmzip-work"
PERLTQA_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
LME_GLOB = R + "/regen/lme/cache_repr/*.pkl"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
BASE = os.path.join(HERE, "..", "baseline", "per_query_top10.jsonl")
THEIRS = json.load(open(os.path.join(
    R, "incoming_20260916", "files", "LLMZIP_HATA_YERI_OZET_2026-09-16.json")))["hit10_percent"]


def sigma_docs(C):
    s = np.std(np.asarray(C, dtype=np.float64), axis=0, ddof=0)
    return np.maximum(s, 1e-12)


def arms_new(C, q, archive_id):
    C = np.asarray(C, dtype=np.float64)
    q = np.asarray(q, dtype=np.float64).reshape(-1)
    sg = sigma_docs(C)
    B = decode_pm1(pack_signs_bool(C >= 0)).astype(np.float64)   # doc bits as +-1
    qb = np.where(q >= 0, 1.0, -1.0)
    return {"qscale": B @ (q / sg), "qsign_dstd": (C / sg[None, :]) @ qb}


def main():
    t0 = time.time()
    # ---------- Part A ----------
    rows = [json.loads(l) for l in open(BASE, encoding="utf-8")]
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        for arm in ("sign96", "float_raw", "float_std", "asym"):
            acc[r["benchmark"]][arm + "|hit"].append(r[arm]["hit10"])
            acc[r["benchmark"]][arm + "|exp"].append(r[arm]["exp_hit10"])
    theirkey = {"sign96": "sign96", "float_raw": "centered_cos",
                "float_std": "standardized_cos", "asym": "doc_sign_query_raw"}
    bench = {"PerLTQA": "PerLTQA", "LME": "LME", "REALTALK": "RealTalk"}
    print("=== PART A: ours (independent code) vs theirs ===")
    print(f"{'bench':9} {'arm':11} {'our_realized':>12} {'our_expected':>12} {'theirs':>8} {'d_exp':>9}")
    maxdev = 0.0
    for b, tb in bench.items():
        for arm, tk in theirkey.items():
            hr = 100 * float(np.mean(acc[b][arm + "|hit"]))
            he = 100 * float(np.mean(acc[b][arm + "|exp"]))
            th = float(THEIRS[tb][tk])
            maxdev = max(maxdev, abs(he - th))
            print(f"{b:9} {arm:11} {hr:12.4f} {he:12.4f} {th:8.2f} {he-th:+9.4f}")
    print(f"max |our_expected - theirs| = {maxdev:.6f} pp  over 12 cells")

    # ---------- Part B ----------
    print("\n=== PART B: independent reproduction of their NEW arms ===")
    out = {}
    res = defaultdict(lambda: defaultdict(list))

    arch = pickle.load(open(PERLTQA_ARCH, "rb"))
    Q = pickle.load(open(PERLTQA_Q, "rb"))
    by_char = defaultdict(list)
    for qid, q in Q.items():
        by_char[q["char"]].append(qid)
    for char, qids in sorted(by_char.items()):
        C = np.asarray(arch[char]["C"], dtype=np.float64)
        for qid in sorted(qids):
            S = arms_new(C, Q[qid]["qC"], char)
            g = np.asarray(Q[qid]["gold"]).ravel().astype(int)
            for a, s in S.items():
                res["PerLTQA"][a + "|hit"].append(hrn(det_top10(s, char, 10), g)[0])
                res["PerLTQA"][a + "|exp"].append(expected_hit(s, g, 10))
    print(f"  PerLTQA done {time.time()-t0:.0f}s", flush=True)

    for f in sorted(glob.glob(LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        qid = d["question_id"]
        S = arms_new(d["C"], d["qC"], qid)
        g = np.asarray(d["gold"]).ravel().astype(int)
        for a, s in S.items():
            res["LME"][a + "|hit"].append(hrn(det_top10(s, qid, 10), g)[0])
            res["LME"][a + "|exp"].append(expected_hit(s, g, 10))

    for f in sorted(glob.glob(RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        aid = str(o["conv_id"])
        C = np.asarray(o["C"], dtype=np.float64)
        for qi, qid in enumerate(o["qids"]):
            g = [int(x) for x in o["gold_rows"][qi]]
            if not g:
                continue
            S = arms_new(C, o["QC"][qi], aid)
            g = np.asarray(g, dtype=int)
            for a, s in S.items():
                res["REALTALK"][a + "|hit"].append(hrn(det_top10(s, aid, 10), g)[0])
                res["REALTALK"][a + "|exp"].append(expected_hit(s, g, 10))

    tnew = {"qscale": "doc_sign_query_std", "qsign_dstd": "query_sign_doc_std"}
    print(f"{'bench':9} {'arm':11} {'n':>6} {'our_realized':>12} {'our_expected':>12} {'theirs':>8} {'d_exp':>9}")
    maxdev2 = 0.0
    for b, tb in bench.items():
        for a, tk in tnew.items():
            n = len(res[b][a + "|hit"])
            hr = 100 * float(np.mean(res[b][a + "|hit"]))
            he = 100 * float(np.mean(res[b][a + "|exp"]))
            th = float(THEIRS[tb][tk])
            maxdev2 = max(maxdev2, abs(he - th))
            out[f"{b}|{a}"] = {"n": n, "realized": hr, "expected": he, "theirs": th}
            print(f"{b:9} {a:11} {n:6d} {hr:12.4f} {he:12.4f} {th:8.2f} {he-th:+9.4f}")
    print(f"max |our_expected - theirs| = {maxdev2:.6f} pp  over 6 cells")

    print("\n=== headline delta: qscale - sign96 (same 12-byte doc codes) ===")
    for b in bench:
        s_r = 100 * float(np.mean(acc[b]["sign96|hit"]))
        s_e = 100 * float(np.mean(acc[b]["sign96|exp"]))
        q_r = 100 * float(np.mean(res[b]["qscale|hit"]))
        q_e = 100 * float(np.mean(res[b]["qscale|exp"]))
        print(f"{b:9} realized {q_r-s_r:+7.3f} pp   expected {q_e-s_e:+7.3f} pp")

    json.dump({"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                          "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
               "partA_max_dev_pp": maxdev, "partB_max_dev_pp": maxdev2,
               "partB": out, "elapsed_s": time.time() - t0},
              open(os.path.join(HERE, "verify_incoming.json"), "w"), indent=2)
    print(f"\nelapsed {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
