"use client";

import type { ComponentProps, ReactNode } from "react";

// Küçük, elle yazılmış Tailwind bileşenleri (yeni bağımlılık yok).

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

const VARIANT: Record<Variant, string> = {
  primary: "bg-brand-strong text-white hover:bg-brand-ink focus-visible:ring-brand",
  secondary: "border border-line bg-surface text-navy hover:bg-mint focus-visible:ring-brand",
  ghost: "text-navy hover:bg-mint focus-visible:ring-brand",
  danger: "border border-danger/30 bg-surface text-danger hover:bg-danger-tint focus-visible:ring-danger",
};

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
  return (
    <button
      type="button"
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      className={`inline-flex shrink-0 items-center justify-center gap-2 rounded-lg font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-mint disabled:cursor-not-allowed disabled:opacity-60 ${VARIANT[variant]} ${SIZE[size]} ${className}`}
      {...rest}
    >
      {busy ? <Spinner className="size-4" /> : icon}
      {children}
    </button>
  );
}

export function Spinner({ className = "size-5" }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}

export const inputClass =
  "h-10 w-full rounded-lg border border-line bg-surface px-3 text-sm text-navy placeholder:text-[#5b6b76] focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30 disabled:bg-surface-2 disabled:text-muted";

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
  return (
    <div className="space-y-1.5">
      <label htmlFor={htmlFor} className="block text-[13px] font-medium text-navy">
        {label}
      </label>
      {children}
      {error ? <p className="text-xs text-danger">{error}</p> : hint ? <p className="text-xs text-muted">{hint}</p> : null}
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
