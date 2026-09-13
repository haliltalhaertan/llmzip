# LLM HANDOFF — llmzip mathematics, empirical tests, and corrections

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## 00. Assignment for the receiving LLM

Continue the llmzip research programme critically, not by defending previous conclusions. The user wants useful mathematics about compact retrieval, executable evidence, and honest investigation of why theory did not transfer to benchmarks. Communicate with the user in Turkish. This handoff is context, not authorization to run new experiments, modify frozen protocols, or publish claims; follow the user's current request.

**Read the correction notes before extending any theorem or quoting any measurement.** Original worker reports deliberately retain known errors. Passing self-tests is not proof that report prose or interpretations are correct.

Standing constraints:
- Keep `main` untouched. Preserve new work on an authorized side branch, never merge into main without explicit permission.
- Use **Muse Code subscription CLI only** for delegated work; do not call paid model/prover APIs or paid Hermes subagents. No surprise embedding/API costs.
- Keep original data and frozen V7/V8/V9 artifacts read-only. Task4F1 remains outside authorized measurement scope.
- Label reports with the four labels above. Prospective exploratory plans are NOT preregistration.
- The user prefers acting without unnecessary clarification, parallel Muse tasks with bounded scope, and concise progress reports. Do not promise a discovery.
- Distinguish algebraic proof, finite exhaustive verification, numerical checks, real-data utility, independent audit and literature priority.

## 01. Repository, immutable anchor and reading order

Private repository: https://github.com/haliltalhaertan/llmzip

Research branch: `findings/campaign-2026-09-13`

**Pinned research snapshot reviewed for this handoff:**
`1021083d4f2faebda760546e1217b4de1eef87ea`

The branch may advance to add this handoff. Use the pinned commit above to reproduce the archived research, not a moving branch name. Main was remotely checked unchanged at:
`5ec3db60c03edde490374bf9cd7c3e56dd6bcd00`.

Main archive:
https://github.com/haliltalhaertan/llmzip/tree/1021083d4f2faebda760546e1217b4de1eef87ea/research_math_theory_2026_09_13

For paths below define:
- `A = research_math_theory_2026_09_13/`
- `M = A/math_discovery_2026_09_13/`
- `T = A/theory_benchmark_test_v1/`

Read in this order:
1. `A/README.md`: archive map and retractions.
2. `T/audit_locomo_provenance/COORDINATOR_REVIEW.md`: withdrawn +12pp claim.
3. `T/audit_mapping/COORDINATOR_REVIEW.md` and `T/audit_real_geometry/COORDINATOR_REVIEW.md`: actual reasons transfer is unproved and corrections to audit prose.
4. For the target mathematical topic, its `COORDINATOR_REVIEW.md`, then original `REPORT.md`, code and raw results.
5. `A/SOURCE_INVENTORY.json`, `A/MANIFEST.sha256`, `A/verify_archive.py` for completeness and byte integrity.

Archive scope verified: **235 files**, including manifest; **234 manifest entries**; **16 completed worker tasks = 9 mathematical investigations + 4 benchmark runs + 3 audits**. It includes original reports, scripts, results, coordinator corrections, task prompts, final logs and failed/restarted attempts. Ten derived REALTALK pickle checkpoints were excluded; their hashes/reasons are recorded and their per-QA outcomes are included. An archival count is NOT a count of new theorems or novel discoveries.

## 02. The research question and actual evaluation objects

Native SIGN96 keeps one sign bit per coordinate of centered 96-dimensional document/query vectors: `D=(C>=0)`, `Q=(qC>=0)`. Rank by Hamming distance; evaluate top3 fractional evidence recall `|retrieved ∩ gold|/|gold|`, not any-hit accuracy. Historical results use 20 seeded tie-priority trials; later analyses sometimes compute exact uniform-tie expectation. These estimands differ slightly and must be labeled separately.

