# Görev kartı — Muratcan (dal: `murat/api-core`)

## Nasıl başlarım (5 dakika)
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh
git checkout murat/api-core
```
Sonra kendi yapay zeka aracına şu ilk mesajı at ve iki dosyayı yapıştır (`AGENTS.md` + bu kart):

> Aşağıda projenin AGENTS.md dosyası ve benim görev kartım var. Kurallara uy. Bilmediğin alan, model adı veya URL uydurma; `TODO(muratcan)` bırak ve sor. Önce 5 maddelik plan ver; onaylayınca küçük adımlarla uygula, her adımda testi koştur. İlk işim: Repo + Neon + şema + API iskeleti (10:30'a kadar main'de).

Bitince: `git add -p` → `git commit` (imza yok) → `git push -u origin murat/api-core` → PR aç (şablon dolu) → gruba "PR açık" yaz.

> Yapay zekaya ilk mesaj: "Aşağıda AGENTS.md ve görev kartım var. Kurallara uy. Bilmediğin alan/model/URL uydurma; `TODO(murat)` bırak ve sor. Önce 5 maddelik plan ver, onaylayınca küçük adımlarla uygula, her adımda testi koştur. Şu an şu adımdayım: ___"

## Rol
Mimari sahibi, entegrasyon lideri, API çekirdeği ve Text-to-SQL asistanı. Gün boyu PR'ları 15 dk içinde inceleyen kişi. Kod dışı: Notion planı ve sunumdaki "Nasıl çalışır" slaydı.

## Bugün teslim edeceklerim
1. **09:30–10:30 İskelet PR (en kritik iş; herkes bunu bekliyor)**
   - `apps/api/pyproject.toml` (uv; bağımlılıklar: fastapi, uvicorn, sqlalchemy>=2, psycopg[binary], pydantic-settings, apscheduler, httpx, anthropic, google-genai, faker, numpy; dev: pytest, ruff, httpx)
   - `app/main.py` (CORS, istek logu, tüm router'lar kayıtlı), `app/config.py` (pydantic-settings, `.env`), `app/db.py` (engine + salt-okur engine), `app/models.py` (docs/schema.sql birebir)
   - Boş router dosyaları: `summary, sales, expenses, products, analytics, assistant, orders, agent` → her biri `router = APIRouter()` + `GET /api/health` çalışır
   - `tests/conftest.py` (Postgres test DB; `DATABASE_URL`'den `_test` türetir), `tests/test_health.py`
   - `docs/schema.sql` Neon'a uygulandı; `otohesap_ro` rolü açıldı; `DATABASE_URL` ve `DATABASE_URL_RO` ekibe Neon davetiyle
   - CI yeşil. **10:30'da main'de.**
2. **10:30–13:00 Çekirdek uçlar:** `/api/summary`, `/api/cashflow/monthly` (view'den), `sales` ve `expenses` CRUD, `products` GET/PATCH (`is_critical`, `open_order_id`). Testler: seed sonrası summary rakamları sabit (Yiğit'in seed'i 11:00'de gelir; o zamana kadar 3 satırlık fixture).
3. **13:30–16:30 Text-to-SQL (`services/text2sql.py`, `services/llm.py`, `routers/assistant.py`)**
   - `llm.py`: `complete(system, user) -> str`; sağlayıcı `anthropic` (varsayılan model `.env`'den, `claude-haiku-4-5`), `gemini`, `fake` (testlerde sabit SQL döner)
   - Prompt: şema (Türkçe sütun açıklamaları) + `docs/soru-bankasi.md`'den 6 örnek + kurallar ("yalnız tek SELECT", "tarih için date_trunc", "kâr = qty*(unit_price-unit_cost)")
   - Koruma: AGENTS.md §7 birebir; `sqlglot` ile parse edip tek SELECT olduğunu doğrula (kurulumu 1 dk; olmazsa regex + `EXPLAIN`)
   - Önbellek: soru bankasındaki soru metni birebir eşleşirse LLM'e gitmeden SQL kullan (`cached:true`)
   - Özet: LLM'e yalnız sütun adları + ilk 20 satır; 1–3 cümle Türkçe
   - `GET /api/assistant/suggestions` çipleri döner
   - Testler: guard (DELETE reddi, LIMIT ekleme, `;` reddi), fake sağlayıcıyla uçtan uca
4. **16:30–19:00 Cila + inceleme:** hata gövdeleri Türkçe, `updated_at` damgası, README çalıştırma adımları, herkesin PR'ları.
5. **19:00–20:00 Yayın:** Render'a api (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`), env'ler, `CORS_ORIGINS` Vercel adresi; `/api/health` canlı.

