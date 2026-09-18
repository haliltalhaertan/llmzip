[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

# Soru parçalama pilotu — mekanizma testi

`evidence_path`: `audit_hard_r4/HINT_SELECTION_PILOT.json`, `hint_selection_pilot.py`
`audit_hard_r4/DECOMPOSITION_PILOT.json` (geçersiz ilk deneme, kayıt için saklandı)

**Dar araştırma sorusu:** Çoklu-gold LME sorularında, ilk erişilebilir kanıt + soru verildiğinde,
eksik ikinci kanıtı bulacak sorgu üretilebilir mi?

**Uygun küme (sıfır tokenla belirlendi):** 86 sorgu — çoklu gold **ve** en az bir gold erişilebilir
**ve** en az bir gold top-10 dışında. Toplam 154 eksik gold.
Bölümler: multi-session 54, temporal-reasoning 19, knowledge-update 9, preference 4.

---

## Önce: bir tasarım varsayımı çöktü

İlk pilot koşuldu ve **geçersiz** çıktı: üretilen "takip sorguları" `0.63`, `0.61`, `0.7` gibi
sayılardı — metin değil.

Sebep API'nin yapısında: **Jev/TypeSafe yalnız yargı primitifleri sunuyor** —
`Noul` (evet/hayır), `Choice` (etiket seçimi), `Score` (sıralı). **Serbest metin üretmiyor.**

> **Bu, hattın literal biçimini imkânsız kılıyor.** *"Jev'e takip sorgusu ürettir"* bu modelle
> yapılamaz. Bir üretici model (LLM) gerekir; Jev onun yerine geçemez.

Bu bir başarısızlık değil, **kapsam bulgusu**: önerilen mimarinin bir bileşeni mevcut araç
kümesinde yok. Kaydedildi, sonra mekanizma **seçim görevi** olarak yeniden kuruldu:

> Çapadan aday varlıklar çıkar → Jev'e sor: *"bu varlık, sorunun ihtiyaç duyduğu ama kanıtın
> çözmediği bağlantı mı?"* → en yüksek skorlu varlıkla ikinci arama.

Bu, M2'den farklı: M2 çapanın **tüm** yüksek-IDF kelimelerini ekler (kör); bu kol Jev'in
seçtiği **tek** varlığı kullanır (seçici).

---

## Sonuç: mekanizma çalışıyor, ama körü yenemiyor

| kol | en az bir eksik gold | recall |
|---|---:|---:|
| taban (soru) | 4,65% | 3,49% |
| **M2 kör sözlüksel** | **22,09%** | **14,96%** |
| Jev seçili varlık | 16,28% | 12,50% |

| karşılaştırma | Δ | CI95 | |
|---|---:|---|---|
| Jev − taban | **+11,63** | [+3,49, +19,77] | **SIG** |
| M2 − taban | **+17,44** | [+9,30, +26,74] | **SIG** |
| **Jev − M2** | −5,81 | [−15,12, +3,49] | ayırt edilemez |

**İki sonuç birden:**

1. **Anlamsal seçim gerçekten çalışıyor** — tabana göre +11,63 pp, anlamlı. Jev, çapadaki
   çözülmemiş bağlantıyı bulabiliyor.
2. **Ama kör sözlüksel genişletmeyi geçemiyor.** Fark −5,81 pp, ayırt edilemez. 344K token
   harcayıp sıfır ek değer.

Örnek seçimler: `protector` (0,82), `boots` (0,74), `went` (0,60), `got` (0,24) — bazıları
anlamlı, bazıları işlev kelimesi.

---

## Ve görünüşte bir çelişki — çözüldü

Bu pilotta M2 **+17,44 pp kazanıyor**. L-112'de aynı M2 uçtan uca **−6,43 pp kaybediyordu**.

**Aynı mekanizma, zıt işaret.** Sebep:

| | bu pilot | L-112 |
|---|---|---|
| metrik | eksik-gold recall@10 | nihai FR@3 (top-3) |
| çapa | skordan çıkarıldı | cevaba dahil |
| küme | 86 zor vaka | 470 sorgunun tamamı |

Kontrol ettim: **aynı 86 vakada** L-112 uçtan uca 28,20 → 23,86, yani **−4,34 pp**.

> **Yani M2 eksik ikinci kanıtı bulmakta gerçekten yardımcı, ama nihai top-3'ü bozuyor** —
> zaten bulunmuş gold'ları dışarı itiyor. Kazanç ve zarar aynı mekanizmanın iki yüzü.

Bu, senin formüle ettiğin dersin ikinci kez doğrulanması:

> **Ara metrik iyileşmesi, uçtan uca iyileşme değildir.**

Üstelik bu sefer **pozitif** yönde yanıltıyor: ara metriğe baksak "M2 harika" derdik.

---

## Ne kapandı, ne kapanmadı

**Kapandı:**
- *"Jev'e takip sorgusu ürettir"* — **araç düzeyinde imkânsız** (yargı API'si, üretici değil)
- *"Jev'in seçtiği varlıkla ikinci arama"* — çalışıyor ama kör genişletmeyi **geçmiyor**

**Kapanmadı:**

| | durum |
|---|---|
| Üretici bir LLM ile gerçek soru parçalama | **denenmedi** — Jev bunu yapamıyor, ayrı model gerekir |
| Kazancı koruyup zararı engelleyen **birleştirme** (iki turun sonuçlarını ayrı slotlara) | ölçülmedi |
| Çapa **vektörüyle** komşu arama | ölçülmedi |
| Koşullu ikinci tur | ölçülmedi |

**En umut verici kalan:** bu pilot gösterdi ki ikinci tur **gerçekten yeni gold buluyor**
(%4,65 → %22,09). Sorun bulmakta değil, **birleştirmede** — ikinci turun sonucu birinci turun
sonucunu eziyor. İki turu ayrı slotlarda tutan bir birleştirme henüz denenmedi.

---

## Maliyet ve sınırlar

- 688 aday yargısı, **343.608 token**, 33 s, 0 hata
- Yalnız sözlüksel ikinci arama; `sign96` tarafı **ölçülemez** (kodlayıcı saklanmamış)
- n=86, tek veri kümesi, **ayrılmış sınav verisi yok**
- Aday çıkarma basit: yüksek-IDF, soruda geçmeyen terimler. Gerçek varlık tanıma denenmedi
