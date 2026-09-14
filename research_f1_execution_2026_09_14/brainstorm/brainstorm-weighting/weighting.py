"""weighting.py — H-W framing: spectral location of query-gold support + whitening sweep."""
import pickle, glob, json
import numpy as np
from collections import defaultdict

ALPHAS = [0.0, 0.5, 1.0, 1.5, 2.0]
K = 3
EPS = 1e-12

def fr3_exact_batch(S, golds, K=3):
    """S: (nq,N) scores; golds: list of lists. Exact tie expectation mean."""
    nq, N = S.shape
    tot, n = 0.0, 0
    perq = np.zeros(nq)
    for i in range(nq):
        s = S[i]; g = list(golds[i])
        if len(g) == 0:
            perq[i] = np.nan; continue
        part = np.partition(s, N - K)
        thr = part[N - K]
        better = np.sum(s > thr); tied = np.sum(s == thr)
        slots = K - better
        gs = sum(1 for r in g if s[r] > thr)
        gt = sum(1 for r in g if s[r] == thr)
        perq[i] = (gs + gt * slots / tied) / len(g)
        tot += perq[i]; n += 1
    return tot / n, perq

def cos_scores(C, Q):
    Cn = C / (np.linalg.norm(C, axis=1, keepdims=True) + 1e-12)
    Qn = Q / (np.linalg.norm(Q, axis=1, keepdims=True) + 1e-12)
    return Qn @ Cn.T

def ham_scores(C, Q):
    Cs = (C >= 0); Qs = (Q >= 0)
    return -(Qs[:, None, :] != Cs[None, :, :]).sum(-1).astype(float)

def wcos_scores(C, Q, v, alpha):
    sc = v ** (alpha / 2.0) + EPS
    return cos_scores(C / sc, Q / sc)