## Bağımlılıklar
- **Bana gelen:** Yiğit'in `seed.py` (11:00), Ömer'in `orders/agent` uçları (13:00), Kutay'ın sözleşme soruları (anlık).
- **Benden giden:** iskelet (10:30), `models.py` değişiklikleri (istek → 15 dk), `assistant/ask` (16:30), PR incelemeleri (15 dk SLA).

## Dosyalarım
`apps/api/{pyproject.toml,app/main.py,config.py,db.py,models.py}`, `routers/{summary,sales,expenses,products,assistant}.py`, `services/{text2sql,llm}.py`, `tests/{conftest,test_health,test_summary,test_text2sql_guard}.py`, `docs/schema.sql`, `.github/workflows/ci.yml`, `README.md`.

## Kabul kriterleri
- 10:30: `uv run uvicorn app.main:app` → `/api/health` `{db:true}`; CI yeşil.
- 13:00: `/api/summary` seed rakamlarını döner; test sabit rakamları doğrular.
- 16:30: soru bankasındaki 15 sorudan ≥ 12'si doğru SQL üretir (Ömer'in beklenen yanıtlarıyla); 5 demo sorusu %100; guard testleri geçer.
- 20:00: canlı `/api/health` yeşil, Vercel'den istek geliyor.

## Risk ve yedek
- LLM anahtarı gecikirse: `LLM_PROVIDER=fake` + önbellekle demo soruları çalışır; anahtar gelince aç.
- Neon soğuk başlangıcı (ilk istek 1–2 sn): demo öncesi `/api/health` ile ısıt.
- sqlglot Türkçe alias'larda takılırsa: alias'ları ASCII tut, prompt'a yaz.

## Yapma
- Ekran kodu yazma (Kutay'ın alanı). `orders/agent/notify` yazma (Ömer). Seed yazma (Yiğit).
- Yeni özellik açma; sözleşmeyi duyurmadan değiştirme.

## Araştırmadan gelen notlar (13 Eyl, SONUC-chatgpt + Claude API referansı)
- **Modeller:** varsayılan `claude-haiku-4-5` (1 $/5 $ per M), kalite modu `claude-sonnet-5` (2 $/10 $). Rapordaki "Sonnet 5 doğrulanamadı" notu yanlış; Sonnet 5 Sonnet 4.6'dan ucuz. Model adına tarih eki yok. Haiku 4.5'te düşünme `budget_tokens` ister; SQL üretiminde düşünme kapalı, `max_tokens` küçük, çıktı JSON.
- **Servis hattı:** Türkçe soru → şema + 6 örnek → LLM'den JSON `{"sql": ...}` → Pydantic `SQLPlan` → sqlglot AST (tek `SELECT`/`WITH`, tablo beyaz listesi: `sales, expenses, products, suppliers, purchase_orders, v_monthly_cashflow`) → salt-okur bağlantı + `statement_timeout=5s` + `LIMIT 200` → Türkçe özet (LLM'e yalnız sütun adları + ilk 20 satır). Vanna/LangChain/LlamaIndex yok.
- **Eval:** başarı ölçütü SQL metni değil; beklenen rakam + izinli tablolar + yazma yok. `tests/test_eval.py` soru bankasını okur, `fake` sağlayıcıyla guard'ı, gerçek sağlayıcıyla (anahtar varsa, `-m live`) doğruluğu ölçer.
- **Gemini yedeği** yalnız sentetik veriyle; ücretsiz katman içeriği ürün geliştirmede kullanabiliyor (KVKK notu, DECISIONS D12).
- **`scripts/warmup.sh`:** `/api/health` + `SELECT 1` (Neon sıfıra iner) + 1 küçük LLM çağrısı + Telegram `getMe`; Render 15 dk boşta uyur, demo öncesi 10 dk'da koşulur. Zamanlayıcı Render uyuyunca fiilen durur; "Şimdi kontrol et" butonu bu yüzden şart.
- **Azure notu (jüri sorarsa):** Azure for Students sayfası Azure OpenAI erişimini listeliyor ama kota tablosunda öğrenci aboneliği "N/A" görünüyordu (7 Eyl kontrolü); doğru cümle: "erişim programda var, model/bölge/kota aboneliğimizde deploy öncesi doğrulanır".
