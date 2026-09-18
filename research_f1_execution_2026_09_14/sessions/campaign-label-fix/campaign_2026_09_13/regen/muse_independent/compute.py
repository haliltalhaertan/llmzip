import sys, pickle, json, hashlib, platform
sys.path.insert(0, "/mnt/c/Users/MDP/dev/llmzip-work/harness/ref")
import numpy as np
import measure_representation_diagnostics as m
print("frozen module:", m.__file__)
print("python", platform.python_version(), "numpy", np.__version__)
print("controls:", m.controls())
from pathlib import Path
lme_dir = Path("/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr")
loc_dir = Path("/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo")
lme_files = sorted(lme_dir.glob("*.pkl"))
loc_files = sorted(loc_dir.glob("locomo_*.pkl"))
print("n_lme", len(lme_files), "n_loc", len(loc_files))

def per_archive(C):
    d = m.matrix_diagnostics(np.asarray(C, dtype=np.float64))
    cp = d["correlation_proxy"]
    return {
        "sign_entropy_ge": d["sign_entropy_ge"],
        "sign_entropy_gt": d["sign_entropy_gt"],
        "zero_mass": d["zero_mass"],
        "cv_sigma": d["cv_sigma"],
        "D4_off_mass": cp["off_mass"] if cp else None,
        "D4_median_abs": cp["median_abs"] if cp else None,
        "D4_p95_abs": cp["p95_abs"] if cp else None,
        "residual_mean_max_abs": d["residual_mean_max_abs"],
        "active": d["active_coordinates"],
    }

def summarize(vals):
    a = np.array([v for v in vals if v is not None], dtype=np.float64)
    return {"n_valid": int(len(a)), "n_missing": int(len(vals)-len(a)),
            "mean": float(a.mean()) if len(a) else None,
            "sd_ddof1": float(a.std(ddof=1)) if len(a)>1 else None,
            "min": float(a.min()) if len(a) else None,
            "max": float(a.max()) if len(a) else None}

def run(files, key):
    rows = []
    for f in files:
        dd = pickle.load(open(f,"rb"))
        C = np.asarray(dd["C"], dtype=np.float64)
        assert C.ndim==2 and C.shape[1]==96 and C.dtype==np.float64, (f, C.shape)
        r = per_archive(C)
        r["id"] = dd.get("question_id", dd.get("conv_id", f.stem))
        r["N"] = int(C.shape[0])
        rows.append(r)
    keys = ["sign_entropy_ge","sign_entropy_gt","zero_mass","cv_sigma","D4_off_mass","D4_median_abs","D4_p95_abs","residual_mean_max_abs"]
    summ = {k: summarize([x[k] for x in rows]) for k in keys}
    return rows, summ

lme_rows, lme_summ = run(lme_files, "q")
loc_rows, loc_summ = run(loc_files, "c")
json.dump({"lme_rows": lme_rows, "lme_summ": lme_summ, "loc_rows": loc_rows, "loc_summ": loc_summ,
           "env": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()}},
          open("/tmp/task1indep/results.json","w"), indent=1)
print(json.dumps({"lme_summ": lme_summ, "loc_summ": loc_summ}, indent=1))
# extra diagnostics for report
import collections
print("LME N: min", min(r["N"] for r in lme_rows), "max", max(r["N"] for r in lme_rows))
print("LOC N:", [(r["id"], r["N"]) for r in loc_rows])
print("LME active<96:", sum(1 for r in lme_rows if r["active"]<96), "D4 null:", sum(1 for r in lme_rows if r["D4_off_mass"] is None))
print("LOC active:", [(r["id"], r["active"]) for r in loc_rows])
