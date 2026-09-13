# PROMPT 1 · Teknoloji, hız ve yol haritası (derin araştırma)

> **Kullanım (önemli):** `---` çizgisinin ALTINDAKİ metni sohbet kutusuna **mesaj olarak yapıştır**. Dosya olarak **ekleme**: ilk denemede dosya eklenip yalnız "Derin araştırma" yazılınca araç prompt'u yürütmek yerine "derin araştırma nasıl yapılır" anlattı. Araç netleştirme sorusu sorarsa kısa cevap ver ("Türkiye odaklı, hepsi, hemen başla"). Sonucu `docs/research/SONUC-1-<arac>.md` olarak kaydet.

---

# GÖREV
Bu mesaj bir **araştırma brief'idir**. "Derin araştırma nasıl yapılır" anlatma, metodoloji veya araştırma protokolü yazma; aşağıdaki soruları **web'de araştırıp cevapla**. Netleştirme ihtiyacın varsa en fazla 3 kısa soru sor, yoksa hemen başla. Çıktı, aşağıdaki "ÇIKTI KURALLARI" bölümündeki biçimde olacak.

# ROL
Sen, KOBİ'lere yönelik SaaS ürünleri kurmuş bir startup CTO'su ve çözüm mimarısın. Görevin: aşağıdaki projeyi 4 kişilik bir öğrenci ekibinin **1 GÜNDE (yaklaşık 12 saat, 09:00–22:00)** uçtan uca çalışır ve canlıda yayınlanmış hale getirmesini sağlayacak, sonrasında da ürünü ölçeklendirecek teknoloji, hazır parça ve yöntemleri derinlemesine araştırmak. Mottolarımız: **Legerdemain** (kullanıcıya el çabukluğu gibi görünen sadelik: karmaşık iş arkada, tek tık önde) ve **Every second counts** (hem KOBİ sahibinin dakikaları hem bizim tek günümüz). Her önerinin ölçütü: *bugün saat kazandırıyor mu, demoda "vay" dedirtiyor mu, yarın ölçeklenebilir mi?*

# PROJE: OtoHesap
KOBİ'lerin gelir, gider, finansal analiz ve stok süreçlerini tek platformda birleştiren yapay zekâ destekli web uygulaması. Dört yetenek:
1. **Akıllı finans asistanı:** Türkçe soru ("En çok kazancım hangi üründen?") → şema temelli Text-to-SQL → PostgreSQL'de yalnız-okur rolle çalıştırma → Türkçe özet; üretilen SQL kullanıcıya gösterilir, kaynak/zaman damgası eklenir.
2. **Görsel analitik:** KPI kartları (gelir, gider, fark, kritik stok), aylık gelir-gider çubuk grafiği, gider kategorisi pastası, dönem filtresi, CSV dışa aktarma.
3. **Otonom tedarik ajanı:** stok ≤ yeniden sipariş eşiği → sipariş taslağı (ürün, miktar = hedef − mevcut, tedarikçi, tahmini tutar, mesaj metni) → **insan onayı** → Telegram Bot API ile tedarikçiye mesaj; zamanlayıcı 10 dakikada bir kontrol eder.
4. **Web arayüzü:** kurulumsuz, 5 ekran (Genel bakış, Kayıtlar, Stok, Asistan, Tedarik), giriş-çıkış CRUD.

**Karar verilmiş stack (değiştirme; hızlandır):** Next.js (App Router) + Tailwind + Recharts · FastAPI (Python 3.12) + SQLAlchemy 2 + Pydantic v2, paket yöneticisi uv, lint ruff, test pytest · PostgreSQL 16 (Neon ücretsiz katman; asistan için ayrı salt-okur rol) · LLM tek adaptör: Anthropic Claude (Haiku 4.5 / Sonnet 5) varsayılan, Google Gemini Flash yedek · APScheduler · Telegram Bot API · Faker + NumPy sentetik veri (seed=42, Nisan–Eylül 2026, 20 ürün, ~600 satış, ~250 gider, tam 2 ürün kritik stokta) · GitHub Actions CI · Yayın: Vercel (web) + Render (api) + Neon (db). Depo: github.com/muratcan-ates/Oto-Hesap (monorepo: apps/web, apps/api, data, docs).

**Veri modeli:** suppliers, products (unit_cost, sale_price, stock_qty, reorder_point, target_stock, supplier_id), sales, expenses, purchase_orders (draft/approved/sent/rejected), chat_log, v_monthly_cashflow görünümü.

