"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Analyse INDUCTIVE_PERLTQA.json: pooled TRANS vs INDEP, archive-clustered bootstrap CI,
leak-vs-size correlation. Writes ANALYSIS.json; prints summary.
"""
import json

import numpy as np

HERE = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r3/leak_perltqa"
R = json.load(open(HERE + "/INDUCTIVE_PERLTQA.json"))
archs = sorted([k for k in R.keys()], key=lambda c: R[c]["idx"])
print(f"archives done: {len(archs)}/30")

# gates
td = sum(R[c]["gate_doc_sign_diffs"] for c in archs)
tt = sum(R[c]["gate_doc_total"] for c in archs)
qd = sum(R[c]["gate_q_sign_diffs"] for c in archs)
qt = sum(R[c]["gate_q_total"] for c in archs)
mpub = max(max(abs(v) for v in R[c]["trans_vs_published_deltas"].values()) for c in archs)
print(f"TRANS identity: doc signs {td}/{tt}, query signs {qd}/{qt}, max|TRANS-published|={mpub:.2e}")

CELLS = [("sym", "h10", "tir"), ("sym", "fr3", "tir"), ("qscale", "h10", "tir"), ("qscale", "fr3", "tir")]
KEYS = {"sym_h10": ("sym", "hit10"), "sym_fr3": ("sym", "fr3"),
        "q_h10": ("qscale", "hit10"), "q_fr3": ("qscale", "fr3")}

nq_tot = sum(R[c]["n_q"] for c in archs)
out = {"n_archives": len(archs), "n_queries": nq_tot,
       "gate_doc": [td, tt], "gate_q": [qd, qt], "max_pub_delta": mpub}

# pooled means (query-weighted = plain mean over queries)
for key, (sc, m) in KEYS.items():
    t = np.concatenate([[float(x) for x in R[c]["perq"][f"trans_{key}"]] for c in archs])
    i = np.concatenate([[float(x) for x in R[c]["perq"][f"indep_{key}"]] for c in archs])
    out[key] = {"trans": float(t.mean()), "indep": float(i.mean()),
                "leak_pp": float((t.mean() - i.mean()) * 100), "n": int(len(t))}

# archive-clustered bootstrap on paired per-query diffs (ablation.py style):
# multinomial(30) cluster multiplicities, 20000 reps, seed 20260916
rng = np.random.default_rng(20260916)
K = len(archs)
counts = rng.multinomial(K, [1 / K] * K, size=20000)
for key, (sc, m) in KEYS.items():
    cs = np.array([sum(float(a) - float(b) for a, b in
                       zip(R[c]["perq"][f"trans_{key}"], R[c]["perq"][f"indep_{key}"])) for c in archs])
    ns = np.array([R[c]["n_q"] for c in archs], dtype=float)
    boots = (counts[:, :K] @ cs) / (counts[:, :K] @ ns)
    lo, hi = np.quantile(boots, [0.025, 0.975])
    out[key].update({"ci_lo_pp": float(lo * 100), "ci_hi_pp": float(hi * 100),
                     "excludes_zero": bool(lo > 0 or hi < 0)})

for key in KEYS:
    d = out[key]
    print(f"{key}: TRANS={d['trans']*100:.2f} INDEP={d['indep']*100:.2f} "
          f"leak={d['leak_pp']:+.2f}pp CI95 [{d['ci_lo_pp']:+.2f},{d['ci_hi_pp']:+.2f}] "
          f"n={d['n']} {'SIG' if d['excludes_zero'] else 'ns'}")

# per-archive leak table + leak-vs-size correlation
print(f"\n{'archive':<16}{'N':>5}{'nq':>5} | {'symH10 leak':>11}{'symFR3 leak':>11}{'qH10 leak':>11}{'qFR3 leak':>11}")
leaks = {k: [] for k in KEYS}
Ns = []
for c in archs:
    row = {}
    for key, (sc, m) in KEYS.items():
        t = np.mean(R[c]["perq"][f"trans_{key}"])
        i = np.mean(R[c]["perq"][f"indep_{key}"])
        row[key] = (t - i) * 100
        leaks[key].append(row[key])
    Ns.append(R[c]["N"])
    print(f"{c:<16}{R[c]['N']:>5}{R[c]['n_q']:>5} | "
          f"{row['sym_h10']:>+11.2f}{row['sym_fr3']:>+11.2f}{row['q_h10']:>+11.2f}{row['q_fr3']:>+11.2f}")

Ns = np.array(Ns, dtype=float)
for key in KEYS:
    L = np.array(leaks[key])
    r = float(np.corrcoef(Ns, L)[0, 1])
    # Spearman via ranks
    ro = np.argsort(np.argsort(Ns)).astype(float)
    rl = np.argsort(np.argsort(L)).astype(float)
    rs = float(np.corrcoef(ro, rl)[0, 1])
    out[key].update({"leak_vs_N_pearson_r": r, "leak_vs_N_spearman_r": rs})
    print(f"{key}: leak-vs-N Pearson r={r:+.3f} Spearman r={rs:+.3f} "
          f"(N range {Ns.min():.0f}-{Ns.max():.0f}, median {np.median(Ns):.0f})")

json.dump(out, open(HERE + "/ANALYSIS.json", "w"), indent=2)
print("\nwrote ANALYSIS.json")
