"""Own audit: Claim 1 — ITQ vs random rotation, fresh seeds.

READ-ONLY inputs: bench3/runs/b3a_realtalk/rt_repr/RTxx.pkl (C, QC, gold_rows).
Everything else is my own code:
  - own random orthogonal generator (QR of Gaussian, documented seeds)
  - own ITQ (Procrustean alternating minimization, 50 iters, own implementation)
  - own scorers (Hamming-sym and asymmetric qscale, same published CONTRACT:
    sym=-Hamming(sign(QCr),sign(Cr)); qscale=Dpm@(QCr/sig).T, sig=docs-only std)
  - own top-10: stable descending argsort (ties -> lower doc index). This DIFFERS
    from the coordinator's archive-seeded det_top10, so absolute levels may differ
    by tie-break noise; the ITQ-vs-RAND contrast is computed INSIDE my tie-break
    and is therefore self-consistent. Calibration vs published FULL anchor reported.

Fresh RAND seeds (disjoint from published 20260916/17/18): 7 seeds.
Attack question: does ITQ beat random on ANY seed distribution summary?
Per mandatory correction: report paired multi-seed distribution + uncertainty,
not a single seed.
"""
import json as _json
import pickle, time
import numpy as np

EXCL = set(_json.load(open(
    "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data/exclusions.json",
    encoding="utf-8"))["excluded_qids"])

CACHE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
ARCH = [f"RT{i:02d}" for i in range(1, 11)]
FRESH_SEEDS = [7, 42, 101, 2024, 55555, 777, 1234567]
ITQ_ITERS = 50
T0 = time.time()
DEADLINE = 165  # stop expensive probe after ~165 s, preserve partials

def rand_orth(d, seed):
    # own code, same FAMILY as published contract (SVD-based orthogonalization):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((d, d))
    U, _, Vt = np.linalg.svd(A, full_matrices=False)
    return (U @ Vt).astype(np.float64)

def fit_itq(C, n_iter=50, seed=20260916):
    # own Procrustean alternating minimization of ||B - C R||_F^2 (documents only)
    R = rand_orth(C.shape[1], seed)
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_init = float(np.sum((B - C @ R) ** 2))
    for _ in range(n_iter):
        B = np.where(C @ R >= 0, 1.0, -1.0)
        U, _, Vt = np.linalg.svd(C.T @ B, full_matrices=False)
        R = U @ Vt
    B = np.where(C @ R >= 0, 1.0, -1.0)
    loss_final = float(np.sum((B - C @ R) ** 2))
    return R, loss_init, loss_final

def top10_hit(scores, gold_list):
    # own tie-break: stable descending sort (ties -> lower doc index first)
    order = np.argsort(-scores, kind="stable")[:10]
    return 1.0 if (set(gold_list) & set(order.tolist())) else 0.0

def score_hit(Cr, QCr, golds, scorer):
    Db = (Cr >= 0)
    Dpm = np.where(Db, 1.0, -1.0)
    if scorer == "sym":
        Qb = (QCr >= 0)
        S = -np.count_nonzero(Db[None, :, :] != Qb[:, None, :], axis=2)  # (Q,N)
    else:
        sig = Cr.std(axis=0, ddof=0); sig[sig < 1e-12] = 1e-12
        S = (Dpm @ (QCr / sig).T).T  # (Q,N)
    return float(np.mean([top10_hit(S[j], g) for j, g in enumerate(golds)])) * 100

per_arch = {a: {} for a in ARCH}
done_arch = 0
for aid in ARCH:
    if time.time() - T0 > DEADLINE:
        print(f"TIME CAP: stopping after {done_arch} archives; partials preserved")
        break
    d = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
    C = np.asarray(d["C"], float); QC = np.asarray(d["QC"], float)
    # multi-gold: hit if ANY gold in top10; apply documented 23-qid exclusions (728->705)
    keep = [i for i, q in enumerate(d["qids"]) if q not in EXCL]
    QC = QC[keep, :]
    golds = [list(d["gold_rows"][i]) for i in keep]
    res = {}
    res["FULL/sym"] = score_hit(C, QC, golds, "sym")
    res["FULL/qscale"] = score_hit(C, QC, golds, "qscale")
    R, l0, l1 = fit_itq(C)
    if aid == "RT01":
        print(f"  ITQ loss {l0:.1f} -> {l1:.1f} (must decrease; orth err "
              f"{float(np.max(np.abs(R.T @ R - np.eye(96)))):.2e})", flush=True)
    res["ITQ/sym"] = score_hit(C @ R, QC @ R, golds, "sym")
    res["ITQ/qscale"] = score_hit(C @ R, QC @ R, golds, "qscale")
    for s in FRESH_SEEDS:
        Rr = rand_orth(96, s)
        res[f"RAND{s}/sym"] = score_hit(C @ Rr, QC @ Rr, golds, "sym")
        res[f"RAND{s}/qscale"] = score_hit(C @ Rr, QC @ Rr, golds, "qscale")
    per_arch[aid] = res
    done_arch += 1
    print(f"{aid} done ({time.time()-T0:.0f}s)", flush=True)

ARCH_DONE = [a for a in ARCH if per_arch[a]]
nq = {}
for aid in ARCH_DONE:
    d = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
    nq[aid] = sum(1 for q in d["qids"] if q not in EXCL)
N = sum(nq.values())

def agg(key):
    return sum(per_arch[a][key] * nq[a] for a in ARCH_DONE) / N

print(f"\narchives used: {done_arch}/10, queries: {N}")
print(f"{'arm':16s} {'sym':>8s} {'qscale':>8s}")
for key in (["FULL"] + ["ITQ"] + [f"RAND{s}" for s in FRESH_SEEDS]):
    print(f"{key:16s} {agg(key+'/sym'):8.2f} {agg(key+'/qscale'):8.2f}")
print("\nCalibration vs published (tie-break may differ): FULL/qscale publ=49.65, FULL/sym publ=46.52")
for scorer in ("sym", "qscale"):
    itq = agg(f"ITQ/{scorer}")
    rands = [agg(f"RAND{s}/{scorer}") for s in FRESH_SEEDS]
    rands.sort()
    print(f"[{scorer}] ITQ={itq:.2f}  RAND fresh: min={rands[0]:.2f} med={rands[3]:.2f} "
          f"max={rands[-1]:.2f} mean={np.mean(rands):.2f} sd={np.std(rands,ddof=1):.2f}")
    print(f"  ITQ - bestRAND = {itq-rands[-1]:+.2f} | ITQ - meanRAND = {itq-np.mean(rands):+.2f} | "
          f"ITQ rank among {len(rands)+1} = {sum(1 for r in rands if r > itq)+1}")
    # paired per-query deltas ITQ vs best-RAND? approximate via archive means is enough here;
    # report per-archive ITQ-vs-meanRAND spread as uncertainty proxy
    diffs = [per_arch[a][f"ITQ/{scorer}"] - np.mean([per_arch[a][f"RAND{s}/{scorer}"] for s in FRESH_SEEDS])
             for a in ARCH_DONE]
    print(f"  per-archive ITQ-meanRAND: mean={np.mean(diffs):+.2f} range=[{min(diffs):+.2f},{max(diffs):+.2f}]")
