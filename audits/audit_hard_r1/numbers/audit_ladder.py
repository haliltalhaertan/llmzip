# Auditor's own Ladder recomputation on 2 smallest archives (RT04, RT05).
# Feature recipe (word+char TF-IDF + latent32) is the shared frozen benchmark
# definition, used read-only via import (no coordinator script executed, nothing
# written to source paths). SVD, sign coding, scoring, metrics are the auditor's own.
import json, hashlib, importlib.util
import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
SALT = "top10-r1"

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

frozen = _load("frozen_audit", f"{W}/drive/v52_t4d_locomo_frozen_cross_benchmark.py")

def my_top10(scores, arch, k=10):
    s = np.asarray(scores, dtype=np.float64).ravel()
    m = np.where(np.isfinite(s), s, -np.inf)
    hs = [hashlib.sha256(f"{SALT}|{arch}|{r}".encode()).hexdigest() for r in range(len(s))]
    return np.array(sorted(range(len(s)), key=lambda r: (-m[r], hs[r], r))[:k])

def my_metrics(S, gold, arch):
    hit = fr3 = 0.0
    n = S.shape[0]
    for r in range(n):
        top = my_top10(S[r], arch, 10)
        g = set(gold[r])
        hit += 1.0 if (g & set(top.tolist())) else 0.0
        fr3 += len(g & set(top[:3].tolist())) / len(g) if g else 0.0
    return 100 * hit / n, 100 * fr3 / n

def my_build(texts, questions, k):
    payload = frozen.fit_input_payload(list(texts))
    wv, cv, sv, Xw, Xc, Xl = frozen.fit_archive_representation(payload)
    Z = sparse.hstack([sparse.csr_matrix(Xl), Xw, Xc], format="csr")
    Qw = normalize(wv.transform(questions))
    Qc = normalize(cv.transform(questions))
    Ql = normalize(sv.transform(Qw))
    Zq = sparse.hstack([sparse.csr_matrix(Ql), Qw, Qc], format="csr")
    kk = min(k, min(Z.shape) - 1)
    tsvd = TruncatedSVD(n_components=kk, random_state=frozen.SVD_SEED)
    Y = normalize(tsvd.fit_transform(Z))
    mu = Y.mean(axis=0, keepdims=True)
    QY = normalize(tsvd.transform(Zq))
    return (Y - mu).astype(np.float64), (QY - mu).astype(np.float64), kk

def my_arms(C, QC, gold, arch):
    out = {}
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    out["sym"] = my_metrics(QB @ B.T, gold, arch)
    sg = C.std(axis=0, ddof=0)
    sg[sg < 1e-12] = 1e-12
    out["qscale"] = my_metrics((QC / sg) @ B.T, gold, arch)
    out["float"] = my_metrics(normalize(QC) @ normalize(C).T, gold, arch)
    return out

def main():
    cache = {}
    for line in open(f"{W}/_wt_top10/research_top10_comparison_2026_09_16/coordinator/LADDER_CACHE.jsonl",
                     encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            cache[r["archive"]] = r
    res = {}
    for aid in ["RT05", "RT04"]:
        d = json.load(open(f"{W}/top10_comparison_r1/data/{aid}.json", encoding="utf-8"))
        docs = d["docs"]
        texts = [x["text"] for x in docs]
        row_of = {x["row"]: j for j, x in enumerate(docs)}
        qs = [q for q in d["queries"] if any(g in row_of for g in q.get("gold", []))]
        questions = [q["text"] for q in qs]
        gold = [[row_of[g] for g in q["gold"] if g in row_of] for q in qs]
        print(f"{aid}: docs={len(docs)} q={len(qs)} (cache n={cache[aid]['n']})", flush=True)
        # fidelity gate at k=96
        C96, Q96, _ = my_build(texts, questions, 96)
        import pickle
        Cc = pickle.load(open(f"{W}/bench3/runs/b3a_realtalk/rt_repr/{aid}.pkl", "rb"))["C"]
        nd = int(np.count_nonzero((C96 >= 0) != (Cc >= 0)))
        print(f"  gate: differing_bits={nd} n_bits={C96.size} (claim {cache[aid]['gate']})", flush=True)
        res[aid] = {"gate": {"differing_bits": nd, "n_bits": int(C96.size)}, "arms": {}}
        for k in [96, 192, 384]:
            C, QC, kk = my_build(texts, questions, k)
            for sc, (h, f) in my_arms(C, QC, gold, aid).items():
                key = f"k{k}/{sc}"
                c = cache[aid]["arms"][key]
                dh, df = h - c["hit10"], f - c["fr3"]
                st = "EXACT" if (dh == 0 and df == 0) else ("CLOSE" if (abs(dh) <= 0.01 and abs(df) <= 0.01) else "MISMATCH")
                print(f"  {key}: audit ({h:.6f},{f:.6f}) vs cache ({c['hit10']:.6f},{c['fr3']:.6f}) d=({dh:+.6f},{df:+.6f}) {st}", flush=True)
                res[aid]["arms"][key] = {"hit10": h, "fr3": f, "d_hit": dh, "d_fr3": df, "status": st}
    json.dump(res, open("audit_ladder_out.json", "w", encoding="utf-8"), indent=1)
    print("WROTE audit_ladder_out.json")

if __name__ == "__main__":
    main()
