# OtoHesap Derin Araştırma Raporu: Teknoloji, Pazar, Yol Haritası ve Jüri Hikâyesi

Bu rapor, güncellenmiş iki araştırma brief’ini **görev olarak yürütür**; “derin araştırma nasıl yapılır?” metodolojisini anlatmaz. Teknoloji tarafında mevcut stack değiştirilmeden hızlandırma, pazar tarafında ise Türkiye KOBİ pazarı, rakipler, Trendyol, Microsoft ekosistemi, KVKK ve pitch ele alınmıştır. Geliştirme Günü kapsamının büyütülmemesi ve yeni fikirlerin yol haritasına atılması kuralı korunmuştur. fileciteturn0file0 fileciteturn0file1 fileciteturn0file2

**Güven etiketleri:** **A** = birincil/resmî kaynak, **B** = birden fazla güvenilir ikincil kaynak, **C** = tek ikincil kaynak, **D** = blog/forum hipotezi, **X** = doğrulanamadı veya ekip tahmini.

## Yönetici kararı

Araştırmanın en önemli sonucu şu: **OtoHesap’ın 1 günlük kapsamı doğru yerde. Yeni framework, yeni mesajlaşma kanalı, gerçek pazaryeri entegrasyonu veya e-Fatura entegrasyonu eklemeyin.** Jüride güçlü görünen kombinasyon zaten elinizde: çalışan dashboard + Türkçe soru → görünür SQL → salt-okur veri erişimi + kritik stok → taslak sipariş → insan onayı → telefona gerçek Telegram mesajı. Bu ürün sınırı güncellenmiş PROMPT-1 ve README ile de uyumlu. fileciteturn0file0 fileciteturn0file2

| Bulgu | Karar | Güven |
|---|---|---|
| shadcn/ui’nun resmî `dashboard-01` bloğu sidebar, grafik ve veri tablosunu birlikte sağlıyor; 2026 güncellemeleriyle block yapısı aktif olarak sürdürülüyor. citeturn0search0turn0search14 | **Dashboard’u sıfırdan tasarlamayın.** shadcn dashboard iskeletini alıp OtoHesap markasına göre sadeleştirin. | **A** |
| FastAPI’nin resmî full-stack şablonu PostgreSQL, test, frontend, CI/CD vb. içeriyor fakat SQLModel tabanlı ve OtoHesap’ın sabit SQLAlchemy 2 monorepo yapısıyla birebir uyuşmuyor. citeturn0search4 | **Projeyi yeni template’e taşımayın.** Session/dependency/test kalıplarından yararlanın; mevcut API’yi ince tutun. | **A** |
| SQLGlot SQL’i AST olarak parse edip tablo/kolon/statement yapısının incelenmesine izin veriyor; dokümantasyon parser’ın tek başına veritabanı doğrulayıcısı olmadığını da açıkça belirtiyor. citeturn0search1 | Text-to-SQL için büyük framework yerine **LLM + Pydantic JSON + SQLGlot + DB salt-okur rolü** kullanın. | **A** |
| Render Free web servisleri 15 dakika gelen trafik olmadığında uykuya geçebiliyor ve yeniden ayağa kalkması yaklaşık bir dakika sürebiliyor. citeturn9search1turn9search0 | **Demo öncesi API ve DB’yi mutlaka ısıtın.** Ayrıca scheduler’ın yanına manuel “Stok kontrolünü şimdi çalıştır” düğmesi koyun. | **A** |
| Trendyol Product V1 servislerinin **15 Eylül 2026 itibarıyla kullanım dışı kalacağı** resmî dokümanda yazıyor. Bugün 13 Eylül 2026. citeturn20search10 | Roadmap entegrasyonunda **V1 için tek satır kod yazmayın; Product V2 hedefleyin.** | **A** |
| Azure for Students’ın güncel resmî sayfası $100 kredi ve Azure OpenAI gibi teknolojilere erişimi açıkça listeliyor. citeturn21search2turn21search9 | Prompttaki “Azure OpenAI öğrenci aboneliğinde destek dışı olabilir” varsayımı yumuşatılmalı: **genel erişim destekleniyor; sizin aboneliğinizde model/bölge/kota uygunluğu portalda ayrıca doğrulanmalı.** | **A / X bireysel kota** |
| Anthropic’in güncel resmî kaynaklarında **Claude Haiku 4.5** ve **Claude Sonnet 4.6** var; ayrıca Opus 5 yayımlanmış durumda. Araştırmada resmî bir “Claude Sonnet 5” modeli doğrulanamadı. citeturn4search0turn4search7turn4search6 | `.env`/config’te “Sonnet 5” hard-code etmeyin. **Haiku 4.5 default, Sonnet 4.6 kalite modu** olarak kullanın; Sonnet 5’i doğrulanana kadar X kabul edin. | **A / X Sonnet 5** |
| Türkiye’de 2024 itibarıyla **3,928 milyon KOBİ** bulunuyor; KOBİ’ler girişimlerin %99,6’sını, istihdamın %68,5’ini ve cironun %44,1’ini oluşturuyor. citeturn15search7 | Sunumun ana pazar rakamı bu olmalı. “Türkiye’de milyonlarca KOBİ” gibi yuvarlak ve kaynaksız cümle yerine bu üç sayı kullanılsın. | **A** |
| KVKK m.9’un yeni yurt dışı aktarım rejimi 1 Haziran 2024’te yürürlüğe girdi; standart sözleşmeler uygun güvence yollarından biri ve imzalandıktan sonra beş iş günü içinde Kuruma bildirim gerekiyor. citeturn19search2turn19search3 | Demo sentetik veriyle kalmalı. Gerçek müşteri verisi yabancı LLM’e geçmeden önce **veri minimizasyonu + aktarım hukuki mekanizması + sağlayıcı sözleşmesi** tasarlanmalı. | **A** |

**Ana teknik karar:** OtoHesap’ı bir günde “mini ERP” yapmaya çalışmayın. **Güçlü bir operasyon zekâsı prototipi** yapın. Ön muhasebe, e-Fatura, banka ve pazaryeri fonksiyonları zaten yerleşik oyuncuların güçlü olduğu alanlar; OtoHesap’ın farklılaştırıcı katmanı “veriyi Türkçe soruyla açıklama ve kontrollü aksiyona dönüştürme” olmalı. Paraşüt ve Logo İşbaşı’nın resmî ürün sayfaları e-belge, stok, banka ve e-ticaret entegrasyonlarının pazarda zaten güçlü beklentiler olduğunu gösteriyor. citeturn22search0turn22search4

## Bugün uygulanacak teknoloji ve mimari

