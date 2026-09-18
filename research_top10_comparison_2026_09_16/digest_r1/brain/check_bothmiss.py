"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
What does the sym+qscale both-miss set look like (RealTalk FULL)?
Join: repr per_query (FULL sym/qscale hit10) x coordinator banding x firststage
code_top500 pool. Reports: both-miss rate by band, and reachability
(gold in CODE top-100?) of the both-miss set.
"""
import json, math, os, re
from collections import defaultdict
import numpy as np

R = "/mnt/c/Users/MDP/dev/llmzip-work"
BRAIN = "/mnt/c/Users/MDP/dev/llmzip-work/top10_comparison_r1/digest_r1/brain"
OUT = BRAIN + "/check_bothmiss.json"
out = {"_label": "[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]"}
TOKEN = re.compile(r"[a-z0-9]+")

def toks(s):
    return set(TOKEN.findall((s or "").lower()))

# bands (coordinator recipe, tokenization 2)
RT_DATA = R + "/top10_comparison_r1/data"
bands = {}
for i in range(1, 11):
    D = json.load(open(os.path.join(RT_DATA, f"RT{i:02d}.json"), encoding="utf-8"))
    N = len(D["docs"])
    df = defaultdict(int)
    dt = []
    for d_ in D["docs"]:
        t = toks(d_.get("text"))
        dt.append(t)
        for w in t:
            df[w] += 1
    row_of = {d_["row"]: j for j, d_ in enumerate(D["docs"])}
    for q in D["queries"]:
        qt = toks(q.get("text"))
        best = -1.0
        for g in q.get("gold", []):
            j = row_of.get(g)
            if j is None:
                continue
            for w in (qt & dt[j]):
                best = max(best, math.log(N / df[w]))
        bands[q["qid"]] = ("no_shared" if best < 0 else "common" if best < 2
                           else "mid" if best < 4 else "rare")

# FULL sym/qscale hit10
hit = defaultdict(dict)
with open(R + "/top10_comparison_r1/math_r1/repr/per_query.jsonl", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if r.get("benchmark") == "RealTalk" and r.get("arm") == "FULL":
            hit[r["qid"]][r["scorer"]] = r["hit10"]

# pool reachability from firststage
pool = {}
with open(R + "/top10_comparison_r1/ideas_r1/firststage/per_query.jsonl", encoding="utf-8") as fh:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        if "code_top500" in r:
            gold = set(r["gold"])
            pool[r["qid"]] = {"in100": bool(gold & set(r["code_top500"][:100])),
                              "in500": bool(gold & set(r["code_top500"][:500]))}

by_band = defaultdict(lambda: {"n": 0, "both_miss": 0, "miss_in100": 0, "miss_out100": 0})
tot = bm = 0
for q, v in hit.items():
    if "sym" not in v or "qscale" not in v:
        continue
    b = bands.get(q, "?")
    tot += 1
    by_band[b]["n"] += 1
    if v["sym"] == 0 and v["qscale"] == 0:
        bm += 1
        by_band[b]["both_miss"] += 1
        if q in pool:
            if pool[q]["in100"]:
                by_band[b]["miss_in100"] += 1
            else:
                by_band[b]["miss_out100"] += 1
out["total"] = tot
out["both_miss"] = bm
out["both_miss_rate"] = round(100 * bm / tot, 2)
out["by_band"] = {k: dict(v) for k, v in by_band.items()}
# reachability of both-miss overall
mi = sum(v["miss_in100"] for v in by_band.values())
mo = sum(v["miss_out100"] for v in by_band.values())
out["bothmiss_reachability"] = {"in_top100": mi, "outside_top100": mo,
    "frac_unreachable_at_100": round(mo / bm, 3)}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out, indent=1))
