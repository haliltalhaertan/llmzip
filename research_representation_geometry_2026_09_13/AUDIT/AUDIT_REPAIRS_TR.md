[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]
# Bağımsız Karşıt Denetim Raporu — dört onarım paketi

Yöntem: yeniden-türetme + yeniden-koşma. Yeniden okunan hiçbir iddia doğrulanmış sayılmadı.
Karar gereken her hesap `fractions.Fraction` ile, tek iş parçacığı, baytkod kapalı.
Dondurulmuş arşive ve denetlenen paketlere yazılmadı.

## Yönetişim

- Dondurulmuş arşiv bayt-değişmez: HEAD = `1021083d4f2faebda760546e1217b4de1eef87ea`,
  `git diff 1021083 -- round4/...` boş, `git status` temiz. DOĞRULANDI.
- Etiketler: 13 `.md` dosyasının ilk satırı doğru; 10 `.py` dosyasının tamamında
  etiket yorum içinde ve tamamı `SyntaxError`-sız (`ast.parse` + koşma ile). DOĞRULANDI.
- "Bağımsız denetimden geçmedi" beyanı dört pakette de var. DOĞRULANDI.
- Katkısallık: dondurulmuş dizinde yazma yok; `verify_orig.py`,
  `verify_orig_copy.py`, `orig_verify_snapshot.py` dondurulmuşla `diff`-temiz. DOĞRULANDI.
- Supersedes satır numaraları: norm_math (8/8), norm_tests (11/11), rank_cert (6/6)
  dondurulmuş satırlarla birebir eşleşti. rank_cover supersedes tablosu ise
  özgün `dosya:satır` vermiyor (BULGU-4).

## norm_math: DÜZELTMELER DOĞRU

Çekirdek sınır sıfırdan yeniden ispatlandı: birim `q,x`, birim `c` için
`q·x = u·ρ + q⊥·x⊥`, `|q⊥·x⊥| ≤ √(1−u²)√(1−ρ²)` (C-S, `c⊥` uzayında). Doğru.

- D1 (yüz kuralı): ispat yeniden türetildi. `m<0` tek-eksen argümanı
  (`Σz≥‖z‖`, çoklu destek `Σz>1`) sağlam; `m=0` yüz karakterizasyonu
  (`N⊆J`) iki yönlü doğru. Tanık `q=(0,0,−1)`, `x=(−3/5,−4/5,0)`: birim,
  `F(s)` içinde, skor 0 = m; iki iyileştirici eksen de dışarıda. Özgün kural
  burada `False`, doğrusu `True`. `proofs_exact.py` 478/478 yeniden koştu, geçti.
- D2 (d=2 tablosu): sekiz hücre bağımsız yeniden hesaplandı; düzeltilmiş
  tablo (T,T / F,T / F,T / F,T) ve dört yanlış bayrak iddiası doğru.
  Kodun bu 8 hücrede düzeltilmişle uyumlu olduğu (kusurun yalnızca REPORT
  düzyazısında olduğu) doğrulandı.
- D3 (ρ lemması): `sᵢxᵢ=|xᵢ|` (sıfır yüzü dahil), `ρ=‖x‖₁/√d ∈ [1/√d,1]`
  yeniden ispatlandı. `ρ=−0.3/0/−1` imkânsız. Soyut `(u,ρ)` matematiğinin
  geçerli kaldığı notu kapsamı doğru çiziyor.
- D4 (`[0.5,1]`): `e₁` skoru 1/2, `F` içinde; kapalı uç doğru.
- D5 (üç geri çekme): (a) skorlar `0.70000000000000007`, fark `1.1e-16` —
  yeniden ölçüldü, "exact" geri çekmesi haklı; (b) iki route aynı dosyada —
  haklı; (c) "equal relevance" desteksiz — haklı. Gereksiz geri çekme yok.
  Uyarı: "new assembly" (REPORT §5 başlığı) ile v2 `sup_independent`
  adlandırması arasındaki terminoloji gerilimi için BULGU-7.
- D6 (kesin top-3): altı `ρ²` değeri belge vektörlerinden bağımsız
  yeniden hesaplandı (`200/201`, `50/51` dahil); kutu eşitsizlikleri ve
  `252/255 > 222/255` (fark `30/255`) tuttu. Sertifikasız kalanlar dürüst listeli.
- D7 (191/256 boş): `m(0.5)=191`, `m(1)=255`, 65 kutunun tanıkları tuttu.

