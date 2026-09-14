# [LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
#!/usr/bin/env python3
"""proofs_exact.py — norm_aware_sign_bounds duzeltmelerinin kesin-aritmetik kanit/tarama betigi.

Stdlib only (fractions, math, json, sys). Bagimsiz calisir. Float, kesin iddia
ispatlamaz; asagida float YALNIZCA D5a'daki gozlemin kendisini sergiler.

Turkce ozet: her D1..D7 icin (1) OZGUN ifadenin yanlisligini somut tanikla gosterir,
(2) DUZELTILMIS ifadenin ayni tanik + sistematik taramada gecerliligini gosterir.
Her bolumun basinda o bolumu BASARISIZ kilacak kosul acikca yazilidir (BASARISIZLIK KOSULU).
Cikis: PASS/FAIL ozeti; herhangi bir kontrol basarisizsa exit 1.
"""
import sys
from fractions import Fraction as Fr

N_PASS, N_TOT = 0, 0


def check(name, ok, detail=""):
    global N_PASS, N_TOT
    N_TOT += 1
    ok = bool(ok)
    if ok:
        N_PASS += 1
    else:
        print("FAIL %s: %s" % (name, detail), flush=True)
    return ok


def vdot(a, b):
    return sum(x * y for x, y in zip(a, b))


def vnorm2(a):
    return vdot(a, a)


def proj_cone(s, v):
    return [vi if si * vi >= 0 else Fr(0) for si, vi in zip(s, v)]


def member_F(s, x):
    for si, xi in zip(s, x):
        if si > 0:
            if xi < 0:
                return False
        else:
            if xi >= 0:
                return False
    return True


def sup_closed(s, q):
    p = proj_cone(s, q)
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', max(si * qi for si, qi in zip(s, q)))


def inf_closed(s, q):
    p = proj_cone(s, [-qi for qi in q])
    if any(v != 0 for v in p):
        return ('norm', vnorm2(p))
    return ('axis', min(si * qi for si, qi in zip(s, q)))


def orig_sup_att(s, q):
    # OZGUN (yanlis) kural: eksen durumu hep tek-eksen testi.
    kind, _ = sup_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] < 0 for i in N)
    m = max(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


def orig_inf_att(s, q):
    kind, _ = inf_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] > 0 for i in N)
    m = min(s[i] * q[i] for i in range(len(s)))
    return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)


def corr_sup_att(s, q):
    # DUZELTILMIS kural: m<0 tek-eksen, m=0 yuz kurali.
    kind, _ = sup_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] < 0 for i in N)
    m = max(s[i] * q[i] for i in range(len(s)))
    if m < 0:
        return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)
    J = [j for j in range(len(s)) if q[j] == 0]
    return set(N) <= set(J)


def corr_inf_att(s, q):
    kind, _ = inf_closed(s, q)
    N = [i for i, si in enumerate(s) if si < 0]
    if kind == 'norm':
        return all(q[i] > 0 for i in N)
    m = min(s[i] * q[i] for i in range(len(s)))
    if m > 0:
        return any(set(N) <= {j} for j in range(len(s)) if s[j] * q[j] == m)
    J = [j for j in range(len(s)) if q[j] == 0]
    return set(N) <= set(J)


def rational_face_witness(s, J):
    """J destekli, F(s)-uyumlu rasyonel birim vektor (sablon agirliklar)."""
    k = len(J)
    if k == 1:
        w = [Fr(1)]
    elif k == 2:
        w = [Fr(3, 5), Fr(4, 5)]
    elif k == 3:
        w = [Fr(2, 3), Fr(2, 3), Fr(1, 3)]
    elif k == 4:
        w = [Fr(1, 2)] * 4
    else:
        raise AssertionError("sablon disi k=%d" % k)
    d = len(s)
    x = [Fr(0)] * d
    for wj, j in zip(w, sorted(J)):
        x[j] = Fr(s[j]) * wj
    assert vnorm2(x) == 1, (s, J)
    return x


