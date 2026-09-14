# 🎤 Kutay — 3 dakikalık sunum akışı (telefonda açık tut)

**İşaretler:** 🟢 = **aynen oku/söyle** · 🔵 = **ekranda yap/göster** · ⏱ = süre · ⚠️ = yedek plan
Toplam 3:00 · hedef 2:50'de bitir · demo soruları **yalnız çiplerden**.

---

## 0 · Başlamadan (sen oturmadan önce, 10 dk) 🔵
- 🔵 `make demo` koşuldu (veri temiz, 2 kritik ürün, sipariş yok).
- 🔵 Tarayıcıda 4 sekme açık: `/` · `/asistan` · `/tedarik` · `/stok`.
- 🔵 PowerPoint açık: `OtoHesap-3dk.pptx`, slayt 1'de.
- 🔵 Telefonda Telegram sohbeti açık, ses açık (Ömer'in telefonu ya da senin).

---

## 1 · Proje Adı ⏱ 0:00–0:20
🔵 Slayt 1 ekranda.
🟢 "Merhaba, biz OtoHesap ekibiyiz. OtoHesap, KOBİ'ler için yapay zekâ destekli bir finans ve stok platformu."
🟢 "İşletme sahibi verisine Türkçe soruyla ulaşıyor; stok bitince sistem sipariş taslağını hazırlıyor, **onay insanda** kalıyor."

## 2 · Problem ⏱ 0:20–0:55
🔵 Slayt 2. Grafiği elinle göster.
🟢 "Türkiye'de yaklaşık 3,9 milyon KOBİ var. İstihdamın yüzde 68'ini, cironun yüzde 44'ünü oluşturuyorlar. Üçte biri ticarette."
🔵 Sağdaki üç kırmızı maddeyi sırayla göster.
🟢 "Bu işletmenin günlük gerçeği şu: raporu Excel'de kovalıyor, stok bitince geç fark ediyor, tek bir sorunun cevabı için menülerde dolaşıyor."

## 3 · Çözüm ⏱ 0:55–1:20
🔵 Slayt 3. Önce sol görsele (Excel), sonra sağa (OtoHesap) işaret et.
🟢 "Solda bugünkü hâl. Sağda OtoHesap: soruyu Türkçe soruyorsunuz, model **yalnızca sorguyu yazıyor**, rakam veritabanından geliyor ve sorgu ekranda görünüyor."
🟢 "Üç şey yapıyoruz: gelir-gider panosu, Türkçe soruyla veri, insan onaylı tedarik ajanı. Şimdi canlı gösterelim."
🔵 PowerPoint'ten tarayıcıya geç (Cmd+Tab).

## 4 · Canlı demo ⏱ 1:20–2:35

### 4a · Genel Bakış ⏱ 1:20–1:40
🔵 Sekme `/`. Dört kartı ve "Kritik ürün: 2"yi göster; aşağıdaki uyarı kartını göster.
🟢 "Bu pano her açılışta veriden hesaplanır. Sistem kendisi uyarıyor: **iki ürün kritik stokta**, reklam gideri geçen aya göre arttı."

### 4b · Asistan ⏱ 1:40–2:05
🔵 Sekme `/asistan`. Çip **"En çok kazancım hangi üründen?"** → tıkla. Yanıt gelince **"Sorguyu gör"** aç, 3 saniye tut.
🟢 "Soruyu Türkçe sorduk. Model SQL'i yazdı, veritabanı yalnızca okundu, rakam gerçek veriden: Powerbank lider."
🟢 "Sorgu görünür; kara kutu yok."

### 4c · Tedarik ⏱ 2:05–2:35
🔵 Sekme `/tedarik`. **"Şimdi kontrol et"** → 2 taslak gelir.
🟢 "Ajan kritik iki ürün için taslak hazırladı: miktar hedef stoğa göre, tutar hesaplı. **Onay bizde.**"
🔵 İlk taslakta **"Onayla"** → telefonu kaldır, jüriye çevir.
🟢 "Onayladım… ve sipariş mesajı tedarikçinin telefonuna düştü."
🔵 Kartta "Gönderildi · teslim alındı değil" yazısını göster.

## 5 · Ekip ve kapanış ⏱ 2:35–2:55
🔵 PowerPoint'e dön, slayt 4.
🟢 "Dört kişiyiz: Kutay arayüz, Muratcan mimari ve asistan, Ömer tedarik ajanı ve Telegram, Yiğit veri ve sunum. Bir günde uçtan uca çalışan ürün, 185 otomatik test, kod GitHub'da."
🟢 "Üç ilke: model sorguyu yazar, rakamı veritabanı verir, siparişi insan onaylar. Sırada Trendyol sipariş akışı ve e-belge. Teşekkürler."

⏱ 2:55–3:00 tampon. Soru gelirse tek cümle.

---

## ⚠️ Yedekler
- ⚠️ Wi-Fi yok → hotspot. LLM yok → çipler **önbellekten** çalışır (serbest soru yazma).
- ⚠️ Telegram gelmezse → kartta "Gönderildi (simülasyon)" rozetini göster: 🟢 "Bugün simülasyon modunda; dün gerçek telefona düştü."
- ⚠️ Uygulama açılmazsa → slayt 3'teki görsellerle anlat, video/ekran görüntüleri `docs/img/`.

## ❓ Jüri sorarsa (tek cümle)
- **Paraşüt'ten farkı?** 🟢 "Onlar e-belge ve banka katmanında güçlü; biz o verinin üstünde doğal dille soru ve onaylı aksiyon katmanıyız."
- **Yanlış SQL üretirse?** 🟢 "Sorgu ayrıştırılıp beyaz listeden geçiyor, salt-okur rolle çalışıyor, süre ve satır sınırı var; SQL görünür."
- **AI kendi başına sipariş verir mi?** 🟢 "Hayır: taslak → onay → gönderim. Onaysız dış mesaj yok."
- **Yerel model mi API mi?** 🟢 "Adaptör arkasında; yerel Qwen da bulut model de aynı sözleşmeyle çalışıyor, veri sentetik."
- **Bir günde mi?** 🟢 "Kapsamı küçük tuttuk, hazır servisler, dosya sahipliği, yapay zekâ destekli paralel geliştirme."
