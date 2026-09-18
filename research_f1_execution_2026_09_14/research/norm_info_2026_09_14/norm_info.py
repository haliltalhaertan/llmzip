#!/usr/bin/env python3
"""
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

norm_info.py -- Does the document norm ||C_i|| (discarded by SIGN quantization)
explain the per-benchmark offset in Delta(FR@3) = sign - float?

Arms (all ranked highest-score-first):
  (a) sign      : -Hamming( C>=0 , q>=0 )                         12 B/doc
  (b) cosine    :  C_i.q / ||C_i||                                384 B/doc
  (c1) signxnorm:  ||C_i|| * (96 - 2*Hamming_i)                   16 B/doc
  (c2) signaddN :  -Hamming_i + lambda * z(||C_i||)               16 B/doc
  (d) rawdot    :  C_i.q                                          384 B/doc
  (e) normonly  :  ||C_i||                                        4 B/doc

Metric: FR@3 = |gold ^ top3| / |gold|, EXACT tie expectation
  E[FR@K] = (g_strict + g_tied * slots / bc) / |gold|

READ-ONLY on all caches. Additive-only output.
"""
import sys, os, json, glob, pickle, math
import numpy as np

B = '/mnt/c/Users/MDP/dev/llmzip-work'
OUT = B + '/agent_out/norm-info'
K = 3
D = 96

# ---------------------------------------------------------------- metric
def frk_exact(scores, gold, K=3):
    """Exact expectation of FR@K under uniform random tie-breaking. higher score = better."""
    n = scores.shape[0]
    g = len(gold)
    if n <= K:
        return 1.0
    thr = np.partition(scores, n - K)[n - K]      # K-th largest value
    better = scores > thr
    nb = int(better.sum())
    slots = K - nb
    bc = int((scores == thr).sum())
    gs = int(better[gold].sum())
    gt = int((scores[gold] == thr).sum())
    return (gs + gt * slots / bc) / g

def random_frk(n, K=3):
    """Expected FR@K of a uniformly random ranking = min(K,n)/n (per-gold inclusion prob)."""
    return min(K, n) / n

# ---------------------------------------------------------------- loaders
def load_lme():
    for f in sorted(glob.glob(B + '/regen/lme/cache_repr/*.pkl')):
        d = pickle.load(open(f, 'rb'))
        gold = np.asarray(d['gold'], dtype=np.int64).ravel()
        if gold.size == 0:
            continue
        yield ('longmemeval', 'all', np.asarray(d['C'], dtype=np.float64),
               np.asarray(d['qC'], dtype=np.float64).ravel(), gold)

