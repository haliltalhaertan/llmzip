"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Audit driver part 1: full 705 lexical reimplementation + corrected expectedHit.
See audit_lexical_lib.py for independent formulas.
"""
import glob
import hashlib
import json
import math
import os
import pickle
import time

from audit_lexical_lib import (bm25_scores, correct_expected_hit, ndcg_at_10,
                               rank_top10, sha256_file, tie_info, tok)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"


def main():
    t0 = time.time()
    # --- record source hashes BEFORE (and verify no writes to DATA) ---
    before = {}
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))) + \
            sorted(glob.glob(os.path.join(DATA, "*.jsonl"))) + \
            [os.path.join(DATA, "run_lexical.py"), os.path.join(DATA, "export_realtalk.py")]:
        if os.path.exists(p):
            before[p] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    with open(os.path.join(HERE, "source_hashes_before.json"), "w") as f:
        json.dump(before, f, indent=2, sort_keys=True)

    # --- load producer rows ---
    prod = {}
    for arm in ("bm25", "tfidf"):
        prod[arm] = {}
        with open(os.path.join(DATA, f"per_query_{arm}.jsonl"), encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                prod[arm][r["qid"]] = r
    assert len(prod["bm25"]) == 705 and len(prod["tfidf"]) == 705

    # --- source/export alignment + unresolved (direct qa_diag) ---
    cache_files = sorted(glob.glob(RT_GLOB))
    assert len(cache_files) == 10
    n_valid = 0
    n_partial_valid = 0
    partial_list = []
    excl_check = []
    align_errors = 0
    for ci, cf in enumerate(cache_files):
        aid = f"RT{ci+1:02d}"
        exp = json.load(open(os.path.join(DATA, aid + ".json"), encoding="utf-8"))
        cache = pickle.load(open(cf, "rb"))
        assert exp["archive_id"] == aid
        assert exp["source_file"] == cache["file"]
        # docs: cached id_to_row order + frozen text from raw
        raw = json.load(open(os.path.join(R, "bench3/REALTALK/data", cache["file"]), encoding="utf-8"))

        def frozen(speaker, text, cap):
            speaker = str(speaker or "").strip()
            text = str(text or "").strip()
            cap = str(cap or "").strip()
            if cap:
                text = f"{text} [IMAGE: {cap}]".strip()
            return f"{speaker}: {text}".strip(": ")
        skeys = sorted([k for k in raw if k.startswith("session_")
                        and not k.endswith("_date_time")
                        and not k.startswith("events_session_")],
                       key=lambda k: int(k.split("_")[1]))
        lines = []
        for sk in skeys:
            for m in raw[sk]:
                lines.append(frozen(m.get("speaker", ""), m.get("clean_text", ""),
                                    m.get("blip_caption", "") or ""))
        for d in exp["docs"]:
            if d["text"] != lines[d["row"]]:
                align_errors += 1
        expq = {q["qid"]: q for q in exp["queries"]}
        for qi, qid in enumerate(cache["qids"]):
            gold = [int(g) for g in cache["gold_rows"][qi]]
            dg = cache["qa_diag"][qi]
            assert dg["qid"] == qid
            if dg["valid"]:
                n_valid += 1
                if dg.get("unresolved"):
                    n_partial_valid += 1
                    partial_list.append({"qid": qid, "archive_id": aid,
                                         "unresolved": dg["unresolved"],
                                         "n_tokens": dg["n_tokens"],
                                         "n_resolved": dg["n_resolved"],
                                         "gold": gold})
                if qid not in expq:
                    align_errors += 1
                else:
                    if expq[qid]["text"] != cache["questions"][qi]:
                        align_errors += 1
                    if [int(g) for g in expq[qid]["gold"]] != gold:
                        align_errors += 1
            else:
                excl_check.append(qid)
                if qid in expq:
                    align_errors += 1
    assert n_valid == 705, n_valid
    assert len(excl_check) == 23, len(excl_check)
    ref = json.load(open(R + "/theory_benchmark_test_v1/realtalk/excluded_ids.json", encoding="utf-8"))
    assert sorted(excl_check) == sorted(ref["excluded_ids"])
    excl_export = json.load(open(os.path.join(DATA, "exclusions.json"), encoding="utf-8"))
    assert sorted(excl_export["excluded_qids"]) == sorted(ref["excluded_ids"])

    # --- full reimplementation + exact top10/metrics check + corrected file ---
    out_comb = open(os.path.join(HERE, "per_query_corrected.jsonl"), "w", encoding="utf-8")
    outs = {a: open(os.path.join(HERE, f"per_query_{a}_corrected.jsonl"), "w", encoding="utf-8")
            for a in ("bm25", "tfidf")}
    summary = {}
    for arm, scorer in (("bm25", "bm25"), ("tfidf", "tfidf")):
        n = 0
        top_mismatch = 0
        actual_mismatch = 0
        prod_exp_frac_count = 0
        tie_at_cut = 0
        h_sum = r_sum = nd_sum = eh_sum = 0.0
        eh_prod_sum = 0.0
        t_arm = time.time()
        for ci in range(1, 11):
            aid = f"RT{ci:02d}"
            exp = json.load(open(os.path.join(DATA, aid + ".json"), encoding="utf-8"))
            docs = [d["text"] for d in exp["docs"]]
            N = len(docs)
            docs_tok = [tok(d) for d in docs]
            avglen = sum(len(d) for d in docs_tok) / N
            for q in exp["queries"]:
                qt = tok(q["text"])
                if arm == "bm25":
                    scores = bm25_scores(docs_tok, qt, avglen)
                else:
                    from audit_lexical_lib import tfidf_scores
                    scores = tfidf_scores(docs_tok, qt)
                assert len(scores) == N and all(math.isfinite(s) for s in scores)
                top = rank_top10(scores, aid)
                g = [int(x) for x in q["gold"]]
                inter = len(set(g).intersection(top))
                hit = int(inter > 0)
                rec = inter / len(g)
                ndcg = ndcg_at_10(top, g)
                eh = correct_expected_hit(scores, g, k=10)
                ti = tie_info(scores, g, k=10)
                if ti["is_tie_at_cut"]:
                    tie_at_cut += 1
                # compare to producer
                pr = prod[arm][q["qid"]]
                if [int(x) for x in pr["top10"]] != [int(x) for x in top]:
                    top_mismatch += 1
                if pr["hit_at_10"] != hit or abs(pr["recall_at_10"] - rec) > 1e-9 or \
                        abs(pr["ndcg_at_10"] - ndcg) > 1e-9:
                    actual_mismatch += 1
                # producer expected_hit equals fractional recall? (bug signature)
                if abs(pr["expected_hit_at_10"] - rec) > 1e-12:
                    prod_exp_frac_count += 1  # counts deviations (expect ~0 per REPORT)
                eh_prod_sum += float(pr["expected_hit_at_10"])
                h_sum += hit
                r_sum += rec
                nd_sum += ndcg
                eh_sum += eh
                row = {"arm": arm, "archive_id": aid, "source_file": exp["source_file"],
                       "qid": q["qid"], "category": q["category"], "N": N, "gold": g,
                       "gold_size": len(g), "top10": [int(x) for x in top],
                       "top10_scores": [float(scores[x]) for x in top],
                       "hit_at_10": hit, "recall_at_10": rec, "ndcg_at_10": ndcg,
                       "expected_hit_at_10_corrected": eh,
                       "expected_hit_at_10_producer": float(pr["expected_hit_at_10"]),
                       "tie": ti}
                outs[arm].write(json.dumps(row) + "\n")
                out_comb.write(json.dumps(row) + "\n")
                n += 1
        outs[arm].close()
        summary[arm] = {"n": n, "top_mismatch": top_mismatch,
                        "actual_mismatch": actual_mismatch,
                        "producer_exp_equals_recall_deviations": prod_exp_frac_count,
                        "tie_at_cut": tie_at_cut,
                        "hit_at_10": h_sum / n, "recall_at_10": r_sum / n,
                        "ndcg_at_10": nd_sum / n,
                        "expected_hit_corrected": eh_sum / n,
                        "expected_hit_producer_mean": eh_prod_sum / n,
                        "elapsed_s": time.time() - t_arm}
        assert n == 705, (arm, n)
    out_comb.close()

    after = {}
    for p in sorted(glob.glob(os.path.join(DATA, "*.json"))) + \
            sorted(glob.glob(os.path.join(DATA, "*.jsonl"))) + \
            [os.path.join(DATA, "run_lexical.py"), os.path.join(DATA, "export_realtalk.py")]:
        if os.path.exists(p):
            after[p] = {"sha256": sha256_file(p), "bytes": os.path.getsize(p)}
    with open(os.path.join(HERE, "source_hashes_after.json"), "w") as f:
        json.dump(after, f, indent=2, sort_keys=True)
    hashes_unchanged = (before == after)

    audit = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                        "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
             "elapsed_s": time.time() - t0,
             "alignment_errors": align_errors,
             "n_valid": n_valid, "n_excluded": len(excl_check),
             "n_partial_valid_with_unresolved": n_partial_valid,
             "partial_examples": partial_list[:10],
             "partial_qids": sorted(p["qid"] for p in partial_list),
             "hashes_unchanged": hashes_unchanged,
             "arms": summary}
    with open(os.path.join(HERE, "lexical_audit.json"), "w") as f:
        json.dump(audit, f, indent=2)
    print(json.dumps(audit, indent=2))
    assert align_errors == 0
    assert hashes_unchanged
    for arm in summary:
        assert summary[arm]["top_mismatch"] == 0, summary[arm]
        assert summary[arm]["actual_mismatch"] == 0, summary[arm]
    print(f"AUDIT LEXICAL PASS: top10+actual exact, corrected expHit saved, "
          f"partial-unresolved={n_partial_valid}, ties BM25={summary['bm25']['tie_at_cut']} "
          f"TFIDF={summary['tfidf']['tie_at_cut']}")


if __name__ == "__main__":
    main()
