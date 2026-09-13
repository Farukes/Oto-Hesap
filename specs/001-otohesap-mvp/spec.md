# Feature Specification: OtoHesap MVP (Geliştirme Günü)

**Feature Branch**: `001-otohesap-mvp`

**Created**: 2026-09-13 (D16–D20 sonrası güncellendi)

**Status**: Draft

**Input**: User description: "KOBİ'ler için tek günde çıkan web uygulaması: gelir-gider ve stok panosu, Türkçe soruyla veriye erişen salt-okur finans asistanı (SQL görünür), kritik stokta sipariş taslağı hazırlayıp insan onayıyla tedarikçiye Telegram mesajı atan otonom tedarik ajanı. Kaynak: AGENTS.md §1–§2, docs/demo-senaryosu.md."

## User Scenarios & Testing *(mandatory)*

Kullanıcı: teknoloji aksesuar mağazası sahibi ("işletme sahibi"). Tek kiracı, giriş yok. Demo akışı `docs/demo-senaryosu.md` (7 adım, 5 dk); aşağıdaki hikâyeler bu adımları birebir kapsar. Tüm ekranlarda veri "sentetik demo verisi · Nisan–Eylül 2026" diye etiketlenir.

### User Story 1 - Genel bakış panosu (Priority: P1)

İşletme sahibi uygulamayı açtığında son 6 ayın gelirini, giderini, **farkını** (gelir − gider) ve kritik stoktaki ürün sayısını tek ekranda görür; "aylık gelir–gider" çubuğu ve gider kategorisi pastası "son güncelleme" damgasıyla birlikte gelir. Her açılış veriden hesaplanır.

**Why this priority**: Demonun ilk 30 saniyesi ve "pano gerçek veriyle" checkpoint'i (13:00). Diğer tüm hikâyeler bu ekrana geri döner (gider ekle → pano güncellendi).

**Independent Test**: Seed yüklü veritabanıyla ana ekran açılır; 4 KPI, 6 aylık çubuk (Nis–Eyl) ve pasta görünür; rakamlar seed özetiyle birebir aynıdır.

**Acceptance Scenarios**:

1. **Given** seed yüklü, **When** işletme sahibi ana ekranı açar, **Then** "Gelir", "Gider", "Fark (Gelir − Gider)" ve "Kritik ürün" (= 2) kartları ile "Son güncelleme: <saat>" damgası görünür; aylık çubukta Nisan–Eylül 2026 için 6 sütun, pastada 6 gider kategorisi vardır.
2. **Given** ana ekran açık, **When** başka bir ekranda 4.500 ₺ reklam gideri eklenip ana ekrana dönülür, **Then** gider KPI'sı 4.500 artar, fark 4.500 azalır, pastada reklam payı büyür.
3. **Given** veritabanında hiç satış/gider yok, **When** ana ekran açılır, **Then** KPI'lar 0 gösterir, grafik alanlarında "Veri yok" kartı çıkar, ekran çökmez.
4. **Given** pano açık, **When** etiketler okunur, **Then** hiçbir yerde "net kâr" veya "nakit akışı" yazmaz (D16).

---

### User Story 2 - Kayıt giriş/çıkış (Priority: P1)

İşletme sahibi satış ve gider kayıtlarını listeler, arar, ekler, düzenler, siler; listeyi CSV olarak indirir. Satış eklerken ürün listeden seçilir; birim fiyat ürünün satış fiyatıyla önceden dolar; satış ürün stoğunu düşürür.

**Why this priority**: Demo adımı 2 (gider ekle → pano güncellendi) ve "kurulumsuz, sade giriş-çıkış" tezi. CRUD olmadan pano canlı görünmez.

**Independent Test**: Kayıtlar ekranından bir gider (reklam, 4.500) eklenir; listede görünür; düzenlenip silinir; her adımda API yanıtı ve liste tutarlıdır. CSV indirilip Excel'de açılır.

**Acceptance Scenarios**:

1. **Given** Kayıtlar → Gider sekmesi, **When** "Ekle" ile kategori `reklam`, tutar `4500`, tarih bugün girilip kaydedilir, **Then** kayıt listede en üstte görünür ve yanıt 201'dir.
2. **Given** var olan bir satış kaydı, **When** miktarı düzenlenir, **Then** `total = qty × unit_price` yeniden hesaplanır ve ilgili ürünün stoğu fark kadar ayarlanır.
3. **Given** eşiğin 1 üstünde stoğu olan ürün, **When** o üründen 1 adet satış eklenir, **Then** ürün Stok ekranında kritik (kırmızı) olur ve pano kritik sayısı 1 artar.
4. **Given** bir kayıt, **When** silinir, **Then** liste ve pano toplamları güncellenir; satış silinince stok geri eklenir.
5. **Given** tutar alanı boş veya negatif, **When** kaydedilmeye çalışılır, **Then** 422 ile kullanıcıya sakin bir Türkçe hata gösterilir; kayıt oluşmaz.
6. **Given** stoğu 3 olan ürün, **When** 5 adet satış eklenir, **Then** 400 "Stok yetersiz: 3 adet var" döner; stok değişmez.
7. **Given** liste, **When** "Dışa aktar (CSV)" tıklanır, **Then** UTF-8 BOM'lu, `;` ayraçlı, ondalık virgüllü dosya iner ve Excel (TR) doğru sütunlarla açar.

