# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""F1 competition metric — independent implementation from the SPEC text.

Written SOLELY from:
  origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:.../R2_COMPETITION_RERUN_CONTRACT.md
  origin/research/e1-v2-raw-cache-recovery-r2-2026-09-13:.../E1_PREANALYSIS_SPEC_V2.md
The auditor's competition_variants.py was read only AFTER this spec was fixed,
for the line-by-line comparison in F1_EXECUTION_REPORT.md. Nothing is imported
from any lead/auditor module. Stdlib only — no numpy/scipy dependency.

Conventions (contract-literal):
  v_j = mean_i(C_ij^2); order = STABLE DESCENDING sort of v;
  TOP k = first k axes; BOT k = last k axes (contract: k=64 of D=96;
  k is a parameter here so hand-computed small-D fixtures can exercise the
  identical code path).
  bit(i,j) = 1 iff C[i][j] >= 0; qbit(j) = 1 iff qC[j] >= 0.
  d_A[i] = Hamming distance on arm A's axes.
  strict_all(A,g)  = #{i : d_A[i] < d_A[g]}          (all rows)
  tie_all(A,g)     = #{i : d_A[i] == d_A[g]}         (all rows; includes g)
  strict_ng(A,g)   = #{i not in G : d_A[i] < d_A[g]} (non-gold competitors)
  tie_ng(A,g)      = #{i not in G : d_A[i] == d_A[g]}
  STRICT_A_q = mean_g strict_all(A,g)  (etc.); GAP = TOP - BOT.
  min-gold (FORBIDDEN as metric; implemented ONLY as bug-reproduction control):
    dmin_A = min_{g in G} d_A[g]; counted ONCE per query over all rows.
Spearman: average ranks (1-based), Pearson on ranks; None when undefined.
Bootstrap: seed 96013, B=2000 default, cluster-level resampling with
  replacement, percentile 2.5/97.5, full attempted/valid/invalid ledger.
