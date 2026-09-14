#!/usr/bin/env python3
import json
spot=json.load(open("/tmp/racev/rv_sign_spot.json"))
anchor=json.load(open("/tmp/racev/rv_sign_anchor.json"))
dispo=json.load(open("/tmp/racev/rv_dispo.json"))
d2=json.load(open("/tmp/racev/rv_diff_RB2.json"))
d3=json.load(open("/tmp/racev/rv_diff_RB3.json"))
details={
 "check1_seal":{"race_sign.py":"6dbb6240453409177470b4bfad38f1a55ba3ed7f03f689e983c5b09ae864b74a",
   "race_faiss.py":"67a4b5e47cfd3dc6b3f24f3423e18f64a6dfcb5e585c733a70435f81cda8aec3",
   "verdict":"EXACT both match PRE_RUN_SEAL_local.json"},
 "check2_sign":{"anchors":anchor["anchors"],"spot_12FR":spot,
   "aggregates_6":"all diff 0.0 (NATIVE96/TOP48/SPREAD80 LME; NATIVE96/BOT80/RAND80_s2 LoCoMo)",
   "math1_5":"all diff 0.0",
   "validity":{"TOP48_LME":0.34949468085106383,"SPREAD80_LME":0.525258865248227,"BOT80_LoCoMo":0.23546142203796927}},
 "check3_faiss":{"byte_replay":{"RQ96":20,"RQ32":12,"PQ":12,"EXT2":44,"verdict":"EXACT"},
   "retrain_PQ":"bit-identical codes on LME 001be529 (N=514) + locomo_1 (N=369); per-archive codes not persisted -> runner code-hash comparison NOT CHECKABLE; 5/5 A6 FRs diff 0.0",
   "self_consistency":"8 arms x 2 benches: summary-vs-perq means diff 0.0; W/T/L counts exact; mean_gap_pp exact (<=1.8e-15); masks all []",
   "rabitq_spot":"A4_spread_rot94101 3/3 FRs diff 0.0"},
 "check4_diff":{"RB2_n_diffs":len(d2),"RB2":d2,"RB3_n_diffs":len(d3),"RB3":d3,
   "byte_worksheet_grep_in_runner":0},
 "check5_disposition":dispo,
 "not_checkable":["per-archive PQ/RaBitQ codes vs runner (only aggregate codes_sha256 persisted)",
   "official manifests reference runner .py files not shipped in official_run/ dirs (verified instead via rb2/rb3 copies + seal)",
   "bootstrap/CI analysis (not in official run scope; deferred to analysis phase)"],
 "manifests":{"sign_details_OK":True,"sign_smoke_OK":True,"faiss_env_OK":True,"faiss_details_OK":True,"faiss_smoke_OK":True}
}
json.dump(details,open("/tmp/racev/racev_details.json","w"),indent=1)
print("details written", len(json.dumps(details)), "bytes")
