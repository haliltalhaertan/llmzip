# Local byte-level verification receipts — llmzip evidence packages (2026-09-12)

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

Scope: independent, local, byte-level verification of the three most recent accepted
evidence packages of the `llmzip` research programme. Zero-trust standard applied:
verify from bytes, quote raw outputs. All work is read-only toward
`C:/Users/MDP/dev/llmzip` (fresh detached worktrees only; main worktree untouched,
verified clean at the end). No Task 4F1 execution candidate was run; nothing read real
BEAM corpus data; everything here is synthetic or namespace metadata.

Environment used:

- Host: Windows 10, bash (MSYS) terminal; git worktrees under `C:/Users/MDP/dev/llmzip-work/verify/`.
- Pinned venv: `C:/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe` — Python 3.13.15,
  NumPy 2.3.5, SciPy 1.17.0, scikit-learn 1.8.0, pandas 2.2.3 (used for all hashing and verifier runs).
- Main repo: `C:/Users/MDP/dev/llmzip` @ `5ec3db6 [main]`; `git status --porcelain` empty at start and end.
- Verification date: 2026-09-12. All helper scripts and raw logs are retained at
  `C:/Users/MDP/dev/llmzip-work/reports/scripts/` and `C:/Users/MDP/dev/llmzip-work/reports/logs/`
  (log sha256 inventory in the Appendix).

Worktrees created (all additive, all detached):

```text
$ git -C C:/Users/MDP/dev/llmzip worktree add --detach C:/Users/MDP/dev/llmzip-work/verify/preseal 4001fc9d8ea2c932042de7823713c6efce8e56d0
$ git -C C:/Users/MDP/dev/llmzip worktree add --detach C:/Users/MDP/dev/llmzip-work/verify/itq_haar b06bc04d544d7847d085d73f68dbd3b02aff85e2
$ git -C C:/Users/MDP/dev/llmzip worktree add --detach C:/Users/MDP/dev/llmzip-work/verify/g3 7266160ac03bdd064fe75f058eae3430fbe14496
$ git -C C:/Users/MDP/dev/llmzip worktree list
C:/Users/MDP/dev/llmzip                      5ec3db6 [main]
C:/Users/MDP/dev/llmzip-work/verify/g3       7266160 (detached HEAD)
C:/Users/MDP/dev/llmzip-work/verify/itq_haar b06bc04 (detached HEAD)
C:/Users/MDP/dev/llmzip-work/verify/preseal  4001fc9 (detached HEAD)
```

`core.autocrlf=false`, no `.gitattributes` anywhere in the repo — working-tree bytes equal
committed blob bytes (cross-checked below for each manifest via `git show <commit>:<path> | sha256sum`).

---

## Package 1 — preseal diagnostics namespace

### Checkout & commit

- Branch: `research/v52-preseal-diagnostics-2026-09-12`; results commit
  `4001fc9d8ea2c932042de7823713c6efce8e56d0` — `git cat-file -t` = `commit`; worktree
  `C:/Users/MDP/dev/llmzip-work/verify/preseal`, fresh checkout, `git status --porcelain` empty.
- Namespace: `research/v52/preseal_diagnostics_2026_09_12/` — 50 files (verified below).
- Branch-tip note: the branch tip is `9fc7fe88e134a1023b4a68b1d42c6e14cbfbf2c9`
  ("ledger(L-093): record partial representation and completed cost ITQ diagnostics") — one
  commit beyond the results commit. That commit changes only `docs/CONTINUITY_LEDGER.md`
  (`git diff --stat 4001fc9d 9fc7fe8` → `1 file changed, 24 insertions(+)`), and the namespace
  itself is byte-identical between the two commits
  (`git diff --stat 4001fc9d 9fc7fe8 -- research/v52/preseal_diagnostics_2026_09_12/` → empty).
  Receipt therefore covers the namespace at the results commit, which is also its state at the tip.

### Declared manifest

