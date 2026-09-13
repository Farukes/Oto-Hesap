# TeknoKampüs Arena 3. Grup kataloğu — diğer 9 proje bize ne söylüyor (13 Eyl 2026)

Kaynak: `katalog-3-grup.txt` (organizatör kataloğu, docx'ten çıkarıldı). Kataloğun 5. sırasındaki OtoHesap girdisi Kutay'ın ilk WhatsApp özeti; posterdeki "yapay zekâ destekli", dört yetenek ve insan onayı vurgusu yok → **organizatöre güncel özeti (`AGENTS.md §1`) gönderip katalog girdisini yenilemek** ilk aksiyon.

## Doğrudan bizi etkileyenler

| # | Proje | Ne yapıyor | Bizim için anlamı | Aksiyon |
|---|-------|-----------|-------------------|---------|
| 3 | **InsightAI** (Caner Tuzluca) | Şirket verisi üstünde doğal dil soru-cevap: RAG + Text-to-SQL + Analytics + Multi-Agent Orchestration | **En yakın rakip.** Jüri Text-to-SQL'i bizden önce (3. sırada) görecek; "sohbet kutusu" tek başına farklılaştırmaz | Sunumda önce **ajan + insan onayı + telefonda mesaj** anını öne al; asistanı "karar katmanının sorgulama yüzü" olarak anlat. KOBİ odağı, görünür SQL, salt-okur rol, 15 soruluk eval = somut farklar. Demo sırası bizde ise asistanı 2. değil 3. adımda göster |
| 10 | **MidRule ai** (Mehmet Alper Dinçerler) | LLM yalnız veriyi yapılandırır; hesap ve kredi kararı %100 deterministik Python kural motorunda ("Sembolik Doğrulayıcı") | Bizim ilkemizle birebir: sayılar LLM'den değil SQL'den gelir, sipariş kararı kuraldan | Slayt 5'e bir cümle: **"LLM yalnız sorguyu yazar; rakamı veritabanı, sipariş kararını kural motoru verir."** Jüri bu dili iki kez duyunca bizde de arar |
| 2 | **SafeGuard AI** (Utku Tokmak) | Deepfake risk skoru; şüpheli vakayı **insan denetimine (HITL)** yönlendirir, kararları denetlenebilir kaydeder | HITL + audit dili jüride tekrar edecek | Bizde HITL soyut kalmasın: onay tuşu + telefonda gerçek mesaj + `purchase_orders` iz kaydı ekranda görünsün |
| 9 | **AI Investigator** (Dönmez, Yağcı) | Sorulmadan problem/anomali keşfi, kök neden, karşıt kanıt, güven seviyesi | Bizim yol haritası için hazır fikir: **"sorulmadan uyarı"** (gider anomalisi, nakit akışı düşüşü, satış trendi) | 1 haftalık sprinte: panoda kural tabanlı 3 "Öngörü" kartı ("Reklam gideri geçen aya göre %40 arttı"); LLM yalnız cümleyi yazar. Finalde 1 saatlik iş, "vay" etkisi yüksek |
| 1 | **Co-Build AI** (Çakar, Alemdar) | vLLM + Llama 3.1 8B (GPU), LangGraph agentic RAG, Supabase pgvector, hibrit arama | Ağır altyapı; bizim "yönetilen servis + 1 gün" tercihimizin karşıt örneği | Jüri "neden kendi modeliniz yok" derse: "1 günde çalışan ürün; adaptör sayesinde model değişir". Supabase'i not al: Auth + Postgres + RLS tek pakette, çok kiracı adımında Neon'a alternatif |

## Dolaylı / ilgisiz
- 6 FeedbackAI (geri bildirim duygu/öncelik analizi), 7 Gözetken (IoT + Gemini + bildirim), 8 StyleBridge (VLM gardırop), 4 Dershanem AI (optik okuma, mobil): teknik kesişim yok. Gözetken'in "ham sayı yerine aksiyona dönük tavsiye" cümlesi bizim asistan özetiyle aynı fikir; kopya değil, dönemin dili.

## Sunum stratejisine yansıması
1. **Açılış cümlesi değişsin:** "Bir sohbet asistanı değil; KOBİ'nin verisini açıklayan ve bir sonraki işi insan onayıyla hazırlayan karar katmanı." (InsightAI'dan ayrışma.)
2. **Slayt 5'te üç katman:** LLM yalnız SQL yazar → veritabanı rakamı verir → kural motoru siparişi hazırlar → insan onaylar. (MidRule + SafeGuard dilini kendi lehimize.)
3. **Yol haritası slaydına "Öngörüler":** sorulmadan uyarı kartları (AI Investigator fikri, KOBİ ölçeğinde).
4. **Katalog girdisi:** organizatöre güncel özet + poster; sunum sırasını öğren (InsightAI bizden önce mi?).