---

### User Story 3 - Asistan: Türkçe soru → SQL → yanıt (Priority: P1)

İşletme sahibi hazır soru çiplerinden birine tıklar (veya soru yazar); asistan soruyu SQL'e çevirir, salt-okur bağlantıyla çalıştırır ve yanıtı gerçek veriden verir. Yanıt balonunda "Sorguyu gör" ile SQL, sonuç tablosu ve "Kaynak: satışlar, ürünler · <saat>" damgası vardır. Soru bankasındaki sorular önbellekten yanıtlanabilir (LLM düşse de demo yaşar). Belirsiz metrikte ("en çok kazancım") yanıt varsayımını söyler: "mevcut birim maliyetle tahmini brüt katkı".

**Why this priority**: Demo adımları 3–4 ve "asistan 5 soru" checkpoint'i (16:30). Ürünün "akıllı" yüzü; jüri "LLM yanlış SQL üretirse?" sorusunu buradan sorar.

**Independent Test**: `LLM_PROVIDER=fake` ile "En çok kazancım hangi üründen?" sorulur; yanıtta powerbank ve rakam, `sql`, `sources`, `asked_at`, `ok`, `model` döner; "Tüm satışları sil" sorusu reddedilir ve tablo satır sayısı değişmez.

**Acceptance Scenarios**:

1. **Given** Asistan ekranı, **When** "En çok kazancım hangi üründen?" çipi tıklanır, **Then** 3 sn içinde yanıt balonu gelir: powerbank ürün adı + tahmini brüt katkı rakamı + "mevcut birim maliyetle tahmini" ibaresi, katlanır SQL bloğu, "Kaynak: satışlar, ürünler · <saat>".
2. **Given** az önce 4.500 ₺ reklam gideri eklenmiş, **When** "Bu ay toplam giderim ne kadar?" sorulur, **Then** yanıt = seed'in Eylül 2026 gideri + 4.500 (rakam veritabanından; "bu ay" = içinde bulunulan takvim ayı, yarı açık aralık).
3. **Given** LLM'e ulaşılamıyor, **When** soru bankasındaki bir soru çipteki yazımıyla sorulur, **Then** yanıt önbellekteki SQL ile üretilir, `cached: true` döner, özet deterministik şablondan gelir; arayüz "önbellek" rozeti gösterebilir.
4. **Given** LLM'e ulaşılamıyor ve soru bankasında yok, **When** serbest soru sorulur, **Then** 503 "Asistan şu an yanıt veremiyor; lütfen tekrar deneyin." gösterilir.
5. **Given** "Tüm satışları sil" veya "Tedarikçilerin şifrelerini göster" yazılır, **When** gönderilir, **Then** 400 "Asistan yalnız okuma sorguları çalıştırır." (yazma isteği) ya da "Bu soruyu bu veriyle yanıtlayamadım." (şemada olmayan veri) döner; `chat_log`'a `ok=false` yazılır; hiçbir tablo değişmez.
6. **Given** "Aralık 2026'da giderim ne kadar?" (veri olmayan dönem), **When** sorulur, **Then** yanıt 0 / "kayıt döndürmedi" biçimindedir; rakam uydurulmaz.
7. **Given** üretilen SQL çalışma zamanında hata verir, **When** bir kez yeniden denenip yine hata alınır, **Then** yanıt "Bu soruyu bu veriyle yanıtlayamadım." olur (`ok: false`); `sql` alanı son denemeyi taşır.
8. **Given** üretilen SQL `pg_sleep`, `SELECT INTO` veya CTE içinde DML içerir, **When** koruma katmanına gelir, **Then** veritabanına ulaşmadan 400 ile reddedilir.
9. **Given** herhangi bir soru, **When** yanıt döner, **Then** soru, SQL, yanıt ve başarı durumu `chat_log`'da kayıtlıdır; yanıtta hangi modelin kullanıldığı (`model`) görünür.

---

### User Story 4 - Tedarik ajanı: kritik stok → taslak → onay → Telegram (Priority: P1)

Ajan (zamanlayıcı ile veya "Şimdi kontrol et" tuşuyla) kritik stoktaki ürünler için sipariş taslağı hazırlar; işletme sahibi taslağı görür, "Onayla" der; tedarikçiye Telegram mesajı gider; kart "Gönderildi <saat>" olur ve "teslim alındı değil" notu taşır; Stok ekranında "sipariş yolda" rozeti çıkar. Reddedilen taslak kapanır. Aynı ürün için açık sipariş (`draft|approved|sent`) varsa yeni taslak üretilmez — bu koruma veritabanı düzeyindedir.

**Why this priority**: Demonun "vay" anı (adım 6: telefonda mesaj) ve "kontrollü otonomi" tezinin somut kanıtı. 16:30 checkpoint'inin ikinci yarısı.

