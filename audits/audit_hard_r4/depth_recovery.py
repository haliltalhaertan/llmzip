"""DERINLIK KURTARMA EGRISI + COKLU-KANIT AYRIMI. Sifir model cagrisi.

Dis degerlendirme hakli: "top-10 genisletmek %16-18 kurtarir" yalniz top-20 icin dogruydu.
Tam kumulatif egri hesaplanir. AMA bir incelik var:

FR@3 = |top3 ∩ gold| / |gold|. Coklu-gold sorularda BIR gold'u havuza sokmak kismi kredi verir;
tam kredi TUM gold'lari gerektirir. "Kurtarildi" sayimi bunu gizleyebilir -> hem ANY-gold hem
ALL-gold erisilebilirligi ayri raporlanir.

Ayrica dis degerlendirmenin uclu tasnifi veriye karsi sinanir:
  1. kolay retrieval   (gold zaten top-10'da)
  2. derin retrieval   (rank 11-100)
  3. yapisal zor       (sifir lexical ortusme + coklu kanit)

Cikti: DEPTH_RECOVERY.json
"""
import json, pickle, re, math
import numpy as np
from collections import Counter
from pathlib import Path

W    = Path("C:/Users/MDP/dev/llmzip-work")
CKPT = W / "_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM = W / "regen/lme/items"
OUT  = W / "audit_hard_r4/DEPTH_RECOVERY.json"

K1, B = 1.2, 0.75
FROZEN = re.compile(r"\b\w\w+\b")
STOP = set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m):
    return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m, dict) else str(m)[:1200]
def bm25_scores(docs, query):
    D=[tok(d) for d in docs]; N=len(D); avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t: math.log(1+(N-c+0.5)/(c+0.5)) for t,c in df.items()}
    q=tok(query); out=[]
    for x in D:
        tf,dl,s=Counter(x),len(x),0.0
        for t in q:
            if t in tf:
                f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
        out.append(s)
    return np.array(out)

def rank_band(scores, g):
    gs=scores[g]; sb=int((scores>gs).sum()); tied=int((scores==gs).sum())-1
    return sb+1, sb+tied+1

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
prev=json.load(open(W/"audit_hard_r4/UNREACHABLE_38.json",encoding="utf-8"))
target={x["qid"] for x in prev["per_query"]}
print(f"kurtarilamaz sorgu: {len(target)}", flush=True)

recs=[]
for r in rows:
    if r["qid"] not in target: continue
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    C,qC=c["C"],c["qC"]; golds=[int(g) for g in c["gold"]]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=C.shape[0]: continue
    texts=[text_of(m) for m in flat]
    sign_sc=-((96-(np.sign(C)@np.sign(qC)))/2)
    bm_sc  = bm25_scores(texts, item["question"])
    q=set(tok(item["question"]))
    per=[]
    for g in golds:
        so,sp=rank_band(sign_sc,g); bo,bp=rank_band(bm_sc,g)
        per.append({"gold":g,"best_opt":min(so,bo),"best_pes":min(sp,bp),
                    "overlap":len(q & set(tok(texts[g])))/max(1,len(q))})
    recs.append({"qid":qid,"section":r.get("section",""),"n_gold":len(golds),
                 "any_opt":min(p["best_opt"] for p in per),
                 "any_pes":min(p["best_pes"] for p in per),
                 "all_opt":max(p["best_opt"] for p in per),
                 "all_pes":max(p["best_pes"] for p in per),
                 "max_overlap":round(max(p["overlap"] for p in per),3),
                 "per_gold":per})
n=len(recs)
print(f"cozumlenen: {n}\n", flush=True)

