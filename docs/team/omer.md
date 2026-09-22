# Ömer Faruk Eskitürk — Görev ve Sorumluluk Alanı

**Rol:** Otonom Tedarik Ajanı, Sipariş Yönetimi ve Telegram Entegrasyonu

## 1 · Sorumluluk Alanları
- **Otonom Tedarik Ajanı:** `apps/api/app/services/agent.py`
  - Kritik stok seviyesi kontrolü (`stock_qty <= reorder_point`)
  - Tedarik miktarı belirleme (`target_stock - stock_qty`)
  - DB düzeyinde mükerrer sipariş koruması (tek açık taslak kuralı)
- **Sipariş Yönetimi & Onay Akışı:** `apps/api/app/routers/orders.py`
  - Sipariş listeleme (`GET /api/orders`)
  - İnsan onayı ile onaylama (`POST /api/orders/{id}/approve`)
  - Sipariş reddetme (`POST /api/orders/{id}/reject`)
- **Bildirim & Entegrasyon Servisi:** `apps/api/app/services/notify.py`
  - Telegram Bot API üzerinden tedarikçiye otomatik mesaj iletimi
  - Test ve simülasyon modları (`NOTIFY_DRY_RUN`)
- **Zamanlayıcı Servisi:** `apps/api/app/services/scheduler.py`
  - APScheduler entegrasyonu ile periyodik stok kontrolü
- **Soru Bankası & Doğrulama:** `apps/api/app/data/soru_bankasi.json` ve tedarik/sipariş senaryoları

## 2 · Tedarik Ajanı Mimarisi
1. **Eşik Kontrolü:** Kural tabanlıdır (deterministik, LLM'siz). `stock_qty <= reorder_point` şartı sağlandığında tetiklenir.
2. **Taslak Oluşturma:** Sipariş taslak (`draft`) statüsünde veritabanına kaydedilir.
3. **İnsan Onayı (Human-in-the-Loop):** Ajan asla izinsiz dış dünyaya mesaj atmaz. Kullanıcı arayüzden "Onayla" butonuna basana kadar mesaj iletilmez.
4. **İletim:** Telegram Bot API aracılığıyla ilgili tedarikçinin iletişim adresine iletilir ve statü `sent` olarak güncellenir.
