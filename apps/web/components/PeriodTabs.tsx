"use client";

import type { Period } from "@/lib/types";

const OPTIONS: { value: Period; label: string }[] = [
  { value: "month", label: "Bu ay" },
  { value: "quarter", label: "3 ay" },
  { value: "half", label: "6 ay" },
];

export function periodLabel(period: Period): string {
  return OPTIONS.find((o) => o.value === period)?.label ?? period;
}

export function PeriodTabs({ value, onChange }: { value: Period; onChange: (p: Period) => void }) {
  return (
    <div role="tablist" aria-label="Dönem" className="inline-flex rounded-lg border border-line bg-surface p-0.5">
      {OPTIONS.map((o) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(o.value)}
            className={`rounded-md px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
              active ? "bg-navy text-white" : "text-muted hover:bg-mint hover:text-navy"
            }`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
