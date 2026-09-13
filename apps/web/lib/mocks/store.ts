// Bellek içi mock API — yalnız gerçek API'ye ulaşılamadığında (fetch ağ hatası) kullanılır.
// Sözleşme davranışını taklit eder: satış stoğu düşürür, taslaklar ürün başına tekildir, approve → sent.
// Veri: lib/mocks/*.json (deterministik; teknoloji aksesuar mağazası, Nisan–Eylül 2026).

import { ApiError } from "../errors";
import type {
  AgentCheckResult,
  ApproveResult,
  AssistantAnswer,
  CashflowMonth,
  Expense,
  ExpenseByCategory,
  ExpenseInput,
  Health,
  Insight,
  ListParams,
  Order,
  OrderStatus,
  Paginated,
  Period,
  Product,
  ProductPatch,
  RejectResult,
  Sale,
  SaleInput,
  SalesByProduct,
  Summary,
} from "../types";
import expensesJson from "./expenses.json";
import insightsJson from "./insights.json";
import ordersJson from "./orders.json";
import productsJson from "./products.json";
import salesJson from "./sales.json";
import suggestionsJson from "./suggestions.json";
import suppliersJson from "./suppliers.json";

interface Supplier {
  id: number;
  name: string;
  contact_channel: "telegram" | "email";
  contact_address: string;
  lead_time_days: number;
}

type ProductRow = Omit<Product, "is_critical" | "open_order_id" | "open_order_status">;

const suppliers = suppliersJson as Supplier[];
const products: ProductRow[] = (productsJson as Product[]).map((p) => ({
  id: p.id,
  name: p.name,
  category: p.category,
  unit_cost: p.unit_cost,
  sale_price: p.sale_price,
  stock_qty: p.stock_qty,
  reorder_point: p.reorder_point,
  target_stock: p.target_stock,
  supplier_id: p.supplier_id,
}));
const sales: Sale[] = (salesJson as Sale[]).map((s) => ({ ...s }));
const expenses: Expense[] = (expensesJson as Expense[]).map((e) => ({ ...e }));
const orders: Order[] = (ordersJson as Order[]).map((o) => ({ ...o }));
const insights = insightsJson as Insight[];
const suggestions = suggestionsJson as string[];

const BUSINESS_NAME = "OtoHesap Demo Mağaza";
const OPEN: OrderStatus[] = ["draft", "approved", "sent"];

const delay = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
const nowIso = () => new Date().toISOString();
const money = (n: number) => `${new Intl.NumberFormat("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n)} ₺`;
const r2 = (n: number) => Math.round(n * 100) / 100;

/** R-17: UTC takvim ayları; month = bu ay, quarter = son 3 ay, half = son 6 ay. */
function periodStart(period: Period): Date {
  const now = new Date();
  const back = period === "month" ? 0 : period === "quarter" ? 2 : 5;
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() - back, 1));
}

function monthStartUtc(offset: number): Date {
  const now = new Date();
  return new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth() + offset, 1));
}

const inPeriod = (iso: string, period: Period) => new Date(iso) >= periodStart(period);
const monthOf = (iso: string) => iso.slice(0, 7);
const productById = (id: number) => products.find((p) => p.id === id);
const supplierById = (id: number | null) => (id === null ? undefined : suppliers.find((s) => s.id === id));
const openOrderFor = (productId: number) =>
  [...orders].sort((a, b) => b.created_at.localeCompare(a.created_at)).find((o) => o.product_id === productId && OPEN.includes(o.status));
const isCritical = (p: ProductRow) => p.stock_qty <= p.reorder_point;

function viewProduct(p: ProductRow): Product {
  const open = openOrderFor(p.id);
  return {
    ...p,
    supplier: supplierById(p.supplier_id)?.name ?? null,
    is_critical: isCritical(p),
    open_order_id: open?.id ?? null,
    open_order_status: open?.status ?? null,
  };
}

// --- sağlık ---
export function getHealth(): Health {
  return { status: "ok", db: false, llm: "mock", scheduler: false, version: "mock" };
}

