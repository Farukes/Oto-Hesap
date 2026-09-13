---

description: "OtoHesap MVP görev listesi — Geliştirme Günü (09:00–22:00); 13 Eyl inşası sonrası kalan işler"
---

# Tasks: OtoHesap MVP (Geliştirme Günü)

**Input**: Design documents from `/specs/001-otohesap-mvp/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Anayasa IV gereği her uç için test görevi vardır (isteğe bağlı değil). Testler `LLM_PROVIDER=fake`, `NOTIFY_DRY_RUN=true` ile koşar; gerçek sağlayıcı yalnız `-m live`.

**Organization**: Görevler kullanıcı hikâyesine göre gruplanır; her hikâye bağımsız test edilir. Sahipler AGENTS.md §4 dosya sahipliğidir; saatler AGENTS.md §11 çizelgesi. `[x]` = 13 Eyl itibarıyla depoda mevcut ve testli. D16–D20 ile gelen işler **T078–T092**.

## Format: `[ID] [P?] [Story] [Sahip] Description — dosya yolu`

- **[P]**: Paralel koşabilir (farklı dosya, tamamlanmamış göreve bağımlı değil)
- **[Story]**: US1 Genel bakış · US2 Kayıtlar · US3 Asistan · US4 Tedarik · US5 Stok · US6 Öngörü · US7 Dönem
- **[Sahip]**: Murat · Ömer · Yiğit · Kutay · Herkes
- Dosya yolları depo köküne göre

## Path Conventions

- API: `apps/api/app/{routers,services,schemas}/`, testler `apps/api/tests/`, soru bankası `apps/api/app/data/soru_bankasi.json`
- Web: `apps/web/app/<rota>/page.tsx`, `apps/web/components/`, `apps/web/lib/`
- Veri: `data/seed.py`; belgeler `docs/`; betikler `scripts/`; komutlar `Makefile`

---

## Phase 1: Kurulum (iskelet — tamamlandı, main'de)

**Purpose**: Herkesin üstüne kod yazacağı iskelet.

- [x] T001 [Murat] `uv` projesi ve bağımlılıklar — apps/api/pyproject.toml
- [x] T002 [Murat] Ortam ayarları (`anthropic|gemini|groq|fake`, ajan, Telegram, `NOTIFY_DRY_RUN`, `BUSINESS_NAME`, CORS, `LOG_LEVEL`) — apps/api/app/config.py
- [x] T003 [Murat] SQLAlchemy motorları: yazar + salt-okur (`default_transaction_read_only=on`, `statement_timeout=5000`) — apps/api/app/db.py
- [x] T004 [Murat] ORM modelleri `docs/schema.sql` ile birebir (`notify_ref` dâhil); `Product.is_critical` — apps/api/app/models.py
- [x] T005 [Murat] Uygulama girişi: CORS, istek log satırı, 500 Türkçe gövde, router kayıtları, `/api/health`, lifespan — apps/api/app/main.py
- [x] T006 [Murat] Router dosyaları (`summary, sales, expenses, products, analytics, assistant, orders, agent, export, insights`) — apps/api/app/routers/*.py
- [x] T007 [Murat] Tek LLM adaptörü (`anthropic | gemini | groq | fake`) ve testi — apps/api/app/services/llm.py, apps/api/tests/test_llm_adapter.py
- [x] T008 [Murat] APScheduler iskeleti (`run_check` çağırır) — apps/api/app/services/scheduler.py
- [x] T009 [Murat] Test altyapısı: ayrı test DB (`TEST_DB_NAME`), TRUNCATE, `small_data` fixture; health testi — apps/api/tests/conftest.py, apps/api/tests/test_health.py
- [x] T010 [Murat] CI, kurulum betiği, AI-imza hook'u, `.env.example`, `.gitignore`, PR şablonu, `Makefile`, `render.yaml`, `Dockerfile` — .github/workflows/ci.yml, scripts/setup.sh, scripts/hooks/commit-msg, .env.example, .gitignore, .github/PULL_REQUEST_TEMPLATE.md, Makefile, render.yaml, apps/api/Dockerfile
- [x] T011 [Murat] Veri modeli DDL + görünüm + indeksler + `notify_ref` + `ux_open_order_per_product` + RO rol/sütun grant yorumları — docs/schema.sql
- [x] T012 [Kutay] Next.js 16 + Tailwind 4 + Recharts 3 iskeleti (Bun) — apps/web/package.json, apps/web/app/globals.css

---

## Phase 2: Temel (engelleyici ön koşullar)

**Purpose**: Hikâyelerin canlı ortamda çalışması için gereken ortak altyapı. ⚠️ T013 olmadan canlı demo yok; T014–T015 sözleşme tutarlılığı.

- [ ] T013 [Murat] Neon: `docs/schema.sql` uygula (idempotent; `notify_ref`, tekil indeks); `otohesap_ro` rolünü aç ve **sütun düzeyi grant** (`REVOKE SELECT ON suppliers …; GRANT SELECT (id, name, contact_channel, lead_time_days) …`, D19); `DATABASE_URL` / `DATABASE_URL_RO`'yu Neon davetiyle paylaş — docs/schema.sql (Neon SQL editörü), quickstart.md §3
- [ ] T014 [Murat] `RequestValidationError` handler: 422 gövdesi tek Türkçe `detail` string'i (FastAPI varsayılan listesi değil); summary/orders `Literal` doğrulamaları da bundan geçer — apps/api/app/main.py, apps/api/tests/test_health.py (ek test)
- [x] T015 [Murat] Dönem tanımını birleştir (R-17): tek yardımcı (`schemas/analytics.py::period_bounds`), yarı açık `[start, end)`, `month` = bu ay, `quarter` = son 3 takvim ayı, `half` = son 6 takvim ayı (1 Nis); `routers/summary.py` ve `_CASHFLOW_SQL` aynı fonksiyonu kullansın; `test_summary.py` ve `test_analytics.py` beklentileri güncellensin — apps/api/app/schemas/analytics.py, apps/api/app/routers/summary.py, apps/api/tests/test_summary.py, apps/api/tests/test_analytics.py
- [x] T016 [Murat] `.env.example`: `NOTIFY_DRY_RUN`, `AGENT_SCHEDULER_ENABLED`, `BUSINESS_NAME`, Groq satırları — .env.example
- [x] T017 [Murat] Pydantic şemaları: `Decimal → float`, ISO tarih, `from_attributes` — apps/api/app/schemas/core.py, apps/api/app/schemas/analytics.py
- [x] T018 [Yiğit] Sentetik veri: Faker(tr_TR) + NumPy rng(42), 2026-04-01…2026-09-13, `--reset`, psycopg COPY; tam 2 kritik, tam 1 eşiğin 1 üstünde, powerbank tek lider; özet basar — data/seed.py
- [x] T019 [Yiğit] Seed testleri: sayılar, determinizm, kategoriler/marjlar, tedarikçiler, stok seviyeleri, kâr lideri, sabit giderler — apps/api/tests/test_seed.py
- [x] T020 [Ömer] `services/notify.py`: `send_message(supplier, text)` / `send_telegram(chat_id, text)` → `{ok, dry_run, channel, message_id}`; dry-run; 10 sn zaman aşımı; token loglanmaz/maskelenir; `NotifyError` — apps/api/app/services/notify.py
- [x] T021 [Ömer] Notify testleri: dry-run, token yok, e-posta kanalı, HTTP/ağ/zaman aşımı hataları, token maskeleme — apps/api/tests/test_notify.py
- [x] T022 [Kutay] API istemcisi: 22 uç tipli; ağ hatasında mock; 4xx/5xx `ApiError` Türkçe `detail` — apps/web/lib/api.ts, apps/web/lib/errors.ts, apps/web/lib/mock-mode.ts, apps/web/lib/mocks/store.ts, apps/web/lib/mocks/*.json
- [x] T023 [Kutay] Biçimlendirme: tr-TR para/yüzde, Europe/Istanbul tarih/saat — apps/web/lib/format.ts
- [x] T024 [Kutay] Uygulama kabuğu: sol menü 5 rota, üst başlık, mobil menü, "mock veri" rozeti, "Sentetik demo verisi · Nisan–Eylül 2026" alt bilgisi, `lang="tr"` — apps/web/app/layout.tsx, apps/web/components/AppShell.tsx, apps/web/components/Sidebar.tsx, apps/web/components/MockBadge.tsx
- [x] T025 [Kutay] Ortak bileşenler: EmptyState, KpiCard, DataTable, Modal, Badge, SqlBlock, InsightCard, ui — apps/web/components/*.tsx

**Checkpoint 1 — 10:30**: T013 Neon'da uygulanmış, T014–T015 PR'da; herkes `git pull --rebase origin main`.

---

## Phase 3: User Story 1 — Genel bakış panosu (Priority: P1) 🎯 MVP

**Goal**: 4 KPI (Gelir, Gider, Fark, Kritik ürün) + "Aylık gelir–gider" çubuğu + gider pastası + "son güncelleme" damgası, gerçek veriden; D16 etiketleri.

**Independent Test**: Seed yüklüyken `GET /api/summary` seed özetiyle aynı rakamları döner; ana ekran 2 sn içinde tüm parçalarıyla yüklenir; boş DB'de "Veri yok"; ekranda "net kâr" / "nakit akışı" yazmaz.

### Tests for User Story 1

- [x] T026 [P] [US1] [Murat] Summary testleri: `small_data` sabit rakamlar; `period` varyasyonları; geçersiz dönem 422; boş DB; aylık seri 6 ay sıfır dolgulu — apps/api/tests/test_summary.py
- [x] T027 [P] [US1] [Yiğit] Analytics testleri: kategori payları; ürün sıralaması; dönem sınırları yarı açık; `top` doğrulama; boş DB — apps/api/tests/test_analytics.py

### Implementation for User Story 1

- [x] T028 [US1] [Murat] `GET /api/summary?period` — apps/api/app/routers/summary.py
- [x] T029 [US1] [Murat] `GET /api/cashflow/monthly` (son 6 ay, sıfır dolgulu) — apps/api/app/routers/summary.py
- [x] T030 [P] [US1] [Yiğit] `GET /api/analytics/expenses-by-category?period` (`share` yüzde) — apps/api/app/routers/analytics.py
- [x] T031 [US1] [Yiğit] `GET /api/analytics/sales-by-product?period&top` (ciro sırası; `profit` = tahmini brüt katkı) — apps/api/app/routers/analytics.py
- [ ] T032 [P] [US1] [Kutay] Grafik bileşenleri: aylık gelir–gider çubuğu (Recharts), kategori pastası; boş dizi → EmptyState — apps/web/components/CashflowChart.tsx, apps/web/components/ExpensePie.tsx
- [ ] T033 [US1] [Kutay] Genel Bakış sayfası: 4 KPI ("Gelir", "Gider", "Fark (Gelir − Gider)", "Kritik ürün") + "Son güncelleme" + çubuk ("Aylık gelir–gider") + pasta; boilerplate kaldır — apps/web/app/page.tsx

**Checkpoint 2 — 13:00**: pano gerçek veriyle; demo turu 1 (adım 1).

---

## Phase 4: User Story 2 — Kayıt giriş/çıkış (Priority: P1) 🎯 MVP

**Goal**: Satış/gider listele, ara, ekle, düzenle, sil; satış stoğu düşürür; ürün seçimi `sale_price` önyükler.

**Independent Test**: Gider (reklam, 4.500) eklenir → listede ve panoda görünür; eşiğin 1 üstündeki üründen 1 satış → ürün kritik olur; 400/404/422 Türkçe.

### Tests for User Story 2

- [x] T034 [P] [US2] [Murat] Kayıt testleri: satış/gider CRUD, `total`, stok düşümü/iadesi/farkı/ürün değişimi, 400 stok yetersiz, 404, 422, sayfalama ve `q` — apps/api/tests/test_sales_expenses.py

### Implementation for User Story 2

- [x] T035 [US2] [Murat] `GET /api/products` (`is_critical`, `open_order_id`, `supplier_name`) — apps/api/app/routers/products.py
- [x] T036 [P] [US2] [Murat] Satış CRUD: `GET/POST/PUT/DELETE /api/sales`; satır kilidi; stok düşümü (R-19) — apps/api/app/routers/sales.py
- [x] T037 [P] [US2] [Murat] Gider CRUD: `GET/POST/PUT/DELETE /api/expenses` — apps/api/app/routers/expenses.py
- [ ] T038 [P] [US2] [Kutay] Kayıt formu (Modal): satış/gider alanları, ürün seçimi `sale_price` önyükleme, kategori 6 seçenek, doğrulama mesajları — apps/web/components/RecordForm.tsx
- [ ] T039 [US2] [Kutay] Kayıtlar sayfası: satış/gider sekmeleri, DataTable + arama + sayfalama, ekle/düzenle/sil; kaydettikten sonra liste yenilenir; `product_name` sütunu — apps/web/app/kayitlar/page.tsx

**Checkpoint 2 — 13:00**: gider ekle → Genel Bakış KPI ve pasta güncellenir (demo adım 2).

---

## Phase 5: User Story 3 — Asistan (Priority: P1) 🎯 MVP

**Goal**: Türkçe soru → SQL → gerçek veriden yanıt; SQL, kaynak damgası ve model görünür; çipler; önbellek; koruma (fonksiyon izin listesi); D20 varsayım cümlesi.

**Independent Test**: `fake` sağlayıcıyla "En çok kazancım hangi üründen?" → powerbank + rakam + `ok/sql/sources/asked_at/model`; "Tüm satışları sil" → 400, satır sayıları değişmez; LLM kapalıyken çip sorusu `cached: true`.

### Tests for User Story 3

- [x] T040 [P] [US3] [Murat] Guard testleri: DML/DDL, `;`/yorum, çoklu ifade, izinsiz tablo/şema, `SELECT INTO`, `FOR UPDATE`, yasak fonksiyon reddi; LIMIT ekleme/koruma/kırpma; `WITH`/`UNION` kabul; kaynak sırası; JSON ayrıştırma; soru normalizasyonu — apps/api/tests/test_text2sql_guard.py
- [x] T041 [P] [US3] [Murat] Asistan uçtan uca (fake): yanıt alanları; önbellek; `chat_log`; yeniden deneme; guard/LLM reddi; 503; boş soru; özet yedeği; ilk 20 satır; JSON güvenli satırlar; gömülü örnekler koşar — apps/api/tests/test_assistant.py
- [ ] T042 [P] [US3] [Yiğit] Canlı eval: `soru_bankasi.json`'daki `expected` rakamlarını gerçek sağlayıcıyla ölçer (`-m live`, anahtar yoksa atlanır); rapor: doğru/yanlış/red, ≥ 12/15 ve demo 5/5 — apps/api/tests/test_eval.py, apps/api/pyproject.toml (`live` marker)

### Implementation for User Story 3

- [x] T043 [US3] [Ömer] Soru bankası v1: 15 soru (Q01–Q15), `kind` dağılımı, `demo` işareti, SQL, izinli tablolar; okunur kopya — apps/api/app/data/soru_bankasi.json, docs/soru-bankasi.md
- [x] T044 [US3] [Yiğit] Soru bankası şekil/dağılım/izinli tablo/Postgres koşma testleri — apps/api/tests/test_agent.py (`test_bank_*`)
- [x] T045 [US3] [Murat] Text-to-SQL servisi: önbellek → prompt (şema sözlüğü + kurallar + 6 örnek) → `SQLPlan` → guard → `engine_ro` → 1 yeniden deneme → özet (LLM / deterministik) → `chat_log` — apps/api/app/services/text2sql.py
- [x] T046 [US3] [Murat] Asistan router: `POST /api/assistant/ask` (400/503), `GET /api/assistant/suggestions` — apps/api/app/routers/assistant.py, apps/api/app/schemas/assistant.py
- [ ] T047 [P] [US3] [Kutay] Sohbet bileşenleri: yanıt balonu, katlanır SqlBlock, sonuç tablosu (ilk 20 satır; `rows` nesne listesi), "Kaynak: satışlar, ürünler · 13 Eyl 10:12" (İngilizce tablo → Türkçe etiket), "önbellek" rozeti, model adı — apps/web/components/ChatBubble.tsx
- [ ] T048 [US3] [Kutay] Asistan sayfası: çipler (`suggestions`), giriş kutusu, "Asistan yalnızca okur" notu, 400/503 sakin hata balonu, `ok:false` yanıtı, yükleniyor — apps/web/app/asistan/page.tsx

**Checkpoint 3 — 16:30**: asistan çipten 5 soru; SQL ve model görünür (demo adım 3–4).

---

## Phase 6: User Story 4 — Tedarik ajanı (Priority: P1) 🎯 MVP

**Goal**: Kritik stok → taslak → onay → Telegram; DB düzeyinde tekrar koruması; `notify_ref`; 502'de `approved` kalır; "Gönderildi · teslim alındı değil".

**Independent Test**: Seed'de `POST /api/agent/check` → 2 taslak, ikinci çağrı `created: 0` + 2 `skipped`; approve (dry-run) → `sent`, `sent_at`, `notify_ref="dry-run"`, `notify.dry_run=true`; ikinci approve 409; gönderim hatası → `approved` + 502.

### Tests for User Story 4

- [x] T049 [P] [US4] [Ömer] Ajan testleri: tam 1 taslak (`small_data`); ikinci çağrı `skipped`; elle taslak/doğrudan insert tekil indeksle çakışır; `IntegrityError` sonrası döngü sürer; açık durumlar bloke eder; `rejected` açık değil; tedarikçisiz atlanır; `qty ≥ 1`; kritik yok; tr-TR tutar; uç — apps/api/tests/test_agent.py
- [x] T050 [P] [US4] [Ömer] Sipariş testleri: liste/filtre/boş; tek sipariş/404; approve dry-run → sent; çift approve 409; notify hatası → approved + 502 → tekrar approve → sent; tedarikçi ve mesaj iletilir; reject draft/approved; sent reject 409 — apps/api/tests/test_orders.py

### Implementation for User Story 4

- [x] T051 [US4] [Ömer] Ajan servisi `run_check(db) -> {created, drafts, skipped}`: savepoint + `ux_open_order_per_product`; `qty = max(1, target − stock)`; `est_amount`; mesaj şablonu; karar logları — apps/api/app/services/agent.py
- [x] T052 [US4] [Ömer] `POST /api/agent/check` — apps/api/app/routers/agent.py
- [x] T053 [US4] [Ömer] Sipariş router: `GET /api/orders?status`, `GET /api/orders/{id}`, `POST approve` (approved commit → `send_message` → sent + `notify_ref`; 409 "Sipariş zaten {status} durumunda."; 502), `POST reject` — apps/api/app/routers/orders.py, apps/api/app/schemas/orders.py
- [x] T054 [US4] [Ömer] Zamanlayıcı `run_check`'i çağırır, log "ajan: N kritik ürün, N taslak, N atlandı"; `AGENT_SCHEDULER_ENABLED=false` ile kapalı — apps/api/app/services/scheduler.py
- [ ] T055 [P] [US4] [Kutay] Sipariş kartı: ürün, miktar, tedarikçi, tahmini tutar, mesaj önizleme ("DEMO · sentetik sipariş #id"), Onayla/Reddet (tek tık; istek sürerken devre dışı), "Gönderildi <saat> · teslim alındı değil", `notify.dry_run` → "gönderildi (simülasyon)", 502 → "gönderilemedi, tekrar dene", 409 → listeyi yenile — apps/web/components/OrderCard.tsx
- [ ] T056 [US4] [Kutay] Tedarik sayfası: "Şimdi kontrol et" (sonuçta `created` ve `skipped` nedenleri: "açık sipariş var" / "tedarikçi yok"), durum sayaçları (Bekliyor / Onaylandı / Gönderildi / Reddedildi), kart listesi; D18 notu ("zamanlayıcı 10 dk'da bir; sunucu uyuyorsa bu tuş") — apps/web/app/tedarik/page.tsx

**Checkpoint 3 — 16:30**: onayla → telefonda mesaj (demo adım 6).

---

## Phase 7: User Story 5 — Stok ekranı (Priority: P2) — 16:30–19:00

**Goal**: Ürün tablosu; kritik kırmızı; rozet ("taslak bekliyor" / "sipariş yolda"); eşik düzenleme.

**Independent Test**: Tam 2 kırmızı satır; `reorder_point` stoğun üstüne çekilince satır kırmızı olur ve `summary.critical_count` artar; negatif 422.

- [x] T057 [US5] [Murat] `PATCH /api/products/{id}` + testleri (bayraklar, en yeni açık sipariş, doğrulama, 404) — apps/api/app/routers/products.py, apps/api/tests/test_products.py
- [ ] T058 [US5] [Kutay] Stok sayfası: DataTable, kritik satır kırmızı, satır içi eşik/hedef düzenleme (PATCH), rozet (T088), "sipariş yolda ≠ teslim alındı" ipucu — apps/web/app/stok/page.tsx

---

## Phase 8: User Story 6 — Öngörü kartları (Priority: P2) — 16:30–19:00

**Goal**: Panoda en çok 5 kural tabanlı kart; D16 sözcükleri.

**Independent Test**: `GET /api/insights` seed ile `critical-stock` başta; reklam artınca `expense-rise.change_pct` değişir; boş DB → `[]`.

- [x] T059 [P] [US6] [Yiğit] Öngörü testleri: biçimleme, `small_data` kartları, boş DB, gider artışı ve fark kuralları — apps/api/tests/test_insights.py
- [x] T060 [US6] [Yiğit] Öngörü servisi: 5 kural, önem sırası, tr-TR biçim, "fark (gelir − gider)" / "tahmini brüt katkı" sözcükleri — apps/api/app/services/insights.py
- [x] T061 [US6] [Yiğit] `GET /api/insights` — apps/api/app/routers/insights.py, apps/api/app/schemas/analytics.py
- [ ] T062 [US6] [Kutay] Öngörü kartlarını Genel Bakış'a yerleştir (InsightCard; önem rengi; boş liste → bölüm gizli) — apps/web/app/page.tsx

---

## Phase 9: User Story 7 — Dönem filtresi (Priority: P3) — 16:30–19:00

**Goal**: "Bu ay / 3 ay / 6 ay" sekmeleri KPI ve pastayı aynı dönem tanımıyla gösterir (T015'e bağlı).

**Independent Test**: Sekme değişince `summary` ve `expenses-by-category` aynı `period` ile çağrılır; üç dönem farklı rakam verir; KPI ile pasta aynı aralığı kullanır.

- [ ] T063 [US7] [Kutay] Dönem sekmeleri bileşeni; seçim URL sorgusunda (`?period=`); varsayılan 6 ay — apps/web/components/PeriodTabs.tsx, apps/web/app/page.tsx

---

## Phase 10: Cila, D16–D20 uyumu, yayın, prova (13:30–22:00; 19:00 özellik dondurma)

**Purpose**: Demo senaryosunu uçtan uca güvenceye almak; yeni kararları koda ve arayüze işlemek; canlı yayın; sunum.

> **Render Free notu (D18):** ücretsiz katmanda API 15 dk boşta uyur ve süreç içi zamanlayıcı durur. Demoda "Şimdi kontrol et" tuşu aynı `run_check` fonksiyonunu çağırır; bu, zamanlayıcının yerine gizlenen bir otomasyon değildir ve sunumda saklanmaz. Demodan 10 dk önce `make warmup`. 7/24 kontrol istenirse Render 7 $/ay instance — final sonrası karar (Murat).

### CSV ve README
- [x] T064 [P] [Yiğit] CSV dışa aktarma: BOM, `;`, ondalık virgül, CRLF, Türkçe başlık, formül enjeksiyonu koruması, `attachment` — apps/api/app/routers/export.py
- [x] T065 [P] [Yiğit] CSV testleri — apps/api/tests/test_export.py
- [ ] T066 [Kutay] Kayıtlar'a "Dışa aktar (CSV)" butonu (`exportUrl`) — apps/web/app/kayitlar/page.tsx
- [x] T067 [Murat] Isıtma betiği: health → summary (DB) → suggestions → ilk çiple ask (LLM); çıkış kodu — scripts/warmup.sh
- [ ] T068 [P] [Murat] README: `make` komutları, Neon/Render/Vercel adımları, canlı link, 3 görsel, D16 sözlüğüne uygun yetenek tablosu ("aylık gelir–gider") — README.md
- [ ] T069 [P] [Yiğit] README görselleri (pano, asistan, tedarik; Kutay ekran görüntüsü verir) — docs/img/

### D19/D20 — asistan (Murat)
- [x] T078 [Murat] Guard'da fonksiyon **izin listesi** (D19): yalnız sum, count, avg, min, max, coalesce, round, date_trunc, date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs; diğer her fonksiyon (özellikle `pg_*`, `set_config`) red; CTE içinde DML testi (E14), `SELECT pg_sleep(60)` testi (E15) — apps/api/app/services/text2sql.py, apps/api/tests/test_text2sql_guard.py
- [x] T079 [Murat] `suppliers.contact_address`'i prompt şemasından (`SCHEMA_DOC`) çıkar; RO rolde sütun düzeyinde kapalı olduğunu test et (`engine_ro` ile `SELECT contact_address` → hata; yerelde rol yoksa atla) — apps/api/app/services/text2sql.py, apps/api/tests/test_assistant.py
- [x] T080 [Murat] Yanıta `model` alanı (D19): `llm.complete` çağrısında kullanılan sağlayıcı/model adı (`"anthropic/claude-haiku-4-5"`, `"fake"`); önbellekte özet için kullanılan model ya da `"cache"` — apps/api/app/services/llm.py, apps/api/app/services/text2sql.py, apps/api/app/schemas/assistant.py, apps/api/tests/test_assistant.py
- [ ] T082 [Murat] D20 varsayım cümlesi: "kâr/kazanç" sorularında özet "mevcut birim maliyetle tahmini brüt katkı" ibaresini içerir (SUMMARY_SYSTEM kuralı + deterministik özette ek cümle); prompt kural 3'e "tahmini brüt katkı" adı — apps/api/app/services/text2sql.py, apps/api/tests/test_assistant.py

### D17/D18 — ajan ve soru bankası (Ömer, Yiğit)
- [x] T081 [Ömer] Çip sırası demo senaryosuyla aynı olsun: bankada `order` alanı ya da `demo` soruları demo sırasına göre yeniden diz (Q09 → Q06 → Q07 → Q03 → Q02); `text2sql.suggestions()` sırayı korusun; `test_bank_demo_questions_verbatim` güncellensin — apps/api/app/data/soru_bankasi.json, docs/soru-bankasi.md, apps/api/app/services/text2sql.py, apps/api/tests/test_agent.py
- [x] T083 [Yiğit] Seed'de Telegram tedarikçisinin `contact_address`'i `TELEGRAM_DEFAULT_CHAT_ID` ortam değişkeninden (yoksa `TELEGRAM_CHAT_ID` yer tutucu + uyarı); `data/README.md` ile nasıl güncelleneceği — data/seed.py, data/README.md
- [ ] T084 [Yiğit] Soru bankası beklenen rakamları: `make seed` çıktısıyla Q01–Q13 `expected` alanlarını doldur (JSON + md); Q13 boş mu doğrula — apps/api/app/data/soru_bankasi.json, docs/soru-bankasi.md
- [x] T085 [Ömer] Mesaj şablonu D17: "DEMO · sentetik sipariş #id — … — OtoHesap"; tr-TR tutar — apps/api/app/services/agent.py
- [ ] T086 [Ömer] APScheduler sertleştirme (D18/SONUC-1 A4): `max_instances=1`, `coalesce=True`, `misfire_grace_time`; log satırında "Render uyuyorsa zamanlayıcı durur" uyarısı yok, sadece sonuç — apps/api/app/services/scheduler.py

### Web — D16/D17 etiketleri ve sözleşme hizası (Kutay)
- [ ] T087 [Kutay] Tedarik ekranı D17: "Gönderildi <saat> · teslim alındı değil"; `notify.dry_run` → "gönderildi (simülasyon)"; 502 → "gönderilemedi, tekrar dene" (sipariş `approved` görünür); 409 → listeyi yenile; `skipped` nedenleri Türkçe — apps/web/app/tedarik/page.tsx, apps/web/components/OrderCard.tsx
- [ ] T088 [Kutay] Stok rozeti: `open_order_id` + `listOrders()` eşlemesiyle "taslak bekliyor" (`draft`) / "onaylandı, gönderilecek" (`approved`) / "sipariş yolda" (`sent`) — apps/web/app/stok/page.tsx
- [ ] T091 [Kutay] D16 etiketleri: "Fark (Gelir − Gider)" (net kâr değil), "En kârlı ürün (tahmini)" + "mevcut birim maliyetle", "Aylık gelir–gider" (nakit akışı değil), "Sentetik demo verisi"; metin araması: "net kâr", "nakit akışı" 0 sonuç — apps/web/app/page.tsx, apps/web/components/*.tsx
- [ ] T092 [Kutay] `types.ts` hizası: `Sale.product_name`, `Product.supplier_name`, `Order.product_name/supplier_name/supplier_channel/notify_ref`, `ApproveResult = Order & {notify}`, `AgentCheckResult.skipped`, `AssistantAnswer.rows: Record<string, unknown>[]`, `ok`, `model`; mock store aynı şekle — apps/web/lib/types.ts, apps/web/lib/mocks/store.ts, apps/web/lib/mocks/*.json

### Sözleşme, cila, yayın
- [ ] T090 [Murat] AGENTS.md §6 PR: R-24 eklemeleri (`skipped`, `notify`, `notify_ref`, `product_name/supplier_name`, `ok/model`, `GET /api/orders/{id}`, `GET /api/insights`, 409/502 metinleri) + WhatsApp duyurusu; DECISIONS'a gerekirse satır — AGENTS.md, docs/DECISIONS.md
- [ ] T070 [Kutay] Her ekranda boş veri / yükleniyor / hata; mobil menü; `bun run lint` ve `bun run build` temiz — apps/web/app/**, apps/web/components/**
- [ ] T071 [Murat] Cila turu: tüm hata gövdeleri Türkçe (`detail` string), asistan/ajan karar logları; ekip PR'larının incelemesi (15 dk SLA) — apps/api/app/**
- [ ] T072 [Murat] API yayını (19:00–20:00): Render blueprint (`render.yaml`), `sync: false` env'ler panelden, `CORS_ORIGINS` = Vercel alan adı, `NOTIFY_DRY_RUN=false`; canlı `/api/health` yeşil — Render panosu
- [ ] T073 [Kutay] Web yayını (19:00–20:00): Vercel Root Directory `apps/web`, `NEXT_PUBLIC_API_URL` = Render; gizli pencerede demo senaryosu — Vercel panosu
- [ ] T089 [Murat] Isıtma betiğine Telegram `getMe` adımı (token varsa; Murat kartı) — scripts/warmup.sh
- [ ] T074 [P] [Ömer] Demo senaryosu final (tıklama tıklama, saniye saniye; adım 6'da "teslim alındı değil" cümlesi), sunum konuşma metni (9 slayt), 10 jüri sorusu (D16–D18 cümleleri dâhil) — docs/demo-senaryosu.md, docs/sunum-metni.md
- [ ] T075 [P] [Yiğit] Slaytlar: 9 slayt PowerPoint (lacivert + yeşil); "Fark" net kâr denmez; "tahmini brüt katkı"; "sentetik demo"; Render uyku dürüstlüğü; mimari diyagram; ekran görüntüleri; yol haritası — docs/sunum/OtoHesap.pptx
- [ ] T076 [Ömer] Prova 1 (20:00–21:00): kronometre; ekran kaydı 3 dk video → USB + Drive; telefon hazır — docs/demo-senaryosu.md
- [ ] T077 [Herkes] Prova 2 (21:00–22:00): düzeltmeler, slaytlar final — docs/
- [ ] T093 [Murat] `v0.1.0` etiketi; `main` CI yeşil — (git etiketi)
- [ ] T094 [Herkes] Bitti tanımı (AGENTS.md §10): sözleşme birebir · Türkçe hata · boş veri · lint/test/CI · tip ipuçları, `any` yok · loglar · `.env.example` ve README güncel · demo senaryosu bozulmamış · sır ve AI imzası yok — (PR şablonu)

---

## Checkpoint eşlemesi (AGENTS.md §11)

| Saat | Checkpoint | Tamamlanmış olmalı |
|------|------------|--------------------|
| **10:30** | Neon hazır, sözleşme tutarlı, herkes rebase | T013, T014, T015 (PR); T090 taslak |
| **11:00** | Seed Neon'da | `make seed` Neon'a; T083, T084 → WhatsApp'a özet rakamlar |
| **13:00** | Pano gerçek veriyle; demo turu 1 | T032, T033 (US1); T038, T039 (US2); T091 etiketler; T092 tipler |
| **15:00** | approve → telefon | T087 (Tedarik ekranı D17), T055, T056; T086; gerçek chat_id (T083) |
| **16:30** | Asistan 5 soru + ajan onay → mesaj; demo turu 2 | T047, T048 (US3); T078–T082 (D19/D20); T081 çip sırası; T042 canlı eval |
| **19:00** | ÖZELLİK DONDURMA | T058, T088 (US5), T062 (US6), T063 (US7), T066 (CSV), T070–T071; sonrası yalnız hata düzeltme |
| **20:00** | Yayın | T068–T069, T072–T073, T089 |
| **21:00** | Prova 1 + video | T074–T076 |
| **22:00** | Prova 2, `v0.1.0`, durulur | T077, T093, T094 |

---

## Dependencies & Execution Order

### Phase Dependencies

- **Kurulum (Phase 1)**: tamamlandı.
- **Temel (Phase 2)**: T013 (Neon) → canlı demo ve T042 canlı eval. T014 → tüm 422 gövdeleri. T015 → T063 (dönem sekmeleri) ve US1 KPI/pasta tutarlılığı. T020–T025 tamamlandı → web sayfaları başlayabilir.
- **Hikâyeler (Phase 3–9)**: API tarafı tamamlandı; web sayfaları T022–T025 üstüne paralel; öncelik P1 → P2 → P3.
- **Cila (Phase 10)**: T078–T082 birbirinden bağımsız (aynı dosya `text2sql.py` → Murat sırayla); T087/T088/T091/T092 web; T090 sözleşme PR'ı T092'den önce merge edilmeli ki tipler tek kaynağa baksın; yayın (T072–T073) tüm P1'lere; provalar yayına bağlı.

### User Story Dependencies

- **US1 Genel bakış**: T032 → T033; T015 → KPI/pasta aynı aralık; T091 etiketler; T062 (öngörü) ve T063 (dönem) aynı sayfaya eklenir.
- **US2 Kayıtlar**: T035 (✔) → T038 (ürün seçimi); T038 → T039; T066 sonra.
- **US3 Asistan**: T045/T046 (✔) → T047 → T048; T080 `model` alanı → T047 model rozeti; T081 çip sırası → demo senaryosu; T084 rakamlar → T042.
- **US4 Tedarik**: T051–T053 (✔) → T055 → T056 → T087; T083 gerçek chat_id → telefon demosu; T086 bağımsız.
- **US5 Stok**: T035/T057 (✔) → T058 → T088 (listOrders eşlemesi).
- **US6 Öngörü**: T059–T061 (✔) → T062.
- **US7 Dönem**: T015 → T063.

### Within Each User Story

- Testler önce yazılır ve implementasyondan önce başarısız olur (Anayasa IV); mevcut API testleri yeşil kalır.
- Şema/model değişmez (Anayasa V; `models.py` yalnız Murat).
- Web sayfası API'ye `lib/api.ts` üzerinden bağlanır; mock yalnız ağ hatasında.

### Parallel Opportunities

- Phase 2'de T013 / T014 / T015 Murat'ta sıralı; diğer üç kişi web ve veri işlerinde paralel.
- Murat: T014 → T015 → T078 → T079 → T080 → T082 (hepsi `text2sql.py`/`summary.py`; aynı dosya → [P] değil). Ömer: T081, T086, T074. Yiğit: T083, T084, T042, T075. Kutay: T032/T033 → T038/T039 → T047/T048 → T055/T056/T087 → T058/T088 → T062/T063 → T091/T092/T070.
- Test görevleri [P] kendi router'ından bağımsız dosyadadır.

---

## Parallel Example: Checkpoint 1 → 2 (10:30–13:00)

```bash
# Murat
T014 422 Türkçe handler                    apps/api/app/main.py
T015 Dönem birleştirme                     apps/api/app/schemas/analytics.py, routers/summary.py
T090 AGENTS §6 PR                          AGENTS.md
# Yiğit
T083 Seed chat_id env                      data/seed.py
T084 Soru bankası rakamları                apps/api/app/data/soru_bankasi.json
# Ömer
T081 Çip sırası                            apps/api/app/data/soru_bankasi.json (Yiğit ile koordine)
T086 APScheduler sertleştirme              apps/api/app/services/scheduler.py
# Kutay
T032/T033 Genel Bakış                      apps/web/app/page.tsx
T038/T039 Kayıtlar                         apps/web/app/kayitlar/page.tsx
```

---

## Implementation Strategy

### MVP kapsamı = US1–US4

Demo senaryosunun 7 adımı yalnız US1 (adım 1), US2 (adım 2), US3 (adım 3–4) ve US4 (adım 5–6; Stok ekranının kırmızı satırı US5'te ama `is_critical` US2'de gelir) ile döner. API tarafı bugün hazır; 16:30'da web sayfaları bu dördü gösteriyorsa demo yapılabilir; US5–US7 19:00'a kadar eklenir, eklenemezse yol haritası slaydına gider.

### Incremental Delivery

1. Phase 2 → Neon + sözleşme tutarlılığı (10:30), seed Neon'da (11:00)
2. US1 + US2 web → pano gerçek, gider ekle (13:00, demo turu 1)
3. US4 web + gerçek chat_id → approve + Telegram (15:00)
4. US3 web + D19/D20 → asistan 5 soru (16:30, demo turu 2)
5. US5, US7, CSV, US6, D16 etiketleri → 19:00 dondurma
6. Yayın → prova ×2 → `v0.1.0`

### Parallel Team Strategy

Dört sahip, dört dal, dosya sahipliği AGENTS.md §4. Çakışma noktaları (`models.py`, `schema.sql`, `main.py`) yalnız Murat; `soru_bankasi.json` Ömer + Yiğit koordineli. 45 dk ilerleme yoksa WhatsApp; 15 dk içinde eşleşme.

---

## Notes

- [P] = farklı dosya, tamamlanmamış göreve bağımlı değil; aynı dosyaya iki görev [P] değildir.
- Her görev sonunda: `make test` / `make lint` → `git add -p` → commit (AI imzası yok) → küçük PR (≤ 400 satır) → "PR açık" mesajı.
- Sözleşme dışı uç/alan gerekiyorsa önce contracts/api.md ve research.md güncellenir, sonra AGENTS.md §6 PR'ı + duyuru (T090).
- 19:00'dan sonra yeni görev açılmaz; yalnız hata düzeltme.
