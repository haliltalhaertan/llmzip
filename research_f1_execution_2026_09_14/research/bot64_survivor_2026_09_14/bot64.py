"""
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

bot64.py -- core library + per-query row extraction for the BOT64 survivor audit.

Definitions (from E1_PREANALYSIS_SPEC_V2.md items 14-18 + task brief):
  v_j        = mean_i(C_ij^2), axes ranked DESCENDING by v_j
  TOP-m      = m highest-variance axes ; BOT-m = m lowest-variance axes
  strict_A(g)= #{rows strictly closer than gold g in Hamming restricted to arm A}
  per-query  = mean over golds
  Delta_q    = FR@3_SIGN96(q) - FR@3_FLOAT96(q)

Metric: FR@3 = |gold cap top3| / |gold| with the EXACT tie expectation
  E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|

C matrices are ALREADY CENTERED -> no re-centering.
"""
import pickle, glob, os, hashlib, json
import numpy as np

BASE = '/mnt/c/Users/MDP/dev/llmzip-work/'
OUT  = BASE + 'agent_out/bot64-survivor/'
EV   = OUT + 'evidence/'
K    = 3
NRAND = 24          # random-64 seeds (>=20 required)
MS   = [8, 16, 24, 32, 48, 64, 80, 96]

# ---------------------------------------------------------------- metric ----
def fr_at_k(score, gold, K=3):
    """score: higher = better. Exact tie expectation of FR@K."""
    n = score.shape[0]
    if n <= K:
        return 1.0
    part = np.sort(score)[::-1]
    thr = part[K - 1]
    n_better = int((score > thr).sum())
    bc = int((score == thr).sum())
    slots = K - n_better
    gs = score[gold]
    g_strict = int((gs > thr).sum())
    g_tied = int((gs == thr).sum())
    if bc == 0:
        return g_strict / len(gold)
    return (g_strict + g_tied * slots / bc) / len(gold)


def spearman(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    if len(x) < 3: return np.nan
    rx, ry = _avgrank(x), _avgrank(y)
    if rx.std() == 0 or ry.std() == 0: return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])


def _avgrank(a):
    """1-based average ranks (ties averaged)."""
    n = len(a)
    order = np.argsort(a, kind='mergesort')
    s = a[order]
    r = np.empty(n, float)
    i = 0
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def partial_spearman(x, y, Z):
    """Spearman partial corr: rank-transform all, then residualise x,y on Z (with intercept)."""
    x = _avgrank(np.asarray(x, float)); y = _avgrank(np.asarray(y, float))
    Zr = np.column_stack([_avgrank(np.asarray(z, float)) for z in Z] + [np.ones(len(x))])
    bx, *_ = np.linalg.lstsq(Zr, x, rcond=None)
    by, *_ = np.linalg.lstsq(Zr, y, rcond=None)
    rx = x - Zr @ bx; ry = y - Zr @ by
    if rx.std() == 0 or ry.std() == 0: return np.nan
    return float(np.corrcoef(rx, ry)[0, 1])


# ------------------------------------------------------------ arm design ----
def arm_names():
    names = [f'TOP{m}' for m in MS] + [f'BOT{m}' for m in MS]
    names += [f'RND64_s{s}' for s in range(NRAND)]
    return names


def per_query_distances(Cs, qs, perm, arch_key):
    """Return D (N, A) Hamming distances for every arm, using cumsum + gemm."""
    M = (Cs != qs).astype(np.float32)             # (N,96) mismatch
    Mp = M[:, perm]                               # variance-descending order
    cs = np.cumsum(Mp, axis=1)                    # (N,96)
    tot = cs[:, -1]
    tops = np.column_stack([cs[:, m - 1] for m in MS])              # TOP-m
    bots = np.column_stack([tot - cs[:, 96 - m - 1] if m < 96 else tot
                            for m in MS])                            # BOT-m
    # random 64-subsets, re-drawn per archive (matches BOT64's archive-dependence)
    R = np.zeros((96, NRAND), np.float32)
    for s in range(NRAND):
        rng = np.random.default_rng(
            int(hashlib.sha256(f'{arch_key}|{s}'.encode()).hexdigest()[:8], 16))
        R[rng.choice(96, 64, replace=False), s] = 1.0
    rnd = M @ R                                                      # (N,NRAND)
    return np.concatenate([tops, bots, rnd], axis=1)


