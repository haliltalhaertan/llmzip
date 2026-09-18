"""Own audit: Claim 4 — sigma-division collapses at high k.

Scorer contracts (read from t3_perltqa_kltn.py, re-implemented NOTHING here,
pure-JSON arithmetic with own code):
  qscale = (QC/sigma) @ B.T   (standardized, query-side sigma division)
  asym   = QC @ B.T           (unstandardized)
  sym    = Hamming(sign(QC),sign(C))  (no sigma anywhere)
Attack: "asym is ALWAYS better, sigma not special" — check per-k gaps AND
within-arm 192->384 deltas on T3 (PerLTQA 8 arch, k<n enforced) + RealTalk LADDER.
"""
import json

PUB = "/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16"
T3 = json.load(open(f"{PUB}/coordinator/T3_PERLTQA_KLTN.json"))["arms"]
LAD = json.load(open(f"{PUB}/coordinator/LADDER.json"))["arms"]
DT = json.load(open(f"{PUB}/coordinator/DECISION_TESTS.json"))

print("== T3 PerLTQA-8 (k<n enforced), FR@3 ==")
for k in (96, 192, 384):
    q = T3[f"k{k}/qscale"]["fr3"]; s = T3[f"k{k}/sym"]["fr3"]; a = T3[f"k{k}/asym"]["fr3"]
    print(f"  k={k}: qscale={q:6.2f} sym={s:6.2f} asym={a:6.2f} | asym-qscale={a-q:+6.2f}")
for sc in ("qscale", "sym", "asym"):
    d1 = T3["k192/"+sc]["fr3"] - T3["k96/"+sc]["fr3"]
    d2 = T3["k384/"+sc]["fr3"] - T3["k192/"+sc]["fr3"]
    print(f"  {sc:6s}: 96->192 {d1:+6.2f} | 192->384 {d2:+6.2f} (Hit@10 192->384 "
          f"{T3['k384/'+sc]['hit10']-T3['k192/'+sc]['hit10']:+6.2f})")

print("== RealTalk LADDER (all archives n>384, i.e. k<n comfortably), Hit@10 ==")
for k in (96, 192, 384):
    q = LAD[f"k{k}/qscale"]["hit10"]; s = LAD[f"k{k}/sym"]["hit10"]; f = LAD[f"k{k}/float"]["hit10"]
    print(f"  k={k}: qscale={q:6.2f} sym={s:6.2f} float={f:6.2f} | qscale-sym={q-s:+6.2f}")
for sc in ("qscale", "sym", "float"):
    d1 = LAD[f"k192/{sc}"]["hit10"] - LAD[f"k96/{sc}"]["hit10"]
    d2 = LAD[f"k384/{sc}"]["hit10"] - LAD[f"k192/{sc}"]["hit10"]
    print(f"  {sc:6s}: 96->192 {d1:+6.2f} | 192->384 {d2:+6.2f}")

print("== full-PerLTQA k=96 cross-check (DECISION_TESTS T2 levels, FR@3) ==")
for ds in ("PerLTQA", "LME", "LoCoMo"):
    lv = DT["T2_rerank"][ds]["levels_fr3"]
    print(f"  {ds:8s}: asym96={lv['asym96']:6.2f} qscale96={lv['qscale96']:6.2f} "
          f"diff={lv['asym96']-lv['qscale96']:+6.2f}")
print("\nAttack test: is asym better at EVERY k (sigma never special)?")
print("Mechanism test: does sym (NO sigma division) also fall at 384?")
