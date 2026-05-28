"use client";

import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react";
import { useAuth } from "@/components/auth-provider";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="h-14 border-b bg-card flex items-center justify-end px-4 shrink-0">
      <div className="flex items-center gap-3">
        {user && (
          <>
            <div className="flex flex-col items-end leading-tight">
              <span className="text-sm font-medium">{user.full_name}</span>
              <span className="text-xs text-muted-foreground capitalize">
                {user.role}
              </span>
            </div>
            <Button variant="ghost" size="sm" onClick={logout}>
              <LogOut className="w-4 h-4 mr-1" />
              Sign out
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
