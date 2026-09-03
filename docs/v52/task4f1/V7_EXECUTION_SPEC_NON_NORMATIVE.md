> # ⚠ NON-NORMATIVE — EXPLANATORY ONLY
>
> **This document binds nothing and authorizes nothing.** It is not part of any sealed payload,
> it is not referenced by any checker, and no statement in it is a requirement. It exists to help
> a human understand what the Task 4F1 runner does. If it disagrees with the authorities listed
> below, **it is wrong and they are right** — do not reconcile, do not "fix" the authority to
> match this text, and do not treat anything here as a specification.

# Task 4F1 — Execution Overview (explanatory)

## Authority precedence

When you need to know what the run actually does, consult these, in this order. Nothing else has
authority, this document least of all.

1. **The accepted runner and its module constants** — `v52_t4f1_beam_retrieval.py` in the
   candidate package. Every threshold, digest, seed, count, dimension, tolerance, tie prefix,
   schema label and identifier that governs execution lives here, and only here.
2. **The dependency lock** — `DEPENDENCY_LOCK.txt`, whose digest the runner verifies.
3. **The sealed preregistration** — once one exists. It fixes the estimands, the denominators,
   the decision rule and the stop rule. None of that is decided by code.
4. **The signed run authorization** — a fresh, HMAC-signed authorization is required before any
   outcome-bearing execution. No authorization, no run.

## What the runner does, in outline

It loads a BEAM archive, fits a representation on the archive text alone, transforms queries
against that fitted model, thresholds coordinates into sign codes, ranks by Hamming distance with
a deterministic tie priority, and scores the top three against frozen gold IDs.

Four arms are evaluated. One is the native sign code. One is a signed-permutation control, which
is a mathematical identity: it must reproduce the native ordered top three and the exact
distances, and any divergence aborts rather than being reported. One is a Haar rotation family
over five preregistered seeds. One is a centred ITQ family, descriptive only.

Nuisance trials are deterministic replication identities under a fixed priority. They must be
identical. They are an integrity check and are never independent evidence.

Finalization refuses to overwrite any existing derived output, recomputes every metric from the
frozen gold rather than trusting stored values, and requires exact native-versus-control agreement
on both IDs and distances before it writes anything.

An outcome-free preflight exercises the same representation on one raw archive and a fixed
invented query string, checks sign-code digests and a stability margin, and touches no probing
question, no gold label, no ranking and no metric. The constants it compares against are in the
runner; they are deliberately not repeated here.

## Why no values appear in this document

Earlier packages restated digests, seeds and counts across several bound documents and then tried
to prove the restatements agreed. Two independent audits defeated that. Values now live in exactly
one place — the runner — and explanatory documents like this one are kept outside the sealed
payload entirely, so a stale sentence here cannot contradict anything that matters.

That is also why this file names constants rather than quoting them. If you want a value, read the
runner.

## What this document cannot tell you

Whether Task 4F1 may be run. It may not, at the time of writing: preregistration and execution are
blocked and retrieval-quality outcome access is forbidden. Those states live in
`ops/CURRENT_STATE.json` and `docs/CONTINUITY_LEDGER.md` on the canonical branch, not here.
