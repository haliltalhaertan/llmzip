"""H1/H2/H3 — 13.7 pp bolum heterojenligini parcalama. SIFIR YENI MODEL CAGRISI.

HIPOTEZLER ANALIZDEN ONCE DONDURULDU (post-hoc fishing korumasi).
Kaynak: dis degerlendirme 2026-09-18, olculmeden once yazildi.

  H1: bolum etkisi, aday havuzu Hit@10 farkiyla aciklaniyor.
  H2: sozluksel ortusme, sign-vs-BM25 farkini aciklıyor.
  H3: her iki havuzda da gold varken yontem farki buyuk olcude kayboluyor.

Bu ucu disinda hicbir ozellik taranmaz. Baska bir sey merak edilirse AYRI
bir dosyada, kesfsel etiketiyle.

Veri: MATCHED_CI.json per_query (saklanmis) + items/*.json (metin).
Cikti: H123_RESULTS.json
"""
import json, re, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/H123_RESULTS.json"

FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}") if isinstance(m, dict) else str(m)

# ---------------------------------------------------------------- veri
pq = json.load(open(W / "audit_hard_r4/MATCHED_CI.json", encoding="utf-8"))["per_query"]
sec = {}
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    for l in f.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l); sec[r["qid"]] = r.get("section", "?")

rows = []
import pickle
for r in pq:
    qid = r["qid"]
    item = json.load(open(ITEM / f"{qid}.json", encoding="utf-8"))
    cache = pickle.load(open(W / f"regen/lme/cache_repr/{qid}.pkl", "rb"))
    sess = item["haystack_sessions"]
    flat = [m for s in sess for m in s] if isinstance(sess[0], list) else sess
    gold = set(int(g) for g in cache["gold"])
    qt   = set(tok(item["question"]))
    gtoks = [set(tok(text_of(flat[g]))) for g in gold if g < len(flat)]
    # sozluksel ortusme: soru ile gold belge arasinda (IDF agirliksiz + agirlikli)
    N = len(flat); df = Counter()
    for m in flat: df.update(set(tok(text_of(m))))
    idf = {t: math.log(1 + (N - n + 0.5) / (n + 0.5)) for t, n in df.items()}
    ov_raw = max((len(qt & g) / max(1, len(qt)) for g in gtoks), default=0.0)
    ov_idf = max((sum(idf.get(t, 0) for t in (qt & g)) / max(1e-9, sum(idf.get(t, 0) for t in qt))
                  for g in gtoks), default=0.0)
    rows.append({
        "qid": qid, "section": sec.get(qid, "?"),
        "delta": 100 * (r["sign96_fr3"] - r["bm25_fr3"]),
        "sign_cand": r["sign96_cand"], "bm25_cand": r["bm25_cand"],
        "sign_fr3": 100 * r["sign96_fr3"], "bm25_fr3": 100 * r["bm25_fr3"],
        "overlap_raw": ov_raw, "overlap_idf": ov_idf,
        "n_docs": N, "n_gold": len(gold), "q_len": len(qt),
    })

def mean(v): return sum(v) / len(v) if v else 0.0
def pearson(x, y):
    n = len(x); mx, my = mean(x), mean(y)
    sx = math.sqrt(sum((a-mx)**2 for a in x)); sy = math.sqrt(sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a, b in zip(x, y)) / (sx*sy) if sx and sy else 0.0

res = {"n": len(rows), "hypotheses_frozen_before_analysis": ["H1", "H2", "H3"]}

# ---------------------------------------------------------------- H1
by = defaultdict(list)
for r in rows: by[r["section"]].append(r)
h1 = {}
for s, v in sorted(by.items(), key=lambda x: mean([r["delta"] for r in x[1]])):
    h1[s] = {"n": len(v),
             "delta_fr3":   round(mean([r["delta"] for r in v]), 2),
             "sign_cand10": round(100*mean([r["sign_cand"] for r in v]), 2),
             "bm25_cand10": round(100*mean([r["bm25_cand"] for r in v]), 2),
             "cand_gap":    round(100*mean([r["sign_cand"]-r["bm25_cand"] for r in v]), 2),
             "sign_fr3":    round(mean([r["sign_fr3"] for r in v]), 2),
             "bm25_fr3":    round(mean([r["bm25_fr3"] for r in v]), 2)}
xs = [h1[s]["cand_gap"] for s in h1]; ys = [h1[s]["delta_fr3"] for s in h1]
res["H1_section_table"] = h1
res["H1_corr_candgap_vs_delta_sections"] = round(pearson(xs, ys), 3)
res["H1_corr_query_level"] = round(pearson([r["sign_cand"]-r["bm25_cand"] for r in rows],
                                           [r["delta"] for r in rows]), 3)