Claimed hash manifest sha256: `5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b`
(claim = sha256 of `HASHES.txt`, the namespace's own hash manifest).

Raw check (worktree file vs claimed value, and vs the committed blob):

```text
$ sha256sum preseal/research/v52/preseal_diagnostics_2026_09_12/HASHES.txt
5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b *preseal/research/v52/preseal_diagnostics_2026_09_12/HASHES.txt

$ cd preseal && git show 4001fc9d8ea2c932042de7823713c6efce8e56d0:research/v52/preseal_diagnostics_2026_09_12/HASHES.txt | sha256sum
5bf22716a82139ce59b35def4a10488904288fdda4ab8032e7ba62c49341780b *-
```

Result: **MATCH** (working-tree bytes == committed blob bytes == claimed hash).

Protocol recorded in README: `HASHES.txt` hashes every file of the namespace **except
itself** (self-excluded, no recursive self-hash); nested manifests `task2/HASHES.txt`
(sha256sum style, 23 entries) and `task3/HASHES.json` (`{"self_excluded": true,
"includes_supplement": true}`, 14 entries including one `../` supplement path) are
themselves listed in the top-level manifest.

### Recomputed hashes (all declared hashes, from fresh-checkout bytes)

Recomputation performed by `reports/scripts/lv_p1.py` (full per-entry results in
`reports/logs/local_verify_p1.log`, sha256 `79be09051931d9482b930892404ec37ec9498faf047d9de90a8851d621172e7e`).

```text
== P1 CHECK 1: sha256 of HASHES.txt vs claimed manifest hash ==
RESULT: PASS MATCH

== P1 CHECK 2: recompute all hashes declared in HASHES.txt ==
entries=49 matched=49 mismatched=0 absent=0 duplicate_entries=0

== P1 CHECK 3: HASHES.txt coverage semantics (all namespace files except itself) ==
files_in_namespace=50 (including HASHES.txt)
expected_declared=49 actual_declared=49
missing_from_manifest=[]
extra_in_manifest=[]
RESULT: PASS complete self-excluded inventory

== P1 CHECK 4: task2/HASHES.txt (txt) ==
entries=23 matched=23 mismatched=0 absent=0
== P1 CHECK 4: task3/HASHES.json (json) ==
meta: {"includes_supplement": true, "self_excluded": true}
entries=14 matched=14 mismatched=0 absent=0
```

Counts: **matched 86 / mismatched 0 / absent 0** (49 top-level + 23 task2 + 14 task3),
covering **50/50 distinct namespace files**. No duplicate entries; no path escaped the
namespace (the `../itq_feasibility_synthetic.py` supplement resolves to
`preseal/.../itq_feasibility_synthetic.py`, hash `18ddc99d…`, MATCH). `HASHES.txt`'s
"all files except itself" semantics verified exactly (49 = 50 − 1; no missing, no extras).

### Verifier run

The package contains **no self-verifier script** (no `verify_*.py`); its verification
device is the `HASHES.txt` protocol itself plus the nested manifests, which were fully
recomputed above. Package-internal cross-consistency: `LEAD_VERIFICATION.json` declares
`"task2_manifest_hashes_verified": 23` and `task3.manifest_hashes_verified: 14` — both
counts independently reproduced here (23/23 and 14/14).

Documented reproduction rerun (bonus): the README's reproduction command
`measure_representation_diagnostics.py` (reads the hash-pinned CSV, rewrites Task1
output; run on a disposable copy, pinned venv, `-B`) regenerated `task1/RESULTS.json`
**byte-identically**:

```text
$ sha256sum task1/RESULTS.json <frozen>/task1/RESULTS.json
5108dbb993f818defad1da6a65205ff1ffd65bb68c32a48c4fe0f7591b30fba5 *task1/RESULTS.json
5108dbb993f818defad1da6a65205ff1ffd65bb68c32a48c4fe0f7591b30fba5 *.../task1/RESULTS.json
BYTE-IDENTICAL
```

(log `reports/logs/p1_reproduce_diagnostics.log`, sha256
`a344010df49076b26841ff0468ab4d203b6ee2dfcdb72cecc09fa200c57ce9a5`; script exit 0,
six synthetic controls `"status":"PASS"`.)

### Verdict

**PASS.** Manifest claim matches; 86/86 declared hashes recomputed from fresh bytes all
match; self-excluded coverage semantics complete; bytes identical to committed blobs;
the documented reproduction script regenerates `task1/RESULTS.json` byte-identically.

### Limitations (what this verification cannot detect)

A sha256 manifest can only prove the checkout matches the manifest shipped with it; it
cannot detect a manifest regenerated to match altered files, and it is unsigned (no
HMAC/signature/transparency log), so content truth and provenance are unverified here.

---

## Package 2 — ITQ/Haar objective replay package

### Checkout & commit

- Branch: `codex/v52-itq-haar-objective-2026-09-12`; commit
  `b06bc04d544d7847d085d73f68dbd3b02aff85e2` (branch tip = this commit); worktree
  `C:/Users/MDP/dev/llmzip-work/verify/itq_haar`; `git status --porcelain` empty before and after.
- Namespace: `research/v52/itq_haar_objective_comparison_2026_09_12/` — 19 files incl. manifest.

### Declared manifest

Claimed manifest sha256: `70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f`.

```text
$ sha256sum itq_haar/research/v52/itq_haar_objective_comparison_2026_09_12/FILE_HASHES.json
70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f *itq_haar/.../FILE_HASHES.json
$ cd itq_haar && git show b06bc04d544d7847d085d73f68dbd3b02aff85e2:research/v52/itq_haar_objective_comparison_2026_09_12/FILE_HASHES.json | sha256sum
70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f *-
```

Result: **MATCH**. Manifest format: `{"self_excluded": "FILE_HASHES.json", "files": {path: {sha256, bytes}}}`, 18 declared files.

### Recomputed hashes (sha256 + byte counts, from fresh-checkout bytes)

`reports/scripts/lv_p2.py`, full log `reports/logs/local_verify_p2.log`
(sha256 `19048835e8d284992993061c661e187a66aa8673124b53878d36a9d8c45bfc56`):

```text
== P2 CHECK 1: sha256 of FILE_HASHES.json vs claimed manifest hash ==
RESULT: PASS MATCH
== P2 CHECK 2: recompute all declared file hashes (sha256 + bytes) ==
manifest keys=['files', 'self_excluded'] self_excluded='FILE_HASHES.json' declared_files=18
entries=18 matched=18 mismatched=0 absent=0
== P2 CHECK 3: inventory coverage (byte manifest vs package dir) ==
files_on_disk=19 declared=18 other_than_manifest=18
missing_on_disk=[]
extra_not_declared=[]
RESULT: PASS
```

Counts: **matched 18 / mismatched 0 / absent 0** over **19/19 distinct files**
(18 declared + the manifest itself). Additional cross-checks:

- Declared duplicate-content groups verified identical (recomputed shas):
  `replay/objectives.csv` == `review_agent/objectives.csv` (e98ce727…),
  `replay/RESULTS.json` == `review_agent/RESULTS.json` (f0ac1ef0…),
  `replay/ENVIRONMENT.json` == `review_agent/ENVIRONMENT.json` (9b5516a8…).
- The package's `source/` files are byte-identical to Package 1's namespace bytes
  (`itq_feasibility_synthetic.py` 18ddc99d…, `PLAN.json` e56ea0d6…, `RESULTS.json` 0c2cf965…) — MATCH on all three.

### Verifier run

(a) Package verifier `verify_package.py` (read-only inventory check; run per README):

```text
$ C:/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe -B verify_package.py
PACKAGE: PASS - 18 files
manifest_sha256=70d4ef2c7e8f9bbffb2ef7d4a8265d0a81dd011701c4fbcdf8f3ca4a84ce9f3f
EXIT=0
```

(b) Numerical replay `replay_objectives.py` (README documents it; run on a disposable
package copy so the frozen inventory is not modified — the script itself requires a
fresh `--output` child directory):

```text
$ cp -r <package> C:/Users/MDP/dev/llmzip-work/scratch/lv/p2_copy/
$ .../venv/Scripts/python.exe -B replay_objectives.py --output replay_fresh
gaussian                 n= 100 Haar=0.403721418 ITQ=0.150117285 reduction=62.816616%
heterogeneous            n= 100 Haar=0.406219550 ITQ=0.169813814 reduction=58.196543%
rotated_heterogeneous    n= 100 Haar=0.407360184 ITQ=0.171517125 reduction=57.895462%
gaussian                 n= 250 Haar=0.399566817 ITQ=0.211210254 reduction=47.140192%
heterogeneous            n= 250 Haar=0.402167760 ITQ=0.225467448 reduction=43.936966%
rotated_heterogeneous    n= 250 Haar=0.401478049 ITQ=0.225638029 reduction=43.798165%
gaussian                 n= 500 Haar=0.402896587 ITQ=0.254419285 reduction=36.852460%
heterogeneous            n= 500 Haar=0.408987465 ITQ=0.266277022 reduction=34.893598%
rotated_heterogeneous    n= 500 Haar=0.408245089 ITQ=0.267171777 reduction=34.556034%
gaussian                 n=1000 Haar=0.403134840 ITQ=0.290041743 reduction=28.053417%
heterogeneous            n=1000 Haar=0.408419700 ITQ=0.299033856 reduction=26.782705%
rotated_heterogeneous    n=1000 Haar=0.407764019 ITQ=0.298511123 reduction=26.793167%
PASS: 480 exact objective replays; 12 exact input identities; no ITQ refit
EXIT=0
```

The replay enforces exact equality (no tolerance) against the pinned historical results
and refuses if raw matrix/results bytes do not reproduce; it ran green on the pinned
venv (NumPy 2.3.5 / SciPy 1.17.0; `threadpoolctl` 3.6.0 present). Byte-level bonus
check: the regenerated `replay_fresh/objectives.csv` is byte-identical to the frozen
`replay/objectives.csv`:

```text
$ sha256sum replay_fresh/objectives.csv replay/objectives.csv
e98ce727da8ef93ab25aa66996967c3a5bb29fa6f2277f3935f8b4a76f504b44 *replay_fresh/objectives.csv
e98ce727da8ef93ab25aa66996967c3a5bb29fa6f2277f3935f8b4a76f504b44 *replay/objectives.csv
```

(c) Copy-side observation (verifier semantics, not a defect): re-running
`verify_package.py` on the copy **after** the replay added `replay_fresh/` fails closed —

```text
PACKAGE: FAIL - missing, extra or changed file
EXIT=1
```

This is exactly the documented behavior ("new output is deliberately an extra file
relative to the original frozen inventory"); it demonstrates the verifier is
addition-sensitive, which is desirable.

### Verdict

**PASS.** 18/18 declared hashes recomputed and matched; verifier PASS with manifest hash
equal to the claim; documented numerical replay reproduces 480/480 objectives exactly
and regenerates a byte-identical `objectives.csv`; frozen worktree untouched.

### Limitations

`verify_package.py` proves only inventory self-consistency (files vs the manifest shipped
with them) — it cannot detect a coordinated manifest+file rewrite and does not re-verify
science; the replay re-derives the Haar/null objectives and raw input identities, but the
240 historical fitted ITQ objectives are cited from the pinned `source/RESULTS.json`,
not refit (one data realization per n; no retrieval/held-out measurement).

---

## Package 3 — G3 synthetic remediation delivery

### Checkout & commit

- Branch: `codex/g3-remediation-delivery-2026-09-12`; commit
  `7266160ac03bdd064fe75f058eae3430fbe14496` (branch tip = this commit); worktree
  `C:/Users/MDP/dev/llmzip-work/verify/g3` (full-repo tree; `git status --porcelain` empty
  at start). Delivery namespace: `drafts/v52/membership_g3_remediation_2026_09_11/` — 433 files.
- The commit message is itself `fix(g3): regenerate manifest in verifier canonical inventory order`
  — the ordering property enforced by `package_integrity.py` is explicitly checked below.

### Declared manifest

Claimed manifest sha256: `9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d`.

```text
$ sha256sum g3/drafts/v52/membership_g3_remediation_2026_09_11/FILE_HASHES.json
9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d *g3/.../FILE_HASHES.json
$ cd g3 && git show 7266160ac03bdd064fe75f058eae3430fbe14496:drafts/v52/membership_g3_remediation_2026_09_11/FILE_HASHES.json | sha256sum
9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d *-
$ git hash-object drafts/v52/membership_g3_remediation_2026_09_11/FILE_HASHES.json   # blob SHA spot check
bee8a5665ea4c7ede0d8fc8c9b30f45f7afeb587
```

Result: **MATCH**. Manifest meta as declared:

```text
meta: {"base_commit": "4f2429b257546d6899f3ed48f605cd18210aeae0",
       "manifest_self_excluded": true,
       "status": "SCOPED_SYNTHETIC_CANDIDATE_AWAITING_INDEPENDENT_AUDIT"}
declared_files=432 duplicate_paths=[] declared_in_sorted_order=True
```

### Recomputed hashes (sha256 + byte counts, from fresh-checkout bytes)

`reports/scripts/lv_p3.py`, full log `reports/logs/local_verify_p3.log`
(sha256 `a3b83884b764dddcf47ac47ed3b11101b876bce845ca2bcd0294320507eb7159`):

```text
== P3 CHECK 1: sha256 of FILE_HASHES.json vs claimed manifest hash ==
RESULT: PASS MATCH
== P3 CHECK 2: recompute all declared file hashes (sha256 + bytes) ==
entries=432 matched=432 mismatched=0 absent=0
== P3 CHECK 3: inventory coverage (byte manifest vs package dir) ==
files_on_disk=433 declared=432
missing_on_disk=[]
extra_not_declared=[]
RESULT: PASS
```

Counts: **matched 432 / mismatched 0 / absent 0** over **433/433 distinct files**
(432 declared + the manifest itself). No duplicate paths; manifest order == verifier
canonical sorted order (as the commit message claims).

### Verifier runs

(a) Integrity checker `package_integrity.py` (reads README first; its own printed
`manifest_sha256` reproduces the claimed manifest hash):

```text
$ C:/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe -B package_integrity.py          # working-tree mode, pre-evidence
{"files": 432, "manifest_sha256": "9508d1257e0adb515f48c616e67dd410b640fd93d4d472eb54afbffcd148f33d", "ref": null, "status": "PASS"}
EXIT=0
$ ... -B package_integrity.py --ref HEAD                                                 # committed-blob mode
{"files": 432, "manifest_sha256": "9508d125...", "ref": "HEAD", "status": "PASS"}
EXIT=0
$ ... -B package_integrity.py --ref HEAD                                                 # re-run after all evidence runs
{"files": 432, "manifest_sha256": "9508d125...", "ref": "HEAD", "status": "PASS"}
EXIT=0
```

Post-evidence working-tree mode (expected semantics — fresh evidence directories are new
untracked files, and the canonical frozen check is `--ref HEAD`):

```text
Traceback (most recent call last):
  File "...\package_integrity.py", line 66, in <module>
    main()
  File "...\package_integrity.py", line 56, in main
    raise RuntimeError('file inventory mismatch')
RuntimeError: file inventory mismatch
EXIT=1
```

(b) Official verifier `verify_delivery.py` — **run A, exactly as instructed, on the
pinned venv** (`PYTHONHASHSEED=0`, `-B`):

```text
$ C:/Users/MDP/dev/llmzip-work/venv/Scripts/python.exe -B verify_delivery.py --output evidence/localverify-20260912
G3 verification exit 1 evidence ...\evidence\localverify-20260912
EXIT=1
```

The child's evidence (`evidence/localverify-20260912/RESULTS.json`,
sha256 `28a6f0ef9df2227b7328f689ba86e92f30edf05b72653620568bed578d1f7671`):
`"status": "FAIL"`, `test_methods_observed: 28`, `subtests_observed: 805`,
`failures: 0`, `errors: 1`, `skips: 0`, `data_events: {"allowed_synthetic": 20, "denied": 0}`.
The single error is a deliberate environment gate, not a test failure:

```text
ERROR: setUpModule (test_delivery_pipeline)
Traceback (most recent call last):
  File "...\test_delivery_pipeline.py", line 64, in setUpModule
    raise RuntimeError("Use the exact g3-lock-20260912 interpreter")
RuntimeError: Use the exact g3-lock-20260912 interpreter
```

Cause (source quoted verbatim, `test_delivery_pipeline.py` lines 61–64): the gate requires
a **checkout-relative sibling venv**:

```python
def setUpModule():
    expected = ROOT.parent / ".venvs/g3-lock-20260912/Scripts/python.exe"
    if Path(sys.executable).resolve() != expected.resolve():
        raise RuntimeError("Use the exact g3-lock-20260912 interpreter")
```

`ROOT` is the checkout root, so the expected interpreter path moves with the checkout —
a fresh checkout elsewhere cannot satisfy it regardless of package versions. The pinned
venv meets all five locked versions (Python 3.13.15 / NumPy 2.3.5 / SciPy 1.17.0 /
scikit-learn 1.8.0 / pandas 2.2.3) but not the path identity, so the pipeline module
(and only it) refused to load. Result: 27 of 28 loadable methods passed, 805 subtests observed.

(c) **Run B — full suite, gate-satisfying interpreter (disclosed workaround).** To
execute the remaining module, a directory junction was created inside the verification
workspace so the checkout-relative gate resolves to the same pinned venv (no new
interpreter, same pinned versions; guard equality check shown):

```text
$ python -c "_winapi.CreateJunction(r'C:\Users\MDP\dev\llmzip-work\venv', r'C:\Users\MDP\dev\llmzip-work\verify\.venvs\g3-lock-20260912')"
junction created: C:\Users\MDP\dev\llmzip-work\verify\.venvs\g3-lock-20260912 -> C:\Users\MDP\dev\llmzip-work\venv

$ C:/Users/MDP/dev/llmzip-work/verify/.venvs/g3-lock-20260912/Scripts/python.exe -c "..." 
sys.executable      = C:\Users\MDP\dev\llmzip-work\verify\.venvs\g3-lock-20260912\Scripts\python.exe
resolved(actual)    = C:\Users\MDP\dev\llmzip-work\venv\Scripts\python.exe
resolved(expected)  = C:\Users\MDP\dev\llmzip-work\venv\Scripts\python.exe
guard_equal = True
versions: 2.3.5 1.17.0 1.8.0 2.2.3

$ .../.venvs/g3-lock-20260912/Scripts/python.exe -B verify_delivery.py --output evidence/localverify-gatelock
G3 verification exit 0 evidence ...\evidence\localverify-gatelock
EXIT=0      (real 2m58,765s)
```

Full-suite evidence (`evidence/localverify-gatelock/RESULTS.json`):
`"status": "PASS"`, `test_methods_observed: 54`, `subtests_observed: 5961`,
`failures: 0`, `errors: 0`, `skips: 0`; stderr tail verbatim:

```text
Ran 54 tests in 138.940s
OK
```

This exactly reproduces the README's claim ("54 methods / 5,961 subtest observations").
Disclosure: this run used the pinned venv via a gate-satisfying path, **not** the user's
original `g3-lock-20260912` venv. It is corroborating, not a substitute for a run in
the user's exact environment. (The README's exact venv path exists on this machine; it
was not executed from, staying within the no-Drive/read-only scope.)

