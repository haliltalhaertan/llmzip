# V7 local test receipt

Status: **IMPLEMENTER TEST RECEIPT ONLY — NOT INDEPENDENT REVIEW.**

Candidate tested:
`storage_semantic_gate_v7.py`

Local environment:
- sandbox Python runtime available;
- no usable repository checkout;
- outbound DNS clone attempt to `github.com` failed.

Command-equivalent test execution:
`python -m unittest -v test_storage_semantic_gate_v7`

Observed result:

- 8 tests discovered;
- 6 PASS;
- 2 SKIP (`canonical repo checkout unavailable`);
- 0 failure;
- 0 error.

Executed PASS cases:
1. q=8 at anchored `N_i` is not authoritative;
2. inflated authoritative population count is rejected;
3. wrong declared `N_i` is rejected;
4. missing authoritative `(N_i,q=1)` is rejected;
5. subset archive roster is rejected;
6. public entry point exposes no caller-controlled anchor semantic or guarded-digest knobs.

Skipped repo-dependent cases:
1. real 470-row anchor + pinned parent/V6 dependencies load from the repository;
2. real anchor byte mutation fails under the fixed digest.

The skipped checks are mandatory for independent audit and are not represented as passed.

No real storage measurement, model fit, retrieval, Task4F1 corpus/query/gold/outcome access, HMAC, seal, finalize, or run occurred.
