# HARD AUDIT — TIMELINESS & INTEGRITY [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

Audit dir: `/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r1/integrity`
Main repo: `/mnt/c/Users/MDP/dev/llmzip` (READ ONLY)
Worktree under test: `/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10` (READ ONLY, branch `findings/top10-comparison-2026-09-15`)
Started: 2026-09-17 UTC. Report written incrementally, in English. NO-ARTIFACT rule: unrun checks are NOT RUN.

> Method note (mandatory corrections): file mtimes alone do NOT establish pre-registration;
> a hash snapshot detects changes, it does not prevent writes. All coordinator claims incl. STOP
> are untrusted hypotheses. This audit examines evidence; it does not certify exhaustively.

## 0. Scope ledger + inventory (evidence)
- [x] Inventory refs/worktrees (§0) — DONE
- [x] §1 Timestamps / pre-commit chronology — DONE (verdict §7 row 1)
- [x] §2 Git history + three named commits + REPORT.md diff — DONE (verdict §7 rows 2a–2c)
- [x] §3 Publication integrity (manifest sample, no clone) — DONE (verdict §7 row 3)
- [x] §4 Five retractions — DONE (verdict §7 row 4)
- [x] §5 Whole-project governance + PROJECT_COVERAGE.csv — DONE (verdict §7 row 5)
- [x] §6 Explicit-challenge items — DONE (verdict §7 row 6)
- [x] §7 Verdict table + coverage ledger — DONE
(Note: sections were appended incrementally per the step-by-step rule, so §3–§4 precede
§1–§2 in file order; content is complete. Finished: 2026-09-17 UTC.)

Refs (read-only `git -C /mnt/c/Users/MDP/dev/llmzip`, observed 2026-09-17):
- `main` = `59b891e` ("ledger L097: ... +10 pp SIGN-beats-FLOAT headline ... unstandardized float").
- `findings/top10-comparison-2026-09-15` = `e672192` ("final(twelve-byte-pilot): complete state, verdict STOP, five retractions preserved").
- `merge-base main findings/...` = `5ec3db6` (ledger L095). `merge-base --is-ancestor main findings/...` = NOT-ANCESTOR.
- `branch --contains 59b891e` = `main`, `origin/main` only → main head is NOT in the findings branch history (diverged after L095; main has L096/L097 the branch lacks).
- `branch --contains e672192` = `findings/top10-comparison-2026-09-15`, `origin/findings/...` only.
- Named commits all resolve (`cat-file -t` = commit): `c31719b`, `a68fcdc`, `8bcdef5`, and all are ancestors of `e672192` (`log --oneline findings/...` lists them in order c31719b → a68fcdc → 74e21e1 → 8bcdef5 → e672192).
- Commit dates (author=Committer=Claude, +03:00): c31719b 16:49:31, a68fcdc 20:59:11, 8bcdef5 21:34:17, e672192 21:37:27, all 2026-09-16.

## 3. Publication integrity — manifest spot check WITHOUT clone (evidence)
Per expanded responsibility, no `git clone` was made (it would duplicate ~GBs and is
unnecessary: the worktree is read directly and blobs are read via `git show`). Two own-code
scripts in this directory (`verify_manifest.py`, `verify_blobs.py`, seed-fixed, read-only):
- Manifest: `FILE_MANIFEST.json`, 756 entries `{path, bytes, sha256, stored}`; sha256 is of
  the ORIGINAL uncompressed bytes (entries with `stored=*.gz` gunzipped before hashing).
  Random sample of 30 (seed 20260917): **30/30 sha256 match, 0 mismatch, 0 missing**.
- Worktree-vs-git: 10 random manifest entries + REPORT.md, FINAL_STATE.md,
  coordinator/decision_tests.py, decision_r1/cost/REFEREE.md — worktree bytes vs
  `git show findings/top10-comparison-2026-09-15:<path>` blobs: **14/14 identical**.
- Coverage gap (manifest ≠ publication): manifest mtime 16:36:35 predates the decision
  round; **0 of 756 entries cover `decision_r1/`, `DECISION_TESTS*`, `T3_*`, or
  `FINAL_STATE.md`**. So the manifest authenticates the pre-decision package but NOT the
  five gate/retraction files this audit cares about most — those are authenticated only by
  git blobs (checked above, 4/4 match) and commit messages. The task's "ZIP vs worktree"
  comparison is NOT RUN as literally specified (no ZIP artifact and no clone per override);
  the blob-identity check above is the read-only substitute.
- `model/` (2.4 GB) and `*.npz` excluded by manifest design (weights via MODEL_DOWNLOAD.json
  sha256+revision — NOT verified here, see §7).

