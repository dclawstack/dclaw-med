"use client";

import { useEffect, useState } from "react";
import {
  getMyPatient,
  getMyPrescriptions,
  getMyLabResults,
  getMyNotes,
  getMyAppointments,
  getMyAllergies,
  PatientResponse,
  PrescriptionResponse,
  LabResultResponse,
  ClinicalNoteResponse,
  AppointmentResponse,
  AllergyResponse,
  ApiError,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";
import { isPatientUser } from "@/lib/permissions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  HeartPulse,
  Pill,
  FlaskConical,
  FileText,
  Calendar,
  AlertTriangle,
  Lock,
  ShieldAlert,
} from "lucide-react";
import { toast } from "sonner";

function severityClass(severity: string): string {
  if (severity === "anaphylaxis" || severity === "severe")
    return "text-destructive font-semibold";
  if (severity === "moderate") return "text-amber-600";
  return "text-muted-foreground";
}

export default function PatientPortalPage() {
  const { user } = useAuth();
  const [patient, setPatient] = useState<PatientResponse | null>(null);
  const [prescriptions, setPrescriptions] = useState<PrescriptionResponse[]>([]);
  const [labResults, setLabResults] = useState<LabResultResponse[]>([]);
  const [notes, setNotes] = useState<ClinicalNoteResponse[]>([]);
  const [appointments, setAppointments] = useState<AppointmentResponse[]>([]);
  const [allergies, setAllergies] = useState<AllergyResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [unlinked, setUnlinked] = useState(false);

  useEffect(() => {
    if (!isPatientUser(user)) {
      setLoading(false);
      return;
    }
    setLoading(true);
    Promise.all([
      getMyPatient(),
      getMyPrescriptions(),
      getMyLabResults(),
      getMyNotes(),
      getMyAppointments(),
      getMyAllergies(),
    ])
      .then(([p, rx, l, n, a, al]) => {
        setPatient(p);
        setPrescriptions(rx);
        setLabResults(l);
        setNotes(n);
        setAppointments(a);
        setAllergies(al);
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 403) {
          setUnlinked(true);
          return;
        }
        toast.error("Failed to load your records", {
          description: err instanceof Error ? err.message : "",
        });
      })
      .finally(() => setLoading(false));
  }, [user]);

  if (!isPatientUser(user)) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center text-sm text-muted-foreground flex flex-col items-center gap-2">
            <Lock className="w-6 h-6" />
            The patient portal is only available to patient accounts.
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <Skeleton className="h-10 w-1/3" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (unlinked) {
    return (
      <div className="max-w-3xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center flex flex-col items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-amber-600" />
            <p className="font-semibold">Account not yet linked</p>
            <p className="text-sm text-muted-foreground">
              Your account exists but isn't connected to a patient record yet.
              Please ask the clinic to complete the link before you can view
              your data here.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <HeartPulse className="w-6 h-6 text-primary" />
          My Records
        </h1>
        <p className="text-sm text-muted-foreground">
          A read-only view of what your care team has recorded. Reach out to
          them for any updates or corrections.
        </p>
      </div>

      {patient && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Profile</CardTitle>
          </CardHeader>
          <CardContent className="text-sm grid grid-cols-1 md:grid-cols-3 gap-2">
            <div><span className="text-muted-foreground">Name: </span>{patient.name}</div>
            <div><span className="text-muted-foreground">MRN: </span>{patient.medical_record_number}</div>
            <div><span className="text-muted-foreground">Date of birth: </span>{patient.date_of_birth}</div>
          </CardContent>
        </Card>
      )}

      {allergies.length > 0 && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold text-destructive">
              Known allergies on file
            </p>
            <p className="text-muted-foreground">
              {allergies
                .map((a) => `${a.allergen} (${a.severity})`)
                .join(" · ")}
            </p>
          </div>
        </div>
      )}

      <Tabs defaultValue="prescriptions">
        <TabsList>
          <TabsTrigger value="prescriptions"><Pill className="w-3 h-3 mr-1" />Prescriptions ({prescriptions.length})</TabsTrigger>
          <TabsTrigger value="labs"><FlaskConical className="w-3 h-3 mr-1" />Labs ({labResults.length})</TabsTrigger>
          <TabsTrigger value="appointments"><Calendar className="w-3 h-3 mr-1" />Appointments ({appointments.length})</TabsTrigger>
          <TabsTrigger value="notes"><FileText className="w-3 h-3 mr-1" />Notes ({notes.length})</TabsTrigger>
          <TabsTrigger value="allergies"><AlertTriangle className="w-3 h-3 mr-1" />Allergies ({allergies.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="prescriptions">
          <Card>
            <CardContent className="pt-6">
              {prescriptions.length === 0 ? (
                <p className="text-sm text-muted-foreground">No prescriptions on file.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Medication</TableHead>
                      <TableHead>Dosage</TableHead>
                      <TableHead>Frequency</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {prescriptions.map((p) => (
                      <TableRow key={p.id}>
                        <TableCell className="font-medium">{p.medication_name}</TableCell>
                        <TableCell>{p.dosage}</TableCell>
                        <TableCell>{p.frequency}</TableCell>
                        <TableCell><Badge variant="outline">{p.status}</Badge></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="labs">
          <Card>
            <CardContent className="pt-6">
              {labResults.length === 0 ? (
                <p className="text-sm text-muted-foreground">No lab results on file.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Test</TableHead>
                      <TableHead>Result</TableHead>
                      <TableHead>Reference</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {labResults.map((l) => (
                      <TableRow key={l.id}>
                        <TableCell className="font-medium">{l.test_name}</TableCell>
                        <TableCell>{l.result_value}{l.unit ? ` ${l.unit}` : ""}</TableCell>
                        <TableCell>{l.reference_range ?? "—"}</TableCell>
                        <TableCell><Badge variant="outline">{l.status}</Badge></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="appointments">
          <Card>
            <CardContent className="pt-6">
              {appointments.length === 0 ? (
                <p className="text-sm text-muted-foreground">No upcoming or past appointments.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>When</TableHead>
                      <TableHead>Duration</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Location</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {appointments.map((a) => (
                      <TableRow key={a.id}>
                        <TableCell>{new Date(a.scheduled_at).toLocaleString()}</TableCell>
                        <TableCell>{a.duration_minutes} min</TableCell>
                        <TableCell><Badge variant="outline">{a.status}</Badge></TableCell>
                        <TableCell>{a.location ?? "—"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notes">
          <Card>
            <CardContent className="pt-6 space-y-3">
              {notes.length === 0 ? (
                <p className="text-sm text-muted-foreground">No clinical notes on file.</p>
              ) : (
                notes.map((n) => (
                  <div key={n.id} className="border rounded-lg p-3">
                    <div className="text-xs text-muted-foreground flex items-center gap-2">
                      <Badge variant="outline">{n.note_type}</Badge>
                      {new Date(n.created_at).toLocaleString()}
                    </div>
                    <div className="text-sm whitespace-pre-wrap mt-2">{n.content}</div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="allergies">
          <Card>
            <CardContent className="pt-6">
              {allergies.length === 0 ? (
                <p className="text-sm text-muted-foreground">No known allergies on file.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Allergen</TableHead>
                      <TableHead>Severity</TableHead>
                      <TableHead>Reaction</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {allergies.map((a) => (
                      <TableRow key={a.id}>
                        <TableCell className="font-medium">{a.allergen}</TableCell>
                        <TableCell className={severityClass(a.severity)}>{a.severity}</TableCell>
                        <TableCell>{a.reaction ?? "—"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
