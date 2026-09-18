import json
C={'LME':(0.14168629605302735,0.14045379360271315),
   'REALTALK':(0.09793912889111700,0.12281952421315011),
   'PERLTQA':(0.25416826537535475,0.27978783415712220)}
MINE={'LME':(0.1416251737011647,0.14069387548880735),
      'REALTALK':(0.09793425648573494,0.12307477776090332),
      'PERLTQA':(0.25413844391463014,0.27982715404990666)}
COORD={'LME':(0.1416251737011647,0.14069387548880735),
       'REALTALK':(0.09793425648573494,0.12307477776090332),
       'PERLTQA':(0.25413844391463014,0.27982715404990666)}
ROUND={'LME':(0.1417,0.1405),'REALTALK':(0.0979,0.1228),'PERLTQA':(0.2542,0.2798)}
TOL=1e-12
print(f"{'bench':9} {'arm':7} {'mine':22} {'coord':22} {'contract(1e-12)':22} {'mine-contract':14} {'mine-coord':12} pass1e-12")
rows={}
for b in ('LME','PERLTQA','REALTALK'):
    for i,arm in enumerate(('strict','tie')):
        m=MINE[b][i]; c=COORD[b][i]; t=C[b][i]
        dmc=m-t; dmco=m-c
        ok = abs(dmc)<=TOL
        print(f"{b:9} {arm:7} {m!r:22} {c!r:22} {t!r:22} {dmc:+.6e} {dmco:+.3e} {'PASS' if ok else 'FAIL'}")
        rows[f'{b}_{arm}']=dict(mine=m,coord=c,contract_full=t,rounded=ROUND[b][i],
            mine_minus_contract=dmc, mine_minus_coord=dmco,
            mine_minus_rounded=m-ROUND[b][i], passes_1e_12=ok)
print()
print("=== agreement mine vs coordinator ===")
mx=max(abs(MINE[b][i]-COORD[b][i]) for b in MINE for i in (0,1))
print("max |mine - coord| =", mx, "-> bit-identical" if mx==0 else "")
print()
print("=== what the coordinator actually compared against ===")
print("He stored auditor_strict=0.1417 etc (4-dp ROUNDED display values), diff ~1e-4, and called it reproduction.")
print("The CONTRACT target is full precision with tolerance 1e-12. Against THAT, all six FAIL by 1e-5..3e-4.")
json.dump(rows, open('/mnt/c/Users/MDP/dev/llmzip-work/agent_out/f1-audit/evidence/three_way.json','w'), indent=2)