PROMPT-1’in “bugün saat kazandıracak hazır parçalar” hedefi açısından en büyük hata, her problemi yeni bir framework ile çözmeye çalışmak olur. OtoHesap’ın veri modeli küçük, akışı belirli ve demo süresi beş dakika; dolayısıyla entegrasyon yüzeyini küçültmek framework zenginliğinden daha değerlidir. fileciteturn0file0

| Alan | Araştırma bulgusu | Kurulum / efor | Ücret / lisans | Risk / tuzak | Karar önerim | Güven |
|---|---|---:|---|---|---|---|
| UI | shadcn/ui resmî dashboard bloğu sidebar, chart ve data table sağlıyor. citeturn0search0turn0search14 | **20–40 dk** ekip tahmini | Açık kaynak | Hazır temayı fazla özelleştirmek | `dashboard-01` + Card/Table/Dialog/Badge; chat ve SQL alanını ince custom component yapın. | **A; süre X** |
| Grafik | Stack zaten Recharts olarak kilitli. fileciteturn0file0 | 30–60 dk | Mevcut | Tremor gibi ikinci katman eklemek CSS/tema çakışması yaratabilir | **Tremor eklemeyin.** Recharts + shadcn kartı yeterli. | **A proje kararı** |
| FastAPI CRUD | Resmî FastAPI full-stack template kapsamlı ama SQLModel kullanıyor. citeturn0search4 | 45–90 dk | Açık kaynak | Template migration’ı yarım günü yiyebilir | Mevcut SQLAlchemy 2 modelleri + generic session dependency + küçük CRUD router’ları. | **A** |
| Text-to-SQL | SQLGlot AST parse/inspect sağlıyor ancak tek başına DB doğrulaması yapmıyor. citeturn0search1 | 2–3 saat | Açık kaynak | “Parser geçti = güvenli” sanmak | **150–250 satırlık kendi servisiniz** daha doğru. | **A + tasarım** |
| Agent/HITL | LangGraph `interrupt()` ile workflow durdurup insan kararından sonra devam edebiliyor; Microsoft Agent Framework de human-in-the-loop akışları destekliyor ve 2026’da hâlâ gelişen/public-preview bir çerçeve. citeturn2search0turn2search1turn1search0turn1search1 | Framework eklemek 1–3+ saat | Değişken | Tek akış için gereksiz soyutlama | Bugün **DB state machine + approval endpoint**. LangGraph/Microsoft Agent Framework yol haritasında. | **A** |
| Scheduler | Projede APScheduler kararı zaten verilmiş. fileciteturn0file0 | 20–30 dk | Açık kaynak | Render uyursa scheduler da fiilen çalışmaz. citeturn9search1 | APScheduler kalsın; demoda ayrıca manuel trigger endpoint’i olsun. | **A** |
| Bildirim | Telegram Bot API HTTP tabanlı ve `sendMessage` resmî olarak doğrudan destekleniyor. citeturn13search0 | 15–30 dk | Standart `sendMessage` için dokümanda ayrı mesaj ücreti belirtilmiyor | Bot/chat ID hazırlanmamışsa demo bloklanır | **Telegram açık ara demo seçimi.** | **A** |
| Sentetik veri | PROMPT seed=42, Nisan–Eylül 2026, yaklaşık 600 satış/250 gider ve tam iki kritik ürün şartını sabitliyor. fileciteturn0file0 | 45–75 dk | Ücretsiz | Tam iki kritik ürünü rastgeleliğe bırakmak | Faker+NumPy; sonunda kritik stokları deterministik olarak düzeltin ve fixture’ı kaydedin. SDV/LLM eklemeyin. | **A proje kararı** |
| Yayın | Vercel Hobby Git tabanlı deploy, preview deployment ve HTTPS sağlıyor; Render Free idle sonrası uyuyor; Neon Free compute idle iken scale-to-zero yapabiliyor. citeturn9search5turn9search1turn9search3 | 45–90 dk | Ücretsiz katmanlar mevcut | Aynı anda Vercel + Render + Neon cold path | Mevcut karar doğru; **demo öncesi warm-up script** ekleyin. | **A** |
| AI coding | Codex AGENTS.md kullanıyor; Copilot CLI de AGENTS.md yükleyebiliyor; Cursor CLI AGENTS.md’yi okuyabiliyor. Gemini CLI’nin standart context dosyası GEMINI.md olsa da `context.fileName` ile AGENTS.md eklenebiliyor. citeturn11search0turn11search1turn11search15turn12search4 | 20–30 dk | Araç planına bağlı | Her aracın farklı talimat dosyası | **Tek gerçek kaynak AGENTS.md**; gerekiyorsa araç-specific küçük köprü dosyaları. | **A** |

**Text-to-SQL için kesin öneri:** Vanna.ai, LangChain SQL agent veya LlamaIndex gibi bir katmanı **Geliştirme Günü’ne sokmayın**. Buradaki ihtiyaç dinamik veri kataloğu, yüzlerce tablo veya karmaşık agent orchestration değil; bir PostgreSQL şeması, bilinen view’lar ve yaklaşık 15 jüri sorusu. SQLGlot’un AST kabiliyeti bu dar problemde koruma katmanına daha doğrudan uyuyor. citeturn0search1

Önerilen servis hattı:

`Türkçe soru → şema + birkaç örnek → LLM’den yapılandırılmış JSON → Pydantic doğrulama → SQLGlot AST → güvenlik kuralları → salt-okur bağlantı → sonuç → Türkçe özet`

Güvenlik sırası **tek katmanlı değil, defense-in-depth** olmalı:

| Kontrol | Uygulama |
|---|---|
| Yapılandırılmış çıktı | `SQLPlan(sql: str)` gibi Pydantic model |
| Statement kontrolü | Tek statement; SELECT/CTE dışını reddet |
| Nesne kontrolü | Yalnız `sales`, `expenses`, `products`, `suppliers`, `purchase_orders`, izin verilen view’lar |
| Sonuç sınırı | Liste sorgularına `LIMIT`; aggregate sorguda gerekmez |
| DB yetkisi | Ayrı salt-okur Postgres rolü; uygulama yazma rolünü LLM’e hiç verme |
| Zaman sınırı | Kısa `statement_timeout` |
| Şeffaflık | Üretilen SQL + sorgu zamanı + veri kaynağı UI’da gösterilsin |
| Hata politikası | Geçersiz SQL’de maksimum bir düzeltme denemesi; sonra kontrollü hata |
| Log | Soru, model, latency, SQL, validation result; gerçek hassas değerleri loglamama |

**15 soruluk eval** kesinlikle yapılmalı; bunun jüri karşılığı çok yüksek. Soruları beş kolay aggregate, üç tarih filtresi, üç join, iki boş/edge case ve iki saldırgan istek olarak dağıtın. “Beklenen SQL string’i” karşılaştırmak yerine **beklenen sonuç/rakam + izin verilen tablolar + herhangi bir yazma işlemi yapılmaması** kriterlerini kontrol edin. Bu, LLM modelini değiştirdiğinizde regresyonu ölçmenizi sağlar.

