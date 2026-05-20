"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  ApiError,
  DemoStatus,
  getDemoStatus,
  resetDemo,
  seedDemo,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { toast } from "sonner";
import { Database, Eraser, LogIn, Sparkles } from "lucide-react";

interface DemoCreds {
  email: string;
  password: string;
}

export function DemoSection() {
  const { login } = useAuth();
  const router = useRouter();

  const [status, setStatus] = useState<DemoStatus | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [signingIn, setSigningIn] = useState(false);
  const [creds, setCreds] = useState<DemoCreds | null>(null);

  // Probe the demo endpoint once on mount. A 403 / network error means the
  // backend either has the feature disabled or isn't reachable — in either
  // case we hide the section entirely.
  const refreshStatus = useCallback(async () => {
    try {
      const s = await getDemoStatus();
      setStatus(s);
    } catch {
      setStatus({ enabled: false, seeded: false, patient_count: 0 });
    } finally {
      setLoadingStatus(false);
    }
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  async function handleSeed() {
    setSeeding(true);
    try {
      const r = await seedDemo();
      setStatus({ enabled: r.enabled, seeded: r.seeded, patient_count: r.patient_count });
      setCreds(r.demo_credentials);
      toast.success("Demo data ready", {
        description: `${r.patient_count} demo patients are loaded.`,
      });
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Could not seed demo", { description: msg });
    } finally {
      setSeeding(false);
    }
  }

  async function handleReset() {
    setResetting(true);
    try {
      const r = await resetDemo();
      setStatus(r);
      setCreds(null);
      toast.success("Demo data cleared");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Could not clear demo", { description: msg });
    } finally {
      setResetting(false);
    }
  }

  async function handleSignIn() {
    if (!creds) return;
    setSigningIn(true);
    try {
      await login(creds.email, creds.password);
      // login() does its own router.replace; nothing else to do here.
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : String(err);
      toast.error("Could not sign in", { description: msg });
      setSigningIn(false);
    }
  }

  // Hide the section entirely if the backend reports demo mode off — keeps
  // production landing pages from advertising a feature that 403s.
  if (loadingStatus || !status?.enabled) return null;

  const isSeeded = status.seeded && status.patient_count > 0;

  return (
    <section id="demo" className="bg-muted/40 py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <div className="text-xs font-semibold uppercase tracking-widest text-primary">
            Try it
          </div>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Spin up a demo dataset.
          </h2>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground">
            One click loads five demo patients with diagnoses and active
            prescriptions, plus a demo clinician account so you can sign in
            and poke around. One click takes it all away.
          </p>
        </div>

        <Card className="mt-10 mx-auto max-w-3xl">
          <CardContent className="p-6 sm:p-8">
            <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
              <div className="flex items-start gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Database className="h-5 w-5" />
                </div>
                <div>
                  <div className="font-semibold">Demo dataset</div>
                  <div className="text-sm text-muted-foreground">
                    {isSeeded
                      ? `${status.patient_count} demo patients loaded · MRN prefix DEMO-`
                      : "Not loaded yet"}
                  </div>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {!isSeeded && (
                  <Button onClick={handleSeed} disabled={seeding}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    {seeding ? "Seeding…" : "Seed demo data"}
                  </Button>
                )}
                {isSeeded && (
                  <>
                    <Button onClick={handleSignIn} disabled={signingIn || !creds}>
                      <LogIn className="h-4 w-4 mr-2" />
                      {signingIn ? "Signing in…" : "Sign in as demo doctor"}
                    </Button>
                    <Button variant="outline" onClick={handleReset} disabled={resetting}>
                      <Eraser className="h-4 w-4 mr-2" />
                      {resetting ? "Clearing…" : "Clear demo data"}
                    </Button>
                  </>
                )}
              </div>
            </div>

            {isSeeded && creds && (
              <div className="mt-6 rounded-md border bg-background p-4 text-sm">
                <div className="font-medium text-foreground">
                  Demo credentials (also auto-used by the button above)
                </div>
                <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-muted-foreground">
                  <dt className="font-mono text-xs">email</dt>
                  <dd className="font-mono text-xs text-foreground">{creds.email}</dd>
                  <dt className="font-mono text-xs">password</dt>
                  <dd className="font-mono text-xs text-foreground">{creds.password}</dd>
                </dl>
              </div>
            )}

            {isSeeded && !creds && (
              <p className="mt-6 text-xs text-muted-foreground">
                Data is loaded but the demo credentials aren&rsquo;t in this
                browser session. Click <em>Seed demo data</em> again (it&rsquo;s
                idempotent) to fetch them, or sign in at <code className="font-mono">/login</code> with
                the credentials your admin shared.
              </p>
            )}
          </CardContent>
        </Card>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          Demo records are MRN-prefixed with <code className="font-mono">DEMO-</code>;
          clearing only removes those rows.
        </p>
      </div>
    </section>
  );
}
