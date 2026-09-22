# Implementation Plan: OtoHesap MVP (Geliştirme Günü)

**Branch**: `001-otohesap-mvp` | **Date**: 2026-09-13 (D16–D20 sonrası güncellendi) | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-otohesap-mvp/spec.md`

**Note**: Bu plan `/speckit-plan` akışının çıktısıdır; çalışma dalları AGENTS.md §8'deki kişi dallarıdır (`murat/api-core`, `kutay/web`, `omer/agent`, `yigit/data`), `001-otohesap-mvp` yalnız spec-kit numarasıdır. API katmanının büyük bölümü 13 Eyl'de inşa edildi; kalan işler `tasks.md`'de işaretlidir.

## Summary

Tek günde (09:00–22:00) KOBİ finans + stok MVP'si: Neon Postgres üstünde deterministik sentetik veri (2026-04-01…2026-09-13); FastAPI çekirdeği (özet, aylık gelir–gider, satış/gider CRUD, ürünler); kendi Text-to-SQL servisi (LLM → JSON → sqlglot AST → beyaz liste + fonksiyon izin listesi → salt-okur rol → LIMIT/timeout); kural tabanlı tedarik ajanı (kritik stok → taslak → insan onayı → Telegram; DB düzeyinde tekrar koruması, `notify_ref`); Next.js 5 ekran; CSV; kural tabanlı öngörü kartları; D16 metrik sözlüğü ile tutarlı etiketler; Vercel + Render + Neon yayını; CI yeşil; 5 dk demo senaryosu iki prova.

## Technical Context

**Language/Version**: Python 3.12 (api, seed) · TypeScript 5 strict (web)

**Primary Dependencies**: FastAPI ≥0.115, SQLAlchemy ≥2.0.30, psycopg[binary] 3, Pydantic v2 + pydantic-settings, sqlglot ≥25, APScheduler 3.x, httpx, anthropic SDK, google-genai, (Groq: httpx ile OpenAI uyumlu uç), Faker, NumPy (api) · Next.js 16.3, React 19.2, Tailwind 4, Recharts 3.10, shadcn/ui `dashboard-01` bloğu (D8), Bun 1.3 (web)

**Storage**: PostgreSQL 16 — Neon ücretsiz katman (üretim/demo), yerel Postgres veya CI servisi (test). Şema `docs/schema.sql` (idempotent; `notify_ref`, `ux_open_order_per_product`); uygulama rolü + salt-okur `otohesap_ro` (sütun düzeyi grant).

**Testing**: pytest (ayrı test DB `TEST_DB_NAME`, her testte TRUNCATE; `LLM_PROVIDER=fake`, `NOTIFY_DRY_RUN=true`, zamanlayıcı kapalı; `small_data` fixture) · ruff (lint + format) · ESLint + `next build` (web) · soru bankası testleri (`tests/test_agent.py::test_bank_*`) · canlı eval `-m live` (`tests/test_eval.py`, yazılacak)

**Target Platform**: Web (tarayıcı, masaüstü + mobil genişlik); API Linux (Render free; `Dockerfile` ile konteyner); tek kiracı

**Project Type**: Web uygulaması (apps/api + apps/web monorepo; `Makefile` ile günlük komutlar)

**Performance Goals**: Pano < 2 sn (ısınmış); asistan önbellek < 3 sn, LLM < 8 sn; onay → telefon < 5 sn; seed < 10 sn

**Constraints**: Tek gün, 19:00 özellik dondurma; ücretsiz katmanlar (Render 15 dk uyku → zamanlayıcı durur, D18; Neon sıfıra iner → `make warmup`); asistan salt-okur, 5 sn `statement_timeout`, `LIMIT 200`, fonksiyon izin listesi; framework yasağı (Anayasa V); AI imzası yok; `.env` yok; D16 sözlüğü dışına çıkan etiket yok

**Scale/Scope**: 1 işletme, 20 ürün, ~600 satış, ~250 gider, 5 ekran, 22 API ucu, 15 soruluk eval, 4 geliştirici

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| İlke (v1.1.0) | Uyum | Kanıt (bu planda / kodda) |
|------|------|-------------------|
| I. Kontrollü otonomi | ✅ | `services/text2sql.py` yalnız SQL üretir, rakam DB'den; `services/agent.py` LLM'siz kural; `orders/approve` tek dış iletişim noktası; zamanlayıcı yalnız `run_check`; `ux_open_order_per_product` + savepoint; `notify_ref`; 502'de `approved` kalır, kör tekrar yok; mesaj "DEMO · sentetik sipariş #id" |
| II. Şeffaflık | ✅ / ⚠ | `ask` yanıtı `ok, sql, sources, asked_at, cached`; `chat_log` her soruda; ajan ve onay `log.info`; D16 sözlüğü `insights.py` ve `schemas/analytics.py`'de. ⚠ `model` alanı (T080) ve D20 varsayım cümlesi (T082) yapılacak; web etiketleri (T091) yapılacak |
| III. Salt-okur + defense-in-depth | ✅ / ⚠ | `db.engine_ro` (RO URL + read-only işlem + 5 sn); guard: tek ifade, yasak token, kök `Select`, `SELECT INTO`/`FOR UPDATE`/DML düğümü reddi, beyaz liste, LIMIT; `chat_log` beyaz listede değil. ⚠ Fonksiyon izin listesine geçiş (T078), `contact_address`'in prompt şemasından çıkarılması (T079), Neon'da sütun düzeyi grant (T013) yapılacak |
| IV. Test-first, CI yeşil | ✅ | 17 test dosyası (health, llm, summary, sales/expenses, products, guard, assistant, agent, orders, notify, seed, analytics, export, insights); soru bankası şekil/dağılım testleri; CI `ci.yml` |
| V. Basitlik ve dürüst altyapı | ✅ | Bağımlılık listesi `pyproject.toml` ile sınırlı; framework yok; Makefile/render.yaml; D18 zamanlayıcı dürüstlüğü sunum notunda (AGENTS §12); Complexity Tracking boş |
| VI. Katkı görünürlüğü ve hijyen | ✅ | `scripts/hooks/commit-msg`, `setup.sh` iCloud denetimi, `.gitignore` `.env`/AI dizinleri; `notify.py` token'ı loglamaz/maskeler |
| VII. Türkçe kullanıcı yüzü | ✅ / ⚠ | `{detail}` Türkçe (router'larda); `lib/format.ts` tr-TR + Europe/Istanbul; CSV Excel TR. ⚠ 422 gövdesi FastAPI varsayılan listesi (T014) |

Post-design re-check: sözleşmeye eklemeler (R-24) mevcut tablolarla, yeni bağımlılık yok; AGENTS.md §6'ya PR + duyuru ile işlenecek. İhlal yok; ⚠ maddeleri açık görevlerdir.

## Project Structure

### Documentation (this feature)

```text
specs/001-otohesap-mvp/
├── plan.md              # Bu dosya
├── research.md          # Faz 0: kararlar ve gerekçeler (D1–D20 + doğrulamalar + sözleşme netleştirmeleri)
├── data-model.md        # Faz 1: 6 tablo + görünüm, tekil indeks, durum makinesi, metrikler, seed hedefleri
├── quickstart.md        # Faz 1: klon → make setup → seed → api → web → test → demo → yayın
├── contracts/
│   └── api.md           # Faz 1: 22 uç, şema, hata, örnek (kodla birebir)
├── checklists/
│   └── requirements.md  # Spec kalite kontrolü
└── tasks.md             # Faz 2: hikâye bazlı görevler, sahipler, checkpoint'ler, kalan işler
```

### Source Code (repository root)

```text
Makefile · render.yaml · .env.example · scripts/{setup.sh,warmup.sh,github-setup.sh,hooks/commit-msg}

