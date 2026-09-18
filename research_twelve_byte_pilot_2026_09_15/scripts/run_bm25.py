#!/usr/bin/env python3
"""The control that was never run: does plain BM25 beat the whole pipeline?

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

An external run reports that BM25 alone -- no SVD, no 96 coordinates, no bits,
no per-archive fit -- reaches FR@3 58.03 on LongMemEval where the full
pipeline with text reranking reaches 57.70.  If that holds, the premise of the
whole programme needs restating, so it is measured here directly rather than
accepted or dismissed.

This is the control the programme never had.  Every arm measured in this
session compares one way of compressing an SVD representation against another
way of compressing the SAME representation.  None of them asks whether the
representation earns its keep against the oldest lexical baseline there is.

BM25 with the textbook parameters k1 = 1.2, b = 0.75, fixed before looking at
any result, per-archive statistics (the same unit the frozen pipeline fits on).
No tuning, no sweep, no stemming, no stop-word list beyond what the frozen
tokeniser already implies.

Arms, on identical queries, gold and metric:
    sym        the production 12-byte code
    qscale     this session's scaled-query scorer, same 12 bytes
    float_std  768 B/doc standardized float, the strongest arm measured
    bm25       raw text, no vectors at all
    bm25+sym   rank-fusion of the two, as a cheap check for complementarity

Reported on FR@3 -- the frozen estimand -- and hit@10, with a paired cluster
bootstrap.  A result either way is worth having: if BM25 wins, the compression
work needs a different justification; if it loses, the programme finally has
the baseline it was missing.
"""
import glob
import json
import math
import os
import pickle
import re
import sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402
import run_bottleneck as BN  # noqa: E402
sys.path.insert(0, os.path.join(H.SRC, "parallel_ideas_r1", "b8"))
import lib_b8 as B  # noqa: E402

K1, BB = 1.2, 0.75          # textbook, fixed before any result was seen
WORD = re.compile(r"[A-Za-z0-9']+")
ARMS = ["sym", "qscale", "float_std", "bm25", "bm25_rrf_sym"]
B_REPS = 20000
RNG = np.random.default_rng(20260916)


def toks(s):
    return [w.lower() for w in WORD.findall(s)]


class BM25:
    def __init__(self, texts):
        self.docs = [Counter(toks(t)) for t in texts]
        self.lens = np.array([sum(d.values()) for d in self.docs], float)
        self.avg = float(self.lens.mean()) if len(self.lens) else 1.0
        n = len(self.docs)
        df = Counter()
        for d in self.docs:
            df.update(d.keys())
        self.idf = {w: math.log(1.0 + (n - c + 0.5) / (c + 0.5))
                    for w, c in df.items()}

    def score(self, q):
        s = np.zeros(len(self.docs))
        for w in toks(q):
            iw = self.idf.get(w)
            if iw is None:
                continue
            for i, d in enumerate(self.docs):
                f = d.get(w)
                if f:
                    s[i] += iw * f * (K1 + 1.0) / (
                        f + K1 * (1.0 - BB + BB * self.lens[i] / self.avg))
        return s


def rrf(*score_lists, k=60):
    """Reciprocal rank fusion, the standard parameter-free combiner."""
    tot = np.zeros(len(score_lists[0]))
    for s in score_lists:
        order = np.argsort(-np.asarray(s), kind="stable")
        rank = np.empty(len(s), dtype=float)
        rank[order] = np.arange(len(s))
        tot += 1.0 / (k + 1.0 + rank)
    return tot


