# V3 strict-preflight test receipt

Status: **LOCAL SYNTHETIC TEST RECEIPT / NOT INDEPENDENT AUDIT / NOT REAL ADAPTER EVIDENCE**.

Prepared and tested candidate logic: `storage_adapter_preflight_v3.py` plus `test_storage_adapter_preflight_v3.py`.

Local command:

`python -B -m unittest -v test_storage_adapter_preflight_v3`

Result: exit code `0`; 4 tests run; 4 passed.

Covered controls:

1. authenticated fixture bytes remain the consumed immutable bytes even if the original path is mutated after preflight;
2. N=0 population returns `EMPTY_NO_AMORTIZATION` with no numeric D_k, while positive population returns its count;
3. duplicate JSON keys are rejected;
4. nonfinite JSON constants are rejected;
5. extra fields inside the exact fixture transform schema are rejected.

The local Python environment emitted an unrelated `artifact_tool` spreadsheet-runtime warmup traceback during one earlier invocation; unittest still exited 0 and reported all tests OK. A subsequent strict-candidate run reported the four tests OK. This receipt does not treat environment warmup output as a V52 test result.

The pushed Git bytes still require independent re-execution. This receipt does not claim real adapter integration, storage measurement, <=12 compliance, retrieval evidence, Task4F1 access, seal or run authorization.
