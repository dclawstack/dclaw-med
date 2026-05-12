"use client";

import { useState } from "react";
import { generateNote, NoteGenerateResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { ClipboardList, Copy, FileText, Lock, Send } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";

export default function NotesPage() {
  const { user } = useAuth();
  const canUse = can.useClinicalTool(user);
  const [patientId, setPatientId] = useState("");
  const [noteType, setNoteType] = useState("progress");
  const [context, setContext] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<NoteGenerateResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!context.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await generateNote({
        patient_id: patientId || "00000000-0000-0000-0000-000000000000",
        note_type: noteType as "progress" | "admission" | "discharge" | "procedure",
        context,
      });
      setResult(res);
      toast.success("Note generated", { description: `${res.word_count} words` });
    } catch (err) {
      toast.error("Generation failed", { description: err instanceof Error ? err.message : "Unknown error" });
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard() {
    if (result?.generated_content) {
      navigator.clipboard.writeText(result.generated_content);
      toast.success("Copied to clipboard");
    }
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ClipboardList className="w-6 h-6 text-primary" />
          Clinical Notes
        </h1>
        <p className="text-muted-foreground">Generate clinical notes from patient context using AI assistance.</p>
      </div>

      {canUse ? (
        <Card>
          <CardContent className="pt-6 space-y-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="patient-id">Patient ID</Label>
                <Input id="patient-id" value={patientId} onChange={(e) => setPatientId(e.target.value)} placeholder="UUID of patient" />
              </div>
              <div className="space-y-2">
                <Label>Note Type</Label>
                <Select value={noteType} onValueChange={(v) => setNoteType(v ?? "progress")}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="progress">Progress Note</SelectItem>
                    <SelectItem value="admission">Admission Note</SelectItem>
                    <SelectItem value="discharge">Discharge Summary</SelectItem>
                    <SelectItem value="procedure">Procedure Note</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="context">Clinical Context</Label>
                <Textarea id="context" value={context} onChange={(e) => setContext(e.target.value)} placeholder="Patient presents with... Include relevant history, vitals, and findings." rows={6} required />
              </div>
              <Button type="submit" disabled={loading || !context.trim()}>
                {loading ? <Skeleton className="w-4 h-4 rounded-full" /> : <Send className="w-4 h-4 mr-2" />}
                Generate Note
              </Button>
            </form>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
            <Lock className="w-6 h-6" />
            Your role does not have access to AI note generation.
          </CardContent>
        </Card>
      )}

      {loading && (
        <Card><CardContent className="p-6 space-y-4">
          <Skeleton className="h-6 w-3/4" /><Skeleton className="h-4 w-full" /><Skeleton className="h-4 w-full" />
        </CardContent></Card>
      )}

      {result && !loading && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-base flex items-center gap-2">
                <FileText className="w-4 h-4 text-primary" />
                {result.note_type.charAt(0).toUpperCase() + result.note_type.slice(1)} Note
              </CardTitle>
              <p className="text-xs text-muted-foreground mt-1">{result.word_count} words · Generated by {result.generated_by}</p>
            </div>
            <Button variant="outline" size="sm" onClick={copyToClipboard}>
              <Copy className="w-4 h-4 mr-1" /> Copy
            </Button>
          </CardHeader>
          <Separator />
          <CardContent className="pt-4">
            <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono bg-muted p-4 rounded-lg">{result.generated_content}</pre>
            <p className="text-xs text-muted-foreground mt-3">{result.disclaimer}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
