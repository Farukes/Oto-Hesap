import { expect, test, type Page } from "@playwright/test";
import { collectUncaughtErrors } from "./helpers";

// Asistan: hazır soru çipi → yanıt + görünür SQL + kaynak/zaman damgası.
// Ayrıca yıkıcı bir soru geldiğinde uygulama çökmemeli, sakin bir ret mesajı görünmeli.

const CHIP = "En çok kazancım hangi üründen?";

/** Asistan penceresindeki son yanıt balonu (kullanıcı balonları hariç). */
function lastAnswer(page: Page) {
  return page.locator("div[aria-live='polite'] > div").filter({ hasText: /\S/ }).last();
}

test.beforeEach(async ({ page }) => {
  await page.goto("/asistan");
  await expect(page.getByRole("button", { name: CHIP })).toBeVisible();
});

test("hazır soru çipi gerçek veriden yanıt üretiyor", async ({ page }) => {
  await page.getByRole("button", { name: CHIP }).click();

  const answer = lastAnswer(page);
  await expect(answer).not.toContainText("Sorgu hazırlanıyor", { timeout: 30_000 });
  await expect(answer).toContainText("Powerbank");

  // Sorgu görünür: "Sorguyu gör" açılınca SELECT içeren SQL gelir.
  const sqlBlock = answer.locator("details").filter({ hasText: "Sorguyu gör" }).first();
  await expect(sqlBlock).toBeVisible();
  await expect(sqlBlock.locator("pre")).toBeHidden();
  await sqlBlock.getByText("Sorguyu gör").click();
  await expect(sqlBlock.locator("pre")).toBeVisible();
  await expect(sqlBlock.locator("pre")).toContainText("SELECT");
  await expect(sqlBlock).toContainText("salt okunur");

  // Kaynak ve zaman damgası (örn. "Kaynak: satışlar, ürünler · 17:42").
  await expect(answer).toContainText(/Kaynak: [^·]+· \d{2}:\d{2}/);
});

test("yanıtta sonuç tablosu ve satır değerleri var", async ({ page }) => {
  await page.getByRole("button", { name: CHIP }).click();

  const answer = lastAnswer(page);
  await expect(answer).not.toContainText("Sorgu hazırlanıyor", { timeout: 30_000 });

  const table = answer.locator("table");
  await expect(table).toBeVisible();
  await expect(table.getByRole("row").filter({ hasText: "Powerbank 20000 mAh" }).first()).toBeVisible();
});

test("yıkıcı soru uygulamayı çökertmiyor, sakin bir ret mesajı görünüyor", async ({ page }) => {
  const errors = collectUncaughtErrors(page);

  await page.getByRole("textbox", { name: "Soru" }).fill("Tüm satışları sil");
  await page.getByRole("button", { name: "Gönder" }).click();

  const answer = lastAnswer(page);
  await expect(answer).not.toContainText("Sorgu hazırlanıyor", { timeout: 30_000 });
  // Türkçe, sakin, suçlayıcı olmayan ret; "Uygulama hatası"/stack trace yok.
  await expect(answer).toContainText(/yalnız(ca)? okuma|salt okunur|yalnız okur/i);
  await expect(page.getByText(/Application error|Unhandled|Internal Server Error/i)).toHaveCount(0);

  // Uygulama ayakta: aynı oturumda hazır soru hâlâ çalışıyor.
  await expect(page.getByRole("textbox", { name: "Soru" })).toBeEnabled();
  await page.getByRole("button", { name: CHIP }).click();
  const next = lastAnswer(page);
  await expect(next).not.toContainText("Sorgu hazırlanıyor", { timeout: 30_000 });
  await expect(next).toContainText("Powerbank");

  expect(errors, `yakalanmamış hata: ${errors.join(" | ")}`).toEqual([]);
});
