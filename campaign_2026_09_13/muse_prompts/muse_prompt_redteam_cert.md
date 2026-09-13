# Muse session — red-team review of a "certified regeneration" methodology (read-only)

You are one of several parallel Muse sessions on this machine. Do not touch other sessions' files.

## Environment

- **No network.** Read files under `/mnt/c/Users/MDP/dev/llmzip-work/` directly (they are Windows
  files visible from WSL). Scratch: `~/muse-work/scratch/redteam/`. Report:
  `~/muse-work/reports/certification_redteam.md`; print it as your final answer too.
- Python for any computation: `~/muse-work/faiss-python -c ...` (numpy 2.5.3).

## What to review

A local session had to recover, for a research programme, certain previously-unavailable
per-question matrices ("C": 470 LongMemEval matrices, and 10 LoCoMo conversation matrices). The
original float matrices were never published. The approach taken: **re-execute the byte-frozen
producer** on the canonical inputs and then **certify** the regenerated matrices against every
previously published summary of the originals. Read:

1. `/mnt/c/Users/MDP/dev/llmzip-work/PLAN_TASK1_COMPLETION.md` — the method and its governance framing.
2. `/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/certification_report.json` — regeneration vs the
   published per-question heterogeneity CSV (11 scalar fields + two 96-length vectors per question,
   470 questions).
3. `/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/code_certification.json` — regeneration vs the frozen
   packed 96-bit sign codes that the retrieval pipeline actually consumed (all 470 questions,
   ~231k documents), plus ITQ code variants refit from the regenerated matrices (if present; if the
   file is absent when you first look, wait up to 8 minutes — `sleep 60` in a loop — then re-check;
   if still absent, review the rest and state the gap).
4. `/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/counts_report.json` and
   `.../regen/locomo/task1_locoMo_stats.json` — LoCoMo side (10 conversations; counts block vs the
   frozen transfer proof, plus computed statistics).
5. The harness scripts that produced these: `/mnt/c/Users/MDP/dev/llmzip-work/harness/lme_regen.py`,
   `.../harness/code_cert_lme.py`, `.../harness/locomo_regen.py` (read for logic; you may run them
   only in a dry/review capacity — do NOT regenerate anything or modify files).

## Your job — attack it

Produce a defect-focused review answering, with specifics:

1. **Logical validity.** Is "re-executed the frozen producer + all published summaries match
   bit-exactly" adequate certification that the matrices equal the originals for the intended use
   (computing additional *coordinate statistics*)? Which functionals of C are covered by the checks,
   and which are NOT? Construct, if you can, a concrete family of matrices that would pass every
   existing check but differ materially in a way that matters for (a) zero-mass/strict>0 entropy,
   (b) correlation-matrix statistics (off-diagonal structure). Be honest if you cannot construct one.
2. **Hash/identity chain holes.** Anything in the scripts where an assertion is vacuous, a gate can
   be bypassed, a hash covers the wrong bytes, a comparison could pass for the wrong reason (e.g.
   float printing/rounding, `== ` on NaN, silent fallbacks), or a claim in the certification JSON is
   not actually produced by the code shown.
3. **Residual risk register.** Enumerate what an independent auditor would still demand before
   citing these numbers as canonical, and which items are cheap to close locally versus impossible
   without the original bytes.
4. **Script bugs.** Read the three harness scripts line by line. Report any bug, however small, with
   the exact line and a concrete failure mode. (Do not fix them.)

Rules: read-only; no repository writes; no network; no speculation presented as fact — mark clearly
what you verified by execution versus by reading. If you run checks, quote commands and outputs in
the report.
