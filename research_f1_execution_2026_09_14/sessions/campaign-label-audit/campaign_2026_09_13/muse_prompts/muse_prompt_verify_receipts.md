# Muse session — verification receipts for three accepted packages (read-only)

You are one of several parallel Muse sessions on this machine. A different session is auditing the
twelve-byte budget; do not touch its files (`~/muse-work/run_twelve_byte.log`,
`~/muse-work/prompt_twelve_byte.md`, `~/muse-work/reports/twelve_byte_audit_report.md`).

## Environment

- Repository clone: `~/muse-work/llmzip-audit` (run `git fetch --quiet origin` first — new branches
  were added on the parent side). Read-only: do not modify the repository. Use `git show <ref>:<path>`
  and `git worktree add` for fresh checkouts ONLY under `~/muse-work/verify/<name>`.
- **No network** (PyPI/github unreachable). Everything needed is local.
- Python options: `/usr/bin/python3` (3.14, no numpy) for hashing; `~/muse-work/faiss-python -c ...`
  for numpy 2.5.3; and the full pinned scientific venv (numpy 2.3.5/pandas/scipy/sklearn) usable
  from WSL via Windows interop at
  `/mnt/c/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe` (pass it Windows-style script paths).
- Scratch: `~/muse-work/scratch/verify/`. Report: write `~/muse-work/reports/verification_receipts.md`
  AND print it as your final answer.

## Task

Independently verify, from bytes, the three packages below. For each: fresh checkout at the exact
commit, recompute every declared hash, run the package's own verifier script (read its README/docs
first), and record raw commands + raw outputs + PASS/FAIL + any defect, verbatim. Then state, in one
line each, what each verifier structurally CANNOT detect.

1. **Preseal diagnostics namespace** — branch `research/v52-preseal-diagnostics-2026-09-12`
   (results commit `4001fc9d8ea2c932042de7823713c6efce8e56d0`; namespace
   `research/v52/preseal_diagnostics_2026_09_12/`; claimed hash manifest sha256
   `5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b`). The namespace's
   `HASHES.txt` is claimed to hash all files of its namespace except itself — recompute each listed
   hash. Also check `LEAD_VERIFICATION.json` claims and `RESULTS.json` task statuses against the
   files present.
2. **ITQ/Haar objective replay package** — branch `codex/v52-itq-haar-objective-2026-09-12`,
   commit `b06bc04d544d7847d085d73f68dbd3b02aff85e2`, namespace
   `research/v52/itq_haar_objective_comparison_2026_09_12/`, claimed manifest
   `70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f`. Run its `verify_package.py`
   (and any `.mjs` companion if the README names one — node may or may not exist; record what you run).
3. **G3 synthetic remediation delivery** — branch `codex/g3-remediation-delivery-2026-09-12`,
   commit `7266160ac03bdd064fe75f058eae3430fbe14496`, claimed manifest
   `9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d`. It contains
   `package_integrity.py` and an official package verifier — find them via its README/receipt and
   run them. (If a check needs a package you don't have, use the interop venv above or record the
   limitation — never guess.)

Hard stops: no writes to the repository, no commits, no pushes, no network. Do not run anything that
touches Task 4F1 execution candidates or real BEAM data — these three packages are synthetic /
namespace metadata only. If a verifier fails, capture the failure exactly; do not fix anything.

Report format: per package — Checkout & commit, Declared manifest, Recomputed hashes (counts:
matched/mismatched/absent), Verifier run (raw output), Verdict, Limitations. End with a summary
table and your one-line "what it cannot detect" per package.
