#!/usr/bin/env python3
"""What separates gold from non-gold INSIDE the top 10? Measure before building.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

`run_where_next.py` established the one number that matters: a perfect
reordering of the ten candidates the 12-byte code already retrieves would lift
FR@3 by +12 to +24 pp, against +0.4 to +2.5 pp for any better reading of the
same bits.  All the remaining value is in the second stage.

The temptation is to go build a reranker.  This session already learned what
that costs: the learned-threshold experiment optimised a proxy successfully in
480/480 archives and made retrieval WORSE, because nobody checked first
whether the proxy pointed at the goal.  So this measures the signals before
anything is built.

For every query, take the top-10 by the 12-byte code, then ask of each cheap
signal: if the ten were reordered by THIS signal alone, what FR@3 results?

  idf_overlap   IDF-weighted term overlap between question and candidate text
  num_overlap   do numbers/dates/times in the question appear in the candidate
  cap_overlap   shared capitalised tokens (a crude proper-noun proxy)
  row_index     position in the archive -- this session found storage order
                carries signal, so it is included as a control, not a feature
  length        candidate character count, as a null-ish control
  base          the code's own order (no reranking)
  ORACLE        the ceiling from run_where_next.py

Nothing here is a model.  Every signal is a few lines over the raw text, and
the point is to find out whether a few lines are enough before paying for
more.  If `idf_overlap` alone closes a third of the gap, a reranker is cheap;
if every signal is flat, the separation is semantic and a model is the only
route -- and that is worth knowing before starting.

Text and cached representation are aligned: `audit_seed.py` verified that
rebuilding from `items/*.json` reproduces the cached codes bit-exactly, so
`build_archive` row order matches the cached `C` row order.
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

TOPM = 10
WORD = re.compile(r"[A-Za-z']+")
NUMLIKE = re.compile(r"\d+(?::\d+)?(?:[/-]\d+)*")
CAPS = re.compile(r"\b[A-Z][a-z]{2,}\b")
SIGNALS = ["base", "idf_overlap", "num_overlap", "cap_overlap",
           "row_index", "neg_row_index", "length", "neg_length",
           "ORACLE"]
COMBOS = ["idf_overlap", "neg_length", "num_overlap", "cap_overlap"]
ALPHAS = (0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0)


def toks(s):
    return [w.lower() for w in WORD.findall(s)]


def archive_idf(texts):
    df = Counter()
    for t in texts:
        df.update(set(toks(t)))
    n = len(texts)
    return {w: math.log((1 + n) / (1 + c)) + 1.0 for w, c in df.items()}


def signal_values(qtext, cand_texts, cand_rows, idf):
    qt = set(toks(qtext))
    qn = set(NUMLIKE.findall(qtext))
    qc = set(CAPS.findall(qtext))
    out = {k: np.zeros(len(cand_texts)) for k in
           ("idf_overlap", "num_overlap", "cap_overlap",
            "row_index", "neg_row_index", "length", "neg_length")}
    for i, t in enumerate(cand_texts):
        tt = set(toks(t))
        out["idf_overlap"][i] = sum(idf.get(w, 0.0) for w in qt & tt)
        out["num_overlap"][i] = len(qn & set(NUMLIKE.findall(t)))
        out["cap_overlap"][i] = len(qc & set(CAPS.findall(t)))
        out["row_index"][i] = cand_rows[i]
        out["neg_row_index"][i] = -cand_rows[i]
        out["length"][i] = len(t)
        out["neg_length"][i] = -len(t)
    return out


def fr3_after_rerank(base_scores, new_order_scores, cand, gold, n):
    """Rerank only `cand` by `new_order_scores`; everything else keeps rank."""
    s = np.array(base_scores, dtype=np.float64, copy=True)
    lo = s[cand].min()
    span = max(s[cand].max() - lo, 1e-12)
    # place reranked candidates above every non-candidate, order by the signal
    r = np.asarray(new_order_scores, dtype=np.float64)
    rr = (r - r.min()) / max(r.max() - r.min(), 1e-12)
    s[cand] = s.max() + 1.0 + rr * span
    return B.exact_frac(s, gold, True)


def main():
    n_items = int(sys.argv[1]) if len(sys.argv) > 1 else 470
    adapter = BN.load_adapter()
    files = sorted(glob.glob(BN.ITEMS))
    assert len(files) == 470, len(files)
    files = files[:n_items]
    acc = defaultdict(list)
    fold = []
    n_done = 0

    for i, f in enumerate(files):
        tag = os.path.basename(f)[:-5]
        cp = os.path.join(H.SRC, "regen", "lme", "cache_repr", tag + ".pkl")
        if not os.path.exists(cp):
            continue
        d = pickle.loads(open(cp, "rb").read())
        C = np.asarray(d["C"], dtype=np.float64)
        q = np.asarray(d["qC"], dtype=np.float64).reshape(-1)
        gold = np.asarray(d["gold"]).ravel().astype(int)
        item = json.loads(open(f, encoding="utf-8").read())
        memories, gold_ids, issues = adapter.build_archive(item)
        if issues:
            continue
        texts = adapter.fit_input_payload(memories)
        if len(texts) != C.shape[0]:
            continue                       # alignment guard, never silent
        st = B.fit_archive(C)
        R = np.where(C >= 0, 1.0, -1.0)
        base = R @ (q / np.asarray(st["std"], dtype=np.float64))
        n = C.shape[0]
        m = min(TOPM, n)
        order = np.argsort(-base, kind="stable")
        thr = base[order[m - 1]]
        cand = np.nonzero(base >= thr)[0]
        idf = archive_idf(texts)
        vals = signal_values(str(item["question"]),
                             [texts[c] for c in cand], cand, idf)

        gset = set(int(x) for x in gold)
        acc["base"].append(B.exact_frac(base, gold, True))
        for k, v in vals.items():
            acc[k].append(fr3_after_rerank(base, v, cand, gold, n))
        # ---- COMBINATIONS: keep the code's own order, ADD the signal ----
        b = base[cand]
        bz = (b - b.mean()) / (b.std() + 1e-12)
        for k in COMBOS:
            v = vals[k]
            vz = (v - v.mean()) / (v.std() + 1e-12)
            for a in ALPHAS:
                acc[f"combo:{k}:{a}"].append(
                    fr3_after_rerank(base, bz + a * vz, cand, gold, n))
        fold.append(n_done % 2)
        # oracle: golds inside the candidate set, first
        inside = sum(1 for c in cand if int(c) in gset)
        acc["ORACLE"].append(min(inside, 3) / len(gset))
        # diagnostics: how separable is gold on each signal, inside the top-M
        isg = np.array([int(c) in gset for c in cand], dtype=bool)
        if isg.any() and (~isg).any():
            for k, v in vals.items():
                acc["sep_" + k].append(float(v[isg].mean() - v[~isg].mean())
                                       / (v.std() + 1e-12))
        n_done += 1
        if n_done % 100 == 0:
            print(f"  {n_done}", flush=True)

    fold = np.asarray(fold)
    combos = {}
    for k in COMBOS:
        per_a = {a: np.asarray(acc[f"combo:{k}:{a}"]) for a in ALPHAS}
        best_all = max(ALPHAS, key=lambda a: per_a[a].mean())
        # cross-fit: choose alpha on one fold, score on the other
        cross = np.empty(len(fold))
        for f_eval in (0, 1):
            tr = fold != f_eval
            a_hat = max(ALPHAS, key=lambda a: per_a[a][tr].mean())
            cross[fold == f_eval] = per_a[a_hat][fold == f_eval]
        combos[k] = {
            "by_alpha_pct": {str(a): float(per_a[a].mean() * 100)
                             for a in ALPHAS},
            "best_alpha_in_sample": best_all,
            "best_in_sample_pct": float(per_a[best_all].mean() * 100),
            "cross_fitted_pct": float(cross.mean() * 100),
            "selection_optimism_pp": float(
                (per_a[best_all].mean() - cross.mean()) * 100)}

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "benchmark": "lme", "top_m": TOPM, "n_queries": n_done,
           "alpha_is_cross_fitted": ("alpha chosen on one half of the queries "
                                     "and scored on the other, both ways; the "
                                     "in-sample value is reported beside it so "
                                     "the optimism is visible"),
           "fr3_percent": {k: float(np.mean(acc[k]) * 100) for k in SIGNALS},
           "combinations": combos,
           "gold_separation_in_sd": {
               k[4:]: float(np.mean(acc[k])) for k in acc if k.startswith("sep_")}}
    with open(os.path.join(HERE, "SIGNALS.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    fp = out["fr3_percent"]
    base, ceil = fp["base"], fp["ORACLE"]
    print(f"\n=== LongMemEval, {n_done} sorgu, ilk {TOPM} aday ===")
    print(f"  {'sinyal':>16s}{'FR@3':>8s}{'taban uzeri':>13s}"
          f"{'tavanin %':>11s}{'gold ayrimi (sd)':>19s}")
    for k in SIGNALS:
        got = fp[k] - base
        pct = got / (ceil - base) * 100 if ceil > base else float("nan")
        sep = out["gold_separation_in_sd"].get(k, float("nan"))
        sp = f"{sep:+.3f}" if sep == sep else "-"
        print(f"  {k:>16s}{fp[k]:8.2f}{got:+13.2f}{pct:10.1f}%{sp:>19s}")
    print(f"\n  --- kodun kendi siralamasina EKLENDIGINDE ---")
    print(f"  {'sinyal':>16s}{'en iyi alpha':>14s}{'ic-orneklem':>13s}"
          f"{'CAPRAZ':>9s}{'taban uzeri':>13s}{'tavanin %':>11s}"
          f"{'iyimserlik':>12s}")
    for k, c in out["combinations"].items():
        got = c["cross_fitted_pct"] - base
        pct = got / (ceil - base) * 100 if ceil > base else float("nan")
        print(f"  {k:>16s}{c['best_alpha_in_sample']:>14}"
              f"{c['best_in_sample_pct']:13.2f}{c['cross_fitted_pct']:9.2f}"
              f"{got:+13.2f}{pct:10.1f}%{c['selection_optimism_pp']:+12.2f}")
    print("\nwrote SIGNALS.json")


if __name__ == "__main__":
    main()
