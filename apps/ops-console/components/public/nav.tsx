"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/public", label: "Overview" },
  { href: "/public/scenarios", label: "Scenarios" },
  { href: "/public/installation", label: "Installation" },
  { href: "/public/deployment-preview", label: "Deployment" },
  { href: "/public/market-readiness", label: "Market Readiness" },
  { href: "/public/mobile-preview", label: "Mobile" },
  { href: "/public/community-preview", label: "Community" },
  { href: "/public/request-pilot", label: "Request Pilot" },
];

export function PublicNav() {
  const pathname = usePathname();

  return (
    <div className="sticky top-4 z-30">
      <div className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 rounded-full border border-white/10 bg-[rgba(10,14,22,0.78)] px-4 py-3 shadow-[0_18px_50px_rgba(0,0,0,0.32)] backdrop-blur-xl sm:px-5">
        <Link href="/public" className="text-sm font-medium tracking-[0.18em] text-slate-100 uppercase">
          Sentinel Core
        </Link>
        <nav className="flex flex-wrap items-center gap-2">
          {navItems.map((item) => {
            const active = pathname === item.href || (item.href === "/public/scenarios" && pathname?.startsWith("/public/scenarios/"));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "rounded-full px-3 py-2 text-sm transition duration-200",
                  active
                    ? "border border-white/14 bg-white/[0.08] text-white"
                    : "text-slate-300 hover:border hover:border-white/10 hover:bg-white/[0.04] hover:text-white",
                ].join(" ")}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
