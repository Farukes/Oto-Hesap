"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Badge } from "../Badge";
import { DataTable, type Column } from "../DataTable";
import { IconDownload, IconEdit, IconPlus, IconSearch, IconTrash } from "../Icons";
import { Modal } from "../Modal";
import { Toast, type ToastData } from "../Toast";
import { Button, Card, Field, Input, Notice, Select, Textarea } from "../ui";
import {
  createExpense,
  createSale,
  deleteExpense,
  deleteSale,
  errorMessage,
  exportUrl,
  getProducts,
  listExpenses,
  listSales,
  updateExpense,
  updateSale,
} from "@/lib/api";
import { categoryLabel, channelLabel, formatDateTime, formatInt, formatMoney, fromDateInputValue, toDateInputValue } from "@/lib/format";
import { EXPENSE_CATEGORIES, type Channel, type Expense, type ExpenseInput, type Product, type Sale, type SaleInput } from "@/lib/types";
import { useAsync } from "@/lib/use-async";

const PAGE = 20;
type Tab = "sales" | "expenses";

function useDebounced(value: string, ms = 300): string {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(value), ms);
    return () => window.clearTimeout(t);
  }, [value, ms]);
  return debounced;
}

function Pagination({ offset, total, onChange }: { offset: number; total: number; onChange: (o: number) => void }) {
  if (total <= PAGE) return null;
  const from = offset + 1;
  const to = Math.min(offset + PAGE, total);
  return (
    <div className="flex items-center justify-between gap-3 border-t border-line px-4 py-2.5 text-[13px] text-muted">
      <span>
        {formatInt(from)}–{formatInt(to)} / {formatInt(total)}
      </span>
      <div className="flex gap-2">
        <Button size="sm" disabled={offset === 0} onClick={() => onChange(Math.max(0, offset - PAGE))}>
          Önceki
        </Button>
        <Button size="sm" disabled={to >= total} onClick={() => onChange(offset + PAGE)}>
          Sonraki
        </Button>
      </div>
    </div>
  );
}

export function RecordsView() {
  const [tab, setTab] = useState<Tab>("sales");
  const [toast, setToast] = useState<ToastData | null>(null);
  const notify = useCallback((text: string, tone: ToastData["tone"] = "success") => setToast({ id: Date.now(), text, tone }), []);
  const closeToast = useCallback((id: number) => setToast((t) => (t?.id === id ? null : t)), []);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Kayıt türü" className="inline-flex rounded-lg border border-line bg-surface p-0.5">
          {(
            [
              ["sales", "Satış"],
              ["expenses", "Gider"],
            ] as const
          ).map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="tab"
              aria-selected={tab === value}
              onClick={() => setTab(value)}
              className={`rounded-md px-4 py-1.5 text-[13.5px] font-medium transition-colors ${tab === value ? "bg-navy text-white" : "text-muted hover:bg-mint hover:text-navy"}`}
            >
              {label}
            </button>
          ))}
        </div>
        <a
          href={exportUrl(tab)}
          className="inline-flex h-9 items-center gap-2 rounded-lg border border-line bg-surface px-3 text-[13px] font-medium text-navy hover:bg-mint"
        >
          <IconDownload size={16} />
          Dışa aktar (CSV)
        </a>
      </div>

      {tab === "sales" ? <SalesPanel notify={notify} /> : <ExpensesPanel notify={notify} />}
      <Toast toast={toast} onClose={closeToast} />
    </div>
  );
}

type Notify = (text: string, tone?: ToastData["tone"]) => void;

// ---------------------------------------------------------------- Satışlar

