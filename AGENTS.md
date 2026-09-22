# OtoHesap — Sistem Mimarisi ve Ajan Özellikleri (AGENTS.md)

OtoHesap, KOBİ'lerin gelir, gider, finansal analiz ve stok süreçlerini tek platformda birleştiren yapay zekâ destekli modern bir finans ve operasyon yönetim platformudur.

---

## 1 · Proje Özeti ve Temel Yetenekler

| # | Yetenek | Açıklama | Davranış & Güvenlik |
|---|---------|----------|---------------------|
| 1 | **Akıllı Finans Asistanı** | Türkçe doğal dil sorusu → AST doğrulamalı SQL → salt-okur veritabanı sorgusu → gerçek veriden analitik yanıt. | Üretilen SQL ekranda şeffaf biçimde gösterilir. Salt-okur DB rolü + AST beyaz liste koruması ile çalışır. |
| 2 | **Görsel Analitik & Raporlama** | Gerçek zamanlı KPI kartları, aylık gelir-gider çubuk grafiği, kategori bazlı harcama dağılımı, dönem filtreleri ve CSV dışa aktarımı. | Gelir/gider eklendiğinde panolar anında güncellenir; kural tabanlı anomali tespit kartları üretir. |
| 3 | **Otonom Tedarik Ajanı** | Kritik stok eşiğine düşen ürünleri tespit eder, sipariş taslağı oluşturur ve insan onayıyla tedarikçiye Telegram mesajı iletir. | **Human-in-the-Loop:** Ajan hiçbir mesajı kullanıcı onayı olmadan göndermez; mükerrer sipariş koruması vardır. |
| 4 | **Modern Web Deneyimi** | Kurulumsuz, her cihazdan erişilebilir, responsive ve erişilebilir arayüz. | Next.js 16 App Router, Tailwind CSS v4 ve Recharts ile modern gösterge paneli. |

---

## 2 · Mimari ve Teknoloji Yığını

```
[Tarayıcı / İstemci]
        │
        ▼ (HTTPS / JSON)
[Next.js 16 + Tailwind CSS v4 + Recharts] (apps/web)
        │
        ▼ NEXT_PUBLIC_API_URL
[FastAPI + SQLAlchemy 2 + Pydantic v2] (apps/api)
        ├── routers/    summary · sales · expenses · products · analytics · assistant · orders · agent
        ├── services/   text2sql (şema + AST doğrulama + salt-okur yürütme)
        │               agent (eşik kontrolü + taslak + onay mekanizması)
        │               notify (Telegram Bot API)
        │               llm (Anthropic / Gemini / Groq / Fake adaptörleri)
        └── scheduler/  APScheduler periyodik arka plan kontrolü
        │
        ▼
[PostgreSQL 16] (Uygulama Rolü + otohesap_ro Salt-Okur Rolü)
```

| Katman | Teknoloji | Açıklama |
|--------|-----------|----------|
| **Web** | Next.js 16, React 19, Tailwind CSS v4, Recharts | Hızlı, tip güvenli ve modern kullanıcı deneyimi |
| **API** | FastAPI, Python 3.12, SQLAlchemy 2, Pydantic v2 | Yüksek performanslı asenkron REST API |
| **Paket Yöneticileri** | `uv` (Python), `bun` (Node.js) | Milisaniyeler mertebesinde bağımlılık çözümü |
| **Veritabanı** | PostgreSQL 16 | ACID uyumlu ilişkisel model; ayrılmış salt-okur kullanıcı rolü |
| **LLM Adaptörü** | `services/llm.py` | Anthropic, Google Gemini, Groq ve Mock/Fake adaptörleri |
| **Bildirim** | Telegram Bot API | Tedarikçilere otomatik formatlı satın alma talebi iletimi |

---

## 3 · Veri Modeli ve Metrik Standartları

### Temel Tablolar
- `suppliers`: id, name, contact_channel (`telegram`/`email`), contact_address, lead_time_days
- `products`: id, name, category, unit_cost, sale_price, stock_qty, reorder_point, target_stock, supplier_id
- `sales`: id, sold_at, product_id, qty, unit_price, total, channel (`magaza`/`online`)
- `expenses`: id, spent_at, category (kira, maas, elektrik, kargo, reklam, tedarik), amount, vendor, note
- `purchase_orders`: id, created_at, product_id, supplier_id, qty, est_amount, status (`draft`/`approved`/`sent`/`rejected`), message_text, sent_at
- `chat_log`: id, asked_at, question, sql_text, answer, ok
- `v_monthly_cashflow` (view): month, income, expense, net

