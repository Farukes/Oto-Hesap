import type { ReactNode } from "react";
import { Skeleton } from "./ui";

export type KpiTone = "default" | "positive" | "negative" | "danger" | "muted";

const VALUE_TONE: Record<KpiTone, string> = {
  default: "text-navy",
  positive: "text-brand-strong",
  negative: "text-danger",
  danger: "text-danger",
  muted: "text-muted",
};

interface KpiCardProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: KpiTone;
  loading?: boolean;
}

export function KpiCard({ label, value, hint, tone = "default", loading = false }: KpiCardProps) {
  return (
    <div className="rounded-card border border-line bg-surface px-5 py-4">
      <div className="text-[12.5px] font-medium uppercase tracking-wide text-muted">{label}</div>
      {loading ? (
        <Skeleton className="mt-2 h-8 w-2/3" />
      ) : (
        <div className={`mt-1.5 whitespace-nowrap text-[24px] font-semibold leading-tight tabular-nums md:text-[26px] ${VALUE_TONE[tone]}`}>{value}</div>
      )}
      {hint && <div className="mt-1.5 text-xs text-muted">{hint}</div>}
    </div>
  );
}
