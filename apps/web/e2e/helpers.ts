import { expect, request, type APIRequestContext, type Locator, type Page } from "@playwright/test";
import { API_URL } from "../playwright.config";

export { API_URL };

// ------------------------------------------------------------------ API (kurulum/temizlik)

/** Testlerin kurulum/temizlik adımları için doğrudan API istemcisi (arayüzden bağımsız). */
export async function apiContext(): Promise<APIRequestContext> {
  return request.newContext({ baseURL: API_URL, extraHTTPHeaders: { Accept: "application/json" } });
}

export interface ApiProduct {
  id: number;
  name: string;
  category: string;
  stock_qty: number;
  reorder_point: number;
  target_stock: number;
  unit_cost: number;
  sale_price: number;
  is_critical: boolean;
  supplier_id: number | null;
  open_order_id: number | null;
}

export interface ApiOrder {
  id: number;
  product_id: number;
  product_name: string;
  status: "draft" | "approved" | "sent" | "rejected";
}

export async function getProducts(api: APIRequestContext): Promise<ApiProduct[]> {
  const res = await api.get("/api/products");
  expect(res.ok(), `GET /api/products başarısız (${res.status()})`).toBeTruthy();
  return (await res.json()) as ApiProduct[];
}

export async function getOrders(api: APIRequestContext, status: ApiOrder["status"]): Promise<ApiOrder[]> {
  const res = await api.get(`/api/orders?status=${status}`);
  expect(res.ok(), `GET /api/orders?status=${status} başarısız (${res.status()})`).toBeTruthy();
  return (await res.json()) as ApiOrder[];
}

/** Bekleyen (draft + approved) siparişleri reddeder; reddedilenler bir sonraki kontrolde yeniden taslağa düşer. */
export async function rejectPendingOrders(api: APIRequestContext): Promise<number> {
  const pending = [...(await getOrders(api, "draft")), ...(await getOrders(api, "approved"))];
  for (const order of pending) {
    const res = await api.post(`/api/orders/${order.id}/reject`);
    // 409 = başka bir adım durumu değiştirmiş; temizlikte sorun değil.
    expect([200, 409]).toContain(res.status());
  }
  return pending.length;
}

export async function patchProduct(api: APIRequestContext, id: number, patch: Record<string, number>): Promise<void> {
  const res = await api.patch(`/api/products/${id}`, { data: patch });
  expect(res.ok(), `PATCH /api/products/${id} başarısız (${res.status()})`).toBeTruthy();
}

// ------------------------------------------------------------------ biçim

/** "1.109.509,10 ₺" → 1109509.1 ; sayı bulunamazsa null. */
export function parseMoney(text: string | null | undefined): number | null {
  if (!text) return null;
  const m = /-?[\d.]+,\d{2}|-?\d[\d.]*/.exec(text.replace(/\s/g, ""));
  if (!m) return null;
  const n = Number(m[0].replace(/\./g, "").replace(",", "."));
  return Number.isFinite(n) ? n : null;
}

// ------------------------------------------------------------------ ortak seçiciler (Türkçe metinlere göre)

/** KPI kartı: etiket metninin (tam eşleşme) üst kutusu. */
export function kpiCard(page: Page, label: string): Locator {
  return page.getByText(label, { exact: true }).first().locator("xpath=..");
}

/** KPI kartının değer satırı (etiketten sonraki kutu). */
export function kpiValue(page: Page, label: string): Locator {
  return kpiCard(page, label).locator("xpath=./div[2]");
}

/** Başlığına göre kart (section) bulur: <section><header><h2>Başlık</h2>… */
export function cardByTitle(page: Page, title: string): Locator {
  return page.locator("section").filter({ has: page.getByRole("heading", { name: title, exact: true }) });
}

/** Sayfanın veri yüklediğini ve gerçek API'ye bağlı olduğunu doğrular (mock rozeti yok). */
export async function expectLiveApi(page: Page): Promise<void> {
  await expect(page.getByText("mock veri")).toHaveCount(0);
  await expect(page.getByText("API bağlı")).toBeVisible();
}

/** Yatay kaydırma olmamalı (1 px tolerans; alt öğeler kendi içinde kayabilir). */
export async function expectNoHorizontalScroll(page: Page): Promise<void> {
  const overflow = await page.evaluate(() => {
    const el = document.documentElement;
    return { scrollWidth: el.scrollWidth, clientWidth: el.clientWidth };
  });
  expect(
    overflow.scrollWidth,
    `sayfa yatay kayıyor: scrollWidth=${overflow.scrollWidth} clientWidth=${overflow.clientWidth}`,
  ).toBeLessThanOrEqual(overflow.clientWidth + 1);
}

// ------------------------------------------------------------------ konsol gözlemi

/** Tarayıcı konsolu ve yakalanmamış hatalar. Gürültü (uzantı, favicon) elenir. */
const IGNORED_CONSOLE = [
  /favicon\.ico/i,
  /Download the React DevTools/i,
  /\[Fast Refresh\]/i,
  /Extra attributes from the server/i,
];

export function collectPageErrors(page: Page): string[] {
  const errors: string[] = collectUncaughtErrors(page);
  page.on("console", (msg) => {
    if (msg.type() !== "error") return;
    const text = msg.text();
    if (IGNORED_CONSOLE.some((re) => re.test(text))) return;
    errors.push(`console.error: ${text}`);
  });
  return errors;
}

/** Yalnız yakalanmamış JavaScript hataları (beklenen 4xx yanıtları konsola hata yazar; onlar sayılmaz). */
export function collectUncaughtErrors(page: Page): string[] {
  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(`pageerror: ${err.message}`));
  return errors;
}
