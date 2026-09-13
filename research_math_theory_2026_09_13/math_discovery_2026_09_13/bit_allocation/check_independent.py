"""Independent finite enumeration without the worker's PMF helpers."""
from fractions import Fraction as F
from itertools import product
from collections import Counter
from pathlib import Path
import json

def evaluate(supports, query, allocation):
    docs=list(product(*supports)); counts=Counter(); contributions=Counter()
    def decode(x,coord,bits):
        if not bits: return F(0)
        if bits==2 or len(supports[coord])==2: return x
        return F(2) if x>0 else F(-2)
    for a,b in product(docs,repeat=2):
        gap=sum(q*(x-y) for q,x,y in zip(query,a,b))
        estimate=sum(query[j]*(decode(a[j],j,allocation[j])-decode(b[j],j,allocation[j])) for j in range(len(query)))
        key='true_tie' if gap==0 else 'estimated_tie' if estimate==0 else 'flip' if gap*estimate<0 else 'correct'
        counts[key]+=1
        if len(query)==3 and key in ('estimated_tie','flip'):
            contributions[str((str(a[0]-b[0]),str(a[1]-b[1]),str(a[2]-b[2]),key))]+=1
    denominator=len(docs)**2-counts['true_tie']
    error=(F(counts['flip'])+F(counts['estimated_tie'],2))/denominator
    return {'error':str(error),'counts':dict(counts),'error_patterns':dict(contributions)}
A=[tuple(map(F,[-3,-1,1,3])),(-F(1,2),F(1,2))]
B=[A[0],(-F(3,2),F(3,2)),(-F(1,10),F(1,10))]
results={}
for tag,supp,q,allocs,expected in [
 ('A',A,[F(1,100),F(1)],[(1,1),(2,0),(0,2)],[F(1,14),F(2,7),F(3,14)]),
 ('B',B,[F(1)]*3,[(1,1,1),(2,1,0)],[F(1,10),F(1,30)])]:
 for alloc,target in zip(allocs,expected):
    value=evaluate(supp,q,alloc); assert F(value['error'])==target
    results[tag+str(alloc)]=value
out=Path(__file__).with_name('coordinator_exact_results.json')
out.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
