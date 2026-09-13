# Data Model: OtoHesap MVP

**Faz**: 1 | **Tarih**: 2026-09-13 (D16–D20 sonrası güncellendi) | **Kaynak**: `docs/schema.sql` (sahibi Murat; değişiklik = PR + WhatsApp duyurusu), `apps/api/app/models.py` (şema ile birebir), `AGENTS.md §5` metrik sözlüğü

Motor: PostgreSQL 16. Para `NUMERIC(12,2)` (JSON'da `number`). Zaman `TIMESTAMPTZ` (JSON'da ISO 8601 UTC). Kimlikler `SERIAL`.

## 1. Tablolar

### suppliers — tedarikçi
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | |
| name | TEXT | NOT NULL | Mesajda "Merhaba {name}" |
| contact_channel | TEXT | NOT NULL, CHECK IN ('telegram','email') | `telegram` gönderilir; `email` bugün dry-run gibi davranır (loglar) |
| contact_address | TEXT | NOT NULL | Telegram `chat_id` veya e-posta. **Salt-okur role sütun düzeyinde kapalı** (D19): `REVOKE SELECT ON suppliers FROM otohesap_ro; GRANT SELECT (id, name, contact_channel, lead_time_days) ON suppliers TO otohesap_ro;` — asistan prompt şemasında da yer almaz |
| lead_time_days | INT | NOT NULL DEFAULT 3 | Mesajda "Teslim süresi N gün" |

İlişki: 1 tedarikçi → N ürün (`products.supplier_id`), 1 → N sipariş. Seed'de Telegram kanallı tedarikçinin adresi `TELEGRAM_CHAT_ID` yer tutucusudur; Ömer'in gerçek `chat_id`'si `.env`/DB'de güncellenir.

### products — ürün
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | |
| name | TEXT | NOT NULL | |
| category | TEXT | NOT NULL | Seed: kulaklik, kilif, kablo-sarj, powerbank, aksesuar |
| unit_cost | NUMERIC(12,2) | NOT NULL | Tahmini brüt katkı ve `est_amount` hesabında (**mevcut** maliyet; tarihsel maliyet yok, D16) |
| sale_price | NUMERIC(12,2) | NOT NULL | Satış formunda varsayılan `unit_price` |
| stock_qty | INT | NOT NULL DEFAULT 0 | Satış oluşturma düşürür, silme geri ekler, düzenleme farkı uygular (R-19); `sent` sipariş stoğu ARTIRMAZ (D17) |
| reorder_point | INT | NOT NULL | Kritik eşik |
| target_stock | INT | NOT NULL | Sipariş sonrası hedef; `qty = max(1, target_stock − stock_qty)` |
| supplier_id | INT | FK suppliers(id), NULL olabilir | NULL ise ajan taslak üretmez, `skipped` (`tedarikci_yok`) döner |

Doğrulama (API PATCH): `reorder_point ≥ 0`, `target_stock ≥ 0`, `stock_qty ≥ 0`; `target_stock > reorder_point` seed'de sağlanır, API zorlamaz.

### sales — satış
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | |
| sold_at | TIMESTAMPTZ | NOT NULL | Indeks `ix_sales_sold_at`; API'de boş bırakılırsa "şimdi (UTC)" |
| product_id | INT | NOT NULL, FK products(id) | Indeks `ix_sales_product` |
| qty | INT | NOT NULL, CHECK qty > 0 | |
| unit_price | NUMERIC(12,2) | NOT NULL | Boş bırakılırsa ürünün `sale_price`'ı |
| total | NUMERIC(12,2) | NOT NULL | Sunucu hesaplar: `qty × unit_price` (Gelir = Σ total, D16) |
| channel | TEXT | NOT NULL DEFAULT 'magaza', CHECK IN ('magaza','online') | |

