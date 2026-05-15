"use client";

import { FormEvent, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Stethoscope, Sparkles, AlertTriangle, ShieldAlert } from "lucide-react";
import { triage, TriageResponse } from "@/lib/api";

function urgencyVariant(
  level: string,
): "default" | "secondary" | "destructive" | "outline" {
  if (level === "critical" || level === "high") return "destructive";
  if (level === "medium") return "default";
  return "secondary";
}

interface TriageWidgetProps {
  /**
   * Title shown in the card header. Defaults to "AI Triage" — patient-portal
   * callers can pass "Symptom triage" or similar.
   */
  title?: string;
  /**
   * Hint text under the form. Defaults to a clinician-facing variant.
   */
  hint?: string;
}

export function TriageWidget({
  title = "Symptom triage",
  hint = "Describe the presenting symptoms in plain language.",
}: TriageWidgetProps) {
  const [symptoms, setSymptoms] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<TriageResponse | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!symptoms.trim()) return;
    setSubmitting(true);
    try {
      const r = await triage({ symptoms: symptoms.trim() });
      setResult(r);
    } catch (err) {
      toast.error("Triage failed", {
        description: err instanceof Error ? err.message : "",
      });
    } finally {
      setSubmitting(false);
    }
  }

  function reset() {
    setSymptoms("");
    setResult(null);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {!result ? (
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="space-y-1">
              <Label htmlFor="triage-input" className="text-xs text-muted-foreground">
                {hint}
              </Label>
              <Textarea
                id="triage-input"
                value={symptoms}
                onChange={(e) => setSymptoms(e.target.value)}
                placeholder="e.g. crushing chest pain radiating to the left arm…"
                rows={3}
              />
            </div>
            <Button
              type="submit"
              disabled={submitting || !symptoms.trim()}
              className="w-full"
            >
              <Stethoscope className="w-4 h-4 mr-2" />
              {submitting ? "Analyzing…" : "Triage"}
            </Button>
          </form>
        ) : (
          <div className="space-y-3 text-sm">
            <div className="flex items-center justify-between">
              <Badge variant={urgencyVariant(result.urgency_level)}>
                {result.urgency_level.toUpperCase()}
              </Badge>
              <span className="text-xs text-muted-foreground">
                → {result.suggested_department}
              </span>
            </div>

            <p className="font-medium">{result.summary}</p>

            {result.red_flags.length > 0 && (
              <div className="rounded-md border border-destructive/30 bg-destructive/5 p-3">
                <p className="text-xs font-semibold text-destructive flex items-center gap-1">
                  <ShieldAlert className="w-3 h-3" />
                  Red flags — seek emergency care if present
                </p>
                <ul className="list-disc list-inside mt-1 text-xs text-muted-foreground space-y-0.5">
                  {result.red_flags.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </div>
            )}

            {result.recommended_tests.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground">
                  Likely tests
                </p>
                <p className="text-xs text-muted-foreground">
                  {result.recommended_tests.join(" · ")}
                </p>
              </div>
            )}

            {result.differential_diagnoses.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-muted-foreground mb-1">
                  Top differentials
                </p>
                <ul className="text-xs text-muted-foreground space-y-1">
                  {result.differential_diagnoses.map((d) => (
                    <li key={d.icd10_code}>
                      <span className="font-medium">{d.condition}</span>
                      <span className="ml-1">({d.icd10_code})</span>
                      <span className="ml-1">
                        · confidence {Math.round(d.confidence * 100)}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <p className="text-[11px] text-muted-foreground flex items-start gap-1 pt-2 border-t">
              <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0" />
              <span>{result.disclaimer}</span>
            </p>

            <Button variant="outline" size="sm" onClick={reset} className="w-full">
              New triage
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
