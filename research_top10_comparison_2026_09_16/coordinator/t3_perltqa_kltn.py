"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

T3 — PerLTQA ladder with k < n enforced.

The incoming package reported a SIGNIFICANT decline 192->384 on PerLTQA
(qscale FR@3 52.98 -> 54.82 -> 51.87, 192->384 CI [-3.87,-2.01]). The coordinator traced
it to RANK OVERFLOW: 8 of 30 archives hold fewer than 384 documents
(293, 343, 359, 371, 376, 377, 380, 381), so surplus dimensions are constant-filled,
their sigma is ~0, and qscale divides by sigma. Unstandardized arms were immune.

This test rebuilds the ladder on those 8 archives with k_eff = min(k, n-1) and scores
BOTH a standardized arm (qscale) and an unstandardized one (asym), plus sym.

PRESPECIFIED READING, fixed before running:
  - If the decline DISAPPEARS under k_eff for the standardized arm  -> confirmed artifact;
    "quality stops improving after 24 B" was measured under a defect.
  - If the decline PERSISTS under k_eff on UNSTANDARDIZED arms      -> gate S3 of the
    referee's stopping rule fires: a real capacity law, and more bits genuinely do not help.
  - The unstandardized arms were already rising in the incoming data; if they keep rising
    while the corrected standardized arm also rises, the artifact explanation is complete.

