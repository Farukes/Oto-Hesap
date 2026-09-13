# Kararlar (ADR-lite)

Her satır bir karar. Değiştirmek isteyen, yeni satır ekler; eskisini silmez. "Neden" boşsa karar sayılmaz.

| # | Tarih | Karar | Neden | Alternatif | Karar veren |
|---|-------|-------|-------|------------|-------------|
| D1 | 2026-09-13 | Web: Next.js + Tailwind + Recharts; API: FastAPI + SQLAlchemy 2; DB: PostgreSQL (Neon) | LLM/ajan ekosistemi Python; 4 kişi tek canlı DB; grafik kütüphanesi hazır | Express, SQLite | Ekip toplantısı (onay bekliyor) |
| D2 | 2026-09-13 | Asistan = şema temelli Text-to-SQL; DB'ye salt-okur rolle, yalnız tek SELECT, LIMIT 200, 5 sn | Güvenlik + jüriye "yalnız okur" mesajı | Vektör RAG | Murat |
| D3 | 2026-09-13 | Bildirim kanalı Telegram Bot API; WhatsApp Business yol haritası | Ücretsiz, 5 dk kurulum, sunumda telefonda görünür | E-posta | Ekip (onay bekliyor) |
| D4 | 2026-09-13 | Commit'lerde AI imzası / Co-Authored-By yok; commit-msg hook zorunlu | Katkılar yalnız ekip adına görünsün | — | Murat |
| D5 | 2026-09-13 | Depo `~/code/Oto-Hesap`; iCloud/Desktop/Documents dışında | iCloud senkronu node_modules ve .git'i bozar, dosya sızdırır | — | Murat |
| D6 | 2026-09-13 | Dal modeli: `main` korumalı + kişi başı 1 dal (`murat/api-core`, `kutay/web`, `omer/agent`, `yigit/data`); küçük PR, squash merge | 1 günde çakışmayı azaltmak | Trunk-based tek dal | Murat |
| D7 | 2026-09-13 | Geliştirme Günü = tek gün, 09:00–22:00; 19:00 özellik dondurma | "Every second counts" | — | Ekip (tarih toplantıda) |
| D8 | 2026-09-13 | UI iskeleti: shadcn/ui `dashboard-01` bloğu (sidebar + kart + tablo + grafik); Tremor gibi ikinci grafik/UI katmanı eklenmez | Sıfırdan tasarım saat yakar; Recharts zaten var | Sıfırdan Tailwind | Araştırma (SONUC-chatgpt) → Kutay onayı bekliyor |
| D9 | 2026-09-13 | Text-to-SQL kendi servisimiz (150–250 satır): LLM → JSON (`SQLPlan`) → Pydantic → sqlglot AST → tablo beyaz listesi → salt-okur rol → LIMIT/timeout. Vanna, LangChain SQL, LlamaIndex, LangGraph, Microsoft Agent Framework **bugün yok** | Dar şema + 15 soru; framework soyutlaması denetlenebilirliği düşürür | Vanna.ai | Murat |
| D10 | 2026-09-13 | LLM varsayılan `claude-haiku-4-5`; kalite modu `claude-sonnet-5` (2 $/10 $ per M token, Sonnet 4.6'dan ucuz; rapordaki "Sonnet 5 doğrulanamadı" notu yanlış, Claude API referansıyla doğrulandı). Gemini yalnız yedek ve yalnız sentetik veriyle: ücretsiz katman içeriği ürün geliştirmede kullanabiliyor | Maliyet + Türkçe/SQL kalitesi; KVKK | Sonnet 4.6, GPT-5 mini | Murat |
| D11 | 2026-09-13 | Trendyol yol haritası yalnız **Product V2** + salt-okur sipariş importu; V1'e tek satır kod yok (V1 15 Eyl 2026'da kapanıyor, developers.trendyol.com doğrulandı) | Ölü API'ye yatırım yapılmaz | — | Ekip |
| D12 | 2026-09-13 | KVKK: demo %100 sentetik veri. Üretimde m.9 yurt dışı aktarım mekanizması (standart sözleşme + 5 iş günü bildirim) + veri minimizasyonu; LLM'e satır değil **şema + toplam rakam** gider; loglarda kişisel veri yok | Yabancı LLM API = yurt dışına aktarım | Türkiye/AB bölgesi model | Ekip |
| D13 | 2026-09-13 | Ölçek yolu: tek şema + `tenant_id` + PostgreSQL RLS (schema-per-tenant değil); Azure hedefi Container Apps + PostgreSQL Flexible + Entra External ID + Key Vault; **Geliştirme Günü'nde taşınmaz** | 10k işletmeye kadar yönetilebilir; Microsoft partner hikâyesi | Schema-per-tenant | Murat |
| D14 | 2026-09-13 | Pitch kuralları: "rakiplerde AI yok" denmez; A etiketli olmayan sayı slayta girmez; konumlama = "ön muhasebenin yerine geçen değil, üstünde çalışan AI karar katmanı"; Paraşüt fiyat çıpası (940 TL + KDV/ay, parasut.com/on-muhasebe-fiyatlari, 13 Eyl doğrulandı; sayfa tarihi belirsiz) yalnız "pazar çıpası" olarak, bizim fiyat hipotezlerimiz "test edilecek" etiketiyle | Kolay çürütülür iddia jüride puan kaybettirir | — | Ekip |
| D15 | 2026-09-13 | Eval: 15 soru = 5 basit toplam + 3 tarih filtresi + 3 join + 2 boş/uç durum + 2 saldırgan istek; başarı ölçütü = beklenen rakam + izinli tablolar + yazma yok (SQL metni birebir eşleşmesi değil) | Model değişince regresyon ölçülsün | SQL string eşleşmesi | Ömer + Yiğit + Murat |
