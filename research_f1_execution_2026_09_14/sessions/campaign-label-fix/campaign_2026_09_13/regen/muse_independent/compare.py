import json
mine = json.load(open("/tmp/task1indep/results.json"))
for p in ["/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/task1_extension_lme.json", "/mnt/c/Users/MDP/dev/llmzip-work/regen/locomo/task1_locoMo_stats.json"]:
    try:
        d = json.load(open(p))
        print("="*20, p)
        s = json.dumps(d)[:1500]
        print(s.replace("\n"," ")[:1500])
        print("top keys:", list(d.keys())[:20])
    except Exception as e:
        print(p, "ERR", e)