**Independent Test**: Seed'de "Şimdi kontrol et" tam 2 taslak üretir; ikinci tıklama `created: 0` ve 2 `skipped` (`acik_siparis_var`); ilk taslak onaylanınca (`NOTIFY_DRY_RUN=true` ile bile) durum `sent`, `sent_at` ve `notify_ref` dolu; aynı taslağa ikinci onay 409.

**Acceptance Scenarios**:

1. **Given** seed yüklü (tam 2 kritik ürün), **When** "Şimdi kontrol et" tıklanır, **Then** `created: 2` ve 2 taslak kartı gelir; her kartta ürün, miktar (`target_stock − stock_qty`), tedarikçi, tahmini tutar (`miktar × unit_cost`) ve "DEMO · sentetik sipariş #id" ile başlayan mesaj önizlemesi vardır.
2. **Given** 2 taslak var, **When** "Şimdi kontrol et" tekrar tıklanır (veya zamanlayıcı aynı anda koşar), **Then** `created: 0`, `skipped` listesinde 2 ürün `acik_siparis_var`; taslak sayısı değişmez (DB tekil indeksi).
3. **Given** bir taslak, **When** "Onayla" tıklanır, **Then** 5 sn içinde tedarikçinin telefonunda Telegram mesajı görünür; kart "Gönderildi <saat> · teslim alındı değil" olur; durum `sent`; `notify_ref` Telegram `message_id`'sidir.
4. **Given** durumu `sent` olan sipariş, **When** "Onayla" tekrar istenir (çift tıklama), **Then** 409 "Sipariş zaten sent durumunda." döner; ikinci mesaj gitmez.
5. **Given** Telegram'a ulaşılamıyor, **When** "Onayla" tıklanır, **Then** 502 "Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin." döner; durum `approved` kalır; kart "gönderilemedi, tekrar dene" gösterir; sistem kendi başına tekrar denemez; insan tekrar onaylayınca yeniden gönderir.
6. **Given** bir taslak, **When** "Reddet" tıklanır, **Then** durum `rejected`, kart reddedildi sayacına geçer; aynı ürün için sonraki kontrolde yeni taslak üretilebilir.
7. **Given** sipariş `sent`, **When** Stok ekranı açılır, **Then** ilgili ürün satırında "sipariş yolda" rozeti vardır; ürünün stoğu artmamıştır.
8. **Given** `NOTIFY_DRY_RUN=true` veya bot token yok, **When** onay verilir, **Then** mesaj gönderilmez, loglanır; sipariş `sent`, `notify_ref = "dry-run"`, yanıtta `notify.dry_run = true`; kart "gönderildi (simülasyon)" gösterir.
9. **Given** kritik ürünün tedarikçisi yok, **When** kontrol koşar, **Then** taslak üretilmez; `skipped` listesinde `tedarikci_yok` görünür.

---

### User Story 5 - Stok ekranı (Priority: P2)

İşletme sahibi tüm ürünleri stok, eşik ve hedef stokla listeler; kritik satırlar kırmızıdır; açık siparişi olan üründe rozet vardır ("taslak bekliyor" / "sipariş yolda"); eşik ve hedef stok satır üstünde düzenlenir.

**Why this priority**: Demo adımı 5 ("iki ürün kritik seviyede") görsel köprüdür; ancak US4 kendi başına da çalışır.

**Independent Test**: Stok ekranında tam 2 kırmızı satır; bir ürünün `reorder_point`'i stoğun üstüne çekilince satır kırmızıya döner ve pano kritik sayısı artar.

**Acceptance Scenarios**:

1. **Given** seed yüklü, **When** Stok ekranı açılır, **Then** 20 ürün listelenir, tam 2 satır kırmızı ("kritik") işaretlidir.
2. **Given** kritik olmayan bir ürün, **When** `reorder_point` stoğun üstüne çekilip kaydedilir, **Then** satır kırmızı olur; `GET /api/summary` kritik sayısı 1 artar.
3. **Given** negatif eşik girilir, **When** kaydedilir, **Then** 422 ve Türkçe hata; değer değişmez.
4. **Given** ürünün açık siparişi `draft`, **When** Stok ekranı açılır, **Then** rozet "taslak bekliyor"; `sent` ise "sipariş yolda".

---

### User Story 6 - Öngörü kartları (Priority: P2)

Panoda, sorulmadan üretilen kural tabanlı içgörü kartları görünür (en çok 5, önem sırasıyla): kritik stok uyarısı; bu ay vs geçen ay fark (gelir − gider) değişimi; en çok artan gider kategorisi ("Reklam gideri geçen aya göre %40 arttı"); son 6 ayın en kârlı ürünü (tahmini); online/mağaza kanal payı. Kart metni şablondan üretilir; LLM karar vermez, cümle bile yazmaz.

**Why this priority**: Katalogdaki AI Investigator fikrinin KOBİ ölçeğinde karşılığı ("sorulmadan uyarı"); jüri etkisi yüksek. Demo senaryosunda adım değil; 19:00 dondurma öncesi zaman kalırsa ekranda yer alır.

**Independent Test**: Seed ile `GET /api/insights` en az 3 kart döner (kritik stok `critical` başta); reklam gideri artırılınca gider kartının `change_pct` değeri değişir; kritik ürün sayısı 0'a indirilince kritik kart kaybolur.

**Acceptance Scenarios**:

