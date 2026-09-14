"use client";

import { useCallback, useState } from "react";
import { Badge, type BadgeTone } from "../Badge";
import { EmptyState } from "../EmptyState";
import { IconCheck, IconChevron, IconClose, IconRefresh } from "../Icons";
import { Toast, type ToastData } from "../Toast";
import { Button, Card, Notice, Skeleton } from "../ui";
import { agentCheck, approveOrder, errorMessage, errorStatus, listOrders, rejectOrder } from "@/lib/api";
import { formatDateTime, formatInt, formatMoney, formatTime } from "@/lib/format";
import type { Order, OrderStatus } from "@/lib/types";
import { useAsync } from "@/lib/use-async";

const STATUS: Record<OrderStatus, { label: string; tone: BadgeTone }> = {
  draft: { label: "Bekliyor", tone: "yellow" },
  approved: { label: "Onaylandı", tone: "blue" },
  sent: { label: "Gönderildi", tone: "green" },
  rejected: { label: "Reddedildi", tone: "neutral" },
};

interface SentMeta {
  simulated: boolean;
  ref: string | null;
}

export function SupplyView() {
  const orders = useAsync(async () => {
    const [draft, approved, sent, rejected] = await Promise.all([listOrders("draft"), listOrders("approved"), listOrders("sent"), listOrders("rejected")]);
    return { draft, approved, sent, rejected };
  });
  const [checking, setChecking] = useState(false);
  const [checkError, setCheckError] = useState<string | null>(null);
  const [busy, setBusy] = useState<Record<number, "approve" | "reject">>({});
  const [errors, setErrors] = useState<Record<number, string>>({});
  const [meta, setMeta] = useState<Record<number, SentMeta>>({});
  const [toast, setToast] = useState<ToastData | null>(null);
  const closeToast = useCallback((id: number) => setToast((t) => (t?.id === id ? null : t)), []);
  const notify = useCallback((text: string, tone: ToastData["tone"] = "success") => setToast({ id: Date.now(), text, tone }), []);

  async function check() {
    setChecking(true);
    setCheckError(null);
    try {
      const r = await agentCheck();
      notify(r.created > 0 ? `${r.created} taslak oluşturuldu` : "Yeni taslak yok: kritik ürünlerin açık siparişi var ya da kritik ürün yok.", r.created > 0 ? "success" : "info");
      orders.reload();
    } catch (err) {
      setCheckError(errorMessage(err));
    } finally {
      setChecking(false);
    }
  }

  function setOrderError(id: number, message: string | null) {
    setErrors((e) => {
      const next = { ...e };
      if (message === null) delete next[id];
      else next[id] = message;
      return next;
    });
  }

  async function approve(o: Order) {
    if (busy[o.id]) return; // çift tıklama koruması
    setBusy((b) => ({ ...b, [o.id]: "approve" }));
    setOrderError(o.id, null);
    try {
      const r = await approveOrder(o.id);
      const simulated = r.simulated ?? r.notify?.dry_run ?? false;
      const ref = r.order?.notify_ref ?? (r.notify?.message_id != null ? String(r.notify.message_id) : null);
      setMeta((m) => ({ ...m, [o.id]: { simulated, ref } }));
      notify(simulated ? "Onaylandı · gönderim simülasyonu" : "Onaylandı ve tedarikçiye gönderildi");
    } catch (err) {
      const status = errorStatus(err);
      if (status === 409) {
        // zaten gönderilmiş/reddedilmiş: sessiz geç, listeyi tazele
      } else if (status === 502 || status === 503) {
        setOrderError(o.id, "Onaylı, gönderilemedi — tekrar dene");
      } else {
        setOrderError(o.id, errorMessage(err));
      }
    } finally {
      setBusy((b) => {
        const next = { ...b };
        delete next[o.id];
        return next;
      });
      orders.reload();
    }
  }

  async function reject(o: Order) {
    if (busy[o.id]) return;
    setBusy((b) => ({ ...b, [o.id]: "reject" }));
    setOrderError(o.id, null);
    try {
      await rejectOrder(o.id);
      notify("Taslak reddedildi.", "info");
    } catch (err) {
      if (errorStatus(err) !== 409) setOrderError(o.id, errorMessage(err));
    } finally {
      setBusy((b) => {
        const next = { ...b };
        delete next[o.id];
        return next;
      });
      orders.reload();
    }
  }

  const d = orders.data;
  const pending = d ? [...d.draft, ...d.approved].sort((a, b) => b.created_at.localeCompare(a.created_at)) : [];
  const trail = d ? [...d.sent, ...d.rejected].sort((a, b) => (b.sent_at ?? b.created_at).localeCompare(a.sent_at ?? a.created_at)) : [];

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <p className="max-w-xl text-[13.5px] text-muted">
          Ajan kritik stoktaki ürünler için sipariş taslağı hazırlar; miktar hedef stoğa göre hesaplanır. <span className="font-medium text-navy">Hiçbir mesaj onaysız gönderilmez.</span>
        </p>
        <Button variant="primary" icon={<IconRefresh size={17} />} className="ml-auto" onClick={check} busy={checking}>
          Şimdi kontrol et
        </Button>
      </div>
      {checkError && <Notice tone="danger">Kontrol başarısız: {checkError}</Notice>}
      {orders.error && <Notice tone="danger">Siparişler alınamadı: {orders.error}</Notice>}

      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {(["draft", "approved", "sent", "rejected"] as const).map((s) => (
          <div key={s} className="rounded-card border border-line bg-surface px-4 py-3">
            <div className="flex items-center gap-2 text-[12px] font-medium uppercase tracking-wide text-muted">
              <span
                className={`size-2 rounded-full ${s === "draft" ? "bg-warn" : s === "approved" ? "bg-info-ink" : s === "sent" ? "bg-brand" : "bg-line"}`}
                aria-hidden="true"
              />
              {STATUS[s].label}
            </div>
            {d ? <div className="mt-1 text-[24px] font-semibold leading-tight tabular-nums text-navy">{d[s].length}</div> : <Skeleton className="mt-2 h-7 w-10" />}
          </div>
        ))}
      </div>

      <section aria-label="Onay bekleyen taslaklar" aria-busy={(orders.loading && !d) || undefined} className="space-y-3">
        <h2 className="text-[15px] font-semibold text-navy">Onay bekleyen taslaklar</h2>
        {orders.loading && !d ? (
          <div className="grid gap-3 md:grid-cols-2">
            <Skeleton className="h-44" />
            <Skeleton className="h-44" />
          </div>
        ) : pending.length === 0 ? (
          <Card>
            <EmptyState
              title="Bekleyen taslak yok"
              description='Kritik stok oluştuğunda "Şimdi kontrol et" ile taslak üretin; zamanlayıcı da aynı kontrolü çalıştırır.'
              compact
            />
          </Card>
        ) : (
          <div className="grid gap-3 md:grid-cols-2">
            {pending.map((o) => (
              <DraftCard key={o.id} order={o} busy={busy[o.id]} error={errors[o.id]} onApprove={() => approve(o)} onReject={() => reject(o)} />
            ))}
          </div>
        )}
      </section>

      <Card title="İz kaydı" padded={false} action={<span className="text-[12px] text-muted">Gönderilen ve reddedilen siparişler</span>}>
        {orders.loading && !d ? (
          <div className="space-y-3 p-5">
            <Skeleton className="h-5" />
            <Skeleton className="h-5" />
          </div>
        ) : trail.length === 0 ? (
          <EmptyState title="Henüz gönderilmiş sipariş yok" description="Onaylanan taslaklar burada oluşturulma → gönderim zamanıyla listelenir." compact />
        ) : (
          <ul className="divide-y divide-line/70">
            {trail.map((o) => {
              const m = meta[o.id];
              const ref = o.notify_ref ?? m?.ref ?? null;
              return (
                <li key={o.id} className="flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-3 text-[13.5px]">
                  <div className="min-w-48 flex-1">
                    <div className="font-medium text-navy">
                      {productName(o)} <span className="whitespace-nowrap text-muted">× {formatInt(o.qty)}</span>
                    </div>
                    <div className="text-[12.5px] text-muted">
                      {supplierName(o)} · #{o.id}
                      {ref ? <span className="ml-2 text-[11.5px] text-muted">ref {ref}</span> : null}
                    </div>
                  </div>
                  <div className="text-[12.5px] text-muted">
                    {formatDateTime(o.created_at)} <span aria-hidden="true">→</span>{" "}
                    {o.status === "sent" ? (
                      <>
                        Gönderildi {formatTime(o.sent_at)} · teslim alındı değil{m?.simulated ? " (simülasyon)" : ""}
                      </>
                    ) : (
                      "Reddedildi"
                    )}
                  </div>
                  <Badge tone={STATUS[o.status].tone}>{STATUS[o.status].label}</Badge>
                </li>
              );
            })}
          </ul>
        )}
      </Card>
      <Toast toast={toast} onClose={closeToast} />
    </div>
  );
}