## norm_tests: SAYIM VE T5 DOĞRU, İKİ BELGE KUSURU

- Yeniden koşma: `verify_v2.py` 5791/5791 (çıkış 0), orijinal 272/272.
  Ayrışım veriden doğrulandı: B2 131, D 8, T1 15, T2 51, T3 51, T4 7,
  T5 5443 (= 2716×2 + 11), T6 8; `272−56+124+5443+8 = 5791`. Gönderilen
  `results.json` ile yeniden koşma isim-isim aynı.
- T5 indirgemesi sıfırdan türetildi: `t−uρ = (d·QX−S1·Sq)/(d√(Q2X2))`,
  kare alma `D≥0` olduğundan eşdeğer; `Bq,Bx≥0`, C-S farkı
  (`(1/2)Σ(qᵢsⱼ−qⱼsᵢ)²` kimliği doğrulandı). Görevdeki indirgeme DOĞRU.
- Kapsama veriden doğrulandı: 2716 vaka; işaret neg 1180 / pos 1129 / zero 407;
  `|u|=1`: 142; `u<−0.9`: 252; her `d` için `min ρ²=1/d`, `max=1`;
  sıfır-koordinat one 729 / multi 193 / face 52. Dokümandaki her sayı tuttu.
- Kırık-sınır deneyi yeniden koştu: 592/2716 red; red kümesi = tam-eşitlik
  kümesi (iki yönde de 0 uyumsuzluk). En sıkı katısız bağıl boşluk `3/2212`,
  mutlak `3/2500` (`c1046-near1-d3`) — ikisi de vektörleriyle doğrulandı.
- Eşitlik tanığı el ile: `q=(0,1/5)`, `x=(1/5,0)`, d=2 için
  `A=−1/25`, `lhs=1/625`, `Bq=Bx=1/25`, `rhs=1/625`. İki yan da `1/625`.
  `T5_EVIDENCE.md:73` buraya `1/2500` yazmış — 4 kat hatalı (BULGU-2).
- `T5.exact-consistency` yalnızca `rejects ≥ n_exact` kilitliyor; prosa
  "reddedilen == tam-eşitlik ... bunu kilitler" diyor. Olgu doğru (kümeler
  eşit), kilit zayıf (BULGU-3).
