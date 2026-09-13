# Murat — yapılacaklar (13 Eyl 2026, sıralı)

## BUGÜN (toplantı sonrası, sırayla) — deneme sunumu yarın, 3 dk
- [ ] 1. GitHub: Kutay'ın erişim isteğini kabul et (repo → Settings → Collaborators) ya da `gh auth login && ./scripts/github-setup.sh` (TEAM dolu).
- [ ] 2. Gruba at: `docs/team/EKIP-KISA.md` (kısa brif) + repo linki; kişilere `docs/team/<isim>.md`.
- [ ] 3. Neon: proje + `docs/schema.sql` + RO rol; `DATABASE_URL`/`_RO` DM ile; `make seed` Neon'a.
- [ ] 4. LLM: Gemini veya Groq anahtarı (takımdan), `.env`; yerel Qwen istenirse sunucu laptopunda Ollama (`docs/team/BUGUN-PLAN.md`).
- [ ] 5. Notion: 3 dk akışı (`docs/sunum/3-dakika-akis.md` Notion sayfasında da var) → gruba link.
- [ ] 6. Video: Canva ile 90 sn, akış = 3-dakika-akis; ekran kaydı QuickTime (`make warmup` sonrası).
- [ ] 7. 22:00 kontrol toplantısı: canlı tur + sunucu kararı.
Aşağısı tam liste (16'sı için).


> Sıra önemli: 1–3 mesaj işi (15 dk), 4–8 hesap/anahtar işi (30 dk), 9–10 Claude'a dönüş. Anahtarları hiçbir sohbete (WhatsApp, Claude) yapıştırma; yalnız `.env` ve Render/Vercel paneline.

## A · Şimdi (15 dk)
- [ ] **1. Gruba mesaj at.** `docs/team/EKIP-BRIFI.md` dosyasını ve altındaki "WhatsApp'a kopyalanacak özet"i gönder + repo linki. Aynı mesajda üç soru: (a) herkesin GitHub kullanıcı adı, (b) Kutay'ın UI aracı (Next.js mi, başka mı), (c) Geliştirme Günü tarihi (öneri: 14 Eyl Pzt 09:00).
- [ ] **2. Kişiye özel kartları at.** Kutay → `docs/team/kutay.md`, Ömer → `docs/team/omer.md`, Yiğit → `docs/team/yigit.md`; yanına `AGENTS.md`. Cümle: "Kartındaki 'Nasıl başlarım' bloğunu uygula, AI'ına ilk mesajı at, 'hazırım' yaz."
- [ ] **3. GitHub'ı tamamla.** Kullanıcı adları gelince `scripts/github-setup.sh` içindeki `TEAM=( )` dizisini doldur, sonra:
  ```bash
  gh auth login && cd ~/code/Oto-Hesap && ./scripts/github-setup.sh
  ```
  (dal koruması, etiketler, açıklama, ekip daveti tek seferde.)

## B · Bu akşam (30 dk)
- [ ] **4. Neon.** neon.tech'te proje `otohesap` (bölge Frankfurt) → SQL editöründe `docs/schema.sql`'i çalıştır → dosyanın sonundaki yorumlu 6 satırla `otohesap_ro` rolünü aç → iki bağlantı dizesini kendi `.env`'ine yaz (`DATABASE_URL`, `DATABASE_URL_RO`) → ekibi Neon "Share project" ile e-postayla davet et.
- [ ] **5. LLM anahtarı.** console.anthropic.com → API key → `.env` `ANTHROPIC_API_KEY`, `LLM_PROVIDER=anthropic`. Kredi yoksa Gemini anahtarı yedek (`LLM_PROVIDER=gemini`), yalnız sentetik veriyle.
- [ ] **6. Telegram.** Ömer'den bot token + chat_id iste; `.env`'e `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID`; seed'deki Telegram kanallı tedarikçinin `contact_address`'ine chat_id (seed `TELEGRAM_CHAT_ID` yer tutucusu; `data/README.md`'de nasıl değiştirileceği yazacak).
- [ ] **7. Organizatör.** Katalogdaki OtoHesap girdisi eski → `AGENTS.md §1`'deki "OtoHesap nedir" paragrafını ve poster PDF'ini gönder; sunum sırasını sor (InsightAI bizden önce mi?).
- [ ] **8. Deneme sunumu ve final tarihi** netleştir (grupta sor).
- [ ] **8b. Render kararı (D18):** ücretsiz katmanda API 15 dk boşta uyur, zamanlayıcı da durur. Demo için yeterli ("Şimdi kontrol et" + warmup). Sürekli çalışsın istiyorsan Render'da 7 $/ay küçük instance; final öncesi karar ver.

## C · Claude'a dönüş (kararlar gelince tek mesaj)
- [ ] **9.** Şunları yaz: Geliştirme Günü / deneme / final tarihleri · Kutay'ın aracı · GitHub adları geldi mi · Neon açıldı mı · anahtar var mı (evet/hayır, anahtarın kendisi değil) · Telegram hazır mı. Ben AGENTS §11, DECISIONS D7, EKIP-BRIFI, Notion ve kartları güncellerim.
- [ ] **10.** İnşa bitince (bildiririm): `git pull`, `make setup && make seed && make api` + `make web`, demo senaryosunu bir kez sür, gördüğün eksikleri yaz.

## Güncellenecekler (kim, nerede)
| Ne | Nerede | Kim |
|----|--------|-----|
| Tarihler (Geliştirme Günü, deneme, final) | `AGENTS.md §11`, `docs/DECISIONS.md D7`, `docs/team/EKIP-BRIFI.md`, Notion, `docs/demo-senaryosu.md` | Sen karar → ben yazarım |
| Kutay'ın UI aracı | `AGENTS.md §3` web satırı, `docs/team/kutay.md` | Kutay yazar → ben |
| GitHub kullanıcı adları | `scripts/github-setup.sh` `TEAM` | Sen |
| Telegram chat_id | `.env`, seed'deki tedarikçi satırı | Sen + Ömer |
| Katalog girdisi | Organizatöre e-posta/WhatsApp | Sen |
| Görev kartları "bugün ne kaldı" (inşa sonrası) | `docs/team/*.md`, `specs/001-otohesap-mvp/tasks.md` | Ben |
| README (çalıştırma adımları, ekran görüntüleri) | `README.md` | Ben + Yiğit |
| Notion sayfası | tarih + kararlar + repo durumu | Ben |
