"""Muse'un bulgularinin BAGIMSIZ dogrulanmasi. Onaylamak icin degil."""
import json, os, numpy as np
SP = os.path.dirname(os.path.abspath(__file__))
J = lambda m: json.load(open(os.path.join(SP, "out", f"MRL_PARITY_{m}.json"), encoding="utf-8"))

print("=" * 72)
print("BULGU 1 - 'hizalama' metrigi: BOS TABANDA kac cikiyor?")
print("=" * 72)
print("Muse iddiasi: bos tabanda hizalama %87.8-90.4, gozlenenlerin UCU DE altinda")
for m, D in (("arctic-xs", 384), ("arctic-m-1.5", 768), ("mxbai-large", 1024)):
    a = J(m)["aggregate"]; nl = a["isotropic_null"]
    obs = a["f_nominal"]["48"] / a["f_sorted"]["48"] * 100
    null = nl["f_nominal"]["48"] / nl["f_sorted"]["48"] * 100
    print(f"  {m:14s} gozlenen {obs:5.1f}%   BOS TABAN {null:5.1f}%   "
          f"fark {obs-null:+6.1f} pp   p_srt={a['p_sorted']:.3f}")
print("  -> Muse hakli mi?", "EVET" if all(
    J(m)["aggregate"]["f_nominal"]["48"]/J(m)["aggregate"]["f_sorted"]["48"] <
    J(m)["aggregate"]["isotropic_null"]["f_nominal"]["48"]/J(m)["aggregate"]["isotropic_null"]["f_sorted"]["48"]
    for m in ("arctic-xs", "arctic-m-1.5", "mxbai-large")) else "HAYIR")

print()
print("=" * 72)
print("BULGU 2 - '0.005 / 0.000 puan' iddiasi uretilebiliyor mu?")
print("=" * 72)
per = J("arctic-m-1.5")["per_archive"]
for k in ("48", "96", "384"):
    v = [x["f_nominal"][k] for x in per]
    m15, m3, m6, m10 = (np.median(v)*100, np.median(v[:3])*100,
                        np.median(v[:6])*100, np.median(v[:10])*100)
    print(f"  f_{k:>3}  med15={m15:.4f}  ilk3={m3:.4f} ({m3-m15:+.4f})  "
          f"ilk6={m6:.4f} ({m6-m15:+.4f})  |  ilk10={m10:.4f}  ilk3-ilk10={m3-m10:+.4f}")
print("  -> raporun iddiasi '15 arsivin medyanindan 0.005 / 0.000'")
print("  -> ilk 10 arsive karsi olculmus olabilir mi? yukaridaki son sutuna bak")

print()
print("=" * 72)
print("BULGU 3 - kesme orani, 5 arsiv (Muse: %15.76-19.84)")
print("=" * 72)
import csv, sys
sys.path.insert(0, SP)
from measure_mrl_parity import archive_texts_only
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("Snowflake/snowflake-arctic-embed-m-v1.5")
frozen = list(csv.DictReader(open("/home/mdp/muse-work/campaign-label-audit/docs/v52/task4c2/V52_T4C2_feature_geometry.csv", encoding="utf-8")))[:5]
by_id = {str(x["question_id"]): x for x in json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json", encoding="utf-8"))}
rates = []
for r in frozen:
    t = archive_texts_only(by_id[r["question_id"]])
    L = np.array([len(x) for x in tok(t, truncation=False)["input_ids"]])
    rt = (L > 512).mean() * 100; rates.append(rt)
    print(f"  {r['question_id']}  n={len(L):4d}  kesilen %{rt:.2f}  max token {L.max()}")
print(f"  -> aralik %{min(rates):.2f} - %{max(rates):.2f}   (Muse: %15.76 - %19.84)")

print()
print("=" * 72)
print("BULGU 4 - model config'lerinde matryoshka_dimensions var mi?")
print("=" * 72)
import urllib.request
for hf in ("Snowflake/snowflake-arctic-embed-m-v1.5", "mixedbread-ai/mxbai-embed-large-v1",
           "Snowflake/snowflake-arctic-embed-xs"):
    found = {}
    for fn in ("config.json", "config_sentence_transformers.json"):
        try:
            c = json.loads(urllib.request.urlopen(
                f"https://huggingface.co/{hf}/raw/main/{fn}", timeout=20).read())
            for key in c:
                if "matryoshka" in key.lower() or "truncate" in key.lower():
                    found[f"{fn}:{key}"] = c[key]
        except Exception as e:
            pass
    print(f"  {hf.split('/')[-1]:32s} {found if found else 'matryoshka anahtari YOK'}")

print()
print("=" * 72)
print("BULGU 5 - mxbai icin 2.85x esigi ve marj")
print("=" * 72)
a = J("mxbai-large")["aggregate"]; nl = a["isotropic_null"]
thr = 2.8532 * nl["f_nominal"]["48"] * 100
print(f"  taban %{nl['f_nominal']['48']*100:.3f}  ->  2.85x esigi %{thr:.2f}")
print(f"  olculen f_48 %{a['f_nominal']['48']*100:.3f}   marj {thr - a['f_nominal']['48']*100:.2f} puan")