Fidelity: rebuilds from the FROZEN PerLTQA builder (step2_build.py, LSA seed 5101,
SVD seed 5204) and gates the k=96 rebuild against the cached production C bit-for-bit
before any ladder number is written.
"""
import json, os, importlib.util, pickle, time
from collections import defaultdict

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

W = "/mnt/c/Users/MDP/dev/llmzip-work"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "T3_PERLTQA_KLTN.json")
B3 = f"{W}/bench3/runs/b3b_perltqa"

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

step2 = _load("step2", f"{B3}/step2_build.py")
lib = _load("lib", f"{W}/top10_comparison_r1/audit/audit_baseline_lib.py")

KS = [96, 192, 384]

def metrics(S, gold, arch):
    hit = fr3 = 0.0
    n = S.shape[0]
    for r in range(n):
        top = lib.det_top10(S[r], arch, 10)
        g = set(gold[r])
        hit += 1.0 if (g & set(top)) else 0.0
        fr3 += len(g & set(top[:3])) / len(g) if g else 0.0
    return 100 * hit / n, 100 * fr3 / n

def score_all(C, QC, gold, arch):
    out = {}
    B = np.where(C >= 0, 1.0, -1.0)
    QB = np.where(QC >= 0, 1.0, -1.0)
    out["sym"] = metrics(QB @ B.T, gold, arch)
    sigma = C.std(axis=0, ddof=0)
    sigma[sigma < 1e-12] = 1e-12
    out["qscale"] = metrics((QC / sigma) @ B.T, gold, arch)      # standardized
    out["asym"] = metrics(QC @ B.T, gold, arch)                  # UNstandardized
    return out

def main():
    t0 = time.time()
    arch_cache = pickle.load(open(f"{B3}/cache_arch_eval.pkl", "rb"))
    q_cache = pickle.load(open(f"{B3}/cache_q_eval.pkl", "rb"))

    small = sorted([a for a, v in arch_cache.items() if v["N"] < 384],
                   key=lambda a: arch_cache[a]["N"])
    print(f"archives with n<384: {len(small)}")
    for a in small:
        print(f"   {a:22s} n={arch_cache[a]['N']}")

    qs_by_arch = defaultdict(list)
    for qid, qv in q_cache.items():
        sec = qv.get("section")
        if sec in arch_cache:
            qs_by_arch[sec].append(qid)

    res = defaultdict(lambda: defaultdict(list))
    gate = {}
    items_fn = getattr(step2, "build_items", None)
    fit_fn = getattr(step2, "fit_archive", None)
    if items_fn is None or fit_fn is None:
        print("BLOCKER: step2_build.py does not expose build_items/fit_archive; "
              f"available: {[n for n in dir(step2) if not n.startswith('_')][:30]}")
        return

    for a in small:
        n = arch_cache[a]["N"]
        qids = sorted(qs_by_arch.get(a, []))
        if not qids:
            print(f"  SKIP {a}: no cached queries")
            continue
        try:
            items = items_fn(a)
            built = fit_fn(items)
        except Exception as e:
            print(f"  BLOCKER on {a}: {type(e).__name__}: {e}")
            continue
        Z = built["Z"] if isinstance(built, dict) and "Z" in built else built[0]
        Zq = built["Zq"] if isinstance(built, dict) and "Zq" in built else None
        gold = [q_cache[q]["gold"] for q in qids]

        arms = {}
        for k in KS:
            k_eff = min(k, n - 1, min(Z.shape) - 1)
            svd = TruncatedSVD(n_components=k_eff, random_state=5204)
            Y = normalize(svd.fit_transform(Z))
            mu = Y.mean(axis=0, keepdims=True)
            C = (Y - mu).astype(np.float64)
            QY = normalize(svd.transform(Zq)) if Zq is not None else None
            if QY is None:
                print(f"  BLOCKER on {a}: no query matrix from builder")
                break
            QC = (QY - mu).astype(np.float64)
            if k == 96:
                Cc = arch_cache[a]["C"]
                gate[a] = {"differing_bits": int(np.count_nonzero((C >= 0) != (Cc >= 0))),
                           "n_bits": int(C.size), "n": n}
            for sc, (h, f) in score_all(C, QC, gold, a).items():
                arms[f"k{k}({k_eff})/{sc}"] = {"hit10": h, "fr3": f, "k_eff": k_eff}
        for key, mv in arms.items():
            base = key.split("(")[0] + "/" + key.split("/")[1]
            res[base]["hit10"].append((mv["hit10"], len(qids)))
            res[base]["fr3"].append((mv["fr3"], len(qids)))
            res[base]["k_eff"].append(mv["k_eff"])
        print(f"  {a:22s} n={n} q={len(qids)} k_eff={sorted({v['k_eff'] for v in arms.values()})} "
              f"gate_diff={gate.get(a,{}).get('differing_bits','?')} {time.time()-t0:.0f}s", flush=True)

    if not res:
        print("NO RESULTS — builder interface mismatch; nothing written.")
        return

    def agg(key, m):
        vals = res[key][m]
        tot = sum(v[1] for v in vals)
        return sum(v[0] * v[1] for v in vals) / tot, tot

    print(f"\n{'arm':18s} {'k_eff used':>14s} {'Hit@10':>8s} {'FR@3':>8s}")
    out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]",
           "scope": "PerLTQA archives with n<384 only", "n_archives": len(small),
           "gate": gate, "arms": {}}
    for k in KS:
        for sc in ("sym", "qscale", "asym"):
            key = f"k{k}/{sc}"
            if key not in res:
                continue
            h, nq = agg(key, "hit10")
            f, _ = agg(key, "fr3")
            keff = sorted(set(res[key]["k_eff"]))
            out["arms"][key] = {"hit10": h, "fr3": f, "n_queries": nq, "k_eff": keff}
            print(f"{key:18s} {str(keff):>14s} {h:8.2f} {f:8.2f}")

    print("\n192 -> 384 change (the contested step):")
    for sc in ("qscale", "asym", "sym"):
        a1, a2 = f"k192/{sc}", f"k384/{sc}"
        if a1 in out["arms"] and a2 in out["arms"]:
            d = out["arms"][a2]["fr3"] - out["arms"][a1]["fr3"]
            std = "standardized" if sc in ("qscale", "sym") else "UNstandardized"
            print(f"  {sc:8s} ({std:14s}) FR@3 {d:+.2f} pp")
            out.setdefault("delta_192_384_fr3", {})[sc] = d

    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"\nWROTE {OUT}  elapsed {time.time()-t0:.0f}s")

if __name__ == "__main__":
    main()
