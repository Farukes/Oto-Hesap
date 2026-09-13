# OtoHesap

[![ci](https://github.com/muratcan-ates/Oto-Hesap/actions/workflows/ci.yml/badge.svg)](https://github.com/muratcan-ates/Oto-Hesap/actions/workflows/ci.yml)

**Verinizi anlayın. İşinizi yönetin.** KOBİ'ler için yapay zekâ destekli finans + stok platformu: gelir-gider panosu, Türkçe soruyla veriye erişen finans asistanı (SQL görünür, yalnız okur), insan onaylı otonom tedarik ajanı. Medeniyet Teknopark TeknoKampüs Arena 2026 projesi.

| Yetenek | Ne yapar |
|---------|----------|
| Akıllı finans asistanı | "En çok kazancım hangi üründen?" → şema temelli Text-to-SQL → gerçek veriden yanıt; üretilen SQL, kaynak ve zaman görünür; salt-okur rol + AST koruması |
| Görsel analitik | KPI kartları, aylık gelir–gider, gider dağılımı, dönem filtresi, CSV; kural tabanlı **Öngörü kartları** |
| Otonom tedarik ajanı | Kritik stok → sipariş taslağı (kural, LLM'siz) → **insan onayı** → tedarikçiye Telegram mesajı; DB düzeyinde mükerrerlik koruması |
| Web arayüzü | Kurulumsuz, her cihazdan; Genel bakış · Kayıtlar · Stok · Asistan · Tedarik |

**İlke:** LLM yalnız sorguyu yazar; rakamı veritabanı, sipariş kararını kural motoru verir; dış dünyaya mesaj yalnız insan onayıyla gider.

## Hızlı başlangıç
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh                       # commit hook, .env, bağımlılıklar (uv + bun)
# .env: DATABASE_URL, DATABASE_URL_RO, LLM_PROVIDER (anthropic|gemini|groq|fake), anahtarlar
psql "$DATABASE_URL" -f docs/schema.sql  # şema (+ dosya sonundaki salt-okur rol komutları)
make seed                                # sentetik 6 ay veri (deterministik, seed=42)
make api                                 # http://localhost:8000/docs
make web                                 # http://localhost:3000
make test                                # API testleri (ayrı test veritabanı)
make warmup                              # demodan 10 dk önce
```
Ayrıntı: [specs/001-otohesap-mvp/quickstart.md](specs/001-otohesap-mvp/quickstart.md) · demo akışı: [docs/demo-senaryosu.md](docs/demo-senaryosu.md)

## Mimari
```
Tarayıcı → apps/web (Next 16, Tailwind 4, Recharts) → apps/api (FastAPI, SQLAlchemy 2)
                                                        ├─ services/text2sql  LLM → JSON → sqlglot AST → beyaz liste → salt-okur rol → özet
                                                        ├─ services/agent     eşik kontrolü → taslak → onay → notify (Telegram)
                                                        ├─ services/insights  kural tabanlı içgörüler
                                                        └─ services/llm       tek adaptör: anthropic | gemini | groq | fake
                                                        → PostgreSQL 16 (Neon) · uygulama rolü + otohesap_ro
```
Yayın: Vercel (web) · Render (`render.yaml`, api) · Neon (db). Container: `apps/api/Dockerfile`.

## Depo
`AGENTS.md` kurallar, mimari, API sözleşmesi, güvenlik ilkeleri · `docs/DECISIONS.md` kararlar · `docs/team/` görev kartları ve ekip brifi · `specs/001-otohesap-mvp/` spec-kit (spec, plan, veri modeli, sözleşme, görevler) · `docs/research/` araştırma ve kontrol notları · `docs/sunum/` pitch paketi

## Ekip
Kutay Yıldırım · Muratcan Ateş · Yiğit Yuşa Kartal · Ömer Faruk Eskitürk
