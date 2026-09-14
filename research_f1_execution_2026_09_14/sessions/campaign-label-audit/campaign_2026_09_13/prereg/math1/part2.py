# ---------- LEVEL-2: binomial plug-in (independent-bits strawman) ----------
def plugin_frac_r3(d, gold, b, n_mc=3000, rng=None, k=K):
    """Independent-bits plug-in: non-gold distances iid ~ Binomial(b, phat),
    phat = empirical non-gold mean/b; gold distances fixed. E[exact formula]
    over multinomial (S,T) draws. Returns MC estimate."""
    d = np.asarray(d); g = np.asarray(g).ravel()
    n = len(d); mask = np.zeros(n, bool); mask[g] = True
    ng = d[~mask]; Np = len(ng)
    if Np == 0: return exact_frac_r3(d, gold, k)
    phat = float(ng.mean()) / b
    phat = min(max(phat, 1e-12), 1 - 1e-12)
    if rng is None: rng = np.random.default_rng(777)
    tot = 0.0
    # precompute binomial pmf values at needed points via log-comb loop
    from math import comb
    def binpmf(x):
        return comb(b, x) * (phat ** x) * ((1 - phat) ** (b - x))
    for gg in g:
        dg = int(d[int(gg)])
        Flo = sum(binpmf(x) for x in range(0, dg))
        Feq = binpmf(dg) if 0 <= dg <= b else 0.0
        draws = rng.multinomial(Np, [Flo, Feq, max(0.0, 1 - Flo - Feq)], size=n_mc)
        Sfix = int(np.count_nonzero(d[list(map(int, g))] < dg))
        Tfix = int(np.count_nonzero(d[list(map(int, g))] == dg))
        S = Sfix + draws[:, 0]; T = Tfix + draws[:, 1]
        p = np.where(S >= k, 0.0, np.where(S + T <= k, 1.0, (k - S) / np.maximum(T, 1)))
        tot += float(p.mean())
    return tot / len(g)

def hspec_qs_only(seed, b):
    r = np.random.default_rng(seed); r.permutation(96); qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b)); Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0); qs.append(Q * sg[None, :])
    return qs

def happly(X, perm, qs, b):
    xp = np.asarray(X, float)[..., perm]; o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b); o[..., sl] = xp[..., sl] @ Q
    return o

def load_all():
    t0 = time.time()
    qsorted = json.loads((BUNDLE/'protocol_sources/qids_500_sorted.json').read_text())
    assert len(qsorted) == 500
    lex = {q: i for i, q in enumerate(qsorted)}
    pkls = sorted(glob.glob(str(PKLDIR/'*.pkl')))
    assert len(pkls) == 470, len(pkls)
    D0, Q0, GOLD, PR, QIDS, VAR = {}, {}, {}, {}, [], {}
    for p in pkls:
        with open(p, 'rb') as f: o = pickle.load(f)
        qid = str(o['question_id'])
        C = np.asarray(o['C'], float); qC = np.asarray(o['qC'], float)
        g = np.asarray(o['gold']).ravel()
        D = C >= 0; Q = qC >= 0
        D0[qid] = D; Q0[qid] = Q; GOLD[qid] = g; QIDS.append(qid)
        VAR[qid] = np.asarray(o['C'], float).var(axis=0)
        lx = lex[qid]
        PR[qid] = [np.random.default_rng(stable_archive_seed(lx, t) + 99).random(len(C)) for t in range(NT)]
    print(f'loaded 470 pkls in {time.time()-t0:.0f}s', flush=True)
    return lex, D0, Q0, GOLD, PR, QIDS, VAR
