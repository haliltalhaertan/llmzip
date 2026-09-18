"""Own audit: Claim 2 — rotation harm vs archive size r=-0.78.

Recomputes from PUBLISHED aggregates (math_r1/quant/RESULTS.json by_archive +
per-archive n_docs in the same file's meta is absent, so sizes come from
top10_comparison_r1/data/RT*.json doc counts). Read-only inputs.

Damage per archive = mean(RAND_qscale over 3 seeds) - FULL_qscale  (Hit@10, pp).
Also repeats with sym scorer and with each seed separately.
Reports Pearson r, Spearman rho, leave-one-out range, and drop-k worst cases.
"""
import json, math
import numpy as np

PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
DATA = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/data"

R = json.load(open(f"{PUB}/math_r1/quant/RESULTS.json"))
by = R["benchmarks"]["RealTalk"]["by_archive"]
SEEDS = R["seeds"]["RAND"]  # [20260916, 20260917, 20260918]

sizes, names = {}, {}
for i in range(1, 11):
    aid = f"RT{i:02d}"
    D = json.load(open(f"{DATA}/{aid}.json", encoding="utf-8"))
    sizes[aid] = len(D["docs"])
    names[aid] = aid

def dmg(arm_full, scorer):
    full = {a: by[f"FULL/{scorer}"][a]["hit10_pct"] for a in sizes}
    out = {}
    for a in sizes:
        rands = [by[f"RAND_{s}/{scorer}"][a]["hit10_pct"] for s in SEEDS]
        out[a] = (sum(rands) / len(rands)) - full[a]
    return out

def pearson(x, y):
    x = np.array(x, float); y = np.array(y, float)
    xm, ym = x - x.mean(), y - y.mean()
    return float(xm @ ym / math.sqrt((xm @ xm) * (ym @ ym)))

def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float)
    ry = np.argsort(np.argsort(y)).astype(float)
    return pearson(rx, ry)

print("archive sizes:", {a: sizes[a] for a in sorted(sizes)})
for scorer in ("qscale", "sym"):
    d = dmg(None, scorer)
    xs = [sizes[a] for a in sorted(sizes)]
    ys = [d[a] for a in sorted(sizes)]
    print(f"\n[{scorer}] per-archive damage (mean3RAND - FULL, Hit@10 pp):")
    for a in sorted(sizes):
        print(f"  {a} N={sizes[a]:5d} dmg={d[a]:+7.2f}")
    print(f"  Pearson r(size, dmg) = {pearson(xs, ys):+.4f}   (claimed -0.78)")
    print(f"  Spearman rho         = {spearman(xs, ys):+.4f}")
    # small vs large split from REPORT (N<700 vs N>=1000)
    sm = [d[a] for a in sizes if sizes[a] < 700]
    lg = [d[a] for a in sizes if sizes[a] >= 1000]
    print(f"  small(N<700,n={len(sm)}) mean dmg={np.mean(sm):+.2f} (claimed -6.56)")
    print(f"  large(N>=1000,n={len(lg)}) mean dmg={np.mean(lg):+.2f} (claimed -23.13)")
    # leave-one-out
    loo = []
    for drop in sorted(sizes):
        xs2 = [sizes[a] for a in sorted(sizes) if a != drop]
        ys2 = [d[a] for a in sorted(sizes) if a != drop]
        loo.append((drop, pearson(xs2, ys2), spearman(xs2, ys2)))
    loo.sort(key=lambda t: t[1])
    print("  LOO Pearson: min", f"{loo[0][0]}={loo[0][1]:+.4f}",
          " max", f"{loo[-1][0]}={loo[-1][1]:+.4f}")
    print("  LOO Spearman: min", f"{min(loo,key=lambda t:t[2])[0]}={min(loo,key=lambda t:t[2])[2]:+.4f}",
          " max", f"{max(loo,key=lambda t:t[2])[0]}={max(loo,key=lambda t:t[2])[2]:+.4f}")
    # drop-3 worst case: remove the 3 points most responsible (greedy: drop LOO-min driver iteratively)
    import itertools
    best = None
    for combo in itertools.combinations(sorted(sizes), 3):
        xs3 = [sizes[a] for a in sorted(sizes) if a not in combo]
        ys3 = [d[a] for a in sorted(sizes) if a not in combo]
        r = pearson(xs3, ys3)
        if best is None or abs(r) < abs(best[1]):
            best = (combo, r, spearman(xs3, ys3))
    print(f"  drop-3 weakest: drop {best[0]} -> Pearson {best[1]:+.4f}, Spearman {best[2]:+.4f} (n=7)")
    # per-seed Pearson (seed sensitivity of r itself)
    for s in SEEDS:
        ys_s = [by[f"RAND_{s}/{scorer}"][a]["hit10_pct"] - by[f"FULL/{scorer}"][a]["hit10_pct"]
                for a in sorted(sizes)]
        print(f"  seed {s}: Pearson {pearson(xs, ys_s):+.4f}  Spearman {spearman(xs, ys_s):+.4f}")
