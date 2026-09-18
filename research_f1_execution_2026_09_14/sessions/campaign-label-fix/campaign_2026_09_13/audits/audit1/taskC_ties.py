#!/usr/bin/env python3
"""[LOCAL AUDIT] Task C — (1) real tie-share stats from committed T4C2 diagnostics;
(2) synthetic validation mc-20 ~= FR_exp using FROZEN rank/tie machinery."""
import csv, json
import numpy as np

# ---------- Part 1: real committed tie diagnostics (LME, SIGN96 + ITQ96) ----------
TIE = "/home/mdp/muse-work/llmzip-audit/docs/v52/task4c2/V52_T4C2_tie_diagnostics.csv"
rows = [r for r in csv.DictReader(open(TIE)) if r["question_id"] != "__SUMMARY__"]
sign = [r for r in rows if r["method"] == "SIGN96_CENTERED"]
itq = [r for r in rows if r["method"] == "ITQ96_CENTERED"]
print(f"SIGN rows={len(sign)} ITQ rows={len(itq)}")
def frac(xs): return sum(xs)/len(xs)
s_tie = [float(r["top3_boundary_tie"]) for r in sign]
s_cand = [float(r["candidates_at_top3_boundary_distance"]) for r in sign]
s_slots = [float(r["slots_remaining_at_boundary"]) for r in sign]
s_min = [float(r["candidates_at_min_distance"]) for r in sign]
print(f"SIGN96: boundary-tie question share = {frac(s_tie):.4f} ({int(sum(s_tie))}/{len(sign)})")
print(f"SIGN96: mean candidates@boundary={np.mean(s_cand):.3f} p50={np.median(s_cand)} p90={np.quantile(s_cand,.9)} max={np.max(s_cand)}")
print(f"SIGN96: mean slots_remaining={np.mean(s_slots):.3f}; min-dist tie share={frac([v>1 for v in s_min]):.4f}")
i_tie = [float(r["top3_boundary_tie"]) for r in itq]
i_cand = [float(r["candidates_at_top3_boundary_distance"]) for r in itq]
print(f"ITQ96(all seeds): boundary-tie row share = {frac(i_tie):.4f}; mean cand@boundary={np.mean(i_cand):.3f} max={np.max(i_cand)}")

# ---------- Part 2: frozen machinery, mirrored EXACTLY ----------
# v52_t4c2_centering_geometry.py lines 69/74/75 + adapter stable_archive_seed (lines 125-132)
def metrics3(indices, gold_rows):
    s = set(map(int, indices)); g = set(map(int, gold_rows)); hit = len(s & g)
    return float(hit > 0), float(hit == len(g) and len(g) > 0), float(hit / len(g)) if g else np.nan
def rank_hamming(dist, priority): return np.lexsort((priority, np.asarray(dist)))
def rank_float(scores, priority): return np.lexsort((priority, -np.asarray(scores, dtype=np.float64)))
def stable_archive_seed(lexical_ordinal, trial=0):
    return 5_100_000 + lexical_ordinal * 100_000 + trial * 100

def conventions(a, t, K=3):
    FR_pess = 1.0 if (a + t <= K - 1) else 0.0
    FR_exp = min(1.0, (K - a) / (t + 1)) if a <= K - 1 else 0.0
    FR_opt = 1.0 if a <= K - 1 else 0.0
    return FR_pess, FR_exp, FR_opt

# Synthetic single-gold questions: N items, gold index 0 with distance dg;
# a items strictly closer; tie group of size t+1 at dg (gold + t others); rest strictly farther.
rng = np.random.default_rng(20260913)
K = 3
cases = []
for N in [50, 200, 500]:
    for a in [0, 1, 2, 3, 5, 10]:
        for t in [0, 1, 2, 4, 9, 19, 49]:
            if a + t + 1 <= N:
                cases.append((N, a, t))
