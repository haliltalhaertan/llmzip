#!/usr/bin/env python3
"""D4-LME: mirror pilot_corrections.py E4 section EXACTLY; gate on seeds 43001-43005, fresh 44001/44002."""
import json, pickle
from pathlib import Path
import numpy as np

WORK = Path("/mnt/c/Users/MDP/dev/llmzip-work")
PIL = WORK / "pilots" / "axis_attack_2026-09-12"
PKL_DIR = WORK / "regen" / "lme" / "cache_repr"
K, NT = 3, 20
GATE_SEEDS = [43001, 43002, 43003, 43004, 43005]
FRESH_SEEDS = [44001, 44002]

def stable_archive_seed(lex, t):
    return 5_100_000 + lex * 100_000 + t * 100

def met(idx, g):
    s = set(map(int, idx)); gg = set(map(int, g)); x = len(s & gg)
    return float(x > 0), float(x == len(gg) and len(gg) > 0), float(x / len(gg))

def hspec_qs(seed, b):
    r = np.random.default_rng(seed)
    r.permutation(96)
    qs = []
    for _ in range(96 // b):
        A = r.standard_normal((b, b))
        Q, R = np.linalg.qr(A)
        sg = np.where(np.diag(R) < 0, -1.0, 1.0)
        qs.append(Q * sg[None, :])
    return qs

def happly(X, perm, qs, b):
    xp = np.asarray(X, float)[..., perm]
    o = np.empty_like(xp)
    for j, Q in enumerate(qs):
        sl = slice(j * b, (j + 1) * b)
        o[..., sl] = xp[..., sl] @ Q
    return o

data = json.loads((WORK / "drive" / "longmemeval_s_cleaned.json").read_text())
lex = {q: i for i, q in enumerate(sorted(str(x["question_id"]) for x in data))}
del data
pkls = sorted(PKL_DIR.glob("*.pkl"))
assert len(pkls) == 470, len(pkls)
pilot = json.loads((PIL / "pilot_results.json").read_text())
nat_by_q = pilot["per_question_native_FR"]
nat = float(np.mean(list(nat_by_q.values())))
ref = json.loads((PIL / "pilot_results_corrections.json").read_text())
print(f"NATIVE_FR = {nat!r} ref = {ref['native_FR']!r} diff = {nat - ref['native_FR']!r}")

acc = {}
for s in GATE_SEEDS + FRESH_SEEDS:
    for arm in ["random", "matched", "antimatched"]:
        acc[f"E4_{arm}_{s}"] = []

for qi, p in enumerate(pkls):
    with open(p, "rb") as f:
        o = pickle.loads(f.read())
    qid = o["question_id"]; C = o["C"]; qC = o["qC"]; g = np.asarray(o["gold"]).ravel()
    n = len(C); D0 = C >= 0; Q0 = qC >= 0
    var = C.var(axis=0)
    rank_desc = np.argsort(var, kind="stable")[::-1]
    pr = [np.random.default_rng(stable_archive_seed(lex[qid], t) + 99).random(n) for t in range(NT)]
    for s in GATE_SEEDS + FRESH_SEEDS:
        qs = hspec_qs(s, 2)
        perms = {
            "random": np.random.default_rng(s).permutation(96),
            "matched": np.argsort(var, kind="stable"),
        }
        am = np.empty(96, dtype=int)
        am[0::2] = rank_desc[:48]; am[1::2] = rank_desc[::-1][:48]
        perms["antimatched"] = am
        for arm, perm in perms.items():
            Cr = happly(C, perm, qs, 2); qr = happly(qC, perm, qs, 2)
            d = np.count_nonzero((Cr >= 0) != (qr >= 0)[None, :], axis=1)
            acc[f"E4_{arm}_{s}"].append(float(np.mean([met(np.lexsort((pz, d))[:K], g)[2] for pz in pr])))
    if (qi + 1) % 100 == 0:
        print(f"  {qi+1}/470", flush=True)

e4 = {}
for s in GATE_SEEDS + FRESH_SEEDS:
    e4[str(s)] = {arm: {"FR": float(np.mean(acc[f"E4_{arm}_{s}"])),
                        "gap_pp": (float(np.mean(acc[f"E4_{arm}_{s}"])) - nat) * 100}
                  for arm in ["random", "matched", "antimatched"]}

print("---- gate: reproduce pilot E4_seeds5 (43001-43005) ----")
gate_ok = True
for s in GATE_SEEDS:
    for arm in ["random", "matched", "antimatched"]:
        got = e4[str(s)][arm]["FR"]
        exp = ref["E4_seeds5"][str(s)][arm]["FR"]
        d = got - exp
        ok = abs(d) <= 1e-12
        gate_ok = gate_ok and ok
        print(f"E4_{arm}_{s}: got={got!r} exp={exp!r} diff={d!r} {'PASS' if ok else 'FAIL'}")
print("LME_GATE_PASS" if gate_ok else "LME_GATE_FAIL")

for s in FRESH_SEEDS:
    print(f"FRESH {s}: " + " ".join(f"{a}={e4[str(s)][a]['FR']!r}({e4[str(s)][a]['gap_pp']:+.4f}pp)" for a in ["matched","random","antimatched"]))

mf = [e4[str(s)]["matched"]["FR"] for s in FRESH_SEEDS]
rf = [e4[str(s)]["random"]["FR"] for s in FRESH_SEEDS]
af = [e4[str(s)]["antimatched"]["FR"] for s in FRESH_SEEDS]
c1 = min(mf) > max(rf); c2 = min(rf) > max(af); c3 = min(mf) > max(af)
print(f"STRICT fresh LME: min(matched)={min(mf)!r} max(random)={max(rf)!r} min(random)={min(rf)!r} max(anti)={max(af)!r}")
print(f"  min(matched_fresh) > max(random_fresh): {c1}")
print(f"  min(random_fresh) > max(anti_fresh): {c2}")
print(f"  min(matched_fresh) > max(anti_fresh): {c3}")
mo = [e4[str(s)]["matched"]["FR"] for s in GATE_SEEDS[:3]]
ro = [e4[str(s)]["random"]["FR"] for s in GATE_SEEDS[:3]]
ao = [e4[str(s)]["antimatched"]["FR"] for s in GATE_SEEDS[:3]]
print(f"ORIG43001-03: min(matched)={min(mo)!r} > max(random)={max(ro)!r}: {min(mo)>max(ro)}; min(random) > max(anti)={max(ao)!r}: {min(ro)>max(ao)}")

out = {"native_FR": nat, "E4": e4, "gate_pass": bool(gate_ok),
       "fresh_strict": {"min_matched_gt_max_random": bool(c1), "min_random_gt_max_anti": bool(c2), "min_matched_gt_max_anti": bool(c3)}}
Path("/tmp/d4/d4_lme_details.json").write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
print("DETAILS_WRITTEN /tmp/d4/d4_lme_details.json")
print("FINAL_JSON_BEGIN")
print(json.dumps(out, sort_keys=True))
print("FINAL_JSON_END")
