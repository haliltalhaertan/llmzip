# V8 implementer test receipt

Status: **IMPLEMENTER TEST RECEIPT ONLY — NOT INDEPENDENT REVIEW**.

Local sandbox execution:

`python -B -m unittest -v test_storage_semantic_gate_v8`

Observed:
- 7 tests discovered;
- 5 PASS;
- 2 SKIP (`canonical repo checkout unavailable`);
- 0 failure;
- 0 error.

Executed PASS cases:
1. fresh pinned execution ignores a monkey-patched preloaded module;
2. immutable freeze rejects a diluted V6 denominator (`10 -> 10^9`);
3. matching semantic/V6 denominator freezes successfully;
4. immutable snapshot fields reject `object.__setattr__` mutation;
5. `V8Context.refresh()` calls the full fresh-preflight path rather than trusting the initial snapshot;
6. public entrypoint exposes no anchor/digest/guarded-digest knobs.

Note: tests 3 and 4 are assertions inside one unittest method, so five executed test methods cover six checks.

Skipped repo-dependent cases:
1. execute V7 + parent guard + V6 from the real pinned repository files;
2. verify the real V7 source hash from a repository checkout.

The two skipped checks are mandatory for independent audit and are not represented as passed.

No real storage measurement, model fit, retrieval, Task4F1 corpus/query/gold/outcome access, HMAC, seal, finalize, or run occurred.