const productName = (o: Order) => o.product ?? o.product_name ?? `Ürün #${o.product_id}`;
const supplierName = (o: Order) => o.supplier ?? o.supplier_name ?? `Tedarikçi #${o.supplier_id}`;

function DraftCard({ order: o, busy, error, onApprove, onReject }: { order: Order; busy?: "approve" | "reject"; error?: string; onApprove: () => void; onReject: () => void }) {
  const approved = o.status === "approved";
  return (
    <article className={`flex flex-col rounded-card border bg-surface ${approved ? "border-info-ink/30" : "border-line"}`}>
      <div className="flex items-start justify-between gap-3 px-5 pt-4">
        <div className="min-w-0">
          <div className="text-[15px] font-semibold text-navy">{productName(o)}</div>
          <div className="text-[12.5px] text-muted">
            Taslak #{o.id} · {formatDateTime(o.created_at)}
          </div>
        </div>
        <Badge tone={STATUS[o.status].tone}>{approved ? "Onaylı · gönderilmedi" : STATUS[o.status].label}</Badge>
      </div>
      <dl className="mt-3 grid grid-cols-3 gap-3 px-5 text-[13px]">
        <div>
          <dt className="text-[11.5px] uppercase tracking-wide text-muted">Miktar</dt>
          <dd className="font-semibold tabular-nums text-navy">{formatInt(o.qty)} adet</dd>
        </div>
        <div>
          <dt className="text-[11.5px] uppercase tracking-wide text-muted">Tahmini tutar</dt>
          <dd className="font-semibold tabular-nums text-navy">{formatMoney(o.est_amount)}</dd>
        </div>
        <div className="min-w-0">
          <dt className="text-[11.5px] uppercase tracking-wide text-muted">Tedarikçi</dt>
          <dd className="truncate font-medium text-navy" title={supplierName(o)}>
            {supplierName(o)}
            {o.supplier_channel && <span className="ml-1 text-[11.5px] font-normal text-muted">({o.supplier_channel === "telegram" ? "Telegram" : "e-posta"})</span>}
          </dd>
        </div>
      </dl>
      {o.message_text && (
        <details className="group mx-5 mt-3 rounded-lg border border-line bg-surface-2">
          <summary className="tap-y flex cursor-pointer select-none items-center gap-1.5 px-3 py-2 text-[12.5px] font-medium text-navy [&::-webkit-details-marker]:hidden">
            <IconChevron size={13} className="text-muted transition-transform group-open:rotate-90" />
            Mesaj önizleme
          </summary>
          <p className="border-t border-line px-3 py-2.5 text-[13px] leading-relaxed text-navy">{o.message_text}</p>
        </details>
      )}
      {error && (
        <Notice tone="danger" className="mx-5 mt-3">
          {error}
        </Notice>
      )}
      <div className="mt-4 flex items-center justify-end gap-2 border-t border-line px-5 py-3">
        <Button size="sm" variant="danger" icon={<IconClose size={15} />} onClick={onReject} busy={busy === "reject"} disabled={busy !== undefined}>
          Reddet
        </Button>
        <Button size="sm" variant="primary" icon={<IconCheck size={15} />} onClick={onApprove} busy={busy === "approve"} disabled={busy !== undefined}>
          {approved ? "Tekrar gönder" : "Onayla"}
        </Button>
      </div>
    </article>
  );
}