- Açık boşluklar gerçekten açık: float nicem sertifikası ve `C.tie`
  ikili-arama için yeni zayıf test uydurulmamış; korunan `C.tie`/`E`
  kontrolleri orijinalle aynı (1'er adet). Kapatılmış gibi gösterilme yok.
- Yapısal not: d=2'de `s⊥` tek boyutlu olduğundan C-S her zaman eşitliktir;
  523 d=2 vakasının tamamı slack-0. 592 kesin-eşitliğin 399'u bu yapısal
  kaynaktan. Deney geçerli ama bileşim açıklanmamış (BULGU-6).

## rank_cert: ÖLÇÜMLER ÜRÜYOR, YORDAM YANLIŞ BELGELİYOR

- Mutasyon deneyi bağımsız yeniden kuruldu ve birebir üredi: bozuk `cA`da
  özgün süit 49/49 GEÇTİ (çıkış 0); v2 süiti aynı mutasyonda 4 kontrolde
  kaldı (`S8-cA-status/direction`, `S8-cB-status/direction`, çıkış 1).
  Daha keskin varyant (mutasyonlu v2 yordamı): yalnızca 2 `cA` hatası. Başlık doğru.
- Çözünürlük yeniden ölçüldü, her sayı tuttu: yapay 1/6→0; fuzz n=2000,
  eff=1759, orig 649 → ayrıştırıcı 6 → v2 0; `agree_viol=0`, `mono_viol=0`,
  `valid_fail=0`. `cB` ayrıştırıcı+yakalama yoluyla (`cross` braketi, uç
  savları −1/+1) sağlam çözülüyor; brakette kesin-rasyonel kök yok.
- S7 totoloji onarımı doğru: koşulsuz `found11 is None`; tanık-zorlamalı
  doğruluk tablosu (eski GEÇER / yeni KALIR) doğrulandı.
- SAĞLAMLIK DELİĞİ (BULGU-1, YÜRÜTMEYLE İSPATLI): `certify_v2` YANLIŞ
  belge üretebiliyor. Girdi `p=(−100,100,0,10000)`, `q=(−200,200,70000,0)`,
  J=[1,4]: gerçek `+1` (1,7/4) aralığında, `−1` (7/4,4) aralığında, bağlar
  1 ve 7/4'te — yani VARIES. v2 `ISOLATED_TIES`, yön `−1` döndürüyor:
  "(1,7/4)'te `f1<f2`" iddiası YANLIŞ. Ölçeklenmemiş ikizde (kökler önceden
  kesme yapılınca) v2 doğru VARIES veriyor; özgün yordam dürüstçe UNRESOLVED
  bırakıyor. Kök neden: `isolate_roots` kesin-vuruş (`exact`) kökleri
  kesişim/teğet diye sınıflandırmıyor; `n_cross` yalnızca braketleri sayıyor;
  `rational_roots` bütçe-aşımında (`skipped=True`) rasyonel kök ön-kesme
  yapılmıyor ve uç-bağ maskelemesiyle birleşince yön kayboluyor. Raporlanan
  ölçümler etkilenmiyor (fuzz'da 0/2000 skip; `cB`'de exact yok) ama
  "yanlış şeyi asla belgelemez" sözü YANLIŞ. Ayrıca `validate_cert` bu
  sahte belgeyi GEÇİRİYOR (BULGU-5).

## rank_cover: İSPATLAR SAĞLAM, YÖNETİŞİM EKSİK

- `coverage_v2.py` 48/48, `realizable_tangent.py` 12/12 yeniden koştu.
- Dal tablosu doğrulandı: DOMAIN_FAIL, deg1 (`P=4z` → STRICT −1), deg0
  (`P=−3` → STRICT −1), VARIES (S5), certify-PT (S2) kapsanıyor; taban
  S6 tekrarı gerçekten deg0/1 içermiyor; gömülü `*_orig` anlık kopyayla
  5/5 aynı sonucu veriyor.
- PT-ulaşılamazlık ispatı yeniden türetildi ve sağlam bulundu: PT ⇒ J'nin
  her noktasında bağ (sıfır-küme çakışması `N1=0⇔N2=0` + uç sürekliliği) ⇒
  5 topk adayı da bağlı ⇒ SAMPLE_TIED. 4000 fuzz denemesinde ulaşan girdi
  yok; PT içeren hedef kümelerin tamamı SAMPLE_TIED. Ulaşan girdi KURULAMADI.
- Sturm-None ulaşılamazlığı sağlam: sıfır polinom sturm öncesi ayrılıyor.
- Gerçeklenebilir teğet bağımsız türetildi: `qc=[1,1/2]`, `c1=[1,1]` →
  `a1=3/2`; `qg=[1/2]`, `g1=[2]` → `b1=1`, `u1=2`, `v1=4`; ikinci tuple
  `(1,0,1,0)`; `P=(3/2+z)²−(2+4z)=(z−1/2)²`; hüküm `[1,0,1]`. Paylaşımlı
  sorgu, G={2} tutarlı. S4'ün soyut-sadece (`u=0,a≠0`) sınıflandırması doğru.
- Kısıtlar (`u,v≥0`; `u=0⇒a=0`; `v=0⇒b=0`) gerekli; ℝ üzerinde tekli ve
  paylaşımlı-sorgu yeterlilik inşası (`Q≥max(Ai²/Ui)`, tamamlayıcı blok)
  doğrulandı. ℚ-sınırlaması ve sıfır-ortalama kapsam-dışılığı dürüstçe yazılı.
- Girdi retleri doğrulandı: L==R→EMPTY, L>R→INVERTED, L≤0→NONPOSITIVE_LEFT
  (öncelik: pozitiflik→boşluk→yön); özgün L==R'de sahte STRICT/yön-0,
  L>R'de sessiz takas üretiyor; geçerli aralıkta `fixed==orig`.
- Supersedes tablosu özgün `dosya:satır` vermiyor (BULGU-4). `TOPK-PT-line`
  izleyici hedefi toplanıp hiç sınanmıyor (ölü izleme, küçük).

## Kırma testleri (7/7 yakaladı)

B1 D1-yüz (bozuk tek-eksen `False` vs tanık `True`); B2 T2-altın
(bozuk izdüşürücü `16/25≠1`); B3 T5-kırık-sınır (592 red); B4 T5-ters-eşitsizlik
(1864 fail); B5 C3-bozuk-doğrulayıcı (4/4); B6 S7-zorlanmış-tanık (eski GEÇER,
yeni KALIR); S8-mutasyon (özgün kör, v2 yakalar). Kırılmaya dayanıklı kontrol yok.

## Aşırı iddia ve çalıştırılabilirlik

- "Novel" iddiası hiçbir pakette yok. "Certified" geçen yerler ya alıntılanan
  özgün terim ya durum-enum değeri. Tespit edilen abartı: BULGU-3'teki
  "kilitler" sözcüğü (kilit `≥`, iddia `==`).
- Çalıştığı iddia edilen her betik koştu: proofs_exact 478/478, norm
  `verify_v2` 5791/5791 + orig 272/272, rank `verify_v2` 53/53 + orig 49/49,
  `fuzz_rates` (6.7sn), `certify_v2` smoke, `coverage_v2` 48/48,
  `realizable_tangent` 12/12. Geçmişteki çıplak-etiket `SyntaxError` sınıfı
  hiçbir dosyada yok (10/10 `ast.parse` temiz).

## Kategori disiplini

- Cebirsel ispat: çekirdek sınır, D1 yüz kuralı, D3 ρ lemması, T5 indirgemesi,
  C-S negatif-olmazlık, PT/sturm ulaşılamazlıkları, gerçeklenebilirlik inşası.
- Sonlu tam doğrulama (kesin `Fraction`): proofs_exact 478, T5 2716 vaka,
  T1–T4/T6, C1/C3 48, teğet 12, fuzz 2000 (örneklem; ispat değil),
  agree/valid çapraz kontrolleri (örneklem; BULGU-5 kapsam notuyla).
- Sayısal gözlem (ispat değil, doğru etiketli): D5a float `1.1e-16`,
  `D.agree`/`worst_rank` 1e-12, `C.tie` 1e-9, BLAS uyum yoklaması.
- Bağımsız denetim (tam): YOK. Bu rapor kısmi karşıt denetimdir (aşağıya bak).
  Hiçbir paket bir kategoriyi diğeri gibi göstermiyor (BULGU-3'teki tek
  kilit/iddia uyumsuzluğu hariç).

## HÜKÜM

REQUEST_CHANGES

### BULGU-1 (BLOCKING, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_rank_cert/out/certify_v2.py:505-539` (özellikle 512-517,
  536-539: exact kökler kesişim/teğet ayrımına girmiyor).
