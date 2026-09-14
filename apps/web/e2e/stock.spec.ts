import { expect, test, type APIRequestContext } from "@playwright/test";
import { apiContext, getProducts, patchProduct, type ApiProduct } from "./helpers";

// Stok: iki kritik satır kırmızı + "Kritik" rozetli; eşik düzenleme PATCH ile kaydediliyor.
// Eşik testi kritik OLMAYAN bir ürün üzerinde çalışır (kritik sayısı değişmesin) ve sonunda eski değere döner.

test.describe.configure({ mode: "serial" });

const DANGER = "rgb(192, 57, 43)"; // --color-danger #c0392b

let api: APIRequestContext;
let target: ApiProduct;
let originalReorderPoint = 0;

test.beforeAll(async () => {
  api = await apiContext();
  const products = await getProducts(api);
  // Eşiği 1 artırınca hâlâ kritik olmayacak bir ürün seç (stok > eşik + 1).
  const candidate = products.find((p) => !p.is_critical && p.stock_qty > p.reorder_point + 1);
  expect(candidate, "eşiği denenebilecek kritik olmayan ürün bulunamadı").toBeTruthy();
  target = candidate!;
  originalReorderPoint = target.reorder_point;
});

test.afterAll(async () => {
  if (!api) return;
  // Güvenlik ağı: test yarıda kalsa bile eşik eski değerine döner.
  if (target) await patchProduct(api, target.id, { reorder_point: originalReorderPoint });
  await api.dispose();
});

test("iki kritik ürün kırmızı ve 'Kritik' rozetli", async ({ page }) => {
  await page.goto("/stok");
  await expect(page.getByRole("heading", { name: "Ürünler" })).toBeVisible();

  // Tam iki kritik ürün (seed hedefi).
  await expect(page.getByText("Kritik", { exact: true })).toHaveCount(2);
  await expect(page.getByText(/2 ürün yeniden sipariş eşiğinin altında/)).toBeVisible();

  for (const name of ["Powerbank 20000 mAh", "Kablosuz Şarjlı Powerbank"]) {
    const row = page.getByRole("row").filter({ hasText: name }).first();
    await expect(row.getByText("Kritik", { exact: true })).toBeVisible();

    // Stok hücresi kırmızı yazılıyor.
    const stockCell = row.getByRole("cell").nth(1);
    const color = await stockCell.locator("span").first().evaluate((el) => getComputedStyle(el).color);
    expect(color, `${name} stok değeri kırmızı olmalı`).toBe(DANGER);
  }

  // Kritik ürün sayacı da 2.
  const criticalBox = page.getByText("Kritik ürün", { exact: true }).locator("xpath=..");
  await expect(criticalBox.locator("xpath=./div[2]")).toHaveText("2");
});

test("eşik düzenleme kaydediliyor ve sayfa güncelleniyor", async ({ page }) => {
  const next = originalReorderPoint + 1;
  await page.goto("/stok");

  const cellButton = (value: number) =>
    page.getByRole("button", { name: `${target.name} eşiği: ${value}, düzenlemek için tıklayın` });

  await expect(cellButton(originalReorderPoint)).toBeVisible();
  await cellButton(originalReorderPoint).click();

  const input = page.getByRole("spinbutton", { name: `${target.name} eşiği` });
  await input.fill(String(next));
  await input.press("Enter");

  await expect(page.getByText(`${target.name} güncellendi.`)).toBeVisible();
  await expect(cellButton(next)).toBeVisible();

  // API'de gerçekten değişti mi?
  await expect
    .poll(async () => (await getProducts(api)).find((p) => p.id === target.id)?.reorder_point, {
      message: "PATCH /api/products eşiği güncellemedi",
    })
    .toBe(next);

  // --- geri al (arayüzden) ---
  await cellButton(next).click();
  const back = page.getByRole("spinbutton", { name: `${target.name} eşiği` });
  await back.fill(String(originalReorderPoint));
  await back.press("Enter");

  await expect(cellButton(originalReorderPoint)).toBeVisible();
  await expect
    .poll(async () => (await getProducts(api)).find((p) => p.id === target.id)?.reorder_point, {
      message: "eşik eski değerine dönmedi",
    })
    .toBe(originalReorderPoint);

  // Kritik ürün sayısı değişmedi.
  await page.reload();
  await expect(page.getByText("Kritik", { exact: true })).toHaveCount(2);
});
