"""Synthetic design pilot for the coordinate-scale draft. No real corpus, no outcomes, no Task 4F1."""
import numpy as np

D96, NARCH, NDOC, NQ = 96, 40, 60, 8
TOPK = 3

def haar_q(rng, d):
    A = rng.standard_normal((d, d)); Q, R = np.linalg.qr(A)
    return Q * np.where(np.diag(R) < 0, -1.0, 1.0)[None, :]

def block(rng, b):
    R = np.zeros((D96, D96)); R[:b, :b] = haar_q(rng, b); R[b:, b:] = haar_q(rng, D96 - b); return R

def make_archive(rng, decay):
    """Anisotropic archive: variance decays over coordinate index; gold doc shares a query's latent."""
    sd = decay ** np.arange(D96)
    Y = rng.standard_normal((NDOC, D96)) * sd
    gold = rng.integers(0, NDOC, NQ)
    QY = Y[gold] + rng.standard_normal((NQ, D96)) * sd * 0.55   # noisy copy of the gold doc
    return Y, QY, gold, sd

def recall(C, QC, gold, T=None):
    if T is not None: C, QC = C @ T, QC @ T
    Db, Qb = C >= 0, QC >= 0
    hits = 0
    for i in range(len(Qb)):
        dist = np.count_nonzero(Db != Qb[i], axis=1)
        if gold[i] in np.argsort(dist, kind="stable")[:TOPK]: hits += 1
    return hits / len(Qb)

def scale_matrix(C, eps=1e-12):
    sd = C.std(axis=0)
    d = np.where(sd >= eps, 1.0 / np.maximum(sd, eps), 1.0)
    return np.diag(d), int((sd < eps).sum())

for decay in (0.97, 0.90):
    rng0 = np.random.default_rng(7)
    acc = {k: [] for k in ("NATIVE","SCALED_NATIVE","FULL","SCALED_FULL","B32","SCALED_B32")}
    ident_ok, degen = True, 0
    for a in range(NARCH):
        rng = np.random.default_rng(1000 + a)
        Y, QY, gold, _ = make_archive(rng, decay)
        mu = Y.mean(axis=0); C, QC = Y - mu, QY - mu
        Dm, nd = scale_matrix(C); degen += nd
        ident_ok &= np.array_equal((C @ Dm) >= 0, C >= 0) and np.array_equal((QC @ Dm) >= 0, QC >= 0)
        for s in range(5):
            r = np.random.default_rng(59001 + s)
            Qf = haar_q(r, D96)
            r2 = np.random.default_rng(59001 + s); Rb = block(r2, 32)
            acc["NATIVE"].append(recall(C, QC, gold))
            acc["SCALED_NATIVE"].append(recall(C @ Dm, QC @ Dm, gold))
            acc["FULL"].append(recall(C, QC, gold, Qf))
            acc["SCALED_FULL"].append(recall(C @ Dm, QC @ Dm, gold, Qf))
            acc["B32"].append(recall(C, QC, gold, Rb))
            acc["SCALED_B32"].append(recall(C @ Dm, QC @ Dm, gold, Rb))
    m = {k: float(np.mean(v)) for k, v in acc.items()}
    d_full = (m["SCALED_FULL"] - m["FULL"]) * 100
    d_blk  = (m["SCALED_B32"] - m["B32"]) * 100
    print(f"--- variance decay {decay} (CV(sd) high={decay<0.95}) ---")
    print(f"  sign(xD)=sign(x) identity holds exactly: {ident_ok}   degenerate coords: {degen}")
    print(f"  NATIVE {m['NATIVE']:.4f}   SCALED_NATIVE {m['SCALED_NATIVE']:.4f}  (must be equal: {abs(m['NATIVE']-m['SCALED_NATIVE'])<1e-15})")
    print(f"  FULL   {m['FULL']:.4f} -> SCALED_FULL {m['SCALED_FULL']:.4f}   delta_full  = {d_full:+.2f} pp")
    print(f"  B32    {m['B32']:.4f} -> SCALED_B32  {m['SCALED_B32']:.4f}   delta_block = {d_blk:+.2f} pp")
    print(f"  INTERACTION I = {d_full - d_blk:+.2f} pp")