apps/api/
├── pyproject.toml · Dockerfile · uv.lock
├── app/
│   ├── config.py                  # pydantic-settings; DATABASE_URL(_RO), LLM_* (anthropic|gemini|groq|fake), AGENT_*, TELEGRAM_*, NOTIFY_DRY_RUN, BUSINESS_NAME, CORS_ORIGINS, LOG_LEVEL
│   ├── db.py                      # engine (yazar) + engine_ro (salt-okur, 5 sn timeout); get_db; db_ok
│   ├── models.py                  # docs/schema.sql birebir (Supplier, Product, Sale, Expense, PurchaseOrder[+notify_ref], ChatLog)
│   ├── main.py                    # CORS, istek logu, 500 Türkçe gövde, router kayıtları, /api/health, lifespan (scheduler)   [422 handler: T014]
│   ├── data/soru_bankasi.json     # 15 soru (Ömer + Yiğit); text2sql örnek + önbellek kaynağı
│   ├── routers/
│   │   ├── summary.py             # GET /api/summary, GET /api/cashflow/monthly            [Murat] ✔
│   │   ├── sales.py               # GET/POST/PUT/DELETE /api/sales (stok düşümü)           [Murat] ✔
│   │   ├── expenses.py            # GET/POST/PUT/DELETE /api/expenses                       [Murat] ✔
│   │   ├── products.py            # GET /api/products, PATCH /api/products/{id}             [Murat] ✔
│   │   ├── analytics.py           # expenses-by-category, sales-by-product                  [Yiğit] ✔
│   │   ├── assistant.py           # POST /api/assistant/ask, GET /api/assistant/suggestions [Murat] ✔ (+model: T080)
│   │   ├── orders.py              # GET /api/orders, GET /{id}, POST approve/reject         [Ömer] ✔
│   │   ├── agent.py               # POST /api/agent/check                                   [Ömer] ✔
│   │   ├── export.py              # GET /api/export/{sales,expenses}.csv                    [Yiğit] ✔
│   │   └── insights.py            # GET /api/insights                                       [Yiğit] ✔
│   ├── services/
│   │   ├── llm.py                 # tek adaptör: anthropic | gemini | groq | fake ✔
│   │   ├── text2sql.py            # önbellek → prompt → SQLPlan → guard (sqlglot) → engine_ro → özet; chat_log ✔ (izin listesi T078, şema T079, D20 T082)
│   │   ├── agent.py               # run_check(db) → {created, drafts, skipped}; savepoint + tekil indeks ✔
│   │   ├── notify.py              # send_message(supplier, text) → {ok, dry_run, channel, message_id}; NotifyError ✔
│   │   ├── scheduler.py           # APScheduler; run_check ✔ (max_instances/coalesce: T086)
│   │   └── insights.py            # 5 kural → kart listesi (D16 sözcükleri) ✔
│   └── schemas/                   # core.py (summary, cashflow, sales, expenses, products) · analytics.py (period, insight) · assistant.py · orders.py ✔
└── tests/                         # conftest (test DB, small_data) + test_{health,llm_adapter,summary,sales_expenses,products,text2sql_guard,assistant,agent,orders,notify,seed,analytics,export,insights}.py ✔ · test_eval.py (T042)

