"use client";

import { cloneElement, isValidElement, type ComponentProps, type ReactElement, type ReactNode } from "react";

// Küçük, elle yazılmış Tailwind bileşenleri (yeni bağımlılık yok).

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

const VARIANT: Record<Variant, string> = {
  primary: "bg-brand-strong text-white hover:bg-brand-ink",
  secondary: "border border-field bg-surface text-navy hover:bg-mint",
  ghost: "text-navy hover:bg-mint",
  danger: "border border-danger/60 bg-surface text-danger hover:bg-danger-tint",
};

/* Devre dışı görünüm: opaklık yerine ölçülmüş renk çifti.
   Eski disabled:opacity-60 primary'de beyaz metni 2.95:1'e düşürüyordu; muted/surface-2 = 6.65:1.
   `busy` durumu devre dışı SAYILMAZ: buton rengini korur, yalnız tıklama kilitlenir. */
const DISABLED = "cursor-not-allowed border border-line bg-surface-2 text-muted";

const SIZE: Record<Size, string> = {
  sm: "h-8 px-3 text-[13px]",
  md: "h-10 px-4 text-sm",
};

export interface ButtonProps extends ComponentProps<"button"> {
  variant?: Variant;
  size?: Size;
  busy?: boolean;
  icon?: ReactNode;
}

export function Button({ variant = "secondary", size = "md", busy = false, icon, className = "", children, disabled, ...rest }: ButtonProps) {
  const inactive = Boolean(disabled) && !busy;
  return (
    <button
      type="button"
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      className={`tap inline-flex shrink-0 items-center justify-center gap-2 rounded-lg font-medium transition-colors ${inactive ? DISABLED : VARIANT[variant]} ${SIZE[size]} ${className}`}
      {...rest}
    >
      {busy ? <Spinner className="size-4" /> : icon}
      {children}
    </button>
  );
}

export function Spinner({ className = "size-5" }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export const inputClass =
  "tap-y h-10 w-full rounded-lg border border-field bg-surface px-3 text-sm text-navy placeholder:text-[#5b6b76] focus:border-brand-strong disabled:bg-surface-2 disabled:text-muted";

export function Input({ className = "", ...rest }: ComponentProps<"input">) {
  return <input className={`${inputClass} ${className}`} {...rest} />;
}

export function Select({ className = "", children, ...rest }: ComponentProps<"select">) {
  return (
    <select className={`${inputClass} appearance-none bg-[url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2216%22 height=%2216%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22%234b5b66%22 stroke-width=%222%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22><path d=%22m6 9 6 6 6-6%22/></svg>')] bg-[length:16px_16px] bg-[position:right_10px_center] bg-no-repeat pr-9 ${className}`} {...rest}>
      {children}
    </select>
  );
}

export function Textarea({ className = "", ...rest }: ComponentProps<"textarea">) {
  return <textarea className={`${inputClass} h-auto min-h-20 py-2 ${className}`} {...rest} />;
}

export function Field({ label, hint, error, children, htmlFor }: { label: string; hint?: ReactNode; error?: string; children: ReactNode; htmlFor?: string }) {
  // Açıklama/hata metni alana aria-describedby ile bağlanır; denetim id'si htmlFor'dan türetilir.
  const describedBy = htmlFor && (error || hint) ? `${htmlFor}-desc` : undefined;
  const control =
    describedBy && isValidElement(children)
      ? cloneElement(children as ReactElement<{ "aria-describedby"?: string; "aria-invalid"?: boolean }>, {
          "aria-describedby": describedBy,
          "aria-invalid": error ? true : undefined,
        })
      : children;
  return (
    <div className="space-y-1.5">
      <label htmlFor={htmlFor} className="block text-[13px] font-medium text-navy">
        {label}
      </label>
      {control}
      {error ? (
        <p id={describedBy} role="alert" className="text-xs text-danger">
          {error}
        </p>
      ) : hint ? (
        <p id={describedBy} className="text-xs text-muted">
          {hint}
        </p>
      ) : null}
    </div>
  );
}

export function Card({ title, action, children, className = "", padded = true }: { title?: ReactNode; action?: ReactNode; children: ReactNode; className?: string; padded?: boolean }) {
  return (
    <section className={`rounded-card border border-line bg-surface ${className}`}>
      {(title || action) && (
        <header className="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          {title && <h2 className="text-[15px] font-semibold text-navy">{title}</h2>}
          {action}
        </header>
      )}
      <div className={padded ? "p-5" : ""}>{children}</div>
    </section>
  );
}

export function Notice({ tone = "info", children, className = "" }: { tone?: "info" | "warn" | "danger" | "success"; children: ReactNode; className?: string }) {
  const tones = {
    info: "border-info-ink/20 bg-info-tint text-info-ink",
    warn: "border-warn/40 bg-warn-tint text-warn-ink",
    danger: "border-danger/30 bg-danger-tint text-danger-ink",
    success: "border-brand/30 bg-brand-tint text-brand-ink",
  };
  return (
    <div role={tone === "danger" ? "alert" : "status"} className={`rounded-lg border px-3.5 py-2.5 text-sm ${tones[tone]} ${className}`}>
      {children}
    </div>
  );
}

export function Skeleton({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-line/60 ${className}`} aria-hidden="true" />;
}
