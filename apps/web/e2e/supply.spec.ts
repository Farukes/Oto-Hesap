import { expect, test, type APIRequestContext, type Locator, type Page } from "@playwright/test";
import { apiContext, getOrders, getProducts, patchProduct, rejectPendingOrders } from "./helpers";

// Tedarik: "Şimdi kontrol et" → taslak → "Onayla" → "Gönderildi · teslim alındı değil".
// İkinci kontrol aynı ürün için YENİ taslak üretmemeli (tekrar koruması).
//
// Test yeniden çalıştırılabilir olsun diye:
//  · beforeAll bekleyen taslakları reddeder (reddedilen ürün bir sonraki kontrolde yine taslağa düşer),
//  · kritik ürünlerin hepsi daha önce "gönderildi"ye geçtiyse yedek bir ürün geçici olarak kritik yapılır,
//  · afterAll kalan taslakları reddeder ve geçici eşiği eski değerine döndürür.
// Not: onaylanan sipariş "sent" olur ve API'de silme ucu yoktur; o ürün yeniden taslak üretmez.

test.describe.configure({ mode: "serial" });

let api: APIRequestContext;
let expectedDrafts = 0;
let restoreThreshold: { id: number; reorder_point: number } | null = null;

function pendingSection(page: Page): Locator {
  return page.locator("section").filter({ has: page.getByRole("heading", { name: "Onay bekleyen taslaklar" }) });
}

/** Üstteki durum sayaçları: "Bekliyor / Onaylandı / Gönderildi / Reddedildi". */
async function statusCount(page: Page, label: string): Promise<number> {
  const box = page.getByText(label, { exact: true }).first().locator("xpath=..");
  const text = (await box.locator("xpath=./div[2]").textContent()) ?? "";
  return Number(text.trim());
}

test.beforeAll(async () => {
  api = await apiContext();

  // Önceki koşulardan kalan taslak/onaylı siparişleri temizle.
  await rejectPendingOrders(api);

  const products = await getProducts(api);
  const ready = products.filter((p) => p.is_critical && p.open_order_id === null && p.supplier_id !== null);

  if (ready.length > 0) {
    expectedDrafts = ready.length;
    return;
  }

  // Kritik ürünlerin tamamının açık (gönderilmiş) siparişi var: yedek bir ürünü geçici olarak kritik yap.
  const spare = products.find((p) => !p.is_critical && p.open_order_id === null && p.supplier_id !== null && p.stock_qty > 0);
  expect(
    spare,
    "Taslak üretilebilecek ürün kalmadı. Veriyi tazeleyin: python data/seed.py --reset",
  ).toBeTruthy();
  restoreThreshold = { id: spare!.id, reorder_point: spare!.reorder_point };
  await patchProduct(api, spare!.id, { reorder_point: spare!.stock_qty });
  expectedDrafts = 1;
});

test.afterAll(async () => {
  if (!api) return;
  await rejectPendingOrders(api);
  if (restoreThreshold) await patchProduct(api, restoreThreshold.id, { reorder_point: restoreThreshold.reorder_point });
  await api.dispose();
});

test("kontrol → taslak → onay → gönderildi; ikinci kontrol yeni taslak üretmiyor", async ({ page }) => {
  await page.goto("/tedarik");

  const section = pendingSection(page);
  const cards = section.locator("article");
  await expect(section.getByText("Bekleyen taslak yok")).toBeVisible();
  await expect(cards).toHaveCount(0);

  // --- 1) Ajan kontrolü: kritik ürünler için taslak ---
  await page.getByRole("button", { name: "Şimdi kontrol et" }).click();
  // Zamanlayıcı aynı anda çalışmış olabilir; iki mesaj da kabul edilir.
  await expect(page.getByText(/taslak oluşturuldu|Yeni taslak yok/)).toBeVisible();
  await expect(cards).toHaveCount(expectedDrafts);
  expect(await statusCount(page, "Bekliyor")).toBe(expectedDrafts);

  const firstCard = cards.first();
  await expect(firstCard).toContainText("Onayla");
  await expect(firstCard).toContainText("adet");
  await expect(firstCard).toContainText("₺");

  const orderId = Number(/Taslak #(\d+)/.exec((await firstCard.innerText()) ?? "")?.[1]);
  expect(Number.isInteger(orderId), "taslak numarası kartta bulunamadı").toBeTruthy();
  const draft = (await getOrders(api, "draft")).find((o) => o.id === orderId);
  expect(draft, `#${orderId} taslağı API'de yok`).toBeTruthy();

  // --- 2) İnsan onayı ---
  await firstCard.getByRole("button", { name: "Onayla" }).click();
  await expect(page.getByText(/Onaylandı/)).toBeVisible();

  // Kart bekleyenlerden çıktı, iz kaydına "Gönderildi" olarak düştü.
  await expect(cards).toHaveCount(expectedDrafts - 1);
  const trailRow = page.locator("li").filter({ hasText: new RegExp(`#${orderId}\\b`) }).first();
  await expect(trailRow).toBeVisible();
  await expect(trailRow).toContainText(draft!.product_name);
  await expect(trailRow).toContainText("Gönderildi");
  await expect(trailRow).toContainText("teslim alındı değil");

  const approved = (await getOrders(api, "sent")).find((o) => o.id === orderId);
  expect(approved, `#${orderId} API'de "sent" olmalı`).toBeTruthy();

  // --- 3) Aynı ürün için ikinci kontrol yeni taslak üretmemeli ---
  const draftsBefore = await statusCount(page, "Bekliyor");
  const draftIdsBefore = (await getOrders(api, "draft")).map((o) => o.id).sort();

  await page.getByRole("button", { name: "Şimdi kontrol et" }).click();
  await expect(page.getByText("Yeni taslak yok: kritik ürünlerin açık siparişi var ya da kritik ürün yok.")).toBeVisible();
  await expect(cards).toHaveCount(expectedDrafts - 1);
  expect(await statusCount(page, "Bekliyor"), "ikinci kontrol taslak sayacını artırmamalı").toBe(draftsBefore);
  expect((await getOrders(api, "draft")).map((o) => o.id).sort()).toEqual(draftIdsBefore);
});
