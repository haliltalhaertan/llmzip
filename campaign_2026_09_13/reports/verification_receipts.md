# Verification receipts — three accepted packages (independent, read-only)

Verifier session: 2026-09-12. Repository `~/muse-work/llmzip-audit` was never
modified (no commits, pushes, checkouts inside it; only `git fetch`, `git show`,
`git cat-file`, `git ls-tree`, `git archive` reads).

Checkout deviation (forced by sandbox): `~/muse-work/verify/` and
`~/muse-work/scratch/verify/` are read-only in this session, so the ordered
`git worktree add ~/muse-work/verify/<name>` was impossible:

```text
$ git worktree add ~/muse-work/verify/preseal 4001fc9d8ea2c932042de7823713c6efce8e56d0
Preparing worktree (detached HEAD 4001fc9)
fatal: could not create leading directories of '/home/mdp/muse-work/verify/preseal/.git': Read-only file system
```

Identical-bytes substitute used: `git archive <commit> [-- <namespace>] | tar -x -C /tmp/verify/<name>`
(no worktree metadata, no repo modification). Namespace bytes below were all
re-hashed from `git cat-file` blobs independently of the extraction, so the
checkout method does not affect the evidence. Report lives at
`~/muse-work/reports/verification_receipts.md` (this session could only stage it
at `/tmp/verify/verification_receipts.md`; canonical copy attempted, see §4).

Environment actually observed (correcting the brief where it differs):
`/usr/bin/python3` is 3.14.4 with numpy 2.5.3 and scipy 1.18.1 importable
(brief said "no numpy"); `~/muse-work/faiss-python` is a `PYTHONPATH=fpylibs`
wrapper around the same interpreter. `node` is absent (`command -v node` empty).
The pinned interop venv is unusable in this sandbox:

```text
$ /mnt/c/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe --version
<3>WSL (4 - ) ERROR: UtilBindVsockAnyPort:309: socket failed 1
```

No network was used. Nothing touching Task 4F1 execution candidates or real BEAM
data was executed (G3 tree was listed, never run, outside its own namespace).

---
## 1. Preseal diagnostics namespace

- Checkout & commit: branch `research/v52-preseal-diagnostics-2026-09-12`.
  Branch tip is `9fc7fe8` ("ledger(L-093)...", touches only
  `docs/CONTINUITY_LEDGER.md`); the tasked results commit `4001fc9d8ea2c932042de7823713c6efce8e56d0`
  is its parent and holds the full namespace. Extracted
  `research/v52/preseal_diagnostics_2026_09_12/` at `4001fc9` to
  `/tmp/verify/preseal` (79 tar entries).
- Declared manifest: `5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b`.
- Recomputed hashes:
  - `sha256sum HASHES.txt` = `5bf22716…780b` — equals declared manifest. PASS.
  - Per-entry recompute: 49 entries, matched 49, mismatched 0, absent 0.
  - Coverage: 49 files on disk besides `HASHES.txt`; listed 49; extras none,
    missing none. "Hashes all files except itself" confirmed exactly.
  - `task2/HASHES.txt` (23 entries) matches `LEAD_VERIFICATION.json`
    `task2_manifest_hashes_verified: 23`. `task3/HASHES.json` lists 14 files;
    all 14 match hash+bytes, matching `manifest_hashes_verified: 14`.
  - All 16 `serialized_checks` byte sizes match files on disk (16 OK, 0 diff),
    including the 0-byte `QUIVER_STYLE48X2_COMPACT/add_0/codes.bin`.
  - `ITQ_STORAGE_RATIOS.csv` has 1881 lines = header + 1880 rows, matching
    `storage_ratio_rows: 1880` (4 variants x 470 archives; N_archive set equals
    `task2/ARCHIVE_COST_RATIOS.csv`'s 470-entry N sequence, so
    `ratio_source_sha256: 85aedf01…` pointing at the ARCHIVE_COST table is
    consistent, not a defect). `.npy` sizes 73856/36992 match claims.
  - `RESULTS.json` statuses vs files present: task1
    `PARTIAL - exact published sufficient statistics recovered; full matrices
    unavailable` (receipt present, sha matches manifest); task2 `COMPLETE`
    (present, matches); task3 `COMPLETED_SYNTHETIC_DIAGNOSTIC_NOT_ACCEPTANCE`
    (present, matches). `sealed: false`, `scientific_arm_decision: NOT_MADE` —
    consistent with README's OPEN task1 / no-decision statements.