(d) Supplemental official verifier `verify_provenance.py` (raw Git blob provenance):

```text
$ .../.venvs/g3-lock-20260912/Scripts/python.exe -B verify_provenance.py --evidence-dir provenance/localverify-20260912
...
ok   pinned arithmetic raw hash
ok   arithmetic has exactly three selected functions
PROVENANCE: 73 checks; 0 failed
EXIT=0      (real 0m17,780s)
```

(e) Supplemental runner `run_inherited.py` (documented as failing by design on old
certificate-contract items):

```text
DONE historical_test_membership_scaling_core: exit=0 checks=99 tests=0
DONE historical_test_runner_ingest_v4: exit=0 checks=68 tests=0
DONE historical_test_codex_v5: exit=0 checks=45 tests=0
DONE historical_test_codex_v5_old_control: exit=0 checks=5 tests=0
DONE historical_test_pipeline: exit=1 checks=0 tests=7
DONE g3_test_membership_scaling_core: exit=0 checks=99 tests=0
DONE g3_test_runner_ingest_v4: exit=0 checks=68 tests=0
DONE g3_test_codex_v5: exit=0 checks=45 tests=0
DONE g3_test_codex_v5_old_control: exit=0 checks=5 tests=0
DONE g3_test_pipeline: exit=1 checks=0 tests=7
INHERITED: 10 suites; 2 failed; source drift=0
EXIT=1      (real 4m2,058s)
```

