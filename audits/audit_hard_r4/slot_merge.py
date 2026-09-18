"""SLOT-KORUYAN IKI-TUR BIRLESIMI. SIFIR MODEL CAGRISI.

L-113 bulgusu: M2 ikinci turda yeni gold buluyor (%4.65 -> %22.09) ama uctan uca
FR@3 dusuyor (-6.43) cunku ikinci tur birinci turun siralamasini EZIYOR.

Test: iki turu AYRI tutup sabit 3 slot butcesinde birlestirirsek FR@3 yukseliyor mu?

KOLLAR (hepsi tam 3 belge, ayni butce):
  base      : Tur1 top-3                        (mevcut taban)
  replace   : M2 genisletilmis sorgunun top-3'u (L-112'nin real_M2 kolu)
  merge_2_1 : Tur1 rank1,rank2 + Tur2'nin yeni en iyisi
  merge_1_2 : Tur1 rank1 + Tur2'nin yeni en iyi 2'si
  rrf_2turn : iki turun siralamalarinin RRF birlesimi, top-3
  anchor_2  : Tur1 rank1 KORUNUR + kalan 2 slot iki turun birlesiminden (RRF)

TUM SORGULARDA kosulur (470), yalniz zor altkumede degil -- cunku karar metrigi budur.
Ayrica coklu-gold altkumesi ayri raporlanir (mekanizmanin hedefi orasi).

Cikti: SLOT_MERGE.json
"""
import json, pickle, re, math, random
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

W=Path("C:/Users/MDP/dev/llmzip-work")
CKPT=W/"_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM=W/"regen/lme/items"
OUT =W/"audit_hard_r4/SLOT_MERGE.json"
K1,B=1.2,0.75; BOOT,SEED=20000,20260918; RRF_K=60
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows+=[json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

ARMS=["base","replace","merge_2_1","merge_1_2","rrf_2turn","anchor_2"]
per=[]
print(f"sorgu: {len(rows)} | {len(ARMS)} kol, hepsi 3 slot", flush=True)

for n,r in enumerate(rows,1):
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    gold=set(int(g) for g in c["gold"])
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=c["C"].shape[0]: continue
    texts=[text_of(m) for m in flat]
    D=[tok(x) for x in texts]; N=len(D); avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t: math.log(1+(N-k+0.5)/(k+0.5)) for t,k in df.items()}
    TF=[Counter(x) for x in D]; DL=[len(x) for x in D]
    def score(qt):
        o=np.zeros(N)
        for i in range(N):
            tf,dl,s=TF[i],DL[i],0.0
            for t in qt:
                if t in tf:
                    f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
            o[i]=s
        return o

    q=tok(item["question"])
    s1=score(q); o1=list(map(int,np.argsort(-s1,kind="stable")))
    anchor=o1[0]
    # Tur2: M2 genisletme (capa = Tur1 rank1, gercek sistem boyle yapar)
    at=tok(texts[anchor]); vals=sorted((idf.get(t,0.0) for t in set(at)),reverse=True)
    thr=vals[max(0,int(0.25*len(vals))-1)] if vals else 0.0
    s2=score(q+[t for t in at if idf.get(t,0.0)>=thr])
    o2=list(map(int,np.argsort(-s2,kind="stable")))

    def new_from_t2(exclude,k):
        out=[]
        for d in o2:
            if d not in exclude and d not in out:
                out.append(d)
                if len(out)>=k: break
        return out
    def rrf(lists,k=3,excl=()):
        sc=defaultdict(float)
        for L in lists:
            for rk,d in enumerate(L[:20],1):
                if d not in excl: sc[d]+=1.0/(RRF_K+rk)
        return [d for d,_ in sorted(sc.items(),key=lambda x:-x[1])[:k]]

    sel={}
    sel["base"]     = o1[:3]
    sel["replace"]  = o2[:3]
    sel["merge_2_1"]= o1[:2] + new_from_t2(set(o1[:2]),1)
    sel["merge_1_2"]= o1[:1] + new_from_t2(set(o1[:1]),2)
    sel["rrf_2turn"]= rrf([o1,o2],3)
    sel["anchor_2"] = [anchor] + rrf([o1,o2],2,excl={anchor})

    row={"qid":qid,"n_gold":len(gold),"multi":len(gold)>1}
    for a in ARMS:
        s=sel[a][:3]
        row[a]=len(set(s)&gold)/len(gold)
    per.append(row)
    if n%150==0: print(f"  {n}/{len(rows)}", flush=True)

M=len(per)
multi=[x for x in per if x["multi"]]
def mean(rows_,k): return 100*sum(x[k] for x in rows_)/len(rows_)
rnd=random.Random(SEED)
def ci(rows_,ka,kb):
    L=len(rows_); ds=[]
    for _ in range(BOOT):
        s=[rows_[rnd.randrange(L)] for _ in range(L)]
        ds.append(100*(sum(x[ka] for x in s)-sum(x[kb] for x in s))/L)
    ds.sort(); return round(ds[int(.025*BOOT)],2), round(ds[int(.975*BOOT)],2)

print(f"\ncozumlenen: {M} (coklu-gold {len(multi)})")
print(f"\n=== TUM SORGULAR (n={M}) — FR@3 ===")
print(f"{'kol':12s} {'FR@3':>7s} {'tabandan':>9s} {'CI95':>20s}")
res={"n":M,"n_multi":len(multi),"model_calls":0,"all":{},"multi_gold":{}}
for a in ARMS:
    v=mean(per,a)
    if a=="base": print(f"{a:12s} {v:>7.2f}"); res["all"][a]={"fr3":round(v,2)}; continue
    d=v-mean(per,"base"); lo,hi=ci(per,a,"base")
    sig="SIG" if not(lo<=0<=hi) else "-"
    res["all"][a]={"fr3":round(v,2),"delta":round(d,2),"ci95":[lo,hi],"significant":sig=="SIG"}
    print(f"{a:12s} {v:>7.2f} {d:>+9.2f}  [{lo:+.2f},{hi:+.2f}] {sig}")

print(f"\n=== COKLU-GOLD ALTKUME (n={len(multi)}) — mekanizmanin hedefi ===")
for a in ARMS:
    v=mean(multi,a)
    if a=="base": print(f"{a:12s} {v:>7.2f}"); res["multi_gold"][a]={"fr3":round(v,2)}; continue
    d=v-mean(multi,"base"); lo,hi=ci(multi,a,"base")
    sig="SIG" if not(lo<=0<=hi) else "-"
    res["multi_gold"][a]={"fr3":round(v,2),"delta":round(d,2),"ci95":[lo,hi],"significant":sig=="SIG"}
    print(f"{a:12s} {v:>7.2f} {d:>+9.2f}  [{lo:+.2f},{hi:+.2f}] {sig}")

best=max([a for a in ARMS if a!="base"], key=lambda a: res["all"][a]["fr3"])
res["best_arm_all"]=best
res["per_query"]=per
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nen iyi kol (tum): {best} = {res['all'][best]['fr3']} (taban {res['all']['base']['fr3']})")
print(f"kayit: {OUT.name}")
