# Muratcan Ateş — Görev ve Sorumluluk Alanı

**Rol:** Backend Çekirdek Mimarı, Veritabanı ve Güvenlik Altyapısı

## 1 · Sorumluluk Alanları
- **Backend Çekirdek:** `apps/api/app/`
  - FastAPI çatısı, SQLAlchemy 2 ve Pydantic v2 veri modelleri
  - API yönlendiricileri (`routers/summary.py`, `sales.py`, `expenses.py`, `products.py`, `assistant.py`)
- **Text-to-SQL Servisi & Güvenlik:** `apps/api/app/services/text2sql.py`
  - SQL üretimi: Doğal dil şeması + az sayıda örnek (few-shot) → LLM → `SQLPlan` JSON çıktısı
  - Güvenlik & AST Analizi: `sqlglot` ile AST ayrıştırma, tablo ve görünüm beyaz listesi, izin verilen SQL fonksiyonları listesi
  - Salt-okur rol güvencesi (`otohesap_ro`), `statement_timeout` ve `LIMIT` kısıtlamaları
- **LLM Adaptör Katmanı:** `apps/api/app/services/llm.py`
  - Çoklu sağlayıcı desteği: Anthropic, Gemini, Groq ve testler için Fake adaptör
- **Veritabanı Şeması & Dağıtım:** `docs/schema.sql`, Dockerfile, Render ve CI/CD iş akışları (`.github/workflows/ci.yml`)
