"""Independent exact check: condition on shared random gold first."""
from fractions import Fraction as F
from itertools import product
from math import factorial
import json
from pathlib import Path
coins=list(product((-1,1), repeat=2))
def top3(n,u,v):
    w=1-u-v; ans=F(0)
    for i in range(n+1):
        for j in range(n-i+1):
            k=n-i-j
            weight=F(factorial(n),factorial(i)*factorial(j)*factorial(k))*u**i*v**j*w**k
            recall=F(0) if i>=3 else min(F(1),F(3-i,j+1))
            ans+=weight*recall
    return ans
results={}
for N in (6,10):
    values={}
    for method,t in [('sign',F(1)),('cos_low',F(1,2)),('cos_high',F(10))]:
        conditional=[]
        for eps in coins:
            gold=[F(1),t*eps[0],t*eps[1]]
            diffs=[]
            for delta in coins:
                nongold=[F(-1),t*delta[0],t*delta[1]]
                # All norms equal within this model, query=(1,1,1).
                if method=='sign':
                    diffs.append(sum(x<0 for x in nongold)-sum(x<0 for x in gold))
                else:
                    diffs.append(sum(gold)-sum(nongold))
            u=F(sum(x<0 for x in diffs),4)
            v=F(sum(x==0 for x in diffs),4)
            conditional.append(top3(N-1,u,v))
        value=sum(conditional,F(0))/4
        values[method]={'exact':str(value),'display':float(value),'conditional':[str(x) for x in conditional]}
    assert F(values['cos_low']['exact'])>F(values['sign']['exact'])>F(values['cos_high']['exact'])
    results[str(N)]=values
out=Path(__file__).with_name('conditional_transport_results.json')
out.write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
