# Research: OtoHesap MVP — kararlar ve gerekçeler

**Faz**: 0 | **Tarih**: 2026-09-13 (D16–D20 sonrası güncellendi) | **Kaynaklar**: `docs/DECISIONS.md` (D1–D20), `docs/research/KONTROL-2026-09-13.md` (kontrol notu 1 ve 2), `docs/research/aksiyon-listesi.md`, `docs/research/katalog-3-grup-analiz.md`, `docs/research/SONUC-chatgpt-2026-09-13.md`, `docs/research/SONUC-1-ChatGPT.md` (A3, A4, A8), `AGENTS.md` §3–§7

Her madde: **Karar / Gerekçe / Alternatifler / Kaynak**. R-01…R-16 ve R-25…R-29 alınmış kararların özeti; R-17…R-24 spec yazımı sırasında netleştirilen sözleşme ayrıntılarıdır (kodla hizalandı; sahibi Murat; AGENTS.md §6'ya PR + duyuru ile işlenir).

## A. Teknoloji ve mimari

### R-01 Yığın: Next.js + Tailwind + Recharts · FastAPI + SQLAlchemy 2 · PostgreSQL (Neon)
- **Karar**: Web Next.js 16 App Router + Tailwind 4 + Recharts 3 (Bun); API FastAPI + SQLAlchemy 2 + Pydantic v2 (`uv`, `ruff`, `pytest`); DB PostgreSQL 16 / Neon. Günlük komutlar `Makefile`; yayın `render.yaml`; konteyner `apps/api/Dockerfile` (Azure yolu).
- **Gerekçe**: LLM/ajan ekosistemi Python; 4 kişi tek canlı DB; grafik kütüphanesi hazır; Kutay'ın başladığı yapı korunur.
- **Alternatifler**: Express, SQLite (reddedildi).
- **Kaynak**: D1; AGENTS.md §3–§4.

### R-02 UI iskeleti: shadcn/ui `dashboard-01`, ikinci UI/grafik katmanı yok
- **Karar**: shadcn/ui `dashboard-01` bloğu iskelet; lacivert + yeşil renk dili. Tremor eklenmez. Mevcut kabuk: `components/AppShell.tsx` + `Sidebar.tsx` (5 rota), "mock veri" rozeti, "Sentetik demo verisi" alt bilgisi.
- **Gerekçe**: Sıfırdan tasarım saat yakar; Recharts zaten var.
- **Alternatifler**: Sıfırdan Tailwind; Tremor.
- **Kaynak**: D8; Kutay kartı; `apps/web/components/`.

### R-03 LLM: tek adaptör; Haiku 4.5 varsayılan, Sonnet 5 kalite, Gemini/Groq yedek, fake test
- **Karar**: `services/llm.py` tek adaptör: `anthropic` (`claude-haiku-4-5`; kalite `claude-sonnet-5`), `gemini` (`gemini-2.5-flash`, yalnız sentetik veri), `groq` (OpenAI uyumlu uç, `llama-3.3-70b-versatile`, ücretsiz katman sınırlı; Türkçe SQL kalitesi eval ile ölçülür), `fake` (testler). Model adı yalnız `.env`'de; SQL üretiminde düşünme kapalı, `max_tokens` küçük, çıktı JSON. Yanıtta `model` alanı (D19).
- **Gerekçe**: Maliyet + Türkçe/SQL kalitesi; KVKK. "Sonnet 5 doğrulanamadı" notu Claude API referansıyla çürütüldü (2 $/10 $, Sonnet 4.6'dan ucuz).
- **Alternatifler**: Sonnet 4.6, GPT-5 mini.
- **Kaynak**: D10; KONTROL "Claude Sonnet 5" satırı; `services/llm.py`, `config.py`, `.env.example`.

### R-04 Text-to-SQL kendi servisimiz; framework yok
- **Karar**: `services/text2sql.py`: soru → önbellek (soru bankası, normalize eşleşme) → prompt (şema sözlüğü + kurallar + bankadan 6 `demo` örneği) → `llm.complete()` → `SQLPlan {sql, refusal}` → guard (sqlglot AST) → `engine_ro` → satırlar → Türkçe özet (yalnız sütun adları + ilk 20 satır; olmazsa deterministik) → `chat_log`. Vanna, LangChain SQL, LlamaIndex, LangGraph, Microsoft Agent Framework, PydanticAI bugün yok.
- **Gerekçe**: Dar şema + 15 soru; framework soyutlaması denetlenebilirliği düşürür; sqlglot tek başına DB doğrulayıcısı değildir → katmanlar üst üste.
- **Alternatifler**: Vanna.ai; LangChain SQL agent; LlamaIndex SQL.
- **Kaynak**: D2, D9; SONUC-1 A3 (yaklaşım karşılaştırması); Murat kartı.

### R-05 Ajan kural tabanlı + APScheduler; LLM kararda yok
- **Karar**: `services/agent.py` `run_check(db)`: `stock_qty <= reorder_point` → savepoint içinde taslak (`qty = max(1, target − stock)`, `est_amount = qty × unit_cost`, mesaj şablondan) → `IntegrityError` (DB tekil indeksi) → `skipped: acik_siparis_var`; tedarikçisiz → `skipped: tedarikci_yok`. APScheduler `AGENT_CHECK_INTERVAL_MIN` (10 dk), sabit job id. LLM ile mesaj cilalama yok.
- **Gerekçe**: Deterministik = demo güvenli; MidRule/SafeGuard dili; tek onay akışı için LangGraph/Agent Framework gereksiz soyutlama.
- **Alternatifler**: LangGraph interrupts, Microsoft Agent Framework HITL, PydanticAI deferred tools, arq/Celery (hepsi "bugün hayır").
- **Kaynak**: AGENTS.md §3; SONUC-1 A4; Ömer kartı; `services/agent.py`.

### R-06 Bildirim: Telegram Bot API; WhatsApp yol haritası
- **Karar**: `services/notify.py` `send_message(supplier, text)` → kanal `telegram` ise `sendMessage` (10 sn zaman aşımı; token loglara/hatalara sızmaz; yanıt `{ok, dry_run, channel, message_id}`); `email` bugün dry-run; token yoksa veya `NOTIFY_DRY_RUN=true` ise loglar, hata fırlatmaz. Hata → `NotifyError` → router 502.
- **Gerekçe**: Ücretsiz, 5 dk kurulum, sunumda telefonda görünür; WhatsApp onboarding/template riski yüksek.
- **Alternatifler**: E-posta; WhatsApp Business / Twilio Sandbox.
- **Kaynak**: D3; aksiyon-listesi; pitch-paketi; `services/notify.py`.

### R-07 Yayın: Vercel + Render + Neon; Azure yol haritası; ısıtma betiği
- **Karar**: Web Vercel (rootDir `apps/web`), API Render (`render.yaml`, free plan), DB Neon; `main`'den otomatik. `scripts/warmup.sh`: `/api/health` → `/api/summary` (DB) → `/api/assistant/suggestions` → ilk çiple `/api/assistant/ask` (LLM); demo öncesi 10 dk'da `make warmup`. CORS yalnız üretim alan adı. Azure (Container Apps + PostgreSQL Flexible + Entra External ID + Key Vault) taşınmaz; `Dockerfile` hazır.
- **Gerekçe**: Render Free 15 dk boşta uyur (~1 dk uyanma), Neon Free sıfıra iner (100 CU-saat/ay, 5 dk autosuspend); Vercel Hobby cron günlük → 10 dk kontrol Vercel'e taşınamaz.
- **Alternatifler**: Railway, Fly.io, Azure Container Apps bugün (hepsi reddedildi).
- **Kaynak**: D13; KONTROL; SONUC-1 A8; `scripts/warmup.sh`, `render.yaml`.

### R-08 Ölçek yolu: tek şema + `tenant_id` + RLS (bugün değil)
- **Karar**: Çok kiracı için schema-per-tenant değil, tek şema + `tenant_id` + PostgreSQL RLS. MVP tek kiracı.
- **Gerekçe**: 10k işletmeye kadar yönetilebilir; Microsoft partner hikâyesi.
- **Alternatifler**: Schema-per-tenant; Supabase (Auth + Postgres + RLS; katalog Co-Build notu).
- **Kaynak**: D13; katalog-3-grup-analiz.

## B. Güvenlik, veri, uyum

### R-09 Asistan salt-okur + defense-in-depth
- **Karar**: `DATABASE_URL_RO` (`otohesap_ro`, yalnız SELECT); bağlantı düzeyinde `default_transaction_read_only=on` + `statement_timeout=5000` (`db.py`); guard: tek ifade, `;`/`--`/`/*` reddi, kök `Select|SetOperation`, `SELECT INTO` ve `FOR UPDATE` reddi, yasak düğümler (Insert/Update/Delete/Create/Drop/Alter/Command/Merge/Truncate/Grant/Copy/Transaction/Set/…), tablo beyaz listesi (CTE adları hariç, yalnız `public`), `LIMIT 200` ekleme/kırpma; bir yeniden deneme; her soru `chat_log`'a.
- **Gerekçe**: "AI'a veritabanının anahtarını vermiyoruz"; "parser geçti = güvenli" sanılmaz.
- **Alternatifler**: Yalnız regex; yalnız RO rol.
- **Kaynak**: AGENTS.md §7; D2, D9; `services/text2sql.py`, `tests/test_text2sql_guard.py`.

### R-10 Eval: 15 soru, başarı = rakam + izinli tablolar + yazma yok
- **Karar**: `apps/api/app/data/soru_bankasi.json` (okunur kopya `docs/soru-bankasi.md`): Q01–Q15; `kind` dağılımı basit 5 · tarih 3 · join 3 · uc 2 · saldirgan 2; `demo: true` = Q02, Q03, Q06, Q07, Q09; saldırganlarda `sql: null`, `expected.reject`. Testler: şekil/dağılım, demo soruları birebir, tek SELECT + izinli tablolar, Postgres'te koşar (`tests/test_agent.py::test_bank_*`). Kabul: ≥ 12/15 ve 5 demo sorusu %100; canlı doğruluk `-m live` (`tests/test_eval.py`, yazılacak).
- **Gerekçe**: Model değişince regresyon ölçülsün; SQL string eşleşmesi kırılgan. SONUC-1 E01–E15 seti bizim 15 soruyla örtüşür; E14/E15 guard birim testleri olarak ayrı.
- **Alternatifler**: SQL string eşleşmesi; `clarify` vakası (E12; bugün reddedildi, bkz. R-29).
- **Kaynak**: D15; AGENTS.md §7.10; SONUC-1 A3; KONTROL notu 2.

### R-11 KVKK: demo %100 sentetik; LLM'e satır değil şema + sınırlı sonuç
- **Karar**: Demo verisi sentetik ve arayüzde öyle etiketli. Üretimde m.9 yurt dışı aktarım mekanizması + veri minimizasyonu; loglarda kişisel veri, bağlantı dizesi, token yok.
- **Gerekçe**: Yabancı LLM API = yurt dışına aktarım.
- **Alternatifler**: Türkiye/AB bölgesi model.
- **Kaynak**: D12; KONTROL.

### R-12 Seed deterministik: Faker(tr_TR) + NumPy rng(42), sabit aralık, `--reset`
- **Karar**: `data/seed.py`: `SEED=42`, `DATE_FROM=2026-04-01`, `DATE_TO=2026-09-13`; 20 ürün / 5 kategori / 5 tedarikçi (ilki Telegram, `TELEGRAM_CHAT_ID` yer tutucu); ~600 satış, ~250 gider; `_set_stock`: tam 2 kritik (`CRITICAL_PRODUCTS`), tam 1 eşiğin 1 üstünde (`NEAR_CRITICAL_PRODUCT`); `_ensure_profit_leader`: powerbank ikinciden `PROFIT_GAP` önde; mağaza saati (UTC+3) ile üretilir, UTC yazılır; psycopg COPY; özet basar.
- **Gerekçe**: Her çalıştırmada aynı rakamlar → soru bankası ve testler sabit; gelecek tarihli kayıt yok (SONUC-1 "30 Eylül" uyarısı).
- **Alternatifler**: Zaman damgası tohumlu rastgelelik (yasak).
- **Kaynak**: AGENTS.md §3, §5; Yiğit kartı; `data/seed.py`, `tests/test_seed.py`.

## C. Süreç ve sunum

### R-13 Git: AI imzası yok, iCloud dışı, kişi dalları, küçük PR, squash
- **Karar**: `scripts/hooks/commit-msg` AI imzasını reddeder; depo `~/code/Oto-Hesap`; `main` korumalı + kişi başı 1 dal; PR ≤ 400 satır, 15 dk inceleme, squash merge; spec-kit script'leri çalıştırılmaz.
- **Gerekçe**: Katkı grafiğinde yalnız ekip; iCloud `.git`/`node_modules` bozar; 1 günde çakışma azalır.
- **Kaynak**: D4, D5, D6; AGENTS.md §8–§9.

### R-14 Tek gün, 19:00 dondurma; demo senaryosu tek gerçek kaynak
- **Karar**: 09:00–22:00; checkpoint 10:30 / 13:00 / 16:30; 19:00 özellik dondurma; 20:00 yayın; 21:00 prova. Ürün büyük ölçüde 13 Eyl'de Claude ile inşa edildiği için AGENTS §11 çizelgesi "kalan işler" için yeniden yazılacak (KONTROL notu 2).
- **Kaynak**: D7; AGENTS.md §2, §11; KONTROL notu 2.

### R-15 Pitch kuralları ve doğrulanmış rakamlar
- **Karar**: "Rakiplerde AI yok" denmez; A etiketli olmayan sayı slayta girmez; konumlama "ön muhasebenin üstünde çalışan AI karar katmanı"; Paraşüt 940 TL + KDV/ay yalnız pazar çıpası; TÜİK 2024 rakamları A. Ek (D16–D18): sunumda "Fark" net kâr diye anlatılmaz, "en kârlı ürün" tahmini brüt katkıdır, veri "sentetik demo" diye etiketlenir, Render Free'de zamanlayıcının uyuduğu saklanmaz.
- **Kaynak**: D14; KONTROL; AGENTS.md §12; pitch-paketi.

### R-16 Trendyol yalnız Product V2 (yol haritası)
- **Karar**: V1'e tek satır kod yok (15 Eyl 2026'da kapanıyor); V2 + salt-okur sipariş importu yol haritasında.
- **Kaynak**: D11; KONTROL.

## D. Sözleşme ayrıntıları (AGENTS.md §6'da belirsizdi; kodla hizalandı)

### R-17 `period` tanımı — BİRLEŞTİRİLECEK
- **Durum (kod)**: Üç farklı hesap var. `routers/summary.py::period_start`: `month` = ay başı (UTC); `quarter` = `now − 3 takvim ayı` (aynı gün/saat, ör. 13 Haz); `half` = `now − 6 ay` (13 Mar). `schemas/analytics.py::period_bounds`: yarı açık `[start, next_month)`; `quarter` = 1 Haz; `half` = 1 Mar (13 Eyl için 7 takvim ayı). `routers/summary.py::_CASHFLOW_SQL`: içinde bulunulan ay dâhil son 6 ay (Nis–Eyl).
- **Karar (öneri, TODO(murat))**: Tek yardımcı (`schemas/analytics.py::period_bounds` ya da yeni `services/period.py`) ve tek tanım: yarı açık `[start, end)`, UTC takvim ayları; `month` = içinde bulunulan ay; `quarter` = içinde bulunulan ay dâhil son 3 takvim ayı (13 Eyl → 1 Tem); `half` = son 6 takvim ayı (1 Nis; seed aralığını tam kapsar ve aylık seriyle aynı pencere). Summary, analytics ve cashflow aynı fonksiyonu kullanır; testler güncellenir.
- **Gerekçe**: AGENTS §7.12 yarı açık aralık ve "bu ay = takvim ayı"; KPI ile pasta aynı dönem sekmesinde farklı aralık kullanırsa jüri sorusu olur. Demo için risk yok (6 ay seed'in tamamı), ama "3 ay" sekmesinde KPI (13 Haz'dan) ile pasta (1 Haz'dan) ayrışır.
- **Kaynak**: AGENTS.md §6, §7.12; `routers/summary.py`, `schemas/analytics.py`, `tests/test_summary.py`, `tests/test_analytics.py`.

### R-18 `share` yüzde, `top` varsayılanı, sıralama
- **Karar**: `expenses-by-category.share` = yüzde (0–100, 1 ondalık; toplam ≈ 100), tutara göre azalan. `sales-by-product` ciroya göre azalan; `top` varsayılan 5, 1–50; dışı 400 "top 1 ile 50 arasında olmalı."; geçersiz dönem 400 "Geçersiz dönem; month, quarter veya half olmalı." (summary'de 422 — T014 ile Türkçe tek gövde).
- **Kaynak**: Yiğit kartı; `routers/analytics.py`.

### R-19 Satış kaydı stoğu düşürür
- **Karar**: `POST /api/sales` ürün satırını kilitleyip stoğu `qty` kadar düşürür; `DELETE` geri ekler; `PUT` (kısmi) farkı uygular, ürün değişirse eskiye iade / yeniye düşüm; stok yetersizse 400 "Stok yetersiz: N adet var". `unit_price` boşsa ürünün `sale_price`'ı; `sold_at` boşsa şimdi (UTC); `total` sunucuda.
- **Gerekçe**: Yiğit kartı "eşiğin 1 üstünde ürün demoda satış ekleyince kritiğe düşer".
- **Kaynak**: `routers/sales.py`, `tests/test_sales_expenses.py`.

### R-20 Onay durum makinesi ve hata kodları
- **Karar**: `draft → approved` (commit) → `send_message` → `sent` + `sent_at` + `notify_ref` (commit). Gönderim hatası → **502** "Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin.", durum `approved` kalır, kör tekrar yok; `approved` insan tarafından yeniden onaylanabilir. `sent`/`rejected` üstüne approve veya reject → **409** "Sipariş zaten {status} durumunda.". Yanıt: sipariş alanları + `notify {ok, dry_run, channel, message_id|null}`. `NOTIFY_DRY_RUN` → `sent`, `notify_ref="dry-run"`, `notify.dry_run=true`.
- **Gerekçe**: D17 (gönderim izi, kör tekrar yok); Ömer kartı; koordinatör notu.
- **Alternatifler**: 503 ve `simulated` alanı (ilk taslak; kod 502 + `notify` ile oturdu).
- **Kaynak**: `routers/orders.py`, `schemas/orders.py`, `tests/test_orders.py`.

### R-21 `open_order_id`; rozet durumu siparişlerden
- **Karar**: `GET /api/products` `open_order_id` (durumu `draft|approved|sent` olan en yeni sipariş; indeks gereği en çok 1) ve `supplier_name` döner. Ayrı `open_order_status` alanı **yok**; arayüz "taslak bekliyor" / "sipariş yolda" ayrımı için `GET /api/orders` sonucunu `open_order_id` ile eşler (Tedarik ekranı zaten listeyi çeker).
- **Alternatifler**: `open_order_status` alanı (ilk taslak; koda girmedi, ihtiyaç doğarsa PR).
- **Kaynak**: `routers/products.py`, `schemas/core.py`, `apps/web/lib/types.ts`.

### R-22 Asistan yanıt ve hata sözleşmesi
- **Karar**: Yanıt `{ok, answer, sql, rows[{sütun: değer}], columns, sources, asked_at, cached, model}`; `model` alanı D19 gereği eklenecek (T080). 400 "Soru boş olamaz."; 400 "Asistan yalnız okuma sorguları çalıştırır." (guard reddi veya LLM'in yazma isteğini reddi); 503 "Asistan şu an yanıt veremiyor; lütfen tekrar deneyin." (LLM erişilemez ve önbellekte yok); 200 + `ok:false` + "Bu soruyu bu veriyle yanıtlayamadım." (LLM "veri yok" dedi veya SQL iki denemede hata); 200 + "Sorgu bu veriyle eşleşen kayıt döndürmedi." (boş sonuç). `question` ≤ 2000 karakter (422). `sources` İngilizce tablo adları; Türkçe etiket arayüzde.
- **Kaynak**: AGENTS.md §7.4–§7.6; koordinatör notu; `routers/assistant.py`, `services/text2sql.py`.

### R-23 CSV biçimi
- **Karar**: UTF-8 BOM, `;` ayraç, ondalık virgül (binlik ayracı yok), CRLF, Türkçe başlıklar (`Tarih;Ürün;Adet;Birim Fiyat;Toplam;Kanal` / `Tarih;Kategori;Tutar;Tedarikçi;Not`), tarih `YYYY-MM-DD HH:MM` (UTC), tarihe göre artan, tüm kayıtlar, `attachment; filename="satislar.csv" | "giderler.csv"`, formül enjeksiyonuna karşı `'` öneki.
- **Kaynak**: Yiğit kartı; `routers/export.py`, `tests/test_export.py`.

### R-24 Sözleşmeye eklemeler (AGENTS.md §6'ya PR ile)
- **Karar**: `GET /api/insights` (en çok 5 kural tabanlı kart: `critical-stock`, `net-change`, `expense-rise`, `top-product`, `channel-share`; eşikler: fark düşüşü > %10 → warn, gider artışı > %25 → warn; boş veri → `[]`), `GET /api/orders/{id}`, `POST /api/agent/check` yanıtında `skipped`, sipariş nesnesinde `product_name/supplier_name/supplier_channel/notify_ref`, approve yanıtında `notify`, satışta `product_name`, üründe `supplier_name`, asistanda `ok`/`model`, `/api/health`'te `scheduler`/`version`.
- **Gerekçe**: Katalog analizi (AI Investigator) "sorulmadan uyarı"; D17/D19 gereklilikleri; arayüzün ikinci istek atmadan ad göstermesi.
- **Kaynak**: katalog-3-grup-analiz; `services/insights.py`; koordinatör notu.

## E. SONUC-1 (13 Eyl akşam) ile gelen kararlar

### R-25 Metrik sözlüğü (D16)
- **Karar**: Gelir = Σ `sales.total`; Gider = Σ `expenses.amount`; **Fark** = Gelir − Gider (net kâr değil); "En kârlı ürün" = **tahmini brüt katkı** = Σ qty × (unit_price − `products.unit_cost`), mevcut birim maliyetle, "tahmini" denir; aylık görünüm "Aylık gelir–gider". Grafik, SQL (prompt kural 3), öngörü kartları ve slayt aynı tanımı kullanır.
- **Gerekçe**: Yanlış finansal iddia jüride puan kaybettirir; şemada KDV/iade/tahakkuk/tarihsel maliyet yok.
- **Alternatifler**: "Net kâr" etiketi (reddedildi).
- **Kaynak**: D16; AGENTS.md §5 sözlük; SONUC-1 A3 "Finansal anlam sözleşmesi"; `services/insights.py`, `schemas/analytics.py`.

### R-26 Sipariş sınırları (D17)
- **Karar**: `sent` = mesaj gönderildi (teslim/kabul/ödeme değil; stok artmaz); `sent` de yeni taslağı bloke eder; DB'de kısmi tekil indeks `ux_open_order_per_product`; Telegram `message_id` → `purchase_orders.notify_ref`; zaman aşımında kör tekrar yok (`approved` kalır, insan tekrar dener); mesajda "DEMO · sentetik sipariş #id".
- **Gerekçe**: Çift/yanlış tedarik aksiyonu ve "teslim alındı" yanılgısı; dış serviste exactly-once ispatı yok.
- **Alternatifler**: Yalnız uygulama düzeyi kontrol; outbox + retry (yarın).
- **Kaynak**: D17; SONUC-1 A4; `docs/schema.sql`, `services/agent.py`, `routers/orders.py`.

### R-27 Zamanlayıcı dürüstlüğü (D18)
- **Karar**: Render Free 15 dk boşta uyur → "kesintisiz 10 dk kontrol" vaat edilmez; demoda "Şimdi kontrol et" (aynı `run_check`); sürekli çalışma için Render 7 $/ay instance (final sonrası karar); sürekli ping mimari değildir; Vercel Hobby ticari değil → SaaS'ta Pro. APScheduler: tek scheduler, sabit job id, `max_instances=1`, `coalesce=True` (T086).
- **Gerekçe**: Ücretsiz katman sınırları resmî.
- **Kaynak**: D18; SONUC-1 A8; MURAT-YAPILACAKLAR 8b; `services/scheduler.py`.

### R-28 Guard genişletmesi (D19)
- **Karar**: Fonksiyon **izin listesi** (sum, count, avg, min, max, coalesce, round, date_trunc, date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs); `pg_sleep`, `set_config`, `pg_read_file`, `pg_*` red; `SELECT INTO`, CTE içinde DML, çoklu ifade red; `suppliers.contact_address` salt-okur role sütun düzeyinde kapalı ve prompt şemasında yok; yanıtta `model` alanı.
- **Durum (kod)**: `SELECT INTO`, `FOR UPDATE`, DML düğümleri ve yasak fonksiyon **kara listesi** (`FORBIDDEN_FUNCTIONS`) uygulanmış; izin listesine geçiş, `contact_address`'in `SCHEMA_DOC`'tan çıkarılması ve `model` alanı **yapılacak** (T078–T080). Neon'da sütun düzeyi REVOKE/GRANT komutları `schema.sql` yorumlarında (T013).
- **Gerekçe**: "SELECT ise güvenli" yanılgısı; geniş yasak listesi yerine küçük izin kümesi daha yönetilebilir.
- **Kaynak**: D19; AGENTS.md §7.11; SONUC-1 A3 "Asgari savunma katmanları"; `services/text2sql.py`.

### R-29 Belirsiz soru: `clarify` yok, varsayım cümlesi (D20)
- **Karar**: "En çok kazancım hangi üründen?" için netleştirme sorusu yok; D16 varsayılanı (tahmini brüt katkı) uygulanır ve yanıt metni varsayımı söyler ("mevcut birim maliyetle tahmini brüt katkı"). Netleştirme yol haritası.
- **Gerekçe**: Demo akıcılığı; dürüstlük yanıt metninde.
- **Alternatifler**: `status = clarify` (SONUC-1 E12; reddedildi).
- **Kaynak**: D20; KONTROL notu 2; `services/text2sql.py` SUMMARY_SYSTEM (T082).

## F. Doğrulama özeti (KONTROL-2026-09-13, not 1 + not 2)

| İddia | Sonuç | Plana etkisi |
|---|---|---|
| TÜİK 2024 KOBİ rakamları | Doğru (A) | Problem slaydı |
| Trendyol V1 15 Eyl 2026 kapanış | Doğru (A) | R-16 |
| Paraşüt 940 TL + KDV/ay | Doğru; sayfa tarihi belirsiz | Pazar çıpası |
| Sonnet 5 doğrulanamadı | YANLIŞ; `claude-sonnet-5` mevcut, 2 $/10 $ | R-03 |
| Azure for Students Azure OpenAI | Kısmen; kota "N/A" görüldü | Jüriye temkinli cümle |
| Render/Neon uyku; Neon 100 CU-saat, 5 dk autosuspend | Resmî davranış | R-07, R-27 |
| Gemini ücretsiz katman içerik politikası | A, tekrar çekilmedi | R-03 yalnız sentetik |
| "Fark ≠ net kâr", tahmini brüt katkı | Doğru ve önemli | R-25 (D16) |
| `sent ≠ received`, DB tekillik, gönderim kimliği | Doğru | R-26 (D17) |
| Guard: fonksiyon izin listesi, CTE-DML, gizli sütun | Doğru | R-28 (D19) |
| E12 `clarify` | Bugün reddedildi | R-29 (D20) |
| PydanticAI / LangGraph / Agent Framework / arq / Celery | "Bugün hayır" | R-05 |
