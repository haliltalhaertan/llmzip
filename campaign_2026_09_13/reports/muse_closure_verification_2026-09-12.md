**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Closure verification complete. All work read-only; scratch in `/tmp/closure7/`.

## 1. NaN-safe `certify` — PASS
Evidence: `grep -n "isfinite" harness/lme_regen.py` → lines 209–214:
`def upd(cur, d, tag): if d is None or not math.isfinite(d): problems.append(f"{tag}: non-finite deviation {d}"); return cur; return max(cur, d)`
Dynamic probe of the extracted helper: `nan→problems+=['t: non-finite deviation nan']`, `inf→recorded`, `None→recorded`, normal `0.7→max taken`. NaN is recorded, never silently kept.
`certification_report.json`: `n_problems: 0`, `non_finite_problems: []`, `pkl_sha256_manifest` length 470, `framing` contains both the BLAS contingency ("NumPy 2.5.3, WSL … 329/470 questions, worst 2.27e-14") and the "≤1e-12" substance gate. No uncertainty.

## 2. Adapter sha gate — PASS
Evidence: `sha256sum …/llmzip-audit/adapters/longmemeval_v52_adapter.py` → `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`, byte-equal to `ADAPTER_SHA` pinned in both `harness/code_cert_v2.py:32` and `harness/code_cert_itq_query.py:35`. Assert sites: `code_cert_v2.py:50,72,115`, `code_cert_itq_query.py:48,74` (`assert sha256_file(...) == ADAPTER_SHA`). Stale-name grep (`code_certification.json` minus suffixed variants) over receipt + `regen/` + both scripts → zero matches. No uncertainty.

## 3. Extended RESULTS coverage — CAVEAT
Evidence: `longmemeval.archives` = 470 rows, every row carries `sign_entropy_gt`, `zero_mass`, `correlation_proxy`, `extension_source`; `extension.longmemeval_archives_filled = 470`. Spot-check (001be529, 3ba21379, 75f70248 × 7 shared fields incl. `correlation_proxy`↔`corr_*` mapping) → **21/21 exact MATCH**.
Frozen-leaf check (`harness/ref/task1_RESULTS.json` vs extended, 5720 non-null leaves): **3 diffs**, verbatim:
- `root/longmemeval/D1_gt_reason 'Zero mass unavailable; >=0 is not silently substituted for >0.' -> None`
- `root/longmemeval/D4_reason 'Full correlation matrix cannot be reconstructed…' -> None`
- `root/locomo/status 'MISSING_FROZEN_MATRIX_OR_SUFFICIENT_STATISTICS' -> 'COMPUTED (LOCAL SESSION) - …'`
These are deliberate builder actions (`build_extended_results.py:53,58,78-79`: reason-for-null cleared when the value is filled; locomo block replaced). So the "0 diffs" preservation claim is literally false on 3 leaves, but each change is the intended extension semantics — hence CAVEAT, not FAIL.

## 4. Receipt wording — PASS (with note)
Evidence: (a) `grep -n "7/7"` on `TASK1_COMPLETION_RECEIPT.md` → no matches; nearest is §6 "all 7 LME means exact; sds and per-archive D4 agree to the last ulp". (b) §8 lines 276–277 list `code_certification_sign.json` + `code_certification_itq.json` (+ `_itq_query`); no stale name. (c) §4b carries "(Scope qualifier per §7: … hidden float bytes are not claimed…)". (d) §7 item 3 states the second-party LoCoMo re-execution (python 3.14.4 / numpy 2.5.3 stack) and the `C_sha256` 0/10 byte-drift caveat. (e) §6 cold-start block lists D1–D5 resolutions plus LoCoMo-reval and ITQ cross-stack bullets. Note (outside receipt scope): the exact string "7/7 quantities bit-equal" survives at `regen/task1_RESULTS_extended.json:12744`, quoting the independent executor.

## 5. ITQ query-channel certificate — PASS
Evidence: `code_certification_itq_query.json` → `itq_query_all_seeds_exact: 470`, `itq_query_mismatches: []`, `bitorder_values: ["big"]`, `itq_doc_all_seeds_exact_recheck: 470`, `adapter_sha256` = `0a1a39a8…bab722`, `zip_sha256` = `40026fe6…13c96d` (both equal the script constants; zip hash independently re-verified by `sha256sum`: exact match). Independent spot-check (`/tmp/closure7/itq_spot.py`, ml-python numpy 2.5.3, `fit_itq` imported from the sha-verified adapter, exact `packbits(C@R>=0)`/`packbits(qC@R>=0)` comparison): **QUERY 25/25 exact, DOC 25/25 exact** across the 5 required qids × 5 seeds — zero cross-stack last-bit flips, nothing hidden.

## 6. Hash manifest — PASS
Evidence: `cd llmzip-work && sha256sum -c HASHES_TASK1.txt | grep -cv ": OK$"` → `0` (every listed file exists and matches; receipt + HASHES self-exclusion as designed). No uncertainty.

## Verdict
**Fix round partially verified: 5 PASS, 1 CAVEAT, 0 FAIL.** Items 1, 2, 4, 5, 6 verified end-to-end with independent re-execution where required (upd probe, adapter/zip hashes, 25+25 ITQ refits, full `sha256sum -c`). Item 3 is CAVEAT only because 3 non-null frozen leaves changed — each traceable to an intentional builder line, but the absolute "every non-null leaf identical" phrasing overstates it.
