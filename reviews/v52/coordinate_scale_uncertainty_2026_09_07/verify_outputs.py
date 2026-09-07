"""Verify persisted bootstrap summaries without resampling."""
import csv
import hashlib
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
def quantile(values,p):
    x=sorted(values);pos=(len(x)-1)*p;i=int(pos);j=min(i+1,len(x)-1)
    return x[i]+(x[j]-x[i])*(pos-i)

def main():
    result=json.loads((HERE/'outputs/RESULTS.json').read_text())
    assert hashlib.sha256((HERE/'bootstrap.py').read_bytes()).hexdigest()==result['code_sha256']
    assert hashlib.sha256((HERE/'ANALYSIS_PLAN.md').read_bytes()).hexdigest()==result['plan_sha256']
    for name,scheme in result['schemes'].items():
        path=HERE/'outputs'/(name+'.csv')
        assert hashlib.sha256(path.read_bytes()).hexdigest()==scheme['replicates_csv_sha256']
        with path.open(newline='') as stream: rows=list(csv.DictReader(stream))
        assert len(rows)==10000 and [int(r['replicate']) for r in rows]==list(range(1,10001))
        for key,entry in scheme['statistics'].items():
            values=[float(r[key]) for r in rows if r[key]!='']
            assert all(math.isfinite(x) for x in values)
            assert len(values)==entry['finite'] and 10000-len(values)==entry['undefined']
            for p,reported in zip([.025,.5,.975],entry['percentiles_2_5_50_97_5']):
                assert math.isclose(quantile(values,p),reported,abs_tol=1e-12,rel_tol=1e-12)
            assert min(values)==entry['min'] and max(values)==entry['max']
        for row in rows:
            for prefix in ['A','B']:
                full,block,interaction=[row[prefix+'_'+s] for s in ['full','block','I']]
                if full=='' or block=='': assert interaction==''
                else: assert math.isclose(float(full)-float(block),float(interaction),abs_tol=1e-12,rel_tol=1e-12)
        print(name+': rows/hash/finite counts/18 quantiles/interactions PASS')
    assert quantile([0,2],.25)==.5
    try:
        assert math.isclose(quantile([0,2],.25),.75,abs_tol=1e-12)
    except AssertionError:
        print('Incorrect quantile negative control REJECTED')
    else: raise AssertionError('negative control failed')
if __name__=='__main__': main()
