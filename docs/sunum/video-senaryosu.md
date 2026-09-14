# 90 saniyelik demo videosu — çekim listesi

> Amaç: sahnede her şey düşerse oynatılacak **yedek video** (ve sosyal/paylaşım sürümü).
> Kaynak akış: `docs/sunum/3-dakika-akis.md`'in kısaltılmışı. Tek gerçek kaynak yine `docs/demo-senaryosu.md`.
> Kurgu: **Canva**. Alt yazılar Canva'da metin katmanı olarak eklenir (videoda seslendirme **yok**, müzik sessiz/enstrümantal).
> Sahibi: Ömer (ekran kaydı) + Yiğit (kurgu). Toplam: **90 sn**.

## Çekim öncesi kontrol listesi

- [ ] `python data/seed.py --reset` koşuldu (rakamlar deterministik: 608 satış, 228 gider, **tam 2 kritik ürün**, kâr lideri Powerbank 20000 mAh)
- [ ] `make warmup` → `/api/health` yeşil (Render Free uykudan kalkmış olsun)
- [ ] Tarayıcı **1440 px genişlik**, açık tema, tam ekran, yer imleri gizli, sekme tek
- [ ] Telegram sohbeti telefonda açık; telefon **Do Not Disturb** ve tam şarj
- [ ] Ekran kaydı **1920×1080, 30 fps**; fare imleci görünür, tıklama vurgusu açık
- [ ] Tedarik ekranında **onay bekleyen en az 1 taslak** var (yoksa "Şimdi kontrol et")
- [ ] Kişisel bildirim / e-posta kapalı, saat çubuğunda özel bilgi yok

---

## Sahne listesi (toplam 90 sn)

| # | Süre | Zaman | Ekran / kaynak | Tıklama ve hareket | Alt yazı (Canva metni) |
|---|------|-------|----------------|--------------------|------------------------|
| 1 | **6 sn** | 0:00–0:06 | Başlık kartı (Canva, lacivert `#0F2A3C` zemin, yeşil `#1C8C6E` marka işareti) | Hareket yok; logo 0,5 sn fade-in | **OtoHesap**<br>Verinizi anlayın. İşinizi yönetin. |
| 2 | **8 sn** | 0:06–0:14 | Metin kartı (nane `#EAF5F1` zemin) | Hareket yok | KOBİ sahibi Excel ile rapor kovalıyor,<br>stok bitince geç fark ediyor. |
| 3 | **12 sn** | 0:14–0:26 | `/` **Genel Bakış** | Sayfa açık; 4 KPI kartında 1 sn zoom (Canva'da yumuşak scale), sonra Öngörü kartlarına yavaş kaydırma | Gelir, gider, **fark** ve kritik stok —<br>her açılışta veriden hesaplanır.<br><sub>Fark = gelir − gider (net kâr değildir)</sub> |
| 4 | **6 sn** | 0:26–0:32 | `/` Öngörü kartları | "2 ürün kritik stokta" kartında dur, kırmızı `#C0392B` çerçeve vurgusu | Sistem kendisi uyarıyor:<br>**2 ürün kritik stokta.** |
| 5 | **16 sn** | 0:32–0:48 | `/asistan` | Çipe tıkla: **"En çok kazancım hangi üründen?"** → yanıt gelsin (2–3 sn) → tabloyu göster | Türkçe sor. Model **yalnız SQL'i yazar**;<br>rakamı veritabanı verir. |
| 6 | **10 sn** | 0:48–0:58 | `/asistan` | **"Sorguyu gör"** aç → SQL bloğunda 4 sn dur → kapat | Kullanılan sorgu **görünür**.<br>Veritabanı rolü **salt-okur**. |
| 7 | **8 sn** | 0:58–1:06 | `/stok` | Sayfaya geç; 2 kırmızı satırda dur | Kritik eşiğin altına düşen ürünler. |
| 8 | **12 sn** | 1:06–1:18 | `/tedarik` | **"Şimdi kontrol et"** → taslak kartı belirsin → miktar ve tutar alanında 2 sn dur | Ajan **taslağı** hazırlar:<br>miktar hedef stoğa göre hesaplanır. |
| 9 | **8 sn** | 1:18–1:26 | `/tedarik` → telefon | **"Onayla"** tıkla → kart "Gönderildi" olsun → kesme (cut) ile telefon ekranı: Telegram mesajı | **Onay insanda.**<br>Onaydan sonra mesaj tedarikçiye gider.<br><sub>"Gönderildi" = mesaj gönderildi, teslim alındı değil</sub> |
| 10 | **4 sn** | 1:26–1:30 | Kapanış kartı (lacivert zemin) | Logo + slogan fade-in | **Karmaşıklık arkada, karar önünde.**<br><sub>Sentetik demo verisi · Nisan–Eylül 2026</sub> |

**Toplam: 6+8+12+6+16+10+8+12+8+4 = 90 sn** ✅

---

## Kurgu notları (Canva)

- **Renk dili:** lacivert `#0F2A3C` (kart zeminleri ve kapanış), yeşil `#1C8C6E` (vurgu, alt yazı şeridi), nane `#EAF5F1` (açık kartlar), kırmızı `#C0392B` **yalnız** kritik stok vurgusunda.
- **Yazı tipi:** sistem sans (Arial/Helvetica). Alt yazı **28–34 pt**, koyu zeminde beyaz; açık zeminde lacivert. Her alt yazı en fazla **2 satır**.
- **Geçişler:** yalnız `cut` ve 0,3 sn `dissolve`. Sahne 9'daki ekran→telefon geçişi **sert cut** olsun; etki oradan geliyor.
- **Hız:** ekran kayıtlarında bekleme anlarını (yanıt beklerken) **1,5×** hızlandır; tıklama anlarını **1×** bırak.
- **Ses:** seslendirme yok. Enstrümantal, düşük ses (−22 dB). Tıklama sesleri kapalı.
- **Telefon çekimi:** telefonu sabit tut veya ekranı kaydet (QuickTime / Android scrcpy); elde sallanan çekim kullanma.
- **Dışa aktarım:** MP4, 1080p, 30 fps, < 40 MB. Dosya adı `otohesap-demo-90sn.mp4`.
- **Nereye:** USB + telefon + sunum bilgisayarının masaüstü. Depoya **video dosyası commit'lenmez** (boyut); bağlantı README'ye eklenir.

## Uyulması zorunlu ifadeler

- "Fark" **net kâr değildir** → alt yazıda parantez notu (sahne 3).
- "Gönderildi" **teslim alındı değildir** → alt yazıda parantez notu (sahne 9).
- "En kârlı ürün" **tahmini brüt katkıdır** → sahne 5'te tabloya ekran içi not düşülemiyorsa kapanış kartına küçük punto not.
- Veri **sentetik demo verisi** → kapanış kartında görünür (sahne 10).
- **"Rakiplerde AI yok"** benzeri hiçbir karşılaştırma cümlesi kullanılmaz.
- Doğrulanmamış yüzde / tasarruf iddiası (ör. "%40 zaman kazandırır") alt yazıya girmez.

## TODO(yigit)

- Sahne 1 ve 10 için Canva başlık kartı tasarımı (marka işareti `docs/img/` ekran görüntülerindeki logo ile aynı dilde olsun).
- Video yüklendikten sonra bağlantıyı README "Ekranlar" bölümüne ekle.
