import { expect, test, type APIRequestContext, type Page } from "@playwright/test";
import { apiContext, kpiValue, parseMoney } from "./helpers";

// Kayıtlar: gider ekle → listede gör → Genel Bakış'ta Gider KPI'ı artsın → kaydı sil (temizlik).
// Ayrıca satış aramasının ürün adına göre filtrelediği doğrulanır.

test.describe.configure({ mode: "serial" });

const VENDOR = `E2E ${Date.now()}`;
const AMOUNT = 4500;

let api: APIRequestContext;

test.beforeAll(async () => {
  api = await apiContext();
});

// Güvenlik ağı: test yarıda kalsa bile eklenen gider veritabanında kalmasın.
test.afterAll(async () => {
  if (!api) return;
  const res = await api.get(`/api/expenses?limit=50&q=${encodeURIComponent(VENDOR)}`);
  if (res.ok()) {
    const body = (await res.json()) as { items: { id: number; vendor: string | null }[] };
    for (const item of body.items.filter((i) => i.vendor === VENDOR)) {
      await api.delete(`/api/expenses/${item.id}`);
    }
  }
  await api.dispose();
});

async function openExpensesTab(page: Page): Promise<void> {
  await page.goto("/kayitlar");
  await page.getByRole("tab", { name: "Gider" }).click();
  await expect(page.getByRole("button", { name: "Yeni gider" }).first()).toBeVisible();
}

test("gider ekleme Genel Bakış'a yansıyor, silince geri alınıyor", async ({ page }) => {
  // --- 1) Eklemeden önce Gider KPI'ı ---
  await page.goto("/");
  const gider = kpiValue(page, "Gider");
  await expect(gider).toHaveText(/₺/);
  const before = parseMoney(await gider.textContent());
  expect(before, "Gider KPI'ı okunamadı").not.toBeNull();

  // --- 2) Kayıtlar → Gider → Yeni gider (kategori: reklam, tutar: 4.500) ---
  await openExpensesTab(page);
  await page.getByRole("button", { name: "Yeni gider" }).first().click();

  const form = page.getByRole("dialog");
  await expect(form).toBeVisible();
  await form.getByLabel("Kategori", { exact: true }).selectOption("reklam");
  await form.getByLabel("Tutar (₺)").fill(String(AMOUNT));
  await form.getByLabel("Tedarikçi / satıcı").fill(VENDOR);
  await form.getByRole("button", { name: "Gideri kaydet" }).click();
  await expect(form).toBeHidden();
  await expect(page.getByText("Gider kaydedildi.")).toBeVisible();

  // --- 3) Listede görünüyor ---
  const row = page.getByRole("row").filter({ hasText: VENDOR });
  await expect(row).toHaveCount(1);
  await expect(row).toContainText("Reklam");
  await expect(row).toContainText("4.500,00 ₺");

  // --- 4) Genel Bakış'ta Gider KPI'ı arttı ---
  await page.goto("/");
  await expect(gider).toHaveText(/₺/);
  await expect
    .poll(async () => parseMoney(await gider.textContent()), { message: "Gider KPI'ı güncellenmedi" })
    .toBeGreaterThan(before!);
  const after = parseMoney(await gider.textContent());
  expect(after! - before!).toBeCloseTo(AMOUNT, 1);

  // --- 5) Temizlik: eklenen gideri sil ---
  await openExpensesTab(page);
  const toDelete = page.getByRole("row").filter({ hasText: VENDOR });
  await toDelete.getByRole("button", { name: "Sil" }).click();

  const confirm = page.getByRole("dialog");
  await expect(confirm).toContainText("Bu işlem geri alınamaz");
  await confirm.getByRole("button", { name: "Sil", exact: true }).click();
  await expect(page.getByText("Gider silindi.")).toBeVisible();
  await expect(page.getByRole("row").filter({ hasText: VENDOR })).toHaveCount(0);

  // Genel Bakış eski değerine döndü.
  await page.goto("/");
  await expect
    .poll(async () => parseMoney(await gider.textContent()), { message: "Gider KPI'ı eski değerine dönmedi" })
    .toBeCloseTo(before!, 1);
});

test("arama kutusu satışları ürün adıyla filtreliyor", async ({ page }) => {
  await page.goto("/kayitlar");

  const counter = page.getByText(/\d+ kayıt/).first();
  await expect(counter).toBeVisible();
  const total = parseMoney(await counter.textContent());
  expect(total, "toplam kayıt sayısı okunamadı").not.toBeNull();

  await page.getByLabel("Satışlarda ara").fill("Powerbank 20000");

  await expect.poll(async () => parseMoney(await counter.textContent()), { message: "arama sonucu değişmedi" }).toBeLessThan(total!);
  const filtered = parseMoney(await counter.textContent());
  expect(filtered!).toBeGreaterThan(0);

  const rows = await page.locator("tbody tr").allInnerTexts();
  expect(rows.length).toBeGreaterThan(0);
  for (const text of rows) {
    expect(text, "filtre dışı satır listelendi").toContain("Powerbank 20000");
  }

  // Eşleşmeyen arama boş durum metnini gösteriyor.
  await page.getByLabel("Satışlarda ara").fill("zzz-eslesme-yok");
  await expect(page.getByText("Eşleşen satış yok")).toBeVisible();
});
