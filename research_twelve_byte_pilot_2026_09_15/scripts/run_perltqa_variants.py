#!/usr/bin/env python3
"""PerLTQA's two unused releases: English v1, and the CHINESE original.

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION]
[DISCLOSE-BEFORE-USE]

PerLTQA is the outlier of the four benchmarks: the only one where SIGN96
loses to plain float, and the only one where asym/b8 beat sym.  Two other
releases of it ship in the repo and have never been run:

  en_v1  bench3/PerLTQA/Dataset/en/      a different English release
  zh     bench3/PerLTQA/Dataset/zh/      the CHINESE original

Both store `perltmem` as a LIST (keyed internally by profile.Protagonist),
not the name->record dict of en_v2, which is why a naive port finds zero
matching characters.  Keyed properly, both give 32 characters.

Archive construction, gold mapping and the fit are ported from
bench3/runs/b3b_perltqa/step2_build.py, INCLUDING the two seeds it gets
right (5101 for the LSA32 stage, 5204 for the final SVD96).  Scoring goes
through run_hit10.score_archive, which asserts frac@3 == lib_b8.exact_frac
for every arm on every query.

CONFOUND, must travel with the Chinese numbers: the frozen word channel is
TfidfVectorizer(ngram_range=(1,2), stop_words='english') with sklearn's
default whitespace-ish token pattern.  Chinese is not whitespace-delimited,
so that channel very nearly collapses and the char_wb 3-5-gram channel
carries the representation alone.  That IS what the frozen recipe does to
Chinese -- a fair test of transfer, not of a tokenizer chosen for Chinese.
Read it as "the frozen recipe applied to Chinese", never as "TF-IDF cannot
do Chinese".

Benchmarks are never pooled; each variant is its own row.
"""
import ast
import json
import os
import sys
from collections import Counter

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_hit10 as H  # noqa: E402

BASE = os.path.join(H.SRC, "bench3", "PerLTQA", "Dataset")
VARIANTS = {
    "en_v1": (os.path.join(BASE, "en"), "perltqa_en.json", "perltmem_en.json"),
    "zh": (os.path.join(BASE, "zh"), "perltqa.json", "perltmem.json"),
}
LATENT_SEED, SVD_SEED = 5101, 5204
GROUPED = ("social_relationship", "events", "dialogues")


def parse_social(v):
    return v if isinstance(v, dict) else ast.literal_eval(v)


def refkey(s):
    s = str(s).strip()
    return [str(x) for x in ast.literal_eval(s)] if s.startswith("[") else [s]


def build_items(b, ordv):
    items = []
    for i, (f, v) in enumerate(b["profile"].items()):
        items.append((f"PQ{ordv:03d}_PRF_{i:03d}", f"[profile] {f}: {v}"))
    items.append((f"PQ{ordv:03d}_DSC_000",
                  f"[profile_description] {b['profile_description']}"))
    soc = parse_social(b["social_relationship"])
    for i, k in enumerate(sorted(soc)):
        e = soc[k]
        extra = "".join(
            f"; {kk}: {vv}" for kk, vv in sorted(e.items())
            if kk not in ("Supporting Characters", "Relationship",
                          "Description"))
        items.append((
            f"PQ{ordv:03d}_SOC_{i:03d}",
            f"[social {k}] {e.get('Supporting Characters', '')} "
            f"({e.get('Relationship', '')}): "
            f"{e.get('Description', '')}{extra}"))
    for i, k in enumerate(sorted(b["events"])):
        ev = b["events"][k]
        if isinstance(ev, dict) and "content" in ev:
            content = ev["content"]
        elif isinstance(ev, str):
            content = ev
        else:
            content = json.dumps(ev, ensure_ascii=False)
        items.append((f"PQ{ordv:03d}_EVE_{i:03d}", f"[event {k}] {content}"))
    t = 0
    for k in sorted(b["dialogues"]):
        for ts in sorted(b["dialogues"][k]["contents"]):
            for turn in b["dialogues"][k]["contents"][ts]:
                items.append((f"PQ{ordv:03d}_DLG_{t:03d}",
                              f"[dialogue {k} @ {ts}] {turn}"))
                t += 1
    return items


