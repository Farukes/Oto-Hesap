"use client";

import { useRef, type KeyboardEvent } from "react";
import type { Period } from "@/lib/types";

const OPTIONS: { value: Period; label: string }[] = [
  { value: "month", label: "Bu ay" },
  { value: "quarter", label: "3 ay" },
  { value: "half", label: "6 ay" },
];

export function periodLabel(period: Period): string {
  return OPTIONS.find((o) => o.value === period)?.label ?? period;
}

/** Dönem filtresi. Sekme kalıbı: gruba tek Tab durağı, içinde ok tuşlarıyla gezinme. */
export function PeriodTabs({ value, onChange }: { value: Period; onChange: (p: Period) => void }) {
  const listRef = useRef<HTMLDivElement>(null);

  function onKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    const keys = ["ArrowRight", "ArrowLeft", "Home", "End"];
    if (!keys.includes(e.key)) return;
    e.preventDefault();
    const i = OPTIONS.findIndex((o) => o.value === value);
    const next =
      e.key === "Home" ? 0 : e.key === "End" ? OPTIONS.length - 1 : e.key === "ArrowRight" ? (i + 1) % OPTIONS.length : (i - 1 + OPTIONS.length) % OPTIONS.length;
    onChange(OPTIONS[next].value);
    listRef.current?.querySelectorAll<HTMLButtonElement>("[role=tab]")[next]?.focus();
  }

  return (
    <div ref={listRef} role="tablist" aria-label="Dönem" onKeyDown={onKeyDown} className="inline-flex rounded-lg border border-field bg-surface p-0.5">
      {OPTIONS.map((o) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            role="tab"
            aria-selected={active}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(o.value)}
            className={`tap-y rounded-md px-3.5 py-1.5 text-[13px] font-medium transition-colors ${
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