- Verifier run (package's own reproduction, README §"Yeniden üretim"):
  ran `measure_representation_diagnostics.py` on a disposable copy
  (`/tmp/run/preseal_ns`, pristine checkout untouched):

```text
$ ~/muse-work/faiss-python -B measure_representation_diagnostics.py
  ... (report JSON to stdout; tail shows D4_reason, per-archive blocks) ...
VERIFIER_EXIT:0
BEFORE: 5108dbb993f818defad1da6a65205ff1ffd65bb68c32a48c4fe0f7591b30fba5  task1/RESULTS.json
AFTER:  bbd494439923709d0ac0251b0676bea2eb293bda2a58eb09f8ccf5a6e7f1f57a  task1/RESULTS.json
```

  Diff of committed vs regenerated (keys identical; only leaf diffs):
  `environment.{python,numpy,platform}` stamp (`3.13.15/2.3.5/Windows` vs
  `3.14.4/2.5.3/Linux`) plus three 1-ulp float diffs —
  `longmemeval/D1_ge/sd_ddof1` (`...3155` vs `...3157`) and per-archive
  `sign_entropy_ge` at indices 160 and 440 (last-digit). All means and every
  other value reproduce exactly.
- Verdict: hashes PASS (49/49 + sub-manifests + LEAD sizes). Reproduction
  exits 0 and is scientifically exact to 1 ulp, but NOT byte-exact outside the
  pinned interpreter (env stamp + numpy/BLAS rounding). No defect in the
  package; limitation is mine (pinned 3.13.15/2.3.5/Windows venv unrunnable
  here — vsock error above).
- Limitations: exact byte reproduction requires the pinned interpreter, which
  could not be launched in this sandbox, so the 1-ulp drift cannot be closed
  to zero here.

---
## 2. ITQ/Haar objective replay package

- Checkout & commit: branch `codex/v52-itq-haar-objective-2026-09-12` tip IS
  `b06bc04d544d7847d085d73f68dbd3b02aff85e2` (verified via `git rev-parse`).
  Extracted `research/v52/itq_haar_objective_comparison_2026_09_12/` to
  `/tmp/verify/itq-haar` (18 files + manifest).
- Declared manifest: `70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f`.
- Recomputed hashes:
  - `sha256sum FILE_HASHES.json` = `70d4ef2c…9f3f` — equals declared. PASS.
  - Per-entry recompute: 18 entries, matched 18, mismatched 0, absent 0.
  - Coverage: 18 files on disk besides manifest; listed 18; extras none.
- Verifier run (`verify_package.py`, read-only; README names no `.mjs`
  companion — `find` for `*.mjs`/`*.js` is empty, and node is absent anyway):

```text
$ /usr/bin/python3 -B verify_package.py
PACKAGE: PASS - 18 files
manifest_sha256=70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f
VERIFIER_EXIT:0
```

- Numerical replay (extra diligence; README's `replay_objectives.py --output`
  on a disposable copy `/tmp/run/itq`, with a local no-op `threadpoolctl`
  stub on PYTHONPATH since that module is not installed — stub disclosed,
  package untouched). Raw result:

```text
$ PYTHONPATH=/tmp/run/stubs:... /usr/bin/python3 -B replay_objectives.py --output replay_fresh
Traceback (most recent call last):
  File ".../replay_objectives.py", line 165, in <module>
    run(parser.parse_args().output)
  File ".../replay_objectives.py", line 104, in run
    require(identity(r) == expected_identity, "null rotation identity")
RuntimeError: null rotation identity
```

  Diagnosis: regenerated null rotation (seed 8312001) matches stored identity
  in shape [96,96], dtype `<f8`, order C, bytes 73728 — only
  `sha256_raw_c_bytes` differs (`a7e4db60…` vs stored `9057ca07…`). So scipy
  1.18.1's QR emits last-ulp-different (valid, sign-canonicalized) bytes than
  pinned scipy 1.17.0, and the script's exact-byte gate fails by design
  outside the locked env. Environment limitation, not package corruption.
- Corroboration of the package's own independent-review claims (all PASS):
  `replay/RESULTS.json` == `review_agent/RESULTS.json` (`f0ac1ef0…`, as
  `VALIDATION.json` states); both `objectives.csv` == `e98ce727…`; both
  `ENVIRONMENT.json` == `9b5516a8…`; `replay_objectives.py` == `3f87cc5c…`;
  and all three `source/` pins equal the raw `git cat-file` blobs at
  `4001fc9` (`18ddc99d…`, `e56ea0d6…`, `0c2cf965…`). The reviewer's exit-0
  480-exact-match replay under the pinned interpreter is therefore
  byte-plausible; it just cannot be re-executed here.
- Verdict: manifest + official verifier PASS. Numerical replay FAILS in this
  sandbox purely on the exact-byte rotation gate (scipy drift); recorded
  verbatim, nothing fixed.
- Limitations: no `.mjs` companion exists; node absent regardless. The pinned
  interpreter (only env where byte-exact replay passes) cannot run here.

---
## 3. G3 synthetic remediation delivery

- Checkout & commit: branch `codex/g3-remediation-delivery-2026-09-12` tip IS
  `7266160ac03bdd064fe75f058eae3430fbe14496` (verified via `git rev-parse`;
  its diff touches only `.../FILE_HASHES.json`). Namespace
  `drafts/v52/membership_g3_remediation_2026_09_11/`. Full tree extracted to
  `/tmp/verify/g3` for namespace reads; Task-4F1/`task4f1_*` dirs were listed
  only, never executed. README + `VERIFICATION_RECEIPT.md` read first, as
  ordered; official verifiers are `package_integrity.py` and `verify_delivery.py`
  (`verify_provenance.py` needs the original side-branch checkouts and the
  delivery clone layout, absent here — not run, recorded).
- Declared manifest: `9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d`.
- Recomputed hashes (read-only, straight from `git cat-file`/`git ls-tree`
  at `7266160`, no working tree involved):
  - `sha256(FILE_HASHES.json blob)` = `9508d125…48f33d` — equals declared. PASS.
  - 432 entries: matched 432, mismatched 0, absent 0.
  - `ls-tree` inventory (minus self) is exactly the declared list, in the
    verifier's canonical sorted order (`declared == sorted(ls)` true; the
    `7266160` "canonical inventory order" regeneration is confirmed working).
  - Manifest metadata: `status: SCOPED_SYNTHETIC_CANDIDATE_AWAITING_INDEPENDENT_AUDIT`,
    `base_commit: 4f2429b2…`, `manifest_self_excluded: true`.
