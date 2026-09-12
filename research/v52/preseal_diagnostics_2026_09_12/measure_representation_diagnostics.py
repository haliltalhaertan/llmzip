"""Representation-only diagnostics. Never imports the historical producer.

This invocation recovers only statistics identifiable from the pinned native
heterogeneity CSV. No missing matrix or strict-positive occupancy is invented.
"""
import argparse
import csv
import hashlib
import io
import json
import platform
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE_SHA256 = '148ae5b727ce1aedc6c84ee9c00727f1454b0e0710d100ac8154fdf8d00924cb'
PRODUCER_SHA256 = '8dce37b1611ba6257570beea559630208f67ffb93697015e95656858a3c7d996'


def entropy(p):
    p = np.asarray(p, dtype=np.float64)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError('invalid occupancy')
    out = np.zeros_like(p)
    mask = (p > 0) & (p < 1)
    out[mask] = -p[mask] * np.log2(p[mask]) - (1-p[mask]) * np.log2(1-p[mask])
    return out


def variance_diagnostics(v):
    v = np.asarray(v, dtype=np.float64)
    if v.shape != (96,) or not np.isfinite(v).all() or (v < 0).any():
        raise ValueError('invalid 96-coordinate variance vector')
    sigma = np.sqrt(v)
    total = float(v.sum())
    order = np.argsort(-v, kind='stable')
    return {
        'cv_sigma': float(sigma.std(ddof=0)/sigma.mean()) if total else None,
        'zero_variance_coordinates': int((v == 0).sum()),
        'total_variance': total,
        'top_variance_fraction': {str(k): float(v[order[:k]].sum()/total) if total else None for k in (16,32,48)},
        'ordered_prefix_fraction': {str(k): float(v[:k].sum()/total) if total else None for k in (16,32,48)},
        'first32_top32_intersection': int(np.isin(order[:32], np.arange(32)).sum()),
    }


def matrix_diagnostics(y):
    """Pure function, exercised on synthetic controls only in this receipt."""
    y = np.asarray(y, dtype=np.float64)
    if y.ndim != 2 or y.shape[1] != 96 or y.shape[0] < 2 or not np.isfinite(y).all():
        raise ValueError('finite N>=2 by96 matrix required')
    v = y.var(axis=0, ddof=0)
    out = variance_diagnostics(v)
    p_gt, p_ge = (y > 0).mean(0), (y >= 0).mean(0)
    out.update(sign_entropy_gt=float(entropy(p_gt).mean()), sign_entropy_ge=float(entropy(p_ge).mean()),
               zero_mass=float((y == 0).mean()), residual_mean_max_abs=float(np.abs(y.mean(0)).max()))
    active = v > 0
    out['active_coordinates'] = int(active.sum())
    out['correlation_proxy'] = None
    if active.sum() >= 2:
        r = np.corrcoef(y[:,active], rowvar=False)
        off = r - np.diag(np.diag(r))
        pairs = np.abs(r[np.triu_indices(int(active.sum()), 1)])
        out['correlation_proxy'] = {'off_mass':float(np.linalg.norm(off)/np.linalg.norm(r)),
                                    'median_abs':float(np.median(pairs)),
                                    'p95_abs':float(np.quantile(pairs,.95,method='linear'))}
    return out


def summary(values):
    a = np.array([v for v in values if v is not None], dtype=np.float64)
    return {'valid_archives':len(a), 'missing_archives':len(values)-len(a),
            'mean':float(a.mean()) if len(a) else None,
            'sd_ddof1':float(a.std(ddof=1)) if len(a)>1 else None,
            'min':float(a.min()) if len(a) else None,'max':float(a.max()) if len(a) else None}