function SalesPanel({ notify }: { notify: Notify }) {
  const [q, setQ] = useState("");
  const dq = useDebounced(q);
  const [offset, setOffset] = useState(0);
  const [editing, setEditing] = useState<{ mode: "create" } | { mode: "edit"; row: Sale } | null>(null);
  const [deleting, setDeleting] = useState<Sale | null>(null);

  const list = useAsync(() => listSales({ limit: PAGE, offset, q: dq || undefined }), `${dq}|${offset}`);
  const products = useAsync(() => getProducts());
  const productName = (row: Sale) => row.product ?? row.product_name ?? products.data?.find((p) => p.id === row.product_id)?.name ?? `Ürün #${row.product_id}`;

  const columns: Column<Sale>[] = [
    { key: "date", header: "Tarih", render: (r) => <span className="whitespace-nowrap text-muted">{formatDateTime(r.sold_at)}</span> },
    { key: "product", header: "Ürün", render: (r) => <span className="font-medium text-navy">{productName(r)}</span> },
    { key: "qty", header: "Adet", align: "right", render: (r) => <span className="tabular-nums">{formatInt(r.qty)}</span> },
    { key: "price", header: "Birim fiyat", align: "right", render: (r) => <span className="tabular-nums">{formatMoney(r.unit_price)}</span> },
    { key: "total", header: "Toplam", align: "right", render: (r) => <span className="font-medium tabular-nums text-navy">{formatMoney(r.total)}</span> },
    { key: "channel", header: "Kanal", render: (r) => <Badge tone={r.channel === "online" ? "blue" : "neutral"}>{channelLabel(r.channel)}</Badge> },
    {
      key: "actions",
      header: <span className="sr-only">İşlemler</span>,
      align: "right",
      render: (r) => (
        <div className="flex justify-end gap-1">
          <button type="button" onClick={() => setEditing({ mode: "edit", row: r })} className="rounded-md p-1.5 text-muted hover:bg-mint hover:text-navy" aria-label="Düzenle">
            <IconEdit size={16} />
          </button>
          <button type="button" onClick={() => setDeleting(r)} className="rounded-md p-1.5 text-muted hover:bg-danger-tint hover:text-danger" aria-label="Sil">
            <IconTrash size={16} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <>
      <Card padded={false}>
        <div className="flex flex-wrap items-center gap-3 border-b border-line px-4 py-3">
          <div className="relative min-w-0 flex-1 sm:max-w-xs">
            <IconSearch size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <Input
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setOffset(0);
              }}
              placeholder="Ürün adında ara"
              className="h-9 pl-9"
              aria-label="Satışlarda ara"
            />
          </div>
          <span className="text-[12.5px] text-muted">{list.data ? `${formatInt(list.data.total)} kayıt` : ""}</span>
          <Button variant="primary" size="sm" icon={<IconPlus size={16} />} className="ml-auto" onClick={() => setEditing({ mode: "create" })}>
            Yeni satış
          </Button>
        </div>
        <DataTable
          columns={columns}
          rows={list.data?.items ?? []}
          rowKey={(r) => r.id}
          loading={list.loading}
          error={list.error}
          caption="Satış kayıtları"
          empty={{
            title: dq ? "Eşleşen satış yok" : "Henüz satış yok",
            description: dq ? "Farklı bir ürün adı deneyin." : "İlk satışınızı ekleyin; Genel Bakış anında güncellenir.",
            action: !dq && (
              <Button variant="primary" size="sm" icon={<IconPlus size={16} />} onClick={() => setEditing({ mode: "create" })}>
                Yeni satış
              </Button>
            ),
          }}
        />
        {list.data && <Pagination offset={offset} total={list.data.total} onChange={setOffset} />}
      </Card>

      <Modal open={editing !== null} title={editing?.mode === "edit" ? "Satışı düzenle" : "Yeni satış"} onClose={() => setEditing(null)}>
        {editing && (
          <SaleForm
            key={editing.mode === "edit" ? editing.row.id : "new"}
            products={products.data ?? []}
            productsLoading={products.loading}
            initial={editing.mode === "edit" ? editing.row : undefined}
            onCancel={() => setEditing(null)}
            onSaved={(mode) => {
              setEditing(null);
              list.reload();
              products.reload();
              notify(mode === "edit" ? "Satış güncellendi." : "Satış kaydedildi.");
            }}
          />
        )}
      </Modal>

      <ConfirmDelete
        open={deleting !== null}
        label={deleting ? `${productName(deleting)} · ${formatMoney(deleting.total)}` : ""}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          if (!deleting) return;
          await deleteSale(deleting.id);
          setDeleting(null);
          list.reload();
          products.reload();
          notify("Satış silindi.", "info");
        }}
      />
    </>
  );
}

