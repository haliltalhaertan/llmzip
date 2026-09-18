"""ROUTER: sign96+Jev mi BM25+Jev mi? ORACLE TAVANI + GERCEK TAHMIN. SIFIR MODEL CAGRISI.

Sira dis degerlendirmenin onerdigi gibi:
  1. once oracle tavanini hesapla  -> yapildi: +5.95 pp ham, gurultu tabani +0.46 -> +5.49 gercek
  2. SONRA gercekten tahmin edilebilir mi diye bak   <- bu betik

DURUSTLUK KURALLARI (L-098'de geri cekilen post-selection hatasina karsi):
  - train/test AYRILIR, router YALNIZ train'den ogrenir
  - oracle ayni veride secilip "kazanc" diye sunulmaz
  - gurultu tabani cikarilir: ayni sistemin iki bagimsiz kosusu +0.46 pp sahte oracle veriyor
  - tek bolunme degil, 200 rastgele bolunme -> dagilim raporlanir (tek split = post-selection riski)

OZELLIKLER (hepsi runtime'da ucuz, gold kullanmaz):
  soru uzunlugu, sayi/tarih icerir mi, zamansal kelime, BM25 top1 skoru,
  BM25 top1-top2 farki, sign96 top1 skoru (negatif Hamming), sign96 top1-top2 farki,
  iki yontem ayni belgeyi mi buldu, top-10 ortusmesi, arsiv boyutu, sorgu terim sayisi

Cikti: ROUTER_PILOT.json
"""
import json, pickle, re, math, random
import numpy as np
from collections import Counter
from pathlib import Path

W=Path("C:/Users/MDP/dev/llmzip-work")
CKPT=W/"_wt_main/research_top10_comparison_2026_09_16/baseline"
ITEM=W/"regen/lme/items"
OUT =W/"audit_hard_r4/ROUTER_PILOT.json"
K1,B=1.2,0.75; SPLITS=200; SEED=20260918
FROZEN=re.compile(r"\b\w\w+\b")
STOP=set("""a an and are as at be by for from has have he in is it its of on that the to was were
will with i you my me we they this these those so but or if then there here what when where who how
not no yes do does did just about your our their her his them him she""".split())
TEMPORAL=set("""before after first last latest recent earlier later then when since until ago
initially originally finally previously now currently still yet already""".split())
def tok(s): return [t for t in FROZEN.findall(s.lower()) if t not in STOP]
def text_of(m): return (f"{m.get('role','')}: {m.get('content','')}"[:1200]) if isinstance(m,dict) else str(m)[:1200]

m=json.load(open(W/"audit_hard_r4/MATCHED_CI.json",encoding="utf-8"))
LAB={x["qid"]:(x["sign96_fr3"],x["bm25_fr3"]) for x in m["per_query"]}
rows=[]
for f in sorted(CKPT.glob("ckpt_top10_lme_*.jsonl")):
    rows+=[json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]

X=[];Y=[];QID=[];GAP=[]
print("ozellik cikariliyor...", flush=True)
for r in rows:
    qid=r["qid"]
    if qid not in LAB: continue
    item=json.load(open(ITEM/f"{qid}.json",encoding="utf-8"))
    c=pickle.load(open(W/f"regen/lme/cache_repr/{qid}.pkl","rb"))
    C,qC=c["C"],c["qC"]; N=C.shape[0]
    sess=item["haystack_sessions"]
    flat=[m2 for s in sess for m2 in s] if isinstance(sess[0],list) else sess
    if len(flat)!=N: continue
    texts=[text_of(x) for x in flat]
    D=[tok(x) for x in texts]; avg=sum(len(x) for x in D)/max(1,N)
    df=Counter()
    for x in D: df.update(set(x))
    idf={t: math.log(1+(N-k+0.5)/(k+0.5)) for t,k in df.items()}
    q=tok(item["question"]); ql=item["question"].lower()
    sc=np.zeros(N)
    for i,x in enumerate(D):
        tf,dl,s=Counter(x),len(x),0.0
        for t in q:
            if t in tf:
                f=tf[t]; s+=idf.get(t,0.0)*f*(K1+1)/(f+K1*(1-B+B*dl/max(1,avg)))
        sc[i]=s
    bo=np.argsort(-sc,kind="stable")
    sg=-((96-(np.sign(C)@np.sign(qC)))/2)
    so=np.argsort(-sg,kind="stable")
    b10=set(map(int,bo[:10])); s10=set(r["sign96"]["ids"])
    feats=[
      len(q),                                        # sorgu terim sayisi
      len(item["question"]),                         # karakter uzunlugu
      1.0 if re.search(r"\d",item["question"]) else 0.0,
      1.0 if (set(FROZEN.findall(ql)) & TEMPORAL) else 0.0,
      float(sc[bo[0]]),                              # BM25 top1 skoru
      float(sc[bo[0]]-sc[bo[1]]) if N>1 else 0.0,    # BM25 margin
      float(sg[so[0]]),                              # sign96 top1 skoru
      float(sg[so[0]]-sg[so[1]]) if N>1 else 0.0,    # sign96 margin
      1.0 if int(bo[0])==int(r["sign96"]["ids"][0]) else 0.0,   # ayni top1 mi
      len(b10&s10)/10.0,                             # top-10 ortusmesi
      math.log(N),                                   # arsiv boyutu
      float(np.mean(sc)), float(np.std(sc)),
    ]
    s_fr,b_fr=LAB[qid]
    X.append(feats); Y.append(1 if s_fr>b_fr else 0); QID.append(qid); GAP.append(s_fr-b_fr)
