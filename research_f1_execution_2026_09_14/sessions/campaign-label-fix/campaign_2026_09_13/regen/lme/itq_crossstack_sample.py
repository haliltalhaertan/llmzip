import importlib.util, io, zipfile, pickle
import numpy as np
spec=importlib.util.spec_from_file_location("a1", "/mnt/c/Users/MDP/dev/llmzip/adapters/longmemeval_v52_adapter.py")
a1=importlib.util.module_from_spec(spec); spec.loader.exec_module(a1)
zf=zipfile.ZipFile("/mnt/c/Users/MDP/dev/llmzip-work/drive/V52_T4C2_BINARY_GEOMETRY.zip")
names=sorted(n for n in zf.namelist() if n.endswith(".npz"))
idxs=[0,47,94,141,188,235,282,329,376,423]
tot=0; bad=0
for i in idxs:
    qid=names[i].split("/")[-1][:-4]
    d=np.load(io.BytesIO(zf.read(names[i])), allow_pickle=False)
    with open(f"/mnt/c/Users/MDP/dev/llmzip-work/regen/lme/cache_repr/{qid}.pkl","rb") as f:
        C=pickle.loads(f.read())["C"]
    nm=0
    for j,s in enumerate([int(x) for x in np.asarray(d["itq_seeds"]).ravel()]):
        R=a1.fit_itq(C, seed=s)
        pk=np.packbits(np.asarray(C)@R>=0, axis=1, bitorder="big")
        if not np.array_equal(pk, d["itq_doc_packed"][j]): nm+=1
    tot+=5; bad+=nm
    print(qid, "mismatched seeds:", nm, "of 5")
print("TOTAL mismatched:", bad, "of", tot, "| numpy", np.__version__)
