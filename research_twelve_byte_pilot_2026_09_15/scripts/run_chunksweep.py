#!/usr/bin/env python3
"""What is the optimal retrieval unit? Narrow (sentence) .. wide (session).

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

The production unit is one conversation TURN (`[date] role: content`), and the
gold label lives on the turn (`has_answer`).  This sweep keeps the gold and the
corpus identical and changes ONLY what counts as one indexed unit:

    sentence  one sentence of a turn
    sent2     two consecutive sentences, stride 1 (overlapping)
    turn      production baseline
    turn2     a turn plus the previous turn of the same session
    session   every turn of one session, concatenated

Comparing "top-10 units" across these is meaningless -- ten sentences and ten
sessions are not the same amount of text.  So the x-axis is the honest shared
resource: CHARACTERS OF ORIGINAL CONVERSATION TEXT the reader must be shown.
Every unit carries the exact (turn, start, end) spans it covers; walking the
ranked list we accumulate the UNION of those spans, so overlapping units are
never double-charged and fine chunking is never charged for context it did
not ask for.

Coverage is reported two ways, because sentence-level gold labels do not exist:
    cov_any   a retrieved span touches a gold turn          (generous to fine)
    cov_full  retrieved spans cover the gold turn entirely  (generous to wide)
The truth is between them; both are reported so neither can be cherry-picked.

Storage is reported as units x 12 bytes -- TOTAL, never bytes-per-vector,
which is the quantity that silently improves when the unit count is inflated.

Usage: python run_chunksweep.py [n_items] [seed] [shard] [n_shards]
"""
import glob
import json
import os
import random
import re
import sys
import time

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
import run_bottleneck as BN  # noqa: E402

ITEMS = BN.ITEMS
SVD_RANDOM_STATE = 5101
DIM = 96
MIN_UNITS = 25                      # adapter's own floor
CHUNKINGS = ["sentence", "sent2", "turn", "turn2", "session"]
ARMS = ["sign", "float"]            # 12-byte production arm, and its ceiling
# character budgets at which coverage is read off
BUDGETS = [250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 64000]
SENT_RE = re.compile(r"[^.!?\n]*[.!?\n]+|[^.!?\n]+$")


def sentence_spans(text):
    """Contiguous [(start, end)] PARTITION of `text` at sentence boundaries.

    A partition, not just the matched pieces: whitespace-only gaps are folded
    into the following sentence so the spans always cover [0, len(text)).
    Otherwise `cov_full` would be unreachable for fine chunking through no
    fault of the method.
    """
    if not text:
        return []
    ends = [m.end() for m in SENT_RE.finditer(text)
            if text[m.start():m.end()].strip()]
    if not ends:
        return [(0, len(text))]
    if ends[-1] < len(text):
        ends[-1] = len(text)
    spans, prev = [], 0
    for e in ends:
        spans.append((prev, e))
        prev = e
    return spans


def build_units(memories, kind):
    """-> list of {text, spans:[(turn_row, s, e)]}. Spans index turn content."""
    units = []
    if kind in ("turn", "turn2", "session"):
        by_sess = {}
        for i, m in enumerate(memories):
            by_sess.setdefault(m["session_index"], []).append(i)
        if kind == "turn":
            for i, m in enumerate(memories):
                units.append({"text": m["memory_text"],
                              "spans": [(i, 0, len(m["content"]))]})
        elif kind == "turn2":
            for rows in by_sess.values():
                for pos, i in enumerate(rows):
                    grp = ([rows[pos - 1]] if pos else []) + [i]
                    units.append({
                        "text": " ".join(memories[r]["memory_text"]
                                         for r in grp),
                        "spans": [(r, 0, len(memories[r]["content"]))
                                  for r in grp]})
        else:
            for rows in by_sess.values():
                units.append({
                    "text": " ".join(memories[r]["memory_text"] for r in rows),
                    "spans": [(r, 0, len(memories[r]["content"]))
                              for r in rows]})
        return units
    # sentence-level
    for i, m in enumerate(memories):
        head = m["memory_text"][:len(m["memory_text"]) - len(m["content"])]
        sp = sentence_spans(m["content"])
        if kind == "sentence":
            groups = [[k] for k in range(len(sp))]
        else:                                    # sent2, stride 1
            groups = ([[k, k + 1] for k in range(len(sp) - 1)]
                      or [[0]] if sp else [])
        for grp in groups:
            s = sp[grp[0]][0]
            e = sp[grp[-1]][1]
            units.append({"text": head + m["content"][s:e],
                          "spans": [(i, s, e)]})
    return units


def union_len(spans_by_turn):
    total = 0
    for iv in spans_by_turn.values():
        iv = sorted(iv)
        cs, ce = iv[0]
        for s, e in iv[1:]:
            if s > ce:
                total += ce - cs
                cs, ce = s, e
            else:
                ce = max(ce, e)
        total += ce - cs
    return total


def covered_fraction(spans_by_turn, turn_row, turn_len):
    iv = sorted(spans_by_turn.get(turn_row, []))
    if not iv or turn_len == 0:
        return 0.0
    tot = 0
    cs, ce = iv[0]
    for s, e in iv[1:]:
        if s > ce:
            tot += ce - cs
            cs, ce = s, e
        else:
            ce = max(ce, e)
    tot += ce - cs
    return min(1.0, tot / turn_len)