- Yanlış: `p=(−100,100,0,10000)`, `q=(−200,200,70000,0)`, J=[1,4] için v2
  `ISOLATED_TIES`/yön `−1` belgeliyor; gerçekte (1,7/4) aralığında `+1`
  (ör. z=5/4 ve 3/2'de `cmp_rank=+1`). YANLIŞ BELGE.
- Kapatma: her `exact` kökün iki yanından örnekleyip kesişim/teğet
  sınıflandırması yap (veya alt-aralığı exact kökte bölüp iki yanı ayrı
  işlet); `n_cross`'a exact-kesişimleri kat; bu girdiyi regresyon testine ekle.

### BULGU-2 (P1, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_norm_tests/out/T5_EVIDENCE.md:73`.
- Yanlış: tanık `q=(0,1/5)`, `x=(1/5,0)` için `lhs=rhs=1/2500` yazıyor;
  doğrusu `1/625` (el hesabı + `t5_stats` çıktısı).
- Kapatma: `1/2500` → `1/625` düzelt.

### BULGU-3 (P1, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_norm_tests/out/T5_EVIDENCE.md:63-64` (iddia) vs
  `fix_norm_tests/out/verify_v2.py:950-951` (kilit `rejects ≥ n_exact`).
- Yanlış: "reddedilen == tam-eşitlik ... bunu kilitler" — kilit `≥`
  denetliyor, `==` değil. Olgu bugün doğru (kümeler eşit, 0 uyumsuzluk)
  ama gelecekteki sapmayı yakalamaz.
- Kapatma: ya kontrole `rejects == n_exact` + küme-eşitliği ekle ya da
  prosa `≥` diye düzelt.

### BULGU-4 (P1, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_rank_cover/out/COVERAGE_DISPOSITION_TR.md:4-14`.
- Yanlış: supersedes tablosu özgün `dosya:satır` vermiyor (kural: her
  yerine-geçme iddiası tam satır adlandırmalı). Diğer üç paket uyuyor.
- Kapatma: her satıra dondurulmuş `verify.py`/`REPORT.md` satır aralığı ekle.

### BULGU-5 (P2, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_rank_cert/out/fuzz_rates.py:74-114` (`validate_cert`).
- Yanlış: tek-yönlü `ISOLATED_TIES` belgesinde sıra örneklemesi yok;
  BULGU-1'in sahte belgesini `None` (geçer) ile geçiriyor. `valid_fail=0`
  bu delik sınıfını dışlamıyor.
- Kapatma: `ISOLATED_TIES` (tek yön) için de 17-nokta sıra taraması ekle
  veya `valid_fail=0` kapsam cümlesine bu körlüğü yaz.

### BULGU-6 (P2, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_norm_tests/out/T5_EVIDENCE.md:59-67`.
- Eksik: 592 kesin-eşitliğin 399'u d=2 yapısal eşitliği (`s⊥` tek boyutlu
  ⇒ C-S her zaman eşitlik; 523 d=2 vakasının tamamı slack-0). Kırık-sınır
  deneyinin bileşimi açıklanmamış. Deney geçerli, raporlama eksik.
