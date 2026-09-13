# Görev kartı — Yiğit (dal: `yigit/data`)

## Nasıl başlarım (5 dakika)
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh
git checkout yigit/data
```
Sonra kendi yapay zeka aracına şu ilk mesajı at ve iki dosyayı yapıştır (`AGENTS.md` + bu kart):

> Aşağıda projenin AGENTS.md dosyası ve benim görev kartım var. Kurallara uy. Bilmediğin alan, model adı veya URL uydurma; `TODO(yigit)` bırak ve sor. Önce 5 maddelik plan ver; onaylayınca küçük adımlarla uygula, her adımda testi koştur. İlk işim: `data/seed.py` — Faker, seed=42, tam 2 kritik ürün.

Bitince: `git add -p` → `git commit` (imza yok) → `git push -u origin yigit/data` → PR aç (şablon dolu) → gruba "PR açık" yaz.

> Yapay zekaya ilk mesaj: "Aşağıda AGENTS.md ve görev kartım var. Kurallara uy. Şema `docs/schema.sql`'dekidir; sütun ekleme/değiştirme önerme (ihtiyaç → Murat). Seed deterministik olacak (seed=42). Uydurma yok; `TODO(yigit)` bırak ve sor. Önce 5 maddelik plan, sonra küçük adımlar, her adımda test. Şu an şu adımdayım: ___"

## Rol
Sentetik veri ve analitik uçlar; rakamların doğruluğu (testler); CSV dışa aktarma; sunum tasarımı (PowerPoint) ve README görselleri; sunumda "Teknoloji ve yöntem + Ekip" slaytları.

## Bugün teslim edeceklerim
1. **09:30–11:00 `data/seed.py` (iskeleti beklemeden; şema `docs/schema.sql`)**
   - Faker (`tr_TR`) + NumPy, `np.random.default_rng(42)`; `--reset` bayrağı tabloları boşaltıp yeniden doldurur; `DATABASE_URL`'e psycopg ile doğrudan yazar (SQLAlchemy'e bağımlı değil ki 11:00'de hazır olsun).
   - Senaryo: teknoloji aksesuar mağazası. 5 tedarikçi (biri Ömer'in Telegram chat_id'si, kanal `telegram`); 20 ürün / 5 kategori (kulaklık, kılıf, kablo-şarj, powerbank, aksesuar); maliyet–fiyat marjı %25–60.
   - `sales`: Nisan–Eylül 2026, ~600 satır; hafta içi/sonu ve Ağustos–Eylül artışı; kanal %60 mağaza / %40 online. **Kâr sıralamasında tek net kazanan: powerbank** (test bunu doğrular).
   - `expenses`: ~250 satır; kira ve maaş her ayın 1'inde sabit; elektrik, kargo, reklam, tedarik değişken.
   - **Tam 2 ürün kritik** (`stock_qty <= reorder_point`); üçüncü bir ürün eşiğin 1 üstünde (demoda satış ekleyince kritiğe düşer).
   - Sonunda özet basar: toplam gelir, gider, net, kritik ürünler, en kârlı ürün → bu rakamlar `docs/soru-bankasi.md`'ye ve testlere girer.
   - **11:00: Neon'a yüklendi, WhatsApp'a özet rakamlar.**
2. **11:00–13:00 Analitik uçlar (`routers/analytics.py`)**: `expenses-by-category` (pay yüzdesiyle), `sales-by-product` (`revenue`, `profit = sum(qty*(unit_price-unit_cost))`, `top`), `period` filtresi (`month|quarter|half`). Testler seed rakamlarıyla.
3. **13:30–15:00 CSV dışa aktarma** (`/api/export/sales.csv`, `expenses.csv`; UTF-8 BOM, `;` ayraç → Excel TR açar) + `tests/test_seed.py` (satır sayıları, 2 kritik, powerbank en kârlı).
4. **13:00–16:30 Soru bankası doğrulama (Ömer ile):** 15 sorunun beklenen SQL'ini seed üstünde koş, rakamları yaz.
5. **15:00–19:00 Sunum tasarımı:** PowerPoint 9 slayt (poster renk dili: lacivert + yeşil; sade); mimari diyagramı (AGENTS.md §3'ten), akış şeritleri, ekran görüntüleri (Kutay 17:00'de verir), stack tablosu, ekip slaydı, yol haritası. README için 3 görsel (pano, asistan, tedarik).
6. **19:00–22:00** Slaytlar final, prova geri bildirimleriyle düzeltme, video yedeği montajı (Ömer kaydeder).

## Bağımlılıklar
- **Bana gelen:** `docs/schema.sql` (09:00'da hazır), Neon bağlantısı (09:00), iskelet (10:30, analytics için), ekran görüntüleri (17:00).
- **Benden giden:** seed + özet rakamlar (11:00) → herkes; analytics (13:00) → Kutay; beklenen rakamlar (16:30) → Murat/Ömer; slaytlar (21:00).

## Dosyalarım
`data/seed.py`, `apps/api/app/routers/analytics.py`, `routers/export.py` (Murat iskelette açar), `tests/{test_seed,test_analytics}.py`, `docs/sunum/OtoHesap.pptx`, `docs/img/*`, `docs/soru-bankasi.md` (Ömer ile).

## Kabul kriterleri
- 11:00: `python data/seed.py --reset` 10 sn altında; özet rakamlar basılır; iki kez koşunca aynı rakamlar.
- 13:00: pasta ve "en kârlı ürün" uçları gerçek; testler geçer.
- 16:30: 15 sorunun beklenen rakamları yazılı.
- 21:00: slaytlar 9, PowerPoint formatında, 10 dk akışa uygun.

## Risk ve yedek
- Neon'a yazma yavaşsa `COPY`/`executemany` toplu ekle.
- Faker Türkçe ad üretimi zayıfsa ürün adları elle liste (20 satır).
- PowerPoint yoksa Keynote → `.pptx` dışa aktar (format zorunlu).

## Yapma
- Şema değiştirme; ekran kodu yazma; ajan/asistan koduna dokunma.
- Seed'e rastgelelik (zaman damgası, `random` tohumsuz) sokma.

## Araştırmadan gelen notlar (13 Eyl, SONUC-chatgpt)
- **Problem slaydı rakamları (TÜİK 2024, A):** 3,928 milyon KOBİ · %99,6 girişim · %68,5 istihdam · %44,1 ciro · %35,1'i ticaret. Kaynak satırı slaytın altına: "TÜİK, KOBİ İstatistikleri 2024".
- **Slayta GİRMEYECEK sayılar:** ön muhasebe yazılımı kullanım oranı, haftalık zaman kaybı, KOBİ AI benimseme oranı, Trendyol "40 milyon müşteri" (aramada 35–37 milyon çıkıyor), bizim fiyat paketlerimiz "pazar fiyatı" gibi. Kullanılabilir: Paraşüt çıpası "940 TL + KDV/ay" (parasut.com, A; sayfa tarihi belirsiz, "güncel sayfa" diye sun), Trendyol "250.000'den fazla satıcı (2024)", ÖHVPS 2.0 "16,4 milyon kullanıcı, günlük 12,3 milyon işlem, 53 katılımcı (TCMB, 17 Mart 2026)", e-Fatura 1 Temmuz 2026 eşikleri (3 milyon TL genel, 500 bin TL e-ticaret; sektör kaynakları, B).
- **Yol haritası slaydı:** Trendyol Product V2 (V1 15 Eyl 2026'da kapanıyor) → e-belge entegratörü → lisanslı açık bankacılık sağlayıcısı → çok kiracı (tenant_id + RLS) → Azure (Container Apps + PostgreSQL + Entra) + Marketplace.
- **"Rakiplerde AI yok" slaytı YOK.** Konumlama: "ön muhasebenin yerine geçen değil, üstünde çalışan karar katmanı".
- Slayt madde listesi, 5 slogan ve konuşmacı notları: `docs/sunum/pitch-paketi.md`.
- Seed: kritik stoktaki 2 ürünü rastgeleliğe bırakma; üretimden sonra deterministik düzelt ve fixture'ı `data/fixture.json` olarak kaydet (CI aynı dosyayı yükler).

## Durum (13 Eyl akşam) — inşa edildi, senin için kalan
**Yapıldı (Claude, main'de):** `data/seed.py` (608 satış, 228 gider, tam 2 kritik, kâr lideri, `as_of`), analitik uçlar, CSV (enjeksiyon korumalı), 5 Öngörü kartı, 24 test; seed özeti `data/README.md`.
**Geliştirme Günü'nde senin işin:** (1) slaytlar: `docs/sunum/pitch-paketi.md` 9 slayt, poster renk dili, TÜİK rakamları kaynaklı, "Rakiplerde AI yok" yok; (2) canlı uygulamadan ekran görüntüleri (pano, asistan, tedarik) → slayt + README; (3) soru bankası beklenen rakamları (Ömer ile); (4) demo verisinde göze batan bir şey varsa (ürün adı, tutar) seed'de düzelt, `make seed`; (5) video yedeği montajı.
