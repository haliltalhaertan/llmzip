"""BYTES probe P1: per-archive pipeline component sizes (READ-ONLY sources).
Rebuilds ONE small archive (RT05, 410 docs) through frozen path at k=96/192/384
and measures every object needed at query time. Writes JSON to THIS dir only.
"""
import importlib.util, json, os, sys, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.stdout.reconfigure(line_buffering=True)
ML = "/home/mdp/muse-work/ml-python"
print("run with ~/muse-work/ml-python P1_pipeline_sizes.py", flush=True)
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
frozen = _load("frozen", f"{W}/drive/v52_t4d_locomo_frozen_cross_benchmark.py")
RT = f"{W}/top10_comparison_r1/data"

def measure(archive="RT05", k=96):
    D = json.load(open(f"{RT}/{archive}.json", encoding="utf-8"))
    texts = [d["text"] for d in D["docs"]]
    N = len(texts)
    payload = frozen.fit_input_payload(list(texts))
    wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
    Vw = int(Xw.shape[1]); Vc = int(Xc.shape[1]); d = int(Xl.shape[1])
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    Ddim = int(Z.shape[1])
    kk = min(k, min(Z.shape)-1)
    s96 = TruncatedSVD(n_components=kk, random_state=frozen.SVD_SEED)
    Y = normalize(s96.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    C = (Y - mu).astype(np.float64)
    sigma = C.std(axis=0, ddof=0)
    # sizes
    comp96 = np.asarray(s96.components_)  # kk x Ddim
    compSV = np.asarray(sv.components_)   # d x Vw
    out = {
        "archive": archive, "k_requested": k, "k_eff": kk, "N_docs": N,
        "V_word": Vw, "V_char": Vc, "d_lsa": d, "D_mixed": Ddim,
        "s96_components_shape": list(comp96.shape),
        "s96_components_nbytes_f64": int(comp96.nbytes),
        "s96_components_nbytes_f32": int(comp96.size*4),
        "sv_components_shape": list(compSV.shape),
        "sv_components_nbytes_f64": int(compSV.nbytes),
        "sv_components_nbytes_f32": int(compSV.size*4),
        "mu_shape": list(mu.shape), "mu_nbytes_f64": int(mu.nbytes), "mu_nbytes_f32": int(mu.size*4),
        "sigma_nbytes_f64": int(sigma.nbytes), "sigma_nbytes_f32": int(sigma.size*4),
        "packed_bits_per_doc": kk/8, "packed_total": int(N*kk/8),
        "word_vocab": int(len(wv.vocabulary_)),
        "char_vocab": int(len(cv.vocabulary_)),
        "word_idf_nbytes_f64": int(np.asarray(wv.idf_).nbytes),
        "char_idf_nbytes_f64": int(np.asarray(cv.idf_).nbytes),
        "itq_R_nbytes_f64": int(kk*kk*8), "itq_R_nbytes_f32": int(kk*kk*4),
        "Z_shape": list(Z.shape),
    }
    # vocab term-byte estimate (utf-8 term bytes + 1 sep + varint df + 4B idf like cost_audit compact per-term overhead)
    w_terms = sum(len(t.encode("utf-8")) for t in wv.vocabulary_.keys())
    c_terms = sum(len(t.encode("utf-8")) for t in cv.vocabulary_.keys())
    out["word_terms_utf8"] = int(w_terms); out["char_terms_utf8"] = int(c_terms)
    return out

res = {}
for k in (96, 192, 384):
    print(f"building RT05 k={k} ...", flush=True)
    res[f"RT05_k{k}"] = measure("RT05", k)
    print(json.dumps(res[f"RT05_k{k}"], indent=1), flush=True)
json.dump(res, open(os.path.join(HERE, "P1_pipeline_sizes.json"), "w"), indent=1)
print("WROTE P1_pipeline_sizes.json", flush=True)
