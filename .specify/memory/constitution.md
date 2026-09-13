<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0 (MINOR: D16–D20 ile ilkelere yeni, test edilebilir kurallar eklendi)
- Modified principles:
  I. Kontrollü Otonomi — `sent ≠ teslim`, DB düzeyinde tekrar koruması, gönderim izi, kör tekrar yok (D17)
  II. Şeffaflık — metrik sözlüğü (D16), belirsiz metrikte varsayım cümlesi (D20), yanıtta `model`
  III. Salt-Okur Asistan — fonksiyon izin listesi, yapı reddi, sütun düzeyi grant, yarı açık tarih (D19, §7.11–12)
  V. Basitlik — zamanlayıcı dürüstlüğü (D18)
- Added sections: yok
- Removed sections: yok
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md — specs/001-otohesap-mvp/plan.md "Constitution Check" tablosu güncellendi; şablon metni değişmedi
  ✅ .specify/templates/spec-template.md — değişiklik gerekmedi
  ✅ .specify/templates/tasks-template.md — değişiklik gerekmedi
- Follow-up TODOs: yok
-->
# OtoHesap Constitution

## Core Principles

### I. Kontrollü Otonomi
- LLM yalnızca SQL yazar (ve isteğe bağlı olarak Türkçe özet cümlesini üretir). Rakam her zaman
  veritabanından gelir; LLM'in ürettiği hiçbir sayı yanıta eklenmez, tahmin edilmez.
- Sipariş kararını deterministik kural motoru verir: `stock_qty <= reorder_point` → taslak,
  `qty = target_stock - stock_qty` (en az 1), `est_amount = qty * unit_cost`. LLM karar
  mekanizmasına girmez.
- Dış iletişim (Telegram) yalnızca insan onayından sonra gerçekleşir. Durum makinesi
  `draft → approved → sent | rejected`; `draft`'tan `sent`'e insan adımı olmadan geçiş YASAKTIR.
  Zamanlayıcı yalnızca taslak üretir; hiçbir zamanlanmış iş mesaj göndermez.
- `sent` = "mesaj gönderildi"; teslim, kabul veya ödeme DEĞİLDİR; stok artmaz (D17). `sent` de
  yeni taslağı bloke eder.
- Tekrar koruması DB düzeyindedir: kısmi tekil indeks `ux_open_order_per_product` ürün başına tek
  `draft|approved|sent` siparişe izin verir; çift tıklama veya çift zamanlayıcı ikinci sipariş
  üretemez. Gönderim izi `purchase_orders.notify_ref`'te saklanır (Telegram `message_id` /
  `dry-run`). Belirsiz sonuçta kör tekrar yoktur: sipariş `approved` kalır, insan tekrar dener.
- Mesaj metni "DEMO · sentetik sipariş #id" önekiyle başlar; gerçek sipariş sanılmaz.

Gerekçe: Jüriye ve müşteriye verilen söz "AI önerir, siz onaylarsınız". Deterministik ajan = demo
güvenliği; DB düzeyinde tekillik = çift/yanlış tedarik aksiyonuna karşı sigorta (AGENTS.md §1, §3;
D17; katalog analizi MidRule/SafeGuard; SONUC-1 A4).

### II. Şeffaflık
- Her asistan yanıtı `sql`, `sources` (kullanılan tablolar), `asked_at` (zaman damgası), `ok` ve
  `model` (yanıtı üreten model adı) döner; arayüz "Sorguyu gör" ve "Kaynak: satışlar · 13 Eyl 10:12"
  gösterir.
- Metrik sözlüğü (D16) tek ve ortaktır; grafik, SQL, yanıt ve slayt aynı tanımı kullanır:
  Gelir = Σ `sales.total` · Gider = Σ `expenses.amount` · **Fark** = Gelir − Gider (net kâr
  DEĞİLDİR: KDV, iade, tahakkuk yok) · "En kârlı ürün" = **tahmini brüt katkı** =
  Σ qty × (unit_price − products.unit_cost), mevcut birim maliyetle, ekranda "tahmini" denir ·
  aylık görünüm "Aylık gelir–gider" (nakit akışı denmez).