# ---------------------------------------------------------------- H2
res["H2_corr_overlap_raw_vs_delta"] = round(pearson([r["overlap_raw"] for r in rows],
                                                    [r["delta"] for r in rows]), 3)
res["H2_corr_overlap_idf_vs_delta"] = round(pearson([r["overlap_idf"] for r in rows],
                                                    [r["delta"] for r in rows]), 3)
srt = sorted(rows, key=lambda r: r["overlap_idf"])
q = len(srt) // 4
res["H2_quartiles_by_idf_overlap"] = [
    {"quartile": i+1, "n": len(srt[i*q:(i+1)*q] if i < 3 else srt[3*q:]),
     "mean_overlap_idf": round(mean([r["overlap_idf"] for r in (srt[i*q:(i+1)*q] if i < 3 else srt[3*q:])]), 3),
     "delta_fr3": round(mean([r["delta"] for r in (srt[i*q:(i+1)*q] if i < 3 else srt[3*q:])]), 2)}
    for i in range(4)]

# ---------------------------------------------------------------- H3
groups = {"both": [], "sign_only": [], "bm25_only": [], "neither": []}
for r in rows:
    k = ("both" if r["sign_cand"] and r["bm25_cand"] else
         "sign_only" if r["sign_cand"] else
         "bm25_only" if r["bm25_cand"] else "neither")
    groups[k].append(r)
res["H3_inclusion_groups"] = {k: {"n": len(v), "pct": round(100*len(v)/len(rows), 1),
                                 "delta_fr3": round(mean([r["delta"] for r in v]), 2)}
                              for k, v in groups.items()}
res["H3_by_section"] = {s: {k: sum(1 for r in v
                            if (("both" if r["sign_cand"] and r["bm25_cand"] else
                                 "sign_only" if r["sign_cand"] else
                                 "bm25_only" if r["bm25_cand"] else "neither") == k))
                            for k in groups} for s, v in by.items()}
b = groups["both"]
res["H3_conditional_both"] = {"n": len(b),
    "sign_fr3": round(mean([r["sign_fr3"] for r in b]), 2),
    "bm25_fr3": round(mean([r["bm25_fr3"] for r in b]), 2),
    "delta_fr3": round(mean([r["delta"] for r in b]), 2)}
res["overall_delta"] = round(mean([r["delta"] for r in rows]), 2)

OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")

print(f"n={res['n']}  genel delta={res['overall_delta']:+.2f} pp\n")
print("=== H1: bolum etkisi aday havuzuyla aciklaniyor mu? ===")
print(f"{'bolum':28s} {'n':>4s} {'delta':>7s} {'signH10':>8s} {'bm25H10':>8s} {'fark':>7s}")
for s, v in h1.items():
    print(f"{s:28s} {v['n']:>4d} {v['delta_fr3']:>+7.2f} {v['sign_cand10']:>8.2f} "
          f"{v['bm25_cand10']:>8.2f} {v['cand_gap']:>+7.2f}")
print(f"  korelasyon (bolum duzeyi, n=6): r={res['H1_corr_candgap_vs_delta_sections']:+.3f}")
print(f"  korelasyon (sorgu duzeyi, n={res['n']}): r={res['H1_corr_query_level']:+.3f}")

print("\n=== H2: sozluksel ortusme farki acikliyor mu? ===")
print(f"  r(ham ortusme, delta)      = {res['H2_corr_overlap_raw_vs_delta']:+.3f}")
print(f"  r(IDF-agirlikli, delta)    = {res['H2_corr_overlap_idf_vs_delta']:+.3f}")
for qd in res["H2_quartiles_by_idf_overlap"]:
    print(f"    Q{qd['quartile']} ortusme={qd['mean_overlap_idf']:.3f} (n={qd['n']:3d}) -> delta {qd['delta_fr3']:+6.2f}")

print("\n=== H3: gold hangi havuzda? ===")
for k, v in res["H3_inclusion_groups"].items():
    print(f"  {k:10s} n={v['n']:3d} ({v['pct']:4.1f}%)  delta={v['delta_fr3']:+6.2f}")
c = res["H3_conditional_both"]
print(f"\n  HER IKISINDE de gold varken (n={c['n']}):")
print(f"    sign+Jev {c['sign_fr3']:.2f}  vs  BM25+Jev {c['bm25_fr3']:.2f}  -> delta {c['delta_fr3']:+.2f} pp")
print(f"    (genel delta {res['overall_delta']:+.2f} pp ile karsilastir)")
