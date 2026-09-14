"""Independent axis-budget implementation (STEP 1).

Method (from CLAIM 1 description only):
  per archive, rank 96 axes by mean_i(C_ij^2) descending; TOP-m = first m.
  SIGN FR@3 = Hamming on (C>=0),(qC>=0) restricted to TOP-m (lower better).
  FLOAT FR@3 = cosine on raw C restricted to TOP-m (higher better).
  Delta = sign - float, in percentage points.
  FR@3 = mean over queries of per-query exact tie expectation:
     E = (g_strict + g_tied * slots / bc) / |gold|, K=3.
Caches are already centered: NO re-centering.
"""
import pickle, glob, numpy as np
from collections import defaultdict

K = 3
MS = [8, 32, 48, 64, 96]

def fr_exact_hamming(dist, gold, k=3):
    # lower better; exact ties at integer distances
    order = np.argsort(dist, kind='stable')
    thr = dist[order[k-1]] if len(dist) >= k else dist[order[-1]]
    better = dist < thr
    tied = dist == thr
    bc = int(np.sum(tied))
    n_strict = int(np.sum(better))
    slots = k - n_strict
    g = np.asarray(gold)
    g_strict = int(np.sum(better[g]))
    g_tied = int(np.sum(tied[g]))
    return (g_strict + g_tied * slots / bc) / len(g)

def fr_exact_cosine(cos, gold, k=3):
    # higher better; guard: NaN (zero norm) ranks last
    cos = np.where(np.isnan(cos), -np.inf, cos)
    order = np.argsort(-cos, kind='stable')
    thr = cos[order[k-1]] if len(cos) >= k else cos[order[-1]]
    better = cos > thr
    tied = cos == thr
    bc = int(np.sum(tied))
    n_strict = int(np.sum(better))
    slots = k - n_strict
    g = np.asarray(gold)
    g_strict = int(np.sum(better[g]))
    g_tied = int(np.sum(tied[g]))
    return (g_strict + g_tied * slots / bc) / len(g)

def subset_scores(C, qC, idx):
    Cs = C[:, idx]
    qs = qC[idx]
    Cb = Cs >= 0
    qb = qs >= 0
    dist = np.sum(Cb != qb, axis=1).astype(np.int32)
    dots = Cs @ qs
    rn = np.sqrt(np.sum(Cs * Cs, axis=1))
    qn = float(np.sqrt(np.sum(qs * qs)))
    denom = rn * qn
    with np.errstate(divide='ignore', invalid='ignore'):
        cos = dots / denom
    cos = np.where(denom == 0, np.nan, cos)
    return dist, cos

def evaluate_queries(queries, m):
    # queries: list of (C, qC, gold); ranking is PER ARCHIVE (= per query's own C here)
    s_sum, f_sum, n = 0.0, 0.0, 0
    for (C, qC, gold) in queries:
        var = np.mean(C * C, axis=0)
        order = np.argsort(-var, kind='stable')
        idx = order[:m]
        dist, cos = subset_scores(C, qC, idx)
        s_sum += fr_exact_hamming(dist, gold)
        f_sum += fr_exact_cosine(cos, gold)
        n += 1
    return s_sum / n, f_sum / n

# ---- LME ----
lme_files = sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl'))
lme_queries = []
for fp in lme_files:
    with open(fp, 'rb') as f:
        d = pickle.load(f)
    lme_queries.append((np.asarray(d['C'], dtype=np.float64),
                        np.asarray(d['qC'], dtype=np.float64).reshape(-1),
                        np.asarray(d['gold']).reshape(-1)))
print("LME queries:", len(lme_queries), flush=True)
print("LME min N:", min(C.shape[0] for C, _, _ in lme_queries),
      "min |gold|:", min(len(g) for _, _, g in lme_queries), flush=True)

lme_res = {}
for m in MS:
    s, f = evaluate_queries(lme_queries, m)
    lme_res[m] = (s, f, (s - f) * 100.0)
    print(f"LME m={m} sign={s*100:.6f} float={f*100:.6f} delta={(s-f)*100:.6f}", flush=True)

# ---- PerLTQA ----
with open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb') as f:
    ARCH = pickle.load(f)
with open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb') as f:
    QQ = pickle.load(f)
print("PerLTQA arch:", len(ARCH), "queries:", len(QQ), flush=True)
# group query indices per char; rank per ARCHIVE (char C), shared across its queries
arch_C = {c: np.asarray(ARCH[c]['C'], dtype=np.float64) for c in ARCH}
arch_order = {}
for c, C in arch_C.items():
    var = np.mean(C * C, axis=0)
    arch_order[c] = np.argsort(-var, kind='stable')
by_char = defaultdict(list)
for qid, q in QQ.items():
    by_char[q['char']].append((qid, np.asarray(q['qC'], dtype=np.float64).reshape(-1),
                               np.asarray(q['gold']).reshape(-1)))
print("chars:", len(by_char),
      "min arch N:", min(C.shape[0] for C in arch_C.values()), flush=True)

plt_res = {}
for m in MS:
    s_sum, f_sum, n = 0.0, 0.0, 0
    for c, qlist in by_char.items():
        C = arch_C[c]
        idx = arch_order[c][:m]
        Cb_full = (C[:, idx] >= 0)
        Cs = C[:, idx]
        cs_norms = np.sqrt(np.sum(Cs * Cs, axis=1))
        for (qid, qC, gold) in qlist:
            qb = (qC[idx] >= 0)
            dist = np.sum(Cb_full != qb, axis=1).astype(np.int32)
            qs = qC[idx]
            qn = float(np.sqrt(np.sum(qs * qs)))
            denom = cs_norms * qn
            with np.errstate(divide='ignore', invalid='ignore'):
                cos = (Cs @ qs) / denom
            cos = np.where(denom == 0, np.nan, cos)
            s_sum += fr_exact_hamming(dist, gold)
            f_sum += fr_exact_cosine(cos, gold)
            n += 1
    s, f = s_sum / n, f_sum / n
    plt_res[m] = (s, f, (s - f) * 100.0)
    print(f"PLTQA m={m} sign={s*100:.6f} float={f*100:.6f} delta={(s-f)*100:.6f} n={n}", flush=True)

print("DONE")
