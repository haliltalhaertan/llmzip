# Twelve-byte preregistration revision for review

**NOT SEALED / NOT AUTHORIZED. Design-only publication.**

Base: `4f2429b257546d6899f3ed48f605cd18210aeae0` (live origin/main verified at task start).
Branch: `codex/twelve-byte-prereg-revision-2026-09-12`.
True origin: `https://github.com/haliltalhaertan/llmzip.git`.
Isolated clone: `C:/Users/MDP/Documents/ChatGPT/LLM_TOKEN_ZIP/work/llmzip_prereg_revision_20260912`.
Local `core.autocrlf=false`. The original G3 checkout is untouched. A local clone
attempt failed Git's dubious-ownership check; this clone came directly from GitHub
with `--no-checkout` before local newline configuration and branch checkout. No
global safe-directory or other global Git configuration was changed.

Review `PREREG_DRAFT.md` first, then `UNRESOLVED_DECISIONS.md`. The former reconciles
the HR budget decision and supplies concrete proposals; the latter names the
exact disposition/replay/implementation gates. `PROPOSED_CONSTANTS.json` makes
seed panels, strata, and statistical choices reviewable source literals, without
claiming that a runner is wired to them or that the choices are approved.

`SOURCE_EVIDENCE_MAP.md` maps every relevant claim to its evidence and limitations.
`SOURCE_VERIFICATION.json` records raw commit/blob checks and published SHA256
matches. `verify_sources.mjs` reproduces that receipt without reading corpus,
gold tables, per-question outcomes, or secrets. It never executes Faiss or a
repository Python script; its sole scalar arithmetic derives the historical
SIMHASH control from five published percentages.

From this clone's root, safe read-only verification commands are:

```powershell
node drafts/v52/twelve_byte_prereg_revision_2026_09_12/verify_sources.mjs
node drafts/v52/twelve_byte_prereg_revision_2026_09_12/verify_package.mjs
git diff --check 4f2429b257546d6899f3ed48f605cd18210aeae0
```

`verify_package.mjs` verifies receipt reproducibility, proposal constants,
namespace-only changes, package inventory, and exact file digests. This is document
and provenance verification, **not runtime/library/runner or scientific validation**.
The parent owns mandatory historical cost-script replay; a verified complete
artifact can close that specific item. Future runner storage/auxiliary/RNG/negative
integration checks are a separate open gate and are not imposed on the historical
script. The reported Windows supplementary checks and PR2 closure are labeled
as parent reports, not independently verified artifacts or authorization.

Digest topology is deliberately nonrecursive:

1. `PREREG_DRAFT.md.sha256` hashes only `PREREG_DRAFT.md`.
2. `SHA256SUMS` hashes all package payload files, including that draft sidecar,
   scripts, source receipt and this README. It excludes itself and its own sidecar.
3. `SHA256SUMS.sha256` hashes only `SHA256SUMS`. It is not listed in `SHA256SUMS`.

No file claims its own digest or future commit hash. The final Git commit is the
publication identity and is reported outside the hashed payload after creation.
The draft, receipt, manifest and branch provide no seal/run/outcome/HMAC authority.
No main ledger/state, G3 file, sealed byte, old source document, or result is edited.
