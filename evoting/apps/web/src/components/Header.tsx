"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { ShieldCheck, LogOut } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { Button } from "./ui";
import { cn } from "@/lib/cn";

interface NavLink {
  href: string;
  label: string;
}

export function Header() {
  const { ready, isAuthenticated, role, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const voterLinks: NavLink[] = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/enroll", label: "Face enrollment" },
    { href: "/receipts", label: "Receipts" },
  ];

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link href="/" className="flex items-center gap-2 font-semibold text-slate-900">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-indigo-600 text-white">
            <ShieldCheck className="h-5 w-5" aria-hidden />
          </span>
          <span className="hidden sm:inline">E-Voting</span>
        </Link>

        <nav className="flex items-center gap-1" aria-label="Primary">
          {ready && isAuthenticated && role === "voter" && (
            <ul className="hidden items-center gap-1 md:flex">
              {voterLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={cn(
                      "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      pathname === link.href
                        ? "bg-indigo-50 text-indigo-700"
                        : "text-slate-600 hover:bg-slate-100",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {ready && isAuthenticated && role === "admin" && (
            <Link
              href="/admin"
              className={cn(
                "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                pathname.startsWith("/admin") && pathname !== "/admin/login"
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-slate-600 hover:bg-slate-100",
              )}
            >
              Admin console
            </Link>
          )}

          {ready && isAuthenticated ? (
            <Button variant="outline" size="sm" onClick={handleLogout} className="ml-2">
              <LogOut className="h-4 w-4" aria-hidden />
              <span className="hidden sm:inline">Log out</span>
            </Button>
          ) : (
            ready && (
              <div className="flex items-center gap-1">
                <Link
                  href="/login"
                  className="rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
                >
                  Log in
                </Link>
                <Link
                  href="/register"
                  className="rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-500"
                >
                  Register
                </Link>
              </div>
            )
          )}
        </nav>
      </div>
    </header>
  );
}