function SaleForm({
  products,
  productsLoading,
  initial,
  onCancel,
  onSaved,
}: {
  products: Product[];
  productsLoading: boolean;
  initial?: Sale;
  onCancel: () => void;
  onSaved: (mode: "create" | "edit") => void;
}) {
  const [productId, setProductId] = useState<string>(initial ? String(initial.product_id) : "");
  const [qty, setQty] = useState<string>(initial ? String(initial.qty) : "1");
  const [unitPrice, setUnitPrice] = useState<string>(initial ? String(initial.unit_price) : "");
  const [channel, setChannel] = useState<Channel>(initial?.channel ?? "magaza");
  const [date, setDate] = useState<string>(() => toDateInputValue(initial?.sold_at));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const product = products.find((p) => String(p.id) === productId);
  const qtyN = Number(qty);
  const priceN = Number(unitPrice);
  const total = Number.isFinite(qtyN) && Number.isFinite(priceN) ? qtyN * priceN : 0;

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (!product) return setError("Lütfen bir ürün seçin.");
    if (!Number.isInteger(qtyN) || qtyN < 1) return setError("Miktar 1 veya daha büyük olmalı.");
    if (!(priceN > 0)) return setError("Birim fiyat 0'dan büyük olmalı.");
    const input: SaleInput = { sold_at: fromDateInputValue(date), product_id: product.id, qty: qtyN, unit_price: priceN, channel };
    setBusy(true);
    try {
      if (initial) await updateSale(initial.id, input);
      else await createSale(input);
      onSaved(initial ? "edit" : "create");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {error && <Notice tone="danger">{error}</Notice>}
      <Field
        label="Ürün"
        htmlFor="sale-product"
        hint={
          product ? (
            <>
              Stok: <span className={product.is_critical ? "font-medium text-danger" : "font-medium text-navy"}>{formatInt(product.stock_qty)}</span>
              {" · "}
              liste fiyatı {formatMoney(product.sale_price)}
              {product.is_critical && " · kritik seviyede"}
            </>
          ) : productsLoading ? (
            "Ürünler yükleniyor…"
          ) : products.length === 0 ? (
            "Ürün listesi alınamadı."
          ) : undefined
        }
      >
        <Select
          id="sale-product"
          value={productId}
          required
          onChange={(e) => {
            const id = e.target.value;
            setProductId(id);
            const p = products.find((x) => String(x.id) === id);
            if (p) setUnitPrice(String(p.sale_price));
          }}
        >
          <option value="" disabled>
            Ürün seçin
          </option>
          {products.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </Select>
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Adet" htmlFor="sale-qty">
          <Input id="sale-qty" type="number" min={1} step={1} inputMode="numeric" value={qty} onChange={(e) => setQty(e.target.value)} required />
        </Field>
        <Field label="Birim fiyat (₺)" htmlFor="sale-price" hint="Ürün seçilince otomatik dolar">
          <Input id="sale-price" type="number" min={0.01} step={0.01} inputMode="decimal" value={unitPrice} onChange={(e) => setUnitPrice(e.target.value)} required />
        </Field>
        <Field label="Kanal" htmlFor="sale-channel">
          <Select id="sale-channel" value={channel} onChange={(e) => setChannel(e.target.value as Channel)}>
            <option value="magaza">Mağaza</option>
            <option value="online">Online</option>
          </Select>
        </Field>
        <Field label="Tarih" htmlFor="sale-date">
          <Input id="sale-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </Field>
      </div>
      <div className="flex items-center justify-between gap-3 border-t border-line pt-4">
        <div className="text-[13px] text-muted">
          Toplam <span className="font-semibold tabular-nums text-navy">{formatMoney(total)}</span>
        </div>
        <div className="flex gap-2">
          <Button type="button" onClick={onCancel} disabled={busy}>
            Vazgeç
          </Button>
          <Button type="submit" variant="primary" busy={busy}>
            {initial ? "Kaydet" : "Satışı kaydet"}
          </Button>
        </div>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------- Giderler

function ExpensesPanel({ notify }: { notify: Notify }) {
  const [q, setQ] = useState("");
  const dq = useDebounced(q);
  const [offset, setOffset] = useState(0);
  const [editing, setEditing] = useState<{ mode: "create" } | { mode: "edit"; row: Expense } | null>(null);
  const [deleting, setDeleting] = useState<Expense | null>(null);

  const list = useAsync(() => listExpenses({ limit: PAGE, offset, q: dq || undefined }), `${dq}|${offset}`);

  const columns: Column<Expense>[] = [
    { key: "date", header: "Tarih", render: (r) => <span className="whitespace-nowrap text-muted">{formatDateTime(r.spent_at)}</span> },
    { key: "category", header: "Kategori", render: (r) => <Badge tone="neutral">{categoryLabel(r.category)}</Badge> },
    { key: "amount", header: "Tutar", align: "right", render: (r) => <span className="font-medium tabular-nums text-navy">{formatMoney(r.amount)}</span> },
    { key: "vendor", header: "Tedarikçi", render: (r) => <span className="text-navy">{r.vendor || <span className="text-muted">—</span>}</span> },
    { key: "note", header: "Not", className: "max-w-56", render: (r) => <span className="block truncate text-muted">{r.note || "—"}</span> },
    {
      key: "actions",
      header: <span className="sr-only">İşlemler</span>,
      align: "right",
      render: (r) => (
        <div className="flex justify-end gap-1">
          <button type="button" onClick={() => setEditing({ mode: "edit", row: r })} className="rounded-md p-1.5 text-muted hover:bg-mint hover:text-navy" aria-label="Düzenle">
            <IconEdit size={16} />
          </button>
          <button type="button" onClick={() => setDeleting(r)} className="rounded-md p-1.5 text-muted hover:bg-danger-tint hover:text-danger" aria-label="Sil">
            <IconTrash size={16} />
          </button>
        </div>
      ),
    },
  ];

  return (
    <>
      <Card padded={false}>
        <div className="flex flex-wrap items-center gap-3 border-b border-line px-4 py-3">
          <div className="relative min-w-0 flex-1 sm:max-w-xs">
            <IconSearch size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <Input
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setOffset(0);
              }}
              placeholder="Kategori, tedarikçi veya notta ara"
              className="h-9 pl-9"
              aria-label="Giderlerde ara"
            />
          </div>
          <span className="text-[12.5px] text-muted">{list.data ? `${formatInt(list.data.total)} kayıt` : ""}</span>
          <Button variant="primary" size="sm" icon={<IconPlus size={16} />} className="ml-auto" onClick={() => setEditing({ mode: "create" })}>
            Yeni gider
          </Button>
        </div>
        <DataTable
          columns={columns}
          rows={list.data?.items ?? []}
          rowKey={(r) => r.id}
          loading={list.loading}
          error={list.error}
          caption="Gider kayıtları"
          empty={{
            title: dq ? "Eşleşen gider yok" : "Henüz gider yok",
            description: dq ? "Farklı bir kelime deneyin." : "Kira, maaş, kargo gibi giderleri buradan ekleyin.",
            action: !dq && (
              <Button variant="primary" size="sm" icon={<IconPlus size={16} />} onClick={() => setEditing({ mode: "create" })}>
                Yeni gider
              </Button>
            ),
          }}
        />
        {list.data && <Pagination offset={offset} total={list.data.total} onChange={setOffset} />}
      </Card>

      <Modal open={editing !== null} title={editing?.mode === "edit" ? "Gideri düzenle" : "Yeni gider"} onClose={() => setEditing(null)}>
        {editing && (
          <ExpenseForm
            key={editing.mode === "edit" ? editing.row.id : "new"}
            initial={editing.mode === "edit" ? editing.row : undefined}
            onCancel={() => setEditing(null)}
            onSaved={(mode) => {
              setEditing(null);
              list.reload();
              notify(mode === "edit" ? "Gider güncellendi." : "Gider kaydedildi.");
            }}
          />
        )}
      </Modal>

      <ConfirmDelete
        open={deleting !== null}
        label={deleting ? `${categoryLabel(deleting.category)} · ${formatMoney(deleting.amount)}` : ""}
        onClose={() => setDeleting(null)}
        onConfirm={async () => {
          if (!deleting) return;
          await deleteExpense(deleting.id);
          setDeleting(null);
          list.reload();
          notify("Gider silindi.", "info");
        }}
      />
    </>
  );
}

const OTHER = "__diger__";

function ExpenseForm({ initial, onCancel, onSaved }: { initial?: Expense; onCancel: () => void; onSaved: (mode: "create" | "edit") => void }) {
  const known = initial ? (EXPENSE_CATEGORIES as readonly string[]).includes(initial.category) : true;
  const [category, setCategory] = useState<string>(initial ? (known ? initial.category : OTHER) : "reklam");
  const [custom, setCustom] = useState<string>(initial && !known ? initial.category : "");
  const [amount, setAmount] = useState<string>(initial ? String(initial.amount) : "");
  const [vendor, setVendor] = useState<string>(initial?.vendor ?? "");
  const [note, setNote] = useState<string>(initial?.note ?? "");
  const [date, setDate] = useState<string>(() => toDateInputValue(initial?.spent_at));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    const cat = category === OTHER ? custom.trim().toLocaleLowerCase("tr-TR") : category;
    const amountN = Number(amount);
    if (!cat) return setError("Kategori girin.");
    if (!(amountN > 0)) return setError("Tutar 0'dan büyük olmalı.");
    const input: ExpenseInput = { spent_at: fromDateInputValue(date), category: cat, amount: amountN, vendor: vendor.trim() || null, note: note.trim() || null };
    setBusy(true);
    try {
      if (initial) await updateExpense(initial.id, input);
      else await createExpense(input);
      onSaved(initial ? "edit" : "create");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {error && <Notice tone="danger">{error}</Notice>}
      <div className="grid grid-cols-2 gap-3">
        <Field label="Kategori" htmlFor="exp-category">
          <Select id="exp-category" value={category} onChange={(e) => setCategory(e.target.value)}>
            {EXPENSE_CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {categoryLabel(c)}
              </option>
            ))}
            <option value={OTHER}>Diğer (serbest)</option>
          </Select>
        </Field>
        <Field label="Tutar (₺)" htmlFor="exp-amount">
          <Input id="exp-amount" type="number" min={0.01} step={0.01} inputMode="decimal" value={amount} onChange={(e) => setAmount(e.target.value)} required autoFocus={!initial} />
        </Field>
        {category === OTHER && (
          <div className="col-span-2">
            <Field label="Kategori adı" htmlFor="exp-custom" hint="Küçük harfle kaydedilir; API yalnız bilinen kategorileri kabul ediyorsa hata döner.">
              <Input id="exp-custom" value={custom} onChange={(e) => setCustom(e.target.value)} placeholder="örn. sigorta" required />
            </Field>
          </div>
        )}
        <Field label="Tedarikçi / satıcı" htmlFor="exp-vendor">
          <Input id="exp-vendor" value={vendor} onChange={(e) => setVendor(e.target.value)} placeholder="örn. Meta Ads" />
        </Field>
        <Field label="Tarih" htmlFor="exp-date">
          <Input id="exp-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
        </Field>
        <div className="col-span-2">
          <Field label="Not" htmlFor="exp-note">
            <Textarea id="exp-note" value={note} onChange={(e) => setNote(e.target.value)} placeholder="İsteğe bağlı" rows={2} />
          </Field>
        </div>
      </div>
      <div className="flex justify-end gap-2 border-t border-line pt-4">
        <Button type="button" onClick={onCancel} disabled={busy}>
          Vazgeç
        </Button>
        <Button type="submit" variant="primary" busy={busy}>
          {initial ? "Kaydet" : "Gideri kaydet"}
        </Button>
      </div>
    </form>
  );
}

// ---------------------------------------------------------------- Silme onayı

function ConfirmDelete({ open, label, onClose, onConfirm }: { open: boolean; label: string; onClose: () => void; onConfirm: () => Promise<void> }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function confirm() {
    setBusy(true);
    setError(null);
    try {
      await onConfirm();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal
      open={open}
      title="Kaydı sil"
      size="sm"
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={busy}>
            Vazgeç
          </Button>
          <Button variant="danger" onClick={confirm} busy={busy}>
            Sil
          </Button>
        </>
      }
    >
      <p className="text-sm text-navy">
        <span className="font-medium">{label}</span> kaydı silinecek. Bu işlem geri alınamaz.
      </p>
      {error && (
        <Notice tone="danger" className="mt-3">
          {error}
        </Notice>
      )}
    </Modal>
  );
}
