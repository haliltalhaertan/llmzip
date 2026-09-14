#!/usr/bin/env python3
# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Step 1: establish + PROVE the row<->turn mapping. No analysis yet.
import json, pickle, glob, os, sys
import numpy as np

BASE = "/mnt/c/Users/MDP/dev/llmzip-work"
OUT = BASE + "/agent_out/role-separation"

# ---------- LME ----------
items = sorted(glob.glob(BASE + "/regen/lme/items/*.json"))
caches = sorted(glob.glob(BASE + "/regen/lme/cache_repr/*.pkl"))
print("n_items", len(items), "n_caches", len(caches))

ex = pickle.load(open(caches[0], "rb"))
print("cache keys:", sorted(ex.keys()))
for k, v in ex.items():
    if isinstance(v, np.ndarray):
        print("  ", k, v.shape, v.dtype)
    else:
        print("  ", k, type(v).__name__, str(v)[:120])

# count match over ALL 470
mismatch = []
gold_mismatch = []
rows = []
for cp in caches:
    qid_file = os.path.basename(cp)[:-4]
    ip = BASE + "/regen/lme/items/" + qid_file + ".json"
    d = json.load(open(ip))
    n_turns = sum(len(s) for s in d["haystack_sessions"] if isinstance(s, list))
    C = ex if False else pickle.load(open(cp, "rb"))
    N = C["C"].shape[0]
    if N != n_turns:
        mismatch.append((qid_file, N, n_turns))
    # gold: has_answer turns in build_archive order
    order_gold = []
    idx = 0
    for s in d["haystack_sessions"]:
        if not isinstance(s, list):
            continue
        for t in s:
            if isinstance(t, dict) and bool(t.get("has_answer", False)):
                order_gold.append(idx)
            idx += 1
    cg = sorted(int(x) for x in np.asarray(C["gold"]).ravel())
    if cg != sorted(order_gold):
        gold_mismatch.append((qid_file, cg[:10], sorted(order_gold)[:10], len(cg), len(order_gold)))
    rows.append((qid_file, N, n_turns, len(cg), len(order_gold)))

print("LME count mismatches:", len(mismatch), mismatch[:5])
print("LME GOLD mismatches:", len(gold_mismatch), gold_mismatch[:3])
print("total rows LME:", sum(r[1] for r in rows))
print("total gold LME:", sum(r[3] for r in rows))

# centering check
c0 = pickle.load(open(caches[0], "rb"))["C"]
print("LME col-mean absmax:", float(np.abs(c0.mean(0)).max()))

# ---------- LoCoMo ----------
lp = sorted(glob.glob(BASE + "/regen/locomo/locomo_*.pkl"))
print("\nlocomo files", len(lp))
L = pickle.load(open(lp[0], "rb"))
print("locomo keys:", sorted(L.keys()))
for k, v in L.items():
    if isinstance(v, np.ndarray):
        print("  ", k, v.shape, v.dtype)
    elif isinstance(v, dict):
        ks = list(v.keys())[:6]
        print("  ", k, "dict n=", len(v), "sample keys", ks)
    elif isinstance(v, list):
        print("  ", k, "list n=", len(v), "first:", json.dumps(v[0])[:300] if v else "")
    else:
        print("  ", k, type(v).__name__, str(v)[:120])

for f in lp:
    L = pickle.load(open(f, "rb"))
    itr = L["id_to_row"]
    N = L["C"].shape[0]
    vals = sorted(itr.values())
    print(os.path.basename(f), "N=", N, "n_ids=", len(itr), "rows_contig=", vals == list(range(N)),
          "sample=", list(itr.items())[:3])
