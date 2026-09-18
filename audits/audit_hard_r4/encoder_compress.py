"""ENCODER SIKISTIRMA: A) int8+pruning  B) sparse hyperplanes  C) learned codebook

L-117 bulgusu: rastgele izdusum/karma/ortak-SVD basarisiz cunku SVD'nin OGRENDIGI
GEOMETRIDEN VAZGECIYORLAR. Bu betik tersini yapar: ayni geometriyi koruyup yalniz
TEMSILINI sikistirir.

BASARI KRITERI -- DENEY ONCESI DONDURULDU (dis degerlendirme formulasyonu):
  1. Hit@10, ayni kohortta tfidf_svd'nin en fazla 3 puan altinda
  2. kodlayici RAM <= 100 KB
  3. sorgu kodlama <= 0.25 ms
  UCU BIRDEN saglanmazsa yontem hedefi COZMUYOR. Kismi basari "basari" diye yazilmaz.

ONEMLI: kodlayici degisince BELGE KODLARI da degisir -> kalite UCTAN UCA olculur.
Ayrica bit-flip orani ayri raporlanir (ara metrik; L-112'de ara metrigin nihai
metrikle isaret olarak celisebildigi olculdu, o yuzden karar metrigi Hit@10).

Cikti: ENCODER_COMPRESS.json
"""
import json, pickle, re, math, time, sys, gc
import numpy as np
from collections import Counter
from pathlib import Path

