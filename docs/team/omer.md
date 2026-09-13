# Görev kartı — Ömer (dal: `omer/agent`)

## Nasıl başlarım (5 dakika)
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh
git checkout omer/agent
```
Sonra kendi yapay zeka aracına şu ilk mesajı at ve iki dosyayı yapıştır (`AGENTS.md` + bu kart):

> Aşağıda projenin AGENTS.md dosyası ve benim görev kartım var. Kurallara uy. Bilmediğin alan, model adı veya URL uydurma; `TODO(omer)` bırak ve sor. Önce 5 maddelik plan ver; onaylayınca küçük adımlarla uygula, her adımda testi koştur. İlk işim: Telegram botu + `notify.py` ilk mesaj.

Bitince: `git add -p` → `git commit` (imza yok) → `git push -u origin omer/agent` → PR aç (şablon dolu) → gruba "PR açık" yaz.

> Yapay zekaya ilk mesaj: "Aşağıda AGENTS.md ve görev kartım var. Kurallara uy. Ajan kural tabanlı ve deterministik olacak; LLM yalnız mesaj metnini cilalamak için, opsiyonel. Telegram Bot API dışında kanal önerme. Uydurma yok; `TODO(omer)` bırak ve sor. Önce 5 maddelik plan, sonra küçük adımlar, her adımda test. Şu an şu adımdayım: ___"

## Rol
Otonom tedarik ajanı (tespit → taslak → insan onayı → Telegram), sipariş uçları, zamanlayıcı; demo senaryosunun ve soru bankasının sahibi; provaları yöneten ve demoyu süren kişi; sunumda "Yol haritası + kapanış".

## Bugün teslim edeceklerim
1. **09:30–10:30 Telegram botu (iskeleti beklemeden)**
   - BotFather'dan bot + token; bir grup/sohbet aç, `chat_id` al (getUpdates ile).
   - `apps/api/app/services/notify.py`: `send_telegram(chat_id, text) -> {ok, message_id}`; `httpx`; token yoksa loglar, hata fırlatmaz (`NOTIFY_DRY_RUN`).
   - Bağımsız script ile ilk mesaj telefona düştü → ekran görüntüsü WhatsApp'a (moral).
2. **10:30–13:00 Ajan çekirdeği (`services/agent.py`, `routers/agent.py`, `routers/orders.py`)**
   - `check()`: `stock_qty <= reorder_point` olan ürünler; aynı ürün için `draft|approved|sent` sipariş varsa atla (tekrar koruması); taslak: `qty = target_stock - stock_qty`, `est_amount = qty * unit_cost`, `message_text` şablondan:
     > "Merhaba {tedarikçi}, OtoHesap üzerinden sipariş talebi: {ürün} × {miktar} adet. Tahmini tutar {tutar} ₺. Teslim: {lead_time_days} gün. Onay için yanıtlayabilirsiniz. — {işletme adı}"
   - `POST /api/agent/check` → `{created, drafts}`; `GET /api/orders?status=`; `POST /api/orders/{id}/approve` → `send_telegram` → `status=sent`, `sent_at`; `reject`.
   - `products` yanıtındaki `open_order_id` için Murat'a bilgi (o alanı Murat doldurur).
   - Testler: kritik ürün taslak üretir; tekrar korumalı; approve `fake` notify ile `sent`.
3. **13:30–15:00 Zamanlayıcı:** APScheduler `main.py` başlangıcında (`AGENT_CHECK_INTERVAL_MIN`), `check()`'i çağırır; logda "ajan: 2 taslak". Demo'da buton yeter; zamanlayıcı slaytta "10 dakikada bir" cümlesi için.
4. **13:00–16:30 Soru bankası (`docs/soru-bankasi.md`) — Yiğit ile**
   - 15 soru; her biri: soru metni (çiplerdeki yazımla birebir), beklenen SQL (Postgres), beklenen yanıt (seed'e göre gerçek rakam), demo sorusu mu (5'i evet).
   - Murat'ın text2sql'i bu dosyadan örnek ve önbellek okur; yazım birebir önemli.
5. **16:30–19:00 Demo senaryosu ve sunum metni:** `docs/demo-senaryosu.md`'yi son haline getir (tıklama tıklama, saniye saniye); sunum konuşma metni (9 slayt, kim ne der); jüri soruları (10) ve cevapları.
6. **20:00–22:00 Provalar:** kronometreyle 2 prova; ekran kaydı (QuickTime) 3 dk video → USB + Drive; telefon hazır (Telegram sohbeti açık, ses açık, ikinci telefon yedek).

## Bağımlılıklar
- **Bana gelen:** iskelet + `models.py` (10:30), seed (11:00, kritik 2 ürün), Kutay'ın Tedarik ekranı (16:30).
- **Benden giden:** `notify.py` (10:30), `orders` uçları (15:00), soru bankası v1 (14:00) → Murat, demo senaryosu final (19:00).

## Dosyalarım
`apps/api/app/services/{agent,notify}.py`, `routers/{agent,orders}.py`, `tests/test_agent.py`, `docs/soru-bankasi.md`, `docs/demo-senaryosu.md`, `docs/sunum-metni.md`.

## Kabul kriterleri
- 13:00: `POST /api/agent/check` seed'de tam 2 taslak üretir; ikinci çağrı 0 üretir.
- 15:00: approve → telefonda mesaj; `sent_at` dolu; reject çalışır.
- 16:30: soru bankası 15 soru, beklenen rakamlar seed ile doğrulanmış.
- 21:00: prova 10 dk'nın altında, demo adımları saniyeleriyle yazılı.

## Risk ve yedek
- Telegram engellenirse (okul ağı): mobil veriden; olmazsa `NOTIFY_DRY_RUN` + ekranda "gönderildi (simülasyon)" rozeti + video.
- Seed'de kritik ürün 2 değilse Yiğit'e söyle; ajan koduna sabit sayı koyma.

## Yapma
- Ekran kodu yazma; `models.py` değiştirme (ihtiyaç → Murat).
- LLM'i karar mekanizmasına sokma; kural yeter, deterministik = güvenli demo.

## Araştırmadan gelen notlar (13 Eyl, SONUC-chatgpt)
- **Soru bankası dağılımı (15):** 5 basit toplam · 3 tarih filtresi · 3 join · 2 boş/uç durum ("Aralık 2026 gideri?" → veri yok) · 2 saldırgan ("tüm satışları sil", "tedarikçi parolalarını göster"). Her satırda: soru (çipteki yazımla birebir), beklenen rakam, izinli tablolar, demo sorusu mu. Beklenen SQL yazılabilir ama ölçüt değildir.
- **Durum makinesi:** `draft → approved → sent | rejected`; `approve` iki kez basılırsa ikinci istek 409 döner (idempotent); Telegram başarısızsa durum `approved` kalır ve kart "gönderilemedi, tekrar dene" gösterir.
- **Demo süresi:** pano 30 sn → kayıt 30 → soru 60 → SQL 30 → kritik stok 30 → taslak 40 → onay 20 → telefon 20 → kapanış 20. En yüksek "vay" anı son 60 saniye; zaman kalmıyorsa grafik değil bu akış korunur.
- **Okul Wi-Fi'ı:** telefon hotspot'u hazır; Telegram sohbeti açık; token `.env`'de; 30–60 sn kayıtlı yedek video.
- Pitch metinleri hazır: `docs/sunum/pitch-paketi.md` (asansör konuşması, 10 jüri sorusu, köprü cümleleri). Rakamlar için `docs/research/KONTROL-2026-09-13.md`'ye bak: A olmayan sayı söylenmez.

## Durum (13 Eyl akşam) — inşa edildi, senin için kalan
**Yapıldı (Claude, main'de):** kural tabanlı ajan (`run_check`), DB tekil indeksle tekrar koruması, durum makinesi (draft→approved→sent | rejected, 409/502 yolları), Telegram `notify.py` (dry-run), zamanlayıcı, `notify_ref`, DEMO etiketli mesaj, soru bankası 15 soru (JSON + md), 47 test.
**Geliştirme Günü'nde senin işin:** (1) BotFather'dan bot + chat_id; `UPDATE suppliers ... WHERE contact_channel='telegram'` (komut `data/README.md`'de); Render'da `TELEGRAM_BOT_TOKEN`, `NOTIFY_DRY_RUN=false`; telefonda gerçek mesaj; (2) `docs/soru-bankasi.md`'de "seed sonrası doldurulacak" rakamları `data/README.md` özetinden doldur (Yiğit ile); (3) `docs/demo-senaryosu.md`'yi canlı adres ve gerçek rakamlarla son haline getir; (4) sunum metni + 10 jüri sorusu (`docs/sunum/pitch-paketi.md`); (5) 3 prova, video kaydı, hotspot.