// --- özet ve analitik ---
export async function getSummary(period: Period): Promise<Summary> {
  await delay(120);
  const income = sales.filter((s) => inPeriod(s.sold_at, period)).reduce((a, s) => a + s.total, 0);
  const expense = expenses.filter((e) => inPeriod(e.spent_at, period)).reduce((a, e) => a + e.amount, 0);
  return {
    income: r2(income),
    expense: r2(expense),
    net: r2(income - expense),
    critical_count: products.filter(isCritical).length,
    updated_at: nowIso(),
  };
}

export async function getCashflowMonthly(): Promise<CashflowMonth[]> {
  await delay(120);
  const map = new Map<string, { income: number; expense: number }>();
  for (const s of sales) {
    const k = monthOf(s.sold_at);
    const v = map.get(k) ?? { income: 0, expense: 0 };
    v.income += s.total;
    map.set(k, v);
  }
  for (const e of expenses) {
    const k = monthOf(e.spent_at);
    const v = map.get(k) ?? { income: 0, expense: 0 };
    v.expense += e.amount;
    map.set(k, v);
  }
  return [...map.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([month, v]) => ({ month, income: r2(v.income), expense: r2(v.expense), net: r2(v.income - v.expense) }));
}

export async function getExpensesByCategory(period: Period): Promise<ExpenseByCategory[]> {
  await delay(120);
  const map = new Map<string, number>();
  for (const e of expenses) {
    if (!inPeriod(e.spent_at, period)) continue;
    map.set(e.category, (map.get(e.category) ?? 0) + e.amount);
  }
  const total = [...map.values()].reduce((a, b) => a + b, 0);
  return [...map.entries()]
    .sort(([, a], [, b]) => b - a)
    .map(([category, amount]) => ({ category, amount: r2(amount), share: total ? Math.round((amount / total) * 1000) / 10 : 0 }));
}

export async function getSalesByProduct(period: Period, top = 5): Promise<SalesByProduct[]> {
  await delay(120);
  const map = new Map<number, SalesByProduct>();
  for (const s of sales) {
    if (!inPeriod(s.sold_at, period)) continue;
    const p = productById(s.product_id);
    if (!p) continue;
    const v = map.get(p.id) ?? { product_id: p.id, product: p.name, revenue: 0, profit: 0, qty: 0 };
    v.revenue += s.total;
    v.profit += s.qty * (s.unit_price - p.unit_cost);
    v.qty += s.qty;
    map.set(p.id, v);
  }
  return [...map.values()]
    .map((v) => ({ ...v, revenue: r2(v.revenue), profit: r2(v.profit) }))
    .sort((a, b) => b.profit - a.profit)
    .slice(0, Math.max(1, Math.min(top, 50)));
}

export async function getInsights(): Promise<Insight[]> {
  await delay(150);
  const critical = products.filter(isCritical);
  return insights.map((i) =>
    i.id === "critical_stock"
      ? {
          ...i,
          severity: critical.length ? "critical" : "info",
          title: critical.length ? `${critical.length} ürün kritik stokta` : "Stok sağlıklı",
          body: critical.length
            ? `${critical.map((p) => p.name).join(", ")} için sipariş taslağı oluşturulabilir.`
            : "Eşiğin altında ürün yok.",
        }
      : i,
  );
}

// --- listeler (en yeni önce) ---
function paginate<T>(rows: T[], params: ListParams): Paginated<T> {
  const limit = Math.max(1, Math.min(params.limit ?? 50, 200));
  const offset = Math.max(0, params.offset ?? 0);
  return { items: rows.slice(offset, offset + limit), total: rows.length };
}

const norm = (s: string) => s.toLocaleLowerCase("tr-TR");

export async function listSales(params: ListParams = {}): Promise<Paginated<Sale>> {
  await delay(150);
  const q = norm(params.q?.trim() ?? "");
  const rows = sales
    .map((s) => ({ ...s, product: productById(s.product_id)?.name ?? `Ürün #${s.product_id}` }))
    .filter((s) => !q || norm(s.product ?? "").includes(q))
    .sort((a, b) => b.sold_at.localeCompare(a.sold_at) || b.id - a.id);
  return paginate(rows, params);
}

function validateSale(input: SaleInput): ProductRow {
  const p = productById(input.product_id);
  if (!p) throw new ApiError(404, "Ürün bulunamadı.");
  if (!Number.isInteger(input.qty) || input.qty < 1) throw new ApiError(422, "Miktar 1 veya daha büyük olmalı.");
  if (!(input.unit_price > 0)) throw new ApiError(422, "Birim fiyat 0'dan büyük olmalı.");
  if (input.channel !== "magaza" && input.channel !== "online") throw new ApiError(422, "Kanal magaza veya online olmalı.");
  return p;
}

