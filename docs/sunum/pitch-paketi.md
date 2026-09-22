# OtoHesap — Sunum ve Pitch Paketi

Bu doküman, jüri sunumu, ürün konumlandırması ve soru-cevap seansları için hazırlanmış konuşmacı notlarını içerir.

## Jüri Sunumu ve Pitch Rehberi

Sunumun merkezinde karmaşık teknoloji jargonu yerine **kontrollü otomasyon (human-in-the-loop)** yer alır. KOBİ pazarının ekonomik büyüklüğü TÜİK verileriyle ortaya konur; sistem *"soru sor → sorguyu gör → onayla → mesajı telefonda gör"* akışıyla somutlaştırılır; yol haritası ise pazaryeri ve bulut entegrasyonlarıyla ölçeklenir.

| Slayt | Üç Ana Nokta | Konuşmacı Notu |
|---|---|---|
| **Kapak** | OtoHesap; Yapay zekâ destekli finans + stok yönetimi | *"KOBİ sahibinin işi dashboard okumak değil, doğru ve hızlı karar vermektir."* |
| **Problem** | 3,928 milyon KOBİ; %68,5 istihdam; %44,1 ciro (TÜİK 2024) | *"Bu devasa ekonomik tabanda tekrarlanan operasyonel yükler ciddi bir verimsizlik yaratıyor."* |
| **Çözüm** | Gelir-gider panosu; kritik stok; doğal dil + kontrollü aksiyon | *"Mevcut ön muhasebe yazılımlarını değiştirmiyoruz; veriye erişim ve aksiyon katmanını sadeleştiriyoruz."* |
| **Temel Yetenekler** | Görsel analitik panoları; Text-to-SQL asistanı; otonom tedarik | Üç ana değere odaklanarak karmaşık iş süreçlerini arka planda çözüyoruz. |
| **Nasıl Çalışır?** | Türkçe soru → SQL; salt-okur DB; ajan → insan onayı | *"Yapay zekâya doğrudan veritabanının yazma anahtarını veya harcama yetkisini vermiyoruz."* |
| **Canlı Demo** | Soru sor; kritik stoğu yakala; Telegram mesajını telefonda göster | En somut an. Hızlıca canlı uygulamaya geçiş yapılır. |
| **Mimari & Güvenlik** | Next.js / FastAPI / PostgreSQL; AST doğrulaması | Güvenlik katmanları ve insan onayı mimarinin merkezindedir. |
| **Ekip** | Frontend, Backend/Mimari, Ajan/Entegrasyon, Veri/Analitik | Ekibin modüler dosya sahipliği ve teslim hızı. |
| **Yol Haritası** | Pazaryeri entegrasyonları (Trendyol V2), e-belge, çok kiracılı SaaS | Pazaryeri satıcı tabanı ve bulut ölçeklenmesi ile kapanış. |

---

## Değer Önerisi Cümleleri

> *"İşletme sahibi rapor menüleri arasında kaybolmak yerine kendi dilinde sorusunu soruyor. Sistem cevabı kara kutu olarak üretmiyor; çalıştırdığı SQL sorgusunu ve verinin zaman damgasını şeffafça gösteriyor. Bir aksiyon gerektiğinde de işletme sahibinin yerine kontrolsüz işlem yapmak yerine taslağı hazırlayıp onay bekliyor."*

### 60 Saniyelik Asansör Konuşması (Elevator Pitch)
> "Türkiye'de yaklaşık **3,9 milyon KOBİ**, istihdamın %68,5'ini ve cironun %44,1'ini oluşturuyor. OtoHesap'ı bu işletmelerin finans ve stok verisini en yalın biçimde yönetebilmeleri için geliştirdik. İşletme sahibi *'Bu ay en çok hangi üründen kazandım?'* diye Türkçe sorduğunda; sistem AST kontrollü güvenli bir SQL sorgusu oluşturuyor, yalnızca okuma yetkisiyle veritabanına gidiyor ve sonucu şeffafça ekrana getiriyor. Stok kritik seviyeye indiğinde ise sistem tek başına sipariş vermiyor; taslağı hazırlıyor, kullanıcı onayını alıyor ve tedarikçiye doğrudan Telegram üzerinden bildiriyor."

---

## Olası Jüri Soruları ve Yanıtları

| Soru | Yanıt |
|---|---|
| **Bu ürün Paraşüt veya Logo İşbaşı'nın rakibi mi?** | *"Paraşüt ve İşbaşı gibi ürünler e-belge, banka ve resmi defter tutma süreçlerinde güçlüdür. Biz onların yerini almayı değil, mevcut verinin üzerinde doğal dille soru sorulan ve insan onayıyla aksiyona geçen karar katmanı olmayı hedefliyoruz."* |
| **Model yanlış SQL üretirse ne olur?** | *"Üretilen SQL sorgusu çalıştırılmadan önce `sqlglot` ile AST analizinden ve katı bir tablo/fonksiyon beyaz listesinden geçer. Veritabanı kullanıcısı yalnızca salt-okur yetkisine sahiptir; sorgu süresi ve sonuç sayısı sınırlandırılmıştır."* |
| **Yapay zekâ kendi başına tedarikçiye sipariş verebilir mi?** | *"Hayır. Sipariş süreci `draft` (taslak) statüsünde başlar; yetkili kullanıcı arayüzden onaylamadıkça dış dünyaya hiçbir mesaj gönderilmez (Human-in-the-Loop)."* |
| **KVKK ve Veri Güvenliği nasıl sağlanıyor?** | *"Sistem mimarisinde veri minimizasyonu esastır. Model adaptör katmanı veritabanı şemasını kullanır, kullanıcı verisi doğrudan modellere aktarılmaz."* |
| **Neden bildirim için Telegram seçildi?** | *"Telegram Bot API webhook ve mesaj iletimi açısından son derece hızlı, güvenilir ve API kotası engeli bulunmayan bir altyapı sunuyor. Mimari gereği bildirim adaptörü WhatsApp Business API veya SMS ağ geçitlerine kolayca genişletilebilir."* |
| **İnternet kesilirse sistem nasıl davranır?** | *"Arayüz mevcut verileri önbellekten ve yerel durumdan göstermeye devam eder; harici servis çağrıları kullanıcıyı bilgilendiren kontrollü hata durumlarıyla ele alınır."* |
