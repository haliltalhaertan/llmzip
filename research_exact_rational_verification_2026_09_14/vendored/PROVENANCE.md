[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Provenance — vendored implementation (PREPARED, NOT ACCEPTED)

The two files in this directory are byte-exact copies made with
`git show origin/<branch>:<path>` (no checkout; the source branch was not touched, no file on
any existing branch was modified). VERIFIED this session by matching sha256 of the vendored
copy against a fresh `git show` pipe (identical digests, see below).

| File in this dir | Source ref | sha256 (VERIFIED) |
| --- | --- | --- |
| `t4f1_exact_rational_outcome_analysis.py` | `origin/impl/t4f1-exact-rational-analysis-2026-09-04:tools/t4f1_exact_rational_outcome_analysis.py` @ tip `4e13ac8387e1ee942fd5c51eb4bc71b0047851d5` (565 lines) | `bda67f03ea3efd989204d2943b0aca485b9eaeeb45084cbdbe82a126ed6367c9` |
| `test_t4f1_exact_rational_outcome_analysis.py` | `origin/impl/t4f1-exact-rational-analysis-2026-09-04:tools/test_t4f1_exact_rational_outcome_analysis.py` @ same tip (189 lines) | `55a83165b1848dfc2e5a46beb01dece6eba9f18009411ef22b8f9e6d1670fa54` |

Related production gate on the same branch (read but NOT vendored — VERIFIED via `git show`
this session): `tools/t4f1_authorized_exact_rational_analysis.py` (81 lines) verifies
provenance/HMAC authorization BEFORE the core parses any retrieval-quality CSV; the core is
only invoked after that gate passes. That ordering was not executed here (seal forbids it).

Status of the vendored code (RELAYED from branch history + task text, plus my own reads):
UNMERGED, UNFROZEN, UNAUDITED, never exercised on real data in this session. The vendored
copies are READ-ONLY test targets: my adversarial tests import them by path and call their
pure functions on synthetic inputs I authored. No real corpus, query, gold label, embedding,
HMAC key, or authorization was supplied at any point.

Fail-closed property (VERIFIED by code read, `vendored/t4f1_exact_rational_outcome_analysis.py`
lines 118–166 `load_cohort` and 169–212 `read_trial_rows`): the `main()` entry point cannot run
on small synthetic fixtures — it demands the sealed cohort CSV (sha256 `9b70e16f…`, exactly 1712
eligible questions with tier split 355/629/553/175) and exactly 96 archive CSVs with the full
trial-row count. Any synthetic end-to-end invocation is therefore REFUSED before any sign is
computed. That refusal is the expected fail-closed behaviour; sign/mean/category testing below
it proceeds via direct calls to `sign`, `mean_fraction`, `d_contrast`, `denominator_bound`,
`classify_primary`, `rational_payload`, `sensitivity_discordance`, `summarize_subset`,
`question_records`, and `parse_cell` on synthetic arrays.