print("== D1: eksen-erisim kurali (m=0 yuz durumu) ==")
print("BASARISIZLIK KOSULU D1: tanik x F(s)'de degilse / skoru m'den farkliysa /")
print("  tek eksenlerden biri F(s)'de ise (ozgunu curutemez) / taramada")
print("  duzeltilmis kural bagimsiz karakterizasyonla celisirsa FAIL.")
# --- Ana tanik: q=(0,0,-1), s=(-,-,+), x=(-3/5,-4/5,0) ---
s1 = (-1, -1, 1)
q1 = (Fr(0), Fr(0), Fr(-1))
x1 = (Fr(-3, 5), Fr(-4, 5), Fr(0))
m1 = max(si * qi for si, qi in zip(s1, q1))
check("D1.tanik.F-uyeligi", member_F(s1, x1), str(x1))
check("D1.tanik.birim", vnorm2(x1) == 1, str(vnorm2(x1)))
check("D1.tanik.skor-esit-m", vdot(q1, x1) == m1 == Fr(0), "skor=%s m=%s" % (vdot(q1, x1), m1))
check("D1.tanik.dejenere", sup_closed(s1, q1)[0] == 'axis', str(sup_closed(s1, q1)))
axes_feas = []
for j in range(3):
    ax = [Fr(0)] * 3
    ax[j] = Fr(s1[j])
    feas = member_F(s1, ax)
    axes_feas.append(feas)
    check("D1.tanik.eksen%d-uygun-degil" % j,
          (not feas) if s1[j] * q1[j] == m1 else True,
          "eksen=%s skor=%s" % (ax, vdot(q1, ax)))
check("D1.ozgun-kural-yanlis", orig_sup_att(s1, q1) is False, "ozgun: erisilmez der")
check("D1.duzeltilmis-erisilir", corr_sup_att(s1, q1) is True, "yuz: N={0,1}<=J={0,1}")
# inf aynasi: q=(0,0,1), s=(-,-,+) -> m'=0, ayni x skoru 0 ile minimuma erisir.
q1m = (Fr(0), Fr(0), Fr(1))
m1i = min(si * qi for si, qi in zip(s1, q1m))
check("D1.inf-ayna.dejenere", inf_closed(s1, q1m) == ('axis', Fr(0)), "m'=%s" % m1i)
check("D1.inf-ayna.ozgun-yanlis", orig_inf_att(s1, q1m) is False, "ozgun: erisilmez der")
check("D1.inf-ayna.duzeltilmis", corr_inf_att(s1, q1m) is True, "yuz kurali erisilir der")
check("D1.inf-ayna.tanik-skor", vdot(q1m, x1) == Fr(0), str(vdot(q1m, x1)))
# --- Sistematik tarama: d=2 tum s x 9 q; d=3 tum s x 7 q ---
D1_Q2 = [(Fr(1), Fr(0)), (Fr(0), Fr(1)), (Fr(3, 5), Fr(4, 5)),
         (Fr(3, 5), Fr(-4, 5)), (Fr(-3, 5), Fr(-4, 5)), (Fr(0), Fr(0)),
         (Fr(1), Fr(1)), (Fr(-1), Fr(0)), (Fr(0), Fr(-1))]
D1_Q3 = [(Fr(0), Fr(0), Fr(-1)), (Fr(0), Fr(0), Fr(1)), (Fr(1), Fr(0), Fr(0)),
         (Fr(0), Fr(0), Fr(0)), (Fr(3, 5), Fr(4, 5), Fr(0)),
         (Fr(-1), Fr(-1), Fr(-1)), (Fr(0), Fr(1), Fr(0))]
