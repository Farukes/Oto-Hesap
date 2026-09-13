"use client";

import { usePathname } from "next/navigation";
import { useState } from "react";
import { IconMenu } from "./Icons";
import { MockBadge } from "./MockBadge";
import { pageTitle, Sidebar } from "./Sidebar";
import { useMockMode } from "@/lib/mock-mode";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const mock = useMockMode();
  const title = pageTitle(pathname);

  return (
    <div className="flex min-h-dvh">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-line bg-surface px-4 md:px-8">
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="-ml-1 rounded-md p-1.5 text-navy hover:bg-mint md:hidden"
            aria-label="Menüyü aç"
          >
            <IconMenu size={22} />
          </button>
          <div className="flex min-w-0 items-baseline gap-2">
            <span className="hidden text-sm font-semibold text-brand-strong sm:inline">OtoHesap</span>
            <span className="hidden text-line sm:inline" aria-hidden="true">
              /
            </span>
            <h1 className="truncate text-[17px] font-semibold text-navy">{title}</h1>
          </div>
          {mock && <MockBadge />}
        </header>
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-5 md:px-8 md:py-7">{children}</main>
        <footer className="mx-auto w-full max-w-7xl px-4 pb-5 pt-2 text-[11.5px] text-muted md:px-8">
          Sentetik demo verisi · Nisan–Eylül 2026
        </footer>
      </div>
    </div>
  );
}
