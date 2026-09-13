# AUDIT-1 — bağımsız denetim kapsamı (kullanıcı talebi: "şüphelendiğin şeyleri muse denetlesin")

**[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]**

**Tarih:** 2026-09-13 · [LOCAL] · Denetçi: bağımsız Muse oturumu (read-only /mnt/c, /tmp/audit1).

## Denetlenen şüpheler
1. **S1 — "+10pp" karışımı:** native = centering+sign; float96'nın donmuş tanımı hiç yeniden
   türetilmedi. Eğer float96 centering'siz ise +10pp = (centering kazancı) + (binarizasyon
   kazancı) toplamıdır ve atıf belgelenmemiştir. → Ayrıştırma: float(Y), float(C), sign(Y),
   sign(C) dörtlüsü ile pay dağılımı.
2. **S2 — Tie-konvansiyonu duyarlılığı:** 20 çekiliş/beklenen FR kuralı alternatiflere karşı
   test edilmedi. → pesimist (a+t≤2), beklenen (a≤2), optimist (a≤2) konvansiyonlarında
   native vs en iyi rakip farkları; yarış hükmü (LME +1.67 MID / LoCoMo +0.11 MID) sağlam mı?
3. **S3 — Çapa provenansı:** native/float96/ITQ/Haar/−15.9pp sayılarının donmuş kaynak
   dosya+satır izleri.

## Beklenen çıktılar
- `/tmp/audit1/report.md` + `audit1_details.json` (Muse) →
  denetçi bitince `audit_2026-09-13/audit1/` altına kopyalanacak.
- Sonuç ne olursa olsun: bulgu güncelleme geçişi (rapor dile/etiket düzeltmeleri tek seferde).

## Durum
- [x] Muse oturumu başlatıldı (proc_47ddeea6f2cd, 13:37)
- [!] **13:50'de dış kaynaklı SIGTERM ile öldürüldü** (exit −15; B3B ile eşzamanlı). Task B
  (ayrıştırma) TAMAM → **S1 şüphesi TEMİZ:** centering +0.149pp, binarization +10.038pp;
  toplam +10.187pp; +10pp'nin ~tamamı binarizasyon (float96 zaten CENTERED çıktı).
  Task C kısmi (sentetik makine doğrulaması + SIGN/ITQ sınır-tie istatistikleri).
- [x] **AUDIT1-CONT ✅ TAMAMLANDI (14:05)** — Task C-real + Task D + rapor bitti.
- [x] Sonuç toplandı + kopyalandı → `audit_2026-09-13/audit1_cont/`
- [~] Dil güncelleme geçişi: dış-prompt v1.1 güncellendi; kalan rapor dili tek geçişte (bekliyor)
- **SONUÇ:** Yarış hükümleri pesimist tie'da da ayakta (LME +1.369 / LoCoMo +0.089pp; monotone
  pess<exp<opt; MID). Task D: TÜM çapalar dosya+satır izli. Rekonstrüksiyon bit-birebir.
- Kanıt: /tmp/audit1 + kopya `audit_2026-09-13/audit1/` (taskB_numbers.json, taskC_*.json, ties.py)