Float96 stores 96 float32 values (384-byte vector payload) and uses centered cosine. SIGN96 is 12-byte vector payload. **Neither payload number includes every global/shared/index/metadata cost.** No universal losslessness or full-system 32x storage reduction was established.

Frozen native MC anchors:
- LongMemEval: 0.5419751773049645, 470 QA.
- LoCoMo: 0.23654714666441054, 1535 valid QA.
- REALTALK: 0.22477507598784194, 705 evaluated of728.
- PerLTQA: 0.488941994930817, 8265 QA,30 archives.

Current comparator status:
- LME centered float MC:0.44159574468085105; historical comparison reproduced.
- REALTALK centered float MC:0.17253405381064957; historical comparison reproduced.
- PerLTQA centered float MC:0.551692074528853; historical comparison reproduced.
- LoCoMo centered float MC:0.16826334541318252 is a **current same-cache measurement**, independently reimplemented, NOT a reproduced historical float anchor. Current SIGN-minus-float MC gap:+6.828380125122796pp.

**RETRACTION:** earlier LoCoMo approximately +12pp statements had no primary measurement support in searched programme materials. Coordinator-generated task briefs propagated that premise. Do not cite it, blame a user measurement, or claim it was explained by Haar/another baseline. Historical Haar-minus-native is a different estimand and does not rescue +12. Limited search does not prove no artifact exists anywhere.

Centering confound was previously checked: the float comparator was already centered; do not reintroduce centering as the established cause of the SIGN advantage.

## 03. Mathematical results and their limits

All paths in this section are relative to `M`. Most inequalities are standard or elementary; NO literature-priority review has established novelty.

### A. Bit-deletion bounds

`ranking_bounds/`: deleting r coordinates changes a pairwise Hamming-distance gap by at most r. If full-code topK boundary gap exceeds r, membership is unchanged. Sufficient, not necessary. Original impossibility example uses K=1; it does not directly establish the same numerical loss for K=3. Quantifiers `for every fixed subset exists failing codebook` do not prove every data-dependent selector fails.

`round2/sharp_bounds/`: from full distances d_i, retained distances lie in
`L_i=max(0,d_i-r)`, `U_i=min(s,d_i)`, s=b-r. With arbitrary binary codebooks, common query/subset and duplicate documents allowed, every product-interval choice is realizable. This gives sharp single-gold extrema. Sharpness is over compatible codebooks, NOT subsets of a fixed known codebook.

`round3/joint_gold_bounds/`: for UNWEIGHTED gold count, exact joint max places ALL golds at L and nongolds at U; min reverses the assignments. Proof uses a fixed-priority coupling: promoting a gold cannot reduce total retrieved gold count. Do not average incompatible individual maxima. Unequal gold weights break this monotonicity; shared archives can prevent simultaneous attainment across questions. No real-data bound-coverage study was run.

### B. SIGN versus cosine synthetic model

`sign_mechanism/` and `round3/all_n_ranking/`:
Model H: fixed q=(1,1,1), gold R=(1,tε1,tε2), nongolds I=(-1,tδ1,tδ2), iid nuisance signs, SAME random gold shared by all comparisons. All document norms equal. Under uniform tie priorities, for every N and K: cosine weakly dominates SIGN for0<t<1, equality at1, SIGN weakly dominates for t>1. Expected inequalities are strict in nontrivial cases1<=K<N. This theorem is specific to H, not real embeddings.

Original top3 calculation incorrectly used marginal pairwise probabilities as independent multinomial trials. Correct method: condition on shared gold first, calculate multinomial, then average. Correct N6/K3 values: SIGN1763/2048; cosine(t=.5)4067/4096; cosine(t=10)1483/2048. Coordinator code and corrections are stored. One later negative control swapped win/loss inputs and detected a mismatch for the wrong reason; main corrected calculations remain valid.

### C. Bit allocation

