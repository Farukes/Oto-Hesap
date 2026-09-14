import { expect, test } from "@playwright/test";
import { collectPageErrors, expectLiveApi } from "./helpers";

// Beş sayfa açılıyor mu: başlık doğru, veri geldi, konsol temiz, "mock veri" rozeti yok.

interface PageCase {
  path: string;
  heading: string;
  title: string;
  /** Sayfanın gerçekten veri yüklediğini gösteren metin. */
  ready: string | RegExp;
}

const PAGES: PageCase[] = [
  { path: "/", heading: "Genel Bakış", title: "OtoHesap", ready: /Son güncelleme/ },
  { path: "/kayitlar", heading: "Kayıtlar", title: "Kayıtlar · OtoHesap", ready: /\d+ kayıt/ },
  { path: "/stok", heading: "Stok", title: "Stok · OtoHesap", ready: "Eşik ve hedef stok hücreleri tıklanarak düzenlenir" },
  { path: "/asistan", heading: "Asistan", title: "Asistan · OtoHesap", ready: "En çok kazancım hangi üründen?" },
  { path: "/tedarik", heading: "Tedarik", title: "Tedarik · OtoHesap", ready: "Onay bekleyen taslaklar" },
];

for (const p of PAGES) {
  test(`${p.path} açılıyor, başlığı doğru ve konsol temiz`, async ({ page }) => {
    const errors = collectPageErrors(page);

    await page.goto(p.path);

    await expect(page.getByRole("heading", { level: 1, name: p.heading })).toBeVisible();
    await expect(page).toHaveTitle(p.title);
    await expect(page.getByText(p.ready).first()).toBeVisible();

    // Gerçek API'ye bağlı: "mock veri" rozeti hiçbir yerde görünmemeli.
    await expectLiveApi(page);

    expect(errors, `konsol hataları: ${errors.join(" | ")}`).toEqual([]);
  });
}

test("kenar menü beş sayfayı da geziyor", async ({ page }) => {
  await page.goto("/");
  const nav = page.getByRole("navigation").or(page.locator("aside")).first();

  for (const p of PAGES.slice(1)) {
    await nav.getByRole("link", { name: p.heading }).click();
    await expect(page).toHaveURL(new RegExp(`${p.path}$`));
    await expect(page.getByRole("heading", { level: 1, name: p.heading })).toBeVisible();
  }
});