1. **Given** seed yüklü, **When** pano açılır, **Then** öngörü kartları görünür; her kartta başlık, tek cümle Türkçe gövde, önem (bilgi / uyarı / kritik) ve varsa yüzde değişim vardır; sıralama kritik > uyarı > bilgi.
2. **Given** bu ay bir kategoride gider geçen aya göre > %25 arttı, **When** kartlar hesaplanır, **Then** o kategori `warn` ile gösterilir.
3. **Given** 2 kritik ürün, **When** kartlar hesaplanır, **Then** kritik kart `critical` ve "2 ürün kritik stokta" der; kritik ürün yoksa bu kart üretilmez.
4. **Given** yalnız bu ayın verisi var, **When** kartlar hesaplanır, **Then** karşılaştırma gerektiren kartlar `change_pct: null` ve "karşılaştırma için yeterli veri yok" gövdesiyle gelir; hiç veri yoksa boş liste; hata olmaz.
5. **Given** fark kartı, **When** okunur, **Then** "Fark (gelir − gider)" der, "net kâr" demez; en kârlı ürün kartı "tahmini brüt katkı (mevcut birim maliyetle)" der.

---

### User Story 7 - Dönem filtresi (Priority: P3)

İşletme sahibi panoda "Bu ay / 3 ay / 6 ay" sekmeleriyle KPI'ları ve pastayı dönemsel görür. Varsayılan 6 ay.

**Why this priority**: Görsel analitik yeteneğinin parçası ama demo tek dönemle (6 ay) geçer.

**Independent Test**: `period=month`, `quarter`, `half` ile summary üç farklı gelir rakamı döner ve `half` seed'in tamamını kapsar.

**Acceptance Scenarios**:

1. **Given** pano açık, **When** "Bu ay" seçilir, **Then** KPI'lar yalnız içinde bulunulan takvim ayının toplamlarını gösterir; pasta o ayın kategorilerini.
2. **Given** geçersiz dönem değeri istenir, **When** API çağrılır, **Then** 4xx ve Türkçe açıklama.
3. **Given** aynı dönem seçili, **When** KPI ve pasta karşılaştırılır, **Then** ikisi aynı tarih aralığını kullanır (bkz. FR-032, T015).

---

### Edge Cases

- **Boş veri**: hiç satış/gider yokken pano 0 gösterir, grafikler "Veri yok"; asistan "kayıt döndürmedi"; ajan `created: 0`; öngörü kartları boş liste.
- **LLM düşer / anahtar yok**: soru bankası soruları önbellekten (`cached: true`), özet deterministik şablondan; diğer sorular 503; demo yalnız çiplerle yapılır.
- **LLM geçersiz JSON / geçersiz SQL üretir**: koruma katmanı reddeder (400); çalışma zamanı hatasında bir yeniden deneme; sonra sabit "yanıtlayamadım".
- **Saldırgan soru** ("Tüm satışları sil", `DROP TABLE`, `;`, yorum, beyaz liste dışı tablo, `pg_*` sistem görünümleri, `pg_sleep`, `SELECT INTO`, CTE içinde DML, `FOR UPDATE`): 400; salt-okur rol ikinci kilit; `suppliers.contact_address` sütun düzeyinde kapalı.
- **Sorgu 5 sn'yi aşar**: `statement_timeout` keser → "yanıtlayamadım".
- **Telegram başarısız / okul ağı engelli / zaman aşımı (10 sn)**: sipariş `approved` kalır, 502, insan tekrar dener; kör otomatik tekrar yok; `NOTIFY_DRY_RUN` ile simülasyon rozeti; yedek video.
- **Aynı taslağa çift tık / çift zamanlayıcı**: DB tekil indeksi ikinci siparişi engeller; ikinci onay 409; tek mesaj.
- **Kritik ürünün tedarikçisi yok**: taslak üretilmez, `skipped: tedarikci_yok`, log satırı.
- **Render uyudu / Neon sıfıra indi**: ilk istek 1–2 sn; `make warmup` demo öncesi koşulur; zamanlayıcı uyurken durur, bu yüzden "Şimdi kontrol et" şart (D18).
- **Satış miktarı stoğu aşar**: 400 "Stok yetersiz: N adet var".
- **Aynı gün iki seed koşusu**: rakamlar birebir aynı; `--reset` tabloları boşaltır ve kimlikleri sıfırlar.
- **Ay sınırı**: "bu ay" UTC takvim ayı, yarı açık aralık; seed zaman damgaları gün içi olduğu için UTC/yerel ay sınırı örtüşür.

## Anahtar Kavramlar (Metrik Sözlüğü, D16)

Grafik, SQL, asistan yanıtı ve slayt aynı tanımı kullanır. Bu tanımlar tasarım kararıdır; muhasebe/vergi görüşü değildir.