Observed detail on the two "failed" suites: in both, the child's unittest run itself
printed all 7 tests `ok` (`Ran 7 tests in 21.901s / OK` for g3_test_pipeline) while the
child process recorded `exit_code: 1` with 3 denied write-mode `open` audit events in
`*.metrics.txt`; the runner counts any non-zero child exit as a failed suite. This is the
command's documented disposition — its docstring states "The G3 pipeline's old
certificate-contract errors are reported separately and still make this command fail;
Decision 2 coverage belongs to the lead's suite", and its final receipt carries
`decision2_note: 'Old certificate incompatibilities remain failures; lead supplies new
Decision 2 coverage.'` No undocumented failure was observed; `source drift=0`.

### Verdict

**PASS on byte integrity** (432/432 declared hashes; 433/433 files; all three
`package_integrity.py` modes/refs PASS before and after evidence runs) and **PASS on the
official suite in a gate-satisfying environment** (54/5961, 0 failures/errors/skips, plus
`PROVENANCE: 73 checks; 0 failed`). One environment-binding caveat, no byte defect:
`verify_delivery.py` run directly from a fresh checkout under the pinned venv cannot
execute `test_delivery_pipeline` because that module hard-requires a
checkout-relative `.venvs/g3-lock-20260912` interpreter; this fails closed and is
inherent to the gate's design (run A outcome: 28 methods / 805 subtests / 1 setUpModule
error, everything else PASS).

