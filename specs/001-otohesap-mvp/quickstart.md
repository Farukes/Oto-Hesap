# Quickstart: OtoHesap MVP

Sıfırdan çalışan yerel kurulum ve demo provası. Gereksinimler: Git, Python 3.12, `uv`, Bun 1.3, `psql` (PostgreSQL 16 istemcisi); yerel Postgres **veya** Neon bağlantısı. Günlük komutlar `Makefile`'da (`make help`).

## 1. Klon ve kurulum

```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
make setup              # = ./scripts/setup.sh: iCloud dışı denetimi · commit-msg hook · .env kopyası · uv sync · bun install
git checkout <dalın>    # murat/api-core · kutay/web · omer/agent · yigit/data
```

`setup.sh` depo iCloud/Desktop/Documents altındaysa durur (Anayasa VI).

## 2. Veritabanı

**Seçenek A — Neon (ekip, demo):** Murat'ın Neon davetini kabul et; bağlantı dizesini `.env`'e yaz (WhatsApp'a değil).

**Seçenek B — yerel Postgres 16:**
```bash
createdb otohesap
export DATABASE_URL=postgresql://localhost:5432/otohesap
```

Şemayı uygula (her iki seçenekte; idempotent, tekrar koşulabilir):
```bash
psql "$DATABASE_URL" -f docs/schema.sql
```
Şema `purchase_orders.notify_ref` sütununu ve `ux_open_order_per_product` kısmi tekil indeksini içerir (D17); mevcut veritabanında `ADD COLUMN IF NOT EXISTS` ile eklenir.

## 3. Salt-okur rol (asistan için, bir kez)

`docs/schema.sql` sonundaki yorumlar; Neon SQL editöründe ya da `psql` ile (`neondb` yerine kendi DB adın):
```sql
CREATE ROLE otohesap_ro LOGIN PASSWORD '<parola>';
GRANT CONNECT ON DATABASE neondb TO otohesap_ro;
GRANT USAGE ON SCHEMA public TO otohesap_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO otohesap_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO otohesap_ro;
ALTER ROLE otohesap_ro SET statement_timeout = '5s';
-- Gizli iletişim alanı asistana kapalı (sütun düzeyi, D19):
REVOKE SELECT ON suppliers FROM otohesap_ro;
GRANT SELECT (id, name, contact_channel, lead_time_days) ON suppliers TO otohesap_ro;
```
Parolayı `.env` → `DATABASE_URL_RO`'ya koy. Yerelde rol açmazsan `DATABASE_URL_RO` boş kalabilir: `db.py` yine de bağlantıyı `default_transaction_read_only=on` + 5 sn zaman aşımıyla açar (rol ve sütun katmanı eksik; demo için rol şart).

## 4. `.env`

`make setup` `.env.example`'ı kopyalar. Doldur:

| Değişken | Not |
|----------|-----|
| `DATABASE_URL`, `DATABASE_URL_RO` | Neon veya yerel |
| `LLM_PROVIDER` | `anthropic` (varsayılan model `claude-haiku-4-5`) · `gemini` (yedek) · `groq` (ücretsiz katman, OpenAI uyumlu) · `fake` (anahtar yokken; önbellekli demo soruları çalışır) |
| `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` / `GROQ_API_KEY` | yalnız `.env`'de; `GROQ_MODEL` adını konsoldan doğrula |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID` | Ömer'in botu; token yoksa gönderim simülasyon |
| `NOTIFY_DRY_RUN` | `.env.example`'da `true` (geliştirme); **demoda `false`** |
| `AGENT_CHECK_INTERVAL_MIN`, `AGENT_SCHEDULER_ENABLED` | 10 · true |
| `BUSINESS_NAME` | Telegram mesajında işletme adı (`OtoHesap Demo Mağaza`) |
| `CORS_ORIGINS` | `http://localhost:3000`; üretimde Vercel alan adı (virgülle birden çok) |
| `NEXT_PUBLIC_API_URL` | web → api adresi (`http://localhost:8000`) |

## 5. Sentetik veri

```bash
make seed               # = uv run --project apps/api python data/seed.py --reset
```
~600 satış, ~250 gider, 20 ürün, 5 tedarikçi; tam 2 kritik ürün; seed=42; 2026-04-01…2026-09-13; < 10 sn. Sonunda basılan özet (gelir, gider, fark, kritik ürünler, en kârlı ürün) `docs/soru-bankasi.md` rakamlarıyla aynı olmalı. İki koşu = aynı rakamlar. Telegram kanallı tedarikçinin `contact_address`'i `TELEGRAM_CHAT_ID` yer tutucusudur; demodan önce Ömer'in `chat_id`'siyle güncellenir (bkz. tasks T083).

## 6. API

```bash
make api                # = cd apps/api && uv run uvicorn app.main:app --reload --port 8000
curl -s localhost:8000/api/health   # {"status":"ok","db":true,"llm":"anthropic","scheduler":true,"version":"0.1.0"}
```
Swagger: http://localhost:8000/docs

## 7. Web

```bash
make web                # = cd apps/web && bun dev  → http://localhost:3000
```
API'ye ulaşılamazsa (ağ hatası) `lib/api.ts` `lib/mocks/*.json` ile yanıt verir ve üstte "mock veri" rozeti görünür; HTTP hataları (4xx/5xx) mock'a düşmez, Türkçe `detail` gösterilir.

## 8. Testler

Testler ayrı bir veritabanı yaratır (`TEST_DB_NAME`, varsayılan `otohesap_test`; `DATABASE_URL`'in DB adı değiştirilir) ve her testte tabloları boşaltır. `DROP/CREATE DATABASE` yetkisi gerekir → **yerel Postgres veya CI** kullan; Neon'daki ortak DB'ye karşı koşma.

```bash
make test               # = cd apps/api && TEST_DB_NAME=otohesap_test uv run pytest -q
make lint               # ruff format --check + ruff check + bun run lint
cd apps/api && uv run pytest -q -m live    # yalnız gerçek LLM anahtarıyla eval doğruluğu (isteğe bağlı; tests/test_eval.py gelince)
cd apps/web && bun run build
```
Paralel oturumlar `TEST_DB_NAME`'i farklı vermeli. CI (`.github/workflows/ci.yml`) aynı komutları Postgres 16 servisiyle koşar.

## 9. Demo provası

1. `make seed`
2. `NOTIFY_DRY_RUN=false`, Telegram tedarikçisinin `chat_id`'si güncel
3. `API_URL=https://<render-adresi> make warmup` — `/api/health` → `/api/summary` (DB) → `/api/assistant/suggestions` → ilk çiple `/api/assistant/ask` (LLM). Render 15 dk boşta uyur, Neon sıfıra iner; demodan 10 dk önce koş. Zamanlayıcı uyurken durur → demoda "Şimdi kontrol et" (D18)
4. Tarayıcıda 5 sekme açık; telefon Telegram sohbetinde, ses açık
5. `docs/demo-senaryosu.md` adım adım (5 dk, kronometre); sorular yalnız çiplerden

Kontrol listesi (sunumdan 30 dk önce): seed reset · health · canlı link · Telegram test mesajı · telefon şarj · kronometre · yedek video · slaytlar PowerPoint.

## 10. Yayın (19:00–20:00)

- **API → Render**: `render.yaml` blueprint (rootDir `apps/api`, `uv sync --frozen --no-dev`, `uvicorn … --port $PORT`, health `/api/health`); env'ler panelden (`sync: false` olanlar elle); `CORS_ORIGINS` = Vercel alan adı; `NOTIFY_DRY_RUN=false`.
- **Web → Vercel**: Root Directory `apps/web`; `NEXT_PUBLIC_API_URL` = Render adresi.
- **DB → Neon**: şema + seed + `otohesap_ro` rolü (sütun düzeyi grant dâhil) uygulanmış.
- **Container (yol haritası)**: `apps/api/Dockerfile` (Azure Container Apps için hazır; bugün kullanılmaz).
- Canlı linkte demo senaryosu bir kez koşulur; gizli pencerede test edilir.
