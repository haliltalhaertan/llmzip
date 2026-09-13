# Cold-start review — Task1 completion package (read-only)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Ordering statement:** I finished Step 1 (independent sample re-derivation) and wrote `/tmp/review5/step1_results.json` (sha256 `fc34f065…`, 12 LME + 2 LoCoMo samples) **before** opening any of the package's own certification/extension outputs. The marker command (`exec-12`) timestamps the sealed Step-1 file, lists the still-unopened JSONs, and only then do `exec-13+` open them. I never read `/tmp/task1indep`, `/tmp/verify`, `/tmp/run`, or any session logs.

**`[PENDING]` scope:** receipt §6 red-team line, §8 `code_certification.json [PENDING, §4b]`, and §8 provenance-hashes block are marked `[PENDING]` and treated as **out of scope**, except where a stale filename is directly observable (noted as minor doc defect D4 below).

---

## Defects / discrepancies (raw command + raw output each)

### D1. Per-archive D4 triple is NOT bit-identical to the frozen definitions — last-ulp diffs (minor numerically, load-bearing for "bit-equal" wording)

My Step-1 values were computed by **importing** `harness/ref/measure_representation_diagnostics.py` (not reimplementing), saved before opening package JSONs, then compared:

```
# /usr/bin/python3 — step1 frozen-fn value vs extension row, per archive
001be529 off 0.16317077829226864 vs 0.16317077829226861 DIFF d=2.7755575615628914e-17
001be529 med 0.005541864250629618 vs 0.005541864250629574 DIFF d=4.423544863740858e-17
001be529 p95 0.021405509935573067 vs 0.021405509935573035 DIFF d=3.122502256758253e-17
...
# 11/12 sampled LME archives show nonzero off_mass diffs; med/p95 differ in 11–12/12.
# Hgt/Hge/zero_mass are exact in all 12. Full table in exec-15 output.
```

LoCoMo, same pattern (`exec-18`):

```
locomo_0 med 0.0023902879396356354 vs 0.0023902879396356233 DIFF 1.214306433183765e-17
locomo_0 p95 0.007684031768217595 vs 0.007684031768217585 DIFF 9.540979117872439e-18
locomo_7 med ...805438 vs ...804403 DIFF -2.168404344971009e-18
# Hgt/Hge/zero_mass/off exact; med/p95 last-ulp.
```

Cause isolated (`exec-25`): re-running the identical formula inline under this session's numpy 2.5.3 reproduces **my** value (`inline off 0.16317077829226864`), not the package's (`…861`). So the extension JSONs carry the originating (Windows desktop) BLAS summation's last bit. `harness/task1_extend_lme.py`'s header ("definitions are identical", imported verbatim) is true at source level but does not confer cross-machine bit-identity for `corrcoef`/`norm`/`quantile` paths. Substantive impact is nil (~3e-17), but any "bit-exact / bit-equal" claim covering per-archive D4 is false at the last bit.

### D2. Receipt §6 "LME 7/7 quantities bit-equal" is overstated — sds differ at last ulp

```
# /usr/bin/python3 — independent report table vs current extension JSON (exec-39)
sign_entropy_ge mean exact | sd DIFF 2.168e-19 indep=0.0009689546162983157 pkg=0.0009689546162983155
off             mean exact | sd DIFF 8.674e-19 indep=0.004794137366943122 pkg=0.004794137366943121
med             mean exact | sd DIFF -8.674e-19 indep=0.0005389887508335249 pkg=0.0005389887508335258
# zero_mass, cv_sigma, p95 sd exact; all 7 means exact.
```

Combined with D1 (per-archive D4 rows differ), the correct wording is "means exact; sds and per-archive D4 agree to last ulp". The underlying independent report (`regen/muse_independent/muse_task1_independent_report.md`) was itself careful — it said LoCoMo D4 agrees "to ~1e-17 … not bit-exact" and made **no** LME bit-equality claim ("extension JSON … do not exist yet — no comparison possible"). The receipt's upgrade to "7/7 bit-equal" (repeated in §0 Turkish summary as "7/7 nicelik bit-eşit") is not supported by the numbers. Grade: prose overstatement, not a data error.

### D3. `task1_RESULTS_extended.json` fills top-level summaries but per-archive new fields remain null (470/470)

```
# /usr/bin/python3 (exec-33)
null Hgt: 470
null zm: 470
null corr: 470
```

`harness/build_extended_results.py` sets `lme["D1_gt"]`, `lme["zero_mass"]`, `lme["D4"]` at top level but never loops over `lme["archives"]`. The receipt never explicitly claims per-archive filling inside the extended file, so this is a **traceability gap, severity low**: per-archive consumers must read `task1_extension_lme.json`, not the extended RESULTS archives. The builder docstring ("fills D1_gt / zero_mass / D4") should say "top-level only".

### D4. Stale file inventory in receipt §8 (minor doc defect)

§8 lists `regen/lme/code_certification.json [PENDING, §4b]`, but the actual deliverables on disk are `code_certification_sign.json` + `code_certification_itq.json` (+ 470-line `.jsonl`). Observed via:

```
ls -la /mnt/c/Users/MDP/dev/llmzip-work/regen/lme/*.json*
# certification_report.json, code_certification_itq.json/jsonl, code_certification_sign.json,
# task1_extension_lme.json — no code_certification.json
```

### D5. §4b "certified at the exact bit level the retrieval pipeline consumed" needs its §7 qualifier inline (mild overstatement, mitigated)