- Belirsiz soruda ("en çok kazancım") `clarify` durumu yoktur; D16 varsayılanı uygulanır ve yanıt
  metni varsayımı söyler ("mevcut birim maliyetle tahmini brüt katkı") (D20).
- Her soru `chat_log`'a (`question, sql_text, answer, ok`) yazılır; her ajan kararı ve her onay
  loglanır; sipariş kaydı `message_text`, `sent_at`, `notify_ref` ile iz bırakır.
- Yanıtlanamayan soru için sabit cümle: "Bu soruyu bu veriyle yanıtlayamadım." Uydurma yoktur.
- Veri arayüzde "sentetik demo verisi" diye etiketlenir.

Gerekçe: Kara kutu değil karar katmanı; yanlış finansal iddia ("net kâr") jüride puan kaybettirir
(AGENTS.md §5 sözlük, §7.5–§7.8; D16, D20; SONUC-1 A3).

### III. Salt-Okur Asistan ve Derinlemesine Savunma (PAZARLIK YOK)
Katmanlar üst üste uygulanır; hiçbiri tek başına yeterli sayılmaz ("parser geçti = güvenli" ve
"SELECT ise güvenli" yanılgıları reddedilir):
1. Asistan bağlantısı `DATABASE_URL_RO` (ayrı `otohesap_ro` rolü, yalnız SELECT yetkisi);
   bağlantı düzeyinde `default_transaction_read_only=on`, `statement_timeout=5000`.
2. `suppliers.contact_address` salt-okur role **sütun düzeyinde kapalı** (REVOKE + sütun GRANT) ve
   prompt şemasında yoktur; `chat_log` ve sistem katalogları beyaz listede değildir.
3. Üretilen SQL tek ifadedir; `SELECT` / `WITH … SELECT` / set işlemi ile başlar; `;`, `--`, `/*`
   reddedilir. Yapı reddi: DDL/DML düğümü (CTE içinde dahi), `SELECT INTO`, `FOR UPDATE/SHARE`,
   çoklu ifade.
