#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Top10-r1 DATA worker: REALTALK canonical export aligned to existing 10 caches.
Reads caches + raw chats read-only. Writes ONLY to CWD (this data/ dir).
Usage: $HOME/muse-work/ml-python export_realtalk.py
"""
import glob
import hashlib
import json
import os
import pickle
import re
import time

R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
RAWDIR = R + "/bench3/REALTALK/data"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "tdd_export.log")


def log(msg):
    ts = time.strftime("%H:%M:%S")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg, flush=True)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def frozen_message_text(speaker, text, cap):
    """VERBATIM frozen T4D message_text (drive/v52_t4d_locomo_frozen_cross_benchmark.py
    lines 107-114): no date, clean_text slot, optional [IMAGE: cap]."""
    speaker = str(speaker if speaker is not None else "").strip()
    text = str(text if text is not None else "").strip()
    cap = str(cap if cap is not None else "" or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")


def norm_evidence_old(x):
    """VERBATIM old normalizer (bench3_realtalk_adapter.py lines 60-81)."""
    if x is None:
        return []
    if isinstance(x, str):
        vals = re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def main():
    t0 = time.time()
    if os.path.exists(LOG):
        os.remove(LOG)
    files = sorted(glob.glob(RT_GLOB))
    assert len(files) == 10, files
    log(f"caches: {len(files)}")
    manifest_src = []
    for f in files:
        manifest_src.append({"path": f, "sha256": sha256_file(f),
                             "bytes": os.path.getsize(f)})
    # raw chat files via cache['file'] binding
    total_valid = 0
    total_qa = 0
    excluded = []
    manifest_raw = []
    seen_raw = set()
    for ci, cf in enumerate(files):
        cache = pickle.load(open(cf, "rb"))
        aid = f"RT{ci + 1:02d}"
        assert cache["chat_no"] == ci + 1, (aid, cache["chat_no"])
        assert cache["conv_id"] == aid
        raw_path = os.path.join(RAWDIR, cache["file"])
        assert os.path.exists(raw_path), raw_path
        if raw_path not in seen_raw:
            seen_raw.add(raw_path)
            manifest_raw.append({"path": raw_path,
                                 "sha256": sha256_file(raw_path),
                                 "bytes": os.path.getsize(raw_path)})
        raw = json.load(open(raw_path, encoding="utf-8"))
        # no event annotations in doc source keys
        skeys = sorted(
            [k for k in raw if k.startswith("session_")
             and not k.endswith("_date_time")
             and not k.startswith("events_session_")],
            key=lambda k: int(k.split("_")[1]))
        assert skeys, f"{aid}: no sessions"
        assert all(not k.startswith("events_") for k in skeys)
        # rebuild doc lines in raw order
        dia_ids, texts = [], []
        for sk in skeys:
            for m in raw[sk]:
                texts.append(frozen_message_text(
                    m.get("speaker", ""), m.get("clean_text", ""),
                    m.get("blip_caption", "") or ""))
                dia_ids.append(str(m["dia_id"]))
        # VERIFY EVERY dia_id <-> cached id_to_row (order + bijection)
        assert len(set(dia_ids)) == len(dia_ids), f"{aid}: dup dia_id"
        expect_map = {d: i for i, d in enumerate(dia_ids)}
        assert cache["id_to_row"] == expect_map, f"{aid}: id_to_row mismatch"
        assert cache["N"] == len(dia_ids)
        # VERIFY EVERY question exact vs raw qa order
        assert len(raw["qa"]) == len(cache["qids"]), aid
        for qi, q in enumerate(raw["qa"]):
            assert str(q.get("question", "")) == cache["questions"][qi], \
                f"{aid} q{qi} question mismatch"
            assert int(q.get("category", 0)) == int(cache["cats"][qi]), \
                f"{aid} q{qi} category mismatch"
        # VERIFY EVERY cached gold stable via old-normalizer recompute
        docs = [{"row": i, "id": d, "text": t}
                for i, (d, t) in enumerate(zip(dia_ids, texts))]
        queries = []
        for qi, qid in enumerate(cache["qids"]):
            toks = norm_evidence_old(raw["qa"][qi].get("evidence"))
            rows = list(dict.fromkeys(int(expect_map[t]) for t in toks
                                      if t in expect_map))
            cached_gold = [int(g) for g in cache["gold_rows"][qi]]
            assert rows == cached_gold, \
                f"{aid} {qid}: recompute {rows} vs cache {cached_gold}"
            if not cached_gold:
                excluded.append({"qid": qid, "archive_id": aid,
                                 "source_file": cache["file"],
                                 "category": int(cache["cats"][qi]),
                                 "question": cache["questions"][qi],
                                 "reason": "empty-gold (original exclusion, "
                                           "no retrievable evidence dia_id)"})
            else:
                queries.append({"qid": qid, "text": cache["questions"][qi],
                                "gold": cached_gold,
                                "category": int(cache["cats"][qi])})
        total_valid += len(queries)
        total_qa += len(cache["qids"])
        out = {"archive_id": aid, "source_file": cache["file"],
               "docs": docs, "queries": queries}
        op = os.path.join(HERE, f"{aid}.json")
        with open(op, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False)
        log(f"{aid} {cache['file']}: N={len(docs)} valid={len(queries)} "
            f"excluded={len(cache['qids']) - len(queries)}")
    assert total_qa == 728, total_qa
    assert total_valid == 705, total_valid
    assert len(excluded) == 23, len(excluded)
    # frozen exclusion cross-check (no new exclusions)
    ref = json.load(open(R + "/theory_benchmark_test_v1/realtalk/excluded_ids.json",
                         encoding="utf-8"))
    assert sorted(e["qid"] for e in excluded) == sorted(ref["excluded_ids"]), \
        "exclusion set differs from frozen list"
    with open(os.path.join(HERE, "exclusions.json"), "w",
              encoding="utf-8") as f:
        json.dump({"n_total": total_qa, "n_valid": total_valid,
                   "n_excluded": len(excluded),
                   "excluded_qids": sorted(e["qid"] for e in excluded),
                   "excluded": excluded}, f, ensure_ascii=False, indent=2)
    log("wrote exclusions.json (23 original empty-gold, no new exclusions)")
    exports = []
    for i in range(1, 11):
        p = os.path.join(HERE, f"RT{i:02d}.json")
        exports.append({"path": p, "sha256": sha256_file(p),
                        "bytes": os.path.getsize(p)})
    for n in ("exclusions.json",):
        p = os.path.join(HERE, n)
        exports.append({"path": p, "sha256": sha256_file(p),
                        "bytes": os.path.getsize(p)})
    manifest = {
        "labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                   "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
        "n_total_qa": total_qa, "n_valid": total_valid, "n_excluded": 23,
        "format": "memory_text = '{speaker}: {clean_text}'"
                  " + ' [IMAGE: {caption}]' if caption; no date; no events",
        "gold": "cache gold_rows verified stable + recomputed via old "
                "norm_evidence; valid-only exports preserve row IDs",
        "cache_files": manifest_src, "raw_chats": manifest_raw,
        "exports": exports}
    with open(os.path.join(HERE, "manifest.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(HERE, "EXPORT_DONE.json"), "w",
              encoding="utf-8") as f:
        json.dump({"status": "EXPORT_DONE", "n_valid": total_valid,
                   "n_archives": 10, "elapsed_s": time.time() - t0,
                   "exports": [f"RT{i:02d}.json" for i in range(1, 11)]
                   + ["exclusions.json", "manifest.json"]}, f, indent=2)
    log(f"EXPORT DONE valid={total_valid}/728 elapsed={time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
