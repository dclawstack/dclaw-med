"use client";

import { useState } from "react";
import { analyzeSymptoms, SymptomAnalysisResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { toast } from "sonner";
import { Stethoscope, AlertTriangle, Send, FlaskConical } from "lucide-react";

export default function SymptomsPage() {
  const [patientId, setPatientId] = useState("");
  const [symptoms, setSymptoms] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SymptomAnalysisResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!symptoms.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await analyzeSymptoms({
        patient_id: patientId || "00000000-0000-0000-0000-000000000000",
        symptoms,
        max_results: 5,
      });
      setResult(res);
      toast.success("Analysis complete", { description: `${res.differential_diagnoses.length} differentials found` });
    } catch (err) {
      toast.error("Analysis failed", { description: err instanceof Error ? err.message : "Unknown error" });
    } finally {
      setLoading(false);
    }
  }

  const urgencyColor = {
    low: "bg-emerald-100 text-emerald-800 border-emerald-300",
    medium: "bg-amber-100 text-amber-800 border-amber-300",
    high: "bg-orange-100 text-orange-800 border-orange-300",
    critical: "bg-red-100 text-red-800 border-red-300",
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Stethoscope className="w-6 h-6 text-primary" />
          Symptom Analyzer
        </h1>
        <p className="text-muted-foreground">Enter symptoms to generate a differential diagnosis with confidence scores.</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="patient-id">Patient ID (optional)</Label>
              <Input id="patient-id" value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="UUID of existing patient" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="symptoms">Symptoms</Label>
              <Textarea id="symptoms" value={symptoms} onChange={(e) => setSymptoms(e.target.value)} placeholder="e.g. chest pain, shortness of breath, sweating" rows={4} required />
              <p className="text-xs text-muted-foreground">Separate multiple symptoms with commas</p>
            </div>
            <Button type="submit" disabled={loading || !symptoms.trim()}>
              {loading ? <Skeleton className="w-4 h-4 rounded-full" /> : <Send className="w-4 h-4 mr-2" />}
              Analyze
            </Button>
          </form>
        </CardContent>
      </Card>

      {loading && (
        <Card><CardContent className="p-6 space-y-4">
          <Skeleton className="h-6 w-3/4" /><Skeleton className="h-4 w-full" /><Skeleton className="h-4 w-5/6" />
        </CardContent></Card>
      )}

      {result && !loading && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Badge className={urgencyColor[result.urgency_level as keyof typeof urgencyColor] || urgencyColor.low}>
              <AlertTriangle className="w-3 h-3 mr-1" />
              {result.urgency_level.toUpperCase()} URGENCY
            </Badge>
            <span className="text-xs text-muted-foreground">{result.disclaimer}</span>
          </div>

          <Card>
            <CardHeader><CardTitle className="text-base">Differential Diagnoses</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              {result.differential_diagnoses.map((dx, i) => (
                <div key={i} className="border rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold">{i + 1}. {dx.condition}</span>
                      <Badge variant="outline">{dx.icd10_code}</Badge>
                    </div>
                    <Badge variant={dx.confidence > 0.7 ? "default" : dx.confidence > 0.4 ? "secondary" : "outline"}>
                      {(dx.confidence * 100).toFixed(0)}% confidence
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{dx.reasoning}</p>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><FlaskConical className="w-4 h-4 text-primary" />Recommended Tests</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {result.recommended_tests.map((t) => (
                  <Badge key={t} variant="secondary">{t}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