| Terim | Tanım | Ekranda | Söylenmez |
|-------|-------|---------|-----------|
| Gelir | Σ `sales.total` (satış anı fiyatı × adet); iade/iskonto yok | "Gelir" | "ciro (KDV dahil)" |
| Gider | Σ `expenses.amount` (kaydedilmiş giderler) | "Gider" | "ödeme" |
| Fark | Gelir − Gider; **net kâr değildir** (KDV, iade, tahakkuk, amortisman yok) | "Fark (Gelir − Gider)" | "net kâr", "kâr" |
| Tahmini brüt katkı | Σ qty × (unit_price − `products.unit_cost`); **mevcut** birim maliyetle (tarihsel maliyet yok) | "En kârlı ürün (tahmini)" + "mevcut birim maliyetle" | "kâr marjı" |
| Aylık görünüm | `v_monthly_cashflow`: ay, gelir, gider, fark | "Aylık gelir–gider" | "nakit akışı" |
| Kritik stok | `stock_qty <= reorder_point` | kırmızı satır, "Kritik ürün" KPI | |
| Sipariş `sent` | Mesaj tedarikçiye gönderildi; teslim/kabul/ödeme değil; stok artmaz | "Gönderildi" + "teslim alındı değil" | "sipariş verildi", "teslim alındı" |
| Dönem | Yarı açık aralık `[başlangıç, bitiş)`; "bu ay" = içinde bulunulan takvim ayı (UTC) | "Bu ay / 3 ay / 6 ay" | |
| Sentetik veri | Seed=42, 2026-04-01…2026-09-13, gerçek işletme değil | "Sentetik demo verisi" | "müşteri verisi" |

Belirsiz soruda ("en çok kazancım hangi üründen?") bugün netleştirme sorusu yoktur; varsayılan tahmini brüt katkıdır ve yanıt varsayımı söyler (D20).

## Requirements *(mandatory)*

### Functional Requirements

Genel bakış (US1)
- **FR-001**: Sistem, seçilen dönem için Gelir, Gider, Fark (gelir − gider), kritik ürün sayısı ve hesaplama zaman damgasını tek istekte vermek ZORUNDADIR (`GET /api/summary`).
- **FR-002**: Sistem aylık gelir/gider/fark serisini `YYYY-MM` etiketiyle, içinde bulunulan ay dâhil son 6 ay için (veri olmayan ay 0) vermek ZORUNDADIR (`GET /api/cashflow/monthly`).
- **FR-003**: Sistem gider dağılımını kategori, tutar ve yüzde payla (0–100, 1 ondalık) vermek ZORUNDADIR (`GET /api/analytics/expenses-by-category`).
- **FR-004**: Sistem ürün bazında ciro, tahmini brüt katkı (`Σ qty × (unit_price − unit_cost)`) ve adet listesini ciroya göre sıralı ve `top` sınırıyla vermek ZORUNDADIR (`GET /api/analytics/sales-by-product`).
- **FR-005**: Arayüz boş veri, yükleniyor ve hata durumlarını her ekranda ele almak ZORUNDADIR; grafik bileşenine boş dizi verilmez.

Kayıtlar (US2)
- **FR-006**: Sistem satış ve gider kayıtlarını sayfalı (`limit` 1–500, `offset`) ve aranabilir (`q`) listelemek, toplam sayıyı döndürmek ZORUNDADIR; sıralama en yeni önce.
- **FR-007**: Sistem satış oluşturma/düzenleme/silme sağlamak ZORUNDADIR; `total = qty × unit_price` sunucuda hesaplanır; `unit_price` boşsa ürünün `sale_price`'ı, `sold_at` boşsa şimdi; oluşturma ürün stoğunu `qty` kadar düşürür, silme geri ekler, düzenleme farkı uygular (ürün değişirse eskiye iade, yeniye düşüm); stok yetersizse 400 "Stok yetersiz: N adet var".
- **FR-008**: Sistem gider oluşturma/düzenleme/silme sağlamak ZORUNDADIR; arayüz kategoriyi 6 sabit seçenekten (kira, maas, elektrik, kargo, reklam, tedarik) seçtirir; API boş olmayan metin kabul eder; `amount > 0`.
- **FR-009**: Bulunmayan kayıt 404 ("Satış bulunamadı", "Gider bulunamadı", "Ürün bulunamadı"), geçersiz gövde 422; tüm hata gövdeleri `{detail}` biçiminde ve Türkçe olmak ZORUNDADIR (422 için özel handler: T014).
- **FR-010**: Sistem satış ve gider listelerini CSV (UTF-8 BOM, `;` ayraç, ondalık virgül, Türkçe başlık, CRLF, formül enjeksiyonuna karşı `'` öneki) olarak vermek ZORUNDADIR (`GET /api/export/{sales,expenses}.csv`).
- **FR-011**: Sistem ürün listesini kayıt formunda seçim için sunmak ZORUNDADIR (`GET /api/products`).

