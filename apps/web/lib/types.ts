// OtoHesap API tipleri — kaynak: AGENTS.md §6 (sözleşme v0) + specs/001-otohesap-mvp/contracts/api.md (eklemeler).
// Yalnız spec eklemelerinde bulunan alanlar opsiyoneldir ("spec ekleme" notu); sözleşmede hiç olmayanlar "sözleşme önerisi".

export type Period = "month" | "quarter" | "half";
export type Channel = "magaza" | "online";
export type OrderStatus = "draft" | "approved" | "sent" | "rejected";
export type ContactChannel = "telegram" | "email";

export const EXPENSE_CATEGORIES = ["kira", "maas", "elektrik", "kargo", "reklam", "tedarik"] as const;

export interface Health {
  status: string;
  db: boolean;
  llm: string;
  scheduler?: boolean;
  version?: string;
}

export interface Summary {
  income: number;
  expense: number;
  net: number;
  critical_count: number;
  updated_at: string;
}

export interface CashflowMonth {
  month: string; // "2026-04" (görünümden ISO tarih gelirse format.ts normalize eder)
  income: number;
  expense: number;
  net: number;
}

export interface ExpenseByCategory {
  category: string;
  amount: number;
  share: number; // yüzde 0–100 (R-18)
}

export interface SalesByProduct {
  product_id: number;
  product: string;
  revenue: number;
  profit: number; // tahmini brüt katkı (D16)
  qty: number;
}

export interface Sale {
  id: number;
  sold_at: string;
  product_id: number;
  product?: string; // spec ekleme: ürün adı
  product_name?: string; // canlı API bu adı kullanıyor (13 Eyl)
  qty: number;
  unit_price: number;
  total: number;
  channel: Channel;
}

export interface SaleInput {
  sold_at: string;
  product_id: number;
  qty: number;
  unit_price: number;
  channel: Channel;
}

export interface Expense {
  id: number;
  spent_at: string;
  category: string;
  amount: number;
  vendor: string | null;
  note: string | null;
}

export interface ExpenseInput {
  spent_at: string;
  category: string;
  amount: number;
  vendor: string | null;
  note: string | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
}

export interface ListParams {
  limit?: number;
  offset?: number;
  q?: string;
}

export interface Product {
  id: number;
  name: string;
  category: string;
  unit_cost: number;
  sale_price: number;
  stock_qty: number;
  reorder_point: number;
  target_stock: number;
  supplier_id: number | null;
  supplier?: string | null; // spec ekleme
  supplier_name?: string | null; // canlı API bu adı kullanıyor (13 Eyl)
  is_critical: boolean;
  open_order_id: number | null;
  open_order_status?: OrderStatus | null; // spec ekleme
}

export interface ProductPatch {
  reorder_point?: number;
  target_stock?: number;
  stock_qty?: number;
}

/** Spec: dizi dizisi (columns sırasıyla). Nesne satırları da toleransla okunur. */
export type AssistantRow = unknown[] | Record<string, unknown>;

export interface AssistantAnswer {
  answer: string;
  sql: string;
  rows: AssistantRow[];
  columns: string[];
  sources: string[];
  asked_at: string;
  cached: boolean;
  ok?: boolean; // sözleşme önerisi: chat_log.ok; yoksa true varsayılır
  model?: string; // sözleşme önerisi: yanıtı üreten model adı
}

export interface Order {
  id: number;
  created_at: string;
  product_id: number;
  product?: string; // spec ekleme
  product_name?: string; // canlı API (13 Eyl)
  supplier_id: number;
  supplier?: string; // spec ekleme
  supplier_name?: string; // canlı API (13 Eyl)
  supplier_channel?: ContactChannel; // sözleşme önerisi
  qty: number;
  est_amount: number | null;
  status: OrderStatus;
  message_text: string | null;
  sent_at: string | null;
  notify_ref?: string | null; // D17: Telegram message_id → purchase_orders.notify_ref
}

export interface AgentCheckResult {
  created: number;
  drafts: Order[];
}

export interface NotifyInfo {
  ok?: boolean;
  dry_run?: boolean;
  channel?: string;
  message_id?: number | string | null;
}

export interface ApproveResult {
  id?: number;
  status: OrderStatus;
  sent_at: string | null;
  simulated?: boolean; // spec ekleme (NOTIFY_DRY_RUN)
  notify?: NotifyInfo; // sözleşme önerisi (koordinatör notu)
  order?: Order;
}

export interface RejectResult {
  id?: number;
  status: OrderStatus;
  order?: Order;
}

export type InsightSeverity = "info" | "warn" | "warning" | "critical";

/** GET /api/insights — spec ekleme R-24 (AGENTS §6'da henüz yok). */
export interface Insight {
  id: string;
  title: string;
  body?: string;
  detail?: string; // eski taslak adı; body yoksa okunur
  severity: InsightSeverity;
  metric?: string;
  change_pct?: number | null;
}
