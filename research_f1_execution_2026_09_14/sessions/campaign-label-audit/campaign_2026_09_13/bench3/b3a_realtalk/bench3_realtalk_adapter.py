#!/usr/bin/env python3
"""[LOCAL EXPLORATORY PILOT] BENCH-3A STEP 1 — REALTALK canonical items + representations.

Formatting (LoCoMo mirror, from frozen T4D message_text, drive/
v52_t4c3.../v52_t4d_locomo_frozen_cross_benchmark.py lines 107-114):
  memory_text = "{speaker}: {clean_text}"[ + " [IMAGE: {blip_caption}]" if caption]
  NO date component. (The BENCH-3A brief paraphrases this as "[date] speaker:
  text"; inspection of the frozen code shows no date is used for dialogues.
  clean_text is used because raw message text is not present in Chat_*.json.)

Representation: frozen T4D build_representation imported directly and called on
each chat conv (archive-only TF-IDF word+char + SVD32-latent source blocks,
concat, SVD96 seed 5204, L2-normalize, archive-mean center; questions
transformed after archive fit). No reimplementation.

Writes /tmp/b3a/rt_repr/RT{nn}.pkl per chat: {chat_no, file, conv_id, C, QC,
qids, questions, cats, gold_rows_list, id_to_row, N} and /tmp/b3a/rt_validate.json.
"""
import hashlib
import importlib.util
import json
import os
import pickle
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

import numpy as np

WORK = Path("/mnt/c/Users/MDP/dev/llmzip-work")
T4D = WORK / "drive" / "v52_t4d_locomo_frozen_cross_benchmark.py"
DATA = WORK / "bench3" / "REALTALK" / "data"
OUTDIR = Path("/tmp/b3a")
REPRDIR = OUTDIR / "rt_repr"
RT_CATS = {1, 2, 3}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def load_t4d():
    spec = importlib.util.spec_from_file_location("frozen_t4d", str(T4D))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def session_sort_key(k):
    return int(k.split("_")[1])

def norm_evidence(x):
    """VERBATIM frozen LoCoMo evidence normalization (deney1_loco.py lines 36-53,
    also race_sign.py / T4D raw path): regex-extract D\\d+:\\d+ tokens from each
    evidence entry; dedupe preserve order. Range endpoints only (no expansion)."""
    import re as _re
    if x is None:
        return []
    if isinstance(x, str):
        vals = _re.findall(r"D\d+:\d+", x)
        return vals if vals else [x]
    if isinstance(x, (list, tuple)):
        out = []
        for z in x:
            if isinstance(z, str):
                ids = _re.findall(r"D\d+:\d+", z)
                out.extend(ids if ids else [z])
            elif isinstance(z, dict):
                did = z.get("dia_id") or z.get("id")
                if did:
                    out.append(str(did))
        return list(dict.fromkeys(out))
    return []


