"""Own audit runner: T1 only from the isolated copy. No in-place execution."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
t0 = time.time()
import decision_tests_copy as dt
print(f"imported copy; OUT would be {dt.OUT}", flush=True)
res = dt.t1()
out = os.path.join(HERE, "T1_RERUN.json")
json.dump(res, open(out, "w"), indent=1)
print(f"WROTE {out} elapsed {time.time()-t0:.0f}s", flush=True)
for v, m in res["bm25_variants"].items():
    print(f"  BM25 {v:18s} Hit@10 {m['hit10']:6.2f}  FR@3 {m['fr3']:6.2f}", flush=True)
print(f"  strongest: {res['strongest_bm25']}", flush=True)