def load_realtalk():
    for f in sorted(glob.glob(B + '/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], dtype=np.float64)
        QC = np.asarray(d['QC'], dtype=np.float64)
        for i, gr in enumerate(d['gold_rows']):
            gold = np.asarray(gr, dtype=np.int64).ravel()
            if gold.size == 0:
                continue
            yield ('realtalk', 'all', C, QC[i], gold)

def load_perltqa():
    ca = pickle.load(open(B + '/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
    cq = pickle.load(open(B + '/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
    Cs = {k: np.asarray(v['C'], dtype=np.float64) for k, v in ca.items()}
    for qid, q in cq.items():
        C = Cs.get(q['char'])
        if C is None:
            continue
        gold = np.asarray(q['gold'], dtype=np.int64).ravel()
        if gold.size == 0:
            continue
        yield ('perltqa', q['section'], C, np.asarray(q['qC'], dtype=np.float64).ravel(), gold)

def load_locomo():
    for f in sorted(glob.glob(B + '/regen/locomo/locomo_*.pkl')):
        d = pickle.load(open(f, 'rb'))
        C = np.asarray(d['C'], dtype=np.float64)
        QC = np.asarray(d['QC'], dtype=np.float64)
        i2r = d['id_to_row']
        for i, qa in enumerate(d['qas']):
            ev = qa.get('raw_evidence') or []
            rows = sorted({i2r[e] for e in ev if e in i2r})
            if not rows:
                continue
            yield ('locomo', 'all', C, QC[i], np.asarray(rows, dtype=np.int64))

LOADERS = {'longmemeval': load_lme, 'perltqa': load_perltqa,
           'realtalk': load_realtalk, 'locomo': load_locomo}

# ---------------------------------------------------------------- control
def control():
    print('=== CONTROL: reproduce frozen LongMemEval headline ===')
    fs, ff, nrm = [], [], []
    for _, _, C, q, gold in load_lme():
        b = (C >= 0); bq = (q >= 0)
        ham = (b != bq).sum(1).astype(np.float64)
        nn = np.linalg.norm(C, axis=1)
        cos = (C @ q) / np.where(nn == 0, 1.0, nn)
        fs.append(frk_exact(-ham, gold, K))
        ff.append(frk_exact(cos, gold, K))
        nrm.append(nn.mean())
    fs, ff = np.array(fs), np.array(ff)
    print(f'  n_queries        = {len(fs)}')
    print(f'  SIGN  FR@3       = {fs.mean():.10f}   (frozen 0.5419751773049645)')
    print(f'  FLOAT FR@3       = {ff.mean():.10f}   (frozen 0.4415957446808511)')
    print(f'  Delta pp         = {100*(fs.mean()-ff.mean()):.6f}   (frozen +10.037943, exact-tie ref +10.053783)')
    ok = abs(100*(fs.mean()-ff.mean()) - 10.053783) < 0.01
    print('  CONTROL', 'PASS' if ok else 'FAIL')
    return ok

# ---------------------------------------------------------------- full run
def zscore(v):
    s = v.std()
    return (v - v.mean()) / s if s > 0 else np.zeros_like(v)

LAMBDAS = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]

def run_bench(name):
    rows = []
    for _, sec, C, q, gold in LOADERS[name]():
        n = C.shape[0]
        b = (C >= 0); bq = (q >= 0)
        ham = (b != bq).sum(1).astype(np.float64)
        sim_bits = (D - 2.0 * ham)                 # binary dot product, in {-96..96}
        nn = np.linalg.norm(C, axis=1)
        safe = np.where(nn == 0, 1.0, nn)
        dot = C @ q
        cos = dot / safe
        z = zscore(nn)

        r = {'sec': sec, 'n': n, 'g': len(gold),
             'sign':     frk_exact(-ham, gold, K),
             'cosine':   frk_exact(cos, gold, K),
             'signxnorm':frk_exact(nn * sim_bits, gold, K),
             'rawdot':   frk_exact(dot, gold, K),
             'normonly': frk_exact(nn, gold, K),
             'random':   random_frk(n, K)}
        for lam in LAMBDAS:
            r[f'signadd_{lam}'] = frk_exact(-ham + lam * z, gold, K)

        # --- norm informativeness diagnostics (query-independent) ---
        gm = np.zeros(n, dtype=bool); gm[gold] = True
        ng = int(gm.sum()); nb_ = n - ng
        if nb_ > 0 and ng > 0:
            # within-query AUC: P(norm(gold) > norm(nongold)) + 0.5*P(tie)
            ranks = np.empty(n)
            order = np.argsort(nn, kind='mergesort')
            sortn = nn[order]
            i = 0; rr = np.empty(n)
            while i < n:
                j = i
                while j + 1 < n and sortn[j + 1] == sortn[i]:
                    j += 1
                rr[i:j + 1] = (i + j) / 2.0 + 1.0
                i = j + 1
            ranks[order] = rr
            R = ranks[gm].sum()
            auc = (R - ng * (ng + 1) / 2.0) / (ng * nb_)
            r['auc'] = auc
            r['zgold'] = float(z[gm].mean())          # standardized mean diff (within-query)
        else:
            r['auc'] = np.nan; r['zgold'] = np.nan
        rows.append(r)
    return rows

def boot_ci(a, b=None, n=2000, seed=0):
    """bootstrap 95% CI of mean(a) or mean(a)-mean(b), paired over queries."""
    rng = np.random.default_rng(seed)
    a = np.asarray(a)
    v = a if b is None else a - np.asarray(b)
    idx = rng.integers(0, len(v), size=(n, len(v)))
    m = v[idx].mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))

def agg(rows, label):
    A = {k: np.array([r[k] for r in rows], dtype=np.float64)
         for k in rows[0] if k not in ('sec',)}
    o = {'label': label, 'n_queries': len(rows),
         'n_docs_mean': float(A['n'].mean()), 'n_docs_median': float(np.median(A['n'])),
         'gold_mean': float(A['g'].mean())}
    for k in ('sign', 'cosine', 'signxnorm', 'rawdot', 'normonly', 'random'):
        o[k] = float(A[k].mean())
    for lam in LAMBDAS:
        o[f'signadd_{lam}'] = float(A[f'signadd_{lam}'].mean())
    o['delta_sign_minus_cosine_pp'] = 100 * (o['sign'] - o['cosine'])
    o['delta_rawdot_minus_cosine_pp'] = 100 * (o['rawdot'] - o['cosine'])
    o['delta_signxnorm_minus_sign_pp'] = 100 * (o['signxnorm'] - o['sign'])
    o['delta_normonly_minus_random_pp'] = 100 * (o['normonly'] - o['random'])
    lo, hi = boot_ci(A['normonly'], A['random']); o['ci_normonly_minus_random_pp'] = [100*lo, 100*hi]
    lo, hi = boot_ci(A['rawdot'], A['cosine']);   o['ci_rawdot_minus_cosine_pp'] = [100*lo, 100*hi]
    lo, hi = boot_ci(A['signxnorm'], A['sign']);  o['ci_signxnorm_minus_sign_pp'] = [100*lo, 100*hi]
    lo, hi = boot_ci(A['sign'], A['cosine']);     o['ci_sign_minus_cosine_pp'] = [100*lo, 100*hi]
    au = A['auc'][~np.isnan(A['auc'])]
    o['norm_auc_mean'] = float(au.mean()); o['norm_auc_n'] = int(au.size)
    lo, hi = boot_ci(au); o['norm_auc_ci'] = [lo, hi]
    o['cliffs_delta'] = 2 * float(au.mean()) - 1
    zg = A['zgold'][~np.isnan(A['zgold'])]
    o['zgold_mean'] = float(zg.mean())                 # Cohen-d-like standardized mean diff
    lo, hi = boot_ci(zg); o['zgold_ci'] = [lo, hi]
    # best lambda (IN-SAMPLE oracle upper bound, flagged as such)
    best = max(LAMBDAS, key=lambda L: o[f'signadd_{L}'])
    o['signadd_best_lambda_INSAMPLE'] = best
    o['signadd_best_fr3_INSAMPLE'] = o[f'signadd_{best}']
    o['signadd_best_gain_over_sign_pp_INSAMPLE'] = 100 * (o[f'signadd_{best}'] - o['sign'])
    return o

def full():
    res = {'_meta': {'metric': 'FR@3 exact tie expectation', 'K': K,
                     'note': 'LOCAL EXPLORATORY PILOT / NOT PREREGISTERED / NOT FOR CITATION'},
           'benchmarks': {}, 'perltqa_sections': {}}
    for name in ('longmemeval', 'perltqa', 'realtalk', 'locomo'):
        rows = run_bench(name)
        res['benchmarks'][name] = agg(rows, name)
        print(f'[{name}] n={len(rows)} sign={res["benchmarks"][name]["sign"]:.6f} '
              f'cos={res["benchmarks"][name]["cosine"]:.6f} '
              f'D={res["benchmarks"][name]["delta_sign_minus_cosine_pp"]:+.4f}pp '
              f'normonly={res["benchmarks"][name]["normonly"]:.6f} '
              f'rand={res["benchmarks"][name]["random"]:.6f} '
              f'AUC={res["benchmarks"][name]["norm_auc_mean"]:.4f}')
        if name == 'perltqa':
            secs = sorted({r['sec'] for r in rows})
            for s in secs:
                sub = [r for r in rows if r['sec'] == s]
                res['perltqa_sections'][s] = agg(sub, f'perltqa/{s}')
                a = res['perltqa_sections'][s]
                print(f'   [{s}] n={len(sub)} D={a["delta_sign_minus_cosine_pp"]:+.4f}pp '
                      f'normonly={a["normonly"]:.6f} rand={a["random"]:.6f} AUC={a["norm_auc_mean"]:.4f}')
    res['_storage_bytes_per_doc'] = {
        'sign': 12, 'signxnorm': 16, 'signadd': 16,
        'cosine': 384, 'rawdot': 384, 'normonly': 4,
        'note': '96 bits = 12 B; +float32 norm = 16 B (+33.3%); 96 x float32 = 384 B'}
    os.makedirs(OUT + '/evidence', exist_ok=True)
    json.dump(res, open(OUT + '/evidence/results.json', 'w'), indent=2)
    print('\nwrote', OUT + '/evidence/results.json')
    return res

if __name__ == '__main__':
    stage = sys.argv[1] if len(sys.argv) > 1 else 'control'
    if stage == 'control':
        sys.exit(0 if control() else 1)
    elif stage == 'full':
        full()