apps/web/
├── package.json                   # next 16.3, react 19.2, recharts 3.10, tailwind 4, bun
├── app/
│   ├── layout.tsx                 # AppShell (sol menü 5 rota, üst başlık, mock rozeti, "Sentetik demo verisi" alt bilgi) ✔
│   ├── page.tsx                   # Genel Bakış: KPI ×4, aylık gelir–gider, pasta, öngörü kartları, dönem sekmeleri   [T033, T062, T063]
│   ├── kayitlar/page.tsx          # satış/gider sekmeleri, tablo, arama, modal form, CSV                             [T039, T066]
│   ├── stok/page.tsx              # ürün tablosu, kritik kırmızı, rozet, eşik düzenleme                              [T058]
│   ├── asistan/page.tsx           # sohbet, çipler, Sorguyu gör, kaynak damgası, model                               [T048]
│   └── tedarik/page.tsx           # Şimdi kontrol et, sayaçlar, taslak kartları, onayla/reddet, skipped              [T056]
├── components/                    # AppShell, Sidebar, Icons, Badge, DataTable, EmptyState, InsightCard, KpiCard, Modal, SqlBlock, MockBadge, ui ✔ · grafikler, record-form, chat-bubble, order-card (yapılacak)
├── lib/
│   ├── api.ts                     # 22 uç için tipli fonksiyon; ağ hatasında mocks/ ✔
│   ├── types.ts                   # sözleşme tipleri ✔ (product_name/supplier_name/notify hizası: T092)
│   ├── format.ts · errors.ts · mock-mode.ts · use-async.ts ✔
│   └── mocks/                     # store.ts + *.json ✔

data/
└── seed.py                        # Faker(tr_TR) + NumPy rng(42); 2026-04-01…2026-09-13; --reset; COPY ✔

docs/
├── schema.sql ✔ · demo-senaryosu.md · soru-bankasi.md ✔ · DECISIONS.md (D1–D20) · team/*.md · research/*.md · sunum/pitch-paketi.md
```

**Structure Decision**: Web uygulaması yapısı; `apps/api` (FastAPI) + `apps/web` (Next.js App Router) + kök `data/seed.py`. Router dosyaları iskelette boş açıldı, sahipleri doldurdu (✔). `models.py`, `schema.sql`, `main.py` yalnız Murat. Dönem hesabı bugün `schemas/analytics.py` ve `routers/summary.py`'de ayrı ayrı; tek yardımcıya birleştirme T015 (R-17).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | Sapma yok |

## Aşamalar

### Faz 0 — Araştırma (tamamlandı)

Çıktı: [research.md](./research.md). Kaynaklar `docs/DECISIONS.md` D1–D20, `docs/research/KONTROL-2026-09-13.md`, `katalog-3-grup-analiz.md`. Spec'te `NEEDS CLARIFICATION` yoktur; sözleşme ayrıntıları R-17…R-24'te kodla hizalandı; tek açık tasarım kararı dönem tanımının birleştirilmesi (R-17, TODO(murat)).

### Faz 1 — Tasarım (tamamlandı)

- [data-model.md](./data-model.md): tablolar, `notify_ref`, `ux_open_order_per_product`, sütun düzeyi grant, durum makinesi (502/409), D16 metrikleri, seed hedefleri (uygulandı).
- [contracts/api.md](./contracts/api.md): AGENTS.md §6 + eklemeler; her uç için yöntem, yol, şema, hata, örnek; kodla birebir.
- [quickstart.md](./quickstart.md): `make` hedefleriyle sıfırdan çalıştırma, RO rol + sütun grant, test, demo, yayın.

### Faz 2 — Görevler

Çıktı: [tasks.md](./tasks.md) (`/speckit-tasks` biçimi; hikâye bazlı fazlar, sahipler, [P] paralellik, checkpoint eşlemesi, bağımlılık grafiği, MVP kapsamı = US1–US4; tamamlananlar `[x]`, D16–D20 görevleri T078–T092).
