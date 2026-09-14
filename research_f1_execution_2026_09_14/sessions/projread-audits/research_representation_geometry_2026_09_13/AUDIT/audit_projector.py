# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BAGIMSIZ DENETIM betigi #3: projektor envanteri + bayt yeniden-turetimi.

Dondurulmus probun sorgu yolundan (buildrep satir 110) BAGIMSIZ envanter:
hangi nesneler kalici olmali? Sonra 2 arsivde bayt hesabi + medyan dogrulama.
Task4F1: etiket yok, retrieval yok.
"""
import csv, importlib.util, inspect, json, os, struct, zlib
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

CORPUS = "/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json"
ADAPTER = "/mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py"
GEOM = "/mnt/c/Users/MDP/dev/llmzip/docs/v52/task4c2/V52_T4C2_feature_geometry.csv"
PB = "/home/mdp/muse-work/projector/out/PROJECTOR_BYTES.json"

def load_adapter(path):
    spec = importlib.util.spec_from_file_location("audit_ad3", path)
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

def main():
    # 1) TruncatedSVD.transform kaynagi: yalnizca components_ mi?
    src = inspect.getsource(TruncatedSVD.transform)
    print("SVD.transform kaynagi 'components_' geciyor:", "components_" in src, flush=True)
    print("--- transform kaynagi ---", flush=True)
    print(src, flush=True)
    # TfidfVectorizer.transform: vocabulary_ + idf_ disinda uydurulan ne kullanir?
    from sklearn.feature_extraction.text import TfidfVectorizer
    tsrc = inspect.getsource(TfidfVectorizer.transform)
    uses = {k: (k in tsrc) for k in ["vocabulary_", "idf_", "stop_words_", "fixed_vocabulary_"]}
    print("TFIDF.transform kullanim:", uses, flush=True)

    # 2) Bagimsiz bayt hesabi, 2 arsiv.
    ad = load_adapter(ADAPTER)
    frozen = list(csv.DictReader(open(GEOM, encoding="utf-8")))
    data = json.load(open(CORPUS, encoding="utf-8"))
    by_id = {str(x["question_id"]): x for x in data}
    mine = {}
    for row in frozen[:2]:
        qid = row["question_id"]
        tx = my_texts(by_id[qid])
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(tx)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        s96 = TruncatedSVD(n_components=96, random_state=5204)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        # vocab: index sirasi + uint32 + utf-8 (kendi kodum).
        def vbytes(vec):
            inv = sorted(vec.vocabulary_.items(), key=lambda kv: kv[1])
            raw = b"".join(struct.pack("<I", len(t.encode("utf-8"))) + t.encode("utf-8") for t, _ in inv)
            u8 = sum(len(t.encode("utf-8")) for t, _ in inv)
            return raw, u8, len(inv)
        wraw, wu8, wn = vbytes(wv); craw, cu8, cn = vbytes(cv)
        n32 = wv.idf_.size * 4 + cv.idf_.size * 4 + sv.components_.size * 4 + s96.components_.size * 4 + mu.size * 4
        tot_a = len(wraw) + len(craw) + n32
        n16 = wv.idf_.size * 2 + cv.idf_.size * 2 + sv.components_.size * 2 + s96.components_.size * 2 + mu.size * 2
        tot_b = len(wraw) + len(craw) + n16
        az = len(zlib.compress(wraw, 6)) + len(zlib.compress(craw, 6))
        for a in (wv.idf_, cv.idf_, sv.components_, s96.components_, mu.reshape(-1)):
            az += len(zlib.compress(np.asarray(a).astype(np.float32).tobytes(), 6))
        print(f"BAYT {qid}: N={Z.shape[0]} tot_a={tot_a} tot_b={tot_b} a_z={az} | s96.shape={tuple(s96.components_.shape)} sv.shape={tuple(sv.components_.shape)}", flush=True)
        mine[qid] = (tot_a, tot_b, az)
    # 3) Onlarin dosyasiyla karsilastir.
    theirs = json.load(open(PB, encoding="utf-8"))
    for p in theirs["per_archive"][:2]:
        q = p["question_id"]
        t = p["totals"]
        print(f"KARSILASTIR {q}: onlar a={t['a_raw_f32_struct']} b={t['b_raw_f16_struct']} az={t['a_zlib']} | benim a={mine[q][0]} b={mine[q][1]} az={mine[q][2]} | esit={t['a_raw_f32_struct']==mine[q][0] and t['b_raw_f16_struct']==mine[q][1] and t['a_zlib']==mine[q][2]}", flush=True)
    agg = theirs["aggregate"]
    print("ONLARIN medyan etkin(a-ham):", agg["ratios_median"]["a_raw"]["effective"], flush=True)
    print("ONLARIN medyan etkin/12 orani:", agg["ratios_median"]["a_raw"]["effective"] / 12, flush=True)
    print("ONLARIN breakeven a_raw:", agg["breakeven_median"]["a_raw"], flush=True)
    # 4) N dagilimi + d kimligi.
    Ns = [int(r["N_archive"]) for r in frozen]
    print(f"frozen N: min={min(Ns)} maks={max(Ns)} medyan={float(np.median(Ns))}", flush=True)
    print(f"kimlik ornegi 001be529: 32+39940+59943={32+39940+59943} (combined 99915)", flush=True)

if __name__ == "__main__":
    main()
