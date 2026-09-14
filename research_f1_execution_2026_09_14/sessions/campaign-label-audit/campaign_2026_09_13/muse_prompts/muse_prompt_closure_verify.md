# Muse session — CLOSURE verification of the Task1 fix round (read-only)

You are a fresh verification session. A previous review round (red-team + cold-start) raised defects;
the orchestrating session applied fixes and re-issued artifacts. Your single job: **verify the fixes
actually landed in the FINAL artifacts, and that nothing else broke.** Do not re-review the science;
do not re-open adjudicated items. Read-only: write nothing outside `/tmp/closure7/`.

## Environment

- Windows work dir: `/mnt/c/Users/MDP/dev/llmzip-work` — read-only for you.
- Repo clone (for frozen adapters): `~/muse-work/llmzip-audit` (read-only).
- Python with sklearn (needed for the ITQ spot-check): `~/muse-work/ml-python`
  (python 3.14.4, numpy 2.5.3, scipy 1.18.1, scikit-learn 1.9.1). System python3 also works for
  non-sklearn checks. No network.

## Fixes to verify (each: PASS / FAIL / CAVEAT + evidence command + observed result)

1. **NaN-safe `certify`** — `harness/lme_regen.py`: the deviation accumulator must reject
   non-finite values (e.g. an `isfinite`-based `upd` helper) instead of silently keeping a previous
   max. Verify statically (read the code) and dynamically if importable: e.g. import the module in
   /tmp and exercise the helper with `float('nan')` / `inf` inputs — a NaN must be recorded as a
   problem (or raise), never ignored. Also confirm `regen/lme/certification_report.json` has
   `n_problems: 0`, `non_finite_problems: []`, a `pkl_sha256_manifest` with 470 entries, and a
   `framing` string that discloses the BLAS contingency and the <=1e-12 substance gate.

2. **Adapter sha gate** — `harness/code_cert_v2.py` and `harness/code_cert_itq_query.py`: both must
   pin `ADAPTER_SHA` and assert the actual adapter file hash before computing. Check statically
   (grep the assert sites) AND dynamically: `sha256sum` the real adapter file
   (`llmzip-audit/adapters/longmemeval_v52_adapter.py`) and confirm it **equals the pinned
   constant** in both scripts. The stale `code_certification.json` name must not be referenced by
   any current artifact (grep the receipt).

3. **Extended RESULTS coverage** — `regen/task1_RESULTS_extended.json`: all 470
   `longmemeval.archives` rows must now carry `sign_entropy_gt`, `zero_mass`, `correlation_proxy`
   and `extension_source`; `extension.longmemeval_archives_filled` == 470. Spot-check 3 rows
   value-for-value against `regen/lme/task1_extension_lme.json` rows (same question_id).
   Also verify the frozen leaf preservation claim: every NON-null leaf present in the frozen
   `regen/lme/task1_RESULTS.json`-style source still has the identical value (wherever the frozen
   original lives — `regen/` tree; if ambiguous, say so).

4. **Receipt wording fixes** — `TASK1_COMPLETION_RECEIPT.md`: (a) NO unqualified "7/7 quantities
   **bit-equal**" claim may remain (it was downgraded to "means exact; sds/per-archive D4 to last
   ulp"); (b) §8 must list `code_certification_sign.json` + `code_certification_itq.json` (not the
   stale `code_certification.json`); (c) §4b must carry the scope qualifier referencing §7;
   (d) §7 item 3 must state the LoCoMo second-party value re-execution and the cross-stack
   `C_sha256` byte-drift caveat; (e) §6 must contain the cold-start review block with its five
   resolved defects (D1–D5) and the LoCoMo reval + ITQ cross-stack bullets. Grep for each.

5. **ITQ query-channel certificate** — `regen/lme/code_certification_itq_query.json`: must show
   `itq_query_all_seeds_exact: 470`, empty `itq_query_mismatches`, `bitorder_values: ["big"]`,
   `itq_doc_all_seeds_exact_recheck: 470`, and `adapter_sha256`/`zip_sha256` equal to the pinned
   values (adapter: `0a1a39a8...bab722`; zip: `40026fe6...13c96d` — full values are constants in
   `harness/code_cert_itq_query.py`). **Independent spot-check**: pick qids
   `["001be529","3ba21379","75f70248","e01b8e2f","gpt4_1d80365e"]` — for each, load
   `regen/lme/cache_repr/<qid>.pkl` (keys C, qC) and `codes/<qid>.npz` from
   `drive/V52_T4C2_BINARY_GEOMETRY.zip`; using `~/muse-work/ml-python`, import `fit_itq` from the
   adapter and for each of the 5 seeds check
   `packbits(C@R >= 0)` == `itq_doc_packed[i]` and `packbits(qC@R >= 0)` == `itq_query_packed[i]`.
   Report exact match counts (cross-stack last-bit flips, if any, are expected and must be
   reported, not hidden).

6. **Hash manifest** — `HASHES_TASK1.txt`: every listed file must exist and its sha256 must match
   (`sha256sum -c` works if paths are relative to llmzip-work). Report any mismatch or missing
   file verbatim. (The receipt itself and HASHES_TASK1.txt are excluded by design — not a defect.)

## Report format

For each item: `PASS`/`FAIL`/`CAVEAT`, one-line evidence (command + key output), then any leftover
uncertainty. End with a one-paragraph verdict: "fix round verified / partially verified / not
verified" + the count. Quote raw command output for anything non-PASS. No repo writes, no network,
no fixes — verify only.
