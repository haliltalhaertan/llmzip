# V7 lead-session zero-trust verification

Status: **REQUEST_CHANGES / LEAD VERIFICATION, NOT INDEPENDENT AUDIT**.

Object inspected: `5eac888b5be36d96fd8219b91bcca8c402c34d16`.
Parent: `695e3c78aee16a719bcfdd622a6527d448f71a47`.

Task4F1 remained `SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN`.
No real storage measurement, retrieval scoring, refit, HMAC, seal, finalize, or production run occurred.

## V7-LEAD-001 — P2 BLOCKING — source hash did not pin runtime module semantics

V7 `_import_pinned_module()` authenticates the expected source file but accepts a module already present in `sys.modules` when its `__file__` resolves to the expected path. It does not reload or reconstruct the module from the authenticated bytes.

Adversarial reproduction on the exact V7 code:
1. create a source file whose `f()` returns `1`;
2. import it normally;
3. replace the in-memory `f` with a lambda returning `999`;
4. call V7 `_import_pinned_module()` with the correct path and correct SHA256.

Observed: the same preloaded module object was returned and `f()` returned `999`.

Consequence: the parent measurement guard or V6 preflight can be monkey-patched in memory while their on-disk source hashes remain correct. Therefore V7's claim that runtime semantics are mechanically tied to pinned source bytes is not established.

Required repair: execute the exact authenticated source bytes in a fresh private module namespace without `importlib.import_module`, `sys.modules` reuse, or `.pyc` authority.

## V7-LEAD-002 — P2 BLOCKING — anchored denominator can be changed after preflight and survive reverify

V7 returns frozen dataclass receipts. Python `frozen=True` blocks normal assignment but not `object.__setattr__`.

Adversarial reproduction:
- initial semantic proof denominator = `10`;
- initial physical-copy denominator = `10`;
- mutate both to `10^9` with `object.__setattr__`;
- call `V7VerifiedContext.reverify()`.

Observed: `reverify()` returned `True` while the denominator remained `10^9`.

Cause: V7 reverify hashes Plan bytes, anchor bytes and artifact bytes, but does not re-derive the semantic proof from the pinned anchor nor cross-check V6's denominator against that fresh proof.

Consequence: a post-preflight stale/mutated receipt can re-open the dilution path at the later-consumption boundary.

Required repair: no mutable/frozen-dataclass receipt may be the consumption authority. Re-run the full pinned chain immediately before use and return recursively immutable primitive snapshots; cross-check every physical denominator with a freshly derived semantic proof.

## Non-blocking auditability note

`V7_GITHUB_APPLY_RECEIPT.md` describes the pre-deployment state in which the branch still pointed at the V6 base. The final GitHub branch later moved to `5eac888b...` and Drive contains a separate `GITHUB_RECEIPT.md`. This is not a scientific defect, but reviewers should treat the older receipt as historical rather than current deployment state.

## Disposition

V7 is not eligible to open literal actual-plan preparation. Prepare an additive V8 repair and independently audit its exact pushed commit.
