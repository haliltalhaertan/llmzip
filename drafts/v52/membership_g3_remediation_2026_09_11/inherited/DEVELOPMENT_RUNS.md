# Development-run receipt

These runs are diagnostic history. The authoritative post-integration run is inherited/final; it completed with exit 0. See final/RECEIPT.md.

| Run | Suite failures | Timeouts | Source drift | Script drift |
| --- | ---: | --- | --- | --- |
| run_001 | 3 | g3_test_pipeline | test_g3_remediation.py | not instrumented |
| run_002 | 2 | g3_test_pipeline | none | not instrumented |
| run_003 | 0 | none | none | not instrumented |
| run_004 | 0 | none | pipeline_g3.py | run_inherited.py |

- run_001: historical v5 and prep hit a Windows audit command-line representation bug in the launcher. The G3 prep subprocess timed out at 180 seconds. Assertions were not weakened.
- run_002: original pinned-arithmetic git show hit a Windows long-path stat failure because its cwd was the deeply nested synthetic directory. The G3 prep subprocess timed out at 180 seconds. Missing dependency packaging could fall back to live root imports; this run is not isolated final evidence.
- The launcher now records cwd-only routing for the exact pinned-arithmetic Git command, removes its live source directory from sys.path, copies transitive local runtime dependencies, and rejects unexpected local module origins.
- The Fraction certificate formerly recalculated exact source bits for each mask. Earlier global profiling amplified its cost. Unittest assertion counting now observes assertion methods without profiling numerical libraries. The lead subsequently optimized exact source-bit reuse while retaining all 97 masks. A new source hash requires a fresh final run.
- run_003: all ten suites passed; it remains development evidence because launcher changes were still being completed.
- run_004: all ten suites passed, including 7 historical and 7 G3 prep tests (433 unittest assertion-method calls in each). The command exited nonzero because the live pipeline and launcher changed during the run. No unexpected source module origins were observed.
- Final per-suite timeout is 600 seconds. A timeout remains a nonzero incomplete result, never an assertion pass.

Only import/path routing changes were applied to inherited test sources. No assertions were deleted, changed to xfail, skipped, or relaxed. The original-v4 controls demonstrate historical vulnerabilities intentionally. No recovered G3 test was executed as final evidence.

Pinned raw source files and synthetic tests were used. No validate_candidate/replay launcher was run. No corpus or real result was materialized.
