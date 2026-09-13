// Tipli API istemcisi — AGENTS.md §6 sözleşmesi.
// API'ye ulaşılamazsa (fetch ağ hatası) lib/mocks/store.ts yanıt verir ve "mock veri" rozeti açılır.
// HTTP hataları (4xx/5xx) mock'a DÜŞMEZ; ApiError olarak fırlatılır (detail Türkçe).

import { ApiError } from "./errors";
import { setMockMode } from "./mock-mode";
import * as mock from "./mocks/store";
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
} from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/+$/, "");

export { ApiError, errorMessage, errorStatus } from "./errors";

function defaultDetail(status: number): string {
  if (status === 404) return "Bu uç henüz hazır değil (404).";
  if (status === 409) return "Bu işlem daha önce yapılmış (409).";
  if (status === 422) return "Gönderilen alanlar geçersiz (422).";
  if (status === 502) return "Mesaj gönderilemedi; tekrar deneyin (502).";
  if (status === 503) return "Servis şu an kullanılamıyor; biraz sonra tekrar deneyin (503).";
  if (status >= 500) return "Sunucu hatası; lütfen tekrar deneyin.";
  return `İstek başarısız (${status}).`;
}

async function readDetail(res: Response): Promise<string> {
  try {
    const body: unknown = await res.json();
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string") return detail === "Not Found" ? defaultDetail(404) : detail;
      if (Array.isArray(detail)) {
        const msgs = detail
          .map((d) => (d && typeof d === "object" && "msg" in d ? String((d as { msg: unknown }).msg) : ""))
          .filter(Boolean);
        if (msgs.length) return msgs.join("; ");
      }
    }
  } catch {
    // gövde JSON değil
  }
  return defaultDetail(res.status);
}

function qs(params: object): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params as Record<string, unknown>)) {
    if (v === undefined || v === null || v === "") continue;
    sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function request<T>(path: string, init: RequestInit | undefined, fallback: () => T | Promise<T>): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init?.body ? { "Content-Type": "application/json" } : {}),
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    // Ağ hatası: API kapalı / ulaşılamıyor → mock
    setMockMode(true);
    return fallback();
  }
  setMockMode(false);
  if (!res.ok) throw new ApiError(res.status, await readDetail(res));
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

const json = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });

// --- sağlık ---
export const getHealth = () => request<Health>("/api/health", undefined, mock.getHealth);

// --- özet ve analitik ---
export const getSummary = (period: Period) =>
  request<Summary>(`/api/summary${qs({ period })}`, undefined, () => mock.getSummary(period));

export const getCashflowMonthly = () => request<CashflowMonth[]>("/api/cashflow/monthly", undefined, mock.getCashflowMonthly);

export const getExpensesByCategory = (period: Period) =>
  request<ExpenseByCategory[]>(`/api/analytics/expenses-by-category${qs({ period })}`, undefined, () =>
    mock.getExpensesByCategory(period),
  );

export const getSalesByProduct = (period: Period, top?: number) =>
  request<SalesByProduct[]>(`/api/analytics/sales-by-product${qs({ period, top })}`, undefined, () =>
    mock.getSalesByProduct(period, top),
  );

// --- öngörüler (sözleşme önerisi; boş dizi → kart gizli) ---
export const getInsights = () => request<Insight[]>("/api/insights", undefined, mock.getInsights);

// --- satışlar ---
export const listSales = (params: ListParams = {}) =>
  request<Paginated<Sale>>(`/api/sales${qs(params)}`, undefined, () => mock.listSales(params));
export const createSale = (input: SaleInput) => request<Sale>("/api/sales", json(input), () => mock.createSale(input));
export const updateSale = (id: number, input: SaleInput) =>
  request<Sale>(`/api/sales/${id}`, { method: "PUT", body: JSON.stringify(input) }, () => mock.updateSale(id, input));
export const deleteSale = (id: number) => request<void>(`/api/sales/${id}`, { method: "DELETE" }, () => mock.deleteSale(id));

// --- giderler ---
export const listExpenses = (params: ListParams = {}) =>
  request<Paginated<Expense>>(`/api/expenses${qs(params)}`, undefined, () => mock.listExpenses(params));
export const createExpense = (input: ExpenseInput) =>
  request<Expense>("/api/expenses", json(input), () => mock.createExpense(input));
export const updateExpense = (id: number, input: ExpenseInput) =>
  request<Expense>(`/api/expenses/${id}`, { method: "PUT", body: JSON.stringify(input) }, () =>
    mock.updateExpense(id, input),
  );
export const deleteExpense = (id: number) =>
  request<void>(`/api/expenses/${id}`, { method: "DELETE" }, () => mock.deleteExpense(id));

// --- ürünler ---
export const getProducts = () => request<Product[]>("/api/products", undefined, mock.getProducts);
export const patchProduct = (id: number, patch: ProductPatch) =>
  request<Product>(`/api/products/${id}`, { method: "PATCH", body: JSON.stringify(patch) }, () =>
    mock.patchProduct(id, patch),
  );

// --- asistan ---
export const askAssistant = (question: string) =>
  request<AssistantAnswer>("/api/assistant/ask", json({ question }), () => mock.askAssistant(question));
export const getSuggestions = () => request<string[]>("/api/assistant/suggestions", undefined, mock.getSuggestions);

// --- tedarik ajanı ve siparişler ---
export const agentCheck = () => request<AgentCheckResult>("/api/agent/check", { method: "POST" }, mock.agentCheck);
export const listOrders = (status?: OrderStatus) =>
  request<Order[]>(`/api/orders${qs({ status })}`, undefined, () => mock.listOrders(status));
export const approveOrder = (id: number) =>
  request<ApproveResult>(`/api/orders/${id}/approve`, { method: "POST" }, () => mock.approveOrder(id));
export const rejectOrder = (id: number) =>
  request<RejectResult>(`/api/orders/${id}/reject`, { method: "POST" }, () => mock.rejectOrder(id));

// --- dışa aktarma (tarayıcı doğrudan indirir) ---
export const exportUrl = (kind: "sales" | "expenses") => `${API_URL}/api/export/${kind}.csv`;
