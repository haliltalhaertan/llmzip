"""Mutation probes: is the PREPARER's own test suite sound, or does it only look sound?

Method. For each mutation, a COPY of the candidate core is written into a throwaway temp
directory (the candidate files in the repository are never touched), the mutation is applied by
exact string substitution, and then both suites are run against the mutant:

  * the preparer's own `test_membership_scaling_core.py`, and
  * this reviewer's `adversarial_core_tests.py`.

A mutation that no suite kills is a hole. A mutation that only the reviewer's suite kills is a
hole in the preparer's suite. Nothing here reads a corpus or runs anything on real data.

Usage: python mutation_probes.py <candidate_dir> <adversarial_tests.py> [json-out]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()
ADV = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else None

MUTATIONS = [
    # (id, description, old, new, why it matters)
    ("M1-ratio-reintroduced",
     "add a genuine Delta/G ratio to the reported output under a neutral name",
     '    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,',
     '    _rel = D_ / G if G != 0 else float("nan")\n'
     '    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_, "relative_change": _rel,',
     "the acceptance record forbids ANY ratio of Delta to G under any name; a token scan for the "
     "word 'rho' cannot see this"),

    ("M2-denominator-distinct",
     "divide the mean by the number of DISTINCT questions instead of the selected slots",
     "    per_seed_g = g[idx].mean(axis=0)          # divide by the number of selected slots\n"
     "    per_seed_gs = gs[idx].mean(axis=0)",
     "    _u = np.unique(idx)\n"
     "    per_seed_g = g[_u].mean(axis=0)\n"
     "    per_seed_gs = gs[_u].mean(axis=0)",
     "acceptance record section 4 step 5 requires division by the total number of selected "
     "question SLOTS, explicitly not by distinct questions"),

    ("M3-denominator-clusters",
     "make the cluster bootstrap average cluster means instead of question slots",
     "        idx = np.concatenate([members[clusters[j]] for j in drawn])   # multiplicity preserved\n"
     "        a = aggregate(g, gs, idx)",
     "        _parts = [aggregate(g, gs, members[clusters[j]]) for j in drawn]\n"
     "        a = {k: float(np.mean([p[k] for p in _parts])) for k in "
     "('G_bar_pp', 'G_bar_scaled_pp', 'Delta_bar_pp')}",
     "cluster-averaging destroys the question-weighting the acceptance record binds"),

    ("M4-per-seed-resample",
     "break pairing across the seed panel: resample each seed column independently",
     "    per_seed_g = g[idx].mean(axis=0)          # divide by the number of selected slots\n"
     "    per_seed_gs = gs[idx].mean(axis=0)",
     "    _r = np.random.default_rng(int(abs(idx.sum())) % 2**31)\n"
     "    _cols = [_r.integers(0, g.shape[0], size=idx.size) for _ in range(g.shape[1])]\n"
     "    per_seed_g = np.array([g[_cols[j], j].mean() for j in range(g.shape[1])])\n"
     "    per_seed_gs = np.array([gs[_cols[j], j].mean() for j in range(gs.shape[1])])",
     "R1 section 6 requires ONE resampled index set per replicate applied identically to all arms "
     "AND all ten seeds"),

    ("M5-flag-off-by-one",
     "fire the per-archive degenerate flag at 4 instead of above 4",
     '        "flagged": bool(n_degenerate > DEGENERATE_FLAG_THRESHOLD),',
     '        "flagged": bool(n_degenerate >= DEGENERATE_FLAG_THRESHOLD),',
     "R1 section 1: an archive is flagged if the count EXCEEDS 4 of 96"),

    ("M6-eps-as-clip",
     "turn the eps fallback into a clip (divide by eps instead of leaving d = 1)",
     "    d = np.where(ok, 1.0 / np.where(ok, sigma, 1.0), 1.0)",
     "    d = 1.0 / np.maximum(sigma, eps)",
     "R1 section 1: the floor is a FALLBACK, not a clip; a dead coordinate is never divided by eps"),

    ("M7-ddof-one",
     "use the sample form of sigma (ddof = 1) instead of the population form",
     "    sigma = C.std(axis=0, ddof=0)",
     "    sigma = C.std(axis=0, ddof=1)",
     "R1 section 1: ddof = 0; the sample form would define a different intervention"),

    ("M8-pp-twice",
     "apply the percentage-point factor twice",
     '    g = (by_arm["B32_FRESH"] - by_arm["RANDOM32_FRESH"]) * PP',
     '    g = (by_arm["B32_FRESH"] - by_arm["RANDOM32_FRESH"]) * PP * PP',
     "the pp conversion must be applied exactly once"),

    ("M9-spans-zero-broken",
     "always report spans_zero as False",
     '        res[k] = {"lo": lo, "hi": hi, "spans_zero": bool(lo <= 0.0 <= hi)}',
     '        res[k] = {"lo": lo, "hi": hi, "spans_zero": False}',
     "an interval spanning zero must be reported as spanning zero (R2 section 5)"),

    ("M10-cv-after-true-cv",
     "report a genuine CV(sigma) after rescaling instead of the plain standard deviation",
     '        "cv_sigma_after": float((C @ np.diag(d)).std(axis=0, ddof=0).std(ddof=0)),',
     '        "cv_sigma_after": float((lambda p: p.std(ddof=0) / p.mean())'
     '((C @ np.diag(d)).std(axis=0, ddof=0))),',
     "R1 section 1 asks for CV(sigma) before AND after; if the preparer's suite cannot tell the "
     "two apart, it does not test the diagnostic it names"),

    ("M11-overwrite-allowed",
     "let results be overwritten silently",
     "    if path.exists():\n"
     '        raise DesignViolation(f"refusing to overwrite an existing result file: {path}")',
     "    if False:\n"
     '        raise DesignViolation(f"refusing to overwrite an existing result file: {path}")',
     "the acceptance record requires refusing to overwrite result files"),

    ("M12-gate-open",
     "open the real-data gate by default",
     "REAL_DATA_EXECUTION_ENABLED = False",
     "REAL_DATA_EXECUTION_ENABLED = True",
     "real-data execution must be OFF by default"),

    ("M13-duplicates-accepted",
     "stop reporting duplicate records",
     "        if key in seen:\n            duplicates.append(key)",
     "        if False:\n            duplicates.append(key)",
     "duplicated records must be refused, not accepted silently"),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800)
    return p.returncode, (p.stdout + p.stderr)


rows = []
base = Path(tempfile.mkdtemp(prefix="v52_mut_"))
try:
    for mid, desc, old, new, why in MUTATIONS:
        work = base / mid
        work.mkdir(parents=True)
        for f in ("membership_scaling_core.py", "test_membership_scaling_core.py"):
            shutil.copy2(CAND / f, work / f)
        core = work / "membership_scaling_core.py"
        src = core.read_text(encoding="utf-8")
        if old not in src:
            rows.append({"id": mid, "applied": False, "note": "mutation anchor not found"})
            print(f"SKIP {mid}: anchor not found")
            continue
        core.write_text(src.replace(old, new, 1), encoding="utf-8")

        rc_prep, out_prep = run([sys.executable, "test_membership_scaling_core.py"], work)
        rc_adv, out_adv = run([sys.executable, str(ADV), str(core)], work)

        prep_kills = rc_prep != 0
        adv_kills = rc_adv != 0
        prep_failed = [l.strip() for l in out_prep.splitlines() if l.startswith("FAIL")]
        adv_failed = [l.strip() for l in out_adv.splitlines() if l.startswith("FAIL")]
        rows.append({"id": mid, "applied": True, "description": desc, "why_it_matters": why,
                     "preparer_suite_kills": prep_kills, "reviewer_suite_kills": adv_kills,
                     "preparer_failing_checks": prep_failed[:4],
                     "reviewer_failing_checks": adv_failed[:4],
                     "preparer_crashed": prep_kills and not prep_failed,
                     "reviewer_crashed": adv_kills and not adv_failed})
        mark = ("BOTH" if prep_kills and adv_kills else
                "REVIEWER ONLY" if adv_kills else
                "PREPARER ONLY" if prep_kills else "*** SURVIVES BOTH ***")
        print(f"{mark:>22}  {mid}: {desc}")
        if not prep_kills and adv_kills:
            print(f"{'':>22}  reviewer caught: {adv_failed[:2]}")
        if not prep_kills and not adv_kills:
            print(f"{'':>22}  NOBODY caught this")
finally:
    shutil.rmtree(base, ignore_errors=True)

survivors = [r for r in rows if r.get("applied") and not r.get("preparer_suite_kills")
             and not r.get("reviewer_suite_kills")]
prep_holes = [r for r in rows if r.get("applied") and not r.get("preparer_suite_kills")]
print(f"\n{len(rows)} mutations; preparer's suite missed {len(prep_holes)}; "
      f"nobody caught {len(survivors)}")
if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"python": sys.version.split()[0], "rows": rows,
                               "preparer_suite_missed": [r["id"] for r in prep_holes],
                               "unkilled_by_anyone": [r["id"] for r in survivors]},
                              indent=2) + "\n", encoding="utf-8")
raise SystemExit(0)
