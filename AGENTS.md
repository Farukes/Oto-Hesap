# OtoHesap — Ekip ve Yapay Zeka Kuralları (AGENTS.md)

> **Bu dosya nasıl kullanılır:** Her ekip üyesi, her yapay zeka oturumunun (Claude Code, Codex, Cursor, Copilot, ChatGPT, Gemini) **ilk mesajına bu dosyayı ve `docs/team/<isim>.md` görev kartını** yapıştırır. Yapay zeka bu kuralların dışına çıkamaz. Uydurma yok: emin olmadığı yerde yer tutucu bırakır ve sorar.
>
> Mottolar: **Legerdemain** (el çabukluğu: karmaşık iş arkada, kullanıcıya tek tık) · **Every second counts** (KOBİ sahibinin dakikaları da, bizim tek günümüz de).

---

## 1 · Proje özeti

**OtoHesap**, KOBİ'lerin gelir, gider, finansal analiz ve stok süreçlerini tek platformda birleştiren yapay zekâ destekli bir web uygulamasıdır. Dört yetenek:

| # | Yetenek | Ne yapar | Demoda görünen an |
|---|---------|----------|-------------------|
| 1 | Akıllı finans asistanı | Türkçe soru → SQL → gerçek veriden yanıt; SQL her zaman görünür | "En çok kazancım hangi üründen?" → yanıt + "Sorguyu gör" |
| 2 | Görsel analitik | KPI kartları, aylık çubuk, kategori pastası, dönem filtresi | Gider eklenir, KPI ve pasta anında güncellenir |
| 3 | Otonom tedarik ajanı | Kritik stok → sipariş taslağı → **insan onayı** → tedarikçiye Telegram mesajı | "Onayla" → telefonda mesaj düşer |
| 4 | Kullanıcı dostu web arayüzü | Kurulumsuz, her cihazdan; sade giriş-çıkış ekranı | Kayıtlar: ekle / düzenle / sil |

