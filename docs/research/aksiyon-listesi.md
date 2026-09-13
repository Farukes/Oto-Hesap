# Geliştirme Günü — araştırmadan gelen aksiyon listesi ve yapmayın listesi

> Kaynak: docs/research/SONUC-chatgpt-2026-09-13.md. Süreler kişi başı tahmin, paralel dağıtılır. AGENTS.md §11 çizelgesi esastır; bu liste onun kontrol listesidir.

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

