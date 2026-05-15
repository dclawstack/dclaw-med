"use client";

import { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { Navbar } from "@/components/navbar";
import { Sidebar } from "@/components/sidebar";
import { useAuth } from "@/components/auth-provider";
import { isPatientUser } from "@/lib/permissions";

const PUBLIC_PATHS = new Set(["/login"]);
const PORTAL_HOME = "/patient-portal";

function isPatientAllowedPath(pathname: string): boolean {
  return (
    pathname === PORTAL_HOME ||
    pathname.startsWith(`${PORTAL_HOME}/`) ||
    pathname === "/settings" ||
    pathname === "/login"
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, loading } = useAuth();

  if (PUBLIC_PATHS.has(pathname)) {
    return <>{children}</>;
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        Loading…
      </div>
    );
  }

  // Provider already redirected to /login; render nothing for a single frame.
  if (!user) return null;

  // Patients hitting a clinician URL: hold rendering until the provider's
  // redirect lands. Prevents a flash of clinical UI before the navigation.
  if (isPatientUser(user) && !isPatientAllowedPath(pathname)) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        Redirecting to your portal…
      </div>
    );
  }

  return (
    <>
      <Navbar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </>
  );
}
