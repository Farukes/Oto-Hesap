# Kutay Yıldırım — Görev ve Sorumluluk Alanı

**Rol:** Frontend Mimarı ve Kullanıcı Deneyimi (UI/UX)

## 1 · Sorumluluk Alanları
- **Web Uygulaması:** `apps/web/`
  - Next.js 16 (App Router), React 19, Tailwind CSS v4, Recharts
- **Arayüz Ekranları:**
  - Genel Bakış (`/`): KPI kartları, aylık gelir-gider çubuk grafiği, kategori dağılımı pasta grafiği, içgörü (insight) kartları
  - Kayıtlar (`/kayitlar`): Gelir ve gider giriş-çıkış CRUD işlemleri, filtreleme, CSV dışa aktarımı
  - Stok Yönetimi (`/stok`): Ürün kataloğu, stok miktarları, yeniden sipariş eşikleri ve kritik stok uyarıları
  - Akıllı Asistan (`/asistan`): Doğal dille finansal soru sorma, SQL sorgusunu ve veri kaynaklarını görüntüleme, hazır soru çipleri
  - Tedarik & Sipariş (`/tedarik`): Kritik stok analizi, sipariş taslağı inceleme ve insan onayı ile tedarikçiye Telegram bildirimi gönderme
- **Bileşenler & Tasarım:** `apps/web/components/`
  - Erişilebilirlik, duyarlı (responsive) tasarım, durum yönetimi ve API bağlantısı (`lib/api.ts`)