export async function createSale(input: SaleInput): Promise<Sale> {
  await delay(250);
  const p = validateSale(input);
  if (p.stock_qty < input.qty) throw new ApiError(409, `Yetersiz stok: ${p.name} için ${p.stock_qty} adet var.`);
  p.stock_qty -= input.qty;
  const sale: Sale = {
    id: Math.max(0, ...sales.map((s) => s.id)) + 1,
    sold_at: input.sold_at,
    product_id: p.id,
    qty: input.qty,
    unit_price: input.unit_price,
    total: r2(input.qty * input.unit_price),
    channel: input.channel,
  };
  sales.push(sale);
  return { ...sale, product: p.name };
}

export async function updateSale(id: number, input: SaleInput): Promise<Sale> {
  await delay(250);
  const sale = sales.find((s) => s.id === id);
  if (!sale) throw new ApiError(404, "Satış kaydı bulunamadı.");
  const p = validateSale(input);
  const old = productById(sale.product_id);
  if (old) old.stock_qty += sale.qty; // iade
  if (p.stock_qty < input.qty) {
    if (old) old.stock_qty -= sale.qty;
    throw new ApiError(409, `Yetersiz stok: ${p.name} için ${p.stock_qty} adet var.`);
  }
  p.stock_qty -= input.qty;
  Object.assign(sale, { ...input, total: r2(input.qty * input.unit_price) });
  return { ...sale, product: p.name };
}

export async function deleteSale(id: number): Promise<void> {
  await delay(200);
  const i = sales.findIndex((s) => s.id === id);
  if (i < 0) throw new ApiError(404, "Satış kaydı bulunamadı.");
  const p = productById(sales[i].product_id);
  if (p) p.stock_qty += sales[i].qty;
  sales.splice(i, 1);
}

export async function listExpenses(params: ListParams = {}): Promise<Paginated<Expense>> {
  await delay(150);
  const q = norm(params.q?.trim() ?? "");
  const rows = expenses
    .filter((e) => !q || [e.category, e.vendor ?? "", e.note ?? ""].some((f) => norm(f).includes(q)))
    .sort((a, b) => b.spent_at.localeCompare(a.spent_at) || b.id - a.id);
  return paginate(rows, params);
}

function validateExpense(input: ExpenseInput): void {
  if (!(input.amount > 0)) throw new ApiError(422, "Tutar 0'dan büyük olmalı.");
  if (!input.category?.trim()) throw new ApiError(422, "Kategori kira, maas, elektrik, kargo, reklam veya tedarik olmalı.");
}

export async function createExpense(input: ExpenseInput): Promise<Expense> {
  await delay(250);
  validateExpense(input);
  const expense: Expense = { id: Math.max(0, ...expenses.map((e) => e.id)) + 1, ...input, amount: r2(input.amount) };
  expenses.push(expense);
  return { ...expense };
}

export async function updateExpense(id: number, input: ExpenseInput): Promise<Expense> {
  await delay(250);
  const expense = expenses.find((e) => e.id === id);
  if (!expense) throw new ApiError(404, "Gider kaydı bulunamadı.");
  validateExpense(input);
  Object.assign(expense, { ...input, amount: r2(input.amount) });
  return { ...expense };
}

export async function deleteExpense(id: number): Promise<void> {
  await delay(200);
  const i = expenses.findIndex((e) => e.id === id);
  if (i < 0) throw new ApiError(404, "Gider kaydı bulunamadı.");
  expenses.splice(i, 1);
}

// --- ürünler ---
export async function getProducts(): Promise<Product[]> {
  await delay(150);
  return [...products].sort((a, b) => a.name.localeCompare(b.name, "tr")).map(viewProduct);
}

