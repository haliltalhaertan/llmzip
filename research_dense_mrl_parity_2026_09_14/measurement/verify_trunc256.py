"""Muse'un 512-vs-256 kesme deneyinin bagimsiz dogrulanmasi.
Ayni metinler, yalniz max_length farkli -> secilim etkisi YOK (benim
trunc_sensitivity.py tasarimimin kusuru buydu)."""
import json, csv, os, sys, numpy as np, torch
from transformers import AutoTokenizer, AutoModel
SP=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,SP)
from measure_mrl_parity import archive_texts_only, geometry_stats
torch.set_num_threads(18)
by_id={str(x["question_id"]):x for x in json.load(open("/mnt/c/Users/MDP/dev/llmzip-work/drive/longmemeval_s_cleaned.json",encoding="utf-8"))}
frozen=list(csv.DictReader(open("/home/mdp/muse-work/campaign-label-audit/docs/v52/task4c2/V52_T4C2_feature_geometry.csv",encoding="utf-8")))[:1]
texts=archive_texts_only(by_id[frozen[0]["question_id"]])
for hf,D in (("Snowflake/snowflake-arctic-embed-m-v1.5",768),("Snowflake/snowflake-arctic-embed-xs",384)):
    tok=AutoTokenizer.from_pretrained(hf); mdl=AutoModel.from_pretrained(hf); mdl.eval()
    res={}
    for ML in (512,256):
        o=np.argsort([-len(t) for t in texts]); E=np.zeros((len(texts),D),dtype=np.float32)
        for i in range(0,len(o),32):
            ix=o[i:i+32]
            e=tok([texts[j] for j in ix],padding=True,truncation=True,max_length=ML,return_tensors="pt")
            with torch.no_grad(): E[ix]=mdl(**e).last_hidden_state[:,0,:].numpy()
        res[ML]=geometry_stats(E,[48])
    d48=(res[256]["f_nominal"]["48"]-res[512]["f_nominal"]["48"])*100
    dp=res[256]["p_nominal"]-res[512]["p_nominal"]
    print(f"{hf.split('/')[-1]:30s} f48@512={res[512]['f_nominal']['48']*100:.4f}%  "
          f"f48@256={res[256]['f_nominal']['48']*100:.4f}%   D(256-512)={d48:+.4f} pp   Dp={dp:+.4f}")