**Ekip ve süreç:** 4 kişi, her biri kendi dalında (web / api-core + text-to-SQL / ajan + bildirim / veri + analitik + sunum), `main` korumalı, küçük PR, CI yeşil şartı, AGENTS.md ile her üyenin kendi yapay zeka aracına (Claude Code, Codex, Cursor, Copilot) bağlam verilmesi. Commit'lerde yapay zeka imzası yok.

**Kısıtlar:** öğrenci bütçesi (ücretsiz/çok ucuz); macOS geliştirme makineleri; Python 3.12, Node 22, Bun var; bir makinede Docker yok; Neon soğuk başlangıcı var; Azure for Students aboneliğinde Azure OpenAI model dağıtımı destek dışı olabilir (doğrula); demo bir sınıfta, okul Wi-Fi'ında, telefonla Telegram göstererek yapılacak.

**Hedef kitle ve sunum:** Medeniyet Teknopark TeknoKampüs jürisi; sunuma Trendyol gibi kurumsal şirketler ve Microsoft çözüm ortağı firmalar (Nephos AI, Pargesoft gibi) katılabilir. 10 dakika, PowerPoint, 5 dakikalık canlı demo.

# ARAŞTIRMA SORULARI

## A · Bugün saat kazandıracak hazır parçalar
Her öneri için tablo satırı: **ad · ne işe yarar · kurulum süresi (dk) · lisans/ücret · resmi bağlantı · risk/tuzak · "1 günde uygulanabilir mi" (evet/hayır/kısmen) · kaynak + tarih.**
- A1 Next.js + Tailwind + Recharts ile uyumlu **dashboard/admin şablonları ve bileşen kitleri** (shadcn/ui admin şablonları, Tremor, benzerleri): KPI kartı, tablo, modal form, sohbet balonu, kod bloğu bileşeni hazır olanlar.
- A2 **FastAPI + SQLAlchemy 2 proje şablonları / CRUD üreteçleri** (fastapi-template'ler, SQLModel, fastapi-crudrouter alternatifleri): 30 dakikada CRUD + test iskeleti veren.
- A3 **Text-to-SQL:** kütüphane ve yaklaşımlar (Vanna.ai, LangChain SQL toolkit, LlamaIndex NLSQL, sqlglot ile doğrulama, few-shot şema açıklama teknikleri); Türkçe sorularda doğruluk; koruma katmanı (tek SELECT, LIMIT, statement_timeout, salt-okur rol) en iyi uygulamaları; **15 soruluk küçük eval nasıl kurulur** (beklenen SQL/rakam karşılaştırma). Bizim durumumuzda kütüphane mi, 150 satırlık kendi servisimiz mi daha hızlı? Gerekçeli karar ver.
- A4 **Ajan:** kural tabanlı + insan onayı (human-in-the-loop) kalıpları; PydanticAI, LangGraph, Microsoft Agent Framework'ün bize bugün katkısı var mı yoksa gürültü mü? APScheduler alternatifleri (arq, Celery beat) gerekli mi?
- A5 **Bildirim:** Telegram Bot API, Meta WhatsApp Cloud API (test numarası/sandbox), Twilio WhatsApp sandbox, e-posta (Resend/SMTP): 2026 itibarıyla kurulum süresi, ücretsiz kota, Türkiye'de kısıt; hangisi demoda telefonda en etkileyici ve en güvenli?
- A6 **Sentetik veri:** Faker + NumPy ile gerçekçi KOBİ gelir-gider dağılımı (mevsimsellik, sabit giderler, marj); SDV veya LLM ile üretim gerekli mi? Deterministik seed en iyi pratikleri.
- A7 **LLM sağlayıcı:** Claude Haiku 4.5 / Sonnet 5, Gemini 2.5 Flash, OpenAI küçük modeller: Türkçe + SQL üretimi kalitesi, gecikme, ücretsiz kota/öğrenci kredisi (2026 güncel, kaynaklı), tek adaptör tasarımı; SQL üretiminde sıcaklık ve çıktı biçimi (JSON) önerileri.
- A8 **Yayın ve CI/CD:** Vercel, Render, Railway, Fly.io, Azure Container Apps (ücretsiz grant) + Azure Static Web Apps, Neon: hangisi **1 saatte canlı** olur, ücretsiz katman sınırları, soğuk başlangıç süreleri; GitHub Actions'ta Postgres servisiyle pytest; PR koruma kuralları.
- A9 **Yapay zeka destekli geliştirme akışı (4 kişi paralel):** AGENTS.md standardı ve hangi araçlar okuyor (Claude Code, Codex, Cursor, Copilot, Gemini CLI); spec-driven küçük PR akışı; AI code review; çakışmayı azaltan dosya sahipliği kalıpları; 1 günlük sprintte en çok zaman kaybettiren 10 hata ve önlemi.

## B · Ürün boşlukları (rakiplerde standart, bizde yok)
Türkiye'deki KOBİ ön muhasebe/finans araçlarında (Paraşüt, Logo İşbaşı, Mikro Jump, Bizim Hesap, Kolay Bi', Zirve, Luca, Odoo TR) standart olup OtoHesap'ta olmayan özellikleri listele; her biri için: **1 günde / 1 haftada / 1 ayda** eklenebilir mi, hangi API veya kütüphaneyle: Trendyol Marketplace (satıcı) API, Hepsiburada, N11 entegrasyonları; GİB e-Fatura/e-Arşiv entegratörleri (Foriba/Sovos, Logo, Uyumsoft, QNB eFinans, e-Logo); açık bankacılık (TCMB/BKM düzenlemeleri, banka API'leri); ödeme (iyzico, PayTR); KDV/cari/çek-senet; çoklu kullanıcı ve rol; yedekleme; KVKK. Önceliği "demo etkisi × düşük efor" ile sırala.

