# Gate table — V52 Head32/Tail64 causal result, cold-start independent audit

Audit target commit `7799502bc3a157f874b4b1aa76f803ec2bf6432f`
on `research/v52-sign-mechanism-locomo-2026-09-04`.

Every result below was measured by the auditor from bytes or from execution. No gate result,
number, or verdict from any prior session was supplied to or used by this audit.

| Gate | Subject | Result | Established vs not falsified | Evidence |
|---|---|---|---|---|
| G1 | Preregistration genuinely preceded outcome access | **PASS** | established | `evidence/ci_provenance_verified.md`, `evidence/digest_verification.txt` |
| G2 | Frozen parameters actually frozen in executed code | **PASS** (3 non-decision-changing divergences) | established | `AUDIT_REPORT.md` §G2 |
| G3 | Source and cohort identity | **PASS** | established | `evidence/digest_verification.txt`, `evidence/locomo_end_to_end_rerun_diff.txt` |
| G4 | Primary numbers re-derived from raw + end-to-end re-run | **PASS (LoCoMo, end-to-end)**; **PASS (LongMemEval, end-to-end)**; with a stated raw-artifact gap | established | `evidence/locomo_end_to_end_rerun_diff.txt`, `evidence/longmemeval_end_to_end_rerun_diff.txt`, `evidence/rederivation_from_raw_csvs.txt` |
| G5 | Verdict follows mechanically from the preregistered rule | **PASS** | established | `evidence/rederivation_from_raw_csvs.txt` |
| G6 | Statistical honesty of the reported quantity | **PASS ON VERDICT / FAIL ON REPORTED PRECISION** | verdict established; magnitude not established | `evidence/rederivation_from_raw_csvs.txt` |
| G7 | Does the intervention establish what the claim says | **PASS via auditor-supplied control** (control absent from the executed design at the target commit) | established on LoCoMo only | `evidence/g7_random_partition_control.json` |
| G8 | Does sharding change semantics | **PASS on semantics / NOT ESTABLISHED on the word "EXACT"** | semantics established | `evidence/shard_order_independence.txt`, `evidence/longmemeval_end_to_end_rerun_diff.txt` |
| G9 | Leakage, tuning, independence | **PASS on tuning and selection / CAVEAT on "cross-benchmark"** | established | `evidence/ci_provenance_verified.md` |
| G10 | Provenance and reproducibility | **PASS** (one time-limited leg, one unreachable leg) | established | `evidence/ci_provenance_verified.md`, `evidence/digest_verification.txt` |
| G11 | Strongest argument against the result | **COMPLETED — the case weakens, does not defeat** | — | `AUDIT_REPORT.md` §G11 |

**Verdict: `AUDIT PASS WITH CAVEATS`.**

The direction and the preregistered band verdict are established. The reported *precision* of
`rho_2`, and the word *"cross-benchmark"*, must be narrowed. See `AUDIT_REPORT.md` §Verdict for
the exact claim accepted.
