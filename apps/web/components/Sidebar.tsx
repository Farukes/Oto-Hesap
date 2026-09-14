"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { IconBox, IconChat, IconClose, IconGrid, IconList, IconTruck, LogoMark } from "./Icons";
import { useApiState } from "@/lib/mock-mode";

export const NAV = [
  { href: "/", label: "Genel Bakış", Icon: IconGrid },
  { href: "/kayitlar", label: "Kayıtlar", Icon: IconList },
  { href: "/stok", label: "Stok", Icon: IconBox },
  { href: "/asistan", label: "Asistan", Icon: IconChat },
  { href: "/tedarik", label: "Tedarik", Icon: IconTruck },
] as const;

export function pageTitle(pathname: string): string {
  const hit = NAV.find((n) => (n.href === "/" ? pathname === "/" : pathname.startsWith(n.href)));
  return hit?.label ?? "OtoHesap";
}

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const FOCUSABLE = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();
  const api = useApiState();
  const asideRef = useRef<HTMLElement>(null);

  // Mobil çekmece açıkken: odak içeride kalır (Tab/Shift+Tab döner), Esc kapatır.
  useEffect(() => {
    if (!open) return;
    const aside = asideRef.current;
    if (!aside) return;
    aside.querySelector<HTMLElement>(FOCUSABLE)?.focus();

    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
        return;
      }
      if (e.key !== "Tab" || !aside) return;
      const items = [...aside.querySelectorAll<HTMLElement>(FOCUSABLE)].filter((el) => el.offsetParent !== null);
      if (items.length === 0) return;
      const first = items[0];
      const last = items[items.length - 1];
      const active = document.activeElement;
      if (e.shiftKey && (active === first || !aside.contains(active))) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && active === last) {
        e.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  return (
    <>
      {open && (
        // Perde yalnız fare/dokunma içindir; klavyede Esc ve "Menüyü kapat" düğmesi çalışır.
        <div aria-hidden="true" onClick={onClose} className="fixed inset-0 z-30 bg-navy/50 md:hidden" />
      )}
      <aside
        ref={asideRef}
        id="ana-menu"
        // Kapalıyken `invisible`: ekran dışı bağlantılar sekme sırasından ve ekran
        // okuyucudan çıkar (md'de `visible` ile geri gelir).
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-navy text-white transition-transform duration-200 [--ring:#ffffff] md:sticky md:top-0 md:h-dvh md:visible md:translate-x-0 ${
          open ? "translate-x-0" : "invisible -translate-x-full"
        }`}
        aria-label="Ana menü"
      >
        <div className="flex h-16 items-center gap-3 px-5">
          <LogoMark size={30} />
          <div className="leading-tight">
            <div className="text-[17px] font-semibold tracking-tight">OtoHesap</div>
            <div className="text-[11px] text-white/70">KOBİ karar katmanı</div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="tap ml-auto inline-flex items-center justify-center rounded-md p-1.5 text-white/80 hover:bg-white/10 hover:text-white md:hidden"
            aria-label="Menüyü kapat"
          >
            <IconClose size={18} />
          </button>
        </div>

        <nav className="mt-2 flex-1 px-3">
          <ul className="space-y-1">
            {NAV.map(({ href, label, Icon }) => {
              const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
              return (
                <li key={href}>
                  <Link
                    href={href}
                    onClick={onClose}
                    aria-current={active ? "page" : undefined}
                    className={`tap-y relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-[14.5px] font-medium transition-colors ${
                      active ? "bg-white/12 text-white" : "text-white/80 hover:bg-white/8 hover:text-white"
                    }`}
                  >
                    {active && <span className="absolute inset-y-2 left-0 w-1 rounded-r bg-brand" aria-hidden="true" />}
                    <Icon size={19} className={active ? "text-brand" : "text-white/70"} />
                    {label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="border-t border-white/10 px-5 py-4 text-[11.5px] leading-relaxed text-white/60">
          <div className="flex items-center gap-2">
            <span
              className={`inline-block size-2 rounded-full ${api === "mock" ? "bg-warn" : api === "live" ? "bg-brand" : "bg-white/30"}`}
              aria-hidden="true"
            />
            {api === "mock" ? "API kapalı · mock veri" : api === "live" ? "API bağlı" : "API bekleniyor"}
          </div>
          <div className="mt-1">Sürüm 0.1 · Demo</div>
        </div>
      </aside>
    </>
  );
}
