# OtoHesap — kısa brif (WhatsApp'a)

**Ürün hazır ve `main`'de:** gelir-gider panosu + Türkçe soruyla veri (SQL görünür) + kritik stokta insan onaylı Telegram siparişi. Deneme sunumu **yarın, 3 dk, tek sunucu**. Bugün iş: kur, çalıştır, prova.

**Herkes bu akşam (30 dk):**
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh      # .env oluşur: DATABASE_URL (Murat'tan Neon), LLM_PROVIDER, anahtar
make seed && make api   # http://localhost:8000/docs
make web                # ayrı terminal → http://localhost:3000
```
Sonra `docs/sunum/3-dakika-akis.md`'yi bir kez sür. Sorun → gruba yaz.

**Kim ne:** Kutay = sunucu laptopu kurulum + 3 prova (+ kendi UI parçaları ekstra) · Ömer = Telegram bot + chat_id + gerçek mesaj · Yiğit = ekran görüntüleri + 16'sı için slaytlar · Murat = Neon, anahtar, Notion akışı, video, GitHub.

**Kurallar:** kendi dalın (`kutay/web`, `omer/agent`, `yigit/data`, `murat/api-core`), küçük PR, commit'te AI imzası yok, `.env` asla. Ayrıntı: `AGENTS.md`, görev kartın `docs/team/<isim>.md`, bugünün planı `docs/team/BUGUN-PLAN.md`. **22:00 kontrol toplantısı.**
