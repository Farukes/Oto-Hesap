import type { ReactNode } from "react";

export type BadgeTone = "neutral" | "green" | "red" | "yellow" | "blue" | "navy";

const TONES: Record<BadgeTone, string> = {
  neutral: "border-line bg-surface-2 text-muted",
  green: "border-brand/30 bg-brand-tint text-brand-ink",
  red: "border-danger/30 bg-danger-tint text-danger-ink",
  yellow: "border-warn/40 bg-warn-tint text-warn-ink",
  blue: "border-info-ink/20 bg-info-tint text-info-ink",
  navy: "border-navy/20 bg-navy text-white",
};

export function Badge({ tone = "neutral", children, className = "", title }: { tone?: BadgeTone; children: ReactNode; className?: string; title?: string }) {
  return (
    <span
      title={title}
      className={`inline-flex items-center gap-1 whitespace-nowrap rounded-full border px-2 py-0.5 text-[11.5px] font-medium leading-4 ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
