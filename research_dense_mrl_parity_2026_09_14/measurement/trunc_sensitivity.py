# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
"""KESME DUYARLILIK KONTROLU.

Bulgu: turlarin %17.03'u 512 token sinirinda kesiliyor. Leksikal tarafta kesme
YOK (TF-IDF tum metni gorur). Bu bir parite acigidir.

Soru: kesme f_48 tahminini bozuyor mu?
Yontem: ayni arsivlerde iki alt kume -
  (A) TUM turlar, kesmeli  (ana olcumdeki durum)
  (B) yalnizca <=512 token turlar, kesme HIC yok
(B) ~ (A) ise kesme tahmini bozmuyor demektir.
"""
import json, csv, os, sys
import numpy as np, torch
from transformers import AutoTokenizer, AutoModel

SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
from measure_mrl_parity import archive_texts_only, geometry_stats

torch.set_num_threads(int(os.environ.get("TORCH_THREADS", 16)))
HF = "Snowflake/snowflake-arctic-embed-m-v1.5"
CORPUS = "/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json"
GEOM = "/home/mdp/muse-work/campaign-label-audit/docs/v52/task4c2/V52_T4C2_feature_geometry.csv"

tok = AutoTokenizer.from_pretrained(HF)
mdl = AutoModel.from_pretrained(HF); mdl.eval()
frozen = list(csv.DictReader(open(GEOM, encoding="utf-8")))[:3]
by_id = {str(x["question_id"]): x for x in json.load(open(CORPUS, encoding="utf-8"))}


def embed(ts, batch=32):
    order = np.argsort([-len(t) for t in ts])
    out = np.zeros((len(ts), 768), dtype=np.float32)
    for i in range(0, len(order), batch):
        ix = order[i:i + batch]
        e = tok([ts[j] for j in ix], padding=True, truncation=True,
                max_length=512, return_tensors="pt")
        with torch.no_grad():
            out[ix] = mdl(**e).last_hidden_state[:, 0, :].numpy()
    return out


print(f"{'arsiv':>10} {'kol':>26} {'N':>5} {'f_48':>9} {'f_96':>9} {'p_nom':>9}")
rows = {"A": [], "B": []}
for r in frozen:
    qid = r["question_id"]
    texts = archive_texts_only(by_id[qid])
    L = np.array([len(x) for x in tok(texts, truncation=False)["input_ids"]])
    keep = [t for t, l in zip(texts, L) if l <= 512]
    for kol, ts in (("A tum turlar (kesmeli)", texts), ("B yalniz <=512 (kesme yok)", keep)):
        s = geometry_stats(embed(ts), [48, 96])
        rows["A" if kol.startswith("A") else "B"].append(s)
        print(f"{qid:>10} {kol:>26} {len(ts):5d} {s['f_nominal']['48']*100:8.3f}% "
              f"{s['f_nominal']['96']*100:8.3f}% {s['p_nominal']:+9.4f}")

print()
for k in ("48", "96"):
    a = np.median([x["f_nominal"][k] for x in rows["A"]]) * 100
    b = np.median([x["f_nominal"][k] for x in rows["B"]]) * 100
    print(f"medyan f_{k}:  A(kesmeli)={a:.3f}%   B(kesmesiz)={b:.3f}%   fark={b-a:+.3f} pp")
pa = np.median([x["p_nominal"] for x in rows["A"]])
pb = np.median([x["p_nominal"] for x in rows["B"]])
print(f"medyan p_nom: A={pa:+.4f}   B={pb:+.4f}   fark={pb-pa:+.4f}")
print()
print("ESIK: 2.85x leksikal denkligi D=768,k=48 icin %17.83 gerektiriyor.")