**LLM karşılaştırması, 13 Eylül 2026:**

| Model | Doğrulanmış fiyat | Güçlü yanı | OtoHesap kararı | Güven |
|---|---:|---|---|---|
| Claude Haiku 4.5 | $1 / milyon input, $5 / milyon output token. citeturn4search0 | Anthropic’in hız/maliyet odaklı Claude modeli | **Default**; SQL üretimi + kısa Türkçe özet | **A** |
| Claude Sonnet 4.6 | $3 / milyon input, $15 / milyon output. Şubat 2026’da yayımlandı. citeturn4search7 | Zor sorgularda kalite modu | Eval’da Haiku’nun kaçırdığı sorular için opsiyonel | **A** |
| Gemini 2.5 Flash | $0.30 / milyon metin input, $2.50 / milyon output; structured outputs destekliyor. citeturn5search1turn8view0 | Düşük maliyet ve büyük context | **Fallback** | **A** |
| GPT-5 mini | $0.25 / milyon input, $2 / milyon output; structured output desteği var, API ücretsiz katmanı desteklemiyor. citeturn3search1 | Fiyat olarak rekabetçi üçüncü sağlayıcı | **Bugün eklemeyin.** Adapter mimarisini üçüncü provider’a açık bırakın. | **A** |
| “Claude Sonnet 5” | Resmî Anthropic kaynaklarında bu araştırmada doğrulanamadı; Sonnet ailesinin doğrulanan güncel modeli 4.6, Opus 5 ise mevcut. citeturn4search7turn4search6 | — | Config’ten çıkarın veya doğrulanana kadar kullanmayın. | **X** |

Örnek bir finans sorusunun **2.000 input + 400 output token** kullandığını varsayarsak, yalnız token fiyatıyla yaklaşık maliyet Haiku 4.5’te **$0,004/soru**, Gemini 2.5 Flash’ta **$0,0016/soru**, GPT-5 mini’de **$0,0013/soru** olur. Bunlar gözlemlenmiş kullanım değil, yukarıdaki resmî fiyatlardan türetilmiş birim ekonomi senaryosudur. citeturn4search0turn8view0turn3search1

Dolayısıyla 1.000 benzer sorgu yaklaşık **$4 / $1,60 / $1,30** token maliyeti demektir. OtoHesap’ın erken aşamasında LLM faturası muhtemelen ana maliyet sürücüsü olmayacaktır; asıl ürünleşme maliyeti entegrasyon, destek, güvenlik ve operasyon olacaktır. Bu son cümle iş modeli çıkarımıdır.

**Gemini Free Tier için önemli KVKK notu:** Google’ın güncel fiyatlandırma sayfası ücretsiz katmanda içeriğin ürünleri iyileştirmek amacıyla kullanılabileceğini, ücretli katmanda ise bunun yapılmadığını belirtiyor. Dolayısıyla ücretsiz Gemini kotası sentetik hackathon verisi için cazip olsa da gerçek KOBİ verisinin üretim kullanımında yalnız “ücretsiz” olduğu için tercih edilmemeli. citeturn8view0

**Bildirim kararı:** Telegram bugün en doğru seçim. Twilio’nun WhatsApp Sandbox’ı test amaçlı; alıcının sandbox’a katılması gerekiyor, business-initiated mesajlar pre-approved template ile sınırlı ve trial hesapta 100 WhatsApp mesajı bulunuyor. citeturn13search1 Resend ise anında production erişimi veriyor ve Free planda ayda 3.000, günde 100 transactional e-posta sağlıyor; bu nedenle Telegram’ın yanında sessiz ikinci kanal/fallback olarak haftalık sprintte değerlendirilebilir. citeturn14search0turn14search4

**Deployment kararı:** Vercel Hobby tarafında Git/CI-CD/HTTPS iyi; ancak Hobby cron en fazla günlük çalışacak şekilde ve düşük zaman hassasiyetinde, bu nedenle 10 dakikalık stok kontrolünü Vercel Cron’a taşımak uygun değil. citeturn9search5turn9search12 Render Free servisinin 15 dakika idle sonrası uyuması ise APScheduler için doğrudan risk. citeturn9search1 Demo günü çözümü yeni altyapı kurmak değil: `/health`, gerçek DB sorgusu ve LLM’e küçük warm-up; ardından manuel stok kontrol butonu.

**Paralel geliştirme düzeni:**

| Kişi | Sahip olduğu alan | Dokunmaması gereken kritik alan |
|---|---|---|
| Web | `apps/web`, UI, API client | DB modelleri/migration |
| API + AI | FastAPI core, `/assistant`, SQL validation | Dashboard CSS, Telegram |
| Agent | purchase order service, scheduler, Telegram | Assistant prompt/SQL |
| Data + analytics | seed, fixture, KPI sorguları, demo/pitch | Ortak API route refactor |

`schema`, `.env.example`, shared DTO ve migration değişikliklerini tek kişi merge etsin. Gün başında veri modelini dondurmak, dört AI aracının birbirinin dosyalarını “iyileştirmeye” çalışmasından daha değerlidir.

## Pazar, rakipler ve entegrasyon fırsatı

Türkiye pazarı OtoHesap için yeterince büyük; ancak sunumda **“KOBİ’ler dijitalleşmemiş”** gibi doğrulanmamış genellemeler kullanılmamalı. TÜİK’in 24 Aralık 2025’te yayımladığı 2024 verisi tek başına problem slaydını taşıyacak kadar güçlüdür: 3,928 milyon KOBİ, işletmelerin %99,6’sı, istihdamın %68,5’i, cironun %44,1’i. KOBİ’lerin %35,1’i toptan/perakende ticaret ve motorlu taşıt onarımı alanında faaliyet gösteriyor; bu OtoHesap’ın stok/ticaret hikâyesiyle doğrudan uyumlu. citeturn15search7

