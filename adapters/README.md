# Frozen LongMemEval adapters

These files are committed byte-for-byte from the original uploaded artifacts. Do not reformat, normalize line endings, or re-serialize them.

- `longmemeval_v52_adapter.py`
  - bytes: `23084`
  - SHA256: `0a1a39a8dc839ff969a3c90b747edd544bdae112bb59091e969ddecb00fab722`
  - Git blob: `16c1349336e143d27d9cac68198cbb50a1e6340b`
- `longmemeval_v52_adapter_v2.py`
  - bytes: `17158`
  - SHA256: `643082d6fc6b82fdd68dc7d97a77258b1d68eb1e479b2e390f13137d3dc1a218`
  - Git blob: `aa0b6f956a9bbc7f27778760c2c6fc708ae72ba1`

Both SHA256 values are the pinned values used by the frozen LongMemEval chain of custody. Their presence closes the prior raw-byte adapter provenance gap for independent audit.

Verify with:

```bash
python3 tools/verify_frozen_artifacts.py --list
```
