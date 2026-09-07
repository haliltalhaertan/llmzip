"""Mutation probes against the v2 candidate suite. ADAPTED, WITH ATTRIBUTION.

Source: `scripts/mutation_probes.py` on branch audit/v52-membership-impl-review-2026-09-07 @
68819424765ed3da89377c89980d7e42546bfe02, written by the independent implementation reviewer. That
audit namespace is NOT modified; this is a re-anchored reimplementation against the v2 core.

WHY RE-ANCHORING WAS NECESSARY AND WHAT IT MEANS. The reviewer's probes substitute exact source
strings. The v2 fixes changed some of those lines, so a verbatim replay would report "anchor not
found" for them and silently understate coverage. Each mutation below records whether its anchor is
UNCHANGED from the reviewer's version or RE-ANCHORED, and why. One mutation is INVERTED: M10 asked
whether the suite could tell a true CV from a plain SD by introducing the CV; v2 reports the CV, so
the mutation that now probes the same weakness is the reverse - reintroduce the SD.

WHAT A KILL COUNT MEANS. A suite that kills every mutation here has been shown to catch exactly
these fault variants. That is evidence about these variants and nothing more; it is not a guarantee
that the core is free of defects, and it must not be reported as one.

Nothing here reads a corpus or runs anything on real data. Mutants are written to a throwaway temp
directory; the candidate files are never touched.

Usage: python mutation_probes_v2.py <candidate_dir> [json-out]
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CAND = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None

# (id, anchor_status, description, old, new, why it matters)
MUTATIONS = [
    ("M1-ratio-reintroduced", "unchanged",
     "add a genuine Delta/G ratio to the reported output under a neutral name",
     '    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,',
     '    _rel = D_ / G if G != 0 else float("nan")\n'
     '    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_, "relative_change": _rel,',
     "the acceptance record forbids ANY ratio of Delta to G under any name; the v1 word scan could not see this"),

    ("M2-denominator-distinct", "unchanged",
     "divide the mean by the number of DISTINCT questions instead of the selected slots",
     "    per_seed_g = g[idx].mean(axis=0)          # divide by the number of selected slots\n"
     "    per_seed_gs = gs[idx].mean(axis=0)",
     "    _u = np.unique(idx)\n    per_seed_g = g[_u].mean(axis=0)\n    per_seed_gs = gs[_u].mean(axis=0)",
     "binding section 4 step 5 requires division by the total number of selected question SLOTS"),

    ("M3-denominator-clusters", "re-anchored twice",
     "make the cluster bootstrap average cluster means instead of question slots. Re-anchored twice: "
     "v2 inserts a diagnostic line between the reviewer's two original anchor lines, and my FIRST "
     "re-anchoring computed the cluster average into an UNUSED variable, so it mutated nothing and "
     "reported a false hole in the suite. That was a defect in the probe, not in the tests, and it is "
     "recorded here rather than quietly corrected",
     "        a = aggregate(g, gs, idx)\n        for k in out:",
     "        _parts = [aggregate(g, gs, members[clusters[j]]) for j in drawn]\n"
     "        a = {k: float(np.mean([p[k] for p in _parts])) for k in ('G_bar_pp', 'G_bar_scaled_pp', 'Delta_bar_pp')}\n"
     "        for k in out:",
     "cluster-averaging destroys the question-weighting the acceptance record binds"),

    ("M4-per-seed-resample", "unchanged",
     "break pairing across the seed panel: resample each seed column independently",
     "    per_seed_g = g[idx].mean(axis=0)          # divide by the number of selected slots\n"
     "    per_seed_gs = gs[idx].mean(axis=0)",
     "    _r = np.random.default_rng(int(abs(idx.sum())) % 2**31)\n"
     "    _cols = [_r.integers(0, g.shape[0], size=idx.size) for _ in range(g.shape[1])]\n"
     "    per_seed_g = np.array([g[_cols[j], j].mean() for j in range(g.shape[1])])\n"
     "    per_seed_gs = np.array([gs[_cols[j], j].mean() for j in range(gs.shape[1])])",
     "R1 section 6 requires ONE resampled index set per replicate applied to all arms AND all ten seeds"),

    ("M5-flag-off-by-one", "unchanged",
     "fire the per-archive degenerate flag at 4 instead of above 4",
     '        "flagged": bool(n_degenerate > DEGENERATE_FLAG_THRESHOLD),',
     '        "flagged": bool(n_degenerate >= DEGENERATE_FLAG_THRESHOLD),',
     "R1 section 1: an archive is flagged if the count EXCEEDS 4 of 96"),

    ("M6-eps-as-clip", "unchanged",
     "turn the eps fallback into a clip (divide by eps instead of leaving d = 1)",
     "    d = np.where(ok, 1.0 / np.where(ok, sigma, 1.0), 1.0)",
     "    d = 1.0 / np.maximum(sigma, eps)",
     "R1 section 1: the floor is a FALLBACK, not a clip"),

    ("M7-ddof-one", "unchanged",
     "use the sample form of sigma (ddof = 1) instead of the population form",
     "    sigma = C.std(axis=0, ddof=0)",
     "    sigma = C.std(axis=0, ddof=1)",
     "R1 section 1: ddof = 0; the sample form would define a different intervention"),

    ("M8-pp-twice", "unchanged",
     "apply the percentage-point factor twice",
     '    g = (by_arm["B32_FRESH"] - by_arm["RANDOM32_FRESH"]) * PP',
     '    g = (by_arm["B32_FRESH"] - by_arm["RANDOM32_FRESH"]) * PP * PP',
     "the pp conversion must be applied exactly once"),

    ("M9-spans-zero-broken", "unchanged",
     "always report spans_zero as False",
     '        res[k] = {"lo": lo, "hi": hi, "spans_zero": bool(lo <= 0.0 <= hi)}',
     '        res[k] = {"lo": lo, "hi": hi, "spans_zero": False}',
     "an interval spanning zero must be reported as spanning zero (R2 section 5)"),

    ("M10-cv-after-reverted-to-sd", "INVERTED",
     "reintroduce the v1 defect: report the plain SD of the post-scaling sigma as cv_sigma_after "
     "(the reviewer's M10 introduced the CV because v1 reported the SD; v2 reports the CV, so the "
     "probe for the same weakness is the reverse substitution)",
     '        "cv_sigma_after": _cv(post_sigma),        # F-1: a genuine CV, not a standard deviation',
     '        "cv_sigma_after": float(post_sigma.std(ddof=0)),',
     "F-1: R1 section 1 asks for CV(sigma) before AND after; a suite that cannot tell the two apart "
     "does not test the diagnostic it names"),

    ("M11-overwrite-allowed", "unchanged",
     "let results be overwritten silently",
     "    if path.exists():\n"
     '        raise DesignViolation(f"refusing to overwrite an existing result file: {path}")',
     "    if False:\n"
     '        raise DesignViolation(f"refusing to overwrite an existing result file: {path}")',
     "the acceptance record requires refusing to overwrite result files"),

    ("M12-gate-open", "unchanged",
     "open the real-data gate by default",
     "REAL_DATA_EXECUTION_ENABLED = False",
     "REAL_DATA_EXECUTION_ENABLED = True",
     "real-data execution must be OFF by default"),

    ("M13-duplicates-accepted", "unchanged",
     "stop reporting duplicate records",
     "        if key in seen:\n            duplicates.append(key)",
     "        if False:\n            duplicates.append(key)",
     "duplicated records must be refused, not accepted silently"),

    # New probes for the v2 fixes themselves. A fix that no test can kill is not a fix.
    ("M14-cluster-labels-unvalidated", "new (probes the F-2 fix)",
     "skip cluster-label validation, restoring the silent empty-cluster path",
     '        if isinstance(lab, float) and math.isnan(lab):\n'
     '            raise DesignViolation(f"cluster label at position {i} is NaN")',
     '        if False:\n'
     '            raise DesignViolation(f"cluster label at position {i} is NaN")',
     "F-2: a NaN label produced an empty cluster that silently removed questions from the numerator "
     "and the slot denominator"),

    ("M15-negative-index-wraps", "new (probes the F-7 fix)",
     "allow negative indices to wrap again",
     "    if int(arr.min()) < 0 or int(arr.max()) >= n_rows:",
     "    if int(arr.max()) >= n_rows:",
     "F-7: a negative index silently wraps in numpy and would select a different question"),

    ("M16-partition-check-removed", "new; EXPECTED TO SURVIVE, see note",
     "drop the partition coverage proof",
     "    if covered != n_questions:",
     "    if False:",
     "F-2: coverage must be PROVED at construction. This guard is UNREACHABLE through the public API, "
     "because label validation precedes it and every question therefore carries exactly one label. A "
     "mutation test cannot kill an unreachable guard, so its survival is a property of defence in depth "
     "rather than a hole in the suite. Reported as such rather than removed, and rather than papered over "
     "with a test that reaches it only by monkeypatching internals."),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800)
    return p.returncode, (p.stdout + p.stderr)


rows = []
base = Path(tempfile.mkdtemp(prefix="v52_mut_v2_"))
try:
    for mid, anchor_status, desc, old, new, why in MUTATIONS:
        work = base / mid
        work.mkdir(parents=True)
        for f in ("membership_scaling_core.py", "test_membership_scaling_core.py"):
            shutil.copy2(CAND / f, work / f)
        core = work / "membership_scaling_core.py"
        src = core.read_text(encoding="utf-8")
        if old not in src:
            rows.append({"id": mid, "anchor_status": anchor_status, "applied": False,
                         "note": "mutation anchor not found in the v2 core"})
            print(f"SKIP {mid}: anchor not found")
            continue
        core.write_text(src.replace(old, new, 1), encoding="utf-8")
        rc, out = run([sys.executable, "-B", "test_membership_scaling_core.py"], work)
        killed = rc != 0
        failing = [l.strip() for l in out.splitlines() if l.startswith("FAIL")]
        rows.append({"id": mid, "anchor_status": anchor_status, "applied": True, "description": desc,
                     "why_it_matters": why, "v2_suite_kills": killed,
                     "failing_checks": failing[:4], "crashed_without_named_failure": killed and not failing})
        print(f"{'KILLED' if killed else '*** SURVIVES ***':>18}  {mid}  [{anchor_status}]")
        if killed and failing:
            print(f"{'':>18}  by: {failing[0][:110]}")
        if not killed:
            print(f"{'':>18}  NOT CAUGHT: {desc}")
finally:
    shutil.rmtree(base, ignore_errors=True)

applied = [r for r in rows if r.get("applied")]
survivors = [r for r in applied if not r.get("v2_suite_kills")]
print(f"\n{len(applied)} of {len(rows)} mutations applied; {len(applied) - len(survivors)} killed; "
      f"{len(survivors)} survived")
print("SCOPE: this shows the suite catches exactly these fault variants. It is not evidence that the "
      "core is free of defects and must not be reported as such.")
if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "python": sys.version.split()[0],
        "source_of_probes": "audit/v52-membership-impl-review-2026-09-07 @ 68819424765ed3da89377c89980d7e42546bfe02, scripts/mutation_probes.py",
        "scope_statement": "kills demonstrate coverage of these specific fault variants only; not a correctness guarantee",
        "rows": rows,
        "applied": len(applied), "killed": len(applied) - len(survivors),
        "survivors": [r["id"] for r in survivors]}, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0)