D1_S2 = [(a, b) for a in (1, -1) for b in (1, -1)]
D1_S3 = [(a, b, c) for a in (1, -1) for b in (1, -1) for c in (1, -1)]
n_orig_miss = 0
for s in D1_S2 + D1_S3:
    N = [i for i, si in enumerate(s) if si < 0]
    for q in (D1_Q2 if len(s) == 2 else D1_Q3):
        d = len(s)
        # sup bagimsiz karakterizasyon
        ks, vs = sup_closed(s, q)
        if ks == 'norm':
            indep = all(q[i] < 0 for i in N)
            check("D1.tara.sup-norm.%s.%s" % (s, tuple(q)), corr_sup_att(s, q) == indep,
                  "N=%s" % N)
            check("D1.tara.sup-deger.%s.%s" % (s, tuple(q)),
                  vs == vnorm2(proj_cone(s, q)), "sup^2=%s" % vs)
        else:
            m = max(s[i] * q[i] for i in range(d))
            assert m <= 0, (s, q, m)
            if m < 0:
                opt = [j for j in range(d) if s[j] * q[j] == m]
                indep = any(set(N) <= {j} for j in opt)
                okc = corr_sup_att(s, q) == indep
                check("D1.tara.sup-mneg.%s.%s" % (s, tuple(q)), okc, "m=%s opt=%s" % (m, opt))
                if indep:
                    j = next(j for j in opt if set(N) <= {j})
                    ax = [Fr(0)] * d
                    ax[j] = Fr(s[j])
                    check("D1.tara.sup-mneg-tanik.%s.%s" % (s, tuple(q)),
                          member_F(s, ax) and vdot(q, ax) == m, str(ax))
            else:
                J = [j for j in range(d) if q[j] == 0]
                indep = set(N) <= set(J)
                check("D1.tara.sup-m0.%s.%s" % (s, tuple(q)), corr_sup_att(s, q) == indep,
                      "J=%s N=%s" % (J, N))
                if indep:
                    xw = rational_face_witness(s, J)
                    check("D1.tara.sup-m0-tanik.%s.%s" % (s, tuple(q)),
                          member_F(s, xw) and vdot(q, xw) == 0, str(xw))
                else:
                    # erisilmezlik: her iyilestirici J-destekli, N\J'de sifir kalir.
                    gap = set(N) - set(J)
                    check("D1.tara.sup-m0-bos.%s.%s" % (s, tuple(q)), len(gap) > 0, "gap=%s" % gap)
                if corr_sup_att(s, q) and not orig_sup_att(s, q):
                    n_orig_miss += 1
        # inf bagimsiz karakterizasyon (ayna)
        ki, vi = inf_closed(s, q)
        if ki == 'norm':
            indep = all(q[i] > 0 for i in N)
            check("D1.tara.inf-norm.%s.%s" % (s, tuple(q)), corr_inf_att(s, q) == indep,
                  "N=%s" % N)
        else:
            m = min(s[i] * q[i] for i in range(d))
            assert m >= 0, (s, q, m)
            if m > 0:
                opt = [j for j in range(d) if s[j] * q[j] == m]
                indep = any(set(N) <= {j} for j in opt)
                check("D1.tara.inf-mpos.%s.%s" % (s, tuple(q)), corr_inf_att(s, q) == indep,
                      "m=%s" % m)
            else:
                J = [j for j in range(d) if q[j] == 0]
                indep = set(N) <= set(J)
                check("D1.tara.inf-m0.%s.%s" % (s, tuple(q)), corr_inf_att(s, q) == indep,
                      "J=%s" % J)
                if indep:
                    xw = rational_face_witness(s, J)
                    check("D1.tara.inf-m0-tanik.%s.%s" % (s, tuple(q)),
                          member_F(s, xw) and vdot(q, xw) == 0, str(xw))
check("D1.tarama-ozgun-eksik-buldu", n_orig_miss >= 1, "ozgunun kacirdigi durum=%d" % n_orig_miss)

print("== D2: d=2 tablosu sekiz erisim bayragi ==")
print("BASARISIZLIK KOSULU D2: degerlerden biri tutmazsa / erisilir denen icin F(s)'de")
print("  rasyonel eriten yoksa / erisilmez denenin iyilestiricisi F(s)'de ise FAIL.")
q2 = (Fr(3, 5), Fr(4, 5))
# (s, sup, sup^2-turu, sup-erisim, inf, inf-erisim)
D2_EXPECT = [
    ((1, 1), Fr(1), 'norm', True, Fr(3, 5), 'axis', True),
    ((1, -1), Fr(3, 5), 'norm', False, Fr(-4, 5), 'norm', True),
    ((-1, 1), Fr(4, 5), 'norm', False, Fr(-3, 5), 'norm', True),
    ((-1, -1), Fr(-3, 5), 'axis', False, Fr(-1), 'norm', True),
]
D2_WIT = {(1, 1): ((Fr(3, 5), Fr(4, 5)), (Fr(1), Fr(0))),
          (1, -1): (None, (Fr(0), Fr(-1))),
          (-1, 1): (None, (Fr(-1), Fr(0))),
          (-1, -1): (None, (Fr(-3, 5), Fr(-4, 5)))}
D2_CLOS = {(1, 1): (None, (Fr(1), Fr(0))), (1, -1): ((Fr(1), Fr(0)), None),
           (-1, 1): ((Fr(0), Fr(1)), None), (-1, -1): ((Fr(-1), Fr(0)), None)}