def controls():
    assert np.array_equal(entropy([0,.5,1]),[0,1,0])
    v=np.tile([1.,4.],48)
    assert np.isclose(variance_diagnostics(v)['cv_sigma'],1/3)
    y=np.zeros((4,96));y[:,0]=[-1,0,0,1];y[:,1]=[-2,0,0,2]
    d=matrix_diagnostics(y)
    assert d['active_coordinates']==2 and np.isclose(d['correlation_proxy']['off_mass'],1/np.sqrt(2))
    assert np.isclose(d['correlation_proxy']['p95_abs'],1)
    # >=0 occupancy alone cannot identify >0 occupancy, even for centered inputs.
    a=np.array([-3.,1,1,1]);b=np.array([-2.,0,1,1])
    assert (a>=0).mean()==(b>=0).mean() and (a>0).mean()!=(b>0).mean()
    assert entropy([(a>0).mean()])[0] != entropy([(b>0).mean()])[0]
    assert matrix_diagnostics(np.zeros((2,96)))['correlation_proxy'] is None
    assert variance_diagnostics(np.zeros(96))['cv_sigma'] is None
    return {'status':'PASS','cases':['entropy endpoints','CV sigma not variance','constant-coordinate mask',
                                  'known perfect-correlation proxy','nonidentifiability of strict-positive occupancy',
                                  'degenerate covariance and CV']}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-csv',type=Path,default=HERE/'task1/V52_T4C3_native_heterogeneity.csv')
    ap.add_argument('--output',type=Path,default=HERE/'task1/RESULTS.json')
    args=ap.parse_args()
    source=args.source_csv.resolve()
    if any('beam' in part.lower() or '4f1' in part.lower() for part in source.parts):
        raise ValueError('outside mechanism input scope')
    raw=source.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError('source byte identity mismatch')
    rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8'),newline='')))
    if len(rows)!=470 or len({r['question_id'] for r in rows})!=470:
        raise ValueError('published archive inventory mismatch')
    archives=[]
    for row in rows:
        v=np.array([float(x) for x in row['variance_vector'].split(';')])
        p=np.array([float(x) for x in row['occupancy_vector'].split(';')])
        if p.shape!=(96,):raise ValueError('occupancy dimension mismatch')
        d=variance_diagnostics(v)
        d.update(archive_id=row['question_id'],sign_entropy_ge=float(entropy(p).mean()),
                 sign_entropy_gt=None,zero_mass=None,correlation_proxy=None)
        archives.append(d)
    h=[x['sign_entropy_ge'] for x in archives]
    report={
        'status':'PARTIAL - exact published sufficient statistics recovered; full matrices unavailable',
        'base_commit':'ae9175676b840ae6a80a31eba9836187dc1b7491',
        'source':{'drive_id':'1PME-hZHxp3fRN0AYgygp1oM7v-GNYm6Z','sha256':SOURCE_SHA256,'bytes':len(raw),
                  'producer_sha256':PRODUCER_SHA256,'producer_operator':'>=0','sampling':False},
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'platform':platform.platform()},
        'controls':controls(),
        'longmemeval':{
            'archive_count':470,'dimensions':96,
            'D1_ge':summary(h),'fraction_H_ge_below_local_075':sum(x<.75 for x in h)/len(h),
            'count_H_ge_equal_local_075':sum(x==.75 for x in h),
            'D1_gt':None,'D1_gt_reason':'Zero mass unavailable; >=0 is not silently substituted for >0.',
            'D2_cv_sigma':summary([x['cv_sigma'] for x in archives]),
            'D3_top_variance_fraction':{str(k):summary([x['top_variance_fraction'][str(k)] for x in archives]) for k in (16,32,48)},
            'D3_ordered_prefix_fraction':{str(k):summary([x['ordered_prefix_fraction'][str(k)] for x in archives]) for k in (16,32,48)},
            'D4':None,'D4_reason':'Full correlation matrix cannot be reconstructed from diagonal variances and published covariance-energy/mean-correlation aggregates.',
            'archives':archives},
        'locomo':{'status':'MISSING_FROZEN_MATRIX_OR_SUFFICIENT_STATISTICS','D1':None,'D2':None,'D3':None,'D4':None},
        'interpretation':[
            '0.75 is a requested local descriptive cut, not a verified universal literature threshold.',
            'Sorted diagonal variance is not the fixed ordered-prefix or PCA eigenvalue spectrum.',
            'Variance retained does not establish retrieval fairness, quality, mechanism or semantic importance.',
            'Archives receive equal summary weight; no independence or population-inference claim.',
            'No query-document distances, rankings, recalls, corpus reconstruction or real ITQ fit.'],
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in report['longmemeval'].items() if k!='archives'},indent=2))


if __name__=='__main__':main()
