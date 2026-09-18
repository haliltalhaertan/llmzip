"""UCUZ KODLAYICI ADAYLARI: sorguyu 96-bit koda en ucuz nasil ceviririz?

L-116 ayrimi: 12 baytlik KODLAR basarili (5.7 KB, 0.103 ms tarama, BM25'ten 4.6x hizli).
TF-IDF/SVD KODLAYICI basarisiz (5.1 MB, 2.85 ms). Hedef: kodlayiciyi ~100 KB / ~0.2 ms'e
indirip KALITEYI korumak.

KRITIK: kodlayici degisirse BELGE KODLARI da degisir. Dolayisiyla her aday icin
kalite UCTAN UCA yeniden olculur -- yalniz hiz/RAM degil. Yoksa "ucuz ama ise yaramaz"
bir kodlayiciyi basari sanariz.

ADAYLAR:
  A. tfidf_svd     : mevcut yontem (yeniden kuruldu) -- referans
  B. hashing_rp    : HashingVectorizer (SOZLUKSUZ) + sabit rastgele izdusum
  C. hash_direct   : kelime -> 96 bite dogrudan karma, hicbir egitim yok (SIFIR parametre)
  D. shared_svd    : TUM arsivlerde bir kez egitilmis ortak TF-IDF+SVD (amortisman)
  E. hashing_rp_idf: B + global IDF agirligi (kucuk sabit tablo)

OLCULEN: kodlayici RAM, sorgu kodlama ms, tarama ms, Hit@10, FR@3 (rerank YOK -- ham getirim)
Cikti: CHEAP_ENCODER.json
"""
import json, pickle, re, math, time, sys, gc, hashlib
import numpy as np
from collections import Counter
from pathlib import Path

W=Path("C:/Users/MDP/dev/llmzip-work")
CKPT=W/"_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM=W/"regen/lme/items"
OUT =W/"audit_hard_r4/CHEAP_ENCODER.json"
N_ARCH=int(sys.argv[1]) if len(sys.argv)>1 else 60
K, REPS, SEED = 96, 5, 20260918
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

from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer
from sklearn.decomposition import TruncatedSVD

rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows+=[json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
rows=rows[:N_ARCH]

# ---- veri yukle
ARCH=[]
for r in rows:
    qid=r["qid"]
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    N=c["C"].shape[0]
    sess=item["haystack_sessions"]
    flat=[m for s in sess for m in s] if isinstance(sess[0],list) else sess
    if len(flat)!=N: continue
    ARCH.append({"qid":qid,"texts":[text_of(m) for m in flat],
                 "q":item["question"],"gold":set(int(g) for g in c["gold"])})
print(f"arsiv {len(ARCH)} | k={K} | tekrar {REPS}", flush=True)

# ---- D icin ortak kodlayici: TUM arsivlerin metinlerinde BIR KEZ egitilir
t0=time.perf_counter()
allt=[t for a in ARCH for t in a["texts"]]
shared_vec=TfidfVectorizer(stop_words=list(STOP), token_pattern=r"\b\w\w+\b", max_features=20000)
Xs=shared_vec.fit_transform(allt)
shared_svd=TruncatedSVD(n_components=K, random_state=0).fit(Xs)
shared_build=time.perf_counter()-t0
shared_ram=deep(shared_vec.vocabulary_)+shared_svd.components_.nbytes
print(f"ortak kodlayici: {shared_build:.1f}s kurma, {shared_ram/1024:.0f} KB", flush=True)

# ---- E icin global IDF (kucuk sabit tablo, en sik 20k kelime)
gdf=Counter()
for t in allt: gdf.update(set(tok(t)))
NT=len(allt)
GIDF={w: math.log(1+(NT-c+0.5)/(c+0.5)) for w,c in gdf.most_common(20000)}
gidf_ram=deep(GIDF)

rng=np.random.default_rng(SEED)
NB=2**18                                   # hashing boyutu
RP=rng.standard_normal((K, 256)).astype(np.float32)   # kucuk izdusum (B/E icin)
rp_ram=RP.nbytes

def hash_feats(text, dim=256):
    """SOZLUKSUZ: kelime -> sabit karma kova, agirlik 1"""
    v=np.zeros(dim, dtype=np.float32)
    for w in tok(text):
        h=int.from_bytes(hashlib.blake2b(w.encode(),digest_size=4).digest(),"little")
        v[h%dim]+= 1.0 if (h>>31)&1 else -1.0
    n=np.linalg.norm(v)
    return v/n if n>0 else v

def hash_feats_idf(text, dim=256):
    v=np.zeros(dim, dtype=np.float32)
    for w in tok(text):
        h=int.from_bytes(hashlib.blake2b(w.encode(),digest_size=4).digest(),"little")
        v[h%dim]+= (1.0 if (h>>31)&1 else -1.0)*GIDF.get(w,1.0)
    n=np.linalg.norm(v)
    return v/n if n>0 else v

def hash_direct(text):
    """SIFIR parametre: her kelime dogrudan bir bite oy verir"""
    v=np.zeros(K, dtype=np.float32)
    for w in tok(text):
        h=int.from_bytes(hashlib.blake2b(w.encode(),digest_size=4).digest(),"little")
        v[h%K]+= 1.0 if (h>>31)&1 else -1.0
    return v

def hit_fr3(codes, qbits, gold):
    d=np.unpackbits(np.bitwise_xor(codes,qbits),axis=1).sum(1)
    o=np.argsort(d,kind="stable")
    return (1.0 if set(map(int,o[:10]))&gold else 0.0,
            len(set(map(int,o[:3]))&gold)/len(gold))

ARMS=["tfidf_svd","hashing_rp","hash_direct","shared_svd","hashing_rp_idf"]
acc={a:{"hit":[],"fr3":[],"enc_ram":[],"enc_ms":[],"scan_ms":[],"build_s":[]} for a in ARMS}

for n,a in enumerate(ARCH,1):
    texts,qq,gold=a["texts"],a["q"],a["gold"]
    N=len(texts)
    for arm in ARMS:
        gc.collect(); t0=time.perf_counter()
        if arm=="tfidf_svd":
            vec=TfidfVectorizer(stop_words=list(STOP), token_pattern=r"\b\w\w+\b")
            X=vec.fit_transform(texts); k=min(K,max(2,min(X.shape)-1))
            svd=TruncatedSVD(n_components=k,random_state=0); Z=svd.fit_transform(X)
            build=time.perf_counter()-t0
            eram=deep(vec.vocabulary_)+svd.components_.nbytes
            enc=lambda s: svd.transform(vec.transform([s]))[0]
        elif arm=="shared_svd":
            Z=shared_svd.transform(shared_vec.transform(texts))
            build=time.perf_counter()-t0            # arsiv basina EK kurma (kodlayici hazir)
            eram=shared_ram/len(ARCH)               # amortize
            enc=lambda s: shared_svd.transform(shared_vec.transform([s]))[0]
        elif arm=="hashing_rp":
            H=np.stack([hash_feats(t) for t in texts]); Z=H@RP.T
            build=time.perf_counter()-t0; eram=rp_ram
            enc=lambda s: hash_feats(s)@RP.T
        elif arm=="hashing_rp_idf":
            H=np.stack([hash_feats_idf(t) for t in texts]); Z=H@RP.T
            build=time.perf_counter()-t0; eram=rp_ram+gidf_ram
            enc=lambda s: hash_feats_idf(s)@RP.T
        else:  # hash_direct
            Z=np.stack([hash_direct(t) for t in texts])
            build=time.perf_counter()-t0; eram=0
            enc=hash_direct
        if Z.shape[1]<K: Z=np.pad(Z,((0,0),(0,K-Z.shape[1])))
        codes=np.packbits(Z[:,:K]>0,axis=1)

        z=enc(qq); t0=time.perf_counter()
        for _ in range(REPS): z=enc(qq)
        enc_ms=1000*(time.perf_counter()-t0)/REPS
        if len(z)<K: z=np.pad(z,(0,K-len(z)))
        qb=np.packbits(z[:K]>0)
        t0=time.perf_counter()
        for _ in range(REPS): hit_fr3(codes,qb,gold)
        scan_ms=1000*(time.perf_counter()-t0)/REPS
        h,f=hit_fr3(codes,qb,gold)
        acc[arm]["hit"].append(h); acc[arm]["fr3"].append(f)
        acc[arm]["enc_ram"].append(eram); acc[arm]["enc_ms"].append(enc_ms)
        acc[arm]["scan_ms"].append(scan_ms); acc[arm]["build_s"].append(build)
    if n%15==0: print(f"  {n}/{len(ARCH)}", flush=True)

res={"n_archives":len(ARCH),"k":K,"model_calls":0,
 "note":("quality is re-measured END TO END for every candidate, because changing the encoder "
         "changes the DOCUMENT codes too. Raw retrieval, no reranking."),
 "bm25_reference":{"ram_kb":2600.7,"query_ms":0.471,"source":"SYSTEM_COST.json / L-116"},
 "arms":{}}
print(f"\n{'kol':16s} {'Hit@10':>7s} {'FR@3':>7s} {'enc KB':>9s} {'enc ms':>7s} {'scan ms':>8s} {'toplam ms':>10s}")
for arm in ARMS:
    d=acc[arm]
    e=float(np.median(d["enc_ram"]))/1024; em=float(np.median(d["enc_ms"]))
    sm=float(np.median(d["scan_ms"]))
    res["arms"][arm]={"hit10":round(100*np.mean(d["hit"]),2),"fr3":round(100*np.mean(d["fr3"]),2),
      "encoder_kb":round(e,1),"encode_ms":round(em,3),"scan_ms":round(sm,3),
      "total_query_ms":round(em+sm,3),"build_s":round(float(np.median(d["build_s"])),4)}
    print(f"{arm:16s} {100*np.mean(d['hit']):>7.2f} {100*np.mean(d['fr3']):>7.2f} "
          f"{e:>9.1f} {em:>7.3f} {sm:>8.3f} {em+sm:>10.3f}")
OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nBM25 referans: 2600.7 KB / 0.471 ms")
print(f"kayit: {OUT.name}")
