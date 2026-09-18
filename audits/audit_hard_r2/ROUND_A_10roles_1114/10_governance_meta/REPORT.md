# REPORT — 10_governance_meta: whole-project coverage + first-audit adjudication

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Role: audit whole-project coverage and the first audit (audit_hard_r1) itself.
Method: read-only. Branch files via `git show` against main repo
`/mnt/c/Users/MDP/dev/llmzip`; worktree sources read-only; no checkout,
fetch, commit, push, or repair. No model downloads, credentials, or API spend.
Mechanical counts: `PROJECT_COVERAGE.csv` has 22 data rows; `COVERAGE.csv`
has 18 check rows (13 reviewed/sampled, 5 NOT RUN); `evidence.json` records
10 adjudicated assertions. Originals copied to this dir
(`prior_PROJECT_COVERAGE.csv`, `prior_CONSOLIDATED_AUDIT.md`,
`prior_RUN_SCOPE.md`).

## 1. Adjudication (severity-prioritized, no forced PASS/FAIL)

### HIGH

1. **Pilot STOP has no Head-Researcher authority; project-wide STOP is an
overreach.** The STOP verdict lives in commit `8bcdef5` on the unmerged
branch `findings/top10-comparison-2026-09-15` (`e672192`), confirmed
`NOT ancestor of main` (`59b891e`). The governing HR twelve-byte budget
decision (`89d3169`, doc
`docs/v52/V52_TWELVE_BYTE_BUDGET_HR_DECISION_2026-09-11.md`) states it
"authorizes no execution, seal, pilot or run" and leaves Task 4F1
SEALED/RUN BLOCKED. `L-096` (`907750f`, unmerged) "grants no verdict or
authorization". `L-097` (on main) records a framing correction only: "no arm
winner declared, no frozen number changed". So the honest reading of STOP is
*this TF-IDF/SVD-sign-vs-lexical pilot line stops*, not *the project stops*.
The r1 consolidation's priority finding 1 is **sustained**. Limits: I did not
re-derive any STOP gate number; gate FAILs are taken from the pilot +
postcheck bodies and r1's exact recomputes.
2. **C1 gate implementation does not match its description (plus an unnamed
third defect).** `coordinator/decision_tests.py:190-191` implements C1 as
`any(vs_strongest >= 2.0 for arms)` — a point-estimate maximum over arms —
while the declared gate (`__main__` dict) requires CI-excludes-0 AND both
benchmarks. Postcheck `9993f95` confirms the two missing conditions and names
the third (`any()` max-over-arms). Severity is bounded: point estimates
already fail, so the verdict FAIL stands, but the gate **cannot certify a
PASS as written**. Any future PASS claim needs the gate rewritten first.

### MEDIUM

