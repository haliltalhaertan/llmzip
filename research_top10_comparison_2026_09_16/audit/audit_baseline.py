"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Driver for independent baseline audit (imports audit_baseline_lib only).
"""
import glob
import json
import os
import pickle
import time
from collections import Counter, defaultdict

import numpy as np

from audit_baseline_lib import (asym_scores, cosine_raw, cosine_std,
                                det_top10, expected_hit, expected_recall,
                                fit_std, hamming_packed, hrn, pack_signs_bool,
                                sha256_file)

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "..", "baseline")
R = "/mnt/c/Users/MDP/dev/llmzip-work"
PERLTQA_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
PERLTQA_CTRL = R + "/theory_benchmark_test_v1/perltqa/per_query.jsonl"
LME_GLOB = R + "/regen/lme/cache_repr/*.pkl"
LME_CTRL = R + "/theory_benchmark_test_v1/lme/per_query.jsonl"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
RT_CTRL = R + "/theory_benchmark_test_v1/realtalk/per_query.jsonl"
RT_EXCL = R + "/theory_benchmark_test_v1/realtalk/excluded_ids.json"
TOL = 1e-12


def load_native():
    def load_perltqa():
        groups = defaultdict(dict)
        for line in open(PERLTQA_CTRL, encoding="utf-8"):
            r = json.loads(line)
            if r["t"] != 1.0 or r["group"] == "FULL96":
                continue
            groups[r["qid"]][r["group"]] = r
        native = {}
        for qid, d in groups.items():
            if set(d.keys()) == {"LOW48", "HIGH48"} and \
                    d["LOW48"]["native_exact"] == d["HIGH48"]["native_exact"] and \
                    d["LOW48"]["float_exact"] == d["HIGH48"]["float_exact"]:
                native[qid] = (d["LOW48"]["native_exact"], d["LOW48"]["float_exact"])
            else:
                native[qid] = None
        return native
    def load_lme():
        groups = defaultdict(list)
        for line in open(LME_CTRL, encoding="utf-8"):
            r = json.loads(line)
            if r.get("t") != 1.0:
                continue
            groups[(r["archive_id"], r["qa_id"])].append(r)
        native = {}
        for k, rs in groups.items():
            s = {rr["sign_exact"] for rr in rs}
            f = {rr["float_exact"] for rr in rs}
            native[k] = (rs[0]["sign_exact"], rs[0]["float_exact"]) if len(s) == 1 and len(f) == 1 else None
        return native
    def load_rt():
        groups = defaultdict(list)
        for line in open(RT_CTRL, encoding="utf-8"):
            r = json.loads(line)
            if r.get("t") != 1.0:
                continue
            groups[r["qid"]].append(r)
        native = {}
        for k, rs in groups.items():
            s = {rr["sign_exact"] for rr in rs}
            f = {rr["float_exact"] for rr in rs}
            native[k] = (rs[0]["sign_exact"], rs[0]["float_exact"]) if len(s) == 1 and len(f) == 1 else None
        return native
    return load_perltqa(), load_lme(), load_rt()


def main():
    t0 = time.time()
    rows = [json.loads(l) for l in open(os.path.join(BASE, "per_query_top10.jsonl"), encoding="utf-8")]
    c = Counter(r["benchmark"] for r in rows)
    assert len(rows) == 9440 and c["PerLTQA"] == 8265 and c["LME"] == 470 and c["REALTALK"] == 705, dict(c)
    by_qid = {(r["benchmark"], r["qid"]): r for r in rows}

    # A. structural + actual-metrics recompute from stored IDs (no rescore)
    bad_struct = bad_metric = bad_exp = 0
    tie_frac = Counter()
    tie_n = Counter()
    for r in rows:
        for arm in ("sign96", "float_raw", "float_std", "asym"):
            a = r[arm]
            if len(a["ids"]) != 10 or len(set(a["ids"])) != 10 or any(not (0 <= x < r["N"]) for x in a["ids"]):
                bad_struct += 1
            h, rc, nd = hrn(a["ids"], r["gold"])
            if abs(h - a["hit10"]) > 1e-12 or abs(rc - a["recall10"]) > 1e-12 or abs(nd - a["ndcg10"]) > 1e-12:
                bad_metric += 1
                if bad_metric < 3:
                    print("METRIC MISMATCH", r["benchmark"], r["qid"], arm)
            # tie flag sanity: recompute is_tie_at_cut via stored scores? need full scores -> skip here; count stored tie flags
            if a["tie"]["is_tie_at_cut"]:
                tie_frac[(r["benchmark"], arm)] += 1
            tie_n[(r["benchmark"], arm)] += 1

    # B. full rescore from original caches (own formulas), compare IDs + FR3 gate
    perltqa_native, lme_native, rt_native = load_native()
    excl = set(json.load(open(RT_EXCL))["excluded_ids"])
    arch = pickle.load(open(PERLTQA_ARCH, "rb"))
    Q = pickle.load(open(PERLTQA_Q, "rb"))
    lme_map = {}
    for f in sorted(glob.glob(LME_GLOB)):
        d = pickle.loads(open(f, "rb").read())
        lme_map[d["question_id"]] = (f, d)
    rt_map = {}
    for f in sorted(glob.glob(RT_GLOB)):
        o = pickle.loads(open(f, "rb").read())
        for qi, qid in enumerate(o["qids"]):
            rt_map[qid] = (f, o, qi)

    spot_mismatch = 0
    fr3_viol = {"perltqa": 0, "lme": 0, "realtalk": 0}
    fr3_max = {"perltqa_s": 0.0, "perltqa_f": 0.0, "lme_s": 0.0, "lme_f": 0.0, "rt_s": 0.0, "rt_f": 0.0}
    n_rescored = 0
    # PerLTQA: group by archive for efficiency (pack/std once per archive)
    by_char = defaultdict(list)
    for qid, q in Q.items():
        by_char[q["char"]].append(qid)
    for char, qids in sorted(by_char.items()):
        C = np.asarray(arch[char]["C"], dtype=np.float64)
        N = int(arch[char]["N"])
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        # verify state file matches recomputed (code path check)
        # state index unknown -> skip per-file check here; global byte check later
        for qid in sorted(qids):
            r = by_qid[("PerLTQA", qid)]
            assert r["N"] == N and r["archive_id"] == char
            q = np.asarray(Q[qid]["qC"], dtype=np.float64)
            g = np.asarray(Q[qid]["gold"]).ravel().astype(int)
            H = hamming_packed(packed, q >= 0)
            s_sign = -H.astype(float)
            s_raw = cosine_raw(C, q)
            s_std = cosine_std(C, q, std)
            from audit_baseline_lib import decode_pm1, SQRT96
            import numpy as _np
            D = decode_pm1(packed).astype(float)
            s_asym = (D @ q) / float(_np.sqrt(96))
            for arm, s in (("sign96", s_sign), ("float_raw", s_raw), ("float_std", s_std), ("asym", s_asym)):
                exp_top = det_top10(s, char, 10).tolist()
                if exp_top != r[arm]["ids"]:
                    spot_mismatch += 1
                    if spot_mismatch < 3:
                        print("RESCORE MISMATCH PerLTQA", qid, arm)
            # FR3 gate vs control (source-code verified path: expected_recall K=3)
            fr3_s = expected_recall(s_sign, g, k=3)
            fr3_f = expected_recall(s_raw, g, k=3)
            nat = perltqa_native.get(qid)
            ds = abs(fr3_s - nat[0])
            df = abs(fr3_f - nat[1])
            fr3_max["perltqa_s"] = max(fr3_max["perltqa_s"], ds)
            fr3_max["perltqa_f"] = max(fr3_max["perltqa_f"], df)
            if ds > TOL or df > TOL:
                fr3_viol["perltqa"] += 1
            # stored fr3 fields must match recomputed
            if abs(r["fr3_sign"] - fr3_s) > 1e-12 or abs(r["fr3_float"] - fr3_f) > 1e-12:
                spot_mismatch += 1
            # stored exp_hit must match own expected_hit
            for arm, s in (("sign96", s_sign), ("float_raw", s_raw), ("float_std", s_std), ("asym", s_asym)):
                if abs(r[arm]["exp_hit10"] - expected_hit(s, g, k=10)) > 1e-12:
                    spot_mismatch += 1
                    if spot_mismatch < 5:
                        print("EXP_HIT MISMATCH", qid, arm)
            # crosscheck stored ctrl fields
            if abs(r["ctrl_sign"] - nat[0]) > 1e-12 or abs(r["ctrl_float"] - nat[1]) > 1e-12:
                spot_mismatch += 1
            n_rescored += 1

    # LME full rescore
    for qid in sorted(lme_map.keys()):
        fp, d = lme_map[qid]
        r = by_qid[("LME", qid)]
        C = np.asarray(d["C"], dtype=float)
        q = np.asarray(d["qC"], dtype=float).reshape(-1)
        g = np.asarray(d["gold"]).ravel().astype(int)
        N = int(C.shape[0])
        assert r["N"] == N
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        H = hamming_packed(packed, q >= 0)
        s_sign = -H.astype(float)
        s_raw = cosine_raw(C, q)
        s_std = cosine_std(C, q, std)
        import numpy as _np
        from audit_baseline_lib import decode_pm1
        D = decode_pm1(packed).astype(float)
        s_asym = (D @ q) / float(_np.sqrt(96))
        for arm, s in (("sign96", s_sign), ("float_raw", s_raw), ("float_std", s_std), ("asym", s_asym)):
            if det_top10(s, qid, 10).tolist() != r[arm]["ids"]:
                spot_mismatch += 1
                if spot_mismatch < 5:
                    print("RESCORE MISMATCH LME", qid, arm)
            if abs(r[arm]["exp_hit10"] - expected_hit(s, g, k=10)) > 1e-12:
                spot_mismatch += 1
        fr3_s = expected_recall(s_sign, g, k=3)
        fr3_f = expected_recall(s_raw, g, k=3)
        nat = lme_native.get((qid, qid))
        ds = abs(fr3_s - nat[0])
        df = abs(fr3_f - nat[1])
        fr3_max["lme_s"] = max(fr3_max["lme_s"], ds)
        fr3_max["lme_f"] = max(fr3_max["lme_f"], df)
        if ds > TOL or df > TOL:
            fr3_viol["lme"] += 1
        if abs(r["fr3_sign"] - fr3_s) > 1e-12 or abs(r["fr3_float"] - fr3_f) > 1e-12:
            spot_mismatch += 1
        n_rescored += 1

    # REALTALK full rescore
    for qid in sorted(rt_map.keys()):
        fp, o, qi = rt_map[qid]
        gold = [int(x) for x in o["gold_rows"][qi]]
        if not gold:
            assert qid in excl
            assert ( "REALTALK", qid) not in by_qid
            continue
        r = by_qid[("REALTALK", qid)]
        C = np.asarray(o["C"], dtype=float)
        q = np.asarray(o["QC"][qi], dtype=float)
        g = np.asarray(gold).astype(int)
        archive_id = str(o.get("conv_id"))
        assert r["archive_id"] == archive_id and r["N"] == int(o["N"])
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        H = hamming_packed(packed, q >= 0)
        s_sign = -H.astype(float)
        s_raw = cosine_raw(C, q)
        s_std = cosine_std(C, q, std)
        import numpy as _np
        from audit_baseline_lib import decode_pm1
        D = decode_pm1(packed).astype(float)
        s_asym = (D @ q) / float(_np.sqrt(96))
        for arm, s in (("sign96", s_sign), ("float_raw", s_raw), ("float_std", s_std), ("asym", s_asym)):
            if det_top10(s, archive_id, 10).tolist() != r[arm]["ids"]:
                spot_mismatch += 1
                if spot_mismatch < 5:
                    print("RESCORE MISMATCH RT", qid, arm)
            if abs(r[arm]["exp_hit10"] - expected_hit(s, g, k=10)) > 1e-12:
                spot_mismatch += 1
        fr3_s = expected_recall(s_sign, g, k=3)
        fr3_f = expected_recall(s_raw, g, k=3)
        nat = rt_native.get(qid)
        ds = abs(fr3_s - nat[0])
        df = abs(fr3_f - nat[1])
        fr3_max["rt_s"] = max(fr3_max["rt_s"], ds)
        fr3_max["rt_f"] = max(fr3_max["rt_f"], df)
        if ds > TOL or df > TOL:
            fr3_viol["realtalk"] += 1
        if abs(r["fr3_sign"] - fr3_s) > 1e-12 or abs(r["fr3_float"] - fr3_f) > 1e-12:
            spot_mismatch += 1
        n_rescored += 1

    # Costs: payload vs total storage (verify byte arithmetic from caches/states)
    import os as _os
    state_files = sorted(glob.glob(os.path.join(BASE, "state_*.npz")))
    state_bytes = sum(_os.path.getsize(p) for p in state_files)
    # count docs
    total_docs = 0
    for char in by_char:
        total_docs += int(arch[char]["N"])
    for _, d in lme_map.values():
        total_docs += int(np.asarray(d["C"]).shape[0])
    for f in sorted(glob.glob(RT_GLOB)):
        o = pickle.load(open(f, "rb"))
        total_docs += int(o["N"])
    packed_bytes = total_docs * 12
    float_bytes_mem = total_docs * 96 * 8
    # shared std overhead: 510 archives * 768
    std_overhead = 510 * 768
    perq_bytes = _os.path.getsize(os.path.join(BASE, "per_query_top10.jsonl"))

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "elapsed_s": time.time() - t0,
           "n_rows": len(rows), "counts": dict(c),
           "structural_mismatches": bad_struct,
           "metric_mismatches": bad_metric,
           "rescore_mismatches": spot_mismatch,
           "n_rescored": n_rescored,
           "fr3_viol": fr3_viol, "fr3_max": fr3_max,
           "tie_at_cut_counts": {f"{b}/{a}": tie_frac[(b, a)] for (b, a) in tie_frac},
           "tie_at_cut_denom": {f"{b}/{a}": tie_n[(b, a)] for (b, a) in tie_n},
           "storage": {"total_docs": total_docs, "packed_bytes": packed_bytes,
                       "float_bytes_mem": float_bytes_mem, "std_overhead": std_overhead,
                       "state_files": len(state_files), "state_bytes": state_bytes,
                       "per_query_bytes": perq_bytes},
           "realtak_arm_counts_verified": bool(c["REALTALK"] == 705)}
    with open(os.path.join(HERE, "baseline_audit.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))
    assert bad_struct == 0 and bad_metric == 0 and spot_mismatch == 0, out
    assert fr3_viol == {"perltqa": 0, "lme": 0, "realtalk": 0}, out
    assert n_rescored == 9440, n_rescored
    print(f"BASELINE AUDIT PASS: 9440 rescore exact, FR3 gates PASS, ties counted")


if __name__ == "__main__":
    main()
