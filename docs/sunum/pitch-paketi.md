# Pitch paketi (kaynak: docs/research/SONUC-chatgpt-2026-09-13.md, 13 Eyl 2026 ChatGPT deep research)

> Rakamlar rapordaki güven etiketiyle gelir; **A** olmayan hiçbir sayı slayta girmez. Sahibi: Ömer (metin) + Yiğit (slayt). Kontrol notları: docs/research/KONTROL-2026-09-13.md

## Jüri sunumu ve pitch paketi

Sunumun merkezine teknoloji isimleri değil **kontrollü otomasyon** konmalı. KOBİ pazarının ekonomik ağırlığı TÜİK ile açılır; demo “soru sor → gör → onayla → mesajı telefonda gör” akışıyla ispatlanır; roadmap Trendyol ve Azure ile ölçeklenir. citeturn15search7turn20search1turn21search12

| Slayt | Üç ana nokta | Konuşmacı notu |
|---|---|---|
| **Kapak** | OtoHesap; “Every second counts”; AI destekli finans + stok | “KOBİ sahibinin işi dashboard okumak değil, karar vermek.” |
| **Problem** | 3,928 milyon KOBİ; %68,5 istihdam; %44,1 ciro. citeturn15search7 | “Bu kadar büyük bir ekonomik tabanda birkaç dakika bile tekrarlandığında ciddi operasyon yüküne dönüşüyor.” |
| **Çözüm** | Gelir-gider; stok; doğal dil + kontrollü aksiyon | “Muhasebe yazılımını değiştirmiyoruz; veriye erişim ve aksiyon katmanını sadeleştiriyoruz.” |
| **Dört yetenek** | Dashboard; AI finans asistanı; stok agentı | Dördüncü nokta olarak CRUD/CSV görselde gösterilebilir; konuşmada üç ana değere odaklanın. fileciteturn0file0 |
| **Nasıl çalışır** | Türkçe → SQL; salt-okur DB; agent → insan onayı | “AI’a veritabanının anahtarını vermiyoruz.” |
| **Canlı demo** | Soru sor; kritik stoğu yakala; Telegram mesajını telefonda göster | En güçlü an. Slaytı 10 saniyede geçip canlıya girin. |
| **Teknoloji ve yöntem** | Next/FastAPI/Postgres; guardrails; 4 kişi paralel AI-assisted development | “AI kod yazdı” değil, “AI hızlandırdı; sınırları CI, eval ve ownership koydu.” |
| **Ekip** | Web; API/AI; agent/integrasyon; data/analytics/pitch | Dosya sahipliği ve 1 günlük delivery vurgusu. |
| **Yol haritası + kapanış** | Trendyol V2; e-belge/açık bankacılık; Azure/Marketplace | Trendyol satıcı tabanı ve Microsoft ürünleşme yolu ile kapanın. citeturn20search1turn23search0turn23search13 |

**“İşletmeler neden kullanmalı?” için üç cümle:**

> “İşletme sahibi rapor menüsü aramak yerine kendi dilinde sorusunu soruyor. Sistem cevabı kara kutu olarak vermiyor; kullandığı SQL’i ve verinin zamanını gösteriyor. Bir aksiyon gerektiğinde de işletme sahibinin yerine kontrolsüz işlem yapmak yerine taslağı hazırlayıp onay bekliyor.”

Bu ifade projenin güncel güvenlik ve UX mimarisiyle birebir uyumludur. fileciteturn0file0

**60 saniyelik asansör konuşması:**

> Türkiye’de yaklaşık **3,9 milyon KOBİ**, istihdamın %68,5’ini ve cironun %44,1’ini oluşturuyor. citeturn15search7 OtoHesap’ı bu işletmelerin finans ve stok verisini daha kolay kullanabilmesi için geliştirdik. İşletme sahibi “Bu ay en çok hangi üründen kazandım?” diye Türkçe soruyor; sistem kontrollü bir SQL sorgusu oluşturuyor, yalnızca okuma yetkisiyle veritabanına gidiyor ve hem sonucu hem SQL’i gösteriyor. Stok kritik seviyeye indiğinde ise kendi başına sipariş vermiyor; sipariş taslağını hazırlıyor, kullanıcıdan onay alıyor ve ardından tedarikçiye mesaj gönderiyor. Bugün bunu dört kişilik ekiple çalışan bir prototip olarak gösteriyoruz. Yarın Trendyol, e-belge ve açık bankacılık bağlantılarıyla KOBİ’nin **finansal operasyon karar katmanı** haline getirmek istiyoruz.

**Beş slogan:**

| Slogan | Kullanım |
|---|---|
| **Sor. Gör. Onayla. OtoHesap halletsin.** | En güçlü demo sloganı |
| **Every second counts. OtoHesap da.** | Motto bağlantısı |
| **Karmaşıklık arkada, karar önünde.** | Legerdemain |
| **Rapor arama. Sor.** | AI asistanı |
| **AI önerir. Siz onaylarsınız.** | Güvenlik/HITL |

**Beş yıl vizyonu:**