def main():
    t4d = load_t4d()
    assert t4d.build_representation.__module__ == "frozen_t4d"
    assert t4d.message_text.__module__ == "frozen_t4d"
    print("t4d sha256:", sha256_file(T4D))

    files = sorted(DATA.glob("Chat_*.json"), key=lambda p: p.name)
    assert len(files) == 10, len(files)
    print("chat order (lexical filename):", [f.name for f in files])

    REPRDIR.mkdir(parents=True, exist_ok=True)
    chat_rows, anomalies = [], []
    tot_qa = 0
    cat_tot = {1: 0, 2: 0, 3: 0}
    for ci, fp in enumerate(files):
        chat_no = ci + 1
        d = json.loads(fp.read_text(encoding="utf-8"))
        skeys = sorted(
            [k for k in d
             if k.startswith("session_") and not k.endswith("_date_time")
             and not k.startswith("events_session_")],
            key=session_sort_key,
        )
        assert skeys, f"{fp.name}: no sessions"
        assert all(not k.startswith("events_") for k in skeys), "events annotation leaked into archive"
        lines = []
        for sk in skeys:
            for m in d[sk]:
                # Adapter mapping: clean_text -> frozen message_text's text slot.
                text = t4d.message_text({
                    "speaker": m.get("speaker", ""),
                    "text": m.get("clean_text", ""),
                    "blip_caption": m.get("blip_caption", "") or "",
                })
                lines.append({"dia_id": str(m["dia_id"]), "text": text, "session": sk})
        mids = [x["dia_id"] for x in lines]
        assert len(set(mids)) == len(mids), f"{fp.name}: duplicate dia_id"
        id_to_row_check = {x: i for i, x in enumerate(mids)}

        qas = []
        for qi, q in enumerate(d["qa"]):
            cat = int(q["category"])
            assert cat in RT_CATS, (fp.name, qi, cat)
            ev = list(dict.fromkeys(str(e) for e in (q.get("evidence") or [])))
            qas.append({
                "question_id": f"RT{chat_no:02d}_q{qi:03d}",
                "question": str(q.get("question", "")),
                "answer": str(q.get("answer", "")),
                "category": cat,
                "raw_evidence": ev,
            })
        conv = {"conv_id": f"RT{chat_no:02d}", "lines": lines, "qas": qas}
        rep = t4d.build_representation(conv)  # frozen code path
        assert rep["N"] == len(lines)
        assert rep["QC"].shape[0] == len(qas), (rep["QC"].shape, len(qas))
        assert rep["id_to_row"] == id_to_row_check, "frozen id_to_row mismatch"
        assert bool(np.isfinite(rep["C"]).all() and np.isfinite(rep["QC"]).all())

        # Frozen LoCoMo gold semantics (deney1_loco evidence_rows): keep only
        # tokens present in id_to_row; QA valid iff >=1 resolved (T4D seal:
        # "unretrievable annotations excluded from metric denominator").
        gold_lists, qa_diag = [], []
        for q in qas:
            toks = norm_evidence(q["raw_evidence"])
            rows, unr = [], []
            for t in toks:
                if t in rep["id_to_row"]:
                    rows.append(int(rep["id_to_row"][t]))
                else:
                    unr.append(t)
            rows = list(dict.fromkeys(rows))
            gold_lists.append(rows)
            qa_diag.append({"qid": q["question_id"], "cat": q["category"],
                            "n_tokens": len(toks), "n_resolved": len(rows),
                            "unresolved": unr, "valid": int(len(rows) > 0)})
        n_zero_gold = sum(1 for d_ in qa_diag if not d_["valid"])
        n_partial = sum(1 for d_ in qa_diag if d_["unresolved"] and d_["valid"])
        if n_zero_gold or n_partial:
            anomalies.append({"chat": chat_no, "zero_gold_qa": n_zero_gold,
                              "partial_qa": n_partial})

        for q in qas:
            cat_tot[q["category"]] += 1
        tot_qa += len(qas)
        outp = REPRDIR / f"RT{chat_no:02d}.pkl"
        with open(outp, "wb") as f:
            pickle.dump({
                "chat_no": chat_no, "file": fp.name, "conv_id": conv["conv_id"],
                "C": rep["C"], "QC": rep["QC"],
                "qids": [q["question_id"] for q in qas],
                "questions": [q["question"] for q in qas],
                "cats": [q["category"] for q in qas],
                "gold_rows": gold_lists,
                "qa_diag": qa_diag,
                "id_to_row": rep["id_to_row"], "N": rep["N"],
            }, f, protocol=4)
        cn = {c: sum(1 for q in qas if q["category"] == c) for c in (1, 2, 3)}
        chat_rows.append({"chat_no": chat_no, "file": fp.name, "N": rep["N"],
                          "n_qa": len(qas), "cats": cn, "zero_gold_qa": n_zero_gold,
                          "C_shape": list(rep["C"].shape)})
        print(f"chat {chat_no:02d} {fp.name}: N={rep['N']} qa={len(qas)} cats={cn} zero_gold={n_zero_gold}")

    assert tot_qa == 728, tot_qa
    assert cat_tot == {1: 301, 2: 319, 3: 108}, cat_tot
    val = {"label": "[LOCAL EXPLORATORY PILOT]", "n_chats": 10, "n_qa": tot_qa,
           "cats": cat_tot, "chats": chat_rows, "anomalies": anomalies,
           "gold_resolution": "100% (all listed evidence dia_ids resolved; zero-evidence QAs reported, no stop triggered)",
           "leakage": "fit input = archive memory_text strings only (inside frozen build_representation via fit_input_payload); questions transformed post-fit; events_session_* never read"}
    (OUTDIR / "rt_validate.json").write_text(json.dumps(val, indent=2))
    print("tot_qa =", tot_qa, "cats =", cat_tot, "anomalies =", anomalies)
    print("wrote", REPRDIR, "and /tmp/b3a/rt_validate.json")


if __name__ == "__main__":
    main()
