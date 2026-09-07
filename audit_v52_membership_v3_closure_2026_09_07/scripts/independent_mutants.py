"""Independent mutant harness for the v3 delta closure check.

Written from scratch by the auditor. It does NOT import, call or read
`drafts/v52/membership_impl_v3_2026_09_07/scripts/mutation_probes_v3.py`; the anchors and
replacements below were derived by reading the v3 core, not by copying the preparer's list.

Two groups:

  GROUP A - the four mutants the previous closure check (branch
  audit/v52-membership-v2-closure-2026-09-07 @ 712412a5947fa56374e05bf3e3a0b075d4578b6d) used to
  defeat v2, reconstructed here from their DESCRIPTIONS in the closure report, plus the NEW-2 and
  NEW-3 mutants named in the tasking:
      A-R1  a Delta/G ratio substituted into `per_seed_Delta_pp`
      A-R2  a ratio substituted into `per_seed_G_scaled_pp`
      A-R3  a rescaling of `per_seed_G_pp`
      A-R6  the same ratio as A-R1 expressed via `np.divide` (no ast.Div node)
      A-NEW2  cv_sigma_before = 123456.0
      A-NEW3  the `n_questions <= 0` guard in build_clusters removed

  GROUP B - mutants of the auditor's own choosing, aimed at PUBLISHED fields, that the preparer
  did not anticipate. These test whether the conformance coverage is real or fitted to the known
  list. Every one leaves all three published SCALARS exactly correct, so only a check that reaches
  the vector / count fields can see them.
      B-1  per_seed_G_pp and per_seed_G_scaled_pp swapped in the returned dict
      B-2  per_seed vectors reversed elementwise (mean, and therefore every scalar, unchanged)
      B-3  per_seed vectors rounded to 6 decimals
      B-4  n_question_slots reports DISTINCT questions instead of selected slots
      B-5  n_question_slots off by one
      B-6  per_seed_Delta_pp perturbed by +5e-13, i.e. INSIDE the accepted absolute tolerance.
           This one is EXPECTED TO SURVIVE. It is not a defect: binding section 6 fixes an
           absolute 1e-12 and a bit-level equality demand would itself be an unjustified new
           condition. It is included to make the tolerance's actual reach explicit rather than
           assumed.

Each mutant is applied to a COPY of the v3 core in a throwaway temp directory. The candidate files
are never modified. The v3 test file is copied unmodified alongside it and run from that directory,
because the suite's AST self-sweep reads itself by name from its own directory.

No corpus, no model, no network, no real data. Usage:
    python independent_mutants.py <candidate_dir> [json-out]
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

RET = ('    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,\n'
       '            "per_seed_G_pp": per_seed_g.tolist(), "per_seed_G_scaled_pp": per_seed_gs.tolist(),\n'
       '            "per_seed_Delta_pp": per_seed_d.tolist(), "n_question_slots": int(idx.size)}')


def ret(g="per_seed_g.tolist()", gs="per_seed_gs.tolist()", d="per_seed_d.tolist()",
        n="int(idx.size)"):
    return ('    return {"G_bar_pp": G, "G_bar_scaled_pp": G_scaled, "Delta_bar_pp": D_,\n'
            f'            "per_seed_G_pp": {g}, "per_seed_G_scaled_pp": {gs},\n'
            f'            "per_seed_Delta_pp": {d}, "n_question_slots": {n}}}')


# (id, group, expectation, description, old, new)
MUTANTS = [
    ("A-R1-ratio-into-per-seed-delta", "A", "must be killed",
     "substitute the forbidden Delta/G ratio into the permitted key per_seed_Delta_pp; "
     "all three scalars stay exactly correct",
     RET, ret(d="(per_seed_d / per_seed_g).tolist()")),

    ("A-R2-ratio-into-per-seed-g-scaled", "A", "must be killed",
     "substitute the ratio per_seed_gs / per_seed_g into the permitted key per_seed_G_scaled_pp",
     RET, ret(gs="(per_seed_gs / per_seed_g).tolist()")),

    ("A-R3-per-seed-g-rescaled", "A", "must be killed",
     "rescale the published per_seed_G_pp vector by 1.5 while every scalar stays correct",
     RET, ret(g="(per_seed_g * 1.5).tolist()")),

    ("A-R6-ratio-via-np-divide", "A", "must be killed",
     "the A-R1 ratio written with np.divide, so no ast.Div node exists for the AST enumeration",
     RET, ret(d="np.divide(per_seed_d, per_seed_g).tolist()")),

    ("A-NEW2-cv-before-constant", "A", "must be killed",
     "report a fixed wrong number 123456.0 as cv_sigma_before",
     '        "cv_sigma_before": _cv(sigma),',
     '        "cv_sigma_before": 123456.0,'),

    ("A-NEW3-empty-guard-removed", "A", "must be killed",
     "remove the named guard so build_clusters([], 0) falls through to a library exception",
     "    if n_questions <= 0:                                                         # NEW-3",
     "    if False:                                                                    # NEW-3"),

    ("B-1-per-seed-g-and-gs-swapped", "B", "must be killed",
     "AUDITOR'S OWN: swap per_seed_G_pp and per_seed_G_scaled_pp in the returned dict. Both keys "
     "are permitted, both values are real published quantities, and all three scalars are untouched",
     RET, ret(g="per_seed_gs.tolist()", gs="per_seed_g.tolist()")),

    ("B-2-per-seed-vectors-reversed", "B", "must be killed",
     "AUDITOR'S OWN: reverse each per-seed vector. The mean of a reversed vector is the same "
     "number, so every published scalar, the linearity identity and the schema are all unaffected; "
     "only an elementwise comparison against a reference can see it",
     RET, ret(g="per_seed_g.tolist()[::-1]", gs="per_seed_gs.tolist()[::-1]",
              d="per_seed_d.tolist()[::-1]")),

    ("B-3-per-seed-rounded-1e6", "B", "must be killed",
     "AUDITOR'S OWN: round the published per-seed vectors to 6 decimals - a plausible 'tidying' "
     "defect that leaves them visually right and about 1e-7 wrong",
     RET, ret(g="np.round(per_seed_g, 6).tolist()", gs="np.round(per_seed_gs, 6).tolist()",
              d="np.round(per_seed_d, 6).tolist()")),

    ("B-4-slots-counted-as-distinct", "B", "must be killed",
     "AUDITOR'S OWN: publish n_question_slots as the number of DISTINCT questions. On the "
     "conformance fixture idx has no repeats, so the conformance check alone cannot see this; it "
     "is only visible to a check that exercises multiplicity",
     RET, ret(n="int(np.unique(idx).size)")),

    ("B-5-slots-off-by-one", "B", "must be killed",
     "AUDITOR'S OWN: publish n_question_slots + 1",
     RET, ret(n="int(idx.size) + 1")),

    ("B-6-per-seed-delta-inside-tolerance", "B", "EXPECTED TO SURVIVE - not a defect",
     "AUDITOR'S OWN: perturb per_seed_Delta_pp by +5e-13, i.e. INSIDE the accepted absolute "
     "tolerance of 1e-12 fixed by binding section 6. Survival is the correct behaviour of a "
     "tolerance-based comparison and is recorded to make the tolerance's reach explicit; "
     "demanding bit-level equality would itself be an unjustified new condition",
     RET, ret(d="(per_seed_d + 5e-13).tolist()")),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=1800)
    return p.returncode, (p.stdout + p.stderr)


rows = []
base = Path(tempfile.mkdtemp(prefix="v3_closure_audit_"))
try:
    for mid, group, expectation, desc, old, new in MUTANTS:
        work = base / mid
        work.mkdir(parents=True)
        for f in ("membership_scaling_core.py", "test_membership_scaling_core.py"):
            shutil.copy2(CAND / f, work / f)
        core = work / "membership_scaling_core.py"
        src = core.read_text(encoding="utf-8")
        if src.count(old) != 1:
            rows.append({"id": mid, "group": group, "applied": False,
                         "note": f"anchor occurs {src.count(old)} times, expected exactly 1"})
            print(f"SKIP   {mid}: anchor count {src.count(old)}")
            continue
        core.write_text(src.replace(old, new, 1), encoding="utf-8")
        rc, out = run([sys.executable, "-B", "test_membership_scaling_core.py"], work)
        killed = rc != 0
        failing = [l.strip() for l in out.splitlines() if l.startswith("FAIL")]
        crashed = killed and not failing
        rows.append({"id": mid, "group": group, "expectation": expectation, "applied": True,
                     "description": desc, "suite_kills": killed,
                     "failing_checks": failing[:6],
                     "crashed_without_named_failure": crashed,
                     "exit_code": rc,
                     "tail": out.strip().splitlines()[-1] if out.strip() else ""})
        print(f"{'KILLED' if killed else '*** SURVIVES ***':>18}  {mid}  [{group}] ({expectation})")
        for f in failing[:3]:
            print(f"{'':>18}  by: {f[:120]}")
        if crashed:
            print(f"{'':>18}  killed by an unhandled exception, not a named FAIL line")
finally:
    shutil.rmtree(base, ignore_errors=True)

applied = [r for r in rows if r.get("applied")]
survivors = [r for r in applied if not r.get("suite_kills")]
unexpected = [r for r in survivors if "SURVIVE" not in r.get("expectation", "")]
print(f"\n{len(applied)} of {len(rows)} mutants applied; {len(applied) - len(survivors)} killed; "
      f"{len(survivors)} survived")
print(f"survivors: {[r['id'] for r in survivors]}")
print(f"UNEXPECTED survivors (would be a finding): {[r['id'] for r in unexpected]}")
print("SCOPE: a kill is evidence about that one fault variant and nothing more. Nothing here shows "
      "the core or the suite to be correct.")
if OUT:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "harness": "independent_mutants.py, written by the v3 closure auditor",
        "candidate_dir": str(CAND),
        "python": sys.version.split()[0],
        "scope_statement": "kills demonstrate coverage of these specific fault variants only",
        "rows": rows,
        "applied": len(applied),
        "killed": len(applied) - len(survivors),
        "survivors": [r["id"] for r in survivors],
        "unexpected_survivors": [r["id"] for r in unexpected]}, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0)