X=np.array(X); Y=np.array(Y); GAP=np.array(GAP); n=len(X)
print(f"sorgu: {n} | ozellik: {X.shape[1]}", flush=True)

sign_fr=np.array([LAB[q][0] for q in QID]); bm_fr=np.array([LAB[q][1] for q in QID])
always_s=100*sign_fr.mean(); always_b=100*bm_fr.mean()
oracle=100*np.maximum(sign_fr,bm_fr).mean()
print(f"\n=== TAVAN ===")
print(f"  hep sign96 {always_s:.2f} | hep BM25 {always_b:.2f} | ORACLE {oracle:.2f}")
print(f"  ham oracle kazanci : +{oracle-max(always_s,always_b):.2f} pp")
print(f"  gurultu tabani     : +0.46 pp (ayni sistemin iki kosusu, ayrica olculdu)")
print(f"  GERCEK tavan       : +{oracle-max(always_s,always_b)-0.46:.2f} pp")

# --- router: lojistik regresyon, 200 rastgele bolunme
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier
    HAVE=True
except ImportError:
    HAVE=False; print("\nsklearn YOK -> yalniz tavan raporlanir")

res={"n":n,"n_features":X.shape[1],"model_calls":0,
     "always_sign96":round(always_s,2),"always_bm25":round(always_b,2),
     "oracle":round(oracle,2),"oracle_gain_raw":round(oracle-max(always_s,always_b),2),
     "noise_floor_same_system":0.46,
     "oracle_gain_noise_adjusted":round(oracle-max(always_s,always_b)-0.46,2),
     "queries_where_methods_differ":int((np.abs(GAP)>1e-9).sum()),
     "label_balance":{"sign96_wins":int(Y.sum()),"bm25_wins_or_tie":int(n-Y.sum())}}

if HAVE:
    rng=random.Random(SEED)
    accs=[]; gains=[]; base_gains=[]
    for sp in range(SPLITS):
        idx=list(range(n)); rng.shuffle(idx)
        cut=int(0.7*n); tr,te=idx[:cut],idx[cut:]
        sca=StandardScaler().fit(X[tr])
        clf=LogisticRegression(max_iter=2000,C=1.0).fit(sca.transform(X[tr]),Y[tr])
        pred=clf.predict(sca.transform(X[te]))
        accs.append(float((pred==Y[te]).mean()))
        routed=np.where(pred==1, sign_fr[te], bm_fr[te])
        best_fixed=max(100*sign_fr[te].mean(),100*bm_fr[te].mean())
        gains.append(100*routed.mean()-best_fixed)
        base_gains.append(100*np.maximum(sign_fr[te],bm_fr[te]).mean()-best_fixed)
    accs=np.array(accs); gains=np.array(gains); base_gains=np.array(base_gains)
    res["router"]={"splits":SPLITS,"train_frac":0.7,
      "accuracy_mean":round(float(accs.mean()),4),"accuracy_sd":round(float(accs.std()),4),
      "gain_mean_pp":round(float(gains.mean()),3),"gain_sd_pp":round(float(gains.std()),3),
      "gain_p2.5":round(float(np.percentile(gains,2.5)),3),
      "gain_p97.5":round(float(np.percentile(gains,97.5)),3),
      "splits_with_positive_gain":int((gains>0).sum()),
      "test_oracle_gain_mean":round(float(base_gains.mean()),3)}
    print(f"\n=== ROUTER ({SPLITS} rastgele bolunme, %70 train / %30 test) ===")
    print(f"  dogruluk        : {accs.mean():.3f} +/- {accs.std():.3f}")
    print(f"  cogunluk taban  : {max(Y.mean(),1-Y.mean()):.3f}")
    print(f"  KAZANC          : {gains.mean():+.3f} pp  SD {gains.std():.3f}")
    print(f"    %95 araligi   : [{np.percentile(gains,2.5):+.3f}, {np.percentile(gains,97.5):+.3f}]")
    print(f"    pozitif cikan : {int((gains>0).sum())}/{SPLITS} bolunme")
    print(f"  test oracle     : {base_gains.mean():+.3f} pp (ayni test kumelerinde tavan)")
    frac=gains.mean()/base_gains.mean() if base_gains.mean() else 0
    res["router"]["fraction_of_oracle_captured"]=round(float(frac),3)
    print(f"  tavanin yakalanan kismi: %{100*frac:.1f}")

OUT.write_text(json.dumps(res,indent=1),encoding="utf-8")
print(f"\nkayit: {OUT.name}")
