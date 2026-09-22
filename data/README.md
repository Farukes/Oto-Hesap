# Sentetik veri — `data/seed.py`

Teknoloji aksesuar mağazası senaryosu, **1 Nisan – 13 Eylül 2026**. Şema: `docs/schema.sql`.
%100 sentetik (KVKK, D12): tedarikçi e-postaları, kişi ve firma adları Faker `tr_TR` üretimidir.

## Çalıştırma

```bash
# depo kökünde; şema önce uygulanmış olmalı: psql "$DATABASE_URL" -f docs/schema.sql
uv run --project apps/api python data/seed.py --reset
# başka bir veritabanına (ör. Neon):
uv run --project apps/api python data/seed.py --reset --url "postgresql://USER:PASS@HOST/otohesap?sslmode=require"
```

- Bağlantı sırası: `--url` > `DATABASE_URL` ortam değişkeni > kökteki `.env` (yalnız `DATABASE_URL` satırı okunur).
- `--reset`: `TRUNCATE sales, expenses, purchase_orders, chat_log, products, suppliers RESTART IDENTITY CASCADE`,
  sonra yeniden doldurur. Bayrak verilmezse mevcut satırların üstüne ekler (demo için hep `--reset`).
- Yalnız `psycopg` + `numpy` + `faker` (SQLAlchemy'ye bağımlı değil); satış ve giderler `COPY` ile yazılır, ~0,1 sn.
- İçe aktarılabilir: `from data.seed import run; run(url, reset=True)` özet sözlüğü döner; script bu özeti JSON basar.

## Determinizm

`numpy.random.default_rng(42)` + `Faker.seed(42)`; ürün/tedarikçi listeleri ve fiyatlar elle sabittir.
Aynı komut iki kez koşulunca aynı özet çıkar (`tests/test_seed.py::test_deterministic` doğrular).
Rastgelelik yalnız tohumlu üreticiden gelir; zaman damgası, `random` ya da sistem saati kullanılmaz.
Stok seviyeleri satışlardan **sonra** deterministik atanır: tam 2 kritik, tam 1 eşiğin bir üstünde,
diğerleri eşiğin en az 2 katı. Kâr lideri doğal olarak ≥ %20 önde; değilse Ağustos–Eylül'e lider satışı
eklenerek güvence altına alınır (`leader_fix_rows`, bugünkü parametrelerle 0).

## Telegram tedarikçisi

`suppliers` tablosunda bir kayıt `contact_channel='telegram'` ve `contact_address='TELEGRAM_CHAT_ID'` yer tutucusuyla
gelir. Demodan önce gerçek chat_id ile değiştir (seed her `--reset`'te yer tutucuya döner, komutu tekrar çalıştır):

```sql
UPDATE suppliers SET contact_address = '<GERÇEK_CHAT_ID>' WHERE contact_channel = 'telegram';
```

Kritik stoktaki iki ürün de bu tedarikçiye bağlıdır; "Onayla" ile giden mesaj telefona düşer.

## Özet (13 Eyl 2026 koşusu, seed=42)

| Alan | Değer |
|------|-------|
| Aralık / `as_of` | 2026-04-01 → 2026-09-13 / son satış 2026-09-13 |
| Tedarikçi / ürün | 5 / 20 (5 kategori × 4: `kulaklik`, `kilif`, `kablo-sarj`, `powerbank`, `aksesuar`) |
| Satış satırı | 608 (mağaza 360 / online 248 ≈ %41 online) |
| Gider satırı | 228 (kira 6 · maaş 6 · elektrik 6 · kargo 123 · reklam 60 · tedarik 27) |
| Gelir | 1.109.509,10 ₺ |
| Gider | 888.225,93 ₺ |
| Fark (gelir − gider) | 221.283,17 ₺ |

**Kritik stok (tam 2, ikisi de Telegram tedarikçisi "Anadolu Güç Sistemleri"):**

| id | Ürün | Stok / eşik | Hedef |
|----|------|-------------|-------|
| 13 | Powerbank 20000 mAh | 5 / 17 | 68 |
| 16 | Kablosuz Şarjlı Powerbank | 4 / 12 | 36 |

Eşiğin 1 üstünde: **id 9 · USB-C Şarj Kablosu 1 m (14 / 13)** — demoda 1 adet satış eklenince kritiğe düşer.

**En kârlı 3 ürün (tahmini brüt katkı = Σ adet × (satış fiyatı − birim maliyet), D16):**

| Ürün | Katkı | Ciro | Adet |
|------|-------|------|------|
| Powerbank 20000 mAh | 80.415,00 ₺ | 227.815,00 ₺ | 134 |
| Kablosuz Kulaklık Pro | 44.600,23 ₺ | 145.100,23 ₺ | 67 |
| Bluetooth Kulak İçi Kulaklık | 43.773,29 ₺ | 122.873,29 ₺ | 113 |

Lider ikinciden %80 önde; "En çok kazancım hangi üründen?" sorusunun tek net yanıtı var.

**Aylık (v_monthly_cashflow):**

| Ay | Gelir | Gider | Fark |
|----|-------|-------|------|
| 2026-04 | 191.846,62 | 150.164,14 | 41.682,48 |
| 2026-05 | 161.193,11 | 143.924,56 | 17.268,55 |
| 2026-06 | 173.761,26 | 137.331,82 | 36.429,44 |
| 2026-07 | 189.630,08 | 163.164,82 | 26.465,26 |
| 2026-08 | 271.378,53 | 159.210,58 | 112.167,95 |
| 2026-09 (1–13) | 121.699,50 | 134.430,01 | −12.730,51 |

Eylül 13 günlük olduğu ve kira+maaş (85.000 ₺) ayın 1'inde düştüğü için fark eksidir; Öngörü kartı bunu
"Bu ay (1–13 Eylül)" diye etiketler. Eylül'de reklam gideri "okula dönüş kampanyası" ile Ağustos'a göre %79 artar
(17.255 ₺ → 30.828 ₺) — "Reklam gideri geçen aya göre arttı" kartının kaynağı.

## Senaryo kuralları (kodda sabit)

- Satış yoğunluğu: hafta içi 1,2× · Cumartesi 0,8× · Pazar 0,5×; ay çarpanı Nis 0,80 → Eyl 1,55 (Ağustos–Eylül artışı).
- Birim fiyat = ürün satış fiyatı ±%5; `total = qty × unit_price` (2 ondalık); adet dağılımı fiyat bandına göre.
- Marj (maliyet üstü) %25–60; birim maliyet 30–1.500 ₺; `reorder_point` 5–20; `target_stock` 3–5 × eşik.
- Giderler: kira 25.000 ve maaş 60.000 her ayın 1'i; elektrik ayın 10'u (yazın yüksek); kargo/reklam/tedarik günlük Poisson.
  Tedarik satırları gerçek ürün maliyeti × parti adedi, tedarikçi adı ürünün tedarikçisi.
- Zaman damgaları mağaza saatiyle (UTC+3) üretilir, veritabanına UTC yazılır.

## Test

```bash
cd apps/api && TEST_DB_NAME=otohesap_test_data uv run pytest -q tests/test_seed.py
```