- Kapatma: d=2 yapısal eşitliğini ve 399/193 bileşimini belgeye ekle.

### BULGU-7 (P2, ŞÜPHELİ/YORUM)

- Dosya: `fix_norm_tests/out/verify_v2.py:195,213` (`sup_independent`,
  `inf_independent` adları + "bağımsız kapalı-form/şahit" söylemi).
- Sorun: D5b aynı-dosyadaki ikinci hesap yoluna "independent" denmesini
  geri çektirdi; T2 aynı-dosya yeniden-gerçekleştirmesi için aynı sözcüğü
  kullanıyor. Hesap-yolu çeşitliliği gerçek (mutant öldürme ile ispatlı)
  ama sözcük geri çekmeyle gerilimli.
- Kapatma: "bağımsız" → "ayrı/çeşitli gerçekleştirme (denetim değil)" dili.

### BULGU-8 (P2, YÜRÜTMEYLE İSPATLI)

- Dosya: `fix_rank_cert/out/FAILS_ON_ORIGINAL.md:4,23,45` ve
  `fix_norm_tests/out/TEST_DISPOSITION_TR.md:72-76`.
- Eksik: mutasyon sürücüleri (`/tmp/mut_exp/mut_cA.py`, `driver_a/b/c/d.py`)
  paketlenmemiş; Deney 1–3 ve 340-gövde ham çıktıları paketten yeniden
  üretilemiyor. Bu denetim hepsini bağımsız yeniden kurup doğruladı
  (çıktılar birebir uydu) ama kanıt pakette durmuyor.
- Kapatma: sürücüleri pakete ekle veya "yeniden-kurulabilir, pakette yok" diye yaz.

## Bakmadıklarım (yok ile bulamadım arasındaki fark)

- Task4F1: mühürlü; corpus/sorgu/gold/sonuç erişimi, retrieval/recall/fit
  denenmedi. Yasak.
- Ağ/benchmark/literatür önceliği: bakılmadı. "Novel" diyen cümle yok;
  öncelik taraması da yok — çelişki yok, kanıt da yok.
- LME önbellek provenance: `15745da0.pkl` verili kabul edildi; ikili-kesin
  okuma aritmetiği doğrulandı, önbelleğin nasıl üretildiği denetlenmedi.
- Float/numpy yolları: yalnızca gözlem olarak yerinde bırakıldı; kapsamlı
  sayısal hata analizi yapılmadı (paketler de iddia etmiyor).
- 340-gövde `driver_a` ham koşması: sürücü pakette yok; aritmetik (216+124)
  ve grup koşmaları (15/51/51/7 hepsi geçti) ile tutarlılık doğrulandı,
  sürücünün kendisi koşturulamadı.
- "Bulamadım" diye kapatmadığım tek av: PT-topk ulaşan girdi (4000 fuzz +
  hedefli denemeler + ispat taraması) — ispat sağlam göründüğünden
  "yok" demeye en yakın olduğum madde, yine de sonlu tarama ispat değildir.

## Bağımsızlık sınırlaması

Bu paketleri üreten oturumlarla aynı model ailesindenim. O çalışmanın
belleğine ve muhakemesine erişimim yok; her şeyi sıfırdan türetip yeniden
koştum. Bu kısmi bağımsızlıktır, tam bağımsızlık DEĞİL. Tam bağımsız taraf
gibi sunulmuyorum; hükmüm aynı-aile karşıt denetimi olarak okunmalı.
