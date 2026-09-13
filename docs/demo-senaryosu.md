# Demo senaryosu (TEK GERÇEK KAYNAK) — sahibi: Ömer

> **Deneme sunumu 14 Eyl: 3 dakika, tek sunucu → `docs/sunum/3-dakika-akis.md` esastır.** Aşağıdaki 5 dakikalık sürüm 16 Eyl finali içindir.

Toplam 5 dk. Sürücü: Ömer. Anlatıcı: Kutay. Telefon: Ömer'in (Telegram sohbeti açık, ses açık). Sunumdan 10 dk önce: `python data/seed.py --reset`, `/api/health` ısıtma, tarayıcıda 5 sekme açık.

| # | Süre | Ekran | Tıklama | Söylenen cümle | Beklenen sonuç |
|---|------|-------|---------|----------------|----------------|
| 1 | 0:00–0:30 | Genel Bakış | — | "Bu ekran her açılışta veriden hesaplanır: gelir, gider, fark, kritik stok." | 4 KPI, aylık çubuk (Nis–Eyl), gider pastası, "son güncelleme" damgası |
| 2 | 0:30–1:15 | Kayıtlar → Gider ekle | Ekle → kategori: reklam, tutar: 4.500, kaydet → Genel Bakış | "Bir gider giriyoruz; pano anında güncellendi." | Gider KPI +4.500, pastada reklam payı büyüdü |
| 3 | 1:15–2:15 | Asistan | Çip: "En çok kazancım hangi üründen?" → Sorguyu gör (3 sn) | "Soru SQL'e çevrildi, veritabanında çalıştı, yanıt gerçek veriden. Asistan yalnız okur." | Yanıt: powerbank + rakam; SQL bloğu; "Kaynak: satışlar, ürünler · <saat>" |
| 4 | 2:15–2:45 | Asistan | Çip: "Bu ay toplam giderim ne kadar?" | "Az önce girdiğimiz gider yanıta dahil." | Rakam = seed bu ay + 4.500 |
| 5 | 2:45–3:15 | Stok | — | "İki ürün kritik seviyede." | 2 satır kırmızı |
| 6 | 3:15–4:15 | Tedarik | Şimdi kontrol et → 2 taslak → Onayla (ilk taslak) | "Ajan taslağı hazırladı; miktar hedef stoğa göre. Onay bizde." → telefonu jüriye çevir | Telefonda Telegram mesajı; kart "Gönderildi <saat>"; Stok'ta "sipariş yolda" rozeti |
| 7 | 4:15–5:00 | Tampon | — | Soru varsa cevapla; yoksa "Yol haritasına geçelim." | — |

**Kesinlikle:** çipler dışında soru yazılmaz · onay tuşuna bir kez basılır · internet düşerse asistan önbellekten yanıtlar (cached rozeti görünse de sorun değil) · her şey düşerse USB'deki 3 dk video.

**Kontrol listesi (sunumdan 30 dk önce):** seed reset ✓ · health ✓ · canlı link ✓ · Telegram test mesajı ✓ · telefon şarj ✓ · kronometre ✓ · yedek video ✓ · slaytlar PowerPoint ✓
