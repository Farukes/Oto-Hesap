# Uçtan uca testler (Playwright)

Demo senaryosunu (`docs/demo-senaryosu.md`) tarayıcıda baştan sona koşan testler.
Mock yok: gerçek `apps/api` + gerçek Postgres + seed verisi üstünde çalışır.
Bir test kırmızıysa demo da kırmızıdır.

## Çalıştırma

```bash
# ön koşul: API ayakta (make api) ve veri yüklü (make seed)
cd apps/web
bun run test:e2e            # tüm testler
bun run test:e2e:ui         # Playwright UI modu
bunx playwright test e2e/supply.spec.ts --reporter=line   # tek dosya
bunx playwright test --headed                              # tarayıcıyı gör
```

Web sunucusu 3000'de zaten çalışıyorsa yeniden kullanılır (`reuseExistingServer`);
çalışmıyorsa Playwright `bun run dev` ile kendisi başlatır.

**Tarayıcı indirmesi yok.** Yerelde sistemdeki Google Chrome kullanılır (`channel: "chrome"`),
`playwright install` çalıştırmaya gerek yoktur. CI'da paketli Chromium kurulur
(`PW_CHANNEL=""` ya da `CI=1` bu davranışı açar).

Ortam değişkenleri: `E2E_WEB_URL` (varsayılan `http://localhost:3000`),
`E2E_API_URL` / `NEXT_PUBLIC_API_URL` (varsayılan `http://localhost:8000`).

## Dosyalar

| Dosya | Kapsam |
|-------|--------|
| `smoke.spec.ts` | Beş sayfa açılıyor, başlık doğru, konsol temiz, "mock veri" rozeti yok, menü geziniyor |
| `overview.spec.ts` | KPI'lar sayı gösteriyor, "Fark (Gelir − Gider)" (ve "Net kâr" etiketi yok), dönem sekmeleri, "2 ürün kritik stokta" öngörüsü, aylık grafik |
| `assistant.spec.ts` | Hazır soru çipi → yanıtta Powerbank, "Sorguyu gör" → SELECT'li SQL, kaynak + saat damgası; "Tüm satışları sil" → sakin ret, uygulama ayakta |
| `supply.spec.ts` | "Şimdi kontrol et" → taslak → "Onayla" → "Gönderildi · teslim alındı değil"; ikinci kontrol yeni taslak üretmiyor |
| `records.spec.ts` | Gider ekle (reklam, 4.500) → listede → Genel Bakış'ta Gider KPI'ı arttı → sil; satış aramasında ürün filtresi |
| `stock.spec.ts` | İki kritik satır kırmızı + "Kritik" rozetli; eşik düzenleme (PATCH) çalışıyor ve geri alınıyor |
| `responsive.spec.ts` | 375 px: menü katlanıyor, yatay kaydırma yok, KPI kartları alt alta |
| `helpers.ts` | Ortak seçiciler (KPI kartı, kart başlığı), para ayrıştırma, API kurulum/temizlik yardımcıları |

## Kurallar

- **Seçiciler Türkçe metne dayanır** (`getByRole`, `getByText`). CSS sınıfı seçmeyin;
  arayüz metni değişirse test bilerek kırılır — sözleşme metindir.
- **Testler birbirinden bağımsızdır** ve veritabanını kalıcı bozmaz: eklenen kayıt silinir,
  değiştirilen eşik geri alınır (`afterAll` güvenlik ağıyla birlikte).
- **Sıralı koşarlar** (`workers: 1`): tek bir veritabanını paylaşıyorlar.

## Tedarik testinin durum bilgisi (önemli)

Onaylanan sipariş `sent` olur ve **API'de sipariş silme ucu yoktur**; bir ürünün açık
(`draft|approved|sent`) siparişi varken ajan o ürün için yeni taslak üretmez. Bu yüzden
`supply.spec.ts`:

1. `beforeAll` bekleyen (`draft`/`approved`) siparişleri `POST /api/orders/{id}/reject` ile reddeder —
   reddedilen ürün bir sonraki kontrolde yeniden taslağa düşer,
2. kritik ürünlerin tamamı daha önce "gönderildi"ye geçtiyse yedek bir ürünün eşiğini geçici olarak
   yükseltip kritik yapar ve `afterAll` eşiği eski değerine döndürür,
3. sonunda kalan taslakları reddeder.

**Demodan önce `make demo` (veya `python data/seed.py --reset`) çalıştırın:** test bir taslağı
onayladığı için o ürün "sipariş yolda" durumunda kalır ve demo akışındaki "2 taslak" görüntüsü
ancak taze veriyle elde edilir.

Yerel `.env`'de `AGENT_SCHEDULER_ENABLED=true` ise zamanlayıcı test sırasında da taslak üretebilir;
test bu ihtimale karşı toleranslı yazıldı. CI'da zamanlayıcı kapalıdır.

## CI

`.github/workflows/e2e.yml` → iş adı **`e2e (web)`**: postgres:16 servisi, `docs/schema.sql`,
`python data/seed.py --reset`, uvicorn, `bun install`, `npx playwright install --with-deps chromium`,
`bunx playwright test`. `LLM_PROVIDER=fake`, `NOTIFY_DRY_RUN=true`. Başarısızlıkta
`playwright-report` artifact olarak yüklenir.

## `.gitignore`

Şunlar depoya girmemeli (depo sahibine bildirildi):

```
apps/web/test-results/
apps/web/playwright-report/
apps/web/blob-report/
```
