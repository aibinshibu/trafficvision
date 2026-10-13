"use client";

import React, { ReactNode, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "../lib/auth-context";
import { canAccess, DEFAULT_HOME } from "../lib/rbac";

/** Blocks rendering of protected pages until the user is authenticated AND allowed. */
export default function RouteGuard({ children }: { children: ReactNode }) {
  const { role, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const allowed = isAuthenticated && canAccess(role, pathname);

  useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    } else if (!canAccess(role, pathname)) {
      router.replace(DEFAULT_HOME);
    }
  }, [isLoading, isAuthenticated, role, pathname, router]);

  if (isLoading || !allowed) {
    return (
      <div className="min-h-screen bg-[#090d16] flex items-center justify-center text-sm text-slate-400">
        Verifying access…
      </div>
    );
  }
  return <>{children}</>;
}