for s, esup, ksup, asup, einf, kinf, ainf in D2_EXPECT:
    ks, vs = sup_closed(s, q2)
    ki, vi = inf_closed(s, q2)
    check("D2.deger-sup.%s" % (s,), ks == ksup and (
        vs == esup * esup if ksup == 'norm' else vs == esup), "%s %s" % (ks, vs))
    check("D2.deger-inf.%s" % (s,), ki == kinf and (
        vi == einf * einf if kinf == 'norm' else vi == einf), "%s %s" % (ki, vi))
    check("D2.erisim-sup.%s" % (s,), corr_sup_att(s, q2) == asup, "beklenen=%s" % asup)
    check("D2.erisim-inf.%s" % (s,), corr_inf_att(s, q2) == ainf, "beklenen=%s" % ainf)
    ws, wi = D2_WIT[s]
    cs, ci = D2_CLOS[s]
    if ws is not None:
        check("D2.tanik-sup.%s" % (s,), member_F(s, ws) and vdot(q2, ws) == esup
              and vnorm2(ws) == 1, str(ws))
    else:
        check("D2.kapanis-sup-dista.%s" % (s,), (not member_F(s, cs))
              and vdot(q2, cs) == esup and vnorm2(cs) == 1, str(cs))
    if wi is not None:
        check("D2.tanik-inf.%s" % (s,), member_F(s, wi) and vdot(q2, wi) == einf
              and vnorm2(wi) == 1, str(wi))
    else:
        check("D2.kapanis-inf-dista.%s" % (s,), (not member_F(s, ci))
              and vdot(q2, ci) == einf, str(ci))
# Orijinalin dort yanlis bayragi: REPORT tablosu (duzyazi) yanlis; degerler dogru.
# NOT: verify.py'deki sup/inf_attained yukumleri bu 8 hucrede DUZELTILMIS ile
# ayni sonucu verir (asagida dogrulanir) — D2 kusuru yalnizca REPORT duzyazisindadir.
# Kodun yanlis oldugu yer D1'deki m=0 eksen durumudur.
FROZEN = "/home/mdp/muse-work/mathpin/research_math_theory_2026_09_13/math_discovery_2026_09_13/round4/norm_aware_sign_bounds"
_rep = open(FROZEN + "/REPORT.md", encoding="utf-8").read().splitlines()
check("D2.ozgun-hata.pp-inf", "inf no" in _rep[93], "REPORT.md:94 '(+,+)' satiri: %s" % _rep[93].strip()[-40:])
check("D2.ozgun-hata.mp-inf", _rep[95].strip().endswith("neither |"), "REPORT.md:96 '(-,+)': %s" % _rep[95].strip()[-20:])
check("D2.ozgun-hata.mm-ters", "sup yes, inf no" in _rep[96], "REPORT.md:97 '(-,-)': %s" % _rep[96].strip()[-40:])
check("D2.ozgun-dogru.pm", "inf yes" in _rep[94] and "sup no" in _rep[94],
      "REPORT.md:95 '(+,-)' satiri zaten dogruydu")
check("D2.kod-bu-hucrelerde-dogru",
      orig_sup_att((1, 1), q2) is True and orig_inf_att((1, 1), q2) is True
      and orig_sup_att((1, -1), q2) is False and orig_inf_att((1, -1), q2) is True
      and orig_sup_att((-1, 1), q2) is False and orig_inf_att((-1, 1), q2) is True
      and orig_sup_att((-1, -1), q2) is False and orig_inf_att((-1, -1), q2) is True,
      "verify.py yukumleri 8/8 duzeltilmisle uyumlu (norm + m<0 eksen)")
_mm_m = max(si * qi for si, qi in zip((-1, -1), q2))
_mm_opt = [j for j in range(2) if (-1) * q2[j] == _mm_m]
check("D2.mm-sup-tek-iyilestirici", _mm_opt == [0], "opt=%s m=%s" % (_mm_opt, _mm_m))

print("== D3: rho destegi [1/kok(d),1] + imkansiz negatif-rho ==")
print("BASARISIZLIK KOSULU D3: s_i*x_i=|x_i| bozulursa / rho^2 sinirlari asilirsa /")
print("  eksen/merkez uclari tutmazsa / verify.py:302'de negatif-rho satiri yoksa FAIL.")
rep_lines = open(FROZEN + "/REPORT.md", encoding="utf-8").read().splitlines()
ver_lines = open(FROZEN + "/verify.py", encoding="utf-8").read().splitlines()
check("D3.belge.negatif-rho-satiri", "negative-rho" in ver_lines[301] and "-0.3" in ver_lines[301],
      "verify.py:302: %s" % ver_lines[301].strip()[:80])