def fit_archive(texts):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2),
                         stop_words="english", sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                         sublinear_tf=True)
    Xw = normalize(wv.fit_transform(texts))
    Xc = normalize(cv.fit_transform(texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    svd = TruncatedSVD(n_components=d, random_state=LATENT_SEED)
    Xl = normalize(svd.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(0, keepdims=True)
    return wv, cv, svd, s96, mu, (Y - mu).astype(np.float64)


def encode_query(wv, cv, svd, s96, mu, q):
    Qw = normalize(wv.transform([q]))
    Qc = normalize(cv.transform([q]))
    Ql = normalize(svd.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s96.transform(Zq)) - mu).reshape(-1)


def section_index(b):
    """item-row index for every gold key, in build_items order."""
    prof_keys = list(b["profile"])
    soc_keys = sorted(parse_social(b["social_relationship"]))
    ev_keys = sorted(b["events"])
    off = len(prof_keys) + 1
    prof = {f: i for i, f in enumerate(prof_keys)}
    soc = {k: off + i for i, k in enumerate(soc_keys)}
    ev = {k: off + len(soc_keys) + i for i, k in enumerate(ev_keys)}
    dbase, t, dlg = off + len(soc_keys) + len(ev_keys), 0, {}
    for k in sorted(b["dialogues"]):
        idxs = []
        for ts in sorted(b["dialogues"][k]["contents"]):
            for _ in b["dialogues"][k]["contents"][ts]:
                idxs.append(dbase + t)
                t += 1
        dlg[k] = idxs
    return prof, soc, ev, dlg


def gold_for(section, key, q, prof, soc, ev, dlg, ttext):
    if section == "social_relationship":
        return [soc[key]] if key in soc else []
    if section == "events":
        return [ev[key]] if key in ev else []
    if key not in dlg:
        return []
    idxs = dlg[key]
    ancs = [(list(a)[0], list(a.values())[0]) for a in q.get("Memory Anchors", [])]
    named = [x for x, span in ancs if span != [-1, -1]]
    if not named:
        return list(idxs)
    hit = [i for i in idxs
           if any(a.lower() in ttext[i].lower() for a in named)]
    return hit if hit else list(idxs)


def run(tag):
    base, qf, mf = VARIANTS[tag]
    qa = json.load(open(os.path.join(base, qf), encoding="utf-8"))
    memlist = json.load(open(os.path.join(base, mf), encoding="utf-8"))
    mem = {}
    for r in memlist:                    # keyed by protagonist, not position
        name = (r.get("profile") or {}).get("Protagonist")
        if name and name not in mem:
            mem[name] = r
    names = sorted({list(e)[0] for e in qa} & set(mem))
    ORD = {c: i for i, c in enumerate(names)}
    res = Counter()
    rows_all, pools, excluded = [], [], []

    for entry in qa:
        for char, d in entry.items():
            if char not in ORD:
                continue
            b = mem[char]
            items = build_items(b, ORD[char])
            wv, cv, svd, s96, mu, C = fit_archive([t for _, t in items])
            # Frozen port rule (bench3/runs/b3b_perltqa/step2_exclude.py):
            # TruncatedSVD silently caps n_components at min(n_samples,
            # n_features) with no warning.  An archive that cannot support
            # SVD96 is EXCLUDED, never silently shrunk.
            if C.shape[1] != 96 or not np.isfinite(C).all():
                res["excluded_cannot_support_svd96"] += 1
                excluded.append({"ordinal": ORD[char], "N": int(C.shape[0]),
                                 "dim": int(C.shape[1]),
                                 "finite": bool(np.isfinite(C).all())})
                print(f"    {ORD[char]:3d}  N={C.shape[0]:4d}  "
                      f"DISLANDI dim={C.shape[1]}", flush=True)
                continue
            prof, soc, ev, dlg = section_index(b)
            ttext = {i: tx for i, (_, tx) in enumerate(items)}

            qs, golds = [], []
            for q in d.get("profile", []):
                rk = refkey(q["Reference Memory"])[0]
                g = [prof[rk]] if rk in prof else []
                res["profile_resolved" if g else "profile_miss"] += 1
                if g:
                    qs.append(str(q["Question"]))
                    golds.append(g)
            for s in GROUPED:
                # en_v1/en_v2 store a LIST of single-key {key: [questions]};
                # zh stores a DICT key -> [questions].  Normalise both.
                sec = d.get(s, [])
                pairs = (list(sec.items()) if isinstance(sec, dict)
                         else [(list(g)[0], list(g.values())[0]) for g in sec])
                for key, qlist in pairs:
                    for q in qlist:
                        g = gold_for(s, key, q, prof, soc, ev, dlg, ttext)
                        res[f"{s}_resolved" if g else f"{s}_miss"] += 1
                        if g:
                            qs.append(str(q["Question"]))
                            golds.append(g)
            if not qs:
                continue
            Q = np.stack([encode_query(wv, cv, svd, s96, mu, x) for x in qs])
            rows_all.extend(
                H.score_archive(C, Q, [np.asarray(g, int) for g in golds]))
            pools.append(C.shape[0])
            print(f"    {ORD[char]:3d}  N={C.shape[0]:4d}  q={len(qs):4d}",
                  flush=True)

    out = {"labels": ["LOCAL EXPLORATORY PILOT", "NOT PREREGISTERED",
                      "NOT FOR CITATION", "DISCLOSE-BEFORE-USE"],
           "variant": tag,
           "n_archives": len(pools),
           "n_queries": len(rows_all),
           "pool_mean": float(np.mean(pools)) if pools else None,
           "resolution": dict(res),
           "excluded_archives": excluded,
           "exclusion_rule": ("archives whose SVD96 silently capped below 96 dims are excluded, not shrunk -- per bench3/runs/b3b_perltqa/step2_exclude.py"),
           "confound": (
               "the frozen word channel is whitespace-tokenised with English "
               "stop words; on Chinese it nearly collapses and char_wb "
               "3-5-grams carry the representation alone"
               if tag == "zh" else None),
           "hit_percent": {}, "frac_percent": {}}
    for k in H.KS:
        out["hit_percent"][str(k)] = {
            a: float(np.mean([r[f"hit{k}_{a}"] for r in rows_all]) * 100)
            for a in H.ARMS}
        out["frac_percent"][str(k)] = {
            a: float(np.mean([r[f"frac{k}_{a}"] for r in rows_all]) * 100)
            for a in H.ARMS}
    with open(os.path.join(HERE, f"PERLTQA_{tag}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    return out


def main():
    for tag in (sys.argv[1:] or list(VARIANTS)):
        print(f"=== {tag} ===", flush=True)
        o = run(tag)
        print(f"\n  {tag}: {o['n_archives']} arsiv, {o['n_queries']} sorgu, "
              f"havuz~{o['pool_mean']:.0f}")
        print("  " + f"{'kol':12s}" + "".join(f"  hit@{k:<5d}" for k in H.KS))
        for a in H.ARMS:
            print("  " + f"{a:12s}" + "".join(
                f"  {o['hit_percent'][str(k)][a]:7.2f}" for k in H.KS))
        print(flush=True)


if __name__ == "__main__":
    main()