- Verifier runs:
  - `package_integrity.py --ref 7266160…` executed for real from a scratch
    local clone (`/tmp/run/g3clone`; repo untouched):

```text
$ /usr/bin/python3 -B drafts/v52/membership_g3_remediation_2026_09_11/package_integrity.py --ref 7266160ac03bdd064fe75f058eae3430fbe14496
{"files": 432, "manifest_sha256": "9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d", "ref": "7266160ac03bdd064fe75f058eae3430fbe14496", "status": "PASS"}
INTEGRITY_EXIT:0
```

  - `verify_delivery.py --output evidence/verify-session-20260912` on a
    disposable namespace copy (`/tmp/run/g3ns`) — verbatim failure, no test
    ran, no evidence dir created:

```text
Traceback (most recent call last):
  File "/usr/lib/python3.14/importlib/metadata/__init__.py", line 407, in from_name
    return next(iter(cls.discover(name=name)))
StopIteration

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ...
  File ".../membership_g3_remediation_2026_09_11/verify_delivery.py", line 114, in main
    runtime()
  File ".../membership_g3_remediation_2026_09_11/verify_delivery.py", line 31, in runtime
    actual.update({k: importlib.metadata.version(k) for k in LOCK if k != 'python'})
importlib.metadata.PackageNotFoundError: No package metadata was found for scikit-learn
NO_EVIDENCE_DIR_CREATED
```

    Cause: the verifier hard-gates the exact lock
    (3.13.15/2.3.5/1.17.0/sklearn-1.8.0/pandas-2.2.3) before spawning anything;
    this sandbox has 3.14.4/2.5.3/1.18.1, pandas 3.0.5, no sklearn, no network
    to install it, and the pinned Windows venv cannot start (vsock error
    above). So the 53-method suite could not be re-executed here at all.
