[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Muse session — cold-start adversarial review of the Task1 completion package (read-only)

You are a fresh reviewer session with no prior context. Other Muse sessions ran on this machine
earlier; do NOT read their scratch (`/tmp/task1indep`, `/tmp/verify`, `/tmp/run` — avoid those
directories entirely) and do not read any other session's logs; form your own view from the package
itself.

## Environment

- **No network.** Read files under `/mnt/c/Users/MDP/dev/llmzip-work/` directly.
  Python with numpy: `~/muse-work/faiss-python -c ...` (numpy 2.5.3); plain `/usr/bin/python3` for
  hashing/JSON. `jq` may not exist — use python. Scratch: `/tmp/review5/` (NOT `~/muse-work/*`,
  which is read-only here). Print your final report as your answer (file writes outside /tmp are
  blocked in this session).
- An optional transitive check can also read the programme clone at `~/muse-work/llmzip-audit`
  (git refs available; read-only).

## The package under review (all under /mnt/c/Users/MDP/dev/llmzip-work/)

- `TASK1_COMPLETION_RECEIPT.md` — the claims. (Sections marked `[PENDING]` near the end are being
  filled concurrently; treat `[PENDING]` items as NOT part of your review scope and say so.)
- `regen/lme/certification_report.json`, `regen/lme/code_certification_sign.json`,
  `regen/lme/code_certification_itq.json` (may appear a few minutes after you start — if absent when
  you first need it, `sleep 60` and retry up to 5 times, then proceed noting the gap).
- `regen/lme/task1_extension_lme.json` (+ `.csv`), `regen/task1_RESULTS_extended.json`,
  `regen/locomo/task1_locoMo_stats.json`, `regen/locomo/counts_report.json`.
- Inputs: `drive/V52_T4C2_BINARY_GEOMETRY.zip` (frozen packed sign codes, sha256 40026fe6...),
  `drive/V52_T4C3_native_heterogeneity.csv` (published statistics, sha 148ae5b7...),
  matrices under `regen/lme/cache_repr/*.pkl` (470) and `regen/locomo/locomo_*.pkl` (10),
  frozen definitions at `harness/ref/measure_representation_diagnostics.py`.

## Your job — falsification-first

Work in this order, keeping raw commands + raw outputs for the report:

1. **Independent sample re-derivation (do NOT read the package's certification JSONs before
   finishing this step; write your sample results down first).**
   - Pick ≥8 LongMemEval question ids yourself (e.g. by hashing the sorted id list and taking
     spread-out indices). For each: load the pkl, compute `np.packbits(C>=0, axis=1,
     bitorder='big')` and the query code, and compare bit-for-bit against the matching
     `codes/<qid>.npz` member inside the Drive zip (`sign_doc_packed`, `sign_query_packed`).
   - Pick ≥6 questions for the statistics level: compute the `hetero`-family fields you can
     (at minimum variance vector and >=0 occupancy vector) from the pkl and compare against the
     same question's row in `V52_T4C3_native_heterogeneity.csv`; parse the `%.17g` strings.
   - Pick ≥10 questions (and ≥2 LoCoMo conversations): compute `sign_entropy_gt`, `zero_mass`,
     and the D4 triple (`off_mass`, `median_abs` upper-triangular |r|, `p95_abs`, on variance>0
     coordinates) using the frozen definitions file — import it, don't reimplement — and compare
     against `task1_extension_lme.json` / `task1_locoMo_stats.json` per-archive rows.
2. **Aggregate claims.** Then (and only then) open `code_certification_sign.json` /
   `certification_report.json` / the extension JSONs and check their reported aggregate values
   against your own sample and against a full recount where cheap (e.g. re-hash the zip; recount
   the number of pkls; verify the CSV's 470 rows).
3. **Extended RESULTS.json conformance.** Compare `task1_RESULTS_extended.json` field-by-field
   against `harness/ref/task1_RESULTS.json` (the frozen schema): every frozen field must be
   unchanged; every added field must trace to one of the JSONs above.
4. **Attack the prose.** In `TASK1_COMPLETION_RECEIPT.md`, hunt for any sentence that overstates
   what the evidence supports (labels, "bit-exact" vs "equal to last printed digit", scope of the
   certification). Grade each overstatement you find.

## Report format

- **Defects / discrepancies first** (each with raw command + raw output), then **confirmed
  checks**, then **what you could not check and why**, then a one-paragraph verdict on whether the
  receipt's claims are supported at the strength claimed.
- State explicitly that you did step 1 before opening the package's own certification outputs.
- No softening, no inventing findings. If everything reproduces, say exactly that.