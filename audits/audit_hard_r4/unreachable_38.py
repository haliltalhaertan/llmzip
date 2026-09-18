"""38 KURTARILAMAZ SORGU: "top-10 biraz kucuk" mu, "temsil bulamiyor" mu? SIFIR MODEL CAGRISI.

RRF_VS_BM25.json'a gore 470 sorgunun 38'inde (%8.1) gold ne sign96 ne BM25 top-10'unda.
Bu 38 vaka icin gold'un GERCEK rank'ini iki sistemde de tam derinlikte olcuyoruz.

SKORLAMA KURTARIMI: sign96 siralamasi yalniz top-10 saklanmis, ama cache_repr/*.pkl icinde
ham C (N x 96) ve qC saklı. Saklanan skor = negatif Hamming mesafesi = -(96 - sign(C)@sign(qC))/2.
470/470 sorguda saklanan skor dizisi birebir yeniden uretildi -> tam derinlik guvenli.

ESITLIK DURUSU: Hamming skorlari cok sayida esitlik uretiyor. Gold'un rank'i esitlik grubu
icinde belirsiz -> HEM iyimser (grubun basi) HEM kotumser (grubun sonu) rank raporlanir.
Tek bir rank uydurmak yerine aralik verilir.

Cikti: UNREACHABLE_38.json
"""
import json, pickle, re, math
import numpy as np
from collections import Counter
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/UNREACHABLE_38.json"

K1, B = 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())

def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]

def bm25_scores(docs, query):
    D=[tok(d) for d in docs]; N=len(D); avg=sum(len(d) for d in D)/max(1,N)
    df=Counter()
    for d in D: df.update(set(d))
    idf={t: math.log(1+(N-n+0.5)/(n+0.5)) for t,n in df.items()}
    q=tok(query); sc=[]
    for d in D:
        tf,dl,s=Counter(d),len(d),0.0
        for t in q:
            if t in tf:
                f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
        sc.append(s)
    return np.array(sc)

def rank_band(scores, gold_ids):
    """Esitlikleri durust ele al: (iyimser, kotumser) rank, 1-tabanli."""
    best=(10**9,10**9)
    for g in gold_ids:
        gs=scores[g]
        strictly_better=int((scores>gs).sum())
        tied_others   =int((scores==gs).sum())-1
        opt=strictly_better+1                       # esitlik grubunun basi
        pes=strictly_better+tied_others+1           # esitlik grubunun sonu
        if opt<best[0]: best=(opt,pes)
    return best

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

# DOGRU KUME: gold ne sign96 top-10'da ne BM25 top-10'da. RRF havuzu DEGIL --
# RRF, sign96'nin bulduğu bir gold'u eleyebiliyor (olculdu), o yuzden RRF tabanli
# kume (40) bu soruyu yanlis cerceveler. Dogru kume H3'teki "neither" = 38.
prev=json.load(open(W/"audit_hard_r4/RRF_VS_BM25.json",encoding="utf-8"))
_bm25_top10={}
unreachable=set(); rrf_dropped=set()
for r in rows:
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=c["C"].shape[0]: continue
    gold=set(int(g) for g in c["gold"])
    bm=bm25_scores([text_of(m) for m in flat], item["question"])
    bm10=set(map(int,np.argsort(-bm,kind="stable")[:10])); _bm25_top10[qid]=bm10
    s10=set(r["sign96"]["ids"])
    if not (gold & s10) and not (gold & bm10): unreachable.add(qid)
prev_neither={x["qid"] for x in prev["per_query"] if not x["bm25_cand"] and not x["rrf_cand"]}
rrf_dropped = prev_neither - unreachable
print(f"gold ne sign96 ne BM25 top-10'unda : {len(unreachable)} / {len(rows)}", flush=True)
print(f"RRF'nin ELEDIGI (sign96'da vardi)  : {len(rrf_dropped)}", flush=True)