| Pazar göstergesi | Bulgu | Sunumda kullanım | Güven |
|---|---|---|---|
| KOBİ sayısı | 2024: **3,928 milyon** girişim. citeturn15search7 | “Türkiye’de yaklaşık 3,9 milyon KOBİ…” | **A** |
| İşletme payı | Toplam girişimlerin **%99,6’sı**. citeturn15search7 | Problemin niş değil yatay olduğunu gösterir. | **A** |
| İstihdam | **%68,5**. citeturn15search7 | Ekonomik önem. | **A** |
| Ciro | **%44,1**. citeturn15search7 | Finans/stok verimliliğinin ekonomik önemini destekler. | **A** |
| Ticaret sektörü | KOBİ’lerin **%35,1’i** toptan/perakende ticaret ve ilgili onarım faaliyetinde. citeturn15search7 | Stok yönetimi personasını destekler. | **A** |
| Ön muhasebe yazılımı kullanım oranı | Savunulabilir güncel ulusal oran bu araştırmada doğrulanamadı. | **Slayta sayı koymayın.** | **X** |
| Finans/stok takibine haftalık ayrılan zaman | Türkiye KOBİ’leri için güvenilir ulusal çalışma doğrulanamadı. | “Haftada X saat” iddiası kullanmayın. | **X** |
| KOBİ AI benimseme oranı | Türkiye geneli için bu araştırmada sunumda kullanılacak resmî 2025–2026 oranı doğrulanamadı. | “KOBİ’lerin %X’i AI kullanıyor” demeyin. | **X** |

KOSGEB’in güncel programları, dijitalleşmenin kamu politikası açısından gerçek bir gündem olduğunu gösteriyor. KOBİ Dijital Dönüşüm Destek Programı imalat sektöründeki küçük/orta işletmeler için yazılım ve donanım yatırımlarını da kapsıyor; program sayfası 1–20 milyon TL kredi aralığı ve finansman desteğini listeliyor. citeturn15search10 Ayrıca Ağustos 2026’da açılan Kapasite Geliştirme programı yazılım giderlerini açık biçimde desteklenen kalemler arasında sayıyor. citeturn15search0 OtoHesap sunumunda “her KOBİ bu destekten yararlanabilir” denmemeli; programların sektör ve başvuru şartları var.

**e-Belge açısından “neden şimdi” daha da güçlü.** GİB’in İstanbul sayfasına göre 2026 fatura düzenleme sınırı **12.000 TL**. citeturn16search2 2025 hesap döneminde genel brüt satış/gayrisafi iş hasılatı 3 milyon TL ve üzerindeki mükellefler ile e-ticaret gibi belirli alanlarda 500 bin TL eşiğini aşanlar için 1 Temmuz 2026 geçişi, birden fazla güncel sektör kaynağında 509 sayılı Tebliğ çerçevesinde aynı şekilde aktarılıyor. Bu rakam için doğrudan güncel konsolide GİB metni bu araştırma çıktısında yakalanmadığından güven etiketi **B** tutulmalıdır. citeturn18search0turn18search6

**Rakiplerin doğrulanabilen mevcut tablosu:**

| Ürün | Doğrulanan güçlü alanlar | 2026 fiyat / bilgi | Doğal dil + otonom tedarik | OtoHesap için ders | Güven |
|---|---|---|---|---|---|
| Paraşüt | e-Fatura/e-Arşiv, cari, stok, çoklu depo, banka entegrasyonu, e-ticaret uyumu. citeturn22search0 | Yıllık planda sayfada **940 TL + KDV/ay**, toplam 11.280 TL + KDV gösteriliyor. citeturn22search0turn22search8 | Güncel incelenen resmî sayfada OtoHesap benzeri NL-to-SQL + HITL tedarik ajanı doğrulanmadı; yokluğu kanıtlanmış değildir. | Uyumluluk tarafında yarışmak yerine intelligence/action layer. | **A / X AI** |
| Logo İşbaşı | Stok, banka takibi, 17 banka entegrasyonu, e-ticaret, e-belge, çek giriş/çıkış, POS. citeturn22search4 | İncelenen resmî sayfada 342 TL + KDV/ay bilgisi var; sayfanın güncellik tarihi net olmadığı için deck fiyat karşılaştırmasında dikkatli olunmalı. | NL-to-SQL/tedarik ajanı bu araştırmada doğrulanmadı. | Özellik listesinden çok kullanıcı etkileşimi farkı yaratın. | **A özellik / C fiyat güncellik** |
| Bizim Hesap | e-Fatura/e-Arşiv, dijital arşiv, raporlama, muhasebeci aktarımı doğrulandı. citeturn22search3 | e-kontör paketleri resmî sayfada yayımlanıyor. citeturn22search3 | OtoHesap benzeri ajan özelliği doğrulanmadı. | Mali müşavir workflow’u ileride önemli. | **A / X AI** |
| Mikro Jump | Bu araştırma turunda güncel resmî fiyat/feature matrisi yeterli derinlikte doğrulanamadı. | — | — | Jüride kesin karşılaştırma yapmayın. | **X** |
| Kolay Bi' | Güncel resmî matris bu turda doğrulanamadı. | — | — | Kesin AI iddiası kullanmayın. | **X** |
| Zirve | Güncel resmî matris bu turda doğrulanamadı. | — | — | Yol haritası araştırmasına bırakın. | **X** |
| Luca | Güncel resmî matris bu turda doğrulanamadı. | — | — | Mali müşavir kanalında ayrıca incelenmeli. | **X** |
| Odoo TR | Türkiye’ye özgü güncel paket/yerelleştirme matrisi bu turda doğrulanamadı. | — | — | Global ERP ile birebir karşılaştırmayın. | **X** |
| QuickBooks / Xero / Zoho Books | Türkiye’ye özgü mevzuat/entegrasyon uygunluğu bu araştırmada tam doğrulanmadı. | — | — | Türkiye’de ana benchmark olarak değil, ürün UX benchmark’ı olarak değerlendirin. | **X** |

Bu tablo kritik bir sunum stratejisi doğuruyor: **“Rakiplerde AI yok” demeyin.** Bu çok kolay çürütülebilecek bir iddia. Onun yerine:

> **“Mevcut ön muhasebe ürünlerinin güçlü olduğu e-belge, banka ve stok katmanlarını değiştirmeye çalışmıyoruz. OtoHesap bu verilerin üzerinde, doğal dille soru sorulan ve insan onayıyla aksiyona geçen bir karar katmanı olmayı hedefliyor.”**

Bu konumlama, resmî rakip sayfalarında görülen güçlü entegrasyon portföyüyle uyumludur. citeturn22search0turn22search4

Üç alternatif “X gibi ama Y” cümlesi:

| Alternatif | Konumlama |
|---|---|
| **En güvenli** | “Paraşüt ve İşbaşı gibi KOBİ operasyonlarını tek yerde topluyor; ama rapor menülerini Türkçe soru ve onaylı aksiyona dönüştürüyor.” |
| **En kurumsal** | “Ön muhasebe sisteminin yerine geçen değil, onun üzerinde çalışan AI karar ve otomasyon katmanı.” |
| **En vurucu** | “Dashboard değil: işletmenin verisini açıklayan, riski fark eden ve bir sonraki işi insan onayıyla hazırlayan finans operasyon asistanı.” |

