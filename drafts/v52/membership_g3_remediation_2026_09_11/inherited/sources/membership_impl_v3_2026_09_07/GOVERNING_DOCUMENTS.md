# Governing documents for this candidate — bound by commit, path and hash

This candidate branch is based on `16019724564b5ac8db4a4d2d8bb08f98feb45c09`, which **predates** the
acceptance record. The documents that govern this code therefore **do not exist on this branch**.
That is deliberate — the candidate does not carry copies of normative documents — and this file
exists so a successor does not have to guess. Read them from `main` at the commits below.

Verify from **raw Git blobs**, not from a checkout: the repository ships no `.gitattributes`, and on
a Windows clone the same file hashes differently after line-ending conversion. Use
`git show <commit>:<path> | sha256sum`.

## Normative, in precedence order R2 → R1 → draft

| # | path on `main` | commit | sha256 | status |
|---|---|---|---|---|
| 0 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_ACCEPTANCE_BINDING_2026-09-07.md` | `9b4af5949c4dc0e5054f8f522f1952ec47513f8f` | `a99d547d525594ec6c6a12ff62f2cbb701cc05de01d7094233c90f21a0d71c71` | **controlling**; its §1 sets precedence and lists the forbidden apparatus |
| 1 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R2_2026-09-07.md` | `16019724564b5ac8db4a4d2d8bb08f98feb45c09` | `39cbfcea3a93307d582f9765529d6d99c09d0204706befa6470b8b932f451669` | in force entirely |
| 2 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_DESIGN_REVISION_R1_2026-09-07.md` | `2eadc41b7133aa5c78e767ce8f1766beb48b4404` | `3d7a79b249e97a1bc2657a6782aec5e6a138f6a8c5e2681978ed66ad217b3391` | in force **except** §4 and §5 |
| 3 | `docs/v52/V52_MEMBERSHIP_UNDER_SCALING_PREREG_DRAFT_2026-09-07.md` | `56c294162412482ca85e77ea991a20eb22f65dac` | `3da80e3424a8f29bcd85ad1c0d5f5b8e97dfba857fbaaf042b2b0d06301e3399` | in force **except** §8 |

All four are also readable at `main` `3279b28c991095f9339fd22d1d99782a4582b613` or later; the commits
above are the ones that introduced each file.

## Review chain this candidate answers

| what | branch | commit | report sha256 |
|---|---|---|---|
| implementation review of v1 | `audit/v52-membership-impl-review-2026-09-07` | `68819424765ed3da89377c89980d7e42546bfe02` | `e245f0da2b0577f8940dfd906746f618638b45481280f93facb1774270bc3e98` |
| delta closure check of v2 | `audit/v52-membership-v2-closure-2026-09-07` | `712412a5947fa56374e05bf3e3a0b075d4578b6d` | `ec75beb4e054c4bc6e7c46aa5c2a006c749e2bd65b3d93f90543d31a1e19d0be` |

## Candidate lineage — every earlier version stays byte-unchanged

| version | branch | commit | core sha256 |
|---|---|---|---|
| v1 | `impl/v52-membership-under-scaling-2026-09-07` | `a6d70ff63ce44ea0f066a075853c9e93dec53122` | `707e166c80d9231d089341a804e0acdd8845781fec7560821c67b3f6d0731a00` |
| v2 | `impl/v52-membership-under-scaling-v2-2026-09-07` | `8179ce31afc8ec9a2469c801a0a5e022b4494518` | `60141d05f2285d268a88d98344770c8cb5d166168a6fa29371a1ea330db0a1e1` |
| v3 | this namespace | see the commit that added it | see `README_IMPL_V3.md` |

Nothing in v1, v2, or either audit namespace is modified by v3.
