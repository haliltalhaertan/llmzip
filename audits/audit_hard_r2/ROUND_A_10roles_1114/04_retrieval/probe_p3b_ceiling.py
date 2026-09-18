"""04_retrieval probe P3b: recompute pool/ceiling/complementarity from per-query top-500 lists.
Own arithmetic; compares against firststage RESULTS.json + REPORT §5 decomposition.
Persists query identities (qid lists per bucket) to own dir.
"""
import gzip, json

D = "/mnt/c/Users/MDP/dev/llmzip-work/audit_hard_r2/04_retrieval/"
P = ("/mnt/c/Users/MDP/dev/llmzip-work/_wt_top10/research_top10_comparison_2026_09_16/"
     "ideas_r1/firststage/per_query.jsonl.gz")
rows = [json.loads(l) for l in gzip.open(P, "rt", encoding="utf-8")]
RES = json.load(open(D + "firststage_RESULTS.orig.json"))
print(f"n={len(rows)}; distinct qids={len({r['qid'] for r in rows})}")

arms = {"CODE": "code_top500", "BM25": "bm25_top500", "RRF": "rrf_top500"}

def hit(lst, gold, M):
    return 1.0 if (set(lst[:M]) & set(gold)) else 0.0

def cfr3(lst, gold, M):
    return min(3, len(set(lst[:M]) & set(gold))) / len(gold)

# pool table @ M vs stored RESULTS.json
maxd = 0
for M in (10, 20, 50, 100, 200, 500):
    for arm, key in arms.items():
        mine_h = sum(hit(r[key], r["gold"], M) for r in rows) / len(rows) * 100
        mine_c = sum(cfr3(r[key], r["gold"], M) for r in rows) / len(rows) * 100
        st = RES["pool"][str(M)][arm]
        dh, dc = abs(mine_h - st["hit"]), abs(mine_c - st["ceiling_fr3"])
        maxd = max(maxd, dh, dc)
        flag = "OK" if max(dh, dc) < 1e-9 else "DIFF"
        print(f"M={M:3d} {arm}: hit mine={mine_h:6.3f} stored={st['hit']:6.3f} | ceil mine={mine_c:6.3f} stored={st['ceiling_fr3']:6.3f} {flag}")
print(f"max_abs_diff={maxd:.2e}")

# REPORT §5 decomposition: 350 hit@10 CODE; 183 gold-in-100-not-top10; 172 outside top100
code_hit10 = [r["qid"] for r in rows if hit(r["code_top500"], r["gold"], 10)]
code_hit100 = set(r["qid"] for r in rows if hit(r["code_top500"], r["gold"], 100))
reach = [q for q in code_hit100 if q not in set(code_hit10)]
unreach = [r["qid"] for r in rows if r["qid"] not in code_hit100]
print(f"\nCODE Hit@10 n={len(code_hit10)} (REPORT 350); in-100-not-10 n={len(reach)} (REPORT 183); outside-100 n={len(unreach)} (REPORT 172)")
print(f"sum check: {len(code_hit10)}+{len(reach)}+{len(unreach)}={len(code_hit10)+len(reach)+len(unreach)} vs n=705")
json.dump({"code_hit10": sorted(code_hit10), "reachable_in100_not10": sorted(reach),
           "unreachable_outside100": sorted(unreach)},
          open(D + "realtalk_reachability_qids.json", "w"), indent=0)
print("WROTE realtalk_reachability_qids.json")

# complementarity @100: CODE-only / BM25-only
both = sum(1 for r in rows if hit(r["code_top500"], r["gold"], 100) and hit(r["bm25_top500"], r["gold"], 100))
co = sum(1 for r in rows if hit(r["code_top500"], r["gold"], 100) and not hit(r["bm25_top500"], r["gold"], 100))
bo = sum(1 for r in rows if not hit(r["code_top500"], r["gold"], 100) and hit(r["bm25_top500"], r["gold"], 100))
ne = sum(1 for r in rows if not hit(r["code_top500"], r["gold"], 100) and not hit(r["bm25_top500"], r["gold"], 100))
print(f"@100 both={both} CODE-only={co} (REPORT 49) BM25-only={bo} (REPORT 67) neither={ne} (REPORT 105)")
# both-miss with EITHER scorer @10 (REPORT: 328 queries both miss @10, 170 outside top100)
bothmiss10 = [r for r in rows if not hit(r["code_top500"], r["gold"], 10) and not hit(r["bm25_top500"], r["gold"], 10)]
out100_either = sum(1 for r in bothmiss10 if (not hit(r["code_top500"], r["gold"], 100) and not hit(r["bm25_top500"], r["gold"], 100)))
print(f"both-miss@10 n={len(bothmiss10)} (REPORT 328); of those outside BOTH top100: {out100_either} (REPORT 170)")
# rerank_ceiling.json cross-check (RealTalk qscale + RT_BM25)
RC = json.load(open(D + "rerank_ceiling.orig.json"))
for b in ("REALTALK", "RT_BM25"):
    arm = "CODE" if b == "REALTALK" else "BM25"
    for M in ("10", "50", "100"):
        mine = sum(cfr3(r[arms[arm]], r["gold"], int(M)) for r in rows) / len(rows) * 100
        st = RC["results"][b]["fr3_ceiling"][M]
        print(f"{b} M={M}: mine={mine:.4f} rerank_ceiling.json={st:.4f} diff={abs(mine-st):.2e}")