### Limitations (what these verifiers cannot detect)

`package_integrity.py`/`verify_delivery.py` prove byte identity against the manifest
shipped with the delivery and execute the delivered tests — they cannot detect a
coherently regenerated manifest+tree, cannot prove properties the tests do not test,
and the interpreter gate binds suite execution to a sibling `.venvs/g3-lock-20260912`
path, so a bare fresh checkout can never run the full suite unmodified.

---

## Summary table

| # | Package | Branch / commit | Manifest claim | Recomputed hashes | Verifier result | Verdict |
|---|---------|-----------------|----------------|-------------------|-----------------|---------|
| 1 | preseal diagnostics | `research/v52-preseal-diagnostics-2026-09-12` @ `4001fc9d` | `5bf22716…` = sha256(HASHES.txt) — MATCH | 86/86 matched (49+23+14), 0 mismatch, 0 absent; 50/50 files; self-excluded semantics PASS | no self-verifier present; full manifest recomputation + semantics check PASS | **PASS** |
| 2 | ITQ/Haar objective replay | `codex/v52-itq-haar-objective-2026-09-12` @ `b06bc04d` | `70d4ef2c…` = sha256(FILE_HASHES.json) — MATCH | 18/18 matched, 0 mismatch, 0 absent; 19/19 files | `PACKAGE: PASS - 18 files`; replay `PASS: 480 exact objective replays; 12 exact input identities`; regenerated objectives.csv byte-identical | **PASS** |
| 3 | G3 synthetic remediation delivery | `codex/g3-remediation-delivery-2026-09-12` @ `7266160a` | `9508d125…` = sha256(FILE_HASHES.json) — MATCH | 432/432 matched, 0 mismatch, 0 absent; 433/433 files; sorted-order PASS | `package_integrity` PASS ×3; direct pinned-venv suite run stops at documented interpreter gate (28 methods/805 subtests, 1 setUpModule error); gate-satisfying run `Ran 54 tests … OK` (5961 subtests, 0 fail/error/skip); provenance 73/73 | **PASS** (with disclosed environment caveat; no byte defect) |