`bit_allocation/`: exact synthetic counterexamples show MSE-optimal allocation can be ranking-worst, and mixed precision can help or hurt. Scoring is asymmetric full-query INNER PRODUCT; target is preservation of full-precision pair order, NOT external relevance or frozen Hamming top3.

`round2/allocation_optimality/`: strict greedy witness with3-bit budget; unique best immediate choices end at(1,1,1), pair-order error117/718, while unique global optimum(2,1,0) gives41/718. Thus one-step greedy is not generally optimal. For separable MSE, diminishing marginal gains plus prefix constraints are SUFFICIENT for greedy optimality, not necessary for every individual instance. Reconstruction levels, thresholds and index maps cost storage; no free extra bits.

### D. Latest normalization-aware directions

`round4/norm_aware_sign_bounds/`:
Valid core: sign-orthant support bounds and standard Cauchy-Schwarz angle bound. If c=sign(x)/sqrt(d), rho=x·c for unit document x, u=q·c for unit full query q, then
`q·x ∈ u*rho ± sqrt((1-u^2)(1-rho^2))`.
An extra8-bit rho scalar can tighten intervals in a specially aligned synthetic top3 example, with explicit extra payload. NO benchmark coverage demonstrated. Original endpoint-attainment table is wrong under sign(0)=positive; zero-face degeneracy also needs correction. A1e-12 numerical slack is not a formal roundoff certificate. `L_i>U_j` is sufficient, not necessarily a sharp iff criterion for true ordering. Read coordinator note before using code.

`round4/rank_crossing_certificates/`:
For actual joint doc/query scaling use z=t² and rank-equivalent score
`f_i(z)=(a_i+b_i*z)/sqrt(u_i+v_i*z)` on positive-denominator domain.
Pair equality candidates satisfy degree<=3 polynomial
`P_ij=(a_i+b_i*z)^2*(u_j+v_j*z)-(a_j+b_j*z)^2*(u_i+v_i*z)`.
Check numerator signs before squaring; handle persistent ties when P identically0. Strict order is constant between genuine equality events. Cross-pair comparisons characterize stable topK sets; boundary ties and expected recall are different objects.
Implemented exact-rational procedure is CONSERVATIVE: same-sign root-containing intervals can return UNRESOLVED; no irrational-root isolation implemented. Selected real LME pair rival-above certified on z∈[1/16,1]; this is NOT the query's complete top3 certificate. Guarantee is for rational interpretation of computed coefficients, not BLAS rounding. One tangent example is abstract-function-only (u=0,a!=0 cannot arise from actual doc/query blocks); complexity and single-zero-root claims also need qualification.

## 04. Benchmark transfer results: what was actually tested

`T/PLAN.md` fixed the intervention before NEW outcomes, but historical benchmark results were already known. Exploratory, not preregistered.

For each real query, LOW48=48 coordinates with lowest(abs(q_j),j); HIGH48 is complement. Scale BOTH documents and query in chosen group by t∈{.25,.5,1,2,4}, without refitting/recentering. SIGN stays unchanged by construction. Primary contrast:
`mean[(SIGN-FLOAT) at t4 - (SIGN-FLOAT) at t.25]`.
A positive contrast means FLOAT worsened relative to invariant SIGN, not that a new compressed method improved.

| Benchmark | QA | Correct effect pp | Nominal cluster95% CI pp | Status |
|---|---:|---:|---|---|
| LME |470|-6.44326|[-9.27340,-3.68706]|Opposite direction|
| REALTALK |705|-0.09361|[-1.93300,+1.84903]|Inconclusive mean effect|
| PerLTQA |8265|+2.46415|[+1.55401,+3.44284]|Endpoint direction only; nonmonotone curve|
| LoCoMo |1535|-2.58291|[-3.77676,-1.31321]|CONDITIONAL, historical float gate bypassed|

2000 bootstrap replicates, seed20260913, whole archives, question-weighted replicate means. LME470 supplied single-QA clusters; REALTALK10, LoCoMo10, PerLTQA30. Few-cluster and upstream-dependence caveats remain. Four primary tests, no pooling or familywise significance claim.

