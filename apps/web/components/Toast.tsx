"use client";

import { useEffect } from "react";
import { IconCheck, IconClose, IconInfo } from "./Icons";

export interface ToastData {
  id: number;
  text: string;
  tone?: "success" | "info" | "danger";
}

/** Sağ altta kısa bildirim; 4 sn sonra kendiliğinden kapanır. */
export function Toast({ toast, onClose }: { toast: ToastData | null; onClose: (id: number) => void }) {
  useEffect(() => {
    if (!toast) return;
    const id = toast.id;
    const t = window.setTimeout(() => onClose(id), 4000);
    return () => window.clearTimeout(t);
  }, [toast, onClose]);

  if (!toast) return null;
  const tone = toast.tone ?? "success";
  const cls =
    tone === "danger"
      ? "border-danger/30 bg-danger-tint text-danger-ink"
      : tone === "info"
        ? "border-info-ink/20 bg-info-tint text-info-ink"
        : "border-brand/30 bg-brand-tint text-brand-ink";

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-4 z-50 flex justify-center px-4 md:justify-end md:px-6">
      <div role={tone === "danger" ? "alert" : "status"} className={`pointer-events-auto flex items-center gap-2.5 rounded-lg border px-3.5 py-2.5 text-sm font-medium ${cls}`}>
        {tone === "success" ? <IconCheck size={18} /> : <IconInfo size={18} />}
        {toast.text}
        <button type="button" onClick={() => onClose(toast.id)} className="tap ml-1 inline-flex items-center justify-center rounded p-1" aria-label="Bildirimi kapat">
          <IconClose size={14} />
        </button>
      </div>
    </div>
  );
}
