# Yiğit — görev kartı (13 Eyl akşam sürümü; deneme sunumu 14 Eyl, 3 dk)

**Durum:** Uygulama `main`'de çalışıyor. Sentetik veri (`data/seed.py`: 608 satış, 228 gider, 20 ürün, tam 2 kritik, kâr lideri Powerbank 20000 mAh), analitik uçlar, Öngörü kartları ve CSV yazıldı ve testli (24 test). Bugün hedefin: **ekran görüntüleri, 16 Eyl için slayt iskeleti, veriyi göz kontrolünden geçirmek.**

## 1 · Yapay zekaya ilk mesaj (olduğu gibi yapıştır; ardından `AGENTS.md` ve bu dosyayı ekle)
> Sen benim geliştirme asistanımsın. Ekli `AGENTS.md` ve görev kartım projenin tek gerçeğidir; dışına çıkma, yeni özellik önerme. Depo: https://github.com/muratcan-ates/Oto-Hesap — dalım `yigit/data`. Ürün çalışır durumda; benim işim karttaki adımları **sırayla** bitirmek. Her adımda: ne yapacağını 3 maddede söyle, ben "devam" deyince yap, çalıştırdığın komutun çıktısını göster, bitince "ADIM N TAMAM" yaz ve sonraki adıma geç. Bilmediğin dosya/alan/komut uydurma; önce dosyayı oku, yine emin değilsen bana sor. Commit mesajına yapay zeka imzası ekleme. `.env` içeriğini ve anahtarları asla sohbete yazma. Şu an Adım 0'dayım.

## 2 · Adımlar (sırayla)
### Adım 0 · Kurulum (15 dk) — herkes aynı
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh                # hook + .env + bağımlılıklar (uv, bun gerekir; yoksa: brew install uv oven-sh/bun/bun)
git checkout yigit/data
```
`.env` doldur: `DATABASE_URL` ve `DATABASE_URL_RO` → Murat'ın DM'le attığı Neon adresleri (kendi Postgres'in varsa: `createdb otohesap && psql -d otohesap -f docs/schema.sql`, salt-okur rol komutları `docs/schema.sql` sonunda). `LLM_PROVIDER=fake` bırakabilirsin; demo soruları anahtarsız da çalışır.
```bash
make seed        # sentetik veri (6 ay, 20 ürün, 2 kritik)  — Neon paylaşımlıysa yalnız Murat koşar
make api         # http://localhost:8000/docs
make web         # ayrı terminal → http://localhost:3000
```
**Kabul:** `http://localhost:3000` açılıyor, sol menü altında "API bağlı" yazıyor (mock rozeti YOK), Genel Bakış'ta "Kritik ürün: 2".

### Adım 1 · Ekran görüntüleri (20 dk)
`http://localhost:3000` açıkken 4 görüntü al (tam pencere, 1440 genişlik, açık tema): Genel Bakış (Öngörü kartları görünsün), Asistan (çip sorusu + "Sorguyu gör" açık), Tedarik (onay sonrası "Gönderildi"), Stok (2 kırmızı satır). Kaydet: `docs/img/genel-bakis.png`, `asistan.png`, `tedarik.png`, `stok.png`. README'de "Ekranlar" bölümü ekle (4 resim, 1'er satır açıklama).
**Kabul:** 4 dosya `docs/img/` altında, README'de görünüyor.

### Adım 2 · 16 Eyl slayt iskeleti (60 dk)
PowerPoint (`docs/sunum/OtoHesap.pptx`), 6 slayt: (1) Kapak "Verinizi anlayın. İşinizi yönetin." (2) Problem: TÜİK 2024 — 3,928 milyon KOBİ, %68,5 istihdam, %44,1 ciro, %35,1'i ticaret (kaynak satırı: TÜİK KOBİ İstatistikleri 2024) (3) Çözüm: 4 yetenek + Adım 1 görüntüleri (4) Nasıl çalışır: "LLM sorguyu yazar → rakamı veritabanı verir → siparişi kural motoru hazırlar → insan onaylar" (5) Ekip: 4 isim + iş bölümü (6) Yol haritası: Trendyol Product V2, e-belge entegratörü, çok kiracılı sürüm, Azure. Renk dili poster: lacivert `#0F2A3C`, yeşil `#1C8C6E`. **"Rakiplerde AI yok" cümlesi yok.** Metinler: `docs/sunum/pitch-paketi.md`.
**Kabul:** dosya depoda, 6 slayt, her slaytta en fazla 3 madde.

### Adım 3 · Veri göz kontrolü (20 dk)
`http://localhost:3000/kayitlar` ve `/stok`'ta ürün adları, tutarlar, kategoriler jüri gözüyle mantıklı mı? Sorun varsa `data/seed.py` içinde ürün listesi/fiyat aralığını düzelt, sonra:
```bash
make seed && cd apps/api && TEST_DB_NAME=otohesap_test_yigit uv run pytest -q tests/test_seed.py
```
**Kabul:** test yeşil; hâlâ tam 2 kritik ürün ve Powerbank kâr lideri (test bunu doğrular).

### Adım 4 · PR aç (10 dk)
```bash
git add -A && git commit -m "docs: ekran görüntüleri, slayt iskeleti" && git push -u origin yigit/data
```
PR: `yigit/data` → `main`. **Kabul:** CI yeşil.

### Adım 5 · Ekstra (zaman kalırsa)
- Öngörü kartı metinleri (`apps/api/app/services/insights.py`) daha doğal Türkçe.
- 90 sn demo videosu için Murat'a kurgu yardımı (Canva).

## 3 · Bilmen gerekenler
- Seed deterministik (seed=42); rastgelelik ekleme, kritik ürünler adla sabit (`CRITICAL_PRODUCTS`).
- "Fark" net kâr değildir; "en kârlı ürün" tahmini brüt katkıdır — slaytlarda bu kelimeler (D16).
- Rakam kaynakları ve hangi sayının slayta girebileceği: `docs/research/KONTROL-2026-09-13.md`.

## 4 · Kurallar (kısa)
- Kendi dalında çalış; `main`'e yalnız PR ile (`git push -u origin yigit/data` → GitHub'da "Compare & pull request"). Push yetkin yoksa Murat'a yaz.
- Küçük commit, imzasız (`git log -1` ile kontrol; hook zaten engeller).
- `.env` ve anahtarlar sohbete/gruba yazılmaz.
- Yeni özellik yok; kırık bir şey görürsen gruba yaz.

## 5 · Takılırsan
45 dakikada ilerleme yoksa gruba yaz: "Adım N'de takıldım, hata: …". Yapay zekaya `docs/team/BUGUN-PLAN.md` ve hata metnini ver. 22:00 kontrol toplantısında canlı bakarız.
