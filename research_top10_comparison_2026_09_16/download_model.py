import concurrent.futures, hashlib, json, pathlib, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parent
META=json.loads((ROOT/'MODEL_SOURCE.json').read_text())
DEST=ROOT/'model'; DEST.mkdir(exist_ok=True)
FILES=[x['rfilename'] for x in META['siblings'] if not x['rfilename'].startswith(('onnx/','assets/','.'))]
def get(name):
    out=DEST/name; out.parent.mkdir(parents=True,exist_ok=True)
    url=f"https://huggingface.co/{META['id']}/resolve/{META['sha']}/{name}"
    tmp=out.with_name(out.name+'.part')
    st=time.time()
    subprocess.run(['curl','-L','--fail','--retry','3','--connect-timeout','20','--max-time','900',url,'-o',str(tmp)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    tmp.replace(out)
    h=hashlib.sha256()
    with out.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    rec={'file':name,'bytes':out.stat().st_size,'sha256':h.hexdigest(),'seconds':time.time()-st,'url':url}
    print(json.dumps(rec),flush=True)
    return rec
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records=list(pool.map(get,FILES))
    (ROOT/'MODEL_DOWNLOAD.json').write_text(json.dumps({'model':META['id'],'revision':META['sha'],'files':records},indent=2))
    print('DOWNLOAD_COMPLETE',len(records),flush=True)
