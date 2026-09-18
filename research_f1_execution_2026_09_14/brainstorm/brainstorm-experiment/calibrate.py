# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# calibrate.py — measure synthetic-dial coordinates on the four real benchmarks (+PerLTQA sections).
# Dials: alpha (spectrum decay), locus rho (where query-gold signal lives), shape (kurtosis/skew),
# N (archive size), ngold. Observational measurement FOR CALIBRATION ONLY — not a mechanism claim.
import pickle, glob, numpy as np, json, os
from collections import defaultdict

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'calibration.json')

def spearman(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    ra = ra - ra.mean(); rb = rb - rb.mean()
    return float((ra * rb).sum() / np.sqrt((ra ** 2).sum() * (rb ** 2).sum() + 1e-30))

def fit_alpha(v):
    vs = np.sort(np.asarray(v, float))[::-1]
    x = np.log(np.arange(1, len(vs) + 1)); y = np.log(vs + 1e-30)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, _ = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(-slope)

def kurt_med(C):
    m2 = (C ** 2).mean(0); m4 = (C ** 4).mean(0)
    return float(np.median(m4 / (m2 ** 2 + 1e-30) - 3.0))

def skew_med(C):
    m2 = (C ** 2).mean(0); m3 = (C ** 3).mean(0)
    return float(np.median(m3 / (m2 ** 1.5 + 1e-30)))

def summarize(name, Cs, QGs):
    # Cs: list of (N,96); QGs: list of (qC, goldvec(mean gold row), ngold)
    V = np.mean([np.mean(C ** 2, axis=0) for C in Cs], axis=0)
    A = np.mean([q * g for q, g, _ in QGs], axis=0)
    An = A / (V + 1e-30)
    o = np.argsort(-V)
    top, bot = o[:16], o[-16:]
    Ns = [C.shape[0] for C in Cs]; ngs = [n for _, _, n in QGs]
    return dict(n_arch=len(Cs), n_q=len(QGs), N_mean=float(np.mean(Ns)), N_min=int(min(Ns)),
                N_max=int(max(Ns)), ngold_mean=float(np.mean(ngs)),
                alpha=float(fit_alpha(V)), top16_share=float(V[o[:16]].sum() / V.sum()),
                var_ratio_16=float(V[o[:15]].mean() / (V[o[-16:]].mean() + 1e-30)),
                eff_rank=float(V.sum() ** 2 / (V ** 2).sum()),
                kurt_med=float(np.mean([kurt_med(C) for C in Cs])),
                skew_med=float(np.mean([skew_med(C) for C in Cs])),
                locus_rho=spearman(A, V), locus_rho_norm=spearman(An, V),
                sig_top=float(A[top].sum()), sig_bot=float(A[bot].sum()),
                abs_top=float(np.abs(A[top]).sum()), abs_bot=float(np.abs(A[bot]).sum()))

# LME
Cs, QGs = [], []
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/*.pkl')):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float)
    Cs.append(C)
    g = np.atleast_1d(np.asarray(d['gold']).ravel())
    QGs.append((np.asarray(d['qC'], float), C[np.asarray(g, int)].mean(0), len(g)))
R = {'LME': summarize('LME', Cs, QGs)}

# PerLTQA (+sections)
pa = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl', 'rb'))
pq = pickle.load(open('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl', 'rb'))
archC = {c: np.asarray(pa[c]['C'], float) for c in pa}
sec = defaultdict(list)
for qid, q in pq.items():
    C = archC[q['char']]
    g = np.atleast_1d(np.asarray(q['gold']).ravel()).astype(int)
    sec[q['section']].append((np.asarray(q['qC'], float), C[g].mean(0), len(g)))
R['PerLTQA_all'] = summarize('PerLTQA', list(archC.values()),
                             [t for v in sec.values() for t in v])
for s, v in sec.items():
    chars = set(pq[q]['char'] for q in pq if pq[q]['section'] == s)
    R[f'PerLTQA_{s}'] = summarize(s, [archC[c] for c in chars], v)

# REALTALK
Cs, QGs = [], []
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr/RT*.pkl')):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
    Cs.append(C)
    for qi, gr in enumerate(d['gold_rows']):
        g = np.atleast_1d(np.asarray(gr).ravel()).astype(int)
        if len(g) == 0:
            continue  # 23/728 RT queries have empty gold; skipping (NaN fix)
        QGs.append((QC[qi], C[g].mean(0), len(g)))
R['REALTALK'] = summarize('REALTALK', Cs, QGs)

# LoCoMo
Cs, QGs = [], []
for f in sorted(glob.glob('/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/locomo_*.pkl')):
    d = pickle.load(open(f, 'rb'))
    C = np.asarray(d['C'], float); QC = np.asarray(d['QC'], float)
    m = d['id_to_row']; Cs.append(C)
    for qi, qa in enumerate(d['qas']):
        rows = [m[e] for e in qa['raw_evidence'] if e in m]
        if not rows:
            continue
        g = np.asarray(rows, int)
        QGs.append((QC[qi], C[g].mean(0), len(g)))
R['LoCoMo'] = summarize('LoCoMo', Cs, QGs)

json.dump(R, open(OUT, 'w'), indent=1)
for k, v in R.items():
    print(f"{k}: n_arch={v['n_arch']} n_q={v['n_q']} N~{v['N_mean']:.0f} ng={v['ngold_mean']:.2f} "
          f"alpha={v['alpha']:.2f} top16={v['top16_share']:.3f} effrank={v['eff_rank']:.1f} "
          f"kurt={v['kurt_med']:.2f} skew={v['skew_med']:.2f} rho={v['locus_rho']:+.3f} "
          f"rho_n={v['locus_rho_norm']:+.3f} sigT={v['sig_top']:+.4f} sigB={v['sig_bot']:+.4f} "
          f"|T|={v['abs_top']:.4f} |B|={v['abs_bot']:.4f}", flush=True)
print('wrote', OUT, flush=True)
