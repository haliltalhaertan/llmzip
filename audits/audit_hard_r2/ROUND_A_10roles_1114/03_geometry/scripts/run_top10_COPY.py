# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""Baseline Top10-r1 runner: gates + 4 cached-representation arms.

Reads caches/comparators read-only; writes ONLY to CWD (assigned baseline dir).
Does NOT import parallel_ideas run.py main; own implementation in metrics_top10.

Usage:
  $HOME/muse-work/ml-python run_top10.py --all
  $HOME/muse-work/ml-python run_top10.py --gate-only
"""
import argparse
import glob
import hashlib
import json
import os
import pickle
import resource
import time
from collections import defaultdict

import numpy as np

from metrics_top10 import (
    TIE_SALT,
    asym_scores,
    cosine_raw,
    cosine_std,
    deterministic_top10,
    expected_hit_at_k,
    expected_recall_at_k,
    fit_std,
    hamming_from_packed,
    hit_recall_ndcg_at_k,
    pack_signs_bool,
)

LABELS = ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED", "NOT FOR CITATION",
          "DISCLOSE-BEFORE-USE"]
TOL = 1e-12
K3 = 3
K10 = 10

R = "/mnt/c/Users/MDP/dev/llmzip-work"
PERLTQA_ARCH = R + "/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
PERLTQA_Q = R + "/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
PERLTQA_CTRL = R + "/theory_benchmark_test_v1/perltqa/per_query.jsonl"
LME_GLOB = R + "/regen/lme/cache_repr/*.pkl"
LME_CTRL = R + "/theory_benchmark_test_v1/lme/per_query.jsonl"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
RT_CTRL = R + "/theory_benchmark_test_v1/realtalk/per_query.jsonl"
RT_EXCL = R + "/theory_benchmark_test_v1/realtalk/excluded_ids.json"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def peak_rss_mb():
    return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0


def load_perltqa_native():
    groups = defaultdict(dict)
    n_t1 = 0
    for line in open(PERLTQA_CTRL, encoding="utf-8"):
        r = json.loads(line)
        if r["t"] != 1.0 or r["group"] == "FULL96":
            continue
        n_t1 += 1
        groups[r["qid"]][r["group"]] = r
    native = {}
    for qid, d in groups.items():
        if set(d.keys()) == {"LOW48", "HIGH48"} and \
                d["LOW48"]["native_exact"] == d["HIGH48"]["native_exact"] and \
                d["LOW48"]["float_exact"] == d["HIGH48"]["float_exact"]:
            native[qid] = (d["LOW48"]["native_exact"], d["LOW48"]["float_exact"],
                           d["LOW48"])
        else:
            native[qid] = None
    return groups, native, n_t1


def load_lme_native():
    groups = defaultdict(list)
    n_t1 = 0
    for line in open(LME_CTRL, encoding="utf-8"):
        r = json.loads(line)
        if r.get("t") != 1.0:
            continue
        n_t1 += 1
        groups[(r["archive_id"], r["qa_id"])].append(r)
    native = {}
    for k, rs in groups.items():
        s = {rr["sign_exact"] for rr in rs}
        f = {rr["float_exact"] for rr in rs}
        if len(s) == 1 and len(f) == 1:
            native[k] = (rs[0]["sign_exact"], rs[0]["float_exact"], rs[0])
        else:
            native[k] = None
    return groups, native, n_t1


def load_rt_native():
    groups = defaultdict(list)
    n_t1 = 0
    for line in open(RT_CTRL, encoding="utf-8"):
        r = json.loads(line)
        if r.get("t") != 1.0:
            continue
        n_t1 += 1
        groups[r["qid"]].append(r)
    native = {}
    for k, rs in groups.items():
        s = {rr["sign_exact"] for rr in rs}
        f = {rr["float_exact"] for rr in rs}
        if len(s) == 1 and len(f) == 1:
            native[k] = (rs[0]["sign_exact"], rs[0]["float_exact"], rs[0])
        else:
            native[k] = None
    return groups, native, n_t1


def score_one_query(C, packed, std, q, gold):
    g = np.asarray(gold).ravel().astype(int)
    H = hamming_from_packed(packed, np.asarray(q) >= 0)
    s_sign = (-H.astype(float))
    s_raw = cosine_raw(C, q)
    s_std = cosine_std(C, q, std)
    s_asym = asym_scores(packed, q)
    return {"H": H, "s_sign": s_sign, "s_raw": s_raw, "s_std": s_std,
            "s_asym": s_asym, "gold": g}


def top10_record(scores, archive_id, gold, k=10):
    top = deterministic_top10(scores, archive_id, k=k)
    assert len(top) == min(k, len(np.asarray(scores).ravel()))
    assert len(set(map(int, top.tolist()))) == len(top)
    hit, rec, ndcg = hit_recall_ndcg_at_k(top, gold, k=k)
    exp_hit = expected_hit_at_k(scores, gold, k=k)
    sm = np.where(np.isfinite(np.asarray(scores, dtype=float)), np.asarray(scores, dtype=float), -np.inf)
    uniq = np.unique(sm)[::-1]
    better = 0
    binfo = {"better": 0, "bucket_size": 0, "gold_in_bucket": 0, "take": 0, "is_tie_at_cut": False}
    gset = set(map(int, np.asarray(gold).ravel().tolist()))
    for lv in uniq:
        idx = np.nonzero(sm == lv)[0]
        B = len(idx)
        if better >= k:
            break
        if better + B <= k:
            better += B
            continue
        gb = sum(1 for i in idx if int(i) in gset)
        binfo = {"better": int(better), "bucket_size": int(B),
                 "gold_in_bucket": int(gb), "take": int(k - better),
                 "is_tie_at_cut": bool(B > 1)}
        break
    top_scores = [float(np.asarray(scores, dtype=float)[int(r)]) if np.isfinite(float(np.asarray(scores, dtype=float)[int(r)])) else None for r in top.tolist()]
    # store None for -inf-mapped nonfinite to make JSON explicit; replay maps None->worst
    return {"ids": [int(x) for x in top.tolist()], "scores": top_scores,
            "hit10": float(hit), "recall10": float(rec), "ndcg10": float(ndcg),
            "exp_hit10": float(exp_hit), "tie": binfo}


def run_all():
    t_all0 = time.perf_counter()
    wall0 = time.time()
    hashes_before = {}
    for p in [PERLTQA_ARCH, PERLTQA_Q, PERLTQA_CTRL, LME_CTRL, RT_CTRL, RT_EXCL]:
        hashes_before[p] = sha256_file(p)
    for f in sorted(glob.glob(LME_GLOB)):
        hashes_before[f] = sha256_file(f)
    for f in sorted(glob.glob(RT_GLOB)):
        hashes_before[f] = sha256_file(f)

    _, perltqa_native, perltqa_t1 = load_perltqa_native()
    _, lme_native, lme_t1 = load_lme_native()
    _, rt_native, rt_t1 = load_rt_native()
    excl = json.load(open(RT_EXCL))
    excluded = set(excl["excluded_ids"])

    gate_rows = {"perltqa": {"n": 0, "viol": [], "maxd_s": 0.0, "maxd_f": 0.0},
                 "lme": {"n": 0, "viol": [], "maxd_s": 0.0, "maxd_f": 0.0},
                 "realtalk": {"n": 0, "viol": [], "maxd_s": 0.0, "maxd_f": 0.0}}
    all_rows = []
    timing = {"archives": [], "t_fit_total": 0.0, "t_score_total": 0.0,
              "t_rank_total": 0.0}
    zero_vec_report = {"perltqa_zero_docs": 0, "perltqa_zero_queries": 0,
                       "lme_zero_docs": 0, "lme_zero_queries": 0,
                       "rt_zero_docs": 0, "rt_zero_queries": 0}
    # ---- PerLTQA (30 archives) ----
    arch = pickle.load(open(PERLTQA_ARCH, "rb"))
    Q = pickle.load(open(PERLTQA_Q, "rb"))
    by_char = defaultdict(list)
    for qid, q in Q.items():
        by_char[q["char"]].append(qid)
    chars = sorted(by_char.keys())
    assert len(chars) == 30 and len(Q) == 8265, (len(chars), len(Q))
    for ai, char in enumerate(chars):
        t_a0 = time.perf_counter()
        C = np.asarray(arch[char]["C"], dtype=np.float64)
        N = int(arch[char]["N"])
        assert C.shape == (N, 96) and np.isfinite(C).all()
        dn = np.linalg.norm(C, axis=1)
        zero_vec_report["perltqa_zero_docs"] += int(np.sum(dn == 0))
        t_fit0 = time.perf_counter()
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        t_fit = time.perf_counter() - t_fit0
        assert packed.shape == (N, 12)
        spath = f"state_perltqa_{ai:02d}.npz"
        np.savez(spath, packed=packed, std=std)
        import os as _os
        state_bytes = int(_os.path.getsize(spath))
        state_sha = sha256_file(spath)
        ql = sorted(by_char[char])
        ckpt = f"ckpt_top10_perltqa_{ai:02d}.jsonl"
        rows = []
        t_score = t_rank = 0.0
        for qid in ql:
            qq = Q[qid]
            q = np.asarray(qq["qC"], dtype=np.float64)
            if float(np.linalg.norm(q)) == 0:
                zero_vec_report["perltqa_zero_queries"] += 1
            g = np.asarray(qq["gold"]).ravel().astype(int)
            assert len(g) > 0 and np.all((g >= 0) & (g < N))
            t_s0 = time.perf_counter()
            sc = score_one_query(C, packed, std, q, g)
            fr3_s = expected_recall_at_k(sc["s_sign"], g, k=K3)
            fr3_f = expected_recall_at_k(sc["s_raw"], g, k=K3)
            t_score += time.perf_counter() - t_s0
            # gate vs control
            nat = perltqa_native.get(qid)
            assert nat is not None, qid
            ds = abs(fr3_s - nat[0])
            df = abs(fr3_f - nat[1])
            gr = gate_rows["perltqa"]
            gr["n"] += 1
            gr["maxd_s"] = max(gr["maxd_s"], ds)
            gr["maxd_f"] = max(gr["maxd_f"], df)
            if ds > TOL or df > TOL:
                gr["viol"].append({"qid": qid, "ds": ds, "df": df})
            t_r0 = time.perf_counter()
            r_sign = top10_record(sc["s_sign"], char, g, k=K10)
            r_raw = top10_record(sc["s_raw"], char, g, k=K10)
            r_std = top10_record(sc["s_std"], char, g, k=K10)
            r_asym = top10_record(sc["s_asym"], char, g, k=K10)
            t_rank += time.perf_counter() - t_r0
            rows.append({
                "benchmark": "PerLTQA", "qid": qid, "archive_id": char,
                "section": qq["section"], "N": N, "gold": [int(x) for x in g.tolist()],
                "gold_size": int(len(g)), "cache_file": PERLTQA_ARCH,
                "cache_sha256": hashes_before[PERLTQA_ARCH],
                "state_file": spath, "state_sha256": state_sha,
                "state_bytes": state_bytes, "packed_bytes": int(N * 12),
                "float_bytes_mem": int(N * 96 * 8), "shared_std_bytes": 768,
                "fr3_sign": float(fr3_s), "fr3_float": float(fr3_f),
                "ctrl_sign": float(nat[0]), "ctrl_float": float(nat[1]),
                "sign96": r_sign, "float_raw": r_raw, "float_std": r_std,
                "asym": r_asym})
        with open(ckpt, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        all_rows.extend(rows)
        dt = time.perf_counter() - t_a0
        timing["archives"].append({"bench": "PerLTQA", "archive": char, "nq": len(rows),
                                   "fit_s": t_fit, "score_s": t_score, "rank_s": t_rank,
                                   "total_s": dt})
        timing["t_fit_total"] += t_fit
        timing["t_score_total"] += t_score
        timing["t_rank_total"] += t_rank
        print(f"PerLTQA {ai+1}/30 {char} nq={len(rows)} fit={t_fit:.2f}s score={t_score:.2f}s rank={t_rank:.2f}s rss={peak_rss_mb():.0f}MB", flush=True)
        del C, packed, std
    # ---- LME (470 single-query archives) ----
    lme_files = sorted(glob.glob(LME_GLOB))
    assert len(lme_files) == 470
    for ai, fp in enumerate(lme_files):
        t_a0 = time.perf_counter()
        d = pickle.loads(open(fp, "rb").read())
        qid = d["question_id"]
        C = np.asarray(d["C"], dtype=float)
        q = np.asarray(d["qC"], dtype=float).reshape(-1)
        g = np.asarray(d["gold"]).ravel().astype(int)
        N = int(C.shape[0])
        assert C.shape[1] == 96 and q.shape == (96,)
        assert len(g) > 0 and np.all((g >= 0) & (g < N))
        if int(np.sum(np.linalg.norm(C, axis=1) == 0)):
            zero_vec_report["lme_zero_docs"] += int(np.sum(np.linalg.norm(C, axis=1) == 0))
        if float(np.linalg.norm(q)) == 0:
            zero_vec_report["lme_zero_queries"] += 1
        t_fit0 = time.perf_counter()
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        t_fit = time.perf_counter() - t_fit0
        spath = f"state_lme_{ai:03d}.npz"
        np.savez(spath, packed=packed, std=std)
        import os as _os
        state_bytes = int(_os.path.getsize(spath))
        state_sha = sha256_file(spath)
        t_s0 = time.perf_counter()
        sc = score_one_query(C, packed, std, q, g)
        fr3_s = expected_recall_at_k(sc["s_sign"], g, k=K3)
        fr3_f = expected_recall_at_k(sc["s_raw"], g, k=K3)
        t_score = time.perf_counter() - t_s0
        key = (qid, qid)
        nat = lme_native.get(key)
        assert nat is not None, key
        ds = abs(fr3_s - nat[0])
        df = abs(fr3_f - nat[1])
        gr = gate_rows["lme"]
        gr["n"] += 1
        gr["maxd_s"] = max(gr["maxd_s"], ds)
        gr["maxd_f"] = max(gr["maxd_f"], df)
        if ds > TOL or df > TOL:
            gr["viol"].append({"qid": qid, "ds": ds, "df": df})
        t_r0 = time.perf_counter()
        r_sign = top10_record(sc["s_sign"], qid, g, k=K10)
        r_raw = top10_record(sc["s_raw"], qid, g, k=K10)
        r_std = top10_record(sc["s_std"], qid, g, k=K10)
        r_asym = top10_record(sc["s_asym"], qid, g, k=K10)
        t_rank = time.perf_counter() - t_r0
        ckpt = f"ckpt_top10_lme_{ai:03d}.jsonl"
        row = {"benchmark": "LME", "qid": qid, "archive_id": qid,
               "section": nat[2].get("section", "unknown"), "N": N,
               "gold": [int(x) for x in g.tolist()], "gold_size": int(len(g)),
               "cache_file": fp, "cache_sha256": hashes_before[fp],
               "state_file": spath, "state_sha256": state_sha,
               "state_bytes": state_bytes, "packed_bytes": int(N * 12),
               "float_bytes_mem": int(N * 96 * 8), "shared_std_bytes": 768,
               "fr3_sign": float(fr3_s), "fr3_float": float(fr3_f),
               "ctrl_sign": float(nat[0]), "ctrl_float": float(nat[1]),
               "sign96": r_sign, "float_raw": r_raw, "float_std": r_std,
               "asym": r_asym}
        with open(ckpt, "w", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
        all_rows.append(row)
        timing["archives"].append({"bench": "LME", "archive": qid, "nq": 1,
                                   "fit_s": t_fit, "score_s": t_score, "rank_s": t_rank,
                                   "total_s": time.perf_counter() - t_a0})
        timing["t_fit_total"] += t_fit
        timing["t_score_total"] += t_score
        timing["t_rank_total"] += t_rank
        if (ai + 1) % 100 == 0 or ai + 1 == len(lme_files):
            print(f"LME {ai+1}/{len(lme_files)} rss={peak_rss_mb():.0f}MB", flush=True)
        del C, packed, std
    # ---- REALTALK (10 archives, 705 valid) ----
    rt_files = sorted(glob.glob(RT_GLOB))
    assert len(rt_files) == 10
    n_valid = 0
    for ci, fp in enumerate(rt_files):
        t_a0 = time.perf_counter()
        o = pickle.loads(open(fp, "rb").read())
        C = np.asarray(o["C"], dtype=float)
        QC = np.asarray(o["QC"], dtype=float)
        N = int(o["N"])
        assert C.shape == (N, 96)
        assert len(o["qids"]) == QC.shape[0] == len(o["gold_rows"])
        id_to_row = o.get("id_to_row", {})
        assert len(id_to_row) == N and set(id_to_row.values()) == set(range(N)), "id_to_row must be full permutation"
        row_to_id = {v: k for k, v in id_to_row.items()}
        dn = np.linalg.norm(C, axis=1)
        zero_vec_report["rt_zero_docs"] += int(np.sum(dn == 0))
        t_fit0 = time.perf_counter()
        std = fit_std(C)
        packed = pack_signs_bool(C >= 0)
        t_fit = time.perf_counter() - t_fit0
        spath = f"state_realtalk_{ci:02d}.npz"
        np.savez(spath, packed=packed, std=std)
        import os as _os
        state_bytes = int(_os.path.getsize(spath))
        state_sha = sha256_file(spath)
        archive_id = str(o.get("conv_id", f"RT{ci+1:02d}"))
        keep = []
        for qi, qid in enumerate(o["qids"]):
            gold = [int(x) for x in o["gold_rows"][qi]]
            if not gold:
                assert qid in excluded, qid
                continue
            assert qid not in excluded
            keep.append((qi, qid, gold))
        ckpt = f"ckpt_top10_realtalk_{ci:02d}.jsonl"
        rows = []
        t_score = t_rank = 0.0
        for (qi, qid, gold) in keep:
            q = QC[qi]
            if float(np.linalg.norm(q)) == 0:
                zero_vec_report["rt_zero_queries"] += 1
            g = np.asarray(gold).astype(int)
            assert np.all((g >= 0) & (g < N)), qid
            t_s0 = time.perf_counter()
            sc = score_one_query(C, packed, std, q, g)
            fr3_s = expected_recall_at_k(sc["s_sign"], g, k=K3)
            fr3_f = expected_recall_at_k(sc["s_raw"], g, k=K3)
            t_score += time.perf_counter() - t_s0
            nat = rt_native.get(qid)
            assert nat is not None, qid
            assert nat[2]["chat"] == o["chat_no"] and nat[2]["file"] == o["file"], qid
            assert nat[2]["N"] == N, qid
            assert nat[2]["gold_count"] == len(g), qid
            ds = abs(fr3_s - nat[0])
            df = abs(fr3_f - nat[1])
            gr = gate_rows["realtalk"]
            gr["n"] += 1
            gr["maxd_s"] = max(gr["maxd_s"], ds)
            gr["maxd_f"] = max(gr["maxd_f"], df)
            if ds > TOL or df > TOL:
                gr["viol"].append({"qid": qid, "ds": ds, "df": df})
            t_r0 = time.perf_counter()
            r_sign = top10_record(sc["s_sign"], archive_id, g, k=K10)
            r_raw = top10_record(sc["s_raw"], archive_id, g, k=K10)
            r_std = top10_record(sc["s_std"], archive_id, g, k=K10)
            r_asym = top10_record(sc["s_asym"], archive_id, g, k=K10)
            t_rank += time.perf_counter() - t_r0
            # attach doc-ID labels for RT (row->id) without changing IDs (rows)
            for r in (r_sign, r_raw, r_std, r_asym):
                r["doc_ids"] = [row_to_id[int(x)] for x in r["ids"]]
            n_valid += 1
            rows.append({"benchmark": "REALTALK", "qid": qid, "archive_id": archive_id,
                         "chat": o["chat_no"], "file": o["file"], "N": N,
                         "gold": [int(x) for x in g.tolist()], "gold_size": int(len(g)),
                         "gold_doc_ids": [row_to_id[int(x)] for x in g.tolist()],
                         "cache_file": fp, "cache_sha256": hashes_before[fp],
                         "state_file": spath, "state_sha256": state_sha,
                         "state_bytes": state_bytes, "packed_bytes": int(N * 12),
                         "float_bytes_mem": int(N * 96 * 8), "shared_std_bytes": 768,
                         "fr3_sign": float(fr3_s), "fr3_float": float(fr3_f),
                         "ctrl_sign": float(nat[0]), "ctrl_float": float(nat[1]),
                         "sign96": r_sign, "float_raw": r_raw, "float_std": r_std,
                         "asym": r_asym})
        with open(ckpt, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        all_rows.extend(rows)
        dt = time.perf_counter() - t_a0
        timing["archives"].append({"bench": "REALTALK", "archive": archive_id, "nq": len(rows),
                                   "fit_s": t_fit, "score_s": t_score, "rank_s": t_rank,
                                   "total_s": dt})
        timing["t_fit_total"] += t_fit
        timing["t_score_total"] += t_score
        timing["t_rank_total"] += t_rank
        print(f"REALTALK {archive_id} nq={len(rows)} rss={peak_rss_mb():.0f}MB", flush=True)
        del C, QC, packed, std
    # ---- write merged + gates + summary ----
    all_rows_sorted = sorted(all_rows, key=lambda r: (r["benchmark"], r["qid"]))
    with open("per_query_top10.jsonl", "w", encoding="utf-8") as f:
        for r in all_rows_sorted:
            f.write(json.dumps(r) + "\n")
    gates = {}
    for bench in ("perltqa", "lme", "realtalk"):
        gr = gate_rows[bench]
        ok = len(gr["viol"]) == 0
        if bench == "perltqa":
            ok = ok and gr["n"] == 8265
        elif bench == "lme":
            ok = ok and gr["n"] == 470
        else:
            ok = ok and gr["n"] == 705 and n_valid == 705
        gates[bench] = {"result": "PASS" if ok else "FAIL", "n": gr["n"],
                        "maxd_s": gr["maxd_s"], "maxd_f": gr["maxd_f"],
                        "n_viol": len(gr["viol"]), "viol": gr["viol"][:5],
                        "tolerance": TOL}
    hashes_after = {}
    for p in [PERLTQA_ARCH, PERLTQA_Q, PERLTQA_CTRL, LME_CTRL, RT_CTRL, RT_EXCL]:
        hashes_after[p] = sha256_file(p)
    for f in sorted(glob.glob(LME_GLOB)):
        hashes_after[f] = sha256_file(f)
    for f in sorted(glob.glob(RT_GLOB)):
        hashes_after[f] = sha256_file(f)
    caches_unchanged = (hashes_before == hashes_after)
    for bench in gates:
        gates[bench]["caches_unchanged"] = caches_unchanged
    json.dump({"labels": LABELS, "gates": gates,
               "hashes_before": hashes_before, "hashes_after": hashes_after,
               "caches_unchanged": caches_unchanged,
               "perltqa_t1": perltqa_t1, "lme_t1": lme_t1, "rt_t1": rt_t1,
               "n_valid_realtalk": n_valid,
               "zero_vectors": zero_vec_report,
               "zero_handling": "nonfinite cosine -> -inf (worst); sign(0)>=0 True; Hamming/asym total",
               "tie_rule": "SHA256('top10-r1|'+archive_id+'|'+str(row_index)) ascending, then row_index",
               "truncation": "none: cached FLOAT96 vectors used directly, no text/model inference"},
              open("gates_top10.json", "w"), indent=2)
    total_wall = time.time() - wall0
    total_cpu = time.perf_counter() - t_all0
    # means per benchmark per arm
    summary = {"labels": LABELS, "n_rows": len(all_rows_sorted),
               "n_perltqa": sum(1 for r in all_rows_sorted if r["benchmark"] == "PerLTQA"),
               "n_lme": sum(1 for r in all_rows_sorted if r["benchmark"] == "LME"),
               "n_realtak": sum(1 for r in all_rows_sorted if r["benchmark"] == "REALTALK"),
               "gates": gates, "timing": {**timing, "wall_s": total_wall, "cpu_s": total_cpu,
                                           "peak_rss_mb": peak_rss_mb()},
               "zero_vectors": zero_vec_report}
    for bench in ("PerLTQA", "LME", "REALTALK"):
        br = [r for r in all_rows_sorted if r["benchmark"] == bench]
        d = {}
        for arm in ("sign96", "float_raw", "float_std", "asym"):
            H = np.array([r[arm]["hit10"] for r in br])
            Rc = np.array([r[arm]["recall10"] for r in br])
            Nd = np.array([r[arm]["ndcg10"] for r in br])
            Eh = np.array([r[arm]["exp_hit10"] for r in br])
            d[arm] = {"hit10_mean": float(H.mean()), "recall10_mean": float(Rc.mean()),
                      "ndcg10_mean": float(Nd.mean()), "exp_hit10_mean": float(Eh.mean()),
                      "n": int(len(br))}
        summary[bench] = d
    json.dump(summary, open("summary_top10.json", "w"), indent=2)
    print(f"DONE n={len(all_rows_sorted)} gates={ {k: v['result'] for k, v in gates.items()} } wall={total_wall:.1f}s rss={peak_rss_mb():.0f}MB", flush=True)
    return gates, summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--gate-only", action="store_true")
    a = ap.parse_args()
    run_all()