def strict_counts(D, gold):
    """(A,) mean-over-golds strict counts, over ALL rows and over NON-GOLD rows."""
    dg = D[gold]                                   # (G,A)
    lt = (D[:, None, :] < dg[None, :, :])          # (N,G,A)
    s_all = lt.sum(0).astype(float)                # (G,A)
    s_ng = s_all - lt[gold].sum(0).astype(float)   # subtract other golds closer
    return s_all.mean(0), s_ng.mean(0)


# ----------------------------------------------------------- extraction ----
def process(archives, bench):
    """archives: iterable of (arch_key, C, [(qid, qC, gold, meta), ...])"""
    names = arm_names()
    rows = []
    for arch_key, C, qlist in archives:
        N = C.shape[0]
        if N < 4: continue
        v = (C ** 2).mean(0)
        perm = np.argsort(-v, kind='mergesort')    # descending variance
        Cs = (C >= 0)
        Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
        for qid, qC, gold, meta in qlist:
            gold = np.asarray(gold, int)
            gold = gold[(gold >= 0) & (gold < N)]
            if len(gold) == 0: continue
            qs = (qC >= 0)
            D = per_query_distances(Cs, qs, perm, arch_key)
            s_all, s_ng = strict_counts(D, gold)
            # metric arms
            ham96 = D[:, MS.index(96)]                       # TOP96 == full 96
            cos = Cn @ (qC / (np.linalg.norm(qC) + 1e-12))
            fr_sign = fr_at_k(-ham96, gold, K)
            fr_flt = fr_at_k(cos, gold, K)
            # float competition controls
            strict_float = float(np.mean([(cos > cos[g]).sum() for g in gold]))
            nong = np.ones(N, bool); nong[gold] = False
            best_non = cos[nong].max() if nong.any() else -1e9
            margin = float(np.mean([cos[g] - best_non for g in gold]))
            r = dict(bench=bench, arch=str(arch_key), qid=str(qid), N=N,
                     ngold=len(gold), fr_sign=fr_sign, fr_float=fr_flt,
                     delta=fr_sign - fr_flt, strict_float=strict_float,
                     float_margin=margin, **meta)
            for i, nm in enumerate(names):
                r['sA_' + nm] = float(s_all[i])
                r['sN_' + nm] = float(s_ng[i])
            rows.append(r)
    return rows


# ------------------------------------------------------------- loaders -----
def load_lme():
    for f in sorted(glob.glob(BASE + 'regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        yield (d['question_id'], d['C'],
               [(d['question_id'], d['qC'], d['gold'], {'section': 'lme'})])


def load_rt():
    for f in sorted(glob.glob(BASE + 'bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        ql = []
        for i, qid in enumerate(d['qids']):
            g = d['gold_rows'][i]
            if not g: continue
            ql.append((qid, d['QC'][i], g, {'section': 'rt'}))
        yield (d['conv_id'], d['C'], ql)


def load_per():
    A = pickle.load(open(BASE + 'bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    Q = pickle.load(open(BASE + 'bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    by = {}
    for qid, q in Q.items():
        by.setdefault(q['char'], []).append(
            (qid, q['qC'], q['gold'], {'section': q['section']}))
    for ch, ql in by.items():
        yield (ch, A[ch]['C'], ql)


def load_loco():
    for f in sorted(glob.glob(BASE + 'regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        i2r = d['id_to_row']
        ql = []
        for i, qa in enumerate(d['qas']):
            ev = qa.get('raw_evidence') or []
            if isinstance(ev, str): ev = [ev]
            g = [i2r[e] for e in ev if e in i2r]
            if not g: continue
            ql.append((qa['question_id'], d['QC'][i], sorted(set(g)),
                       {'section': 'cat%s' % qa.get('category')}))
        yield (d['conv_id'], d['C'], ql)


LOADERS = {'LME': load_lme, 'REALTALK': load_rt,
           'PerLTQA': load_per, 'LoCoMo': load_loco}

if __name__ == '__main__':
    import sys
    os.makedirs(EV, exist_ok=True)
    allrows = []
    for b, ld in LOADERS.items():
        rs = process(ld(), b)
        print(b, 'queries', len(rs), flush=True)
        allrows += rs
    with open(EV + 'rows.pkl', 'wb') as fh:
        pickle.dump(allrows, fh)
    # headline gate
    for b in LOADERS:
        rs = [r for r in allrows if r['bench'] == b]
        s = np.mean([r['fr_sign'] for r in rs]); f = np.mean([r['fr_float'] for r in rs])
        print(f'{b}: SIGN {s:.12f} FLOAT {f:.12f} Delta {100*(s-f):.6f} pp  n={len(rs)}')
