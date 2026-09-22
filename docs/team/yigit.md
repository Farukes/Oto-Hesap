# Yiğit Yuşa Kartal — Görev ve Sorumluluk Alanı

**Rol:** Veri Mühendisi ve İş Zekası (BI/Analitik)

## 1 · Sorumluluk Alanları
- **Sentetik Veri Üretimi & Simülasyon:** `data/seed.py`
  - Deterministik tohumlama (`seed=42`) ile gerçekçi KOBİ finansal verisi (teknoloji aksesuarları mağazası)
  - 20 ürün, 5 kategori, 5 tedarikçi, 600+ satış kaydı, 250+ gider kaydı
  - Kontrollü kâr lideri senaryosu ve tam 2 adet kritik stok ürünü simülasyonu
- **Analitik & Raporlama Servisleri:**
  - Kategori bazlı gider analizi (`routers/analytics.py`)
  - Ürün bazlı satış ve kâr katkısı hesaplamaları
  - CSV formatında veri dışa aktarımı (`routers/export.py`)
- **Kural Tabanlı İçgörüler (Insights):** `apps/api/app/services/insights.py`
  - Anomali tespiti ve işletme için otomatik finansal uyarı kartları
