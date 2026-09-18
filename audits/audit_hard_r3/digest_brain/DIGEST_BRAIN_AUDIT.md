[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# DIGEST-BRAIN AUDIT (round 3, dark-corner role)

Read-only audit. Nothing outside this directory was written. All probes used
`python3` + numpy only, each bounded to minutes. Sampled or partial checks are
labelled as such; everything else is a full re-derivation.

## 1. VERDICT

No published number or conclusion is wrong: every brain claim I re-ran
reproduces exactly, every incoming_20260916b number that entered the decision
brief re-aggregates exactly from raw shards, and the STOP verdict survives
(the fair-BM25 correction only strengthens it). Two MED qualifications
(stale coarse baseline in CRITIQUE sec 1a; overstated RT04 "falsification",
z=1.30 ns) and three LOW label/cohort hazards follow. The brief's premise
that NEW_VS_KNOWN.md is missing is false: the file exists and was read.

## 2. FINDINGS

| ID | Sev | Check | Result |
|----|-----|-------|--------|
| F1 | LOW | PerLTQA 30 vs 31 arch caches | Both scripts faithful, 0.3% diff, no number wrong |
| F2 | LOW | Banding 341 vs 412 rare | Disclosed both rules, join hazard only |
| F3 | MED | Brain uses coarse BM25 54.18 | Stale, verdict survives stronger |
| F4 | LOW | Tie convention 46.68 vs 46.52 | Internally consistent |
| F5 | MED | RT04 +7.04 "falsifies" | z=1.30 ns, rhetoric overstates |
| F6 | LOW | NEW_VS_KNOWN.md missing? | Exists, recheck still true |
| F7 | OK | incoming_20260916b verified? | Yes, re-aggregated exact |
| F8 | OK | Contradictions with STOP? | None found |

## 3. PER-FINDING DETAIL

### A. Brain scripts — all numeric claims reproduce exactly

Sources (read-only):
`top10_comparison_r1/digest_r1/brain/check_pools.py`,
`check_bothmiss.py`, `check_decisive.py`, `check_corpora.py` and their
`.json` outputs; inputs `math_r1/{repr,quant}/per_query.jsonl`,
`ideas_r1/firststage/per_query.jsonl`, `coordinator/cost_audit.json`,
`top10_comparison_r1/data/RT*.json`, `bench3/runs/b3a_realtalk/rt_repr/RT*.pkl`,
`bench3/runs/b3b_perltqa/cache_{arch_eval,q_eval,items.json}`.
My probes live in `/tmp/probe_{pools,decisive,corpora,recheck,ladder,final}.py`
(scratch, not deliverables); I never executed the brain scripts in place
because they write their `.json` next to themselves in a read-only tree.

- Rotation per archive (qscale FULL vs RAND_20260916): all 10 rows reproduce
  to 2 decimals incl. RT04 +7.04 (n=71), small-arch mean -6.56,
  large-arch mean -23.13. Command: `python3 /tmp/probe_pools.py`.
- Oracle sym|qscale RealTalk FULL: n=705, sym 46.52, qscale 49.65, oracle
  53.48, both-miss 328. check_bothmiss.json (705/328/46.52, bands
  133/153/412/7, reachability in-100 158 / outside 170 / 0.518) is
  cross-consistent with the oracle count. No mismatch.
- CODE pool decomposition: n=705, hit10 350, in-top100 183, outside 172,
  pool@100 75.6. Byte arithmetic: 8944 docs, code 115008 B,
  compact index 670511 B, 75.0 / 186.6 B/doc, ratio 5.83. All match.
- LOO on IDF_p2 rare-band FR@3: n_rare=412, mean +4.78, all 10
  kept-diff rows reproduce (RT08 dropped-arch -8.43 confirmed).
  Banding code reproduces the coordinator recipe to the digit.
- Float-dot settler: RT01 spot re-score gives 51.76 vs stored 51.76
  (n=85). Full 705-query 42.70 accepted on method-read + this sample
  (PARTIAL check, stated).
- Corpora: RealTalk 8944 docs / 705 queries / per-archive counts exact;
  RT05 vocab 2630 / df1 1198 / median_df 2 exact.
  PerLTQA text counts: cache_items.json has 31 archives / 12323 docs,
  exactly as check_decisive §C reports.

### F1 (LOW): two PerLTQA snapshots blended in one argument

check_corpora.py reads `cache_arch_eval.pkl` (30 archives, 12288 docs,
min 293 / median 408 / max 546); check_decisive.py §C reads
`cache_items.json` (31 archives, 12323 docs). CRITIQUE sec 1b takes archive
sizes from the first and doc-length/template-redundancy stats from the
second without noting they are different cohorts (delta: 1 archive,
35 docs, 0.3%). Both scripts report their own input faithfully, and
FINDINGS_DIGEST's "30 archives / 12288 docs" matches the eval cache, so no
published number is wrong. The size-gradient mechanism is insensitive to
0.3% of docs, but the two-cache fact should be stated wherever the two
stat blocks are combined.

### F2 (LOW): two banding rules in circulation (rare 341 vs 412)

Brain banding (`[a-z0-9]+`, cutoffs 2/4) gives no_shared 7 / common 133 /
mid 153 / rare 412; FINDINGS_DIGEST's stratification table gives
24 / 224 / 116 / 341. The digest discloses this ("two tokenization rules
give 341 and 412") and the mechanism row it defends (rare n=412, +4.78) is
the brain's rule, so the defended claim is self-consistent. Residual hazard:
joining brain's both-miss-by-band table with the digest's CODE-vs-BM25
by-band table row-for-row silently mismatches bands. Label, don't merge.

### F3 (MED): CRITIQUE sec 1a grades against the coarse BM25

"Best-tested float still loses to BM25 by 5.67pp" uses frozen coarse BM25
54.18. The decision round later established fair BM25 at 61.70 (RealTalk
Hit@10, brief §C: +6.38 for the frozen tokenizer). Under the fair baseline
the float deficit roughly doubles. Direction unchanged: the verdict survives
a fortiori and supports STOP more strongly, but the "5.67pp" sentence is
stale and must not be quoted against the fair baseline.

### F4 (LOW): tie-convention variants (46.68 vs 46.52)

check_decisive's compare block quotes sign96 46.68 (expected uniform-tie
convention, same as the HATA package); coordinator frozen deterministic is
46.5248 and LADDER.json uses 46.5248. Brain is internally consistent
(oracle arithmetic closes at 46.52/49.65/53.48), and this mix class is
already listed as known. Noting for completeness so the two figures are
never differenced against each other.

### F5 (MED): RT04 +7.04 does not carry the weight CRITIQUE puts on it

"RT04 gains +7.04pp from random rotation ... falsifies any universal
axes-are-meaningful claim." Paired query-level SE on RT04 (n=71) is 5.43pp,
z=1.30, not significant. RT01 -4.71 (SE 4.07, z=-1.16) is likewise noise.
The load-bearing evidence is the group contrast, which survives proper
clustering: small-arch deltas mean -6.56 (archive-level SE ~3.8, n=5),
large-arch mean -23.13 (SE ~1.1, n=5), gap ~16.6pp. So: the size-gradient
finding stands; the single-cell "falsification" rhetoric overstates an
n=71 noise cell. The "mean hides a 34-point spread" point itself is valid
and unaffected.

### F6 (LOW): inventory premise correction + recheck still true

`inventory/incoming/NEW_VS_KNOWN.md` EXISTS (5229 bytes, read in full; §3
documents the single real contradiction, the query_sign_doc_std
definitional fork, with the do-not-merge warning). The "known to be
missing" premise is false. `recheck.py` + `recheck_results.json` exist;
my spot re-derivation from the raw CSVs matches exactly: HATA 94400 rows,
max dev 2.2e-16; HIZ 65826 rows, max dev 0.0pp; RealTalk
weighted-minus-hamming +2.9645; LoCoMo adapter 1986 -> 1531 with
exclusion reasons 446/4/5 exactly. The recheck conclusion (sec 3 table:
qscale minus old asym = LME +2.77 / PerLTQA -0.19 / RealTalk +6.10 /
LoCoMo +0.39 CI covering zero) still holds. I did not re-run recheck.py
itself (it writes into the read-only tree).

### F7 (OK): incoming_20260916b WAS verified before its numbers entered reports

Provenance: decision brief `decision_r1/keep.txt` §A quotes the ladder
(LME 52.47->61.48->61.75, PerLTQA 52.98->54.82->51.87 with 192->384
-2.95 CI [-3.87,-2.01], LoCoMo rising with gold-dispute flag) explicitly
as "independently verified by our worker ... 66 cells re-derived, worst
deviation 2.2e-14" (the a_ladder/LADDER_AUDIT.md audit; q4_result.json
shows 0 top-10 diffs / 0.0 metric diffs on 5 rescored cells).
My independent checks, read-only:

- Re-aggregated all 510 shard `quality.jsonl.gz` files: PerLTQA
  (n=8265 each) qscale FR@3 52.98/54.82/51.87, asym
  53.71/57.30/58.03, hamming 49.01/50.68/47.74 — brief §B table matches
  to the digit. Command: `python3 /tmp/probe_ladder.py`.
- Packed payloads are exactly 12/24/48 B/doc (P96/P192/P384 shapes on
  sampled shards 000/255/509). The "bytes" claim is true for document
  payload; query/scales/encoder are floats (brief §E-style caveat
  already carried by the ladder audit).
- RealTalk ladder in brief §A (49.65->55.32->57.87 / 22.41->29.75->32.79)
  is COORDINATOR-LOCAL (coordinator/ladder.py + LADDER.json, fidelity
  gate 0/858624 bits, k96 anchors exact: qscale 49.6454, sym-det
  46.5248, FR@3 22.41). It does NOT originate from the incoming package
  (which measured LME/PerLTQA/LoCoMo only, 0 RealTalk rows — correctly
  refused). Provenance clean; CASE_FOR's "recomputes exactly" deltas
  (-2.95/+0.73/+1.88) are arithmetic on verified tables.
- FIKIR1 rerank (brief §E): re-aggregated 164256-row
  `text_rerank_per_query.csv` — qscale96_bm25 and BM25_full FR@3 match
  OZET.json to ~2e-16 on all three benchmarks; net code contribution
  -0.33/+0.33/+1.07 and first-stage gains +3.43/+4.22/+6.97 confirmed
  to the digit.