Important corrections:
- REALTALK worker used mean bootstrap estimate as point estimate. Correct raw mean above is independently recomputed; original report retained.
- LOW48(t) and HIGH48(1/t) are globally proportional transformations; cosine/Hamming agree. HIGH48 is NOT independent confirmation.
- Pointwise increasing-delta violations: LME114/470; REALTALK41/705; LoCoMo151/1535; PerLTQA961/8265. Positive PerLTQA endpoint does NOT validate monotonicity.
- PerLTQA sections disagree: events+4.94708pp, social+8.64929pp, profile-18.61862pp, dialogues-.81466pp (secondary exploratory contrasts).
- LoCoMo original SIGN gate passed; historical float gate missing. Worker should have stopped but substituted fresh baseline. Independent current reproduction cannot retroactively satisfy protocol.

## 05. Where inference failed — do not repeat these mistakes

1. **Identification:** low query magnitude was never shown to mean nuisance. A toy theorem does not identify its latent variables on arbitrary real embeddings.
2. **Normalization:** actual documents have different group norm contributions. Compare full numerator AND denominator, not only dots.
3. **Parameter mismatch, properly qualified:** H varies documents with fixed query; real test changes both, yielding t². BUT t versus t² alone does not explain reversed dominance: the exact H family with joint scaling still has the same crossover against SIGN at t=1.
4. **Oracle examples are not prediction:** selecting gold/rival after observing a flip is descriptive. A random nuisance term can favor gold by chance; one positive group-dot witness does not prove statistical relevance.
5. **Actual witness correction:** LME15745da0, gold56/rival368, t4: gold dot1.02997959496 < rival1.04672119662, but gold norm1.76610890175 < rival1.81716646361 and cosines .54573812 > .53902568. Worker said numerator alone overcame deficit; FALSE. Normalization is essential here.
6. **Dependence:** shared gold invalidates unconditional multinomial; shared archives require cluster-aware inference but do not alone prove every stochastic independence claim false.
7. **Uncertainty:** CI spanning0 is inconclusive, not falsification because estimate is negative. A valid conditional theorem can coexist with unsupported transfer.
8. **Provenance:** repeated +12pp text was not independent evidence. Preserve retractions explicitly.

## 06. Prior engineering context (already preserved; not the main next research task)

Static-storage accounting had duplicate-copy denominator inflation and loader/test weaknesses. Additive integrated V10 candidate:
`9802b49fe7b662f873f985c39790d4f6ca16523d`
branch `findings/static-integrated-v10-2026-09-13`.

Public entrypoint:
`drafts/v52/static_storage_integration_v10_2026_09_13/static_storage_preflight_v10.py:preflight_longmemeval_v10`.

Coordinator reran12/12 integration tests and7/7 adversarial E2E tests. Valid-plan940 distinct copies still yielded231606 unique logical vectors. Physical byte costs must not be deduplicated. Old V7/V8/V9 remain historical and are not upgraded by merely keeping their files. This is a tested repair candidate, not universal security certification or a completed storage measurement.

Index/evidence: `static_storage_review_2026_09_13/README.md` on campaign branch. Previous research: `campaign_2026_09_13/README.md`.

## 07. Environment and reproduction

Local host Windows10; terminal tools use MSYS bash. Native Windows executables require `C:/Users/MDP/...`, not `/c/...`. WSL distribution Ubuntu, Linux home `/home/mdp`.