## C · Ölçek ve yayılma (yarından sonrası)
- Çok kiracılı (multi-tenant) SaaS mimarisine geçiş yolu (şema-başına mı, satır-başına tenant_id + RLS mi); kimlik (Clerk, Supabase Auth, Auth0, Microsoft Entra External ID); KVKK ve veri yerleşimi; yedekleme; gözlemlenebilirlik.
- **Azure yolu:** Container Apps + Azure SQL/PostgreSQL Flexible + Azure OpenAI/Foundry; Azure for Students kısıtları; Microsoft ISV Success / Marketplace / co-sell programlarına giriş şartları; bir Microsoft çözüm ortağının (Nephos AI, Pargesoft gibi) bu ürünü "referans mimari" olarak nasıl paketleyeceği.
- Ücretlendirme modelleri ve birim ekonomisi (LLM maliyeti/soru, DB maliyeti/kiracı).

## D · Yol haritası tablosu
`1 gün · 1 hafta · 1 ay · 3 ay · 12 ay` sütunlarıyla: özellik, teknoloji, efor (kişi-saat), bağımlılık, risk, demo/"vay" etkisi (1–5). 1 gün sütunu bugünkü kapsamı aşamaz; 1 hafta sütunu deneme sunumu → final arasını hedefler.

## E · Riskler ve tuzaklar
1 günlük projede zamanın en çok nerede kaybedildiği (CORS, zaman dilimi, Türkçe karakter, Neon soğuk başlangıç, LLM kota/gecikme, Recharts boş veri, Vercel env, Render uyku), Text-to-SQL halüsinasyonu ve önlemleri, demo günü kontrol listesi.

# ÇIKTI KURALLARI
- **Her iddiaya güven etiketi:** A = birincil/resmî kaynak doğrudan doğruluyor · B = birden fazla güvenilir ikincil kaynak uyumlu · C = tek ikincil kaynak · D = blog/forum (hipotez olarak) · X = doğrulanmadı. Sonunda etiket dağılımını bir satırda ver.
- **Türkçe yaz;** kaynakları hem İngilizce hem Türkçe tara.
- Her iddiaya **kaynak bağlantısı ve tarih**; 2025–2026 güncelliğini belirt; emin değilsen **"doğrulanmadı"** etiketi koy; **URL, ürün adı, fiyat veya kota uydurma.**
- Öncelik sırası: (1) 1 günde uygulanabilir, (2) ücretsiz/öğrenci dostu, (3) demo etkisi yüksek, (4) yarın ölçeklenebilir.
- Biçim: A–E bölüm başlıkları; her bölümde tablo; her tabloda "Karar önerim" satırı.
- Sonunda üç liste: **"Bugün yapılacak ilk 10 iş"** (saat tahminiyle), **"Yapmayın"** (zaman tuzakları), **"Jüriye söylenecek 5 teknik cümle."**
- Tekrar yok; her öneri tek satırda gerekçeli. Uzunluk sınırı yok, ama dolgu yok.
