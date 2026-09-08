# Governing documents, the bound core, and the review chain — by commit, path and hash

This branch is based on `dcb568d0a6c33154c1568500325ad457b4d6f455`, the closed candidate v3, so the
audited core is present here **byte-unchanged** and importable. That branch in turn descends from a
commit that **predates** the acceptance record, so the normative documents do **not** exist on it.
That is deliberate — a candidate carries no copies of normative documents — and this file exists so a
successor does not have to guess. Read them from `main`.

Verify from **raw Git blobs**, not from a checkout: the repository ships no `.gitattributes`, and on a
Windows clone the same file hashes differently after line-ending conversion. Use
`git cat-file blob <commit>:<path> | sha256sum`.

## Normative, in precedence order R2 → R1 → draft

| # | path on `main` | commit | sha256 | status |
|---|---|---|---|---|
| 0 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` | `9b4af5949c4dc0e5054f8f522f1952ec47513f8f` | `a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71` | **controlling**; §4 fixes the cluster bootstrap, §6 the tolerance, §7 what is authorized |
| 1 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R2_2026-09-07.md` | `16019724564b5ac8db4a4d2d8bb08f98feb45c09` | `39cbfcea3a93307d582f9765529d6d99c09d0204706befa6470b8b932f451669` | in force entirely; line 141 forbids a LongMemEval cluster bootstrap |
| 2 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R1_2026-09-07.md` | `2eadc41b7133aa5c78e767ce8f1766beb48b4404` | `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391` | in force **except** §4 and §5 |
| 3 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_PREREG_DRAFT_2026-09-07.md` | `56c294162412482ca85e77ea991a20eb22f65dac` | `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399` | in force **except** §8 |

**None of the four binds an execution environment, and none supplies a conversation-id inventory or a
question→conversation map.** Both gaps are recorded — `ENVIRONMENT_LOCK_PROPOSAL.md` and
`RUNNER_SPEC.md` §4 — and neither was filled by invention.

## The core this runner imports — closed, and untouched

| item | value |
|---|---|
| path | `drafts/v52/membership_impl_v3_2026_09_07/membership_scaling_core.py` |
| commit | `dcb568d0a6c33154c1568500325ad457b4d6f455` |
| core sha256 | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` |
| tests sha256 | `1d426abcc908718ae2d95f0a84e323603fd05199dc3da8809d03e6795f5b2d87` |
| closure | `audit/v52-membership-v3-closure-2026-09-07` @ `aa0ee8a9b1468ceaf7fa6dc3acab17acc8423ae9`, report sha256 `aad45ff8fb6b88bda9a53b1182666ef0229a0ad2f1ff7d8baa0bf1bcca35b29a`, verdict **CLOSURE PASS** |

This runner adds a new namespace and changes **nothing** in `membership_impl_v3_2026_09_07/`,
`membership_impl_v2_2026_09_07/` or `membership_impl_2026_09_07/`.

## Review chain

| what | branch | commit | report sha256 | verdict |
|---|---|---|---|---|
| implementation review of v1 | `audit/v52-membership-impl-review-2026-09-07` | `68819424765ed3da89377c89980d7e42546bfe02` | `e245f0da2b0577f8940dfd906746f618638b45481280f93facb1774270bc3e98` | PASS WITH FINDINGS (F-1…F-12) |
| delta closure check of v2 | `audit/v52-membership-v2-closure-2026-09-07` | `712412a5947fa56374e05bf3e3a0b075d4578b6d` | `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be` | CLOSURE PASS WITH FINDINGS (NEW-1…NEW-5) |
| delta closure check of v3 | `audit/v52-membership-v3-closure-2026-09-07` | `aa0ee8a9b1468ceaf7fa6dc3acab17acc8423ae9` | `aad45ff8fb6b88bda9a53b1182666ef0229a0ad2f1ff7d8baa0bf1bcca35b29a` | CLOSURE PASS (NEW-1, NEW-2, NEW-3) |

**Closed and not to be reopened:** F-1 … F-12, NEW-1, NEW-2, NEW-3.

**Open, and deliberately separate from that list:** NEW-4 and NEW-5 (both answered here **at the
ingestion boundary only**, with the core untouched); O-1 (`build_clusters(None, 0)` leaks a
`TypeError` from `list()` one line above the NEW-3 guard); W-1 (stale `v2` version labels in the v3
test docstring — every hash they state is correct); W-2 (the v3 README understates the reach of its
own sweep). O-1, W-1 and W-2 are **not** addressed here and remain backlog.

## Candidate lineage — every earlier version stays byte-unchanged

| version | branch | commit | core sha256 |
|---|---|---|---|
| v1 | `impl/v52-membership-under-scaling-2026-09-07` | `a6d70ff63ce44ea0f066a075853c9e93dec53122` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` |
| v2 | `impl/v52-membership-under-scaling-v2-2026-09-07` | `8179ce31afc8ec9a2469c801a0a5e022b4494518` | `60141d05f2285d268a88d98344770c8cb5d166168a6fa29371a1ea330db0a1e1` |
| v3 | `impl/v52-membership-under-scaling-v3-2026-09-07` | `dcb568d0a6c33154c1568500325ad457b4d6f455` | `bc2282d3fccfe83c3e9fc36a59d7df8e4f748048ff94baebdfa4010584404e72` |
| runner v1 | this branch | see the commit that added it | — |