export async function patchProduct(id: number, patch: ProductPatch): Promise<Product> {
  await delay(200);
  const p = productById(id);
  if (!p) throw new ApiError(404, "Ürün bulunamadı.");
  const entries = Object.entries(patch).filter(([, v]) => v !== undefined) as [keyof ProductPatch, number][];
  if (!entries.length) throw new ApiError(422, "En az bir alan gönderilmeli.");
  if (entries.some(([, v]) => !Number.isInteger(v) || v < 0)) throw new ApiError(422, "Değerler 0 veya daha büyük olmalı.");
  for (const [k, v] of entries) p[k] = v;
  return viewProduct(p);
}

// --- asistan ---
export function getSuggestions(): string[] {
  return [...suggestions];
}

type Answer = Omit<AssistantAnswer, "asked_at" | "cached">;

function bankAnswer(q: string): Answer | null {
  const monthly = (start: Date, end: Date) => ({
    sales: sales.filter((s) => new Date(s.sold_at) >= start && new Date(s.sold_at) < end),
    expenses: expenses.filter((e) => new Date(e.spent_at) >= start && new Date(e.spent_at) < end),
  });

  if (q.includes("en çok kazanc")) {
    const rows = [...(productProfitRows())].slice(0, 5);
    const top = rows[0];
    return {
      answer: top
        ? `En yüksek tahmini brüt katkı ${top[0]} ürününden: ${money(top[1] as number)} (${top[2]} adet). Mevcut birim maliyetle hesaplanmıştır.`
        : "Bu soru için kayıt bulunamadı.",
      sql: "SELECT p.name AS urun, SUM(s.qty*(s.unit_price-p.unit_cost)) AS kar, SUM(s.qty) AS adet FROM sales s JOIN products p ON p.id=s.product_id GROUP BY p.name ORDER BY kar DESC LIMIT 5",
      columns: ["urun", "kar", "adet"],
      rows,
      sources: ["sales", "products"],
    };
  }
  if (q.includes("bu ay") && q.includes("gider")) {
    const { expenses: rows } = monthly(monthStartUtc(0), monthStartUtc(1));
    const total = r2(rows.reduce((a, e) => a + e.amount, 0));
    return {
      answer: `Bu ay toplam gider: ${money(total)} (${rows.length} kayıt).`,
      sql: "SELECT COALESCE(SUM(amount), 0) AS bu_ay_gider FROM expenses WHERE spent_at >= date_trunc('month', now()) AND spent_at < date_trunc('month', now()) + interval '1 month'",
      columns: ["bu_ay_gider"],
      rows: [[total]],
      sources: ["expenses"],
    };
  }
  if (q.includes("son 3 ay")) {
    const rows: unknown[][] = [];
    for (let i = -2; i <= 0; i++) {
      const start = monthStartUtc(i);
      const { sales: s, expenses: e } = monthly(start, monthStartUtc(i + 1));
      const inc = r2(s.reduce((a, x) => a + x.total, 0));
      const exp = r2(e.reduce((a, x) => a + x.amount, 0));
      rows.push([start.toISOString().slice(0, 7), inc, exp, r2(inc - exp)]);
    }
    const last = rows[rows.length - 1];
    return {
      answer: `Son 3 ayın gelir–gider farkı: ${rows.map((r) => `${r[0]}: ${money(r[3] as number)}`).join(", ")}. Son ay (${last[0]}) henüz tamamlanmadı.`,
      sql: "SELECT to_char(month, 'YYYY-MM') AS ay, income AS gelir, expense AS gider, net AS fark FROM v_monthly_cashflow WHERE month >= date_trunc('month', now()) - interval '2 months' ORDER BY month",
      columns: ["ay", "gelir", "gider", "fark"],
      rows,
      sources: ["v_monthly_cashflow"],
    };
  }
  if (q.includes("en çok gider") && q.includes("kategori")) {
    const map = new Map<string, number>();
    for (const e of expenses) map.set(e.category, (map.get(e.category) ?? 0) + e.amount);
    const [cat, amount] = [...map.entries()].sort(([, a], [, b]) => b - a)[0] ?? ["—", 0];
    return {
      answer: `En çok gider "${cat}" kategorisinde: ${money(r2(amount))}.`,
      sql: "SELECT category AS kategori, SUM(amount) AS toplam_gider FROM expenses GROUP BY category ORDER BY toplam_gider DESC LIMIT 1",
      columns: ["kategori", "toplam_gider"],
      rows: [[cat, r2(amount)]],
      sources: ["expenses"],
    };
  }
  if (q.includes("kritik stok")) {
    const rows = products
      .filter(isCritical)
      .sort((a, b) => a.name.localeCompare(b.name, "tr"))
      .map((p) => [p.name, p.stock_qty, p.reorder_point, p.target_stock]);
    return {
      answer: rows.length
        ? `${rows.length} ürün kritik stokta: ${rows.map((r) => `${r[0]} (${r[1]} adet)`).join(", ")}.`
        : "Kritik stokta ürün yok.",
      sql: "SELECT name AS urun, stock_qty AS stok, reorder_point AS esik, target_stock AS hedef FROM products WHERE stock_qty <= reorder_point ORDER BY name",
      columns: ["urun", "stok", "esik", "hedef"],
      rows,
      sources: ["products"],
    };
  }
  if (q.includes("online") && q.includes("mağaza")) {
    const map = new Map<string, { n: number; inc: number }>();
    for (const s of sales) {
      const v = map.get(s.channel) ?? { n: 0, inc: 0 };
      v.n += 1;
      v.inc += s.total;
      map.set(s.channel, v);
    }
    const rows = [...map.entries()].sort(([, a], [, b]) => b.inc - a.inc).map(([k, v]) => [k, v.n, r2(v.inc)]);
    return {
      answer: rows.map((r) => `${r[0]}: ${r[1]} işlem, ${money(r[2] as number)}`).join(" · ") + ".",
      sql: "SELECT channel AS kanal, COUNT(*) AS islem_sayisi, SUM(total) AS gelir FROM sales GROUP BY channel ORDER BY gelir DESC",
      columns: ["kanal", "islem_sayisi", "gelir"],
      rows,
      sources: ["sales"],
    };
  }
  if (q.includes("geçen ay") && q.includes("satış")) {
    const { sales: rows } = monthly(monthStartUtc(-1), monthStartUtc(0));
    const inc = r2(rows.reduce((a, s) => a + s.total, 0));
    return {
      answer: `Geçen ay ${rows.length} satış işlemi, toplam ${money(inc)} gelir.`,
      sql: "SELECT COUNT(*) AS islem_sayisi, COALESCE(SUM(total), 0) AS gelir FROM sales WHERE sold_at >= date_trunc('month', now()) - interval '1 month' AND sold_at < date_trunc('month', now())",
      columns: ["islem_sayisi", "gelir"],
      rows: [[rows.length, inc]],
      sources: ["sales"],
    };
  }
  if (q.includes("kategori bazında") && q.includes("satış")) {
    const map = new Map<string, { inc: number; qty: number }>();
    for (const s of sales) {
      const p = productById(s.product_id);
      if (!p) continue;
      const v = map.get(p.category) ?? { inc: 0, qty: 0 };
      v.inc += s.total;
      v.qty += s.qty;
      map.set(p.category, v);
    }
    const rows = [...map.entries()].sort(([, a], [, b]) => b.inc - a.inc).map(([k, v]) => [k, r2(v.inc), v.qty]);
    return {
      answer: rows.length ? `En yüksek gelir "${rows[0][0]}" kategorisinden: ${money(rows[0][1] as number)}.` : "Bu soru için kayıt bulunamadı.",
      sql: "SELECT p.category AS kategori, SUM(s.total) AS gelir, SUM(s.qty) AS adet FROM sales s JOIN products p ON p.id = s.product_id GROUP BY p.category ORDER BY gelir DESC",
      columns: ["kategori", "gelir", "adet"],
      rows,
      sources: ["sales", "products"],
    };
  }
  if (q.includes("aralık 2026")) {
    return {
      answer: "Bu soru için kayıt bulunamadı.",
      sql: "SELECT COALESCE(SUM(amount), 0) AS gider FROM expenses WHERE spent_at >= '2026-12-01' AND spent_at < '2027-01-01'",
      columns: ["gider"],
      rows: [],
      sources: ["expenses"],
    };
  }
  return null;
}