Asistan (US3)
- **FR-012**: Sistem Türkçe soruyu SQL'e çevirip çalıştırmak ve `ok, answer, sql, rows, columns, sources, asked_at, cached, model` alanlarıyla yanıtlamak ZORUNDADIR (`POST /api/assistant/ask`); `rows` sütun adlı nesnelerdir; `model` yanıtı üreten sağlayıcı/model adıdır (D19).
- **FR-013**: Sistem üretilen SQL'i şu katmanlardan geçirmek ZORUNDADIR: tek ifade ve `SELECT`/`WITH … SELECT`/set işlemi; `;`, `--`, `/*` reddi; DDL/DML düğümü (CTE içinde dâhil), `SELECT INTO`, `FOR UPDATE/SHARE` reddi; sqlglot AST tablo beyaz listesi (`sales, expenses, products, suppliers, purchase_orders, v_monthly_cashflow`, yalnız `public`); **fonksiyon izin listesi** (sum, count, avg, min, max, coalesce, round, date_trunc, date_part, extract, now, current_date, to_char, lower, upper, cast, nullif, greatest, least, abs) — `pg_sleep`, `set_config`, `pg_read_file` ve diğer `pg_*` red; `LIMIT` yoksa `LIMIT 200`, büyükse 200'e kırpma; 5 sn `statement_timeout`; salt-okur bağlantı (`DATABASE_URL_RO`); `suppliers.contact_address` prompt şemasında yok ve role sütun düzeyinde kapalı.
- **FR-014**: SQL çalışma zamanı hatasında sistem hata mesajıyla tam bir kez yeniden denemek, yine hata alırsa `ok: false` ve "Bu soruyu bu veriyle yanıtlayamadım." döndürmek ZORUNDADIR. Güvenlik reddi başka bir modele tekrar sorulmaz.
- **FR-015**: Yanıt özeti yalnız sorgu sonucundan üretilmek ZORUNDADIR; özet için modele yalnız sütun adları ve ilk 20 satır verilir; sonuç boşsa "Sorgu bu veriyle eşleşen kayıt döndürmedi."; özet üretilemezse deterministik şablon ("Sorgu N satır döndürdü; ilk satır: …").
- **FR-016**: Sistem soru bankasındaki (`apps/api/app/data/soru_bankasi.json`; okunur kopya `docs/soru-bankasi.md`) soruları normalize metin eşleşmesiyle (küçük harf, noktalama ve fazla boşluk atılır) önbellekten yanıtlamak (`cached: true`) ZORUNDADIR; önbellekten gelen SQL de koruma katmanından geçer.
- **FR-017**: Her soru (reddedilenler dâhil) `chat_log`'a `question, sql_text, answer, ok` ile yazılmak ZORUNDADIR.
- **FR-018**: Sistem hazır soru çiplerini soru bankasındaki `demo: true` sorulardan vermek ZORUNDADIR (`GET /api/assistant/suggestions`); banka yoksa gömülü 5 demo sorusu; sıra demo senaryosuyla uyumlu olmalıdır (T081).
- **FR-019**: Koruma katmanının reddettiği istek 400 "Asistan yalnız okuma sorguları çalıştırır." ile dönmek, veritabanında hiçbir satırı değiştirmemek ZORUNDADIR; LLM'e ulaşılamıyorsa 503 "Asistan şu an yanıt veremiyor; lütfen tekrar deneyin."; boş soru 400 "Soru boş olamaz."
- **FR-020**: Tarih filtreleri yarı açık aralık `[başlangıç, bitiş)` kullanmak; "bu ay" = içinde bulunulan takvim ayı (UTC); belirsiz metrikte D16 varsayılanı uygulanıp yanıt metninde varsayım cümlesi ("mevcut birim maliyetle tahmini brüt katkı") yer almak ZORUNDADIR (D20).

Tedarik (US4)
- **FR-021**: Sistem `stock_qty <= reorder_point` olan her ürün için taslak üretmek ZORUNDADIR: `qty = max(1, target_stock − stock_qty)`, `est_amount = qty × unit_cost`, `message_text` şablondan (FR-028), `status = draft`; yanıt `{created, drafts, skipped[{product_id, reason}]}`.
- **FR-022**: Aynı ürün için durumu `draft|approved|sent` olan sipariş varsa yeni taslak üretilmemek ZORUNDADIR; koruma veritabanı düzeyindedir (kısmi tekil indeks `ux_open_order_per_product`); çift tıklama veya çift zamanlayıcı ikinci sipariş üretemez; atlanan ürün `skipped` (`acik_siparis_var`) olarak döner; `rejected` engel değildir (D17).
- **FR-023**: Sistem siparişleri duruma göre listelemek ve tek sipariş getirmek ZORUNDADIR (`GET /api/orders?status=`, `GET /api/orders/{id}`); sipariş nesnesi `notify_ref` taşır.
- **FR-024**: Onay şu sırayla işlemek ZORUNDADIR: `draft → approved` (commit) → mesaj gönder → `sent` + `sent_at` + `notify_ref` (commit). Gönderim başarısızsa durum `approved` kalır ve 502 "Mesaj gönderilemedi; sipariş onaylı bekliyor, tekrar deneyin." döner; sistem kör tekrar yapmaz; `approved` sipariş insan tarafından yeniden onaylanabilir; `sent`/`rejected` için 409 "Sipariş zaten {status} durumunda.". Yanıt: sipariş + `notify{ok, dry_run, channel, message_id}`.
- **FR-025**: Reddetme `draft|approved → rejected` geçişini yapmak, `sent|rejected` için 409 vermek ZORUNDADIR.
- **FR-026**: Zamanlayıcı `AGENT_CHECK_INTERVAL_MIN` dakikada bir kontrolü koşturmak (`max_instances=1`, `coalesce=True`, sabit job kimliği) ve sonucu loglamak ZORUNDADIR; "Şimdi kontrol et" aynı `run_check` fonksiyonudur. Zamanlayıcı mesaj göndermez. Render Free'de API uyurken zamanlayıcının durduğu sunumda saklanmaz (D18).
- **FR-027**: `NOTIFY_DRY_RUN=true` veya bot token yokken sistem mesajı göndermeden loglamak, siparişi `sent` yapmak, `notify_ref = "dry-run"` ve yanıtta `notify.dry_run = true` döndürmek ZORUNDADIR; `email` kanalı bugün dry-run gibi davranır.
- **FR-028**: Telegram mesajı Türkçe şablondan üretilmek ZORUNDADIR: "DEMO · sentetik sipariş #{id} — Merhaba {tedarikçi}, {işletme adı} için sipariş talebi: {ürün} × {miktar} adet. Tahmini tutar {tutar} ₺. Teslim süresi {lead_time_days} gün. Onay için bu mesajı yanıtlayabilirsiniz. — OtoHesap" (`BUSINESS_NAME`; tutar tr-TR biçimi). Bot token'ı hiçbir log veya hata metninde yer almaz.
- **FR-029**: `sent` durumu "mesaj gönderildi" anlamına gelmek ZORUNDADIR; teslim, kabul veya ödeme değildir; stok artırılmaz; arayüz "Gönderildi" yanında "teslim alındı değil" notu gösterir (D17).