**Ürün tezi (jüri, Trendyol gibi kurumsal katılımcılar ve Microsoft çözüm ortağı firmalar için):**
- *İşletmeler neden kullanmalı?* Excel ve karmaşık ERP arasında sıkışan KOBİ sahibi, verisine soru sorarak ulaşır; stok tükenmeden sipariş taslağı önüne gelir; hepsi tek ekranda, kurulumsuz. Zaman = para: raporlama ve tedarik takibi otonomlaşır.
- *Neden şimdi?* LLM maliyeti düştü, Text-to-SQL olgunlaştı, ajan mimarileri insan onayıyla güvenli hale geldi.
- *Nasıl büyür?* Pazar yeri entegrasyonları (Trendyol / Hepsiburada satıcı API'leri → satışlar otomatik akar), mali müşavir kanalı, çok kiracılı SaaS, Azure üzerinde referans mimari ve Marketplace. Çözüm ortağı dili: **problem → 2 haftalık pilot → ölçekleme**.
- *Kontrollü otonomi:* Ajan hiçbir mesajı onaysız göndermez; asistan veritabanına yalnız okur.
- *Pazar rakamları (TÜİK 2024, güven A, slayta girer):* 3,928 milyon KOBİ · girişimlerin %99,6'sı · istihdamın %68,5'i · cironun %44,1'i · KOBİ'lerin %35,1'i toptan/perakende ticarette. Kaynak: data.tuik.gov.tr, "Küçük ve Orta Büyüklükteki Girişim İstatistikleri, 2024".
- *Konumlama cümlesi:* "Paraşüt ve İşbaşı gibi ürünlerin güçlü olduğu e-belge, banka ve stok katmanlarını değiştirmiyoruz; OtoHesap bu verinin üstünde, doğal dille soru sorulan ve insan onayıyla aksiyona geçen karar katmanıdır." **"Rakiplerde AI yok" asla denmez.**

---

## 2 · Geliştirme Günü kapsamı (tek gün, ~12 saat)

**Durum 13 Eyl akşam:** MVP'nin tamamı `main`'de inşa edildi (API 184 test, web lint+build temiz, seed, ajan, asistan, Öngörü kartları, CSV). Geliştirme Günü artık **entegrasyon, anahtarlar, canlı yayın, eval, prova ve cila** günüdür; özellik listesi büyümez.

**Yapılır (MVP):** Neon Postgres + sentetik 6 ay veri · Genel bakış (KPI + çubuk + pasta) · Kayıtlar (satış/gider CRUD) · Stok (kritik kırmızı) · Asistan (15 soruluk bankadan en az 5'i güvenli; SQL görünür; kaynak damgası; hazır soru çipleri) · Tedarik (kontrol et → taslak → onayla → Telegram) · CSV dışa aktar · canlı yayın (Vercel + Render + Neon) · README + CI yeşil · demo videosu yedeği.

**Yapılmaz (yol haritası slaytı):** giriş/kimlik, çok kiracı, e-Fatura/e-İrsaliye, banka entegrasyonu, WhatsApp Business, mobil uygulama, Excel içe aktarma. **Bugün eklenmez:** Vanna/LangChain/LlamaIndex, LangGraph/Microsoft Agent Framework, Tremor, Azure taşıma, Trendyol entegrasyonu (yol haritasında yalnız Product V2; V1 15 Eyl 2026'da kapanıyor).

**Tek gerçek kaynak:** `docs/demo-senaryosu.md`. Bir iş demo senaryosundaki bir adımı ilerletmiyorsa bugün yapılmaz.

---

## 3 · Mimari ve teknoloji (karar verildi; yeniden tartışılmaz)

```
Tarayıcı ──> apps/web (Next.js + Tailwind + Recharts)
                │  NEXT_PUBLIC_API_URL
                ▼
            apps/api (FastAPI, Python 3.12, SQLAlchemy 2, Pydantic v2)
                ├── routers/  summary · sales · expenses · products · analytics · assistant · orders · agent
                ├── services/ text2sql (şema + örnekler → LLM → koruma → çalıştır → özet)
                │             agent (eşik kontrolü → taslak → tekrar koruması)
                │             notify (Telegram Bot API)  ·  llm (tek adaptör: anthropic | gemini | fake)
                └── APScheduler (AGENT_CHECK_INTERVAL_MIN)
                ▼
            PostgreSQL (Neon)  — uygulama rolü + asistan için salt-okur rol (otohesap_ro)
```

| Katman | Seçim | Not |
|--------|-------|-----|
| Web | Next.js (App Router) + Tailwind + Recharts; UI kiti serbest (shadcn/ui önerilir) | Kutay'ın başladığı yapı korunur |
| API | FastAPI + SQLAlchemy 2 + Pydantic v2; paket yöneticisi `uv`; lint `ruff`; test `pytest` | Tüm Python kodu tip ipuçlu |
| DB | PostgreSQL 16 (Neon ücretsiz katman) | Şema: `docs/schema.sql`; yerel test için CI'daki Postgres servisi |
| LLM | `services/llm.py` tek adaptör: `anthropic` (varsayılan `claude-haiku-4-5`; kalite modu `claude-sonnet-5`), `gemini` (ücretsiz katman içeriği ürün geliştirmede kullanabiliyor → yalnız sentetik veri), `groq` (OpenAI uyumlu uç, ücretsiz katman dakika/gün sınırlı; Türkçe SQL kalitesi 15 soruluk eval'le ölçülür), `fake` (testler) | Model adı yalnız `.env`'de; çıktı JSON (`SQLPlan`), sıcaklık düşük |
| Ajan | Kural tabanlı (LLM'siz) + APScheduler; mesaj metni şablon, LLM ile cilalama opsiyonel | Deterministik = demo güvenli |
| Bildirim | Telegram Bot API (`notify.py`) | Tedarikçi kaydında `contact_channel='telegram'`, `contact_address=<chat_id>` |
| Veri | `data/seed.py`: Faker + NumPy, `seed=42`, `--reset` bayrağı | Her çalıştırmada aynı rakamlar |
| Yayın | Vercel (web) · Render (api) · Neon (db); ikisi de `main`'den otomatik | Azure (Container Apps + Azure SQL) yol haritası |
| CI | GitHub Actions `.github/workflows/ci.yml`: api ruff+pytest, web lint+build | PR yeşil olmadan merge yok |

---

## 4 · Depo yapısı ve sahiplik

```
Oto-Hesap/
  AGENTS.md                 bu dosya (herkes)
  README.md · Makefile      jüriye dönük özet; make api / web / seed / test / lint / warmup
  .env.example              ortam değişkenleri (değişen kişi günceller)
  render.yaml               Render blueprint (api); web Vercel'de rootDir=apps/web
  .github/workflows/ci.yml  CI (Murat) · PULL_REQUEST_TEMPLATE.md
  scripts/                  setup.sh, warmup.sh, github-setup.sh, hooks/commit-msg
  .specify/ · specs/001-otohesap-mvp/   spec-kit: anayasa, spec, plan, veri modeli, sözleşme, görevler
  .claude/skills/speckit-*  spec-kit komutları (/speckit-specify, -plan, -tasks, -implement)
  docs/
    demo-senaryosu.md       TEK GERÇEK KAYNAK (Ömer sahibi)
    schema.sql              veri modeli (Murat sahibi; değişiklik = duyuru)
    soru-bankasi.md         15 soru (Ömer + Yiğit); makine kopyası apps/api/app/data/soru_bankasi.json
    DECISIONS.md            kararlar · team/*.md görev kartları · research/*.md · sunum/pitch-paketi.md
  apps/api/                 FastAPI (Python 3.12, uv)
    app/config.py db.py models.py main.py          çekirdek (Murat)
    app/routers/  summary sales expenses products assistant   (Murat)
                  analytics export insights                     (Yiğit)
                  orders agent                                  (Ömer)
    app/services/ llm.py text2sql.py (Murat) · agent.py notify.py scheduler.py (Ömer) · insights.py (Yiğit)
    app/schemas/  pydantic şemaları (alan sahibi)
    app/data/soru_bankasi.json
    tests/        conftest.py (Murat) + alan testleri
    Dockerfile
  apps/web/                 Next 16 + Tailwind 4 + Recharts (Kutay): app/{page,kayitlar,stok,asistan,tedarik}, components/, lib/api.ts, lib/mocks/
  data/seed.py              sentetik veri (Yiğit)
```

**Çakışma kuralı:** `models.py`, `schema.sql`, `main.py` yalnız Murat değiştirir; ihtiyaç WhatsApp'ta yazılır, 15 dk içinde main'e gelir. Router dosyaları iskelette boş `APIRouter()` ile açılır, sahibi doldurur.

---

## 5 · Veri modeli (özet; tam DDL `docs/schema.sql`)

| Tablo | Alanlar |
|-------|---------|
| `suppliers` | id, name, contact_channel (`telegram`/`email`), contact_address, lead_time_days |
| `products` | id, name, category, unit_cost, sale_price, stock_qty, reorder_point, target_stock, supplier_id |
| `sales` | id, sold_at, product_id, qty, unit_price, total, channel (`magaza`/`online`) |
| `expenses` | id, spent_at, category (kira, maas, elektrik, kargo, reklam, tedarik), amount, vendor, note |
| `purchase_orders` | id, created_at, product_id, supplier_id, qty, est_amount, status (`draft`/`approved`/`sent`/`rejected`), message_text, sent_at |
| `chat_log` | id, asked_at, question, sql_text, answer, ok |
| `v_monthly_cashflow` (view) | month, income, expense, net |

**Metrik sözlüğü (D16; grafik, SQL, slayt aynı tanımı kullanır):**

| Terim | Tanım | Ekranda |
|-------|-------|---------|
| Gelir | Σ `sales.total` (satış anı fiyatı × adet) | "Gelir" |
| Gider | Σ `expenses.amount` | "Gider" |
| Fark | Gelir − Gider; **net kâr değildir** (KDV, iade, tahakkuk yok) | "Fark (Gelir − Gider)" |
| Tahmini brüt katkı | Σ qty × (unit_price − products.unit_cost); mevcut birim maliyetle | "En kârlı ürün (tahmini)" |
| Aylık görünüm | `v_monthly_cashflow`: ay, gelir, gider, fark | "Aylık gelir–gider" (nakit akışı denmez) |
| Sipariş `sent` | Mesaj gönderildi; teslim/kabul/ödeme değil; stok artmaz | "Gönderildi" + "teslim alındı değil" notu |

Seed hedefi: teknoloji aksesuar mağazası senaryosu; 20 ürün / 5 kategori / 5 tedarikçi; Nisan–Eylül 2026; ~600 satış, ~250 gider; **tam 2 ürün kritik stokta**; kâr sorusunun tek net kazananı var (powerbank). Kritik: `stock_qty <= reorder_point`.

---

## 6 · API sözleşmesi v0 (herkes buna göre kodlar; değişiklik = PR + duyuru)

```
GET    /api/health                                -> {status:"ok", db:true, llm:"anthropic"}
GET    /api/summary?period=month|quarter|half     -> {income, expense, net, critical_count, updated_at}
GET    /api/cashflow/monthly                      -> [{month:"2026-04", income, expense, net}]
GET    /api/analytics/expenses-by-category?period -> [{category, amount, share}]
GET    /api/analytics/sales-by-product?period&top -> [{product_id, product, revenue, profit, qty}]
GET    /api/sales?limit&offset&q                  -> {items:[...], total}
POST   /api/sales {sold_at, product_id, qty, unit_price, channel}   -> 201 kayıt
PUT    /api/sales/{id}  · DELETE /api/sales/{id}
GET/POST/PUT/DELETE /api/expenses (aynı kalıp; alanlar: spent_at, category, amount, vendor, note)
GET    /api/products                              -> [{..., is_critical, open_order_id}]
PATCH  /api/products/{id} {reorder_point?, target_stock?, stock_qty?}
POST   /api/assistant/ask {question}              -> {ok, answer, sql, rows, columns, sources:[tablo...], asked_at, cached, model}
GET    /api/assistant/suggestions                 -> ["Bu ay toplam giderim ne kadar?", ...]
POST   /api/agent/check                           -> {created:int, drafts:[...], skipped:[{product_id, reason}]}
GET    /api/insights                              -> [{id, title, body, severity: info|warn|critical, metric, change_pct}]
GET    /api/orders?status=draft|approved|sent|rejected -> [...]
POST   /api/orders/{id}/approve                   -> sipariş + notify:{ok, dry_run, channel, message_id}; 409 draft değilse; 502 gönderilemedi (approved kalır)
POST   /api/orders/{id}/reject                    -> {status:"rejected"}
GET    /api/export/sales.csv · /api/export/expenses.csv
```

Kurallar: tarihler ISO 8601 UTC; para `NUMERIC(12,2)` → JSON'da string değil **number**; hata gövdesi `{detail:"Türkçe açıklama"}`; 4xx kullanıcı hatası, 5xx bizim hatamız; `period` varsayılanı `half` (6 ay).

---

## 7 · Asistan (Text-to-SQL) güvenlik ilkeleri — pazarlık yok

1. DB bağlantısı `DATABASE_URL_RO` (salt-okur rol).
2. Üretilen SQL: tek ifade, `SELECT` veya `WITH ... SELECT` ile başlar; `;`, `--`, `/*`, DDL/DML anahtar kelimeleri reddedilir.
3. `LIMIT` yoksa `LIMIT 200` eklenir; sorgu zaman aşımı 5 sn (`statement_timeout`).
4. Hata → hata mesajıyla **bir** yeniden deneme; yine hata → "Bu soruyu bu veriyle yanıtlayamadım." (uydurma yok).
5. Yanıt özeti yalnız sorgu sonucundan; sayı eklenmez, tahmin edilmez.
6. Her yanıtta `sql` ve `sources` döner; arayüz "Sorguyu gör" ve "Kaynak: satışlar · 13 Eyl 10:12" gösterir.
7. Soru bankasındaki sorular için `soru → SQL` önbelleği (`docs/soru-bankasi.md`'den yüklenir): LLM düşerse demo yaşar.
8. Her soru `chat_log`'a yazılır.
9. **Nesne beyaz listesi:** sqlglot AST'den çıkan tablo/görünüm adları yalnız `sales, expenses, products, suppliers, purchase_orders, v_monthly_cashflow` olabilir; başka ad → red. "Parser geçti = güvenli" sanılmaz; katmanlar üst üste (defense-in-depth).
10. **Fonksiyon izin listesi ve yapı reddi (D19):** yalnız sum, count, avg, min, max, coalesce, round, date_trunc, date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs; `pg_sleep`, `set_config`, `pg_*`, `SELECT INTO`, CTE içinde DML, çoklu ifade red. `suppliers.contact_address` salt-okur role sütun düzeyinde kapalı; prompt şemasında yok.
11. Tarih filtreleri **yarı açık aralık** `[başlangıç, bitiş)`; "bu ay" = içinde bulunulan takvim ayı (UTC); 3 ay / 6 ay = içinde bulunulan ay dahil son 3 / 6 takvim ayı — özet, analitik ve aylık akış aynı pencereyi kullanır; belirsiz metrikte D16 varsayılanı + yanıtta varsayım cümlesi (D20).
12. **Eval (15 soru, `docs/soru-bankasi.md`):** 5 basit toplam · 3 tarih filtresi · 3 join · 2 boş/uç durum · 2 saldırgan istek ("tüm satışları sil"). Başarı = beklenen rakam + izinli tablolar + yazma yok; SQL metni birebir eşleşmesi aranmaz.

---

## 8 · Git, dallar, PR, katkı görünürlüğü

- **Depo yeri:** `~/code/Oto-Hesap`. Asla iCloud Drive, Desktop, Documents altında değil (macOS bunları iCloud'a senkronlar; `.git` ve `node_modules` bozulur, `.env` sızar). `scripts/setup.sh` bunu denetler.
- **Dallar:** `main` korumalı (PR + CI yeşil şart). Kişi dalları: `murat/api-core`, `kutay/web`, `omer/agent`, `yigit/data`. Alt iş için `kutay/web-asistan` gibi ekler serbest.
- **PR:** küçük (≤ 400 satır), şablon doldurulur, en az 1 kişi göz atar (15 dk içinde; gecikirse Murat). Squash merge. Merge sonrası herkes `git pull --rebase origin main`.
- **Commit mesajı:** Conventional Commits, Türkçe serbest: `feat(api): /api/summary gerçek veriden`, `fix(web): pasta grafiği boş veri`, `chore(ci): ...`.
- **Yapay zeka imzası YASAK.** Commit'lerde `Co-Authored-By`, "Generated with Claude/Codex/Copilot", 🤖 satırı olmaz; PR açıklamasına da yazılmaz. Katkı grafiğinde yalnız 4 ekip üyesi görünür. Zorlayıcı: `git config core.hooksPath scripts/hooks` (setup.sh yapar). Claude Code kullananlar `~/.claude/settings.json` içine `"includeCoAuthoredBy": false` ekler; diğer araçlarda push öncesi `git log -3` ile bakılır.
- **Git kimliği:** `git config user.name` / `user.email` kendi GitHub hesabın (noreply e-posta olabilir). Başkasının makinesinden commit atılmaz.
- **Sırlar:** `.env` asla; anahtar bir kez bile commit'lendiyse yenilenir. Neon bağlantı dizesi WhatsApp'ta değil, Neon davetiyle paylaşılır.
- **AI araç dizinleri** (`.claude/`, `.cursor/`, `.codex/`) `.gitignore`'da; kişisel kalır.

---

## 9 · AI-SDLC: yapay zekayla nasıl çalışıyoruz (hafif, 1 günlük sürüm)

**Spec-kit (kurulu):** `.specify/memory/constitution.md` ilkeler, `specs/001-otohesap-mvp/` altında `spec.md` (kullanıcı hikâyeleri + kabul senaryoları), `plan.md`, `data-model.md`, `contracts/api.md`, `quickstart.md`, `tasks.md` (görev listesi, sahip ve [P] paralellik etiketiyle). Claude Code kullananlar `/speckit-tasks`, `/speckit-implement` komutlarını görür; diğer araçlar aynı dosyaları bağlam olarak alır. Yeni bir özellik = `specs/00N-<ad>/` altında önce spec, sonra kod. `.specify/scripts/*` git dalı açar; dal modelimizle çakışmaması için o script'ler çalıştırılmaz, klasör elle açılır.


1. **Bağlam ver:** oturumun ilk mesajı = `AGENTS.md` + görev kartın + dokunacağın dosyalar. Bağlamsız "şunu yap" yok.
2. **Önce plan, sonra kod:** yapay zekadan 5 maddelik plan iste, onayla, sonra küçük adımlarla uygulat. Her adım çalışır durumda biter.
3. **Uydurma yasağı:** "Bilmediğin API alanı, model adı, URL uydurma; `TODO(<isim>)` yer tutucusu bırak ve sor." Bu cümle her oturumda.
4. **Test yazdır:** her uç için en az bir `pytest`; seed sonrası özet rakamlar sabit (test bunları doğrular).
5. **AI inceleme:** PR açmadan önce diff'i yapay zekaya "hata, güvenlik, sözleşmeye uyum" için incelet; bulguları PR'a yaz.
6. **İnsan kontrolü:** çalıştırıp gözünle gör; ekran görüntüsü PR'a.
7. **Kararlar:** teknoloji/sözleşme değişikliği `docs/DECISIONS.md`'ye satır + WhatsApp duyurusu.
8. **Zaman kutusu:** bir işte 45 dk ilerleme yoksa WhatsApp'a yaz; 15 dk içinde eşleşme (pair) yapılır. Blokajı gizlemek en pahalı hata.

---

## 10 · Mühendislik mükemmelliği: bitti tanımı (Definition of Done)

- [ ] Sözleşmedeki uç/ekran birebir; Türkçe hata mesajları; boş veri durumu ele alınmış
- [ ] Lint temiz, testler geçiyor, CI yeşil
- [ ] Tip ipuçları (Python) / TypeScript strict; `any` yok
- [ ] Loglama: her istek satırı (yöntem, yol, süre); asistan ve ajan kararları loglanır
- [ ] `.env.example` ve `AGENTS.md` güncel; README'de çalıştırma adımı doğru
- [ ] Demo senaryosu baştan sona bozulmamış (PR'ı açan bir kez koşar)
- [ ] Sır yok, AI imzası yok

---

## 11 · Geliştirme Günü çizelgesi v2 (09:00–22:00; tarih toplantıda)

Ürün `main`'de çalışır durumda. Gün, "kodu yazma" değil **"canlıya al, doğrula, prova et"** günüdür.

| Saat | Kilometre taşı | Kim |
|------|----------------|-----|
| 09:00–09:30 | Kickoff: `git pull`, `make setup`, `.env` (Neon URL'leri Murat'tan, anahtarlar), `make seed && make api && make web`; herkes demo senaryosunu yerelde bir kez sürer | Herkes |
| 09:30–11:00 | **Murat:** Neon'da şema + `otohesap_ro` + seed; Render'a API (`render.yaml`), env'ler, CORS; `/api/health` canlı. **Kutay:** Vercel'e web (`NEXT_PUBLIC_API_URL` = Render), kendi dokunuşları, mobil kontrol. **Ömer:** Telegram botu + chat_id'yi tedarikçiye yaz (`data/README.md`), `NOTIFY_DRY_RUN=false` ile gerçek mesaj testi. **Yiğit:** seed özetindeki rakamları `docs/soru-bankasi.md`'ye işle, ekran görüntüleri, slayt iskeleti | Herkes |
| **11:00** | **Checkpoint 1:** canlı link açılıyor, telefonda gerçek Telegram mesajı düştü | Herkes |
| 11:00–13:00 | **Murat + Ömer:** `make eval` gerçek sağlayıcıyla (Gemini/Groq/Anthropic) → 15 sorudan kaçı doğru; kaçıranlar için few-shot/prompt düzeltmesi; sağlayıcı kararı (D15). **Kutay:** hata/boş durum cilası, canlıda CSV, "Sorguyu gör". **Yiğit:** slaytlar (pitch-paketi), README görselleri | Herkes |
| **13:00** | **Checkpoint 2 (öğle):** canlıda demo turu 1, kronometreyle | Herkes |
| 13:30–16:30 | Bulunan hataların düzeltilmesi; jüri soruları provası (pitch-paketi'ndeki 10 soru); Öngörü kartı metinleri; "Fark ≠ net kâr", "sent ≠ teslim" cümleleri sunum metninde; `scripts/warmup.sh` canlı adrese | Herkes |
| **16:30** | **Checkpoint 3:** demo turu 2 canlıda + telefon; video kaydı (3 dk) | Ömer sürer |
| 16:30–19:00 | Slaytlar final (PowerPoint), sunum metni, kapanış cümleleri; README son hal | Yiğit + Ömer |
| **19:00** | **DONDURMA.** Yalnız bloklayıcı hata; `v0.1.0` etiketi | Murat |
| 19:00–21:00 | Prova 3 (okul Wi-Fi senaryosu: hotspot), yedek video kontrol, seed reset provası | Herkes |
| 21:00 | Durulur | Herkes |

**İletişim:** saat başı WhatsApp'a 1 satır; checkpoint'lerde 10 dk görüntülü. Blokaj 45 dk'yı geçince yaz.

## 12 · Sunum notu (kısa)

10 dk, PowerPoint, 9 slayt; ayrıntı `docs/demo-senaryosu.md` ve Notion planı. Jüride kurumsal ve Microsoft çözüm ortağı katılımcılar olabilir: **README, CI rozeti, canlı link, temiz commit geçmişi** görünür kalite göstergesidir. Demo yalnız soru bankasındaki sorularla yapılır. Sunumda "Fark" net kâr diye anlatılmaz, "en kârlı ürün" tahmini brüt katkıdır, veri "sentetik demo" diye etiketlenir, Render Free'de zamanlayıcının uyuduğu saklanmaz ("Şimdi kontrol et" aynı fonksiyondur).

---

## 13 · Araştırma bulguları (13 Eyl 2026)

- Tam rapor: `docs/research/SONUC-chatgpt-2026-09-13.md` (iki brief'i birleştirip yürüten ChatGPT deep research; güven etiketleri A–X).
- Doğrulama notu: `docs/research/KONTROL-2026-09-13.md` — hangi iddia birincil kaynaktan doğrulandı, hangisi düzeltildi (Sonnet 5, Paraşüt fiyatı, katılımcı/müşteri sayıları).
- Pitch paketi: `docs/sunum/pitch-paketi.md` (9 slayt, 3 cümle, asansör konuşması, 5 slogan, 10 jüri sorusu, kapanış cümleleri).
- Aksiyon ve yapmayın listesi: `docs/research/aksiyon-listesi.md`.
- Kararlar D8–D15: `docs/DECISIONS.md`.
