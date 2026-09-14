import { expect, test } from "@playwright/test";
import { cardByTitle, kpiCard, kpiValue, parseMoney } from "./helpers";

// Genel Bakış: KPI'lar, "Fark (Gelir − Gider)" adlandırması, dönem sekmeleri, Öngörü kartları, aylık grafik.

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText(/Son güncelleme/)).toBeVisible();
});

test("KPI kartları gerçek sayı gösteriyor", async ({ page }) => {
  for (const label of ["Gelir", "Gider", "Fark (Gelir − Gider)"]) {
    const value = kpiValue(page, label);
    await expect(value, `${label} KPI'ı para değeri göstermeli`).toHaveText(/\d.*₺/);
    expect(parseMoney(await value.textContent()), `${label} sayıya çevrilemedi`).not.toBeNull();
  }

  const critical = kpiValue(page, "Kritik ürün");
  await expect(critical).toHaveText(/^\d+$/);
  await expect(critical).toHaveText("2");
});

test('"Fark (Gelir − Gider)" etiketi var, "Net kâr" başlığı yok', async ({ page }) => {
  await expect(kpiCard(page, "Fark (Gelir − Gider)")).toBeVisible();

  // Sayfada tam olarak "Net kâr" diye bir etiket bulunmamalı.
  // (KPI ipucu "Net kâr değildir; KDV ve iade dahil değil" cümlesini bilerek içerir.)
  await expect(page.getByText("Net kâr", { exact: true })).toHaveCount(0);
  await expect(kpiCard(page, "Fark (Gelir − Gider)")).toContainText("Net kâr değildir");
});

test("dönem sekmeleri rakamları değiştiriyor", async ({ page }) => {
  const income = kpiValue(page, "Gelir");
  await expect(income).toHaveText(/₺/);

  const readIncome = async () => {
    await expect(income).toHaveText(/₺/);
    return parseMoney(await income.textContent());
  };

  // Varsayılan dönem: 6 ay
  await expect(page.getByRole("tab", { name: "6 ay" })).toHaveAttribute("aria-selected", "true");
  const half = await readIncome();

  await page.getByRole("tab", { name: "Bu ay" }).click();
  await expect(page.getByRole("tab", { name: "Bu ay" })).toHaveAttribute("aria-selected", "true");
  await expect(kpiCard(page, "Gelir")).toContainText("Bu ay");
  const month = await readIncome();

  await page.getByRole("tab", { name: "3 ay" }).click();
  await expect(page.getByRole("tab", { name: "3 ay" })).toHaveAttribute("aria-selected", "true");
  await expect(kpiCard(page, "Gelir")).toContainText("3 ay");
  const quarter = await readIncome();

  expect(half, "6 aylık gelir okunamadı").not.toBeNull();
  expect(month, "aylık gelir okunamadı").not.toBeNull();
  expect(quarter, "3 aylık gelir okunamadı").not.toBeNull();
  // Dönem daraldıkça gelir küçülmeli (tarihsel veri birikimli).
  expect(month!).toBeLessThan(quarter!);
  expect(quarter!).toBeLessThan(half!);
});

test("Öngörü kartlarında kritik stok uyarısı var", async ({ page }) => {
  const insight = page.getByRole("article").filter({ hasText: "kritik stokta" }).first();
  await expect(insight).toBeVisible();
  await expect(insight).toContainText("2 ürün kritik stokta");
  await expect(insight).toContainText("Powerbank");
  await expect(insight.getByRole("link", { name: /Tedarik ekranına git/ })).toBeVisible();
});

test("aylık gelir–gider grafiği render oluyor", async ({ page }) => {
  const card = cardByTitle(page, "Aylık gelir–gider");
  await expect(card).toBeVisible();

  const svg = card.locator("svg").first();
  await expect(svg).toBeVisible();

  // Çubuklar çizilmiş olmalı (recharts <path>/<rect> üretir).
  await expect
    .poll(async () => svg.locator("path, rect").count(), { message: "grafikte çubuk çizilmedi" })
    .toBeGreaterThan(3);

  // Efsane (legend) iki seriyi de gösteriyor.
  await expect(card.getByText("Gelir", { exact: true })).toBeVisible();
  await expect(card.getByText("Gider", { exact: true })).toBeVisible();
});