> **“OtoHesap’ı Türkiye’deki küçük işletmelerin pazaryeri, banka, e-belge ve tedarik verilerini tek karar katmanında buluşturan, insan kontrollü AI operasyon platformuna dönüştürmek.”**

Açık bankacılığın 2026’da 16,4 milyon kullanıcı ve 53 katılımcıya ulaşmış olması bu vizyonun bankacılık ayağının olgunlaşan bir altyapıya dayandığını gösteriyor. citeturn23search0

**Muhtemel jüri soruları:**

| Soru | Kısa cevap |
|---|---|
| **Bu zaten Paraşüt değil mi?** | “Paraşüt gibi ürünler e-belge, banka, stok ve e-ticarette çok güçlü. citeturn22search0 Biz onların yerine geçmeyi değil, veriyi doğal dille erişilebilir ve aksiyona hazır hale getiren karar katmanını hedefliyoruz.” |
| **LLM yanlış SQL üretirse?** | “SQL önce parse ve whitelist kontrolünden geçiyor, DB kullanıcısı salt-okur, sorgu süresi sınırlandırılıyor ve SQL kullanıcıya gösteriliyor.” |
| **AI kendi başına tedarikçiye sipariş veriyor mu?** | “Hayır. Draft → approved → sent state’i var; dış iletişim ancak insan onayından sonra.” fileciteturn0file0 |
| **KVKK ne olacak?** | “Demo tamamen sentetik. Üretimde veri minimizasyonu ve KVKK m.9 yurt dışı aktarım mekanizmalarını sağlayıcı bazında uygulamamız gerekiyor.” citeturn19search2turn19search3 |
| **Neden Telegram, neden WhatsApp değil?** | “Bir günlük doğrulamada Telegram’ın HTTP Bot API’si çok hızlı. WhatsApp sandbox/onboarding ve template kısıtları ek operasyon getiriyor. citeturn13search0turn13search1 Production’da notification adapter ile kanal değişebilir.” |
| **İnternet giderse?** | “Dashboard mevcut veriyi göstermeye devam eder; demo için hotspot ve kayıtlı fallback bulunur. External AI/Telegram çağrıları kontrollü hata verir.” |
| **Rakip bunu iki ayda kopyalamaz mı?** | “Tek başına chat kutusu savunulabilir değil. Savunma hattı entegrasyonlar, yerel iş akışları, eval setleri, approval/audit güvenliği ve zamanla biriken operasyon bilgisidir.” |
| **Neden Azure’da değil?** | “Bugün hız için Vercel/Render/Neon. Ürünleşme yolunda Container Apps, PostgreSQL, Foundry ve Entra referans mimarisi var. Azure for Students da Azure OpenAI erişimini güncel programında listeliyor.” citeturn21search2 |
| **Trendyol entegrasyonunuz hazır mı?** | “Bugün roadmap. Resmî sipariş API’sini doğruladık; ayrıca Product V1 iki gün sonra kapanıyor, bu yüzden doğrudan V2 ile ilerleyeceğiz.” citeturn20search6turn20search10 |
| **Bunu gerçekten dört kişi bir günde mi yaptınız?** | “Kapsamı bilinçli küçülttük, managed servisleri kullandık, dosya sahipliğini böldük ve AI araçlarını paralel hızlandırıcı olarak kullandık. Ürünleşme özelliklerini demo gününe sokmadık.” fileciteturn0file0turn0file2 |

**Demoya girerken:**

> “Şimdi size bir dashboard göstermek yerine, işletme sahibinin üç dakikada yaptığı bir işi yaklaşık otuz saniyeye nasıl indirdiğimizi göstermek istiyorum.”

Buradaki “üç dakika” ölçülmüş pazar verisi olmadığı için sahnede literal zaman iddiası yapmak yerine daha güvenlisi:

> **“Şimdi size menüler arasında dolaşmak yerine, tek soruyla veriye ulaşıp tek onayla aksiyona geçtiğimiz akışı göstermek istiyorum.”**

**Demodan çıkarken:**

> **“Buradaki kritik nokta AI’ın aksiyon alabilmesi değil; doğru sınırlar içinde ne zaman durup insana sorması gerektiğini bilmesi.”**

**Trendyol temsilcisine kapanış:**

> **“Trendyol’un yaklaşık 250 bin satıcılık ekosisteminde sipariş verisinin yalnız raporlanmasını değil, küçük işletmenin stok ve nakit kararına dönüşmesini hedefliyoruz.”** Satıcı sayısı resmî Trendyol kaynaklıdır; KOBİ oranı ayrıca doğrulanmamıştır. citeturn20search1turn20search3

**Microsoft çözüm ortağı temsilcisine kapanış:**

> **“Bugün use case’i hızlı managed servislerle doğruladık; bir sonraki aşamada bunu Azure üzerinde tenant isolation, govern edilmiş AI, enterprise identity ve Marketplace’e çıkabilecek bir referans mimariye dönüştürmek istiyoruz.”**

Bu yol Microsoft’un ISV Success ve co-sell süreçleriyle yapısal olarak uyumludur. citeturn23search13turn21search12