def pearson(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    if np.std(x) < 1e-15 or np.std(y) < 1e-15:
        return np.nan
    return float(np.corrcoef(x, y)[0, 1])

# ---- load archives: list of (name, C, Q, golds, sections) ----
archives = []  # (tag, bench, C, Q, golds, secs)
# LME: one archive per query
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    archives.append(('lme', 'LME', d['C'], d['qC'][None, :], [list(d['gold'])], [None]))
# PerLTQA: group by char
arch = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
qq = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
bychar = defaultdict(list)
for qid, v in qq.items():
    bychar[v['char']].append((qid, v))
for ch, items in bychar.items():
    C = arch[ch]['C']
    Q = np.stack([v['qC'] for _, v in items])
    golds = [list(v['gold']) for _, v in items]
    secs = [v['section'] for _, v in items]
    archives.append((ch, 'PerLTQA', C, Q, golds, secs))
# REALTALK
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d = pickle.load(open(f, 'rb'))
    archives.append((d['conv_id'], 'REALTALK', d['C'], d['QC'], [list(g) for g in d['gold_rows']], [None]*len(d['gold_rows'])))
# LoCoMo
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
    d = pickle.load(open(f, 'rb'))
    m = d['id_to_row']
    golds = []
    for qa in d['qas']:
        ev = qa['raw_evidence']
        golds.append([m[e] for e in ev if e in m])
    archives.append((f.split('/')[-1], 'LoCoMo', d['C'], d['QC'], golds, [None]*len(golds)))

# ---- per-query spectral quantities + scores ----
rec = []  # dicts
for tag, bench, C, Q, golds, secs in archives:
    v = (C ** 2).mean(0)
    lv = np.log(v + EPS)
    S_sign = ham_scores(C, Q)
    S_cos = cos_scores(C, Q)
    S_w = {a: wcos_scores(C, Q, v, a) for a in ALPHAS}
    G = np.stack([C[g].mean(0) if len(g) else np.zeros(C.shape[1]) for g in golds])
    for i in range(Q.shape[0]):
        if len(golds[i]) == 0:
            continue
        s = Q[i] * G[i]
        r_signed = pearson(lv, s)
        r_abs = pearson(lv, np.abs(s))
        r_gold = pearson(lv, G[i] ** 2)
        pos = s > 0
        if pos.sum() > 0:
            order = np.argsort(-v)  # rank1 = highest variance
            rank = np.empty(96); rank[order] = np.arange(1, 97)
            cent = float(np.sum(rank[pos] * s[pos]) / np.sum(s[pos]))
        else:
            cent = np.nan
        rec.append(dict(bench=bench, sec=secs[i], r=r_signed, ra=r_abs, rg=r_gold,
                        cent=cent, v=v.copy(), q=Q[i].copy(), g=G[i].copy(),
                        s_sign=S_sign[i], s_cos=S_cos[i],
                        s_w={a: S_w[a][i] for a in ALPHAS}, gold=golds[i]))

def summ(vals):
    x = np.array([t for t in vals if np.isfinite(t)])
    m = float(x.mean())
    ci = 1.96 * float(x.std(ddof=1)) / np.sqrt(len(x))
    return m, ci, len(x)

print('=== Q-SPEC spectral quantities (VERIFIED this run) ===')
qres = {}
groups = [('LME', None), ('LoCoMo', None), ('REALTALK', None), ('PerLTQA', None),
          ('PerLTQA', 'profile'), ('PerLTQA', 'social_relationship'),
          ('PerLTQA', 'dialogues'), ('PerLTQA', 'events')]
for b, s in groups:
    sub = [r for r in rec if r['bench'] == b and (s is None or r['sec'] == s)]
    m, ci, n = summ([r['r'] for r in sub])
    ma, cia, _ = summ([r['ra'] for r in sub])
    mg, cig, _ = summ([r['rg'] for r in sub])
    mc, cic, nc = summ([r['cent'] for r in sub])
    qres[f'{b}|{s}'] = dict(R=m, ci=ci, n=n, Rabs=ma, Rgold=mg, cent=mc, centci=cic)
    print(f'{b:8s} {str(s):18s} R={m:+.4f}+/-{ci:.4f} n={n}  Rabs={ma:+.4f} Rgold={mg:+.4f} cent={mc:.2f}+/-{cic:.2f}')

print('=== FR@3 arms (VERIFIED this run) ===')

def fr_of(scores_list, golds):
    tot, n = 0.0, 0
    for sv, g in zip(scores_list, golds):
        sv = np.asarray(sv, float)
        N = len(sv)
        thr = np.partition(sv, N - K)[N - K]
        better = np.sum(sv > thr); tied = np.sum(sv == thr)
        slots = K - better
        gs = sum(1 for r in g if sv[r] > thr)
        gt = sum(1 for r in g if sv[r] == thr)
        tot += (gs + gt * slots / tied) / len(g)
        n += 1
    return tot / n

fres = {}
for b, s in groups:
    sub = [r for r in rec if r['bench'] == b and (s is None or r['sec'] == s)]
    golds = [r['gold'] for r in sub]
    fs = fr_of([r['s_sign'] for r in sub], golds)
    fc = fr_of([r['s_cos'] for r in sub], golds)
    row = dict(sign=fs, cos=fc, delta=(fs - fc) * 100, n=len(sub))
    for a in ALPHAS:
        fw = fr_of([r['s_w'][a] for r in sub], golds)
        row[f'a{a}'] = fw
        row[f'd{a}'] = (fs - fw) * 100
    fres[f'{b}|{s}'] = row
    al = ' '.join(f'a{a}={row[f"a{a}"]:.4f}' for a in ALPHAS)
    print(f'{b:8s} {str(s):18s} sign={fs:.6f} cos={fc:.6f} D={row["delta"]:+.4f}pp n={len(sub)}')
    print(f'    whitened: {al}')
    print(f'    D(alpha): ' + ' '.join(f'{row[f"d{a}"]:+.2f}' for a in ALPHAS))

json.dump(dict(q=qres, fr=fres),
          open('/home/mdp/muse-work/brainstorm-weighting/results.json', 'w'), indent=1)
print('saved results.json')