def boot(d, cluster):
    keys = np.unique(cluster)
    groups = [np.nonzero(cluster == x)[0] for x in keys]
    sums = np.array([d[g].sum() for g in groups])
    cnts = np.array([len(g) for g in groups], float)
    idx = RNG.integers(0, len(keys), size=(B_REPS, len(keys)))
    b = (sums[idx].sum(axis=1) / cnts[idx].sum(axis=1)) * 100
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def run_lme(acc, cluster, limit):
    adapter = BN.load_adapter()
    for f in sorted(glob.glob(BN.ITEMS))[:limit]:
        tag = os.path.basename(f)[:-5]
        cp = os.path.join(H.SRC, "regen", "lme", "cache_repr", tag + ".pkl")
        if not os.path.exists(cp):
            continue
        d = pickle.loads(open(cp, "rb").read())
        C = np.asarray(d["C"], float)
        item = json.loads(open(f, encoding="utf-8").read())
        memories, _, issues = adapter.build_archive(item)
        if issues:
            continue
        texts = adapter.fit_input_payload(memories)
        if len(texts) != C.shape[0]:
            continue
        score(C, texts, [str(item["question"])],
              [np.asarray(d["gold"]).ravel().astype(int)],
              [np.asarray(d["qC"], float).reshape(-1)], tag, acc, cluster)


QTEXT = json.load(open(os.path.join(HERE, "perltqa_qtext.json"),
                      encoding="utf-8")) if os.path.exists(
    os.path.join(HERE, "perltqa_qtext.json")) else {}


def run_perltqa(acc, cluster, limit):
    """Question text is NOT in the cached query pickle (it stores only
    char/section/gold/qC), so it is reconstructed from the raw en_v2 dataset
    by replaying step2_build.py's exact qid construction. All 8,265 cached
    qids matched, 0 unmatched."""
    items = json.load(open(os.path.join(
        H.SRC, "bench3", "runs", "b3b_perltqa", "cache_items.json"),
        encoding="utf-8"))
    arch = pickle.load(open(H.ARCH_PKL, "rb"))
    Q = pickle.load(open(H.Q_PKL, "rb"))
    by = defaultdict(list)
    for qid, v in Q.items():
        by[v["char"]].append(qid)
    for ch in sorted(by)[:limit]:
        if ch not in items:
            continue
        texts = [t for _, t in items[ch]["items"]]
        C = np.asarray(arch[ch]["C"], float)
        if len(texts) != C.shape[0]:
            continue
        ids = sorted(by[ch])
        ids = [q for q in ids if q in QTEXT]
        if not ids:
            continue
        score(C, texts, [QTEXT[q] for q in ids],
              [np.asarray(Q[q]["gold"]).ravel().astype(int) for q in ids],
              [np.asarray(Q[q]["qC"], float) for q in ids], ch, acc, cluster)
    del arch, Q