**Trendyol açısı güçlü ve somut.** Trendyol’un resmî kurumsal sayfası yaklaşık **250.000 satıcıyı** ve 40 milyondan fazla müşteriyi bildiriyor; Türkçe “Hakkımızda” sayfası da 250.000’den fazla satıcının dijitalleşmesine destek verildiğini söylüyor. citeturn20search1turn20search3 Ancak bu satıcıların tam olarak kaçının KOBİ olduğu için güncel resmî oran bulunmadı; **“250 bin KOBİ satıcı” demeyin.**

Trendyol’un resmî Marketplace API dokümanında satıcının sipariş paketlerini çekebildiği `orders` servisi doğrulandı; ürün entegrasyon servisleri de mevcut. citeturn20search6turn20search10 Ayrıca buybox bilgisi için production ve stage endpoint’leri yayımlanmış durumda. citeturn20search4 En kritik güncel bilgi ise Product V1’in **15 Eylül 2026’da kapanacak olmasıdır**; roadmap doğrudan V2 ile başlamalı. citeturn20search10

**Jüriye anlatılacak Trendyol hikâyesi:**

> “Bugün satışları sentetik veriyle gösteriyoruz. Bir sonraki adımımız Trendyol Marketplace sipariş akışını OtoHesap’a bağlamak. Satış geldikçe finans ve stok görünümü güncellenecek; stok kritik seviyeye indiğinde sistem kullanıcı adına sipariş vermeyecek, önce tedarik taslağını hazırlayıp onay isteyecek.”

Bu cümle API’nin doğrulanmış sipariş yönünü kullanır, henüz doğrulanmamış stok/iade endpoint ayrıntılarını olduğundan fazla vaat etmez. Trendyol stok ve iade API’lerinin kesin endpoint/onboarding koşulları bu araştırma turunda tamamlanmadığından **X** kabul edilmelidir.

**Entegrasyon öncelik matrisi:**

| Sıra | Özellik | Demo etkisi | Efor | Ufuk | Karar |
|---|---|---:|---:|---|---|
| Birinci | Trendyol **read-only sipariş importu** | 5/5 | Orta | 1 hafta–1 ay | İlk gerçek entegrasyon; V2 dokümanlarıyla başlanmalı. citeturn20search6turn20search10 |
| İkinci | e-Fatura/e-Arşiv özel entegratör bağlantısı | 5/5 | Yüksek | 1 ay | KOBİ ürünü için stratejik; doğrudan GİB entegrasyonunu hackathon kapsamına sokmayın. |
| Üçüncü | Çoklu kullanıcı + roller | 3/5 | Düşük/orta | 1 hafta | SaaS’a geçiş için pazaryerinden bile daha temel. |
| Dördüncü | Mali müşavir erişimi | 4/5 | Orta | 1 ay | Rakiplerde müşavir akışlarının varlığı bunun pazar beklentisi olduğunu gösteriyor. citeturn22search3turn22search4 |
| Beşinci | Açık bankacılık partneri | 5/5 | Yüksek | 3 ay | Doğrudan banka banka entegrasyon yerine lisanslı ekosistem ortağı. |
| Altıncı | Hepsiburada | 4/5 | Orta | 1–3 ay | API ayrıntıları bu koşuda resmî kaynaktan tamamlanmadı: **X** |
| Yedinci | N11 | 4/5 | Orta | 1–3 ay | API ayrıntıları bu koşuda resmî kaynaktan tamamlanmadı: **X** |
| Sekizinci | iyzico / PayTR tahsilat | 3/5 | Orta | 1–3 ay | Satış/tahsilat senaryosu netleşince. API ticari koşulları ayrıca doğrulanmalı: **X** |

Açık bankacılık yol haritası özellikle güçlü. TCMB, 17 Mart 2026 itibarıyla ÖHVPS 2.0’ın devreye alındığını; ekosistemin **16,4 milyon kullanıcı, günlük ortalama 12,3 milyon işlem ve 53 katılımcıya** ulaştığını bildiriyor. Yeni sürüm kart bilgileri ve hareketleri ile ileri tarihli/düzenli ödeme emri işlevlerini genişletiyor. citeturn23search0 Ancak TCMB’nin 2025 Faaliyet Raporu, ödeme/e-para kuruluşlarının Yetkili Ödeme Hizmeti Sağlayıcısı rolü için teknik sertifikasyonun yanında gerekli faaliyet izinlerine tabi olduğunu açıkça anlatıyor. citeturn23search8

Bu nedenle OtoHesap’ın hikâyesi **“bankalara doğrudan bağlanacağız” değil, “lisanslı açık bankacılık sağlayıcısı üzerinden hesap hareketlerini konsolide edeceğiz”** olmalı.

## Ölçekleme, Azure, KVKK ve iş modeli

İlk ölçekleme kararında **schema-per-tenant yerine `tenant_id` + PostgreSQL Row-Level Security yaklaşımı** daha uygun. OtoHesap’ın 10.000 işletmeye kadar hedeflenen SaaS hikâyesinde her müşteri için schema/migration yönetmek yerine ortak şema, her iş tablosunda `tenant_id`, uygulama bağlamında tenant ve RLS politikaları daha yönetilebilir bir başlangıç verir. Bu mimari bir araştırma verisi değil, OtoHesap’ın veri modeli ve hedef ölçeği için mimari öneridir. fileciteturn0file0turn0file1

Önerilen sıralama:

`single tenant demo → user/org modeli → tenant_id → RLS → audit log → tenant bazlı quota → enterprise isolation ihtiyacı doğarsa ayrı DB`

Kimlik tarafında Development Day’de hiçbir provider migration’ına girilmemeli. Bir haftalık sprintte gerçek kullanıcı/organizasyon modeli kurulabilir; Microsoft kurumsal satış yolu netleştiğinde Entra External ID değerlendirmek anlamlı hale gelir. Mevcut demo için auth çözümü seçmek, dört ana yeteneğin çalışmasından daha düşük öncelikli.

**Azure geçiş yolu:**

| Katman | Bugün | Azure ürünleşme hedefi | Neden |
|---|---|---|---|
| Web | Vercel | Vercel kalabilir veya Azure frontend hosting değerlendirilebilir | Web katmanını sırf Azure için taşımak zorunlu değil |
| API | Render | **Azure Container Apps** | Containerized API, scale-to-zero ve yönetilen servis yolu |
| DB | Neon PostgreSQL | **Azure Database for PostgreSQL Flexible Server** | PostgreSQL modelini korur |
| AI | Anthropic + Gemini adapter | **Azure AI Foundry / Azure OpenAI** veya model-agnostic adapter | Provider bağımlılığını azaltan mevcut adapter korunur |
| Identity | Demo düzeyi | **Microsoft Entra External ID** | Kurumsal kimlik ve Microsoft hikâyesi |
| Secrets/ops | Env | Key Vault + Azure Monitor/Application Insights | Ürünleşme / audit |
| Marketplace | Yok | Microsoft Marketplace SaaS offer | Distribution/co-sell yolu |