def score_units(adapter, units, question):
    texts = [u["text"] for u in units]
    wv, cv, base_svd, Xw, Xc, Xl = adapter.fit_archive_representation(texts)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    sv = TruncatedSVD(n_components=DIM, random_state=SVD_RANDOM_STATE)
    Y = normalize(sv.fit_transform(Z))
    Qw = normalize(wv.transform([question]))
    Qc = normalize(cv.transform([question]))
    Ql = normalize(base_svd.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    QY = normalize(sv.transform(Zq))
    mu = Y.mean(axis=0, keepdims=True)
    C = Y - mu
    q = (QY - mu).reshape(-1)
    dn = np.linalg.norm(C, axis=1)
    qn = np.linalg.norm(q)
    with np.errstate(divide="ignore", invalid="ignore"):
        flt = (C @ q) / (dn * qn)
    sgn = -np.count_nonzero((C >= 0) != (q >= 0)[None, :],
                            axis=1).astype(np.float64)
    return {"sign": sgn, "float": flt}


def walk(scores, units, gold_rows, turn_lens, budgets, rng):
    """Accumulate spans down the ranked list; read coverage at each budget."""
    order = np.lexsort((rng.random(len(scores)), -np.asarray(scores)))
    spans_by_turn = {}
    out_any = {b: 0.0 for b in budgets}
    out_full = {b: 0.0 for b in budgets}
    bi = 0
    chars = 0
    budgets = sorted(budgets)
    for idx in order:
        for (r, s, e) in units[idx]["spans"]:
            spans_by_turn.setdefault(r, []).append((s, e))
        chars = union_len(spans_by_turn)
        while bi < len(budgets) and chars > budgets[bi]:
            bi += 1
        if bi >= len(budgets):
            break
        hit_any = any(r in spans_by_turn for r in gold_rows)
        full = max((covered_fraction(spans_by_turn, r, turn_lens[r])
                    for r in gold_rows), default=0.0)
        for b in budgets[bi:]:
            out_any[b] = max(out_any[b], 1.0 if hit_any else 0.0)
            out_full[b] = max(out_full[b], 1.0 if full >= 0.999 else 0.0)
        if hit_any and full >= 0.999:
            for b in budgets[bi:]:
                out_any[b] = 1.0
                out_full[b] = 1.0
            break
    return out_any, out_full


def main():
    n_items = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260915
    shard = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    nshard = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    files = sorted(glob.glob(ITEMS))
    assert len(files) == 470, len(files)
    if n_items < len(files):
        files = sorted(random.Random(seed).sample(files, n_items))
    if nshard > 1:
        files = files[shard::nshard]
    adapter = BN.load_adapter()
    acc = {c: {a: {"any": {b: [] for b in BUDGETS},
                   "full": {b: [] for b in BUDGETS}} for a in ARMS}
           for c in CHUNKINGS}
    nunits = {c: [] for c in CHUNKINGS}
    skipped, t0 = [], time.perf_counter()
    for i, f in enumerate(files):
        try:
            item = json.loads(open(f, encoding="utf-8").read())
            memories, gold_ids, issues = adapter.build_archive(item)
            if issues:
                raise RuntimeError(f"issues {issues[:1]}")
            id_to_row = {m["memory_id"]: k for k, m in enumerate(memories)}
            gold_rows = [id_to_row[g] for g in gold_ids]
            turn_lens = [len(m["content"]) for m in memories]
            question = str(item["question"])
            rng = np.random.default_rng(seed + i)
            for c in CHUNKINGS:
                units = build_units(memories, c)
                if len(units) < MIN_UNITS:
                    skipped.append({"file": os.path.basename(f),
                                    "chunking": c, "n_units": len(units)})
                    continue
                nunits[c].append(len(units))
                sc = score_units(adapter, units, question)
                for a in ARMS:
                    oa, of = walk(sc[a], units, gold_rows, turn_lens,
                                  BUDGETS, rng)
                    for b in BUDGETS:
                        acc[c][a]["any"][b].append(oa[b])
                        acc[c][a]["full"][b].append(of[b])
        except Exception as e:  # noqa: BLE001
            skipped.append({"file": os.path.basename(f), "error": repr(e)})
        if (i + 1) % 5 == 0:
            el = time.perf_counter() - t0
            print(f"  {i + 1}/{len(files)} {el:.0f}s "
                  f"({el / (i + 1):.1f}s/item)", flush=True)
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "lme", "seed": seed, "shard": [shard, nshard],
           "chunkings": CHUNKINGS, "arms": ARMS, "budgets_chars": BUDGETS,
           "x_axis": "characters of original conversation text shown",
           "storage_note": "total bytes = n_units * 12; never per-vector",
           "n_units_mean": {c: (float(np.mean(v)) if v else None)
                            for c, v in nunits.items()},
           "total_bytes_mean": {c: (float(np.mean(v)) * 12 if v else None)
                                for c, v in nunits.items()},
           "skipped": skipped,
           "raw": {c: {a: {k: {str(b): acc[c][a][k][b] for b in BUDGETS}
                           for k in ("any", "full")} for a in ARMS}
                   for c in CHUNKINGS},
           "elapsed_seconds": time.perf_counter() - t0}
    name = ("CHUNKSWEEP.json" if nshard == 1
            else f"CHUNKSWEEP_shard{shard}of{nshard}.json")
    with open(name, "w") as fh:
        json.dump(res, fh, indent=2)
    print(f"wrote {name}", flush=True)


if __name__ == "__main__":
    main()
