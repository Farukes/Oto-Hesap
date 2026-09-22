<div align="center">

<img src="docs/img/logo.png" alt="OtoHesap Logo" width="160" />

# OtoHesap

**KOBİ'ler için Yapay Zekâ Destekli Finans, Analitik ve Otonom Stok Yönetim Platformu**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)

</div>

---

## 📌 Proje Hakkında

**OtoHesap**, küçük ve orta ölçekli işletmelerin (KOBİ) finansal gelir-gider takibini, envanter kontrolünü ve tedarik süreçlerini tek bir çatı altında birleştiren yeni nesil bir karar ve operasyon platformudur.

Geleneksel karmaşık ERP sistemleri ile yetersiz kalan elektronik tablolar arasında sıkışan işletmeler için doğal dil arayüzü ve insan kontrollü otonom iş akışları sunar.

### 🌟 Temel Yetenekler

| Yetenek | Açıklama |
|---|---|
| 💬 **Akıllı Finans Asistanı (Text-to-SQL)** | Türkçe doğal dilde soru sorun (*"En çok kâr getiren ürünüm hangisi?"*); sistem soruyu AST kontrollü güvenli SQL'e dönüştürür ve gerçek veriden anında yanıtlar. Üretilen SQL sorgusu şeffafça görüntülenebilir. |
| 📊 **Görsel Analitik & Raporlama** | Gerçek zamanlı finansal KPI kartları (Gelir, Gider, Fark, Kritik Stok), aylık gelir-gider trendi, harcama kategorileri pasta grafiği, dönem filtreleri ve CSV dışa aktarımı. |
| 🤖 **Otonom Tedarik Ajanı (Human-in-the-Loop)** | Kritik stok seviyesine düşen ürünleri otomatik tespit eder, sipariş taslağı hazırlar ve **kullanıcı onayıyla** tedarikçiye doğrudan Telegram üzerinden mesaj iletir. |
| 💡 **Kural Tabanlı Finansal İçgörüler** | Gelir-gider dengesini ve stok devir hızını sürekli denetleyerek işletme sahibine aksiyon alınabilir uyarı ve içgörü kartları sunar. |

---

## 🖼️ Ekran Görüntüleri

### Genel Bakış & Finansal Gösterge Paneli
![Genel Bakış](docs/img/genel-bakis.png)

<br/>

| Akıllı Finans Asistanı (Text-to-SQL) | Otonom Tedarik Ajanı & Onay Paneli |
|:---:|:---:|
| ![Asistan](docs/img/asistan.png) | ![Tedarik](docs/img/tedarik.png) |

---

## 🏗️ Sistem Mimarisi

```
[ Web Tarayıcısı ]
       │
       ▼ (HTTPS / REST)
[ Next.js 16 Web Uygulaması ] (apps/web)
       │
       ▼ NEXT_PUBLIC_API_URL
[ FastAPI Backend Servisi ] (apps/api)
       ├── routers/    summary · sales · expenses · products · analytics · assistant · orders · agent
       ├── services/   text2sql (Doğal Dil → AST Doğrulama → Salt-Okur Sorgu → Özet)
       │               agent (Kritik Stok Eşik Kontrolü → Taslak Sipariş)
       │               notify (Telegram Bot API Entegrasyonu)
       │               llm (Anthropic / Gemini / Groq / Fake adaptör katmanı)
       │               insights (Kural tabanlı anomali ve içgörü motoru)
       └── scheduler/  APScheduler periyodik arka plan kontrolü
       │
       ▼
[ PostgreSQL 16 ] (Uygulama Rolü + otohesap_ro Salt-Okur Rolü)
```

---

## 🛡️ Güvenlik ve Kontrollü Otonomi İlkeleri

1. **Defense-in-Depth (Text-to-SQL Güvenliği):**
   - **Salt-Okur Rol:** Asistan sorguları veritabanında yalnızca `SELECT` yetkisine sahip `otohesap_ro` rolüyle yürütülür; veri değiştirme veya silme teknik olarak imkansızdır.
   - **AST Doğrulaması:** Üretilen SQL sorguları `sqlglot` ile soyut sözdizim ağacına ayrıştırılır. Yalnızca izin verilen tablolar ve güvenli matematik/tarih fonksiyonları çalıştırılabilir.
   - **Kısıtlamalar:** Çoklu sorgular (`;`), yorum satırları (`--`), DDL/DML ifadeleri reddedilir. Sorgulara otomatik `LIMIT 200` eklenir ve 5 saniye zaman aşımı uygulanır.
2. **Human-in-the-Loop Tedarik:**
   - Tedarik ajanı stok eşiğini aştığında yalnızca **taslak (`draft`)** oluşturur.
   - Yetkili kullanıcı arayüz üzerinden açıkça "Onayla" butonuna basmadıkça dış dünyaya (Telegram) hiçbir mesaj iletilmez.

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.12+ ve [`uv`](https://docs.astral.sh/uv/)
- Node.js 20+ veya [`bun`](https://bun.sh/)
- PostgreSQL 16 (Yerel veya Neon / Supabase)

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/<kullanici_adiniz>/Oto-Hesap.git
cd Oto-Hesap
```

### 2. Ortam Değişkenlerini Ayarlayın
`.env.example` dosyasını `.env` olarak kopyalayın ve bağlantı bilgilerinizi girin:
```bash
cp .env.example .env
```
Gerekli alanlar:
- `DATABASE_URL`: Ana veritabanı bağlantı adresi
- `DATABASE_URL_RO`: Salt-okur veritabanı rolü adresi
- `LLM_PROVIDER`: `anthropic` | `gemini` | `groq` | `fake` (test/demo için)
- `TELEGRAM_BOT_TOKEN` & `TELEGRAM_DEFAULT_CHAT_ID`: Tedarik bildirimleri için (isteğe bağlı)

### 3. Veritabanını Hazırlayın ve Sentetik Veriyi Yükleyin
```bash
# Şemayı oluşturun
psql "$DATABASE_URL" -f docs/schema.sql

# Sentetik 6 aylık KOBİ verisini yükleyin (seed=42)
make seed
```

### 4. Servisleri Başlatın

**Terminal 1 (Backend API):**
```bash
make api
# http://localhost:8000/docs adresinde Swagger arayüzü açılır
```

**Terminal 2 (Frontend Web):**
```bash
make web
# http://localhost:3000 adresinde gösterge paneli açılır
```

---

## 📋 Kullanışlı Komutlar (`Makefile`)

| Komut | Açıklama |
|---|---|
| `make api` | FastAPI geliştirme sunucusunu `:8000` portunda başlatır |
| `make web` | Next.js arayüzünü `:3000` portunda başlatır |
| `make seed` | Veritabanını temizler ve deterministik sentetik veriyi yükler |
| `make test` | API test paketini çalıştırır |
| `make lint` | Python (`ruff`) ve Web (`eslint`) kod denetimlerini çalıştırır |
| `make warmup` | Sunum/demo öncesi API ve veritabanı bağlantılarını ısıtır |

---

## 👥 Ekip

- **Kutay Yıldırım** — Frontend & UI/UX Mimarisi
- **Muratcan Ateş** — Backend Çekirdek, Veritabanı & Güvenlik
- **Ömer Faruk Eskitürk** — Otonom Tedarik Ajanı, Sipariş Yönetimi & Telegram Entegrasyonu
- **Yiğit Yuşa Kartal** — Veri Modelleme, Sentetik Simülasyon & İş Zekası (BI)
