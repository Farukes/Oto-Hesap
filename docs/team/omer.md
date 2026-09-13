# Ömer — görev kartı (13 Eyl akşam sürümü; deneme sunumu 14 Eyl, 3 dk)

**Durum:** Uygulama `main`'de çalışıyor. Tedarik ajanı, sipariş onayı ve Telegram bildirimi (`apps/api/app/services/agent.py`, `notify.py`, `routers/orders.py`) yazıldı ve testli (47 test). Şu an mesaj **simülasyon** modunda (`NOTIFY_DRY_RUN=true`). Bugün hedefin: **gerçek Telegram mesajını telefona düşürmek, soru bankasındaki beklenen rakamları doldurmak, demoda sunucuya eşlik etmek.**

## 1 · Yapay zekaya ilk mesaj (olduğu gibi yapıştır; ardından `AGENTS.md` ve bu dosyayı ekle)
> Sen benim geliştirme asistanımsın. Ekli `AGENTS.md` ve görev kartım projenin tek gerçeğidir; dışına çıkma, yeni özellik önerme. Depo: https://github.com/muratcan-ates/Oto-Hesap — dalım `omer/agent`. Ürün çalışır durumda; benim işim karttaki adımları **sırayla** bitirmek. Her adımda: ne yapacağını 3 maddede söyle, ben "devam" deyince yap, çalıştırdığın komutun çıktısını göster, bitince "ADIM N TAMAM" yaz ve sonraki adıma geç. Bilmediğin dosya/alan/komut uydurma; önce dosyayı oku, yine emin değilsen bana sor. Commit mesajına yapay zeka imzası ekleme. `.env` içeriğini ve anahtarları asla sohbete yazma. Şu an Adım 0'dayım.

## 2 · Adımlar (sırayla)
### Adım 0 · Kurulum (15 dk) — herkes aynı
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh                # hook + .env + bağımlılıklar (uv, bun gerekir; yoksa: brew install uv oven-sh/bun/bun)
git checkout omer/agent
```
`.env` doldur: `DATABASE_URL` ve `DATABASE_URL_RO` → Murat'ın DM'le attığı Neon adresleri (kendi Postgres'in varsa: `createdb otohesap && psql -d otohesap -f docs/schema.sql`, salt-okur rol komutları `docs/schema.sql` sonunda). `LLM_PROVIDER=fake` bırakabilirsin; demo soruları anahtarsız da çalışır.
```bash
make seed        # sentetik veri (6 ay, 20 ürün, 2 kritik)  — Neon paylaşımlıysa yalnız Murat koşar
make api         # http://localhost:8000/docs
make web         # ayrı terminal → http://localhost:3000
```
**Kabul:** `http://localhost:3000` açılıyor, sol menü altında "API bağlı" yazıyor (mock rozeti YOK), Genel Bakış'ta "Kritik ürün: 2".

### Adım 1 · Telegram botu (20 dk)
1. Telegram'da **@BotFather** → `/newbot` → ad ve kullanıcı adı → token'ı kopyala (yalnız `.env`'e).
2. Botu telefonunda aç, **Start**'a bas ve "merhaba" yaz (bot sana mesaj atabilsin diye şart).
3. chat_id'ni al: tarayıcıda `https://api.telegram.org/bot<TOKEN>/getUpdates` → `"chat":{"id":123456789` → bu sayı.
4. `.env`: `TELEGRAM_BOT_TOKEN=<token>`, `TELEGRAM_DEFAULT_CHAT_ID=<chat_id>`, `NOTIFY_DRY_RUN=false`.
5. Demo tedarikçisini kendi telefonuna bağla (veritabanı Neon paylaşımlıysa herkes için geçerli olur, istenen de bu):
```bash
psql "$DATABASE_URL" -c "UPDATE suppliers SET contact_address='<chat_id>' WHERE contact_channel='telegram';"
```
(`data/README.md` aynı komutu açıklar.)
**Kabul:** `make api` yeniden başlat → `http://localhost:3000/tedarik` → "Şimdi kontrol et" → Onayla → **telefonda mesaj**: "DEMO · sentetik sipariş #N — Merhaba Anadolu Güç Sistemleri…". Ekran görüntüsünü gruba at. Kartta "Gönderildi HH:MM · teslim alındı değil" ve küçük gri `ref <message_id>`.

### Adım 2 · Soru bankası rakamları (20 dk)
`docs/soru-bankasi.md` ve `apps/api/app/data/soru_bankasi.json` içinde "seed sonrası doldurulacak" notlarını `data/README.md` özetindeki gerçek rakamlarla doldur (en azından 5 demo sorusu: en kârlı ürün Powerbank 20000 mAh 80.415 ₺; bu ayki gider; son 3 ay farkı; kritik 2 ürün; en çok gider kategorisi maaş). Rakamı doğrulamak için `http://localhost:8000/docs` → `POST /api/assistant/ask`.
**Kabul:** 5 demo sorusunun beklenen değeri yazılı; `cd apps/api && uv run pytest -q tests/test_agent.py -k bank` yeşil.

### Adım 3 · Demo eşlik + jüri soruları (30 dk)
Sunucuyla (Kutay) 3 dakikalık akışı 2 kez birlikte sür; sen telefonu tutan kişisin. `docs/sunum/3-dakika-akis.md` sonundaki 5 jüri sorusuna 1 cümlelik cevapları ezberle; `docs/sunum/pitch-paketi.md`'deki 10 soruyu oku.
**Kabul:** Onay → telefon arası ≤ 5 sn; her soruya tek cümle cevabın hazır.

### Adım 4 · PR aç (10 dk)
```bash
git add -A && git commit -m "docs(bank): demo sorularının beklenen rakamları" && git push -u origin omer/agent
```
PR: `omer/agent` → `main`. **Kabul:** CI yeşil.

### Adım 5 · Ekstra (zaman kalırsa)
- `make eval` gerçek sağlayıcıyla (anahtar gelirse) → kaç soru doğru; sonucu gruba yaz.
- Wi-Fi olmayan sınıf için hotspot provası; video için onay anını 20 sn kaydet.

## 3 · Bilmen gerekenler
- Ajan LLM kullanmaz: `stock_qty <= reorder_point` → taslak; miktar = hedef − mevcut; ürün başına tek açık sipariş (DB tekil indeks). `sent` = mesaj gönderildi, teslim değil; stok artmaz.
- Onay iki kez basılırsa 409; gönderim düşerse sipariş `approved` kalır, tekrar denenir (502).
- Token loglara ve mesajlara yazılmaz; `.env` dışına çıkmaz.

## 4 · Kurallar (kısa)
- Kendi dalında çalış; `main`'e yalnız PR ile (`git push -u origin omer/agent` → GitHub'da "Compare & pull request"). Push yetkin yoksa Murat'a yaz.
- Küçük commit, imzasız (`git log -1` ile kontrol; hook zaten engeller).
- `.env` ve anahtarlar sohbete/gruba yazılmaz.
- Yeni özellik yok; kırık bir şey görürsen gruba yaz.

## 5 · Takılırsan
45 dakikada ilerleme yoksa gruba yaz: "Adım N'de takıldım, hata: …". Yapay zekaya `docs/team/BUGUN-PLAN.md` ve hata metnini ver. 22:00 kontrol toplantısında canlı bakarız.
