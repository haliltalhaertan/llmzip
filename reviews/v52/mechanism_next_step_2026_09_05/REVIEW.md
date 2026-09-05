# V52 mechanism research: audit receipt and next scientific decision

Date: 2026-09-05. Author: Codex, continuing research reviewer.

Disposition: **BYTE RECEIPT AND PERSISTED-RESULT RECONSTRUCTION PASS; ACCEPTANCE RECOMMENDED WITH INTERPRETATION CORRECTIONS.**

This is a review of an independent audit, not another cold-start audit. The reviewer has seen the research discussion. It is not a canonical acceptance, preregistration, stop-rule release or execution authorization.

## Exact handoff

- Canonical main examined: `45e6ddea247fdb8614715a717bea8015283178d0` (L-042).
- Research target: `1a33ef0d1a2715257920201f7a3db8ab4677a007`.
- Published boundary audit: `27f50f44490b419921b1d634f11006529b290a6f`, direct child of the research target.
- Audit report: `audit_v52_boundary_localization_independent_2026_09_04/AUDIT_REPORT.md`.
- Report SHA256 independently matched to its sidecar: `80f6a3aa0da5e9e81442c486cb35f11c3bf91a4384840f8cb53ff2d2d90965f3`.
- Review branch: `codex/v52-mechanism-next-step-2026-09-05`.

Main still says the boundary audit is RUNNING; its report is now published with verdict AUDIT PASS WITH CAVEATS. Publication is not acceptance. Main's next action is specifically independent receipt/hash verification. That work is now supplied here for the designated state writer. Task 4F1 remains run BLOCKED and outcome access FORBIDDEN. The default GitHub branch still points to `claude/itq-frontier-audit-wfrz6a`; explicit main was used.

The older status prose contains stale preregistration/V3 instructions. `ops/CURRENT_STATE.json` and the recent entry-point seal paragraph agree on preregistration SEALED and run BLOCKED. The continuity verifier passes anchor checks; it does not resolve those prose inconsistencies. This review makes no state transition and leaves the sole writer's files unchanged.

## Verification actually performed

`verify_evidence.py` uses only the Python standard library and pinned `git cat-file blob` inputs. It imports no research runner, downloads no corpus and performs no retrieval. It establishes:

- All 20 target files named by the auditor's `AUDIT_HASHES.json` match their SHA256, Git blob and byte-size declarations.
- The report matches its sidecar. All 21 additions in the audit commit are confined to its audit namespace. This review records an additional SHA256 inventory of those 21 files: the original AUDIT_HASHES inventory covers target files, not the complete auditor output package.
- The two per-question files contain 92,100 and 28,200 records, with 1,535 and 470 unique questions, exactly one cell per question/arm/seed, six arms and ten seeds. Native contributions agree across cells.
- All 120 seed-level arm means reconstructed from these persisted contributions match the published seed CSVs; maximum error is `1.1102230246251565e-16`.
- Native means and the boundary sets reconstruct. Historical Full-Haar denominators remain fixed inputs, not newly reproduced outcomes.

| Quantity | LoCoMo | LongMemEval |
|---|---:|---:|
| B32 rho | 0.082396 | 0.161883 |
| B48 rho | 0.303437 | 0.193872 |
| RANDOM32 rho | 0.937182 | 0.990920 |
| Sufficient tested boundaries | {32} | {32,48} |
| Direct B32 minus RANDOM32 Fractional R@3 | +8.448609 pp | +13.203121 pp |

The direct contrast is an algebraic restatement of the published arms, not a new preregistered primary endpoint. It shows the empirical membership contrast without dividing by the inherited Full-Haar gap. Its uncertainty has not been newly estimated here.

This verifies the stored-results chain, not the correctness of individual retrieval/gold joins or a fresh execution from raw data. The independent auditor reports broader A-R checks; those checks were not all repeated here. Its bootstrap was inspected statically, not rerun.

## Corrections needed in acceptance wording

1. **A frozen-panel set and a population claim are different.** `S_common={32}` is exactly the result of the frozen decision rule on the persisted panel. Question resampling does not make that descriptive fact only 73% true. The auditor's 72.95% is a frequency under its empirical bootstrap, conditional on the seed panel, fixed denominator and resampling assumptions; it is not a posterior probability of a scientific hypothesis or a guaranteed future replication rate.
2. **The bootstrap is a sensitivity analysis.** The script resamples questions with replacement and correctly shares resample indices across arms. It does not cluster by conversation/archive, resample rotation seeds, or propagate Full-Haar uncertainty. Questions sharing an archive need not be independent. A population-level interval requires a declared sampling target and appropriate dependence treatment. The exploratory analysis usefully challenges strong uniqueness language, but cannot certify complete sampling uncertainty. A frequency of zero among 20,000 resamples is not proof of zero probability.
3. **Avoid absolute integrity and robustness claims.** Recorded Git ancestry and Actions history support ordering and observed execution provenance. They cannot establish that no private/local computation ever existed. Use 'no undisclosed execution found in the inspected records', not 'no result could have existed'. Similarly, replace 'unassailable', 'nothing else' and 'no sampling argument touches this' with claims bounded to the measured contrast and inspected design.
4. **Membership is the manipulated factor, not an identified mediator.** Matching numeric Q32/Q64 while changing block membership is strong design evidence. Its downstream changes to energy mixing, sign dependence and query relevance have not been disentangled. Both datasets use the same representation pipeline; they are not independent methodological replications.
5. **The Turkish audit summary's phrase '32 tek basina yeterlidir' is ambiguous.** B32 uses all 96 coordinates under a 32/64 partition. It is not a Head32-only code. Say '32/64 bolunmesi, donmus panelde her iki veri kumesinde yeterlilik kuralini saglar'. Retain both frozen labels, including BOUNDARY-SET HETEROGENEITY PRESENT.

