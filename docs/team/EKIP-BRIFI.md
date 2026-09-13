# OtoHesap — Ekip Brifi (13 Eyl 2026)

> Bu dosya WhatsApp grubuna atılır. Ayrıntı depoda: `AGENTS.md` (kurallar, mimari, sözleşme), `docs/team/<isim>.md` (görev kartın), Notion planı (sunum akışı). Sorun varsa gruba yaz; 15 dk içinde eşleşiriz.

## Ne yapıyoruz
KOBİ'ler için web uygulaması: gelir-gider + stok panosu · Türkçe soruyla veriye erişen finans asistanı (SQL görünür, yalnız okur) · kritik stokta sipariş taslağı hazırlayıp **insan onayıyla** tedarikçiye Telegram mesajı atan ajan. Mottolar: **Legerdemain** (karmaşık iş arkada, kullanıcıya tek tık) · **Every second counts**.

## Ne zaman
| Ne | Zaman |
|----|-------|
| Geliştirme Günü (tek gün, hepsi) | 09:00–22:00 — tarih: **___** (toplantıda) |
| Checkpoint'ler | 10:30 iskelet main'de · 13:00 pano gerçek veriyle · 16:30 asistan + ajan · **19:00 özellik dondurma** · 20:00 yayın · 21:00 prova |
| Deneme sunumu | **___** |
| Final | 10 dk, PowerPoint, süre aşılmaz — tarih **___** |

Depo: https://github.com/muratcan-ates/Oto-Hesap · Plan (Notion): https://app.notion.com/p/3dac9fef3abb8132a124cce984e2827d

## Bu akşam herkes (30 dk)
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh            # iCloud dışı kontrolü + AI-imza engeli + .env
git checkout <dalın>          # murat/api-core · kutay/web · omer/agent · yigit/data
```
1. `AGENTS.md`'yi oku (10 dk). Kendi kartını oku: `docs/team/<isim>.md`.
2. `.env` dosyanı doldur (Neon bağlantısı Murat'tan davetle gelir; sırlar WhatsApp'a yazılmaz).
3. Kendi yapay zeka aracına kartındaki **ilk mesajı** at; bugün için tek küçük işini yaptır.
4. Gruba yaz: "hazırım / blokajım: ___".

## Kim ne yapıyor
| Kişi | Dal | Alan | Bu akşam |
|------|-----|------|----------|
| Kutay | `kutay/web` | 5 ekran, API bağlama, Vercel | Ekran iskeletleri (mock veriyle), kullandığı UI aracını gruba yaz |
| Murat | `murat/api-core` | Mimari, şema, API çekirdeği, Text-to-SQL | Neon + şema + API iskeleti + anahtarlar |
| Yiğit | `yigit/data` | Sentetik veri, analitik uçlar, CSV, slaytlar | `data/seed.py` (Faker, seed=42, tam 2 kritik ürün) |
| Ömer | `omer/agent` | Tedarik ajanı, Telegram, soru bankası, demo senaryosu, prova | Telegram botu + ilk test mesajı |

## 7 kural
1. Depo `~/code` altında; iCloud/Desktop/Documents **yasak** (`setup.sh` denetler).
2. Herkes kendi dalında; `main`'e yalnız PR + CI yeşil ile; küçük PR, 15 dk'da inceleme.
3. Commit'lerde yapay zeka imzası **yok** (Co-Authored-By, "Generated with…"); hook zaten engeller.
4. `.env` asla commit; anahtar sızarsa yenilenir.
5. API sözleşmesi `AGENTS.md §6`; değişiklik = PR + gruba duyuru. `models.py` ve `schema.sql` yalnız Murat.
6. Bir işte 45 dk ilerleme yoksa gruba yaz; blokajı gizlemek en pahalı hata.
7. Deneme sunumuna kadar yeni özellik yok; `docs/demo-senaryosu.md` tek gerçek kaynak.

## Yapay zekayla çalışma (herkes)
Her oturumun ilk mesajı = `AGENTS.md` + kendi kartın. Cümle: "Kurallara uy. Bilmediğin alan/model/URL uydurma; `TODO(<isim>)` bırak ve sor. Önce 5 maddelik plan, onaylayınca küçük adımlar, her adımda test." Diff'i PR'dan önce yapay zekaya incelet; sonra gözünle çalıştır.

## WhatsApp'a kopyalanacak özet
> OtoHesap planı hazır. Depo: github.com/muratcan-ates/Oto-Hesap — `AGENTS.md` kurallar, `docs/team/<isim>.md` görev kartın, `docs/team/EKIP-BRIFI.md` bu özet. Bu akşam: klonla → `./scripts/setup.sh` → kartını oku → dalını çek → AI'ına ilk mesajı at → "hazırım" yaz. Geliştirme Günü tek gün 09:00–22:00, 19:00 dondurma. Kutay: UI aracını yaz. Ömer: Telegram botu. Yiğit: seed. Ben: Neon + API iskeleti + anahtarlar.