Stok (US5)
- **FR-030**: Ürün listesi her ürün için `is_critical` (= `stock_qty <= reorder_point`), `supplier_name` ve `open_order_id` (durumu `draft|approved|sent` olan en yeni sipariş; yoksa null) taşımak ZORUNDADIR; rozet metni için arayüz sipariş durumunu `GET /api/orders` ile eşler.
- **FR-031**: Sistem `reorder_point`, `target_stock`, `stock_qty` alanlarını kısmi güncellemeye izin vermek ZORUNDADIR (`PATCH /api/products/{id}`); negatif değer 422.
- **FR-032**: `period` parametresi `month|quarter|half` değerlerini almak, varsayılan `half` olmak, geçersiz değerde 4xx Türkçe açıklama vermek ZORUNDADIR; özet, analitik ve aylık seri **aynı** dönem tanımını kullanmak ZORUNDADIR (bugün üç ayrı hesap var; birleştirme T015, research.md R-17).

Öngörü (US6)
- **FR-033**: Sistem en çok 5 kural tabanlı içgörü kartı üretmek ZORUNDADIR (`GET /api/insights`): kritik stok (`critical`); bu ay vs geçen ay fark değişimi (`warn` düşüş > %10); en çok artan gider kategorisi (`warn` artış > %25); son 6 ayın en kârlı ürünü (tahmini); kanal payı; her kart `id, title, body, severity(info|warn|critical), metric, change_pct`; sıralama critical > warn > info; boş veri → boş liste; metin şablondan, LLM yok; sözcükler D16.

Kesişen
- **FR-034**: Arayüz metinleri D16 sözlüğünü kullanmak ZORUNDADIR: "Fark (Gelir − Gider)" (net kâr değil), "En kârlı ürün (tahmini)", "Aylık gelir–gider" (nakit akışı değil), "Sentetik demo verisi" etiketi.
- **FR-035**: `GET /api/health` `{status, db, llm, scheduler, version}` döndürmek ZORUNDADIR; `db` gerçek bir `SELECT 1` sonucudur.
- **FR-036**: Tarihler ISO 8601 UTC, para JSON `number` olmak ZORUNDADIR; 4xx kullanıcı hatası, 5xx bizim hatamız.
- **FR-037**: Her HTTP isteği (yöntem, yol, durum, süre) ve her asistan/ajan kararı loglanmak ZORUNDADIR; loglarda kişisel veri, bağlantı dizesi veya token olmaz.
- **FR-038**: Seed deterministik olmak ZORUNDADIR (`seed=42`, sabit aralık 2026-04-01…2026-09-13, `--reset`); hedefler `data-model.md` §6.
- **FR-039**: Yayında CORS yalnız üretim web adresi + yerel geliştirme adresine açık olmak ZORUNDADIR.
- **FR-040**: Demo öncesi ısıtma betiği (`scripts/warmup.sh`) health, DB'ye dokunan bir istek, öneri listesi ve küçük bir LLM çağrısı koşturmak ZORUNDADIR.

### Key Entities *(include if feature involves data)*

