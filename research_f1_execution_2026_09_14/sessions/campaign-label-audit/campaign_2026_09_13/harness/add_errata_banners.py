#!/usr/bin/env python3
"""Insert orchestrator-errata banners at the top of the five round-3 session reports."""
from pathlib import Path

BASE = Path('C:/Users/MDP/dev/llmzip-work/pilots/axis_attack_2026-09-12/round3/muse_sessions')
BANNERS = {
    'd2': "> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F1/C8: the T/M model "
          "features (all except `margin`, `top20_entropy`) REQUIRE GOLD QRELS at inference — this is a "
          "MECHANISM result, not a deployable-predictor claim; the §4 verdict is downgraded to "
          "\"cleared the roadmap kill-bar; the tie story graduates to c2 exploration\". "
          "See ERRATA_ROUND3_D5.md §F1.",
    'c2': "> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F2: the LoCoMo leg is "
          "VACUOUS vs random-abstention (random routing alone passes the +0.5pp leg; COMBO AUC 0.558). "
          "\"PROMOTE\" is CONDITIONAL on a future preregistration carrying a BINDING vs-random "
          "superiority gate (model gain > random-range max at alpha=0.20); LoCoMo must NOT be called a "
          "replication. See ERRATA_ROUND3_D5.md §F2.",
    'd1v': "> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** F3: cannot-check items "
           "1–2 were oversights, not limits. RE-CHECKED (f3_rechecks.txt): LoCoMo split counts/balance "
           "verified for all 10 splits; 5 nonzero-FR test qids recomputed EXACT (membership aligned); "
           "r2c_replicate.py located at round2/session_scripts/. HASHES_ROUND3.txt: 6/6 OK; delta64 "
           "cols EXACT. See ERRATA_ROUND3_D5.md §F3.",
    'd3': "> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** C5: the licensed "
          "conclusion is \"utilities are benchmark-local; transfer ~ chance\"; var-row FAV is "
          "TAUTOLOGICAL (src==own by construction). See ERRATA_ROUND3_D5.md §C5.",
    'd4': "> **ORCHESTRATOR ERRATA (2026-09-13, after D5 adversarial review).** C6: language is "
          "CONFIRMATORY-ONLY (n=2 fresh draws); seed-numeral collision flagged (43004/05 are "
          "LoCoMo-fresh but LME gate-seed numerals; LME fresh set is 44001/44002); full-5-seed LME "
          "contrast noted (strict separation fails on all five, robust on fresh 44001/02 draws). "
          "See ERRATA_ROUND3_D5.md §C6.",
}
for key, banner in BANNERS.items():
    # find the report file
    cands = sorted((BASE/key).glob('*.md'))
    assert len(cands) == 1, (key, cands)
    fp = cands[0]
    t = fp.read_text(encoding='utf-8')
    assert 'ORCHESTRATOR ERRATA' not in t, fp
    out = banner + '\n\n' + t
    fp.write_text(out, encoding='utf-8', newline='\n')
    print('banner ->', fp.name)
print('BANNERS_DONE')