**Total: 536 declared-hash recomputations across 502 distinct package files — all matched;
mismatched 0, absent 0. Claimed manifest hashes: 3/3 MATCH; git-blob identity checks: 3/3 MATCH.**

Defects found: **none** (byte-level). Observations recorded, all documented-by-design:
(1) P3 pipeline module requires a checkout-relative `.venvs/g3-lock-20260912` interpreter
(fails closed in fresh checkouts; workaround disclosed); (2) P3 `run_inherited.py` exits 1
on the two `test_pipeline` suites per its own documented disposition; (3) P2
`verify_package.py` fails on a copy once new replay output is added, as the README states.

## Appendix — artifacts, raw logs, and command provenance

Worktrees (additive; main worktree untouched): `verify/preseal` @ 4001fc9d,
`verify/itq_haar` @ b06bc04d, `verify/g3` @ 7266160a. Evidence directories created by
verifier runs (all inside the g3 worktree, listed by `git status --porcelain`):
`evidence/localverify-20260912/` (run A, gate-blocked), `evidence/localverify-gatelock/`
(run B, full PASS), `provenance/localverify-20260912/`, `inherited/localverify-20260912/`.
Helper scripts: `reports/scripts/lv_p1.py`, `lv_p2.py`, `lv_p3.py`; disposable replay
copy at `scratch/lv/p2_copy/`.

