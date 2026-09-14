# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BAGIMSIZ DENETIM betigi #2: kapinin KORLESTIRDIGI varyantlar.

Soru: dort tamsayi eslesirken asagidaki istatistikleri degistiren maddi
farkli hatlar var mi? Task4F1: etiket yok, retrieval yok.
"""
import importlib.util, json, os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

CORPUS = "/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json"
ADAPTER = "/mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py"
QID = "001be529"

def load_adapter(path):
    spec = importlib.util.spec_from_file_location("audit_ad2", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def my_texts(item):
    out = []
    for sid, date, sess in zip(item["haystack_session_ids"], item["haystack_dates"], item["haystack_sessions"]):
        if type(sess) is not list:
            continue
        for turn in sess:
            if type(turn) is not dict:
                continue
            c = turn.get("content")
            if type(c) is not str:
                c = "" if c is None else str(c)
            out.append("[" + str(date) + "] " + str(turn.get("role")) + ": " + c)
    return out

def spec_of(Z, seed):
    s = TruncatedSVD(n_components=96, random_state=seed)
    Y = normalize(s.fit_transform(Z))
    mu = Y.mean(0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    sg = np.asarray(s.singular_values_, dtype=np.float64)
    v = np.var(C, axis=0)
    return sg, v, C

def main():
    ad = load_adapter(ADAPTER)
    data = json.load(open(CORPUS, encoding="utf-8"))
    by_id = {str(x["question_id"]): x for x in data}
    tx = my_texts(by_id[QID])
    wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(tx)
    Z0 = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    base_shape = (int(Z0.shape[0]), int(Xw.shape[1]), int(Xc.shape[1]), int(Z0.shape[1]))
    sg0, v0, C0 = spec_of(Z0, 5204)
    print(f"BAZ {QID}: sekil={base_shape} sg0[:3]={sg0[:3]} v0[:3]={v0[:3]}", flush=True)

    # (a) SVD tohumu: kapi sekle bakmaz bile (SVD kapidan SONRA).
    for seed in (0, 999, 5204):
        sg, v, C = spec_of(Z0, seed)
        dsg = float(np.max(np.abs(sg - sg0)))
        dv = float(np.max(np.abs(np.sort(v) - np.sort(v0))))
        print(f"VARYANT svd_seed={seed}: kapi-sekli AYNI (SVD sekli degistirmez); max|dsigma|={dsg:.3e} max|dvar_sorted|={dv:.3e}", flush=True)

    # (b) sublinear_tf=False: sutun sayisi ayni mi, degerler/istatistik degisir mi?
    wv2 = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english", sublinear_tf=False)
    cv2 = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=False)
    Xw2 = normalize(wv2.fit_transform(tx)); Xc2 = normalize(cv2.fit_transform(tx))
    from sklearn.decomposition import TruncatedSVD as TS
    d = min(32, Xw2.shape[0] - 1, Xw2.shape[1] - 1)
    sv2 = TS(n_components=d, random_state=5101)
    Xl2 = normalize(sv2.fit_transform(Xw2))
    Z2 = sparse.hstack([sparse.csr_matrix(Xl2), Xw2, Xc2], format="csr")
    shp2 = (int(Z2.shape[0]), int(Xw2.shape[1]), int(Xc2.shape[1]), int(Z2.shape[1]))
    print(f"VARYANT sublinear_tf=False: kapi-sekli={shp2} eslesme={shp2==base_shape} (degerler FARKLI, kapi KOR)", flush=True)
    sg2, v2, _ = spec_of(Z2, 5204)
    print(f"  etki: max|dsigma|={float(np.max(np.abs(sg2-sg0))):.4f} (olcekli), max|dvar|={float(np.max(np.abs(v2-v0))):.6f}", flush=True)

    # (c) hstack sira takasi: [Xw,Xc,Xl].
    Z3 = sparse.hstack([Xw, Xc, sparse.csr_matrix(Xl)], format="csr")
    shp3 = (int(Z3.shape[0]), int(Xw.shape[1]), int(Xc.shape[1]), int(Z3.shape[1]))
    sg3, v3, _ = spec_of(Z3, 5204)
    print(f"VARYANT hstack-sirasi [Xw,Xc,Xl]: kapi-sekli={shp3} eslesme={shp3==base_shape}; max|dsigma|={float(np.max(np.abs(sg3-sg0))):.3e}", flush=True)

    # (d) leksik SVD tohumu 5101 -> 777.
    sv4 = TS(n_components=d, random_state=777)
    Xl4 = normalize(sv4.fit_transform(Xw))
    Z4 = sparse.hstack([sparse.csr_matrix(Xl4), Xw, Xc], format="csr")
    sg4, v4, _ = spec_of(Z4, 5204)
    print(f"VARYANT lexseed=777: kapi-sekli AYNI; max|dsigma|={float(np.max(np.abs(sg4-sg0))):.4f}, max|dvar|={float(np.max(np.abs(v4-v0))):.6f}", flush=True)

    # (e) norm sirasi: normalize ETME (ham TF-IDF) — sutunlar ayni.
    Xw5 = wv.fit_transform(tx); Xc5 = cv.fit_transform(tx)
    print(f"VARYANT normsuz: kapi-sekli={(int(Xw5.shape[0]), int(Xw5.shape[1]), int(Xc5.shape[1]))} sutunlar AYNI (kapi deger gormez)", flush=True)

    # (f) Gercekten yakalanan: stop_words=None sutunlari degistirir mi?
    wv6 = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words=None, sublinear_tf=True)
    Xw6 = normalize(wv6.fit_transform(tx))
    print(f"VARYANT stop_words=None: word_sutun {int(Xw6.shape[1])} vs {int(Xw.shape[1])} -> kapi {'YAKALAR' if int(Xw6.shape[1])!=int(Xw.shape[1]) else 'KACIRIR'}", flush=True)

if __name__ == "__main__":
    main()