Recommended acceptance: accept the byte-bound audit evidence and its correctly reconstructed fixed-panel verdict, with the above external interpretation addendum. Preserve the audit and frozen research bytes. The authorized writer must record whether the stop rule is released; this review does not release it.

## What is known and what may be distinctive

Binary Hamming retrieval, PCA-based hashing, rotation-based coding and subspace allocation have substantial prior art. Binary memory retrieval on LoCoMo/LongMemEval is already present in Hippocampus. The defensible contribution candidate is the controlled comparison between spectral block membership and matched random membership under this particular SIGN96 pipeline. The present search did not identify an exact predecessor; it does not prove priority.

Literature corrections reviewed in this conversation should be persisted by the literature owner: C1 revise; C2 narrow; C8 refuted; C9 a search-qualified narrow claim. These references are navigation to primary sources, not a completed systematic-search log:

- Xiao, [arXiv:2605.17524v2](https://arxiv.org/html/2605.17524v2), 29 May 2026. Appendix G targets ranking-fidelity response, while H distinguishes heterogeneity's magnitude-bit benefit from absolute fidelity. Its shuffle and synthetic correlated-block probes must be acknowledged. Its contrastive Gaussian assumptions do not establish the mechanism of archive-local TF-IDF/SVD.
- [Hippocampus, MLSys 2026](https://proceedings.mlsys.org/paper_files/paper/2026/hash/a1d04870cf83a0f29819d66f1dfdbfcb-Abstract-Conference.html): binary signatures and memory retrieval on the two benchmarks.
- [Pairwise Rotation Hashing](https://arxiv.org/abs/1501.07422): rotational quantization/entropy trade-offs.
- [R2PCAH](https://www.sciencedirect.com/science/article/abs/pii/S0925231217300504): top PCA projections, rotations/shifts and concatenated short codes. Publisher-exposed method text was available; the paywalled full article was not read.

## One next scientific target, after closure

**Test whether relative coordinate scale contributes to the damage caused by cross-band mixing.** This is a research direction for the next decision, not an executable experiment package. No new seeds, workflow, run trigger or preregistration is issued here, consistent with the current stop rule.

For any positive diagonal matrix D, `sign(x D) = sign(x)`. Thus a common positive, archive-derived coordinate rescaling can preserve the native sign code exactly while changing `sign(x D Q)` after an orthogonal mixing Q. This creates a useful intervention: changes in rotated retrieval cannot be attributed to a change in the unrotated sign baseline. Query labels/outcomes must not determine D. Standard deviations would have to be defined on the exact centered archive representation, not assumed equal to raw SVD singular values. Zero-variance coordinates and numerical underflow require fixed handling before a run.

The decisive future comparison should be an interaction: does rescaling improve full mixing more than within-head/tail mixing, using paired queries and fixed rotations? A reduction in the native/full gap alone would be incomplete evidence. Rescaling before rotation changes continuous geometry, so norm/dot equality must be checked within each transformed representation and its rotation; it is not expected between the original and rescaled representations. A positive result supports scale participation, not exclusive mediation or improved production retrieval. A null result restricts this specific intervention, not every energy-based explanation.

Before authorizing that work: freeze the scale rule, handling of degenerate coordinates, arms, seeds, direct paired estimand, decision threshold, sampling unit and stopping rule. Preserve per-question and archive identities for all arms, including fresh full-Haar controls if authorized. Treat old outcomes as hypothesis-generating; additional seeds on the same questions do not create independent dataset evidence. Prefer this bounded mechanism test over a finer boundary search, because PC32 uniqueness is currently a less informative question than why cross-band mixing loses retrieval quality.

## Next action and reproduction

The sole state writer should consume this pinned receipt, record acceptance plus the interpretation addendum, and explicitly decide the stop-rule disposition. The older random-partition stage remains a separate unaudited historical stage; the boundary stage's matched random arms provide current evidence without retroactively auditing the older stage. No automatic new auditor, run or canonical-state rewrite is requested.

Reproduce from this review branch with Python 3 using:

```text
python -B tools/verify_continuity_state.py
python -B reviews/v52/mechanism_next_step_2026_09_05/verify_evidence.py
```

The second command requires the pinned target/audit objects; fetch the research and boundary-audit branches if absent. `VERIFICATION.json` records exact hashes and recomputed quantities. `REVIEW_HASHES.json` binds this review's payload files and excludes itself. Git binds the inventory file.

Local validation used the bundled Python at `C:/Users/MDP/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`; the bare `python` Windows alias was unavailable. The standard-library checks do not claim to satisfy the research execution dependency lock.
