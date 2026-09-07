"""Compare score records; this cannot certify top-three document identities."""
import csv, gzip, hashlib, io, json, math, pathlib, sys
KEY=['question_id','rotation_seed','arm']
NUM=['native_fractional_R3','fractional_R3']
ARMS={'NATIVE','SCALED_NATIVE','FULLHAAR_FRESH','SCALED_FULLHAAR','BLOCK32_FRESH','SCALED_BLOCK32'}
def keyed(rows):
    result={}
    for r in rows:
        k=tuple(r[x] for x in KEY)
        if k in result: raise ValueError('duplicate key')
        result[k]=r
    return result
def compare_rows(a,b):
    a,b=keyed(a),keyed(b)
    if a.keys()!=b.keys(): raise ValueError('key-set mismatch')
    maximum=0.0; changes=0
    for k,x in a.items():
        y=b[k]
        if x.keys()!=y.keys(): raise ValueError('column mismatch')
        for c in x:
            if c in NUM:
                v,w=float(x[c]),float(y[c])
                if not math.isfinite(v) or not math.isfinite(w): raise ValueError('nonfinite')
                d=abs(v-w); maximum=max(maximum,d); changes+=d!=0
            elif x[c]!=y[c]: raise ValueError('metadata mismatch')
    return {'max_absolute_numeric_difference':maximum,'changed_numeric_cells':changes,'numeric_within_1e_12':maximum<=1e-12,'rows':len(a)}
def controls():
    a=[{'question_id':'a','rotation_seed':'59001','arm':'NATIVE','native_fractional_R3':'0.2','fractional_R3':'0.2','tie_identity':'fixed'}]
    assert compare_rows(a,a)['numeric_within_1e_12']
    changed=[dict(a[0],fractional_R3='0.3')]
    assert not compare_rows(a,changed)['numeric_within_1e_12']
    for bad in [a+a,[],[dict(a[0],rotation_seed='59002')],[dict(a[0],fractional_R3='nan')],[dict(a[0],tie_identity='wrong')]]:
        try: compare_rows(a,bad)
        except ValueError: pass
        else: raise AssertionError('negative control accepted')
    return {'positive_control':'PASS','negative_controls':['numeric perturbation','duplicate key','missing row','wrong seed','NaN','metadata drift'],'status':'ALL_REJECTED'}
def summary_differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        if a.keys()!=b.keys(): return [{'path':path,'type':'key-set mismatch'}]
        return [d for k in a for d in summary_differences(a[k],b[k],path+'/'+k)]
    if isinstance(a,list) and isinstance(b,list):
        if len(a)!=len(b): return [{'path':path,'type':'length mismatch'}]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in summary_differences(x,y,path+'/'+str(i))]
    if a==b: return []
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return [{'path':path,'original':a,'reproduction':b,'absolute_difference':abs(a-b)}]
    return [{'path':path,'original':a,'reproduction':b,'type':'value mismatch'}]
def main():
    tests=controls()
    if len(sys.argv)==1:
        print(json.dumps(tests,indent=2)); return
    p,q=map(pathlib.Path,sys.argv[1:3]); x,y=p.read_bytes(),q.read_bytes(); a,b=gzip.decompress(x),gzip.decompress(y)
    rows_a=list(csv.DictReader(io.StringIO(a.decode()))); rows_b=list(csv.DictReader(io.StringIO(b.decode())))
    for rows in [rows_a,rows_b]:
        assert len(rows)==92100
        assert {r['arm'] for r in rows}==ARMS
        assert {int(r['rotation_seed']) for r in rows}==set(range(59001,59011))
        assert len({r['question_id'] for r in rows})==1535
    result={'controls':tests,**compare_rows(rows_a,rows_b),'compressed_bytes_equal':x==y,'decompressed_csv_bytes_equal':a==b,'original_sha256':hashlib.sha256(x).hexdigest(),'reproduction_sha256':hashlib.sha256(y).hexdigest(),'original_csv_sha256':hashlib.sha256(a).hexdigest(),'reproduction_csv_sha256':hashlib.sha256(b).hexdigest(),'limitation':'Only persisted question scores and metadata are compared; retrieval top-three document IDs were not persisted.'}
    result['csv_after_crlf_to_lf_equal']=a.replace(b'\r\n',b'\n')==b.replace(b'\r\n',b'\n')
    result['csv_line_endings']={'original_crlf':a.count(b'\r\n'),'reproduction_crlf':b.count(b'\r\n'),'original_lf':a.count(b'\n'),'reproduction_lf':b.count(b'\n')}
    result['csv_columns']=list(rows_a[0])
    result['gzip_header']={'original_first_10_bytes_hex':x[:10].hex(),'reproduction_first_10_bytes_hex':y[:10].hex(),'original_mtime':int.from_bytes(x[4:8],'little'),'reproduction_mtime':int.from_bytes(y[4:8],'little')}
    sa=p.parent/'locomo_scale_summary.json'; sb=q.parent/'locomo_scale_summary.json'
    if sa.exists() and sb.exists():
        result['summary_differences']=summary_differences(json.loads(sa.read_bytes()),json.loads(sb.read_bytes()))
        result['summary_original_sha256']=hashlib.sha256(sa.read_bytes()).hexdigest()
        result['summary_reproduction_sha256']=hashlib.sha256(sb.read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if len(sys.argv)>3: pathlib.Path(sys.argv[3]).write_text(json.dumps(result,indent=2),encoding='utf-8')
if __name__=='__main__': main()
