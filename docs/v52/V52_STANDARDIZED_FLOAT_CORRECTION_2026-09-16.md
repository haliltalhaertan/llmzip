# V52 — the "+10 pp SIGN beats FLOAT" headline is measured against an unstandardized float

Authored body for the continuity ledger. Binding when committed on an `hr/`
branch and attached under the next free ledger number at landing — this body
reserves no number, following the L-095 precedent, because `L-096` is already
carried by the unmerged `hr/consolidation-l096-2026-09-14`.

```text
actor_role: Continuity Lead, preparing; Head Researcher approved the recording of this correction on 2026-09-16
scope: A correction of INTERPRETATION only. No frozen number is disputed, no sealed byte is touched, no Task 4F1 / BEAM surface is run or read. The frozen G = +10.037943 pp is arithmetically correct and stands.
finding: The programme headline "SIGN96 beats FLOAT by about +10 pp" is measured against FLOAT96_UNCENTERED, an unstandardized reference. Standardizing the same float reverses the sign of the comparison. On hit@10, a metric added in the 2026-09-15 pilot and not the frozen task's own FR@3, SIGN96 is BEHIND standardized float on every benchmark measured.
numbers_hit10_pct: LongMemEval sym 86.08 / float 82.55 / float_std 88.30. PerLTQA en_v2 sym 75.76 / float 80.81 / float_std 83.96. RealTalk sym 46.68 / float 36.60 / float_std 48.51. LoCoMo sym 43.84 / float 34.66 / float_std 50.03. sym minus float_std: -2.22, -8.20, -1.83, -6.19 pp.
narrowing: float_std is NOT universally the strongest reference. On two further PerLTQA releases raw float wins: en_v1 float 91.16 vs float_std 89.48, and zh float 82.22 vs float_std 77.90. The correct statement is that the comparison depends on the reference chosen, not that standardized float is best everywhere.
cost_caveat: float_std costs 768 B/doc against 12 B for SIGN96, i.e. 64x. It is a CEILING, not a competitor at the byte budget. Nothing here says the 12-byte code should be replaced. What it says is that "sign quantization beats float" holds only against a weak reference, and that every round built on the old headline inherits the error.
metric_caveat: These are hit@k numbers from a local exploratory pilot. The frozen tasks measure expected fractional R@3. This correction is about how the comparison is FRAMED; it is not a re-measurement of any frozen estimand and does not license reading any frozen outcome.
evidence: findings/top10-comparison-2026-09-15, directory research_twelve_byte_pilot_2026_09_15/. See HANDOFF_2026-09-15.md section 6a and section 12a, results/HIT10.json, results/LOCOMO.json, results/PERLTQA_en_v1.json, results/PERLTQA_zh.json. Every script self-checks frac@3 against lib_b8.exact_frac on every arm and every query before reporting.
labels: The evidence branch carries [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE] throughout, and those labels travel with these numbers.
disposition: RECORDED AS A FRAMING CORRECTION. No arm winner is declared, no representation change is authorized, no benchmark is pooled.
next: Before any future round quotes the +10 pp gap, it must state which float reference it is measured against. The open question the pilot sharpened is separate and unresolved: binarising the QUERY costs 4.43 pp on PerLTQA and is beneficial on RealTalk, and nobody knows why.
outcome_boundary: Task 4F1 SEALED / RUN BLOCKED / NO AUTHORIZATION / OUTCOME ACCESS FORBIDDEN. Unchanged by this entry.
status: FRAMING CORRECTION RECORDED; NO FROZEN NUMBER CHANGED
```
