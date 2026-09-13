# Görev kartı — Kutay (dal: `kutay/web`)

## Nasıl başlarım (5 dakika)
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh
git checkout kutay/web
```
Sonra kendi yapay zeka aracına şu ilk mesajı at ve iki dosyayı yapıştır (`AGENTS.md` + bu kart):

> Aşağıda projenin AGENTS.md dosyası ve benim görev kartım var. Kurallara uy. Bilmediğin alan, model adı veya URL uydurma; `TODO(kutay)` bırak ve sor. Önce 5 maddelik plan ver; onaylayınca küçük adımlarla uygula, her adımda testi koştur. İlk işim: Ekran iskeletleri, mock veri katmanı `lib/api.ts`.

Bitince: `git add -p` → `git commit` (imza yok) → `git push -u origin kutay/web` → PR aç (şablon dolu) → gruba "PR açık" yaz.

> Yapay zekaya ilk mesaj: "Aşağıda AGENTS.md ve görev kartım var. Kurallara uy. Mevcut Next.js yapımı koru, yeni framework önerme. API sözleşmesi (AGENTS.md §6) dışında uç uydurma; eksikse `TODO(kutay)` bırak. Önce 5 maddelik plan, sonra ekran ekran uygula; her ekran mock veriyle de çalışsın. Şu an şu adımdayım: ___"

## Rol
Web arayüzünün tamamı: 5 ekran, API bağlantısı, demo akışının arayüz tarafı, Vercel yayını. Sunumda "Problem / Çözüm / Dört yetenek" slaytlarını anlatan kişi.

## Ekranlar (sıra = önem)
| # | Ekran | İçerik | Uçlar |
|---|-------|--------|-------|
| 1 | **Genel Bakış** `/` | 4 KPI kartı (gelir, gider, fark, kritik ürün sayısı) + "son güncelleme" damgası; aylık gelir-gider çubuk (Recharts); gider kategorisi pastası; dönem sekmeleri (Bu ay / 3 ay / 6 ay) | `summary`, `cashflow/monthly`, `analytics/expenses-by-category` |
| 2 | **Kayıtlar** `/kayitlar` | Satış ve gider sekmeleri; tablo + arama; ekle/düzenle/sil formu (modal); "Dışa aktar (CSV)" | `sales`, `expenses`, `export/*.csv`, `products` (ürün seçimi) |
| 3 | **Stok** `/stok` | Ürün tablosu; kritik satır kırmızı; "sipariş yolda" rozeti (`open_order_id`); eşik düzenleme (PATCH) | `products` |
| 4 | **Asistan** `/asistan` | Sohbet; hazır soru çipleri (`assistant/suggestions`); yanıt balonunda katlanır "Sorguyu gör" (SQL kod bloğu) + sonuç tablosu + "Kaynak: satışlar · 13 Eyl 10:12"; üstte "Asistan yalnızca okur" notu; hata yanıtı sakin | `assistant/ask` |
| 5 | **Tedarik** `/tedarik` | "Şimdi kontrol et" butonu; durum sayaçları (Bekliyor / Onaylandı / Gönderildi / Reddedildi); taslak kartı: ürün, miktar, tedarikçi, tahmini tutar, mesaj önizleme; Onayla / Reddet; gönderildi damgası | `agent/check`, `orders`, `orders/{id}/approve|reject` |

Ortak: sol menü (5 ekran), üstte "OtoHesap" + "Genel bakış" başlığı, mobilde menü katlanır. Para formatı `tr-TR` (1.234,56 ₺). Boş veri ve yükleniyor durumları her ekranda.

## Saatlik plan
- **09:30–10:30** Mock veri katmanı: `lib/api.ts` içinde sözleşmedeki her uç için fonksiyon; `NEXT_PUBLIC_API_URL` yoksa `mocks/*.json` döner. Genel Bakış iskeleti.
- **10:30–13:00** Genel Bakış ve Kayıtlar gerçek API'ye bağlı (Murat'ın uçları 11:00–12:00 arası gelir; gelene kadar mock). CRUD formu çalışır.
- **13:30–16:30** Asistan ve Tedarik ekranları (Murat 16:30'da `ask`, Ömer 15:00'te `orders` verir; önce mock).
- **16:30–19:00** Stok ekranı, rozetler, dönem sekmeleri, CSV butonu, hata/boş durumlar, mobil kontrol, `lint` temiz.
- **19:00–20:00** Vercel yayını (`NEXT_PUBLIC_API_URL` = Render adresi); canlı linkte demo senaryosu.
- **20:00–22:00** Prova düzeltmeleri.

## Bağımlılıklar
- **Bana gelen:** iskelet ve sözleşme (10:30), `summary/cashflow/CRUD` (13:00), `orders` (15:00), `assistant/ask` (16:30).
- **Benden giden:** ekran görüntüleri (Yiğit slaytlar için, 17:00), canlı link (20:00).

## Dosyalarım
`apps/web/**` (tamamı). `.env.example`'a web değişkeni eklersen satırı Murat'a yaz.

## Kabul kriterleri
- 13:00: Genel Bakış gerçek rakamlarla; gider eklenince KPI ve pasta güncellenir (yeniden istek).
- 16:30: Asistan çipten soru sorar, SQL'i gösterir; Tedarik'te onayla akışı çalışır.
- 19:00: 5 ekran, mobilde kırılmıyor, `bun run build` temiz.
- 20:00: Vercel'de canlı.

## Risk ve yedek
- API gecikirse mock ile ilerle; bağlama işi 30 dk'yı geçmez.
- Recharts pastası boş veriyle çökerse "Veri yok" kartı.
- Vercel build'i CI ile aynı komut; yerelde `build` geçiyorsa geçer.

## Yapma
- Backend kodu yazma; sözleşme dışı uç isteme (ihtiyaç → WhatsApp → Murat).
- Yeni UI kütüphanesi ekleme (bir tane yeter). Tasarım sistemi turu: bugün değil.

## Araştırmadan gelen notlar (13 Eyl, SONUC-chatgpt)
- **Dashboard'u sıfırdan tasarlama:** shadcn/ui'nin resmî `dashboard-01` bloğu (sidebar + KPI kart + grafik + veri tablosu) iskelet olarak alınır, OtoHesap renk diline (lacivert + yeşil) sadeleştirilir. Tremor gibi ikinci bir grafik/UI katmanı eklenmez; Recharts + shadcn `Card` yeter. Next.js dışında bir araçla başladıysan bu maddeyi atla, WhatsApp'a yaz.
- Sohbet balonu, katlanır SQL bloğu ve kaynak damgası küçük özel bileşenler; hazır sohbet kütüphanesi arama.
- Recharts'a boş dizi verme: `data.length === 0` → "Veri yok" kartı. Para `tr-TR`, tarih `Europe/Istanbul`.
- Yayında CORS için yalnız üretim alan adı; Vercel preview URL'lerine güvenme. Prod env'i gün ortasında sabitle, demo öncesi gizli pencerede test et.

## Durum (13 Eyl akşam) — inşa edildi, senin için kalan
**Yapıldı (Claude, main'de):** Next 16 uygulaması, 5 ekran, Öngörü kartları, `lib/api.ts` tipli istemci + mock modu rozeti, tr-TR biçim, lint/build temiz, canlı API'ye karşı doğrulanmış.
**Geliştirme Günü'nde senin işin:** (1) `make web` ile aç, tasarımı kendi dokunuşunla sahiplen (renk/boşluk/ikon; yapı değişmez); (2) Vercel: Root Directory `apps/web`, env `NEXT_PUBLIC_API_URL` = Render API adresi; (3) mobil ve boş durum turu; (4) demo senaryosundaki 7 adımı canlıda kronometreyle sür, takılan yeri düzelt; (5) Kayıtlar formunda "diğer" kategori sınırı gibi küçük pürüzler. Kendi UI'ın varsa: aynı `lib/api.ts` ile bağlanır; ekran ekran değiştirilebilir.
