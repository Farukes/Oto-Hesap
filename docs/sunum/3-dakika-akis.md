# OtoHesap — 3 dakikalık sunum akışı (tek sunucu, deneme sunumu 14 Eyl)

> Sunucu telefonda/iPad'de bunu açık tutar. Emojiler = ne yapılacağı. Süre 3:00; 2:45'te bitir. Demo soruları yalnız çiplerden. Sunum bilgisayarında `make warmup` 10 dk önce koşulmuş, Telegram sohbeti telefonda açık, ses açık.

| Süre | 🎬 Cue | Ekranda | Söylenecek (kısa) |
|------|--------|---------|-------------------|
| 0:00–0:25 | 🎯 Aç | Kapak slaydı (tek slayt) veya doğrudan uygulama | "KOBİ sahibi Excel ile rapor kovalıyor, stok bitince geç fark ediyor. OtoHesap: gelir-gider panosu, Türkçe soruyla veriye erişim ve stok bitince **insan onaylı** sipariş mesajı. Bir günde, 4 kişi." |
| 0:25–0:55 | 📊 Genel Bakış | `/` — KPI'lar, aylık gelir–gider, Öngörü kartları | "Gelir, gider, fark; altı aylık akış. Sistem kendisi uyarıyor: **2 ürün kritik stokta**, reklam gideri %79 arttı." (Kartı işaret et.) |
| 0:55–1:40 | 💬 Asistan | `/asistan` → çip **"En çok kazancım hangi üründen?"** → yanıt → **Sorguyu gör** | "Soruyu Türkçe soruyoruz; model yalnız **SQL'i yazıyor**, rakam veritabanından geliyor, sorgu görünür ve veritabanı **yalnızca okunur**. Powerbank lider." (SQL'i 3 sn göster, kapat.) |
| 1:40–2:25 | 📦 Tedarik | `/tedarik` → **Şimdi kontrol et** → 2 taslak → **Onayla** → 📱 telefonu göster | "Kritik stok için ajan taslağı hazırladı: miktar hedef stoğa göre, tutar hesaplı. **Onay bizde.** Onaylıyorum… mesaj tedarikçinin telefonuna düştü." (Telefonu jüriye çevir.) |
| 2:25–2:50 | 🚀 Kapat | Uygulama veya kapanış slaydı | "Üç ilke: LLM sorguyu yazar, rakamı veritabanı verir, siparişi insan onaylar. Sırada: Trendyol sipariş akışı, e-belge entegratörü, çok kiracılı sürüm. Teşekkürler." |
| 2:50–3:00 | 🛟 Tampon | — | Soru gelirse tek cümle; gelmezse bitir. |

## Yedek planlar
- 🌐 Wi-Fi yok → telefon hotspot; LLM yok → asistan **önbellekten** yanıtlar (çipler çalışır); Telegram yok → "Gönderildi (simülasyon)" rozeti + 20 sn video.
- 🎥 Her şey düşerse: 90 sn video (Canva), aynı akış.

## Jüri sorarsa (tek cümlelik cevaplar)
- **Paraşüt'ten farkı?** "Onlar e-belge/banka katmanında güçlü; biz o verinin üstünde doğal dille soru ve onaylı aksiyon katmanıyız."
- **Yanlış SQL üretirse?** "Sorgu ayrıştırılıp beyaz listeden geçiyor, salt-okur rolle çalışıyor, süre ve satır sınırı var; SQL görünür."
- **AI kendi başına sipariş verir mi?** "Hayır; taslak → onay → gönderim; onaysız dış mesaj yok."
- **Neden yerel model / neden API?** "Adaptör arkasında; yerel Qwen da bulut model de aynı sözleşmeyle çalışıyor, veri sentetik."
- **Bunu bir günde mi?** "Kapsamı küçük tuttuk, yönetilen servisler, dosya sahipliği, yapay zekâ destekli paralel geliştirme."