print("=== KUMULATIF KURTARMA: derinlik kac vakayi kurtarir? ===")
print(f"{'derinlik':>9s} | {'EN AZ BIR gold':>22s} | {'TUM goldlar':>22s}")
print(f"{'':9s} | {'iyimser':>10s} {'kotumser':>10s} | {'iyimser':>10s} {'kotumser':>10s}")
curve={}
for dep in [10,20,30,50,75,100,200]:
    ao=sum(1 for x in recs if x["any_opt"]<=dep); ap=sum(1 for x in recs if x["any_pes"]<=dep)
    lo=sum(1 for x in recs if x["all_opt"]<=dep); lp=sum(1 for x in recs if x["all_pes"]<=dep)
    curve[dep]={"any_opt":ao,"any_pes":ap,"all_opt":lo,"all_pes":lp}
    print(f"top-{dep:<6d}| {ao:>4d}/{n} {100*ao/n:>4.0f}% {ap:>4d}/{n} {100*ap/n:>4.0f}% "
          f"| {lo:>4d}/{n} {100*lo/n:>4.0f}% {lp:>4d}/{n} {100*lp/n:>4.0f}%")

multi=[x for x in recs if x["n_gold"]>1]; single=[x for x in recs if x["n_gold"]==1]
print(f"\n=== COKLU-KANIT AYRIMI ===")
print(f"  tek gold  : {len(single)}/{n}   coklu gold: {len(multi)}/{n}")
for dep in [50,100]:
    s_ok=sum(1 for x in single if x["any_pes"]<=dep)
    m_any=sum(1 for x in multi if x["any_pes"]<=dep)
    m_all=sum(1 for x in multi if x["all_pes"]<=dep)
    print(f"  top-{dep} (kotumser): tek gold {s_ok}/{len(single)} | "
          f"coklu: en az bir {m_any}/{len(multi)}, TUMU {m_all}/{len(multi)}")

print(f"\n=== UCLU TASNIF SINAMASI (kotumser, derinlik 100) ===")
g2=[x for x in recs if x["any_pes"]<=100 and not (x["max_overlap"]==0 and x["n_gold"]>1)]
g3=[x for x in recs if x["max_overlap"]==0 and x["n_gold"]>1]
g3b=[x for x in recs if x["max_overlap"]==0]
other=[x for x in recs if x not in g2 and x not in g3]
print(f"  grup 2 'derin retrieval' (rank<=100, yapisal degil) : {len(g2)}")
print(f"  grup 3 'yapisal zor' (sifir ortusme VE coklu kanit) : {len(g3)}")
print(f"     (yalniz sifir ortusme, gold sayisi farketmez)    : {len(g3b)}")
print(f"  ikisine de girmeyen                                  : {len(other)}")
zero_multi=sum(1 for x in recs if x["max_overlap"]==0 and x["n_gold"]>1)
zero_single=sum(1 for x in recs if x["max_overlap"]==0 and x["n_gold"]==1)
print(f"\n  sifir-ortusme & coklu : {zero_multi}   sifir-ortusme & tek : {zero_single}")
print(f"  ortusme>0 & coklu     : {sum(1 for x in recs if x['max_overlap']>0 and x['n_gold']>1)}"
      f"   ortusme>0 & tek : {sum(1 for x in recs if x['max_overlap']>0 and x['n_gold']==1)}")

res={"n":n,"curve":curve,
     "note":"any = at least one gold reachable; all = every gold reachable (FR@3 needs all for full credit)",
     "multi_gold":len(multi),"single_gold":len(single),
     "taxonomy":{"deep_retrieval_rank_le_100":len(g2),"structural_zero_overlap_multi":len(g3),
                 "zero_overlap_any":len(g3b)},
     "cross_tab":{"zero_overlap_multi":zero_multi,"zero_overlap_single":zero_single,
                  "overlap_multi":sum(1 for x in recs if x["max_overlap"]>0 and x["n_gold"]>1),
                  "overlap_single":sum(1 for x in recs if x["max_overlap"]>0 and x["n_gold"]==1)},
     "per_query":recs}
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nkayit: {OUT.name}")
