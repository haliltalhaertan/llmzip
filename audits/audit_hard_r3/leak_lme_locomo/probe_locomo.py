"""LoCoMo inductive probe (k=96). READ-ONLY on source trees; writes own dir only.
Usage: ml-python probe_locomo.py <conv_idx 0-9>
TRANS: projector fitted on the conv's own lines (production recipe).
INDEP: projector fitted on pooled lines of the other 9 convs.
Gate: sign(C_trans) bit-equality vs regen/locomo/locomo_<i>.pkl + pooled anchor check.
Metric: per-question Hit@10 (sym + qscale), det top-10 tie-break, gold from
pkl qas' raw_evidence mapped via pkl id_to_row; questions with empty gold skipped
(identical filter both arms).
"""
import hashlib, json, os, pickle, sys
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
try:
    from threadpoolctl import threadpool_limits; threadpool_limits(limits=1)
except Exception:
    pass

W = "/mnt/c/Users/MDP/dev/llmzip-work"
HERE = os.path.dirname(os.path.abspath(__file__))
RAW = W + "/drive/locomo10.json"
PKL = W + "/regen/locomo/locomo_%d.pkl"

def message_text(msg):
    speaker = str(msg.get("speaker", "")).strip()
    text = str(msg.get("text", "")).strip()
    cap = str(msg.get("blip_caption", "") or "").strip()
    if cap:
        text = f"{text} [IMAGE: {cap}]".strip()
    return f"{speaker}: {text}".strip(": ")

def conv_lines(item):
    c = item.get("conversation", {})
    lines = []
    for sk in sorted([k for k in c if k.startswith("session_") and not k.endswith("_date_time")],
                     key=lambda x: int(x.split("_")[1])):
        for msg in c.get(sk, []) or []:
            did = str(msg.get("dia_id", ""))
            if did:
                lines.append({"dia_id": did, "text": message_text(msg)})
    return lines

def fit_projector(fit_texts, k=96):
    wv = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), stop_words="english",
                         sublinear_tf=True)
    cv = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    Xw = normalize(wv.fit_transform(fit_texts))
    Xc = normalize(cv.fit_transform(fit_texts))
    d = min(32, Xw.shape[0] - 1, Xw.shape[1] - 1)
    sv = TruncatedSVD(n_components=d, random_state=5101)
    Xl = normalize(sv.fit_transform(Xw))
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    s = TruncatedSVD(n_components=min(k, min(Z.shape) - 1), random_state=5204)
    Y = normalize(s.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    return wv, cv, sv, s, mu

def encode(P, texts):
    wv, cv, sv, s, mu = P
    Qw = normalize(wv.transform(texts))
    Qc = normalize(cv.transform(texts))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    return (normalize(s.transform(Zq)) - mu).astype(np.float64)

def det_top10(scores, aid, k=10):
    s = np.asarray(scores, float).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"top10-r1|{aid}|{r}".encode()).hexdigest() for r in range(len(s))]
    return sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k]

def main():
    i = int(sys.argv[1])
    raw = json.load(open(RAW, encoding="utf-8"))
    assert isinstance(raw, list) and len(raw) == 10
    lines = conv_lines(raw[i])
    texts = [l["text"] for l in lines]
    cached = pickle.load(open(PKL % i, "rb"))
    Cc = np.asarray(cached["C"], dtype=np.float64)
    assert len(texts) == Cc.shape[0], (len(texts), Cc.shape)
    id_to_row = dict(cached["id_to_row"])
    for r, l in enumerate(lines):
        assert id_to_row.get(l["dia_id"]) == r, "line order != id_to_row"
    qas = list(cached["qas"])
    qtexts = [q["question"] for q in qas]
    gold = []
    for q in qas:
        ev = q.get("raw_evidence") or []
        gold.append([id_to_row[e] for e in ev if e in id_to_row])
    keep = [r for r in range(len(qas)) if gold[r]]
    n_skip = len(qas) - len(keep)
    qtexts_k = [qtexts[r] for r in keep]
    gold_k = [gold[r] for r in keep]
    conv_id = cached["conv_id"]

    P_t = fit_projector(texts)
    C_t = encode(P_t, texts); Q_t = encode(P_t, qtexts_k)
    bg = []
    for j in range(10):
        if j != i:
            bg.extend([l["text"] for l in conv_lines(raw[j])])
    P_i = fit_projector(bg)
    C_i = encode(P_i, texts); Q_i = encode(P_i, qtexts_k)

    dbits = int(np.count_nonzero((C_t >= 0) != (Cc >= 0)))
    maxabs = float(np.max(np.abs(C_t - Cc)))
    out = {"conv": i, "conv_id": conv_id, "N": len(texts), "n_q_kept": len(keep),
           "n_q_skipped_empty_gold": n_skip, "bg_docs": len(bg),
           "gate_diff_bits": dbits, "gate_total_bits": int(Cc.size),
           "gate_max_abs": maxabs}
    for tag, (C, Q) in (("TRANS", (C_t, Q_t)), ("INDEP", (C_i, Q_i))):
        B = np.where(C >= 0, 1.0, -1.0)
        QB = np.where(Q >= 0, 1.0, -1.0)
        sig = C.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
        for name, S in (("sym", QB @ B.T), ("qscale", (Q / sig) @ B.T)):
            hits = [1.0 if (set(gold_k[r]) & set(det_top10(S[r], conv_id, 10))) else 0.0
                    for r in range(S.shape[0])]
            out[f"{tag}_{name}"] = 100.0 * sum(hits) / len(hits)
            out[f"perq_{tag}_{name}"] = hits
    json.dump(out, open(os.path.join(HERE, f"LOCOMO_IND_{i}.json"), "w"), indent=1)
    print(f"conv{i} N={len(texts)} keptQ={len(keep)} skip={n_skip} bg={len(bg)} "
          f"gate={dbits}/{Cc.size} maxabs={maxabs:.2e} | "
          f"TRANS sym={out['TRANS_sym']:.2f} qs={out['TRANS_qscale']:.2f} | "
          f"INDEP sym={out['INDEP_sym']:.2f} qs={out['INDEP_qscale']:.2f}", flush=True)

main()
