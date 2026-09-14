# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""BAGIMSIZ DENETIM betigi #4: bag (ties) + rol (roles) yeniden-turetimi.

Kendi LOO Hamming kodum, kendi alt-orneklem tohumum, kendi bitisik-cift
mantigim. Task4F1: etiket yok, retrieval yok, dogruluk yok.
"""
import csv, importlib.util, json, os
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
    spec = importlib.util.spec_from_file_location("audit_ad4", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def my_texts_roles(item):
    tx, ro, ss, tt = [], [], [], []
    for si, (sid, date, sess) in enumerate(zip(item["haystack_session_ids"], item["haystack_dates"], item["haystack_sessions"])):
        if type(sess) is not list:
            continue
        for ti, turn in enumerate(sess):
            if type(turn) is not dict:
                continue
            c = turn.get("content")
            if type(c) is not str:
                c = "" if c is None else str(c)
            tx.append("[" + str(date) + "] " + str(turn.get("role")) + ": " + c)
            ro.append(turn.get("role")); ss.append(si); tt.append(ti)
    return tx, ro, np.array(ss), np.array(tt)

def fit_C(ad, tx):
    wv, cv, sv, Xw, Xc, Xl = ad.fit_archive_representation(tx)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s96 = TruncatedSVD(n_components=96, random_state=5204)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(0, keepdims=True)
    return (Y - mu).astype(np.float64)

def loo_bc(D):
    # Kendi LOO: oz-vektor cozumu, argsort ile d3.
    n = D.shape[0]
    X = D.astype(np.int8)
    bc = np.empty(n, dtype=int); d3v = np.empty(n, dtype=int)
    for p in range(n):
        dist = np.count_nonzero(X[p] != X, axis=1).astype(float)
        dist[p] = np.inf
        part = np.partition(dist, 3)
        d3 = int(part[3]) if False else int(np.sort(dist)[2])
        d3v[p] = d3
        bc[p] = int(np.sum(dist == d3))
    return bc, d3v

def rescore(C, bc, d3v):
    n = C.shape[0]
    B = np.where(C >= 0, 1.0, -1.0)
    X = (C >= 0).astype(np.int8)
    tied_slots = 0; distinct = 0; full = 0; tied_probes = 0
    for p in range(n):
        if bc[p] <= 1:
            continue
        tied_probes += 1
        dist = np.count_nonzero(X[p] != X, axis=1)
        dist[p] = 10 ** 9
        T = np.flatnonzero(dist == d3v[p])
        sc = C[p].astype(np.float64) @ B[T].T
        u = len(np.unique(sc))
        tied_slots += int(T.size); distinct += u
        full += int(u == T.size)
    return tied_probes, tied_slots, distinct, full

def main():
    ad = load_adapter(ADAPTER)
    frozen = list(csv.DictReader(open(GEOM, encoding="utf-8")))
    data = json.load(open(CORPUS, encoding="utf-8"))
    by_id = {str(x["question_id"]): x for x in data}
    ties = json.load(open("/home/mdp/muse-work/ties/out/TIES.json", encoding="utf-8"))
    roles = json.load(open("/home/mdp/muse-work/roles/out/ROLES.json", encoding="utf-8"))
    t_by = {p["question_id"]: p for p in ties["per_archive"]}
    r_by = {p["question_id"]: p for p in roles["per_archive"]}

    for qi in (0, 4):
        qid = frozen[qi]["question_id"]
        tx, ro, ss, tt = my_texts_roles(by_id[qid])
        C = fit_C(ad, tx)
        D = (C >= 0)
        # --- BAG ---
        bc, d3v = loo_bc(D)
        med = float(np.median(bc)); p90 = float(np.percentile(bc, 90)); mx = int(bc.max())
        f1 = float(np.mean(bc > 1)); f3 = float(np.mean(bc > 3))
        tb = t_by[qid]["hamming"]["boundary"]
        print(f"BAG {qid}: benim med={med:.0f} p90={p90:.1f} maks={mx} f>1={f1:.4f} f>3={f3:.4f} | onlar med={tb['median']:.0f} p90={tb['p90']:.1f} maks={tb['max']} f>1={tb['frac_gt1']:.4f} f>3={tb['frac_gt3']:.4f}", flush=True)
        # alt-ornekleme egilimi KENDI tohumumla (7777+qi).
        for ns in (50, 200):
            rng = np.random.default_rng(7777 + qi)
            idx = rng.choice(len(D), ns, replace=False)
            b2, _ = loo_bc(D[idx])
            print(f"  ALT {qid} N={ns}: med={float(np.median(b2)):.0f} f>1={float(np.mean(b2>1)):.3f}", flush=True)
        bfull_f1 = float(np.mean(bc > 1))
        print(f"  TAM {qid} N={len(D)}: med={med:.0f} f>1={bfull_f1:.3f} (yon: N buyuyunce bag {'AZALIYOR' if bfull_f1 < 0.5 else 'AZALMIYOR'})", flush=True)
        # yeniden-skorlama.
        tp, tsl, dsc, ful = rescore(C, bc, d3v)
        tc = t_by[qid]["continuous"]
        print(f"  SKOR {qid}: benim bagli-sonda={tp} slot={tsl} ayrik={dsc} tam={ful} | onlar sonda={tc['n_tied_probes']} slot={tc['total_tied_slots']} ayrik={tc['total_distinct_scores']}", flush=True)
        # --- ROL ---
        n = len(tx)
        H = np.count_nonzero(D[:, None, :] != D[None, :, :], axis=2)
        key = {(int(s), int(t)): i for i, (s, t) in enumerate(zip(ss.tolist(), tt.tolist()))}
        adj, oth = [], []
        for i in range(n):
            if ro[i] != "assistant":
                continue
            j = key.get((int(ss[i]), int(tt[i]) - 1))
            if j is None or ro[j] != "user":
                continue
            adj.append(int(H[i, j]))
            m = np.ones(n, bool); m[i] = False; m[j] = False
            oth.extend(H[i][m].tolist())
        adj = np.array(adj, float); oth = np.array(oth, float)
        ra = r_by[qid]["adjacent"]
        print(f"ROL {qid}: benim bitisik-med={float(np.median(adj)):.1f} diger-med={float(np.median(oth)):.1f} fark={float(np.median(oth)-np.median(adj)):.1f} | onlar bitisik={ra['hamming_adjacent']['median']} diger={ra['hamming_all_other']['median']}", flush=True)
        # yakin-kopya sayimi (esik <=16).
        iu = np.triu_indices(n, k=1)
        allh = H[iu]
        print(f"  KOPYA {qid}: cift={int(allh.size)} <=16: {int((allh<=16).sum())} (oran {float(np.mean(allh<=16)):.6f}) | onlar: {r_by[qid]['duplication']['thresholds']['16']}", flush=True)

if __name__ == "__main__":
    main()
