import Link from "next/link";
import { IconAlert, IconInfo, IconSpark } from "./Icons";
import type { Insight } from "@/lib/types";

const STYLE = {
  critical: { wrap: "border-l-danger bg-danger-tint/60", icon: "text-danger", Icon: IconAlert, label: "Kritik" },
  warn: { wrap: "border-l-warn bg-warn-tint/70", icon: "text-warn-ink", Icon: IconSpark, label: "Uyarı" },
  info: { wrap: "border-l-brand bg-brand-tint/60", icon: "text-brand-strong", Icon: IconInfo, label: "Bilgi" },
} as const;

function normalize(severity: Insight["severity"]): keyof typeof STYLE {
  if (severity === "critical") return "critical";
  if (severity === "warn" || severity === "warning") return "warn";
  return "info";
}

/** Öngörü kartı: severity'e göre renk; metin şablondan, LLM yok. */
export function InsightCard({ insight }: { insight: Insight }) {
  const s = STYLE[normalize(insight.severity)];
  const body = insight.body ?? insight.detail ?? "";
  const href = insight.metric === "critical_count" ? "/tedarik" : insight.metric?.startsWith("expense") ? "/kayitlar" : null;

  return (
    <article className={`flex gap-3 rounded-card border border-line border-l-4 bg-surface px-4 py-3.5 ${s.wrap}`}>
      <s.Icon size={20} className={`mt-0.5 shrink-0 ${s.icon}`} />
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
          <h3 className="text-[14px] font-semibold text-navy">{insight.title}</h3>
          <span className="text-[11px] font-medium uppercase tracking-wide text-muted">{s.label}</span>
        </div>
        <p className="mt-0.5 text-[13.5px] leading-snug text-muted">{body}</p>
        {href && (
          <Link href={href} className="mt-1.5 inline-block rounded text-[13px] font-medium text-brand-strong hover:underline">
            {href === "/tedarik" ? "Tedarik ekranına git" : "Kayıtlara git"} →
          </Link>
        )}
      </div>
    </article>
  );
}
