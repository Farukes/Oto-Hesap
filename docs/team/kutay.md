# Kutay — görev kartı (13 Eyl akşam sürümü; deneme sunumu 14 Eyl, 3 dk)

**Durum:** Uygulama `main`'de çalışıyor: Next.js arayüzü (5 ekran), FastAPI, sentetik veri, Türkçe soru → SQL asistanı, insan onaylı tedarik ajanı (Telegram). Senin alanın `apps/web`. Bugün hedefin: **sunucu laptopunu kurmak, 3 dakikalık akışı kronometreyle 3 kez prova etmek, küçük arayüz dokunuşları.** Sunucu sen olursan telefonda açık tutacağın akış: `docs/sunum/3-dakika-akis.md`.

## 1 · Yapay zekaya ilk mesaj (olduğu gibi yapıştır; ardından `AGENTS.md` ve bu dosyayı ekle)
> Sen benim geliştirme asistanımsın. Ekli `AGENTS.md` ve görev kartım projenin tek gerçeğidir; dışına çıkma, yeni özellik önerme. Depo: https://github.com/muratcan-ates/Oto-Hesap — dalım `kutay/web`. Ürün çalışır durumda; benim işim karttaki adımları **sırayla** bitirmek. Her adımda: ne yapacağını 3 maddede söyle, ben "devam" deyince yap, çalıştırdığın komutun çıktısını göster, bitince "ADIM N TAMAM" yaz ve sonraki adıma geç. Bilmediğin dosya/alan/komut uydurma; önce dosyayı oku, yine emin değilsen bana sor. Commit mesajına yapay zeka imzası ekleme. `.env` içeriğini ve anahtarları asla sohbete yazma. Şu an Adım 0'dayım.

## 2 · Adımlar (sırayla)
### Adım 0 · Kurulum (15 dk) — herkes aynı
```bash
git clone https://github.com/muratcan-ates/Oto-Hesap.git ~/code/Oto-Hesap && cd ~/code/Oto-Hesap
./scripts/setup.sh                # hook + .env + bağımlılıklar (uv, bun gerekir; yoksa: brew install uv oven-sh/bun/bun)
git checkout kutay/web
```
`.env` doldur: `DATABASE_URL` ve `DATABASE_URL_RO` → Murat'ın DM'le attığı Neon adresleri (kendi Postgres'in varsa: `createdb otohesap && psql -d otohesap -f docs/schema.sql`, salt-okur rol komutları `docs/schema.sql` sonunda). `LLM_PROVIDER=fake` bırakabilirsin; demo soruları anahtarsız da çalışır.
```bash
make seed        # sentetik veri (6 ay, 20 ürün, 2 kritik)  — Neon paylaşımlıysa yalnız Murat koşar
make api         # http://localhost:8000/docs
make web         # ayrı terminal → http://localhost:3000
```
**Kabul:** `http://localhost:3000` açılıyor, sol menü altında "API bağlı" yazıyor (mock rozeti YOK), Genel Bakış'ta "Kritik ürün: 2".

### Adım 1 · 3 dakikalık akışı prova et (30 dk)
`docs/sunum/3-dakika-akis.md` tablosunu aç; `make warmup` koş; akışı kronometreyle 3 kez sür: Genel Bakış → Asistan çipi "En çok kazancım hangi üründen?" → Sorguyu gör → Tedarik "Şimdi kontrol et" → Onayla → (Telegram Ömer'de) → kapanış cümlesi. Her turda süreyi not et.
**Kabul:** 3. tur ≤ 2:50; takılan ekran yok. Takılan varsa Adım 2'de düzelt.

### Adım 2 · Küçük arayüz dokunuşları (45 dk, isteğe bağlı)
Yalnız görünüm: renk/başlık/ikon/boşluk. Renk token'ları `apps/web/app/globals.css` (`@theme`), kabuk `apps/web/components/AppShell.tsx` ve `Sidebar.tsx`, KPI kartı `components/KpiCard.tsx`. Yapı, rota ve `lib/api.ts` değişmez. Her değişiklikten sonra:
```bash
cd apps/web && bun run lint && bun run build
```
**Kabul:** lint ve build temiz; 5 ekran hâlâ açılıyor; mobil genişlikte menü katlanıyor.

### Adım 3 · PR aç (10 dk)
```bash
git add -A && git commit -m "feat(web): sunum öncesi arayüz dokunuşları" && git push -u origin kutay/web
```
GitHub'da PR: `kutay/web` → `main`, şablonu doldur. Gruba "PR açık" yaz. **Kabul:** CI yeşil.

### Adım 4 · Ekstra (zaman kalırsa)
- Kendi yaptığın UI çalışmasından bir ekranı taşımak istersen: aynı `lib/api.ts` fonksiyonlarını kullan, tek ekranla başla, ayrı PR.
- Vercel: Root Directory `apps/web`, env `NEXT_PUBLIC_API_URL` = Render API adresi (Murat verir). 16'sı için.

## 3 · Bilmen gerekenler
- API sözleşmesi: `AGENTS.md §6`. Tipler: `apps/web/lib/types.ts`. Mock modu: API kapalıysa sol altta "mock veri" rozeti çıkar; demoda çıkmamalı.
- KPI etiketi "Fark (Gelir − Gider)" — "net kâr" yazma (D16). Tedarik'te "Gönderildi · teslim alındı değil" kalır (D17).
- Asistan çipleri demo sırasında; serbest soru sorma, çipleri kullan.

## 4 · Kurallar (kısa)
- Kendi dalında çalış; `main`'e yalnız PR ile (`git push -u origin kutay/web` → GitHub'da "Compare & pull request"). Push yetkin yoksa Murat'a yaz.
- Küçük commit, imzasız (`git log -1` ile kontrol; hook zaten engeller).
- `.env` ve anahtarlar sohbete/gruba yazılmaz.
- Yeni özellik yok; kırık bir şey görürsen gruba yaz.

## 5 · Takılırsan
45 dakikada ilerleme yoksa gruba yaz: "Adım N'de takıldım, hata: …". Yapay zekaya `docs/team/BUGUN-PLAN.md` ve hata metnini ver. 22:00 kontrol toplantısında canlı bakarız.
