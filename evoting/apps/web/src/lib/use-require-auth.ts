"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth, type Role } from "./auth";

interface RequireAuthResult {
  ready: boolean;
  allowed: boolean;
}

/**
 * Redirect unauthenticated users (or users with the wrong role) away from a
 * protected route. Returns readiness/allowed flags so the page can render a
 * loading state until hydration completes.
 */
export function useRequireAuth(requiredRole?: Role, redirectTo?: string): RequireAuthResult {
  const { ready, isAuthenticated, role } = useAuth();
  const router = useRouter();

  const allowed =
    isAuthenticated && (requiredRole === undefined || role === requiredRole);

  useEffect(() => {
    if (!ready) return;
    if (allowed) return;
    const target = redirectTo ?? (requiredRole === "admin" ? "/admin/login" : "/login");
    router.replace(target);
  }, [ready, allowed, requiredRole, redirectTo, router]);

  return { ready, allowed };
}
