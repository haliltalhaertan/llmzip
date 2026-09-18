"""Own audit: Claim 1 (PerLTQA side) — ITQ vs random rotation, fresh seeds.

READ-ONLY inputs: bench3/runs/b3b_perltqa/cache_arch_eval.pkl (C per archive)
  + cache_q_eval.pkl (qC + gold per query, joined via 'char' field).
Own code throughout (same generators/scorers/top-10 as au_c1_itq.py).
Published anchors: FULL/qscale=80.00 Hit@10, ITQ_C/qscale=78.91,
  RAND mean(qscale)=(78.77+79.48+78.86)/3=79.04 -> ITQ-RAND=-0.13.
"""
import pickle, time
import numpy as np

ARCH_P = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_arch_eval.pkl"
Q_P = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3b_perltqa/cache_q_eval.pkl"
FRESH_SEEDS = [7, 42, 101, 2024, 55555, 777, 1234567]
T0 = time.time(); DEADLINE = 165

def rand_orth(d, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((d, d))
    U, _, Vt = np.linalg.svd(A, full_matrices=False)
    return (U @ Vt).astype(np.float64)

def fit_itq(C, n_iter=50, seed=20260916):
    R = rand_orth(C.shape[1], seed)
    for _ in range(n_iter):
        B = np.where(C @ R >= 0, 1.0, -1.0)
        U, _, Vt = np.linalg.svd(C.T @ B, full_matrices=False)
        R = U @ Vt
    return R

def top10_hit(scores, gold_list):
    order = np.argsort(-scores, kind="stable")[:10]
    return 1.0 if (set(int(g) for g in gold_list) & set(order.tolist())) else 0.0

def score_hit(Cr, QCr, golds, scorer):
    Db = (Cr >= 0)
    Dpm = np.where(Db, 1.0, -1.0)
    if scorer == "sym":
        Qb = (QCr >= 0)
        S = -np.count_nonzero(Db[None, :, :] != Qb[:, None, :], axis=2)
    else:
        sig = Cr.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
        S = (Dpm @ (QCr / sig).T).T
    return float(np.mean([top10_hit(S[j], golds[j]) for j in range(len(golds))])) * 100

arch = pickle.load(open(ARCH_P, "rb"))
qd = pickle.load(open(Q_P, "rb"))
by_arch = {}
for qk, v in qd.items():
    by_arch.setdefault(v["char"], []).append((qk, np.asarray(v["qC"], float),
                                              [int(g) for g in np.asarray(v["gold"]).ravel()]))
print(f"archives: {len(by_arch)}, queries: {sum(len(v) for v in by_arch.values())}")

per_arch, done = {}, 0
for ch in sorted(by_arch):
    if time.time() - T0 > DEADLINE:
        print(f"TIME CAP after {done} archives; partials preserved"); break
    if ch not in arch:
        print(f"  {ch}: NO C CACHE -> skipped"); continue
    C = np.asarray(arch[ch]["C"], float)
    qs = by_arch[ch]
    QC = np.stack([q[1] for q in qs])
    golds = [q[2] for q in qs]
    # guard: gold indices must fit N
    if max(max(g) for g in golds) >= C.shape[0]:
        print(f"  {ch}: gold index out of range (max gold {max(max(g) for g in golds)} vs N={C.shape[0]}) -> skipped")
        continue
    res = {"FULL/sym": score_hit(C, QC, golds, "sym"),
           "FULL/qscale": score_hit(C, QC, golds, "qscale")}
    R = fit_itq(C)
    res["ITQ/sym"] = score_hit(C @ R, QC @ R, golds, "sym")
    res["ITQ/qscale"] = score_hit(C @ R, QC @ R, golds, "qscale")
    for s in FRESH_SEEDS:
        Rr = rand_orth(96, s)
        res[f"RAND{s}/sym"] = score_hit(C @ Rr, QC @ Rr, golds, "sym")
        res[f"RAND{s}/qscale"] = score_hit(C @ Rr, QC @ Rr, golds, "qscale")
    per_arch[ch] = (res, len(qs)); done += 1
    if done % 10 == 0:
        print(f"  {done} archives ({time.time()-T0:.0f}s)", flush=True)

N = sum(n for _, n in per_arch.values())
def agg(key):
    return sum(r[key] * n for r, n in per_arch.values()) / N
print(f"\narchives used {len(per_arch)}, queries {N}")
print(f"{'arm':14s} {'sym':>8s} {'qscale':>8s}")
for key in (["FULL", "ITQ"] + [f"RAND{s}" for s in FRESH_SEEDS]):
    print(f"{key:14s} {agg(key+'/sym'):8.2f} {agg(key+'/qscale'):8.2f}")
print("Calibration vs published: FULL/qscale publ=80.00, FULL/sym publ=75.68, "
      "ITQ/qscale publ=78.91, RANDmean/qscale publ=79.04")
for scorer in ("sym", "qscale"):
    itq = agg(f"ITQ/{scorer}")
    rands = sorted(agg(f"RAND{s}/{scorer}") for s in FRESH_SEEDS)
    print(f"[{scorer}] ITQ={itq:.2f} RAND fresh min={rands[0]:.2f} med={rands[3]:.2f} "
          f"max={rands[-1]:.2f} mean={np.mean(rands):.2f} sd={np.std(rands,ddof=1):.2f}")
    print(f"  ITQ-bestRAND={itq-rands[-1]:+.2f} ITQ-meanRAND={itq-np.mean(rands):+.2f} "
          f"rank={sum(1 for r in rands if r>itq)+1}/8")