W=Path("C:/Users/MDP/dev/llmzip-work")
CKPT=W/"_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM=W/"regen/lme/items"
OUT =W/"audit_hard_r4/ENCODER_COMPRESS.json"
N_ARCH=int(sys.argv[1]) if len(sys.argv)>1 else 60
K, REPS, SEED = 96, 5, 20260918
CRIT={"max_hit10_drop_pp":3.0,"max_encoder_kb":100.0,"max_encode_ms":0.25}
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]
def deep(o,seen=None):
    if seen is None: seen=set()
    i=id(o)
    if i in seen: return 0
    seen.add(i); s=sys.getsizeof(o)
    if isinstance(o,dict):
        for k,v in o.items(): s+=deep(k,seen)+deep(v,seen)
    elif isinstance(o,(list,tuple,set)):
        for v in o: s+=deep(v,seen)
    elif isinstance(o,np.ndarray): s=o.nbytes
    return s

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows+=[json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
ARCH=[]
for r in rows[:N_ARCH]:
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    N=c["C"].shape[0]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=N: continue
    ARCH.append({"qid":qid,"texts":[text_of(m) for m in flat],
                 "q":item["question"],"gold":set(int(g) for g in c["gold"])})
print(f"arsiv {len(ARCH)} | kriter: Hit@10 >= taban-3, RAM <= 100 KB, kodlama <= 0.25 ms", flush=True)

def evaluate(Zdocs, zq, gold):
    if Zdocs.shape[1]<K: Zdocs=np.pad(Zdocs,((0,0),(0,K-Zdocs.shape[1])))
    if len(zq)<K: zq=np.pad(zq,(0,K-len(zq)))
    codes=np.packbits(Zdocs[:,:K]>0,axis=1); qb=np.packbits(zq[:K]>0)
    d=np.unpackbits(np.bitwise_xor(codes,qb),axis=1).sum(1)
    o=np.argsort(d,kind="stable")
    return (1.0 if set(map(int,o[:10]))&gold else 0.0,
            len(set(map(int,o[:3]))&gold)/len(gold), codes)

ARMS=["baseline_tfidf_svd","A_int8","A_int8_prune50","A_int8_prune90","A_int8_prune95",
      "B_sparse32","B_sparse64","B_sparse128","C_codebook256","C_codebook512","BC_hybrid"]
acc={a:{"hit":[],"fr3":[],"ram":[],"enc_ms":[],"flip":[]} for a in ARMS}

for n,a in enumerate(ARCH,1):
    texts,qq,gold=a["texts"],a["q"],a["gold"]
    vec=TfidfVectorizer(stop_words=list(STOP), token_pattern=r"\b\w\w+\b")
    X=vec.fit_transform(texts); k=min(K,max(2,min(X.shape)-1))
    svd=TruncatedSVD(n_components=k,random_state=0); Z0=svd.fit_transform(X)
    Wm=svd.components_.astype(np.float32)          # (k, V) -- ogrenilen geometri
    V=Wm.shape[1]
    xq=np.asarray(vec.transform([qq]).todense()).ravel().astype(np.float32)
    Xd=np.asarray(X.todense()).astype(np.float32)
    base_ram=deep(vec.vocabulary_)+Wm.nbytes
    t0=time.perf_counter()
    for _ in range(REPS): svd.transform(vec.transform([qq]))
    base_ms=1000*(time.perf_counter()-t0)/REPS
    h,f,c0=evaluate(Z0,Z0.mean(0)*0+ (xq@Wm.T), gold)   # taban: gercek projeksiyon
    zq0=xq@Wm.T
    h,f,c0=evaluate(Xd@Wm.T, zq0, gold)
    acc["baseline_tfidf_svd"]["hit"].append(h); acc["baseline_tfidf_svd"]["fr3"].append(f)
    acc["baseline_tfidf_svd"]["ram"].append(base_ram); acc["baseline_tfidf_svd"]["enc_ms"].append(base_ms)
    acc["baseline_tfidf_svd"]["flip"].append(0.0)

    voc_ram=deep(vec.vocabulary_)                  # sozluk her kolda gerekli
    def record(name, Wc, extra_ram=0, dense=True):
        t=time.perf_counter()
        for _ in range(REPS): z=xq@Wc.T
        ms=1000*(time.perf_counter()-t)/REPS
        Zd=Xd@Wc.T; z=xq@Wc.T
        hh,ff,cc=evaluate(Zd,z,gold)
        flip=float(np.mean(np.unpackbits(np.bitwise_xor(c0,cc),axis=1).sum(1))/K)
        ram=voc_ram+ (Wc.nbytes if dense else 0) + extra_ram
        acc[name]["hit"].append(hh); acc[name]["fr3"].append(ff)
        acc[name]["ram"].append(ram); acc[name]["enc_ms"].append(ms); acc[name]["flip"].append(flip)

    # ---- A: int8 kuantizasyon + budama
    sc=np.abs(Wm).max()/127.0
    W8=(np.round(Wm/sc).astype(np.int8).astype(np.float32))*sc
    record("A_int8", W8)
    for p,nm in [(50,"A_int8_prune50"),(90,"A_int8_prune90"),(95,"A_int8_prune95")]:
        thr=np.percentile(np.abs(W8),p); Wp=np.where(np.abs(W8)>=thr,W8,0.0).astype(np.float32)
        nz=int((Wp!=0).sum())
        record(nm, Wp, extra_ram=nz*(1+4)-Wp.nbytes, dense=True)   # seyrek: deger+indeks

    # ---- B: bit basina seyrek hiperduzlem (en buyuk |agirlik| terimleri tut)
    for s,nm in [(32,"B_sparse32"),(64,"B_sparse64"),(128,"B_sparse128")]:
        Ws=np.zeros_like(Wm)
        for j in range(Wm.shape[0]):
            idx=np.argpartition(-np.abs(Wm[j]), min(s,V-1))[:s]
            Ws[j,idx]=Wm[j,idx]
        nz=int((Ws!=0).sum())
        record(nm, Ws, extra_ram=nz*(1+4)-Ws.nbytes)

    # ---- C: ogrenilmis kelime kod kitabi (SVD satirlarini kumele)
    rowsW=Wm.T                                     # (V, k) her kelimenin vektoru
    for nc,nm in [(256,"C_codebook256"),(512,"C_codebook512")]:
        ncl=min(nc, max(2, rowsW.shape[0]//2))
        km=KMeans(n_clusters=ncl,n_init=3,random_state=0,max_iter=50).fit(rowsW)
        Wc=km.cluster_centers_[km.labels_].T.astype(np.float32)
        # RAM: kelime->prototip (1-2 bayt) + prototipler int8
        pid=V*(1 if ncl<=256 else 2)
        proto=ncl*k                                 # int8
        record(nm, Wc, extra_ram=pid+proto-Wc.nbytes)

    # ---- B+C birlesimi: kod kitabi + bit basina seyrek duzeltme
    ncl=min(256, max(2, rowsW.shape[0]//2))
    km=KMeans(n_clusters=ncl,n_init=3,random_state=0,max_iter=50).fit(rowsW)
    Wc=km.cluster_centers_[km.labels_].T.astype(np.float32)
    R=Wm-Wc
    Wh=Wc.copy()
    for j in range(Wm.shape[0]):
        idx=np.argpartition(-np.abs(R[j]), min(32,V-1))[:32]
        Wh[j,idx]=Wm[j,idx]
    record("BC_hybrid", Wh, extra_ram=V*1+ncl*k+96*32*(1+4)-Wh.nbytes)
    if n%15==0: print(f"  {n}/{len(ARCH)}", flush=True)

base_hit=100*np.mean(acc["baseline_tfidf_svd"]["hit"])
res={"n_archives":len(ARCH),"k":K,"model_calls":0,"criteria_frozen_before_run":CRIT,
 "note":("criteria were frozen before the run. Quality measured END TO END because changing the "
         "encoder changes document codes. bit_flip is an intermediate metric, reported but not "
         "the decision metric (L-112 showed intermediate metrics can disagree in sign)."),
 "arms":{}}
print(f"\n{'kol':20s} {'Hit@10':>7s} {'fark':>6s} {'FR@3':>6s} {'RAM KB':>8s} {'ms':>6s} {'flip%':>6s} {'KRITER':>8s}")
for arm in ARMS:
    d=acc[arm]
    hit=100*np.mean(d["hit"]); fr=100*np.mean(d["fr3"])
    ram=float(np.median(d["ram"]))/1024; ms=float(np.median(d["enc_ms"]))
    flip=100*float(np.mean(d["flip"]))
    drop=base_hit-hit
    ok = (drop<=CRIT["max_hit10_drop_pp"] and ram<=CRIT["max_encoder_kb"] and ms<=CRIT["max_encode_ms"])
    res["arms"][arm]={"hit10":round(hit,2),"drop_pp":round(drop,2),"fr3":round(fr,2),
      "encoder_kb":round(ram,1),"encode_ms":round(ms,3),"bit_flip_pct":round(flip,2),
      "meets_all_criteria":bool(ok)}
    print(f"{arm:20s} {hit:>7.2f} {drop:>+6.2f} {fr:>6.2f} {ram:>8.1f} {ms:>6.3f} {flip:>6.2f} "
          f"{'GECTI' if ok else '-':>8s}")
passed=[a for a in ARMS if res["arms"][a]["meets_all_criteria"] and a!="baseline_tfidf_svd"]
res["arms_meeting_all_three"]=passed
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nUC KRITERI DE GECEN: {passed or '(hicbiri)'}")
print(f"kayit: {OUT.name}")
