# Sunum sabahı — 14 Eyl, 10:00 (deneme sunumu, 3 dk, tek sunucu)

Format organizatörden: yalnız **Proje Adı · Problem · Çözüm · Ekip**. Deste: `docs/sunum/OtoHesap-3dk.pptx` (4 slayt; canlı demo "Çözüm" slaydından sonra). Akış: `docs/sunum/3-dakika-akis.md` (Notion'da da var).

## Sunum laptopunda, sırayla (≈25 dk)
1. `cd ~/code/Oto-Hesap && git pull` (sabah push'lanan düzeltmeler).
2. `.env`: Ömer'in DM'lediği Neon `DATABASE_URL` / `DATABASE_URL_RO`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID`, `NOTIFY_DRY_RUN=false`. LLM anahtarı varsa `LLM_PROVIDER=gemini|groq` + anahtar; yoksa `fake` kalır (çipler önbellekten çalışır, serbest soru sorma).
3. `make doctor` → kırmızı yoksa devam.
4. Terminal 1: `make api` · Terminal 2: `make web-prod` (ilk derleme ~1 dk).
5. `make demo` → veriyi sıfırlar, açık siparişleri temizler, ısıtır, kontrol listesini basar. **Neon paylaşımlıysa bunu yalnız sunucu koşar.**
6. Tarayıcıda 4 sekme: `/` · `/asistan` · `/tedarik` · `/stok`. Telefonda Telegram sohbeti açık, ses açık.
7. Akışı bir kez kronometreyle sür (hedef ≤ 2:50). Sonra tekrar `make demo` (temiz başlangıç).

## Yedekler
- Wi-Fi yok → hotspot. LLM yok → çipler önbellekten. Telegram yok → "Gönderildi (simülasyon)" rozeti + 90 sn video (`docs/sunum/video-senaryosu.md`; kayıt yoksa ekran görüntüleri `docs/img/`).
- Uygulama açılmazsa → `make doctor` çıktısını gruba yaz.

## Söylenecek üç cümle (jüri sorarsa)
- "LLM yalnız sorguyu yazar; rakamı veritabanı verir; siparişi insan onaylar."
- "Veritabanına yalnız okuma yetkisiyle gidiyoruz, sorgu ekranda görünüyor."
- "Veri sentetik; Trendyol, e-belge ve çok kiracılı sürüm yol haritasında."
