# Muse audit run — environment notes (prepended by the desktop session that launches this run)

You are running headless inside WSL on the Head Researcher's desktop. The original task text
follows after a separator, then a facts-only postscript. The original task remains the task.

- Repository clone: `~/muse-work/llmzip-audit` — cloned from the desktop's pristine clone.
  `main` is at `5ec3db6`. All refs named in the task or postscript are present locally:
  `main`, `draft/v52-twelve-byte-baseline-prereg-2026-09-10` (commit `d2cfbaa`),
  `hr/twelve-byte-budget-decision-2026-09-11`, `codex/twelve-byte-prereg-revision-2026-09-12`
  (commit `a73393a6`). Use `git show <ref>:<path>` / `git cat-file` to read; do not modify.
- **There is no network access in this environment** (PyPI and github.com are unreachable —
  verified). Do NOT attempt installs or web fetches. Everything needed is already local.
  If a claim requires something only the network could provide, grade `UNVERIFIABLE` and say why.
- faiss is preinstalled offline for you: run `~/muse-work/faiss-python -c "..."` (a wrapper that
  sets PYTHONPATH to `~/muse-work/fpylibs`), preinstalled versions: faiss-cpu 1.15.0,
  numpy 2.5.3. Example: `~/muse-work/faiss-python -c "import faiss; print(faiss.RaBitQuantizer(96).code_size)"`.
  A scratch virtualenv install is not possible here (no network); this preinstalled environment
  substitutes for it.
- Scratch directory: `~/muse-work/scratch/` (create if missing). Save the final report to
  `~/muse-work/reports/twelve_byte_audit_report.md` (create the dir) AND print it as your final
  answer. The report file is the primary deliverable; make it complete.
- For each claim, establish the fact by a command you actually ran in this session; quote the
  command and its raw output (or the exact file line) in the report. A grade is itself a claim.
- `--disable-write` is on for this run: you cannot write into the repository — that is intended.
  (`~/muse-work/reports/` and `~/muse-work/scratch/` may still be writable for you as your
  workspace; if file writes are blocked entirely, print the report as your final answer and say
  the file could not be written.)

---
---