3. **"Gates before results" is unproven — gates and verdict share one
commit.** `FINAL_STATE.md` claims three gates "were written down *before*
the deciding tests ran (`decision_r1/cost/REFEREE.md`)". Git history shows
`REFEREE.md` and `coordinator/decision_tests.py` both first appear in
`8bcdef5` (2026-09-16 21:34), the same commit as the STOP verdict. Same-commit
is not pre-registration; joint gate/results commits do not establish it.
This matches r1 consolidation finding 7; verified from history, not assumed.
4. **FINAL_STATE is stale at the postcheck tip.** Postcheck `8f7beaa`
refutes sigma-only, rank-overflow (superseding `74e21e1`), C1b, C2, W5, C6b —
but both postcheck commits are append-only: `FINAL_STATE.md` at
`findings/audit4-postcheck-2026-09-17` tip is byte-identical to `e672192`,
still presenting the superseded σ-division mechanism as fact 3 and only five
retractions. Supersession lives only in commit bodies. A reader of
FINAL_STATE alone is misled; r1 finding 8 (no supersession banner) is
**still true**. Fix belongs to the pilot owner (banner or amended section),
not to this audit.
5. **T3 producer/artifact mismatch stands.** R1 numbers finding (committed
`coordinator/t3_perltqa_kltn.py` cannot produce `T3_PERLTQA_KLTN.json`: tuple
call convention, `built[0]`-is-vectorizer, four schema/key mismatches) was
not re-tested here but is consistent with everything read; the T3 numbers
themselves stand on r1's independent 8/8 rebuild, not on that script. The
script must be marked non-canonical or replaced by the actual producer.
6. **ITQ wording overclaim verified from files.** `claims/au_c1_itq.py:85`
fits ITQ **once** (default seed 20260916); `FRESH_SEEDS` (7) drive fresh
**RAND** arms only (`:91-124`). `HARD_AUDIT_CLAIMS.md:50` writes "7
pre-registered-fresh seeds" — wrong twice: RAND seeds, not ITQ
initializations, and "pre-registered" contradicts the pilot's own
NOT PREREGISTERED labels. Correct reading: one ITQ solution vs a
fresh-random distribution (RealTalk ITQ beats 0/7; PerLTQA inside seed noise;
sym arm reverses under the worker's alternate ties). R1 consolidation already
states this; I confirm it from the code. The changed tie rule (stable index
sort vs `TIE_SALT` det_top10) means contrasts are self-consistent but not
exact replications (~0.29 pp level spread observed in `9993f95`).

### LOW (wording / hygiene, already mitigated in-file)

7. **"101/101 checks" is arithmetically documented but quotable out of
context.** `HARD_AUDIT_NUMBERS.md` TOTALS: EXACT 84 + CLOSE 17 = 101
in-scope rows, MISMATCH 0 — but only ~23 bullets carry verdicts; 101 comes
from the rows-checked expansion (T2 42 + T1 11 + Ladder 30 + T3 18). The same
file's ledger states sampled scope (2/10 RealTalk archives fresh SVD; rest
exact re-aggregation) with an explicit NOT REVIEWED list, and the
consolidation header says "sampled audit, NOT a whole-project certificate".
**No overclaim inside the worker file**; the hazard is downstream quotation
of "101/101" without the ledger. Same for the coordinator review, which says
"not exhaustive programme validation".
8. **No cleanroom overclaim in files.** The integrity report states
"WITHOUT clone", "No clone per override (substitute documented)", and logs
clean-clone as NOT RUN; consolidation finding 9 warns against reporting an
executed universal failure. Verified; risk is downstream only.
9. **"Pre-registered-fresh" and similar MUST NOT be quoted.** See (6).
Mtime/hash discipline in r1 is correct (mtimes disclaimed; no hash-as-proof).

## 2. Governance ledger (enumerated)

Refs: 182 total — 26 local heads, 147 remote-tracking, 9 other
(`refs/muse/*`,=_measured via `git for-each-ref`). All 26 local heads match
`REFS_BEFORE.txt`. Read: `L-087` budget decision scope; `L-094` scoped G3
acceptance; `L-095` Haar replay receipt; `L-096` consolidation (unmerged,
bookkeeping only); `L-097` standardized-float framing correction (on main
`59b891e`; branch `7501991` unmerged but body carried into ledger). Pilot
STOP (`e672192`) and postcheck (`9993f95`) unmerged; main untouched by them.
Prereg drafts (`d2cfbaa`, `a73393a`) NOT REVIEWED beyond the L-092
"unapproved draft" note — pre-registration lineage remains unaudited.

## 3. Labels, drift, novelty

- Labels: REPORT/PROTOCOL/FINAL_STATE/REFEREE heads + decision-test `_label`
all carry the four-tag banner. Consistent; no prereg document found.
- Scope drift: pilot-internal STOP verdict vs project-closure language is the
live drift risk (see HIGH-1). HR scope fences (Task 4F1 sealed; budget track
only) held on every document read.
- Novelty: FINAL_STATE's six "genuinely ours" items are **NOT VERIFIED** —
`lit_r2` maps and `top10_literature_20260915/sources` were listed, no primary
source opened here or (per finding 10) in r1. Absent literature proves
nothing.

## 4. What remains outside my scope (whole-project remainder)

NOT REVIEWED by r1 and NOT RUN here (assigned to r2 roles 01–09):
F1 execution/decoder; dense-MRL/residual/alternate representations;
KV/inverse-memory; static-storage/rank/membership contracts; E1 + older
geometry theory; v52-T4F1-era bulk (~40 refs); ~147 remote-tracking refs;
agents/* work; 2.4 GB weights; run caches; LME ablation liveness. Numeric
re-verification of postcheck's matched-protocol RealTalk table (sym 46.68 vs
float_std 48.51 ns) NOT RUN here. Same-CLI provenance: partial independence
only — my file-level verifications (gate code, commit ancestry, label bytes,
seed loops) are mechanical and re-runnable, but I share the CLI family with
the authors.

## 5. Deliverables in this dir

`REPORT.md` (this file), `PROJECT_COVERAGE.csv` (22 lines),
`COVERAGE.csv` (18 checks), `evidence.json` (10 assertions),
`prior_*.csv/md` (copies of r1 originals), `STATUS.md`.
No source files modified; no heavy compute used (all probes far under 180 s;
`compute.sh` serialization not needed — no memory-intensive job was run).
