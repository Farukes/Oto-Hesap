# Konuşmacı notları — `OtoHesap.pptx` (16 Eyl 2026 finali)

> Hedef süre: **8–10 dakika** (slaytlar ~5 dk + canlı demo ~4 dk + tampon).
> Aynı metin slaytların "Konuşmacı Notları" alanına da gömülüdür (PowerPoint'te Görünüm → Not Sayfası).
> Kurallar: **"Fark" net kâr değildir**, "en kârlı ürün" tahmini brüt katkıdır, veri **sentetik demo verisidir**, "Gönderildi" **teslim alındı değildir**. Rakam kaynağı: `docs/research/KONTROL-2026-09-13.md`.
>
> Sunumdan 10 dk önce: `make warmup` · `/api/health` yeşil · Telegram sohbeti telefonda açık, ses açık · tarayıcıda 5 sekme hazır.

---

## S1 · Kapak — "OtoHesap · Verinizi anlayın. İşinizi yönetin." (~35 sn)

> "Merhaba, biz OtoHesap ekibiyiz. KOBİ'ler için yapay zekâ destekli bir finans ve stok platformu geliştirdik. Sloganımız şu: **verinizi anlayın, işinizi yönetin.** Önce problemi, sonra çözümü anlatacağım; ardından ürünü canlı göstereceğiz."

**Cue:** İsimleri tek tek okuma; "dört kişilik ekibiz" de, geç.

---

## S2 · Problem — TÜİK 2024 (~60 sn)

> "Türkiye'de **3,928 milyon KOBİ** var. Bu işletmeler girişimlerin **%99,6'sı**, istihdamın **%68,5'i**, cironun **%44,1'i**. Ve bunların **%35,1'i toptan–perakende ticarette**; yani günlük işi doğrudan stokla dönen işletmeler."
>
> "Bu kadar büyük bir tabanda tablo şu: **Excel ile rapor kovalayan işletme, stok bitince geç fark ediyor.** Rapor menüsünde aranan bir soru, elde tutulan bir stok defteri ve gecikmiş bir tedarik siparişi — problem burada."

**Cue:** Rakamları tek tek okuma; 3,928'i ve %68,5'i vurgula, kalanı slayt göstersin. Kaynak satırını işaret et: "TÜİK, Küçük ve Orta Büyüklükteki Girişim İstatistikleri, 2024."

---

## S3 · Çözüm — dört yetenek (~50 sn)

> "OtoHesap dört yetenekten oluşuyor: **Türkçe soru soran bir finans asistanı**, **görsel analitik**, kritik stokta devreye giren **otonom tedarik ajanı** ve **kurulum gerektirmeyen bir web arayüzü**."
>
> "Sağdaki ekran gerçek uygulamadan alındı. Gelir, gider, **fark** ve kritik ürün sayısı her açılışta veriden hesaplanıyor. Not düşeyim: **fark, gelir eksi giderdir; net kâr değildir** — KDV, iade ve tahakkuk bu hesapta yok. Ekrandaki veri de **sentetik demo verisi**."

**Cue:** "Fark ≠ net kâr" cümlesini atlama; jüri bunu sorar, sen önden söylersen puan.

---

## S4 · Nasıl çalışır — güvenlik mimarisi (~70 sn)

> "İki akış var. Birincisi soru–yanıt: kullanıcı **Türkçe soruyor**, model **yalnızca SQL yazıyor**. O SQL sqlglot ile ayrıştırılıp tablo ve fonksiyon **beyaz listesinden** geçiyor, **salt-okur** bir veritabanı rolüyle çalışıyor; süre ve satır sınırı var. **Rakam modelden değil veritabanından geliyor** ve kullanılan sorgu ekranda görünüyor."
>
> "İkincisi aksiyon akışı: stok kritik seviyeye inince **kural motoru** — LLM değil — sipariş taslağı hazırlıyor. Sonra **insan onayı**. Ancak onaydan sonra tedarikçiye Telegram mesajı gidiyor."
>
> "Tek cümlede: **AI'a veritabanının anahtarını vermiyoruz.** Ajan hiçbir mesajı onaysız göndermiyor; asistan veritabanına yalnız okuyor."

**Cue:** Yeşil "İNSAN ONAYI" kutusunu parmakla göster. Bu slayt sunumun teknik güven ânı; acele etme.

---

## S5 · Canlı demo — "Sor. Gör. Onayla." (~10 sn slayt + ~3,5 dk canlı)

> "Ekranlar burada duruyor ama asıl göstereceğimiz canlı ürün."

**Cue: Slaytı 10 saniyede geç, canlıya gir.** Demo sırası (`docs/demo-senaryosu.md`):

1. **Genel Bakış** — "Gelir, gider, fark, kritik stok; altı aylık akış. Sistem kendisi uyarıyor: iki ürün kritik stokta."
2. **Kayıtlar → gider ekle** (reklam, 4.500) → Genel Bakış'a dön — "Pano anında güncellendi."
3. **Asistan** → çip **"En çok kazancım hangi üründen?"** → yanıt → **Sorguyu gör** (3 sn aç, kapat) — "Rakam veritabanından, sorgu görünür. Burada 'kâr' mevcut birim maliyetle **tahmini brüt katkıdır**."
4. **Asistan** → çip **"Bu ay toplam giderim ne kadar?"** — "Az önce girdiğimiz gider yanıta dahil."
5. **Stok** — "İki satır kırmızı."
6. **Tedarik** → **Şimdi kontrol et** → taslak → **Onayla** → 📱 telefonu jüriye çevir — "Mesaj tedarikçinin telefonuna düştü. Not: **'Gönderildi' mesaj gönderimidir, teslim alındı değildir**; stok bu adımda artmaz."

**Yedekler:** Wi-Fi yok → hotspot · LLM yok → asistan **önbellekten** yanıtlar (çipler çalışır) · Telegram yok → "Gönderildi (simülasyon)" rozeti + 90 sn video · her şey düşerse USB'deki video.
**Kesin kural:** Yalnız çiplerden soru; onay tuşuna bir kez bas.

---

## S6 · Teknoloji ve yöntem (~50 sn)

> "Web tarafı **Next.js 16**, API **FastAPI**, veritabanı **Neon üstünde PostgreSQL**. Asistanın ürettiği SQL **sqlglot** ile denetleniyor, stok kontrolü **APScheduler** ile dönüyor, bildirim **Telegram Bot API** üzerinden gidiyor. **GitHub Actions** her PR'da çalışıyor; şu an **185 test** yeşil."
>
> "Yöntem tarafında altını çizmek istediğimiz şey şu: **AI kod yazdı değil; AI hızlandırdı. Sınırları CI, eval ve dosya sahipliği koydu.** 15 soruluk Türkçe bir eval setimiz var; her dosyanın tek sahibi var; CI yeşil olmadan hiçbir şey main'e girmiyor."

**Cue:** Render Free'de zamanlayıcının uyuduğunu saklama — sorulursa: "'Şimdi kontrol et' düğmesi zamanlayıcıyla aynı fonksiyonu çağırır."

---

## S7 · Ekip ve iş bölümü (~35 sn)

> "Dört kişiyiz ve işi **dosya sahipliğiyle** böldük: **Kutay** web arayüzünü, **Muratcan** mimariyi, API'yi ve Text-to-SQL katmanını, **Ömer** tedarik ajanını, bildirimi ve demo akışını, **Yiğit** veriyi, analitiği ve sunumu üstlendi."
>
> "Çakışmayı böyle engelledik: küçük PR'lar, 15 dakikada gözden geçirme, yeşil CI. Ürünü **bir günde uçtan uca** böyle çıkardık."

---

## S8 · Yol haritası + kapanış (~45 sn)

> "Sırada ne var: **Trendyol Product V2** ile salt-okur sipariş importu; **e-belge entegratörü**; **lisanslı açık bankacılık** bağlantısı; `tenant_id` ve RLS ile **çok kiracılı SaaS**; ardından **Azure üzerinde kurumsal referans mimari**."
>
> "Kapatırken üç ilke: **LLM sorguyu yazar, rakamı veritabanı verir, siparişi insan onaylar.** Bizim cümlemiz şu: **Karmaşıklık arkada, karar önünde.** Teşekkürler."

**Cue:** Trendyol temsilcisi salondaysa: "Pazaryeri sipariş verisinin yalnız raporlanmasını değil, küçük işletmenin stok ve nakit kararına dönüşmesini hedefliyoruz."
**Cue:** Microsoft çözüm ortağı salondaysa: "Bugün hız için yönetilen servisler; sonraki adımda Azure'da tenant izolasyonu, yönetişimli AI ve kurumsal kimlik."

---

## 3 dakikaya sıkışırsa hangi slaytlar atlanır

**Atla:** **S6 (Teknoloji ve yöntem)** ve **S7 (Ekip)** — tek cümleyle özetlenir: "Next.js + FastAPI + PostgreSQL, 185 test ve yeşil CI ile; dört kişi, bir gün."
**Kısalt:** S2'de yalnız **3,928 milyon KOBİ** ve **%68,5 istihdam** söylenir; S3 slaytta gösterilir, sayılmaz; S8'de yalnız **Trendyol V2** ve **çok kiracılı SaaS** söylenir.
**Asla atlama:** **S1 → S2 (tek rakam) → S4 (güvenlik akışı) → S5 (canlı demo) → S8 (kapanış cümlesi).**
Ayrıntılı 3 dk akışı: `docs/sunum/3-dakika-akis.md`.

---

## Jüri sorularına kısa cevaplar (cepte dursun)

| Soru | Tek cümle |
|---|---|
| Bu zaten Paraşüt değil mi? | "Paraşüt gibi ürünler e-belge, banka ve stok katmanında güçlü; biz o verinin üstünde doğal dille soru ve **insan onaylı aksiyon** katmanıyız." |
| LLM yanlış SQL üretirse? | "Sorgu ayrıştırılıp beyaz listeden geçiyor, salt-okur rolle çalışıyor, süre ve satır sınırı var, SQL kullanıcıya görünüyor; hata olursa bir kez deniyor, sonra 'yanıtlayamadım' diyor — uydurmuyor." |
| AI kendi başına sipariş verir mi? | "Hayır: taslak → onay → gönderim; onaysız hiçbir dış mesaj yok." |
| KVKK? | "Demo tamamen sentetik veri. Üretimde veri minimizasyonu ve KVKK m.9 yurt dışı aktarım mekanizmaları sağlayıcı bazında uygulanır." |
| Neden Telegram, WhatsApp değil? | "Bir günlük doğrulamada Telegram Bot API çok hızlı; bildirim adaptörü arkasında kanal değişebilir." |
| İnternet giderse? | "Pano mevcut veriyi göstermeye devam eder; asistan önbellekten yanıtlar; dış çağrılar kontrollü hata verir." |
| Bunu gerçekten bir günde mi yaptınız? | "Kapsamı bilinçli küçülttük, yönetilen servisleri kullandık, dosya sahipliğini böldük, AI'ı paralel hızlandırıcı olarak kullandık." |
| Neden Azure'da değil? | "Bugün hız için Vercel/Render/Neon; ürünleşme yolunda Container Apps, PostgreSQL ve kurumsal kimlik referans mimarisi var." |
| Rakip iki ayda kopyalamaz mı? | "Tek başına sohbet kutusu savunulabilir değil; savunma hattı entegrasyonlar, eval setleri, onay/iz kaydı güvenliği ve biriken operasyon bilgisi." |
| Fark = kâr mı? | "Hayır. Fark, gelir eksi giderdir; KDV, iade ve tahakkuk içermez." |