Sign codes (231,606 docs + queries) and ITQ variants are the certified codes; full float bytes are explicitly **not** claimed in §7 ("not frozen-byte recovery"). §4b read alone overstates; with §7 it is correctly scoped. No data issue — grading the sentence, not the evidence.

### Non-defect note (prevents misreading)

Receipt tables round to ~16 figures while JSONs carry full precision, so receipt-vs-JSON diffs like `D4 off min JSON=0.14136795136168 RECEIPT=0.14136795136168004 DIFF -2.776e-17` (`exec-21`) are display rounding, not errors. Same for LoCoMo `D4 off mean …757 vs …76`.

---

## Confirmed checks (all reproduced here)

- **Step-1 sign-bit exact, 12/12** (`exec-11`): `np.packbits(C>=0, axis=1, bitorder='big')` and query codes match `codes/<qid>.npz` (`sign_doc_packed`, `sign_query_packed`) with 0 mismatched bytes; `gold` and `N_archive` match; `bitorder ['big']`. Samples spread over sorted indices `[0,47,94,141,188,235,282,329,376,423,469,23]`, sorted-list sha256 `7523cf1f…`.
- **Statistics level, 6/6 exact** (`exec-11`): `C.var(axis=0, ddof=0)` and `(C>=0).mean(0)` equal parsed `%.17g` CSV vectors bit-for-bit (`maxabs 0.0`, `varexact/occexact True`). CSV `%.17g` round-trip spot-check passes (`exec-40`).
- **Entropy/zero-mass exact vs extension rows** (`exec-15`, `exec-18`): `sign_entropy_gt/ge`, `zero_mass` exact in all 12 LME + 2 LoCoMo samples; active coordinates 96 everywhere sampled.
- **Input pins**: zip sha256 `40026fe6…` and CSV sha256 `148ae5b7…` re-hashed and match claims (`exec-12`); adapter sha `0a1a39a8…` matches `code_cert_v2.py` pin (`exec-34`).
- **Full recounts** (`exec-19`, `exec-20`): 470 pkls, 470 zip `codes/` members, ΣN = **231606** docs (matches cert), 470 CSV rows / 470 unique qids, 470-row extension CSV. Full exact-zero scan: **0 zeros in 22,234,176 LME entries** (470 files, all finite) and 0 in all 10 LoCoMo matrices — confirms `zero_mass = 0.0` cohort-wide and the `D1_gt ≡ D1_ge` mechanism (measurement, not assumption).
- **Extension JSON self-consistency** (`exec-23`): means/sds/mins/maxs recomputed from the 470 rows equal reported aggregates bit-for-bit.
- **ITQ coverage counts** (`exec-26`): `.jsonl` has 470 lines, 470 unique qids, uniform seeds `(101,202,303,404,505)`, zero non-all-true lines — consistent with the "2350 refits, 0 mismatches" claim at the record level.
- **Extended-RESULTS conformance** (`exec-29`, `exec-32`): every previously **non-null** frozen leaf preserved (0 diffs across 470 archives; `base_commit`/`source`/`controls`/`environment`, `D1_ge`, `D2`, `D3`, counts all preserved). Top-level fills (`D1_gt`, `zero_mass`, `D4`, `extension` block) trace to the extension/cert JSONs; `locomo.archives` equals the LoCoMo stats archives bit-for-bit. The only nulled previously-non-null strings are the two `_reason` fields, intentionally superseded (documented in builder).
- **D3/cross-benchmark rounding** (`exec-40`): LoCoMo `0.4634647/0.7508988/0.8276080`, LME `0.7599/0.4975/0.00457` all round correctly from JSON means.

---

## What I could not check and why

- **Full 470-question sign-bit sweep and 470-row hetero re-derivation**: only 12/6 sampled here; the full-coverage claim rests on the package's own (read, not re-executed) cert scripts.
- **ITQ refit re-execution**: blocked — adapter needs `sklearn`, absent in both Linux interpreters; the Windows `venv` under `llmzip-work/venv` is a Windows-only tree unusable from WSL (`exec-35`–`exec-37`). Record-level counts and adapter hash verified instead.
- **§3 producer gates** (dataset `d6f21ea9…`, seals, manifests, 500/470 cohort, parent aggregates ≤1e-12): not re-hashed/re-run except zip + CSV + adapter; the R@3 anchor `0.23654714666441054` has no artifact in my scope to compare against.
- **§2 "108 branches, no pkl" sweep**: programme repo shows 116 `branch -a` lines (consistent-ish with "108" plus remotes/HEAD), but per-branch content search was not attempted in this session.
- **[PENDING] items** (red-team review, final provenance hashes): out of scope per instructions.

---

## Verdict

The receipt's core technical claims reproduce at the strength that matters: sign codes bit-exact in all samples, hetero vectors exact, zero-mass truly zero cohort-wide (0/22.2M entries scanned), entropy equality by measurement, and aggregate means exact. The failures are all at the last bit and in the prose, not the data: per-archive D4 rows and three LME sds agree only to the last ulp across numpy/BLAS environments, so §6/§0's unqualified "7/7 bit-equal" (and any reading of "bit-exact" that extends to D4 rows) overstates by one bit and should be downgraded to "means exact, sds/per-archive D4 to last ulp"; the extended RESULTS file fills only top-level summaries while per-archive new fields stay null (consumers must use the extension JSONs); and §8's `code_certification.json` filename is stale. With those wording corrections — and with §7's "not frozen-byte recovery, not an audit" caveat kept attached to §4b — the package supports its substance.