"""

import math
import random

# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def col_mean_squares(C):
    """v_j = mean_i(C_ij^2). C is a list of n rows of D floats."""
    n = len(C)
    if n == 0:
        raise ValueError("empty archive matrix")
    d = len(C[0])
    v = [0.0] * d
    for row in C:
        if len(row) != d:
            raise ValueError("ragged archive matrix")
        for j, x in enumerate(row):
            v[j] += x * x
    return [s / n for s in v]


def topbot_axes(v, k=64):
    """Stable DESCENDING order of v; first k axes TOP, last k axes BOT.

    Python's sorted() is stable, so sorting indices by (-value) keeps the
    original axis order among exact ties — the literal contract reading.
    """
    if k > len(v) or k < 1:
        raise ValueError("k out of range")
    # NOTE: the contract takes first-k AND last-k of 96, so TOP64/BOT64
    # overlap in the middle 32 axes by construction (the audit independently
    # records topbot_overlap_values [32] on all 520 archives).
    order = sorted(range(len(v)), key=lambda j: -v[j])
    return order[:k], order[-k:]


def hamming_distances(C, qC, axes):
    """Hamming distance of each archive row to the query on `axes`."""
    qb = [1 if qC[j] >= 0 else 0 for j in axes]
    out = []
    for row in C:
        out.append(sum(1 for t, j in enumerate(axes)
                       if (1 if row[j] >= 0 else 0) != qb[t]))
    return out


def _unique_gold(gold, n):
    g = sorted(set(int(x) for x in gold))
    if not g:
        raise ValueError("empty gold set")
    if g[0] < 0 or g[-1] >= n:
        raise ValueError("gold index out of range")
    return g


def competition_row(d_top, d_bot, gold):
    """One query -> full metric row (primary + sensitivity + bug control).

    Returns dict with per-arm means and TOP-BOT gaps:
      strict_top/bot, tie_top/bot            (primary, all rows, per-gold mean)
      strict_top_ng/bot_ng, tie_top_ng/bot_ng (sensitivity, non-gold mask)
      strict_gap, tie_gap, strict_gap_ng, tie_gap_ng
      min_strict_gap, min_tie_gap             (FORBIDDEN bug variant, control)
      gold_n
    """
    n = len(d_top)
    if len(d_bot) != n:
        raise ValueError("arm length mismatch")
    G = _unique_gold(gold, n)
    gset = set(G)
    m = len(G)

    def per_arm(d):
        s_all = t_all = s_ng = t_ng = 0.0
        for g in G:
            dg = d[g]
            a_s = a_t = ng_s = ng_t = 0
            for i, di in enumerate(d):
                if di < dg:
                    a_s += 1
                    if i not in gset:
                        ng_s += 1
                elif di == dg:
                    a_t += 1
                    if i not in gset:
                        ng_t += 1
            s_all += a_s
            t_all += a_t
            s_ng += ng_s
            t_ng += ng_t
        dmin = min(d[g] for g in G)
        min_s = sum(1 for di in d if di < dmin)
        min_t = sum(1 for di in d if di == dmin)
        return (s_all / m, t_all / m, s_ng / m, t_ng / m, min_s, min_t)

    sT, tT, sTng, tTng, mTs, mTt = per_arm(d_top)
    sB, tB, sBng, tBng, mBs, mBt = per_arm(d_bot)
    return {
        "gold_n": m,
        "strict_top": sT, "tie_top": tT,
        "strict_bot": sB, "tie_bot": tB,
        "strict_top_ng": sTng, "tie_top_ng": tTng,
        "strict_bot_ng": sBng, "tie_bot_ng": tBng,
        "strict_gap": sT - sB, "tie_gap": tT - tB,
        "strict_gap_ng": sTng - sBng, "tie_gap_ng": tTng - tBng,
        "min_strict_gap": float(mTs - mBs), "min_tie_gap": float(mTt - mBt),
    }


def query_row(C, qC, gold, delta, k=64, qid=None, benchmark=None,
              cluster=None, section=None):
    """Full per-query row: geometry + distances + competition + Delta."""
    v = col_mean_squares(C)
    top, bot = topbot_axes(v, k)
    row = competition_row(hamming_distances(C, qC, top),
                          hamming_distances(C, qC, bot), gold)
    row.update({"qid": qid, "benchmark": benchmark, "cluster": cluster,
                "section": section, "delta": float(delta)})
    return row

# --------------------------------------------------------------------------
# average-rank Spearman (frozen convention)
# --------------------------------------------------------------------------

def average_ranks(xs):
    """1-based average ranks with ties averaged. Non-finite -> None entry."""
    n = len(xs)
    order = sorted((x, i) for i, x in enumerate(xs)
                   if isinstance(x, (int, float)) and math.isfinite(x))
    ranks = [None] * n
    pos = 0
    while pos < len(order):
        end = pos
        while end + 1 < len(order) and order[end + 1][0] == order[pos][0]:
            end += 1
        avg = (pos + 1 + end + 1) / 2.0  # 1-based positions pos+1..end+1
        for t in range(pos, end + 1):
            ranks[order[t][1]] = avg
        pos = end + 1
    return ranks


def spearman_rho(xs, ys):
    """Average-rank Spearman; None when undefined (<2 valid pairs or a
    constant rank vector). Non-finite pairs are dropped (documented)."""
    if len(xs) != len(ys):
        raise ValueError("length mismatch")
    pairs = [(x, y) for x, y in zip(xs, ys)
             if isinstance(x, (int, float)) and isinstance(y, (int, float))
             and math.isfinite(x) and math.isfinite(y)]
    if len(pairs) < 2:
        return None
    rx = average_ranks([p[0] for p in pairs])
    ry = average_ranks([p[1] for p in pairs])
    n = len(pairs)
    mx = sum(rx) / n
    my = sum(ry) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


def benchmark_summary(rows, strict_key="strict_gap", tie_key="tie_gap"):
    """n, multi-gold n/rate, rho(Delta, strict gap), rho(Delta, tie gap)."""
    deltas = [r["delta"] for r in rows]
    return {
        "n": len(rows),
        "multi_gold_n": sum(1 for r in rows if r["gold_n"] > 1),
        "multi_gold_rate": (sum(1 for r in rows if r["gold_n"] > 1) / len(rows)
                            if rows else 0.0),
        "rho_strict": spearman_rho(deltas, [r[strict_key] for r in rows]),
        "rho_tie": spearman_rho(deltas, [r[tie_key] for r in rows]),
    }

# --------------------------------------------------------------------------
# headline gates + descriptive cluster bootstrap (contract C3/C8)
# --------------------------------------------------------------------------

HEADLINE_GATES = {
    # benchmark: (SIGN, centered float); LoCoMo float is the frozen-cache
    # candidate, not an old accepted anchor (contract binding side-condition).
    "LME": (0.5419751773049645, 0.4415957446808511),
    "REALTALK": (0.22477507598784194, 0.17253405381064954),
    "PERLTQA": (0.488941994930817, 0.551692074528853),
    "LOCOMO": (0.23654714666441054, 0.16826334541318252),
}


def check_headline_gates(sign_means, float_means, tol=1e-12):
    """sign_means/float_means: {benchmark: mean}. Returns {bm: (ok, detail)}."""
    out = {}
    for bm, (s_ref, f_ref) in HEADLINE_GATES.items():
        s, f = sign_means.get(bm), float_means.get(bm)
        if s is None or f is None:
            out[bm] = (False, "missing benchmark mean")
            continue
        ds, df = abs(s - s_ref), abs(f - f_ref)
        out[bm] = (ds <= tol and df <= tol,
                   "dsign=%.3g dfloat=%.3g tol=%g" % (ds, df, tol))
    return out


def cluster_bootstrap(rows, keys=("strict_gap", "tie_gap"), seed=96013,
                      n_boot=2000, cluster_key="cluster"):
    """Descriptive/post-hoc cluster bootstrap over per-query rows.

    Resamples CLUSTERS with replacement (queries inherit their cluster's draw
    count; a query without cluster id forms its own singleton cluster).
    Recomputes average-rank Spearman of Delta vs each key per replicate.
    Returns {key: {'interval_95': (lo, hi) or (None, None), 'attempted': B,
    'valid': v, 'invalid': i, 'invalid_reasons': {reason: count}}}.
    Labels: DESCRIPTIVE/POST-HOC, NOT preregistered inference.
    """
    clusters = {}
    for idx, r in enumerate(rows):
        c = r.get(cluster_key, None)
        clusters.setdefault(("__q_%d" % idx if c is None else c), []).append(idx)
    names = sorted(clusters)
    rng = random.Random(seed)
    result = {}
    for key in keys:
        vals, reasons = [], {}
        for _ in range(n_boot):
            draws = [rng.choice(names) for _ in names]
            idxs = [i for c in draws for i in clusters[c]]
            rho = spearman_rho([rows[i]["delta"] for i in idxs],
                               [rows[i][key] for i in idxs])
            if rho is None:
                reasons["undefined_spearman"] = reasons.get(
                    "undefined_spearman", 0) + 1
            else:
                vals.append(rho)
        vals.sort()
        if vals:
            lo = vals[min(len(vals) - 1, int(0.025 * len(vals)))]
            hi = vals[min(len(vals) - 1, int(0.975 * len(vals)))]
            interval = (lo, hi)
        else:
            interval = (None, None)
        result[key] = {"label": "descriptive/post-hoc percentile interval",
                       "interval_95": interval, "attempted": n_boot,
                       "valid": len(vals),
                       "invalid": n_boot - len(vals),
                       "invalid_reasons": reasons}
    return result
