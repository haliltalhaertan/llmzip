# LLMZIP — 15–16 Eylül 2026 bulgu arşivi

[LOCAL EXPLORATORY PILOT] [NOT PREREGISTERED] [NOT FOR CITATION] [DISCLOSE-BEFORE-USE]

## Kayıt durumu

**Drive: TAM. GitHub: ENVENTER VE DOĞRULAMA KAYDI; dosyaların tam kopyası değil.**

28 özgün dosyanın tamamı Google Drive'a ayrı ayrı, ayrıca tek birleşik ZIP içinde byte-değişmeden yüklendi. Birleşik ZIP geri indirildi; içindeki 28 dosyanın SHA-256 ve boyutları özgünlerle eşleşti. Ayrı yüklenen 28 dosya da geri indirildi ve aynı şekilde doğrulandı. Dokuz deney ZIP paketinin CRC kontrolü geçti; içlerinde toplam 1.170 dosya girdisi envanterlendi. Bu kontrol deneyleri yeniden çalıştırmaz veya bilimsel iddiaları onaylamaz.

Bu GitHub dizini tam 45,58 MB özgün veri kopyası değildir. Bağlantı üzerinden dosya-yolu tabanlı ikili paket yükleme yolu bulunamadı; yerel git ağ denemesi `Could not resolve host: github.com` hatası verdi. Bu nedenle asıl raporlar, kod/ham-sonuç ZIP'leri ve JSON dosyaları Drive'dadır. Eksiklik açıkça kayıtlıdır; depo envanteri, Drive payload'ı yerine geçirilmez.

## Erişim

- [Drive arşiv klasörü](https://drive.google.com/drive/folders/1eTS7HjgmRF5Cg4Lumlo0QYfucHG2BCbE)
- [Bütün özgün dosyalar: birleşik ZIP](https://drive.google.com/file/d/17wX4aScWOOM_p3duhXvThtC1F9GQRbir/view)
- [Son kısıtlı ceza deneyinin raporu](https://drive.google.com/file/d/1AYOmRbSjEHdfZQza3M_CtVAG1XLULyFK/view)
- [Tüm dosyaların envanteri, boyutları ve SHA-256 değerleri](ARCHIVE_INDEX.json)

ARCHIVE_INDEX.json her özgün dosyanın Drive kimliğini içerir. Dosya bağlantısı biçimi `https://drive.google.com/file/d/<drive_id>/view` şeklindedir. Drive erişim izinleri değiştirilmedi.

## Kapsam

13 Markdown belge, 6 JSON sonuç/koordinat dosyası, 9 ZIP deney paketi. Paketler yeniden benchmark, hata yeri, hız ve veri aktarımı, denetim karşı incelemesi, literatür ek hesapları, özgün metinle yeniden sıralama, nadirlik matematiği, toplamsal ceza kontrolü ve kısıtlı ceza pilotunu içerir. Gelen üç diğer-sohbet denetim/literatür metni ve ilk HANDOFF da tarihsel kaynak olarak korundu.

Eski büyük ham veri yedekleri yeniden çoğaltılmadı. Bu sohbette dosya olarak bulunmayan, yalnız metinde adı geçen diğer-sohbet deneyleri mevcutmuş gibi eklenmedi.

## Okuma ve sürüm uyarısı

Son deney için LLMZIP_KISITLI_CEZA_RAPORU_2026-09-16.md ile başlayın; MATEMATIK_INCELEME.md ve KONTROL_VE_DENEY_EKI.md adayın türetimini ve risklerini içerir. Eski raporları sonraki düzeltmelerle birlikte okuyun. HANDOFF ve gelen notlar yanlışlanmış/tartışılmış yorumlar içerebilir; arşivlenmeleri bu yorumları onaylamaz. Hiçbir bilimsel içerik değiştirilmedi veya yeni teyit statüsü verilmedi.

## Depo sınırı

Başlangıç main: `59b891efda7b6c06f44da7fa0ae4fe3c13f79a2e`. Yeni dal: `archive/findings-2026-09-16-session`. Yalnız bu yeni namespace'e ekleme; main'e yazma, merge, eski ankraj/dondurulmuş görev değişikliği veya Task4F1/BEAM çalıştırma yok.

## SHA-256 ile geri kontrol

Birleşik ZIP: 45.402.141 bayt.

```text
f8bd13f4798b27a7bc5ef27dce98d25ddf39d04d6fb31d910c66c27ce209ea74
```

ZIP'i açınca içindeki `python verify_archive.py` komutu 28 özgün dosyanın boyutunu ve SHA-256 değerini doğrular; arşivlenmiş deney kodunu çalıştırmaz.