- **Tedarikçi (suppliers)**: sipariş mesajının alıcısı; iletişim kanalı (`telegram|email`) ve adresi (chat_id / e-posta; asistana kapalı), teslim süresi (gün). Bir tedarikçinin çok ürünü olur.
- **Ürün (products)**: satılan mal; kategori, birim maliyet (mevcut), satış fiyatı, mevcut stok, kritik eşik (`reorder_point`), sipariş sonrası hedef (`target_stock`), tedarikçi. Türetilmiş: `is_critical`, `open_order_id`.
- **Satış (sales)**: tarih-saat, ürün, adet, birim fiyat, toplam, kanal (`magaza|online`). Gelirin kaynağı.
- **Gider (expenses)**: tarih-saat, kategori (6 sabit), tutar, tedarikçi/satıcı adı, not. Giderin kaynağı.
- **Sipariş (purchase_orders)**: ajan taslağı; ürün, tedarikçi, adet, tahmini tutar, durum (`draft|approved|sent|rejected`), mesaj metni, gönderim zamanı, gönderim izi (`notify_ref`). Ürün başına en çok bir açık sipariş. İnsan onayı izi.
- **Sohbet kaydı (chat_log)**: soru, üretilen SQL, yanıt, başarı; şeffaflık ve eval izi; asistana kapalı.
- **Aylık gelir–gider (v_monthly_cashflow, görünüm)**: ay, gelir, gider, fark; pano çubuğunun ve öngörü kartlarının kaynağı.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 15 soruluk eval setinde (5 basit toplam · 3 tarih filtresi · 3 join · 2 boş/uç · 2 saldırgan) en az 12 soru doğru: beklenen rakam + yalnız izinli tablolar + yazma yok.
- **SC-002**: Demo senaryosundaki 5 soru %100 doğru yanıtlanır (rakam seed özetiyle aynı).
- **SC-003**: 2 saldırgan istek ve guard birim testlerindeki tüm zararlı girdiler (DML, CTE-DML, `SELECT INTO`, `pg_sleep`, izinsiz tablo) %100 reddedilir; eval sonrası tablo satır sayıları eval öncesiyle aynıdır.
- **SC-004**: 5 dakikalık demo senaryosu (7 adım) üst üste 2 provada hatasız, süre aşımsız tamamlanır.
- **SC-005**: Isınmış sistemde Genel Bakış ekranı 2 sn içinde tüm KPI ve grafiklerle yüklenir; asistan yanıtı 3 sn içinde gelir (önbellek) / 8 sn içinde (LLM).
- **SC-006**: "Onayla" tıklanmasından telefonda mesajın görünmesine kadar geçen süre 5 sn'nin altındadır.
- **SC-007**: Seed iki kez koşulduğunda özet rakamlar birebir aynıdır; kritik ürün sayısı tam 2, eşiğin 1 üstünde tam 1'dir; koşu 10 sn'nin altındadır.
- **SC-008**: Gider eklendikten sonra panoya dönüldüğünde KPI ve pasta tek yüklemede güncel görünür.
- **SC-009**: CI (`ruff`, `pytest`, `lint`, `build`) `main`'de yeşildir; canlı adres okul ağı dışından bir cihazdan uçtan uca çalışır.
- **SC-010**: Her asistan yanıtında SQL, kaynak damgası ve model adı görünür (100 yanıtta 100).
- **SC-011**: 10 ardışık "Şimdi kontrol et" çağrısı ve eşzamanlı çift onay tıklaması toplamda ürün başına en çok 1 açık sipariş ve en çok 1 Telegram mesajı üretir.
- **SC-012**: Arayüz ve slaytlarda "net kâr" / "nakit akışı" ifadesi geçmez; "en kârlı ürün" her yerde "tahmini" etiketlidir (metin araması 0 sonuç).

## Kapsam Dışı (AGENTS.md §2)

Giriş/kimlik doğrulama · çok kiracı · e-Fatura/e-İrsaliye · banka entegrasyonu · WhatsApp Business · mobil uygulama · Excel içe aktarma · Vanna/LangChain/LlamaIndex/LangGraph/Microsoft Agent Framework/PydanticAI/arq/Celery · Tremor · Azure taşıma · Trendyol entegrasyonu (yol haritası: yalnız Product V2) · LLM'in mesaj metnini cilalaması · asistanda `clarify` (netleştirme sorusu) durumu (D20) · sipariş `received/cancelled` ve kısmi teslim (D17) · tarihsel maliyet / KDV / iade modeli (D16) · Render ücretli instance ile 7/24 zamanlayıcı (D18, final sonrası karar).

## Assumptions

- Kullanıcı tek işletme sahibidir; giriş yoktur; tarayıcıdan (masaüstü ve mobil genişlik) erişir.
- Demo verisi %100 sentetiktir (D12) ve öyle etiketlenir; gerçek müşteri verisi bu sürüme girmez; mali müşavir doğrulaması gerçek müşteri öncesi kapıdır.
- Neon, Render ve Vercel ücretsiz katmanları demo günü erişilebilirdir; soğuk başlangıç ısıtma betiğiyle giderilir; zamanlayıcı uyuması bilinir ve söylenir.
- Telegram Bot API'ye demo ağından erişilebilir; erişilemezse hotspot, olmazsa `NOTIFY_DRY_RUN` ve yedek video.
- Soru bankası (15 soru) yazıldı; beklenen rakamlar seed sonrası Yiğit tarafından doldurulur; çiplerdeki yazım bankayla birebirdir.
- Ekipteki dört kişi kendi dalında, AGENTS.md §4 dosya sahipliğiyle paralel çalışır.
- Seed tarih aralığı sabittir (2026-04-01 … 2026-09-13); "bu ay" demo günü Eylül 2026'dır; gelecek tarihli kayıt yoktur.