recs=[]
for r in rows:
    if r["qid"] not in unreachable: continue
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    C,qC=c["C"],c["qC"]; N=C.shape[0]
    gold=[int(g) for g in c["gold"]]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=N: continue
    texts=[text_of(m) for m in flat]

    sign_sc = -((96-(np.sign(C)@np.sign(qC)))/2)
    bm_sc   = bm25_scores(texts, item["question"])
    s_opt,s_pes = rank_band(sign_sc, gold)
    b_opt,b_pes = rank_band(bm_sc,   gold)

    # gold ile soru arasinda lexical ortusme
    q=set(tok(item["question"]))
    ov=max((len(q & set(tok(texts[g])))/max(1,len(q))) for g in gold)
    recs.append({"qid":qid,"section":r.get("section",""),"N":N,"n_gold":len(gold),
                 "sign_rank_opt":s_opt,"sign_rank_pes":s_pes,
                 "bm25_rank_opt":b_opt,"bm25_rank_pes":b_pes,
                 "best_rank_opt":min(s_opt,b_opt),"best_rank_pes":min(s_pes,b_pes),
                 "q_gold_overlap":round(ov,3)})

print(f"cozumlenen: {len(recs)}\n", flush=True)

def band(v,lo,hi): return sum(1 for x in v if lo<=x<=hi)
bo=[x["best_rank_opt"] for x in recs]; bp=[x["best_rank_pes"] for x in recs]
print("=== GOLD'UN EN IYI RANK'I (iki sistemin iyisi) ===")
print(f"{'aralik':>12s} {'iyimser':>9s} {'kotumser':>9s}")
for lo,hi,lab in [(11,20,"11-20"),(21,50,"21-50"),(51,100,"51-100"),(101,10**9,"101+")]:
    print(f"{lab:>12s} {band(bo,lo,hi):>9d} {band(bp,lo,hi):>9d}")
print(f"{'medyan':>12s} {int(np.median(bo)):>9d} {int(np.median(bp)):>9d}")

near_o=band(bo,11,20); near_p=band(bp,11,20)
res={"n_unreachable":len(recs),"n_total":len(rows),
     "rrf_dropped_golds":sorted(rrf_dropped),
     "scoring_recovery":"stored score = -(96 - sign(C)@sign(qC))/2; verified 470/470 exact",
     "tie_handling":"optimistic = head of tie group, pessimistic = tail; both reported",
     "median_best_rank_optimistic":int(np.median(bo)),
     "median_best_rank_pessimistic":int(np.median(bp)),
     "band_11_20":{"optimistic":near_o,"pessimistic":near_p},
     "band_21_50":{"optimistic":band(bo,21,50),"pessimistic":band(bp,21,50)},
     "band_51_100":{"optimistic":band(bo,51,100),"pessimistic":band(bp,51,100)},
     "band_101_plus":{"optimistic":band(bo,101,10**9),"pessimistic":band(bp,101,10**9)},
     "median_corpus_size":int(np.median([x["N"] for x in recs])),
     "median_q_gold_overlap":round(float(np.median([x["q_gold_overlap"] for x in recs])),3),
     "multi_gold":sum(1 for x in recs if x["n_gold"]>1),
     "by_section":dict(Counter(x["section"] for x in recs)),
     "per_query":sorted(recs,key=lambda x:x["best_rank_opt"])}

print(f"\n=== TESHIS ===")
print(f"  'top-10 biraz kucuk' (rank 11-20) : {near_o} iyimser / {near_p} kotumser  "
      f"({100*near_o/len(recs):.0f}% / {100*near_p/len(recs):.0f}%)")
deep_o=band(bo,101,10**9)
print(f"  'temsil bulamiyor'   (rank 101+)  : {deep_o} iyimser / {band(bp,101,10**9)} kotumser")
print(f"  medyan korpus boyutu: {res['median_corpus_size']} belge")
print(f"  soru-gold lexical ortusme medyani: {res['median_q_gold_overlap']}")
print(f"  birden fazla gold gerektiren: {res['multi_gold']}/{len(recs)}")
print(f"\n  bolum dagilimi: {res['by_section']}")
print(f"\n  en yakin 8 (iyimser rank):")
for x in res["per_query"][:8]:
    print(f"    {x['qid'][:28]:28s} sign {x['sign_rank_opt']:>4d}-{x['sign_rank_pes']:<4d} "
          f"bm25 {x['bm25_rank_opt']:>4d}-{x['bm25_rank_pes']:<4d} N={x['N']:>4d}")
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nkayit: {OUT.name}")
