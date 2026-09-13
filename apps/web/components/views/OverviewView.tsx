"use client";

import Link from "next/link";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, Tooltip, XAxis, YAxis } from "recharts";
import { EmptyState } from "../EmptyState";
import { InsightCard } from "../InsightCard";
import { KpiCard } from "../KpiCard";
import { PeriodTabs, periodLabel } from "../PeriodTabs";
import { Card, Notice, Skeleton } from "../ui";
import { getCashflowMonthly, getExpensesByCategory, getInsights, getSalesByProduct, getSummary } from "@/lib/api";
import { categoryLabel, formatInt, formatMoney, formatMoneyCompact, formatMonthLong, formatMonthShort, formatShare, formatTime } from "@/lib/format";
import type { Insight, Period } from "@/lib/types";
import { useAsync } from "@/lib/use-async";

const INCOME = "#1C8C6E";
const EXPENSE = "#0F2A3C";
const PIE = ["#1C8C6E", "#0F2A3C", "#B7791F", "#5FB49C", "#4A6478", "#C0392B", "#8FBFAF", "#7A5210"];

const moneyTip = (value: unknown) => formatMoney(typeof value === "number" ? value : Number(value));

export function OverviewView() {
  const [period, setPeriod] = useState<Period>("half");
  const summary = useAsync(() => getSummary(period), period);
  const cashflow = useAsync(() => getCashflowMonthly());
  const byCategory = useAsync(() => getExpensesByCategory(period), period);
  const topProducts = useAsync(() => getSalesByProduct(period, 5), period);
  const insights = useAsync(() => getInsights().catch(() => [] as Insight[]));

  const s = summary.data;
  const hint = periodLabel(period);
  const bars = (cashflow.data ?? []).map((m) => ({ ...m, label: formatMonthShort(m.month), full: formatMonthLong(m.month) }));
  const slices = (byCategory.data ?? []).map((c) => ({ name: categoryLabel(c.category), value: c.amount, share: c.share }));

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <PeriodTabs value={period} onChange={setPeriod} />
        <div className="text-[12.5px] text-muted">
          {s ? (
            <>
              Son güncelleme <span className="font-medium text-navy">{formatTime(s.updated_at)}</span>
            </>
          ) : summary.loading ? (
            "Güncelleniyor…"
          ) : null}
        </div>
      </div>

      {summary.error && <Notice tone="danger">Özet alınamadı: {summary.error}</Notice>}

      <div className="grid gap-3 sm:grid-cols-2 md:gap-4 xl:grid-cols-4">
        <KpiCard label="Gelir" value={formatMoney(s?.income)} hint={hint} loading={summary.loading && !s} />
        <KpiCard label="Gider" value={formatMoney(s?.expense)} hint={hint} loading={summary.loading && !s} />
        <KpiCard
          label="Fark (Gelir − Gider)"
          value={formatMoney(s?.net)}
          hint="Net kâr değildir; KDV ve iade dahil değil"
          tone={s ? (s.net < 0 ? "negative" : "positive") : "default"}
          loading={summary.loading && !s}
        />
        <KpiCard
          label="Kritik ürün"
          value={s ? formatInt(s.critical_count) : "—"}
          hint={
            <Link href="/stok" className="text-brand-strong hover:underline">
              Stok ekranında gör →
            </Link>
          }
          tone={s && s.critical_count > 0 ? "danger" : "default"}
          loading={summary.loading && !s}
        />
      </div>

      {insights.data && insights.data.length > 0 && (
        <section aria-label="Öngörüler" className="grid gap-3 md:grid-cols-3">
          {insights.data.map((i) => (
            <InsightCard key={i.id} insight={i} />
          ))}
        </section>
      )}

      <div className="grid gap-4 xl:grid-cols-3">
        <Card title="Aylık gelir–gider" className="xl:col-span-2" action={<span className="text-[12px] text-muted">Tüm aylar</span>}>
          {cashflow.loading && !cashflow.data ? (
            <Skeleton className="h-72 w-full" />
          ) : cashflow.error ? (
            <EmptyState tone="danger" title="Grafik yüklenemedi" description={cashflow.error} compact />
          ) : bars.length === 0 ? (
            <EmptyState title="Veri yok" description="Satış veya gider kaydı girildiğinde aylık görünüm burada oluşur." compact />
          ) : (
            <BarChart responsive width="100%" height={288} data={bars} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barCategoryGap="28%">
              <CartesianGrid vertical={false} stroke="#D6E3DD" />
              <XAxis dataKey="label" tickLine={false} axisLine={{ stroke: "#D6E3DD" }} tick={{ fill: "#4B5B66", fontSize: 12 }} />
              <YAxis
                tickLine={false}
                axisLine={false}
                width={64}
                tick={{ fill: "#4B5B66", fontSize: 12 }}
                tickFormatter={(v: number) => formatMoneyCompact(v)}
              />
              <Tooltip
                cursor={{ fill: "#EAF5F1" }}
                formatter={moneyTip}
                labelFormatter={(_, payload) => (payload?.[0]?.payload as { full?: string } | undefined)?.full ?? ""}
                contentStyle={{ borderRadius: 10, border: "1px solid #D6E3DD", fontSize: 13 }}
              />
              <Legend iconType="circle" iconSize={9} wrapperStyle={{ fontSize: 12.5, paddingTop: 8 }} />
              <Bar dataKey="income" name="Gelir" fill={INCOME} radius={[4, 4, 0, 0]} />
              <Bar dataKey="expense" name="Gider" fill={EXPENSE} radius={[4, 4, 0, 0]} />
            </BarChart>
          )}
        </Card>

        <Card title="Gider kategorileri" action={<span className="text-[12px] text-muted">{hint}</span>}>
          {byCategory.loading && !byCategory.data ? (
            <Skeleton className="h-72 w-full" />
          ) : byCategory.error ? (
            <EmptyState tone="danger" title="Dağılım yüklenemedi" description={byCategory.error} compact />
          ) : slices.length === 0 ? (
            <EmptyState title="Bu dönemde gider yok" description="Kayıtlar ekranından gider ekleyince dağılım burada görünür." compact />
          ) : (
            <div className="flex flex-col items-center gap-4 sm:flex-row xl:flex-col">
              <div className="w-[190px] shrink-0">
                <PieChart responsive width="100%" height={190} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                  <Pie data={slices} dataKey="value" nameKey="name" innerRadius={54} outerRadius={88} paddingAngle={2} stroke="#FFFFFF" strokeWidth={2}>
                    {slices.map((_, i) => (
                      <Cell key={i} fill={PIE[i % PIE.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={moneyTip} contentStyle={{ borderRadius: 10, border: "1px solid #D6E3DD", fontSize: 13 }} />
                </PieChart>
              </div>
              <ul className="w-full space-y-1.5 text-[13px]">
                {slices.map((c, i) => (
                  <li key={c.name} className="flex items-center gap-2">
                    <span className="size-2.5 shrink-0 rounded-full" style={{ background: PIE[i % PIE.length] }} aria-hidden="true" />
                    <span className="truncate text-navy">{c.name}</span>
                    <span className="ml-auto tabular-nums text-muted">{formatShare(c.share)}</span>
                    <span className="w-24 text-right tabular-nums text-navy">{formatMoney(c.value)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      </div>

      <Card
        title="En kârlı ürünler (tahmini brüt katkı)"
        action={<span className="text-[12px] text-muted">qty × (satış fiyatı − mevcut birim maliyet) · {hint}</span>}
        padded={false}
      >
        {topProducts.loading && !topProducts.data ? (
          <div className="space-y-3 p-5">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-5 w-full" />
            ))}
          </div>
        ) : topProducts.error ? (
          <EmptyState tone="danger" title="Liste yüklenemedi" description={topProducts.error} compact />
        ) : (topProducts.data ?? []).length === 0 ? (
          <EmptyState title="Bu dönemde satış yok" description="Satış girildikçe en kârlı ürünler burada sıralanır." compact />
        ) : (
          <ol className="divide-y divide-line/70">
            {topProducts.data!.map((p, i) => (
              <li key={p.product_id} className="flex items-center gap-3 px-5 py-3 text-[13.5px]">
                <span className="flex size-6 shrink-0 items-center justify-center rounded-full bg-mint text-[12px] font-semibold text-brand-strong">{i + 1}</span>
                <span className="min-w-0 flex-1 truncate font-medium text-navy">{p.product}</span>
                <span className="hidden text-muted sm:inline">
                  {formatInt(p.qty)} adet · ciro {formatMoney(p.revenue)}
                </span>
                <span className="w-28 text-right font-semibold tabular-nums text-brand-strong">{formatMoney(p.profit)}</span>
              </li>
            ))}
          </ol>
        )}
      </Card>
    </div>
  );
}
