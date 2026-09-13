# V9 implementer test receipt

Status: **IMPLEMENTER TEST RECEIPT ONLY — NOT INDEPENDENT REVIEW**.

Command-equivalent local run:
`python -B -m unittest -v test_consumption_gate_v9`

Observed:
- 7 tests discovered;
- 5 PASS;
- 2 SKIP (`canonical repo checkout unavailable`);
- 0 failure;
- 0 error.

Executed PASS cases:
1. `V9Context` exposes no retained `initial_snapshot` field;
2. preflight validates once but discards that snapshot from the returned context;
3. every `fresh_snapshot()` call reruns the fresh V8 chain;
4. exact-source loader ignores a monkey-patched preloaded module of the same name;
5. public entrypoint exposes no anchor/digest/guarded-digest knobs.

Skipped canonical-repo cases:
1. execute the exact V8 chain from the real repository files;
2. verify the three pinned V8 module raw SHA256 values from a repository checkout.

The skipped checks are mandatory for independent audit and are not represented as passed.

No storage measurement, retrieval, model fit, Task4F1 outcome access, HMAC, seal, finalize or run occurred.
