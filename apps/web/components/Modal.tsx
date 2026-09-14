"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { IconClose } from "./Icons";

interface ModalProps {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
  footer?: ReactNode;
  size?: "sm" | "md";
}

/** Native <dialog> üzerine ince bir katman: Esc ve arka plan tıklaması kapatır. */
export function Modal({ open, title, onClose, children, footer, size = "md" }: ModalProps) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    else if (!open && el.open) el.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
      // Diyalog başka bir yoldan kapanırsa (Esc dışı native kapanış) React
      // durumu senkron kalsın; aksi halde modal bir daha açılamaz.
      onClose={onClose}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      aria-labelledby="modal-title"
      className={`m-auto max-h-[90dvh] overflow-auto rounded-card border border-line bg-surface p-0 text-ink shadow-none ${
        size === "sm" ? "w-[min(92vw,26rem)]" : "w-[min(92vw,34rem)]"
      }`}
    >
      <div className="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
        <h2 id="modal-title" className="text-[15.5px] font-semibold text-navy">
          {title}
        </h2>
        <button type="button" onClick={onClose} className="tap -mr-1 inline-flex items-center justify-center rounded-md p-1.5 text-muted hover:bg-mint hover:text-navy" aria-label="Kapat">
          <IconClose size={18} />
        </button>
      </div>
      <div className="px-5 py-4">{children}</div>
      {footer && <div className="flex flex-wrap items-center justify-end gap-2 border-t border-line bg-surface-2 px-5 py-3">{footer}</div>}
    </dialog>
  );
}
