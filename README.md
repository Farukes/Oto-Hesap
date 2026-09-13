# OtoHesap

[![ci](https://github.com/muratcan-ates/Oto-Hesap/actions/workflows/ci.yml/badge.svg)](https://github.com/muratcan-ates/Oto-Hesap/actions/workflows/ci.yml)

**Verinizi anlayın. İşinizi yönetin.** KOBİ'ler için yapay zekâ destekli finans + stok platformu: gelir-gider panosu, Türkçe soruyla veriye erişen finans asistanı, insan onaylı otonom tedarik ajanı. Medeniyet Teknopark TeknoKampüs 2026 projesi.

| Yetenek | Ne yapar |
|---------|----------|
| Akıllı finans asistanı | "En çok kazancım hangi üründen?" → şema temelli Text-to-SQL → gerçek veriden yanıt; SQL görünür, yalnız okur |
| Görsel analitik | KPI kartları, aylık gelir-gider, gider dağılımı, dönem filtresi, CSV |
| Otonom tedarik ajanı | Kritik stok → sipariş taslağı → onay → tedarikçiye Telegram mesajı |
| Web arayüzü | Kurulumsuz, her cihazdan; 5 ekran |

## Çalıştırma
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh                 # hook + .env + bağımlılıklar
psql "$DATABASE_URL" -f docs/schema.sql
python data/seed.py --reset        # sentetik 6 ay veri
cd apps/api && uv run uvicorn app.main:app --reload   # http://localhost:8000/docs
cd apps/web && bun dev                                 # http://localhost:3000
```

## Teknoloji
Next.js · Tailwind · Recharts · FastAPI · SQLAlchemy 2 · PostgreSQL (Neon) · Claude / Gemini (tek adaptör) · APScheduler · Telegram Bot API · GitHub Actions · Vercel + Render

## Ekip
Kutay Yıldırım · Muratcan Ateş · Yiğit Yuşa Kartal · Ömer Faruk Eskitürk

Ekip brifi: [docs/team/EKIP-BRIFI.md](docs/team/EKIP-BRIFI.md) · Ekip kuralları ve mimari: [AGENTS.md](AGENTS.md) · Demo: [docs/demo-senaryosu.md](docs/demo-senaryosu.md) · Kararlar: [docs/DECISIONS.md](docs/DECISIONS.md)
