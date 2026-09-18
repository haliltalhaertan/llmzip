# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BAGIMSIZ DENETIM re-fit betigi #1: kapi + spektrum + budama.

Dondurulmus uretim yapitinin geri kazanimi DEGILDIR; gercek derlem uzerinde
temsil hattinin bagimsiz yeniden uyarlanmasidir. Task4F1 muhru: gold/evidence
acilmaz, recall/dogruluk/siralama/benchmark yok; yalnizca temsilin tanimlayici
istatistikleri. Bu betik 'question'/'answer'/has_answer alanlarini HIC okumaz;
adapterin build_archive islevini CAGIRMAZ (etiket okudugu icin).
"""
import csv, importlib.util, json, os, sys
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

def load_adapter(path):
    spec = importlib.util.spec_from_file_location("audit_ad", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def my_texts(item):
    # Bagimsiz yazim: ayni semantics (tarih/rol/icerik), etiket yok.
    out = []
    sids = item["haystack_session_ids"]; dates = item["haystack_dates"]
    sessions = item["haystack_sessions"]
    for sid, date, sess in zip(sids, dates, sessions):
        if type(sess) is not list:
            continue
        for ti in range(len(sess)):
            turn = sess[ti]
            if type(turn) is not dict:
                continue
            r = turn.get("role")
            c = turn.get("content")
            if type(c) is not str:
                c = "" if c is None else str(c)
            out.append("[" + str(date) + "] " + str(r) + ": " + c)
    return out

def my_loglog(values):
    # polyfit KULLANMAZ: kapali-form en-kucuk-kareler, ln v = a - p ln i.
    v = np.array([float(x) for x in values], dtype=np.float64)
    idx = np.arange(1, len(v) + 1, dtype=np.float64)
    keep = v > 0
    v = v[keep]; idx = idx[keep]
    x = np.log(idx); y = np.log(v)
    xm = x.mean(); ym = y.mean()
    slope = float(((x - xm) * (y - ym)).sum() / ((x - xm) ** 2).sum())
    icept = float(ym - slope * xm)
    yh = slope * x + icept
    ss_res = float(((y - yh) ** 2).sum()); ss_tot = float(((y - ym) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return -slope, r2

def main():
    ad = load_adapter(ADAPTER)
    frozen = list(csv.DictReader(open(GEOM, encoding="utf-8")))
    print("frozen rows:", len(frozen), flush=True)
    # Kimlik: 32 + word + char == combined tum satirlarda mi?
    bad = 0
    for r in frozen:
        if 32 + int(r["word_columns"]) + int(r["char_columns"]) != int(r["combined_columns"]):
            bad += 1
            if bad < 5:
                print("KIMLIK BOZUK:", r["question_id"], r["word_columns"], r["char_columns"], r["combined_columns"], flush=True)
    print(f"kimlik 32+w+c==combined: {len(frozen)-bad}/{len(frozen)} tutuyor", flush=True)
    data = json.load(open(CORPUS, encoding="utf-8"))
    by_id = {str(x["question_id"]): x for x in data}
    print("corpus:", len(data), flush=True)

    # KAPI: paketin 15'i + GORULMEMIS arsivler (16-25 + orta + son).
    extra_idx = list(range(15, 25)) + [100, 200, 300, 400, 460, 469]
    test_rows = frozen[:15] + [frozen[i] for i in extra_idx]
    gate_all = True
    for row in test_rows:
        qid = row["question_id"]
        tx = my_texts(by_id[qid])
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(tx)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        exp = (int(row["N_archive"]), int(row["word_columns"]), int(row["char_columns"]), int(row["combined_columns"]))
        got = (int(Z.shape[0]), int(Xw.shape[1]), int(Xc.shape[1]), int(Z.shape[1]))
        ok = exp == got
        gate_all &= ok
        tag = "PAKET" if row in frozen[:15] else "YENI "
        print(f"KAPI-{tag} {qid}: exp={exp} got={got} -> {'GECTI' if ok else 'KALDI'} d_lex={int(sv.components_.shape[0])}", flush=True)
    print("KAPI GENEL:", "GECTI" if gate_all else "KALDI", flush=True)

    # SPEKTRUM: paketin icinden 3 arsivde bagimsiz fit + bagimsiz regresyon.
    for qid in [frozen[0]["question_id"], frozen[7]["question_id"], frozen[14]["question_id"]]:
        tx = my_texts(by_id[qid])
        wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(tx)
        Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
        s96 = TruncatedSVD(n_components=96, random_state=5204)
        Y = normalize(s96.fit_transform(Z))
        mu = Y.mean(0, keepdims=True)
        C = (Y - mu).astype(np.float64)
        sigma = np.asarray(s96.singular_values_, dtype=np.float64)
        pA, r2A = my_loglog(sigma)
        f12A = float((sigma[:12] ** 2).sum() / (sigma ** 2).sum())
        varC = np.var(C, axis=0)
        pB, r2B = my_loglog(varC)
        f12B = float(varC[:12].sum() / varC.sum())
        occ = np.mean(C >= 0, axis=0)
        n45 = int(np.sum((occ < 0.45) | (occ > 0.55)))
        n30 = int(np.sum((occ < 0.30) | (occ > 0.70)))
        # Budama: kumulatif varyans (SIRALI ilk-k, rapordaki gibi).
        tot = float(varC.sum())
        cums = {k: float(varC[:k].sum() / tot) for k in (8, 12, 16, 24, 32, 48, 64, 96)}
        tail32 = float(varC[64:].sum() / tot)
        v96_o_v64 = float(varC[95] / varC[63])
        print(f"SPEK {qid}: pA={pA:.6f} R2A={r2A:.6f} f12A={f12A:.6f} | pB={pB:.6f} R2B={r2B:.6f} f12B={f12B:.6f} | dis45={n45} dis30={n30}", flush=True)
        print(f"  BUDAMA {qid}: " + " ".join(f"k{k}={cums[k]:.6f}" for k in (8,12,16,24,32,48,64,96)) + f" tail32={tail32:.6f} v96/v64={v96_o_v64:.6f}", flush=True)

if __name__ == "__main__":
    main()