Azure Container Apps’in resmî fiyatlandırması abonelik başına aylık belirli ücretsiz vCPU/GiB-saniye ve 2 milyon request grant’i içeriyor ve scale-to-zero destekliyor; bu nedenle sonraki aşama pilot için teknik olarak makul. citeturn10search1 **Fakat Development Day’de Render’ı Azure’a taşımak yanlış optimizasyondur.**

Prompttaki Azure for Students endişesi için araştırma önemli bir düzeltme getiriyor. Microsoft’un güncel Azure for Students sayfası **$100 kredi, tam ürün kataloğuna krediler ölçüsünde erişim ve Azure OpenAI’ye erişimi** açıkça söylüyor. citeturn21search2turn21search9 Dolayısıyla jüri önünde “Azure OpenAI öğrenci hesaplarında çalışmıyor” denmemeli. Daha doğru cümle:

> “Azure for Students bugün Azure OpenAI erişimini program kapsamında listeliyor; ancak kullandığımız modelin bölge ve abonelik kotasını deploy etmeden önce doğrulamamız gerekiyor.”

İkinci kısmın sizin bireysel subscription durumunuz araştırmada doğrulanmadığı için **X**.

**Microsoft ISV yolu gerçek ve OtoHesap’la uyumlu.** ISV Success’ın güncel uygunluk şartları arasında B2B software projesi, Microsoft Cloud üzerinde geliştirme/entegrasyon, dış müşterilere tekrarlı satış amacı, en az bir atanmış geliştirici, geliştirmeye üç ay içinde başlayıp 12 ay içinde bitirme ve Microsoft Marketplace’e yayınlama taahhüdü bulunuyor. citeturn23search13

Core Benefits tarafında Microsoft **$5.000 yıllık Azure kredisi**, Azure Standard Support, geliştirme lisansları ve teknik danışmanlık avantajlarını listeliyor. citeturn23search1turn23search11 ISV Success FAQ, yeni Microsoft Cloud B2B yazılım şirketleri için ilk yıl faydalarının ücretsiz sağlanabildiğini belirtiyor. citeturn23search3 Bu, **bugünkü öğrenci projesinin otomatik olarak programa kabul edildiği** anlamına gelmez; şirketleşme/partner hesabı ve uygunluk aşaması gerekir.

Co-sell-ready için de yol nettir: aktif PartnerID ve Marketplace hesabı, tamamlanmış business profile, Marketplace’te canlı offer, uygun co-sell bölgelerinde satış kontağı ve gerekli solution belgeleri. citeturn21search12 Dolayısıyla 12 aylık hedef “Microsoft bize ortak olsun” değil:

`ürünleşme → şirket/partner yapısı → Azure pilot → Marketplace offer → müşteri referansı → co-sell readiness`

**Pargesoft açısı güçlü biçimde doğrulandı.** Pargesoft’un kendi sitesi şirketin Microsoft Solutions Partner unvanlarını **Data & AI (Azure), Business Applications, Modern Work ve Digital & App Innovation (Azure)** alanlarında ve Tier 1 Direct CSP statüsünü listeliyor; ayrıca Dynamics 365, Azure, Power Platform ve AI projelerini vurguluyor. citeturn21search0turn21search5

Pargesoft temsilcisine şu dille konuşmak doğru:

> “Bugün managed servislerle doğruladığımız use case’i, ikinci aşamada Azure üzerinde tenant isolation, kurumsal identity, observability ve govern edilmiş AI katmanıyla referans mimariye dönüştürmek istiyoruz.”

Bu cümle onların “ürün + kurumsal teslimat” diline çok daha yakındır.

**Nephos AI için daha temkinli olunmalı.** Bu araştırmada birincil web sitesi yerine erişilebilir LinkedIn şirket profili; Microsoft Azure, AI/ML ve generative AI odağını bildiriyor. Ancak profil metnindeki kuruluş yılı ifadesi ile metadata arasında tutarsızlık var ve belirli güncel Microsoft Solutions Partner designation’ı birincil kaynaktan doğrulanamadı. citeturn22search7 Dolayısıyla Nephos temsilcisinin önünde “siz Microsoft’un X statüsündesiniz” şeklinde ezber bir cümle kurmayın. Güven etiketi **C**; partner designation **X**.

**KVKK, ürünleşmenin gerçek mimari gereksinimi.** 6698 sayılı Kanun’un 9. maddesindeki yeni yurt dışı aktarım rejimi 1 Haziran 2024’te yürürlüğe girdi. KVKK, standart sözleşmeleri uygun güvence yöntemlerinden biri olarak tanımlıyor; standart sözleşme imzalandığında beş iş günü içinde Kuruma bildirim gerekiyor. citeturn19search2turn19search3 10 Temmuz 2024 tarihli Yönetmelik ve dört farklı taraf rolü için standart sözleşme metinleri de Kurum tarafından yayımlandı. citeturn19search0turn19search4

OtoHesap için güvenlik/KVKK tasarımı:

| Durum | Politika |
|---|---|
| Demo | Sadece sentetik veri. En güvenli ve en kolay savunulabilir durum. |
| SQL oluşturma | Mümkün olduğunda LLM’e **DB satırlarını değil şema + soru + örnekler** gönderin. |
| Sonucu açıklama | Ham müşteri/tedarikçi isimleri yerine aggregate sonuç veya gerekli minimum alan. |
| Gerçek kişisel veri | Hangi sağlayıcıya/hangi ülkeye veri gittiğini veri envanterinde tutun. |
| Yurt dışı LLM | KVKK m.9 aktarım mekanizmasını, sağlayıcı sözleşmesini ve bildirim gerekliliklerini hukuk danışmanıyla değerlendirin. citeturn19search2turn19search3 |
| Log | Prompt/output/log’da gereksiz kişisel veri tutmayın. |
| AI izinleri | DB rolü salt-okur; agent siparişi yalnız taslak oluşturur; dış iletişim insan onayından sonra. |
| Denetlenebilirlik | SQL, timestamp, kaynak ve approval audit kaydı saklayın. |

Buradaki kritik pitch şudur:

> **“Biz AI’a veritabanının anahtarını vermiyoruz.”**

Asistan ayrı read-only kullanıcıyla sadece sorguluyor; tedarik ajanı ise kendi başına sipariş vermiyor, taslak oluşturup insan onayı bekliyor. Bu mimari doğrudan güncellenmiş proje brief’inde tanımlanmış durumda. fileciteturn0file0