- Implementer receipts present and hash-covered (reported, NOT re-run here):
  `evidence/final/RESULTS.json` = PASS, 53 methods / 5959 subtests / 0 fail /
  0 errors / 0 skips, runtime exactly the pinned lock, `COMMAND.json` exit 0;
  `provenance/final/RESULTS.json` = 73 checks; `inherited/final/RESULTS.json`
  = complete, 0 failed suites. All these files are inside the 432/432
  hash-verified set.
- Defect (minor, in-package prose inconsistency — nothing fixed):
  `README.md:8` claims the updated suite passes "**54 methods / 5,961**",
  but `evidence/final/RESULTS.json` (`test_methods_observed: 53`,
  `subtests_observed: 5959`) and `VERIFICATION_RECEIPT.md` ("53 test methods;
  5,959 subtest observations") agree on 53/5959. README overstates by +1
  method / +2 subtests.
- Verdict: integrity PASS (432/432 + official script PASS). Delivery suite:
  NOT re-runnable in this sandbox (refused at runtime gate — captured
  verbatim). One stale-count defect in README prose.
- Limitations: `verify_provenance.py`/`run_inherited.py` not run (need absent
  original checkouts); suite re-execution needs the pinned venv + network,
  both unavailable.

---

## 4. Summary

| Package | Hashes | Verifier | Verdict |
|---|---|---|---|
| Preseal | 49/49, +23 +14 | repro exit 0, 1-ulp drift | PASS, env drift noted |
| ITQ/Haar | 18/18 | verify PASS; replay gated | PASS, replay env-blocked |
| G3 delivery | 432/432 | integrity PASS; suite refused | PASS hashes, 1 prose defect |

What each verifier structurally CANNOT detect (one line each):

- Preseal `HASHES.txt` (+ sub-manifests): byte-identity only — a
  scientifically wrong but stably-hashed file, or a silently substituted
  statistic, passes as long as the manifest matches it.
- ITQ/Haar `verify_package.py`: inventory + byte gate only — the 240
  historical ITQ finals are cited, never refitted, so a self-consistent but
  incorrect historical `RESULTS.json` still passes.
- G3 `package_integrity.py` + `verify_delivery.py`: byte-inventory plus a
  locked-env self-test — neither can detect real-world correctness (synthetic
  only: no corpus, gold, or retrieval), and the exact-runtime gate means no
  other environment can execute the suite at all.

Report staging: this file was assembled at `/tmp/verify/verification_receipts.md`
(canonical `~/muse-work/reports/` is read-only in this sandbox; copy attempt
below is the verbatim record).

```text
$ cp /tmp/verify/verification_receipts.md ~/muse-work/reports/verification_receipts.md
cp: cannot create regular file '/home/mdp/muse-work/reports/verification_receipts.md': Read-only file system
```

A session with write access to `~/muse-work/reports/` can promote the staged
file with the same `cp` command; its bytes are the report above.