### Metrik Sözlüğü
- **Gelir:** $\sum \text{sales.total}$ (satış anındaki fiyat $\times$ miktar)
- **Gider:** $\sum \text{expenses.amount}$
- **Fark:** Gelir $-$ Gider (net kâr değildir; KDV/vergi düşülmemiş operasyonel farktır)
- **Kritik Stok Koşulu:** `stock_qty <= reorder_point`

---

## 4 · API Sözleşmesi

```
GET    /api/health                                -> {status:"ok", db:true, llm:string}
GET    /api/summary?period=month|quarter|half     -> {income, expense, net, critical_count, updated_at}
GET    /api/cashflow/monthly                      -> [{month:"2026-04", income, expense, net}]
GET    /api/analytics/expenses-by-category?period -> [{category, amount, share}]
GET    /api/analytics/sales-by-product?period&top -> [{product_id, product, revenue, profit, qty}]
GET    /api/sales?limit&offset&q                  -> {items:[...], total}
POST   /api/sales                                 -> {sold_at, product_id, qty, unit_price, channel} -> 201
PUT    /api/sales/{id}                            -> Satış kaydı güncelleme
DELETE /api/sales/{id}                            -> Satış kaydı silme
GET/POST/PUT/DELETE /api/expenses                 -> Gider CRUD operasyonları
GET    /api/products                              -> [{..., is_critical, open_order_id}]
PATCH  /api/products/{id}                         -> {reorder_point?, target_stock?, stock_qty?}
POST   /api/assistant/ask                         -> {question} -> {ok, answer, sql, rows, columns, sources, asked_at}
GET    /api/assistant/suggestions                 -> Hazır finansal analiz soruları
POST   /api/agent/check                           -> {created:int, drafts:[...], skipped:[...]}
GET    /api/insights                              -> Otomatik içgörü ve uyarı listesi
GET    /api/orders?status=...                     -> Sipariş listesi
POST   /api/orders/{id}/approve                   -> Sipariş onayı ve Telegram gönderimi
POST   /api/orders/{id}/reject                    -> Sipariş iptali
GET    /api/export/sales.csv                      -> Satış verileri CSV dışa aktarımı
GET    /api/export/expenses.csv                   -> Gider verileri CSV dışa aktarımı
```

---

## 5 · Akıllı Asistan (Text-to-SQL) Güvenlik Mimarisi

OtoHesap asistanı, doğal dil sorularını güvenli SQL sorgularına dönüştürmek için katmanlı bir savunma mekanizması (Defense-in-Depth) uygular:

1. **Ayrı Salt-Okur Rol (`otohesap_ro`):** Asistan sorguları yalnızca `SELECT` iznine sahip kısıtlı bir veritabanı kullanıcısı üzerinden çalışır. Tablo değiştirme, silme veya yapısal işlem yapamaz.
2. **AST Beyaz Liste Doğrulaması:** Üretilen SQL, `sqlglot` ile soyut sözdizim ağacına (AST) ayrıştırılır. Yalnızca izin verilen tablolar (`sales`, `expenses`, `products`, `suppliers`, `purchase_orders`, `v_monthly_cashflow`) sorgulanabilir.
3. **Fonksiyon İzin Listesi:** Yalnızca güvenli toplama ve matematik fonksiyonlarına (`sum`, `count`, `avg`, `min`, `max`, `coalesce`, `round`, `date_trunc` vb.) izin verilir. `pg_sleep`, `set_config` gibi sistem fonksiyonları derhal reddedilir.
4. **Tek İfade & Sınır Kuralı:** Birden fazla SQL ifadesi (`;` ile ayrılmış) ve yorum satırları (`--`, `/*`) engellenir. `LIMIT` bulunmayan sorgulara otomatik `LIMIT 200` eklenir. `statement_timeout` 5 saniyedir.
5. **Şeffaflık:** Asistanın ürettiği sorgu, dokunduğu kaynak tablolar ve sorgu zamanı kullanıcı arayüzünde her zaman açıkça gösterilir.

---

## 6 · Otonom Tedarik Ajanı İlkeleri

1. **Deterministik Eşik Kontrolü:** Ajan, stok miktarı yeniden sipariş noktasının altına düştüğünde sipariş taslağı üretir. Sipariş miktarı: $\text{target\_stock} - \text{stock\_qty}$.
2. **Mükerrer Sipariş Önleme:** Aynı ürün için halihazırda onay bekleyen veya iletilmiş açık bir sipariş varsa yeni taslak üretilmez.
3. **Kontrollü Otonomi:** Sipariş taslağı oluşturulduktan sonra yetkili kullanıcı arayüzden onaylamadıkça dış dünyaya (Telegram Bot API) hiçbir mesaj gönderilmez.
