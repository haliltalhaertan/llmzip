#!/usr/bin/env python3
# Audit helper preserved for reproducibility. It inspects ZIP member names and NPZ schemas only.
from pathlib import Path
from zipfile import ZipFile
import io, json, hashlib, numpy as np

def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inspect_t4c2(path):
    with ZipFile(path) as outer:
        name=next(n for n in outer.namelist() if n.endswith("V52_T4C2_BINARY_GEOMETRY.zip"))
        data=outer.read(name)
    with ZipFile(io.BytesIO(data)) as inner:
        codes=[n for n in inner.namelist() if n.endswith(".npz")]
        arr=np.load(io.BytesIO(inner.read(codes[0])),allow_pickle=False)
        return {"nested_sha256":hashlib.sha256(data).hexdigest(),"npz_count":len(codes),"sample":codes[0],"schema":{k:{"shape":list(arr[k].shape),"dtype":str(arr[k].dtype),"nbytes":int(arr[k].nbytes)} for k in arr.files}}
