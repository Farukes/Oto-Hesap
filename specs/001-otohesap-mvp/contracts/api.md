# API Sözleşmesi v0 — OtoHesap

**Kaynak**: `AGENTS.md §6` + eklemeler (research.md R-24; AGENTS.md'ye PR + duyuru ile işlenir) + D16–D20. **Tarih**: 2026-09-13. **Durum**: kodla birebir (`apps/api/app/routers/*`, `schemas/*`); "yapılacak" işaretli alanlar `tasks.md`'ye bağlıdır.

## Genel kurallar

- Taban yol `/api`; JSON; `Content-Type: application/json` (CSV uçları hariç).
- Tarih/zaman ISO 8601 UTC (`2026-09-13T07:12:00Z`); arayüz `Europe/Istanbul` ile gösterir.
- Para `NUMERIC(12,2)` → JSON **number** (`4500.0`), string değil.
- `period` = `month | quarter | half`; varsayılan `half`; yarı açık aralık `[start, end)`; "bu ay" = içinde bulunulan takvim ayı (UTC). **Not:** summary, analytics ve cashflow bugün üç ayrı hesap kullanır; birleştirme T015 (research.md R-17).
- Hata gövdesi `{"detail": "<Türkçe açıklama>"}`. FastAPI'nin varsayılan 422 gövdesi (liste) henüz tek Türkçe cümleye çevrilmedi (T014); web istemcisi listeyi `msg` alanlarından birleştirir. 4xx kullanıcı hatası, 5xx bizim hatamız; 500 gövdesi `"Sunucu hatası; lütfen tekrar deneyin."`.
- Kimlik doğrulama yok (tek kiracı). CORS: `CORS_ORIGINS` (üretimde yalnız Vercel alan adı).
- Liste uçlarında sıralama: en yeni önce (`sold_at`/`spent_at`/`created_at DESC`, eşitlikte `id DESC`); ürünler `id ASC`.
- Metrik sözlüğü (D16): `income` = Gelir, `expense` = Gider, `net` = **Fark** (net kâr değil), `profit` = **tahmini brüt katkı** (mevcut birim maliyetle). Alan adları değişmez; etiketler arayüzde.

Ortak tipler:

```ts
type Money = number;                 // 2 ondalık
type ISODate = string;               // UTC
type Period = "month" | "quarter" | "half";
type OrderStatus = "draft" | "approved" | "sent" | "rejected";
type Channel = "magaza" | "online";
type ContactChannel = "telegram" | "email";
type ExpenseCategory = "kira" | "maas" | "elektrik" | "kargo" | "reklam" | "tedarik"; // arayüz seçenekleri; API boş olmayan metin kabul eder
type SkipReason = "acik_siparis_var" | "tedarikci_yok";
```

---

## Sağlık

### GET /api/health
Yanıt 200:
```json
{"status": "ok", "db": true, "llm": "anthropic", "scheduler": true, "version": "0.1.0"}
```
`db`: gerçek `SELECT 1` sonucu (false olsa da 200; ısıtma betiği bakar). `llm`: `anthropic | gemini | groq | fake`.

---

## Genel bakış

### GET /api/summary?period=half
| Sorgu | Tip | Varsayılan |
|-------|-----|------------|
| period | Period | half |

Yanıt 200:
```json
{"income": 412350.0, "expense": 198420.5, "net": 213929.5, "critical_count": 2, "updated_at": "2026-09-13T07:12:00Z"}
```
`net` = Fark (Gelir − Gider). `critical_count` dönemden bağımsızdır (anlık stok). Bugünkü dönem hesabı: `month` = ay başından; `quarter` = şimdi − 3 takvim ayı; `half` = şimdi − 6 takvim ayı (T015 ile yarı açık ay sınırlarına taşınacak). Geçersiz dönem → 422.

### GET /api/cashflow/monthly
Sorgu yok. İçinde bulunulan ay dâhil son 6 ay; veri olmayan ay 0. Yanıt 200:
```json
[{"month": "2026-04", "income": 61200.0, "expense": 33100.0, "net": 28100.0}, {"month": "2026-05", "income": 0.0, "expense": 0.0, "net": 0.0}]
```
Ekranda "Aylık gelir–gider"; `net` "Fark".

### GET /api/analytics/expenses-by-category?period=half
Yanıt 200 (tutara göre azalan; `share` yüzde, 1 ondalık, toplam ≈ 100):
```json
[{"category": "maas", "amount": 90000.0, "share": 45.4}, {"category": "kira", "amount": 60000.0, "share": 30.2}]
```
Boş → `[]`. 400: `"Geçersiz dönem; month, quarter veya half olmalı."` Dönem: yarı açık `[months_ago(ay başı, n), gelecek ay başı)`, `half` için 1 Mar (T015).

### GET /api/analytics/sales-by-product?period=half&top=5
| Sorgu | Tip | Varsayılan / sınır |
|-------|-----|--------------------|
| period | Period | half |
| top | int | 5; 1–50 |

Yanıt 200 (**ciroya** göre azalan):
```json
[{"product_id": 7, "product": "PowerBank 20000 mAh", "revenue": 84500.0, "profit": 31200.0, "qty": 130}]
```
`profit` = tahmini brüt katkı = `Σ qty × (unit_price − products.unit_cost)` (mevcut birim maliyetle). 400: `"top 1 ile 50 arasında olmalı."` / geçersiz dönem.

---

## Kayıtlar — satışlar

### GET /api/sales?limit=50&offset=0&q=
| Sorgu | Tip | Varsayılan / sınır |
|-------|-----|--------------------|
| limit | int | 50; 1–500 |
| offset | int | 0; ≥ 0 |
| q | string | ürün adında `ILIKE %q%` |

Yanıt 200:
```json
{"items": [{"id": 601, "sold_at": "2026-09-13T08:30:00Z", "product_id": 7, "product_name": "PowerBank 20000 mAh", "qty": 2, "unit_price": 650.0, "total": 1300.0, "channel": "magaza"}], "total": 601}
```

### POST /api/sales
Gövde (`sold_at` ve `unit_price` isteğe bağlı):
```json
{"sold_at": "2026-09-13T08:30:00Z", "product_id": 7, "qty": 2, "unit_price": 650.0, "channel": "magaza"}
```
Kurallar: `qty ≥ 1`; `unit_price ≥ 0`, boşsa ürünün `sale_price`'ı; `sold_at` boşsa şimdi (UTC; saat dilimsizse UTC varsayılır); `channel` varsayılan `magaza`; `total` sunucuda; ürün satırı kilitlenir, stok `qty` kadar düşer.
Yanıt 201: satış nesnesi (yukarıdaki `items[0]` biçimi).
Hatalar: 404 `"Ürün bulunamadı"` · 400 `"Stok yetersiz: {stok} adet var"` · 422 doğrulama (qty ≤ 0, kanal, tip).

### PUT /api/sales/{id}
Gövde: aynı alanlar, **hepsi isteğe bağlı** (kısmi güncelleme). Stok farkı uygulanır; ürün değişirse eski ürüne iade, yeniye düşüm (yetersizse hiçbir şey değişmez). `unit_price` açıkça `null` → ürünün fiyatı. Yanıt 200: satış nesnesi. 404 `"Satış bulunamadı"`; 400/422 POST gibi.

### DELETE /api/sales/{id}
Yanıt 204 (gövde yok). Ürün stoğu `qty` kadar geri eklenir. 404 `"Satış bulunamadı"`.

---

## Kayıtlar — giderler

### GET /api/expenses?limit=50&offset=0&q=
`q`: `category`, `vendor`, `note` üzerinde `ILIKE`. Yanıt 200:
```json
{"items": [{"id": 251, "spent_at": "2026-09-13T08:35:00Z", "category": "reklam", "amount": 4500.0, "vendor": "Meta Ads", "note": null}], "total": 251}
```

### POST /api/expenses
```json
{"spent_at": "2026-09-13T08:35:00Z", "category": "reklam", "amount": 4500.0, "vendor": "Meta Ads", "note": null}
```
`amount > 0`; `category` boş olmayan metin (arayüz 6 seçenek sunar); `spent_at` boşsa şimdi; `vendor`, `note` isteğe bağlı. Yanıt 201: gider nesnesi. 422 doğrulama.

### PUT /api/expenses/{id} · DELETE /api/expenses/{id}
PUT kısmi (tüm alanlar isteğe bağlı; `vendor`/`note` `null` gönderilirse temizlenir) → 200 gider nesnesi; DELETE → 204. 404 `"Gider bulunamadı"`.

---

## Ürünler / stok

### GET /api/products
Sorgu yok; `id` artan. Yanıt 200:
```json
[{"id": 7, "name": "PowerBank 20000 mAh", "category": "powerbank", "unit_cost": 420.0, "sale_price": 650.0, "stock_qty": 4, "reorder_point": 8, "target_stock": 40, "supplier_id": 2, "supplier_name": "Anadolu Güç Sistemleri", "is_critical": true, "open_order_id": 12}]
```
`is_critical = stock_qty <= reorder_point`; `open_order_id`: durumu `draft|approved|sent` olan en yeni sipariş (indeks gereği en çok 1), yoksa `null`. Rozet metni ("taslak bekliyor" / "sipariş yolda") için arayüz `GET /api/orders` sonucunu bu id ile eşler.

### PATCH /api/products/{id}
Gövde (hepsi isteğe bağlı):
```json
{"reorder_point": 10, "target_stock": 40, "stock_qty": 12}
```
Tüm değerler tam sayı ≥ 0; `null` alanlar atlanır; boş gövde değişiklik yapmadan 200 döner. Yanıt 200: ürün nesnesi. 404 `"Ürün bulunamadı"` · 422 (negatif / tip).

---

## Asistan

### POST /api/assistant/ask
Gövde:
```json
{"question": "En çok kazancım hangi üründen?"}
```
`question`: en çok 2000 karakter (422); boşluk kırpılır; boş → 400.

Yanıt 200 (başarılı):
```json
{
  "ok": true,
  "answer": "En yüksek tahmini brüt katkı PowerBank 20000 mAh ürününden: 31.200 TL (mevcut birim maliyetle).",
  "sql": "SELECT p.name AS urun, SUM(s.qty * (s.unit_price - p.unit_cost)) AS kar FROM sales AS s JOIN products AS p ON p.id = s.product_id GROUP BY p.name ORDER BY kar DESC LIMIT 1",
  "rows": [{"urun": "PowerBank 20000 mAh", "kar": 31200.0}],
  "columns": ["urun", "kar"],
  "sources": ["sales", "products"],
  "asked_at": "2026-09-13T07:14:02Z",
  "cached": true,
  "model": "anthropic/claude-haiku-4-5"
}
```
| Alan | Tip | Açıklama |
|------|-----|----------|
| ok | bool | sorgu çalıştı ve özet üretildi; `chat_log.ok` ile aynı |
| answer | string | yalnız satırlardan; boş sonuç `"Sorgu bu veriyle eşleşen kayıt döndürmedi."`; LLM özeti yoksa deterministik `"Sorgu N satır döndürdü; ilk satır: …"`; belirsiz metrikte varsayım cümlesi (D20, T082) |
| sql | string \| null | guard'dan geçmiş, `LIMIT` eklenmiş son SQL (sqlglot Postgres yazımı) |
| rows | object[] | en çok 200; `{sütun: değer}`; Decimal → number, tarih → ISO |
| columns | string[] | sütun adları (ASCII alias) |
| sources | string[] | AST'den çıkan tablo/görünüm adları (İngilizce); arayüz Türkçe etiketler (`sales→satışlar, products→ürünler, expenses→giderler, suppliers→tedarikçiler, purchase_orders→siparişler, v_monthly_cashflow→aylık gelir–gider`) |
| asked_at | ISODate | |
| cached | bool | SQL soru bankasından (LLM'e gidilmedi); yeniden denemede `false` olur |
| model | string | yanıtı üreten sağlayıcı/model (`"anthropic/claude-haiku-4-5"`, `"fake"`); **yapılacak (T080, D19)** |

Başarısız ama 200: `{"ok": false, "answer": "Bu soruyu bu veriyle yanıtlayamadım.", "sql": <son deneme veya null>, "rows": [], "columns": [], ...}` — LLM "bu veriyle yanıtlanamaz" dedi ya da SQL iki denemede de hata verdi.

Hatalar:
| Kod | detail | Ne zaman |
|-----|--------|----------|
| 400 | `"Soru boş olamaz."` | boş / yalnız boşluk |
| 400 | `"Asistan yalnız okuma sorguları çalıştırır."` | koruma reddi: DML/DDL (CTE içinde dâhil), `;`/yorum, çoklu ifade, `SELECT INTO`, `FOR UPDATE`, beyaz liste dışı tablo/şema, yasak fonksiyon, boş SQL; ya da LLM yazma isteğini reddetti |
| 422 | (FastAPI doğrulama; T014 ile Türkçe) | 2000 karakter üstü |
| 503 | `"Asistan şu an yanıt veremiyor; lütfen tekrar deneyin."` | LLM'e ulaşılamadı (anahtar yok, ağ, 4xx/5xx, refusal) ve soru önbellekte yok |

Her istek (400/503 dâhil) `chat_log`'a yazılır; 400/503 ve `ok:false` → `chat_log.ok=false`. Önbellekten gelen SQL de koruma katmanından geçer. Guard (D19 hedef): fonksiyon izin listesi — bugün kara liste (`pg_sleep`, `set_config`, `pg_read_file`, `dblink`, `lo_*`, …); izin listesine geçiş T078.

### GET /api/assistant/suggestions
Yanıt 200: soru bankasındaki `demo: true` sorular, dosya sırasıyla; banka yoksa gömülü 5 soru. Bugünkü sıra (banka sırası):
```json
["En çok gider hangi kategoride?", "Hangi ürünler kritik stokta?", "Bu ay toplam giderim ne kadar?", "Son 3 ayda gelir-gider farkı nasıl değişti?", "En çok kazancım hangi üründen?"]
```
Demo senaryosu ilk çipin "En çok kazancım hangi üründen?" olmasını bekler → sıra düzeltmesi T081.

---

## Tedarik ajanı ve siparişler

Sipariş nesnesi (`Order`):
```json
{"id": 12, "created_at": "2026-09-13T07:20:00Z", "product_id": 7, "product_name": "PowerBank 20000 mAh", "supplier_id": 2, "supplier_name": "Anadolu Güç Sistemleri", "supplier_channel": "telegram", "qty": 36, "est_amount": 15120.0, "status": "draft", "message_text": "DEMO · sentetik sipariş #12 — Merhaba Anadolu Güç Sistemleri, OtoHesap Demo Mağaza için sipariş talebi: PowerBank 20000 mAh × 36 adet. Tahmini tutar 15.120,00 ₺. Teslim süresi 3 gün. Onay için bu mesajı yanıtlayabilirsiniz. — OtoHesap", "sent_at": null, "notify_ref": null}
```
`notify_ref`: `sent`'te Telegram `message_id` (string), `"dry-run"` (simülasyon) veya `"sent"` (id gelmezse); aksi `null` (D17).

### POST /api/agent/check
Gövde yok. Kritik ürünleri (`stock_qty <= reorder_point`) tarar; her ürün için savepoint içinde taslak dener. Yanıt 200:
```json
{"created": 2, "drafts": [Order, Order], "skipped": [{"product_id": 3, "reason": "acik_siparis_var"}, {"product_id": 9, "reason": "tedarikci_yok"}]}
```
- `drafts`: yalnız bu çağrıda üretilenler (`qty = max(1, target_stock − stock_qty)`, `est_amount = qty × unit_cost`).
- `skipped.reason`: `acik_siparis_var` (DB tekil indeksi `ux_open_order_per_product`: ürünün `draft|approved|sent` siparişi var) · `tedarikci_yok` (`supplier_id` NULL).
- İkinci çağrı → `{"created": 0, "drafts": [], "skipped": [...]}`. Zamanlayıcı aynı servisi çağırır (`services/agent.run_check`); LLM yok.

### GET /api/orders?status=draft
| Sorgu | Tip | Varsayılan |
|-------|-----|------------|
| status | OrderStatus | yok (hepsi) |

Yanıt 200: `[Order, ...]` (`created_at DESC, id DESC`). Geçersiz durum → 422.

### GET /api/orders/{id}
Yanıt 200: `Order`. 404 `"Sipariş bulunamadı"`.

### POST /api/orders/{id}/approve
Gövde yok. Akış: `draft → approved` (commit; gönderim çökse bile kalıcı) → `notify.send_message(supplier, message_text)` → `sent` + `sent_at` + `notify_ref` (commit).
Yanıt 200: sipariş şeması + `notify`:
```json
{"id": 12, "...": "Order alanları", "status": "sent", "sent_at": "2026-09-13T07:21:05Z", "notify_ref": "4821", "notify": {"ok": true, "dry_run": false, "channel": "telegram", "message_id": 4821}}
```
`notify.dry_run: true` → `NOTIFY_DRY_RUN=true`, bot token yok veya kanal `email` (mesaj loglandı, gönderilmedi; `notify_ref="dry-run"`, `message_id: null`).
Hatalar:
| Kod | detail | Durum sonrası |
|-----|--------|---------------|
| 404 | `"Sipariş bulunamadı"` | — |
| 409 | `"Sipariş zaten sent durumunda."` / `"Sipariş zaten rejected durumunda."` | değişmez |
| 502 | `"Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin."` | `approved` (Telegram zaman aşımı 10 sn, ağ/HTTP hatası, `ok:false`); kör tekrar yok, insan tekrar approve eder |

### POST /api/orders/{id}/reject
Gövde yok. `draft|approved → rejected`. Yanıt 200: `Order` (`status: "rejected"`).
409 `"Sipariş zaten sent durumunda."` / `"Sipariş zaten rejected durumunda."`; 404 `"Sipariş bulunamadı"`.

---

## Dışa aktarma

### GET /api/export/sales.csv · GET /api/export/expenses.csv
Sorgu yok (tüm kayıtlar, tarihe göre artan). Yanıt 200:
- `Content-Type: text/csv; charset=utf-8`; gövde UTF-8 BOM ile başlar; ayraç `;`; ondalık virgül, binlik ayracı yok (`1300,00`); satır sonu CRLF; `=`, `+`, `-`, `@`, sekme, CR ile başlayan metin hücrelerine `'` öneki (formül enjeksiyonu).
- `Content-Disposition: attachment; filename="satislar.csv"` / `"giderler.csv"`.
- Başlıklar (satış): `Tarih;Ürün;Adet;Birim Fiyat;Toplam;Kanal` — tarih `YYYY-MM-DD HH:MM` (UTC).
- Başlıklar (gider): `Tarih;Kategori;Tutar;Tedarikçi;Not`.

Örnek satır: `2026-09-13 08:30;PowerBank 20000 mAh;2;650,00;1300,00;magaza`

---

## Öngörüler (ekleme, R-24)

### GET /api/insights
Sorgu yok. Yanıt 200: en çok 5 kart, önem sırası critical > warn > info (aynı önemde kural sırası); boş veri → `[]`:
```json
[
  {"id": "critical-stock", "title": "2 ürün kritik stokta", "body": "PowerBank 20000 mAh (4/8), USB-C Kablo 1m (3/10) yeniden sipariş eşiğinin altında. Tedarik ekranından sipariş taslağı oluşturabilirsiniz.", "severity": "critical", "metric": "critical_count", "change_pct": null},
  {"id": "expense-rise", "title": "Reklam gideri geçen aya göre %40 arttı", "body": "Reklam gideri geçen aya göre %40 arttı (3.200 ₺ → 4.480 ₺).", "severity": "warn", "metric": "expense:reklam", "change_pct": 40.0},
  {"id": "net-change", "title": "Fark (gelir − gider) geçen aya göre %12 arttı", "body": "Bu ay (1–13 Eylül) 41.200 ₺, Ağustos 36.800 ₺.", "severity": "info", "metric": "net", "change_pct": 12.0},
  {"id": "top-product", "title": "En kârlı ürün (tahmini): PowerBank 20000 mAh", "body": "Son 6 ayda 31.200 ₺ tahmini brüt katkı (mevcut birim maliyetle), 130 adet satış.", "severity": "info", "metric": "top_product_profit", "change_pct": null},
  {"id": "channel-share", "title": "Online kanal payı %38 → %42", "body": "Ciroda online payı geçen aya göre +4 puan değişti; kalanı mağaza satışı.", "severity": "info", "metric": "online_share", "change_pct": 4.0}
]
```
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | `critical-stock \| net-change \| expense-rise \| top-product \| channel-share` | kural kimliği |
| title | string | kısa Türkçe başlık (tr-TR sayı biçimi) |
| body | string | tek-iki cümle, şablondan; LLM yok |
| severity | `info \| warn \| critical` | kritik stok → critical; fark düşüşü > %10 → warn; gider artışı > %25 → warn; diğerleri info |
| metric | string | `critical_count`, `net`, `expense:<kategori>`, `top_product_profit`, `online_share` |
| change_pct | number \| null | yüzde (fark/gider) veya puan (kanal); önceki ay verisi yoksa null ve gövde "yeterli veri yok" |

Kurallar (`services/insights.py`): (1) kritik ürünler (en çok 3 ad + "ve N ürün daha"); (2) bu ay vs geçen ay fark, UTC takvim ayları; (3) en çok artan gider kategorisi (mutlak artış); (4) son 6 ayın en yüksek tahmini brüt katkılı ürünü; (5) online kanal payı bu ay vs geçen ay. Sözcükler D16: "fark (gelir − gider)", "tahmini brüt katkı (mevcut birim maliyetle)".

---

## Uç listesi (22)

| # | Yöntem | Yol | Sahip | Kaynak | Durum |
|---|--------|-----|-------|--------|-------|
| 1 | GET | /api/health | Murat | §6 (+scheduler, version) | ✔ |
| 2 | GET | /api/summary | Murat | §6 | ✔ (dönem birleştirme T015) |
| 3 | GET | /api/cashflow/monthly | Murat | §6 | ✔ |
| 4 | GET | /api/analytics/expenses-by-category | Yiğit | §6 | ✔ |
| 5 | GET | /api/analytics/sales-by-product | Yiğit | §6 | ✔ |
| 6 | GET | /api/sales | Murat | §6 (+product_name) | ✔ |
| 7 | POST | /api/sales | Murat | §6 | ✔ |
| 8 | PUT | /api/sales/{id} | Murat | §6 (kısmi) | ✔ |
| 9 | DELETE | /api/sales/{id} | Murat | §6 | ✔ |
| 10 | GET/POST | /api/expenses | Murat | §6 | ✔ |
| 11 | PUT/DELETE | /api/expenses/{id} | Murat | §6 | ✔ |
| 12 | GET | /api/products | Murat | §6 (+supplier_name) | ✔ |
| 13 | PATCH | /api/products/{id} | Murat | §6 | ✔ |
| 14 | POST | /api/assistant/ask | Murat | §6 (+ok, model) | ✔ (`model` T080) |
| 15 | GET | /api/assistant/suggestions | Murat | §6 | ✔ (sıra T081) |
| 16 | POST | /api/agent/check | Ömer | §6 (+skipped) | ✔ |
| 17 | GET | /api/orders | Ömer | §6 | ✔ |
| 18 | GET | /api/orders/{id} | Ömer | ekleme | ✔ |
| 19 | POST | /api/orders/{id}/approve | Ömer | §6 (+notify, notify_ref, 409/502) | ✔ |
| 20 | POST | /api/orders/{id}/reject | Ömer | §6 | ✔ |
| 21 | GET | /api/export/sales.csv · expenses.csv | Yiğit | §6 | ✔ |
| 22 | GET | /api/insights | Yiğit | ekleme | ✔ |