4. sqlglot AST'den çıkan tablo/görünüm adları yalnızca `sales, expenses, products, suppliers,
   purchase_orders, v_monthly_cashflow`; şema yalnız `public`.
5. Fonksiyon izin listesi (D19): yalnızca sum, count, avg, min, max, coalesce, round, date_trunc,
   date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least,
   abs. `pg_sleep`, `set_config`, `pg_read_file`, `pg_*`, `dblink`, `lo_*` vb. red.
6. `LIMIT` yoksa `LIMIT 200` eklenir; 200'den büyükse 200'e çekilir.
7. Tarih filtreleri yarı açık aralık `[başlangıç, bitiş)`; "bu ay" = içinde bulunulan takvim ayı
   (UTC) (§7.12).
8. Hata → hata mesajıyla BİR yeniden deneme; yine hata → sabit "yanıtlayamadım" cümlesi.
   Güvenlik reddi daha gevşek bir modele tekrar sorulmaz.
9. Reddedilen istek de `chat_log`'a `ok=false` ile yazılır.

Gerekçe: "AI'a veritabanının anahtarını vermiyoruz" (AGENTS.md §7; D2, D9, D19).

### IV. Test-First ve Yeşil CI
- Her API ucu için en az bir `pytest`; koruma katmanı için ayrı guard testleri (DML reddi, `;`
  reddi, LIMIT ekleme/kırpma, beyaz liste, CTE içinde DML, `SELECT INTO`, yasak fonksiyon).
- Seed deterministiktir (`seed=42`, sabit aralık 2026-04-01…2026-09-13); seed sonrası özet
  rakamlar sabittir ve testler bunları doğrular (tam 2 kritik ürün, tam 1 ürün eşiğin 1 üstünde,
  powerbank tek net kâr lideri).
- Testler `LLM_PROVIDER=fake`, `NOTIFY_DRY_RUN=true` ile koşar; canlı sağlayıcı testleri yalnızca
  `-m live` işaretiyle; soru bankası (`apps/api/app/data/soru_bankasi.json`) şekil, dağılım ve
  izinli tablo testlerinden geçer.
- `main`'e yalnızca PR ile ve CI (ruff + pytest, lint + build) yeşilken merge edilir.

Gerekçe: Model değişince regresyon ölçülsün; demo rakamları prova ile aynı olsun (AGENTS.md §9.4,
§10; D15).

### V. Basitlik (YAGNI) ve Dürüst Altyapı
- Framework eklenmez: Vanna, LangChain, LlamaIndex, LangGraph, Microsoft Agent Framework,
  PydanticAI, arq/Celery, Tremor bugün YOKTUR. Text-to-SQL kendi servisimizdir.
- Yönetilen servisler: Neon (DB), Render (API), Vercel (web). Azure taşıma yol haritasıdır.
- Zamanlayıcı dürüstlüğü (D18): Render Free 15 dk boşta uyur ve süreç içi zamanlayıcı durur;
  "kesintisiz 10 dakikada bir kontrol" vaat edilmez, sunumda saklanmaz. Demoda "Şimdi kontrol et"
  aynı `run_check` fonksiyonudur. Sürekli çalışma = Render ücretli instance (final sonrası karar);
  ücretsiz servisi sürekli ping ile ayakta tutmak mimari değildir. Vercel Hobby ticari değil →
  SaaS'ta Pro.
- Kapsam tek gün; `docs/demo-senaryosu.md` tek gerçek kaynaktır. Demo senaryosundaki bir adımı
  ilerletmeyen iş bugün yapılmaz.
- `models.py`, `docs/schema.sql`, `main.py` yalnız Murat değiştirir; API sözleşmesi (AGENTS.md §6)
  değişikliği = PR + duyuru + `docs/DECISIONS.md` satırı.

Gerekçe: Dar şema + 15 soru için soyutlama denetlenebilirliği düşürür; ücretsiz katman sınırları
resmîdir (D9, D18; aksiyon-listesi "Yapmayın"; SONUC-1 A8).

### VI. Katkı Görünürlüğü ve Depo Hijyeni
- Commit'lerde ve PR açıklamalarında yapay zeka imzası YOKTUR (`Co-Authored-By`, "Generated with",
  🤖). `scripts/hooks/commit-msg` bunu zorlar; `core.hooksPath` setup ile ayarlanır.
- `.env` asla commit edilmez; sızan anahtar yenilenir; Neon bağlantı dizesi ve bot token'ı hiçbir
  sohbete, log satırına veya hata mesajına yazılmaz.
- Depo `~/code/Oto-Hesap` altındadır; iCloud Drive / Desktop / Documents yasaktır
  (`scripts/setup.sh` denetler).
- AI araç dizinleri (`.claude/`, `.cursor/`, `.codex/`) `.gitignore`'dadır; yalnız spec-kit
  komutları depoda kalır.

Gerekçe: Katkı grafiğinde yalnız 4 ekip üyesi görünür; sır ve senkron kazaları önlenir (D4, D5;
AGENTS.md §8).

### VII. Türkçe Kullanıcı Yüzü
- Arayüz metinleri, hata gövdeleri (`{detail: "Türkçe açıklama"}`), asistan yanıtları, Telegram
  mesajları ve öngörü kartları Türkçedir. Teknik terimler, kod ve alan adları İngilizce kalabilir.
- Para arayüzde `tr-TR` biçiminde (1.234,56 ₺), tarih `Europe/Istanbul` ile gösterilir; CSV
  Excel (TR) uyumludur (UTF-8 BOM, `;`, ondalık virgül).
- API'de tarih ISO 8601 UTC, para `NUMERIC(12,2)` → JSON `number` (string değil).

Gerekçe: Hedef kullanıcı KOBİ sahibi; jüri Türkçe (AGENTS.md §6 kurallar, Kutay kartı).

## Teknoloji ve Güvenlik Kısıtları

- Yığın karar verilmiştir, yeniden tartışılmaz (AGENTS.md §3): Next.js 16 App Router + Tailwind 4
  + Recharts 3 (web, Bun); FastAPI + SQLAlchemy 2 + Pydantic v2, `uv`, `ruff`, `pytest` (api);
  PostgreSQL 16 / Neon (db); APScheduler 3.x (ajan zamanlayıcı); Telegram Bot API (bildirim);
  `Makefile`, `render.yaml`, `apps/api/Dockerfile` (çalıştırma ve yayın).
- LLM tek adaptör arkasındadır (`services/llm.py`): `anthropic` varsayılan `claude-haiku-4-5`,
  kalite modu `claude-sonnet-5`; `gemini` yalnız yedek ve yalnız sentetik veriyle; `groq`
  (OpenAI uyumlu uç, ücretsiz katman sınırlı; Türkçe SQL kalitesi eval ile ölçülür); `fake`
  testler için. Model adı yalnız `.env`'de; çıktı JSON (`SQLPlan`), sıcaklık düşük (D10).
- KVKK: demo verisi %100 sentetik. LLM'e satır değil şema + sınırlı sonuç gider; loglarda kişisel
  veri yoktur (D12).
- Yayında CORS yalnız üretim alan adı + yerel geliştirme adresi.
- Tek kiracı. Giriş/kimlik, çok kiracı, e-Fatura, banka, WhatsApp, mobil, Excel içe aktarma kapsam
  dışıdır (AGENTS.md §2).

## Geliştirme Akışı ve Kalite Kapıları

- Dallar: `main` korumalı; kişi dalları `murat/api-core`, `kutay/web`, `omer/agent`, `yigit/data`
  (alt dallar serbest). PR ≤ 400 satır, şablon dolu, 15 dk içinde en az 1 inceleme, squash merge,
  sonra `git pull --rebase origin main` (D6). Spec-kit script'leri (`.specify/scripts/*`) dal
  açtığı için çalıştırılmaz; klasör elle açılır.
- Bitti tanımı (AGENTS.md §10): sözleşme birebir · Türkçe hata · boş veri ele alınmış · lint temiz
  ve testler geçiyor · tip ipuçları / TS strict (`any` yok) · istek ve karar logları ·
  `.env.example` ve README güncel · demo senaryosu bozulmamış · sır ve AI imzası yok.
- AI-SDLC (AGENTS.md §9): oturumun ilk mesajı `AGENTS.md` + görev kartı; önce 5 maddelik plan;
  uydurma yasağı (`TODO(<isim>)` bırak ve sor); her uç için test; PR öncesi AI inceleme; insan
  gözüyle çalıştırma; 45 dk ilerleme yoksa WhatsApp'a yaz.
- Çizelge: Geliştirme Günü 09:00–22:00; checkpoint'ler 10:30 / 13:00 / 16:30; **19:00 özellik
  dondurma** (yalnız hata düzeltme); 20:00 yayın; 21:00 prova (D7, AGENTS.md §11).

## Governance

- Bu anayasa `AGENTS.md` ile birlikte değişir: ikisi çelişirse önce `AGENTS.md` düzeltilir, sonra
  bu belge sürümlenir. `docs/DECISIONS.md` kararların kaydıdır; anayasayı etkileyen her karar orada
  bir satır alır ("Neden" boş olan karar sayılmaz).
- Sürümleme: MAJOR = ilke kaldırma/yeniden tanımlama; MINOR = yeni ilke, bölüm veya ilkeye eklenen
  yeni kural; PATCH = ifade düzeltmesi. Değişiklik PR ile gelir, `Sync Impact Report` yorumu
  güncellenir.
- Her PR incelemesi bu ilkelere uyumu kontrol eder; karmaşıklık artışı `plan.md` "Complexity
  Tracking" tablosunda gerekçelendirilmeden kabul edilmez.
- Çalışma zamanı rehberi: `AGENTS.md` (kurallar, mimari, sözleşme, metrik sözlüğü),
  `docs/team/<isim>.md` (görev kartları), `docs/demo-senaryosu.md` (tek gerçek kaynak).

**Version**: 1.1.0 | **Ratified**: 2026-09-13 | **Last Amended**: 2026-09-13
