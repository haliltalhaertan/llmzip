"""Coordinator independent check of the adversarial suite. Stdlib only, exact Fractions.
Does NOT import worker truth.py/oracle.py/validate.py. Writes JSON receipt."""
from fractions import Fraction as F
from pathlib import Path
import json, sys, subprocess, tempfile, os

ADV = Path.home()/"muse-work/geometry-cert-adversarial/research_representation_geometry_followup/adversarial"
OUT = Path("/mnt/c/Users/MDP/dev/llmzip-work/representation_geometry_fix")
OUT.mkdir(parents=True, exist_ok=True)
res = {}

# ---------- 1. my own comparator, written from the score definition ----------
def score(p, z):
    # score = num/sqrt(den); comparison must respect sign of num
    return (p[0] + p[1]*z, p[2] + p[3]*z)

def my_cmp(p, q, z):
    n1, d1 = score(p, z); n2, d2 = score(q, z)
    if d1 <= 0 or d2 <= 0:
        return None  # domain failure
    if n1 >= 0 and n2 < 0: return 1
    if n2 >= 0 and n1 < 0: return -1
    if n1 == 0 and n2 == 0: return 0
    # same sign: compare squares with sign correction
    lhs = n1*n1*d2; rhs = n2*n2*d1
    c = (lhs > rhs) - (lhs < rhs)
    return c if n1 >= 0 else -c

cases_doc = json.loads((ADV/"cases.json").read_text())
cases = cases_doc["cases"]
def frac4(v): return tuple(F(x) for x in v)

# 2. Independently recompute the frozen truth signs stored in cases.json
mismatch = []
checked_pts = 0
for c in cases:
    p = frac4(c["p"]); q = frac4(c["q"])
    for pt, expected in c.get("oracle", {}).get("truth", {}).items():
        got = my_cmp(p, q, F(pt))
        checked_pts += 1
        if got != expected:
            mismatch.append({"case": c["id"], "z": pt, "frozen": expected, "mine": got})
    # also re-derive the plus/minus flags the safety gate G1 depends on
    tv = {v for v in ((my_cmp(p, q, F(z))) for z in c.get("oracle", {}).get("truth", {}))}
    o = c.get("oracle", {})
    if "plus" in o and (1 in tv) != bool(o["plus"]):
        mismatch.append({"case": c["id"], "flag": "plus", "frozen": o["plus"]})
    if "minus" in o and (-1 in tv) != bool(o["minus"]):
        mismatch.append({"case": c["id"], "flag": "minus", "frozen": o["minus"]})
res["frozen_truth_points_checked"] = checked_pts
res["frozen_truth_mismatches"] = mismatch

# 3. the POC blocker, recomputed here
p = (F(-100), F(100), F(0), F(10000)); q = (F(-200), F(200), F(70000), F(0))
res["poc_truth"] = {str(z): my_cmp(p, q, F(z)) for z in ["5/4", "3/2", "7/4", "5/2", "4"]}
res["poc_varies"] = len({v for v in res["poc_truth"].values() if v != 0}) > 1

# 4. canary targets: does the suite reject cheats and accept honest ignorance?
canaries = {
  "always_strict": "from fractions import Fraction\ndef P4(*a):return tuple(Fraction(x) for x in a)\ndef certify_pair(p,q,L,R):return {'status':'STRICT','direction':1,'ties':[]}\n",
  "always_unresolved": "from fractions import Fraction\ndef P4(*a):return tuple(Fraction(x) for x in a)\ndef certify_pair(p,q,L,R):return {'status':'UNRESOLVED','direction':None,'ties':[]}\n",
  "v2_relabelled": ("import sys;sys.path.insert(0,%r)\nimport certify_v2 as _v\nP4=_v.P4\n"
      "def certify_pair(p,q,L,R):\n r=dict(_v.certify_pair(p,q,L,R))\n"
      " if r.get('status')=='ISOLATED_TIES':r['status']='SAFE_ISOLATED'\n return r\n")
      % str(Path.home()/"muse-work/geometry-cert-adversarial/research_representation_geometry_2026_09_13/repairs/rank_cert"),
}
env = dict(os.environ, OMP_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
res["canaries"] = {}
for name, src in canaries.items():
    f = Path(tempfile.gettempdir())/f"canary_{name}.py"; f.write_text(src)
    r = subprocess.run([sys.executable, "-B", "run_suite.py", "--target", str(f),
                        "--out", str(Path(tempfile.gettempdir())/f"res_{name}.json")],
                       cwd=ADV, capture_output=True, text=True, env=env)
    tail = [l for l in r.stdout.splitlines() if l.startswith("cases=")]
    res["canaries"][name] = {"exit": r.returncode, "summary": tail[-1] if tail else r.stdout[-200:]}

# 5. worker's own soundness tests, rerun by me
r = subprocess.run([sys.executable, "-B", "test_soundness.py"], cwd=ADV,
                   capture_output=True, text=True, env=env)
res["test_soundness_exit"] = r.returncode
res["test_soundness_tail"] = r.stdout.strip().splitlines()[-3:]

(OUT/"COORDINATOR_ADVERSARIAL_CHECK.json").write_text(json.dumps(res, indent=2, default=str))
print(json.dumps(res, indent=2, default=str))
