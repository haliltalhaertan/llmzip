# Chain of Custody — repository rules

These rules exist because a real defect occurred: `V52_T4C2_PRE_RUN_SEAL.json` was
committed as a **re-serialized** copy. Its content was semantically identical to the
frozen original, but the JSON had been re-dumped with different whitespace, so its
SHA256 changed from `19883841…` to `d0541e97…` and no longer matched the value its own
`V52_T4C2_POST_RUN_MANIFEST.json` attests to.

Nothing scientific was wrong. But under a zero-trust protocol an auditor reaching that
file has to declare a BLOCKING FAILURE on the single most load-bearing chain-of-custody
artifact in the task. A packaging defect became indistinguishable from tampering.

## The rules

1. **`main` is canonical.** Only research state accepted by the Head Researcher.
2. **`audit/...` branches are for independent auditors.** Auditor working output does
   not belong on `main` until accepted.
3. **Frozen artifacts are byte-exact. Reformatting is forbidden.** Seals, manifests,
   preregistrations, method specs and sealed compute scripts are carried byte-for-byte.
   Never pretty-print, re-serialize, normalize line endings, strip trailing newlines, or
   round-trip them through a JSON/YAML library. Copy the bytes.
4. **Every frozen file has a published SHA256.** Recorded in its task manifest and
   checkable with `tools/verify_frozen_artifacts.py`.
5. **Large raw data stays in Drive**, reachable from Git by SHA256 + Drive pointer.
   See `DATASETS_AND_LARGE_ARTIFACTS.md`.
6. **Adapters and sealed scripts belong in Git**, byte-exact, as soon as raw bytes can
   be materialized. They are small, and their absence forces NOT VERIFIABLE verdicts.
7. **Every audit prompt opens with the verification instruction** (see below).

## Required first instruction in every audit prompt

> Before interpreting any result, verify every committed frozen artifact byte-for-byte
> against the corresponding manifest SHA256. Treat any mismatch as a packaging /
> chain-of-custody defect until the canonical Drive copy is independently checked.

## How to verify

```
python3 tools/verify_frozen_artifacts.py          # exit 1 on any mismatch
python3 tools/verify_frozen_artifacts.py --list   # show every checked path
```

The verifier also checks **cross-manifest bindings** — that the pre-run seal hashes to
the value the post-run manifest claims, and that the sealed compute script hashes to the
value the pre-run seal claims. That binding chain is what makes the seal meaningful.

## Repairing a mismatch

Never repair by regenerating, reformatting or re-exporting the file — that destroys the
evidence that a defect existed. Fetch the canonical Drive copy, confirm it hashes to the
manifest value, and restore those exact bytes. Record the incident.

## Current status

`python3 tools/verify_frozen_artifacts.py` reports 24 matched, 0 mismatched,
2 intentionally Drive-only, 1 compact artifact still to be committed
(`V52_T4C2_same_input_proof.csv`).

Open gap: the frozen adapters `longmemeval_v52_adapter.py` /
`longmemeval_v52_adapter_v2.py` are pinned by SHA256 in both the 4C1 and 4C2 seals but
their raw bytes have not yet been materialized from the File Library. Until they are in
Git byte-exact, every independent audit must continue to return NOT VERIFIABLE for
archive-only feature fitting and for the ITQ encode orientation.
