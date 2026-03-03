"use client";

import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";
import { Activity, Command, type LucideIcon } from "lucide-react";

const links = [
  { href: "/", label: "Command Center", icon: Command },
  { href: "/viewer", label: "Bespoke Viewer", icon: Activity }
] satisfies ReadonlyArray<{ href: Route; label: string; icon: LucideIcon }>;

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-2">
      {links.map((link) => {
        const Icon = link.icon;
        const active = pathname === link.href;
        return (
          <Link
            key={link.href}
            href={link.href}
            className={`inline-flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
              active ? "border-cyan bg-cyan/10 text-ink" : "border-slate-300 bg-white"
            }`}
          >
            <Icon size={16} />
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
