# OtoHesap Web Arayüzü

OtoHesap platformunun kullanıcı arayüzü; Next.js 16 (App Router), React 19, Tailwind CSS v4 ve Recharts ile geliştirilmiştir.

## Özellikler

- **Genel Bakış (`/`):** Temel finansal KPI kartları (Gelir, Gider, Fark, Kritik Stok), aylık gelir-gider trendi, harcama dağılımı grafiği ve kural tabanlı öngörü kartları.
- **Kayıtlar (`/kayitlar`):** Gelir ve gider giriş-çıkış CRUD işlemleri, arama, sayfalama ve CSV dışa aktarımı.
- **Stok Yönetimi (`/stok`):** Ürün envanteri, yeniden sipariş eşiği ve kritik stok durumlarının anlık takibi.
- **Finans Asistanı (`/asistan`):** Doğal dilde soru sorarak veritabanından anlık yanıt alma; üretilen SQL sorgusunu ve veri kaynaklarını şeffafça görüntüleme.
- **Tedarik Yönetimi (`/tedarik`):** Kritik stoğa düşen ürünler için otomatik hazırlanan sipariş taslaklarını inceleme ve tek tıkla tedarikçiye bildirim gönderme.

## Geliştirme Ortamı

### Bağımlılıkları Yükleme
```bash
bun install
# veya
npm install
```

### Ortam Değişkenleri
`.env` dosyasında API adresi tanımlanabilir:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Geliştirme Sunucusunu Başlatma
```bash
bun dev
# veya
npm run dev
```
Uygulama `http://localhost:3000` adresinde çalışacaktır.

### Üretim Derlemesi
```bash
bun run build
bun run start
```