### expenses — gider
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | |
| spent_at | TIMESTAMPTZ | NOT NULL | Indeks `ix_expenses_spent_at` |
| category | TEXT | NOT NULL | Arayüz 6 sabit seçenek sunar: kira, maas, elektrik, kargo, reklam, tedarik (DB'de CHECK yok; API boş olmayan metin kabul eder) |
| amount | NUMERIC(12,2) | NOT NULL, CHECK amount > 0 | Gider = Σ amount (D16) |
| vendor | TEXT | NULL | |
| note | TEXT | NULL | |

### purchase_orders — sipariş taslağı / kaydı
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | Mesajda "#id" |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | |
| product_id | INT | NOT NULL, FK products(id) | |
| supplier_id | INT | NOT NULL, FK suppliers(id) | Taslak anındaki `products.supplier_id` |
| qty | INT | NOT NULL, CHECK qty > 0 | `max(1, target_stock − stock_qty)` |
| est_amount | NUMERIC(12,2) | NULL | `qty × unit_cost` (2 ondalık) |
| status | TEXT | NOT NULL DEFAULT 'draft', CHECK IN ('draft','approved','sent','rejected') | Indeks `ix_orders_status` |
| message_text | TEXT | NULL | Şablon (FR-027); taslakta doldurulur, gönderimde aynen kullanılır |
| sent_at | TIMESTAMPTZ | NULL | Yalnız `sent`'te dolu |
| notify_ref | TEXT | NULL | **Gönderim izi (D17)**: Telegram `message_id` (string) · `dry-run` · `sent` (message_id gelmezse). `ALTER TABLE … ADD COLUMN IF NOT EXISTS` ile idempotent |

**Kısmi tekil indeks (D17):**
```sql
CREATE UNIQUE INDEX IF NOT EXISTS ux_open_order_per_product
  ON purchase_orders (product_id) WHERE status IN ('draft', 'approved', 'sent');
```
Ürün başına yalnız BİR açık sipariş; çift tıklama, çift zamanlayıcı ve çok worker ikinci sipariş üretemez. Ajan her ürünü savepoint içinde dener; `IntegrityError` → `skipped` (`acik_siparis_var`).

### chat_log — asistan izi
| Alan | Tip | Kısıt | Açıklama |
|------|-----|-------|----------|
| id | SERIAL | PK | |
| asked_at | TIMESTAMPTZ | NOT NULL DEFAULT now() | Yanıttaki `asked_at` |
| question | TEXT | NOT NULL | Ham soru |
| sql_text | TEXT | NULL | Son denenen SQL; koruma reddinde reddedilen metin (varsa) |
| answer | TEXT | NULL | Yanıt veya red/hata cümlesi |
| ok | BOOLEAN | NOT NULL DEFAULT false | Sorgu çalıştı ve özet üretildi → true |

`chat_log` beyaz listede DEĞİLDİR: asistan kendi geçmişini sorgulayamaz.

## 2. Görünüm

### v_monthly_cashflow
```
month (timestamptz, ay başı; API "YYYY-MM" verir) · income · expense · net = income − expense
```
`sales` ve `expenses`'in ay kümelerinin birleşimi; veri olmayan taraf `COALESCE(…, 0)`. `date_trunc('month', …)` oturum saat diliminde çalışır (Neon: UTC). Görünüm adı korunur; **ekranda "Aylık gelir–gider" yazılır, "nakit akışı" denmez** (D16: tahsilat/ödeme alanı yok). `net` sütunu ekranda "Fark" etiketiyle gösterilir. Pano çubuğunun ve öngörü kartlarının kaynağıdır; beyaz listededir.

## 3. İlişki özeti

```
suppliers 1──N products 1──N sales
    │                 │
    └──────N purchase_orders N──┘   (ürün başına en çok 1 açık sipariş: ux_open_order_per_product)
chat_log (bağımsız)
```

## 4. Durum makinesi — purchase_orders.status

```
            run_check()            approve (commit)        send_message ok
  (yok) ──────────────► draft ─────────────────► approved ─────────────────► sent (+sent_at, +notify_ref)
                          │                        │   ▲
                          │ reject                 │   └── gönderim başarısız: approved kalır (502),
                          ▼                        │       insan tekrar approve = yeniden gönderim
                       rejected ◄──────────────────┘ reject
```

| Mevcut | approve | reject | run_check aynı ürün |
|--------|---------|--------|---------------------|
| draft | → approved (commit) → gönder → sent; başarısız → approved + 502 | → rejected | `skipped: acik_siparis_var` (DB indeksi) |
| approved | yeniden gönder → sent; başarısız → approved + 502 | → rejected | `skipped` |
| sent | 409 "Sipariş zaten sent durumunda." | 409 "Sipariş zaten sent durumunda." | `skipped` (D17: `sent` de bloke eder) |
| rejected | 409 "Sipariş zaten rejected durumunda." | 409 "Sipariş zaten rejected durumunda." | yeni taslak üretilebilir |

Kurallar: `sent_at` ve `notify_ref` yalnız `sent`'e geçişte set edilir; `sent`'ten geri dönüş yoktur; `sent` = mesaj gönderildi, teslim/kabul/ödeme değil, stok artmaz (D17). `NOTIFY_DRY_RUN=true` veya token yokken gönderim "başarılı simülasyon" sayılır (`sent`, `notify_ref='dry-run'`, yanıtta `notify.dry_run=true`). Onay ve gönderim aynı istekte ama iki ayrı commit'tir ki başarısız gönderimde onay izi kalsın. Belirsiz ağ sonucunda (istek gitti, yanıt kayboldu) otomatik tekrar yoktur; insan kontrolüne bırakılır. Gerçek ürün için `received/cancelled` ve kısmi teslim yol haritasıdır.

## 5. Türetilmiş alanlar ve metrikler (DB'de saklanmaz)

| Alan / metrik | Tanım (D16) | Nerede | Ekranda |
|---------------|-------------|--------|---------|
| Gelir | Σ `sales.total` (satış anı fiyatı × adet) | `summary.income`, `v_monthly_cashflow.income` | "Gelir" |
| Gider | Σ `expenses.amount` | `summary.expense` | "Gider" |
| Fark | Gelir − Gider; **net kâr değildir** | `summary.net`, `v_monthly_cashflow.net` | "Fark (Gelir − Gider)" |
| Tahmini brüt katkı | Σ qty × (unit_price − products.unit_cost); mevcut birim maliyetle | `analytics/sales-by-product.profit`, asistan kural 3, öngörü `top-product` | "En kârlı ürün (tahmini)" |
| `products.is_critical` | `stock_qty <= reorder_point` | `models.Product.is_critical`; `GET /api/products`; `summary.critical_count` | kırmızı satır |
| `products.open_order_id` | ürünün `status IN ('draft','approved','sent')` olan en yeni siparişi (indeks gereği en çok 1); yoksa null | `GET /api/products` | rozet (durum için `GET /api/orders`) |
| `sales.total` | `qty × unit_price`; sunucu hesaplar | POST/PUT sales | |
| `purchase_orders.qty` / `est_amount` | `max(1, target_stock − stock_qty)` / `qty × unit_cost` | `services/agent.py` | taslak kartı |
| `expenses-by-category.share` | `amount / Σ amount × 100`, 1 ondalık | `routers/analytics.py` | pasta etiketi |
| dönem (`period`) | yarı açık aralık `[start, end)`; `month` = içinde bulunulan takvim ayı (UTC) | `schemas/analytics.py` (`period_bounds`), `routers/summary.py` (`period_start`) — **tanımlar henüz birleşik değil, bkz. research.md R-17 / T015** | sekmeler |

## 6. Seed hedefleri (`data/seed.py`, sahibi Yiğit) — uygulandı

Determinizm: `np.random.default_rng(42)`, `Faker("tr_TR")` + `Faker.seed(42)`; sabit tarih aralığı **2026-04-01 … 2026-09-13** (`DATE_FROM`, `DATE_TO` kod sabiti; değiştirmek = DECISIONS satırı). `--reset`: tabloları boşaltıp yeniden doldurur. `DATABASE_URL`'e `psycopg` ile doğrudan yazar (COPY). Sonunda özet basar (toplam gelir, gider, fark, kritik ürünler, en kârlı ürün, süre) → `docs/soru-bankasi.md` "beklenen" sütunu ve testler.

| Hedef | Değer | Test |
|-------|-------|------|
| Senaryo | Teknoloji aksesuar mağazası (`BUSINESS_NAME` mesajda) | — |
| Tedarikçiler | 5; ilki `telegram` + `TELEGRAM_CHAT_ID` yer tutucu (gerçek id Ömer'den, `.env`/DB); `lead_time_days` sabit | `test_suppliers` |
| Ürünler | 20; 5 kategori; maliyet–fiyat marjı %25–60; her ürünün tedarikçisi var (kategori → tedarikçi eşlemesi) | `test_categories_and_margins` |
| Kritik stok | **tam 2 ürün** (`CRITICAL_PRODUCTS`; `stock_qty = max(1, reorder_point // 3)`) | `test_stock_levels` |
| Eşiğin 1 üstünde | **tam 1 ürün** (`NEAR_CRITICAL_PRODUCT`; `stock_qty = reorder_point + 1`); diğerleri ≥ 2× eşik | `test_stock_levels` |
| Satışlar | ~600 satır; hafta içi/sonu; Ağustos–Eylül artışı; kanal ~%60 mağaza / ~%40 online; `total = qty × unit_price` | `test_counts`, `test_sales_shape` |
| Kâr lideri | `PROFIT_LEADER` (powerbank); ikinciden en az `PROFIT_GAP` önde; gerekirse Ağustos–Eylül'e lider satışı eklenir | `test_profit_leader_is_powerbank` |
| Giderler | ~250 satır; kira ve maaş her ayın 1'inde sabit; elektrik, kargo, reklam, tedarik değişken; Eylül 2026'da kayıt var | `test_fixed_expenses` |
| Zaman damgaları | Mağaza saati (UTC+3) ile üretilir, DB'ye UTC yazılır; gün içi saatler ay sınırını taşırmaz | `test_deterministic` |
| Siparişler, chat_log | boş (demo "Şimdi kontrol et" ile 2 taslak üretir) | `test_agent_check_endpoint` |

## 7. Roller ve erişim

| Rol | Kullanan | Yetki |
|-----|----------|-------|
| uygulama rolü (`DATABASE_URL`) | API (CRUD, ajan, chat_log yazımı), seed | tam |
| `otohesap_ro` (`DATABASE_URL_RO`) | yalnız asistan sorguları (`db.engine_ro`) | `SELECT` on all tables **hariç** `suppliers.contact_address` (sütun düzeyi grant); `statement_timeout='5s'`; bağlantıda ayrıca `default_transaction_read_only=on` |

Rol komutları `docs/schema.sql` sonundaki yorumlarda (8 satır); `quickstart.md` §3'te tekrarlanır.