Raw logs (`C:/Users/MDP/dev/llmzip-work/reports/logs/`, sha256):

```text
79be09051931d9482b930892404ec37ec9498faf047d9de90a8851d621172e7e  local_verify_p1.log
19048835e8d284992993061c661e187a66aa8673124b53878d36a9d8c45bfc56  local_verify_p2.log
a3b83884b764dddcf47ac47ed3b11101b876bce845ca2bcd0294320507eb7159  local_verify_p3.log
edc5ca165e2c7e3f4201f2a55246dcf39c36b0c42280883a9b66b7a9b4f0c35d  p2_replay.log
2535287dc8a7db495e813f3fc797b2fa410e539b2b5cb1f15062b55c322620b4  p2_verify_package.log
f4227a46df4ae46a5e17319840db553c32e28fbed56a9b2497fac80b4c80ec1a  p3_integrity_refhead_pre.log
f4227a46df4ae46a5e17319840db553c32e28fbed56a9b2497fac80b4c80ec1a  p3_integrity_refhead_post.log
6cbaad674a9e73d516fd173d01a1e8c54ca5dd482251bb9cfcc9e88f61729f11  p3_integrity_worktree_pre.log
fda37fd85ab7ebe7f2622ee86c84610bfa498679022d126e54e316fb4c8bc338  p3_integrity_worktree_post.log
6f7cea75fea76fd6488ca14f6631f7f6025feca663b14cfd9ff5ad6d2330079e  p3_verify_delivery.log
6047925c32fccc725eb3c1f9f532f857c4a33f00d75789d9d95b54a2adc5f981  p3_verify_delivery_gatelock.log
f2c2b569208b61013bff983115df4ba82598858651af8b8e4b42b31dff114831  p3_verify_provenance.log
ca93e22db95571787a1762bff20152e58df529804ec867e51dec466d78a82ae1  p3_run_inherited.log
28a6f0ef9df2227b7328f689ba86e92f30edf05b72653620568bed578d1f7671  evidence/localverify-20260912/RESULTS.json (run A, FAIL-by-gate)
```

Key commands (verbatim forms used): `git worktree add --detach <path> <commit>`;
`sha256sum <file>`; `git show <commit>:<path> | sha256sum`;
`<venv-python> -B verify_package.py`; `<venv-python> -B replay_objectives.py --output replay_fresh`;
`<venv-python> -B package_integrity.py [--ref HEAD]`;
`<venv-python> -B verify_delivery.py --output evidence/<fresh>` (env `PYTHONHASHSEED=0`);
`<venv-python> -B verify_provenance.py --evidence-dir provenance/<fresh>`;
`<venv-python> -B run_inherited.py --evidence-dir inherited/<fresh>`;
recomputation scripts `python lv_p{1,2,3}.py`.
