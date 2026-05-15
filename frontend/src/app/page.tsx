"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import Link from "next/link";
import {
  listPatients, listPrescriptions, listNotes, listDiagnoses,
  PatientResponse, PrescriptionResponse, ClinicalNoteResponse, DiagnosisResponse,
} from "@/lib/api";
import { TriageWidget } from "@/components/triage-widget";
import {
  Activity,
  ArrowRight,
  ClipboardList,
  Database,
  FileText,
  Pill,
  Stethoscope,
  Users,
} from "lucide-react";

export default function DashboardPage() {
  const [patients, setPatients] = useState<PatientResponse[]>([]);
  const [prescriptions, setPrescriptions] = useState<PrescriptionResponse[]>([]);
  const [notes, setNotes] = useState<ClinicalNoteResponse[]>([]);
  const [diagnoses, setDiagnoses] = useState<DiagnosisResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      listPatients().catch((err) => { toast.error("Failed to load patients", { description: err.message }); return []; }),
      listPrescriptions().catch((err) => { toast.error("Failed to load prescriptions", { description: err.message }); return []; }),
      listNotes().catch((err) => { toast.error("Failed to load notes", { description: err.message }); return []; }),
      listDiagnoses().catch((err) => { toast.error("Failed to load diagnoses", { description: err.message }); return []; }),
    ]).then(([p, rx, n, dx]) => {
      setPatients(p);
      setPrescriptions(rx);
      setNotes(n);
      setDiagnoses(dx);
    }).finally(() => setLoading(false));
  }, []);

  const activePrescriptions = prescriptions.filter((r) => r.status === "active").length;
  const pendingDiagnoses = diagnoses.filter((d) => d.status === "provisional").length;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="w-6 h-6 text-primary" />
          DClaw Med
        </h1>
        <p className="text-muted-foreground">Clinical intelligence at your fingertips</p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="w-4 h-4 text-primary" />
              Patients
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{loading ? <Skeleton className="h-8 w-12" /> : patients.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Total registered</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Pill className="w-4 h-4 text-primary" />
              Prescriptions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{loading ? <Skeleton className="h-8 w-12" /> : activePrescriptions}</div>
            <p className="text-xs text-muted-foreground mt-1">Active medications</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileText className="w-4 h-4 text-primary" />
              Notes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{loading ? <Skeleton className="h-8 w-12" /> : notes.length}</div>
            <p className="text-xs text-muted-foreground mt-1">Clinical notes</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Stethoscope className="w-4 h-4 text-primary" />
              Diagnoses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{loading ? <Skeleton className="h-8 w-12" /> : pendingDiagnoses}</div>
            <p className="text-xs text-muted-foreground mt-1">Pending review</p>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <div className="space-y-3">
        <h2 className="text-lg font-semibold">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Link href="/patients">
            <Button><Users className="w-4 h-4 mr-2" />New Patient</Button>
          </Link>
          <Link href="/symptoms">
            <Button variant="outline"><Stethoscope className="w-4 h-4 mr-2" />Symptom Check</Button>
          </Link>
          <Link href="/notes">
            <Button variant="outline"><ClipboardList className="w-4 h-4 mr-2" />Write Note</Button>
          </Link>
          <Link href="/icd10">
            <Button variant="outline"><Database className="w-4 h-4 mr-2" />ICD-10 Lookup</Button>
          </Link>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <TriageWidget />
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent Patients</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            ) : patients.length === 0 ? (
              <p className="text-sm text-muted-foreground">No patients yet. Create your first patient to get started.</p>
            ) : (
              <div className="space-y-2">
                {patients.slice(0, 5).map((p) => (
                  <div key={p.id} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{p.medical_record_number}</Badge>
                      <span className="text-sm font-medium">{p.name}</span>
                    </div>
                    <Link href={`/patients/${p.id}`}>
                      <Button variant="ghost" size="sm">View</Button>
                    </Link>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle className="text-sm">System Status</CardTitle></CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">Backend API</span><Badge variant="secondary">Port 8092</Badge></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Frontend</span><Badge variant="secondary">Port 3004</Badge></div>
          <div className="flex justify-between"><span className="text-muted-foreground">Database</span><Badge variant="secondary">PostgreSQL 16</Badge></div>
          <div className="flex justify-between"><span className="text-muted-foreground">LLM Gateway</span><Badge variant="secondary">OpenRouter</Badge></div>
        </CardContent>
      </Card>
    </div>
  );
}
