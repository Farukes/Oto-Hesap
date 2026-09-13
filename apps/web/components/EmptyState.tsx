import type { ReactNode } from "react";
import { IconAlert, IconInfo } from "./Icons";

interface EmptyStateProps {
  title: string;
  description?: ReactNode;
  action?: ReactNode;
  tone?: "neutral" | "danger";
  compact?: boolean;
}

/** Boş veri / hata durumu. Recharts'a boş dizi vermek yerine bu gösterilir. */
export function EmptyState({ title, description, action, tone = "neutral", compact = false }: EmptyStateProps) {
  const Icon = tone === "danger" ? IconAlert : IconInfo;
  return (
    <div className={`flex flex-col items-center justify-center text-center ${compact ? "py-6" : "py-10"}`}>
      <div className={`mb-3 flex size-10 items-center justify-center rounded-full ${tone === "danger" ? "bg-danger-tint text-danger" : "bg-mint text-brand-strong"}`}>
        <Icon size={20} />
      </div>
      <div className="text-[14.5px] font-semibold text-navy">{title}</div>
      {description && <div className="mt-1 max-w-sm text-[13px] leading-snug text-muted">{description}</div>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
