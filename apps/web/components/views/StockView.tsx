"use client";

import { useCallback, useState, type KeyboardEvent } from "react";
import { Badge } from "../Badge";
import { DataTable, type Column } from "../DataTable";
import { IconRefresh } from "../Icons";
import { Toast, type ToastData } from "../Toast";
import { Button, Card, Notice } from "../ui";
import { errorMessage, getProducts, patchProduct } from "@/lib/api";
import { formatInt, formatMoney } from "@/lib/format";
import type { Product, ProductPatch } from "@/lib/types";
import { useAsync } from "@/lib/use-async";

export function StockView() {
  const products = useAsync(() => getProducts());
  const [toast, setToast] = useState<ToastData | null>(null);
  const closeToast = useCallback((id: number) => setToast((t) => (t?.id === id ? null : t)), []);

  const rows = [...(products.data ?? [])].sort((a, b) => Number(b.is_critical) - Number(a.is_critical) || a.name.localeCompare(b.name, "tr"));
  const critical = rows.filter((p) => p.is_critical).length;
  const onTheWay = rows.filter((p) => p.open_order_id !== null).length;

  async function save(product: Product, patch: ProductPatch) {
    try {
      await patchProduct(product.id, patch);
      products.reload();
      setToast({ id: Date.now(), text: `${product.name} güncellendi.` });
    } catch (err) {
      setToast({ id: Date.now(), text: errorMessage(err), tone: "danger" });
    }
  }

  const columns: Column<Product>[] = [
    {
      key: "name",
      header: "Ürün",
      render: (p) => (
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="font-medium text-navy">{p.name}</span>
            {p.is_critical && <Badge tone="red">Kritik</Badge>}
            {p.open_order_id !== null && (
              <Badge tone="blue" title={`Sipariş #${p.open_order_id}${p.open_order_status ? ` · ${p.open_order_status}` : ""}`}>
                Sipariş yolda
              </Badge>
            )}
          </div>
          <div className="text-[12px] text-muted">
            {p.category}
            {p.supplier ?? p.supplier_name ? ` · ${p.supplier ?? p.supplier_name}` : ""}
          </div>
        </div>
      ),
    },
    {
      key: "stock",
      header: "Stok",
      align: "right",
      render: (p) => <span className={`tabular-nums ${p.is_critical ? "font-semibold text-danger" : "font-medium text-navy"}`}>{formatInt(p.stock_qty)}</span>,
    },
    {
      key: "reorder",
      header: "Eşik",
      align: "right",
      render: (p) => <EditableNumber value={p.reorder_point} label={`${p.name} eşiği`} onSave={(v) => save(p, { reorder_point: v })} />,
    },
    {
      key: "target",
      header: "Hedef stok",
      align: "right",
      render: (p) => <EditableNumber value={p.target_stock} label={`${p.name} hedef stoğu`} onSave={(v) => save(p, { target_stock: v })} />,
    },
    { key: "cost", header: "Maliyet", align: "right", render: (p) => <span className="tabular-nums text-muted">{formatMoney(p.unit_cost)}</span> },
    { key: "price", header: "Satış fiyatı", align: "right", render: (p) => <span className="tabular-nums text-navy">{formatMoney(p.sale_price)}</span> },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className={`rounded-card border px-4 py-2.5 ${critical > 0 ? "border-danger/30 bg-danger-tint" : "border-line bg-surface"}`}>
          <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">Kritik ürün</div>
          <div className={`text-[22px] font-semibold leading-tight tabular-nums ${critical > 0 ? "text-danger" : "text-navy"}`}>{products.data ? critical : "—"}</div>
        </div>
        <div className="rounded-card border border-line bg-surface px-4 py-2.5">
          <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">Sipariş yolda</div>
          <div className="text-[22px] font-semibold leading-tight tabular-nums text-navy">{products.data ? onTheWay : "—"}</div>
        </div>
        <div className="rounded-card border border-line bg-surface px-4 py-2.5">
          <div className="text-[11.5px] font-medium uppercase tracking-wide text-muted">Toplam ürün</div>
          <div className="text-[22px] font-semibold leading-tight tabular-nums text-navy">{products.data ? rows.length : "—"}</div>
        </div>
        <Button size="sm" icon={<IconRefresh size={15} />} className="ml-auto" onClick={products.reload} busy={products.loading && !!products.data}>
          Yenile
        </Button>
      </div>

      {critical > 0 && (
        <Notice tone="danger">
          {critical} ürün yeniden sipariş eşiğinin altında (stok ≤ eşik). Tedarik ekranında &quot;Şimdi kontrol et&quot; ile taslak oluşturabilirsiniz.
        </Notice>
      )}

      <Card padded={false} title="Ürünler" action={<span className="text-[12px] text-muted">Eşik ve hedef stok hücreleri tıklanarak düzenlenir</span>}>
        <DataTable
          columns={columns}
          rows={rows}
          rowKey={(p) => p.id}
          loading={products.loading}
          error={products.error}
          caption="Ürün stok tablosu"
          rowClassName={(p) => (p.is_critical ? "bg-danger-tint/60 hover:bg-danger-tint" : "")}
          empty={{ title: "Ürün yok", description: "Ürün kataloğu boş; seed verisi yüklenince liste burada görünür." }}
        />
      </Card>
      <Toast toast={toast} onClose={closeToast} />
    </div>
  );
}

/** Satır içi sayı düzenleme: tıkla → yaz → Enter/odak dışı kaydeder, Esc vazgeçer. */
function EditableNumber({ value, label, onSave }: { value: number; label: string; onSave: (v: number) => Promise<void> }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(String(value));
  const [busy, setBusy] = useState(false);

  function start() {
    setDraft(String(value));
    setEditing(true);
  }

  async function commit() {
    const n = Number(draft);
    setEditing(false);
    if (!Number.isInteger(n) || n < 0 || n === value) return;
    setBusy(true);
    try {
      await onSave(n);
    } finally {
      setBusy(false);
    }
  }

  function onKey(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      void commit();
    } else if (e.key === "Escape") {
      e.preventDefault();
      setEditing(false);
    }
  }

  if (editing) {
    return (
      <input
        type="number"
        min={0}
        step={1}
        inputMode="numeric"
        aria-label={label}
        value={draft}
        autoFocus
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => void commit()}
        onKeyDown={onKey}
        className="tap-y h-8 w-20 rounded-md border border-brand-strong bg-surface px-2 text-right text-[13.5px] tabular-nums text-navy"
      />
    );
  }

  return (
    <button
      type="button"
      onClick={start}
      disabled={busy}
      aria-label={`${label}: ${value}, düzenlemek için tıklayın`}
      className="tap-y h-8 min-w-14 rounded-md border border-transparent px-2 text-right tabular-nums text-navy hover:border-field hover:bg-surface disabled:cursor-not-allowed disabled:text-muted"
    >
      {busy ? "…" : formatInt(value)}
    </button>
  );
}
