import { expect, test } from "@playwright/test";
import { expectNoHorizontalScroll, kpiCard } from "./helpers";

// 375 px (iPhone SE/12 mini genişliği): menü katlanıyor, yatay kaydırma yok, KPI kartları alt alta.

test.use({ viewport: { width: 375, height: 812 } });

const PATHS = ["/", "/kayitlar", "/stok", "/asistan", "/tedarik"];

test("375 px: menü katlanıyor, hamburger ile açılıp kapanıyor", async ({ page }) => {
  await page.goto("/");

  const menuButton = page.getByRole("button", { name: "Menüyü aç" });
  await expect(menuButton).toBeVisible();

  // Kenar menü ekran dışında (katlanmış).
  const sidebar = page.locator("aside");
  const closed = await sidebar.boundingBox();
  expect(closed, "kenar menü bulunamadı").not.toBeNull();
  expect(closed!.x + closed!.width, "kenar menü 375 px'te ekran dışında olmalı").toBeLessThanOrEqual(1);

  // Açılıyor.
  await menuButton.click();
  await expect.poll(async () => (await sidebar.boundingBox())?.x ?? -1, { message: "menü açılmadı" }).toBeGreaterThanOrEqual(0);
  await expect(sidebar.getByRole("link", { name: "Stok" })).toBeVisible();

  // Kapanıyor.
  await sidebar.getByRole("button", { name: "Menüyü kapat" }).click();
  await expect.poll(async () => (await sidebar.boundingBox())?.x ?? 0, { message: "menü kapanmadı" }).toBeLessThan(0);
});

test("375 px: KPI kartları alt alta diziliyor", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/Son güncelleme/)).toBeVisible();

  const income = await kpiCard(page, "Gelir").boundingBox();
  const expense = await kpiCard(page, "Gider").boundingBox();
  expect(income, "Gelir kartı ölçülemedi").not.toBeNull();
  expect(expense, "Gider kartı ölçülemedi").not.toBeNull();

  expect(Math.abs(income!.x - expense!.x), "kartlar aynı sütunda olmalı").toBeLessThanOrEqual(1);
  expect(expense!.y, "Gider kartı Gelir kartının altında olmalı").toBeGreaterThanOrEqual(income!.y + income!.height - 1);
  expect(income!.width, "kart ekran genişliğini aşmamalı").toBeLessThanOrEqual(375);
});

for (const path of PATHS) {
  test(`375 px: ${path} yatay kaydırma yapmıyor`, async ({ page }) => {
    await page.goto(path);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
    // Veri geldikten sonra ölç (tablolar/grafikler yerleşsin).
    await page.waitForLoadState("networkidle");
    await expectNoHorizontalScroll(page);
  });
}
