"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { APP_NAME, APP_COLOR } from "@/lib/tokens";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import {
  Activity,
  Calendar,
  ClipboardList,
  Database,
  FileText,
  Home,
  Pill,
  Search,
  Settings,
  ShieldCheck,
  Stethoscope,
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/patients", label: "Patients", icon: Database },
  { href: "/appointments", label: "Appointments", icon: Calendar },
  { href: "/symptoms", label: "Symptoms", icon: Stethoscope },
  { href: "/diagnoses", label: "Diagnoses", icon: ClipboardList },
  { href: "/prescriptions", label: "Prescriptions", icon: Pill },
  { href: "/notes", label: "Clinical Notes", icon: FileText },
  { href: "/icd10", label: "ICD-10", icon: Search },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const showAudit = can.viewAudit(user);

  return (
    <aside className="w-64 border-r bg-card flex flex-col">
      <div className="p-4 border-b">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg">
          <span
            className="inline-flex items-center justify-center w-8 h-8 rounded-lg text-white"
            style={{ backgroundColor: APP_COLOR }}
          >
            <Activity className="w-4 h-4" />
          </span>
          {APP_NAME}
        </Link>
        <p className="text-xs text-muted-foreground mt-1 ml-10">
          Clinical intelligence
        </p>
      </div>
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )}
            >
              <Icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
        {showAudit && (
          <Link
            href="/audit"
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              pathname === "/audit" || pathname.startsWith("/audit/")
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <ShieldCheck className="w-4 h-4" />
            Audit Trail
          </Link>
        )}
      </nav>
      <div className="p-3 border-t">
        <Link
          href="/settings"
          className={cn(
            "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
            pathname === "/settings"
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          )}
        >
          <Settings className="w-4 h-4" />
          Settings
        </Link>
      </div>
    </aside>
  );
}