**İş modeli:** Rakip fiyat çıpası olarak en temiz güncel veri Paraşüt’te yıllık abonelikte **940 TL + KDV/ay**. citeturn22search0turn22search8 OtoHesap’ın henüz üretim maliyeti, support load’u ve entegrasyon maliyeti ölçülmediği için bugünden “nihai fiyatımız 499 TL” demek doğru olmaz.

Daha savunulabilir hipotez:

| Paket | Fiyat hipotezi | İçerik | Statü |
|---|---:|---|---|
| Demo / Free | 0 TL | Sentetik/demo veya sınırlı kayıt | Hipotez |
| Başlangıç | 490–690 TL/ay | Finans + stok + sınırlı AI sorusu | Hipotez |
| Pro | 890–1.190 TL/ay | AI + agent + ekip rolleri | Hipotez |
| Commerce | 1.490 TL+/ay | Pazaryeri/e-belge entegrasyonları | Hipotez |

Bunlar **pazar fiyatı olarak sunulmamalı**; Paraşüt’ün 940 TL/ay çıpası etrafında oluşturulmuş test edilecek fiyat hipotezleridir. citeturn22search0

LLM açısından ise soru başına birkaç ondalık cent seviyesindeki senaryolar, 1.000 soruda yaklaşık $1,30–$4 token gideri oluşturuyor. citeturn4search0turn8view0turn3search1 Dolayısıyla ilk pricing görüşmesinde “AI çok pahalı” varsayımına değil, **support, integrations, compliance ve reliability** maliyetine odaklanın.

## Yol haritası ve demo güvenliği

README’deki ana kural burada korunmalı: araştırma sonucu ne kadar heyecan verici olursa olsun **Geliştirme Günü kapsamı büyümez**. fileciteturn0file2

| Boyut | **1 gün** | **1 hafta** | **1 ay** | **3 ay** | **12 ay** |
|---|---|---|---|---|---|
| Özellik | Dashboard + CRUD + Text-to-SQL + stok agentı + approval + Telegram + CSV | 15 soruluk eval, auth/rol temeli, audit, demo hardening, Trendyol adapter prototipi | Multi-tenant, Trendyol gerçek entegrasyon, e-belge PoC, mali müşavir görünümü | Lisanslı açık bankacılık partneri, observability, Azure pilot | Marketplace ürünleşme, daha fazla pazar yeri, co-sell hazırlığı |
| Teknoloji | Sabit mevcut stack. fileciteturn0file0 | Aynı stack; ek servis minimum | tenant_id + RLS, entegrasyon adapter’ları | Azure Container Apps/PostgreSQL/Foundry yolu | Marketplace/Entra/enterprise ops |
| Tahmini toplam efor | 28–40 kişi-saat | +40–60 kişi-saat | +100–160 kişi-saat | +250–400 kişi-saat | Ürün ekibine göre değişir |
| Ana bağımlılık | API key, Neon, Render, Vercel, Telegram | Seller credential / test tenant | Entegratör anlaşmaları | Lisanslı açık bankacılık partneri | Şirketleşme, müşteriler, Microsoft partner süreçleri |
| Ana risk | Demo entegrasyonu | Scope creep | KVKK + external API | Operasyon/güvenilirlik | GTM ve support |
| “Vay” etkisi | **5/5** | **5/5** | **5/5** | **4/5** | **5/5** |

Eforlar dış kaynaklardan alınmış endüstri normları değil, dört kişilik öğrenci ekibinin tanımlı stack’i için **X/planlama tahminidir**.

**Development Day’de yaklaşık iş bütçesi:** dört kişi × 12 saat = teorik 48 kişi-saat. Bunun tamamı feature geliştirmeye gitmez; merge, deployment, yemek, hata ayıklama ve prova payı gerekir. Bu nedenle 28–40 kişi-saatlik planned work makul, kalan süre entegrasyon tamponudur.

En yüksek demo riskleri:

| Risk | Neden kritik | Önlem | Güven |
|---|---|---|---|
| Render uyku | 15 dk idle sonrası free instance spin-down; yeniden başlatma yaklaşık bir dakika sürebilir. citeturn9search1 | Demo öncesi `/health` çağır; DB ve API’yi warm tut. | **A** |
| Scheduler durmuş görünür | Render process uyursa in-process APScheduler da fiilen çalışamaz. Bu, hosting davranışından yapılan çıkarımdır. citeturn9search1 | UI’da **“Şimdi kontrol et”** butonu; scheduler yine arka planda kalsın. | **A→çıkarım** |
| Neon scale-to-zero | Free compute idle durumda scale-to-zero davranışı gösteriyor. citeturn9search3turn9search14 | İlk demo öncesi gerçek `SELECT 1`/health query. | **A** |
| LLM kota/timeout | API bağımlılığı | 8–10 altın soruyu prova et; provider adapter fallback; 8–12 sn timeout. |
| SQL halüsinasyonu | Yanlış tablo/kolon/tehlikeli statement | Pydantic + SQLGlot + whitelist + read-only DB + timeout. citeturn0search1 |
| Vercel env eksik | Frontend API’ye erişemez | Prod env’i gün ortasında sabitle; demo öncesi incognito test. |
| CORS | Vercel origin değişebilir | Demo production domain’ini explicit allow et; preview URL’ye güvenme. |
| Zaman dilimi | Tarih filtrelerinde gün kayması | DB timestamp yaklaşımını sabitle; UI’da Europe/Istanbul göster. |
| Türkçe karakter | “İ/i/ı/I” gibi case problemleri | SQL isimlerinde ASCII; doğal dil yalnız prompt katmanında; fixture UTF-8. |
| Recharts boş data | Grafikte crash/boş render | `data.length === 0` için EmptyState. |
| Telegram telefon | Chat ID/token hatası | Botla demo telefonundan önceden konuş; test mesajı gönder; token secret’ta. citeturn13search0 |
| Okul Wi‑Fi | Harici API’ler çalışmayabilir | Telefon hotspot’u hazır; ayrıca 30–60 sn kayıtlı fallback demo bulunsun. |
| Trendyol V1 | 15 Eylül 2026’da kapanıyor. citeturn20search10 | Haftalık sprintte yalnız V2. | **A** |

**Demo akışı beş dakika içinde şöyle olmalı:**

`Dashboard 30 sn → kayıt ekle 30 sn → Türkçe soru 60 sn → SQL’i göster 30 sn → kritik stok 30 sn → sipariş taslağı 40 sn → Onayla 20 sn → telefon Telegram bildirimi 20 sn → kapanış 20 sn`

Burada en yüksek “vay” anı son 60 saniyedir: **stok → taslak → insan onayı → gerçek telefonda mesaj**. Zaman kalmadığında daha fazla grafik yerine bu akışı sağlamlaştırın.

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