- "8 of 30 PerLTQA archives hold <384 docs" confirmed from
  cache_arch_eval.pkl (8/30, min 293, median 408).
- UNVERIFIED (flagged, not in any report): coordinator/ladder.py's
  docstring cites "External audit 3 ... PerLTQA: -6.98 SIG at 96 ->
  +0.46 ns at 384". I could not locate this contrast in
  QUALITY_LEVELS.csv (BM25_matched FR@3 60.14 implies gaps -7.16/-8.28,
  not -6.98/+0.46) or any report (grep over keep/kill/cost texts,
  CASE files, REFEREE, FINDINGS_DIGEST: zero hits). It motivated local
  work but no published conclusion depends on it; resolve the baseline
  before quoting.

### F8 (OK): no contradiction with published conclusions

Brain's attacks point the same way as STOP (representation-or-folding
guilty, rotation/IDF/rerank lines dead or artifactual, ladder rises but
never reaches fair BM25). The one post-brain development (fair BM25
61.70/65.67) widens every deficit the brain reports. Nothing in
digest_r1/brain/ contradicts FINDINGS_DIGEST, the decision brief, or the
STOP verdict. No CRITICAL findings.

## 4. WHAT I COULD NOT CHECK AND WHY

- Full 705-query float-dot rescore (check_decisive §A overall 42.70):
  rescored RT01 only (51.76 exact) and read the method; a full rerun
  duplicates ~10 min of cache scoring for a diagnostic nobody disputes.
- Three-seed agreement for per-archive rotation ( Mani-trip: brain's
  per-archive table is one seed; the three-seed claim is STORED from the
  quant REPORT, not re-opened). Single-seed table stands as far as the
  group contrast goes (F5).
- KISITLI_CEZA / IKI_FIKIR / HATA_YERI-raw-rebuild / kernel timings /
  nDCG counter-review inside incoming_20260916b: out of role scope (only
  ladder + FIKIR1 numbers entered the brief); per b_ideas audit these
  carry their own caveats (machine-bound timings, tie conventions).
  Treated as CLAIM, not verified here.
- LoCoMo ladder column (35.11->41.21->44.15): arithmetic verified in
  QUALITY_LEVELS.csv but gold authority is disputed (1531 vs 1535, 156
  unapplied corrections) — applicability flag already carried by the
  brief; not re-adjudicated.
- The `-6.98 -> +0.46` docstring contrast (F7): baseline unidentified
  within the time box; needs the author to name the contrast.
- No web access per instructions; literature items in CRITIQUE/NEXT_5
  taken as RECALLED, not checked.
