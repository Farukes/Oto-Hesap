# Bugün (13 Eyl Paz akşam) — deneme sunumu YARIN, 3 dakika, tek sunucu

> Toplantı (12:39) kararları: kapsam kısa ve mock kalır; herkes kendi dalında; Gemini/Groq ücretsiz anahtar; Nurullah hoca yerel model öneriyor; 22:00–23:00 kontrol toplantısı; Murat Notion akışı + Canva video; tek sunucu (Kutay güçlü aday). **Ürün `main`'de çalışır durumda** — bugün kod yazma günü değil, kurma ve prova günü.

## ZORUNLU (bu akşam, sırayla)
| # | İş | Kim | Süre | Nasıl |
|---|----|-----|------|-------|
| 1 | Depoyu çek, çalıştır, demo akışını bir kez sür | Herkes | 30 dk | `git clone … && ./scripts/setup.sh` → `.env` → `make seed && make api` + `make web` → `docs/sunum/3-dakika-akis.md` |
| 2 | Ortak veritabanı: Neon projesi + `docs/schema.sql` + salt-okur rol; URL'leri DM'le | Murat | 15 dk | Yerel Postgres'i olmayan Neon'u kullanır |
| 3 | LLM kararı + anahtar: Gemini **veya** Groq (5 dk) — yerel Qwen istenirse sunucu laptopuna Ollama (30 dk indirme) | Murat + sunucu | 5–30 dk | `.env`: `LLM_PROVIDER=gemini|groq|ollama`; demo çipleri LLM olmasa da çalışır (önbellek) |
| 4 | Telegram botu + chat_id → tedarikçi satırı → gerçek mesaj testi | Ömer | 20 dk | `data/README.md`'deki `UPDATE suppliers …`; `.env` `NOTIFY_DRY_RUN=false` |
| 5 | Sunucu laptopu: tam kurulum + 3 prova kronometreyle | Kutay (sunucu) | 45 dk | `make warmup` → akış → süre ≤ 2:50 |
| 6 | 3 dk akışı Notion'a + video (Canva, 90 sn, aynı akış) | Murat | 60 dk | `docs/sunum/3-dakika-akis.md` (Notion'da da var) |
| 7 | 22:00 kontrol toplantısı: canlı tur, sunucu kararı, açık sorular | Herkes | 30 dk | Blokaj varsa burada çözülür |

## EKSTRA (zaman kalırsa; 16'sı için)
- Vercel + Render + Neon canlı yayın (`render.yaml`; `scripts/warmup.sh` canlı adrese).
- `make eval` gerçek sağlayıcıyla 15 soru; sağlayıcı seçimi.
- Kutay'ın kendi UI çalışmasından parçalar (aynı `lib/api.ts` ile bağlanır).
- README ekran görüntüleri; 16'sı için slaytlar (`docs/sunum/pitch-paketi.md`).
- Öngörü kartı metinleri, boş durumlar, mobil cila.
- e-Fatura/e-İrsaliye: **yapılmaz**, yol haritasında (toplantıda da GİB/MERSİS gerekçesiyle kapatıldı).

## Yerel model mi, API mi? (kısa karar)
- **Yarın için:** Gemini veya Groq anahtarı; 5 dakikada hazır, laptop yorulmaz. Demo çipleri zaten önbellekten yanıtlanır; LLM yalnız özet cümlesi ve serbest soru için.
- **Hocanın önerisi için (16'sı):** sunucu laptopuna `brew install ollama && ollama pull qwen2.5:7b`, `.env` `LLM_PROVIDER=ollama`. M-serisi 16 GB'da 7B model 5–15 sn yanıt; sunumda "modelimiz yerelde çalışıyor" cümlesi. Adaptör hazır, kod değişmez.
- **Söylenecek cümle:** "Model sağlayıcı adaptör arkasında; yerel Qwen da bulut model de aynı sözleşmeyle çalışıyor; veri sentetik."

## Kısaltılmış kapsam (toplantıya göre)
Gelir-gider grafikleri ✅ · arama çubuğu Türkçe soru → SQL → yanıt ✅ · stok bitince otomatik mesaj (insan onaylı) ✅ · Öngörü kartları ✅ (bonus, kapatılabilir). Başka özellik eklenmez.