## 4. Five retractions: FINAL_STATE.md + REPORT.md + git (evidence)
FINAL_STATE.md §"Retractions (five...)" (lines 60–75) lists: (R1) "no better 96 directions"
impossibility; (R2) "12 bytes isn't enough, 48 is"; (R3) "SVD discards rare terms";
(R4) "CODE wins the common band"; (R5) "PerLTQA decline is rank overflow" — "Four were
caught by external review; the fifth by my own test. All are recorded rather than edited away."
Cross-check per retraction (worktree reads + `git show <commit>:<path>`, observed 2026-09-17):
- R1 impossibility: REPORT.md lines 65–76 labeled "SECOND CORRECTION, same day — the
  impossibility claim is RETRACTED", with the rho=1.0000/0.0000 counterexample and
  "does not follow / must not be quoted". EXTERNAL_AUDIT3_RESPONSE.md lines 183–209 same.
  Git: introduced by `a68fcdc` (message names it). Residual REPORT.md lines 84–86 ("keeping
  every unique detail at full strength is arithmetically impossible") is the narrower
  mean-claim, still arithmetically true (all-rho=1 would need sum=n>k) — examined, consistent.
- R2 dims≠bytes: EXTERNAL_AUDIT3_RESPONSE.md lines 215–222 ("Also retracted...", 384 coords =
  48 B only as sign bits; float32 = 1536 B/doc; PerLTQA row is rare-bucket only; +0.46 ns is
  failure-to-detect, not equivalence). Git: `a68fcdc`. REPORT.md carries only the weak form
  (line 292: "12 bytes, competitive retrieval ... not defensible") — the "48 is" half was
  never in REPORT.md (no match at 6800356 either), so there was nothing to correct there.
- R3 SVD-discards: REPORT.md lines 56–63 labeled CORRECTED block (0.94×/3.79× null, "framing
  was wrong"). Git: pre-`c31719b` REPORT said "they are discarded first" (line 53);
  post-`c31719b` keeps the math but prepends the labeled correction — inline, not silent.
- R4 common-band: REPORT.md lines 239–242 ("both methods fail on 93% ... not an advantage
  worth claiming"). Git: `c31719b` body names the circularity (BM25 scores zero on
  97.8–100% of that bucket by construction).
- R5 rank-overflow: DECISION_TESTS.md lines 71–91 (k_eff=min(k,n−1), constant_dims@384=0 in
  all 8 archives, decline persists −3.60/−5.17, "So the decline is NOT rank overflow ... It
  is ... dividing by σ") + lines 111–112 ("A fourth retraction ... caught by my own test").
  Git: `8bcdef5` message ("T3 RETRACTS MY OWN EXPLANATION ... Fidelity gate 0 differing of
  276,480 bits").
- GAP FOUND (stale superseded explanation, no silent edit but a missing pointer):
  `LADDER_REALTALK.md` (written by `74e21e1`, never touched afterwards) still presents rank
  overflow as the live cause — title line 3 "why PerLTQA's decline was an artifact",
  §"Why the two disagree: rank overflow, not a bit-budget limit" (line 20), "That is the
  entire pattern" (line 45), "The honest rule is k<n per archive" (line 51). Zero occurrences
  of retract/corrected/superseded/wrong (grep: only hit is the word "wrong" in "wrong
  design", line 51). It also still tabulates 384 dims as "48 bytes/doc" with no sign-bits
  caveat (lines 12–15), i.e. the R2 conflation in tabular form. A reader following the
  ladder doc alone never learns either retraction. Likewise REPORT.md §8 (line 304) still
  lists only the older retraction set ("rare-band majority, truncation as sole cause, our
  axes are a feature") — stale, since REPORT.md was last touched by `a68fcdc`, before T3.
  The retractions ARE preserved (FINAL_STATE + DECISION_TESTS + commit messages), so this
  is not a silent correction — it is an un-annotated superseded document. Severity: moderate,
  recorded in §7.

## 1. Timestamps / pre-commit chronology (evidence; mtimes are NOT proof of pre-registration)
Worktree file mtimes (`ls --time-style=full-iso`, +0300, 2026-09-16):
- `decision_r1/cost/REFEREE.md` 21:26:23; `coordinator/decision_tests.py` 21:30:32;
  `coordinator/DECISION_TESTS.json` + `decision_tests.log` 21:31:00/21:31:00;
  `coordinator/t3_perltqa_kltn.py` 21:31:23; `coordinator/T3_PERLTQA_KLTN.json` 21:33:14.
- `REPORT.md` 20:58:38 (≈ a68fcdc 20:59:11 — committed seconds after write).
- `FINAL_STATE.md` 21:37:19 (≈ e672192 21:37:27).
- `FILE_MANIFEST.json` 16:36:35 — predates the whole decision round.
Git history (path-scoped `git log --oneline findings/... -- <path>`, observed):
- `decision_r1/cost/REFEREE.md`: exactly ONE commit, `8bcdef5`.
- `coordinator/decision_tests.py`: exactly ONE commit, `8bcdef5` (same commit).
- `REPORT.md`: three commits on the branch — `6800356`, `c31719b`, `a68fcdc`; NOT touched by `8bcdef5`/`e672192`.
Chronology reading: REFEREE.md mtime (21:26) < decision_tests.py mtime (21:30) < test output JSONs (21:31–21:33) < commit 8bcdef5 (21:34:17). So on disk the referee text predates the test script by ~4 min and both predate their joint commit. BUT both files entered git in the SAME commit, so git cannot separate "gates fixed first" from "written together then committed together". Per mandatory corrections, mtimes alone do not establish pre-registration. Gate-vs-result separation must come from DECISION_TESTS.md/log content (gate definitions vs run output), examined in §4/§6 — provisional status FAIL-open: chronology claim NOT PROVEN by timestamps alone.

## 2. Git history: three named commits + REPORT.md handling (evidence)
- `c31719b` audit(twelve-byte-pilot): external audit 3 corrects mechanism (dimension budget, not discard). Files: `EXTERNAL_AUDIT3_RESPONSE.md` (new, +178) + `REPORT.md` (+15/−2). REPORT.md edited in the SAME commit as the correction — inline-correction style, not silent (commit message names the correction).
- `a68fcdc` retract(twelve-byte-pilot): impossibility claim wrong (mean vs individual rho + 4 companion retractions). Files: `EXTERNAL_AUDIT3_RESPONSE.md` (437 lines changed) + `REPORT.md` (27 lines changed). Message explicitly lists what is retracted.
- `8bcdef5` decision(twelve-byte-pilot): three prespecified gates fail, STOP verdict, T3 self-retraction (rank overflow NOT the cause). Files (10, +1874, all NEW): DECISION_TESTS.md, ablation_r2/perltqa/t3_ladder.py, coordinator/{DECISION_TESTS.json, T3_PERLTQA_KLTN.json, decision_tests.log, decision_tests.py, t3_perltqa_kltn.py}, decision_r1/{cost/REFEREE.md, keep/CASE_FOR.md, kill/CASE_AGAINST.md}. No REPORT.md edit here — decision recorded in new files.
- `e672192` final: adds FINAL_STATE.md (+142) + 19 agent prompt/log files. No REPORT.md edit.
- REPORT.md edit pattern: every REPORT.md change on this branch rides in a commit whose message names the correction/retraction (6800356, c31719b, a68fcdc). No silent REPORT.md-only commit found on the branch path history. Full `git log -p` word-diff of REPORT.md across these commits is still to be spot-checked (§4) for softening language.

## 1. (pending)
## 2. (pending)
## 3. (pending)
## 4. (pending)
## 5. (pending)
## 6. (pending)
## 5. Whole-project governance (evidence; see PROJECT_COVERAGE.csv)
- Ref universe: 173 total refs (`branch -a` count). Local research lines classified in
  PROJECT_COVERAGE.csv: v52-task4f1 era (Aug 31–Sep 3), v52-static v10 era (Sep 13),
  representation-geometry/campaign (Sep 13), dense-mrl-parity (Sep 14, `36c7bf0`, current
  main-repo checkout), f1-execution (Sep 14), governance/rank-cert repairs (Sep 14),
  hr consolidation + standardized-float correction (Sep 14–16), twelve-byte prereg +
  budget-decision + pilot (Sep 10–16), audit4-postcheck (Sep 17, live, NOT REVIEWED).
  ~130 remote-tracking refs NOT REVIEWED (no fetch; counted only).
- Main ledger state: `main@59b891e` = L097, an INTERPRETATION correction (frozen
  +10.037943 pp stands; reference was uncentered float; standardized float reverses it on
  all four families). L097 body explicitly documents the L096 gap (carried by unmerged
  `hr/consolidation` @`907750f`) and cites the hr correction branch by commit+hash
  "following the L-094 pattern" — the gap is declared, not hidden.
- Unmerged findings: pilot branch, hr/float-correction, hr/consolidation-L096,
  governance-repair (PREPARED NOT ACCEPTED) are all UNMERGED into main (ancestor checks).
  No evidence of silent merging: main duplicates hr content via cited ledger entries.
- STOP scope: the pilot STOP (`8bcdef5`/`e672192`, "STOP the retrieval-optimization
  programme") has NO receipt in main history (`log main --grep=pilot` shows nothing past
  L-083-era items; merge-base L095 confirms divergence). It is a coordinator verdict on an
  unmerged exploratory branch whose every doc carries [NOT PREREGISTERED][NOT FOR CITATION].
  In-repo misrepresentation: NOT FOUND. Downstream citation risk remains (labels only
  mitigate); FINAL_STATE's reopen-condition (§"One thing that would reopen this") correctly
  scopes the STOP to "comparisons against BM25 with text available".
- Pending obligations (from FINAL_STATE + ledger): LME channel ablation was 322/470 at
  publication ("already paid for; finish and freeze"); LoCoMo gold contradictory
  (n=1531 vs 1535); hr consolidation (L096) unmerged. Frozen vs exploratory: v52 task
  packages are frozen/ledger-sealed lines; the pilot, prereg drafts, and agent branches are
  exploratory (labels agree).

## 6. Explicit-challenge items (mandatory; evidence-grounded)
1. **sym vs sigma.** CHALLENGE SUSTAINED in part. T3 code (`t3_perltqa_kltn.py` lines 64–68):
   `sym = QB @ B.T` (no division), `qscale = (QC/sigma) @ B.T` with sigma floored at 1e-12,
   `asym = QC @ B.T`. sign() is invariant to positive scaling, so the "dividing by tiny
   sigma" story fits qscale exactly but NOT sym — yet DECISION_TESTS.md line 168 groups sym
   as "standardized" and the decline narrative covers sym (−5.17) jointly. sym's fall needs
   a different micro-story (binarized-query noise dims), which the docs never give. The T3
   *data* (decline persists at constant_dims=0; asym rises) stand; the attached *causal
   gloss* is imprecise for sym. Severity: low-moderate (does not change any gate outcome).
2. **Rank-overflow causal explanation.** REPLACED, correctly, by the authors themselves (R5).
   The replacement (tiny-sigma division) is a single-experiment association (8 archives,
   2,217 queries, one k_eff rule), not an independently randomized cause — plausible
   mechanism, n=1 design. The honest part is that S3 "did not fire" and the verdict followed
   the prespecified rule anyway.
3. **Rerank removes first-stage importance.** Data: 164,256 paired rows, 0.58 pp post-rerank
   spread over 11.58 pp pre-rerank, 4/10–6/10 inversions. Scope respected in-doc: LoCoMo
   pass flagged "disputed gold"; claim is about pipelines WITH a text reranker (which needs
   the text — the storage premise it erases). No overclaim found beyond the noted gold dispute.
4. **BM25 needs raw text.** Accounting verified as methodology (varint 670,511 B vs pickle
   1,450,229 B artifact disclaimed; index+text 1,669,165 B). "Needs" is deployment-relative
   and FINAL_STATE concedes the reopen condition (bits-only, no-reranker deployment). OK.
5. **RealTalk-only delta applied to all datasets.** NOT DONE — T1 gate C1 required BOTH
   benchmarks and FAILED; T2 reported per-dataset (2 ns + 1 disputed pass). No
   generalization claimed. OK.
6. **Best-of-4 BM25 on seen gold.** CONFIRMED as selection (DECISION_TESTS.md lines 17–24:
   four variants, max 65.67 chosen, no held-out split stated). Bias direction is
   conservative here (strongest opponent makes C1 harder; C1 still failed by 7.80 pp), so no
   outcome flips — but any future reuse of 65.67 as "the" BM25 number inherits seen-gold
   optimism. Recorded as caveat, severity low.
7. **STOP misrepresented as closure.** See §5: not found in-repo (scoped wording + labels +
   no main receipt). Residual risk is external citation; mitigation present (labels,
   reopen-condition, L097's "local exploratory pilot, not a re-measurement of any frozen
   estimand").
- Literature absence ≠ novelty: FINAL_STATE line 111–113 ("appears unstudied — our results
  cannot be checked against anyone else's") correctly frames absence as uncheckability,
  not as novelty proof. OK.
- Paired multi-seed note: T2 used archive-clustered bootstrap (20,000 reps, seed 20260916)
  with CIs — adequate uncertainty for the ns claims; single-seed spot values elsewhere
  (e.g. 0.1934 vs 0.1920 leverage check) are presented as identities/diagnostics, and the
  L-033-era seed-defect history (`BOTTLENECK.json` INVALID_SEED_DEFECT, seeds pinned
  LSA32=5101/SVD96=5204) shows the failure mode was met before. No fresh multi-seed rerun
  was performed here (180 s rule + read-only scope) — flagged, does not block integrity
  verdicts which concern preservation, not re-estimation.

## 7. VERDICTS + coverage ledger
| # | Check | Verdict | Key evidence |
|---|---|---|---|
| 1 | Gates fixed before tests (chronology) | NOT PROVEN (timestamps only) | REFEREE.md mtime 21:26 < decision_tests.py 21:30 < joint commit 8bcdef5 21:34:17; same-commit entry means git cannot separate joint authorship from pre-fixation. Content separation (gates in REFEREE/DECISION_TESTS.md lines 5–8 vs run logs) is consistent with the claim but is self-attestation. A hash snapshot detects change; it does not prevent writes. |
| 2a | main=59b891e; branch HEAD=e672192 | PASS | `rev-parse` both exact; `branch --contains` disjoint as expected (main head only in main/origin/main; e672192 only in findings/origin-findings). |
| 2b | main absent from branch history | PASS (diverged, declared) | merge-base=5ec3db6 (L095); NOT-ANCESTOR both directions past L095; L097 body declares the L096 gap + cites hr branch by hash. |
| 2c | c31719b / a68fcdc / 8bcdef5 traced; corrections in-report | PASS | All three resolve, all ancestors of e672192, subjects name the correction; REPORT.md diffs show labeled inline correction blocks (R3 pre/post "discarded first" → CORRECTED block; R1 RETRACTED block), never silent-only edits. |
| 3 | Manifest 30-file sha256; worktree==published | PASS with noted scope | Own code: 30/30 manifest match; 14/14 worktree-vs-blob identity. No clone per override (substitute documented). Manifest covers 0/756 decision-round files (predates them) — gate files authenticated via git blobs only. weights (`model/`) NOT RUN. |
| 4 | Five retractions preserved with evidence | PASS with one GAP | R1–R5 each in FINAL_STATE + ≥1 doc + commit message (§4). GAP (moderate): LADDER_REALTALK.md still asserts rank overflow with zero retraction pointers; REPORT.md §8 list stale (pre-T3). Not silent editing — un-annotated superseded docs. Recommend a one-line header pointer (cannot apply: read-only rule). |
| 5 | Whole-project governance | SAMPLED (see CSV) | 173 refs classified; main ledger L095→L097 + declared L096 carry; STOP unmerged+unreceipted; pending items listed. ~130 remote refs + v52-era bulk NOT REVIEWED — no exhaustive certification claimed. |
| 6 | Explicit challenges (7 + novelty + seeds) | 2 caveats stand | sym/sigma gloss imprecise (low-moderate); best-of-4 BM25 seen-gold selection (low, conservative direction). Others OK/scoped. |

Severity-ranked findings:
1. (Moderate) Superseded LADDER_REALTALK.md has no pointer to its own T3 retraction; still
   tabulates dims-as-bytes without the sign-bits caveat. Reader-trap, not data corruption.
2. (Moderate) Manifest authenticates everything except the decision round it is cited to
   protect (0/756 decision files). Git blobs fill the gap here (14/14), but any consumer
   trusting FILE_MANIFEST.json alone gets pre-decision coverage only.
3. (Low-moderate) sym grouped under the sigma-division causal story it cannot mechanically
   share (sign scale-invariance; `sym = QB@B.T` has no division).
4. (Low) REPORT.md §8 retraction list stale (pre-T3); best-of-4 BM25 number reusable without
   its seen-gold caveat; L096/L-merge hygiene pending (declared); weights unverified (NOT RUN).
NOT RUN ledger (no fabrication): clean-clone readback as literally specified (substituted
with blob-identity); ZIP-vs-worktree (no ZIP artifact found; substituted); MODEL_DOWNLOAD
weights hash; multi-seed reruns; remote-ref reconciliation; v52-era bulk review.
Scope: EXAMINED = pilot branch + main ledger tip + hr correction lines; SAMPLED = f1-execution
head, governance-repair subject; NOT REVIEWED = everything else in PROJECT_COVERAGE.csv.
Addendum (post-close, 2026-09-17): `git status --porcelain` in the main checkout shows one
untracked `research_top10_comparison_2026_09_16/AUDIT4_POST...` artifact — consistent with
the live `findings/audit4-postcheck-2026-09-17` branch writing into that checkout during
this audit. Not authored by this audit; no verdict above changes.
[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
