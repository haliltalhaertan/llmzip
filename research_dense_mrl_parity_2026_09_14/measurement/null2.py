import numpy as np
def stats(X,k):
    Y=X/(np.linalg.norm(X,axis=1,keepdims=True)+1e-12)
    C=(Y-Y.mean(0,keepdims=True)).astype(np.float64)
    v=np.var(C,axis=0); vs=np.sort(v)[::-1]; tot=v.sum()
    r=np.arange(1,len(v)+1)
    p_s=-np.polyfit(np.log(r),np.log(vs),1)[0]
    return v[:k].sum()/tot, vs[:k].sum()/tot, p_s
rng=np.random.default_rng(20260914)
print("IZOTROPIK TABAN, N=490 (arsiv medyani), 40 tekrar")
print(f"{'D':>6} {'k':>5} {'k/D':>8} {'nominal':>9} {'sirali':>9} {'sisme':>7} {'p_sirali':>9}")
for D in (384,768,1024):
    for k in (48, D//8):
        a=np.array([stats(rng.standard_normal((490,D)).astype(np.float32),k) for _ in range(40)])
        print(f"{D:6d} {k:5d} {k/D*100:7.2f}% {a[:,0].mean()*100:8.3f}% {a[:,1].mean()*100:8.3f}% "
              f"{a[:,1].mean()/a[:,0].mean():6.3f}x {a[:,2].mean():9.4f}")
