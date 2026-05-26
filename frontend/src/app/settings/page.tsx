"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { APP_NAME } from "@/lib/tokens";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";
import { Lock } from "lucide-react";

export default function SettingsPage() {
  const { user } = useAuth();
  if (!can.viewAppSettings(user)) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
            <Lock className="w-6 h-6" />
            Settings are restricted to administrators.
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Configuration and system information for {APP_NAME}.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>Backend connection settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">API Base URL</span>
            <Badge variant="secondary">{process.env.NEXT_PUBLIC_API_URL || "http://localhost:8092"}</Badge>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Frontend Port</span>
            <Badge variant="secondary">3004</Badge>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Backend Port</span>
            <Badge variant="secondary">8092</Badge>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>About</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p><strong>Product:</strong> {APP_NAME}</p>
          <p><strong>Version:</strong> 0.1.0</p>
          <p><strong>Category:</strong> Healthcare</p>
          <p className="text-muted-foreground">Part of the DClaw Stack — an AI-native application platform.</p>
        </CardContent>
      </Card>
    </div>
  );
}