function productProfitRows(): unknown[][] {
  const map = new Map<number, { name: string; profit: number; qty: number }>();
  for (const s of sales) {
    const p = productById(s.product_id);
    if (!p) continue;
    const v = map.get(p.id) ?? { name: p.name, profit: 0, qty: 0 };
    v.profit += s.qty * (s.unit_price - p.unit_cost);
    v.qty += s.qty;
    map.set(p.id, v);
  }
  return [...map.values()].sort((a, b) => b.profit - a.profit).map((v) => [v.name, r2(v.profit), v.qty]);
}

const ATTACK = /\b(sil|delete|drop|update|insert|truncate|alter|şifre|parola|password)\b/i;

export async function askAssistant(question: string): Promise<AssistantAnswer> {
  await delay(700);
  const trimmed = question.trim();
  if (!trimmed) throw new ApiError(422, "Soru boş olamaz.");
  if (trimmed.length > 500) throw new ApiError(422, "Soru en fazla 500 karakter olabilir.");
  if (ATTACK.test(trimmed)) throw new ApiError(400, "Asistan yalnızca okuma sorguları çalıştırır; bu istek reddedildi.");

  const q = norm(trimmed);
  const found = bankAnswer(q);
  const cached = suggestions.some((s) => norm(s) === q);
  if (found) return { ...found, asked_at: nowIso(), cached, ok: true, model: "mock" };
  return {
    answer: "Bu soruyu bu veriyle yanıtlayamadım.",
    sql: "",
    rows: [],
    columns: [],
    sources: [],
    asked_at: nowIso(),
    cached: false,
    ok: false,
    model: "mock",
  };
}

