"""[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
Gemini'nin karar esiklerinin dayandigi "izotropik taban = %12.5" iddiasinin testi.
Hicbir model gerekmiyor: saf izotropik gurultu uretip ayni boru hattindan gecir.
"""
import numpy as np

def pipeline(X, k):
    Y = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)   # row L2
    C = Y - Y.mean(axis=0)                                        # center
    v = np.var(C, axis=0)                                         # coord variance
    f_nom = v[:k].sum() / v.sum()                                 # NOMINAL ilk k
    vs = np.sort(v)[::-1]
    f_srt = vs[:k].sum() / v.sum()                                # SIRALI ust k
    r = np.arange(1, len(vs) + 1)
    p_srt = -np.polyfit(np.log(r), np.log(vs + 1e-12), 1)[0]      # sirali p_B
    p_nom = -np.polyfit(np.log(r), np.log(v + 1e-12), 1)[0]       # nominal p_B
    return f_nom, f_srt, p_srt, p_nom

D, K, N = 384, 48, 500
rng = np.random.default_rng(20260914)
res = np.array([pipeline(rng.standard_normal((N, D)), K) for _ in range(200)])

print("IZOTROPIK BOS HIPOTEZ  (N=500, D=384, k=48, 200 tekrar)")
print("=" * 62)
lbl = ["f_48 NOMINAL ilk-48", "f_48 SIRALI  ust-48", "p_B  SIRALI eksen", "p_B  NOMINAL eksen"]
for i, name in enumerate(lbl):
    c = res[:, i]
    unit = "%" if i < 2 else ""
    m = c * 100 if i < 2 else c
    print(f"{name:22s} ortalama {m.mean():7.4f}{unit}   sd {m.std():.4f}   "
          f"[%95: {np.percentile(m,2.5):.4f} , {np.percentile(m,97.5):.4f}]")

print()
print(f"Gemini'nin ilan ettigi taban          : %12.50")
print(f"NOMINAL icin dogru mu?                : EVET  (olculen %{res[:,0].mean()*100:.3f})")
print(f"SIRALI icin dogru mu?                 : HAYIR (olculen %{res[:,1].mean()*100:.3f}) "
      f"-> {res[:,1].mean()/0.125:.2f}x sisme, saf gurultuden")
print()
print("Anlami: 48/384 eksen SIRALANIRSA, bos hipotez bile %12.5'i degil "
      f"%{res[:,1].mean()*100:.1f}'i verir.")
print("        Ayni sekilde siralama tek basina p_B ~ "
      f"{res[:,2].mean():.3f} uretir; olculen p_B bununla kiyaslanmali, 0 ile degil.")

# N'e bagimlilik: sirali sismesi N ile azalir mi?
print("\nSIRALI tabanin N'e bagimliligi:")
for n in (200, 500, 1000, 2000):
    r2 = np.array([pipeline(rng.standard_normal((n, D)), K) for _ in range(40)])
    print(f"  N={n:5d}  f_48 sirali taban = %{r2[:,1].mean()*100:5.2f}   p_B sirali taban = {r2[:,2].mean():.3f}")