def sign_code(x):
    return tuple(1 if xi >= 0 else -1 for xi in x)


def rho2_of(x):
    # s=sign(x) icin rho^2 = ||x||_1^2/d (kesin, koksuz).
    d = len(x)
    s = sign_code(x)
    l1 = sum(si * xi for si, xi in zip(s, x))
    assert l1 == sum(abs(xi) for xi in x), (x, s)
    return l1 * l1 / d, s


# Tarama: d=1..6 eksen + merkez + rasyonel birim vektorler.
D3_VECS = {1: [[Fr(1)], [Fr(-1)]],
           2: [[Fr(1), Fr(0)], [Fr(0), Fr(-1)], [Fr(3, 5), Fr(4, 5)],
               [Fr(-3, 5), Fr(4, 5)], [Fr(0), Fr(1)]],
           3: [[Fr(1), Fr(0), Fr(0)], [Fr(2, 3), Fr(2, 3), Fr(1, 3)],
               [Fr(-2, 3), Fr(2, 3), Fr(1, 3)], [Fr(0), Fr(0), Fr(-1)]],
           4: [[Fr(1), Fr(0), Fr(0), Fr(0)], [Fr(1, 2)] * 4,
               [Fr(3, 5), Fr(4, 5), Fr(0), Fr(0)]]}
for d, vecs in D3_VECS.items():
    for x in vecs:
        assert vnorm2(x) == 1, x
        r2, s = rho2_of(x)
        lo, hi = Fr(1, d), Fr(1)
        check("D3.sinir.d%d.%s" % (d, tuple(x)), lo <= r2 <= hi, "rho^2=%s" % r2)
# Uclar: eksen alt siniri, merkez ust siniri verir (karelerde kesin).
for d in (1, 2, 3, 4, 8):
    e = [Fr(0)] * d
    e[0] = Fr(1)
    r2e, _ = rho2_of(e)
    check("D3.uc-alt.d%d" % d, r2e == Fr(1, d), "eksen rho^2=%s" % r2e)
# Sifir-yuzu: sifir koordinat +1 sayilir, s_i*x_i=|x_i| bozulmaz.
zx = [Fr(0), Fr(-1), Fr(0)]
check("D3.sifir-yuzu", sign_code(zx) == (1, -1, 1)
      and all(si * xi == abs(xi) for si, xi in zip(sign_code(zx), zx)), str(sign_code(zx)))
# Imkansizlik: rho=-0.3, 0, -1 hicbir d>=1 icin [1/kok(d),1]'de degil (hepsi <=0 < alt sinir).
for nm, rv in [("neg03", Fr(-3, 10)), ("sifir", Fr(0)), ("eksi1", Fr(-1))]:
    check("D3.imkansiz.%s" % nm, rv <= 0, "rho=%s <= 0 < 1/kok(d) her d>=1 icin" % rv)
check("D3.belge.genis-aralik", "[-1,1]" in rep_lines[131].replace(" ", "").replace("−", "-"),
      "REPORT.md:132: %s" % rep_lines[131].strip()[:70])

print("== D4: d=4 parantez hatasi (0.5,1] -> [0.5,1] ==")
print("BASARISIZLIK KOSULU D4: e1 skoru 1/2'den farkliysa / e1 ya da q F-disinda ise /")
print("  belgede '(0.5,1]' alintisi bulunamazsa FAIL.")
s4 = (1, 1, 1, 1)
q4 = (Fr(1, 2),) * 4
e1 = (Fr(1), Fr(0), Fr(0), Fr(0))
check("D4.q-birim", vnorm2(q4) == 1, str(vnorm2(q4)))
check("D4.N-bos", all(si > 0 for si in s4), "F=Fbar, uclar erisilir")
check("D4.alt-uc-erisilir", member_F(s4, e1) and vdot(q4, e1) == Fr(1, 2)
      and vnorm2(e1) == 1, "e1 skoru=1/2")
check("D4.ust-uc-erisilir", member_F(s4, q4) and vdot(q4, q4) == 1, "q skoru=1")
check("D4.deger-inf", inf_closed(s4, q4) == ('axis', Fr(1, 2)), str(inf_closed(s4, q4)))
check("D4.deger-sup", sup_closed(s4, q4) == ('norm', Fr(1)), str(sup_closed(s4, q4)))
for j in range(4):
    ej = tuple(Fr(1) if i == j else Fr(0) for i in range(4))
    check("D4.tum-eksenler.d%d" % j, member_F(s4, ej) and vdot(q4, ej) == Fr(1, 2), str(ej))