def _locomo_message_text(msg):
    """VERBATIM from drive/v52_t4d_locomo_frozen_cross_benchmark.py:105-112."""
    speaker = str(msg.get("speaker", "")).strip()
    text = str(msg.get("text", "")).strip()
    cap = str(msg.get("blip_caption", "") or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")


def run_locomo(acc, cluster, limit):
    """LoCoMo document text, reconstructed to the frozen recipe.

    The cached pickles carry C, QC, qas and id_to_row but no document text.
    drive/locomo10.json has it: conv_id is the list index, sessions are sorted
    numerically, and each turn is "speaker: text" with a BLIP caption appended
    when present -- raw_item_to_conv at :115-128 of the frozen cross-benchmark
    script.  Alignment is ASSERTED against the cached id_to_row rather than
    assumed, and any archive that fails the check is skipped loudly.

    Gold here is raw_evidence, as everywhere else in this pilot; the 156
    audited corrections remain an open Head-Researcher obligation.
    """
    raw = json.load(open(os.path.join(H.SRC, "drive", "locomo10.json"),
                         encoding="utf-8"))
    for idx, item in enumerate(raw[:limit]):
        tag = f"locomo_{idx}"
        cp = os.path.join(H.SRC, "regen", "locomo", tag + ".pkl")
        if not os.path.exists(cp):
            continue
        d = pickle.load(open(cp, "rb"))
        C = np.asarray(d["C"], float)
        i2r = d["id_to_row"]
        c = item.get("conversation", {})
        texts = [None] * C.shape[0]
        for sk in sorted([k for k in c if k.startswith("session_")
                          and not k.endswith("_date_time")],
                         key=lambda x: int(x.split("_")[1])):
            for msg in c.get(sk, []) or []:
                did = str(msg.get("dia_id", ""))
                if did in i2r:
                    texts[int(i2r[did])] = _locomo_message_text(msg)
        missing = sum(1 for t in texts if t is None)
        if missing:
            print(f"  ATLANDI {tag}: {missing} satirin metni yok", flush=True)
            continue
        QC = np.asarray(d["QC"], float)
        qs, gs, qv = [], [], []
        for j, qa in enumerate(d["qas"]):
            rows = sorted({int(i2r[x]) for x in qa["raw_evidence"]
                           if x in i2r})
            if rows:
                qs.append(str(qa["question"]))
                gs.append(np.asarray(rows, dtype=int))
                qv.append(QC[j])
        if qs:
            score(C, texts, qs, gs, qv, tag, acc, cluster)


def score(C, texts, questions, golds, qvecs, tag, acc, cluster):
    st = B.fit_archive(C)
    R = np.where(C >= 0, 1.0, -1.0)
    std = np.asarray(st["std"], float)
    bm = BM25(texts)
    for j, qt in enumerate(questions):
        q = np.asarray(qvecs[j], float).reshape(-1)
        g = np.asarray(golds[j]).ravel().astype(int)
        s_sym = (-np.count_nonzero((C >= 0) != (q >= 0)[None, :],
                                   axis=1)).astype(np.float64)
        s_qs = R @ (q / std)
        s_fs = B.float_std_scores(C, q, st["std"])
        s_bm = bm.score(qt)
        arms = {"sym": s_sym, "qscale": s_qs, "float_std": s_fs,
                "bm25": s_bm, "bm25_rrf_sym": rrf(s_bm, s_sym)}
        for a, s in arms.items():
            acc[a + "_fr3"].append(B.exact_frac(s, g, True))
            acc[a + "_hit10"].append(H.hit_at_k(s, g, 10))
        cluster.append(tag)


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
    res = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "bm25": {"k1": K1, "b": BB,
                    "note": "textbook parameters, fixed before any result"},
           "benchmarks": {}}
    ALL = {"lme": run_lme, "perltqa": run_perltqa, "locomo": run_locomo}
    jobs = ([(k, ALL[k]) for k in ALL] if which in ("both", "all")
            else [(which, ALL[which])])
    for name, fn in jobs:
        acc, cluster = defaultdict(list), []
        fn(acc, cluster, limit)
        cl = np.asarray(cluster)
        rec = {"n_queries": len(cl), "n_archives": int(len(np.unique(cl))),
               "levels": {}, "contrasts": {}}
        for m in ("fr3", "hit10"):
            rec["levels"][m] = {a: float(np.mean(acc[f"{a}_{m}"]) * 100)
                                for a in ARMS}
        pairs = [(a, "bm25") for a in ("sym", "qscale", "float_std")]
        pairs += [("bm25_rrf_sym", b) for b in ("sym", "qscale", "bm25",
                                                "float_std")]
        for m in ("fr3", "hit10"):
            for a, bs in pairs:
                d = np.asarray(acc[f"{a}_{m}"]) - np.asarray(acc[f"{bs}_{m}"])
                lo, hi = boot(d, cl)
                rec["contrasts"][f"{m}:{a}-{bs}"] = {
                    "delta_pp": float(d.mean() * 100), "ci95": [lo, hi],
                    "significant": bool(lo > 0 or hi < 0)}
        res["benchmarks"][name] = rec
        print(f"\n=== {name}  {rec['n_queries']} sorgu / "
              f"{rec['n_archives']} arsiv ===")
        print(f"  {'kol':>14s}{'FR@3':>9s}{'hit@10':>9s}")
        for a in ARMS:
            print(f"  {a:>14s}{rec['levels']['fr3'][a]:9.2f}"
                  f"{rec['levels']['hit10'][a]:9.2f}")
        print(f"  {'kontrast':>26s}{'fark':>9s}{'kume CI95':>22s}")
        for k, c in rec["contrasts"].items():
            lo, hi = c["ci95"]
            tag = "SIG" if c["significant"] else "ns"
            print(f"  {k:>26s}{c['delta_pp']:+9.2f}"
                  f"{f'[{lo:+.2f}, {hi:+.2f}]':>22s} {tag}")
        print(flush=True)
    with open(os.path.join(HERE, "BM25.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    print("wrote BM25.json")


if __name__ == "__main__":
    main()