print(f"synthetic single-gold cases: {len(cases)}")
per_q = []
for qi, (N, a, t) in enumerate(cases):
    dist = np.empty(N, dtype=float)
    dg = 30.0
    dist[0] = dg
    closer = rng.choice(np.arange(1, N), size=a, replace=False) if a else np.array([], dtype=int)
    dist[closer] = rng.integers(0, int(dg), size=a) if a else np.array([])
    pool = np.setdiff1d(np.arange(1, N), closer)
    tied = rng.choice(pool, size=t, replace=False) if t else np.array([], dtype=int)
    dist[tied] = dg
    rest = np.setdiff1d(pool, tied)
    dist[rest] = dg + 1 + rng.integers(0, 20, size=len(rest))
    # a,t as the brief defines (t excludes gold)
    a_obs = int(np.sum(dist[1:] < dg) + 0)  # gold is idx0; strictly closer among others
    # careful: closer[] all < dg by construction; tied == dg; rest > dg
    assert a_obs == a, (a_obs, a)
    t_obs = int(np.sum(dist[1:] == dg))
    assert t_obs == t, (t_obs, t)
    FR_pess, FR_exp, FR_opt = conventions(a, t)
    # frozen mc-20: 20 trials, priority=rng(seed+99).random(N)
    fr = []
    for tr in range(20):
        seed = stable_archive_seed(qi, tr)
        priority = np.random.default_rng(seed + 99).random(N)
        top3 = rank_hamming(dist, priority)[:K]
        fr.append(metrics3(top3, [0])[2])
    mc20 = float(np.mean(fr))
    per_q.append({"qid": f"syn_{qi}", "N": N, "a": a, "t": t,
                  "FR_pess": FR_pess, "FR_exp": FR_exp, "FR_opt": FR_opt,
                  "mc20": mc20, "diff_mc_minus_exp": mc20 - FR_exp})

diffs = np.array([q["diff_mc_minus_exp"] for q in per_q])
print(f"mc20 vs FR_exp: n={len(diffs)} max|diff|={np.max(np.abs(diffs)):.4f} "
      f"mean|diff|={np.mean(np.abs(diffs)):.4f} mean(diff)={np.mean(diffs):+.4f}")
# systematic pattern: bias vs tie size
for t in sorted(set(q["t"] for q in per_q)):
    d = np.array([q["diff_mc_minus_exp"] for q in per_q if q["t"] == t])
    print(f"  t={t:3d}: n={len(d):3d} mean(diff)={np.mean(d):+.4f} max|diff|={np.max(np.abs(d)):.4f}")
# tolerance logic: mc-20 is a Monte-Carlo mean of Bernoulli(p=FR_exp); SE<=sqrt(.25/20)=0.1118
print("tolerance logic: per-question mc-20 SE <= sqrt(0.25/20) = 0.1118 (Bernoulli worst case); "
      "no systematic bias expected since priorities are i.i.d. continuous.")

# continuous-score arm with exact ties (mirrors float ranking path)
q2 = []
for qi in range(60):
    N = 300
    a = int(rng.integers(0, 4)); t = int(rng.choice([0, 1, 3, 8, 25]))
    if a + t + 1 > N: continue
    sg = 0.7
    scores = np.empty(N); scores[0] = sg
    closer = rng.choice(np.arange(1, N), size=a, replace=False) if a else np.array([], dtype=int)
    scores[closer] = sg + 0.01 * rng.random(a)
    pool = np.setdiff1d(np.arange(1, N), closer)
    tied = rng.choice(pool, size=t, replace=False) if t else np.array([], dtype=int)
    scores[tied] = sg
    rest = np.setdiff1d(pool, tied)
    scores[rest] = sg - 0.01 * rng.random(len(rest)) - 0.001
    FR_pess, FR_exp, FR_opt = conventions(a, t)
    fr = []
    for tr in range(20):
        seed = stable_archive_seed(1000 + qi, tr)
        priority = np.random.default_rng(seed + 99).random(N)
        top3 = rank_float(scores, priority)[:K]
        fr.append(metrics3(top3, [0])[2])
    mc20 = float(np.mean(fr))
    q2.append({"qid": f"synf_{qi}", "N": N, "a": a, "t": t,
               "FR_pess": FR_pess, "FR_exp": FR_exp, "FR_opt": FR_opt,
               "mc20": mc20, "diff_mc_minus_exp": mc20 - FR_exp})
d2 = np.array([q["diff_mc_minus_exp"] for q in q2])
print(f"float-path: n={len(d2)} max|diff|={np.max(np.abs(d2)):.4f} mean|diff|={np.mean(np.abs(d2)):.4f} mean(diff)={np.mean(d2):+.4f}")

json.dump({"hamming_single_gold": per_q, "float_single_gold": q2},
          open("/tmp/audit1/taskC_synthetic_perq.json", "w"), indent=1)
# real per-question boundary-tie rows for details.json
real = [{"question_id": r["question_id"], "method": r["method"], "itq_seed": r["itq_seed"],
         "N_archive": int(float(r["N_archive"])),
         "top3_boundary_distance": float(r["top3_boundary_distance"]),
         "candidates_at_top3_boundary_distance": float(r["candidates_at_top3_boundary_distance"]),
         "slots_remaining_at_boundary": float(r["slots_remaining_at_boundary"]),
         "top3_boundary_tie": float(r["top3_boundary_tie"])} for r in rows]
json.dump(real, open("/tmp/audit1/taskC_real_boundary_ties.json", "w"), indent=1)
print("wrote /tmp/audit1/taskC_synthetic_perq.json + /tmp/audit1/taskC_real_boundary_ties.json")