check("D4.belge.R104", "(0.5, 1]" in rep_lines[104], "REPORT.md:105: %s" % rep_lines[104].strip()[:60])
check("D4.belge.R152", "(0.5,1]" in rep_lines[152], "REPORT.md:153: %s" % rep_lines[152].strip()[-50:])
check("D4.belge.V369", "(0.5,1]" in ver_lines[369], "verify.py:370: %s" % ver_lines[369].strip()[:60])

print("== D5: uc geri cekme (a) esitlik (b) bagimsizlik (c) ilgililik ==")
print("BASARISIZLIK KOSULU D5: bag yarisi tekrarinda |skor-0.7|>=1e-9 ise (yaklasik bile")
print("  tutmaz) / skor tam 0.7'ye esit cikarsa (geri cekme anlamsiz) / alintilar")
print("  belgede bulunamazsa FAIL. NOT: buradaki float GOZLEMDİR, ispat degil.")
import math as _math
_lo, _hi = 0.0, 100.0
for _ in range(200):
    _mid = 0.5 * (_lo + _hi)
    _v = (0.6 * _mid + 0.8) / _math.sqrt(_mid * _mid + 1) - 0.7
    if _v > 0:
        _lo = _mid
    else:
        _hi = _mid
_t = 0.5 * (_lo + _hi)
_xA = (_t / _math.sqrt(_t * _t + 1), 1 / _math.sqrt(_t * _t + 1))
_lo2, _hi2 = 0.0, 1.0
for _ in range(200):
    _mid = 0.5 * (_lo2 + _hi2)
    _v = (-0.6 * _mid + 0.8) / _math.sqrt(_mid * _mid + 1) - 0.7
    if _v > 0:
        _lo2 = _mid
    else:
        _hi2 = _mid
_u = 0.5 * (_lo2 + _hi2)
_xE = (-_u / _math.sqrt(_u * _u + 1), 1 / _math.sqrt(_u * _u + 1))
_sA = 0.6 * _xA[0] + 0.8 * _xA[1]
_sE = 0.6 * _xE[0] + 0.8 * _xE[1]
print("D5a gozlem: sA=%.17g sE=%.17g sA-0.7=%.3e sE-0.7=%.3e fark=%.3e"
      % (_sA, _sE, _sA - 0.7, _sE - 0.7, _sA - _sE))
check("D5a.yaklasik-tutar", abs(_sA - 0.7) < 1e-9 and abs(_sE - 0.7) < 1e-9,
      "1e-9 toleransla yaklasik esitlik")
check("D5a.tam-degil", (_sA - 0.7) != 0.0 and (_sE - 0.7) != 0.0,
      "'exact' iddiasi float gozlemle bile tutmaz")
check("D5a.belge.exact-tie", "Exact cross-pattern tie" in rep_lines[110],
      "REPORT.md:111: %s" % rep_lines[110].strip()[:60])
check("D5b.belge.iki-bagimsiz", "independent routes" in rep_lines[19],
      "REPORT.md:20: %s" % rep_lines[19].strip()[:70])
_vfull = "\n".join(ver_lines)
check("D5b.tek-dosya-tek-yazar", "Route 1" in _vfull and "Route 2" in _vfull,
      "iki 'route' ayni verify.py dosyasinda: bagimsiz denetim degil")
check("D5c.belge.equal-relevance", "equal relevance" in rep_lines[112],
      "REPORT.md:113: %s" % rep_lines[112].strip()[:60])

print("== D6: 1e-12 gevsekligi sertifika degil + kesin top-3 sertifikasi ==")
print("BASARISIZLIK KOSULU D6: rasyonel kutu esitsizliklerinden biri bozulursa /")
print("  kesin ayrisma 252/255>222/255 tutmazsa / belgede 1e-12 alintisi yoksa FAIL.")
check("D6.belge.K-HALF", "1e-12" in ver_lines[320], "verify.py:321: %s" % ver_lines[320].strip()[:70])
check("D6.belge.R133", "1e" in rep_lines[133].replace("−", "-"), "REPORT.md:134: %s" % rep_lines[133].strip()[:60])
# Kesin sertifika: u=1 (q=c) icin cap [rho,rho]; kutu atamasi kareli rasyonel esitsizliklerle.
# d1..d6 icin S=ham-toplam, Q=ham-kare-norm; rho^2=S^2/(4Q).
_cert = [("d1", Fr(2), Fr(1), 255, None), ("d2", Fr(2), Fr(201, 200), 255, None),
         ("d3", Fr(2), Fr(51, 50), 254, None), ("d4", Fr(1), Fr(1), 191, None),
         ("d5", Fr(2), Fr(2), 218, None), ("d6", Fr(3), Fr(3), 238, None)]
