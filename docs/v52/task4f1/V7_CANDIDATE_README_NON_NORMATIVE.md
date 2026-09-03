> # ⚠ NON-NORMATIVE — EXPLANATORY ONLY
>
> **This document binds nothing and authorizes nothing.** It is not part of any sealed payload and
> no statement in it is a requirement. It orients a human to the V7 candidate package. Where it
> disagrees with the runner, the dependency lock, a sealed preregistration or a signed run
> authorization, **those are right and this is wrong.**

# Task 4F1 V7 candidate — orientation (explanatory)

## What is in the sealed package

Four functional files are bound, plus the inventory and seal that bind them:

- the retrieval runner — the single home of every execution value;
- the dependency lock, whose digest the runner verifies;
- an inert run-authorization template, which cannot authorize anything;
- a package checker.

**No narrative document is bound.** This file and the execution overview beside it live here in
`docs/`, deliberately outside the package. That is the design, not an oversight.

## What the package checker actually claims

One thing, and it is narrow on purpose: the bound payload is exactly that set of functional files.
Because no document is bound, no bound document can state a requirement, so there is nothing
restated and nothing to reconcile. The check is a comparison of file names, not an inspection of
prose.

It also confirms that the runner is byte-identical to the accepted runner, that the seal records
only what was submitted for audit, and that the authorization commitment is still fail-closed.

That is the whole claim. It is smaller than what earlier packages asserted, and the reduction is
deliberate.

## Authority precedence

1. the accepted runner and its module constants;
2. the dependency lock;
3. the sealed preregistration, once one exists;
4. the signed run authorization.

This document is not on that list.

## Status

The candidate is prepared and has **not** been independently audited or sealed. Task 4F1 is
blocked for preregistration and execution, and retrieval-quality outcome access is forbidden.
Current state lives in `ops/CURRENT_STATE.json` and `docs/CONTINUITY_LEDGER.md`, not here.

The history of how the package reached this shape — including approaches that were tried and
blocked — is recorded in the continuity ledger. It is deliberately not repeated here, because a
stale description of a mechanism that no longer exists is exactly the kind of misleading text this
document is meant to stop being.
