"""P2: per-archive vocab/D dims for ALL 10 RT archives (no big SVD; vectorizer fit only).
READ-ONLY sources. Writes P2_vocab_dims.json in THIS dir."""
import importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
frozen = _load("frozen", f"{W}/drive/v52_t4d_locomo_frozen_cross_benchmark.py")
RT = f"{W}/top10_comparison_r1/data"
out = {}
for i in range(1, 11):
    a = f"RT{i:02d}"
    D = json.load(open(f"{RT}/{a}.json", encoding="utf-8"))
    texts = [d["text"] for d in D["docs"]]
    N = len(texts)
    payload = frozen.fit_input_payload(list(texts))
    wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
    Vw, Vc, d = int(Xw.shape[1]), int(Xc.shape[1]), int(Xl.shape[1])
    Dm = Vw + Vc + d
    w_terms = sum(len(t.encode("utf-8")) for t in wv.vocabulary_.keys())
    c_terms = sum(len(t.encode("utf-8")) for t in cv.vocabulary_.keys())
    out[a] = {"N": N, "Vw": Vw, "Vc": Vc, "d": d, "D": Dm,
              "s96_f32_k96": 96*Dm*4, "s96_f32_k192": 192*Dm*4, "s96_f32_k384": 384*Dm*4,
              "sv_f32": d*Vw*4,
              "word_terms_utf8": int(w_terms), "char_terms_utf8": int(c_terms),
              "word_idf_f64": Vw*8, "char_idf_f64": Vc*8}
    print(f"{a} N={N} Vw={Vw} Vc={Vc} D={Dm} s96f32_k96={96*Dm*4:,} packed96={N*12:,}", flush=True)
json.dump(out, open(os.path.join(HERE, "P2_vocab_dims.json"), "w"), indent=1)
print("WROTE P2_vocab_dims.json")