- Repo: `C:/Users/MDP/dev/llmzip`
- Publication worktree: `C:/Users/MDP/dev/llmzip-work/github-publish-static`
- Original research inputs/outputs: `C:/Users/MDP/dev/llmzip-work`
- WSL workers: `/home/mdp/muse-work/<task>`
- Existing NumPy interpreter: `/home/mdp/muse-work/ml-python -B` (observed Python3.14.4,NumPy2.5.3); verify live environment before use.
- Set OMP/MKL/OPENBLAS/NUMEXPR thread counts to1 and PYTHONDONTWRITEBYTECODE=1.
- Muse observed version1.2.1. Tasks use `muse exec --disable-approval --trust-workspace --reasoning-effort high --prompt-file <absolute-path>` in isolated directories. Use early STATUS/checkpoints and notification-enabled background runs. Laptop shutdown interrupted a wave; early outputs were absent, so it restarted. Model-stream180s idle timeouts also happened; logs are retained. Do not assume historical task PIDs are live.

Archive-only reproduction (requires authorized access to private GitHub; no credentials in this handoff):

```bash
git clone --branch findings/campaign-2026-09-13 https://github.com/haliltalhaertan/llmzip.git llmzip-review
cd llmzip-review
git checkout --detach 1021083d4f2faebda760546e1217b4de1eef87ea
python3 -B research_math_theory_2026_09_13/verify_archive.py
```

On Windows use your actual Python executable (`python -B` if appropriate). Verifier is stdlib-only, checks16 workers,235-file archive coverage via234 manifest hashes, required correction pairs, four dataset counts, and raw mean contrasts. **It does not verify every theorem or regenerate embeddings.**

Original worker verification scripts may have absolute paths or write results in their own directory; run copies in an isolated scratch location, not in a frozen archive tree. Inspect before executing. For full vector recompute restore required original caches; the review archive intentionally does not contain every heavy input.

Previously uploaded heavy backup:
https://drive.google.com/drive/folders/1-8DYki9uXVPIVsKBAL2xCzw_LeUJH0q4
Earlier checks verified uploaded sizes, not a new remote content-hash audit. Do not claim every later cache is on Drive. Never copy credentials, .env or provider session dumps into bundles.

## 08. Current state and worthwhile next tasks

At this handoff all dispatched research workers described above completed; no automatic follow-up is assumed. Newest findings are in round4 and have unaddressed implementation/prose caveats. Everything described is preserved at the pinned research commit, but not all defects are patched in original worker files; corrections live alongside originals.

Recommended continuation, conditional on the user's request:
1. **Repair one bounded mathematical artifact before another expansive discovery wave.** Correct norm-bound endpoint/zero-face logic and build independent exact tests; distinguish analytic certificate from floating implementation. Or harden rank-crossing certificates with realizable tangent cases and exact root isolation. Do not silently overwrite originals.
2. **Test utility only after validity.** If adding a scalar or using rank intervals on real data, predeclare coverage/runtime/storage metrics and held-out evaluation. An extra byte is extra payload; query-specific code changes cannot masquerade as shared compression.
3. **Do not rescue LOW48 post-hoc.** A replacement signal/nuisance mapping needs independent identification and a new prospective/held-out test. Prior benchmarks have already been inspected.
4. **Retain LoCoMo qualification.** Current comparator is reproducible; historical +12 remains unsupported. A new honest study can use a newly frozen baseline, but cannot rewrite the past gate as passed.
5. **Independent review with output format below.** Most immediate value may be a cold-start proof/implementation audit of corrected candidates rather than more same-model self-checks.

Suggested reviewer output:
- Table: claim ID | PASS/FAIL/CAVEAT/NOT CHECKABLE | exact file/line or executed evidence | correction.
- Explicit unsupported-claim list, including scope/attainment/independence/roundoff/priority issues.
- Recompute counts and estimands from raw rows; never force agreement with summary prose.
- List missing heavy inputs separately from invalid mathematics.
- One-paragraph Turkish verdict: what is actually proved, what is merely observed, what to stop claiming, and the next smallest discriminating test.

**Final caution:** The programme has produced useful scoped mathematical tools, counterexamples and an empirical failure of a proposed transfer proxy. It has NOT yet established a new generally superior codec, a universal lossless compression theorem, or literature novelty.
