# Synthetic preflight test receipt

Status: PASS_SCOPED_SYNTHETIC_PREFLIGHT_TESTS_NOT_REAL_ADAPTER

Tested `storage_adapter_preflight.py` SHA256 `1838411020e8c3f13bf24c9dfe1e241703254df5d55b1bd41e78b2e5f2291315` (9554 bytes) on Python 3.13.5 / Linux.

Command: `python -m unittest -v test_storage_adapter_preflight.py`

Result: 5 tests, exit 0.

Verified synthetic behaviors:
- valid fixture/physical bindings pass and D_k is derived from population count;
- fixture byte tamper is rejected;
- operation-section mapping change is rejected;
- physical source byte tamper is rejected;
- missing physical binding coverage is rejected.

Local test-file SHA256: `29ac1d3998c1d5e2702ea211f489d20c8dda4b27b3beb5b2134c7a93e46f62e7` (4572 bytes). The test-file upload itself was rejected by the write layer, so this receipt does not claim that file is present in GitHub.

Limits: no real fitted artifact, real adapter, storage measurement, retrieval/query/gold/outcome access, seal or run authorization.