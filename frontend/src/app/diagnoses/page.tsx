"use client";

import { useEffect, useState } from "react";
import { listDiagnoses, deleteDiagnosis, DiagnosisResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ClipboardList, Trash2 } from "lucide-react";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";
import { useAuth } from "@/components/auth-provider";
import { can } from "@/lib/permissions";

export default function DiagnosesPage() {
  const { user } = useAuth();
  const canWrite = can.writeDiagnosis(user);
  const [diagnoses, setDiagnoses] = useState<DiagnosisResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await listDiagnoses();
      setDiagnoses(data);
    } catch (err) {
      toast.error("Failed to load diagnoses", { description: err instanceof Error ? err.message : "" });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    try {
      await deleteDiagnosis(id);
      setDiagnoses((prev) => prev.filter((d) => d.id !== id));
      toast.success("Diagnosis deleted");
    } catch (err) {
      toast.error("Failed to delete diagnosis");
    }
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <ClipboardList className="w-6 h-6 text-primary" />
          Diagnoses
        </h1>
        <p className="text-muted-foreground">View and manage all clinical diagnoses.</p>
      </div>

      <Card>
        {loading ? (
          <CardContent className="p-6 space-y-2"><Skeleton className="h-8 w-full" /><Skeleton className="h-8 w-full" /></CardContent>
        ) : diagnoses.length === 0 ? (
          <CardContent className="p-8 text-center text-sm text-muted-foreground">No diagnoses yet. Add diagnoses from a patient record.</CardContent>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ICD-10</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead className="w-[80px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {diagnoses.map((d) => (
                <TableRow key={d.id}>
                  <TableCell className="font-mono">{d.icd10_code}</TableCell>
                  <TableCell className="font-medium">{d.name}</TableCell>
                  <TableCell><Badge variant={d.status === "confirmed" ? "default" : d.status === "provisional" ? "secondary" : "outline"}>{d.status}</Badge></TableCell>
                  <TableCell>{(d.confidence * 100).toFixed(0)}%</TableCell>
                  <TableCell>
                    {canWrite && (
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(d.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </div>
  );
}
