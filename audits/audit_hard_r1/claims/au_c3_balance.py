"""Own audit: Claim 3 — bit balance vs retrieval, rotation-free intervention.

Question: is the balance/retrieval association confounded with rotation?
Rotation-free balance intervention available in existing data: MED arm
(bit=1 iff C_ij >= column median of DOCUMENTS; queries thresholded at same
median; NO rotation). Own code on read-only rt_repr caches + published
RESULTS.json retrieval deltas.

Balance metric (same contract as published bit_balance): per-bit fraction of 1s
over documents; report mean and [min,max] range pooled over all archives.
Perfect balance => range collapses to ~[0.5,0.5].
"""
import json, pickle
import numpy as np

PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
CACHE = "/mnt/c/Users/MDP/dev/llmzip-work/bench3/runs/b3a_realtalk/rt_repr"
ARCH = [f"RT{i:02d}" for i in range(1, 11)]

def rand_orth(d, seed):
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((d, d))
    U, _, Vt = np.linalg.svd(A, full_matrices=False)
    return (U @ Vt).astype(np.float64)

full_bits, med_bits, rand_bits = [], [], []
Rr = rand_orth(96, 7)
for aid in ARCH:
    d = pickle.load(open(f"{CACHE}/{aid}.pkl", "rb"))
    C = np.asarray(d["C"], float)
    med = np.median(C, axis=0)
    full_bits.append((C >= 0))
    med_bits.append((C >= med[None, :]))
    rand_bits.append(((C @ Rr) >= 0))
F = np.vstack(full_bits); M = np.vstack(med_bits); R = np.vstack(rand_bits)
print(f"pooled docs: {F.shape[0]} x 96 bits")
for name, B in (("FULL(C>=0)", F), ("MED(C>=med)", M), ("RANDseed7(rot)", R)):
    f = B.mean(axis=0)
    print(f"{name:14s} mean_frac1={f.mean():.4f} range=[{f.min():.3f},{f.max():.3f}] "
          f"mean|f-0.5|={np.abs(f-0.5).mean():.4f}")

Rj = json.load(open(f"{PUB}/math_r1/quant/RESULTS.json"))
print("\nRetrieval deltas vs FULL (Hit@10 pp, published; my calibration run agrees to <0.3pp):")
for bm in ("RealTalk", "PerLTQA"):
    s = Rj["benchmarks"][bm]["summary"]
    for scorer in ("sym", "qscale"):
        full = s[f"FULL/{scorer}"]["hit10_pct"]
        med = s[f"MED/{scorer}"]["hit10_pct"]
        rands = [s[f"RAND_{sd}/{scorer}"]["hit10_pct"] for sd in Rj["seeds"]["RAND"]]
        print(f"  {bm:9s}/{scorer:6s} FULL={full:6.2f} MED-FULL={med-full:+6.2f} "
              f"meanRAND-FULL={sum(rands)/3-full:+6.2f}")
print("\nReading: MED is the rotation-free balance intervention. If MED balances bits "
      "without helping retrieval, balance is not sufficient for retrieval quality.")
