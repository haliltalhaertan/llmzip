EXTERNAL LLM TRANSFERS — llmzip local session work (2026-09-12/13)
=================================================================

FOUR self-contained, independently-reviewable bundles (the axis-pilot line supersedes
earlier editions; Task1 bundle unchanged). All were fresh-extraction verified
(unzip to a clean dir -> all checks pass).

------------------------------------------------------------------------------
1) TASK1 COMPLETION REVIEW (certified regeneration of the frozen representations)
   FULL  EXTERNAL_LLM_REVIEW_TASK1_2026-09-12.zip      (20.6 MB, 93 entries)
     sha256 83a68fbb16df44718c420caafbba55871b7d8bccfcf14fd6572ed996ec9339a1
   LITE  EXTERNAL_LLM_REVIEW_TASK1_LITE.zip           (0.5 MB, 64 entries)
     sha256 ac8f28f864fbd0a890884eecbbb1c62c006ccec506a11e7b8368e51c094b52cf
   Checks: sha256sum -c HASHES_TASK1.txt (60/60) + SUPPLEMENTARY_HASHES.txt (31/31)
           + python3 verify_consistency.py -> ALL CHECKS PASS

2) AXIS-ATTACK PILOT — ROUND 1 (superseded by #4, kept for provenance)
   EXTERNAL_LLM_REVIEW_AXIS_PILOT_2026-09-12.zip      (12.3 MB, 66 entries)
     sha256 ec3c707b90cb563966b3c3d6f81b98cc8f3a5ac8db22d08a1c2c07b3f3043df0
   EXTERNAL_LLM_REVIEW_AXIS_PILOT_LITE.zip            (0.3 MB, 33 entries)
     sha256 a884c29e284fd77c4ae4a85108597ce0bac980812992c44df48e62616d58b147

3) AXIS-ATTACK PILOT — EDITION 2 (superseded by #4, kept for provenance)
   FULL  EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED2_2026-09-13.zip (15.3 MB, 91 entries)
     sha256 b340df7ca11b3aeb5bf1e34bd659dd93d9e8c06d0619d4340b67953821bef6f2
   LITE  EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED2_LITE.zip       (1.9 MB, 53 entries)
     sha256 9b3842ffe6c36a96123cd8b521bc9ea4eef55d9f413965e94e7cb2837716ec17

4) AXIS-ATTACK PILOT — EDITION 3  ***latest: rounds 1+2+3 + missing analyses (v1.1) — recommended***
   FULL  EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_2026-09-13.zip (16.1 MB)
     sha256 1e6d0264633fa19006a2f667abec5ade30eeb6db5d9daf6c9de2649f95876d5e
   LITE  EXTERNAL_LLM_REVIEW_AXIS_PILOT_ED3_LITE.zip       (2.2 MB)
     sha256 6c8285c05fb801cf75ca0c364b0289b9a0f6920079c8e4119c2c4772d7300e89
   Round 3 added: the roadmap Design-1 robustness experiment (learned-selection premium
   KILLED — 3/3 pre-declared triggers); tie-mass mechanism decomposition (D2); cross-benchmark
   utility transfer (D3); fresh-Q mixing confirmation (D4); gold-free adaptive-routing probe
   (c2, closed); independent recomputation (D1V: 24/25 EXACT) and adversarial design review
   (D5: F1-F3 + C1-C9, all dispositioned). v1.1 adds the three D5 follow-up missing analyses
   (m1 kill-null; m2 D2 multi-split + gold-free; m3 c2 ablation — c2 NOT prereg-ready) under
   round3/missing_analyses/. See 01c_ROUND3_ADDENDUM.md + pilots/.../round3/.
   Checks inside (fresh-extraction verified, all exit 0):
           sha256sum -c  (supplementary 54/54, pilots r1 18/18, r2 18/18, r3 49/49)
           python3 verify_round3.py             -> ROUND-3 ALL CHECKS PASS
           python3 verify_pilot.py              -> ALL CHECKS PASS
           python3 pilots/.../round2/verify_round2.py -> ALL ROUND-2 CHECKS PASS
           python3 verify_sample_numpy.py       -> 32/32 exact (FULL only; needs numpy)

HOW TO USE WITH ANOTHER LLM
  Hand it one zip; inside, read 00_READ_ME_FIRST.md -> skim the addenda/reports ->
  run the checks in 03_VERIFY_COMMANDS.md -> answer the assignment in
  02_INDEPENDENT_REVIEW_PROMPT.md (structured findings table + verdict, TR or EN).
  Bundles are companions: the pilot line runs on the Task1 certified regeneration.

NOTE: read-only review; nothing instructs any write or push. Labels
([LOCAL SESSION - NOT PUSHED] / [LOCAL EXPLORATORY PILOT] [DISCLOSE-BEFORE-USE])
must travel with any citation.