for nm, S, Q, m, _ in _cert:
    R = S * S / (4 * Q)
    if m == 255:
        lo2 = Fr(254, 255) * Fr(254, 255)
        check("D6.kutu.%s" % nm, lo2 < R <= 1, "rho^2=%s > (254/255)^2" % R)
    else:
        a, b = Fr(2 * m - 1, 255) - 1, Fr(2 * m + 1, 255) - 1
        check("D6.kutu.%s" % nm, a * a < R < b * b, "rho^2=%s in (%s^2,%s^2)" % (R, a, b))
    r0 = Fr(2 * m, 255) - 1
    L, U = r0 - Fr(1, 255), r0 + Fr(1, 255)
    check("D6.sert-kap.%s" % nm, L <= U, "m=%d kesin cert=[%s,%s]" % (m, L, U))
_Ls = [Fr(2 * m, 255) - 1 - Fr(1, 255) for _, _, _, m, _ in _cert]
_Us = [Fr(2 * m, 255) - 1 + Fr(1, 255) for _, _, _, m, _ in _cert]
check("D6.ayrisma", min(_Ls[:3]) > max(_Us[3:]),
      "min L123=%s > max U456=%s, fark=%s" % (min(_Ls[:3]), max(_Us[3:]), min(_Ls[:3]) - max(_Us[3:])))
check("D6.marj-tolerans-disi", min(_Ls[:3]) - max(_Us[3:]) > Fr(1, 10**9),
      "marj 1e-12 toleransin cok ustunde")
# d4 ozel: rho=1/2 tam rasyonel, m=191 kutusunda.
check("D6.d4-tam", Fr(1, 2) > Fr(126, 255) and Fr(1, 2) < Fr(128, 255), "1/2 in (126/255,128/255)")

print("== D7: d=4 yuk tasiyici israf muhasebesi (191/256 kod bos) ==")
print("BASARISIZLIK KOSULU D7: m(0.5)!=191 ya da m(1)!=255 ise / bir k icin tanik")
print("  rho [0.5,1] disinda kalirsa ya da kutusu tutmazsa / sayi 191 cikmazsa FAIL.")


def m_of(rho):
    # Kesin: y=(rho+1)*255/2 rasyonel, bag disi degerde klasik yuvarlama.
    y = (Fr(rho) + 1) * Fr(255, 2)
    q, r = divmod(y.numerator, y.denominator)
    return int(q) + (1 if 2 * r > y.denominator else 0)


check("D7.uc-alt", m_of(0.5) == 191, "m(0.5)=191 (191.25 asagi yuvarlanir)")
check("D7.uc-ust", m_of(1.0) == 255, "m(1)=255")
for k in range(191, 256):
    if k == 191:
        rk = Fr(1, 2)
    else:
        rk = Fr(2 * k, 255) - 1
    inrange = Fr(1, 2) <= rk <= 1
    y = (rk + 1) * Fr(255, 2)
    binok = (abs(y - k) < Fr(1, 2)) if k == 191 else (y == k)
    check("D7.kod-kullanilir.%d" % k, inrange and binok, "tanik rho=%s y=%s" % (rk, y))
check("D7.kullanilmayan-sayisi", 256 - (255 - 191 + 1) == 191, "191/256 = %.1f%% bos" % (191 / 256 * 100))
# Daginik iddia: ayni baytin baska harcamasiyla kiyas YOK (belgede kiyas aranir, bulunmamali).
check("D7.belge.kiyas-yok", "benchmark-codec" in rep_lines[136] or "no byte-storage" in rep_lines[136],
      "REPORT.md:137 kiyas-disi biraktigini soyler: %s" % rep_lines[136].strip()[:60])

print("----")
print("%d/%d checks passed" % (N_PASS, N_TOT))
sys.exit(0 if N_PASS == N_TOT else 1)