// --- tedarik ajanı ve siparişler ---
function messageFor(p: ProductRow, s: Supplier, qty: number, est: number): string {
  return `Merhaba ${s.name}, OtoHesap üzerinden sipariş talebi: ${p.name} × ${qty} adet. Tahmini tutar ${money(est)}. Teslim: ${s.lead_time_days} gün. Onay için yanıtlayabilirsiniz. — ${BUSINESS_NAME}`;
}

export async function agentCheck(): Promise<AgentCheckResult> {
  await delay(500);
  const drafts: Order[] = [];
  for (const p of products) {
    if (!isCritical(p) || openOrderFor(p.id)) continue;
    const s = supplierById(p.supplier_id);
    if (!s) continue; // tedarikçisi yok → atla
    const qty = Math.max(1, p.target_stock - p.stock_qty);
    const est = r2(qty * p.unit_cost);
    const order: Order = {
      id: Math.max(0, ...orders.map((o) => o.id)) + 1,
      created_at: nowIso(),
      product_id: p.id,
      product: p.name,
      supplier_id: s.id,
      supplier: s.name,
      supplier_channel: s.contact_channel,
      qty,
      est_amount: est,
      status: "draft",
      message_text: messageFor(p, s, qty, est),
      sent_at: null,
      notify_ref: null,
    };
    orders.push(order);
    drafts.push({ ...order });
  }
  return { created: drafts.length, drafts };
}

export async function listOrders(status?: OrderStatus): Promise<Order[]> {
  await delay(150);
  return orders
    .filter((o) => !status || o.status === status)
    .sort((a, b) => b.created_at.localeCompare(a.created_at) || b.id - a.id)
    .map((o) => ({ ...o }));
}

export async function approveOrder(id: number): Promise<ApproveResult> {
  await delay(700);
  const o = orders.find((x) => x.id === id);
  if (!o) throw new ApiError(404, "Sipariş bulunamadı.");
  if (o.status === "sent") throw new ApiError(409, "Sipariş zaten gönderilmiş.");
  if (o.status === "rejected") throw new ApiError(409, "Reddedilmiş sipariş onaylanamaz.");
  o.status = "sent";
  o.sent_at = nowIso();
  o.notify_ref = `sim:${o.id}`;
  return {
    id: o.id,
    status: "sent",
    sent_at: o.sent_at,
    simulated: true,
    notify: { ok: true, dry_run: true, channel: o.supplier_channel ?? "telegram", message_id: null },
    order: { ...o },
  };
}

export async function rejectOrder(id: number): Promise<RejectResult> {
  await delay(300);
  const o = orders.find((x) => x.id === id);
  if (!o) throw new ApiError(404, "Sipariş bulunamadı.");
  if (o.status === "sent") throw new ApiError(409, "Gönderilmiş sipariş reddedilemez.");
  if (o.status === "rejected") throw new ApiError(409, "Sipariş zaten reddedilmiş.");
  o.status = "rejected";
  return { id: o.id, status: "rejected", order: { ...o } };
}
