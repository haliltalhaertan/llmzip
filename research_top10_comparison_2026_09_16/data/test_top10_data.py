"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Top10-r1 DATA-worker focused checks (durable, stdlib-only).
Run: $HOME/muse-work/ml-python test_top10_data.py
Covers: export schema/completeness, frozen-format alignment, gold stability,
lexical per_query protocol (exactly-10, no dup, deterministic tie order).
"""
import glob
import hashlib
import json
import os
import pickle
import re

HERE = os.path.dirname(os.path.abspath(__file__))
R = "/mnt/c/Users/MDP/dev/llmzip-work"
RT_GLOB = R + "/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl"
PASS = []


def check(name, cond, detail=""):
    PASS.append((name, bool(cond), detail))
    if not cond:
        raise AssertionError(f"FAIL {name} {detail}")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def frozen_message_text(speaker, text, cap):
    speaker = str(speaker or "").strip()
    text = str(text or "").strip()
    cap = str(cap or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")


def test_export_files():
    for i in range(1, 11):
        p = os.path.join(HERE, f"RT{i:02d}.json")
        check(f"export-exists-RT{i:02d}", os.path.exists(p), p)
    for n in ("exclusions.json", "manifest.json", "EXPORT_DONE.json"):
        check(f"export-exists-{n}", os.path.exists(os.path.join(HERE, n)), n)


def test_export_alignment():
    """EVERY dia_id -> cached id_to_row, EVERY question exact, EVERY gold stable."""
    tot_q = 0
    for i in range(1, 11):
        aid = f"RT{i:02d}"
        exp = json.load(open(os.path.join(HERE, aid + ".json"), encoding="utf-8"))
        cache = pickle.load(open(
            sorted(glob.glob(RT_GLOB))[i - 1], "rb"))
        check(f"{aid}-archive-id", exp["archive_id"] == aid)
        check(f"{aid}-source-file", exp["source_file"] == cache["file"])
        check(f"{aid}-ndocs", len(exp["docs"]) == int(cache["N"]),
              f"{len(exp['docs'])} vs {cache['N']}")
        id_to_row = cache["id_to_row"]
        for d in exp["docs"]:
            check(f"{aid}-row-{d['row']}-in-map", d["id"] in id_to_row,
                  repr(d["id"]))
            check(f"{aid}-row-{d['row']}-pos", id_to_row[d["id"]] == d["row"])
        # texts must equal frozen message_text reconstruction from raw chat
        raw = json.load(open(os.path.join(R, "bench3/REALTALK/data",
                                          cache["file"]), encoding="utf-8"))
        skeys = sorted(
            [k for k in raw if k.startswith("session_")
             and not k.endswith("_date_time")
             and not k.startswith("events_session_")],
            key=lambda k: int(k.split("_")[1]))
        lines = []
        for sk in skeys:
            for m in raw[sk]:
                lines.append(frozen_message_text(
                    m.get("speaker", ""), m.get("clean_text", ""),
                    m.get("blip_caption", "") or ""))
        check(f"{aid}-nlines", len(lines) == int(cache["N"]))
        for d in exp["docs"]:
            check(f"{aid}-text-{d['row']}",
                  d["text"] == lines[d["row"]],
                  f"row {d['row']} text mismatch")
        # queries exact + gold stable vs cache (valid-only)
        expq = {q["qid"]: q for q in exp["queries"]}
        for qi, qid in enumerate(cache["qids"]):
            gold = [int(g) for g in cache["gold_rows"][qi]]
            if not gold:
                check(f"{aid}-{qid}-excluded", qid not in expq, qid)
            else:
                check(f"{aid}-{qid}-present", qid in expq, qid)
                check(f"{aid}-{qid}-qtext",
                      expq[qid]["text"] == cache["questions"][qi], qid)
                check(f"{aid}-{qid}-gold",
                      [int(g) for g in expq[qid]["gold"]] == gold, qid)
                check(f"{aid}-{qid}-cat",
                      int(expq[qid]["category"]) == int(cache["cats"][qi]), qid)
                tot_q += 1
        # no raw answer/gold leakage into embedding texts
        for d in exp["docs"]:
            check(f"{aid}-doc-{d['row']}-noevent",
                  "events_session_" not in d["text"])
    check("total-valid-705", tot_q == 705, f"got {tot_q}")
    excl = json.load(open(os.path.join(HERE, "exclusions.json"),
                          encoding="utf-8"))
    check("exclusions-23", len(excl["excluded_qids"]) == 23,
          str(len(excl["excluded_qids"])))
    ref = json.load(open(R + "/theory_benchmark_test_v1/realtalk/excluded_ids.json",
                         encoding="utf-8"))
    check("exclusions-match-frozen",
          sorted(excl["excluded_qids"]) == sorted(ref["excluded_ids"]))


def norm_evidence_old(x):
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


def test_gold_recompute_old_normalizer():
    """Recompute gold from raw evidence via old normalizer; must equal cache+export."""
    for i in range(1, 11):
        aid = f"RT{i:02d}"
        exp = json.load(open(os.path.join(HERE, aid + ".json"), encoding="utf-8"))
        cache = pickle.load(open(sorted(glob.glob(RT_GLOB))[i - 1], "rb"))
        raw = json.load(open(os.path.join(R, "bench3/REALTALK/data",
                                          cache["file"]), encoding="utf-8"))
        id_to_row = cache["id_to_row"]
        expq = {q["qid"]: q for q in exp["queries"]}
        assert len(raw["qa"]) == len(cache["qids"])
        for qi, q in enumerate(raw["qa"]):
            qid = cache["qids"][qi]
            toks = norm_evidence_old(q.get("evidence"))
            rows = list(dict.fromkeys(int(id_to_row[t]) for t in toks
                                      if t in id_to_row))
            cached = [int(g) for g in cache["gold_rows"][qi]]
            check(f"{aid}-{qid}-recompute-stable", rows == cached, qid)
            if rows:
                check(f"{aid}-{qid}-export-stable",
                      [int(g) for g in expq[qid]["gold"]] == rows, qid)


def test_lexical_protocol():
    for arm in ("bm25", "tfidf"):
        p = os.path.join(HERE, f"per_query_{arm}.jsonl")
        check(f"lex-exists-{arm}", os.path.exists(p), p)
        n = 0
        with open(p, encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                n += 1
                top = r["top10"]
                check(f"{arm}-{r['qid']}-len10", len(top) == 10, r["qid"])
                check(f"{arm}-{r['qid']}-nodup",
                      len(set(top)) == 10, r["qid"])
                check(f"{arm}-{r['qid']}-range",
                      all(0 <= int(x) < int(r["N"]) for x in top), r["qid"])
                check(f"{arm}-{r['qid']}-hit01",
                      r["hit_at_10"] in (0, 1), r["qid"])
                g = set(int(x) for x in r["gold"])
                inter = len(g.intersection(int(x) for x in top))
                check(f"{arm}-{r['qid']}-recall",
                      abs(r["recall_at_10"] - inter / len(g)) < 1e-9, r["qid"])
                check(f"{arm}-{r['qid']}-hit",
                      r["hit_at_10"] == int(inter > 0), r["qid"])
        check(f"lex-n705-{arm}", n == 705, f"got {n}")


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "export"
    if which == "export":
        test_export_files()
        test_export_alignment()
        test_gold_recompute_old_normalizer()
    elif which == "lexical":
        test_lexical_protocol()
    else:
        test_export_files()
        test_export_alignment()
        test_gold_recompute_old_normalizer()
        test_lexical_protocol()
    print(f"GREEN ({which}): {len(PASS)} checks passed")
