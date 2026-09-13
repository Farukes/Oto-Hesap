"use client";

import { useState } from "react";
import { IconChevron } from "./Icons";

/** Katlanır "Sorguyu gör" bloğu; SQL <pre> içinde, kopyalanabilir. */
export function SqlBlock({ sql, defaultOpen = false }: { sql: string; defaultOpen?: boolean }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      // pano erişimi yoksa sessiz geç
    }
  }

  return (
    <details className="group mt-3 rounded-lg border border-line bg-surface-2" open={defaultOpen}>
      <summary className="flex cursor-pointer select-none items-center gap-1.5 px-3 py-2 text-[13px] font-medium text-navy [&::-webkit-details-marker]:hidden">
        <IconChevron size={14} className="text-muted transition-transform group-open:rotate-90" />
        Sorguyu gör
        <span className="ml-auto text-[11.5px] font-normal text-muted">SQL · salt okunur</span>
      </summary>
      <div className="relative border-t border-line">
        <pre className="whitespace-pre-wrap break-words px-3 py-2.5 pr-24 font-mono text-[12.5px] leading-relaxed text-navy">
          <code>{sql}</code>
        </pre>
        <button
          type="button"
          onClick={copy}
          className="absolute right-2 top-2 rounded-md border border-line bg-surface px-2 py-0.5 text-[11.5px] font-medium text-muted hover:text-navy"
        >
          {copied ? "Kopyalandı" : "Kopyala"}
        </button>
      </div>
    </details>
  );
}