## Bugünkü nihai aksiyon listesi ve güven özeti

**Bugün yapılacak ilk işler:**

| Öncelik | İş | Tahmini süre | Başarı kriteri |
|---|---|---:|---|
| **P0** | Şema, API contract, branch ownership ve `.env.example` dondur | 25 dk | Dört kişi aynı veri modelini kullanıyor |
| **P0** | shadcn dashboard skeleton + beş route | 30–45 dk | Tüm ekranlar gezilebilir. citeturn0search0 |
| **P0** | PostgreSQL schema + seed=42 fixture | 45–60 dk | 20 ürün, ~600 satış, ~250 gider, **tam iki kritik stok** |
| **P0** | FastAPI session + CRUD + health | 60–90 dk | UI gerçek API’den kayıt okuyup yazıyor |
| **P0** | Analytics endpoints + CSV | 60–90 dk | KPI ve grafikler gerçek DB’den geliyor |
| **P0** | Text-to-SQL service + Pydantic + SQLGlot guard | 2–3 saat | Yasak SQL reddediliyor, SQL görünür. citeturn0search1 |
| **P0** | Purchase-order draft → approval state machine | 60–90 dk | Tam iki kritik üründe doğru taslak |
| **P0** | Telegram `sendMessage` | 20–30 dk | Onay sonrası gerçek telefonda mesaj. citeturn13search0 |
| **P0** | Vercel + Render + Neon prod deployment ve CI smoke test | 60–90 dk | Okul dışı cihazdan uçtan uca çalışıyor |
| **P0** | 15 soru eval + iki tam demo provası + warm-up script | 2–3 saat | Beş dakikalık demo üst üste iki kez hatasız |

İşler dört kişiye paralel dağıtılmalı; tabloda görünen sürelerin toplanması duvar-saati değildir.

**Yapmayın:**

| Zaman tuzağı | Neden |
|---|---|
| LangGraph/Microsoft Agent Framework’ü bugün entegre etmek | Tek approval akışı için gereksiz abstraction; bu frameworkler güçlü ama OtoHesap’ın bir günlük akışından daha geniş problemleri hedefliyor. citeturn2search0turn1search1 |
| Vanna/LangChain/LlamaIndex ile framework savaşı | Dar şema için custom service daha denetlenebilir |
| WhatsApp production onboarding | Demo değerine kıyasla onboarding/template riski yüksek; Twilio Sandbox da test odaklı. citeturn13search1 |
| Azure migration | Azure roadmap doğru, bugün stack değiştirmek yanlış |
| Trendyol entegrasyonunu son dakika yapmak | Credential/onboarding ve API değişimi riski; ayrıca V1, 15 Eylül’de kapanıyor. citeturn20search10 |
| e-Fatura “gerçek entegrasyonu” | Mevzuat + özel entegratör + sertifika süreçleri demo kapsamının dışında |
| Çok kiracılık | Demo tek tenant kalmalı |
| UI pixel perfection | Agent + assistant reliability daha değerli |
| 30 farklı AI sorusu | 15 golden eval yeterli; kalite > kapsam |
| Son iki saate deployment bırakmak | Render/Neon/Vercel/env sorunları demo başlamadan çözülmeli. citeturn9search1turn9search3 |

**Jüriye söylenecek beş teknik cümle:**

1. **“LLM doğrudan veritabanına yetkili değil; oluşturduğu SQL doğrulanıyor ve ayrı salt-okur rolüyle çalışıyor.”**
2. **“Agent otonom olarak ödeme veya sipariş vermiyor; state machine insan onayı olmadan dış aksiyona geçemiyor.”**
3. **“Model sağlayıcısını adapter arkasına aldık; Haiku ana model, Gemini fallback, dolayısıyla iş mantığı provider’a bağımlı değil.”** Haiku 4.5 ve Gemini 2.5 Flash güncel resmî API modelleridir. citeturn4search0turn5search1
4. **“15 soruluk golden eval ile yalnız cevabı değil, sorgunun güvenlik kurallarına uyup uymadığını da ölçüyoruz.”**
5. **“Bugün managed servislerle hız kazandık; ürünleşmede tenant isolation, KVKK transfer mekanizması, observability ve Azure/Marketplace yolumuz ayrı bir ölçekleme katmanı.”** KVKK ve Marketplace süreçlerinin güncel resmî çerçeveleri bu ayrımı gerektiriyor. citeturn19search2turn23search13

**Promptlarda yapılması gereken son iki güncelleme:** Birincisi, PROMPT-1’de **“Claude Sonnet 5” → “Claude Sonnet 4.6 veya güncel doğrulanmış Sonnet modeli”** olarak değiştirilmesi; mevcut resmî kaynaklarda Sonnet 4.6 doğrulanmış, Sonnet 5 doğrulanmamıştır. citeturn4search7 İkincisi, Trendyol roadmap metnine **“Product V2 kullan; Product V1 15 Eylül 2026’da kapanıyor”** uyarısının eklenmesidir. citeturn20search10 Azure for Students notu da “Azure OpenAI destek dışı olabilir” yerine “program Azure OpenAI erişimini listeliyor; abonelik/bölge/model kotasını deploy öncesi doğrula” şeklinde güncellenmelidir. citeturn21search2turn21search9

**En savunulabilir tek cümlelik ürün stratejisi:**

> **OtoHesap, Paraşüt veya Logo’nun daha küçük bir kopyası değil; KOBİ’nin finans, stok ve gelecekte pazaryeri/banka/e-belge verisinin üzerinde çalışan, şeffaf sorgu üreten ve kritik işlerde insandan onay alan AI karar katmanıdır.**

Bu konum, doğrulanan KOBİ pazar büyüklüğüne, yerleşik rakiplerin güçlü operasyon özelliklerine, Trendyol’un geniş satıcı ekosistemine, gelişen açık bankacılık altyapısına ve Microsoft ürünleşme yoluna aynı anda oturuyor. citeturn15search7turn22search0turn22search4turn20search1turn23search0turn23search13

**Güven etiketi dağılımı — ana araştırma/bulgu satırları:** **A: 36 · B: 2 · C: 4 · D: 0 · X: 13.** X’lerin büyük bölümü hata değil, özellikle **Türkiye’de ön muhasebe kullanım oranı, KOBİ’lerin haftalık zaman kaybı, bazı rakiplerin 2026 AI özellikleri, Hepsiburada/N11 API ayrıntıları, Nephos’un güncel Microsoft designation’ı ve “Claude Sonnet 5”** gibi bu araştırmada savunulabilir birincil kaynakla doğrulanamayan noktaların bilinçli olarak sunumdan çıkarılmasıdır.